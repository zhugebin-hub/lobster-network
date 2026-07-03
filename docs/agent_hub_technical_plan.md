# 智能体中枢平台技术方案 v1.0

> **基于 OpenClaw 龙虾网络演进** | **日期**: 2026-07-03
> **架构代号**: LobsterHub v2.0

---

## 一、总体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        智能体中枢平台 (LobsterHub)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 微信通道  │  │ 飞书通道  │  │ 小程序通道│  │ API通道  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │              │              │              │             │
│  ┌────┴──────────────┴──────────────┴──────────────┴─────┐      │
│  │              统一接入网关 (Gateway Hub)                │      │
│  │  • 协议适配 (HTTP/WebSocket/MQTT)                     │      │
│  │  • 租户路由 (Tenant Router)                           │      │
│  │  • 限流/鉴权 (Rate Limit / Auth)                      │      │
│  └─────────────────────────┬─────────────────────────────┘      │
│                            │                                     │
│  ┌─────────────────────────┴─────────────────────────────┐      │
│  │              智能体编排层 (Agent Orchestrator)          │      │
│  │  • 任务分解 (DAG Scheduler)                            │      │
│  │  • Sub-agent 路由 (Capability Matching)                │      │
│  │  • 人工审核队列 (Human-in-the-loop)                    │      │
│  │  • 状态持久化 (State Machine)                          │      │
│  └─────────────────────────┬─────────────────────────────┘      │
│                            │                                     │
│  ┌─────────────────────────┴─────────────────────────────┐      │
│  │              通信总线 (Communication Fabric)           │      │
│  │  • MQTT Broker (实时消息)                              │      │
│  │  • HTTP/gRPC (服务间通信)                              │      │
│  │  • 事件总线 (Event Sourcing)                           │      │
│  └─────────────────────────┬─────────────────────────────┘      │
│                            │                                     │
│  ┌─────────────────────────┴─────────────────────────────┐      │
│  │              Sub-agent 层 (Digital Humans)             │      │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │      │
│  │  │感知Agent │ │决策Agent │ │执行Agent │ │反馈Agent │ │      │
│  │  │(Percept) │ │(Decide)  │ │(Act)     │ │(Review)  │ │      │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              基础设施层 (Infrastructure)                  │   │
│  │  • LLM 服务 (多模型/多租户/成本控制)                     │   │
│  │  • 向量记忆 (Embedding + 检索)                          │   │
│  │  • 工具集 (文件/数据库/API/外部服务)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心模块设计

### 2.1 多租户架构

```
Tenant (租户)
├── Team (团队)
│   ├── Member (成员)
│   │   ├── Role (角色: admin/manager/agent/user)
│   │   └── Permissions (权限集)
│   └── AgentGroup (智能体组)
│       └── Sub-agent (子智能体)
└── ResourceQuota (资源配额)
    ├── Token Limit (Token 限额)
    ├── Agent Count (智能体数量)
    └── Storage Quota (存储配额)
```

**数据隔离策略：**

| 层级 | 隔离方式 | 实现 |
|------|---------|------|
| 租户级 | 逻辑隔离 | `tenant_id` 前缀 + 数据库行级安全 |
| 团队级 | 逻辑隔离 | `team_id` 分组 + RBAC |
| 智能体级 | 进程隔离 | 独立 MQTT Client ID + 独立 Topic 命名空间 |
| 数据级 | 物理隔离 | 可选独立数据库/存储桶 |

**MQTT Topic 多租户扩展：**

```
{tenant_id}/{team_id}/{agent_id}/...

示例:
acme/engineering/agent-001/coach/cmd
acme/engineering/agent-001/student/ack
acme/sales/agent-002/coach/cmd
```

### 2.2 团队定义与权限

**角色体系：**

| 角色 | 权限 | 说明 |
|------|------|------|
| `super_admin` | 全平台管理 | 平台管理员 |
| `tenant_admin` | 租户内全权限 | 租户所有者 |
| `team_manager` | 团队管理 | 创建/管理智能体、分配任务 |
| `agent` | 执行权限 | 智能体身份，受限操作 |
| `user` | 只读/交互 | 普通用户，与智能体对话 |

**权限控制矩阵：**

```yaml
permissions:
  agent:
    create: ["tenant_admin", "team_manager"]
    execute: ["agent"]
    review: ["team_manager", "human_reviewer"]
    approve: ["team_manager"]
  task:
    create: ["team_manager", "agent"]
    execute: ["agent"]
    approve: ["human_reviewer"]
  resource:
    deploy_model: ["tenant_admin"]
    switch_model: ["team_manager"]
    view_cost: ["tenant_admin", "team_manager"]
```

### 2.3 Sub-agent 数字人 (感知→决策→执行→反馈)

**四阶段闭环架构：**

```
┌─────────────────────────────────────────────────────────┐
│                    任务请求 (User/External)              │
└───────────────────────────┬─────────────────────────────┘
                            │
                   ┌────────▼────────┐
                   │  1. 感知 Agent   │ Perception
                   │  (Percept Agent) │
                   └────────┬────────┘
                            │ 理解意图、提取参数、识别上下文
                   ┌────────▼────────┐
                   │  2. 决策 Agent   │ Decision
                   │  (Decide Agent)  │
                   └────────┬────────┘
                            │ 生成执行计划、选择工具、风险评估
                            │
                    ┌───────┴───────┐
                    │  人工审核?     │ 高风险操作需人工审批
                    └───────┬───────┘
                            │ 通过
                   ┌────────▼────────┐
                   │  3. 执行 Agent   │ Execution
                   │  (Act Agent)     │
                   └────────┬────────┘
                            │ 调用工具、执行操作、收集结果
                   ┌────────▼────────┐
                   │  4. 反馈 Agent   │ Review
                   │  (Review Agent)  │
                   └────────┬────────┘
                            │ 质量评估、用户反馈、经验沉淀
                            │
                   ┌────────▼────────┐
                   │  结果返回        │
                   └─────────────────┘
```

**Sub-agent 通信协议：**

```json
{
  "task_id": "task_20260703_xxxxx",
  "tenant_id": "acme",
  "team_id": "engineering",
  "stage": "percept|decide|act|review",
  "current_agent": "agent-001",
  "input": {
    "user_message": "帮我分析一下上周的销售数据",
    "context": {"history": [...], "files": [...]},
    "constraints": {"max_cost": 1000, "timeout": 300}
  },
  "state": {
    "percept": {"intent": "data_analysis", "entities": ["sales", "last_week"]},
    "decide": {"plan": [...], "tools": ["sql_query", "chart_gen"], "risk": "low"},
    "approved": true,
    "act": {"results": [...]},
    "review": {"score": 85, "feedback": "..."}
  },
  "status": "pending|perceiving|deciding|approved|executing|reviewing|completed|failed|rejected",
  "created_at": "2026-07-03T19:00:00Z",
  "updated_at": "2026-07-03T19:00:30Z"
}
```

### 2.4 企业级保障体系

#### 2.4.1 状态持久化 & 断点恢复

```python
class TaskStateMachine:
    """任务状态机 - 支持断点恢复"""

    STATES = [
        "pending", "perceiving", "deciding", "approved",
        "executing", "reviewing", "completed", "failed", "rejected"
    ]

    def transition(self, task_id, new_state, data=None):
        """状态转换 + 持久化"""
        checkpoint = {
            "task_id": task_id,
            "from_state": self.current_state(task_id),
            "to_state": new_state,
            "data": data,  # 当前阶段数据快照
            "timestamp": datetime.now().isoformat(),
        }
        # 写入 checkpoint
        self.storage.save_checkpoint(checkpoint)
        # 更新状态
        self.update_state(task_id, new_state)
        # 发送事件
        self.event_bus.emit("task.state_changed", checkpoint)
```

#### 2.4.2 异常重试 & 降级

```python
class RetryPolicy:
    """指数退避重试策略"""

    def __init__(self, max_retries=3, base_delay=2, max_delay=60):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def should_retry(self, attempt, error):
        if attempt >= self.max_retries:
            return False, self._degrade(error)
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        return True, delay

    def _degrade(self, error):
        """降级策略"""
        if isinstance(error, LLMTimeoutError):
            return {"action": "switch_model", "fallback": "smaller_model"}
        elif isinstance(error, ToolError):
            return {"action": "skip_tool", "notify_user": True}
        elif isinstance(error, CostExceededError):
            return {"action": "abort", "notify_admin": True}
        return {"action": "abort", "reason": str(error)}
```

#### 2.4.3 Token 成本 & 延迟控制

```python
class CostController:
    """Token 成本控制器"""

    def __init__(self, tenant_id):
        self.quota = self.load_quota(tenant_id)
        self.usage = self.load_usage(tenant_id)

    def check_budget(self, estimated_tokens):
        """检查预算"""
        if self.usage.total + estimated_tokens > self.quota.daily_limit:
            raise CostExceededError(
                f"超出每日限额: 已用 {self.usage.total}/{self.quota.daily_limit}"
            )
        # 预警阈值
        if self.usage.total / self.quota.daily_limit > 0.8:
            self.notify_warning(tenant_id, "token_usage_warning")

    def record_usage(self, model, tokens, cost):
        """记录用量"""
        self.usage.add(model=model, tokens=tokens, cost=cost)
        self.save_usage(self.usage)
```

```python
class LatencyController:
    """延迟控制器"""

    def select_model(self, task_complexity, timeout_budget):
        """根据复杂度+超时预算选择模型"""
        if task_complexity == "simple" and timeout_budget < 5:
            return "qwen3.5-plus"  # 快速模型
        elif task_complexity == "complex" and timeout_budget > 30:
            return "claude-opus-4.6"  # 高质量模型
        else:
            return "qwen3.5-plus"  # 默认平衡
```

#### 2.4.4 高风险规则拦截

```python
class RiskInterceptor:
    """高风险操作拦截器"""

    RISK_RULES = {
        "file_delete": {"level": "high", "require_approval": True},
        "database_drop": {"level": "critical", "require_approval": True, "block": True},
        "api_call_external": {"level": "medium", "require_approval": False},
        "model_switch": {"level": "low", "require_approval": False},
        "financial_transfer": {"level": "critical", "require_approval": True, "block": True},
    }

    def evaluate(self, action, context):
        rule = self.RISK_RULES.get(action)
        if not rule:
            return {"risk": "unknown", "approved": True}

        result = {
            "action": action,
            "level": rule["level"],
            "approved": not rule.get("block", False),
            "requires_human_review": rule.get("require_approval", False),
        }

        # 动态风险评估
        if context.get("is_first_time"):
            result["level"] = "critical"
            result["block"] = True

        return result
```

#### 2.4.5 AIOps 监控

```python
class AIOpsMonitor:
    """AI 运维监控"""

    METRICS = {
        "agent_health": "每个智能体健康状态",
        "task_success_rate": "任务成功率",
        "avg_latency": "平均响应延迟",
        "token_cost_per_day": "每日 Token 成本",
        "error_rate_by_type": "按类型错误率",
        "queue_depth": "任务队列深度",
        "model_switch_count": "模型切换次数",
    }

    ALERTS = {
        "agent_offline": {"threshold": 1, "action": "restart"},
        "error_rate_high": {"threshold": 0.05, "action": "notify_admin"},
        "cost_anomaly": {"threshold": "2x_daily_avg", "action": "notify_tenant_admin"},
        "latency_spike": {"threshold": "p95 > 30s", "action": "scale_up"},
        "queue_backlog": {"threshold": 100, "action": "add_agents"},
    }
```

### 2.5 开源 LLM 部署 & 调优

#### 2.5.1 硬件配置推荐

| 模型 | 参数量 | GPU 推荐 | 显存 | 内存 | 存储 | 预期 QPS |
|------|--------|----------|------|------|------|----------|
| Qwen2.5-7B | 7B | 1× RTX 4090 | 24GB | 32GB | 100GB | 20-30 |
| Qwen2.5-14B | 14B | 1× A100-40G | 40GB | 64GB | 200GB | 10-15 |
| Qwen2.5-32B | 32B | 1× A100-80G | 80GB | 128GB | 400GB | 5-8 |
| Qwen2.5-72B | 72B | 2× A100-80G | 160GB | 256GB | 800GB | 3-5 |
| Llama-3.1-70B | 70B | 4× A100-80G | 320GB | 512GB | 1TB | 2-3 |

#### 2.5.2 部署架构

```
┌─────────────────────────────────────────────┐
│              LLM 服务集群                    │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ vLLM     │  │ vLLM     │  │ vLLM     │  │
│  │ Qwen-7B  │  │ Qwen-32B │  │ Llama-70B│  │
│  │ (GPU 1)  │  │ (GPU 2)  │  │ (GPU 3-4)│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │              │              │        │
│  ┌────┴──────────────┴──────────────┴─────┐ │
│  │        模型路由 (Model Router)          │ │
│  │  • 负载均衡                            │ │
│  │  • 模型切换                            │ │
│  │  • 成本控制                            │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │        推理优化                          │ │
│  │  • vLLM (PagedAttention)               │ │
│  │  • GGUF 量化 (4bit/8bit)               │ │
│  │  • LoRA 适配器 (多任务)                │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

#### 2.5.3 模型调优策略

```yaml
tuning:
  # SFT 监督微调
  sft:
    data_format: "alpaca"
    max_length: 4096
    epochs: 3
    lr: 2e-5
    lora:
      r: 16
      alpha: 32
      target_modules: ["q_proj", "v_proj"]

  # RLHF/DPO 人类反馈
  dpo:
    reference_model: "base_model"
    beta: 0.1
    batch_size: 4

  # 量化部署
  quantization:
    method: "AWQ"  # 或 GPTQ/llama.cpp
    bits: 4
    group_size: 128
```

### 2.6 模型切换

```python
class ModelRouter:
    """智能模型路由器"""

    MODELS = {
        "fast": {"model": "qwen3.5-plus", "max_tokens": 4096, "cost_per_k": 0.002},
        "balanced": {"model": "qwen3.5-plus", "max_tokens": 8192, "cost_per_k": 0.004},
        "quality": {"model": "claude-opus-4.6", "max_tokens": 32768, "cost_per_k": 0.06},
        "local": {"model": "qwen2.5-32b-local", "max_tokens": 8192, "cost_per_k": 0},
    }

    def route(self, task):
        """根据任务特征选择模型"""
        # 1. 检查成本预算
        if task.max_cost < 0.01:
            return self.MODELS["local"]

        # 2. 检查复杂度
        if task.complexity == "simple":
            return self.MODELS["fast"]

        # 3. 检查质量要求
        if task.quality_requirement == "high":
            return self.MODELS["quality"]

        # 4. 默认
        return self.MODELS["balanced"]

    def switch(self, tenant_id, model_name):
        """手动切换租户默认模型"""
        self.validate_model(model_name)
        self.update_tenant_config(tenant_id, model_name)
        self.notify_change(tenant_id, model_name)
```

### 2.7 微信 & 飞书接入

```python
class ChannelAdapter:
    """统一渠道适配器"""

    CHANNELS = {
        "wechat": {
            "type": "polling",
            "protocol": "HTTP",
            "message_format": "xml",
            "media_support": ["image", "voice", "video", "file"],
        },
        "feishu": {
            "type": "webhook",
            "protocol": "HTTP",
            "message_format": "json",
            "media_support": ["image", "file", "card"],
        },
        "miniprogram": {
            "type": "websocket",
            "protocol": "WSS",
            "message_format": "json",
            "media_support": ["image", "voice", "location"],
        },
    }

    def normalize_message(self, channel, raw_message):
        """统一消息格式"""
        return {
            "channel": channel,
            "user_id": raw_message["sender"],
            "content": raw_message["text"],
            "attachments": raw_message.get("media", []),
            "context": {"session_id": raw_message.get("session")},
            "timestamp": raw_message["time"],
        }

    def send_message(self, channel, user_id, message):
        """渠道适配发送"""
        adapter = self.get_adapter(channel)
        return adapter.send(user_id, message)
```

### 2.8 小程序接入

```
┌─────────────────────────────────────────────┐
│              小程序前端                       │
│  • 用户界面 (聊天/任务/报告)                  │
│  • WebSocket 实时通信                        │
│  • 文件上传/图片预览                         │
└──────────────────────┬──────────────────────┘
                       │ WSS
┌──────────────────────┴──────────────────────┐
│              小程序后端 API                   │
│  • 用户认证 (微信登录)                       │
│  • 消息路由 (→ 智能体中枢)                   │
│  • 任务查询 & 状态同步                       │
│  • 文件存储 (OSS)                            │
└──────────────────────┬──────────────────────┘
                       │ HTTP/gRPC
┌──────────────────────┴──────────────────────┐
│              智能体中枢 (LobsterHub)          │
└─────────────────────────────────────────────┘
```

---

## 三、与小龙虾网络演进路径

### Phase 1: 基础扩展 (1-2个月)

| 任务 | 内容 | 基于现有 |
|------|------|---------|
| 多租户 | 添加 tenant_id 前缀，数据库隔离 | MQTT Topic 扩展 |
| 团队定义 | RBAC 权限模型 | 现有教练/学员角色 |
| 模型切换 | ModelRouter 集成 | Hermes /model 命令 |
| 飞书接入 | 飞书机器人适配器 | 微信通道经验 |

### Phase 2: Sub-agent 闭环 (2-3个月)

| 任务 | 内容 | 基于现有 |
|------|------|---------|
| 感知Agent | 意图识别+参数提取 | 现有消息解析 |
| 决策Agent | 任务分解+工具选择 | 现有训练调度 |
| 执行Agent | 工具调用+结果收集 | 现有 AI 引擎 |
| 反馈Agent | 质量评估+经验沉淀 | 现有 NWDAF 评估 |

### Phase 3: 企业级保障 (2-3个月)

| 任务 | 内容 | 基于现有 |
|------|------|---------|
| 状态持久化 | 任务状态机+断点恢复 | 现有 checkpoint |
| 成本控制 | Token 追踪+预算告警 | 现有龙虾币 |
| 规则拦截 | 高风险操作拦截 | 现有熔断器 |
| AIOps | 监控+告警+自动恢复 | 现有 monitor 脚本 |

### Phase 4: LLM 部署 & 小程序 (3-4个月)

| 任务 | 内容 | 新增 |
|------|------|------|
| 本地部署 | vLLM + 量化部署 | 全新 |
| 微调调优 | SFT + DPO | 全新 |
| 小程序 | 微信小程序开发 | 全新 |

---

## 四、技术栈选型

| 层级 | 技术 | 说明 |
|------|------|------|
| **通信** | MQTT (Eclipse Mosquitto) + gRPC | 实时消息 + 服务间通信 |
| **编排** | Python + DAG 调度器 | 任务分解+Sub-agent 路由 |
| **LLM** | vLLM + HuggingFace Transformers | 本地模型推理 |
| **记忆** | ChromaDB / Weaviate | 向量数据库 |
| **存储** | PostgreSQL + Redis | 关系数据 + 缓存 |
| **监控** | Prometheus + Grafana | AIOps 指标 |
| **部署** | Docker + systemd | 容器化 + 进程管理 |
| **前端** | 微信小程序 + Web Dashboard | 用户界面 |

---

## 五、部署架构

```
┌─────────────────────────────────────────────────┐
│  生产环境 (3 节点集群)                            │
├─────────────────────────────────────────────────┤
│                                                 │
│  节点1 (诸葛马 47.93.6.57)                       │
│  • MQTT Broker (Mosquitto)                      │
│  • PostgreSQL + Redis                           │
│  • Gateway Hub + Agent Orchestrator             │
│  • Prometheus + Grafana                         │
│                                                 │
│  节点2 (GPU 服务器)                              │
│  • vLLM 推理集群 (Qwen/Llama)                   │
│  • 向量数据库 (ChromaDB)                        │
│                                                 │
│  节点3 (应用服务器)                               │
│  • 微信/飞书/小程序 接入网关                      │
│  • Web Dashboard                                │
│  • 文件存储 (OSS)                               │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 六、关键指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 并发租户 | 100+ | 支持100个独立组织 |
| 并发智能体 | 1000+ | 每租户10个智能体 |
| 消息延迟 | <100ms | MQTT 内部通信 |
| 任务完成率 | >95% | 端到端任务成功 |
| 人工审核率 | <10% | 低风险操作自动通过 |
| Token 成本 | <¥0.01/任务 | 智能模型路由 |
| 可用性 | 99.9% | 断点恢复+降级 |

---

## 七、风险 & 对策

| 风险 | 影响 | 对策 |
|------|------|------|
| MQTT Broker 单点故障 | 全平台瘫痪 | 主备集群 + 自动切换 |
| Token 成本失控 | 预算超支 | 硬限额 + 实时告警 |
| 高风险操作未拦截 | 数据损失 | 多层拦截 + 人工审核 |
| LLM 服务质量下降 | 任务失败 | 多模型备份 + 自动切换 |
| 多租户数据泄露 | 安全事件 | 行级安全 + 加密存储 |

---

**文档版本**: v1.0 | **作者**: 诸葛马 (Hermes) | **日期**: 2026-07-03
