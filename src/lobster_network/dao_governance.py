#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 DAO 治理系统 V2.2
去中心化自治组织

功能：
1. 提案创建/投票/执行
2. 治理 token 质押
3. 多签钱包
4. 治理参数调整
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .token_economy import TokenEconomy

# 导入常量
from .token_economy import TX_TYPE_TRANSFER


# ========== 常量定义 ==========

# 提案状态
PROPOSAL_STATUS_DRAFT = "draft"            # 草稿
PROPOSAL_STATUS_ACTIVE = "active"                 # 活跃
PROPOSAL_STATUS_PASSED = "passed"                 # 通过
PROPOSAL_STATUS_REJECTED = "rejected"             # 拒绝
PROPOSAL_STATUS_EXECUTED = "executed"             # 已执行
PROPOSAL_STATUS_CANCELLED = "cancelled"           # 已取消

# 提案类型
PROPOSAL_TYPE_PARAM = "param"              # 参数调整
PROPOSAL_TYPE_TREASURY = "treasury"        #  treasury 支出
PROPOSAL_TYPE_CONTRACT = "contract"        # 合约升级
PROPOSAL_TYPE_GENERIC = "generic"          # 通用提案

# 投票选项
VOTE_OPTION_FOR = "for"                    # 赞成
VOTE_OPTION_AGAINST = "against"            # 反对
VOTE_OPTION_ABSTAIN = "abstain"            # 弃权


# ========== 数据类定义 ==========

@dataclass
class Vote:
    """投票"""
    voter_id: str
    option: str
    weight: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "voter_id": self.voter_id,
            "option": self.option,
            "weight": self.weight,
            "timestamp": self.timestamp,
            "reason": self.reason,
        }


@dataclass
class Proposal:
    """提案"""
    proposal_id: str
    title: str
    description: str
    proposal_type: str
    creator_id: str
    status: str = PROPOSAL_STATUS_DRAFT
    votes: List[Vote] = field(default_factory=list)
    for_votes: float = 0.0
    against_votes: float = 0.0
    abstain_votes: float = 0.0
    quorum: float = 0.1  # 法定人数比例
    threshold: float = 0.5  # 通过阈值
    voting_start: Optional[str] = None
    voting_end: Optional[str] = None
    executed_at: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    @property
    def total_votes(self) -> float:
        """总票数"""
        return self.for_votes + self.against_votes + self.abstain_votes

    @property
    def approval_rate(self) -> float:
        """赞成率"""
        if self.total_votes == 0:
            return 0.0
        return self.for_votes / self.total_votes

    def to_dict(self) -> dict:
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "proposal_type": self.proposal_type,
            "creator_id": self.creator_id,
            "status": self.status,
            "votes": [v.to_dict() for v in self.votes],
            "for_votes": self.for_votes,
            "against_votes": self.against_votes,
            "abstain_votes": self.abstain_votes,
            "total_votes": self.total_votes,
            "approval_rate": self.approval_rate,
            "quorum": self.quorum,
            "threshold": self.threshold,
            "voting_start": self.voting_start,
            "voting_end": self.voting_end,
            "executed_at": self.executed_at,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class Treasury:
    """国库"""
    treasury_id: str
    balance: float = 0.0
    multi_sig_required: int = 3
    signers: List[str] = field(default_factory=list)
    transactions: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "treasury_id": self.treasury_id,
            "balance": self.balance,
            "multi_sig_required": self.multi_sig_required,
            "signers": self.signers,
            "transactions": self.transactions,
            "created_at": self.created_at,
        }


# ========== DAO 治理系统 ==========

class DAOGovernance:
    """DAO 治理系统"""

    def __init__(self, token_economy: TokenEconomy, data_dir: str = "/shared/lobster-network-data/dao"):
        self.token_economy = token_economy
        self.data_dir = data_dir
        self.proposals: Dict[str, Proposal] = {}
        self.treasuries: Dict[str, Treasury] = {}
        self._proposal_counter = 0
        self._treasury_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 提案管理 ==========

    def create_proposal(
        self,
        creator_id: str,
        title: str,
        description: str,
        proposal_type: str = PROPOSAL_TYPE_GENERIC,
        quorum: float = 0.1,
        threshold: float = 0.5,
        voting_duration_hours: int = 168,  # 7 天
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """创建提案"""
        # 检查创建者是否有足够质押
        wallet = self.token_economy.get_wallet(creator_id)
        if not wallet:
            return False, f"钱包不存在: {creator_id}"

        if wallet.staked < 10.0:  # 至少质押 10 🦞
            return False, f"质押不足: {wallet.staked} < 10.0 🦞"

        self._proposal_counter += 1
        proposal_id = f"proposal-{self._proposal_counter:04d}"

        # 计算投票时间
        now = datetime.now()
        voting_start = now.isoformat()
        voting_end = (now + timedelta(hours=voting_duration_hours)).isoformat()

        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            creator_id=creator_id,
            quorum=quorum,
            threshold=threshold,
            voting_start=voting_start,
            voting_end=voting_end,
            metadata=metadata or {},
        )
        self.proposals[proposal_id] = proposal

        return True, f"提案 {proposal_id} 创建成功"

    def submit_proposal(self, proposal_id: str) -> Tuple[bool, str]:
        """提交提案（进入投票阶段）"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False, f"提案 {proposal_id} 不存在"

        if proposal.status != PROPOSAL_STATUS_DRAFT:
            return False, f"提案 {proposal_id} 状态为 {proposal.status}，不可提交"

        proposal.status = PROPOSAL_STATUS_ACTIVE
        return True, f"提案 {proposal_id} 已提交，进入投票阶段"

    def cancel_proposal(self, proposal_id: str, reason: str = "") -> Tuple[bool, str]:
        """取消提案"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False, f"提案 {proposal_id} 不存在"

        if proposal.status not in [PROPOSAL_STATUS_DRAFT, PROPOSAL_STATUS_ACTIVE]:
            return False, f"提案 {proposal_id} 状态为 {proposal.status}，不可取消"

        proposal.status = PROPOSAL_STATUS_CANCELLED
        proposal.metadata["cancel_reason"] = reason
        return True, f"提案 {proposal_id} 已取消"

    # ========== 投票系统 ==========

    def vote(
        self,
        proposal_id: str,
        voter_id: str,
        option: str,
        reason: str = "",
    ) -> Tuple[bool, str]:
        """投票"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False, f"提案 {proposal_id} 不存在"

        if proposal.status != PROPOSAL_STATUS_ACTIVE:
            return False, f"提案 {proposal_id} 状态为 {proposal.status}，不可投票"

        # 检查投票选项
        if option not in [VOTE_OPTION_FOR, VOTE_OPTION_AGAINST, VOTE_OPTION_ABSTAIN]:
            return False, f"无效的投票选项: {option}"

        # 计算投票权重（基于质押量）
        wallet = self.token_economy.get_wallet(voter_id)
        if not wallet:
            return False, f"钱包不存在: {voter_id}"

        weight = wallet.staked
        if weight == 0:
            return False, f"质押量为 0，无法投票"

        # 检查是否已投票
        for v in proposal.votes:
            if v.voter_id == voter_id:
                return False, f"已投票: {voter_id}"

        # 创建投票
        vote = Vote(
            voter_id=voter_id,
            option=option,
            weight=weight,
            reason=reason,
        )
        proposal.votes.append(vote)

        # 更新票数
        if option == VOTE_OPTION_FOR:
            proposal.for_votes += weight
        elif option == VOTE_OPTION_AGAINST:
            proposal.against_votes += weight
        else:
            proposal.abstain_votes += weight

        return True, f"投票成功: {option} (权重: {weight})"

    def check_proposal_result(self, proposal_id: str) -> Tuple[bool, str]:
        """检查提案结果"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False, f"提案 {proposal_id} 不存在"

        if proposal.status != PROPOSAL_STATUS_ACTIVE:
            return False, f"提案 {proposal_id} 状态为 {proposal.status}，不可检查"

        # 检查法定人数
        total_supply = self.token_economy.get_total_supply()
        participation_rate = proposal.total_votes / total_supply if total_supply > 0 else 0

        if participation_rate < proposal.quorum:
            return False, f"法定人数不足: {participation_rate:.2%} < {proposal.quorum:.2%}"

        # 检查通过阈值
        if proposal.approval_rate >= proposal.threshold:
            proposal.status = PROPOSAL_STATUS_PASSED
            return True, f"提案 {proposal_id} 通过 (赞成率: {proposal.approval_rate:.2%})"
        else:
            proposal.status = PROPOSAL_STATUS_REJECTED
            return True, f"提案 {proposal_id} 拒绝 (赞成率: {proposal.approval_rate:.2%})"

    # ========== 执行提案 ==========

    def execute_proposal(self, proposal_id: str) -> Tuple[bool, str]:
        """执行提案"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False, f"提案 {proposal_id} 不存在"

        if proposal.status != PROPOSAL_PASSED:
            return False, f"提案 {proposal_id} 状态为 {proposal.status}，不可执行"

        # 根据提案类型执行不同操作
        if proposal.proposal_type == PROPOSAL_TYPE_TREASURY:
            # Treasury 支出
            amount = proposal.metadata.get("amount", 0)
            recipient = proposal.metadata.get("recipient", "")
            if amount > 0 and recipient:
                treasury = self.get_treasury("treasury-0001")
                if treasury and treasury.balance >= amount:
                    treasury.balance -= amount
                    self.token_economy.update_user_balance(recipient, amount)
                    treasury.transactions.append({
                        "type": "proposal_execution",
                        "proposal_id": proposal_id,
                        "amount": amount,
                        "recipient": recipient,
                        "timestamp": datetime.now().isoformat(),
                    })

        proposal.status = PROPOSAL_STATUS_EXECUTED
        proposal.executed_at = datetime.now().isoformat()
        return True, f"提案 {proposal_id} 已执行"

    # ========== 国库管理 ==========

    def create_treasury(
        self,
        treasury_id: str,
        initial_balance: float = 0.0,
        signers: List[str] = None,
        multi_sig_required: int = 3,
    ) -> Tuple[bool, str]:
        """创建国库"""
        if treasury_id in self.treasuries:
            return False, f"国库 {treasury_id} 已存在"

        treasury = Treasury(
            treasury_id=treasury_id,
            balance=initial_balance,
            signers=signers or [],
            multi_sig_required=multi_sig_required,
        )
        self.treasuries[treasury_id] = treasury

        return True, f"国库 {treasury_id} 创建成功"

    def get_treasury(self, treasury_id: str) -> Optional[Treasury]:
        """获取国库"""
        return self.treasuries.get(treasury_id)

    def deposit_to_treasury(
        self,
        treasury_id: str,
        depositor_id: str,
        amount: float,
    ) -> Tuple[bool, str]:
        """向国库存款"""
        treasury = self.treasuries.get(treasury_id)
        if not treasury:
            return False, f"国库 {treasury_id} 不存在"

        # 从存款人账户扣款
        ok, msg = self.token_economy.transfer(depositor_id, "treasury_pool", amount)
        if not ok:
            return False, msg

        treasury.balance += amount
        return True, f"存款成功: {amount} 🦞"

    def withdraw_from_treasury(
        self,
        treasury_id: str,
        recipient_id: str,
        amount: float,
        signatures: List[str] = None,
    ) -> Tuple[bool, str]:
        """从国库取款（需要多签）"""
        treasury = self.treasuries.get(treasury_id)
        if not treasury:
            return False, f"国库 {treasury_id} 不存在"

        if treasury.balance < amount:
            return False, f"国库余额不足: {treasury.balance} < {amount}"

        # 检查多签
        if signatures and len(signatures) < treasury.multi_sig_required:
            return False, f"签名不足: {len(signatures)} < {treasury.multi_sig_required}"

        # 执行取款
        treasury.balance -= amount
        self.token_economy.update_user_balance(recipient_id, amount)

        treasury.transactions.append({
            "type": "withdrawal",
            "recipient": recipient_id,
            "amount": amount,
            "signatures": signatures,
            "timestamp": datetime.now().isoformat(),
        })

        return True, f"取款成功: {amount} 🦞"

    # ========== 查询功能 ==========

    def get_proposal(self, proposal_id: str) -> Optional[Dict]:
        """获取提案"""
        proposal = self.proposals.get(proposal_id)
        return proposal.to_dict() if proposal else None

    def get_active_proposals(self, limit: int = 20) -> List[Dict]:
        """获取活跃提案"""
        proposals = [
            p.to_dict() for p in self.proposals.values()
            if p.status == PROPOSAL_STATUS_ACTIVE
        ]
        return sorted(proposals, key=lambda x: x["created_at"], reverse=True)[:limit]

    def get_proposals_by_creator(self, creator_id: str) -> List[Dict]:
        """获取创建者的提案"""
        proposals = [
            p.to_dict() for p in self.proposals.values()
            if p.creator_id == creator_id
        ]
        return sorted(proposals, key=lambda x: x["created_at"], reverse=True)

    def get_governance_statistics(self) -> Dict:
        """获取治理统计"""
        return {
            "total_proposals": len(self.proposals),
            "active_proposals": len([p for p in self.proposals.values() if p.status == PROPOSAL_STATUS_ACTIVE]),
            "passed_proposals": len([p for p in self.proposals.values() if p.status == PROPOSAL_PASSED]),
            "executed_proposals": len([p for p in self.proposals.values() if p.status == PROPOSAL_EXECUTED]),
            "total_treasuries": len(self.treasuries),
            "total_treasury_balance": sum(t.balance for t in self.treasuries.values()),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "proposals": {pid: p.to_dict() for pid, p in self.proposals.items()},
            "treasuries": {tid: t.to_dict() for tid, t in self.treasuries.items()},
            "counters": {
                "proposal": self._proposal_counter,
                "treasury": self._treasury_counter,
            },
        }
        with open(os.path.join(self.data_dir, "dao_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "dao_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.proposals = {}
            for pid, p_data in data.get("proposals", {}).items():
                proposal = Proposal(
                    proposal_id=p_data["proposal_id"],
                    title=p_data["title"],
                    description=p_data.get("description", ""),
                    proposal_type=p_data.get("proposal_type", PROPOSAL_TYPE_GENERIC),
                    creator_id=p_data["creator_id"],
                    status=p_data.get("status", PROPOSAL_STATUS_DRAFT),
                    quorum=p_data.get("quorum", 0.1),
                    threshold=p_data.get("threshold", 0.5),
                    voting_start=p_data.get("voting_start"),
                    voting_end=p_data.get("voting_end"),
                    executed_at=p_data.get("executed_at"),
                    created_at=p_data.get("created_at", datetime.now().isoformat()),
                    metadata=p_data.get("metadata", {}),
                )

                # 加载投票
                for v_data in p_data.get("votes", []):
                    vote = Vote(
                        voter_id=v_data["voter_id"],
                        option=v_data["option"],
                        weight=v_data["weight"],
                        timestamp=v_data.get("timestamp", datetime.now().isoformat()),
                        reason=v_data.get("reason", ""),
                    )
                    proposal.votes.append(vote)

                    if v_data["option"] == VOTE_OPTION_FOR:
                        proposal.for_votes += v_data["weight"]
                    elif v_data["option"] == VOTE_OPTION_AGAINST:
                        proposal.against_votes += v_data["weight"]
                    else:
                        proposal.abstain_votes += v_data["weight"]

                self.proposals[pid] = proposal

            self.treasuries = {tid: Treasury(**t) for tid, t in data.get("treasuries", {}).items()}

            counters = data.get("counters", {})
            self._proposal_counter = counters.get("proposal", 0)
            self._treasury_counter = counters.get("treasury", 0)

            return True
        return False
