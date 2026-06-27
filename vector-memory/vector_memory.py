#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 向量记忆系统
版本: V1.0 | 日期: 2026-06-27
功能: 基于向量数据库的智能体记忆系统，支持语义搜索和长期记忆
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class VectorMemory:
    """向量记忆系统"""
    
    def __init__(self, storage_path: str = None):
        if storage_path is None:
            # 优先 /shared，fallback 到本地
            shared_path = "/shared/training/go/vector_memory"
            local_path = os.path.expanduser("~/.lobster-network/vector_memory")
            if os.access("/shared/training/go", os.W_OK):
                storage_path = shared_path
            else:
                storage_path = local_path
        self.storage_path = storage_path
        self.collections = {
            "episodic": [],      # 事件记忆
            "semantic": [],      # 语义记忆
            "procedural": []     # 程序记忆
        }
        self.metadata = {}
        self._ensure_storage()
        self._load_data()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
        for collection in self.collections.keys():
            os.makedirs(os.path.join(self.storage_path, collection), exist_ok=True)
    
    def _load_data(self):
        """加载现有数据"""
        for collection, items in self.collections.items():
            collection_path = os.path.join(self.storage_path, f"{collection}.json")
            if os.path.exists(collection_path):
                with open(collection_path, "r", encoding="utf-8") as f:
                    self.collections[collection] = json.load(f)
    
    def _save_data(self):
        """保存数据"""
        for collection, items in self.collections.items():
            collection_path = os.path.join(self.storage_path, f"{collection}.json")
            with open(collection_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
    
    def add_memory(self, memory_type: str, content: str, metadata: Dict = None) -> str:
        """添加记忆"""
        if memory_type not in self.collections:
            raise ValueError(f"未知记忆类型: {memory_type}")
        
        # 生成唯一ID
        memory_id = hashlib.md5(f"{memory_type}:{content}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        memory = {
            "id": memory_id,
            "type": memory_type,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0,
            "importance": self._calculate_importance(content, metadata)
        }
        
        self.collections[memory_type].append(memory)
        self._save_data()
        
        return memory_id
    
    def search(self, query: str, memory_type: str = None, top_k: int = 5) -> List[Dict]:
        """搜索记忆"""
        results = []
        
        # 确定搜索范围
        if memory_type:
            collections = {memory_type: self.collections.get(memory_type, [])}
        else:
            collections = self.collections
        
        # 简单关键词匹配（实际应使用向量相似度）
        for coll_type, items in collections.items():
            for item in items:
                score = self._calculate_relevance(query, item)
                if score > 0:
                    item_copy = item.copy()
                    item_copy["score"] = score
                    item_copy["access_count"] = item.get("access_count", 0) + 1
                    results.append(item_copy)
        
        # 按相关性排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取记忆"""
        for collection in self.collections.values():
            for item in collection:
                if item["id"] == memory_id:
                    item["access_count"] = item.get("access_count", 0) + 1
                    self._save_data()
                    return item
        return None
    
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        """更新记忆"""
        for collection in self.collections.values():
            for item in collection:
                if item["id"] == memory_id:
                    item.update(updates)
                    item["updated_at"] = datetime.now().isoformat()
                    self._save_data()
                    return True
        return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        for collection in self.collections.values():
            for i, item in enumerate(collection):
                if item["id"] == memory_id:
                    collection.pop(i)
                    self._save_data()
                    return True
        return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total_memories": sum(len(items) for items in self.collections.values()),
            "by_type": {k: len(v) for k, v in self.collections.items()},
            "storage_path": self.storage_path
        }
        return stats
    
    def _calculate_importance(self, content: str, metadata: Dict = None) -> float:
        """计算重要性分数"""
        importance = 0.5  # 基础分数
        
        # 关键词权重
        important_keywords = ["评估", "考核", "晋升", "突破", "关键", "重要"]
        for keyword in important_keywords:
            if keyword in content:
                importance += 0.1
        
        # 元数据权重
        if metadata:
            if metadata.get("priority") == "high":
                importance += 0.2
            elif metadata.get("priority") == "medium":
                importance += 0.1
        
        return min(importance, 1.0)
    
    def _calculate_relevance(self, query: str, item: Dict) -> float:
        """计算相关性分数"""
        content = item.get("content", "").lower()
        query_lower = query.lower()
        
        # 简单关键词匹配
        query_words = query_lower.split()
        match_count = sum(1 for word in query_words if word in content)
        
        if match_count == 0:
            return 0.0
        
        # 基础分数
        score = match_count / len(query_words)
        
        # 重要性加权
        importance = item.get("importance", 0.5)
        score *= (0.5 + importance * 0.5)
        
        # 时间衰减（较新的记忆权重更高）
        created_at = item.get("created_at", "")
        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                days_old = (datetime.now() - created).days
                time_factor = max(0.5, 1.0 - days_old * 0.01)
                score *= time_factor
            except:
                pass
        
        return score
    
    def import_from_files(self, directory: str = "/home/admin/.openclaw/workspace/memory"):
        """从文件导入记忆"""
        if not os.path.exists(directory):
            return
        
        imported = 0
        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 解析日期
                date_str = filename.replace(".md", "")
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    metadata = {
                        "source": "memory_file",
                        "date": date_str,
                        "original_file": filename
                    }
                    
                    self.add_memory("episodic", content, metadata)
                    imported += 1
                except:
                    pass
        
        self._save_data()
        return imported

if __name__ == "__main__":
    # 测试向量记忆系统
    vm = VectorMemory()
    
    print("🦞 向量记忆系统测试")
    print(f"   存储路径: {vm.storage_path}")
    
    # 添加记忆
    print("\n📝 添加记忆...")
    id1 = vm.add_memory("episodic", "2026-06-27: 小陈完成V6 W1D1训练，25题，准确率83.3%", {"date": "2026-06-27", "student": "xiaochen"})
    id2 = vm.add_memory("episodic", "2026-06-27: 诸葛虾完成V6 W1D1训练，33题，准确率76.7%", {"date": "2026-06-27", "student": "zhuguxia"})
    id3 = vm.add_memory("semantic", "围棋九段训练方案V6: 26周训练周期，四阶段路径", {"topic": "training_plan", "version": "V6"})
    id4 = vm.add_memory("procedural", "验证门控规则: 准确率>90%升档，<70%降档，连续3天<60%专项补强", {"topic": "validation"})
    
    print(f"   已添加4条记忆")
    
    # 搜索记忆
    print("\n🔍 搜索记忆...")
    results = vm.search("小陈 训练", top_k=3)
    print(f"   找到 {len(results)} 条结果")
    for r in results:
        print(f"   - {r['content'][:50]}... (score: {r['score']:.2f})")
    
    # 获取记忆
    print("\n📖 获取记忆...")
    memory = vm.get_memory(id1)
    if memory:
        print(f"   找到: {memory['content'][:50]}...")
    
    # 统计信息
    print("\n📊 统计信息:")
    stats = vm.get_stats()
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   按类型: {stats['by_type']}")
    
    print("\n✅ 向量记忆系统测试完成")
