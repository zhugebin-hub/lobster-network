#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 三层记忆系统 (Three-Layer Memory System)
实现短期工作记忆、中期会话记忆、长期知识记忆的自动流转与检索。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import json
import os
import time
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

@dataclass
class MemoryItem:
    """记忆单元"""
    id: str
    content: str
    timestamp: float
    type: str = "short"  # short, medium, long
    tags: List[str] = field(default_factory=list)
    importance: float = 0.5
    access_count: int = 0
    last_access: float = 0.0
    
    def to_dict(self):
        return asdict(self)

class ThreeLayerMemory:
    """三层记忆核心引擎"""
    
    def __init__(self, base_dir: str = "/home/admin/lobster-network/shared/memory"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
        self.short_term: List[MemoryItem] = []
        self.medium_term_file = os.path.join(base_dir, "medium_term.json")
        self.long_term_file = os.path.join(base_dir, "long_term.json")
        
        self._load()
        print(f"🧠 三层记忆系统初始化完成: {base_dir}")
        
    def _load(self):
        """加载持久化记忆"""
        if os.path.exists(self.medium_term_file):
            with open(self.medium_term_file, 'r') as f:
                data = json.load(f)
                self.medium_term = [MemoryItem(**item) for item in data]
        else:
            self.medium_term = []
            
        if os.path.exists(self.long_term_file):
            with open(self.long_term_file, 'r') as f:
                data = json.load(f)
                self.long_term = [MemoryItem(**item) for item in data]
        else:
            self.long_term = []
            
    def _save(self):
        """持久化记忆"""
        with open(self.medium_term_file, 'w') as f:
            json.dump([m.to_dict() for m in self.medium_term], f, ensure_ascii=False, indent=2)
        with open(self.long_term_file, 'w') as f:
            json.dump([m.to_dict() for m in self.long_term], f, ensure_ascii=False, indent=2)
            
    def add_short(self, content: str, tags: List[str] = None, importance: float = 0.5) -> str:
        """添加短期记忆"""
        item = MemoryItem(
            id=hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:8],
            content=content,
            timestamp=time.time(),
            type="short",
            tags=tags or [],
            importance=importance
        )
        self.short_term.append(item)
        # 短期记忆上限 50 条，超出自动转入中期
        if len(self.short_term) > 50:
            self._consolidate()
        return item.id
        
    def _consolidate(self):
        """记忆巩固：短期 -> 中期"""
        if not self.short_term:
            return
            
        # 按重要性排序，取前 20% 转入中期
        self.short_term.sort(key=lambda x: x.importance, reverse=True)
        transfer_count = max(1, len(self.short_term) // 5)
        transfer_items = self.short_term[:transfer_count]
        
        for item in transfer_items:
            item.type = "medium"
            self.medium_term.append(item)
            
        self.short_term = self.short_term[transfer_count:]
        self._save()
        print(f"🔄 记忆巩固: {len(transfer_items)} 条短期记忆转入中期")
        
    def add_medium(self, content: str, tags: List[str] = None) -> str:
        """添加中期记忆"""
        item = MemoryItem(
            id=hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:8],
            content=content,
            timestamp=time.time(),
            type="medium",
            tags=tags or [],
            importance=0.7
        )
        self.medium_term.append(item)
        self._save()
        return item.id
        
    def add_long(self, content: str, tags: List[str] = None) -> str:
        """添加长期记忆"""
        item = MemoryItem(
            id=hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:8],
            content=content,
            timestamp=time.time(),
            type="long",
            tags=tags or [],
            importance=0.9
        )
        self.long_term.append(item)
        self._save()
        return item.id
        
    def retrieve(self, query: str, layer: str = "all", limit: int = 5) -> List[MemoryItem]:
        """检索记忆"""
        results = []
        search_layers = [self.short_term, self.medium_term, self.long_term] if layer == "all" else []
        if layer == "short": search_layers = [self.short_term]
        elif layer == "medium": search_layers = [self.medium_term]
        elif layer == "long": search_layers = [self.long_term]
        
        for layer_mem in search_layers:
            for item in layer_mem:
                if query.lower() in item.content.lower() or any(query.lower() in t.lower() for t in item.tags):
                    item.access_count += 1
                    item.last_access = time.time()
                    results.append(item)
                    
        # 按相关度/重要性排序
        results.sort(key=lambda x: (x.importance, x.access_count), reverse=True)
        return results[:limit]
        
    def get_stats(self) -> Dict[str, int]:
        """获取记忆统计"""
        return {
            "short_term": len(self.short_term),
            "medium_term": len(self.medium_term),
            "long_term": len(self.long_term),
            "total": len(self.short_term) + len(self.medium_term) + len(self.long_term)
        }

# 示例用法
if __name__ == "__main__":
    mem = ThreeLayerMemory()
    
    # 添加短期记忆
    mem.add_short("今日站会：qoder 完成数据源爬取脚本", tags=["standup", "qoder"], importance=0.8)
    mem.add_short("耐虾肽-1 结合自由能 -12.3 kcal/mol", tags=["drug", "docking"], importance=0.9)
    mem.add_short("MQTT Broker 已恢复运行", tags=["infra", "mqtt"], importance=0.6)
    
    print("\n📊 记忆统计:", mem.get_stats())
    print("\n🔍 检索 'drug':", [m.content for m in mem.retrieve("drug")])
    
    # 模拟大量短期记忆触发巩固
    for i in range(55):
        mem.add_short(f"临时数据点 {i}", importance=0.3)
        
    print("\n📊 巩固后统计:", mem.get_stats())
    print("✅ 三层记忆系统测试完成")
