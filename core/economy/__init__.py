#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙虾币 (LBC) 经济系统

参考：小龙虾生态_v3.1补充_Agent劳务市场与经济模型

核心组件：
- LBCWallet:       钱包管理
- SDPPricing:      SDP 定价引擎
- TransactionLedger: 交易账本（不可变）
- MarketOrderBook:  技能市场挂单
- RewardDistributor: 奖励分配
"""

from .lbc_economy import (
    LBCWallet,
    SDPPricing,
    TransactionLedger,
    MarketOrderBook,
    RewardDistributor,
    LBCEconomy,
    INITIAL_ALLOCATIONS,
)

__all__ = [
    "LBCWallet",
    "SDPPricing",
    "TransactionLedger",
    "MarketOrderBook",
    "RewardDistributor",
    "LBCEconomy",
    "INITIAL_ALLOCATIONS",
]
