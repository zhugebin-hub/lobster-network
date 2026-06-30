"""
知识库预处理模块
功能：文档清洗、切片、元数据标注
"""

import os
import re
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Document:
    """文档对象"""
    path: str
    title: str
    category: str
    credibility: str
    date: str
    content: str
    chunks: List[str] = None


class KnowledgeProcessor:
    """知识库处理器"""
    
    def __init__(self, kb_path: str = "knowledge_base"):
        self.kb_path = kb_path
        self.documents: List[Document] = []
    
    def load_all_documents(self) -> List[Document]:
        """加载所有文档"""
        for root, dirs, files in os.walk(self.kb_path):
            for file in sorted(files):
                if file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    doc = self._parse_document(filepath)
                    if doc:
                        self.documents.append(doc)
        print(f"📄 加载了 {len(self.documents)} 份文档")
        return self.documents
    
    def _parse_document(self, filepath: str) -> Document:
        """解析单个文档"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取元数据
        title = ""
        category = "unknown"
        credibility = "medium"
        date = "unknown"
        
        for line in content.split('\n'):
            if '【知识文档】' in line:
                title = line.split('】')[-1].strip()
            if '类别：' in line:
                category = re.search(r'类别：([^|]+)', line).group(1).strip()
            if '可信度：' in line:
                credibility = re.search(r'可信度：([^|]+)', line).group(1).strip()
            if '日期：' in line:
                date = re.search(r'日期：(.+)', line).group(1).strip()
        
        return Document(
            path=filepath,
            title=title,
            category=category,
            credibility=credibility,
            date=date,
            content=content
        )
    
    def clean_document(self, doc: Document) -> str:
        """清洗文档内容"""
        content = doc.content
        # 移除文档头部标记
        content = re.sub(r'【知识文档】.*?\n', '', content)
        # 移除元数据行
        content = re.sub(r'(类别|可信度|日期|来源)：[^\n]+\n?', '', content)
        # 清理多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        # 统一编码
        content = content.encode('utf-8', errors='ignore').decode('utf-8')
        return content.strip()
    
    def chunk_document(self, content: str, min_size: int = 300, max_size: int = 800, overlap: int = 100) -> List[str]:
        """按语义切片文档"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        chunks = []
        current = ""
        
        for para in paragraphs:
            if len(current) + len(para) <= max_size:
                current += "\n\n" + para if current else para
            else:
                if current:
                    chunks.append(current)
                # 保留重叠部分
                if overlap > 0 and current:
                    words = current.split('\n\n')
                    overlap_text = "\n\n".join(words[-1:]) if len(words) > 0 else ""
                    current = overlap_text + "\n\n" + para if overlap_text else para
                else:
                    current = para
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def process_all(self) -> List[Dict]:
        """处理所有文档：清洗→切片→标注"""
        self.load_all_documents()
        all_chunks = []
        
        for doc in self.documents:
            clean_content = self.clean_document(doc)
            chunks = self.chunk_document(clean_content)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "id": f"{doc.title}_part{i+1}",
                    "content": chunk,
                    "source": os.path.basename(doc.path),
                    "category": doc.category,
                    "date": doc.date,
                    "credibility": doc.credibility,
                    "title": doc.title
                })
        
        print(f"📊 共生成 {len(all_chunks)} 个知识片段")
        return all_chunks
    
    def save_processed(self, output_path: str = "output/processed_knowledge.json"):
        """保存处理后的知识库"""
        chunks = self.process_all()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "total_documents": len(self.documents),
                "total_chunks": len(chunks),
                "chunks": chunks
            }, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {output_path}")


if __name__ == "__main__":
    processor = KnowledgeProcessor()
    processor.save_processed()
