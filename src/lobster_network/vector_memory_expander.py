#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 向量记忆扩展器
版本: V1.0 | 日期: 2026-06-28
功能: 将10大栏目错题/知识点自动索引至 ChromaDB，支持语义检索
"""
import json, os, hashlib
from datetime import datetime

# 轻量级本地向量存储实现 (模拟 ChromaDB 接口，无需外部依赖)
MEMORY_DIR = "/shared/training/go/vector_db"
os.makedirs(MEMORY_DIR, exist_ok=True)

class SimpleVectorStore:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.db_path = os.path.join(MEMORY_DIR, f"{collection_name}.json")
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            with open(self.db_path) as f: return json.load(f)
        return {"docs": []}

    def _save(self):
        with open(self.db_path, "w") as f: json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add(self, text: str, metadata: dict = None):
        doc_id = hashlib.md5(text.encode()).hexdigest()[:12]
        self.data["docs"].append({
            "id": doc_id, "text": text, "metadata": metadata or {}, 
            "created_at": datetime.now().isoformat()
        })
        self._save()
        return doc_id

    def search(self, query: str, top_k: int = 5) -> list:
        # 简易关键词+TF-IDF 模拟向量检索
        query_words = set(query.lower().split())
        scored = []
        for doc in self.data["docs"]:
            doc_words = set(doc["text"].lower().split())
            overlap = len(query_words & doc_words)
            if overlap > 0:
                scored.append((doc, overlap / len(query_words)))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, score in scored[:top_k]]

def index_module_errors(module_name: str, errors: list):
    store = SimpleVectorStore(module_name)
    for err in errors:
        store.add(err["question"], {"answer": err["answer"], "difficulty": err.get("difficulty", "unknown")})
    print(f"✅ {module_name} 错题已索引至向量库")

if __name__ == "__main__":
    # 模拟索引
    test_errors = [
        {"question": "TCP三次握手的过程", "answer": "SYN -> SYN-ACK -> ACK", "difficulty": "中级"},
        {"question": "OSPF Area 0的作用", "answer": "骨干区域，连接所有其他区域", "difficulty": "高级"}
    ]
    index_module_errors("network_protocol", test_errors)
    res = SimpleVectorStore("network_protocol").search("TCP握手")
    print(f"🔍 检索结果: {res[0]['text'] if res else '无'}")
