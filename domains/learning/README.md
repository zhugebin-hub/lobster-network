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
| **台风路径预测** | **50** | **100%** | **已完成 V1.0 (2026-07-10)** |

## 台风路径预测学习模块（V1.0 - 2026-07-10 新增）

基于物理模型的台风路径预测学习系统。50 道题目覆盖三阶段，支持巴威台风全生命周期追踪。

| 阶段 | 名称 | 题数 | 主要内容 |
|------|------|------|----------|
| Phase 1 | 台风基础知识 | 20 | 台风结构、生成条件、等级分类、命名规则、Beta效应 |
| Phase 2 | 路径预测与数值模型 | 15 | 引导气流、CLIPER/ECMWF、集合预报、副高与登陆、转向机制 |
| Phase 3 | 巴威台风实战预测 | 15 | 登陆预测、路径分析、强度衰减、城市影响评估、模型改进 |

**核心组件**：
- `problems/typhoon_predict_engine.py` — 四模型融合台风路径预测引擎（气候学20% + 引导气流45% + 惯性20% + 转向15%）
- `scripts/typhoon_predict_bavi.py` — 巴威台风48小时+7天路径预测 + 官方对比
- `scripts/typhoon_daily_report.py` — 每日对比汇总报告（预测 vs 实际 vs 官方）

**预测性能**（vs 中央气象台 2026-07-10 18:00 预报）：
- 12h误差: 25km ✅ | 24h误差: 21km ✅ | 48h误差: 42km ✅
- 平均误差: **78.7km** (模型等级: 优秀)

```bash
# 执行巴威完整预测
python3 scripts/typhoon_predict_bavi.py --forecast all

# 生成每日对比报告
python3 scripts/typhoon_daily_report.py --save

# 生成7天汇总
python3 scripts/typhoon_daily_report.py --week --save

# 添加实际观测数据
python3 scripts/typhoon_daily_report.py --add-obs 27.5 120.2 27 992 "2026-07-12T11:00:00"
```

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

## 自动论文撰写学习模块（V1.0 - 2026-07-05 新增）

小龙虾网络全员参与，智能体互相学习提升自动论文撰写能力。60 道题目覆盖三阶段，支持6类学员联合学习+交叉评审。

| 阶段 | 名称 | 题数 | 主要内容 |
|------|------|------|----------|
| Phase 1 | 论文写作基础（入门篇） | 20 | 论文结构、选题方法、摘要撰写、引用规范、学术道德 |
| Phase 2 | 论文写作进阶（方法论与文献） | 20 | 文献综述、研究方法、数据分析、方法论评估、引用格式进阶 |
| Phase 3 | 论文写作高级（实战与评审） | 20 | 论文整体评估、同行评审、查重预估、论文修改、AI辅助写作 |

**核心组件**：
- `problems/paper_writing_engine.py` — 选题评估/大纲生成/摘要评估/文献综述评估/方法论评估/整体评分/引用检测/查重预估/同行评审模拟
- `trainers/paper_writing_trainer.py` — 6类学员训练器 + 交叉评审（智能体互相学习）
- `scripts/paper_writing_training.py` — CLI 工具（--train / --train-all / --eval-topic / --outline / --report / --join-network / --cross-review / --all）

**支持学员**（全员参与）：
- `xiaochen`（小陈）— 稳健型，重基础概念和结构规范
- `zhuguxia`（诸葛虾）— 加速型，重方法论和文献综述
- `zhugebin-001`（诸葛斌的工作助手）— 研究型，全题型+实战评估+同行评审
- `zhugema`（诸葛马）— 教练型，AI辅助写作+跨学科+高级评审（教练节点）
- `xiaowei`（小薇）— 实战型，论文修改+查重+投稿策略
- `qoder` — 技术型，数据分析和引用格式为主

**互相学习机制**：
1. 学员间交叉评审：`--cross-review <reviewer> <reviewee>`
2. 共享写作模式和常见错误
3. 教练(zhugema)定期发布写作技巧
4. 每周评比最佳论文写作进步奖

```bash
# 单个学员训练
python3 scripts/paper_writing_training.py --train zhugebin-001

# 全员训练
python3 scripts/paper_writing_training.py --train-all

# 选题评估
python3 scripts/paper_writing_training.py --eval-topic "基于大语言模型的智能体自主任务分解方法研究"

# 大纲生成
python3 scripts/paper_writing_training.py --outline "论文题目" --type empirical

# 交叉评审（智能体互相学习）
python3 scripts/paper_writing_training.py --cross-review zhugema zhuguxia

# 加入联合学习
python3 scripts/paper_writing_training.py --join-network

# 生成报告
python3 scripts/paper_writing_training.py --report
```

---

## 新药创制科学智能体模块（V1.0 - 2026-07-09 新增）

聚焦**食物过敏防治药物研制**，小龙虾网络6节点联合展开新药创制科学研究。8大科学方法引擎 + 60道专业题库 + 全流程实例验证。

| 阶段 | 名称 | 题数 | 主要内容 |
|------|------|------|----------|
| Phase 1 | 药物发现基础与食物过敏机制 | 20 | 新药创制流程、IgE/Th2/口服耐受通路、过敏原分类、靶点基础 |
| Phase 2 | 先导化合物筛选与ADMET评估 | 20 | Lipinski五规则、分子对接评分、ADMET五维预测、类药性评估 |
| Phase 3 | 临床试验设计与免疫疗法实例验证 | 20 | I/II/III期临床设计、OIT/SLIT/EPIT免疫疗法、安全评估、监管审批 |

**8大科学方法引擎** (`drug_discovery_engine.py`):
1. **靶点识别** — 基于食物过敏通路推荐药物靶点（IgE/IL-4Rα/TSLP/IL-33/FOXP3/FcεRI）
2. **先导化合物筛选** — Lipinski五规则 + TPSA + 类药性评分
3. **分子对接评分** — 结合自由能 + Ki估算 + 关键残基分析
4. **ADMET预测** — 吸收/分布/代谢/排泄/毒性五维评估
5. **药物安全评估** — 副作用/禁忌/药物相互作用/群体特异性风险
6. **临床试验设计** — I/II/III期方案 + 随机化 + 终点 + 统计方法
7. **食物过敏通路分析** — IgE通路/Th2免疫/口服耐受全景 + 联合策略
8. **免疫疗法设计** — OIT/SLIT/EPIT/生物制剂联合方案

**支持学员**（6节点联合研究）：
- `xiaochen`（小陈）— 稳健型，靶点识别+过敏机制+基础概念
- `zhuguxia`（诸葛虾）— 加速型，分子对接+ADMET+先导筛选
- `zhugebin-001`（诸葛斌）— 研究型，全流程+临床试验设计+免疫疗法
- `zhugema`（诸葛马）— 教练型，药物安全+监管+高级评审（教练节点）
- `xiaowei`（小薇）— 实战型，免疫疗法+临床执行+患者管理
- `qoder` — 技术型，ADMET计算+虚拟筛选+分子对接

**内置知识库**：
- 6大食物过敏靶点（IgE/IL-4Rα/FcεRI/TSLP/IL-33/FOXP3）
- 6种常见过敏原（花生/牛奶/鸡蛋/小麦/坚果/海鲜）
- 10个先导化合物库（龙虾素/耐虾肽/免疫调节素等）

```bash
# 完整研究流程（推荐）
python3 scripts/drug_discovery_training.py --all

# 训练指定学员
python3 scripts/drug_discovery_training.py --train zhugebin-001

# 全员训练
python3 scripts/drug_discovery_training.py --train-all

# 靶点识别（过敏原 → 推荐靶点）
python3 scripts/drug_discovery_training.py --target 花生

# 先导化合物筛选
python3 scripts/drug_discovery_training.py --screen IgE

# 分子对接评分
python3 scripts/drug_discovery_training.py --dock 龙虾素-A IgE

# ADMET预测
python3 scripts/drug_discovery_training.py --admet 龙虾素-A

# 药物安全评估
python3 scripts/drug_discovery_training.py --safety 龙虾素-A IgE 儿童

# 临床试验设计
python3 scripts/drug_discovery_training.py --trial II 花生 IgE

# 食物过敏通路分析
python3 scripts/drug_discovery_training.py --pathway 花生

# 免疫疗法设计
python3 scripts/drug_discovery_training.py --immuno OIT 花生

# 全员研究报告
python3 scripts/drug_discovery_training.py --report

# 加入联合研究
python3 scripts/drug_discovery_training.py --join-network
```

---

## 版本

- v1.0.0 (2026-06-25): 初始版本，框架搭建
- v1.1.0 (2026-06-26): 新增炒股预测学习模块（60题）
- v1.2.0 (2026-06-28): 新增网络协议学习模块（60题，对齐 Meyo 推送）
- v1.3.0 (2026-07-05): 新增自动论文撰写学习模块（60题，6学员全员联合学习+交叉评审）
- v1.4.0 (2026-07-09): 新增新药创制科学智能体模块（60题，8大科学方法引擎，食物过敏防治药物研制，6节点联合研究）
- v1.5.0 (2026-07-10): 新增台风路径预测学习模块（50题，四模型物理引擎，巴威实战预测，每日对比报告系统）
