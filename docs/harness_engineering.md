# Harness Engineering — 小龙虾网络驾驭工程

> **Agent = Model + Harness**
> 
> 模型负责推理，Harness 负责"剩下的所有事情"。
> 
> —— LangChain 官方 + Mitchell Hashimoto

## 理论来源

基于阿里云开发者《[给野马套上缰绳：Agent Harness 工程实践](https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw)》，
融合 Mitchell Hashimoto、Anthropic、LangChain 的工程实践经验。

## 三代范式演进

| 代际 | 范式 | 核心问题 | 龙虾网络对应 |
|:---|:---|:---|:---|
| 第一代 | **Prompt Engineering** | 怎么把话说清楚 | `dialogue.py` — 对话引擎 |
| 第二代 | **Context Engineering** | 怎么给AI喂对信息 | `context_engineering.py` — 结构化上下文 |
| 第三代 | **Harness Engineering** | 怎么让Agent可控地工作 | **本模块 (v0.8.0 新增)** |

## 四条反直觉铁律

| # | 铁律 | 本能反应 | Harness 真相 | 落地模块 |
|:---|:---|:---|:---|:---|
| 1 | **上下文越少越好** | 信息越多决策越准 | 稀缺资源要精挑 | `ContextBuilder` |
| 2 | **专才 > 通才** | 一个超级Agent全包 | 2-3个Agent + 无限Skill | `SubAgentIsolationPattern` |
| 3 | **状态写文件** | 让Agent"记住" | Workspace 是 Agent 的 Git 仓库 | `Workspace` |
| 4 | **约束可执行** | 把规则写进文档 | 能写成 Linter 的，别停留在文档 | `ConstraintEngine` |

## 模块架构

```
harness/
├── __init__.py                   # 模块入口，四根护栏
├── context_engineering.py        # 上下文工程 — 结构化/分段化/可回放/可审计
├── architecture_constraints.py   # 架构约束 — Linter 级可执行规则
├── feedback_loop.py              # 反馈回路 — Agent审Agent + 失败分析
├── entropy_manager.py            # 熵管理 — 文档园丁 + 漂移检测
├── workspace.py                  # 工作空间 — Agent 的持久化状态基座
├── dual_stage.py                 # 双阶段架构 — Init + Exec 不共享Context
└── patterns.py                   # 六大工程模式 — 可组合原语
```

## 核心组件

### 1. ContextBuilder（上下文工程）
```python
from lobster_network.harness import ContextBuilder

builder = ContextBuilder(task_id="task-001", max_total_tokens=4000)
builder.add_slot("system", ROLE_PROMPT, priority=1, source="orchestrator")
builder.add_slot("task", "处理对局结果", priority=2)
builder.add_slot("state", workspace.get_state(), priority=3, max_tokens=500)
builder.add_slot("tools", tool_signatures, priority=4)
builder.add_slot("history", summary_only, priority=10, max_tokens=300)

context = builder.build()  # 自动排序、截断、裁剪
snapshot = builder.snapshot()  # 可回放、可 diff
```

### 2. ConstraintEngine（架构约束）
```python
from lobster_network.harness import ConstraintEngine, LinterConstraint

engine = ConstraintEngine()

# 每条约束对应一个真实失败案例
engine.register(LinterConstraint(
    id="no-bare-except",
    description="禁止使用裸 except:",
    failure_case="2026-06: sync_manager.py 裸 except 捕获 KeyboardInterrupt",
    check_pattern=r"^\s*except\s*:",
    severity=Severity.ERROR,
))

violations = engine.check_file("sync_manager.py")
if engine.has_fatal(violations):
    print("阻断: 发现致命违规")
```

### 3. FeedbackLoop（反馈回路）
```python
from lobster_network.harness import FeedbackLoop, AgentReviewer

reviewer = AgentReviewer("senior-reviewer")
reviewer.add_rule("输出必须是完整可执行的结果")
reviewer.add_rule("不能有未解决的外部依赖")

result = reviewer.review_diff(original_code, modified_code)
# → ReviewResult: APPROVE / REVISE / REJECT
```

### 4. Workspace（工作空间）
```python
from lobster_network.harness import Workspace, RpaLock

ws = Workspace("zhugebin-001")
ws.save_state({"mode": "training", "current_task": "go-match"})
ws.save_plan("deploy-v4", plan_content)
ws.checkpoint("before-deploy")  # 断点续传
```

### 5. DualStageExecutor（双阶段架构）
```python
from lobster_network.harness import DualStageExecutor, Workspace

ws = Workspace("zhugebin-001")
executor = DualStageExecutor("deploy-v4", ws)

def my_executor(task_id, step_id, workspace):
    # Exec Stage: 从 workspace 读取 plan.md，不共享 Init 的 Context
    return f"执行 {step_id} 完成"

executor.init("推送到服务器 47.93.6.57")  # Init Stage
executor.set_executor(my_executor)
results = executor.run()  # Exec Stage
```

## 六大工程模式

| 模式 | 解决问题 | 龙虾网络对应 |
|:---|:---|:---|
| 1. 双阶段架构 | 跨会话延续 | `DualStagePattern` / `DualStageExecutor` |
| 2. 工具签名即文档 | Agent选错工具 | `ToolSignaturePattern` |
| 3. Sub-Agent隔离 | 上下文污染 | `SubAgentIsolationPattern` |
| 4. 上下游反压 | 无限循环 | `BackpressurePattern` |
| 5. 智能体审智能体 | 自我偏差 | `AgentReviewPattern` + CC Protocol ACK |
| 6. 熵管理与文档园丁 | 代码腐化 | `EntropyManagementPattern` / `DocGardener` |

## 与龙虾网络现有架构的融合

| 现有组件 | Harness 增强 |
|:---|:---|
| `sync_manager.py` | → `ConstraintEngine` 检查 "禁止裸 except" |
| `messenger.py` / CC Protocol | → `AgentReviewPattern` 审查消息内容 |
| `registry/` 节点状态 | → `Workspace` 持久化状态文件 |
| `scripts/cc_escalate_expired.py` | → `FeedbackLoop` 失败分析 → 自动生成约束 |
| 学习模块 trainers/ | → `SubAgentIsolationPattern` 每个学员独立 Context |
| Go 训练系统 | → `DualStageExecutor` Init(分析棋局) + Exec(下棋) |

## 龙王铁律（速记）

| # | 心法 | 一句话 |
|:---|:---|:---|
| 1 | 你优化的不是 Agent，是 Agent 的**工作环境** | 把它当员工，不是工具 |
| 2 | 上下文是**稀缺资源**，不是无限仓库 | 少即是多 |
| 3 | **状态写在文件里**，不在脑子里 | Workspace = Agent 的 Git |
| 4 | 能写成 **Linter** 的约束，别写成文档 | 机器强制 > 人力记忆 |
| 5 | Agent 是**昂贵**的，Skill 是**廉价**的，护栏是**最便宜**的 | 能用 Skill 别加 Agent |
| 6 | 对外说话和动用户数据的地方，**硬护栏要早一步** | Prompt 可以漏，合规底线不能 |

---

*版本: v0.8.0 | 集成时间: 2026-06-30 | 理论来源: 阿里云开发者 Harness Engineering 实践*
