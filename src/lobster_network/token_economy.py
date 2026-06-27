#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Token 经济系统 V2.0
参考比特币分布式货币机制

设计理念：
1. 分布式发行 - 通过挖矿（完成任务/对话）获得 token
2. 总量控制 - 2100 万枚 lobster token，每 4 年减半
3. 共识机制 - 涌现共识（Emergence Consensus）
4. 分布式账本 - 每个节点维护完整账本
5. 对标的资产 - token（计算力/注意力/创造力）
"""

import json
import os
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .node import Node


# ========== 常量定义 ==========

# Token 总量
TOTAL_SUPPLY = 21_000_000  # 2100 万枚
INITIAL_BLOCK_REWARD = 50  # 初始区块奖励 50 token
HALVING_INTERVAL = 210_000  # 每 21 万个区块减半
MINING_DIFFICULTY = 4  # 挖矿难度（前导零数量）

# Token 单位
TOKEN_UNIT = "LOBSTER"
TOKEN_SYMBOL = "🦞"
TOKEN_DECIMALS = 8  # 小数位数

# 共识机制
CONSENSUS_EMERGENCE = "emergence"  # 涌现共识
CONSENSUS_PROOF_OF_WORK = "pow"    # 工作量证明
CONSENSUS_PROOF_OF_STAKE = "pos"   # 权益证明

# 交易类型
TX_TYPE_MINING = "mining"          # 挖矿奖励
TX_TYPE_TRANSFER = "transfer"      # 转账
TX_TYPE_TASK_REWARD = "task_reward" # 任务奖励
TX_TYPE_STAKING = "staking"        # 质押
TX_TYPE_BURN = "burn"              # 销毁


# ========== 数据类定义 ==========

@dataclass
class Transaction:
    """交易"""
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    tx_type: str = TX_TYPE_TRANSFER
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    block_hash: Optional[str] = None
    nonce: int = 0
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "from": self.from_address,
            "to": self.to_address,
            "amount": self.amount,
            "type": self.tx_type,
            "timestamp": self.timestamp,
            "block_hash": self.block_hash,
            "nonce": self.nonce,
            "metadata": self.metadata,
        }

    def serialize(self) -> str:
        """序列化交易"""
        return json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)


@dataclass
class Block:
    """区块"""
    index: int
    timestamp: str
    transactions: List[Transaction]
    previous_hash: str
    nonce: int = 0
    difficulty: int = MINING_DIFFICULTY
    miner: str = ""

    @property
    def hash(self) -> str:
        """计算区块哈希"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "miner": self.miner,
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(block_string.encode()).hexdigest()

    @property
    def is_valid(self) -> bool:
        """验证区块有效性"""
        return self.hash[:self.difficulty] == "0" * self.difficulty

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "miner": self.miner,
        }


@dataclass
class Wallet:
    """钱包"""
    address: str
    balance: float = 0.0
    staked: float = 0.0
    transactions: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "balance": self.balance,
            "staked": self.staked,
            "transactions": self.transactions,
            "created_at": self.created_at,
        }


# ========== Token 经济系统 ==========

class TokenEconomy:
    """小龙虾网络 Token 经济系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/token"):
        self.data_dir = data_dir
        self.wallets: Dict[str, Wallet] = {}
        self.blockchain: List[Block] = []
        self.mempool: List[Transaction] = []
        self._tx_counter = 0
        self._current_difficulty = MINING_DIFFICULTY

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

        # 初始化创世区块
        if not self.blockchain:
            self._create_genesis_block()

    def _create_genesis_block(self):
        """创建创世区块"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            transactions=[],
            previous_hash="0" * 64,
            miner="genesis",
        )
        self.blockchain.append(genesis_block)

    # ========== 钱包管理 ==========

    def create_wallet(self, node_id: str) -> Tuple[bool, str]:
        """创建钱包"""
        if node_id in self.wallets:
            return False, f"钱包已存在: {node_id}"

        # 生成地址（基于 node_id 的哈希）
        address = hashlib.sha256(node_id.encode()).hexdigest()[:16]

        self.wallets[node_id] = Wallet(
            address=address,
            balance=0.0,
        )
        return True, f"钱包创建成功: {address}"

    def get_wallet(self, node_id: str) -> Optional[Wallet]:
        """获取钱包"""
        return self.wallets.get(node_id)

    def get_balance(self, node_id: str) -> float:
        """获取余额"""
        wallet = self.wallets.get(node_id)
        return wallet.balance if wallet else 0.0

    # ========== 挖矿系统 ==========

    def get_block_reward(self, block_index: int) -> float:
        """计算区块奖励（减半机制）"""
        halvings = block_index // HALVING_INTERVAL
        if halvings >= 64:  # 64 次减半后奖励为 0
            return 0
        reward = INITIAL_BLOCK_REWARD / (2 ** halvings)
        return reward

    def mine_block(self, miner_id: str, emergence_score: float = 0.5) -> Tuple[bool, str]:
        """
        挖矿 - 基于涌现共识

        参数:
            miner_id: 矿工 ID
            emergence_score: 涌现值（0-1），影响挖矿成功率
        """
        wallet = self.wallets.get(miner_id)
        if not wallet:
            return False, f"钱包不存在: {miner_id}"

        # 计算挖矿难度（基于涌现值调整）
        adjusted_difficulty = max(2, self._current_difficulty - int(emergence_score * 2))

        # 模拟挖矿（工作量证明）
        last_block = self.blockchain[-1]
        new_block = Block(
            index=len(self.blockchain),
            timestamp=datetime.now().isoformat(),
            transactions=self.mempool[:10],  # 最多 10 笔交易
            previous_hash=last_block.hash,
            difficulty=adjusted_difficulty,
            miner=miner_id,
        )

        # 挖矿（寻找有效 nonce）
        nonce = 0
        while not new_block.is_valid and nonce < 10000:
            new_block.nonce = nonce
            nonce += 1

        if not new_block.is_valid:
            return False, "挖矿失败，未找到有效 nonce"

        # 添加区块到链
        self.blockchain.append(new_block)

        # 发放挖矿奖励
        reward = self.get_block_reward(new_block.index)
        wallet.balance += reward

        # 创建挖矿交易
        mining_tx = Transaction(
            tx_id=f"tx-mining-{new_block.index}",
            from_address="genesis",
            to_address=wallet.address,
            amount=reward,
            tx_type=TX_TYPE_MINING,
            block_hash=new_block.hash,
            nonce=new_block.nonce,
        )
        wallet.transactions.append(mining_tx.tx_id)

        # 清空已打包的交易
        self.mempool = self.mempool[10:]

        return True, f"挖矿成功！获得 {reward} {TOKEN_UNIT}"

    # ========== 转账系统 ==========

    def transfer(
        self,
        from_id: str,
        to_id: str,
        amount: float,
        tx_type: str = TX_TYPE_TRANSFER,
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """转账"""
        from_wallet = self.wallets.get(from_id)
        to_wallet = self.wallets.get(to_id)

        if not from_wallet:
            return False, f"发送方钱包不存在: {from_id}"
        if not to_wallet:
            return False, f"接收方钱包不存在: {to_id}"
        if from_wallet.balance < amount:
            return False, f"余额不足: {from_wallet.balance} < {amount}"

        # 创建交易
        self._tx_counter += 1
        tx_id = f"tx-{self._tx_counter:06d}"

        tx = Transaction(
            tx_id=tx_id,
            from_address=from_wallet.address,
            to_address=to_wallet.address,
            amount=amount,
            tx_type=tx_type,
            metadata=metadata or {},
        )

        # 执行转账
        from_wallet.balance -= amount
        to_wallet.balance += amount
        from_wallet.transactions.append(tx_id)
        to_wallet.transactions.append(tx_id)

        # 添加到内存池
        self.mempool.append(tx)

        return True, f"转账成功: {amount} {TOKEN_UNIT} ({tx_id})"

    # ========== 质押系统 ==========

    def stake(self, node_id: str, amount: float) -> Tuple[bool, str]:
        """质押 token"""
        wallet = self.wallets.get(node_id)
        if not wallet:
            return False, f"钱包不存在: {node_id}"
        if wallet.balance < amount:
            return False, f"余额不足: {wallet.balance} < {amount}"

        wallet.balance -= amount
        wallet.staked += amount

        # 创建质押交易
        self._tx_counter += 1
        tx_id = f"tx-stake-{self._tx_counter:06d}"

        tx = Transaction(
            tx_id=tx_id,
            from_address=wallet.address,
            to_address="staking_pool",
            amount=amount,
            tx_type=TX_TYPE_STAKING,
        )
        wallet.transactions.append(tx_id)
        self.mempool.append(tx)

        return True, f"质押成功: {amount} {TOKEN_UNIT}"

    def unstake(self, node_id: str, amount: float) -> Tuple[bool, str]:
        """解除质押"""
        wallet = self.wallets.get(node_id)
        if not wallet:
            return False, f"钱包不存在: {node_id}"
        if wallet.staked < amount:
            return False, f"质押不足: {wallet.staked} < {amount}"

        wallet.staked -= amount
        wallet.balance += amount

        return True, f"解除质押成功: {amount} {TOKEN_UNIT}"

    # ========== 销毁系统 ==========

    def burn(self, node_id: str, amount: float) -> Tuple[bool, str]:
        """销毁 token"""
        wallet = self.wallets.get(node_id)
        if not wallet:
            return False, f"钱包不存在: {node_id}"
        if wallet.balance < amount:
            return False, f"余额不足: {wallet.balance} < {amount}"

        wallet.balance -= amount

        # 创建销毁交易
        self._tx_counter += 1
        tx_id = f"tx-burn-{self._tx_counter:06d}"

        tx = Transaction(
            tx_id=tx_id,
            from_address=wallet.address,
            to_address="burn_address",
            amount=amount,
            tx_type=TX_TYPE_BURN,
        )
        wallet.transactions.append(tx_id)
        self.mempool.append(tx)

        return True, f"销毁成功: {amount} {TOKEN_UNIT}"

    # ========== 任务奖励 ==========

    def reward_task(
        self,
        task_id: str,
        worker_id: str,
        reward_amount: float,
    ) -> Tuple[bool, str]:
        """发放任务奖励"""
        worker_wallet = self.wallets.get(worker_id)
        if not worker_wallet:
            return False, f"钱包不存在: {worker_id}"

        # 从系统池发放奖励（新铸造）
        worker_wallet.balance += reward_amount

        # 创建奖励交易
        self._tx_counter += 1
        tx_id = f"tx-task-{self._tx_counter:06d}"

        tx = Transaction(
            tx_id=tx_id,
            from_address="system_pool",
            to_address=worker_wallet.address,
            amount=reward_amount,
            tx_type=TX_TYPE_TASK_REWARD,
            metadata={"task_id": task_id},
        )
        worker_wallet.transactions.append(tx_id)
        self.mempool.append(tx)

        return True, f"任务奖励发放: {reward_amount} {TOKEN_UNIT} ({tx_id})"

    # ========== 查询功能 ==========

    def get_blockchain_info(self) -> Dict:
        """获取区块链信息"""
        return {
            "chain_length": len(self.blockchain),
            "current_difficulty": self._current_difficulty,
            "mempool_size": len(self.mempool),
            "total_wallets": len(self.wallets),
            "total_supply": self.get_total_supply(),
            "circulating_supply": self.get_circulating_supply(),
        }

    def get_total_supply(self) -> float:
        """获取总供应量"""
        return sum(w.balance + w.staked for w in self.wallets.values())

    def get_circulating_supply(self) -> float:
        """获取流通量"""
        return sum(w.balance for w in self.wallets.values())

    def get_staked_supply(self) -> float:
        """获取质押量"""
        return sum(w.staked for w in self.wallets.values())

    def get_transactions(self, node_id: str) -> List[Dict]:
        """获取交易历史"""
        wallet = self.wallets.get(node_id)
        if not wallet:
            return []

        txs = []
        for tx in self.mempool:
            if tx.from_address == wallet.address or tx.to_address == wallet.address:
                txs.append(tx.to_dict())

        # 从区块链中查找历史交易
        for block in self.blockchain:
            for tx in block.transactions:
                if tx.from_address == wallet.address or tx.to_address == wallet.address:
                    txs.append(tx.to_dict())

        return sorted(txs, key=lambda x: x["timestamp"], reverse=True)

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """获取排行榜"""
        wallets = sorted(
            self.wallets.items(),
            key=lambda x: x[1].balance + x[1].staked,
            reverse=True,
        )[:limit]

        return [
            {
                "node_id": node_id,
                "address": wallet.address,
                "balance": wallet.balance,
                "staked": wallet.staked,
                "total": wallet.balance + wallet.staked,
            }
            for node_id, wallet in wallets
        ]

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "wallets": {nid: w.to_dict() for nid, w in self.wallets.items()},
            "blockchain": [b.to_dict() for b in self.blockchain],
            "mempool": [tx.to_dict() for tx in self.mempool],
            "counters": {
                "tx": self._tx_counter,
            },
            "difficulty": self._current_difficulty,
        }
        with open(os.path.join(self.data_dir, "token_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "token_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.wallets = {nid: Wallet(**w) for nid, w in data.get("wallets", {}).items()}

            # 加载区块链
            self.blockchain = []
            for b_data in data.get("blockchain", []):
                block = Block(
                    index=b_data["index"],
                    timestamp=b_data["timestamp"],
                    transactions=[],
                    previous_hash=b_data["previous_hash"],
                    nonce=b_data.get("nonce", 0),
                    miner=b_data.get("miner", ""),
                )
                self.blockchain.append(block)

            # 加载内存池
            self.mempool = []
            for tx_data in data.get("mempool", []):
                tx = Transaction(
                    tx_id=tx_data["tx_id"],
                    from_address=tx_data["from"],
                    to_address=tx_data["to"],
                    amount=tx_data["amount"],
                    tx_type=tx_data.get("type", TX_TYPE_TRANSFER),
                    timestamp=tx_data.get("timestamp", datetime.now().isoformat()),
                    nonce=tx_data.get("nonce", 0),
                    metadata=tx_data.get("metadata", {}),
                )
                self.mempool.append(tx)

            counters = data.get("counters", {})
            self._tx_counter = counters.get("tx", 0)
            self._current_difficulty = data.get("difficulty", MINING_DIFFICULTY)

            return True
        return False
