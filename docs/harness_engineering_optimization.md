# 🦞 小龙虾网络 × Harness Engineering 优化方案

> 版本：v1.0  
> 作者：信电大虾  
> 日期：2026-06-30  
> 状态：架构优化

---

## 一、Harness Engineering 核心原则

### 1.1 基本公式

```
Agent = Model + Harness
```

**模型负责推理，Harness 负责剩下的所有事情**：
- 工具系统
- 上下文管理
- 权限控制
- 反馈回路
- 记忆与协作

### 1.2 四条铁律

| 铁律 | 本能反应 | Harness 真相 | 启示 |
|------|----------|--------------|------|
| 一 | 信息越多决策越准 | 上下文越少越好 | 像 Code Review 一样精挑细选上下文 |
| 二 | 一个超级 Agent 全包 | 专才 Agent 永远赢过通才 | Agent 昂贵，Skill 廉价 |
| 三 | 让 Agent "记住"任务进展 | 状态要写文件，不要塞上下文 | Workspace 是真相，Context 只是工位 |
| 四 | 把规则写进 AGENTS.md | 能写成 Linter 的约束，别停留在文档 | 机器可执行的约束比文档可靠十倍 |

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

| 痛点 | 违反的铁律 | Harness 解法 |
|------|------------|--------------|
| 消息散落在 inbox/outbox | 铁律三：状态未写文件 | Workspace 作为真相之源 |
| 训练数据难以复现 | 铁律三：状态未持久化 | 文件化状态管理 |
| 节点状态不一致 | 铁律三：Context 替代 Workspace | 统一 Workspace 结构 |
| 工具执行位置漂移 | 铁律四：缺乏 Linter 约束 | 工具签名 + 事务边界 |
| 记忆系统独立于流程 | 铁律一：上下文污染 | 结构化上下文管理 |

---

## 三、优化方案：四条铁律落地

### 3.1 铁律一：上下文越少越好

**当前问题：**
- 消息队列中堆积大量未处理消息
- 训练任务包含过多无关信息
- Agent 处理时上下文污染

**优化方案：**

```python
# 优化前：所有消息一起处理
def process_all_messages(agent, messages):
    context = "\n".join([m.content for m in messages])
    return agent.process(context)

# 优化后：结构化上下文，只给必要信息
def process_message(agent, message, context_schema):
    # 1. 只加载当前任务相关的上下文
    relevant_context = filter_context(message, context_schema)
    
    # 2. 分段化上下文
    structured_context = {
        "system_constraint": context_schema.system,
        "task_definition": message.task,
        "current_state": message.state,
        "tool_signatures": message.tools,
        "history_summary": message.history[:3]  # 只保留最近 3 条
    }
    
    return agent.process(structured_context)
```

**实施步骤：**
1. 定义上下文 Schema（任务类型、阶段、当前焦点）
2. 实现上下文过滤器（只加载相关部分）
3. 实现上下文分段化（系统约束/任务定义/当前状态/工具签名/历史摘要）
4. 实现上下文可回放（每次构造可重放、可 diff）

### 3.2 铁律二：专才 Agent 永远赢过通才 Agent

**当前问题：**
- Agent 职责不清晰
- 工具列表过长，Agent "逛超市"
- 通才 Agent 性能不稳定

**优化方案：**

```
当前架构：
├── 通才 Agent (10+ 工具)
└── 所有任务都由此 Agent 处理

优化架构：
├── Orchestrator Agent (悟空)
│   ├── 职责：拆任务、分发、维护 Workspace
│   ├── 工具：3 个 (dispatch, monitor, archive)
│   └── Prompt: 100 行
│
├── Training Agent (训练专才)
│   ├── 职责：围棋训练调度、评估
│   ├── 工具：4 个 (schedule, evaluate, promote, profile)
│   └── Prompt: 80 行
│
├── Communication Agent (通信专才)
│   ├── 职责：消息路由、ACK 确认
│   ├── 工具：3 个 (route, ack, notify)
│   └── Prompt: 90 行
│
└── N 个原子化 Skill
    ├── parse_training_data
    ├── evaluate_performance
    ├── generate_report
    └── ...
```

**实施步骤：**
1. 识别当前通才 Agent 的职责
2. 拆分为 2-3 个专才 Agent
3. 每个 Agent 只装载必要工具（≤5 个）
4. 剩余功能下沉为 Skill（函数 + 明确签名）
5. Agent 数量不超过 3 个

### 3.3 铁律三：状态要写文件，不要塞上下文

**当前问题：**
- 状态分散在消息队列中
- 跨会话无法延续
- 难以审计和回放

**优化方案：**

```
当前 Workspace 结构：
.shared/
├── messages/
│   ├── queue/
│   └── from-*/
├── profiles/
└── training/

优化后 Workspace 结构：
.shared/
├── workspace/                    # 真相之源
│   ├── agents/                   # Agent 状态
│   │   ├── orchestrator/
│   │   │   ├── state.json        # 当前状态
│   │   │   ├── tasks/            # 任务列表
│   │   │   └── history/          # 操作历史
│   │   ├── training/
│   │   │   ├── state.json
│   │   │   ├── schedule.json
│   │   │   └── evaluations/
│   │   └── communication/
│   │       ├── state.json
│   │       ├── routes.json
│   │       └── ack_log.json
│   │
│   ├── tasks/                    # 任务状态
│   │   ├── {task_id}/
│   │   │   ├── plan.md           # 任务计划
│   │   │   ├── state.json        # 任务状态
│   │   │   ├── progress.json     # 进度追踪
│   │   │   └── result.json       # 执行结果
│   │
│   ├── context/                  # 上下文管理
│   │   ├── schema.json           # 上下文 Schema
│   │   ├── filters/              # 上下文过滤器
│   │   └── cache/                # 上下文缓存
│   │
│   └── locks/                    # 事务锁
│       ├── rpa_lock/             # RPA 事务锁
│       ├── training_lock/        # 训练事务锁
│       └── communication_lock/   # 通信事务锁
```

**实施步骤：**
1. 创建统一 Workspace 结构
2. 实现状态文件化（state.json, progress.json, result.json）
3. 实现事务锁机制（lock 文件 + 断点续传）
4. 实现上下文可回放（每次构造可 diff）
5. 实现操作可审计（history 目录）

### 3.4 铁律四：能写成 Linter 的约束，别写成文档

**当前问题：**
- 规则写在 AGENTS.md 中
- Agent 可能"创造性解读"
- 缺乏强制约束

**优化方案：**

```python
# 优化前：文档约束
# AGENTS.md:
# - 训练任务必须在 24 小时内完成
# - 消息必须在 4 小时内回复
# - 工具调用不能超过 5 个

# 优化后：Linter 约束
class TrainingLinter:
    """训练任务 Linter"""
    
    def check_timeout(self, task: Dict) -> bool:
        """检查任务是否超时"""
        created = datetime.fromisoformat(task['created_at'])
        timeout = timedelta(hours=24)
        
        if datetime.now() - created > timeout:
            raise TaskTimeoutError(f"任务 {task['id']} 已超时")
        return True
    
    def check_tool_calls(self, task: Dict) -> bool:
        """检查工具调用次数"""
        tool_calls = len(task.get('tool_calls', []))
        if tool_calls > 5:
            raise ToolLimitError(f"工具调用超过限制：{tool_calls}")
        return True

class CommunicationLinter:
    """通信 Linter"""
    
    def check_ack_timeout(self, message: Dict) -> bool:
        """检查 ACK 超时"""
        sent = datetime.fromisoformat(message['sent_at'])
        timeout = timedelta(hours=4)
        
        if datetime.now() - sent > timeout and not message.get('acked'):
            raise AckTimeoutError(f"消息 {message['id']} ACK 超时")
        return True
    
    def check_external_message(self, message: Dict) -> bool:
        """检查外发消息合规性"""
        # 第 1 层：白名单工具检查
        if message['tool'] not in ALLOWED_TOOLS:
            raise UnauthorizedToolError(f"工具 {message['tool']} 未授权")
        
        # 第 2 层：敏感词检查
        if contains_sensitive_words(message['content']):
            raise SensitiveContentError("包含敏感词")
        
        # 第 3 层：合规检查
        if not compliance_check(message['content']):
            raise ComplianceError("不合规")
        
        return True
```

**实施步骤：**
1. 识别 AGENTS.md 中的规则
2. 将规则编码为 Linter 检查
3. 实现工具调用限制（≤5 个）
4. 实现超时检查（训练 24h，通信 4h）
5. 实现外发消息三层护栏（白名单 + 敏感词 + 合规）

---

## 四、六大工程模式落地

### 4.1 模式 1：双阶段架构（Initializer + Executor）

```python
class TrainingWorkflow:
    """围棋训练工作流（双阶段）"""
    
    def run(self, task: Dict) -> Dict:
        # 阶段 1: Initializer - 制定计划
        initializer = InitializerAgent()
        plan = initializer.create_plan(task)
        
        # 写入 plan.md
        with open(f"workspace/tasks/{task['id']}/plan.md", 'w') as f:
            f.write(plan)
        
        # 阶段 2: Executor - 按步执行
        executor = ExecutorAgent()
        result = executor.execute_plan(plan)
        
        # 写入 result.json
        with open(f"workspace/tasks/{task['id']}/result.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
```

### 4.2 模式 2：工具签名即文档

```python
# 优化前：工具签名不清晰
def process_task(task):
    # 参数不明确，返回值不固定
    pass

# 优化后：工具签名即文档
def schedule_training(
    student_id: str,        # 学员 ID (xiaochen/zhuguxia/qoder)
    day: int,               # 训练天数 (1-35)
    problem_count: int,     # 题目数量 (10-200)
    game_count: int         # 对局数量 (1-20)
) -> Dict:
    """
    调度训练任务
    
    返回:
    {
        "task_id": str,
        "status": "scheduled",
        "scheduled_at": str,
        "estimated_completion": str
    }
    """
    pass
```

### 4.3 模式 3：Sub-Agent 隔离

```python
class TrainingSubAgent:
    """训练 Sub-Agent（隔离上下文）"""
    
    def __init__(self):
        self.context_window = ContextWindow()  # 独立上下文
        self.tools = [                         # 只装载必要工具
            schedule_training,
            evaluate_performance,
            update_profile
        ]
    
    def process(self, task: Dict) -> Dict:
        # 只接收结构化输出
        result = self.context_window.process(task)
        return {
            "status": result.status,
            "accuracy": result.accuracy,
            "rating": result.rating
        }
```

### 4.4 模式 4：上下游反压

```python
class TrainingPipeline:
    """训练流水线（反压机制）"""
    
    def run(self, task: Dict) -> Dict:
        # 上游：确定性设置
        context = self.prepare_context(task)
        
        # Agent 执行
        result = self.agent.execute(context)
        
        # 下游：验证
        if not self.validate(result):
            # 错误信号回传上游
            error_info = self.generate_error_feedback(result)
            return self.retry_with_feedback(task, error_info)
        
        return result
    
    def validate(self, result: Dict) -> bool:
        """验证结果有效性"""
        # Linter 检查
        if result['accuracy'] < 0.5:
            return False
        if result['tool_calls'] > 5:
            return False
        return True
```

### 4.5 模式 5：智能体审智能体

```python
class ReviewWorkflow:
    """Agent 审 Agent 工作流"""
    
    def review(self, task: Dict, result: Dict) -> Dict:
        # Reviewer Sub-Agent（独立 Context）
        reviewer = ReviewAgent()
        reviewer.context = {
            "git_diff": result['diff'],
            "rules": load_rules("docs/rules/*.md"),
            "role": "Senior Reviewer (怀疑态度)"
        }
        
        # 执行审查
        review_result = reviewer.review(result)
        
        return {
            "approved": review_result.approved,
            "comments": review_result.comments,
            "suggestions": review_result.suggestions
        }
```

### 4.6 模式 6：熵管理与文档园丁

```python
class DocumentGardener:
    """文档园丁 Agent"""
    
    def run(self):
        """定期扫描文档健康度"""
        # 1. 扫描过期文档
        expired = self.scan_expired_docs()
        
        # 2. 检测架构漂移
        drift = self.detect_architecture_drift()
        
        # 3. 提交清理 PR
        if expired or drift:
            self.create_cleanup_pr(expired, drift)
    
    def scan_expired_docs(self) -> List[str]:
        """扫描过期文档"""
        expired = []
        for doc in self.workspace_docs:
            if doc.last_modified < datetime.now() - timedelta(days=30):
                expired.append(doc.path)
        return expired
    
    def detect_architecture_drift(self) -> Dict:
        """检测架构漂移"""
        # 比较实际架构与设计文档
        actual = self.scan_actual_architecture()
        designed = self.load_design_docs()
        
        return self.compare(actual, designed)
```

---

## 五、实施计划

### Phase 1：Workspace 重构（1 周）
- [ ] 创建统一 Workspace 结构
- [ ] 实现状态文件化
- [ ] 实现事务锁机制
- [ ] 测试状态持久化

### Phase 2：Agent 拆分（1 周）
- [ ] 识别通才 Agent 职责
- [ ] 拆分为 2-3 个专才 Agent
- [ ] 工具下沉为 Skill
- [ ] 测试专才 Agent 性能

### Phase 3：Linter 约束（1 周）
- [ ] 识别 AGENTS.md 规则
- [ ] 编码为 Linter 检查
- [ ] 实现三层护栏
- [ ] 测试约束有效性

### Phase 4：工程模式（2 周）
- [ ] 实现双阶段架构
- [ ] 实现工具签名文档
- [ ] 实现 Sub-Agent 隔离
- [ ] 实现反压机制
- [ ] 实现 Agent 审查
- [ ] 实现文档园丁

---

## 六、预期收益

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| 上下文污染率 | 高 | 低 | -70% |
| Agent 任务成功率 | 60% | 85% | +42% |
| 状态可追溯性 | 低 | 高 | +100% |
| 工具调用准确率 | 70% | 90% | +29% |
| 外发消息事故率 | 每周 1-2 次 | 每月<1 次 | -90% |

---

## 七、总结

**Harness Engineering 核心：**
- 你优化的不是 Agent，是 Agent 的工作环境
- 上下文是稀缺资源，不是无限仓库
- 状态写在文件里，不在脑子里
- 能写成 Linter 的约束，别写成文档
- Agent 昂贵，Skill 廉价，护栏最便宜
- 对外说话和动用户数据要有硬护栏

**小龙虾网络融合 Harness Engineering 后：**
- ✅ 上下文精简，污染率 -70%
- ✅ 专才 Agent，任务成功率 +42%
- ✅ Workspace 状态化，可追溯 +100%
- ✅ Linter 约束，工具准确率 +29%
- ✅ 三层护栏，外发消息事故 -90%

**Agent = Model + Harness** 🦞
