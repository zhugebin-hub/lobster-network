#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络智能合约系统 V2.1
自动结算功能

功能：
1. 智能合约创建/执行/结算
2. 条件触发自动结算
3. 多签合约
4. 合约模板库
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field

from .token_economy import TokenEconomy, Transaction, TX_TYPE_TRANSFER


# ========== 常量定义 ==========

# 合约状态
CONTRACT_STATUS_DRAFT = "draft"          # 草稿
CONTRACT_STATUS_ACTIVE = "active"        # 活跃
CONTRACT_STATUS_EXECUTING = "executing"  # 执行中
CONTRACT_STATUS_COMPLETED = "completed"  # 已完成
CONTRACT_STATUS_CANCELLED = "cancelled"  # 已取消
CONTRACT_STATUS_DISPUTED = "disputed"    # 争议中

# 合约类型
CONTRACT_TYPE_TASK = "task"              # 任务合约
CONTRACT_TYPE_ESCROW = "escrow"          # 托管合约
CONTRACT_TYPE_SUBSCRIPTION = "subscription"  # 订阅合约
CONTRACT_TYPE_MILESTONE = "milestone"    # 里程碑合约

# 结算条件类型
CONDITION_TYPE_TIME = "time"             # 时间条件
CONDITION_TYPE_TASK = "task"             # 任务完成条件
CONDITION_TYPE_APPROVAL = "approval"     # 审批条件
CONDITION_TYPE_ORACLE = "oracle"         # 预言机条件


# ========== 数据类定义 ==========

@dataclass
class ContractCondition:
    """合约条件"""
    condition_id: str
    condition_type: str
    description: str
    target_value: str
    current_value: Optional[str] = None
    is_met: bool = False
    met_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "condition_id": self.condition_id,
            "condition_type": self.condition_type,
            "description": self.description,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "is_met": self.is_met,
            "met_at": self.met_at,
        }


@dataclass
class SmartContract:
    """智能合约"""
    contract_id: str
    title: str
    description: str
    contract_type: str
    creator_id: str
    executor_id: str
    amount: float
    currency: str = "🦞"
    status: str = CONTRACT_STATUS_DRAFT
    conditions: List[ContractCondition] = field(default_factory=list)
    signatures: Dict[str, str] = field(default_factory=dict)
    required_signatures: int = 2
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def hash(self) -> str:
        """计算合约哈希"""
        contract_string = json.dumps({
            "contract_id": self.contract_id,
            "title": self.title,
            "creator_id": self.creator_id,
            "executor_id": self.executor_id,
            "amount": self.amount,
            "created_at": self.created_at,
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(contract_string.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "title": self.title,
            "description": self.description,
            "contract_type": self.contract_type,
            "creator_id": self.creator_id,
            "executor_id": self.executor_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "conditions": [c.to_dict() for c in self.conditions],
            "signatures": self.signatures,
            "required_signatures": self.required_signatures,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "executed_at": self.executed_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
            "hash": self.hash,
        }


# ========== 智能合约系统 ==========

class SmartContractSystem:
    """智能合约系统"""

    def __init__(self, token_economy: TokenEconomy, data_dir: str = "/shared/lobster-network-data/contracts"):
        self.token_economy = token_economy
        self.data_dir = data_dir
        self.contracts: Dict[str, SmartContract] = {}
        self._contract_counter = 0
        self._condition_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 合约创建 ==========

    def create_contract(
        self,
        creator_id: str,
        executor_id: str,
        title: str,
        description: str,
        contract_type: str = CONTRACT_TYPE_TASK,
        amount: float = 10.0,
        conditions: List[Dict] = None,
        required_signatures: int = 2,
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """创建智能合约"""
        # 检查创建者余额
        creator_balance = self.token_economy.get_balance(creator_id)
        if creator_balance < amount:
            return False, f"创建者余额不足: {creator_balance} < {amount}"

        self._contract_counter += 1
        contract_id = f"contract-{self._contract_counter:04d}"

        # 创建条件
        contract_conditions = []
        if conditions:
            for cond in conditions:
                self._condition_counter += 1
                condition = ContractCondition(
                    condition_id=f"cond-{self._condition_counter:04d}",
                    condition_type=cond.get("type", CONDITION_TYPE_TASK),
                    description=cond.get("description", ""),
                    target_value=cond.get("target_value", ""),
                )
                contract_conditions.append(condition)

        contract = SmartContract(
            contract_id=contract_id,
            title=title,
            description=description,
            contract_type=contract_type,
            creator_id=creator_id,
            executor_id=executor_id,
            amount=amount,
            conditions=contract_conditions,
            required_signatures=required_signatures,
            metadata=metadata or {},
        )
        self.contracts[contract_id] = contract

        # 冻结创建者资金
        self.token_economy.stake(creator_id, amount)

        return True, f"合约 {contract_id} 创建成功，已冻结 {amount} 🦞"

    # ========== 合约签署 ==========

    def sign_contract(
        self,
        contract_id: str,
        signer_id: str,
    ) -> Tuple[bool, str]:
        """签署合约"""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False, f"合约 {contract_id} 不存在"

        if contract.status != CONTRACT_STATUS_DRAFT:
            return False, f"合约 {contract_id} 状态为 {contract.status}，不可签署"

        if signer_id in contract.signatures:
            return False, f"已签署过合约 {contract_id}"

        # 生成签名
        signature = hashlib.sha256(
            f"{contract_id}:{signer_id}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        contract.signatures[signer_id] = signature
        contract.updated_at = datetime.now().isoformat()

        # 检查是否满足签署要求
        if len(contract.signatures) >= contract.required_signatures:
            contract.status = CONTRACT_STATUS_ACTIVE
            return True, f"合约 {contract_id} 签署完成，进入活跃状态"

        return True, f"合约 {contract_id} 签署成功 ({len(contract.signatures)}/{contract.required_signatures})"

    # ========== 条件验证 ==========

    def check_condition(
        self,
        contract_id: str,
        condition_id: str,
        current_value: str,
    ) -> Tuple[bool, str]:
        """检查合约条件"""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False, f"合约 {contract_id} 不存在"

        condition = None
        for c in contract.conditions:
            if c.condition_id == condition_id:
                condition = c
                break

        if not condition:
            return False, f"条件 {condition_id} 不存在"

        # 更新当前值
        condition.current_value = current_value

        # 验证条件
        if condition.condition_type == CONDITION_TYPE_TIME:
            # 时间条件：检查是否到达指定时间
            try:
                target_time = datetime.fromisoformat(condition.target_value)
                if datetime.now() >= target_time:
                    condition.is_met = True
                    condition.met_at = datetime.now().isoformat()
            except ValueError:
                pass

        elif condition.condition_type == CONDITION_TYPE_TASK:
            # 任务条件：检查任务是否完成
            condition.is_met = (current_value.lower() in ["completed", "done", "完成"])
            if condition.is_met:
                condition.met_at = datetime.now().isoformat()

        elif condition.condition_type == CONDITION_TYPE_APPROVAL:
            # 审批条件：检查是否获得批准
            condition.is_met = (current_value.lower() in ["approved", "yes", "批准"])
            if condition.is_met:
                condition.met_at = datetime.now().isoformat()

        contract.updated_at = datetime.now().isoformat()

        if condition.is_met:
            return True, f"条件 {condition_id} 已满足"
        else:
            return False, f"条件 {condition_id} 未满足"

    # ========== 自动结算 ==========

    def auto_settle(self, contract_id: str) -> Tuple[bool, str]:
        """自动结算合约"""
        contract = self.contracts.get(contract_id)
        if not contract:
            return False, f"合约 {contract_id} 不存在"

        if contract.status not in [CONTRACT_STATUS_ACTIVE, CONTRACT_STATUS_EXECUTING]:
            return False, f"合约 {contract_id} 状态为 {contract.status}，不可结算"

        # 检查所有条件是否满足
        all_met = all(c.is_met for c in contract.conditions)

        if not all_met:
            unmet = [c.condition_id for c in contract.conditions if not c.is_met]
            return False, f"条件未全部满足: {unmet}"

        # 执行结算
        contract.status = CONTRACT_STATUS_COMPLETED
        contract.executed_at = datetime.now().isoformat()
        contract.completed_at = datetime.now().isoformat()

        # 解冻资金并转账
        self.token_economy.unstake(contract.creator_id, contract.amount)
        ok, msg = self.token_economy.transfer(
            contract.creator_id,
            contract.executor_id,
            contract.amount,
            tx_type="contract_settlement",
            metadata={"contract_id": contract_id},
        )

        if ok:
            return True, f"合约 {contract_id} 结算成功，{contract.amount} 🦞 已转账"
        else:
            return False, f"合约 {contract_id} 结算失败: {msg}"

    # ========== 合约模板 ==========

    def create_from_template(
        self,
        template_name: str,
        creator_id: str,
        executor_id: str,
        params: Dict = None,
    ) -> Tuple[bool, str]:
        """从模板创建合约"""
        templates = {
            "task_contract": {
                "title": "任务合约",
                "description": "完成任务后自动结算",
                "contract_type": CONTRACT_TYPE_TASK,
                "conditions": [
                    {
                        "type": CONDITION_TYPE_TASK,
                        "description": "任务完成",
                        "target_value": "completed",
                    }
                ],
                "required_signatures": 2,
            },
            "escrow_contract": {
                "title": "托管合约",
                "description": "资金托管，条件满足后释放",
                "contract_type": CONTRACT_TYPE_ESCROW,
                "conditions": [
                    {
                        "type": CONDITION_TYPE_APPROVAL,
                        "description": "双方确认",
                        "target_value": "approved",
                    }
                ],
                "required_signatures": 2,
            },
            "milestone_contract": {
                "title": "里程碑合约",
                "description": "分阶段付款",
                "contract_type": CONTRACT_TYPE_MILESTONE,
                "conditions": [
                    {
                        "type": CONDITION_TYPE_TASK,
                        "description": "第一阶段完成",
                        "target_value": "completed",
                    },
                    {
                        "type": CONDITION_TYPE_TASK,
                        "description": "第二阶段完成",
                        "target_value": "completed",
                    },
                ],
                "required_signatures": 2,
            },
        }

        template = templates.get(template_name)
        if not template:
            return False, f"模板 {template_name} 不存在"

        # 合并参数
        title = params.get("title", template["title"]) if params else template["title"]
        description = params.get("description", template["description"]) if params else template["description"]
        amount = params.get("amount", 10.0) if params else 10.0

        return self.create_contract(
            creator_id=creator_id,
            executor_id=executor_id,
            title=title,
            description=description,
            contract_type=template["contract_type"],
            amount=amount,
            conditions=template["conditions"],
            required_signatures=template["required_signatures"],
        )

    # ========== 查询功能 ==========

    def get_contract(self, contract_id: str) -> Optional[Dict]:
        """获取合约"""
        contract = self.contracts.get(contract_id)
        return contract.to_dict() if contract else None

    def get_contracts_by_user(self, user_id: str, role: str = "creator") -> List[Dict]:
        """获取用户相关合约"""
        if role == "creator":
            contracts = [c.to_dict() for c in self.contracts.values() if c.creator_id == user_id]
        else:
            contracts = [c.to_dict() for c in self.contracts.values() if c.executor_id == user_id]
        return sorted(contracts, key=lambda x: x["created_at"], reverse=True)

    def get_active_contracts(self, limit: int = 20) -> List[Dict]:
        """获取活跃合约"""
        contracts = [
            c.to_dict() for c in self.contracts.values()
            if c.status in [CONTRACT_STATUS_ACTIVE, CONTRACT_STATUS_EXECUTING]
        ]
        return sorted(contracts, key=lambda x: x["created_at"], reverse=True)[:limit]

    def get_contract_statistics(self) -> Dict:
        """获取合约统计"""
        return {
            "total_contracts": len(self.contracts),
            "active_contracts": len([c for c in self.contracts.values() if c.status == CONTRACT_STATUS_ACTIVE]),
            "completed_contracts": len([c for c in self.contracts.values() if c.status == CONTRACT_STATUS_COMPLETED]),
            "disputed_contracts": len([c for c in self.contracts.values() if c.status == CONTRACT_STATUS_DISPUTED]),
            "total_amount": sum(c.amount for c in self.contracts.values()),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "contracts": {cid: c.to_dict() for cid, c in self.contracts.items()},
            "counters": {
                "contract": self._contract_counter,
                "condition": self._condition_counter,
            },
        }
        with open(os.path.join(self.data_dir, "contracts_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "contracts_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.contracts = {}
            for cid, c_data in data.get("contracts", {}).items():
                contract = SmartContract(
                    contract_id=c_data["contract_id"],
                    title=c_data["title"],
                    description=c_data.get("description", ""),
                    contract_type=c_data.get("contract_type", CONTRACT_TYPE_TASK),
                    creator_id=c_data["creator_id"],
                    executor_id=c_data["executor_id"],
                    amount=c_data.get("amount", 0.0),
                    currency=c_data.get("currency", "🦞"),
                    status=c_data.get("status", CONTRACT_STATUS_DRAFT),
                    required_signatures=c_data.get("required_signatures", 2),
                    created_at=c_data.get("created_at", datetime.now().isoformat()),
                    updated_at=c_data.get("updated_at", datetime.now().isoformat()),
                    executed_at=c_data.get("executed_at"),
                    completed_at=c_data.get("completed_at"),
                    metadata=c_data.get("metadata", {}),
                )

                # 加载条件
                for cond_data in c_data.get("conditions", []):
                    condition = ContractCondition(
                        condition_id=cond_data["condition_id"],
                        condition_type=cond_data["condition_type"],
                        description=cond_data["description"],
                        target_value=cond_data["target_value"],
                        current_value=cond_data.get("current_value"),
                        is_met=cond_data.get("is_met", False),
                        met_at=cond_data.get("met_at"),
                    )
                    contract.conditions.append(condition)

                # 加载签名
                contract.signatures = c_data.get("signatures", {})

                self.contracts[cid] = contract

            counters = data.get("counters", {})
            self._contract_counter = counters.get("contract", 0)
            self._condition_counter = counters.get("condition", 0)

            return True
        return False
