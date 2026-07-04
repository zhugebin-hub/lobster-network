#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 龙虾币经济系统
版本: V1.0 | 日期: 2026-06-28
功能: 激励训练、惩罚挂机、API调用消耗
"""
import json, os
from datetime import datetime

LEDGER_PATH = "/shared/training/go/ledger.json"

class LobsterCoin:
    def __init__(self):
        self.ledger = self._load()
    
    def _load(self):
        if os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH) as f: return json.load(f)
        return {"balances": {}, "transactions": []}
    
    def _save(self):
        with open(LEDGER_PATH, "w") as f: json.dump(self.ledger, f, ensure_ascii=False, indent=2)
    
    def reward(self, user: str, amount: float, reason: str):
        self.ledger["balances"][user] = self.ledger["balances"].get(user, 0) + amount
        self.ledger["transactions"].append({
            "type": "reward", "user": user, "amount": amount, "reason": reason, "time": datetime.now().isoformat()
        })
        self._save()
        print(f"💰 奖励 {user} +{amount} LC (原因: {reason})")
    
    def charge(self, user: str, amount: float, reason: str):
        if self.ledger["balances"].get(user, 0) < amount:
            raise Exception(f"余额不足！{user} 需要 {amount} LC")
        self.ledger["balances"][user] -= amount
        self.ledger["transactions"].append({
            "type": "charge", "user": user, "amount": -amount, "reason": reason, "time": datetime.now().isoformat()
        })
        self._save()
        print(f"💸 扣费 {user} -{amount} LC (原因: {reason})")
    
    def get_balance(self, user: str) -> float:
        return self.ledger["balances"].get(user, 0)

if __name__ == "__main__":
    coin = LobsterCoin()
    coin.reward("xiaochen", 50, "完成网络协议 Phase 2")
    coin.reward("zhuguxia", 30, "提交高质量复盘")
    coin.charge("xiaochen", 5, "调用 Signal Arena API")
    print(f"📊 余额: 小陈={coin.get_balance('xiaochen')}, 诸葛虾={coin.get_balance('zhuguxia')}")
