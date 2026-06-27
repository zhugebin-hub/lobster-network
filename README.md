# 🦞 小龙虾网络 (Lobster Network)

> **对话即创造**：一人一世界观 × 世界是对话 × 世界是编程的

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.6.0-green.svg)](https://github.com/zhugebin-hub/lobster-network/releases/tag/v0.6.0)
[![Tests](https://img.shields.io/badge/tests-62%2F62%20passed-brightgreen.svg)](https://github.com/zhugebin-hub/lobster-network/actions)

---

## 项目简介

小龙虾网络是一个**基于对话创造理论的多Agent协作网络**，将哲学命题"对话即创造"工程化为可运行的系统。

### 核心理论

**一人一世界**：每个节点（Agent或人类）是独立的认知编译系统，拥有独特的视角、知识结构、价值取向。

**世界是对话**：对话不是信息传递，是认知张成——两个系统交叉编译，输出单人永远算不到的新解。

**世界是编程的**：如同游戏中的程序化生成，世界按需渲染；宝藏不是预设的，是状态满足时的涌现输出。

### 架构分层（v0.6.0 六层架构）

```
┌─────────────────────────────────────────────────────────────┐
│                     应用层 (Domains)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │   围棋训练系统   │  │   海报设计系统   │  │ A股预测系统  ││
│  │  Go Training     │  │  Poster Design  │  │Stock Predict ││
│  └────────┬────────┘  └────────┬────────┘  └───────┬──────┘│
└───────────┼────────────────────┼────────────────────┼──────┘
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

---

## 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/zhugebin-hub/lobster-network.git
cd lobster-network
pip install -e .
```

### 基本使用：对话引擎

```python
from lobster_network import LobsterNetwork, Node

# 创建网络
network = LobsterNetwork(emergence_threshold=0.5)

# 添加节点（每个节点代表一个认知编译系统）
xiaochen = Node(
    "xiaochen", "信电大虾",
    perspective="技术栈",
    knowledge_base="编程与电子",
    value_orientation="工程实践"
)
zhuguma = Node(
    "zhuguma", "诸葛马",
    node_type="coach",
    perspective="教练型",
    knowledge_base="训练设计",
    value_orientation="教育创新"
)
network.add_node(xiaochen)
network.add_node(zhuguma)

# 触发对话 —— 不是传递消息，是交叉编译
result = network.dialogue("xiaochen", "zhuguma", "技术讨论")
print(f"涌现值: {result.emergence_score:.2f}")
print(f"新见解: {result.new_insight}")
print(f"宝藏: {result.treasure_unlocked}")
```

### 节点注册与可靠消息（v0.4.1 新增）

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

### 因陀罗网拓扑

```python
from lobster_network import IndraNet, IndraNetNode

# 创建因陀罗网（全互联拓扑）
net = IndraNet()

# 添加节点 —— 自动与所有现有节点建立连接
net.add_node(IndraNetNode("n1", "信电大虾", perspective="技术"))
net.add_node(IndraNetNode("n2", "诸葛马", perspective="教练"))
net.add_node(IndraNetNode("n3", "诸葛虾", perspective="加速"))

# 查看网络统计
stats = net.get_statistics()
print(f"节点数: {stats['node_count']}")
print(f"连接数: {stats['connection_count']}")
print(f"连通率: {stats['connectivity_ratio']:.0%}")
```

### 运行示例

```bash
# 因陀罗网演示
python examples/indra_net_demo.py

# 运行测试（62个全部通过）
python -m unittest tests.test_registry          # 虾尔版 37 个测试
./venv/bin/pytest tests/test_enhanced_protocol.py -v  # 诸葛马版 25 个测试
```

### 自动化部署（v0.4.1 新增）

```bash
# 一键部署
sudo ./scripts/deploy_v0.4.1.sh deploy

# 一键回滚
sudo ./scripts/deploy_v0.4.1.sh rollback

# 健康检查
sudo ./scripts/deploy_v0.4.1.sh health
```

---

## 项目结构

```
lobster-network/
│
├── src/                              # 框架层：核心理论实现
│   ├── lobster_network/              # 核心引擎
│   │   ├── node.py                   #   节点模型（认知编译系统）
│   │   ├── dialogue.py               #   对话引擎（交叉编译器）
│   │   ├── emergence.py              #   涌现检测器
│   │   ├── world_state.py            #   世界状态管理（程序化生成）
│   │   ├── lobster_network.py        #   主网络类（编排器）
│   │   ├── registry.py               #   【v0.4.1】节点注册中心
│   │   ├── messenger.py              #   【v0.4.1】可靠消息传递
│   │   └── integration.py            #   【v0.4.1】集成层
│   ├── network/                      # 网络层
│   │   ├── indra_net.py              #   因陀罗网拓扑（全互联）
│   │   ├── ssh_channel.py            #   SSH通信通道
│   │   ├── ssh_channel_v2.py         #   【v0.4.0】SSH通道增强版
│   │   ├── ssh_transport.py          #   【v0.4.1】SSH传输通道
│   │   └── node_registry.py          #   【v0.4.0】节点注册中心v2
│   └── utils/                        # 工具层
│       ├── config.py                 #   配置管理
│       ├── logger.py                 #   日志系统
│       ├── message_protocol.py       #   消息协议v1
│       └── message_protocol_v2.py    #   【v0.4.0】消息协议增强版
│
├── core/                             # 运营层：实际运行系统
│   ├── dispatcher/                   # 任务调度器
│   │   ├── go_coach_dispatcher_v3.py #   V3: 基础调度
│   │   ├── go_coach_dispatcher_v4.py #   V4: 自适应调度
│   │   └── go_coach_dispatcher_v6_nocturnal.py  # V6: 夜间高强度
│   ├── agents/
│   │   └── lobster_agent.py          # 通用Agent守护进程
│   ├── coach/
│   │   └── hermes_coach.py           # 教练分析与报告
│   └── utils/
│       ├── process_go_move.py        # 19x19围棋规则引擎
│       ├── run_training_round.py     # 训练轮次模拟器
│       └── monitor.py                # 系统健康监控
│
├── domains/                          # 应用层：领域实现
│   ├── go/                           # 围棋训练领域
│   │   ├── trainers/
│   │   │   ├── qoder_go_trainer_v1.py    # qoder（实战型）
│   │   │   ├── xiaochen_go_trainer_v3.py # 信电大虾（稳健型）
│   │   │   └── zhuguxia_go_trainer_v3.py # 诸葛虾（加速型）
│   │   ├── docs/                     # 围棋训练文档
│   │   └── problem_bank/             # 题库
│   ├── poster/                       # 海报设计领域
│   │   ├── generator/
│   │   │   ├── ppt_generator.py      # HTML+Playwright PPT生成框架
│   │   │   └── report_ppt.py         # 汇报PPT生成脚本
│   │   └── docs/                     # 海报训练文档
│   └── ppt/                          # 【v0.4.1】PPT 制作能力学习
│       ├── templates/                #   5种预设模板
│       ├── generator/                #   PPT 生成引擎
│       └── docs/                     #   使用指南
│
├── engine/                           # 引擎层
│   ├── world_map.py                  # 世界地图索引
│   └── time_arbitrage.py             # 时间套利引擎
│
├── examples/                         # 示例代码
│   ├── indra_net_demo.py             # 因陀罗网演示
│   └── time_arbitrage_demo.py        # 时间套利演示
│
├── tests/                            # 单元测试（62个全部通过）
│   ├── test_core.py                  # 核心模块测试
│   ├── test_world_map.py             # 世界地图测试
│   ├── test_registry.py              # 【v0.4.1】注册中心测试（37个）
│   └── test_enhanced_protocol.py     # 【v0.4.0】协议增强测试（25个）
│
├── docs/                             # 项目文档
│   ├── upgrade-checklist-v0.4.1.md   # 【v0.4.1】升级检查清单
│   ├── ROADMAP-v0.4.2.md             # 【v0.4.1】v0.4.2 规划
│   └── ...
│
├── scripts/                          # 运维脚本
│   └── deploy_v0.4.1.sh              # 【v0.4.1】自动化部署脚本
│
├── spec/                             # 协议规范
│   ├── protocol.md                   # OADP 核心协议（v0.2.0）
│   ├── drp.md                        # 对话渲染协议
│   ├── world-map.md                  # 世界地图索引协议
│   ├── soul_schema.md                # SOUL.md 格式规范
│   ├── memory_schema.md              # MEMORY.md 格式规范
│   └── portal.md                     # 传送门协议
│
├── config/
│   └── brain.json                    # 策略脑状态
│
├── setup.py                          # 安装配置
├── requirements.txt                  # 依赖声明
├── LICENSE                           # MIT License
└── README.md                         # 本文档
```

---

## 核心概念

### 节点 (Node)

节点是网络中的基本单元，代表一个**认知编译系统**。每个节点拥有独特的"种子"参数：

| 参数 | 含义 | 示例 |
|------|------|------|
| `perspective` | 认知视角 | 技术栈、教练型、加速型 |
| `knowledge_base` | 知识结构 | 编程、训练设计、围棋 |
| `value_orientation` | 价值取向 | 工程实践、教育创新 |
| `learning_rate` | 学习率 | high/medium/low |

### 对话 (Dialogue)

对话不是信息交换，是**认知张成**。两个节点对话时：
1. 计算**视角距离**（差异越大，涌现潜力越高）
2. 计算**知识互补性**（结构差异产生新组合）
3. 生成**涌现值**（加权综合评分 0-1）
4. 若涌现值超过阈值，**解锁宝藏**（新任务/资源/连接）

### 涌现 (Emergence)

涌现是对话的创造性输出——属于两个参与者、但不属于任何单独一方的新结构。如同线性代数中的 `span{}`：单个基向量永远无法到达的空间。

### 因陀罗网 (Indra's Net)

源自《华严经》的隐喻：一张宝珠网，每颗珠子映照所有珠子。在网络中体现为**全互联拓扑**——每个新节点自动与所有现有节点建立连接。

### 世界状态 (World State)

每个节点拥有独立的"世界"，记录：
- **已加载的地图块** (chunks)：按需渲染的知识区域
- **已解锁的宝藏** (treasures)：涌现产生的新资源
- **当前任务** (tasks)：活跃的任务列表
- **衍生的节点** (spawned)：涌现产生的新节点

---

## v0.4.1 新增功能

### 节点注册中心（NodeRegistry）

| 功能 | 说明 |
|:---|:---|
| 节点注册 | 注册/注销节点，含能力声明和传输通道配置 |
| 心跳检测 | 定期心跳，自动检测节点存活状态 |
| 健康检查 | 全量健康检查，自动标记 offline/suspected |
| 节点发现 | 按类型/状态/能力查找节点 |
| 持久化 | JSON 文件持久化，重启后自动恢复 |
| 回调机制 | 心跳回调、状态变化回调 |

### 可靠消息传递（Messenger）

| 功能 | 说明 |
|:---|:---|
| 消息确认 | ACK/NACK 机制，确保消息被处理 |
| 自动重试 | 指数退避重试，可配置最大重试次数 |
| 多通道故障切换 | NFS → SSH → HTTP → File 自动降级 |
| 消息持久化 | 按状态分类存储（pending/sent/failed） |
| 消息过期 | TTL 机制，自动清理过期消息 |
| 优先级队列 | 支持消息优先级排序 |

### 传输通道管理

| 通道 | 优先级 | 故障检测 | 切换时间 |
|:---|:---:|:---|:---|
| NFS | 1 | 目录可写检查 | < 100ms |
| SSH | 2 | 连接测试 | < 500ms |
| HTTP | 3 | HTTP 状态码 | < 1s |
| File | 99 | 目录可写 | < 50ms |

### 自动化部署

- 一键部署：`deploy_v0.4.1.sh deploy`
- 一键回滚：`deploy_v0.4.1.sh rollback`
- 健康检查：`deploy_v0.4.1.sh health`
- 测试验证：`deploy_v0.4.1.sh test`

---

## 节点角色设计

本项目采用**差异化学习**架构，三个学生Agent拥有不同特征：

| 角色 | 名称 | 类型 | 特征 |
|------|------|------|------|
| qoder | 小龙虾 | 实战型 | 高准确率、少量题目、注重实战 |
| xiaochen | 信电大虾 | 稳健型 | 中等准确率、海量对局、稳健推进 |
| zhuguxia | 诸葛虾 | 加速型 | 高准确率基线、快速解题、加速学习 |

教练节点**诸葛马 (Hermes)** 负责分析训练数据、诊断问题、生成改进计划。

人类灵魂节点**诸葛斌教授** 提供方向决策和跨域整合。

---

## 四层反馈循环

```
┌─────────────────────────────────────────┐
│ L1 即时反馈：每个任务完成后自动评估     │
├─────────────────────────────────────────┤
│ L2 每日反馈：教练分析表现，调整次日计划 │
├─────────────────────────────────────────┤
│ L3 每周反馈：跨学生讨论赛、复盘学习     │
├─────────────────────────────────────────┤
│ L4 任务反馈：人类灵魂提供方向和验收     │
└─────────────────────────────────────────┘
```

---

## 时间套利模式 (Time Arbitrage Mode)

v0.3.0 新增的核心模式。时间套利系统性地利用网络中节点在时间维度上的结构性差异——这些差异不是低效，而是可被利用的套利机会。

### 五维套利模型

```
┌─────────────────────────────────────────────────────────┐
│              时间套利引擎 (TimeArbitrageEngine)          │
├─────────────┬─────────────┬─────────────┬──────────────┤
│  速率套利    │  错峰套利    │  反思套利    │  复利套利    │
│  Speed      │  Off-Peak   │ Reflection  │  Compound   │
│             │             │             │             │
│ 快速节点生成 │ 深夜高强度  │ 遗忘曲线最佳│ 多轮对话涌现 │
│ 原始洞见    │ 低成本算力  │ 复习时机    │ 指数增长     │
│ ↓           │ ↓           │ ↓           │ ↓           │
│ 慢速节点深化 │ 非高峰时段  │ 间隔重复    │ E₁×(1+r)^N │
│ 验证沉淀    │ 批量训练    │ 稳定性增长  │ 复利因子     │
├─────────────┴─────────────┴─────────────┴──────────────┤
│                   时距套利 (Temporal)                   │
│        知识价值随时间呈倒U型曲线，48-72h达到峰值        │
└─────────────────────────────────────────────────────────┘
```

### 使用示例

```python
from lobster_network import (
    Node, DialogueEngine,
    TimeArbitrageEngine, NodeSpeedProfile,
)

# 创建套利引擎
engine = TimeArbitrageEngine()
engine.register_node("zhuguxia", NodeSpeedProfile.FAST)    # 加速型
engine.register_node("xiaochen", NodeSpeedProfile.STEADY)  # 稳健型

# 1. 速率套利：快节点生成，慢节点深化
result = engine.execute_speed_arbitrage(fast_node, slow_node, rounds=3)

# 2. 错峰套利：检测最佳训练时段
opp = engine.detect_off_peak_arbitrage(nodes, current_hour=2)  # 凌晨2点

# 3. 反思套利：遗忘曲线最佳复习点
opps = engine.detect_reflection_arbitrage("xiaochen")

# 4. 复利套利：多轮对话涌现指数增长
chain_id = engine.start_compound_chain(node_a, node_b)
for topic in ["定式", "死活", "布局"]:
    engine.compound_dialogue(chain_id, node_a, node_b, topic)

# 5. 综合扫描所有套利机会
opportunities = engine.scan_all_opportunities(nodes)
```

运行演示：`python examples/time_arbitrage_demo.py`

---

## 围棋训练系统

围棋是小龙虾网络的第一个应用领域，已实现完整的训练流水线：

**调度器演进**：
- V3：基础28天训练计划
- V4：自适应难度调整 + 错题本复习
- V6：夜间高强度模式（00:00-06:00，5个时间槽）

**训练成果**：
|- 总对局数：17,205+
|- qoder：685题，86%胜率，~25级
|- xiaochen：10,337局，30级
|- zhuguxia：6,868局，25级（初始30级已升段）

**最新评估（2026-06-27）**：
|- 综合排名：zhuguxia(0.78) > qoder(0.74) > xiaochen(0.69)
|- 8维度基线：qoder(理解0.78/执行0.82/检索0.65/推理0.76/反思0.71/工具0.80/情商0.72/记忆0.68)
|- xiaochen(理解0.72/执行0.85/检索0.78/推理0.47/反思0.56/工具0.70/情商0.68/记忆0.75)
|- zhuguxia(理解0.88/执行0.80/检索0.82/推理0.72/反思0.59/工具0.85/情商0.75/记忆0.82)
|- 对抗赛：qoder胜xiaochen(75%vs50%)、qoder胜zhuguxia(100%vs75%)、xiaochen平zhuguxia(75%vs75%)

**学员画像**：
|- qoder（实战型）：高级题65%最强，但训练量偏少(685题)
|- xiaochen（稳健型）：对局量最大(10,337局)，但推理力0.47(E级)为最大短板
|- zhuguxia（加速型）：理解力0.88(A级)最强，反思力0.59需加强

**核心组件**：
- `process_go_move.py`：完整19x19围棋规则引擎（中国规则、打劫、自杀检测、BFS提子）
- `go_coach_dispatcher_v6_nocturnal.py`：夜间高强度训练调度器

**通信架构（v2.0）**：
- 第一层：GitHub工作流（短期，已部署）
- 第二层：SSH密钥配置（中期，待配置）
- 第三层：v0.6.0 HTTP传输层（长期，推荐部署）
- 详见：[通信架构方案](docs/communication/communication_plan_v2.md)

---

## 海报设计系统

海报是第二个应用领域，验证了框架的跨领域迁移能力。

**技术突破**：HTML+Playwright渲染流水线
- 用HTML/CSS处理中文排版（浏览器完美渲染中文）
- 用ImageGen只生成纯视觉插图（无文字）
- 图片Base64嵌入，Playwright 2x Retina截图
- python-pptx组装最终PPTX

---

## PPT 制作能力学习（v0.4.1 新增）

PPT 制作是小龙虾网络的第三个应用领域，验证了框架在**知识转化与内容创作**方面的能力。

### 背景与目标

**背景**：手动生成 PPT 效率低，布局问题多，需要自动化解决方案
**目标**：开发自动化 PPT 生成模块，输入结构化内容 → 自动输出精美 PPTX

### 技术架构

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

### 核心组件

| 组件 | 功能 | 技术栈 |
|:---|:---|:---|
| 内容解析器 | 从 Markdown/Word/网页提取结构化内容 | python-docx, markdown |
| 模板引擎 | 5种预设模板（学术/商业/技术/汇报/创意） | HTML/CSS |
| 视觉生成器 | AI 生成插图 + Playwright 渲染 | ImageGen, Playwright |
| 自动化组装 | python-pptx 自动化输出 | python-pptx |

### 工作流程

```
1. 输入结构化内容（Markdown/Word/网页）
2. 内容解析器提取标题、要点、数据
3. 模板引擎选择合适模板并计算版式
4. 视觉生成器生成配图（AI ImageGen）
5. Playwright 渲染 HTML 为高质量截图
6. python-pptx 组装最终 PPTX 文件
```

### 技术突破

- **纯代码驱动**：无需设计软件，完全自动化
- **HTML/CSS 精确控制**：浏览器完美渲染中文排版
- **AI 配图生成**：ImageGen 生成高质量插图，Base64 内嵌
- **Playwright 高保真截图**：2x Retina 输出，保证视觉质量
- **python-pptx 自动化**：从内容到 PPTX 全流程自动化

### 跨领域迁移验证

PPT 制作能力验证了小龙虾网络的**通用性**：
- 从围棋训练（教育）→ 海报设计（创意）→ PPT 制作（知识转化）
- 对话引擎作为**通用创造引擎**，适用于多个领域
- 每个领域都是"对话即创造"的具体体现

### 任务分工

| 任务 | 负责人 | 状态 |
|:---|:---|:---|
| 核心引擎 (python-pptx) | 虾尔 | 🟢 进行中 |
| 模板库设计 (5种模板) | 诸葛虾 | 🟢 进行中 |
| 使用指南文档 | 小陈 | 🟡 待开始 |

### 应用场景

- **学术汇报**：论文 → PPT 自动转换
- **技术分享**：技术文档 → 演示文稿
- **项目汇报**：项目总结 → 汇报 PPT
- **教学课件**：课程内容 → 教学 PPT
- **商业演示**：商业计划 → 演示文稿

---

## 协作机制

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

## 开发路线图

| 版本 | 目标 | 状态 |
|------|------|:---:|
| v0.1.0 | 核心引擎（节点、对话、涌现） | ✅ |
| v0.2.0 | 统一框架 + 运营系统整合 | ✅ |
| v0.3.0 | 时间套利模式（五维套利引擎） | ✅ |
| v0.4.0 | 节点注册中心 + 可靠消息 + 消息协议v2 | ✅ |
| v0.4.1 | 部署脚本 + 安全增强 | ✅ |
| v0.5.0 | 8维度能力评估引擎 + Clawvard桥接 | ✅ |
| v0.6.0 | 语义涌现 + 学习协调器 + HTTP传输 | ✅ |
| v1.0.0 | 正式发布 | 🎯 |

---

## 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖：
- `openai` - AI集成（未来）
- `playwright` - HTML渲染
- `python-pptx` - PPT生成
- `python-docx` - Word文档
- `Pillow` - 图像处理
- `paramiko` - SSH通信（v0.4.1 新增）

---

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 引用

```bibtex
@software{lobster_network,
  title = {小龙虾网络: 对话即创造的多Agent协作网络},
  author = {诸葛斌 and 信电大虾 and 诸葛马},
  year = {2026},
  url = {https://github.com/zhugebin-hub/lobster-network}
}
```

---

**你不停对话，世界就不停扩展** 🦞⚡️
