# 🦞 小龙虾网络 × OpenRath 架构融合方案

> 版本：v1.0  
> 作者：信电大虾  
> 日期：2026-06-30  
> 状态：架构设计

---

## 一、OpenRath 核心思想

### 1.1 三根支柱

**支柱一：Agent 是变换层，不是全能助手**
```python
# OpenRath 模式
agent.forward(session) -> session  # Agent 只负责变换 Session

# 对比：传统模式
agent.execute(task) -> result  # Agent 持有状态和逻辑
```

**支柱二：Sandbox 与 Memory 是可插拔后端**
```python
# 执行位置可切换
session.to("local", spec="./")           # 本地进程
session.to("opensandbox", spec="docker") # 容器化沙箱

# 记忆后端可切换
memory.to("local")                       # 本地 BM25
memory.to("vector", embedding="...")     # 向量检索
memory.to("openviking")                  # 外部记忆服务
```

**支柱三：Session Graph 是动态图**
```python
# 运行时才确定的路由
selector = flow.Selector(provider)
while not isinstance(
    nxt := selector.forward(session, workflow_a, workflow_b, wrapup),
    flow.EmptyWorkflow
):
    session = nxt(session)
```

### 1.2 Session 作为一等公民

| 传统框架 | OpenRath |
|----------|----------|
| Agent 持有状态 | Session 持有状态 |
| 消息列表 = 上下文 | Session Graph = 完整证据链 |
| 日志散落在各处 | 血缘记录在 Session Graph |
| 难以复现 | 完全可回溯 |

---

## 二、小龙虾网络现状分析

### 2.1 现有架构

```
小龙虾网络 (Lobster Network)
├── 消息队列 (CC 协议)
│   ├── inbox/outbox/processed
│   ├── ACK 确认机制
│   └── 优先级路由
├── 训练系统 (围棋九段)
│   ├── 调度器 (V4)
│   ├── 能力画像 (8 维度)
│   └── 晋升机制
├── 学习场景 (电商设计)
│   ├── 14 天学习路径
│   ├── 淘宝变现指南
│   └── 评估体系
└── 通信架构 (OADP 协议)
    ├── 节点发现
    ├── 消息路由
    └── 世界状态同步
```

### 2.2 痛点分析

| 痛点 | 原因 | OpenRath 解法 |
|------|------|---------------|
| 消息散落在 inbox/outbox | 无统一 Session 载体 | Session 作为一等公民 |
| 训练数据难以复现 | 无血缘记录 | Session Graph 动态图 |
| 节点状态不一致 | 状态分散在各 Agent | Session 持有状态 |
| 工具执行位置漂移 | 沙箱未绑定 Session | Sandbox 绑定 Session |
| 记忆系统独立于流程 | Memory 未集成 | Memory 作为可插拔后端 |

---

## 三、融合方案

### 3.1 架构升级：从消息队列到 Session Graph

**当前：消息队列模式**
```
Agent A → inbox → Agent B → outbox → Agent C
         ↑ 每条消息独立，无血缘关系
```

**升级后：Session Graph 模式**
```
Session_001 → fork → Session_001_A (Agent A 处理)
            → fork → Session_001_B (Agent B 处理)
            → merge → Session_001_AB (合并结果)
            → Session_001_C (Agent C 接力)
            ↑ 完整血缘，可回溯、可复现
```

### 3.2 核心改造

#### 3.2.1 Session 数据结构

```json
{
  "session_id": "session_001",
  "parent_id": null,
  "status": "active",
  "created_at": "2026-06-30T16:00:00",
  "updated_at": "2026-06-30T16:30:00",
  
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "type": "message",
      "from_node": "xiaochen",
      "to_node": "hermes",
      "content": "Day 5 训练完成",
      "timestamp": "2026-06-30T16:00:00",
      "sandbox": "local",
      "memory_refs": ["mem_001"]
    },
    {
      "chunk_id": "chunk_002",
      "type": "tool_call",
      "tool": "training_evaluator",
      "input": {"student": "xiaochen", "day": 5},
      "output": {"accuracy": 0.85, "rating": "A"},
      "timestamp": "2026-06-30T16:15:00",
      "sandbox": "opensandbox",
      "memory_refs": ["mem_002"]
    }
  ],
  
  "graph": {
    "forks": [],
    "merges": [],
    "branches": ["session_001_a", "session_001_b"]
  },
  
  "metadata": {
    "workflow": "go_training_day5",
    "agents": ["xiaochen", "hermes", "qoder"],
    "tools": ["training_evaluator", "ability_profiler"],
    "memory_backend": "local",
    "sandbox_backend": "opensandbox"
  }
}
```

#### 3.2.2 Agent 变换层

```python
class TrainingAgent:
    """围棋训练 Agent（OpenRath 模式）"""
    
    def forward(self, session: Session) -> Session:
        """训练处理：读取 Session → 执行训练 → 写回 Session"""
        # 1. 从 Session 读取训练任务
        task = session.get_chunk("training_task")
        
        # 2. 执行训练
        result = self.execute_training(task)
        
        # 3. 写回 Session
        session.add_chunk({
            "type": "training_result",
            "content": result,
            "timestamp": datetime.now().isoformat()
        })
        
        # 4. 更新记忆
        self.memory.commit(result)
        
        return session
```

#### 3.2.3 Sandbox 绑定

```python
# 当前：工具执行位置可能漂移
def execute_tool(tool_name, params):
    # 可能在本地、可能在远程、可能在容器
    result = subprocess.run([tool_name, params])
    return result

# 升级后：Sandbox 绑定 Session
def execute_tool(tool_name, params, session: Session):
    # 工具在 Session 指定的 Sandbox 执行
    sandbox = session.get_sandbox()
    result = sandbox.execute(tool_name, params)
    
    # Session 记住执行位置
    session.set_metadata("last_sandbox", sandbox.id)
    return result
```

#### 3.2.4 Memory 集成

```python
class MemoryBackend:
    """记忆后端（可插拔）"""
    
    def recall(self, query: str) -> List[Dict]:
        """训练前召回相关记忆"""
        if self.backend == "local":
            return self.bm25_search(query)
        elif self.backend == "vector":
            return self.vector_search(query)
        elif self.backend == "openviking":
            return self.openviking_search(query)
    
    def commit(self, data: Dict):
        """训练后提交记忆"""
        if self.backend == "local":
            self.local_store(data)
        elif self.backend == "vector":
            self.vector_store(data)
        elif self.backend == "openviking":
            self.openviking_store(data)
```

---

## 四、实施计划

### Phase 1：Session 基础（1 周）
- [ ] 创建 Session 数据结构
- [ ] 实现 Session fork/merge/detach
- [ ] 改造消息队列为 Session 模式
- [ ] 测试 Session 血缘追踪

### Phase 2：Sandbox 集成（1 周）
- [ ] 实现 Sandbox 绑定 Session
- [ ] 支持 local/opensandbox 后端
- [ ] 工具执行位置追踪
- [ ] 测试 Sandbox 切换

### Phase 3：Memory 集成（1 周）
- [ ] 实现 Memory 可插拔后端
- [ ] 支持 local/vector/openviking
- [ ] 训练前 recall/训练后 commit
- [ ] 测试 Memory 检索

### Phase 4：Session Graph（2 周）
- [ ] 实现动态路由（Selector）
- [ ] 实现 Session 序列化/反序列化
- [ ] 实现 Session 可观测层
- [ ] 测试完整工作流

---

## 五、预期收益

| 指标 | 当前 | 升级后 | 提升 |
|------|------|--------|------|
| 消息可追溯性 | 低 | 高 | +100% |
| 训练可复现性 | 中 | 高 | +50% |
| 节点状态一致性 | 中 | 高 | +50% |
| 工具执行可靠性 | 中 | 高 | +50% |
| 记忆系统效率 | 中 | 高 | +50% |

---

## 六、与现有架构兼容

### 6.1 渐进式升级

```
阶段 1: 消息队列 + Session 并行
阶段 2: 逐步迁移到 Session 模式
阶段 3: 完全切换到 Session Graph
```

### 6.2 向后兼容

- 现有 CC 协议消息 → 自动转换为 Session chunk
- 现有训练数据 → 自动导入 Session Graph
- 现有记忆系统 → 作为 Memory 后端之一

---

## 七、技术风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Session 数据膨胀 | 存储压力 | 定期压缩、分层存储 |
| Session Graph 复杂度 | 性能下降 | 图数据库优化、缓存 |
| Sandbox 切换延迟 | 执行效率 | 预分配、连接池 |
| Memory 检索延迟 | 响应时间 | 向量索引、异步检索 |

---

## 八、总结

OpenRath 的核心价值：**把 Session 当成一等公民，而非 Agent 的附属品。**

小龙虾网络融合 OpenRath 后：
- ✅ 消息有血缘，可追溯
- ✅ 训练可复现，可回溯
- ✅ 节点状态一致，不漂移
- ✅ 工具执行可靠，不丢失
- ✅ 记忆系统集成，不孤立

**Agent 是工人，Session 才是工作本身。** 🦞
