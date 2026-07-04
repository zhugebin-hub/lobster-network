#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙虾币 (LBC) 经济系统 — 完整实现

核心组件：
- LBCWallet:       钱包（余额、交易记录、冻结金额）
- SDPPricing:      SDP 定价引擎  P = P_base × D_factor × Q_premium × U_discount
- TransactionLedger: 交易账本（不可变，追加写入）
- MarketOrderBook:  技能市场挂单（买/卖双向，撮合引擎）
- RewardDistributor: 奖励分配（解题/对局/贡献奖励）

初始分配：
  xiaochen: 100 LBC
  zhuguxia: 100 LBC
  qoder: 100 LBC
  hermes(教练): 500 LBC
  系统池: 1000 LBC

参考：小龙虾生态_v3.1补充_Agent劳务市场与经济模型
"""

import json
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock


# ============================================================
# 日志与存储
# ============================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("lbc_economy")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(DATA_DIR / "economy.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_handler)


# ============================================================
# 初始分配
# ============================================================

INITIAL_ALLOCATIONS = {
    "xiaochen": 100.0,
    "zhuguxia": 100.0,
    "qoder": 100.0,
    "hermes": 500.0,
    "system_pool": 1000.0,
}

# 技能基础定价（LBC）
SKILL_BASE_PRICES = {
    "document": 5.0,      # 文档类（撰写/分析/翻译）
    "code": 8.0,          # 编程类
    "design": 6.0,        # 设计类（海报/PPT）
    "data_analysis": 10.0, # 数据分析
    "teaching": 7.0,      # 教学辅导
    "research": 12.0,     # 研究类
    "consulting": 15.0,   # 咨询类
    "coaching": 20.0,     # 教练类
    "routing": 3.0,       # 路由/编排
    "basic": 2.0,         # 基础任务
}


# ============================================================
# 枚举与数据模型
# ============================================================

class OrderType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    OPEN = "open"
    PARTIAL = "partial"
    FILLED = "filled"
    CANCELLED = "cancelled"


@dataclass
class Transaction:
    """交易记录（不可变结构）"""
    tx_id: str
    timestamp: str
    from_account: str
    to_account: str
    amount: float
    skill: str = ""
    description: str = ""
    tx_hash: str = ""

    def compute_hash(self) -> str:
        """计算交易哈希（确保不可篡改）"""
        raw = f"{self.tx_id}|{self.timestamp}|{self.from_account}|{self.to_account}|{self.amount}|{self.skill}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def verify(self) -> bool:
        """验证交易完整性"""
        return self.compute_hash() == self.tx_hash


@dataclass
class Order:
    """市场挂单"""
    order_id: str
    account: str
    order_type: OrderType
    skill: str
    amount: float        # 单价
    quantity: int = 1
    filled: int = 0
    status: OrderStatus = OrderStatus.OPEN
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# LBCWallet — 钱包管理
# ============================================================

class LBCWallet:
    """
    龙虾币钱包

    功能：余额查询、转账、冻结/解冻、交易记录
    """

    def __init__(self, owner_id: str, initial_balance: float = 0.0):
        self.owner_id = owner_id
        self._balance = initial_balance
        self._frozen = 0.0
        self._transactions: List[Transaction] = []
        self._lock = Lock()

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def available(self) -> float:
        return self._balance - self._frozen

    @property
    def frozen(self) -> float:
        return self._frozen

    def can_spend(self, amount: float) -> bool:
        """检查是否有足够可用余额"""
        return self.available >= amount

    def deposit(self, amount: float) -> bool:
        """入账"""
        if amount <= 0:
            return False
        with self._lock:
            self._balance += amount
        logger.info(f"[{self.owner_id}] 入账 +{amount:.2f} LBC | 余额 {self._balance:.2f}")
        return True

    def withdraw(self, amount: float) -> bool:
        """出账"""
        if amount <= 0:
            return False
        with self._lock:
            if self.available < amount:
                logger.warning(f"[{self.owner_id}] 余额不足: 需要 {amount:.2f}, 可用 {self.available:.2f}")
                return False
            self._balance -= amount
        logger.info(f"[{self.owner_id}] 出账 -{amount:.2f} LBC | 余额 {self._balance:.2f}")
        return True

    def freeze(self, amount: float) -> bool:
        """冻结金额（用于挂单/合约）"""
        if amount <= 0:
            return False
        with self._lock:
            if self.available < amount:
                return False
            self._frozen += amount
        return True

    def unfreeze(self, amount: float) -> bool:
        """解冻金额"""
        if amount <= 0:
            return False
        with self._lock:
            if self._frozen < amount:
                return False
            self._frozen -= amount
        return True

    def add_transaction(self, tx: Transaction):
        """添加交易记录"""
        if not tx.tx_hash:
            tx.tx_hash = tx.compute_hash()
        self._transactions.append(tx)

    def get_transactions(self, last_n: int = 50) -> List[Transaction]:
        """获取最近交易记录"""
        return self._transactions[-last_n:]

    def to_dict(self) -> dict:
        return {
            "owner_id": self.owner_id,
            "balance": self._balance,
            "frozen": self._frozen,
            "available": self.available,
            "transaction_count": len(self._transactions),
        }


# ============================================================
# SDPPricing — SDP 定价引擎
# ============================================================

class SDPPricing:
    """
    SDP (Software-Defined Pricing) 定价引擎

    公式：P(skill) = P_base × D_factor × Q_premium × U_discount

    参数:
      P_base:      基础价（技能类别决定）
      D_factor:    需求因子（市场供需，默认 1.0）
      Q_premium:   质量溢价（评价分 / 5.0，范围 0.6-1.4）
      U_discount:  紧迫度折扣（正常 1.0 / 加急 1.5）
    """

    def __init__(self):
        self._demand_history: Dict[str, List[float]] = {}
        self._quality_scores: Dict[str, float] = {}

    def set_quality_score(self, agent_id: str, score: float):
        """设置 Agent 质量评分（0-5）"""
        self._quality_scores[agent_id] = max(0.0, min(5.0, score))

    def get_quality_score(self, agent_id: str) -> float:
        return self._quality_scores.get(agent_id, 4.0)  # 默认 4.0

    def record_demand(self, skill: str, price: float):
        """记录市场需求"""
        if skill not in self._demand_history:
            self._demand_history[skill] = []
        self._demand_history[skill].append(price)
        if len(self._demand_history[skill]) > 100:
            self._demand_history[skill].pop(0)

    def compute_demand_factor(self, skill: str) -> float:
        """
        计算需求因子 D_factor

        基于近期交易价格均值与基准价的比值。
        """
        if skill not in self._demand_history or not self._demand_history[skill]:
            return 1.0
        avg_price = sum(self._demand_history[skill]) / len(self._demand_history[skill])
        base_price = SKILL_BASE_PRICES.get(skill, 5.0)
        if base_price == 0:
            return 1.0
        return min(3.0, max(0.3, avg_price / base_price))

    def price(
        self,
        skill: str,
        agent_id: str = "",
        urgent: bool = False,
    ) -> float:
        """
        计算技能定价

        P(skill) = P_base × D_factor × Q_premium × U_discount

        参数:
          skill:     技能类别
          agent_id:  服务提供者 ID
          urgent:    是否加急
        """
        p_base = SKILL_BASE_PRICES.get(skill, 5.0)
        d_factor = self.compute_demand_factor(skill)
        q_score = self.get_quality_score(agent_id) if agent_id else 4.0
        q_premium = q_score / 5.0  # 0.6-1.4 范围
        u_discount = 1.5 if urgent else 1.0

        price = p_base * d_factor * q_premium * u_discount

        logger.debug(
            f"SDP 定价: skill={skill} | P_base={p_base:.1f} × "
            f"D={d_factor:.2f} × Q={q_premium:.2f} × U={u_discount:.1f} = {price:.2f} LBC"
        )
        return round(price, 2)

    def estimate(self, skill: str, agent_id: str = "", urgent: bool = False) -> dict:
        """返回定价明细"""
        p_base = SKILL_BASE_PRICES.get(skill, 5.0)
        d_factor = self.compute_demand_factor(skill)
        q_score = self.get_quality_score(agent_id) if agent_id else 4.0
        q_premium = q_score / 5.0
        u_discount = 1.5 if urgent else 1.0
        total = round(p_base * d_factor * q_premium * u_discount, 2)

        return {
            "skill": skill,
            "agent_id": agent_id or "N/A",
            "p_base": p_base,
            "d_factor": round(d_factor, 2),
            "q_premium": round(q_premium, 2),
            "u_discount": u_discount,
            "total_lbc": total,
            "urgent": urgent,
        }


# ============================================================
# TransactionLedger — 交易账本
# ============================================================

class TransactionLedger:
    """
    交易账本 — 不可变追加写入

    所有交易通过本账本记录，确保完整审计轨迹。
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or (DATA_DIR / "ledger.jsonl")
        self._transactions: List[Transaction] = []
        self._tx_counter = 0
        self._lock = Lock()

        # 从文件恢复
        self._load()

    def _load(self):
        """从 JSONL 恢复账本"""
        if self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            tx = Transaction(**data)
                            self._transactions.append(tx)
                            self._tx_counter = max(self._tx_counter, int(tx.tx_id.split("_")[-1]))
                        except (json.JSONDecodeError, TypeError):
                            pass
            logger.info(f"账本恢复: {len(self._transactions)} 条交易")

    def record(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        skill: str = "",
        description: str = "",
    ) -> Transaction:
        """记录一笔交易（不可变追加）"""
        with self._lock:
            self._tx_counter += 1
            tx = Transaction(
                tx_id=f"TX_{self._tx_counter:06d}",
                timestamp=datetime.now().isoformat(),
                from_account=from_account,
                to_account=to_account,
                amount=round(amount, 2),
                skill=skill,
                description=description,
            )
            tx.tx_hash = tx.compute_hash()
            self._transactions.append(tx)

            # 追加写入 JSONL
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({
                    "tx_id": tx.tx_id,
                    "timestamp": tx.timestamp,
                    "from_account": tx.from_account,
                    "to_account": tx.to_account,
                    "amount": tx.amount,
                    "skill": tx.skill,
                    "description": tx.description,
                    "tx_hash": tx.tx_hash,
                }, ensure_ascii=False) + "\n")

            logger.info(f"交易记录: {tx.tx_id} | {from_account} -> {to_account} | {amount:.2f} LBC")
            return tx

    def get_by_account(self, account: str, last_n: int = 50) -> List[Transaction]:
        """查询某账户相关交易"""
        result = []
        for tx in reversed(self._transactions):
            if tx.from_account == account or tx.to_account == account:
                result.append(tx)
                if len(result) >= last_n:
                    break
        return list(reversed(result))

    def get_all(self, last_n: int = 100) -> List[Transaction]:
        return self._transactions[-last_n:]

    def verify_all(self) -> Tuple[int, int]:
        """验证全部交易完整性，返回 (通过, 失败)"""
        passed, failed = 0, 0
        for tx in self._transactions:
            if tx.verify():
                passed += 1
            else:
                failed += 1
        return passed, failed

    @property
    def total_transactions(self) -> int:
        return len(self._transactions)

    @property
    def total_volume(self) -> float:
        return sum(tx.amount for tx in self._transactions)


# ============================================================
# MarketOrderBook — 技能市场挂单
# ============================================================

class MarketOrderBook:
    """
    技能市场挂单簿 — 双向撮合引擎

    支持买单和卖单，自动撮合匹配。
    """

    def __init__(self):
        self._orders: Dict[str, Order] = {}
        self._order_counter = 0
        self._lock = Lock()

    def place_order(
        self,
        account: str,
        order_type: OrderType,
        skill: str,
        amount: float,
        quantity: int = 1,
    ) -> Order:
        """挂单"""
        with self._lock:
            self._order_counter += 1
            order = Order(
                order_id=f"ORD_{self._order_counter:06d}",
                account=account,
                order_type=order_type,
                skill=skill,
                amount=amount,
                quantity=quantity,
            )
            self._orders[order.order_id] = order
            logger.info(f"挂单: {order.order_id} | {account} {order_type.value} {skill} ×{quantity} @{amount:.2f}")
            return order

    def cancel_order(self, order_id: str) -> bool:
        """撤单"""
        with self._lock:
            order = self._orders.get(order_id)
            if not order or order.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
                return False
            order.status = OrderStatus.CANCELLED
            logger.info(f"撤单: {order_id}")
            return True

    def match(self, skill: str) -> List[Tuple[Order, Order, int]]:
        """
        撮合引擎：匹配同一技能下的买单和卖单。

        返回 [(buy_order, sell_order, match_quantity), ...]
        """
        with self._lock:
            buys = [o for o in self._orders.values()
                    if o.skill == skill and o.order_type == OrderType.BUY and o.status == OrderStatus.OPEN]
            sells = [o for o in self._orders.values()
                     if o.skill == skill and o.order_type == OrderType.SELL and o.status == OrderStatus.OPEN]

            # 买单高价优先，卖单低价优先
            buys.sort(key=lambda o: o.amount, reverse=True)
            sells.sort(key=lambda o: o.amount)

            matches = []
            for buy in buys:
                for sell in sells:
                    if buy.amount >= sell.amount:
                        # 可成交
                        buy_remaining = buy.quantity - buy.filled
                        sell_remaining = sell.quantity - sell.filled
                        match_qty = min(buy_remaining, sell_remaining)
                        if match_qty > 0:
                            buy.filled += match_qty
                            sell.filled += match_qty
                            buy.status = OrderStatus.FILLED if buy.filled >= buy.quantity else OrderStatus.PARTIAL
                            sell.status = OrderStatus.FILLED if sell.filled >= sell.quantity else OrderStatus.PARTIAL
                            matches.append((buy, sell, match_qty))
                            logger.info(f"撮合: {buy.order_id} ↔ {sell.order_id} | {skill} ×{match_qty} @{sell.amount:.2f}")

            return matches

    def get_open_orders(self, skill: Optional[str] = None) -> List[Order]:
        """获取所有开放订单"""
        result = [o for o in self._orders.values() if o.status == OrderStatus.OPEN]
        if skill:
            result = [o for o in result if o.skill == skill]
        return result

    def get_order_book_snapshot(self, skill: str) -> dict:
        """获取某个技能的市场深度"""
        buys = [o for o in self._orders.values()
                if o.skill == skill and o.order_type == OrderType.BUY and o.status == OrderStatus.OPEN]
        sells = [o for o in self._orders.values()
                 if o.skill == skill and o.order_type == OrderType.SELL and o.status == OrderStatus.OPEN]
        return {
            "skill": skill,
            "bids": sorted([{"price": o.amount, "quantity": o.quantity - o.filled} for o in buys], key=lambda x: x["price"], reverse=True),
            "asks": sorted([{"price": o.amount, "quantity": o.quantity - o.filled} for o in sells], key=lambda x: x["price"]),
        }


# ============================================================
# RewardDistributor — 奖励分配
# ============================================================

class RewardDistributor:
    """
    奖励分配器

    三种奖励类型：
    - 解题奖励：每答对一题奖励
    - 对局奖励：每完成一局奖励
    - 贡献奖励：额外贡献（代码/文档/教学）
    """

    REWARD_TABLE = {
        "problem_solve": {"easy": 0.5, "medium": 1.0, "hard": 2.0},
        "game_play": {"win": 3.0, "draw": 1.0, "loss": 0.2},
        "contribution": {"code": 5.0, "document": 3.0, "teaching": 4.0, "review": 2.0},
    }

    def __init__(self, system_pool_wallet: LBCWallet):
        self.system_pool = system_pool_wallet

    def reward_problem(self, agent_id: str, difficulty: str, wallet: LBCWallet) -> float:
        """解题奖励"""
        reward = self.REWARD_TABLE["problem_solve"].get(difficulty, 1.0)
        if self.system_pool.withdraw(reward):
            wallet.deposit(reward)
            logger.info(f"解题奖励: {agent_id} +{reward:.2f} LBC ({difficulty})")
            return reward
        return 0.0

    def reward_game(self, agent_id: str, result: str, wallet: LBCWallet) -> float:
        """对局奖励"""
        reward = self.REWARD_TABLE["game_play"].get(result, 0.2)
        if self.system_pool.withdraw(reward):
            wallet.deposit(reward)
            logger.info(f"对局奖励: {agent_id} +{reward:.2f} LBC ({result})")
            return reward
        return 0.0

    def reward_contribution(self, agent_id: str, contrib_type: str, wallet: LBCWallet) -> float:
        """贡献奖励"""
        reward = self.REWARD_TABLE["contribution"].get(contrib_type, 2.0)
        if self.system_pool.withdraw(reward):
            wallet.deposit(reward)
            logger.info(f"贡献奖励: {agent_id} +{reward:.2f} LBC ({contrib_type})")
            return reward
        return 0.0


# ============================================================
# LBCEconomy 主类 — 经济系统统一入口
# ============================================================

class LBCEconomy:
    """
    龙虾币经济系统统一入口

    用法:
        economy = LBCEconomy()
        economy.initialize()

        # 转账
        economy.transfer("xiaochen", "qoder", 15.0, skill="teaching")

        # 定价
        price = economy.pricing.price("data_analysis", agent_id="hermes", urgent=True)

        # 挂单撮合
        economy.order_book.place_order("xiaochen", OrderType.SELL, "code", 8.0, quantity=3)
        economy.order_book.place_order("qoder", OrderType.BUY, "code", 10.0, quantity=2)
        matches = economy.order_book.match("code")

        # 奖励
        economy.reward_distributor.reward_problem("xiaochen", "hard", economy.get_wallet("xiaochen"))
    """

    def __init__(self):
        self.wallets: Dict[str, LBCWallet] = {}
        self.pricing = SDPPricing()
        self.ledger = TransactionLedger()
        self.order_book = MarketOrderBook()
        self.reward_distributor: Optional[RewardDistributor] = None

    def initialize(self, allocations: Optional[dict] = None):
        """
        初始化经济系统。

        按初始分配方案创建钱包。
        """
        alloc = allocations or INITIAL_ALLOCATIONS
        for account, balance in alloc.items():
            self.wallets[account] = LBCWallet(account, initial_balance=balance)

        # 设置初始评分
        self.pricing.set_quality_score("hermes", 5.0)
        self.pricing.set_quality_score("qoder", 4.2)
        self.pricing.set_quality_score("zhuguxia", 3.8)
        self.pricing.set_quality_score("xiaochen", 3.5)

        # 初始化奖励分配器
        system_pool = self.wallets.get("system_pool")
        if system_pool:
            self.reward_distributor = RewardDistributor(system_pool)

        logger.info(f"经济系统初始化: {len(self.wallets)} 个钱包, 总发行 {sum(w.balance for w in self.wallets.values()):.0f} LBC")

    def get_wallet(self, account: str) -> Optional[LBCWallet]:
        """获取钱包"""
        return self.wallets.get(account)

    def get_or_create_wallet(self, account: str, initial: float = 0.0) -> LBCWallet:
        """获取或创建钱包"""
        if account not in self.wallets:
            self.wallets[account] = LBCWallet(account, initial_balance=initial)
        return self.wallets[account]

    def transfer(
        self,
        from_account: str,
        to_account: str,
        amount: float,
        skill: str = "",
        description: str = "",
    ) -> bool:
        """
        转账：from -> to，amount LBC

        返回是否成功。
        """
        from_wallet = self.get_wallet(from_account)
        to_wallet = self.get_wallet(to_account)

        if not from_wallet:
            logger.error(f"转账失败: 付款方 [{from_account}] 不存在")
            return False
        if not to_wallet:
            logger.error(f"转账失败: 收款方 [{to_account}] 不存在")
            return False

        if not from_wallet.withdraw(amount):
            return False

        to_wallet.deposit(amount)

        # 记录账本
        tx = self.ledger.record(from_account, to_account, amount, skill=skill, description=description)
        from_wallet.add_transaction(tx)
        to_wallet.add_transaction(tx)

        # 记录市场需求
        if skill:
            self.pricing.record_demand(skill, amount)

        return True

    def get_all_balances(self) -> dict:
        """获取所有账户余额"""
        return {account: wallet.to_dict() for account, wallet in self.wallets.items()}

    def get_total_supply(self) -> float:
        """总发行量"""
        return sum(w.balance for w in self.wallets.values())

    def get_market_summary(self) -> dict:
        """市场概况"""
        return {
            "total_transactions": self.ledger.total_transactions,
            "total_volume": round(self.ledger.total_volume, 2),
            "open_orders": len(self.order_book.get_open_orders()),
            "total_wallets": len(self.wallets),
            "total_supply": round(self.get_total_supply(), 2),
        }
