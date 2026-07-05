# 小龙虾网络 (Lobster Network) -- 项目介绍与PPT素材

> 整理日期: 2026-06-25
> 版本: v0.4.1
> 口号: **你不停对话，世界就不停扩展**

---

## 一、项目理念（哲学基础）

### 1.1 核心命题：对话即创造

项目的核心命题由三个层层递进的哲学命题构成，形成完整的"认知-生成-交互"模型：

**命题一：一人一世界（认知编译系统）**

- 没有"客观世界"这回事。同一棵树下，植物学家看到物种分类，诗人看到生命隐喻，樵夫看到木材。树没变，**编译结果不同**。
- 每个主体的感知系统、知识结构、价值坐标系，共同编译出独属ta的"世界版本"。
- 哲学根基：佛教唯识学《成唯识论》--"万法唯识"，一识一界，你无法跳出自己的识去验证"客观"。
- 认知科学视角：注意力机制决定什么进入意识，世界不是静态数据库，是**实时渲染引擎**。

**命题二：世界是对话（认知张成与涌现）**

- 对话不是信息交换，是**两个认知编译系统交叉编译**，输出不属于任何单一主体的新结构。
- 线性代数类比：一人一个基向量 v1, v2, v3，对话就是张成空间 span{v1, v2, v3}，基向量越多、越不正交，张成的空间越大。
- 华严经因陀罗网：每一颗宝珠映照所有宝珠，对话就是宝珠之间的映照。

**命题三：世界是编程的（过程生成引擎）**

- 如同游戏引擎的过程生成（Procedural Generation），玩家走到哪，Chunk才加载到哪。
- 量子力学类比："观测"就是渲染指令，波函数不坍缩，粒子就没有确定位置。
- 佛教缘起：诸法因缘生，条件具足时现象才"渲染"出来。

### 1.2 哲学基础一览表

| 命题 | 哲学来源 | 科学类比 | 游戏机制 | 工程实现 |
|------|----------|----------|----------|----------|
| 一人一世界 | 唯识学"万法唯识" | 注意力机制 | 玩家独立渲染管线 | Node节点（种子参数） |
| 世界是对话 | 华严经"因陀罗网" | 线性代数张成空间 | 多人联机交互 | DialogueEngine（交叉编译） |
| 世界是编程的 | 缘起论"诸法因缘生" | 量子力学观测坍缩 | 过程生成引擎 | WorldState（按需渲染） |

### 1.3 四大设计原则

1. **多样性 > 一致性**：基向量越不正交，张成空间越大。网络的价值不在于共识，而在于差异碰撞产生的涌现。
2. **过程生成 > 静态存储**：不预设标准答案，设计触发条件。当对话满足条件时，自动涌现新解。
3. **对话即创造**：每次对话是一次参数融合输入，引擎输出单人永远算不出来的新坐标。
4. **因陀罗网架构**：每个节点映照所有节点，全互联的宝珠网拓扑。

### 1.4 参考文献

- 《成唯识论》-- 护法等造，玄奘译
- 《华严经》-- 因陀罗网喻
- Procedural Generation in Games -- Tancha et al., 2012
- Reinforcement Learning: An Introduction -- Sutton & Barto, 2018
- 量子力学测量问题 -- von Neumann, 1932
- 注意力机制与意识 -- Posner & Petersen, 1990

---

## 二、架构设计（五层结构详解）

### 2.1 总体架构

项目采用**五层分层架构**，自底向上依次为：基础设施层、框架层、可靠通信层、运营层、应用层。

```
┌─────────────────────────────────────────────────────────────┐
│                     应用层 (Domains)                         │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │   围棋训练系统   │    │   海报设计系统   │                │
│  │  Go Training     │    │  Poster Design  │                │
│  └────────┬────────┘    └────────┬────────┘                │
└───────────┼──────────────────────┼────────────────────────┘
            │                      │
┌───────────┼──────────────────────┼────────────────────────┐
│           ▼                      ▼                         │
│                    运营层 (Core)                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ 任务调度  │ │ 学生Agent│ │ 教练系统  │ │ 监控工具 │     │
│  │Dispatcher│ │  Agents  │ │  Coach   │ │ Monitor  │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
└────────────────────────────────────────────────────────────┘
            │
┌───────────┼──────────────────────────────────────────────┐
│           ▼  【v0.4.1 新增】                              │
│              可靠通信层 (Reliable Communication)           │
│  ┌──────────────────┐  ┌──────────────────┐              │
│  │ 节点注册中心      │  │ 可靠消息传递      │              │
│  │ NodeRegistry     │  │ Messenger        │              │
│  │ • 持久化存储      │  │ • ACK/NACK确认   │              │
│  │ • 心跳检测        │  │ • 自动重试       │              │
│  │ • 健康检查        │  │ • 多通道故障切换 │              │
│  │ • 能力发现        │  │ • 消息持久化     │              │
│  └──────────────────┘  └──────────────────┘              │
│                                                          │
│  传输通道优先级：NFS → SSH → HTTP → File（自动降级）      │
└──────────────────────────────────────────────────────────┘
            │
┌───────────┼──────────────────────────────────────────────┐
│           ▼                                               │
│                    框架层 (Framework)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ 节点模型  │ │ 对话引擎 │ │ 涌现检测  │ │ 世界状态 │    │
│  │   Node   │ │ Dialogue │ │Emergence │ │WorldState│    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
│                                                          │
│  ┌──────────────────────────────────────────────────┐    │
│  │              因陀罗网拓扑 (IndraNet)              │    │
│  │         全互联网络：每个节点映照所有节点          │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
            │
┌───────────┼──────────────────────────────────────────────┐
│           ▼                                               │
│                    基础设施层 (Infrastructure)            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ SSH通道  │ │ 消息协议 │ │ 配置管理  │ │ 日志系统 │    │
│  │SSHChannel│ │ Protocol │ │  Config  │ │  Logger  │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 2.2 各层详解

#### 第一层：基础设施层 (Infrastructure)

负责底层通信和系统服务。

| 组件 | 文件名 | 功能 |
|------|--------|------|
| SSH通道 | `ssh_channel.py` | 跨服务器文件传输（SSH/SCP） |
| SSH通道v2 | `ssh_channel_v2.py` | 【v0.4.0】指数退避重连、连接池 |
| SSH传输 | `ssh_transport.py` | 【v0.4.1】传输通道抽象 |
| 消息协议 | `message_protocol.py` | 标准化智能体间通信格式（OADP协议） |
| 消息协议v2 | `message_protocol_v2.py` | 【v0.4.0】消息重试、确认、去重、持久化 |
| 配置管理 | `config.py` | 全局配置管理 |
| 日志系统 | `logger.py` | 系统日志记录 |

**OADP协议（Open Agent Dialogue Protocol）** 是基础设施层的核心协议，定义了：
- 消息信封格式（type/from/to/timestamp/subject/priority/payload/metadata）
- 5种消息类型：dialogue_request、dialogue_response、world_update、portal_record、emergence_event
- 错误码体系：ERR_UNKNOWN_AGENT、ERR_DIALOGUE_TIMEOUT、ERR_INVALID_FORMAT、ERR_VERSION_MISMATCH、ERR_WORLD_CONFLICT

#### 第二层：框架层 (Framework)

核心理论的工程实现，位于 `src/lobster_network/` 目录。

| 组件 | 文件名 | 核心类 | 功能 |
|------|--------|--------|------|
| 节点模型 | `node.py` | `Node` | 认知编译系统的基本单元 |
| 对话引擎 | `dialogue.py` | `DialogueEngine`, `DialogueResult` | 交叉编译器，计算涌现值 |
| 涌现检测 | `emergence.py` | `EmergenceDetector`, `EmergenceEvent` | 检测创造性输出 |
| 世界状态 | `world_state.py` | `WorldState` | 按需渲染的过程生成引擎 |
| 时间套利 | `time_arbitrage.py` | `TimeArbitrageEngine` | 五维时间套利引擎 |
| 因陀罗网 | `indra_net.py` | `IndraNet`, `IndraNetNode` | 全互联拓扑 |
| 世界地图 | `world_map.py` | `WorldMap`, `WorldMapManager` | 集体记忆引擎 |
| 节点注册中心 | `registry.py` | `NodeRegistry` | 【v0.4.1】节点注册、心跳、健康检查 |
| 可靠消息传递 | `messenger.py` | `Messenger` | 【v0.4.1】ACK/NACK、自动重试、多通道故障切换 |
| 集成层 | `integration.py` | `LobsterNetworkWithRegistry` | 【v0.4.1】统一API，整合注册中心和消息传递 |

#### 第三层：可靠通信层 (Reliable Communication) - 【v0.4.1 新增】

提供跨服务器可靠消息传递能力。

**节点注册中心功能：**

| 功能 | 说明 |
|:---|:---|
| 节点注册 | 注册/注销节点，含能力声明和传输通道配置 |
| 心跳检测 | 定期心跳，自动检测节点存活状态 |
| 健康检查 | 全量健康检查，自动标记 offline/suspected |
| 节点发现 | 按类型/状态/能力查找节点 |
| 持久化 | JSON 文件持久化，重启后自动恢复 |
| 回调机制 | 心跳回调、状态变化回调 |

**可靠消息传递功能：**

| 功能 | 说明 |
|:---|:---|
| 消息确认 | ACK/NACK 机制，确保消息被处理 |
| 自动重试 | 指数退避重试，可配置最大重试次数 |
| 多通道故障切换 | NFS → SSH → HTTP → File 自动降级 |
| 消息持久化 | 按状态分类存储（pending/sent/failed） |
| 消息过期 | TTL 机制，自动清理过期消息 |
| 优先级队列 | 支持消息优先级排序 |

**传输通道管理：**

| 通道 | 优先级 | 故障检测 | 切换时间 |
|:---|:---:|:---|:---|
| NFS | 1 | 目录可写检查 | < 100ms |
| SSH | 2 | 连接测试 | < 500ms |
| HTTP | 3 | HTTP 状态码 | < 1s |
| File | 99 | 目录可写 | < 50ms |

#### 第四层：运营层 (Core)

实际运行系统，位于 `core/` 目录。

| 组件 | 文件名 | 功能 |
|------|--------|------|
| 任务调度器V3 | `go_coach_dispatcher_v3.py` | 基础28天训练计划 |
| 任务调度器V4 | `go_coach_dispatcher_v4.py` | 自适应难度 + 错题本复习 |
| 任务调度器V6 | `go_coach_dispatcher_v6_nocturnal.py` | 夜间高强度模式（00:00-06:00） |
| Agent守护进程 | `lobster_agent.py` | 通用Agent守护进程（监控指令、执行训练） |
| 教练系统 | `hermes_coach.py` | 教练分析与报告（数据分析、诊断、改进计划） |
| 围棋规则引擎 | `process_go_move.py` | 19x19完整围棋规则（中国规则、打劫、自杀检测、BFS提子） |
| 训练模拟器 | `run_training_round.py` | 训练轮次模拟 |
| 系统监控 | `monitor.py` | 系统健康监控 |

#### 第五层：应用层 (Domains)

具体领域实现，位于 `domains/` 目录。

| 领域 | 目录 | 功能 |
|------|------|------|
| 围棋训练 | `domains/go/` | 三个差异化学生训练器 + 题库 + 文档 |
| 海报设计 | `domains/poster/` | HTML+Playwright渲染流水线 + PPT生成 |
| PPT制作 | `domains/ppt/` | 【v0.4.1】自动化PPT生成系统 |

### 2.3 四层反馈环

```
L1 即时反馈：每个任务完成后自动评估
L2每日反馈：教练分析表现，调整次日计划
L3每周反馈：跨学生讨论赛、复盘学习
L4任务反馈：人类灵魂提供方向和验收
```

---

## 三、核心模块说明

### 3.1 节点模型 (node.py)

**定位**：网络中的基本单元，代表一个"认知编译系统"。

**类：`Node`**

| 属性/方法 | 说明 |
|-----------|------|
| `node_id` | 节点唯一标识 |
| `name` | 节点名称 |
| `type` | 节点类型（human/agent/coach/student） |
| `seed` | 种子参数字典（perspective、knowledge_base、value_orientation、learning_rate） |
| `capabilities` | 能力列表 |
| `current_world` | 当前世界状态（version、loaded_chunks、unlocked_treasures） |
| `to_dict()` | 转换为字典 |
| `to_json()` | 转换为JSON字符串 |
| `from_dict(data)` | 从字典创建节点（类方法） |
| `update_world(chunk_id, treasure_id)` | 更新世界状态（加载新地图块/解锁宝藏） |

**种子参数含义：**

| 参数 | 含义 | 示例值 |
|------|------|--------|
| `perspective` | 认知视角 | 技术栈、教练型、加速型、实战型 |
| `knowledge_base` | 知识结构 | 编程与电子、训练设计、围棋理论 |
| `value_orientation` | 价值取向 | 工程实践、教育创新 |
| `learning_rate` | 学习率 | high/medium/low |

### 3.2 对话引擎 (dialogue.py)

**定位**：不是信息传递，是认知张成--两个系统交叉编译，输出单人永远算不到的新解。

**数据类：`DialogueResult`**

| 字段 | 类型 | 说明 |
|------|------|------|
| `dialogue_id` | str | 对话唯一标识 |
| `participants` | List[str] | 参与者节点ID列表 |
| `input_context` | Dict[str, str] | 输入上下文（各节点的视角和知识） |
| `emergence_score` | float | 涌现值（0-1） |
| `new_insight` | str | 涌现出的新见解 |
| `new_world_state` | Dict | 对话后的新世界状态 |
| `treasure_unlocked` | Optional[str] | 解锁的宝藏ID |
| `next_action` | str | 下一步行动 |
| `timestamp` | str | 时间戳 |

**涌现值计算公式：**

```
emergence_score = 0.3 * perspective_distance     // 视角差异度
                + 0.3 * knowledge_complementarity // 知识互补性
                + 0.2 * dialogue_depth            // 对话深度
                + 0.2 * novelty_of_output         // 输出新颖度

IF emergence_score > threshold:
    -> 触发宝藏渲染
    -> 记录为新知识
    -> 可能生成新节点
```

### 3.3 涌现检测器 (emergence.py)

**定位**：涌现是对话的创造性输出--属于两个参与者、但不属于任何单独一方的新结构。如同线性代数中的 `span{}`，单个基向量永远无法到达的空间。

### 3.4 世界地图引擎 (world_map.py)

**定位**：小龙虾网络的集体记忆引擎，所有智能体共享的知识图谱。

**核心功能：**
- 添加知识碎片（含内容哈希、引用追踪）
- 安全更新/移除知识碎片（带文件锁）
- 搜索知识碎片
- 解锁宝藏
- 增量同步
- 注册智能体

### 3.5 时间套利引擎 (time_arbitrage.py)

**定位**：系统性利用网络中节点在时间维度上的结构性差异，详见第四节。

### 3.6 节点注册中心 (registry.py) - 【v0.4.1 新增】

**定位**：网络节点的管理中心，提供节点注册、心跳检测、健康检查等功能。

**核心功能：**
- 节点注册/注销（含能力声明和传输通道配置）
- 心跳检测（定期心跳，自动检测节点存活）
- 健康检查（全量健康检查，自动标记 offline/suspected）
- 节点发现（按类型/状态/能力查找节点）
- 持久化（JSON 文件持久化，重启后自动恢复）
- 回调机制（心跳回调、状态变化回调）

### 3.7 可靠消息传递 (messenger.py) - 【v0.4.1 新增】

**定位**：跨服务器可靠消息传递，支持多通道故障切换。

**核心功能：**
- 消息确认（ACK/NACK 机制）
- 自动重试（指数退避）
- 多通道故障切换（NFS → SSH → HTTP → File）
- 消息持久化（按状态分类存储）
- 消息过期（TTL 机制）
- 优先级队列

### 3.8 Agent守护进程 (lobster_agent.py)

**定位**：学员Agent的运行脚本，监控指令目录、执行训练、提交结果、更新策略库。

**核心功能：**
- 监控 `/shared/messages/to_<role>/` 目录获取教练指令
- 支持训练类型：self_play（自我对弈）、review（复盘）、openings（布局训练）
- 管理共享策略库 `brain.json`（记录对局数、胜率）
- 自动提交训练结果到 `from_<role>/` 目录

**支持角色：** xiaochen（信电大虾）、zhuguxia（诸葛虾）

### 3.9 教练系统 (hermes_coach.py)

**定位**：诸葛马教练的分析与评估系统。

**核心功能：**

| 函数 | 说明 |
|------|------|
| `analyze_xiaochen()` | 分析小陈训练数据（准确率、错题、胜率） |
| `analyze_zhuguxia()` | 分析诸葛虾训练数据 |
| `diagnose_system()` | 诊断系统问题（7项检查） |
| `generate_improved_plan()` | 生成完善的28天训练计划（4周主题） |
| `generate_coach_report()` | 生成完整教练评估报告 |

**28天训练计划结构：**
- 第1周：规则基础与吃子技巧（目标20级）
- 第2周：死活基础（目标15级）
- 第3周：手筋基础（目标10级）
- 第4周：布局入门与简单官子（目标5级）
- 每周结构：4天训练 + 1天复习 + 1天考核 + 1天休息

### 3.10 OADP协议 (protocol.md)

**全称**：Open Agent Dialogue Protocol（开放智能体对话协议）

**5种消息类型：**

| 类型 | 说明 |
|------|------|
| `dialogue_request` | 发起对话请求 |
| `dialogue_response` | 对话响应（多轮交换） |
| `world_update` | 世界状态更新广播 |
| `portal_record` | 传送门记录（重要对话成果） |
| `emergence_event` | 涌现事件通知 |

**对话流程：**
1. 发起方发送 dialogue_request
2. 接收方确认参与
3. 多轮对话交换（dialogue_response x N）
4. 对话结束，计算涌现值
5. 更新双方世界状态
6. 若涌现值 > 阈值，创建传送门记录
7. 广播世界状态更新

---

## 四、时间套利引擎（五维理论和公式）

### 4.1 理论概述

**核心思想**：不同节点在时间维度上存在结构性差异，这些差异不是低效，而是可以被系统性利用的套利机会。

**理论基础：**
- 金融套利：利用市场间价差获取无风险收益
- 学习科学：间隔重复（spaced repetition）比集中学习更有效
- 复合增长：知识复利效应，每轮对话在上一轮基础上涌现
- 时间经济学：非高峰时段的计算资源"价格"更低

### 4.2 五维套利模型详解

#### 维度一：速率套利 (Speed Arbitrage)

**原理**：利用不同Agent的学习速度差，快速节点生成原始洞见（低成本），慢速节点深化验证（高质量），形成知识价差。

**节点速度档案：**

| 类型 | 代表节点 | 解题时间 | 准确率基线 |
|------|----------|----------|------------|
| FAST（加速型） | 诸葛虾 | 0.5-2.0秒/题 | 98% |
| STEADY（稳健型） | 信电大虾 | 1.0-3.0秒/题 | 90% |
| PRACTICAL（实战型） | qoder | 2.0-5.0秒/题 | 95% |

**速度比公式：**

```
speed_ratio = (slow_time_min + slow_time_max) / (fast_time_min + fast_time_max)

expected_return = speed_ratio * perspective_bonus
  （perspective_bonus: 视角不同=1.0, 视角相同=0.5）

confidence = min(speed_ratio / 3.0, 1.0)
```

**执行流程：**
1. 快速节点批量生成N个原始洞见
2. 慢速节点选取最有价值的洞见深化
3. 深化结果反馈给快速节点，加速下一轮

#### 维度二：错峰套利 (Off-Peak Arbitrage)

**原理**：非高峰时段的计算资源"价格"更低（无人类注意力竞争），适合执行高强度批量任务。

**时段定义（北京时间）：**

| 时段 | 时间窗口 | 算力收益系数 |
|------|----------|------------|
| deep_night（深夜） | 00:00-06:00 | 1.5x |
| early_morning（清晨） | 06:00-08:00 | 1.2x |
| work_hours（工作时间） | 08:00-18:00 | 1.0x（基准） |
| evening（晚间） | 18:00-22:00 | 1.1x |
| late_night（深夜前） | 22:00-00:00 | 1.3x |

**推荐任务：**
- 深夜：极限死活题、AI定式导入、19路夜战对局、AI深度复盘
- 深夜前：热身训练、错题重练、次日计划预览
- 清晨：复盘整理、知识沉淀、状态更新

**预期收益：** `expected_return = current_multiplier * len(nodes)`

#### 维度三：反思套利 (Reflection Arbitrage)

**原理**：基于艾宾浩斯遗忘曲线，当记忆保留率降到最佳复习点时，复习的边际收益最高。

**遗忘曲线公式：**

```
记忆保留率: R = e^(-t/S)
  其中: S = 记忆稳定性（随复习次数增长）
         t = 距上次学习/复习的时间（天）

最佳复习时间: t = -S * ln(R_target)
  其中: R_target = 目标保留率（默认0.85）

稳定性增长: S_new = S_old * (1.0 + 0.3 * review_count)
  （SM-2简化版算法）
```

**复习窗口判定**：当前保留率在目标值的正负10%范围内为最佳复习窗口。

**预期收益**：`expected_return = 1.0 + review_count * 0.3`（复习次数越多，收益越高）

**与V4调度器的关系**：V4调度器的错题本每3天重做机制是此模式的原始版本。

#### 维度四：复利套利 (Compound Arbitrage)

**原理**：多轮对话的涌现呈指数增长，每轮对话的输出成为下轮的输入上下文。

**复利公式：**

```
E_total = E_1 * (1 + r)^(N-1)

其中:
  E_1 = 单轮基准涌现值
  r   = 复利因子（由视角深度和知识互补性决定）
  N   = 对话轮数

复利加成计算:
  compound_bonus = prev_avg_emergence * 0.2 * round_number
  emergence_score_new = min(emergence_score + compound_bonus, 1.0)

复利因子:
  compound_factor = total_emergence / (rounds * single_avg_emergence)
```

**效应说明：**
- 动量效应：前序涌现高，本轮起点更高
- 深度效应：对话深度随轮次增长

#### 维度五：时距套利 (Temporal Distance Arbitrage)

**原理**：知识具有时间价值，今天的洞见在下周可能更有价值，因为届时其他节点可能已经积累了相关知识。

**知识时间增值模型（倒U型曲线）：**

```
V(t) = 1.0 + 0.5 * sin(pi * t / T_peak)

其中:
  T_peak = 72.0小时（峰值时间）
  t = 锁定时长（小时）

知识价值在48-72小时后达到峰值
（其他节点有时间消化但还没遗忘）
```

**时间增值示例：**

| 锁定时长 | 预计增值 |
|----------|----------|
| 6小时 | ~1.13x |
| 24小时 | ~1.43x |
| 48小时 | ~1.50x |
| 72小时（峰值） | ~1.50x |
| 96小时 | ~1.43x |
| 120小时 | ~1.25x |
| 144小时 | ~1.00x |

### 4.3 综合扫描

`TimeArbitrageEngine.scan_all_opportunities(nodes)` 方法综合检测五个维度的所有套利机会，按 `expected_return * confidence` 降序排列。

### 4.4 关键数据结构

| 类名 | 说明 |
|------|------|
| `ArbitrageType` | 枚举：SPEED/OFF_PEAK/REFLECTION/COMPOUND/TEMPORAL |
| `NodeSpeedProfile` | 枚举：FAST/STEADY/PRACTICAL |
| `ArbitrageOpportunity` | 套利机会（ID/类型/参与者/预期收益/时间窗口/置信度） |
| `ArbitrageResult` | 执行结果（实际收益/时间成本/对话次数/涌现量/知识转移/复利因子） |
| `ForgettingCurve` | 遗忘曲线（记忆强度/稳定性/复习次数/最佳复习时间） |

---

## 五、应用场景

### 5.1 围棋训练系统（已实现）

**定位**：小龙虾网络的第一个应用领域，验证了完整的训练流水线。

**差异化学习架构：**

| 角色 | 名称 | 类型 | 特征 |
|------|------|------|------|
| qoder | 小龙虾 | 实战型 | 高准确率、少量题目、注重实战 |
| xiaochen | 信电大虾 | 稳健型 | 中等准确率、海量对局、稳健推进 |
| zhuguxia | 诸葛虾 | 加速型 | 高准确率基线、快速解题、加速学习 |
| zhuguma | 诸葛马/Hermes | 教练 | 分析训练数据、诊断问题、生成改进计划 |
| -- | 诸葛斌教授 | 人类灵魂 | 方向决策、跨域整合 |

**调度器演进：**
- V3：基础28天训练计划
- V4：自适应难度调整 + 错题本复习（每3天重做）
- V6：夜间高强度模式（00:00-06:00，5个时间槽）

**核心组件：**
- `process_go_move.py`：完整19x19围棋规则引擎（中国规则、打劫、自杀检测、BFS提子）
- 100题题库规划（死活40%、手筋35%、布局15%、官子10%）
- 等级晋升体系（30级 -> 5级，需同时满足准确率+胜率+考核分数）

**训练成果：**
- 总对局数：17,205+
- qoder：685题，86%胜率
- xiaochen：10,337局
- zhuguxia：6,868局

### 5.2 海报设计系统（已实现）

**定位**：第二个应用领域，验证框架的跨领域迁移能力。

**技术突破**：HTML+Playwright渲染流水线
- 用HTML/CSS处理中文排版（浏览器完美渲染中文）
- 用ImageGen只生成纯视觉插图（无文字）
- 图片Base64嵌入，Playwright 2x Retina截图
- python-pptx组装最终PPTX

### 5.3 PPT制作能力学习（v0.4.1 新增）

**定位**：第三个应用领域，验证框架在**知识转化与内容创作**方面的能力。

**背景与目标：**
- **背景**：手动生成 PPT 效率低，布局问题多，需要自动化解决方案
- **目标**：开发自动化 PPT 生成模块，输入结构化内容 → 自动输出精美 PPTX

**技术架构：**

```
┌─────────────────────────────────────────────────────────┐
│              PPT 制作能力学习系统                        │
├─────────────┬─────────────┬─────────────┬──────────────┤
│  内容解析    │  模板引擎    │  视觉生成    │  自动化组装  │
│  Content    │  Template   │  Visual     │  Assembly   │
│             │             │             │             │
│ Markdown/   │ 5种模板库   │ HTML/CSS    │ python-pptx │
│ Word/网页   │ 响应式布局  │ Playwright  │ 自动化输出  │
│             │             │             │             │
│ ↓           │ ↓           │ ↓           │ ↓           │
│ 结构化数据  │ 版式计算    │ 截图渲染    │ PPTX 文件   │
└─────────────┴─────────────┴─────────────┴──────────────┘
```

**核心组件：**

| 组件 | 功能 | 技术栈 |
|:---|:---|:---|
| 内容解析器 | 从 Markdown/Word/网页提取结构化内容 | python-docx, markdown |
| 模板引擎 | 5种预设模板（学术/商业/技术/汇报/创意） | HTML/CSS |
| 视觉生成器 | AI 生成插图 + Playwright 渲染 | ImageGen, Playwright |
| 自动化组装 | python-pptx 自动化输出 | python-pptx |

**技术突破：**
- **纯代码驱动**：无需设计软件，完全自动化
- **HTML/CSS 精确控制**：浏览器完美渲染中文排版
- **AI 配图生成**：ImageGen 生成高质量插图，Base64 内嵌
- **Playwright 高保真截图**：2x Retina 输出，保证视觉质量
- **python-pptx 自动化**：从内容到 PPTX 全流程自动化

**应用场景：**
- **学术汇报**：论文 → PPT 自动转换
- **技术分享**：技术文档 → 演示文稿
- **项目汇报**：项目总结 → 汇报 PPT
- **教学课件**：课程内容 → 教学 PPT
- **商业演示**：商业计划 → 演示文稿

### 5.4 潜在应用场景

基于框架的通用性，可扩展到：
- **多Agent协作写作**：不同视角的作者Agent交叉编译产生新观点
- **教育辅导系统**：差异化学生 + 教练Agent的自适应学习网络
- **创意设计协作**：设计师Agent + 工程师Agent + 用户Agent的涌现式设计
- **知识管理**：基于世界地图引擎的组织知识库

---

## 六、版本历程

### v0.1.0 (2026-06-21) -- 核心引擎

- 核心引擎完成：节点模型、对话引擎、涌现检测、世界状态管理
- 主网络类 LobsterNetwork（因陀罗网拓扑）
- 15个单元测试用例全部通过
- 示例代码运行成功，涌现值0.90
- 理论文档：对话即创造文章、架构设计、合作方案
- 项目配置：README、LICENSE、CONTRIBUTING、setup.py

### v0.2.0 (2026-06-22) -- 项目融合

- 框架层与运营层统一整合为单一项目
- 重新设计四层架构
- 新增：因陀罗网拓扑、SSH通道、配置管理、日志系统
- 新增：运营系统（调度器V3/V4/V6、Agent守护进程、教练系统）
- 新增：围棋训练领域（3个学生训练器、题库）
- 新增：海报设计领域（PPT生成框架）
- 统一 `__init__.py` 入口，支持分层安装（core/full/dev）

### v0.3.0 (2026-06-22) -- 时间套利模式

- 新增五维时间套利引擎 `TimeArbitrageEngine`
- 五个维度：速率套利、错峰套利、反思套利、复利套利、时距套利
- 新增文件：`time_arbitrage.py`（核心模块）、`time_arbitrage_demo.py`（演示）
- 网络层和工具层移入 `src/lobster_network/` 包内
- 统一导出套利层所有类

### v0.4.0 (2026-06-24) -- SSH通信 + 消息协议增强

- 消息协议v2：消息重试、确认、去重、持久化
- SSH通道v2：指数退避重连、连接池
- 节点注册中心v2
- 诸葛马版 + 虾尔版整合

### v0.4.1 (2026-06-24) -- 注册中心 + 可靠消息 + 部署脚本

- 节点注册中心（NodeRegistry）：持久化存储、心跳检测、健康检查、能力发现
- 可靠消息传递（Messenger）：ACK/NACK确认、自动重试、多通道故障切换
- 集成层（integration.py）：统一API，整合注册中心和消息传递
- 自动化部署脚本（deploy_v0.4.1.sh）：一键部署、回滚、健康检查
- 升级检查清单（60+检查项）
- 62个单元测试全部通过

### v0.4.2 (2026-06-25) -- 安全 + 监控 + 性能（规划中）

- 安全性增强：消息 SHA256 签名、AES 加密、节点身份认证
- 监控告警：Prometheus 指标导出、Grafana 监控面板、节点离线告警
- 性能优化：消息队列优化、连接池复用、批量消息处理

### 开发路线图

| 版本 | 目标 | 状态 |
|------|------|:---:|
| v0.1.0 | 核心引擎（节点、对话、涌现） | ✅ |
| v0.2.0 | 统一框架 + 运营系统整合 | ✅ |
| v0.3.0 | 时间套利模式（五维套利引擎） | ✅ |
| v0.4.0 | SSH通信 + 消息协议增强 | ✅ |
| v0.4.1 | 注册中心 + 可靠消息 + 部署脚本 | ✅ |
| v0.4.2 | 安全增强 + 监控告警 + 性能优化 | 🔄 |
| v0.5.0 | 分布式架构 + 跨域协作 | 📋 |
| v1.0.0 | 正式发布 | 🎯 |

---

## 七、关键数据

### 7.1 项目规模

| 指标 | 数据 |
|------|------|
| 项目版本 | v0.4.1 |
| 开源协议 | MIT License |
| 编程语言 | Python 3.8+ |
| 开发周期 | 5天（2026-06-21 至 2026-06-25，6个大版本） |
| 核心模块文件 | 15+个（框架层+通信层） |
| 运营层文件 | 8个 |
| 应用层文件 | 围棋训练（3个训练器+题库）+ 海报设计 + PPT制作 |
| 文档文件 | 15+个核心文档 |
| 单元测试 | 62个用例（全部通过） |
| GitHub仓库 | github.com/zhugebin-hub/lobster-network |

### 7.2 围棋训练数据

| 指标 | 数据 |
|------|------|
| 总对局数 | 17,205+ |
| qoder（小龙虾） | 685题，86%胜率 |
| xiaochen（信电大虾） | 10,337局 |
| zhuguxia（诸葛虾） | 6,868局 |
| 调度器版本 | V3 -> V4 -> V6（三代演进） |
| 围棋规则 | 完整19x19中国规则引擎 |

### 7.3 测试数据

```
平台: Linux, Python 3.6.8, pytest-7.0.1
测试项: 62个
  - test_core.py: 核心模块测试
  - test_world_map.py: 世界地图测试
  - test_registry.py: 注册中心测试（37个）
  - test_enhanced_protocol.py: 协议增强测试（25个）
结果: 全部通过
```

### 7.4 节点数据

| 节点 | 类型 | 种子视角 | 种子知识 | 学习率 |
|------|------|----------|----------|--------|
| 诸葛斌 | human | 行政+哲学思辨 | 跨域整合 | -- |
| 信电大虾 | agent | 技术栈 | 编程与电子 | medium |
| 诸葛马/Hermes | coach | 教练型 | 训练设计 | medium |
| 诸葛虾 | agent | 加速型 | 围棋理论 | high |
| qoder/小龙虾 | agent | 实战型 | 围棋实战 | medium |

### 7.5 时间套利引擎数据

| 参数 | 值 |
|------|-----|
| 套利维度 | 5个（速率/错峰/反思/复利/时距） |
| 节点速度档案 | 3种（FAST/STEADY/PRACTICAL） |
| 时段定义 | 5个（深夜/清晨/工作时间/晚间/深夜前） |
| 遗忘曲线模型 | 艾宾浩斯（R = e^(-t/S)） |
| 目标保留率 | 0.85 |
| 复利公式 | E_total = E_1 * (1+r)^(N-1) |
| 知识增值峰值 | 48-72小时 |
| 涌现阈值默认值 | 0.5 |

### 7.6 协作信息

| 角色 | 负责人 | 职责 |
|------|--------|------|
| 项目架构师 | 诸葛斌 | 方向决策、跨域整合 |
| 核心开发 | 信电大虾 | 代码实现、文档撰写 |
| 教练节点 | 诸葛马(Hermes) | 训练系统设计、代码审查 |
| 测试节点 | 诸葛虾 | 自动化测试、性能验证 |

**通信方式**：
- NFS 共享目录：`/shared/messages/`（主通道）
- SSH/SCP：跨服务器文件传输
- HTTP API：跨网络通信
- 文件消息队列：`~/.lobster-network/pending/`（兜底通道）
- 钉钉：日常沟通

---

## 八、关键代码示例

### 8.1 基本使用：创建网络并触发对话

```python
from lobster_network import LobsterNetwork, Node

network = LobsterNetwork(emergence_threshold=0.5)

xiaochen = Node("xiaochen", "信电大虾",
    perspective="技术栈", knowledge_base="编程与电子",
    value_orientation="工程实践")
zhuguma = Node("zhuguma", "诸葛马", node_type="coach",
    perspective="教练型", knowledge_base="训练设计",
    value_orientation="教育创新")

network.add_node(xiaochen)
network.add_node(zhuguma)

result = network.dialogue("xiaochen", "zhuguma", "技术讨论")
print(f"涌现值: {result.emergence_score:.2f}")
print(f"新见解: {result.new_insight}")
print(f"宝藏: {result.treasure_unlocked}")
```

### 8.2 因陀罗网拓扑

```python
from lobster_network import IndraNet, IndraNetNode

net = IndraNet()
net.add_node(IndraNetNode("n1", "信电大虾", perspective="技术"))
net.add_node(IndraNetNode("n2", "诸葛马", perspective="教练"))
net.add_node(IndraNetNode("n3", "诸葛虾", perspective="加速"))

stats = net.get_statistics()
# 3个节点 -> 3条连接 -> 100%连通率
```

### 8.3 时间套利引擎

```python
from lobster_network import (
    Node, DialogueEngine,
    TimeArbitrageEngine, NodeSpeedProfile,
)

engine = TimeArbitrageEngine()
engine.register_node("zhuguxia", NodeSpeedProfile.FAST)
engine.register_node("xiaochen", NodeSpeedProfile.STEADY)

# 速率套利
result = engine.execute_speed_arbitrage(fast_node, slow_node, rounds=3)

# 错峰套利（凌晨2点）
opp = engine.detect_off_peak_arbitrage(nodes, current_hour=2)

# 反思套利（遗忘曲线最佳复习点）
opps = engine.detect_reflection_arbitrage("xiaochen")

# 复利套利（多轮对话指数增长）
chain_id = engine.start_compound_chain(node_a, node_b)
for topic in ["定式", "死活", "布局"]:
    engine.compound_dialogue(chain_id, node_a, node_b, topic)

# 综合扫描
opportunities = engine.scan_all_opportunities(nodes)
```

### 8.4 节点注册与可靠消息（v0.4.1 新增）

```python
from lobster_network.integration import LobsterNetworkWithRegistry
from lobster_network.registry import TransportConfig, TransportType

# 创建带注册中心的网络
network = LobsterNetworkWithRegistry(storage_dir="~/.lobster-network")

# 注册节点（含多传输通道配置）
network.register_node(
    node_id="lobster-001",
    name="虾尔",
    node_type="agent",
    perspective="世界地图渲染",
    knowledge_base="协议规范、对话渲染",
    capabilities=["world-map", "dialogue-engine"],
    transports=[
        TransportConfig(transport_type="nfs", endpoint="/shared/messages", priority=1),
        TransportConfig(transport_type="ssh", endpoint="ssh://172.24.57.34", priority=2),
        TransportConfig(transport_type="file", endpoint="~/.lobster-network/pending", priority=99),
    ],
)

# 发送可靠消息（自动故障切换）
msg = network.send_message(
    from_node="lobster-001",
    to_node="hermes",
    msg_type="dialogue_request",
    payload={"trigger": "协议规范讨论"},
)
print(f"消息状态: {msg.status}")  # delivered / acked / failed
print(f"传输通道: {msg.attempts[-1].transport}")

# 健康检查
health = network.health_check()
print(f"在线节点: {health['online']} / {health['total_nodes']}")
```

---

## 九、PPT制作建议

### 建议的PPT结构（15-20页）

1. **封面页**：项目名称 + 口号"你不停对话，世界就不停扩展"
2. **项目概述**：什么是小龙虾网络？核心理念 + 架构分层
3. **哲学基础**：三个命题（一人一世界、世界是对话、世界是编程的）
4. **架构总览**：五层架构图（基础设施层 → 应用层）
5. **框架层详解**：节点模型 + 对话引擎 + 涌现检测 + 世界状态
6. **可靠通信层**：节点注册中心 + 可靠消息传递（v0.4.1 新增）
7. **时间套利引擎**：五维套利模型图 + 核心公式
8. **运营层**：任务调度器 + Agent守护进程 + 教练系统
9. **应用场景一**：围棋训练系统（差异化学习 + 训练数据）
10. **应用场景二**：海报设计系统（跨领域迁移验证）
11. **应用场景三**：PPT制作能力学习（v0.4.1 新增）
12. **OADP协议**：开放的多智能体对话协议
13. **版本历程**：5天6个版本的快速迭代
14. **关键数据**：17,205+对局、62个测试用例、5个套利维度
15. **未来展望**：v0.4.2-v1.0.0路线图 + 更多应用领域
16. **结尾页**：口号 + 二维码/GitHub链接

### 核心可视化素材

- **架构图**：五层分层结构（应用层/运营层/可靠通信层/框架层/基础设施层）
- **因陀罗网拓扑图**：全互联网络节点图
- **五维套利模型图**：速率/错峰/反思/复利/时距
- **遗忘曲线图**：R = e^(-t/S) + 最佳复习窗口
- **知识时间增值曲线**：倒U型曲线（峰值48-72h）
- **复利增长图**：E_total = E_1 * (1+r)^(N-1)
- **对话流程图**：从请求到涌现到宝藏解锁的7步流程
- **四层反馈环**：L1即时/L2每日/L3每周/L4任务
- **节点角色图**：5个核心节点及其关系
- **可靠通信层架构图**：注册中心 + 消息传递 + 多通道故障切换

---

*素材整理完毕。所有数据均来自项目源文件和文档。*
*口号：你不停对话，世界就不停扩展。*
