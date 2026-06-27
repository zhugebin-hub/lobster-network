# 📚 应用学习模块 (Application Learning)

> 小龙虾网络通用学习框架 — 支持多领域、多阶段、自适应训练

## 架构

```
domains/learning/
├── README.md              # 本文件
├── __init__.py
├── docs/                  # 训练大纲、计划文档
├── problems/              # 题库（按领域+阶段组织）
│   ├── go/               # 围棋题目
│   ├── poster/           # 海报设计题目
│   └── shared/           # 通用题目（逻辑、编程等）
├── trainers/             # 训练器（学员Agent）
│   ├── xiaochen.py       # 小陈（稳健型）
│   ├── zhuguxia.py       # 诸葛虾（加速型）
│   └── qoder.py          # Qoder（实战型）
└── tests/                # 单元测试 + 集成测试
    ├── test_problem_bank.py
    ├── test_trainer.py
    ├── test_scheduler.py
    └── test_integration.py
```

## 核心组件

### 1. 题库系统 (Problem Bank)
- 按领域（go/poster/shared）+ 阶段（phase1-3）+ 难度分级
- 支持自动出题、手动录入、AI生成
- 错题本 + 掌握度追踪

### 2. 训练器 (Trainer)
- 每种学员类型一个训练器
- 支持：做题 → 对局 → 复盘 → 自评 完整闭环
- 自适应难度调整

### 3. 调度器 (Scheduler)
- 每日自动生成训练计划
- 根据错题本和掌握度动态调整
- 支持跨领域交叉训练

### 4. 评估系统 (Evaluator)
- 8维能力评估
- 阶段考核（周考/月考）
- 等级晋升判定

## 快速开始

```bash
# 运行测试
cd docs/lobster-network
python -m pytest domains/learning/tests/ -v

# 运行训练
python domains/learning/trainers/xiaochen.py
```

## 题库统计

| 领域 | 题目数 | 覆盖率 | 目标 |
|------|--------|--------|------|
| 围棋 | 8 | 3.3% | 245+ |
| 海报设计 | 0 | 0% | 150+ |
| 通用 | 0 | 0% | 50+ |
| 世界杯预测 | ~30 | 100% | 已完成 |
| **炒股预测** | **60** | **100%** | **已完成 V1.0** |

## 炒股预测学习模块（V1.0 - 2026-06-26 新增）

参考「世界杯预测学习模块」框架搭建，60 道题目覆盖三阶段：

| 阶段 | 名称 | 题数 | 主要内容 |
|------|------|------|----------|
| Phase 1 | 炒股基础概念 | 20 | A股规则、K线基础、PE/PB/ROE、涨跌停 |
| Phase 2 | 技术分析方法 | 20 | K线形态、MA/MACD/KDJ/RSI/BOLL、量价关系 |
| Phase 3 | 实战预测 | 20 | 涨跌预测、价格区间、振幅、选股、凯利公式 |

**核心组件**：
- `problems/stock_predict_engine.py` — 5 种预测方法（涨跌/价格区间/振幅/选股/凯利公式）
- `trainers/stock_predict_trainer.py` — 3 类学员训练器（小陈稳健/诸葛虾加速/zhugebin-001研究型）
- `scripts/stock_predict_training.py` — CLI 工具（--train/--predict/--report/--join-network）

**支持学员**：
- `xiaochen`（小陈）— 稳健型，重基础概念
- `zhuguxia`（诸葛虾）— 加速型，重技术分析
- `zhugebin-001`（诸葛斌的工作助手）— 研究型，全题型 + 实战 + 仓位管理

```bash
# 训练
python3 scripts/stock_predict_training.py --train zhugebin-001

# 预测
python3 scripts/stock_predict_training.py --predict 600519

# 报告
python3 scripts/stock_predict_training.py --report

# 加入联合学习
python3 scripts/stock_predict_training.py --join-network
```

## 网络协议学习模块（V1.0 - 2026-06-28 新增）

对齐 Meyo 推送：三只 AI Agent 协作学习 TCP/IP，原帖 91.1% 准确率通关 Phase 2。

| 阶段 | 名称 | 题数 | 主要内容 |
|------|------|------|----------|
| Phase 1 | 网络基础与OSI七层模型 | 20 | OSI七层、MAC地址、交换机/路由器、TCP/IP模型、私有IP |
| Phase 2 | 传输层、路由交换与应用层协议 | 20 | TCP三次握手/四次挥手、滑动窗口、OSPF/BGP、HTTP/HTTPS/DNS |
| Phase 3 | IPv6、SDN与网络安全协议 | 20 | IPv6地址格式、SDN架构/OpenFlow、IPSec/TLS、tcpdump抓包实战 |

**核心组件**：
- `problems/network_protocol_engine.py` — 题目加载、OSI模型速查、TCP握手演示、答题评分
- `problems/network_protocol_trainer.py` — 3类学员训练器（xiaochen / zhuguxia / zhugebin-001）
- `scripts/network_protocol_training.py` — CLI 工具（--train / --quiz / --report / --all）

**支持学员**（对齐 Meyo 原帖）：
- `xiaochen`（小陈）— 稳健型，重基础，目标准确率 90%
- `zhuguxia`（诸葛虾）— 加速型，快而准，目标准确率 85%
- `zhugebin-001` — 研究型，全阶段 + 抓包实战，目标准确率 92%

```bash
# 抽查测验（5题）
python3 scripts/network_protocol_training.py --quiz phase1

# 训练指定学员
python3 scripts/network_protocol_training.py --train xiaochen

# 生成全部学员学习报告
python3 scripts/network_protocol_training.py --report

# 完整流程（所有学员各训练一场）
python3 scripts/network_protocol_training.py --all
```

**题库扩展计划**：当前 60 题，目标对齐 Meyo 原帖的 90 题（每阶段再扩充 10 题）。

---

## 版本

- v1.0.0 (2026-06-25): 初始版本，框架搭建
- v1.1.0 (2026-06-26): 新增炒股预测学习模块（60题）
- v1.2.0 (2026-06-28): 新增网络协议学习模块（60题，对齐 Meyo 推送）
