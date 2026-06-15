#  围棋九段培训系统 v4.0 - MCP 架构版学习方案

> **版本**: v4.0 (MCP架构)  
> **日期**: 2026-06-12  
> **设计者**: 虾尔  
> **架构**: MCP Router Server + MCP Go Training Server  
> **背景**: 从 NFS 文件通信升级为 MCP 标准协议，支持多智能体实时协作

---

## 一、架构升级概述

### 从 v3.0 到 v4.0 的核心变化

| 维度 | v3.0 (NFS) | v4.0 (MCP) |
|------|------------|------------|
| 通信方式 | 文件读写 + 30秒轮询 | SSE 实时流 + 毫秒级响应 |
| 消息路由 | 手动约定文件路径 | 自动匹配路由规则 |
| 服务发现 | 预定义目录结构 | 动态注册 + 心跳检测 |
| 消息可靠性 | 无确认机制 | pending→delivered→acked 全流程 |
| 扩展性 | 每新增服务需建目录 | 标准协议即插即用 |
| 围棋训练 | 直接读写 /shared/training/go/ | MCP Go Training Server 封装 |

---

## 二、新架构下的学习流程

### 2.1 日常训练流程（MCP化）

```
用户/教练                   MCP Router                  业务服务
  │                            │                            │
  │── 发起训练任务 ───────────→│                            │
  │   (go_training_task)       │── 自动路由 ──→ 诸葛虾/小陈  │
  │                            │                            │
  │                            │  ◄── 学员执行训练 ────────│
  │                            │   (通过 MCP Go Training)   │
  │                            │                            │
  │── 提交训练结果 ───────────→│── 路由 → 诸葛马 ─────────│
  │   (go_training_result)     │   (教练审阅)               │
  │                            │                            │
  │                            │  ◄── 诸葛马点评 ──────────│
  │                            │   (go_review)              │
  │── 接收点评 ────────────────│── 路由 → 虾尔 ───────────│
  │   (go_review_response)     │   (转发给用户)             │
```

### 2.2 对局流程（MCP化）

```
虾尔(入口)                MCP Router              诸葛马(裁判)        小陈/诸葛虾
  │                          │                        │                  │
  │── 对局请求 ─────────────→│── 路由 → 诸葛马 ──────→│                  │
  │   (go_match_request)     │                        │── 创建对局 ────→│
  │                          │                        │   (start_match)  │
  │                          │                        │                  │
  │                          │  ◄── 小陈落子 ─────────│                  │
  │                          │   (submit_move)        │                  │
  │                          │── 广播 ──→ 诸葛虾 ────→│                  │
  │                          │   (broadcast)          │                  │
  │                          │                        │                  │
  │                          │  ◄── 诸葛虾落子 ───────│                  │
  │                          │   (submit_move)        │                  │
  │                          │── 广播 ──→ 小陈 ──────→│                  │
  │                          │                        │                  │
  │                          │  [... 循环直到终局 ...] │                  │
  │                          │                        │                  │
  │                          │── 终局 → 诸葛马 ──────→│                  │
  │                          │   (go_match_end)       │── 计算胜负 ───→│
  │                          │                        │   (记录结果)     │
  │── 对局结果 ─────────────→│── 路由 → 虾尔 ───────→│                  │
  │   (go_match_result)      │   (转发给用户)         │                  │
```

---

## 三、MCP Tool 调用映射表

### 3.1 路由中枢 Tool（虾尔调用）

| 场景 | 调用 Tool | 参数示例 |
|------|-----------|----------|
| 虾尔启动 | `register_service` | service_id=lobster-001, name=虾尔, role=gateway |
| 保活 | `heartbeat` | service_id=lobster-001 |
| 发送消息 | `send_message` | from=lobster-001, to=hermes-001, type=go_training_task |
| 收取消息 | `receive_messages` | service_id=lobster-001, max_count=10 |
| 确认处理 | `ack_message` | message_id=xxx, service_id=lobster-001 |
| 查看服务 | `list_services` | role=worker |
| 查看统计 | `get_stats` | - |

### 3.2 围棋训练 Tool（诸葛虾/诸葛马调用）

| 场景 | 调用 Tool | 参数示例 |
|------|-----------|----------|
| 查询训练状态 | `get_training_status` | - |
| 获取学员档案 | `get_player_profile` | player_id=xiaochen |
| 获取学员进度 | `get_player_progress` | player_id=zhuguxia |
| 提交训练结果 | `submit_training_result` | player_id=zhuguxia, date=2026-06-12, solved=50, correct=40 |
| 发起对局 | `start_match` | black=xiaochen, white=zhuguxia, board_size=9 |
| 提交落子 | `submit_move` | match_id=xxx, player=xiaochen, coord=Q16 |
| 获取对局状态 | `get_match_status` | match_id=xxx |
| 生态总览 | `get_ecosystem_training_overview` | - |

---

## 四、第6周学习方案（MCP架构下执行）

### 4.1 本周目标：布局理论（中国流、小林流）

| 学员 | 每日任务 | MCP Tool 调用 |
|------|----------|---------------|
| 小陈 | 5道死活题 + 3道手筋题 + 学习中国流 + 1局9路棋 | `get_player_profile` → `submit_training_result` |
| 诸葛虾 | 8道死活题 + 5道手筋题 + 2个布局主题 + 2局9路棋 | `get_player_progress` → `submit_training_result` |

### 4.2 每日执行流程

**早晨 8:00 - 虾尔发起训练**
```python
# 虾尔通过 MCP Router 向两位学员发送训练任务
send_message(
    from_service="lobster-001",
    to_service="lobster-002",  # 诸葛虾
    type="go_training_task",
    payload={
        "week": 6,
        "day": 1,
        "tasks": [
            {"type": "life", "count": 8},
            {"type": "tesuji", "count": 5},
            {"type": "fuseki", "topic": "中国流"},
            {"type": "fuseki", "topic": "小林流"},
            {"type": "match", "board": 9}
        ]
    },
    priority="normal"
)
```

**白天 - 诸葛虾/小陈执行训练**
```python
# 学员通过 MCP Go Training 提交结果
submit_training_result(
    player_id="zhuguxia",
    date="2026-06-12",
    problems_solved=15,
    problems_correct=12,
    time_minutes=45,
    summary="今日学习了中国流和小林流布局，对中国流的小目挂角变化有了深入理解。",
    next_focus="明天重点练习小林流的变招"
)
```

**晚上 20:00 - 诸葛马审阅**
```python
# 诸葛马通过 MCP Router 收取结果并审阅
receive_messages(service_id="hermes-001")
# 审阅后发送点评
send_message(
    from_service="hermes-001",
    to_service="lobster-001",
    type="go_review",
    payload={
        "student": "zhuguxia",
        "date": "2026-06-12",
        "review": "今日表现良好，中国流理解到位。小林流还需加强实战练习。建议明天多下2局。",
        "rating": "A"
    }
)
```

**晚上 21:00 - 虾尔转发给用户**
```python
# 虾尔收到诸葛马点评，通过钉钉转发给则白
receive_messages(service_id="lobster-001")
# 钉钉消息: "则白，诸葛虾今日围棋学习已完成。诸葛马点评：今日表现良好..."
```

---

## 五、对局安排（MCP架构下）

### 5.1 本周对局计划

| 日期 | 对局 | 棋盘 | 裁判 |
|------|------|------|------|
| 周一 | 小陈(黑) vs 诸葛虾(白) | 9路 | 诸葛马 |
| 周三 | 诸葛虾(黑) vs 小陈(白) | 9路 | 诸葛马 |
| 周五 | 小陈(黑) vs 诸葛虾(白) | 9路 | 诸葛马 |
| 周六 | 复盘日（分析本周3局） | - | 诸葛马 |

### 5.2 对局 MCP 调用序列

```
# 1. 虾尔发起对局请求
send_message(from="lobster-001", to="hermes-001",
    type="go_match_request",
    payload={"black": "xiaochen", "white": "zhuguxia", "board": 9})

# 2. 诸葛马创建对局
start_match(black="xiaochen", white="zhuguxia", board_size=9)
# 返回 match_id

# 3. 小陈落子
submit_move(match_id=xxx, player="xiaochen", coord="Q16", reason="占据右上星位")

# 4. 诸葛虾收到落子并回应
receive_messages(service_id="lobster-002")  # 收到广播
submit_move(match_id=xxx, player="zhuguxia", coord="D4", reason="对角星位")

# 5. 循环直到终局...

# 6. 诸葛马记录结果并通知
send_message(from="hermes-001", to="lobster-001",
    type="go_match_result",
    payload={"match_id": xxx, "winner": "zhuguxia", "score": "B+2.5"})
```

---

## 六、新增 MCP 业务服务规划

### 6.1 近期计划

| 服务 | 功能 | 优先级 |
|------|------|--------|
| MCP Review Server | 论文/文档评审服务（AI黑客松评审迁移） | 高 |
| MCP Teaching Server | 教学分析服务（课程分析迁移） | 中 |
| MCP Schedule Server | 日程管理服务 | 低 |

### 6.2 MCP Review Server 设计（AI黑客松评审迁移）

```python
# Tool 设计
- review_document(url, criteria) - 评审指定文档
- submit_review_result(review_id, scores, comments) - 提交评审结果
- get_review_status(review_id) - 获取评审状态
- list_reviews(status) - 列出评审任务
```

---

## 七、监控与告警

### 7.1 健康检查

| 指标 | 阈值 | 告警方式 |
|------|------|----------|
| 服务在线率 | < 90% | 虾尔→钉钉通知 |
| 消息积压 | pending > 50 | 虾尔→钉钉通知 |
| 路由延迟 | > 5秒 | 记录日志 |
| 数据库大小 | > 100MB | 虾尔→钉钉通知 |

### 7.2 每日报告

虾尔每日 21:30 通过 MCP Router 获取统计并发送钉钉日报：
```
🦞 小龙虾生态日报 - 2026-06-12
━━━━━━━━━━━━━━━━━━━━
在线服务: 3/3
今日消息: 45条
待处理: 2条
围棋训练: 小陈15题(67%) 诸葛虾23题(82%)
对局: 1局进行中
```

---

## 八、回退方案

如果 MCP 架构出现问题，保留 NFS 作为备份：

1. **双写模式**: 关键消息同时写入 MCP 和 NFS
2. **NFS 轮询**: 保留原有轮询脚本作为备用
3. **切换开关**: `use_mcp=true/false` 配置文件控制

---

**方案版本**: v4.0  
**设计日期**: 2026-06-12  
**下一步**: 诸葛虾、诸葛马实际接入 + AI黑客松评审MCP化
