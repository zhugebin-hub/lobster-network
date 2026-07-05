#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络跨链桥系统 V3.0
支持多链资产转移

功能：
1. 跨链资产锁定/铸造
2. 中继器网络
3. 跨链消息传递
4. 桥接安全监控
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ========== 常量定义 ==========

# 链类型
CHAIN_LOBSTER = "lobster"
CHAIN_BITCOIN = "bitcoin"
CHAIN_ETHEREUM = "ethereum"
CHAIN_SOLANA = "solana"
CHAIN_POLKADOT = "polkadot"

# 跨链状态
BRIDGE_STATUS_PENDING = "pending"        # 待处理
BRIDGE_STATUS_LOCKED = "locked"          # 已锁定
BRIDGE_STATUS_MINTED = "minted"          # 已铸造
BRIDGE_STATUS_COMPLETED = "completed"    # 已完成
BRIDGE_STATUS_FAILED = "failed"          # 失败

# 中继器状态
RELAYER_STATUS_ACTIVE = "active"         # 活跃
RELAYER_STATUS_INACTIVE = "inactive"     # 不活跃
RELAYER_STATUS_SLASHED = "slashed"       # 被罚没


# ========== 数据类定义 ==========

@dataclass
class BridgeAsset:
    """桥接资产"""
    asset_id: str
    symbol: str
    name: str
    chains: List[str]
    total_supply: float = 0.0
    bridge_fee: float = 0.001
    status: str = "active"

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "symbol": self.symbol,
            "name": self.name,
            "chains": self.chains,
            "total_supply": self.total_supply,
            "bridge_fee": self.bridge_fee,
            "status": self.status,
        }


@dataclass
class BridgeTransaction:
    """跨链交易"""
    tx_id: str
    from_chain: str
    to_chain: str
    from_address: str
    to_address: str
    asset: str
    amount: float
    fee: float
    status: str = BRIDGE_STATUS_PENDING
    lock_tx_hash: Optional[str] = None
    mint_tx_hash: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    relayer_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "tx_id": self.tx_id,
            "from_chain": self.from_chain,
            "to_chain": self.to_chain,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "asset": self.asset,
            "amount": self.amount,
            "fee": self.fee,
            "status": self.status,
            "lock_tx_hash": self.lock_tx_hash,
            "mint_tx_hash": self.mint_tx_hash,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "relayer_id": self.relayer_id,
        }


@dataclass
class Relayer:
    """中继器"""
    relayer_id: str
    name: str
    chains: List[str]
    status: str = RELAYER_STATUS_ACTIVE
    total_processed: int = 0
    total_fee_earned: float = 0.0
    stake: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "relayer_id": self.relayer_id,
            "name": self.name,
            "chains": self.chains,
            "status": self.status,
            "total_processed": self.total_processed,
            "total_fee_earned": self.total_fee_earned,
            "stake": self.stake,
            "created_at": self.created_at,
        }


@dataclass
class CrossChainMessage:
    """跨链消息"""
    message_id: str
    from_chain: str
    to_chain: str
    sender: str
    recipient: str
    payload: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "from_chain": self.from_chain,
            "to_chain": self.to_chain,
            "sender": self.sender,
            "recipient": self.recipient,
            "payload": self.payload,
            "status": self.status,
            "created_at": self.created_at,
        }


# ========== 跨链桥系统 ==========

class CrossChainBridge:
    """跨链桥系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/cross-chain-bridge"):
        self.data_dir = data_dir
        self.assets: Dict[str, BridgeAsset] = {}
        self.transactions: Dict[str, BridgeTransaction] = {}
        self.relayers: Dict[str, Relayer] = {}
        self.messages: Dict[str, CrossChainMessage] = {}
        self._asset_counter = 0
        self._tx_counter = 0
        self._relayer_counter = 0
        self._message_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 资产管理 ==========

    def register_asset(
        self,
        symbol: str,
        name: str,
        chains: List[str],
        bridge_fee: float = 0.001,
    ) -> Tuple[bool, str]:
        """注册桥接资产"""
        self._asset_counter += 1
        asset_id = f"asset-{self._asset_counter:04d}"

        asset = BridgeAsset(
            asset_id=asset_id,
            symbol=symbol,
            name=name,
            chains=chains,
            bridge_fee=bridge_fee,
        )
        self.assets[asset_id] = asset

        return True, f"资产 {symbol} 注册成功"

    def get_asset(self, symbol: str) -> Optional[BridgeAsset]:
        """获取资产"""
        for asset in self.assets.values():
            if asset.symbol == symbol:
                return asset
        return None

    # ========== 跨链交易 ==========

    def create_bridge_transaction(
        self,
        from_chain: str,
        to_chain: str,
        from_address: str,
        to_address: str,
        asset: str,
        amount: float,
    ) -> Tuple[bool, str]:
        """创建跨链交易"""
        # 检查资产是否支持
        bridge_asset = self.get_asset(asset)
        if not bridge_asset:
            return False, f"资产 {asset} 未注册"

        if from_chain not in bridge_asset.chains or to_chain not in bridge_asset.chains:
            return False, f"资产 {asset} 不支持 {from_chain} → {to_chain}"

        # 计算手续费
        fee = amount * bridge_asset.bridge_fee

        self._tx_counter += 1
        tx_id = f"bridge-tx-{self._tx_counter:06d}"

        tx = BridgeTransaction(
            tx_id=tx_id,
            from_chain=from_chain,
            to_chain=to_chain,
            from_address=from_address,
            to_address=to_address,
            asset=asset,
            amount=amount,
            fee=fee,
        )
        self.transactions[tx_id] = tx

        return True, f"跨链交易 {tx_id} 创建成功 (手续费: {fee:.6f})"

    def lock_assets(self, tx_id: str, lock_tx_hash: str) -> Tuple[bool, str]:
        """锁定资产（源链）"""
        tx = self.transactions.get(tx_id)
        if not tx:
            return False, f"交易 {tx_id} 不存在"

        if tx.status != BRIDGE_STATUS_PENDING:
            return False, f"交易 {tx_id} 状态为 {tx.status}，不可锁定"

        tx.status = BRIDGE_STATUS_LOCKED
        tx.lock_tx_hash = lock_tx_hash

        return True, f"资产已锁定 (tx_hash: {lock_tx_hash[:16]}...)"

    def mint_assets(self, tx_id: str, mint_tx_hash: str, relayer_id: str) -> Tuple[bool, str]:
        """铸造资产（目标链）"""
        tx = self.transactions.get(tx_id)
        if not tx:
            return False, f"交易 {tx_id} 不存在"

        if tx.status != BRIDGE_STATUS_LOCKED:
            return False, f"交易 {tx_id} 状态为 {tx.status}，不可铸造"

        tx.status = BRIDGE_STATUS_MINTED
        tx.mint_tx_hash = mint_tx_hash
        tx.relayer_id = relayer_id

        return True, f"资产已铸造 (tx_hash: {mint_tx_hash[:16]}...)"

    def complete_transaction(self, tx_id: str) -> Tuple[bool, str]:
        """完成跨链交易"""
        tx = self.transactions.get(tx_id)
        if not tx:
            return False, f"交易 {tx_id} 不存在"

        if tx.status != BRIDGE_STATUS_MINTED:
            return False, f"交易 {tx_id} 状态为 {tx.status}，不可完成"

        tx.status = BRIDGE_STATUS_COMPLETED
        tx.completed_at = datetime.now().isoformat()

        # 更新中继器统计
        relayer = self.relayers.get(tx.relayer_id)
        if relayer:
            relayer.total_processed += 1
            relayer.total_fee_earned += tx.fee

        return True, f"跨链交易 {tx_id} 已完成"

    # ========== 中继器管理 ==========

    def register_relayer(
        self,
        name: str,
        chains: List[str],
        stake: float = 100.0,
    ) -> Tuple[bool, str]:
        """注册中继器"""
        self._relayer_counter += 1
        relayer_id = f"relayer-{self._relayer_counter:04d}"

        relayer = Relayer(
            relayer_id=relayer_id,
            name=name,
            chains=chains,
            stake=stake,
        )
        self.relayers[relayer_id] = relayer

        return True, f"中继器 {name} 注册成功"

    def get_active_relayer(self, from_chain: str, to_chain: str) -> Optional[Relayer]:
        """获取活跃中继器"""
        for relayer in self.relayers.values():
            if relayer.status == RELAYER_STATUS_ACTIVE:
                if from_chain in relayer.chains and to_chain in relayer.chains:
                    return relayer
        return None

    def slash_relayer(self, relayer_id: str, reason: str = "") -> Tuple[bool, str]:
        """罚没中继器"""
        relayer = self.relayers.get(relayer_id)
        if not relayer:
            return False, f"中继器 {relayer_id} 不存在"

        relayer.status = RELAYER_STATUS_SLASHED
        return True, f"中继器 {relayer_id} 已被罚没: {reason}"

    # ========== 跨链消息 ==========

    def send_cross_chain_message(
        self,
        from_chain: str,
        to_chain: str,
        sender: str,
        recipient: str,
        payload: str,
    ) -> Tuple[bool, str]:
        """发送跨链消息"""
        self._message_counter += 1
        message_id = f"message-{self._message_counter:06d}"

        message = CrossChainMessage(
            message_id=message_id,
            from_chain=from_chain,
            to_chain=to_chain,
            sender=sender,
            recipient=recipient,
            payload=payload,
        )
        self.messages[message_id] = message

        return True, f"跨链消息 {message_id} 发送成功"

    def receive_cross_chain_message(self, message_id: str) -> Tuple[bool, str]:
        """接收跨链消息"""
        message = self.messages.get(message_id)
        if not message:
            return False, f"消息 {message_id} 不存在"

        if message.status != "pending":
            return False, f"消息 {message_id} 状态为 {message.status}，不可接收"

        message.status = "received"
        return True, f"跨链消息 {message_id} 已接收"

    # ========== 安全监控 ==========

    def get_bridge_statistics(self) -> Dict:
        """获取桥接统计"""
        total_volume = sum(tx.amount for tx in self.transactions.values() if tx.status == BRIDGE_STATUS_COMPLETED)
        total_fees = sum(tx.fee for tx in self.transactions.values())

        return {
            "total_assets": len(self.assets),
            "total_transactions": len(self.transactions),
            "completed_transactions": len([tx for tx in self.transactions.values() if tx.status == BRIDGE_STATUS_COMPLETED]),
            "total_volume": total_volume,
            "total_fees": total_fees,
            "total_relayers": len(self.relayers),
            "active_relayers": len([r for r in self.relayers.values() if r.status == RELAYER_STATUS_ACTIVE]),
            "total_messages": len(self.messages),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "assets": {aid: a.to_dict() for aid, a in self.assets.items()},
            "transactions": {tid: t.to_dict() for tid, t in self.transactions.items()},
            "relayers": {rid: r.to_dict() for rid, r in self.relayers.items()},
            "messages": {mid: m.to_dict() for mid, m in self.messages.items()},
            "counters": {
                "asset": self._asset_counter,
                "tx": self._tx_counter,
                "relayer": self._relayer_counter,
                "message": self._message_counter,
            },
        }
        with open(os.path.join(self.data_dir, "bridge_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "bridge_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.assets = {aid: BridgeAsset(**a) for aid, a in data.get("assets", {}).items()}
            self.transactions = {tid: BridgeTransaction(**t) for tid, t in data.get("transactions", {}).items()}
            self.relayers = {rid: Relayer(**r) for rid, r in data.get("relayers", {}).items()}
            self.messages = {mid: CrossChainMessage(**m) for mid, m in data.get("messages", {}).items()}

            counters = data.get("counters", {})
            self._asset_counter = counters.get("asset", 0)
            self._tx_counter = counters.get("tx", 0)
            self._relayer_counter = counters.get("relayer", 0)
            self._message_counter = counters.get("message", 0)

            return True
        return False
