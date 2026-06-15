"""
简化版RAG系统 - 检索增强生成实践
从与小龙虾的对话中获得灵感
"""

import json
import hashlib
import os
from typing import List, Tuple, Dict


class SimpleRAG:
    """简化版RAG系统"""
    
    def __init__(self):
        self.knowledge_base: List[Dict] = []
    
    def add_document(self, content: str, source: str, category: str):
        """添加知识文档"""
        chunks = self._chunk_text(content)
        for i, chunk in enumerate(chunks):
            self.knowledge_base.append({
                "id": f"{source}_part{i+1}",
                "content": chunk,
                "source": source,
                "category": category,
                "embedding": self._make_embedding(chunk)
            })
    
    def _chunk_text(self, text: str, max_len: int = 300) -> List[str]:
        """按段落切分文本"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current = ""
        for para in paragraphs:
            if len(current) + len(para) <= max_len:
                current = current + "\n\n" + para if current else para
            else:
                if current:
                    chunks.append(current)
                current = para
        if current:
            chunks.append(current)
        return chunks
    
    def _make_embedding(self, text: str) -> List[float]:
        """生成简化版向量"""
        h = hashlib.md5(text.encode()).hexdigest()
        emb = [int(h[i:i+2], 16) / 255.0 for i in range(0, min(len(h), 32), 2)]
        while len(emb) < 16:
            emb.append(0.0)
        return emb[:16]
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[Dict, float]]:
        """检索最相关的知识片段"""
        query_emb = self._make_embedding(query)
        results = []
        for doc in self.knowledge_base:
            score = self._cosine_similarity(query_emb, doc["embedding"])
            # 关键词匹配加分
            keyword_score = self._keyword_match(query, doc["content"])
            final_score = 0.7 * score + 0.3 * keyword_score
            results.append((doc, final_score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """余弦相似度"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a)) if a else 0
        norm_b = math.sqrt(sum(x * x for x in b)) if b else 0
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def _keyword_match(self, query: str, content: str) -> float:
        """关键词匹配"""
        query_chars = set(query)
        if not query_chars:
            return 0.0
        matched = sum(1 for c in query_chars if c in content)
        return matched / len(query_chars)
    
    def answer(self, query: str) -> str:
        """基于检索生成回答"""
        results = self.retrieve(query, top_k=3)
        response = f"🔍 查询: {query}\n\n📚 相关知识：\n\n"
        for i, (doc, score) in enumerate(results, 1):
            preview = doc["content"][:200]
            response += f"[{i}] {doc['source']} | {doc['category']} (相关度: {score:.1%})\n"
            response += f"    {preview}...\n\n"
        response += "💡 以上信息来自知识库，引用已标注来源。"
        return response


import math


def main():
    rag = SimpleRAG()
    
    # 加载知识库
    documents = [
        ("机器学习是人工智能的核心分支，让计算机从数据中自动学习规律。主要包括三大范式：监督学习（有标签数据）、无监督学习（无标签数据）、强化学习（与环境交互学习）。代表算法包括线性回归、决策树、神经网络等。", "教材", "ML基础"),
        ("深度学习是机器学习的子领域，使用多层神经网络学习数据的分层表示。主流架构包括：CNN（卷积神经网络，擅长图像）、RNN（循环神经网络，擅长序列）、Transformer（基于自注意力机制，擅长文本）。训练关键包括损失函数、优化器、正则化。", "课件", "深度学习"),
        ("Transformer架构由Vaswani等人于2017年提出，核心是自注意力机制。Attention(Q,K,V) = softmax(QK^T/√d_k)V。由编码器和解码器组成，支持并行计算。代表模型包括BERT、GPT系列、T5等，是当今大语言模型的基础架构。", "论文", "NLP"),
        ("RAG（检索增强生成）将信息检索与文本生成结合。流程：用户查询→检索相关文档→拼接上下文→大模型生成回答。优势：减少幻觉、知识可更新、答案可追溯。应用场景：企业知识库、客服机器人、学术研究辅助。", "技术博客", "RAG"),
        ("AI伦理问题包括：1.算法偏见（训练数据偏见被放大）2.隐私保护（大规模数据收集风险）3.可解释性（深度学习黑盒问题）4.责任归属（AI出错谁负责）5.深度伪造（AI生成虚假内容）。需要技术+法律+公众共同参与治理。", "行业报告", "AI伦理"),
    ]
    
    for content, source, category in documents:
        rag.add_document(content, source, category)
    
    # 测试查询
    queries = [
        "什么是机器学习？",
        "Transformer的原理是什么？",
        "RAG技术有什么用？",
        "AI伦理问题有哪些？",
    ]
    
    print("=" * 50)
    print("🧪 RAG系统测试")
    print("=" * 50)
    
    all_results = []
    for query in queries:
        print(f"\n📝 {query}")
        print("-" * 40)
        answer = rag.answer(query)
        print(answer)
        all_results.append({"query": query, "response": answer})
    
    # 保存结果
    os.makedirs("output", exist_ok=True)
    with open("output/rag_test_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print(f"✅ 测试完成，共 {len(queries)} 个查询")
    print(f"💾 知识库包含 {len(rag.knowledge_base)} 个知识片段")
    print("=" * 50)


if __name__ == "__main__":
    main()
