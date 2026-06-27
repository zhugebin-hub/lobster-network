#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 向量记忆系统
版本: V1.0 | 日期: 2026-06-27
功能: 基于向量数据库的智能体记忆系统，支持语义搜索和长期记忆
"""

import json
import os
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class VectorMemory:
    """向量记忆系统"""
    
    def __init__(self, storage_path: str = None, embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        if storage_path is None:
            # 优先 /shared，fallback 到本地
            shared_path = "/shared/training/go/vector_memory"
            local_path = os.path.expanduser("~/.lobster-network/vector_memory")
            if os.access("/shared/training/go", os.W_OK):
                storage_path = shared_path
            else:
                storage_path = local_path
        self.storage_path = storage_path
        self.collections = {
            "episodic": [],      # 事件记忆
            "semantic": [],      # 语义记忆
            "procedural": []     # 程序记忆
        }
        self.metadata = {}
        self._ensure_storage()
        self._load_data()
        
        # 加载向量嵌入模型
        self._embedding_model_name = embedding_model
        self._embedding_model = None
    
    @property
    def embedding_model(self):
        """懒加载嵌入模型（仅在有缓存时加载，否则使用离线 n-gram）"""
        if self._embedding_model is None:
            # 检查是否有本地缓存
            cache_path = os.path.expanduser(f"~/.cache/huggingface/hub/models--sentence-transformers--{self._embedding_model_name.replace('/', '--')}")
            if os.path.exists(cache_path):
                try:
                    from sentence_transformers import SentenceTransformer
                    self._embedding_model = SentenceTransformer(self._embedding_model_name)
                    print(f"✅ 向量嵌入模型已加载: {self._embedding_model_name}")
                except Exception as e:
                    print(f"⚠️ 向量嵌入模型加载失败: {e}，将使用离线 n-gram 嵌入")
                    self._embedding_model = False
            else:
                # 无缓存，直接使用离线 n-gram
                self._embedding_model = False
        return self._embedding_model if self._embedding_model else None
    
    def _generate_ngram_embedding(self, text: str, n: int = 3, dim: int = 256) -> List[float]:
        """
        使用字符 n-gram + hash trick 生成离线向量嵌入
        不依赖网络，完全本地计算
        """
        import hashlib
        
        # 生成字符 n-gram
        ngrams = []
        for i in range(len(text) - n + 1):
            ngrams.append(text[i:i+n])
        
        if not ngrams:
            # 如果文本太短，用单个字符
            ngrams = list(text)
        
        # 使用 hash trick 将 n-gram 映射到向量
        embedding = [0.0] * dim
        for ngram in ngrams:
            hash_val = int(hashlib.md5(ngram.encode('utf-8')).hexdigest(), 16)
            index = hash_val % dim
            # 使用符号 hash 决定正负
            sign = 1 if (hash_val >> 32) % 2 == 0 else -1
            embedding[index] += sign
        
        # L2 归一化
        norm = np.sqrt(sum(x*x for x in embedding))
        if norm > 0:
            embedding = [x / norm for x in embedding]
        
        return embedding
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
        for collection in self.collections.keys():
            os.makedirs(os.path.join(self.storage_path, collection), exist_ok=True)
    
    def _load_data(self):
        """加载现有数据"""
        for collection, items in self.collections.items():
            collection_path = os.path.join(self.storage_path, f"{collection}.json")
            if os.path.exists(collection_path):
                with open(collection_path, "r", encoding="utf-8") as f:
                    self.collections[collection] = json.load(f)
    
    def _save_data(self):
        """保存数据"""
        for collection, items in self.collections.items():
            collection_path = os.path.join(self.storage_path, f"{collection}.json")
            with open(collection_path, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
    
    def add_memory(self, memory_type: str, content: str, metadata: Dict = None) -> str:
        """添加记忆"""
        if memory_type not in self.collections:
            raise ValueError(f"未知记忆类型: {memory_type}")
        
        # 生成唯一ID
        memory_id = hashlib.md5(f"{memory_type}:{content}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        # 生成向量嵌入
        embedding = self._generate_embedding(content)
        
        memory = {
            "id": memory_id,
            "type": memory_type,
            "content": content,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0,
            "importance": self._calculate_importance(content, metadata),
            "embedding": embedding  # 新增：向量嵌入
        }
        
        self.collections[memory_type].append(memory)
        self._save_data()
        
        return memory_id
    
    def _generate_embedding(self, content: str) -> Optional[List[float]]:
        """生成文本的向量嵌入（优先使用 sentence-transformers，fallback 到离线 n-gram）"""
        # 尝试使用 sentence-transformers
        model = self.embedding_model
        if model:
            try:
                embedding = model.encode(content)
                return embedding.tolist()
            except Exception as e:
                pass  # 继续尝试离线 fallback
        
        # Fallback: 使用离线 n-gram 嵌入
        return self._generate_ngram_embedding(content)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        a = np.array(vec1)
        b = np.array(vec2)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def search(self, query: str, memory_type: str = None, top_k: int = 5) -> List[Dict]:
        """搜索记忆（优先使用向量相似度，fallback 到关键词匹配）"""
        results = []
        
        # 确定搜索范围
        if memory_type:
            collections = {memory_type: self.collections.get(memory_type, [])}
        else:
            collections = self.collections
        
        # 尝试使用向量嵌入搜索
        query_embedding = self._generate_embedding(query)
        use_vector = query_embedding is not None
        
        for coll_type, items in collections.items():
            for item in items:
                if use_vector and item.get("embedding"):
                    # 向量相似度搜索
                    score = self._cosine_similarity(query_embedding, item["embedding"])
                    # 将余弦相似度 [-1,1] 映射到 [0,1]
                    score = (score + 1) / 2
                    # 重要性加权
                    importance = item.get("importance", 0.5)
                    score = score * 0.7 + importance * 0.3
                    search_method = "vector"
                else:
                    # Fallback: 关键词匹配
                    score = self._calculate_relevance(query, item)
                    search_method = "keyword"
                
                if score > 0:
                    item_copy = item.copy()
                    item_copy["score"] = score
                    item_copy["search_method"] = search_method
                    item_copy["access_count"] = item.get("access_count", 0) + 1
                    results.append(item_copy)
        
        # 按相关性排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取记忆"""
        for collection in self.collections.values():
            for item in collection:
                if item["id"] == memory_id:
                    item["access_count"] = item.get("access_count", 0) + 1
                    self._save_data()
                    return item
        return None
    
    def update_memory(self, memory_id: str, updates: Dict) -> bool:
        """更新记忆"""
        for collection in self.collections.values():
            for item in collection:
                if item["id"] == memory_id:
                    item.update(updates)
                    item["updated_at"] = datetime.now().isoformat()
                    self._save_data()
                    return True
        return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        for collection in self.collections.values():
            for i, item in enumerate(collection):
                if item["id"] == memory_id:
                    collection.pop(i)
                    self._save_data()
                    return True
        return False
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = sum(len(items) for items in self.collections.values())
        with_embedding = sum(1 for items in self.collections.values() for item in items if item.get("embedding"))
        stats = {
            "total_memories": total,
            "memories_with_embedding": with_embedding,
            "by_type": {k: len(v) for k, v in self.collections.items()},
            "storage_path": self.storage_path,
            "embedding_model": self._embedding_model_name if self.embedding_model else "unavailable"
        }
        return stats
    
    def batch_embed(self, memory_type: str = None) -> int:
        """批量为没有嵌入的记忆生成向量"""
        count = 0
        collections_to_process = {}
        if memory_type:
            collections_to_process[memory_type] = self.collections.get(memory_type, [])
        else:
            collections_to_process = self.collections
        
        for coll_type, items in collections_to_process.items():
            for item in items:
                if not item.get("embedding") and item.get("content"):
                    embedding = self._generate_embedding(item["content"])
                    if embedding:
                        item["embedding"] = embedding
                        count += 1
        
        if count > 0:
            self._save_data()
        
        return count
    
    def _calculate_importance(self, content: str, metadata: Dict = None) -> float:
        """计算重要性分数"""
        importance = 0.5  # 基础分数
        
        # 关键词权重
        important_keywords = ["评估", "考核", "晋升", "突破", "关键", "重要"]
        for keyword in important_keywords:
            if keyword in content:
                importance += 0.1
        
        # 元数据权重
        if metadata:
            if metadata.get("priority") == "high":
                importance += 0.2
            elif metadata.get("priority") == "medium":
                importance += 0.1
        
        return min(importance, 1.0)
    
    def _calculate_relevance(self, query: str, item: Dict) -> float:
        """计算相关性分数"""
        content = item.get("content", "").lower()
        query_lower = query.lower()
        
        # 简单关键词匹配
        query_words = query_lower.split()
        match_count = sum(1 for word in query_words if word in content)
        
        if match_count == 0:
            return 0.0
        
        # 基础分数
        score = match_count / len(query_words)
        
        # 重要性加权
        importance = item.get("importance", 0.5)
        score *= (0.5 + importance * 0.5)
        
        # 时间衰减（较新的记忆权重更高）
        created_at = item.get("created_at", "")
        if created_at:
            try:
                created = datetime.fromisoformat(created_at)
                days_old = (datetime.now() - created).days
                time_factor = max(0.5, 1.0 - days_old * 0.01)
                score *= time_factor
            except:
                pass
        
        return score
    
    def import_from_files(self, directory: str = "/home/admin/.openclaw/workspace/memory"):
        """从文件导入记忆"""
        if not os.path.exists(directory):
            return
        
        imported = 0
        for filename in os.listdir(directory):
            if filename.endswith(".md"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 解析日期
                date_str = filename.replace(".md", "")
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    metadata = {
                        "source": "memory_file",
                        "date": date_str,
                        "original_file": filename
                    }
                    
                    self.add_memory("episodic", content, metadata)
                    imported += 1
                except:
                    pass
        
        self._save_data()
        return imported

if __name__ == "__main__":
    # 测试向量记忆系统 V2.0
    vm = VectorMemory()
    
    print("🦞 向量记忆系统 V2.0 测试")
    print(f"   存储路径: {vm.storage_path}")
    
    # 检查嵌入模型
    model = vm.embedding_model
    if model:
        print(f"   嵌入模型: {vm._embedding_model_name} ✅")
    else:
        print(f"   嵌入模型: 不可用（将使用关键词匹配 fallback）⚠️")
    
    # 添加记忆
    print("\n📝 添加记忆...")
    id1 = vm.add_memory("episodic", "2026-06-27: 小陈完成V6 W1D1训练，25题，准确率83.3%", {"date": "2026-06-27", "student": "xiaochen"})
    id2 = vm.add_memory("episodic", "2026-06-27: 诸葛虾完成V6 W1D1训练，33题，准确率76.7%", {"date": "2026-06-27", "student": "zhuguxia"})
    id3 = vm.add_memory("semantic", "围棋九段训练方案V6: 26周训练周期，四阶段路径", {"topic": "training_plan", "version": "V6"})
    id4 = vm.add_memory("procedural", "验证门控规则: 准确率>90%升档，<70%降档，连续3天<60%专项补强", {"topic": "validation"})
    id5 = vm.add_memory("episodic", "小陈在死活题上表现优异，准确率达到87.5%，但官子部分只有50%正确率", {"date": "2026-06-27", "student": "xiaochen", "topic": "weakness"})
    id6 = vm.add_memory("episodic", "诸葛虾征子路线判断能力不足，需要专项训练长征子题目", {"date": "2026-06-27", "student": "zhuguxia", "topic": "weakness"})
    
    print(f"   已添加6条记忆")
    
    # 向量搜索测试
    print("\n🔍 向量语义搜索（语义相似度）...")
    results = vm.search("学员训练表现评估", top_k=3)
    print(f"   找到 {len(results)} 条结果")
    for r in results:
        print(f"   - [{r.get('search_method', '?')}] {r['content'][:60]}... (score: {r['score']:.3f})")
    
    # 关键词搜索测试
    print("\n🔍 关键词搜索（fallback）...")
    results = vm.search("小陈 训练", top_k=3)
    print(f"   找到 {len(results)} 条结果")
    for r in results:
        print(f"   - [{r.get('search_method', '?')}] {r['content'][:60]}... (score: {r['score']:.3f})")
    
    # 语义搜索测试 - 相似语义不同词汇
    print("\n🔍 语义搜索（相似语义不同词汇）...")
    results = vm.search("学生成绩分析", top_k=3)
    print(f"   找到 {len(results)} 条结果")
    for r in results:
        print(f"   - [{r.get('search_method', '?')}] {r['content'][:60]}... (score: {r['score']:.3f})")
    
    # 获取记忆
    print("\n📖 获取记忆...")
    memory = vm.get_memory(id1)
    if memory:
        print(f"   找到: {memory['content'][:50]}...")
        emb = memory.get('embedding')
        if emb:
            print(f"   向量维度: {len(emb)}")
        else:
            print(f"   向量维度: 无（嵌入模型不可用）")
    
    # 统计信息
    print("\n📊 统计信息:")
    stats = vm.get_stats()
    print(f"   总记忆数: {stats['total_memories']}")
    print(f"   有嵌入的记忆: {stats['memories_with_embedding']}")
    print(f"   按类型: {stats['by_type']}")
    print(f"   嵌入模型: {stats['embedding_model']}")
    
    print("\n✅ 向量记忆系统 V2.0 测试完成")
