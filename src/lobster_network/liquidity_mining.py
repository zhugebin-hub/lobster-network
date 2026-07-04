#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络流动性挖矿系统 V2.2
为流动性提供者提供额外奖励

功能：
1. 挖矿池创建/管理
2. 流动性质押
3. 奖励分配
4. 挖矿周期管理
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

from .token_economy import TokenEconomy


# ========== 常量定义 ==========

# 挖矿池状态
POOL_STATUS_INACTIVE = "inactive"    # 未激活
POOL_STATUS_ACTIVE = "active"        # 活跃
POOL_STATUS_CLOSED = "closed"        # 已关闭

# 挖矿奖励类型
REWARD_TYPE_FIXED = "fixed"          # 固定奖励
REWARD_TYPE_PROPORTIONAL = "proportional"  # 按比例奖励


# ========== 数据类定义 ==========

@dataclass
class MiningPool:
    """挖矿池"""
    pool_id: str
    name: str
    pair_id: str
    reward_token: str
    reward_rate: float  # 每日奖励量
    reward_type: str = REWARD_TYPE_FIXED
    total_staked: float = 0.0
    total_shares: float = 0.0
    status: str = POOL_STATUS_INACTIVE
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "pool_id": self.pool_id,
            "name": self.name,
            "pair_id": self.pair_id,
            "reward_token": self.reward_token,
            "reward_rate": self.reward_rate,
            "reward_type": self.reward_type,
            "total_staked": self.total_staked,
            "total_shares": self.total_shares,
            "status": self.status,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "created_at": self.created_at,
            "metadata": self.metadata,
        }


@dataclass
class MiningPosition:
    """挖矿头寸"""
    position_id: str
    pool_id: str
    staker_id: str
    shares: float
    staked_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    pending_rewards: float = 0.0
    total_rewards: float = 0.0

    def to_dict(self) -> dict:
        return {
            "position_id": self.position_id,
            "pool_id": self.pool_id,
            "staker_id": self.staker_id,
            "shares": self.shares,
            "staked_at": self.staked_at,
            "updated_at": self.updated_at,
            "pending_rewards": self.pending_rewards,
            "total_rewards": self.total_rewards,
        }


@dataclass
class RewardRecord:
    """奖励记录"""
    record_id: str
    pool_id: str
    staker_id: str
    amount: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "pool_id": self.pool_id,
            "staker_id": self.staker_id,
            "amount": self.amount,
            "timestamp": self.timestamp,
        }


# ========== 流动性挖矿系统 ==========

class LiquidityMining:
    """流动性挖矿系统"""

    def __init__(self, token_economy: TokenEconomy, data_dir: str = "/shared/lobster-network-data/mining"):
        self.token_economy = token_economy
        self.data_dir = data_dir
        self.pools: Dict[str, MiningPool] = {}
        self.positions: Dict[str, MiningPosition] = {}
        self.reward_records: List[RewardRecord] = []
        self._pool_counter = 0
        self._position_counter = 0
        self._record_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 挖矿池管理 ==========

    def create_pool(
        self,
        name: str,
        pair_id: str,
        reward_token: str = "🦞",
        reward_rate: float = 100.0,
        reward_type: str = REWARD_TYPE_FIXED,
        duration_days: int = 30,
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """创建挖矿池"""
        self._pool_counter += 1
        pool_id = f"pool-{self._pool_counter:04d}"

        # 计算开始和结束时间
        now = datetime.now()
        start_time = now.isoformat()
        end_time = (now + timedelta(days=duration_days)).isoformat()

        pool = MiningPool(
            pool_id=pool_id,
            name=name,
            pair_id=pair_id,
            reward_token=reward_token,
            reward_rate=reward_rate,
            reward_type=reward_type,
            start_time=start_time,
            end_time=end_time,
            metadata=metadata or {},
        )
        self.pools[pool_id] = pool

        return True, f"挖矿池 {pool_id} 创建成功 ({name})"

    def activate_pool(self, pool_id: str) -> Tuple[bool, str]:
        """激活挖矿池"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"挖矿池 {pool_id} 不存在"

        if pool.status != POOL_STATUS_INACTIVE:
            return False, f"挖矿池 {pool_id} 状态为 {pool.status}，不可激活"

        pool.status = POOL_STATUS_ACTIVE
        return True, f"挖矿池 {pool_id} 已激活"

    def close_pool(self, pool_id: str) -> Tuple[bool, str]:
        """关闭挖矿池"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"挖矿池 {pool_id} 不存在"

        if pool.status != POOL_STATUS_ACTIVE:
            return False, f"挖矿池 {pool_id} 状态为 {pool.status}，不可关闭"

        pool.status = POOL_STATUS_CLOSED
        return True, f"挖矿池 {pool_id} 已关闭"

    # ========== 质押管理 ==========

    def stake(
        self,
        pool_id: str,
        staker_id: str,
        shares: float,
    ) -> Tuple[bool, str]:
        """质押流动性份额"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"挖矿池 {pool_id} 不存在"

        if pool.status != POOL_STATUS_ACTIVE:
            return False, f"挖矿池 {pool_id} 状态为 {pool.status}，不可质押"

        # 查找是否已有头寸
        existing_position = None
        for pos in self.positions.values():
            if pos.pool_id == pool_id and pos.staker_id == staker_id:
                existing_position = pos
                break

        if existing_position:
            existing_position.shares += shares
            existing_position.updated_at = datetime.now().isoformat()
        else:
            self._position_counter += 1
            position_id = f"position-{self._position_counter:06d}"

            position = MiningPosition(
                position_id=position_id,
                pool_id=pool_id,
                staker_id=staker_id,
                shares=shares,
            )
            self.positions[position_id] = position

        pool.total_staked += shares
        pool.total_shares += shares

        return True, f"质押成功: {shares} 份额"

    def unstake(
        self,
        pool_id: str,
        staker_id: str,
        shares: float,
    ) -> Tuple[bool, str]:
        """解除质押"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"挖矿池 {pool_id} 不存在"

        # 查找头寸
        position = None
        for pos in self.positions.values():
            if pos.pool_id == pool_id and pos.staker_id == staker_id:
                position = pos
                break

        if not position:
            return False, f"头寸不存在"

        if position.shares < shares:
            return False, f"份额不足: {position.shares} < {shares}"

        # 计算待领取奖励
        rewards = self.calculate_rewards(pool_id, staker_id)

        # 更新头寸
        position.shares -= shares
        position.updated_at = datetime.now().isoformat()
        pool.total_staked -= shares
        pool.total_shares -= shares

        return True, f"解除质押成功: {shares} 份额，待领取奖励: {rewards:.4f} {pool.reward_token}"

    # ========== 奖励分配 ==========

    def calculate_rewards(self, pool_id: str, staker_id: str) -> float:
        """计算待领取奖励"""
        pool = self.pools.get(pool_id)
        if not pool:
            return 0.0

        # 查找头寸
        position = None
        for pos in self.positions.values():
            if pos.pool_id == pool_id and pos.staker_id == staker_id:
                position = pos
                break

        if not position or position.shares == 0:
            return 0.0

        # 计算时间
        if pool.start_time and pool.end_time:
            try:
                start = datetime.strptime(pool.start_time, "%Y-%m-%dT%H:%M:%S.%f") if "." in pool.start_time else datetime.strptime(pool.start_time, "%Y-%m-%dT%H:%M:%S")
                end = datetime.strptime(pool.end_time, "%Y-%m-%dT%H:%M:%S.%f") if "." in pool.end_time else datetime.strptime(pool.end_time, "%Y-%m-%dT%H:%M:%S")
                now = datetime.now()
                elapsed = (now - start).total_seconds() / 86400  # 转换为天
                total_days = (end - start).total_seconds() / 86400

                if elapsed > total_days:
                    elapsed = total_days
            except ValueError:
                elapsed = 0
        else:
            elapsed = 0

        # 计算奖励
        if pool.reward_type == REWARD_TYPE_FIXED:
            # 固定奖励：按时间线性分配
            total_reward = pool.reward_rate * elapsed
            staker_share = position.shares / pool.total_shares if pool.total_shares > 0 else 0
            rewards = total_reward * staker_share
        else:
            # 按比例奖励：按质押比例分配
            staker_share = position.shares / pool.total_shares if pool.total_shares > 0 else 0
            rewards = pool.reward_rate * elapsed * staker_share

        return max(0, rewards)

    def claim_rewards(self, pool_id: str, staker_id: str) -> Tuple[bool, str]:
        """领取奖励"""
        pool = self.pools.get(pool_id)
        if not pool:
            return False, f"挖矿池 {pool_id} 不存在"

        # 查找头寸
        position = None
        for pos in self.positions.values():
            if pos.pool_id == pool_id and pos.staker_id == staker_id:
                position = pos
                break

        if not position:
            return False, f"头寸不存在"

        # 计算奖励
        rewards = self.calculate_rewards(pool_id, staker_id)
        if rewards <= 0:
            return False, "无待领取奖励"

        # 发放奖励
        self.token_economy.reward_task(f"mining-{pool_id}", staker_id, rewards)

        # 更新头寸
        position.pending_rewards += rewards
        position.total_rewards += rewards

        # 记录奖励
        self._record_counter += 1
        record = RewardRecord(
            record_id=f"reward-{self._record_counter:06d}",
            pool_id=pool_id,
            staker_id=staker_id,
            amount=rewards,
        )
        self.reward_records.append(record)

        return True, f"领取奖励成功: {rewards:.4f} {pool.reward_token}"

    # ========== 查询功能 ==========

    def get_pool(self, pool_id: str) -> Optional[Dict]:
        """获取挖矿池"""
        pool = self.pools.get(pool_id)
        return pool.to_dict() if pool else None

    def get_all_pools(self) -> List[Dict]:
        """获取所有挖矿池"""
        return [p.to_dict() for p in self.pools.values()]

    def get_active_pools(self) -> List[Dict]:
        """获取活跃挖矿池"""
        return [p.to_dict() for p in self.pools.values() if p.status == POOL_STATUS_ACTIVE]

    def get_mining_positions(self, staker_id: str) -> List[Dict]:
        """获取挖矿头寸"""
        positions = [
            p.to_dict() for p in self.positions.values()
            if p.staker_id == staker_id
        ]
        return positions

    def get_reward_records(self, staker_id: str = None, limit: int = 20) -> List[Dict]:
        """获取奖励记录"""
        records = [r.to_dict() for r in self.reward_records]
        if staker_id:
            records = [r for r in records if r["staker_id"] == staker_id]
        return sorted(records, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_mining_statistics(self) -> Dict:
        """获取挖矿统计"""
        total_staked = sum(p.total_staked for p in self.pools.values())
        total_rewards = sum(r.amount for r in self.reward_records)

        return {
            "total_pools": len(self.pools),
            "active_pools": len([p for p in self.pools.values() if p.status == POOL_STATUS_ACTIVE]),
            "total_positions": len(self.positions),
            "total_staked": total_staked,
            "total_rewards": total_rewards,
            "total_reward_records": len(self.reward_records),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "pools": {pid: p.to_dict() for pid, p in self.pools.items()},
            "positions": {pid: p.to_dict() for pid, p in self.positions.items()},
            "reward_records": [r.to_dict() for r in self.reward_records],
            "counters": {
                "pool": self._pool_counter,
                "position": self._position_counter,
                "record": self._record_counter,
            },
        }
        with open(os.path.join(self.data_dir, "mining_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "mining_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.pools = {pid: MiningPool(**p) for pid, p in data.get("pools", {}).items()}
            self.positions = {pid: MiningPosition(**p) for pid, p in data.get("positions", {}).items()}
            self.reward_records = [RewardRecord(**r) for r in data.get("reward_records", [])]

            counters = data.get("counters", {})
            self._pool_counter = counters.get("pool", 0)
            self._position_counter = counters.get("position", 0)
            self._record_counter = counters.get("record", 0)

            return True
        return False
