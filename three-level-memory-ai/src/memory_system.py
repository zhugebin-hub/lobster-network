"""
三级记忆 AI 助手 - 核心系统
实现感知记忆、短期记忆、长期记忆三层架构
"""

import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict


# ============================================================
# 第一级：感知记忆（对话上下文窗口）
# ============================================================
class SensoryMemory:
    """感知记忆：保留单轮对话的即时信息"""
    
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns  # 最多保留的对话轮数
        self.context: List[Dict] = []  # 对话上下文
    
    def add_turn(self, role: str, content: str):
        """添加一轮对话"""
        self.context.append({
            "role": role,
            "content": content,
            "timestamp": time.time()
        })
        # 超出窗口时移除最旧的
        if len(self.context) > self.max_turns:
            self.context = self.context[-self.max_turns:]
    
    def get_context(self) -> List[Dict]:
        """获取当前上下文"""
        return self.context.copy()
    
    def get_context_text(self) -> str:
        """获取格式化的对话历史"""
        return "\n".join([
            f"[{turn['role']}]: {turn['content']}"
            for turn in self.context
        ])
    
    def clear(self):
        """清空感知记忆"""
        self.context.clear()


# ============================================================
# 第二级：短期记忆（跨会话历史缓存）
# ============================================================
class ShortTermMemory:
    """短期记忆：保留数天对话记录，支持跨会话检索"""
    
    def __init__(self, retention_days: int = 7, storage_path: str = "output/short_term_memory.json"):
        self.retention_days = retention_days
        self.storage_path = storage_path
        self.sessions: Dict[str, Dict] = {}
        self._load()
        self._cleanup()
    
    def _load(self):
        """从文件加载"""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.sessions = data.get('sessions', {})
    
    def _save(self):
        """保存到文件"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump({'sessions': self.sessions, 'updated': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    
    def _cleanup(self):
        """清理过期会话"""
        cutoff = time.time() - self.retention_days * 86400
        self.sessions = {
            k: v for k, v in self.sessions.items()
            if v.get('last_access', 0) > cutoff
        }
        self._save()
    
    def add_message(self, session_id: str, role: str, content: str, tags: List[str] = None):
        """添加消息到短期记忆"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created": time.time(),
                "last_access": time.time(),
                "messages": [],
                "tags": []
            }
        
        session = self.sessions[session_id]
        session["messages"].append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "tags": tags or []
        })
        session["last_access"] = time.time()
        if tags:
            session["tags"] = list(set(session["tags"] + tags))
        
        self._save()
    
    def get_recent_messages(self, session_id: str, limit: int = 20) -> List[Dict]:
        """获取最近的消息"""
        if session_id not in self.sessions:
            return []
        messages = self.sessions[session_id]["messages"]
        return messages[-limit:]
    
    def search_by_tags(self, tags: List[str]) -> List[Dict]:
        """按标签搜索"""
        results = []
        for sid, session in self.sessions.items():
            if any(tag in session.get("tags", []) for tag in tags):
                results.append({
                    "session_id": sid,
                    "messages": session["messages"][-5:],  # 最近5条
                    "tags": session["tags"]
                })
        return results


# ============================================================
# 第三级：长期记忆（RAG向量知识库）
# ============================================================
@dataclass
class KnowledgeChunk:
    """知识片段"""
    id: str
    content: str
    source: str
    category: str
    date: str
    credibility: str
    embedding: Optional[List[float]] = None


class LongTermMemory:
    """长期记忆：向量化知识库 + RAG语义检索"""
    
    def __init__(self, kb_path: str = "knowledge_base", output_path: str = "output/vector_store.json"):
        self.kb_path = kb_path
        self.output_path = output_path
        self.chunks: List[KnowledgeChunk] = []
        self._load_or_build()
    
    def _load_or_build(self):
        """加载或构建知识库"""
        # 尝试加载已有向量库
        if os.path.exists(self.output_path):
            with open(self.output_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks = [KnowledgeChunk(**item) for item in data.get('chunks', [])]
                print(f"📚 加载了 {len(self.chunks)} 个知识片段")
        else:
            self._build_knowledge_base()
    
    def _build_knowledge_base(self):
        """构建知识库：读取文档、切片、标注"""
        print("🔨 开始构建知识库...")
        chunk_id = 0
        
        for root, dirs, files in os.walk(self.kb_path):
            for file in files:
                if file.endswith('.txt'):
                    filepath = os.path.join(root, file)
                    chunks = self._process_document(filepath)
                    self.chunks.extend(chunks)
                    chunk_id += len(chunks)
        
        # 生成简化版嵌入（实际项目中使用Embedding模型）
        for chunk in self.chunks:
            chunk.embedding = self._simple_embedding(chunk.content)
        
        self._save()
        print(f"✅ 知识库构建完成，共 {len(self.chunks)} 个片段")
    
    def _process_document(self, filepath: str) -> List[KnowledgeChunk]:
        """处理单个文档：清洗、切片、标注"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取元数据
        metadata = self._extract_metadata(content)
        clean_content = self._clean_content(content)
        
        # 按段落切片（模拟500-1000 tokens切片）
        paragraphs = clean_content.split('\n\n')
        chunks = []
        
        current_chunk = ""
        chunk_idx = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(current_chunk) + len(para) > 800:  # 约500-1000 tokens
                if current_chunk:
                    chunks.append(KnowledgeChunk(
                        id=f"chunk_{len(chunks):04d}",
                        content=current_chunk,
                        source=os.path.basename(filepath),
                        category=metadata.get('category', 'unknown'),
                        date=metadata.get('date', 'unknown'),
                        credibility=metadata.get('credibility', 'medium')
                    ))
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        if current_chunk:
            chunks.append(KnowledgeChunk(
                id=f"chunk_{len(chunks):04d}",
                content=current_chunk,
                source=os.path.basename(filepath),
                category=metadata.get('category', 'unknown'),
                date=metadata.get('date', 'unknown'),
                credibility=metadata.get('credibility', 'medium')
            ))
        
        return chunks
    
    def _extract_metadata(self, content: str) -> Dict:
        """从文档头部提取元数据"""
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
    
    def _simple_embedding(self, text: str) -> List[float]:
        """简化版嵌入生成（实际使用text-embedding模型）"""
        # 使用hash生成伪向量用于演示
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()
        embedding = []
        for i in range(0, min(len(h), 32), 2):
            embedding.append(int(h[i:i+2], 16) / 255.0)
        while len(embedding) < 16:
            embedding.append(0.0)
        return embedding[:16]
    
    def _save(self):
        """保存向量库"""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        data = {
            'chunks': [asdict(c) for c in self.chunks],
            'total': len(self.chunks),
            'built_at': datetime.now().isoformat()
        }
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[KnowledgeChunk, float]]:
        """语义检索：返回最相关的top_k个知识片段"""
        query_embedding = self._simple_embedding(query)
        scores = []
        
        for chunk in self.chunks:
            score = self._cosine_similarity(query_embedding, chunk.embedding or [])
            scores.append((chunk, score))
        
        # 按相似度排序
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
    
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


# ============================================================
# 三级记忆系统（整合）
# ============================================================
class ThreeLevelMemorySystem:
    """三级记忆AI助手主系统"""
    
    def __init__(self):
        # 第一级：感知记忆
        self.sensory = SensoryMemory(max_turns=10)
        # 第二级：短期记忆
        self.short_term = ShortTermMemory(retention_days=7)
        # 第三级：长期记忆
        self.long_term = LongTermMemory()
        
        self.session_id = "default_session"
        print("=" * 50)
        print("🧠 三级记忆 AI 助手已启动")
        print("=" * 50)
    
    def chat(self, user_input: str) -> str:
        """处理用户输入，生成回复"""
        # 第一级：感知记忆 - 记录当前对话
        self.sensory.add_turn("user", user_input)
        
        # 第二级：短期记忆 - 记录并检索历史
        self.short_term.add_message(self.session_id, "user", user_input)
        recent_history = self.short_term.get_recent_messages(self.session_id, limit=5)
        
        # 第三级：长期记忆 - 从知识库检索
        retrieved_knowledge = self.long_term.retrieve(user_input, top_k=3)
        
        # 生成回复
        response = self._generate_response(user_input, recent_history, retrieved_knowledge)
        
        # 记录回复
        self.sensory.add_turn("assistant", response)
        self.short_term.add_message(self.session_id, "assistant", response)
        
        return response
    
    def _generate_response(self, query: str, history: List[Dict], knowledge: List[Tuple[KnowledgeChunk, float]]) -> str:
        """生成回复（模拟LLM）"""
        # 检查知识库是否有相关内容
        if knowledge and knowledge[0][1] > 0.3:
            relevant_chunks = [k.content for k, s in knowledge if s > 0.3]
            response = f"📚 根据知识库信息：\n\n"
            for i, chunk in enumerate(relevant_chunks[:2], 1):
                # 截取前200字作为回复内容
                preview = chunk[:300] + "..." if len(chunk) > 300 else chunk
                response += f"> 【知识片段{i}】{preview}\n\n"
            response += "💡 以上信息来自长期记忆（RAG知识库），引用已标注来源。"
        else:
            response = f"🤔 关于「{query}」，我的知识库中没有直接相关的内容。\n\n"
            response += "不过基于我的训练知识，我可以尝试回答：\n"
            response += "这是一个很好的问题！建议查阅相关教材或学术论文获取更详细的信息。"
        
        # 如果有历史对话，提及上下文
        if len(history) > 2:
            response += f"\n\n📋 （当前对话已进行{len(history)}轮，短期记忆正常工作）"
        
        return response
    
    def show_memory_status(self) -> str:
        """显示三级记忆状态"""
        status = "🧠 三级记忆状态报告\n"
        status += "=" * 40 + "\n"
        status += f"第一级・感知记忆：{len(self.sensory.context)} 轮对话\n"
        status += f"第二级・短期记忆：{len(self.short_term.sessions)} 个会话\n"
        status += f"第三级・长期记忆：{len(self.long_term.chunks)} 个知识片段\n"
        
        # 统计知识库类别
        categories = {}
        for chunk in self.long_term.chunks:
            categories[chunk.category] = categories.get(chunk.category, 0) + 1
        
        status += "\n📊 知识库分布：\n"
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            status += f"  - {cat}: {count} 个片段\n"
        
        return status


# ============================================================
# 主程序
# ============================================================
if __name__ == "__main__":
    # 初始化系统
    system = ThreeLevelMemorySystem()
    
    # 显示状态
    print("\n" + system.show_memory_status())
    
    # 模拟对话测试
    test_queries = [
        "什么是机器学习？",
        "深度学习有哪些主要架构？",
        "Transformer的原理是什么？",
        "RAG技术有什么用？",
        "AI伦理问题有哪些？",
    ]
    
    print("\n" + "=" * 50)
    print("🧪 开始测试对话")
    print("=" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 测试 {i}: {query}")
        print("-" * 40)
        response = system.chat(query)
        print(response)
        print()
    
    # 最终状态
    print("\n" + system.show_memory_status())
    print("\n✅ 三级记忆系统测试完成！")
