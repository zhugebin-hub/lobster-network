#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量记忆扩展器 (Vector Memory Expander) - 小龙虾网络 V3.1
轻量级向量存储，支持错题语义检索

功能:
- 错题自动分词索引
- 语义相似度检索
- 跨模块错题关联
- 记忆强度衰减模型
"""

import json
import math
import hashlib
import logging
import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class VectorEntry:
    """向量记忆条目"""
    id: str
    content: str
    category: str          # 分类: wrong_answer/concept/case
    module: str            # 所属模块: go/networking/poster...
    vector: List[float]    # 特征向量
    metadata: Dict = field(default_factory=dict)
    strength: float = 1.0  # 记忆强度 0-1
    access_count: int = 0
    created_at: str = ""
    last_reviewed: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category,
            "module": self.module,
            "vector": self.vector,
            "metadata": self.metadata,
            "strength": self.strength,
            "access_count": self.access_count,
            "created_at": self.created_at,
            "last_reviewed": self.last_reviewed,
        }


class SimpleTokenizer:
    """轻量级分词器（不依赖外部库）"""

    # 中文停用词
    STOP_WORDS = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
        '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '想',
        '这', '那', '吗', '什么', '怎么', '为什么', '如何', '可以', '这个',
        '那个', '之', '其', '与', '及', '等', '或', '但', '如果', '则',
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'of', 'in', 'to',
        'for', 'with', 'on', 'at', 'by', 'from', 'this', 'that', 'and',
        'or', 'but', 'if', 'then', 'than', 'it', 'as', 'be', 'has', 'had',
    }

    # 关键词模式（提取专业术语）
    TERM_PATTERNS = [
        r'[A-Z][a-z]+(?:[A-Z][a-z]+)+',    # CamelCase 术语
        r'[A-Z_]{2,}',                       # 全大写缩写
        r'\d+[\w]*[Bb]it',                   # 位宽相关
        r'(?:TCP|UDP|HTTP|DNS|SSH|SSL|TLS|OSI|VLAN|VXLAN|OpenFlow)',
    ]

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        """分词"""
        tokens = []

        # 提取专业术语
        for pattern in cls.TERM_PATTERNS:
            tokens.extend(re.findall(pattern, text))

        # 中文分词（按字符粒度 + 双字符组合）
        cn_text = re.sub(r'[a-zA-Z0-9\s]', '', text)
        for i, ch in enumerate(cn_text):
            if ch not in cls.STOP_WORDS and len(ch.strip()) > 0:
                tokens.append(ch)
                if i + 1 < len(cn_text):
                    bigram = cn_text[i:i+2]
                    if bigram not in cls.STOP_WORDS:
                        tokens.append(bigram)

        # 英文分词
        en_words = re.findall(r'[a-zA-Z]+', text)
        for w in en_words:
            if w.lower() not in cls.STOP_WORDS and len(w) > 1:
                tokens.append(w.lower())

        # 去重
        return list(dict.fromkeys(tokens))


class VectorHasher:
    """基于哈希的特征向量生成器"""

    DIMENSION = 64  # 向量维度

    @classmethod
    def text_to_vector(cls, text: str) -> List[float]:
        """将文本转换为特征向量（SimHash 风格）"""
        tokens = SimpleTokenizer.tokenize(text)
        if not tokens:
            return [0.0] * cls.DIMENSION

        # 初始化累加器
        accumulator = [0.0] * cls.DIMENSION

        for token in tokens:
            # 对每个 token 生成哈希
            token_hash = hashlib.md5(token.encode('utf-8')).hexdigest()
            for i in range(cls.DIMENSION):
                byte_idx = (i // 4) % len(token_hash)
                hex_val = int(token_hash[byte_idx], 16)
                bit = (hex_val >> (3 - i % 4)) & 1
                accumulator[i] += (1.0 if bit else -1.0)

        # 二值化
        vector = [1.0 if v > 0 else (-1.0 if v < 0 else 0.0) for v in accumulator]
        return vector

    @classmethod
    def similarity(cls, v1: List[float], v2: List[float]) -> float:
        """计算余弦相似度"""
        if len(v1) != len(v2):
            return 0.0

        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot / (norm1 * norm2)


class VectorMemoryExpander:
    """向量记忆扩展器"""

    SIMILARITY_THRESHOLD = 0.6  # 相似度阈值

    def __init__(self, name: str = "default", storage_path: Optional[str] = None):
        self.name = name
        self._entries: Dict[str, VectorEntry] = {}
        self._tokenizer = SimpleTokenizer()
        self._hasher = VectorHasher()

        if storage_path:
            self._storage_path = Path(storage_path)
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            self._load()
        else:
            self._storage_path = None

        logger.info(f"[向量记忆:{self.name}] 初始化, 维度={self._hasher.DIMENSION}")

    def add(self, content: str, category: str = "wrong_answer",
            module: str = "general", metadata: Optional[Dict] = None) -> str:
        """添加记忆条目"""
        entry_id = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]

        if entry_id in self._entries:
            # 更新已有条目
            entry = self._entries[entry_id]
            entry.strength = min(1.0, entry.strength + 0.1)
            entry.access_count += 1
            return entry_id

        vector = self._hasher.text_to_vector(content)
        entry = VectorEntry(
            id=entry_id,
            content=content[:500],  # 限制长度
            category=category,
            module=module,
            vector=vector,
            metadata=metadata or {},
        )
        self._entries[entry_id] = entry
        return entry_id

    def search(self, query: str, top_k: int = 5, module: Optional[str] = None) -> List[Tuple[VectorEntry, float]]:
        """语义搜索"""
        query_vector = self._hasher.text_to_vector(query)
        results = []

        for entry in self._entries.values():
            if module and entry.module != module:
                continue
            sim = self._hasher.similarity(query_vector, entry.vector)
            # 考虑记忆强度衰减
            adjusted_sim = sim * entry.strength
            if adjusted_sim >= self.SIMILARITY_THRESHOLD:
                results.append((entry, round(adjusted_sim, 3)))

        # 按相似度排序
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def search_by_module(self, module: str, category: Optional[str] = None) -> List[VectorEntry]:
        """按模块搜索"""
        results = []
        for entry in self._entries.values():
            if entry.module == module:
                if category is None or entry.category == category:
                    results.append(entry)
        return results

    def decay_strength(self, days: int = 7, decay_factor: float = 0.1):
        """记忆强度衰减（模拟遗忘曲线）"""
        now = datetime.now()
        for entry in self._entries.values():
            created = datetime.fromisoformat(entry.created_at)
            age_days = (now - created).days
            if age_days > days:
                entry.strength = max(0.1, entry.strength - decay_factor * (age_days - days) / 7)

    def get_stats(self) -> Dict:
        """获取统计信息"""
        modules = {}
        categories = {}
        for entry in self._entries.values():
            modules[entry.module] = modules.get(entry.module, 0) + 1
            categories[entry.category] = categories.get(entry.category, 0) + 1

        avg_strength = (sum(e.strength for e in self._entries.values()) / len(self._entries)
                       if self._entries else 0)

        return {
            "name": self.name,
            "total_entries": len(self._entries),
            "by_module": modules,
            "by_category": categories,
            "avg_strength": round(avg_strength, 3),
        }

    def save(self):
        """持久化"""
        if not self._storage_path:
            return
        try:
            data = {
                "name": self.name,
                "saved_at": datetime.now().isoformat(),
                "entries": {k: v.to_dict() for k, v in self._entries.items()},
            }
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"[向量记忆:{self.name}] 已保存 {len(self._entries)} 条")
        except Exception as e:
            logger.warning(f"[向量记忆:{self.name}] 保存失败: {e}")

    def _load(self):
        """从文件加载"""
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            with open(self._storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for k, v in data.get("entries", {}).items():
                entry = VectorEntry(**v)
                self._entries[k] = entry
            logger.info(f"[向量记忆:{self.name}] 加载 {len(self._entries)} 条")
        except Exception as e:
            logger.warning(f"[向量记忆:{self.name}] 加载失败: {e}")


# ========== 预定义实例 ==========

# 各模块错题本
go_memory = VectorMemoryExpander(name="go")
networking_memory = VectorMemoryExpander(name="networking")
poster_memory = VectorMemoryExpander(name="poster")
ai_ml_memory = VectorMemoryExpander(name="ai_ml")
cybersecurity_memory = VectorMemoryExpander(name="cybersecurity")
data_structure_memory = VectorMemoryExpander(name="data_structure")

_memories: Dict[str, VectorMemoryExpander] = {
    "go": go_memory,
    "networking": networking_memory,
    "poster": poster_memory,
    "ai_ml": ai_ml_memory,
    "cybersecurity": cybersecurity_memory,
    "data_structure": data_structure_memory,
}


def get_memory(module: str) -> VectorMemoryExpander:
    """获取模块记忆"""
    if module not in _memories:
        _memories[module] = VectorMemoryExpander(name=module)
    return _memories[module]


def add_wrong_answer(module: str, question: str, answer: str, correct_answer: str):
    """添加错题（便捷函数）"""
    content = f"问题: {question}\n我的答案: {answer}\n正确答案: {correct_answer}"
    mem = get_memory(module)
    return mem.add(content, category="wrong_answer", module=module)


def search_similar_wrong(module: str, question: str, top_k: int = 3):
    """搜索相似错题"""
    mem = get_memory(module)
    return mem.search(question, top_k=top_k)
