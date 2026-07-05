# 🦞 小龙虾网络 OpenRath 架构升级方案

> 生成时间：2026-06-30 10:00 UTC+8
> 设计人：诸葛马 (Hermes)
> 基于：清华大学/中山大学/HKU OpenRath v1.2.1

---

## 一、问题诊断：为什么需要 OpenRath？

### 1.1 当前架构痛点

| 痛点 | 描述 | 影响 |
|------|------|------|
| Session混乱 | 文件散落在from-hermes/results/acks/，无统一追踪 | 无法回溯工作流 |
| Agent膨胀 | 单个Agent承担规划/执行/审查多角色 | Prompt过大，上下文混乱 |
| 无血缘追溯 | 无法知道结论来自哪个Agent/哪次工具调用 | 调试困难 |
| 无动态路由 | 流程写死，无法根据中间结果改变走向 | 灵活性差 |
| 记忆散落 | 各Agent各自维护记忆，无法共享 | 知识无法复用 |
| 执行位置漂移 | 对话历史和执行位置分开管理 | 工具调用位置不确定 |

### 1.2 OpenRath 核心主张

> **"Agent是工人，Session才是工作本身"**

| PyTorch概念 | OpenRath映射 | 小龙虾网络映射 |
|-------------|-------------|----------------|
| Tensor（数据） | Session | 学员训练Session |
| Module/Linear（变换层） | Agent/Workflow | Planner/Researcher/Executor/Reviewer/Memory |
| Device（执行位置） | Sandbox/Backend | 本地/SSH/容器 |
| Parameter（参数） | Memory | 长期记忆/知识 |
| Function（函数） | Tool | 训练工具/评估工具 |
| 控制流 | Selector | 动态路由器 |

---

## 二、架构设计

### 2.1 Session-centric 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Session Graph（动态图）                    │
│  ┌──────────┐    fork    ┌──────────┐    merge   ┌────────┐ │
│  │ Session A├───────────→│ Session B├───────────→│Session │ │
│  │ (小陈)   │            │ (小陈-重试)│          │ (合并) │ │
│  └──────────┘            └──────────┘            └────────┘ │
│       │ detach                                              │
│       ↓                                                     │
│  ┌──────────┐                                               │
│  │ Session C│ (独立演化)                                     │
│  └──────────┘                                               │
└─────────────────────────────────────────────────────────────┘
         │
         ↓ forward(session) → session
┌─────────────────────────────────────────────────────────────┐
│                    Agent Cluster（变换层）                    │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐      │
│  │ Planner │→│Researcher│→│Executor │→│Reviewer │      │
│  │ (规划)  │  │ (研究)   │  │ (执行)  │  │ (审查)  │      │
│  └─────────┘  └──────────┘  └─────────┘  └─────────┘      │
│                                    │                        │
│                              fork/ retry                   │
│                                    ↓                        │
│  ┌─────────┐  ┌──────────┐                               │
│  │ Memory  │←│Executor  │                               │
│  │ (记忆)  │  │ (重试)   │                               │
│  └─────────┘  └──────────┘                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Session 数据结构

```python
Session {
    session_id: "session-abc123"
    student_id: "xiaochen"
    task_type: "go_training"
    status: "active"
    chunks: [
        SessionChunk {
            chunk_id: "chunk-001"
            chunk_type: "message"
            agent_id: "hermes"
            content: {"task": "Day5训练"}
            timestamp: "2026-06-30 10:00:00"
            sandbox_backend: "local"
        }
        SessionChunk {
            chunk_id: "chunk-002"
            chunk_type: "tool_call"
            agent_id: "planner"
            content: {"tool": "select_problems", "args": {"count": 50}}
            timestamp: "2026-06-30 10:00:05"
            sandbox_backend: "local"
        }
        SessionChunk {
            chunk_id: "chunk-003"
            chunk_type: "tool_result"
            agent_id: "executor"
            content: {"result": "50题已选择", "accuracy": 0.82}
            timestamp: "2026-06-30 10:05:00"
            sandbox_backend: "local"
        }
        SessionChunk {
            chunk_id: "chunk-004"
            chunk_type: "state_change"
            agent_id: "reviewer"
            content: {"review": "通过", "feedback": "良好"}
            timestamp: "2026-06-30 10:05:30"
            sandbox_backend: "local"
        }
        SessionChunk {
            chunk_id: "chunk-005"
            chunk_type: "memory"
            agent_id: "memory"
            content: {"insights": [...], "memory_refs": ["mem-001"]}
            timestamp: "2026-06-30 10:05:35"
            sandbox_backend: "local"
        }
    ]
    parent_session_id: null
    branch_id: null
    sandbox_backend: "local"
    memory_refs: ["mem-001"]
    metadata: {"plan": {...}, "execution": {...}, "review": {...}}
}
```

### 2.3 Agent Cluster 设计

| Agent | 职责 | 输入 | 输出 | 变换 |
|-------|------|------|------|------|
| **Planner** | 分析任务，制定计划 | Session | Session+plan | 理解→策略→步骤 |
| **Researcher** | 检索知识库 | Session+plan | Session+research | 检索→过滤→排序 |
| **Executor** | 执行任务 | Session+research | Session+execution | 执行→验证→记录 |
| **Reviewer** | 审查结果 | Session+execution | Session+review | 评估→反馈→决策 |
| **Memory** | 管理记忆 | Session | Session+memory | 提取→存储→索引 |

**核心接口：**
```python
class BaseAgent:
    def forward(self, session: Session) -> Session:
        """吃进Session，吐出Session"""
        raise NotImplementedError
```

### 2.4 Session Graph 操作

| 操作 | 描述 | 场景 |
|------|------|------|
| **fork** | 分叉Session，创建独立分支 | 审查不通过，重试 |
| **merge** | 合并两个Session | 多条路径结果汇总 |
| **detach** | 切断血缘关系 | 独立任务，不需要追溯 |
| **lineage** | 获取血缘链 | 调试：这个结论怎么来的？ |
| **branches** | 获取所有分叉 | 审计：有哪些并行路径？ |

### 2.5 Selector 动态路由

```python
# 动态路由：根据Session状态选择下一个Workflow
selector = Selector()
while not isinstance(nxt := selector.forward(session, 
    training_workflow,
    assessment_workflow,
    prompt_workflow,
    general_workflow), EmptyWorkflow):
    session = nxt(session)
```

**路由策略：**
- 训练任务 → training_workflow
- 评估任务 → assessment_workflow
- 提示词任务 → prompt_workflow
- 其他任务 → general_workflow

### 2.6 Memory Backend

| 后端类型 | 存储方式 | 检索方式 | 适用场景 |
|----------|----------|----------|----------|
| **LocalMemory** | JSON文件 | BM25词法检索 | 无LLM依赖，快速 |
| **VectorMemory** | 向量数据库 | 语义相似度 | 需要语义理解 |
| **ExternalMemory** | OpenViking等 | API调用 | 已有记忆系统 |

### 2.7 Sandbox Backend

| 后端类型 | 执行位置 | 适用场景 |
|----------|----------|----------|
| **LocalSandbox** | 本地进程 | 快速测试 |
| **SSHSandbox** | 远程服务器 | 跨服务器执行 |
| **ContainerSandbox** | Docker容器 | 隔离执行 |

---

## 三、实施计划

### 3.1 阶段1：核心模块（已完成）

- [x] Session 数据结构
- [x] Agent 基类（forward接口）
- [x] Agent Cluster（5个Agent）
- [x] Workflow（可组合）
- [x] Session Graph（fork/merge/detach）
- [x] Selector（动态路由）
- [x] Memory Backend（BM25）
- [x] Sandbox Backend（本地）
- [x] LobsterNetworkRuntime（集成入口）

### 3.2 阶段2：集成现有系统（下一步）

- [ ] 将现有训练任务迁移到Session
- [ ] 将sync_reminder集成到Executor
- [ ] 将e2e_validation集成到Reviewer
- [ ] 将time_protection集成到Selector
- [ ] 将dynamic_profile集成到Memory

### 3.3 阶段3：增强功能（未来）

- [ ] 向量记忆后端（语义检索）
- [ ] SSH沙箱后端（远程执行）
- [ ] LLM驱动的Selector（模型路由）
- [ ] Session可视化（血缘图）
- [ ] 多学员并行Session

---

## 四、对比：改造前 vs 改造后

| 维度 | 改造前 | 改造后 |
|------|--------|--------|
| 数据载体 | 文件散落 | Session统一 |
| Agent角色 | 全能助手 | 变换层 |
| 状态管理 | 各自维护 | Session Graph |
| 血缘追溯 | 无 | 完整证据链 |
| 动态路由 | 写死流程 | Selector驱动 |
| 记忆系统 | 散落各Agent | 统一Memory Backend |
| 执行位置 | 不确定 | Sandbox绑定 |
| 调试能力 | 困难 | Session报告 |
| 可扩展性 | 低 | 高（组合Agent） |

---

## 五、使用方式

```bash
# 运行任务
python3 core/openrath_runtime.py run --student xiaochen --task go_training

# 查看Session报告（证据链）
python3 core/openrath_runtime.py report --session-id <id>

# 查看Session Graph
python3 core/openrath_runtime.py graph
```

---

## 六、预期收益

| 收益 | 描述 |
|------|------|
| 可观测性 | 每个结论都有完整证据链 |
| 可调试性 | 可以回溯到任意Agent/工具调用 |
| 可组合性 | Agent如积木一样自由组合 |
| 可扩展性 | 新增Agent只需实现forward接口 |
| 可复用性 | Session可以fork/merge/复用 |
| 动态性 | Selector根据运行时状态路由 |

---

*方案由诸葛马 (Hermes) 自动生成 | 基于OpenRath v1.2.1架构理念*
