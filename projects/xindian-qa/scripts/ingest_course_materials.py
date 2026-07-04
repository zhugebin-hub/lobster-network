#!/usr/bin/env python3
"""
课程材料入库脚本
负责将课程教材、笔记等材料上传到百炼知识库
"""

import os
import json
import requests
import hashlib
from typing import List, Dict, Optional
from pathlib import Path

class CourseMaterialIngestor:
    """课程材料入库器"""
    
    def __init__(self, config_path: str = None):
        """初始化入库器"""
        if config_path is None:
            config_path = os.path.expanduser("~/.openclaw/config/bailian-kb.json")
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.api_key = self.config['api_key']
        self.api_endpoint = self.config['api_endpoint']
        self.kb_id = self.config['knowledge_base']['id']
        self.chunk_size = self.config['knowledge_base']['chunk_size']
        self.chunk_overlap = self.config['knowledge_base']['chunk_overlap']
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def ingest_pdf(self, pdf_path: str, course_name: str) -> Dict:
        """
        入库 PDF 教材
        
        Args:
            pdf_path: PDF 文件路径
            course_name: 课程名称
            
        Returns:
            入库结果
        """
        print(f"📖 处理 PDF: {pdf_path}")
        print(f"   课程：{course_name}")
        
        # 1. 解析 PDF（需要 pdfplumber 或 PyPDF2）
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except ImportError:
            print("   ⚠️ 缺少 pdfplumber，尝试使用 PyPDF2")
            try:
                import PyPDF2
                with open(pdf_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() or ""
            except ImportError:
                print("   ❌ 缺少 PDF 解析库，请安装：pip install pdfplumber")
                return {'status': 'error', 'message': '缺少 PDF 解析库'}
        
        # 2. 智能分块
        chunks = self._chunk_text(text, self.chunk_size, self.chunk_overlap)
        print(f"   ✅ 分块完成：{len(chunks)} 块")
        
        # 3. 上传到百炼知识库
        results = []
        for i, chunk in enumerate(chunks):
            result = self._upload_chunk(chunk, course_name, i)
            results.append(result)
        
        return {
            'status': 'success',
            'course': course_name,
            'chunks': len(chunks),
            'results': results
        }
    
    def ingest_markdown(self, md_path: str, course_name: str) -> Dict:
        """
        入库 Markdown 笔记
        
        Args:
            md_path: Markdown 文件路径
            course_name: 课程名称
            
        Returns:
            入库结果
        """
        print(f"📝 处理 Markdown: {md_path}")
        print(f"   课程：{course_name}")
        
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 1. 智能分块
        chunks = self._chunk_text(text, self.chunk_size, self.chunk_overlap)
        print(f"   ✅ 分块完成：{len(chunks)} 块")
        
        # 2. 上传到百炼知识库
        results = []
        for i, chunk in enumerate(chunks):
            result = self._upload_chunk(chunk, course_name, i)
            results.append(result)
        
        return {
            'status': 'success',
            'course': course_name,
            'chunks': len(chunks),
            'results': results
        }
    
    def ingest_html(self, html_path: str, course_name: str) -> Dict:
        """
        入库 HTML 课程页面
        
        Args:
            html_path: HTML 文件路径
            course_name: 课程名称
            
        Returns:
            入库结果
        """
        print(f"🌐 处理 HTML: {html_path}")
        print(f"   课程：{course_name}")
        
        try:
            from bs4 import BeautifulSoup
            with open(html_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
        except ImportError:
            print("   ⚠️ 缺少 beautifulsoup4，尝试使用正则表达式")
            import re
            with open(html_path, 'r', encoding='utf-8') as f:
                text = f.read()
                text = re.sub(r'<[^>]+>', '\n', text)
                text = re.sub(r'\n+', '\n', text)
        
        # 1. 智能分块
        chunks = self._chunk_text(text, self.chunk_size, self.chunk_overlap)
        print(f"   ✅ 分块完成：{len(chunks)} 块")
        
        # 2. 上传到百炼知识库
        results = []
        for i, chunk in enumerate(chunks):
            result = self._upload_chunk(chunk, course_name, i)
            results.append(result)
        
        return {
            'status': 'success',
            'course': course_name,
            'chunks': len(chunks),
            'results': results
        }
    
    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        智能分块文本
        
        Args:
            text: 输入文本
            chunk_size: 块大小
            overlap: 重叠大小
            
        Returns:
            分块列表
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # 尽量在句子边界处断开
            if end < len(text):
                # 查找最后一个句号、问号、感叹号
                for i in range(len(chunk) - 1, -1, -1):
                    if chunk[i] in ['。', '？', '！', '.', '?', '!', '\n']:
                        chunk = chunk[:i+1]
                        end = start + i + 1
                        break
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def _upload_chunk(self, chunk: str, course_name: str, index: int) -> Dict:
        """
        上传单个知识块
        
        Args:
            chunk: 知识块内容
            course_name: 课程名称
            index: 块索引
            
        Returns:
            上传结果
        """
        # 生成文档 ID
        doc_id = hashlib.md5(f"{course_name}_{index}".encode()).hexdigest()
        
        # 构建请求
        url = f"{self.api_endpoint}/api/v1/knowledge/documents"
        payload = {
            'kb_id': self.kb_id,
            'document_id': doc_id,
            'title': f"{course_name}_chunk_{index}",
            'content': chunk,
            'metadata': {
                'course': course_name,
                'chunk_index': index
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return {
                'status': 'success',
                'doc_id': doc_id,
                'chunk_index': index
            }
        except Exception as e:
            return {
                'status': 'error',
                'doc_id': doc_id,
                'chunk_index': index,
                'error': str(e)
            }

# 测试代码
if __name__ == '__main__':
    ingestor = CourseMaterialIngestor()
    print("✅ 课程材料入库器初始化成功")
    print(f"   知识库 ID: {ingestor.kb_id}")
    print(f"   分块大小：{ingestor.chunk_size}")
    print(f"   重叠大小：{ingestor.chunk_overlap}")
