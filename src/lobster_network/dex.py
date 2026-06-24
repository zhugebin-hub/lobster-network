#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络去中心化交易所 (DEX) V2.2
基于 AMM 自动做市商

功能：
1. 交易对管理
2. 流动性提供/移除
3. Token 兑换
4. 手续费分配
5. 价格预言机
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .token_economy import TokenEconomy


# ========== 常量定义 ==========

# 交易手续费
TRADING_FEE = 0.003  # 0.3%
LIQUIDITY_FEE = 0.0005  # 0.05% 流动性提供者手续费
PROTOCOL_FEE = 0.0005  # 0.05% 协议手续费

# 滑点保护
MAX_SLIPPAGE = 0.05  # 最大滑点 5%


# ========== 数据类定义 ==========

@dataclass
class TradingPair:
    """交易对"""
    pair_id: str
    token_a: str
    token_b: str
    reserve_a: float = 0.0
    reserve_b: float = 0.0
    total_shares: float = 0.0
    fees_a: float = 0.0
    fees_b: float = 0.0
    volume_24h: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def price(self) -> float:
        """计算价格 (token_b / token_a)"""
        if self.reserve_a == 0:
            return 0
        return self.reserve_b / self.reserve_a

    @property
    def tvl(self) -> float:
        """计算总锁仓价值"""
        return self.reserve_a + self.reserve_b * self.price

    def to_dict(self) -> dict:
        return {
            "pair_id": self.pair_id,
            "token_a": self.token_a,
            "token_b": self.token_b,
            "reserve_a": self.reserve_a,
            "reserve_b": self.reserve_b,
            "total_shares": self.total_shares,
            "fees_a": self.fees_a,
            "fees_b": self.fees_b,
            "volume_24h": self.volume_24h,
            "price": self.price,
            "tvl": self.tvl,
            "created_at": self.created_at,
        }


@dataclass
class LiquidityPosition:
    """流动性头寸"""
    position_id: str
    pair_id: str
    provider_id: str
    shares: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "position_id": self.position_id,
            "pair_id": self.pair_id,
            "provider_id": self.provider_id,
            "shares": self.shares,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Trade:
    """交易记录"""
    trade_id: str
    pair_id: str
    trader_id: str
    from_token: str
    to_token: str
    amount_in: float
    amount_out: float
    fee: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "trade_id": self.trade_id,
            "pair_id": self.pair_id,
            "trader_id": self.trader_id,
            "from_token": self.from_token,
            "to_token": self.to_token,
            "amount_in": self.amount_in,
            "amount_out": self.amount_out,
            "fee": self.fee,
            "timestamp": self.timestamp,
        }


# ========== DEX 系统 ==========

class DEX:
    """去中心化交易所"""

    def __init__(self, token_economy: TokenEconomy, data_dir: str = "/shared/lobster-network-data/dex"):
        self.token_economy = token_economy
        self.data_dir = data_dir
        self.trading_pairs: Dict[str, TradingPair] = {}
        self.liquidity_positions: Dict[str, LiquidityPosition] = {}
        self.trades: List[Trade] = []
        self._pair_counter = 0
        self._position_counter = 0
        self._trade_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 交易对管理 ==========

    def create_pair(
        self,
        token_a: str,
        token_b: str,
        initial_a: float = 1000.0,
        initial_b: float = 1000.0,
    ) -> Tuple[bool, str]:
        """创建交易对"""
        self._pair_counter += 1
        pair_id = f"pair-{self._pair_counter:04d}"

        pair = TradingPair(
            pair_id=pair_id,
            token_a=token_a,
            token_b=token_b,
            reserve_a=initial_a,
            reserve_b=initial_b,
            total_shares=initial_a,  # 初始份额
        )
        self.trading_pairs[pair_id] = pair

        return True, f"交易对 {pair_id} 创建成功 ({token_a}/{token_b})"

    def get_pair(self, pair_id: str) -> Optional[TradingPair]:
        """获取交易对"""
        return self.trading_pairs.get(pair_id)

    def get_pair_by_tokens(self, token_a: str, token_b: str) -> Optional[TradingPair]:
        """根据 token 获取交易对"""
        for pair in self.trading_pairs.values():
            if (pair.token_a == token_a and pair.token_b == token_b) or \
               (pair.token_a == token_b and pair.token_b == token_a):
                return pair
        return None

    # ========== 流动性管理 ==========

    def add_liquidity(
        self,
        pair_id: str,
        provider_id: str,
        amount_a: float,
        amount_b: float,
    ) -> Tuple[bool, str]:
        """添加流动性"""
        pair = self.trading_pairs.get(pair_id)
        if not pair:
            return False, f"交易对 {pair_id} 不存在"

        # 计算份额
        if pair.reserve_a == 0:
            shares = amount_a
        else:
            # 按当前比例计算
            optimal_b = amount_a * pair.reserve_b / pair.reserve_a
            if amount_b < optimal_b:
                # token_b 不足，按 token_b 计算
                shares = amount_b * pair.total_shares / pair.reserve_b
                amount_a = shares * pair.reserve_a / pair.total_shares
            else:
                shares = amount_a * pair.total_shares / pair.reserve_a

        # 更新储备
        pair.reserve_a += amount_a
        pair.reserve_b += amount_b
        pair.total_shares += shares

        # 创建流动性头寸
        self._position_counter += 1
        position_id = f"position-{self._position_counter:06d}"

        # 查找是否已有头寸
        existing_position = None
        for pos in self.liquidity_positions.values():
            if pos.pair_id == pair_id and pos.provider_id == provider_id:
                existing_position = pos
                break

        if existing_position:
            existing_position.shares += shares
            existing_position.updated_at = datetime.now().isoformat()
        else:
            position = LiquidityPosition(
                position_id=position_id,
                pair_id=pair_id,
                provider_id=provider_id,
                shares=shares,
            )
            self.liquidity_positions[position_id] = position

        return True, f"添加流动性成功，获得 {shares:.4f} 份额"

    def remove_liquidity(
        self,
        pair_id: str,
        provider_id: str,
        shares: float,
    ) -> Tuple[bool, str, float, float]:
        """移除流动性"""
        pair = self.trading_pairs.get(pair_id)
        if not pair:
            return False, f"交易对 {pair_id} 不存在", 0, 0

        # 查找头寸
        position = None
        for pos in self.liquidity_positions.values():
            if pos.pair_id == pair_id and pos.provider_id == provider_id:
                position = pos
                break

        if not position:
            return False, f"头寸不存在", 0, 0

        if position.shares < shares:
            return False, f"份额不足: {position.shares} < {shares}", 0, 0

        # 计算返还金额
        amount_a = shares * pair.reserve_a / pair.total_shares
        amount_b = shares * pair.reserve_b / pair.total_shares

        # 更新储备
        pair.reserve_a -= amount_a
        pair.reserve_b -= amount_b
        pair.total_shares -= shares
        position.shares -= shares

        return True, f"移除流动性成功: {amount_a:.4f} {pair.token_a} + {amount_b:.4f} {pair.token_b}", amount_a, amount_b

    # ========== Token 兑换 ==========

    def swap(
        self,
        pair_id: str,
        trader_id: str,
        from_token: str,
        to_token: str,
        amount_in: float,
        min_amount_out: float = 0,
    ) -> Tuple[bool, str, float]:
        """兑换 token"""
        pair = self.trading_pairs.get(pair_id)
        if not pair:
            return False, f"交易对 {pair_id} 不存在", 0

        # 检查 token 对
        if from_token == pair.token_a and to_token == pair.token_b:
            reserve_in = pair.reserve_a
            reserve_out = pair.reserve_b
        elif from_token == pair.token_b and to_token == pair.token_a:
            reserve_in = pair.reserve_b
            reserve_out = pair.reserve_a
        else:
            return False, f"不支持的 token 对: {from_token}/{to_token}", 0

        # 计算兑换数量（AMM 公式）
        amount_with_fee = amount_in * (1 - TRADING_FEE)
        amount_out = (amount_with_fee * reserve_out) / (reserve_in + amount_with_fee)

        # 检查滑点
        if min_amount_out > 0 and amount_out < min_amount_out:
            return False, f"滑点过大: {amount_out} < {min_amount_out}", 0

        # 检查余额
        trader_balance = self.token_economy.get_balance(trader_id)
        if trader_balance < amount_in:
            return False, f"余额不足: {trader_balance} < {amount_in}", 0

        # 执行兑换
        self.token_economy.transfer(trader_id, "dex_pool", amount_in)
        self.token_economy.transfer("dex_pool", trader_id, amount_out)

        # 更新储备
        if from_token == pair.token_a:
            pair.reserve_a += amount_in
            pair.reserve_b -= amount_out
        else:
            pair.reserve_b += amount_in
            pair.reserve_a -= amount_out

        # 更新 24h 交易量
        pair.volume_24h += amount_in

        # 计算手续费
        fee = amount_in * TRADING_FEE
        liquidity_fee = amount_in * LIQUIDITY_FEE
        protocol_fee = amount_in * PROTOCOL_FEE

        # 分配手续费
        pair.fees_a += liquidity_fee if from_token == pair.token_a else 0
        pair.fees_b += liquidity_fee if from_token == pair.token_b else 0

        # 记录交易
        self._trade_counter += 1
        trade = Trade(
            trade_id=f"trade-{self._trade_counter:06d}",
            pair_id=pair_id,
            trader_id=trader_id,
            from_token=from_token,
            to_token=to_token,
            amount_in=amount_in,
            amount_out=amount_out,
            fee=fee,
        )
        self.trades.append(trade)

        return True, f"兑换成功: {amount_in} {from_token} → {amount_out:.6f} {to_token}", amount_out

    # ========== 价格预言机 ==========

    def get_price(self, pair_id: str) -> float:
        """获取价格"""
        pair = self.trading_pairs.get(pair_id)
        return pair.price if pair else 0

    def get_price_impact(self, pair_id: str, from_token: str, amount_in: float) -> float:
        """计算价格影响"""
        pair = self.trading_pairs.get(pair_id)
        if not pair:
            return 0

        if from_token == pair.token_a:
            reserve_in = pair.reserve_a
            reserve_out = pair.reserve_b
        elif from_token == pair.token_b:
            reserve_in = pair.reserve_b
            reserve_out = pair.reserve_a
        else:
            return 0

        if reserve_in == 0:
            return 0

        # 价格影响 = 交易金额 / 储备量
        return amount_in / reserve_in

    # ========== 查询功能 ==========

    def get_all_pairs(self) -> List[Dict]:
        """获取所有交易对"""
        return [p.to_dict() for p in self.trading_pairs.values()]

    def get_liquidity_positions(self, provider_id: str) -> List[Dict]:
        """获取流动性头寸"""
        positions = [
            p.to_dict() for p in self.liquidity_positions.values()
            if p.provider_id == provider_id
        ]
        return positions

    def get_recent_trades(self, limit: int = 20) -> List[Dict]:
        """获取最近交易"""
        return [t.to_dict() for t in self.trades[-limit:]]

    def get_dex_statistics(self) -> Dict:
        """获取 DEX 统计"""
        total_tvl = sum(p.tvl for p in self.trading_pairs.values())
        total_volume_24h = sum(p.volume_24h for p in self.trading_pairs.values())

        return {
            "total_pairs": len(self.trading_pairs),
            "total_positions": len(self.liquidity_positions),
            "total_trades": len(self.trades),
            "total_tvl": total_tvl,
            "volume_24h": total_volume_24h,
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "trading_pairs": {pid: p.to_dict() for pid, p in self.trading_pairs.items()},
            "liquidity_positions": {pid: p.to_dict() for pid, p in self.liquidity_positions.items()},
            "trades": [t.to_dict() for t in self.trades],
            "counters": {
                "pair": self._pair_counter,
                "position": self._position_counter,
                "trade": self._trade_counter,
            },
        }
        with open(os.path.join(self.data_dir, "dex_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "dex_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.trading_pairs = {pid: TradingPair(**p) for pid, p in data.get("trading_pairs", {}).items()}
            self.liquidity_positions = {pid: LiquidityPosition(**p) for pid, p in data.get("liquidity_positions", {}).items()}
            self.trades = [Trade(**t) for t in data.get("trades", [])]

            counters = data.get("counters", {})
            self._pair_counter = counters.get("pair", 0)
            self._position_counter = counters.get("position", 0)
            self._trade_counter = counters.get("trade", 0)

            return True
        return False
