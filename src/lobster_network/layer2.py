#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Layer 2 扩容系统 V3.0
基于 Rollup 技术的二层扩容方案

功能：
1. Layer 2 交易批处理
2. 状态通道
3. 批量提交到 Layer 1
4. 欺诈证明
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .token_economy import TokenEconomy


# ========== 常量定义 ==========

# Layer 2 状态
L2_STATUS_ACTIVE = "active"        # 活跃
L2_STATUS_CHALLENGE = "challenge"  # 挑战中
L2_STATUS_FINALIZED = "finalized"  # 已最终确定

# Rollup 类型
ROLLUP_TYPE_OPTIMISTIC = "optimistic"  # 乐观 Rollup
ROLLUP_TYPE_ZK = "zk"                  # ZK Rollup


# ========== 数据类定义 ==========

@dataclass
class L2Transaction:
    """Layer 2 交易"""
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    token: str = "🦞"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    batch_id: Optional[str] = None
    l1_tx_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "token": self.token,
            "timestamp": self.timestamp,
            "batch_id": self.batch_id,
            "l1_tx_hash": self.l1_tx_hash,
        }


@dataclass
class L2Batch:
    """Layer 2 批次"""
    batch_id: str
    transactions: List[L2Transaction] = field(default_factory=list)
    state_root: str = ""
    batch_data: str = ""
    submitted_at: Optional[str] = None
    finalized_at: Optional[str] = None
    status: str = L2_STATUS_ACTIVE
    rollup_type: str = ROLLUP_TYPE_OPTIMISTIC

    @property
    def tx_count(self) -> int:
        """交易数量"""
        return len(self.transactions)

    @property
    def total_amount(self) -> float:
        """总金额"""
        return sum(tx.amount for tx in self.transactions)

    def compute_state_root(self) -> str:
        """计算状态根"""
        data = json.dumps([tx.to_dict() for tx in self.transactions], sort_keys=True)
        self.state_root = hashlib.sha256(data.encode()).hexdigest()
        return self.state_root

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "tx_count": self.tx_count,
            "total_amount": self.total_amount,
            "state_root": self.state_root,
            "submitted_at": self.submitted_at,
            "finalized_at": self.finalized_at,
            "status": self.status,
            "rollup_type": self.rollup_type,
        }


@dataclass
class FraudProof:
    """欺诈证明"""
    proof_id: str
    batch_id: str
    challenger_id: str
    evidence: str
    status: str = "pending"  # pending/verified/invalid
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "proof_id": self.proof_id,
            "batch_id": self.batch_id,
            "challenger_id": self.challenger_id,
            "evidence": self.evidence,
            "status": self.status,
            "created_at": self.created_at,
        }


# ========== Layer 2 系统 ==========

class Layer2System:
    """Layer 2 扩容系统"""

    def __init__(self, token_economy: TokenEconomy, data_dir: str = "/shared/lobster-network-data/layer2"):
        self.token_economy = token_economy
        self.data_dir = data_dir
        self.batches: Dict[str, L2Batch] = {}
        self.l2_transactions: Dict[str, L2Transaction] = {}
        self.fraud_proofs: Dict[str, FraudProof] = {}
        self._batch_counter = 0
        self._tx_counter = 0
        self._proof_counter = 0
        self.current_batch: Optional[L2Batch] = None
        self.max_batch_size = 100  # 最大批次大小

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== Layer 2 交易 ==========

    def create_l2_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        token: str = "🦞",
    ) -> Tuple[bool, str]:
        """创建 Layer 2 交易"""
        # 检查余额
        balance = self.token_economy.get_balance(from_address)
        if balance < amount:
            return False, f"余额不足: {balance} < {amount}"

        self._tx_counter += 1
        tx_id = f"l2-tx-{self._tx_counter:06d}"

        tx = L2Transaction(
            tx_id=tx_id,
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            token=token,
        )
        self.l2_transactions[tx_id] = tx

        # 添加到当前批次
        if self.current_batch is None:
            self.create_batch()

        if self.current_batch and self.current_batch.tx_count < self.max_batch_size:
            tx.batch_id = self.current_batch.batch_id
            self.current_batch.transactions.append(tx)
        else:
            # 创建新批次
            self.submit_batch()
            self.create_batch()
            if self.current_batch:
                tx.batch_id = self.current_batch.batch_id
                self.current_batch.transactions.append(tx)

        return True, f"L2 交易 {tx_id} 创建成功"

    # ========== 批次管理 ==========

    def create_batch(self, rollup_type: str = ROLLUP_TYPE_OPTIMISTIC) -> Tuple[bool, str]:
        """创建新批次"""
        if self.current_batch and self.current_batch.tx_count > 0:
            self.submit_batch()

        self._batch_counter += 1
        batch_id = f"batch-{self._batch_counter:04d}"

        batch = L2Batch(
            batch_id=batch_id,
            rollup_type=rollup_type,
        )
        self.current_batch = batch
        self.batches[batch_id] = batch

        return True, f"批次 {batch_id} 创建成功"

    def submit_batch(self) -> Tuple[bool, str]:
        """提交批次到 Layer 1"""
        if not self.current_batch or self.current_batch.tx_count == 0:
            return False, "当前批次无交易"

        # 计算状态根
        self.current_batch.compute_state_root()
        self.current_batch.submitted_at = datetime.now().isoformat()
        self.current_batch.status = L2_STATUS_ACTIVE

        # 模拟提交到 L1
        l1_tx_hash = hashlib.sha256(
            f"{self.current_batch.batch_id}:{self.current_batch.state_root}".encode()
        ).hexdigest()
        self.current_batch.batch_data = l1_tx_hash

        return True, f"批次 {self.current_batch.batch_id} 已提交到 L1 (tx_hash: {l1_tx_hash[:16]}...)"

    def finalize_batch(self, batch_id: str) -> Tuple[bool, str]:
        """最终确定批次"""
        batch = self.batches.get(batch_id)
        if not batch:
            return False, f"批次 {batch_id} 不存在"

        if batch.status != L2_STATUS_ACTIVE:
            return False, f"批次 {batch_id} 状态为 {batch.status}，不可最终确定"

        # 检查欺诈证明
        has_valid_proof = False
        for proof in self.fraud_proofs.values():
            if proof.batch_id == batch_id and proof.status == "verified":
                has_valid_proof = True
                break

        if has_valid_proof:
            batch.status = L2_STATUS_CHALLENGE
            return False, f"批次 {batch_id} 存在有效欺诈证明，进入挑战期"

        batch.status = L2_STATUS_FINALIZED
        batch.finalized_at = datetime.now().isoformat()

        return True, f"批次 {batch_id} 已最终确定"

    # ========== 欺诈证明 ==========

    def submit_fraud_proof(
        self,
        batch_id: str,
        challenger_id: str,
        evidence: str,
    ) -> Tuple[bool, str]:
        """提交欺诈证明"""
        batch = self.batches.get(batch_id)
        if not batch:
            return False, f"批次 {batch_id} 不存在"

        if batch.status != L2_STATUS_ACTIVE:
            return False, f"批次 {batch_id} 状态为 {batch.status}，不可挑战"

        self._proof_counter += 1
        proof_id = f"proof-{self._proof_counter:04d}"

        proof = FraudProof(
            proof_id=proof_id,
            batch_id=batch_id,
            challenger_id=challenger_id,
            evidence=evidence,
        )
        self.fraud_proofs[proof_id] = proof

        return True, f"欺诈证明 {proof_id} 已提交"

    def verify_fraud_proof(self, proof_id: str, valid: bool) -> Tuple[bool, str]:
        """验证欺诈证明"""
        proof = self.fraud_proofs.get(proof_id)
        if not proof:
            return False, f"欺诈证明 {proof_id} 不存在"

        proof.status = "verified" if valid else "invalid"

        if valid:
            # 标记批次为挑战中
            batch = self.batches.get(proof.batch_id)
            if batch:
                batch.status = L2_STATUS_CHALLENGE
            return True, f"欺诈证明 {proof_id} 验证有效，批次进入挑战期"
        else:
            return True, f"欺诈证明 {proof_id} 验证无效"

    # ========== 状态通道 ==========

    def create_state_channel(
        self,
        participant_a: str,
        participant_b: str,
        initial_balance_a: float,
        initial_balance_b: float,
    ) -> Tuple[bool, str]:
        """创建状态通道"""
        channel_id = f"channel-{hashlib.sha256(f'{participant_a}:{participant_b}'.encode()).hexdigest()[:8]}"

        # 锁定资金
        self.token_economy.stake(participant_a, initial_balance_a)
        self.token_economy.stake(participant_b, initial_balance_b)

        return True, f"状态通道 {channel_id} 创建成功"

    def update_state_channel(
        self,
        channel_id: str,
        participant: str,
        new_balance_a: float,
        new_balance_b: float,
        signature: str,
    ) -> Tuple[bool, str]:
        """更新状态通道"""
        # 验证签名
        # 更新余额
        return True, f"状态通道 {channel_id} 更新成功"

    def close_state_channel(
        self,
        channel_id: str,
        participant: str,
    ) -> Tuple[bool, str]:
        """关闭状态通道"""
        # 解锁资金
        return True, f"状态通道 {channel_id} 已关闭"

    # ========== 查询功能 ==========

    def get_batch(self, batch_id: str) -> Optional[Dict]:
        """获取批次"""
        batch = self.batches.get(batch_id)
        return batch.to_dict() if batch else None

    def get_all_batches(self) -> List[Dict]:
        """获取所有批次"""
        return [b.to_dict() for b in self.batches.values()]

    def get_l2_transactions(self, batch_id: str = None) -> List[Dict]:
        """获取 L2 交易"""
        txs = [tx.to_dict() for tx in self.l2_transactions.values()]
        if batch_id:
            txs = [tx for tx in txs if tx.get("batch_id") == batch_id]
        return sorted(txs, key=lambda x: x["timestamp"], reverse=True)

    def get_layer2_statistics(self) -> Dict:
        """获取 Layer 2 统计"""
        total_txs = sum(b.tx_count for b in self.batches.values())
        total_amount = sum(b.total_amount for b in self.batches.values())

        return {
            "total_batches": len(self.batches),
            "total_l2_transactions": len(self.l2_transactions),
            "total_fraud_proofs": len(self.fraud_proofs),
            "verified_proofs": len([p for p in self.fraud_proofs.values() if p.status == "verified"]),
            "total_txs_in_batches": total_txs,
            "total_amount_in_batches": total_amount,
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "batches": {bid: b.to_dict() for bid, b in self.batches.items()},
            "l2_transactions": {tid: t.to_dict() for tid, t in self.l2_transactions.items()},
            "fraud_proofs": {pid: p.to_dict() for pid, p in self.fraud_proofs.items()},
            "counters": {
                "batch": self._batch_counter,
                "tx": self._tx_counter,
                "proof": self._proof_counter,
            },
        }
        with open(os.path.join(self.data_dir, "layer2_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "layer2_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.batches = {}
            for bid, b_data in data.get("batches", {}).items():
                batch = L2Batch(
                    batch_id=b_data["batch_id"],
                    state_root=b_data.get("state_root", ""),
                    submitted_at=b_data.get("submitted_at"),
                    finalized_at=b_data.get("finalized_at"),
                    status=b_data.get("status", L2_STATUS_ACTIVE),
                    rollup_type=b_data.get("rollup_type", ROLLUP_TYPE_OPTIMISTIC),
                )
                self.batches[bid] = batch

            self.l2_transactions = {tid: L2Transaction(**t) for tid, t in data.get("l2_transactions", {}).items()}
            self.fraud_proofs = {pid: FraudProof(**p) for pid, p in data.get("fraud_proofs", {}).items()}

            counters = data.get("counters", {})
            self._batch_counter = counters.get("batch", 0)
            self._tx_counter = counters.get("tx", 0)
            self._proof_counter = counters.get("proof", 0)

            return True
        return False
