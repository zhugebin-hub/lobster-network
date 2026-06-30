# 🦞 龙虾网络 API 限速防护机制

> 版本：v1.0.0  
> 作者：虾尔（lobster-001）  
> 日期：2026-06-25  
> 状态：设计草案

---

## 一、问题定义

### 1.1 限速错误类型

龙虾网络中可能遇到的 API 限速错误分为 **三层**：

| 层级 | 错误来源 | 典型错误信息 | 影响范围 |
|------|---------|-------------|---------|
| **L1 模型层** | DashScope / Claude / OpenAI | `API rate limit reached`、`429`、`Try again in ~9500 min` | 单个节点所有 LLM 调用 |
| **L2 通信层** | 钉钉机器人 | `rate limit exceeded`、每分钟 20 条上限 | 龙虾间消息传递 |
| **L3 调度层** | 多节点并发 | 多个龙虾同时调用同一 API | 全局性雪崩 |

### 1.2 根因分析

```
┌─────────────────────────────────────────────┐
│  根因：多节点 + 多定时任务 + 无协调 = 并发碰撞  │
├─────────────────────────────────────────────┤
│  触发场景：                                   │
│  ① 9:00 定时汇报 + 心跳检查 → 模型层碰撞      │
│  ② 多个龙虾同时向钉钉群发消息 → 通信层碰撞     │
│  ③ 心跳轮询 + cron 任务 + 用户对话 → 三层叠加 │
│  ④ 子智能体批量 spawn → 瞬时请求爆发          │
└─────────────────────────────────────────────┘
```

---

## 二、整体架构：三层防护

```
┌─────────────────────────────────────────────────────────────────┐
│                    L3 调度层防护（全局协调）                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ 全局请求队列  │  │ 错峰调度器    │  │ 智能体预算分配器       │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    L2 通信层防护（钉钉通道）                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ 消息令牌桶   │  │ 优先级队列    │  │ 通道降级（钉钉→NFS→SSH）│  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    L1 模型层防护（LLM 调用）                       │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────┐  │
│  │ 滚动窗口计数器│  │ 分级降级策略  │  │ 指数退避 + 自动恢复    │  │
│  └─────────────┘  └──────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、L1 模型层防护：智能体级限速器

### 3.1 滚动窗口计数器

每个龙虾节点维护自己的请求计数器：

```python
# 每个节点独立的状态文件
# ~/.openclaw/workspace/rate-limit-state.json

{
  "provider": "dashscope",
  "model": "qwen3.5-plus",
  "window": {
    "duration_minutes": 60,
    "max_requests": 50,        # 保守估计，留 20% 缓冲
    "requests": [
      {"ts": "2026-06-25T09:00:12", "tokens": 3200, "type": "chat"},
      {"ts": "2026-06-25T09:01:45", "tokens": 1800, "type": "cron"}
    ]
  },
  "tier": "ok",                # ok | cautious | throttled | critical | paused
  "backoff": {
    "consecutive_429s": 0,
    "last_backoff_ms": 0,
    "paused_until": null
  }
}
```

### 3.2 五级降级策略

| 级别 | 触发条件 | 行为 | 示例 |
|------|---------|------|------|
| **ok** | 使用率 < 70% | 正常操作 | 所有任务正常执行 |
| **cautious** | 70% ≤ 使用率 < 85% | 跳过非核心后台检查 | 跳过天气检查、非紧急心跳 |
| **throttled** | 85% ≤ 使用率 < 95% | 仅处理用户消息，跳过 cron | 只回复直接对话 |
| **critical** | 95% ≤ 使用率 < 100% | 仅处理紧急用户消息，极简回复 | 一句话回复，不调用工具 |
| **paused** | 收到 429 | 暂停所有操作，指数退避 | 等待恢复时间 |

### 3.3 指数退避算法

```python
import random
import time

def calculate_backoff(consecutive_429s: int) -> int:
    """
    计算退避时间（毫秒），带抖动
    
    公式：base * 2^attempt + jitter
    - base = 30000ms (30秒)
    - max = 3600000ms (1小时)
    - jitter = 随机 0-30%
    """
    base = 30000
    max_backoff = 3600000
    
    backoff = min(base * (2 ** consecutive_429s), max_backoff)
    jitter = backoff * random.uniform(0, 0.3)
    return int(backoff + jitter)

# 退避时间表：
# 第1次 429 → 等待 30-40 秒
# 第2次 429 → 等待 60-80 秒
# 第3次 429 → 等待 120-160 秒
# 第4次 429 → 等待 240-320 秒
# 第5次 429 → 等待 480-640 秒
# 第6次 429 → 等待 960-1280 秒（16分钟）
# 第7次 429 → 等待 1920-2560 秒（32分钟）
# 第8次 429 → 等待 3600000ms（1小时，上限）
```

### 3.4 Gate-Record 模式

每个龙虾节点在执行 LLM 调用前后执行：

```bash
# 调用前：检查是否允许
python3 ~/.openclaw/workspace/skills/agent-rate-limiter/scripts/rate-limiter.py gate
EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo "🛑 限速中，跳过本次操作"
    exit 0  # 静默跳过，不报错
fi

if [ $EXIT_CODE -eq 1 ]; then
    echo "⚡ 限速警告，降级执行"
    # 跳过子智能体、后台任务
fi

# --- 执行实际 LLM 调用 ---

# 调用后：记录消耗
python3 ~/.openclaw/workspace/skills/agent-rate-limiter/scripts/rate-limiter.py record $TOKEN_COUNT
```

---

## 四、L2 通信层防护：钉钉消息限速

### 4.1 令牌桶算法

钉钉机器人限制：**每分钟 20 条**，超限封禁 10 分钟。

```python
# 全局消息令牌桶（所有龙虾共享）
# /shared/messages/token-bucket.json

{
  "capacity": 20,              # 桶容量 = 每分钟最大消息数
  "refill_rate": 20,           # 每分钟 refill 20 个令牌
  "last_refill": "2026-06-25T09:00:00",
  "tokens": 20,
  "queue": [
    {
      "msg_id": "msg-xxx",
      "from": "lobster-001",
      "to": "group",
      "priority": "high",       # high | normal | low
      "created_at": "2026-06-25T09:00:30",
      "content": "股票汇报..."
    }
  ]
}
```

### 4.2 消息优先级

| 优先级 | 消息类型 | 示例 |
|--------|---------|------|
| **P0 紧急** | 用户直接提问、定时汇报超时 | "帮我查一下XX"、15:00 股票汇报 |
| **P1 重要** | 龙虾间协作请求、任务结果 | "请处理任务 #123"、"PPT 已完成" |
| **P2 常规** | 心跳检查、状态同步 | "HEARTBEAT_OK"、"world-map 已更新" |
| **P3 低优** | 主动推送、社区互动 | 天气提醒、觅游社区动态 |

### 4.3 通道降级链

```
钉钉群（主通道）
    ↓ 失败/限速
NFS 文件通道（/shared/messages/）
    ↓ 失败/不可用
SSH 通道（远程写入）
    ↓ 失败/不可用
本地队列（待下次通道恢复后补发）
```

---

## 五、L3 调度层防护：全局协调

### 5.1 错峰调度

**核心原则：不同龙虾的不同定时任务错开时间，避免并发碰撞。**

```
┌─────────────────────────────────────────────────────────────────┐
│  全局定时任务错峰表                                              │
├────────────┬──────────┬────────────────────────────────────────┤
│  时间      │  执行者   │  任务                                  │
├────────────┼──────────┼────────────────────────────────────────┤
│  09:00:00  │ 虾尔      │ 股票汇报（Signal Arena）               │
│  09:00:30  │ 诸葛马    │ 每日简报                               │
│  09:01:00  │ 小陈      │ 文档同步检查                           │
│  09:02:00  │ 虾尔      │ 心跳检查（跳过 LLM 调用）              │
│  09:03:00  │ 院史馆龙虾│ 院史馆内容更新                         │
├────────────┼──────────┼────────────────────────────────────────┤
│  15:00:00  │ 虾尔      │ 股票汇报                               │
│  15:01:00  │ 诸葛马    │ 项目状态检查                           │
├────────────┼──────────┼────────────────────────────────────────┤
│  20:00:00  │ 虾尔      │ 股票汇报                               │
│  20:01:00  │ 觅游龙虾  │ 社区互动                               │
├────────────┼──────────┼────────────────────────────────────────┤
│  21:30     │ 虾尔      │ 心跳检查（读取日报）                    │
│  21:31     │ 诸葛马    │ 夜间同步                               │
└────────────┴──────────┴────────────────────────────────────────┘
```

### 5.2 智能体预算分配

每个 OpenClaw 实例的每日 token 预算：

```json
{
  "daily_budget": {
    "total_tokens": 500000,     // 每日总预算
    "reset_at": "00:00"
  },
  "node_allocations": {
    "lobster-001": {
      "daily_tokens": 200000,    // 40% - 主力节点
      "max_requests_per_hour": 30,
      "priority": "high"
    },
    "hermes": {
      "daily_tokens": 100000,    // 20%
      "max_requests_per_hour": 15,
      "priority": "high"
    },
    "zhuguxia": {
      "daily_tokens": 80000,     // 16%
      "max_requests_per_hour": 12,
      "priority": "medium"
    },
    "xiaochen": {
      "daily_tokens": 50000,     // 10%
      "max_requests_per_hour": 8,
      "priority": "medium"
    },
    "qoder": {
      "daily_tokens": 40000,     // 8%
      "max_requests_per_hour": 6,
      "priority": "low"
    },
    "lobster-museum-001": {
      "daily_tokens": 30000,     // 6%
      "max_requests_per_hour": 5,
      "priority": "low"
    }
  },
  "overflow_policy": "borrow_from_low_priority"
  // 高优先级节点可用完后可借用低优先级节点的剩余额度
}
```

### 5.3 批量合并策略

**原则：能一次调用解决的，不拆成多次。**

```
❌ 坏的做法：
  虾尔 → 调用 LLM 生成股票汇报 → 发送到钉钉
  虾尔 → 调用 LLM 生成天气提醒 → 发送到钉钉
  虾尔 → 调用 LLM 生成心跳摘要 → 发送到钉钉
  （3 次 LLM 调用 + 3 条钉钉消息）

✅ 好的做法：
  虾尔 → 调用 LLM 一次生成综合报告 → 合并发送
  （1 次 LLM 调用 + 1 条钉钉消息）
```

---

## 六、实现方案

### 6.1 新增文件

```
src/lobster_network/
├── rate_limiter.py          # L1 模型层限速器
├── message_queue.py         # L2 消息队列 + 令牌桶
├── global_scheduler.py      # L3 全局调度协调器
└── config/
    └── rate-limit-config.json  # 限速配置
```

### 6.2 rate_limiter.py 核心接口

```python
class RateLimiter:
    """龙虾网络统一限速器"""
    
    def gate(self, operation: str) -> GateResult:
        """
        调用前检查
        
        Returns:
            GateResult(allowed=True/False, tier, reason, wait_ms)
        """
        pass
    
    def record(self, tokens: int, operation: str):
        """调用后记录"""
        pass
    
    def on_429(self, provider: str, retry_after_ms: int = None):
        """收到 429 时的处理"""
        pass
    
    def get_status(self) -> dict:
        """当前限速状态"""
        pass
```

### 6.3 集成点

| 集成位置 | 调用方式 | 触发时机 |
|---------|---------|---------|
| **心跳检查** | `rate_limiter.gate("heartbeat")` | 每次心跳开始时 |
| **Cron 任务** | `rate_limiter.gate("cron")` | cron 执行前 |
| **用户对话** | `rate_limiter.gate("chat")` | 用户消息到达时 |
| **子智能体 spawn** | `rate_limiter.gate("spawn")` | spawn 前 |
| **钉钉消息发送** | `message_queue.push(msg)` | 发送消息时 |
| **LLM 调用** | `rate_limiter.record(tokens)` | 调用完成后 |

---

## 七、应急处理流程

### 7.1 收到 429 时的自动处理

```
收到 429
  │
  ├─ 1. 立即暂停当前任务
  ├─ 2. 记录 429 事件到日志
  ├─ 3. 计算退避时间（指数退避 + 抖动）
  ├─ 4. 设置恢复定时器
  ├─ 5. 降级当前 tier（ok → cautious → throttled → critical → paused）
  ├─ 6. 通知其他龙虾（通过 NFS 写入 /shared/messages/from-{node}/rate-limit-alert.json）
  │
  └─ 7. 恢复后：
       ├─ 7a. 恢复 tier 到 cautious（非直接回 ok）
       ├─ 7b. 检查是否有积压任务需要处理
       └─ 7c. 通知其他龙虾已恢复
```

### 7.2 降级通知格式

```json
{
  "event": "rate_limit_alert",
  "from": "lobster-001",
  "timestamp": "2026-06-25T09:00:15Z",
  "severity": "critical",
  "details": {
    "provider": "dashscope",
    "model": "qwen3.5-plus",
    "current_tier": "throttled",
    "estimated_resume": "2026-06-25T09:05:00Z",
    "affected_operations": ["heartbeat", "cron", "spawn"]
  },
  "requested_action": "其他龙虾请降低调用频率"
}
```

---

## 八、监控与告警

### 8.1 限速状态看板

每个龙虾节点暴露限速状态：

```json
// ~/.openclaw/workspace/rate-limit-status.json
{
  "node_id": "lobster-001",
  "updated_at": "2026-06-25T09:00:00Z",
  "model_layer": {
    "tier": "ok",
    "usage_pct": 45,
    "requests_this_hour": 12,
    "requests_this_day": 89,
    "tokens_this_day": 156000,
    "consecutive_429s": 0,
    "last_429_at": null
  },
  "comm_layer": {
    "dingtalk_tokens_remaining": 15,
    "messages_this_minute": 5,
    "channel_status": "active"
  },
  "schedule_layer": {
    "pending_jobs": 2,
    "skipped_jobs_today": 0,
    "next_maintenance_window": "2026-06-25T03:00:00Z"
  }
}
```

### 8.2 告警规则

| 条件 | 告警级别 | 通知方式 |
|------|---------|---------|
| tier 降至 throttled | ⚠️ 警告 | 写入状态文件，不主动通知 |
| tier 降至 critical | 🔶 重要 | NFS 通知其他龙虾 |
| tier 降至 paused | 🔴 紧急 | NFS 通知 + 钉钉消息（如果通道正常） |
| 连续 3 次 429 | 🔴 紧急 | 通知龙虾网络管理员 |
| 单日 token 消耗 > 80% 预算 | ⚠️ 警告 | 写入状态文件 |
| 钉钉通道封禁 | 🔶 重要 | 自动切换到 NFS 通道 |

---

## 九、渐进式实施计划

### Phase 1：立即可做（无需改代码）✅ 已完成 2026-06-25

- [x] 在每个龙虾的 HEARTBEAT.md 中添加 gate 检查
- [x] 在 cron 任务脚本开头添加限速检查
- [x] 错峰调整现有 cron 时间（错开整点）
  - 龙虾日报检查：9:00 → 9:05
  - 宿舍日报：9:00 → 9:10, 15:00 → 15:05, 20:00 → 20:05, 0:00 → 0:05
  - 股票汇报保持整点（核心任务）
- [ ] 合并同类定时汇报（股票+天气+心跳合并）

### Phase 2：代码级实现（1-2 周）

- [ ] 实现 `rate_limiter.py` 核心逻辑
- [ ] 实现 `message_queue.py` 令牌桶
- [ ] 在 `messenger.py` 中集成消息优先级
- [ ] 实现通道降级链

### Phase 3：全局协调（2-4 周）

- [ ] 实现 `global_scheduler.py`
- [ ] 实现龙虾间限速状态共享
- [ ] 实现预算分配和溢出策略
- [ ] 实现批量合并发送

---

## 十、配置示例

### 10.1 全局限速配置

```json
// config/rate-limit-config.json
{
  "version": "1.0.0",
  "updated_at": "2026-06-25T00:00:00Z",
  
  "model_limits": {
    "dashscope": {
      "qwen3.5-plus": {
        "requests_per_minute": 10,
        "requests_per_hour": 50,
        "tokens_per_day": 200000
      },
      "qwen-vl-plus": {
        "requests_per_minute": 5,
        "requests_per_hour": 30,
        "tokens_per_day": 100000
      }
    }
  },
  
  "comm_limits": {
    "dingtalk": {
      "messages_per_minute": 20,
      "messages_per_hour": 200,
      "cooldown_minutes_on_limit": 10
    }
  },
  
  "tier_thresholds": {
    "cautious": 0.70,
    "throttled": 0.85,
    "critical": 0.95,
    "critical": 0.95
  },
  
  "backoff": {
    "base_ms": 30000,
    "max_ms": 3600000,
    "jitter_pct": 0.3
  },
  
  "merge_policy": {
    "heartbeat_merge_window_minutes": 5,
    "report_merge_window_minutes": 10,
    "max_messages_per_merge": 3
  }
}
```

---

## 附录 A：现有 cron 错峰调整建议

```bash
# 当前冲突：
# 0 9 * * *  龙虾日报检查     → 与股票汇报 9:00 碰撞
# 0 9 * * *  宿舍日报         → 与股票汇报 9:00 碰撞
# */5 * * *  消息去重监控     → 高频，但无 LLM 调用，安全

# 建议调整：
# 股票汇报保持 9:00（核心任务）
# 龙虾日报检查 → 9:05（错开 5 分钟）
# 宿舍日报     → 9:10（再错开 5 分钟）
```

---

## 附录 B：与现有技能的集成

| 现有技能 | 集成方式 | 收益 |
|---------|---------|------|
| `agent-rate-limiter` | 作为 L1 层的基础实现 | 零开发成本，开箱即用 |
| `token-budget-monitor` | 作为 L3 层预算分配的数据源 | 全局 token 可视 |
| `model-rate-limit-recovery` | 作为 429 后的恢复流程 | 自动恢复流程 |
| `token-tracker-v2` | 作为 token 消耗统计 | 历史数据分析 |

**推荐方案：优先复用 `agent-rate-limiter` 技能，在其基础上扩展龙虾网络的多节点协调能力。**
