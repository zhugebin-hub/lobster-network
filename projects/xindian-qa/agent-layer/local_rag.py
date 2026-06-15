#!/usr/bin/env python3
"""
本地 RAG 系统
使用 DashScope Embedding + 本地向量数据库 + DashScope LLM
替代百炼知识库 API（认证失败问题）
"""

import json
import math
import os
import sqlite3
import hashlib
from typing import List, Dict, Optional, Tuple

import requests


class LocalRAG:
    """本地 RAG 系统"""
    
    def __init__(self, config_path: str = None):
        """初始化"""
        if config_path is None:
            config_path = os.path.expanduser("~/.openclaw/config/bailian-kb.json")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['api_key']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 本地数据库路径
        self.db_path = self.config.get('local_db', {}).get(
            'path',
            os.path.expanduser("~/.openclaw/workspace/projects/xindian-qa/knowledge-base/vector_db.sqlite")
        )
        
        # 确保数据库存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                title TEXT,
                content TEXT,
                course TEXT,
                section TEXT,
                chunk_index INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                embedding BLOB,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)
    
    def get_embedding(self, texts: List[str], text_type: str = "query") -> List[List[float]]:
        """获取文本向量"""
        resp = requests.post(
            "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
            headers={**self.headers, 'X-DashScope-Api-Version': '2024-06-01'},
            json={
                "model": "text-embedding-v3",
                "input": {"texts": texts},
                "parameters": {"text_type": text_type}
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return [e.get('embedding', []) for e in data.get('output', {}).get('embeddings', [])]
        return []
    
    def add_document(self, title: str, content: str, course: str, section: str = "") -> str:
        """添加文档到知识库"""
        doc_id = hashlib.md5(f"{course}_{title}_{content[:50]}".encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 插入文档
        cursor.execute(
            'INSERT OR REPLACE INTO documents VALUES (?, ?, ?, ?, ?, ?)',
            (doc_id, title, content, course, section, 0)
        )
        
        # 获取向量
        embeddings = self.get_embedding([content], text_type="document")
        if embeddings:
            cursor.execute(
                'INSERT OR REPLACE INTO embeddings VALUES (?, ?, ?)',
                (doc_id, doc_id, json.dumps(embeddings[0]).encode('utf-8'))
            )
        
        conn.commit()
        conn.close()
        
        return doc_id
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """搜索知识库"""
        # 获取查询向量
        query_embeddings = self.get_embedding([query], text_type="query")
        if not query_embeddings:
            return []
        
        query_embedding = query_embeddings[0]
        
        # 从数据库获取所有文档
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, title, content, course FROM documents')
        documents = cursor.fetchall()
        
        # 获取所有向量
        similarities = []
        for doc_id, title, content, course in documents:
            cursor.execute('SELECT embedding FROM embeddings WHERE id = ?', (doc_id,))
            row = cursor.fetchone()
            
            if row:
                doc_embedding = json.loads(row[0].decode('utf-8'))
                similarity = self.cosine_similarity(query_embedding, doc_embedding)
                similarities.append({
                    'title': title,
                    'content': content,
                    'course': course,
                    'similarity': similarity
                })
        
        conn.close()
        
        # 按相似度排序
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]
    
    def generate_answer(self, query: str, context: str) -> str:
        """生成答案"""
        prompt = f"""你是信电学院 AI 知识问答助手"小龙虾数字员工"。

请基于以下知识片段回答用户问题：

知识片段：
{context}

用户问题：{query}

请根据知识片段给出准确回答。如果知识片段不足以回答问题，请说明。

回答格式：
1. 直接给出答案
2. 引用相关原文（如有）
3. 提供进一步学习建议（如有）"""
        
        resp = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=self.headers,
            json={
                "model": self.config.get('llm', {}).get('model', 'qwen-plus'),
                "messages": [
                    {"role": "system", "content": "你是信电学院 AI 知识问答助手，基于教材知识回答学生问题。回答要准确、专业、友好。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": self.config.get('llm', {}).get('max_tokens', 2000),
                "temperature": self.config.get('llm', {}).get('temperature', 0.3)
            },
            timeout=60
        )
        
        if resp.status_code == 200:
            return resp.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        return ""
    
    def query(self, query: str, top_k: int = 3) -> Dict:
        """完整查询流程"""
        # 1. 搜索
        results = self.search(query, top_k)
        
        if not results:
            return {
                'answer': '抱歉，知识库中未找到相关内容。请尝试其他关键词。',
                'sources': [],
                'query': query
            }
        
        # 2. 构建上下文
        context = "\n\n".join([
            f"[{r['title']}]\n{r['content']}" 
            for r in results
        ])
        
        # 3. 生成答案
        answer = self.generate_answer(query, context)
        
        return {
            'answer': answer,
            'sources': [
                {
                    'title': r['title'],
                    'course': r['course'],
                    'similarity': r['similarity'],
                    'content': r['content'][:200] + '...'
                }
                for r in results
            ],
            'query': query
        }


# 测试代码
if __name__ == '__main__':
    rag = LocalRAG()
    print("✅ 本地 RAG 系统初始化成功")
    
    # 测试查询
    test_queries = [
        "基尔霍夫定律是什么？",
        "傅里叶变换的定义",
        "触发器的特性方程"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询：{query}")
        result = rag.query(query)
        print(f"   📝 回答：{result['answer'][:200]}...")
        print(f"   📚 来源：{len(result['sources'])} 个片段")
