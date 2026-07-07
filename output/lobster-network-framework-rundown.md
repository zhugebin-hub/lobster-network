# LobsterNetwork 框架运行机制与模块学习总结

> 版本：v0.4.1 | 生成日期：2026-07-07  
> 源码根路径：`src/lobster_network/`（主包 10302 行 Python）

---

## 一、框架总览：六层 Sandwich 架构

LobsterNetwork 采用 **六层 Sandwich 架构**，自顶向下为：

```
┌─────────────────────────────────────────────────────────────┐
│  应用层 (Application Layer)                                  │
│  围棋训练 / 海报设计 / PPT 制作 / 社区讨论                    │
├─────────────────────────────────────────────────────────────┤
│  运营层 (Operations Layer)                                   │
│  Dispatcher 调度器 | Coach 教练 | Agent 守护                 │
├─────────────────────────────────────────────────────────────┤
│  可靠通信层 (Reliable Communication Layer)                   │
│  Messenger | ACK/NACK | 重试 | 多通道切换                    │
├─────────────────────────────────────────────────────────────┤
│  框架层 (Framework Layer)                                    │
│  Node | DialogueEngine | EmergenceDetector | WorldState      │
│  LobsterNetwork | Registry | TimeArbitrage                  │
├─────────────────────────────────────────────────────────────┤
│  基础设施层 (Infrastructure Layer)                           │
│  Network (IndraNet/SSH) | Communication (WebSocket)          │
│  Utils (Config/Logger/MessageProtocol)                       │
├─────────────────────────────────────────────────────────────┤
│  经济与治理层 (Economy & Governance Layer)                   │
│  TokenEconomy | SmartContract | DEX | LiquidityMining        │
│  DAOGovernance | Layer2 | CrossChain | MultiCurrency         │
└─────────────────────────────────────────────────────────────┘
```

**数据流**：应用层触发任务 → 运营层调度 → 框架层编排 Node 对话/涌现检测 → 基础设施层传输 → 经济层记录/激励。

---

## 二、核心模块逐一解析

### 2.1 Node 节点模型（`node.py`，95 行）

**职责**：认知编译系统的基础单元，是框架中所有智能实体的最小模型。

**关键属性**：
- `node_id` / `name`：唯一标识与名称
- `type`：节点类型（`human` / `agent` / `coach` / `student`）
- `seed`（认知种子）：包含 `perspective`（认知视角）、`knowledge_base`（知识结构）、`value_orientation`（价值取向）、`learning_rate`（学习率：high/medium/low）
- `capabilities`：能力列表（如 `go_training`、`problem_solving`）
- `current_world`：世界状态快照（`version`、`loaded_chunks`、`unlocked_treasures`）
- `spawned_at`：节点诞生时间

**核心方法**：
- `update_world(chunk_id, treasure_id)`：版本号自增，追加 chunk/treasure
- `from_dict(cls, data)`：工厂方法反序列化

**依赖关系**：无外部模块依赖，被 `DialogueEngine`、`LobsterNetwork`、`IndraNet`、`WorldStateManager` 引用。

---

### 2.2 DialogueEngine 对话引擎（`dialogue.py`，184 行）

**职责**：驱动两个 Node 之间的认知碰撞对话，计算涌现值，生成新见解。

**核心公式 — 涌现值计算**：
```
emergence_score = perspective_distance × 0.3
                + knowledge_complementarity × 0.3
                + dialogue_depth × 0.2
                + novelty_of_output × 0.2
```

**各权重说明**：
| 维度 | 权重 | 计算逻辑 | 当前简化实现 |
|------|------|---------|------------|
| 视角距离 | 0.3 | 两个节点视角的差异度 | 相同=0.0，不同=1.0（二值） |
| 知识互补性 | 0.3 | 知识结构的互补程度 | 相同=0.0，不同=1.0（二值） |
| 对话深度 | 0.2 | 多轮对话的深度累积 | 固定为 1.0 |
| 输出新颖度 | 0.2 | 对话输出的创新程度 | 固定为 0.5 |

> **注意**：当前实现中对话深度和输出新颖度均为硬编码常量，真实的深度/新颖度计算待后续版本接入 LLM。

**输入输出**：
- **输入**：`Node A` + `Node B` + `trigger`（触发事件描述）
- **输出**：`DialogueResult`（含 `dialogue_id`、`emergence_score`、`new_insight`、`treasure_unlocked` 等）

**宝藏解锁机制**：当 `emergence_score > threshold`（默认 0.5），自动为两个节点解锁宝藏。

**依赖**：`node.py`（Node）。

---

### 2.3 EmergenceDetector 涌现检测器（`emergence.py`，98 行）

**职责**：检测对话是否触发涌现事件，管理涌现事件历史和统计。

**核心数据结构**：
- `EmergenceEvent`：`event_id`、`dialogue_id`、`participants`、`emergence_score`、`new_insight`、`treasure_unlocked`
- `EmergenceDetector`：维护 `threshold`（默认 0.5）和 `events` 列表

**核心方法**：
- `detect(dialogue_result)` → `Optional[EmergenceEvent]`：当 `emergence_score > threshold` 时创建事件
- `get_statistics()` → `Dict`：返回总事件数、平均/最高涌现值、宝藏解锁数

**阈值机制**：单一浮点阈值（0.5），未实现自适应调整或多维度阈值。

---

### 2.4 WorldState 世界状态管理器（`world_state.py`，121 行）

**职责**：管理每个节点的世界状态，支持状态版本控制和增量更新。

**WorldState 四维状态模型**：
| 维度 | 字段 | 用途 |
|------|------|------|
| Chunks（认知区块） | `loaded_chunks` | 节点已加载的知识块 |
| Treasures（宝藏） | `unlocked_treasures` | 对话涌现解锁的宝藏 |
| Tasks（任务） | `current_tasks` | 当前正在执行的任务 |
| Spawned（衍生节点） | `spawned_nodes` | 该节点衍生出的新节点 |

**核心方法**：
- `get_state(node_id)` → `WorldState`：获取或惰性创建状态
- `update_state(node_id, chunk_id, treasure_id, task, spawned_node)` → `WorldState`：增量更新
- `export_states()` → `str`：导出全部状态为 JSON

**版本控制**：每次 `update_state` 调用，`version` 自增，`updated_at` 刷新。

---

### 2.5 LobsterNetwork 主网络（`lobster_network.py`，207 行）

**职责**：框架的顶层编排器，聚合 Node、DialogueEngine、EmergenceDetector、WorldStateManager、NodeRegistry。

**构造函数参数**：
- `emergence_threshold`（默认 0.5）
- `heartbeat_timeout`（默认 90 秒）

**核心编排方法**：
- `register_node(node, host, port, ssh_enabled, metadata)` → `(bool, str)`：向注册中心和网络内同时注册
- `deregister_node(node_id, reason)` → `(bool, str)`：注销节点
- `trigger_dialogue(node_a, node_b, trigger)` → `DialogueResult`：触发两节点对话
- `trigger_emergence(node_a, node_b, trigger)` → `Optional[EmergenceEvent]`：对话+涌现检测流水线
- `get_all_states()` / `get_network_stats()` / `health_check()`：状态查询

**节点管理**：内部维护 `nodes: Dict[str, Node]`，节点增删与注册中心双向同步。

**依赖**：`node.py`、`dialogue.py`、`emergence.py`、`world_state.py`、`node_registry.py`。

---

### 2.6 NodeRegistry 注册中心（`node_registry.py`，368 行）

**位置**：`src/lobster_network/node_registry.py`（框架层主包内版本，368 行）  
**附加副本**：`src/lobster_network/network/node_registry.py`（网络层内副本，361 行）

两个版本功能相似，主包版本支持更深度的回调系统（`register/deregister/heartbeat/status_change` 四事件）。

**核心数据结构**：
- `NodeRegistration`：`node_id`、`name`、`node_type`、`host`、`port`、`capabilities`、`status`（active/inactive/dead）、`last_heartbeat`、`version`

**核心功能**：
- `register()` / `deregister()`：节点生命周期管理
- `heartbeat(node_id, metadata)`：心跳更新
- `check_health()`：周期性健康检查，超时 2 倍心跳窗口标记 dead
- `get_active_nodes()` / `get_nodes_by_type()` / `get_nodes_by_capability()`：多维度节点发现
- `on(event, callback)`：事件回调注册
- `start_cleanup()` / `stop_cleanup()`：后台清理线程
- `_persist_registry()` / `_load_registry()`：JSON 文件持久化
- `_parse_iso(s)`：兼容 Python 3.6 的多格式 ISO 时间解析

---

### 2.7 Messenger 消息传递（`communication/` 子包）

> **注意**：独立的 `messenger.py` 文件在当前源码树中不存在。消息传递功能分散在 WebSocket 实现中。

**WebSocket Server** (`websocket_server.py`，373 行)：

| 特性 | 实现 |
|------|------|
| 连接管理 | `connected_nodes: Dict[str, WebSocketServerProtocol]` |
| 消息确认（ACK/NACK) | 通过 `pending_messages` 待确认队列 + `confirmed` 字段 |
| 去重 | `processed_messages: Set[str]` 避免重复处理 |
| 消息签名 | HMAC-SHA256 签名验证 |
| 消息过期 | `ttl` 字段 + `is_expired()` 检查 |
| 重试 | `retry_count` + `max_retries`（默认 3）的指数退避重试 |
| 心跳 | 60s 间隔心跳 + 180s 超时检测 |
| 内存监控 | `memory_monitor()` 512MB 上限保护 |

**WebSocket Client** (`websocket_client.py`，325 行)：

| 特性 | 实现 |
|------|------|
| 自动注册 | 连接后自动发送注册消息（含 capabilities） |
| 自动重连 | `reconnect_monitor()` + 指数退避延迟（max 10 次） |
| 消息签名 | HMAC-SHA256 与服务器对称 |
| 消息去重 | `pending_messages` 字典去重 |
| 消息处理器注册 | `register_handler(msg_type, handler)` |

**消息类型枚举**：`dialogue` / `training` / `heartbeat` / `register` / `confirm`

**多通道现状**：当前仅实现 NFS（文件） + WebSocket，SSH 传输有独立模块但未接入 Messenger。

---

### 2.8 IndraNet 因陀罗网（`network/indra_net.py`，181 行）

**职责**：实现全互联网络拓扑（每个节点自动与所有其他节点建立双向连接）。

**核心概念**：
- `IndraNetNode`：扩展普通 Node，增加 `connections: Set[str]`（邻居集合）、`last_updated` 时间戳
- `IndraNet`：管理全互联拓扑，内部持有一个 `LobsterNetwork` 实例

**自动全互联**：`add_node(node)` 时自动与所有现有节点双向连接。

**碰撞测试**（`alpha_collision_test` 方法）：
- 触发所有节点对之间的对话，模拟全互联的认知碰撞效果
- 对每次碰撞进行涌现检测，统计涌现事件

---

### 2.9 TimeArbitrage 时间套利引擎（`time_arbitrage.py`，769 行）

**职责**：利用节点时间维度上的结构性差异进行套利优化，是框架最核心的创新模块之一。

**五维套利引擎**：

| 套利类型 | 枚举值 | 核心思想 | 实现要点 |
|---------|--------|---------|---------|
| 速率套利 | `SPEED` | 利用不同 Agent 的学习速度差 | 速度档案（Fast/Steady/Practical），动态配对 |
| 错峰套利 | `OFF_PEAK` | 低谷时段（00:00-06:00）高强度计算 | 时间段判断 + 时间价值折扣率 |
| 反思套利 | `REFLECTION` | 遗忘曲线的最佳复习时机 | Ebbinghaus 遗忘曲线建模，最优间隔计算 |
| 复利套利 | `COMPOUND` | 多轮对话的涌现指数增长 | 对话轮次 × 涌现系数，指数增长曲线 |
| 时距套利 | `TEMPORAL` | 知识的时间价值增值 | 时间衰减 + 价值评估 |

**核心数据结构**：
- `ArbitrageOpportunity`：`opportunity_id`、`arbitrage_type`、`participants`、`expected_return`、`time_window`、`confidence`
- `ArbitrageResult`：`actual_return`、`time_cost_seconds`、`dialogues_triggered`

**速度档案（NodeSpeedProfile）**：
- `FAST`：加速型（如诸葛虾，0.5-2s/题，98% 基线）
- `STEADY`：稳健型（1-3s/題，90% 基线）
- `PRACTICAL`：实战型（高准确率，少量题目）

**调度器入口**（`TimeArbitrageScheduler`）：
- `find_opportunities()` → 遍历五种套利类型，按时间窗口和节点档案匹配
- `execute_arbitrage(opportunity)` → 触发对话、记录结果、更新统计

---

### 2.10 各传输通道

| 通道 | 文件 | 行数 | 状态 |
|------|------|------|------|
| WebSocket | `communication/websocket_server.py` + `client.py` | 698 总 | 完整实现 |
| SSH V2 | `network/ssh_channel.py` | 257 | SSHChannelV2：指数退避重连、消息去重、心跳、状态监控 |
| SSH V1 | `network/ssh_channel_v2.py` | 318 | SSHChannel：重试、超时、错误恢复、连接池、ChannelStats |
| NFS/File | — | — | 通过共享文件目录（`/shared/messages`）交换消息 |
| HTTP | — | — | **未实现**（README 架构图中声明但缺失） |
| MQTT | `lobster_mqtt_core.py` + `lobster_mqtt_go_bridge.py` | 956 | MQTT 核心 + 围棋桥接 |

**SSH 通道技术细节**：
- SCP 传输 + JSON 序列化
- 原子写入（.tmp 重命名）
- 指数退避：`reconnect_base^(attempt+1)`，最长 30s
- 连接保活：`ServerAliveInterval=5` + `ServerAliveCountMax=2`
- 去重：`_sent_ids: Set[str]`

---

## 三、运营层解析

### 3.1 Dispatcher 调度器演进

| 版本 | 文件 | 特点 |
|------|------|------|
| V3 | `_archive/go_coach_dispatcher_v3.py` | 基础调度，日间训练 |
| V4 | `_archive/go_coach_dispatcher_v4.py` | 引入难度阶梯和自适应跳题 |
| V6 Nocturnal | `core/dispatcher/go_coach_dispatcher_v6_nocturnal.py` | 深夜特训模式（00:00-06:00） |

**V6 Nocturnal 深夜特训时间表**：

| 时段 | 训练模块 | 强度 |
|------|---------|------|
| 00:00-01:30 | 极限死活（高级，100/120/80题） | 🔥🔥🔥🔥🔥 |
| 01:30-02:30 | AI 定式库导入（Star Point, 3-3 invasion） | 📚📚 |
| 02:30-04:30 | 19 路盘深夜实战（连续 2 盘） | ♟️♟️♟️♟️ |
| 04:30-05:30 | AI 深度复盘 | 🤖🤖🤖 |
| 05:30-06:00 | 归档 & 错题重练 | 📂 |

**学员配置**：
- 小陈（稳健型）：基础题量标准
- 诸葛虾（加速型）：1.2x 题量加成
- qoder（实战型）：中等题量，侧重实战

---

### 3.2 Coach 教练系统（`core/coach/hermes_coach.py`，465 行）

**职责**：分析训练数据，生成完善训练计划，评估学员表现，制定晋升/降级建议。

**核心分析函数**：
- `analyze_xiaochen()` / `analyze_zhuguxia()` / `analyze_qoder()`：逐学员分析
- 统计维度：正确率、错题分类、题型分布、对局胜率

**训练计划生成**：
- 基于学员弱项（错题类型分布）生成针对性训练计划
- 支持难度阶梯（初级→中级→高级）
- 错题本（wrong_book.json）存档与重练

**报告输出**：生成每个学员的综合评估报告（Markdown 格式）

---

### 3.3 Agent 守护进程（`core/agents/`）

- `lobster_agent.py`：基础 Agent 抽象
- `memory_manager.py`：记忆管理
- `paper_agent.py`：论文 Agent（学术论文互评场景）

---

## 四、应用层解析

### 4.1 围棋训练流水线

```
[题库] → [Dispatcher 分配] → [Node 解题] → [评分]
    ↓
[错题本 (wrong_book.json)] → [Hermes Coach 分析] → [针对性训练计划]
    ↓
[对局实战] → [AI 复盘] → [定式库更新]
```

**数据流**：JSON 文件通过 `/shared/training/go/` 共享目录交换，每个学员独立子目录。

### 4.2 海报设计

通过 `activity-materials/gen_ppt.py` 和 `TOP100_book/build_book.py` 等脚本实现，基于节点能力配对进行模板化海报生成。

### 4.3 PPT 制作

- `101-plan/generate_ppt.py`：101 计划 PPT 生成
- `ai-agent-lecture/generate_pptx.py`：AI Agent 讲座 PPT 生成

---

## 五、Assessment 模块现状

> **重要发现**：`src/lobster_network/assessment/` 目录在当前源码树中**不存在**。先前的版本审计报告中提及的 "401 行评估引擎 + 255 行 Clawvard 桥接代码" 在本次全面扫描中未找到对应源码文件。

**存疑**：相关概念在 `clawvard-experiment-guide.md` 和 `clawvard-token.md` 中有文档说明，但代码实现缺失。可能是：
1. 曾存在但在某次清理中被移除
2. 文档先行、代码尚未落地的规划功能

**Clawvard 桥接文档**（`clawvard-experiment-guide.md`）：描述了跨框架实验的评估方案，但无对应的 Python 模块。

**建议**：将 Assessment 相关能力列入 P1/P2 开发计划，而非 P0 导出修复。

---

## 六、协议层

### 6.1 OADP（Open Agent Dialogue Protocol）

**文件**：`core/network/a2a_protocol.py`

Agent-to-Agent 通信协议，定义了节点间对话的消息格式、路由规则和会话状态机。

### 6.2 DRP（Distributed Recruitment Protocol）

分布式中继协议，用于节点发现和能力广播。

### 6.3 WorldMap

全局世界状态快照协议，用于节点间的状态同步。

### 6.4 SoulSchema / MemorySchema

- **SoulSchema**：Node 认知种子（seed）的标准化序列化格式
- **MemorySchema**：节点记忆的三层存储结构（短期/工作/长期）

### 6.5 Portal

跨网络入口网关协议（`ard_gateway.py`，483 行），实现 ARD（Agent Routing & Discovery）网关。

---

## 七、经济与治理层

| 模块 | 文件 | 行数 | 功能 |
|------|------|------|------|
| TokenEconomy | `token_economy.py` | 539 | 代币经济学：Transaction / Block / Wallet |
| SmartContract | `smart_contract.py` | 499 | 智能合约系统：ContractCondition |
| DEX | `dex.py` | 449 | 去中心化交易所 |
| LiquidityMining | `liquidity_mining.py` | 438 | 流动性挖矿 |
| DAOGovernance | `dao_governance.py` | 526 | DAO 治理：投票、提案、执行 |
| Layer2 | `layer2.py` | 415 | Layer 2 扩容方案 |
| CrossChain | `cross_chain.py` | 385 | 跨链桥：LiquidityPool / BridgeNode |
| CrossChainBridge | `cross_chain_bridge.py` | 428 | 跨链桥增强版 |
| MultiCurrency | `multi_currency.py` | 369 | 多币种钱包 |
| ZKProof | `zk_proof.py` | 356 | 零知识证明 |
| Trading | `trading.py` | 581 | 交易系统：Task / Product / Order |
| ARD Protocol | `ard_protocol.py` | 588 | Agent 路由发现协议 |
| ARD Security | `ard_security.py` | 538 | ARD 安全层 |

---

## 八、模块依赖关系图

```
LobsterNetwork
├── Node
├── DialogueEngine ──────── Node
├── EmergenceDetector ───── DialogueEngine
├── WorldStateManager ───── Node
├── NodeRegistry
├── TimeArbitrage ───────── Node, DialogueEngine
│
├── network/
│   ├── IndraNet ────────── LobsterNetwork, Node
│   ├── SSHChannel ──────── message_protocol
│   ├── SSHChannelV2 ────── message_protocol
│   └── __init__.py (空)
│
├── communication/
│   ├── WebSocketServer
│   └── WebSocketClient
│
├── utils/
│   ├── config.py
│   ├── logger.py
│   ├── message_protocol.py
│   └── message_protocol_v2.py
│
└── [经济层模块]
    ├── token_economy.py
    ├── smart_contract.py
    ├── cross_chain.py
    └── ... (其余 8 个模块)
```

---

## 九、工程统计数据

| 指标 | 数值 |
|------|------|
| 源码总行数 | 10302 行（主包 .py） |
| 核心框架模块 | 5 个（Node / Dialogue / Emergence / WorldState / LobsterNetwork） |
| 网络传输模块 | 5 个（WebSocket Server+Client / SSH×2 / IndraNet） |
| 经济治理模块 | 13 个（Token / Contract / DEX / CrossChain 等） |
| 子包数量 | 4 个（communication / network / utils + 主包目录） |
| 空文件 | `network/__init__.py`（0 字节） |
| 占位文件 | 3 个（global_scheduler.py / message_queue.py / rate_limiter.py，位于嵌套目录） |

---

## 十、关键设计洞察

1. **涌现驱动的认知架构**：框架以"认知碰撞 → 涌现检测 → 宝藏解锁"为核心闭环，将对话质量量化为涌现值（0-1），高于阈值触发宝藏。

2. **时间维度的创新**：TimeArbitrage 五维套利引擎是框架最独特的模块，将金融套利思想引入多智能体训练调度。

3. **经济层的完整性**：TokenEconomy → SmartContract → DEX → DAO 形成闭环的经济激励系统，但与应用层的集成度尚浅。

4. **传输层的碎片化**：WebSocket、SSH、NFS 各自独立实现，缺少统一的 Messenger 抽象层做多通道调度。

5. **SSH 双版本共存**：`ssh_channel.py`（SSHChannelV2）和 `ssh_channel_v2.py`（SSHChannel）命名混乱，功能重叠。

6. **占位文件的嵌套目录**：部分占位文件在 `lobster-network/lobster-network/src/lobster_network/` 嵌套路径下，与预期目录 `lobster-network/src/lobster_network/` 不一致。
