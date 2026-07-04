#!/usr/bin/env python3
"""
百炼 API 调用 Skill（带本地 RAG 回退）
优先使用百炼知识库 API，失败时自动回退到本地 RAG 系统
"""

import json
import requests
import os
from typing import List, Dict, Optional

class BailianAPISkill:
    """百炼 API Skill（带本地 RAG 回退）"""
    
    def __init__(self, config_path: str = None):
        """初始化百炼 API Skill"""
        if config_path is None:
            config_path = os.path.expanduser("~/.openclaw/config/bailian-kb.json")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['api_key']
        self.api_endpoint = self.config['api_endpoint']
        self.kb_id = self.config['knowledge_base']['id']
        self.embedding_model = self.config['knowledge_base']['embedding_model']
        self.dimension = self.config['knowledge_base']['dimension']
        self.chunk_size = self.config['knowledge_base']['chunk_size']
        self.chunk_overlap = self.config['knowledge_base']['chunk_overlap']
        self.top_k = self.config['knowledge_base']['top_k']
        self.rerank_model = self.config['knowledge_base']['rerank_model']
        self.llm_model = self.config['llm']['model']
        self.temperature = self.config['llm']['temperature']
        self.max_tokens = self.config['llm']['max_tokens']
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 导入本地 RAG（回退方案）
        try:
            from local_rag import LocalRAG
            self.local_rag = LocalRAG(config_path)
            self.use_local_rag = True
            print("✅ 本地 RAG 系统已加载（作为回退方案）")
        except Exception as e:
            print(f"⚠️ 本地 RAG 加载失败: {e}")
            self.local_rag = None
            self.use_local_rag = False
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """
        语义检索（优先百炼 API，回退本地 RAG）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = self.top_k
        
        # 尝试百炼 API
        try:
            url = f"{self.api_endpoint}/api/v1/knowledge/documents/search"
            payload = {
                'kb_id': self.kb_id,
                'query': query,
                'top_k': top_k,
                'embedding_model': self.embedding_model,
                'rerank_model': self.rerank_model
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            if response.status_code == 200:
                return response.json().get('results', [])
        except Exception as e:
            print(f"⚠️ 百炼 API 搜索失败: {e}，回退到本地 RAG")
        
        # 回退到本地 RAG
        if self.use_local_rag and self.local_rag:
            results = self.local_rag.search(query, top_k)
            return [
                {
                    'title': r['title'],
                    'content': r['content'],
                    'score': r['similarity'],
                    'course': r['course']
                }
                for r in results
            ]
        
        return []
    
    def upload_document(self, file_path: str) -> Dict:
        """
        上传文档到知识库
        
        Args:
            file_path: 文件路径
            
        Returns:
            上传结果
        """
        url = f"{self.api_endpoint}/api/v1/knowledge/documents"
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'kb_id': self.kb_id,
                'chunk_size': self.chunk_size,
                'chunk_overlap': self.chunk_overlap
            }
            response = requests.post(url, files=files, data=data, headers=self.headers)
            response.raise_for_status()
            return response.json()
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示
        
        Args:
            text: 输入文本
            
        Returns:
            向量表示
        """
        url = f"{self.api_endpoint}/api/v1/embeddings"
        payload = {
            'model': self.embedding_model,
            'input': text
        }
        
        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json().get('data', [{}])[0].get('embedding', [])
    
    def generate_answer(self, query: str, context: str) -> str:
        """
        生成答案（通过 DashScope 兼容模式）
        
        Args:
            query: 用户问题
            context: 检索到的知识片段
            
        Returns:
            生成的答案
        """
        url = f"{self.api_endpoint}/compatible-mode/v1/chat/completions"
        payload = {
            'model': self.llm_model,
            'messages': [
                {'role': 'system', 'content': '你是信电学院 AI 知识问答助手。请基于提供的知识片段回答用户问题。如果知识片段不足以回答问题，请说明。'},
                {'role': 'user', 'content': f'知识片段：\n{context}\n\n问题：{query}'}
            ],
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=60)
            if response.status_code == 200:
                return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        except Exception as e:
            print(f"⚠️ DashScope 生成答案失败: {e}")
        
        # 回退到本地 RAG 的生成方法
        if self.use_local_rag and self.local_rag:
            return self.local_rag.generate_answer(query, context)
        
        return '抱歉，生成答案时出现错误，请稍后重试。'

# 测试代码
if __name__ == '__main__':
    skill = BailianAPISkill()
    print("百炼 API Skill 初始化成功")
    print(f"知识库 ID: {skill.kb_id}")
    print(f"Embedding 模型：{skill.embedding_model}")
    print(f"大模型：{skill.llm_model}")
    print(f"使用本地 RAG: {skill.use_local_rag}")
