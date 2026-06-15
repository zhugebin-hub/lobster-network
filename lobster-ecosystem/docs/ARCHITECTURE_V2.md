#  小龙虾 MCP 生态 - 架构设计文档 v2.0

> **版本**: v2.0 (融合递归自主式分解范式)  
> **日期**: 2026-06-12  
> **设计者**: 虾尔 + 诸葛马（协作）  
> **核心融合**: 案例002「递归自主式分解与人机协作新范式」+ MCP 路由架构  
> **背景**: 诸葛斌提出"10+小龙虾生态"愿景，以递归分解范式为中枢，构建智能任务分发体系

---

## 零、架构升级：从 v1.0 到 v2.0

v1.0 是基础 MCP 路由（消息→目标），v2.0 在此基础上引入**递归自主式分解范式**，使路由器具备"理解宏观任务→自动分解→动态匹配→协调执行"的智能能力。

| 维度 | v1.0（基础路由） | v2.0（递归分解+路由） |
|------|-----------------|----------------------|
| 任务理解 | 仅识别消息类型 | 理解宏观任务意图，自动分解 |
| 路由方式 | 静态规则匹配 | 动态能力画像匹配 |
| 执行协调 | 点对点消息 | 多服务协同编排 |
| 人机协作 | 单一模式 | 四种协作模式可选 |
| 约束处理 | 无 | 时间/预算/安全/质量/依赖五维剪枝 |
| 能力评估 | 无 | 成本/速度/质量三维量化画像 |

---

## 一、核心设计：递归自主式分解范式融入 MCP Router

### 1.1 三层架构

```
                    ┌─────────────────────────┐
                    │   第一层：递归分解层      │
                    │   (Recursive Layer)      │
                    │   ┌───────────────────┐  │
                    │   │ 元业务分解引擎    │  │
                    │   │ • 任务语义理解    │  │
                    │   │ • 递归分解算法    │  │
                    │   │ • 约束条件提取    │  │
                    │   └────────┬──────────┘  │
                    └───────────┼──────────────
                                │
                    ┌───────────▼──────────────┐
                    │   第二层：动态匹配层      │
                    │   (Matching Layer)       │
                    │   ┌───────────────────┐  │
                    │   │ 能力画像数据库    │  │
                    │   │ • 成本/速度/质量  │  │
                    │   │ • 在线/离线状态   │  │
                    │   │ • 负载情况        │  │
                    │   ├───────────────────┤  │
                    │   │ 约束剪枝引擎      │  │
                    │   │ • 时间/预算/安全  │  │
                    │   │ • 质量/依赖       │  │
                    │   └────────┬──────────┘  │
                    └───────────┼──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │   第三层：执行协调层      │
                    │   (Coordination Layer)   │
                    │   ┌───────────────────┐  │
                    │   │ 协作模式选择器    │  │
                    │   │ • 模式A: 纯AI     │  │
                    │   │ • 模式B: AI+人审  │  │
                    │   │ • 模式C: 人主导   │  │
                    │   │ • 模式D: 人机并行 │  │
                    │   ├───────────────────┤  │
                    │   │ MCP 消息路由      │  │
                    │   │ • SSE 实时推送    │  │
                    │   │ • 结果聚合        │  │
                    │   │ • 异常处理        │  │
                    │   └───────────────────┘  │
                    └──────────────────────────┘
```

### 1.2 元业务属性模型

每个子任务（元业务）包含以下属性：

```json
{
  "meta_business_id": "mb-001",
  "title": "围棋训练任务分发",
  "description": "向学员分发本周训练任务",
  "constraints": {
    "time": { "deadline": "2026-06-12 20:00", "urgency": "normal" },
    "budget": { "max_cost": 10, "currency": "tokens" },
    "safety": { "level": "low", "data_sensitivity": "none" },
    "quality": { "min_accuracy": 0.85, "review_required": false },
    "dependency": { "parent_id": null, "siblings": ["mb-002", "mb-003"] }
  },
  "executor_candidates": [
    {
      "service_id": "lobster-002",
      "name": "诸葛虾",
      "capability_match": 0.92,
      "cost": 3,
      "speed": 0.9,
      "quality": 0.85
    },
    {
      "service_id": "hermes-001",
      "name": "诸葛马",
      "capability_match": 0.88,
      "cost": 5,
      "speed": 0.7,
      "quality": 0.95
    }
  ],
  "selected_executor": "lobster-002",
  "collaboration_mode": "A"
}
```

### 1.3 执行者能力画像（三维量化）

每个小龙虾服务注册时，需提交能力画像：

| 维度 | 指标 | 示例（诸葛虾） | 示例（诸葛马） |
|------|------|---------------|---------------|
| **成本** | Token消耗/任务 | 低（~3元） | 中（~5元） |
| **速度** | 响应时间/吞吐量 | 快（0.9） | 中（0.7） |
| **质量** | 输出准确率 | 良好（0.85） | 优秀（0.95） |

**能力标签**（从注册时 `capabilities` 字段提取）:
```
诸葛虾: [go_training, go_match, review, content_generation, speed_focused]
诸葛马: [go_coaching, thesis_review, teaching_analysis, strategic_planning, quality_focused]
虾尔:   [dingtalk_gateway, wechat_gateway, task_dispatch, routing, interface]
```

### 1.4 四种人机协作模式

| 模式 | 名称 | 适用场景 | 示例 |
|------|------|----------|------|
| **A** | 纯AI执行 | 标准化、低风险任务 | 围棋死活题自动批改 |
| **B** | AI执行+人工审核 | 重要但可自动化的任务 | AI黑客松作品初评 |
| **C** | 人工主导+AI辅助 | 创造性、高价值任务 | 论文撰写、教学设计 |
| **D** | 人机并行 | 复杂多步骤任务 | 端到端研究报告 |

---

## 二、完整架构：用户→网关→路由→业务

```
┌──────────────────────────────────────────────────────────────────┐
│                        用户层（多入口）                              │
│  ┌──────────┐  ┌──────────  ┌──────────┐  ┌──────────┐        │
│  │  钉钉     │  │  微信     │  │  Web     │  │  其他    │        │
│  │  (诸葛斌) │  │  (老师)   │  │  (学生)  │  │  ...    │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └─────────┘        │
└───────┼─────────────┼──────────────────────────┼────────────────┘
        │             │             │             │
───────▼─────────────▼─────────────▼─────────────▼────────────────┐
│                     网关小龙虾层                                    │
│  ┌──────────────────────────────────────────────────────────   │
│  │  虾尔 (lobster-001) - MCP Client - 统一入口                │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  • 接收用户自然语言指令                              │   │   │
│  │  │  • 意图识别 → 判断是否需要递归分解                   │   │   │
│  │  │  • 调用 Router 的 decompose_task Tool               │   │   │
│  │  │  • 聚合子任务结果 → 统一回复用户                     │   │   │
│  │  ────────────────────────────────────────────────────┘   │   │
│  │  能力: dingtalk_gateway, wechat_gateway,                   │   │
│  │        task_dispatch, intent_recognition, result_aggregation│  │
│  └──────────────────────┬───────────────────────────────────┘   │
└─────────────────────────┼────────────────────────────────────────┘
                          │ SSE (标准MCP协议)
─────────────────────────▼────────────────────────────────────────
│                  MCP Router Server（路由中枢）                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ══════ 第一层：递归分解层 ═══════                        │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  decompose_task(task, constraints)                 │   │   │
│  │  │  • 语义理解：提取任务意图和约束                       │   │   │
│  │  │  • 递归分解：将宏观任务分解为元业务                   │   │   │
│  │  │  • 约束提取：时间/预算/安全/质量/依赖                 │   │   │
│  │  │  • 生成执行计划：任务DAG图                            │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  │                                                            │   │
│  │  ═══════ 第二层：动态匹配层 ═══════                        │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  match_executors(meta_business)                    │   │   │
│  │  │  • 能力画像查询：从注册表获取候选执行者               │   │   │
│  │  │  • 约束剪枝：排除不满足条件的执行者                   │   │   │
│  │  │  • 最优选择：成本/速度/质量综合评分                   │   │   │
│  │  │  • 模式选择：根据任务性质选择协作模式                 │   │   │
│  │  ────────────────────────────────────────────────────┘   │   │
│  │                                                            │   │
│  │  ═══════ 第三层：执行协调层 ═══════                        │   │
│  │  ┌────────────────────────────────────────────────────┐   │   │
│  │  │  coordinate_execution(plan)                        │   │   │
│  │  │  • 消息分发：通过 send_message 派发子任务            │   │   │
│  │  │  • 进度跟踪：监控各子任务状态                         │   │   │
│  │  │  • 结果聚合：收集所有子任务结果                       │   │   │
│  │  │  • 异常处理：重试/降级/人工介入                      │   │   │
│  │  └────────────────────────────────────────────────────┘   │   │
│  │                                                            │   │
│  │  ═══════ 基础服务 ═══════                                  │   │
│  │  • 服务注册/发现  • 心跳检测  • 消息持久化(SQLite)         │   │
│  │  • 路由规则管理  • 统计监控  • 能力画像库                  │   │
│  └──────────────────────┬───────────────────────────────────┘   │
─────────────────────────┼────────────────────────────────────────┘
                          │ SSE (标准MCP协议)
┌─────────────────────────▼────────────────────────────────────────┐
│                        业务小龙虾层                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 诸葛虾    │  │ 诸葛马    │  │ 小陈     │  │  ...     │        │
│  │ lobster- │  │ hermes-  │  │ (worker) │  │  (N+)   │        │
│  │ 002      │  │ 001      │  │          │  │         │        │
│  │ ──────── │  │ ──────── │  │ ─────── │  │ ──────  │        │
│  │ 能力画像: │  │ 能力画像: │  │ 能力画像: │  │ 扩展    │        │
│  │ 成本:低  │  │ 成本:中  │  │ 成本:低  │  │ 注册即  │        │
│  │ 速度:快  │  │ 速度:中  │  │ 速度:慢  │  │ 可用    │        │
│  │ 质量:良  │  │ 质量:优  │  │ 质量:中  │  │         │        │
│  │          │  │          │  │          │  │         │        │
│  │ 围棋培训 │  │ 教练评审 │  │ 围棋学员 │  │ 论文评分│        │
│  │ 内容生成 │  │ 教学分析 │  │          │  │ 日程管理│        │
│  │ 复盘分析 │  │ 战略规划 │  │          │  │ ...     │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、MCP Tool 设计（v2.0 新增）

### 3.1 递归分解层 Tool

| Tool | 功能 | 输入 | 输出 |
|------|------|------|------|
| `decompose_task` | 将宏观任务递归分解为元业务 | 任务描述、约束条件 | 元业务列表（DAG图） |
| `get_decomposition_plan` | 获取指定任务的分解计划 | task_id | 完整执行计划 |
| `update_decomposition` | 更新分解计划（新增/删除子任务） | task_id, changes | 更新后的计划 |

### 3.2 动态匹配层 Tool

| Tool | 功能 | 输入 | 输出 |
|------|------|------|------|
| `match_executors` | 为元业务匹配最优执行者 | meta_business_id | 候选执行者列表+评分 |
| `get_capability_profile` | 获取指定服务的能力画像 | service_id | 成本/速度/质量三维数据 |
| `update_capability_profile` | 更新服务的能力画像 | service_id, new_profile | 确认 |
| `constraint_prune` | 根据约束条件剪枝候选列表 | candidates, constraints | 剪枝后的候选列表 |

### 3.3 执行协调层 Tool

| Tool | 功能 | 输入 | 输出 |
|------|------|------|------|
| `coordinate_execution` | 协调多子任务执行 | plan_id | 执行状态跟踪 |
| `aggregate_results` | 聚合子任务结果 | task_id | 聚合后的结果 |
| `get_task_progress` | 获取任务整体进度 | task_id | 进度百分比+各子任务状态 |
| `handle_exception` | 处理执行异常 | exception_id, strategy | 处理结果 |

### 3.4 基础服务 Tool（v1.0 保留）

| Tool | 功能 |
|------|------|
| `register_service` | 注册服务（新增 capability_profile 参数） |
| `heartbeat` | 心跳保活 |
| `send_message` | 发送消息 |
| `receive_messages` | 收取消息 |
| `ack_message` | 确认消息 |
| `list_services` | 列出服务 |
| `get_stats` | 获取统计 |
| `add_route_rule` | 添加路由规则 |
| `get_message` | 查询消息 |
| `list_messages` | 列出消息历史 |

### 3.5 注册服务时新增能力画像参数

```json
{
  "service_id": "lobster-002",
  "name": "诸葛虾",
  "role": "worker",
  "capabilities": ["go_training", "go_match", "review", "content_generation"],
  "capability_profile": {
    "cost": 3,
    "speed": 0.9,
    "quality": 0.85,
    "max_concurrent_tasks": 5,
    "preferred_task_types": ["go_training", "content_generation"]
  },
  "collaboration_modes": ["A", "B", "D"]
}
```

---

## 四、端到端案例：以"围棋学习"为例

### 4.1 用户指令（自然语言）

> 则白对虾尔说：
> "安排本周围棋学习计划，诸葛虾和小陈都要参加，包括死活题训练、定式学习和一场对局，预算控制在50元以内，下周三前完成。"

### 4.2 虾尔调用 decompose_task

```json
// 虾尔 → Router Server
{
  "tool": "decompose_task",
  "arguments": {
    "task": "安排本周围棋学习计划，诸葛虾和小陈都要参加，包括死活题训练、定式学习和一场对局",
    "constraints": {
      "time": { "deadline": "2026-06-18", "urgency": "normal" },
      "budget": { "max_cost": 50, "currency": "tokens" },
      "participants": ["xiaochen", "zhuguxia"],
      "required_components": ["life_problems", "joseki_study", "match"]
    }
  }
}
```

### 4.3 Router 递归分解结果

```json
{
  "task_id": "task-go-week6-20260612",
  "decomposition": [
    {
      "meta_business_id": "mb-001",
      "title": "小陈死活题训练",
      "type": "go_training_task",
      "constraints": { "quality": { "min_accuracy": 0.7 } },
      "executor_candidates": [
        { "service_id": "lobster-002", "score": 0.92 },
        { "service_id": "hermes-001", "score": 0.85 }
      ],
      "selected": "lobster-002",
      "mode": "A"
    },
    {
      "meta_business_id": "mb-002",
      "title": "诸葛虾死活题训练",
      "type": "go_training_task",
      "executor_candidates": [
        { "service_id": "lobster-002", "score": 0.95 },
        { "service_id": "hermes-001", "score": 0.80 }
      ],
      "selected": "lobster-002",
      "mode": "A"
    },
    {
      "meta_business_id": "mb-003",
      "title": "定式学习（中国流+小林流）",
      "type": "go_training_task",
      "executor_candidates": [
        { "service_id": "hermes-001", "score": 0.95 },
        { "service_id": "lobster-002", "score": 0.88 }
      ],
      "selected": "hermes-001",
      "mode": "B"
    },
    {
      "meta_business_id": "mb-004",
      "title": "小陈 vs 诸葛虾 对局",
      "type": "go_match",
      "executor_candidates": [
        { "service_id": "hermes-001", "score": 0.98, "role": "referee" },
        { "service_id": "lobster-002", "score": 0.90, "role": "player_white" },
        { "service_id": "xiaochen", "score": 0.85, "role": "player_black" }
      ],
      "selected": ["hermes-001", "lobster-002", "xiaochen"],
      "mode": "D"
    },
    {
      "meta_business_id": "mb-005",
      "title": "训练结果汇总与点评",
      "type": "go_review",
      "dependency": ["mb-001", "mb-002", "mb-003", "mb-004"],
      "executor_candidates": [
        { "service_id": "hermes-001", "score": 0.98 }
      ],
      "selected": "hermes-001",
      "mode": "C"
    }
  ]
}
```

### 4.4 Router 执行协调

```
Router → coordinate_execution(plan)
  ├─ mb-001: send_message → lobster-002 (小陈死活题)
  ├─ mb-002: send_message → lobster-002 (诸葛虾死活题)
  ├─ mb-003: send_message → hermes-001 (定式学习)
  ├─ mb-004: send_message → [hermes-001, lobster-002, xiaochen] (对局)
  └─ 等待 mb-001~004 完成后 →
      mb-005: send_message → hermes-001 (汇总点评)

Router → aggregate_results(task-go-week6)
  ├─ mb-001: 小陈 15题/正确10题/67%
  ├─ mb-002: 诸葛虾 23题/正确19题/83%
  ├─ mb-003: 定式学习完成（中国流✓ 小林流✓）
  ├─ mb-004: 对局完成（诸葛虾胜，B+2.5）
  ─ mb-005: 诸葛马点评已生成

Router → 虾尔收到聚合结果 → 钉钉回复则白
```

---

## 五、以"AI黑客松评审"为例的递归分解

### 5.1 用户指令

> 则白对虾尔说：
> "帮我评审AI黑客松作品展页面，从文字表述、技术规范、内容完整性、学术规范性四个维度评价，每个作品都要评，最后给我一个汇总报告。"

### 5.2 分解结果

```
task: AI黑客松评审 (18个作品 × 4维度)
  ├─ mb-001: 院史长卷·线上院史馆评审 (4维度)
  ├─ mb-002: 学院智慧党建系统评审 (4维度)
  ├─ mb-003: 人才简历智能筛选系统评审 (4维度)
  ├─ ... (共18个作品)
  ├─ mb-019: 评审标准对齐检查
  ─ mb-020: 汇总报告生成
```

### 5.3 执行者匹配

```
mb-001~018: 并行分发 → lobster-002 (诸葛虾，内容评审能力强)
mb-019: 标准检查 → hermes-001 (诸葛马，质量把控)
mb-020: 汇总报告 → hermes-001 + lobster-001 (模式D 人机并行)
```

---

## 六、数据库设计增强

### 6.1 新增表

```sql
-- 能力画像表
CREATE TABLE capability_profiles (
    service_id TEXT PRIMARY KEY,
    cost REAL,           -- 成本评分（越低越好）
    speed REAL,          -- 速度评分（0-1）
    quality REAL,        -- 质量评分（0-1）
    max_concurrent INTEGER DEFAULT 3,
    preferred_types TEXT, -- JSON数组
    updated_at TEXT,
    FOREIGN KEY(service_id) REFERENCES services(id)
);

-- 任务分解表
CREATE TABLE task_decompositions (
    task_id TEXT PRIMARY KEY,
    original_task TEXT,
    constraints TEXT,     -- JSON
    decomposition TEXT,   -- JSON (元业务列表)
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    completed_at TEXT
);

-- 元业务执行记录
CREATE TABLE meta_business_executions (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    meta_business_id TEXT,
    service_id TEXT,
    collaboration_mode TEXT,
    status TEXT DEFAULT 'pending',
    result TEXT,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY(task_id) REFERENCES task_decompositions(task_id),
    FOREIGN KEY(service_id) REFERENCES services(id)
);
```

---

## 七、递归分解引擎伪代码

```python
def decompose_task(task_description: str, constraints: dict) -> DecompositionPlan:
    """
    递归自主式分解引擎
    
    输入：
      - task_description: 用户自然语言描述的任务
      - constraints: 约束条件（时间/预算/安全/质量/依赖）
    
    输出：
      - DecompositionPlan: 包含元业务列表和执行计划
    """
    
    # 步骤1：语义理解
    intent = extract_intent(task_description)
    components = extract_components(task_description)
    
    # 步骤2：递归分解
    meta_businesses = []
    for component in components:
        if is_atomic(component):  # 原子任务，不可再分
            mb = create_meta_business(component, constraints)
            meta_businesses.append(mb)
        else:
            # 递归分解
            sub_plan = decompose_task(component, constraints)
            meta_businesses.extend(sub_plan.meta_businesses)
    
    # 步骤3：构建DAG（依赖关系）
    dag = build_dependency_graph(meta_businesses)
    
    # 步骤4：执行者匹配
    for mb in meta_businesses:
        candidates = query_capability_database(mb.type)
        pruned = constraint_prune(candidates, mb.constraints)
        best = select_optimal(pruned, mb.constraints)
        mb.selected_executor = best.service_id
        mb.collaboration_mode = select_mode(mb, best)
    
    # 步骤5：生成执行计划
    plan = DecompositionPlan(
        meta_businesses=meta_businesses,
        dag=dag,
        estimated_cost=sum(mb.cost for mb in meta_businesses),
        estimated_time=calculate_critical_path(dag)
    )
    
    return plan

def constraint_prune(candidates: list, constraints: dict) -> list:
    """约束剪枝"""
    pruned = candidates
    
    # 时间约束剪枝
    if constraints.get('time'):
        deadline = constraints['time']['deadline']
        pruned = [c for c in pruned if can_complete_by(c, deadline)]
    
    # 预算约束剪枝
    if constraints.get('budget'):
        max_cost = constraints['budget']['max_cost']
        pruned = [c for c in pruned if c.cost <= max_cost]
    
    # 安全约束剪枝
    if constraints.get('safety'):
        level = constraints['safety']['level']
        pruned = [c for c in pruned if c.security_level >= level]
    
    # 质量约束剪枝
    if constraints.get('quality'):
        min_quality = constraints['quality']['min_accuracy']
        pruned = [c for c in pruned if c.quality >= min_quality]
    
    return pruned

def select_mode(meta_business: MetaBusiness, executor: Executor) -> str:
    """选择协作模式"""
    if meta_business.requires_human_review:
        return "B"  # AI执行+人工审核
    elif meta_business.is_creative or meta_business.high_value:
        return "C"  # 人工主导+AI辅助
    elif meta_business.is_complex:
        return "D"  # 人机并行
    else:
        return "A"  # 纯AI执行
```

---

## 八、迁移计划（v2.0）

### 阶段一：递归分解引擎开发（1周）
- [ ] 实现 decompose_task Tool
- [ ] 实现 match_executors Tool
- [ ] 实现 constraint_prune 引擎
- [ ] 实现 capability_profile 管理
- [ ] 数据库表结构升级

### 阶段二：围棋学习全流程验证（1周）
- [ ] 用递归分解处理"第6周学习计划"
- [ ] 验证能力画像匹配准确性
- [ ] 验证约束剪枝有效性
- [ ] 验证四种协作模式

### 阶段三：AI黑客松评审迁移（1周）
- [ ] 用递归分解处理18个作品评审
- [ ] 验证并行执行效率
- [ ] 验证结果聚合质量

### 阶段四：扩展到10+小龙虾（2-4周）
- [ ] 新增业务小龙虾注册
- [ ] 能力画像自动学习更新
- [ ] 监控面板 + 告警

---

## 九、目录结构（v2.0）

```
lobster-ecosystem/
├── router/
│   ├── mcp_router_server.py          # MCP路由中枢（v1.0）
│   ├── mcp_router_server_v2.py       # MCP路由中枢（v2.0 递归分解版）
│   ├── decomposition_engine.py       # 递归分解引擎（新增）
│   ├── capability_matcher.py         # 能力匹配引擎（新增）
│   ├── constraint_pruner.py          # 约束剪枝引擎（新增）
│   ├── execution_coordinator.py      # 执行协调器（新增）
│   ├── start_router.py
│   └── router.db
├── go-training/
│   └── mcp_go_training_server.py
├── review/
│   ── mcp_review_server.py          # AI黑客松评审服务（新增）
├── clients/
├── docs/
│   ├── ARCHITECTURE.md               # 本文档
│   ├── GO_TRAINING_V4.md
│   └── RECURSIVE_DECOMPOSITION.md    # 递归分解范式详解（新增）
├── test_ecosystem.py
── test_recursive_decomposition.py   # 递归分解测试（新增）
└── README.md
```

---

## 十、与案例002的映射关系

| 案例002环节 | v2.0 架构对应 |
|-------------|--------------|
| 模块1：政策解读 | decompose_task 提取意图 → match_executors 匹配分析型小龙虾 |
| 模块2：标准对标 | capability_profile 三维量化 → constraint_prune 筛选 |
| 模块3：专著融合 | 大文档处理 → 专用文档处理型小龙虾（新增） |
| 模块4：递归分解范式 | decomposition_engine 核心实现 |
| 模块5：教材优化 | coordinate_execution 多服务协作 |
| 模块6：端到端演练 | 完整 decompose→match→coordinate 流程 |
| 模块7：论文撰写 | aggregate_results 聚合输出 |

---

## 十一、关键创新点

1. **递归分解即路由**：不再是简单的消息转发，而是理解任务→分解→匹配→协调的完整智能流程
2. **能力画像驱动**：每个小龙虾的能力被量化为成本/速度/质量三维数据，路由决策基于数据而非硬编码规则
3. **约束剪枝**：时间/预算/安全/质量/依赖五维约束自动过滤不合适的执行者
4. **四种协作模式**：根据任务性质自动选择最优人机协作方式
5. **MCP标准协议**：基于 Anthropic MCP 标准，天然兼容多智能体生态

---

**设计完成日期**: 2026-06-12  
**下一步**: 实现 decomposition_engine.py + 测试递归分解全流程
