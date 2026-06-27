#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学习引擎 (Learn Engine)
负责策略优化、经验积累、知识传承
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class LearnEngine:
    """学习引擎 - 多智能体协作学习"""
    
    def __init__(self, world_map=None):
        """
        初始化学习引擎
        
        Args:
            world_map: 世界地图实例（用于知识碎片管理）
        """
        self.world_map = world_map
        self.strategies = {}  # 策略库
        self.experiences = []  # 经验记录
        self.insights = []  # 涌现洞察
    
    def add_strategy(self, strategy_id: str, strategy_data: Dict) -> Dict:
        """
        添加策略到策略库
        
        Args:
            strategy_id: 策略 ID
            strategy_data: 策略数据
        
        Returns:
            策略信息
        """
        strategy = {
            "strategy_id": strategy_id,
            "name": strategy_data.get("name", ""),
            "description": strategy_data.get("description", ""),
            "type": strategy_data.get("type", "unknown"),
            "indicators": strategy_data.get("indicators", []),
            "entry_condition": strategy_data.get("entry_condition", ""),
            "exit_condition": strategy_data.get("exit_condition", ""),
            "backtest_result": strategy_data.get("backtest_result", {}),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
        }
        
        self.strategies[strategy_id] = strategy
        
        # 添加到世界地图
        if self.world_map:
            chunk_data = {
                "chunk_id": f"strategy_{strategy_id}",
                "domain": "stock",
                "title": strategy["name"],
                "description": strategy["description"],
                "tags": ["stock", "strategy", strategy["type"]],
                "data": strategy,
            }
            self.world_map.add_chunk(chunk_data, "learn_engine")
        
        return strategy
    
    def add_experience(self, experience_data: Dict) -> Dict:
        """
        添加交易经验
        
        Args:
            experience_data: 经验数据
        
        Returns:
            经验记录
        """
        experience = {
            "experience_id": f"exp_{len(self.experiences) + 1:03d}",
            "trade_id": experience_data.get("trade_id", ""),
            "symbol": experience_data.get("symbol", ""),
            "action": experience_data.get("action", ""),
            "result": experience_data.get("result", ""),
            "lesson": experience_data.get("lesson", ""),
            "timestamp": datetime.now().isoformat(),
        }
        
        self.experiences.append(experience)
        return experience
    
    def add_insight(self, insight_data: Dict) -> Dict:
        """
        添加涌现洞察
        
        Args:
            insight_data: 洞察数据
        
        Returns:
            洞察记录
        """
        insight = {
            "insight_id": f"insight_{len(self.insights) + 1:03d}",
            "title": insight_data.get("title", ""),
            "description": insight_data.get("description", ""),
            "source_dialogue": insight_data.get("source_dialogue", ""),
            "participants": insight_data.get("participants", []),
            "emergence_score": insight_data.get("emergence_score", 0),
            "related_strategies": insight_data.get("related_strategies", []),
            "timestamp": datetime.now().isoformat(),
        }
        
        self.insights.append(insight)
        
        # 添加到世界地图（作为宝藏）
        if self.world_map:
            treasure_data = {
                "treasure_id": insight["insight_id"],
                "title": insight["title"],
                "description": insight["description"],
                "rarity": "rare" if insight["emergence_score"] > 0.6 else "common",
                "insight": insight["description"],
                "source_dialogue_id": insight["source_dialogue"],
                "related_chunks": [f"strategy_{s}" for s in insight["related_strategies"]],
            }
            self.world_map.unlock_treasure(treasure_data, insight["participants"])
        
        return insight
    
    def get_strategy(self, strategy_id: str) -> Optional[Dict]:
        """获取策略"""
        return self.strategies.get(strategy_id)
    
    def get_strategies(self, strategy_type: str = None) -> List[Dict]:
        """获取策略列表"""
        strategies = list(self.strategies.values())
        if strategy_type:
            strategies = [s for s in strategies if s["type"] == strategy_type]
        return strategies
    
    def get_experiences(self, limit: int = 100) -> List[Dict]:
        """获取经验记录"""
        return self.experiences[-limit:]
    
    def get_insights(self, limit: int = 50) -> List[Dict]:
        """获取涌现洞察"""
        return self.insights[-limit:]
    
    def optimize_strategy(self, strategy_id: str, optimization_data: Dict) -> Dict:
        """
        优化策略
        
        Args:
            strategy_id: 策略 ID
            optimization_data: 优化数据
        
        Returns:
            优化后的策略
        """
        if strategy_id not in self.strategies:
            raise KeyError(f"策略不存在：{strategy_id}")
        
        strategy = self.strategies[strategy_id]
        
        # 应用优化
        for key, value in optimization_data.items():
            if key in strategy:
                strategy[key] = value
        
        strategy["updated_at"] = datetime.now().isoformat()
        strategy["version"] = strategy.get("version", 1) + 1
        
        # 更新世界地图
        if self.world_map:
            chunk_id = f"strategy_{strategy_id}"
            chunk_data = {
                "chunk_id": chunk_id,
                "domain": "stock",
                "title": strategy["name"],
                "description": strategy["description"],
                "tags": ["stock", "strategy", strategy["type"]],
                "data": strategy,
            }
            self.world_map.update_chunk(chunk_id, chunk_data, "learn_engine")
        
        return strategy


if __name__ == "__main__":
    # 测试学习引擎
    from engine.world_map import WorldMap
    import tempfile
    
    test_dir = tempfile.mkdtemp()
    wm = WorldMap(map_id="stock-wm", storage_dir=test_dir)
    
    engine = LearnEngine(world_map=wm)
    
    # 添加策略
    strategy = engine.add_strategy("trend_001", {
        "name": "趋势跟踪策略",
        "description": "基于 SMA20/SMA50 的趋势跟踪策略",
        "type": "trend_following",
        "indicators": ["SMA20", "SMA50"],
        "entry_condition": "SMA20 > SMA50",
        "exit_condition": "SMA20 < SMA50",
    })
    print(f"添加策略：{strategy['name']}")
    
    # 添加经验
    experience = engine.add_experience({
        "trade_id": "trade_001",
        "symbol": "sh600519",
        "action": "buy",
        "result": "盈利",
        "lesson": "趋势跟踪策略在上升通道中表现良好",
    })
    print(f"添加经验：{experience['lesson']}")
    
    # 添加洞察
    insight = engine.add_insight({
        "title": "技术 + 基本面融合策略",
        "description": "技术分析确定入场时机，基本面分析确定选股方向",
        "source_dialogue": "dlg_001",
        "participants": ["lobster-001", "hermes"],
        "emergence_score": 0.75,
        "related_strategies": ["trend_001"],
    })
    print(f"添加洞察：{insight['title']}")
    
    # 查看策略
    strategies = engine.get_strategies()
    print(f"策略数量：{len(strategies)}")
    
    # 查看洞察
    insights = engine.get_insights()
    print(f"洞察数量：{len(insights)}")
