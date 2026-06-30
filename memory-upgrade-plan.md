# OpenClaw 记忆系统升级实施计划

> **状态**：🟡 进行中  
> **创建时间**：2026-04-19  
> **负责人**：诸葛虾  
> **参考文档**：`hermes-design-analysis.md`

---

## 📋 项目概述

**目标**：借鉴 Hermes Agent 设计理念，增强 OpenClaw 记忆系统和自改进能力

**范围**：
- ✅ 增强 self-improvement skill
- ✅ 添加全文搜索工具
- ⏳ 评估 ChromaDB 向量存储
- ⏳ 开发自改进引擎

---

## 🎯 阶段一：轻量级增强（1-2 周）

### 任务 1：增强 self-improvement skill

**当前状态**：⏳ 待实施

**需求**：
- 自动从任务失败/成功中提取 learnings
- 自动更新 MEMORY.md
- 自动生成技能优化建议

**实施步骤**：

```bash
# 1. 查看当前 self-improvement skill
cd ~/.openclaw/workspace/skills/self-improving-agent/
cat SKILL.md

# 2. 增强自动提取逻辑
# 3. 添加自动更新 MEMORY.md 功能
# 4. 生成技能优化建议
```

**验收标准**：
- [ ] 任务完成后自动询问是否记录 learning
- [ ] 支持一键更新 MEMORY.md
- [ ] 生成技能建议文档

**预计时间**：3-5 天

---

### 任务 2：添加全文搜索工具

**当前状态**：⏳ 待实施

**需求**：
- 开发 search-memory 命令
- 支持关键词高亮
- 按日期/主题过滤

**实施步骤**：

```bash
# 1. 创建搜索脚本
cat > ~/.openclaw/workspace/scripts/search-memory.sh << 'EOF'
#!/bin/bash
# OpenClaw 记忆搜索工具

QUERY="$1"
DATE_FILTER="$2"

echo "🔍 搜索记忆：$QUERY"
echo "================================"

# 搜索 MEMORY.md
echo "📄 长期记忆："
grep -n -C 2 "$QUERY" ~/.openclaw/workspace/MEMORY.md 2>/dev/null || echo "  未找到"

echo ""

# 搜索每日记忆
echo "📅 每日记忆："
if [ -n "$DATE_FILTER" ]; then
    grep -n -C 2 "$QUERY" ~/.openclaw/workspace/memory/$DATE_FILTER.md 2>/dev/null || echo "  未找到"
else
    grep -r -n -C 2 "$QUERY" ~/.openclaw/workspace/memory/ 2>/dev/null | head -20
fi

echo ""
echo "================================"
echo "搜索完成"
EOF

chmod +x ~/.openclaw/workspace/scripts/search-memory.sh

# 2. 测试搜索
~/.openclaw/workspace/scripts/search-memory.sh "关键词"
```

**验收标准**：
- [ ] 支持关键词搜索
- [ ] 支持日期过滤
- [ ] 显示上下文（前后 2 行）
- [ ] 结果高亮显示

**预计时间**：2-3 天

---

### 任务 3：改进记忆管理

**当前状态**：⏳ 待实施

**需求**：
- 自动去重
- 智能归档
- 定期清理

**实施步骤**：

```bash
# 1. 创建记忆管理脚本
cat > ~/.openclaw/workspace/scripts/manage-memory.sh << 'EOF'
#!/bin/bash
# OpenClaw 记忆管理工具

ACTION="$1"

case $ACTION in
    "dedup")
        echo "🔄 执行去重..."
        # 实现去重逻辑
        ;;
    "archive")
        echo "📦 归档旧记忆..."
        # 实现归档逻辑
        ;;
    "clean")
        echo "🧹 清理过期记忆..."
        # 实现清理逻辑
        ;;
    "status")
        echo "📊 记忆状态："
        echo "  长期记忆：$(wc -l < ~/.openclaw/workspace/MEMORY.md) 行"
        echo "  每日记忆：$(ls ~/.openclaw/workspace/memory/*.md 2>/dev/null | wc -l) 个文件"
        echo "  总大小：$(du -sh ~/.openclaw/workspace/memory/ 2>/dev/null | cut -f1)"
        ;;
    *)
        echo "用法：manage-memory.sh [dedup|archive|clean|status]"
        ;;
esac
EOF

chmod +x ~/.openclaw/workspace/scripts/manage-memory.sh
```

**验收标准**：
- [ ] 查看记忆状态
- [ ] 执行去重操作
- [ ] 归档旧记忆（>30 天）
- [ ] 清理临时文件

**预计时间**：2-3 天

---

## 🎯 阶段二：向量存储实验（2-4 周）

### 任务 4：技术验证

**当前状态**：⏳ 待实施

**需求**：
- 安装 ChromaDB
- 测试嵌入模型（中文支持）
- 性能基准测试

**实施步骤**：

```bash
# 1. 安装 ChromaDB 和嵌入模型
pip3 install chromadb sentence-transformers

# 2. 测试中文嵌入模型
python3 << 'EOF'
from sentence_transformers import SentenceTransformer

# 加载模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 测试中文
texts = ["今天天气很好", "我喜欢吃小龙虾", "OpenClaw 很强大"]
embeddings = model.encode(texts)

print(f"嵌入维度：{embeddings.shape}")
print("✅ 中文嵌入测试通过")
EOF

# 3. 性能测试
# - 索引 1000 条记录的时间
# - 搜索响应时间
# - 内存占用
```

**验收标准**：
- [ ] ChromaDB 安装成功
- [ ] 中文嵌入模型工作正常
- [ ] 性能满足要求（搜索<100ms）

**预计时间**：3-5 天

---

### 任务 5：开发索引服务

**当前状态**：⏳ 待实施

**需求**：
- 初始索引构建
- 增量更新机制
- 后台守护进程

**实施步骤**：

```bash
# 1. 创建索引服务脚本
cat > ~/.openclaw/workspace/scripts/vector-index.py << 'EOF'
#!/usr/bin/env python3
"""
OpenClaw 向量索引服务
"""

import chromadb
from sentence_transformers import SentenceTransformer
import os
import json
from datetime import datetime

class MemoryIndexer:
    def __init__(self):
        # 初始化 ChromaDB
        self.client = chromadb.Client(chromadb.config.Settings(
            persist_directory=os.path.expanduser("~/.openclaw/workspace/vector-store/"),
            anonymized_telemetry=False
        ))
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="openclaw-memory",
            metadata={"description": "OpenClaw 记忆向量存储"}
        )
        
        # 加载嵌入模型
        print("加载嵌入模型...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ 模型加载完成")
    
    def index_memory_file(self, filepath):
        """索引单个记忆文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 生成嵌入
        embedding = self.model.encode(content).tolist()
        
        # 生成 ID
        doc_id = f"memory-{os.path.basename(filepath)}"
        
        # 添加到集合
        self.collection.upsert(
            embeddings=[embedding],
            documents=[content],
            metadatas=[{
                "source": filepath,
                "indexed_at": datetime.now().isoformat()
            }],
            ids=[doc_id]
        )
        
        print(f"✅ 已索引：{filepath}")
    
    def index_all(self):
        """索引所有记忆文件"""
        memory_dir = os.path.expanduser("~/.openclaw/workspace/memory/")
        
        # 索引 MEMORY.md
        self.index_memory_file(os.path.expanduser("~/.openclaw/workspace/MEMORY.md"))
        
        # 索引每日记忆
        if os.path.exists(memory_dir):
            for filename in os.listdir(memory_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(memory_dir, filename)
                    self.index_memory_file(filepath)
        
        print(f"✅ 索引完成。集合中共有 {self.collection.count()} 个文档")
    
    def search(self, query, n_results=5):
        """语义搜索"""
        query_embedding = self.model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        return results

if __name__ == "__main__":
    import sys
    
    indexer = MemoryIndexer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "index":
            indexer.index_all()
        elif sys.argv[1] == "search":
            query = sys.argv[2] if len(sys.argv) > 2 else "测试查询"
            results = indexer.search(query)
            for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
                print(f"\n来源：{meta['source']}")
                print(f"相似度：{1-dist:.3f}")
                print(f"内容：{doc[:200]}...")
    else:
        print("用法：vector-index.py [index|search] [query]")
EOF

chmod +x ~/.openclaw/workspace/scripts/vector-index.py
```

**验收标准**：
- [ ] 成功索引所有记忆文件
- [ ] 增量更新工作正常
- [ ] 搜索返回相关结果

**预计时间**：5-7 天

---

### 任务 6：集成到 OpenClaw

**当前状态**：⏳ 待实施

**需求**：
- 在任务前自动检索相关上下文
- 注入到系统提示
- 提升任务准确性

**实施步骤**：

```python
# 1. 创建 OpenClaw 集成模块
cat > ~/.openclaw/workspace/scripts/openclaw-context.py << 'EOF'
#!/usr/bin/env python3
"""
OpenClaw 上下文检索模块
在任务执行前自动检索相关记忆
"""

from vector_index import MemoryIndexer
import json
import sys

def get_relevant_context(query, max_tokens=1000):
    """获取相关上下文"""
    indexer = MemoryIndexer()
    results = indexer.search(query, n_results=3)
    
    context = []
    total_tokens = 0
    
    for doc, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
        similarity = 1 - dist
        if similarity > 0.6:  # 相似度阈值
            context.append({
                "source": meta['source'],
                "similarity": similarity,
                "content": doc[:500]  # 限制长度
            })
            total_tokens += len(doc) // 4  # 粗略估算
    
    return {
        "query": query,
        "context": context,
        "total_tokens": total_tokens
    }

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "当前任务"
    result = get_relevant_context(query)
    print(json.dumps(result, ensure_ascii=False, indent=2))
EOF
```

**验收标准**：
- [ ] 任务前自动检索
- [ ] 上下文注入到提示
- [ ] 任务准确性提升

**预计时间**：3-5 天

---

## 📅 时间表

| 阶段 | 任务 | 开始日期 | 结束日期 | 状态 |
|------|------|----------|----------|------|
| 阶段一 | 任务 1：增强 self-improvement | 2026-04-19 | 2026-04-24 | ⏳ 待开始 |
| 阶段一 | 任务 2：添加全文搜索 | 2026-04-22 | 2026-04-25 | ⏳ 待开始 |
| 阶段一 | 任务 3：改进记忆管理 | 2026-04-25 | 2026-04-28 | ⏳ 待开始 |
| 阶段二 | 任务 4：技术验证 | 2026-04-26 | 2026-05-01 | ⏳ 待开始 |
| 阶段二 | 任务 5：开发索引服务 | 2026-05-01 | 2026-05-08 | ⏳ 待开始 |
| 阶段二 | 任务 6：集成到 OpenClaw | 2026-05-08 | 2026-05-13 | ⏳ 待开始 |

---

## 📊 进度追踪

### 总体进度

```
[████████░░░░░░░░░░░░] 20% 完成

阶段一：轻量级增强 [░░░░░░░░░░] 0%
阶段二：向量存储实验 [░░░░░░░░░░] 0%
```

### 本周目标

- [ ] 完成 self-improvement skill 增强
- [ ] 创建全文搜索工具
- [ ] 编写用户使用指南

---

## 📝 会议记录

### 2026-04-19 启动会议

**参会人员**：诸葛虾

**决策**：
1. 采用渐进式升级策略
2. 先实施方案 A（轻量级增强）
3. 并行验证方案 B（向量存储）

**待办**：
- [ ] 开始实施任务 1
- [ ] 准备技术验证环境

---

## 🔗 相关文档

- 调研报告：`hermes-agent-research.md`
- 设计分析：`hermes-design-analysis.md`
- 部署框架：`hermes-agent-framework.md`
- 需求分析：`teaching-automation-requirements.md`

---

**最后更新**：2026-04-19  
**下次更新**：2026-04-22
