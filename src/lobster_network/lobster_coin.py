#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙虾币 (Lobster Coin) - 小龙虾网络 V3.1
训练经济闭环系统

功能:
- 训练奖励 +50LC，API 调用 -5LC
- 余额不足时限制非核心请求
- 排行榜与成就系统
- 学员经济行为分析
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class TransactionType(Enum):
    EARN_TRAINING = "earn_training"       # 训练奖励
    EARN_TASK = "earn_task"               # 任务奖励
    EARN_BONUS = "earn_bonus"             # 额外奖励
    SPEND_API = "spend_api"               # API 调用
    SPEND_TOOL = "spend_tool"             # 工具调用
    SPEND_STORAGE = "spend_storage"       # 存储费用
    TRANSFER = "transfer"                 # 转账
    BONUS = "bonus"                       # 系统奖励
    PENALTY = "penalty"                   # 惩罚


@dataclass
class Transaction:
    """交易记录"""
    tx_id: str
    from_account: str
    to_account: str
    amount: float
    tx_type: str
    description: str = ""
    timestamp: str = ""
    metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "tx_id": self.tx_id,
            "from": self.from_account,
            "to": self.to_account,
            "amount": self.amount,
            "type": self.tx_type,
            "description": self.description,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class Achievement:
    """成就"""
    id: str
    name: str
    description: str
    icon: str = "🏆"
    condition: str = ""           # 条件描述
    earned: bool = False
    earned_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "condition": self.condition,
            "earned": self.earned,
            "earned_at": self.earned_at,
        }


@dataclass
class Account:
    """账户"""
    account_id: str
    name: str
    balance: float = 0.0
    total_earned: float = 0.0
    total_spent: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    achievements: List[Achievement] = field(default_factory=list)
    created_at: str = ""
    level: int = 1
    daily_earn_limit: float = 500.0   # 每日赚取上限
    _daily_earned: float = 0.0
    _last_reset_date: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def _check_daily_reset(self):
        """检查是否需要重置每日统计"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self._last_reset_date != today:
            self._daily_earned = 0.0
            self._last_reset_date = today

    def can_spend(self, amount: float) -> bool:
        """是否可以支出"""
        return self.balance >= amount

    def earn(self, amount: float, tx_type: str = "earn_training",
             description: str = "", metadata: Optional[Dict] = None) -> Transaction:
        """收入"""
        self._check_daily_reset()
        if self._daily_earned + amount > self.daily_earn_limit:
            raise ValueError(f"超出每日赚取上限 {self.daily_earn_limit}LC")

        tx_id = f"tx_{self.account_id}_{int(time.time()*1000)}"
        tx = Transaction(
            tx_id=tx_id,
            from_account="system",
            to_account=self.account_id,
            amount=amount,
            tx_type=tx_type,
            description=description,
            metadata=metadata or {},
        )
        self.balance += amount
        self.total_earned += amount
        self._daily_earned += amount
        self.transactions.append(tx)
        self._check_achievements()
        return tx

    def spend(self, amount: float, tx_type: str = "spend_api",
              description: str = "", metadata: Optional[Dict] = None) -> Transaction:
        """支出"""
        if not self.can_spend(amount):
            raise ValueError(f"余额不足: {self.balance}LC < {amount}LC")

        tx_id = f"tx_{self.account_id}_{int(time.time()*1000)}"
        tx = Transaction(
            tx_id=tx_id,
            from_account=self.account_id,
            to_account="system",
            amount=-amount,
            tx_type=tx_type,
            description=description,
            metadata=metadata or {},
        )
        self.balance -= amount
        self.total_spent += amount
        self.transactions.append(tx)
        return tx

    def _check_achievements(self):
        """检查成就"""
        for ach in self.achievements:
            if ach.earned:
                continue
            earned = False
            if ach.id == "first_earn" and self.total_earned > 0:
                earned = True
            elif ach.id == "earn_100" and self.total_earned >= 100:
                earned = True
            elif ach.id == "earn_500" and self.total_earned >= 500:
                earned = True
            elif ach.id == "earn_1000" and self.total_earned >= 1000:
                earned = True
            elif ach.id == "level_5" and self.level >= 5:
                earned = True
            elif ach.id == "level_10" and self.level >= 10:
                earned = True

            if earned:
                ach.earned = True
                ach.earned_at = datetime.now().isoformat()
                logger.info(f"[龙虾币:{self.name}] 获得成就: {ach.icon} {ach.name}")

    def update_level(self):
        """更新等级"""
        self.level = int(self.total_earned / 100) + 1

    def to_dict(self) -> Dict:
        self.update_level()
        return {
            "account_id": self.account_id,
            "name": self.name,
            "balance": round(self.balance, 2),
            "total_earned": round(self.total_earned, 2),
            "total_spent": round(self.total_spent, 2),
            "level": self.level,
            "daily_earned": round(self._daily_earned, 2),
            "daily_limit": self.daily_earn_limit,
            "transaction_count": len(self.transactions),
            "achievements": [a.to_dict() for a in self.achievements if a.earned],
            "created_at": self.created_at,
        }


# ========== 默认成就 ==========

DEFAULT_ACHIEVEMENTS = [
    Achievement("first_earn", "第一桶金", "首次获得龙虾币", "💰", "赚取 > 0 LC"),
    Achievement("earn_100", "小有积蓄", "累计赚取 100 LC", "🪙", "累计赚取 ≥ 100 LC"),
    Achievement("earn_500", "龙虾富翁", "累计赚取 500 LC", "💎", "累计赚取 ≥ 500 LC"),
    Achievement("earn_1000", "龙虾大亨", "累计赚取 1000 LC", "👑", "累计赚取 ≥ 1000 LC"),
    Achievement("level_5", "资深学员", "达到 5 级", "⭐", "等级 ≥ 5"),
    Achievement("level_10", "龙虾大师", "达到 10 级", "🦞", "等级 ≥ 10"),
]

# 默认价格表
DEFAULT_PRICING = {
    "training_reward": 50.0,          # 完成训练奖励
    "api_call": 5.0,                  # API 调用费用
    "tool_call": 3.0,                 # 工具调用费用
    "storage_per_day": 1.0,           # 每日存储费用
    "task_complete": 30.0,            # 完成任务奖励
    "bonus_perfect": 20.0,            # 满分奖励
    "penalty_fail": 10.0,             # 失败惩罚
}


class LobsterCoin:
    """龙虾币经济系统"""

    def __init__(self, name: str = "lobster-network", storage_path: Optional[str] = None):
        self.name = name
        self._accounts: Dict[str, Account] = {}
        self._pricing = dict(DEFAULT_PRICING)
        self._storage_path = storage_path

        if storage_path:
            self._load()

        logger.info(f"[龙虾币:{self.name}] 初始化, 价格表: {len(self._pricing)} 项")

    def create_account(self, account_id: str, name: str,
                       initial_balance: float = 100.0) -> Account:
        """创建账户"""
        if account_id in self._accounts:
            return self._accounts[account_id]

        account = Account(
            account_id=account_id,
            name=name,
            balance=initial_balance,
            total_earned=initial_balance,
            achievements=[Achievement(**a.__dict__) if isinstance(a, Achievement) else a
                         for a in DEFAULT_ACHIEVEMENTS],
        )
        self._accounts[account_id] = account
        logger.info(f"[龙虾币:{self.name}] 创建账户: {name} (初始 {initial_balance}LC)")
        return account

    def get_account(self, account_id: str) -> Optional[Account]:
        """获取账户"""
        return self._accounts.get(account_id)

    def earn(self, account_id: str, amount: float, tx_type: str = "earn_training",
             description: str = "") -> Transaction:
        """收入"""
        account = self._accounts.get(account_id)
        if not account:
            raise ValueError(f"账户不存在: {account_id}")
        tx = account.earn(amount, tx_type, description)
        self._save()
        return tx

    def spend(self, account_id: str, amount: float, tx_type: str = "spend_api",
              description: str = "") -> Transaction:
        """支出"""
        account = self._accounts.get(account_id)
        if not account:
            raise ValueError(f"账户不存在: {account_id}")
        tx = account.spend(amount, tx_type, description)
        self._save()
        return tx

    def transfer(self, from_id: str, to_id: str, amount: float,
                 description: str = "") -> Transaction:
        """转账"""
        from_acc = self._accounts.get(from_id)
        to_acc = self._accounts.get(to_id)
        if not from_acc:
            raise ValueError(f"发送方账户不存在: {from_id}")
        if not to_acc:
            raise ValueError(f"接收方账户不存在: {to_id}")

        tx = from_acc.spend(amount, "transfer", f"转账给 {to_acc.name}: {description}")
        to_acc.earn(amount, "transfer", f"收到 {from_acc.name} 转账: {description}")
        tx.to_account = to_id
        self._save()
        return tx

    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """获取排行榜"""
        ranked = sorted(self._accounts.values(),
                       key=lambda a: a.total_earned, reverse=True)
        return [a.to_dict() for a in ranked[:top_n]]

    def get_economy_stats(self) -> Dict:
        """获取经济系统统计"""
        total_supply = sum(a.balance for a in self._accounts.values())
        total_earned = sum(a.total_earned for a in self._accounts.values())
        total_spent = sum(a.total_spent for a in self._accounts.values())

        return {
            "name": self.name,
            "total_accounts": len(self._accounts),
            "total_supply": round(total_supply, 2),
            "total_earned": round(total_earned, 2),
            "total_spent": round(total_spent, 2),
            "circulating": round(total_earned - total_spent, 2),
            "pricing": self._pricing,
        }

    def set_pricing(self, key: str, value: float):
        """设置价格"""
        self._pricing[key] = value

    def _save(self):
        """持久化"""
        if not self._storage_path:
            return
        try:
            data = {
                "name": self.name,
                "saved_at": datetime.now().isoformat(),
                "accounts": {k: v.to_dict() for k, v in self._accounts.items()},
                "pricing": self._pricing,
            }
            Path(self._storage_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[龙虾币:{self.name}] 保存失败: {e}")

    def _load(self):
        """加载"""
        if not self._storage_path:
            return
        try:
            path = Path(self._storage_path)
            if not path.exists():
                return
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k, v in data.get("accounts", {}).items():
                account = Account(
                    account_id=v["account_id"],
                    name=v["name"],
                    balance=v.get("balance", 0),
                    total_earned=v.get("total_earned", 0),
                    total_spent=v.get("total_spent", 0),
                    created_at=v.get("created_at", ""),
                    level=v.get("level", 1),
                )
                self._accounts[k] = account
            self._pricing = data.get("pricing", dict(DEFAULT_PRICING))
            logger.info(f"[龙虾币:{self.name}] 加载 {len(self._accounts)} 个账户")
        except Exception as e:
            logger.warning(f"[龙虾币:{self.name}] 加载失败: {e}")


# ========== 预定义实例 ==========

# 主经济系统
main_economy = LobsterCoin(
    name="lobster-network",
    storage_path=None,  # 按需设置路径
)

# 预创建学员账户
def init_student_accounts(economy: Optional[LobsterCoin] = None):
    """初始化学员账户（空投初始资金）"""
    econ = economy or main_economy
    students = [
        ("xiaochen", "小陈（稳健型）", 100),
        ("zhuguxia", "诸葛虾（加速型）", 100),
        ("zhugema", "诸葛马（教练型）", 200),
        ("qoder", "Qoder（实战型）", 100),
    ]
    for account_id, name, balance in students:
        econ.create_account(account_id, name, balance)
    return econ


# 便捷函数
def student_earn(account_id: str, amount: Optional[float] = None,
                 description: str = "") -> Transaction:
    """学员训练收入"""
    amount = amount or main_economy._pricing.get("training_reward", 50)
    return main_economy.earn(account_id, amount, "earn_training", description)


def api_cost(account_id: str, description: str = "") -> Transaction:
    """API 调用支出"""
    cost = main_economy._pricing.get("api_call", 5)
    return main_economy.spend(account_id, cost, "spend_api", description)
