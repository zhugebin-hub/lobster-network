---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 43fef9909290d56b1cb7d908f8d89930_cf85993b76f611f1a7da5254006c9bbf
    ReservedCode1: zY0KNTBmQK5kpoZL44qjPf2UooWvZD1Mt7vzbTGawlTbjMLXL7z0WKE+L01buVCUZEV6hQaq/tBhOqWkSsYoEzOR3G9ki+WU7Yk2g+0ezf68M/vOiMJYA2Q9/B7fNWF79qspVetpgcPR/VJA+X9tl0hg2pfyHHsiHMaEWdZ96Ov+5R6owtqGqGiQc48=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 43fef9909290d56b1cb7d908f8d89930_cf85993b76f611f1a7da5254006c9bbf
    ReservedCode2: zY0KNTBmQK5kpoZL44qjPf2UooWvZD1Mt7vzbTGawlTbjMLXL7z0WKE+L01buVCUZEV6hQaq/tBhOqWkSsYoEzOR3G9ki+WU7Yk2g+0ezf68M/vOiMJYA2Q9/B7fNWF79qspVetpgcPR/VJA+X9tl0hg2pfyHHsiHMaEWdZ96Ov+5R6owtqGqGiQc48=
---

# 小龙虾网络 MQTT 集成方案设计

> 目标：围棋学习和对局场景最小闭环 | 策略：不追求完美，先跑通

---

## 一、MQTT 在智能体网络的最新应用（联网调研）

### 1.1 A2A over MQTT（2026年6月，EMQ/Google）

Google 推出的 **Agent-to-Agent (A2A)** 协议定义了智能体间通信的四大核心概念：

| 概念 | 说明 |
|------|------|
| **Agent Cards** | 结构化元数据（JSON），描述Agent能力、接口与安全要求 |
| **Messages** | Agent间单次通信，含请求/回复/问询澄清三类 |
| **Tasks** | 带状态的工作单元，完整生命周期：submitted→working→completed |
| **Artifacts** | 任务过程中逐步产出的中间结果（支持流式推送） |

A2A 采用传输层无关设计，基于 MQTT 实现后得到天然优势：

- **Agent发现**：保留消息(Retained)让新订阅者立即获取所有Agent Card，无需等待重新上报
- **在线检测**：遗嘱消息(LWT)自动推送异常宕机告警，区分 agent/lwt/broker 三种状态来源
- **负载均衡**：共享订阅将任务分发给同组多个消费者
- **权限管控**：主题级 ACL 按 `{org_id}/{unit_id}/{agent_id}` 精确控制
- **流式传输**：离散事件流式推送，QoS 1 保证断线重连后消息补传
- **多轮交互**：中断式任务（同Task ID）和多步骤会话（同Context ID，独立Task ID）

### 1.2 EMQX 6.2 企业级Agent治理（2026年4月）

EMQX Enterprise 6.2 原生集成 A2A Registry：
- 三种注册方式：MQTT自注册 / 控制面板注册 / REST API注册，消费者无感知差异
- 速率限制防止注册风暴
- Agent Card 模式校验
- 内置在线状态跟踪（基于 MQTT session state）
- AI Agent 可通过标准化 API 直接管理 Broker

### 1.3 MCP over MQTT（2025年 EMQ）

将 MCP 协议与 MQTT 结合，解决 IoT/物理世界设备通信痛点：
- 轻量：MQTT 比 HTTP 更适合低功耗设备
- 大规模：MQTT 天然支持百万级连接
- 弱网：QoS 分级保证 + 离线消息
- 自动路由：基于主题的发布/订阅，无需代码中硬编码路由

### 1.4 行业趋势总结

```
个人智能体(Skills+MCP) → 多智能体框架(CrewAI/LangGraph) → A2A 协议(开放互通)
                                    ↓
                        通信层从「进程内函数调用」→「发布/订阅模式(MQTT)」
```

---

## 二、小龙虾网络现状分析

### 2.1 已有通信体系

```
┌─────────────────────────────────────────────────────┐
│                  小龙虾网络 V4.1                      │
├─────────────────────────────────────────────────────┤
│  L2 消息队列(message_queue.py)                       │
│  ├── 令牌桶算法(20条/分钟)                            │
│  ├── P0-P3 四级优先级                                │
│  ├── 通道降级: 钉钉 → NFS → SSH → 本地              │
│  └── 重试机制(最多3次)                               │
├─────────────────────────────────────────────────────┤
│  围棋训练系统(文件系统消息队列)                        │
│  ├── /shared/messages/queue/{node}/inbox            │
│  ├── /shared/messages/queue/{node}/outbox           │
│  ├── /shared/messages/queue/{node}/processed        │
│  └── JSON消息: task_id, type, task                  │
├─────────────────────────────────────────────────────┤
│  MCP 围棋训练服务器                                  │
│  ├── get_training_status / get_player_profile       │
│  ├── submit_training_result / start_match           │
│  ├── submit_move / get_match_status                 │
│  └── stdio 通信（通过路由中枢调用）                   │
└─────────────────────────────────────────────────────┘
```

### 2.2 核心痛点

1. **文件系统消息队列**：依赖共享目录，跨机器需 NFS，延迟高、不可靠
2. **无实时通知**：学员需要轮询 inbox 目录，无法即时感知新任务
3. **无状态感知**：不知道其他节点是否在线，对局匹配靠人工
4. **扩展性差**：新增节点需手动配置目录和 NFS 挂载

### 2.3 可复用资产

- `go_learning_tools_package.py`（43KB）：完整的 GoBoard、GoProblemGenerator、GoAnalyzer、GoLearningDashboard
- `mcp_go_training_server.py`：12个MCP工具，已覆盖训练管理+对局操作
- `xiaochen_go_trainer_v2.py`：消息驱动的学员训练脚本
- `message_queue.py`：带优先级和降级通道的消息队列

---

## 三、MQTT 集成方案

### 3.1 设计原则

> **核心策略：用围棋学习和对局场景先跑通最小闭环，不做完美架构**

- ✅ 围棋训练任务分发 + 结果回传
- ✅ 围棋对局实时落子 + 状态同步
- ✅ 节点心跳 + 在线感知
- ✅ 与现有文件系统消息队列兼容（双通道并存）
- ❌ 不做 Agent 自动发现（二期）
- ❌ 不做 A2A Agent Card（二期）
- ❌ 不做多租户（二期）

### 3.2 主题结构

```
lobster/go/
├── {node_id}/                    # 节点专属命名空间
│   ├── training/task            # 教练→学员：训练任务
│   ├── training/result          # 学员→教练：训练结果
│   └── training/status          # 训练状态更新
│
├── matches/                      # 对局命名空间
│   ├── {match_id}/move          # 落子事件
│   ├── {match_id}/status        # 对局状态
│   └── {match_id}/chat          # 对局分析/聊天
│
└── system/                       # 系统级
    ├── heartbeat                # 心跳（全节点发布）
    ├── announce                 # 公告（教练→全员）
    └── status/request           # 状态查询请求
```

### 3.3 消息格式

统一 JSON 格式，与现有文件系统消息队列兼容：

```json
{
  "msg_id": "msg-xiaochen-1688-a1b2c3d4",
  "type": "training_task | training_result | match_move | match_status | heartbeat | announce",
  "from": "xiaochen",
  "to": "zhugema",
  "timestamp": "2026-07-03T14:30:00",
  "payload": {
    // 与现有训练系统 JSON 格式保持一致
    "task_id": "task-001",
    "lesson_type": "life_death",
    "problem": { ... },
    "result": { ... }
  }
}
```

### 3.4 通信流程（围棋场景）

#### 训练流程
```
教练(诸葛马)                     MQTT Broker                     学员(小陈)
    │                                │                              │
    │── publish go/xiaochen/         │                              │
    │   training/task ──────────────>│                              │
    │   {type:training_task,         │                              │
    │    payload:{deck:死活题10道}}   │                              │
    │                                │── push ───────────────────>│
    │                                │   go/xiaochen/training/task │
    │                                │                              │── 做题中...
    │                                │         go/xiaochen/         │
    │                                │   <── publish ──────────────│
    │                                │         training/result      │
    │<── push ──────────────────────│                              │
    │    {type:training_result,      │                              │
    │     payload:{correct:7/10}}    │                              │
    │── 分析成绩，准备下轮 ──────────>                              │
```

#### 对局流程
```
小陈(黑)                        MQTT Broker                      诸葛虾(白)
    │                                │                              │
    │── publish go/matches/          │                              │
    │   m001/move ──────────────────>│                              │
    │   {player:xiaochen,color:black,│                              │
    │    coord:Q16}                  │── push ───────────────────>│
    │                                │   go/matches/m001/move       │── 分析局面
    │                                │                              │── 落子
    │                                │         go/matches/m001/     │
    │                                │   <── publish ──────────────│
    │<── push ──────────────────────│         move                 │
    │   {player:zhuguxia,            │                              │
    │    color:white,coord:D4}       │                              │
```

### 3.5 双通道兼容策略

```
                     ┌──────────────┐
                     │  消息路由器   │
                     └──────┬───────┘
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ MQTT通道  │ │ NFS通道  │ │ 本地通道  │
        │ (优先)    │ │ (降级)   │ │ (兜底)   │
        └──────────┘ └──────────┘ └──────────┘
              │             │             │
              └─────────────┼─────────────┘
                            ▼
              ┌────────────────────────┐
              │ 现有 Go Training System │
              └────────────────────────┘
```

- MQTT 通道可用时：实时推送，低延迟（<100ms）
- MQTT 不可用时：自动降级到 NFS/本地文件系统
- 消息格式统一，通道切换对上层透明

### 3.6 Broker 选型

| Broker | 适用场景 | 说明 |
|--------|---------|------|
| **Mosquitto** | 开发/单机 | 轻量，brew install mosquitto，零配置即可用 |
| EMQX Serverless | 生产/多机 | 永久免费套餐，无需管理基础设施 |
| EMQX Enterprise 6.2 | 大规模 | 原生 A2A Registry，Agent治理 |

**当前推荐**：Mosquitto（开发阶段，本地运行）→ 二期迁移 EMQX Serverless（多节点互联）

---

## 四、实现计划

### Phase 1：核心 MQTT 客户端（本次）

| 文件 | 功能 |
|------|------|
| `lobster_mqtt_core.py` | MQTT 连接管理、发布/订阅、自动重连、心跳 |
| `lobster_mqtt_go_bridge.py` | 围棋训练桥接：MQTT ⇄ 现有训练系统 |

### Phase 2：多节点对局（下一步）

- MQTT 对局匹配
- 实时落子同步
- SGF 棋谱生成

### Phase 3：Agent 网络（远期）

- A2A Agent Card 注册
- 能力自动发现
- 跨节点任务协同

---

## 五、关键指标

| 指标 | 目标值 | 备注 |
|------|--------|------|
| 消息延迟 | <100ms（MQTT） | 相比 NFS 轮询（>1s）提升10倍+ |
| 离线可靠性 | QoS 1（至少一次） | MQTT Broker 持久化 |
| 改造量 | 0改动现有代码 | 桥接模式，双通道并存 |
| 部署 | 1条命令启动 | `brew install mosquitto && mosquitto -d` |
*（内容由AI生成，仅供参考）*
