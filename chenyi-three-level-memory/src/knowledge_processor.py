"""
知识库预处理模块
负责文档的读取、清洗、切片和元数据标注
"""

import os
import re
from typing import List, Dict, Tuple
from datetime import datetime


class KnowledgeProcessor:
    """知识库处理器"""
    
    def __init__(self, kb_path: str = "knowledge_base"):
        self.kb_path = kb_path
        self.documents = []
    
    def load_all_documents(self) -> List[Dict]:
        """加载所有文档"""
        self.documents = []
        
        for root, dirs, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    doc = self._load_document(filepath)
                    if doc:
                        self.documents.append(doc)
        
        print(f"📄 加载了 {len(self.documents)} 份文档")
        return self.documents
    
    def _load_document(self, filepath: str) -> Dict:
        """加载单个文档"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = self._extract_metadata(content)
            clean_content = self._clean_content(content)
            
            return {
                "filepath": filepath,
                "filename": os.path.basename(filepath),
                "category": self._get_category(filepath),
                "metadata": metadata,
                "content": clean_content,
                "word_count": len(clean_content)
            }
        except Exception as e:
            print(f"⚠️ 加载文档失败 {filepath}: {e}")
            return None
    
    def _extract_metadata(self, content: str) -> Dict:
        """提取元数据"""
        metadata = {}
        for line in content.split('\n')[:5]:
            if '类别：' in line:
                metadata['category'] = line.split('类别：')[1].split('|')[0].strip()
            if '可信度：' in line:
                metadata['credibility'] = line.split('可信度：')[1].split('|')[0].strip()
            if '日期：' in line:
                metadata['date'] = line.split('日期：')[1].strip()
        return metadata
    
    def _clean_content(self, content: str) -> str:
        """清洗内容"""
        lines = content.split('\n')
        cleaned = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('【知识文档】'):
                cleaned.append(line)
        return '\n\n'.join(cleaned)
    
    def _get_category(self, filepath: str) -> str:
        """从路径获取分类"""
        parts = filepath.split('/')
        if 'articles' in parts:
            return 'articles'
        elif 'courseware' in parts:
            return 'courseware'
        elif 'web_pages' in parts:
            return 'web_pages'
        return 'unknown'
    
    def chunk_document(self, content: str, max_chunk_size: int = 800) -> List[str]:
        """将文档切片"""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def process_all(self) -> List[Dict]:
        """处理所有文档：加载 + 切片"""
        docs = self.load_all_documents()
        all_chunks = []
        
        for doc in docs:
            chunks = self.chunk_document(doc['content'])
            for i, chunk in enumerate(chunks):
                all_chunks.append({
                    "doc_id": doc['filename'],
                    "chunk_id": f"{doc['filename']}_chunk_{i}",
                    "content": chunk,
                    "category": doc['category'],
                    "metadata": doc['metadata'],
                    "word_count": len(chunk)
                })
        
        print(f"✂️ 共生成 {len(all_chunks)} 个知识片段")
        return all_chunks
    
    def generate_statistics(self) -> Dict:
        """生成统计信息"""
        stats = {
            "total_documents": len(self.documents),
            "categories": {},
            "credibility": {},
            "total_words": 0,
            "avg_words_per_doc": 0
        }
        
        for doc in self.documents:
            cat = doc['metadata'].get('category', 'unknown')
            cred = doc['metadata'].get('credibility', 'unknown')
            
            stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
            stats['credibility'][cred] = stats['credibility'].get(cred, 0) + 1
            stats['total_words'] += doc['word_count']
        
        if stats['total_documents'] > 0:
            stats['avg_words_per_doc'] = stats['total_words'] / stats['total_documents']
        
        return stats


# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    processor = KnowledgeProcessor()
    
    # 处理所有文档
    chunks = processor.process_all()
    
    # 生成统计
    stats = processor.generate_statistics()
    
    print("\n📊 知识库统计：")
    print(f"  文档总数：{stats['total_documents']}")
    print(f"  总字数：{stats['total_words']}")
    print(f"  平均每篇字数：{stats['avg_words_per_doc']:.0f}")
    print(f"\n  分类分布：")
    for cat, count in stats['categories'].items():
        print(f"    - {cat}: {count}")
    print(f"\n  可信度分布：")
    for cred, count in stats['credibility'].items():
        print(f"    - {cred}: {count}")
