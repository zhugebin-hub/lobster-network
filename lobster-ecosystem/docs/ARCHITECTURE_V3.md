#  小龙虾 MCP 生态 - 完整架构方案 v3.0

> **版本**: v3.0（递归自主式分解 + MCP 路由）  
> **日期**: 2026-06-12  
> **设计者**: 虾尔（牵头）+ 诸葛马（协作）  
> **核心融合**: 案例002「递归自主式分解与人机协作新范式」+ MCP 路由中枢  
> **愿景**: 10+小龙虾协作生态，参考"2虾一马"通信模式扩展

---

## 零、设计原则

1. **用户无感知**：用户只与入口小龙虾交互（钉钉/微信），不感知后端路由和分解
2. **能力自注册**：业务小龙虾启动时自动向 Router 注册能力画像
3. **递归分解驱动路由**：Router 不是简单转发，而是理解任务→分解→匹配→协调
4. **MCP 标准协议**：基于 Anthropic MCP 标准，天然兼容多智能体生态
5. **渐进式迁移**：保留 NFS 为备份，MCP 为主通道，双轨并行逐步切换

---

## 一、整体架构图

```
──────────────────────────────────────────────────────────────────┐
│                      用户层（多入口，统一体验）                       │
│                                                                  │
│   ┌─────────┐  ─────────┐  ┌─────────┐  ┌─────────┐          │
│   │  钉钉    │  │  微信    │  │  Web    │  │  其他   │          │
│   │  (诸葛斌)│  │  (老师)  │  │  (学生)  │  │  ...   │          │
│   └────┬────┘  └────┬────┘  └────┬────┘  └─────────┘          │
│        │             │             │                              │
└────────┼─────────────┼─────────────┼──────────────────────────────┘
         │             │             │
─────────▼─────────────▼─────────────▼──────────────────────────────
│                     网关小龙虾层（统一入口）                           │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────   │
│   │  虾尔 (lobster-001) - 唯一对外入口                          │   │
│   │  ┌───────────────────────────────────────────────────   │   │
│   │  │  职责：                                              │   │
│   │  │  1. 接收用户自然语言指令（钉钉/微信/Web）               │   │
│   │  │  2. 意图识别 → 判断任务类型和复杂度                    │   │
│   │  │  3. 调用 Router.decompose_task 进行递归分解           │   │
│   │  │  4. 调用 Router.coordinate_execution 执行任务        │   │
│   │  │  5. 聚合子任务结果 → 统一回复用户                     │   │
│   │  ──────────────────────────────────────────────────   │   │
│   │  能力画像:                                              │   │
│   │    成本=2 | 速度=0.95 | 质量=0.80 | 并发=10            │   │
│   │  能力标签: [gateway, routing, aggregation, dispatch]   │   │
│   │  协作模式: 支持 A/B/D                                   │   │
│   └──────────────────────┬───────────────────────────────   │   │
└─────────────────────────┼──────────────────────────────────────┘
                          │
                    ┌─────▼──────┐
                    │   MCP      │
                    │  Router    │
                    │  Server    │
                    │ (路由中枢)  │
                    └─────┬──────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌─────▼─────┐     ┌────▼────┐
   │ 诸葛虾   │      │  诸葛马    │     │  小陈   │
   │ lobster │      │ hermes   │     │ student │
   │ -002    │      │ -001     │     │         │
   └─────────┘      └──────────┘     └─────────┘
    围棋培训          教练评审          围棋学员
    内容生成          教学分析
    复盘分析          战略规划
```

---

## 二、核心流程：从用户指令到任务完成

### 2.1 完整任务流

```
用户（自然语言）
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤1：用户提交任务                                     │
│ "安排本周围棋学习计划，诸葛虾和小陈都要参加..."             │
│ 入口：钉钉 → 虾尔                                       │
└─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤2：虾尔意图识别                                     │
│ - 识别任务类型：围棋学习计划                              │
│ - 识别参与者：诸葛虾、小陈                                │
│ - 识别组件：死活题训练、定式学习、对局                     │
│ - 识别约束：预算50以内                                    │
└─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤3：虾尔调用 Router.decompose_task                  │
│ Router 执行递归自主式分解：                               │
│ - 第一层：理解宏观任务意图                                │
│ - 第二层：递归分解为元业务（原子任务）                      │
│ - 第三层：提取约束条件（时间/预算/质量）                   │
│ - 输出：10个元业务 + DAG依赖图 + 预估成本/时间             │
─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤4：Router 能力匹配（动态匹配层）                       │
│ 对每个元业务：                                            │
│ - 查询能力画像数据库                                      │
│ - 约束剪枝（排除不满足条件的执行者）                        │
│ - 综合评分（质量40% + 速度30% + 成本20% + 匹配10%）       │
│ - 选择最优执行者                                          │
│ - 确定协作模式（A/B/C/D）                                │
└─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤5：Router 执行协调                                   │
│ 按 DAG 顺序执行：                                        │
│ - 无依赖任务并行执行                                      │
│ - 有依赖任务串行执行                                      │
│ - 通过 send_message 派发给对应小龙虾                     │
│ - 实时跟踪各子任务状态                                    │
└─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤6：业务小龙虾执行任务                                 │
│ 各小龙虾通过 MCP Go Training / MCP Review 等服务         │
│ 执行具体任务，完成后 ack_message                          │
└─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤7：Router 聚合结果                                   │
│ - 收集所有子任务结果                                      │
│ - 按依赖关系组装最终结果                                  │
│ - 生成汇总报告（如有）                                    │
─────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────┐
│ 步骤8：虾尔回复用户                                       │
│ 通过钉钉发送统一回复：                                     │
│ "本周围棋学习计划已安排：诸葛虾完成死活题23题(83%)..."     │
└─────────────────────────────────────────────────────┘
```

---

## 三、递归自主式分解引擎

### 3.1 三层架构

```
                    ┌─────────────────────────────────┐
                    │  第一层：递归分解层                 │
                    │  (Recursive Decomposition Layer)  │
                    │  ┌─────────────────────────────┐ │
                    │  │ • 任务语义理解                │ │
                    │  │ • 参与者提取                  │ │
                    │  │ • 任务组件识别                │ │
                    │  │ • 递归分解（最大深度5）         │ │
                    │  │ • 约束条件提取                │ │
                    │  └─────────────────────────────┘ │
                    └───────────────┬─────────────────┘
                                    │ 元业务列表 + DAG
                    ───────────────▼─────────────────┐
                    │  第二层：动态匹配层                 │
                    │  (Dynamic Matching Layer)         │
                    │  ┌─────────────────────────────┐ │
                    │  │ • 能力画像查询                │ │
                    │  │ • 约束剪枝                    │ │
                    │  │   - 时间/预算/安全/质量/依赖  │ │
                    │  │ • 最优执行者选择              │ │
                    │  │ • 协作模式选择 (A/B/C/D)      │ │
                    │  └─────────────────────────────┘ │
                    └───────────────┬─────────────────┘
                                    │ 执行计划
                    ┌───────────────▼─────────────────┐
                    │  第三层：执行协调层                 │
                    │  (Execution Coordination Layer)   │
                    │  ┌─────────────────────────────┐ │
                    │  │ • MCP 消息分发                │ │
                    │  │ • 进度跟踪                    │ │
                    │  │ • 结果聚合                    │ │
                    │  │ • 异常处理 (重试/降级)         │ │
                    │  └─────────────────────────────┘ │
                    ─────────────────────────────────┘
```

### 3.2 元业务属性模型

```json
{
  "meta_business_id": "mb-001",
  "title": "诸葛虾死活题训练",
  "description": "为诸葛虾执行死活题训练任务",
  "task_type": "go_training_task",
  "constraints": {
    "time": { "deadline": "2026-06-18", "urgency": "normal" },
    "budget": { "max_cost": 50, "currency": "tokens" },
    "quality": { "min_accuracy": 0.7 },
    "dependencies": []
  },
  "executor_candidates": [
    {
      "service_id": "lobster-002",
      "name": "诸葛虾",
      "capability_match": 0.92,
      "cost": 3,
      "speed": 0.9,
      "quality": 0.85,
      "score": 0.73
    },
    {
      "service_id": "xiaochen",
      "name": "小陈",
      "capability_match": 0.70,
      "cost": 1,
      "speed": 0.6,
      "quality": 0.70,
      "score": 0.63
    }
  ],
  "selected_executor": "lobster-002",
  "collaboration_mode": "A",
  "dependency_ids": [],
  "estimated_cost": 3.0,
  "estimated_time": 15.0,
  "status": "pending"
}
```

### 3.3 四种人机协作模式

| 模式 | 图标 | 名称 | 适用场景 | 示例 |
|------|------|------|----------|------|
| **A** |  | 纯AI执行 | 标准化、低风险任务 | 围棋死活题自动批改、日程管理 |
| **B** | 🤖👤 | AI执行+人工审核 | 重要但可自动化的任务 | AI黑客松作品初评、教学分析 |
| **C** | 👤🤖 | 人工主导+AI辅助 | 创造性、高价值任务 | 论文撰写、教学设计、战略规划 |
| **D** | 👥🤖 | 人机并行 | 复杂多步骤任务 | 围棋对局（多方参与）、端到端研究报告 |

---

## 四、能力画像体系

### 4.1 三维量化模型

每个小龙虾服务注册时提交能力画像：

| 维度 | 说明 | 评分范围 | 优化方向 |
|------|------|----------|----------|
| **成本** | 完成任务的 Token 消耗 | 1-10（越低越好） | 降低 Token 用量 |
| **速度** | 响应速度和吞吐量 | 0-1（越高越快） | 提升响应效率 |
| **质量** | 输出准确率和完成度 | 0-1（越高越好） | 提升输出质量 |

### 4.2 能力标签

从注册时 `capabilities` 字段提取，用于模糊匹配：

```
虾尔 (lobster-001):
  [dingtalk_gateway, wechat_gateway, task_dispatch, routing, aggregation]
  
诸葛虾 (lobster-002):
  [go_training, go_match, review, content_generation, speed_focused]
  
诸葛马 (hermes-001):
  [go_coaching, thesis_review, teaching_analysis, strategic_planning, quality_focused]
  
小陈 (xiaochen):
  [go_training, go_match, student]
```

### 4.3 综合评分公式

```
综合评分 = 质量 × 40% + 速度 × 30% + (1/成本) × 20% + 能力匹配度 × 10%
```

### 4.4 能力画像自动学习

每次任务完成后，Router 根据实际结果更新执行者画像：
- 实际成本 vs 预估成本 → 更新成本评分
- 实际用时 vs 预估用时 → 更新速度评分
- 用户满意度/审核通过率 → 更新质量评分

---

## 五、约束剪枝引擎

五维约束自动过滤不合适的执行者：

| 约束维度 | 剪枝规则 | 示例 |
|----------|----------|------|
| **时间** | 排除无法在截止时间前完成的执行者 | deadline=2026-06-18 → 排除速度慢的 |
| **预算** | 排除成本超过预算的执行者 | max_cost=50 → 排除成本>50的 |
| **安全** | 高安全级别排除低成本执行者 | safety=high → 排除成本<3的 |
| **质量** | 排除质量低于最低要求的执行者 | min_accuracy=0.85 → 排除质量<0.85的 |
| **依赖** | 确保依赖任务先执行 | mb-005 依赖 mb-001~004 → DAG排序 |

---

## 六、MCP Router Server Tool 设计

### 6.1 核心 Tool（15个）

#### 分解层 Tool
| Tool | 功能 | 调用方 |
|------|------|--------|
| `decompose_task` | 将宏观任务递归分解为元业务 | 虾尔 |
| `get_decomposition_plan` | 获取指定任务的分解计划 | 虾尔/管理员 |
| `update_decomposition` | 更新分解计划 | 虾尔 |

#### 匹配层 Tool
| Tool | 功能 | 调用方 |
|------|------|--------|
| `match_executors` | 为元业务匹配最优执行者 | Router 内部 |
| `get_capability_profile` | 获取指定服务的能力画像 | 管理员 |
| `update_capability_profile` | 更新服务的能力画像（自动学习） | Router 内部 |
| `constraint_prune` | 根据约束条件剪枝候选列表 | Router 内部 |

#### 协调层 Tool
| Tool | 功能 | 调用方 |
|------|------|--------|
| `coordinate_execution` | 协调多子任务执行 | 虾尔/Router |
| `aggregate_results` | 聚合子任务结果 | Router |
| `get_task_progress` | 获取任务整体进度 | 虾尔 |
| `handle_exception` | 处理执行异常 | Router |

#### 基础服务 Tool
| Tool | 功能 | 调用方 |
|------|------|--------|
| `register_service` | 注册服务（含能力画像） | 所有小龙虾 |
| `heartbeat` | 心跳保活 | 所有小龙虾 |
| `send_message` | 发送消息 | 所有小龙虾 |
| `receive_messages` | 收取待处理消息 | 所有小龙虾 |
| `ack_message` | 确认消息已处理 | 所有小龙虾 |
| `list_services` | 列出所有服务 | 管理员 |
| `get_stats` | 获取路由统计 | 管理员 |

### 6.2 注册服务参数

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
    "preferred_task_types": ["go_training", "go_match", "content_generation"]
  },
  "collaboration_modes": ["A", "B", "D"],
  "endpoint": "sse://lobster-002.local/mcp",
  "metadata": {
    "version": "v2.0",
    "owner": "诸葛斌",
    "tags": ["speed_focused", "go_expert"]
  }
}
```

---

## 七、端到端案例

### 7.1 案例1：围棋学习计划

**用户指令**（钉钉→虾尔）：
> "安排本周围棋学习计划，诸葛虾和小陈都要参加，包括死活题训练、定式学习和一场对局，预算控制在50以内，下周三前完成。"

**Router 分解结果**（10个元业务）：

```
task-id: task-go-week6-20260612
原始任务: 安排本周围棋学习计划...
预估总成本: 30 tokens
预估总时间: 15 分钟

执行序列:
  1. [🤖 A] 诸葛虾_死活题训练 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.73), 小陈(0.63)
     类型: go_training_task | 成本: 3 | 时间: 15min

  2. [🤖 A] 诸葛虾_定式学习 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.73), 诸葛马(0.68)
     类型: go_training_task | 成本: 3 | 时间: 15min

  3. [ A] 小陈_死活题训练 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.73), 小陈(0.63)
     类型: go_training_task | 成本: 3 | 时间: 15min

  4. [🤖 A] 小陈_定式学习 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.73), 小陈(0.63)
     类型: go_training_task | 成本: 3 | 时间: 15min

  5. [🤖 A] 创建对局 → lobster-002 (诸葛虾)
     类型: go_match_setup | 成本: 2 | 时间: 2min

  6. [🤖 A] 对局进行中 → lobster-002 (诸葛虾)
     类型: go_match_play | 成本: 5 | 时间: 25min

  7. [🤖 A] 对局结束 → lobster-002 (诸葛虾)
     类型: go_match_end | 成本: 2 | 时间: 3min

  8. [🤖 A] 训练结果汇总 → hermes-001 (诸葛马)
     类型: go_review | 成本: 5 | 时间: 20min
     依赖: [1,2,3,4,5,6,7]
```

**执行协调**：
```
Router 并行派发 mb-001~004（无依赖，4个训练任务）
Router 串行执行 mb-005→006→007（对局流程）
等待 mb-001~007 完成后 → 执行 mb-008（汇总点评）
```

**虾尔回复用户**：
> "🦞 本周围棋学习计划已安排：
> 
> 诸葛虾：
> - 死活题训练（预计15分钟）→ 诸葛虾执行
> - 定式学习（预计15分钟）→ 诸葛虾执行
> 
> 小陈：
> - 死活题训练（预计15分钟）→ 诸葛虾执行
> - 定式学习（预计15分钟）→ 诸葛虾执行
> 
> 对局安排：
> - 诸葛虾 vs 小陈（9路棋盘，预计30分钟）
> 
> 总预估：30 tokens / 15分钟
> 所有任务将在下周三前完成 ✅"

### 7.2 案例2：AI黑客松评审

**用户指令**（钉钉→虾尔）：
> "帮我评审AI黑客松作品展页面，从文字表述、技术规范、内容完整性、学术规范性四个维度评价，最后给我一个汇总报告。"

**Router 分解结果**（5个元业务）：

```
task-id: task-review-hackathon-20260612
原始任务: 帮我评审AI黑客松作品展页面...
预估总成本: 31 tokens
预估总时间: 20 分钟

执行序列:
  1. [👤 B] 评审标准对齐 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.70), 诸葛马(0.68)
     类型: review_setup | 成本: 2 | 时间: 5min

  2. [🤖👤 B] 逐项评审 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.70), 诸葛马(0.68)
     类型: review_execute | 成本: 6 | 时间: 20min

  3. [🤖👤 B] 评审汇总 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.70), 诸葛马(0.68)
     类型: review_summary | 成本: 3 | 时间: 10min

  4. [🤖👤 B] 内容生成 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.76)
     类型: content_generation | 成本: 15 | 时间: 45min

  5. [🤖👤 B] 训练结果汇总与点评 → lobster-002 (诸葛虾)
     候选: 诸葛虾(0.71), 诸葛马(0.69)
     类型: go_review | 成本: 5 | 时间: 20min
```

---

## 八、数据库设计

### 8.1 表结构

```sql
-- 服务注册表
CREATE TABLE services (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    capabilities TEXT,               -- JSON数组
    status TEXT DEFAULT 'offline',
    last_heartbeat TEXT,
    registered_at TEXT,
    endpoint TEXT,
    metadata TEXT,                   -- JSON
    collaboration_modes TEXT         -- JSON数组 ["A","B","D"]
);

-- 能力画像表
CREATE TABLE capability_profiles (
    service_id TEXT PRIMARY KEY,
    cost REAL,                       -- 成本评分（越低越好）
    speed REAL,                      -- 速度评分（0-1）
    quality REAL,                    -- 质量评分（0-1）
    max_concurrent INTEGER DEFAULT 3,
    preferred_types TEXT,            -- JSON数组
    load REAL DEFAULT 0.0,           -- 当前负载（0-1）
    total_tasks INTEGER DEFAULT 0,
    completed_tasks INTEGER DEFAULT 0,
    updated_at TEXT,
    FOREIGN KEY(service_id) REFERENCES services(id)
);

-- 消息队列表
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    from_service TEXT NOT NULL,
    to_service TEXT NOT NULL,
    type TEXT NOT NULL,
    priority TEXT DEFAULT 'normal',
    payload TEXT NOT NULL,           -- JSON
    status TEXT DEFAULT 'pending',
    created_at TEXT,
    delivered_at TEXT,
    ack_at TEXT,
    error TEXT,
    route_log TEXT                   -- JSON
);

-- 任务分解表
CREATE TABLE task_decompositions (
    task_id TEXT PRIMARY KEY,
    original_task TEXT,
    constraints TEXT,                -- JSON
    decomposition TEXT,              -- JSON (元业务列表)
    dag TEXT,                        -- JSON (DAG图)
    estimated_cost REAL,
    estimated_time REAL,
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
    result TEXT,                     -- JSON
    actual_cost REAL,
    actual_time REAL,
    started_at TEXT,
    completed_at TEXT,
    FOREIGN KEY(task_id) REFERENCES task_decompositions(task_id),
    FOREIGN KEY(service_id) REFERENCES services(id)
);

-- 路由规则表
CREATE TABLE route_rules (
    id TEXT PRIMARY KEY,
    pattern TEXT NOT NULL,
    target_service TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    active INTEGER DEFAULT 1,
    created_at TEXT
);

-- 心跳记录表
CREATE TABLE heartbeats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id TEXT NOT NULL,
    timestamp TEXT,
    FOREIGN KEY(service_id) REFERENCES services(id)
);
```

---

## 九、迁移计划

### 阶段一：MCP Router 核心开发（当前 ✅ 进行中）
- [x] MCP Router Server v1.0（基础路由）
- [x] MCP Go Training Server（围棋训练迁移）
- [x] 递归分解引擎 DecompositionEngine
- [x] 能力匹配器 CapabilityMatcher
- [x] 3个服务注册测试 + 端到端测试通过
- [ ] 诸葛虾、诸葛马实际接入

### 阶段二：递归分解全流程验证（1周）
- [ ] 围棋学习计划端到端验证（案例1）
- [ ] AI黑客松评审端到端验证（案例2）
- [ ] 能力画像自动学习机制
- [ ] 四种协作模式实际测试

### 阶段三：业务迁移（2周）
- [ ] MCP Review Server（AI黑客松评审迁移）
- [ ] MCP Teaching Server（教学分析迁移）
- [ ] 围棋学习全流程 MCP 化
- [ ] 心跳检测 + 离线重连 + 异常处理

### 阶段四：扩展到10+小龙虾（2-4周）
- [ ] 新增业务小龙虾注册（论文评分、日程管理等）
- [ ] 支持微信入口（新增 gateway 小龙虾）
- [ ] 消息持久化增强（Redis）
- [ ] 监控面板 + 告警系统

### 阶段五：稳定运行（持续）
- [ ] 关闭 NFS 写入，仅保留读取（备份）
- [ ] 性能优化（消息队列、缓存）
- [ ] 安全加固（鉴权、审计）

---

## 十、目录结构

```
lobster-ecosystem/
├── router/
│   ├── mcp_router_server.py          # MCP路由中枢 v1.0
│   ├── mcp_router_server_v3.py       # MCP路由中枢 v3.0（递归分解版）
│   ├── decomposition_engine.py       # 递归分解引擎 ✅
│   ├── capability_matcher.py         # 能力匹配引擎（集成在decomposition中）
│   ├── start_router.py               # 启动脚本
│   └── router.db                     # SQLite数据库
├── go-training/
│   └── mcp_go_training_server.py     # 围棋训练MCP服务 ✅
├── review/                           # 待开发
│   └── mcp_review_server.py          # AI黑客松评审服务
├── clients/                          # 各小龙虾Client配置
── docs/
│   ├── ARCHITECTURE.md               # v1.0架构文档
│   ├── ARCHITECTURE_V2.md            # v2.0架构文档
│   ├── ARCHITECTURE_V3.md            # 本文档（v3.0完整版）
│   ├── GO_TRAINING_V4.md             # v4.0学习方案
│   └── RECURSIVE_DECOMPOSITION.md    # 递归分解范式详解
├── test_ecosystem.py                 # 集成测试 ✅
├── test_recursive_decomposition.py   # 递归分解测试
└── README.md                         # 项目总览
```

---

## 十一、与 NFS 兼容策略

| 策略 | 说明 |
|------|------|
| **双写模式** | 关键消息同时写入 MCP 和 NFS，确保不丢失 |
| **NFS 轮询备份** | 保留原有轮询脚本作为备用通道 |
| **切换开关** | `use_mcp=true/false` 配置文件控制主通道 |
| **逐步关闭** | 稳定后逐步关闭 NFS 写入，仅保留读取归档 |

---

## 十二、关键创新点

1. **递归分解即路由**：Router 不是简单转发，而是理解任务→分解→匹配→协调的智能中枢
2. **能力画像驱动**：每个小龙虾的能力被量化为成本/速度/质量三维数据，路由决策基于数据而非硬编码
3. **约束剪枝**：时间/预算/安全/质量/依赖五维约束自动过滤不合适的执行者
4. **四种协作模式**：根据任务性质自动选择最优人机协作方式
5. **MCP 标准协议**：基于 Anthropic MCP 标准，天然兼容多智能体生态
6. **能力自动学习**：每次任务完成后自动更新执行者画像，越用越准

---

## 十三、与案例002的映射

| 案例002环节 | v3.0 架构对应 |
|-------------|--------------|
| 模块1：政策解读 | decompose_task 提取意图 → match_executors 匹配分析型小龙虾 |
| 模块2：标准对标 | capability_profile 三维量化 → constraint_prune 筛选 |
| 模块3：专著融合 | 大文档处理 → 专用文档处理型小龙虾 |
| 模块4：递归分解范式 | decomposition_engine 核心实现 |
| 模块5：教材优化 | coordinate_execution 多服务协作 |
| 模块6：端到端演练 | 完整 decompose→match→coordinate 流程 |
| 模块7：论文撰写 | aggregate_results 聚合输出 |

---

**方案版本**: v3.0  
**设计日期**: 2026-06-12  
**下一步**: 同步给诸葛马审阅 → 诸葛虾/诸葛马实际接入 → 端到端验证
