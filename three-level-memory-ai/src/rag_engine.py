"""
RAG 检索引擎
功能：向量相似度检索、混合检索、结果重排
"""

import json
import os
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SearchResult:
    """检索结果"""
    chunk_id: str
    content: str
    source: str
    category: str
    score: float
    relevance: str  # "high", "medium", "low"


class RAGEngine:
    """RAG检索引擎"""
    
    def __init__(self, vector_store_path: str = "output/vector_store.json"):
        self.vector_store_path = vector_store_path
        self.chunks = []
        self._load()
    
    def _load(self):
        """加载向量库"""
        if os.path.exists(self.vector_store_path):
            with open(self.vector_store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks = data.get('chunks', [])
                print(f"📚 RAG引擎加载了 {len(self.chunks)} 个向量片段")
        else:
            print("⚠️ 向量库不存在，请先运行 memory_system.py 构建知识库")
    
    def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.0) -> List[SearchResult]:
        """检索最相关的知识片段"""
        query_embedding = self._simple_embedding(query)
        results = []
        
        for chunk in self.chunks:
            chunk_embedding = chunk.get('embedding', [])
            if not chunk_embedding:
                continue
            
            # 计算相似度
            similarity = self._cosine_similarity(query_embedding, chunk_embedding)
            
            # 关键词匹配加分
            keyword_score = self._keyword_match(query, chunk.get('content', ''))
            final_score = 0.7 * similarity + 0.3 * keyword_score
            
            if final_score >= min_score:
                relevance = "high" if final_score > 0.5 else ("medium" if final_score > 0.3 else "low")
                results.append(SearchResult(
                    chunk_id=chunk.get('id', ''),
                    content=chunk.get('content', ''),
                    source=chunk.get('source', ''),
                    category=chunk.get('category', ''),
                    score=round(final_score, 4),
                    relevance=relevance
                ))
        
        # 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def _simple_embedding(self, text: str) -> List[float]:
        """简化版嵌入（实际使用text-embedding-3等模型）"""
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        embedding = []
        for i in range(0, min(len(h), 32), 2):
            embedding.append(int(h[i:i+2], 16) / 255.0)
        while len(embedding) < 16:
            embedding.append(0.0)
        return embedding[:16]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """余弦相似度"""
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def _keyword_match(self, query: str, content: str) -> float:
        """关键词匹配分数"""
        # 简单的词频匹配
        query_words = set(list(query))
        if not query_words:
            return 0.0
        matched = sum(1 for w in query_words if w in content)
        return matched / len(query_words)
    
    def format_results(self, results: List[SearchResult]) -> str:
        """格式化检索结果"""
        if not results:
            return "未找到相关知识片段"
        
        output = f"🔍 检索到 {len(results)} 个相关知识片段：\n\n"
        for i, r in enumerate(results, 1):
            output += f"【结果{i}】相关度: {r.score:.2%} ({r.relevance})\n"
            output += f"来源: {r.source} | 类别: {r.category}\n"
            preview = r.content[:200] + "..." if len(r.content) > 200 else r.content
            output += f"内容: {preview}\n\n"
        
        return output


if __name__ == "__main__":
    engine = RAGEngine()
    
    test_queries = [
        "什么是Transformer？",
        "深度学习有哪些网络架构？",
        "RAG技术原理",
        "机器学习分类算法",
    ]
    
    for query in test_queries:
        print(f"\n🔎 查询: {query}")
        results = engine.retrieve(query, top_k=3)
        print(engine.format_results(results))
