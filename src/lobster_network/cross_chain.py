#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络跨链交易系统 V2.1
支持多链 token 交换

功能：
1. 跨链 token 交换
2. 流动性池
3. 汇率计算
4. 跨链桥
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ========== 常量定义 ==========

# 链类型
CHAIN_TYPE_LOBSTER = "lobster"       # 小龙虾链
CHAIN_TYPE_BITCOIN = "bitcoin"       # 比特币链
CHAIN_TYPE_ETHEREUM = "ethereum"     # 以太坊链
CHAIN_TYPE_SOLANA = "solana"         # Solana 链

# 跨链状态
CROSS_CHAIN_STATUS_PENDING = "pending"      # 待处理
CROSS_CHAIN_STATUS_LOCKING = "locking"      # 锁定中
CROSS_CHAIN_STATUS_LOCKED = "locked"        # 已锁定
CROSS_CHAIN_STATUS_MINTING = "minting"      # 铸造中
CROSS_CHAIN_STATUS_MINTED = "minted"        # 已铸造
CROSS_CHAIN_STATUS_COMPLETED = "completed"  # 已完成
CROSS_CHAIN_STATUS_FAILED = "failed"        # 失败


# ========== 数据类定义 ==========

@dataclass
class LiquidityPool:
    """流动性池"""
    pool_id: str
    token_a: str
    token_b: str
    reserve_a: float = 0.0
    reserve_b: float = 0.0
    total_shares: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def price(self) -> float:
        """计算价格"""
        if self.reserve_a == 0:
            return 0
        return self.reserve_b / self.reserve_a

    def to_dict(self) -> dict:
        return {
            "pool_id": self.pool_id,
            "token_a": self.token_a,
            "token_b": self.token_b,
            "reserve_a": self.reserve_a,
            "reserve_b": self.reserve_b,
            "total_shares": self.total_shares,
            "price": self.price,
            "created_at": self.created_at,
        }


@dataclass
class CrossChainTransaction:
    """跨链交易"""
    tx_id: str
    from_chain: str
    to_chain: str
    from_address: str
    to_address: str
    amount: float
    token: str
    status: str = CROSS_CHAIN_STATUS_PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "from_chain": self.from_chain,
            "to_chain": self.to_chain,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "token": self.token,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }


@dataclass
class BridgeNode:
    """桥接节点"""
    node_id: str
    name: str
    chains: List[str]
    status: str = "active"
    total_volume: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "chains": self.chains,
            "status": self.status,
            "total_volume": self.total_volume,
            "created_at": self.created_at,
        }


# ========== 跨链交易系统 ==========

class CrossChainSystem:
    """跨链交易系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/cross-chain"):
        self.data_dir = data_dir
        self.pools: Dict[str, LiquidityPool] = {}
        self.transactions: Dict[str, CrossChainTransaction] = {}
        self.bridge_nodes: Dict[str, BridgeNode] = {}
        self._pool_counter = 0
        self._tx_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 流动性池 ==========

    def create_pool(
        self,
        token_a: str,
        token_b: str,
        initial_a: float = 100.0,
        initial_b: float = 100.0,
    ) -> Tuple[bool, str]:
        """创建流动性池"""
        self._pool_counter += 1
        pool_id = f"pool-{self._pool_counter:04d}"

        pool = LiquidityPool(
            pool_id=pool_id,
            token_a=token_a,
            token_b=token_b,
            reserve_a=initial_a,
            reserve_b=initial_b,
            total_shares=initial_a,  # 初始份额等于 token_a 数量
        )
        self.pools[pool_id] = pool

        return True, f"流动性池 {pool_id} 创建成功 ({token_a}/{token_b})"

    def add_liquidity(
        self,
        pool_id: str,
        amount_a: float,
        amount_b: float,
    ) -> Tuple[bool, str]:
        """添加流动性"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"流动性池 {pool_id} 不存在"

        # 计算份额
        if pool.reserve_a == 0:
            shares = amount_a
        else:
            shares = min(
                amount_a * pool.total_shares / pool.reserve_a,
                amount_b * pool.total_shares / pool.reserve_b,
            )

        pool.reserve_a += amount_a
        pool.reserve_b += amount_b
        pool.total_shares += shares

        return True, f"添加流动性成功，获得 {shares:.2f} 份额"

    def remove_liquidity(
        self,
        pool_id: str,
        shares: float,
    ) -> Tuple[bool, str]:
        """移除流动性"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"流动性池 {pool_id} 不存在"

        if shares > pool.total_shares:
            return False, f"份额不足: {shares} > {pool.total_shares}"

        # 计算返还金额
        amount_a = shares * pool.reserve_a / pool.total_shares
        amount_b = shares * pool.reserve_b / pool.total_shares

        pool.reserve_a -= amount_a
        pool.reserve_b -= amount_b
        pool.total_shares -= shares

        return True, f"移除流动性成功: {amount_a:.2f} {pool.token_a} + {amount_b:.2f} {pool.token_b}"

    def swap(
        self,
        pool_id: str,
        from_token: str,
        to_token: str,
        amount_in: float,
    ) -> Tuple[bool, str, float]:
        """兑换 token"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"流动性池 {pool_id} 不存在", 0

        # 检查 token 对
        if from_token == pool.token_a and to_token == pool.token_b:
            reserve_in = pool.reserve_a
            reserve_out = pool.reserve_b
        elif from_token == pool.token_b and to_token == pool.token_a:
            reserve_in = pool.reserve_b
            reserve_out = pool.reserve_a
        else:
            return False, f"不支持的 token 对: {from_token}/{to_token}", 0

        # 计算兑换数量（AMM 公式）
        amount_with_fee = amount_in * 0.997  # 0.3% 手续费
        amount_out = (amount_with_fee * reserve_out) / (reserve_in + amount_with_fee)

        # 更新储备
        if from_token == pool.token_a:
            pool.reserve_a += amount_in
            pool.reserve_b -= amount_out
        else:
            pool.reserve_b += amount_in
            pool.reserve_a -= amount_out

        return True, f"兑换成功: {amount_in} {from_token} → {amount_out:.4f} {to_token}", amount_out

    # ========== 跨链交易 ==========

    def create_cross_chain_tx(
        self,
        from_chain: str,
        to_chain: str,
        from_address: str,
        to_address: str,
        amount: float,
        token: str = "🦞",
    ) -> Tuple[bool, str]:
        """创建跨链交易"""
        self._tx_counter += 1
        tx_id = f"cross-tx-{self._tx_counter:06d}"

        tx = CrossChainTransaction(
            tx_id=tx_id,
            from_chain=from_chain,
            to_chain=to_chain,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            token=token,
        )
        self.transactions[tx_id] = tx

        return True, f"跨链交易 {tx_id} 创建成功"

    def process_cross_chain_tx(self, tx_id: str) -> Tuple[bool, str]:
        """处理跨链交易"""
        tx = self.transactions.get(tx_id)
        if not tx:
            return False, f"交易 {tx_id} 不存在"

        if tx.status != CROSS_CHAIN_STATUS_PENDING:
            return False, f"交易 {tx_id} 状态为 {tx.status}，不可处理"

        # 模拟跨链处理流程
        tx.status = CROSS_CHAIN_STATUS_LOCKING
        tx.status = CROSS_CHAIN_STATUS_LOCKED
        tx.status = CROSS_CHAIN_STATUS_MINTING
        tx.status = CROSS_CHAIN_STATUS_MINTED
        tx.status = CROSS_CHAIN_STATUS_COMPLETED
        tx.completed_at = datetime.now().isoformat()

        return True, f"跨链交易 {tx_id} 处理完成"

    # ========== 桥接节点 ==========

    def register_bridge_node(
        self,
        node_id: str,
        name: str,
        chains: List[str],
    ) -> Tuple[bool, str]:
        """注册桥接节点"""
        if node_id in self.bridge_nodes:
            return False, f"桥接节点 {node_id} 已存在"

        node = BridgeNode(
            node_id=node_id,
            name=name,
            chains=chains,
        )
        self.bridge_nodes[node_id] = node

        return True, f"桥接节点 {node_id} 注册成功"

    def get_available_bridges(self, from_chain: str, to_chain: str) -> List[Dict]:
        """获取可用桥接节点"""
        bridges = []
        for node in self.bridge_nodes.values():
            if from_chain in node.chains and to_chain in node.chains:
                bridges.append(node.to_dict())
        return bridges

    # ========== 查询功能 ==========

    def get_pool(self, pool_id: str) -> Optional[Dict]:
        """获取流动性池"""
        pool = self.pools.get(pool_id)
        return pool.to_dict() if pool else None

    def get_all_pools(self) -> List[Dict]:
        """获取所有流动性池"""
        return [p.to_dict() for p in self.pools.values()]

    def get_cross_chain_tx(self, tx_id: str) -> Optional[Dict]:
        """获取跨链交易"""
        tx = self.transactions.get(tx_id)
        return tx.to_dict() if tx else None

    def get_cross_chain_statistics(self) -> Dict:
        """获取跨链统计"""
        return {
            "total_pools": len(self.pools),
            "total_transactions": len(self.transactions),
            "completed_transactions": len([t for t in self.transactions.values() if t.status == CROSS_CHAIN_STATUS_COMPLETED]),
            "total_volume": sum(t.amount for t in self.transactions.values()),
            "bridge_nodes": len(self.bridge_nodes),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "pools": {pid: p.to_dict() for pid, p in self.pools.items()},
            "transactions": {tid: t.to_dict() for tid, t in self.transactions.items()},
            "bridge_nodes": {nid: n.to_dict() for nid, n in self.bridge_nodes.items()},
            "counters": {
                "pool": self._pool_counter,
                "tx": self._tx_counter,
            },
        }
        with open(os.path.join(self.data_dir, "cross_chain_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "cross_chain_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.pools = {pid: LiquidityPool(**p) for pid, p in data.get("pools", {}).items()}
            self.transactions = {tid: CrossChainTransaction(**t) for tid, t in data.get("transactions", {}).items()}
            self.bridge_nodes = {nid: BridgeNode(**n) for nid, n in data.get("bridge_nodes", {}).items()}

            counters = data.get("counters", {})
            self._pool_counter = counters.get("pool", 0)
            self._tx_counter = counters.get("tx", 0)

            return True
        return False
