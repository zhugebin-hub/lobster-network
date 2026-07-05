#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易引擎 (Trade Engine)
负责买卖决策、仓位管理、订单执行
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class TradeEngine:
    """交易引擎 - 多智能体协作交易决策"""
    
    def __init__(self, initial_capital: float = 1_000_000, currency: str = "CNY"):
        """
        初始化交易引擎
        
        Args:
            initial_capital: 初始资金
            currency: 货币类型 (CNY/USD/HKD)
        """
        self.initial_capital = initial_capital
        self.currency = currency
        self.cash = initial_capital
        self.positions = {}  # 持仓：{symbol: {"quantity": x, "cost": y, ...}}
        self.trade_history = []  # 交易历史
        self.risk_limits = {
            "max_position_pct": 0.3,  # 单只股票最大仓位 30%
            "max_total_position": 0.8,  # 总仓位上限 80%
            "stop_loss_pct": 0.1,  # 止损线 10%
        }
    
    def get_account_status(self) -> Dict:
        """获取账户状态"""
        total_value = self.cash
        for symbol, pos in self.positions.items():
            total_value += pos.get("market_value", pos["cost"] * pos["quantity"])
        
        return {
            "initial_capital": self.initial_capital,
            "current_capital": total_value,
            "cash": self.cash,
            "positions_count": len(self.positions),
            "return_rate": (total_value - self.initial_capital) / self.initial_capital,
            "currency": self.currency,
        }
    
    def check_risk_limits(self, symbol: str, quantity: int, price: float) -> Tuple[bool, str]:
        """
        检查风险限制
        
        Args:
            symbol: 股票代码
            quantity: 交易数量
            price: 交易价格
        
        Returns:
            (是否通过，原因)
        """
        trade_value = quantity * price
        
        # 检查单只股票仓位限制
        max_position_value = self.initial_capital * self.risk_limits["max_position_pct"]
        if trade_value > max_position_value:
            return False, f"单只股票仓位超限（最大 {max_position_value:.0f}）"
        
        # 检查总仓位限制
        current_position_value = sum(
            pos["cost"] * pos["quantity"] for pos in self.positions.values()
        )
        max_total_value = self.initial_capital * self.risk_limits["max_total_position"]
        
        if current_position_value + trade_value > max_total_value:
            return False, f"总仓位超限（最大 {max_total_value:.0f}）"
        
        # 检查现金是否充足
        if trade_value > self.cash:
            return False, f"现金不足（需要 {trade_value:.0f}，可用 {self.cash:.0f}）"
        
        return True, "通过"
    
    def execute_trade(self, symbol: str, action: str, quantity: int, price: float) -> Dict:
        """
        执行交易
        
        Args:
            symbol: 股票代码
            action: 操作 (buy/sell)
            quantity: 数量
            price: 价格
        
        Returns:
            交易结果
        """
        # 风险检查
        passed, reason = self.check_risk_limits(symbol, quantity, price)
        if not passed:
            return {"status": "rejected", "reason": reason}
        
        trade_value = quantity * price
        timestamp = datetime.now().isoformat()
        
        if action == "buy":
            # 买入
            self.cash -= trade_value
            
            if symbol in self.positions:
                pos = self.positions[symbol]
                # 计算加权平均成本
                total_cost = pos["cost"] * pos["quantity"] + trade_value
                total_quantity = pos["quantity"] + quantity
                pos["cost"] = total_cost / total_quantity
                pos["quantity"] = total_quantity
            else:
                self.positions[symbol] = {
                    "quantity": quantity,
                    "cost": price,
                    "market_value": trade_value,
                    "bought_at": timestamp,
                }
            
            trade_record = {
                "symbol": symbol,
                "action": "buy",
                "quantity": quantity,
                "price": price,
                "value": trade_value,
                "timestamp": timestamp,
                "status": "executed",
            }
        
        elif action == "sell":
            # 卖出
            if symbol not in self.positions:
                return {"status": "rejected", "reason": "持仓不足"}
            
            pos = self.positions[symbol]
            if pos["quantity"] < quantity:
                return {"status": "rejected", "reason": f"持仓不足（持有{pos['quantity']}，卖出{quantity}）"}
            
            self.cash += trade_value
            pos["quantity"] -= quantity
            
            if pos["quantity"] == 0:
                del self.positions[symbol]
            
            trade_record = {
                "symbol": symbol,
                "action": "sell",
                "quantity": quantity,
                "price": price,
                "value": trade_value,
                "timestamp": timestamp,
                "status": "executed",
            }
        
        else:
            return {"status": "rejected", "reason": f"未知操作：{action}"}
        
        self.trade_history.append(trade_record)
        return trade_record
    
    def get_positions(self) -> Dict:
        """获取所有持仓"""
        return self.positions.copy()
    
    def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """获取交易历史"""
        return self.trade_history[-limit:]
    
    def calculate_pnl(self) -> Dict:
        """计算盈亏"""
        total_pnl = 0
        position_pnl = {}
        
        for symbol, pos in self.positions.items():
            cost = pos["cost"] * pos["quantity"]
            market_value = pos.get("market_value", cost)
            pnl = market_value - cost
            pnl_pct = pnl / cost if cost > 0 else 0
            
            position_pnl[symbol] = {
                "cost": cost,
                "market_value": market_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
            }
            total_pnl += pnl
        
        return {
            "total_pnl": total_pnl,
            "total_pnl_pct": total_pnl / self.initial_capital,
            "positions": position_pnl,
        }


if __name__ == "__main__":
    # 测试交易引擎
    engine = TradeEngine(initial_capital=1_000_000)
    
    # 买入测试
    result = engine.execute_trade("sh600519", "buy", 100, 1257.00)
    print(f"买入贵州茅台：{result}")
    
    # 查看账户状态
    status = engine.get_account_status()
    print(f"账户状态：{json.dumps(status, indent=2, ensure_ascii=False)}")
    
    # 查看持仓
    positions = engine.get_positions()
    print(f"持仓：{json.dumps(positions, indent=2, ensure_ascii=False)}")
    
    # 计算盈亏
    pnl = engine.calculate_pnl()
    print(f"盈亏：{json.dumps(pnl, indent=2, ensure_ascii=False)}")
