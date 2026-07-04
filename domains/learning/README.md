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

## 版本

- v1.0.0 (2026-06-25): 初始版本，框架搭建
- v1.1.0 (2026-06-26): 新增炒股预测学习模块（60题）
