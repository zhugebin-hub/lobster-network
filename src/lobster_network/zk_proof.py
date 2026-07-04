#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络零知识证明系统 V3.0
基于 zk-SNARK 的隐私保护

功能：
1. 零知识证明生成/验证
2. 隐私交易
3. 匿名转账
4. 合规证明
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ========== 常量定义 ==========

# 证明类型
PROOF_TYPE_TRANSFER = "transfer"       # 转账证明
PROOF_TYPE_BALANCE = "balance"         # 余额证明
PROOF_TYPE_MERKLE = "merkle"           # Merkle 树证明

# 证明状态
PROOF_STATUS_PENDING = "pending"       # 待验证
PROOF_STATUS_VALID = "valid"           # 有效
PROOF_STATUS_INVALID = "invalid"       # 无效


# ========== 数据类定义 ==========

@dataclass
class ZKProof:
    """零知识证明"""
    proof_id: str
    proof_type: str
    prover_id: str
    verifier_id: str
    proof_data: str
    public_inputs: Dict
    status: str = PROOF_STATUS_PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    verified_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "proof_id": self.proof_id,
            "proof_type": self.proof_type,
            "prover_id": self.prover_id,
            "verifier_id": self.verifier_id,
            "proof_data": self.proof_data,
            "public_inputs": self.public_inputs,
            "status": self.status,
            "created_at": self.created_at,
            "verified_at": self.verified_at,
        }


@dataclass
class PrivacyTransaction:
    """隐私交易"""
    tx_id: str
    from_commitment: str
    to_commitment: str
    amount: float
    proof_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "from_commitment": self.from_commitment,
            "to_commitment": self.to_commitment,
            "amount": self.amount,
            "proof_id": self.proof_id,
            "timestamp": self.timestamp,
        }


@dataclass
class MerkleTree:
    """Merkle 树"""
    leaves: List[str]
    root: str = ""
    tree: List[List[str]] = field(default_factory=list)

    def __post_init__(self):
        """构建 Merkle 树"""
        if self.leaves and not self.root:
            self.build_tree()

    def build_tree(self):
        """构建 Merkle 树"""
        if not self.leaves:
            self.root = ""
            return

        # 叶子节点哈希
        current_level = [hashlib.sha256(leaf.encode()).hexdigest() for leaf in self.leaves]
        self.tree = [current_level]

        # 逐层构建
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                parent = hashlib.sha256((left + right).encode()).hexdigest()
                next_level.append(parent)
            current_level = next_level
            self.tree.append(current_level)

        self.root = current_level[0] if current_level else ""

    def get_proof(self, leaf_index: int) -> List[Dict]:
        """获取 Merkle 证明"""
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            return []

        proof = []
        index = leaf_index

        for level in self.tree[:-1]:
            if index % 2 == 0:
                sibling_index = index + 1
                position = "right"
            else:
                sibling_index = index - 1
                position = "left"

            if sibling_index < len(level):
                proof.append({
                    "hash": level[sibling_index],
                    "position": position,
                })

            index //= 2

        return proof

    def verify_proof(self, leaf: str, proof: List[Dict]) -> bool:
        """验证 Merkle 证明"""
        current_hash = hashlib.sha256(leaf.encode()).hexdigest()

        for step in proof:
            sibling_hash = step["hash"]
            if step["position"] == "right":
                current_hash = hashlib.sha256((current_hash + sibling_hash).encode()).hexdigest()
            else:
                current_hash = hashlib.sha256((sibling_hash + current_hash).encode()).hexdigest()

        return current_hash == self.root

    def to_dict(self) -> dict:
        return {
            "leaves": self.leaves,
            "root": self.root,
            "tree_depth": len(self.tree),
        }


# ========== 零知识证明系统 ==========

class ZKProofSystem:
    """零知识证明系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/zk-proof"):
        self.data_dir = data_dir
        self.proofs: Dict[str, ZKProof] = {}
        self.privacy_transactions: List[PrivacyTransaction] = []
        self.merkle_trees: Dict[str, MerkleTree] = {}
        self._proof_counter = 0
        self._tx_counter = 0
        self._tree_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 零知识证明 ==========

    def create_proof(
        self,
        proof_type: str,
        prover_id: str,
        verifier_id: str,
        proof_data: str,
        public_inputs: Dict = None,
    ) -> Tuple[bool, str]:
        """创建零知识证明"""
        self._proof_counter += 1
        proof_id = f"zk-proof-{self._proof_counter:04d}"

        proof = ZKProof(
            proof_id=proof_id,
            proof_type=proof_type,
            prover_id=prover_id,
            verifier_id=verifier_id,
            proof_data=proof_data,
            public_inputs=public_inputs or {},
        )
        self.proofs[proof_id] = proof

        return True, f"零知识证明 {proof_id} 创建成功"

    def verify_proof(self, proof_id: str) -> Tuple[bool, str]:
        """验证零知识证明"""
        proof = self.proofs.get(proof_id)
        if not proof:
            return False, f"证明 {proof_id} 不存在"

        if proof.status != PROOF_STATUS_PENDING:
            return False, f"证明 {proof_id} 状态为 {proof.status}，不可验证"

        # 模拟验证（实际应使用 zk-SNARK 验证器）
        # 这里简化为检查 proof_data 是否有效
        if proof.proof_data and len(proof.proof_data) > 10:
            proof.status = PROOF_STATUS_VALID
            proof.verified_at = datetime.now().isoformat()
            return True, f"证明 {proof_id} 验证通过"
        else:
            proof.status = PROOF_STATUS_INVALID
            proof.verified_at = datetime.now().isoformat()
            return False, f"证明 {proof_id} 验证失败"

    # ========== 隐私交易 ==========

    def create_privacy_transaction(
        self,
        from_commitment: str,
        to_commitment: str,
        amount: float,
        proof_id: str,
    ) -> Tuple[bool, str]:
        """创建隐私交易"""
        # 验证证明
        proof = self.proofs.get(proof_id)
        if not proof:
            return False, f"证明 {proof_id} 不存在"

        if proof.status != PROOF_STATUS_VALID:
            return False, f"证明 {proof_id} 状态为 {proof.status}，不可用于交易"

        self._tx_counter += 1
        tx_id = f"privacy-tx-{self._tx_counter:06d}"

        tx = PrivacyTransaction(
            tx_id=tx_id,
            from_commitment=from_commitment,
            to_commitment=to_commitment,
            amount=amount,
            proof_id=proof_id,
        )
        self.privacy_transactions.append(tx)

        return True, f"隐私交易 {tx_id} 创建成功"

    # ========== Merkle 树 ==========

    def create_merkle_tree(self, leaves: List[str]) -> Tuple[bool, str]:
        """创建 Merkle 树"""
        self._tree_counter += 1
        tree_id = f"merkle-{self._tree_counter:04d}"

        tree = MerkleTree(leaves=leaves)
        self.merkle_trees[tree_id] = tree

        return True, f"Merkle 树 {tree_id} 创建成功 (root: {tree.root[:16]}...)"

    def get_merkle_proof(self, tree_id: str, leaf_index: int) -> Optional[List[Dict]]:
        """获取 Merkle 证明"""
        tree = self.merkle_trees.get(tree_id)
        if not tree:
            return None
        return tree.get_proof(leaf_index)

    def verify_merkle_proof(self, tree_id: str, leaf: str, proof: List[Dict]) -> bool:
        """验证 Merkle 证明"""
        tree = self.merkle_trees.get(tree_id)
        if not tree:
            return False
        return tree.verify_proof(leaf, proof)

    # ========== 查询功能 ==========

    def get_proof(self, proof_id: str) -> Optional[Dict]:
        """获取证明"""
        proof = self.proofs.get(proof_id)
        return proof.to_dict() if proof else None

    def get_all_proofs(self) -> List[Dict]:
        """获取所有证明"""
        return [p.to_dict() for p in self.proofs.values()]

    def get_valid_proofs(self) -> List[Dict]:
        """获取有效证明"""
        return [p.to_dict() for p in self.proofs.values() if p.status == PROOF_STATUS_VALID]

    def get_privacy_transactions(self) -> List[Dict]:
        """获取隐私交易"""
        return [tx.to_dict() for tx in self.privacy_transactions]

    def get_zk_statistics(self) -> Dict:
        """获取 ZK 统计"""
        return {
            "total_proofs": len(self.proofs),
            "valid_proofs": len([p for p in self.proofs.values() if p.status == PROOF_STATUS_VALID]),
            "invalid_proofs": len([p for p in self.proofs.values() if p.status == PROOF_STATUS_INVALID]),
            "privacy_transactions": len(self.privacy_transactions),
            "merkle_trees": len(self.merkle_trees),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "proofs": {pid: p.to_dict() for pid, p in self.proofs.items()},
            "privacy_transactions": [tx.to_dict() for tx in self.privacy_transactions],
            "merkle_trees": {tid: t.to_dict() for tid, t in self.merkle_trees.items()},
            "counters": {
                "proof": self._proof_counter,
                "tx": self._tx_counter,
                "tree": self._tree_counter,
            },
        }
        with open(os.path.join(self.data_dir, "zk_proof_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "zk_proof_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.proofs = {pid: ZKProof(**p) for pid, p in data.get("proofs", {}).items()}
            self.privacy_transactions = [PrivacyTransaction(**tx) for tx in data.get("privacy_transactions", [])]

            self.merkle_trees = {}
            for tid, t_data in data.get("merkle_trees", {}).items():
                tree = MerkleTree(leaves=t_data.get("leaves", []))
                tree.root = t_data.get("root", "")
                self.merkle_trees[tid] = tree

            counters = data.get("counters", {})
            self._proof_counter = counters.get("proof", 0)
            self._tx_counter = counters.get("tx", 0)
            self._tree_counter = counters.get("tree", 0)

            return True
        return False
