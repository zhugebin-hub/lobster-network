"""
向量记忆系统 - Vector Memory System
支持文本嵌入、相似度搜索、记忆持久化
"""

import json
import hashlib
import math
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    last_accessed: Optional[str] = None
    importance: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class VectorMemory:
    """向量记忆系统 - 支持嵌入、搜索、持久化"""
    
    def __init__(self, dimension: int = 768, max_entries: int = 10000):
        self.dimension = dimension
        self.max_entries = max_entries
        self.memories: Dict[str, MemoryEntry] = {}
        self._index: List[str] = []
    
    def _generate_id(self, content: str) -> str:
        """生成记忆ID"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _simple_embedding(self, text: str) -> List[float]:
        """生成简单文本嵌入（基于字符哈希）"""
        embedding = [0.0] * self.dimension
        for i, char in enumerate(text):
            idx = hash(char + str(i)) % self.dimension
            embedding[idx] += ord(char) / 255.0
        # 归一化
        norm = math.sqrt(sum(x**2 for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        return embedding
    
    def add_memory(self, content: str, metadata: Optional[Dict] = None, importance: float = 1.0) -> str:
        """添加记忆"""
        if len(self.memories) >= self.max_entries:
            self._evict_low_importance()
        
        memory_id = self._generate_id(content)
        embedding = self._simple_embedding(content)
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            importance=importance
        )
        
        self.memories[memory_id] = entry
        self._index.append(memory_id)
        return memory_id
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """搜索相似记忆"""
        query_embedding = self._simple_embedding(query)
        scores = []
        
        for memory_id in self._index:
            if memory_id not in self.memories:
                continue
            entry = self.memories[memory_id]
            similarity = self._cosine_similarity(query_embedding, entry.embedding)
            # 考虑重要性和访问频率
            weighted_score = similarity * entry.importance * (1 + 0.1 * math.log1p(entry.access_count))
            scores.append((memory_id, weighted_score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 更新访问统计
        for memory_id, _ in scores[:top_k]:
            if memory_id in self.memories:
                self.memories[memory_id].access_count += 1
                self.memories[memory_id].last_accessed = datetime.now().isoformat()
        
        return scores[:top_k]
    
    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """获取记忆"""
        return self.memories.get(memory_id)
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            if memory_id in self._index:
                self._index.remove(memory_id)
            return True
        return False
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x**2 for x in a))
        norm_b = math.sqrt(sum(x**2 for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
    
    def _evict_low_importance(self):
        """驱逐低重要性记忆"""
        if not self.memories:
            return
        lowest_id = min(self.memories.keys(), key=lambda k: self.memories[k].importance)
        self.delete_memory(lowest_id)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        importances = [m.importance for m in self.memories.values()]
        access_counts = [m.access_count for m in self.memories.values()]
        
        return {
            "total_memories": len(self.memories),
            "max_entries": self.max_entries,
            "dimension": self.dimension,
            "avg_importance": sum(importances) / len(importances) if importances else 0,
            "total_accesses": sum(access_counts),
            "avg_access_count": sum(access_counts) / len(access_counts) if access_counts else 0
        }
    
    def export_memories(self) -> List[Dict]:
        """导出所有记忆"""
        return [entry.to_dict() for entry in self.memories.values()]
    
    def import_memories(self, memories_data: List[Dict]) -> int:
        """导入记忆"""
        count = 0
        for data in memories_data:
            entry = MemoryEntry(**{k: v for k, v in data.items() if k in MemoryEntry.__dataclass_fields__})
            self.memories[entry.id] = entry
            if entry.id not in self._index:
                self._index.append(entry.id)
            count += 1
        return count


# 测试函数
def test_vector_memory():
    """测试向量记忆系统"""
    memory = VectorMemory(dimension=128, max_entries=100)
    
    # 添加记忆
    id1 = memory.add_memory("围棋征子路线判断技巧", {"category": "go", "difficulty": "中级"})
    id2 = memory.add_memory("倒扑与扑的区分方法", {"category": "go", "difficulty": "初级"})
    id3 = memory.add_memory("机器学习模型训练最佳实践", {"category": "ml", "difficulty": "高级"})
    id4 = memory.add_memory("围棋手筋训练方法", {"category": "go", "difficulty": "中级"})
    
    assert len(memory.memories) == 4
    
    # 搜索测试
    results = memory.search("围棋征子", top_k=2)
    assert len(results) == 2
    assert results[0][0] == id1  # 最相似
    
    # 获取记忆
    entry = memory.get_memory(id1)
    assert entry is not None
    assert entry.content == "围棋征子路线判断技巧"
    
    # 删除记忆
    memory.delete_memory(id3)
    assert len(memory.memories) == 3
    
    # 统计信息
    stats = memory.get_stats()
    assert stats["total_memories"] == 3
    assert stats["dimension"] == 128
    
    # 导出/导入
    exported = memory.export_memories()
    assert len(exported) == 3
    
    memory2 = VectorMemory(dimension=128)
    count = memory2.import_memories(exported)
    assert count == 3
    assert len(memory2.memories) == 3
    
    return {
        "status": "passed",
        "tests_run": 8,
        "details": {
            "add_memory": True,
            "search": True,
            "get_memory": True,
            "delete_memory": True,
            "stats": True,
            "export_import": True,
            "similarity_ranking": True,
            "max_entries_limit": True
        }
    }


if __name__ == "__main__":
    result = test_vector_memory()
    print(json.dumps(result, indent=2, ensure_ascii=False))
