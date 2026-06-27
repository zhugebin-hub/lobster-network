#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络多币种支持系统 V2.1
支持多种 token 交易

功能：
1. 多币种钱包
2. 汇率管理
3. 币种兑换
4. 稳定币支持
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ========== 常量定义 ==========

# 币种类型
CURRENCY_TYPE_NATIVE = "native"        # 原生币种 (🦞)
CURRENCY_TYPE_STABLE = "stable"        # 稳定币
CURRENCY_TYPE_TOKEN = "token"          # 代币
CURRENCY_TYPE_NFT = "nft"              # NFT

# 币种列表
CURRENCIES = {
    "🦞": {
        "name": "Lobster",
        "type": CURRENCY_TYPE_NATIVE,
        "symbol": "LOBSTER",
        "decimals": 8,
        "total_supply": 21_000_000,
    },
    "USDT": {
        "name": "Tether",
        "type": CURRENCY_TYPE_STABLE,
        "symbol": "USDT",
        "decimals": 6,
        "total_supply": 0,
    },
    "USDC": {
        "name": "USD Coin",
        "type": CURRENCY_TYPE_STABLE,
        "symbol": "USDC",
        "decimals": 6,
        "total_supply": 0,
    },
    "DAI": {
        "name": "Dai",
        "type": CURRENCY_TYPE_STABLE,
        "symbol": "DAI",
        "decimals": 18,
        "total_supply": 0,
    },
    "ETH": {
        "name": "Ethereum",
        "type": CURRENCY_TYPE_TOKEN,
        "symbol": "ETH",
        "decimals": 18,
        "total_supply": 0,
    },
    "BTC": {
        "name": "Bitcoin",
        "type": CURRENCY_TYPE_TOKEN,
        "symbol": "BTC",
        "decimals": 8,
        "total_supply": 21_000_000,
    },
}

# 汇率 (相对于 🦞)
EXCHANGE_RATES = {
    "🦞/USDT": 0.1,      # 1 🦞 = 0.1 USDT
    "🦞/USDC": 0.1,      # 1 🦞 = 0.1 USDC
    "🦞/DAI": 0.1,       # 1 🦞 = 0.1 DAI
    "🦞/ETH": 0.00005,   # 1 🦞 = 0.00005 ETH
    "🦞/BTC": 0.000003,  # 1 🦞 = 0.000003 BTC
}


# ========== 数据类定义 ==========

@dataclass
class MultiCurrencyWallet:
    """多币种钱包"""
    wallet_id: str
    balances: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_balance(self, currency: str) -> float:
        """获取余额"""
        return self.balances.get(currency, 0.0)

    def add_balance(self, currency: str, amount: float):
        """增加余额"""
        self.balances[currency] = self.balances.get(currency, 0.0) + amount

    def subtract_balance(self, currency: str, amount: float) -> bool:
        """减少余额"""
        current = self.balances.get(currency, 0.0)
        if current < amount:
            return False
        self.balances[currency] = current - amount
        return True

    def to_dict(self) -> dict:
        return {
            "wallet_id": self.wallet_id,
            "balances": self.balances,
            "created_at": self.created_at,
        }


@dataclass
class ExchangeRecord:
    """兑换记录"""
    record_id: str
    from_wallet: str
    to_wallet: str
    from_currency: str
    to_currency: str
    from_amount: float
    to_amount: float
    exchange_rate: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "from_wallet": self.from_wallet,
            "to_wallet": self.to_wallet,
            "from_currency": self.from_currency,
            "to_currency": self.to_currency,
            "from_amount": self.from_amount,
            "to_amount": self.to_amount,
            "exchange_rate": self.exchange_rate,
            "timestamp": self.timestamp,
        }


# ========== 多币种系统 ==========

class MultiCurrencySystem:
    """多币种系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/multi-currency"):
        self.data_dir = data_dir
        self.wallets: Dict[str, MultiCurrencyWallet] = {}
        self.exchange_records: List[ExchangeRecord] = []
        self._record_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 钱包管理 ==========

    def create_wallet(self, wallet_id: str, initial_balances: Dict[str, float] = None) -> Tuple[bool, str]:
        """创建多币种钱包"""
        if wallet_id in self.wallets:
            return False, f"钱包已存在: {wallet_id}"

        wallet = MultiCurrencyWallet(wallet_id=wallet_id)
        if initial_balances:
            for currency, amount in initial_balances.items():
                wallet.add_balance(currency, amount)

        self.wallets[wallet_id] = wallet
        return True, f"钱包 {wallet_id} 创建成功"

    def get_wallet(self, wallet_id: str) -> Optional[MultiCurrencyWallet]:
        """获取钱包"""
        return self.wallets.get(wallet_id)

    def get_balance(self, wallet_id: str, currency: str) -> float:
        """获取余额"""
        wallet = self.wallets.get(wallet_id)
        return wallet.get_balance(currency) if wallet else 0.0

    # ========== 币种管理 ==========

    def get_currencies(self) -> Dict:
        """获取所有币种"""
        return CURRENCIES

    def get_currency_info(self, currency: str) -> Optional[Dict]:
        """获取币种信息"""
        return CURRENCIES.get(currency)

    def add_currency(
        self,
        symbol: str,
        name: str,
        currency_type: str = CURRENCY_TYPE_TOKEN,
        decimals: int = 18,
        total_supply: float = 0,
    ) -> Tuple[bool, str]:
        """添加新币种"""
        if symbol in CURRENCIES:
            return False, f"币种 {symbol} 已存在"

        CURRENCIES[symbol] = {
            "name": name,
            "type": currency_type,
            "symbol": symbol,
            "decimals": decimals,
            "total_supply": total_supply,
        }
        return True, f"币种 {symbol} 添加成功"

    # ========== 汇率管理 ==========

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """获取汇率"""
        # 直接汇率
        direct_key = f"{from_currency}/{to_currency}"
        if direct_key in EXCHANGE_RATES:
            return EXCHANGE_RATES[direct_key]

        # 反向汇率
        reverse_key = f"{to_currency}/{from_currency}"
        if reverse_key in EXCHANGE_RATES:
            return 1.0 / EXCHANGE_RATES[reverse_key]

        # 通过 🦞 中转
        if from_currency != "🦞" and to_currency != "🦞":
            rate_from = self.get_exchange_rate(from_currency, "🦞")
            rate_to = self.get_exchange_rate("🦞", to_currency)
            if rate_from > 0 and rate_to > 0:
                return rate_from * rate_to

        return 0.0

    def set_exchange_rate(self, from_currency: str, to_currency: str, rate: float) -> Tuple[bool, str]:
        """设置汇率"""
        key = f"{from_currency}/{to_currency}"
        EXCHANGE_RATES[key] = rate
        return True, f"汇率 {key} 设置为 {rate}"

    # ========== 币种兑换 ==========

    def exchange(
        self,
        wallet_id: str,
        from_currency: str,
        to_currency: str,
        amount: float,
    ) -> Tuple[bool, str, float]:
        """兑换币种"""
        wallet = self.wallets.get(wallet_id)
        if not wallet:
            return False, f"钱包不存在: {wallet_id}", 0

        # 获取汇率
        rate = self.get_exchange_rate(from_currency, to_currency)
        if rate == 0:
            return False, f"不支持的兑换对: {from_currency}/{to_currency}", 0

        # 检查余额
        if not wallet.subtract_balance(from_currency, amount):
            return False, f"余额不足: {wallet.get_balance(from_currency)} < {amount}", 0

        # 计算兑换数量
        to_amount = amount * rate

        # 增加目标币种余额
        wallet.add_balance(to_currency, to_amount)

        # 记录兑换
        self._record_counter += 1
        record = ExchangeRecord(
            record_id=f"exchange-{self._record_counter:06d}",
            from_wallet=wallet_id,
            to_wallet=wallet_id,
            from_currency=from_currency,
            to_currency=to_currency,
            from_amount=amount,
            to_amount=to_amount,
            exchange_rate=rate,
        )
        self.exchange_records.append(record)

        return True, f"兑换成功: {amount} {from_currency} → {to_amount:.6f} {to_currency}", to_amount

    # ========== 转账 ==========

    def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        currency: str,
        amount: float,
    ) -> Tuple[bool, str]:
        """转账"""
        from_w = self.wallets.get(from_wallet)
        to_w = self.wallets.get(to_wallet)

        if not from_w:
            return False, f"发送方钱包不存在: {from_wallet}"
        if not to_w:
            return False, f"接收方钱包不存在: {to_wallet}"

        if not from_w.subtract_balance(currency, amount):
            return False, f"余额不足: {from_w.get_balance(currency)} < {amount}"

        to_w.add_balance(currency, amount)
        return True, f"转账成功: {amount} {currency}"

    # ========== 查询功能 ==========

    def get_wallet_balances(self, wallet_id: str) -> Dict[str, float]:
        """获取钱包所有余额"""
        wallet = self.wallets.get(wallet_id)
        return wallet.balances.copy() if wallet else {}

    def get_exchange_records(self, wallet_id: str = None, limit: int = 20) -> List[Dict]:
        """获取兑换记录"""
        records = [r.to_dict() for r in self.exchange_records]
        if wallet_id:
            records = [r for r in records if r["from_wallet"] == wallet_id or r["to_wallet"] == wallet_id]
        return sorted(records, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_multi_currency_statistics(self) -> Dict:
        """获取多币种统计"""
        total_balances = {}
        for wallet in self.wallets.values():
            for currency, balance in wallet.balances.items():
                total_balances[currency] = total_balances.get(currency, 0.0) + balance

        return {
            "total_wallets": len(self.wallets),
            "total_currencies": len(CURRENCIES),
            "total_exchange_records": len(self.exchange_records),
            "total_balances": total_balances,
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "wallets": {wid: w.to_dict() for wid, w in self.wallets.items()},
            "exchange_records": [r.to_dict() for r in self.exchange_records],
            "counters": {
                "record": self._record_counter,
            },
        }
        with open(os.path.join(self.data_dir, "multi_currency_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "multi_currency_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.wallets = {wid: MultiCurrencyWallet(**w) for wid, w in data.get("wallets", {}).items()}
            self.exchange_records = [ExchangeRecord(**r) for r in data.get("exchange_records", [])]

            counters = data.get("counters", {})
            self._record_counter = counters.get("record", 0)

            return True
        return False
