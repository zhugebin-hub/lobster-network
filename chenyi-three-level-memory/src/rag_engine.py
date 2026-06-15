"""
RAG 检索引擎
实现语义检索、关键词检索和混合检索
"""

import hashlib
import math
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class SearchResult:
    """检索结果"""
    chunk_id: str
    content: str
    source: str
    score: float
    category: str


class RAGEngine:
    """RAG检索引擎"""
    
    def __init__(self):
        self.chunks = []
        self.vector_dim = 16
    
    def load_chunks(self, chunks: List[Dict]):
        """加载知识片段"""
        self.chunks = chunks
        # 为每个片段生成嵌入向量
        for chunk in self.chunks:
            chunk['embedding'] = self._generate_embedding(chunk['content'])
        print(f"🔍 RAG引擎已加载 {len(self.chunks)} 个片段")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """生成嵌入向量（简化版）"""
        h = hashlib.md5(text.encode()).hexdigest()
        embedding = []
        for i in range(0, min(len(h), 32), 2):
            embedding.append(int(h[i:i+2], 16) / 255.0)
        while len(embedding) < self.vector_dim:
            embedding.append(0.0)
        return embedding[:self.vector_dim]
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """语义检索（基于向量相似度）"""
        query_embedding = self._generate_embedding(query)
        results = []
        
        for chunk in self.chunks:
            score = self._cosine_similarity(query_embedding, chunk['embedding'])
            results.append(SearchResult(
                chunk_id=chunk['chunk_id'],
                content=chunk['content'],
                source=chunk['doc_id'],
                score=score,
                category=chunk['category']
            ))
        
        # 按相似度排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def keyword_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """关键词检索（基于BM25简化版）"""
        keywords = self._extract_keywords(query)
        results = []
        
        for chunk in self.chunks:
            score = self._bm25_score(keywords, chunk['content'])
            results.append(SearchResult(
                chunk_id=chunk['chunk_id'],
                content=chunk['content'],
                source=chunk['doc_id'],
                score=score,
                category=chunk['category']
            ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def hybrid_search(self, query: str, top_k: int = 5, alpha: float = 0.7) -> List[SearchResult]:
        """混合检索（语义 + 关键词）"""
        semantic_results = self.semantic_search(query, top_k=top_k*2)
        keyword_results = self.keyword_search(query, top_k=top_k*2)
        
        # 合并结果
        combined = {}
        for r in semantic_results:
            combined[r.chunk_id] = {
                'result': r,
                'semantic_score': r.score,
                'keyword_score': 0
            }
        
        for r in keyword_results:
            if r.chunk_id in combined:
                combined[r.chunk_id]['keyword_score'] = r.score
            else:
                combined[r.chunk_id] = {
                    'result': r,
                    'semantic_score': 0,
                    'keyword_score': r.score
                }
        
        # 计算混合分数
        for item in combined.values():
            item['result'].score = alpha * item['semantic_score'] + (1 - alpha) * item['keyword_score']
        
        # 排序
        final_results = [item['result'] for item in combined.values()]
        final_results.sort(key=lambda x: x.score, reverse=True)
        
        return final_results[:top_k]
    
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
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版）"""
        # 移除标点符号
        clean = ''
        for char in text:
            if char.isalnum() or char == ' ':
                clean += char
        return clean.split()
    
    def _bm25_score(self, keywords: List[str], content: str) -> float:
        """BM25评分（简化版）"""
        score = 0.0
        content_words = self._extract_keywords(content)
        content_len = len(content_words)
        
        for keyword in keywords:
            if keyword in content_words:
                tf = content_words.count(keyword) / content_len if content_len > 0 else 0
                score += tf * math.log(100 / (1 + tf))  # 简化版IDF
        
        return score
    
    def get_relevant_context(self, query: str, top_k: int = 3, max_chars: int = 1500) -> str:
        """获取相关上下文（用于增强提示）"""
        results = self.hybrid_search(query, top_k=top_k)
        
        context = ""
        for i, result in enumerate(results, 1):
            if result.score > 0.3:  # 只包含相关性高的结果
                preview = result.content[:max_chars//top_k]
                context += f"[知识片段{i}（来源：{result.source}，相关度：{result.score:.2f}）]\n{preview}\n\n"
        
        return context if context else "未找到相关知识片段。"


# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    # 模拟数据
    test_chunks = [
        {
            "chunk_id": "test_1",
            "content": "机器学习是人工智能的一个分支，它使用统计技术让计算机系统能够在没有被明确编程的情况下从数据中学习。",
            "doc_id": "test.txt",
            "category": "test"
        },
        {
            "chunk_id": "test_2",
            "content": "深度学习是机器学习的一个子领域，使用多层神经网络学习数据的分层表示。",
            "doc_id": "test.txt",
            "category": "test"
        }
    ]
    
    engine = RAGEngine()
    engine.load_chunks(test_chunks)
    
    # 测试检索
    query = "什么是机器学习？"
    print(f"\n🔍 查询：{query}")
    
    print("\n📊 语义检索结果：")
    for r in engine.semantic_search(query, top_k=2):
        print(f"  - 分数：{r.score:.3f} | {r.content[:50]}...")
    
    print("\n📊 混合检索结果：")
    for r in engine.hybrid_search(query, top_k=2):
        print(f"  - 分数：{r.score:.3f} | {r.content[:50]}...")
