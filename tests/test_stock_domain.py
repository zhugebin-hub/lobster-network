#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
炒股模块测试
测试交易引擎、学习引擎、世界地图集成
"""

import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from domains.stock.trade_engine import TradeEngine
from domains.stock.learn_engine import LearnEngine
from engine.world_map import WorldMap


class TestTradeEngine(unittest.TestCase):
    """测试交易引擎"""
    
    def setUp(self):
        """创建交易引擎"""
        self.engine = TradeEngine(initial_capital=1_000_000)
    
    def test_initial_state(self):
        """测试初始状态"""
        status = self.engine.get_account_status()
        self.assertEqual(status["initial_capital"], 1_000_000)
        self.assertEqual(status["cash"], 1_000_000)
        self.assertEqual(status["positions_count"], 0)
        self.assertEqual(status["return_rate"], 0)
    
    def test_buy_stock(self):
        """测试买入股票"""
        result = self.engine.execute_trade("sh600519", "buy", 100, 1257.00)
        
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["symbol"], "sh600519")
        self.assertEqual(result["action"], "buy")
        self.assertEqual(result["quantity"], 100)
        self.assertEqual(result["price"], 1257.00)
        
        # 检查现金
        status = self.engine.get_account_status()
        self.assertEqual(status["cash"], 1_000_000 - 100 * 1257.00)
        
        # 检查持仓
        positions = self.engine.get_positions()
        self.assertIn("sh600519", positions)
        self.assertEqual(positions["sh600519"]["quantity"], 100)
        self.assertEqual(positions["sh600519"]["cost"], 1257.00)
    
    def test_sell_stock(self):
        """测试卖出股票"""
        # 先买入
        self.engine.execute_trade("sh600519", "buy", 100, 1257.00)
        
        # 再卖出
        result = self.engine.execute_trade("sh600519", "sell", 50, 1300.00)
        
        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["action"], "sell")
        self.assertEqual(result["quantity"], 50)
        
        # 检查持仓
        positions = self.engine.get_positions()
        self.assertEqual(positions["sh600519"]["quantity"], 50)
    
    def test_risk_limits(self):
        """测试风险限制"""
        # 单只股票超仓位限制（30%）
        result = self.engine.execute_trade("sh600519", "buy", 300, 1257.00)
        self.assertEqual(result["status"], "rejected")
        self.assertIn("仓位超限", result["reason"])
    
    def test_cash_insufficient(self):
        """测试总仓位限制"""
        # 先买入（在单只股票限制内：30%）
        self.engine.execute_trade("sh600519", "buy", 200, 1257.00)  # 251,400 元 (25.14%)
        
        # 再买入另一只股票（总仓位：251,400 + 500,000 = 751,400 < 800,000，通过）
        self.engine.execute_trade("sz300750", "buy", 200, 400.00)  # 80,000 元
        
        # 总仓位：251,400 + 80,000 = 331,400 元 (33.14%)
        
        # 再买入应该失败（超过 80% 总仓位限制）
        result = self.engine.execute_trade("hk00700", "buy", 1000, 450.00)  # 450,000 元
        self.assertEqual(result["status"], "rejected")
        self.assertIn("仓位超限", result["reason"])
    
    def test_sell_without_holding(self):
        """测试无持仓卖出"""
        result = self.engine.execute_trade("sh600519", "sell", 100, 1257.00)
        self.assertEqual(result["status"], "rejected")
        self.assertIn("持仓不足", result["reason"])
    
    def test_trade_history(self):
        """测试交易历史"""
        self.engine.execute_trade("sh600519", "buy", 100, 1257.00)
        self.engine.execute_trade("sz300750", "buy", 200, 400.00)
        
        history = self.engine.get_trade_history()
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["symbol"], "sh600519")
        self.assertEqual(history[1]["symbol"], "sz300750")
    
    def test_calculate_pnl(self):
        """测试盈亏计算"""
        self.engine.execute_trade("sh600519", "buy", 100, 1257.00)
        
        # 更新市值（模拟）
        self.engine.positions["sh600519"]["market_value"] = 130000
        
        pnl = self.engine.calculate_pnl()
        self.assertGreater(pnl["total_pnl"], 0)  # 盈利
        self.assertGreater(pnl["total_pnl_pct"], 0)


class TestLearnEngine(unittest.TestCase):
    """测试学习引擎"""
    
    def setUp(self):
        """创建学习引擎"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="stock-test-wm", storage_dir=self.test_dir)
        self.engine = LearnEngine(world_map=self.wm)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_add_strategy(self):
        """测试添加策略"""
        strategy = self.engine.add_strategy("trend_001", {
            "name": "趋势跟踪策略",
            "description": "基于 SMA20/SMA50 的趋势跟踪策略",
            "type": "trend_following",
            "indicators": ["SMA20", "SMA50"],
        })
        
        self.assertEqual(strategy["strategy_id"], "trend_001")
        self.assertEqual(strategy["name"], "趋势跟踪策略")
        self.assertEqual(strategy["type"], "trend_following")
        
        # 检查世界地图
        chunks = self.wm.search_chunks(domain="stock")
        self.assertGreater(len(chunks), 0)
    
    def test_add_experience(self):
        """测试添加经验"""
        experience = self.engine.add_experience({
            "trade_id": "trade_001",
            "symbol": "sh600519",
            "action": "buy",
            "result": "盈利",
            "lesson": "趋势跟踪策略有效",
        })
        
        self.assertIn("experience_id", experience)
        self.assertEqual(experience["symbol"], "sh600519")
        self.assertEqual(experience["lesson"], "趋势跟踪策略有效")
    
    def test_add_insight(self):
        """测试添加洞察"""
        insight = self.engine.add_insight({
            "title": "技术 + 基本面融合策略",
            "description": "技术分析确定入场时机，基本面分析确定选股方向",
            "source_dialogue": "dlg_001",
            "participants": ["lobster-001", "hermes"],
            "emergence_score": 0.75,
        })
        
        self.assertIn("insight_id", insight)
        self.assertEqual(insight["title"], "技术 + 基本面融合策略")
        self.assertEqual(insight["emergence_score"], 0.75)
        
        # 检查世界地图宝藏
        treasures = self.wm._map["treasures"]
        self.assertIn(insight["insight_id"], treasures)
    
    def test_optimize_strategy(self):
        """测试优化策略"""
        # 添加策略
        self.engine.add_strategy("trend_001", {
            "name": "趋势跟踪策略",
            "description": "初始版本",
            "type": "trend_following",
        })
        
        # 优化策略
        optimized = self.engine.optimize_strategy("trend_001", {
            "description": "优化版本",
            "indicators": ["SMA20", "SMA50", "MACD"],
        })
        
        self.assertEqual(optimized["description"], "优化版本")
        self.assertEqual(len(optimized["indicators"]), 3)
        self.assertEqual(optimized["version"], 2)


class TestStockWorldMapIntegration(unittest.TestCase):
    """测试炒股模块与世界地图集成"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="stock-integration-wm", storage_dir=self.test_dir)
        self.trade_engine = TradeEngine(initial_capital=1_000_000)
        self.learn_engine = LearnEngine(world_map=self.wm)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_trade_knowledge_chunk(self):
        """测试交易知识碎片"""
        # 执行交易
        self.trade_engine.execute_trade("sh600519", "buy", 100, 1257.00)
        
        # 添加策略
        self.learn_engine.add_strategy("value_investing", {
            "name": "价值投资策略",
            "description": "基于 PE/PB 的价值投资策略",
            "type": "value_investing",
            "indicators": ["PE", "PB", "ROE"],
        })
        
        # 搜索股票相关碎片
        chunks = self.wm.search_chunks(domain="stock")
        self.assertGreater(len(chunks), 0)
        
        # 验证碎片内容
        chunk = chunks[0]
        self.assertEqual(chunk["domain"], "stock")
        self.assertIn("strategy", chunk["chunk_id"])
    
    def test_emergence_treasure(self):
        """测试涌现宝藏"""
        # 添加洞察（高涌现）
        insight = self.learn_engine.add_insight({
            "title": "半导体板块轮动规律",
            "description": "半导体板块 3-5 年周期轮动规律",
            "source_dialogue": "dlg_002",
            "participants": ["lobster-001", "hermes", "xiaochen"],
            "emergence_score": 0.85,
            "related_strategies": ["trend_001"],
        })
        
        # 验证宝藏
        treasure = self.wm.get_treasure(insight["insight_id"])
        self.assertIsNotNone(treasure)
        self.assertEqual(treasure["rarity"], "rare")  # 高涌现 = 稀有宝藏
        self.assertIn("lobster-001", treasure["unlocked_by"])


if __name__ == "__main__":
    unittest.main()
