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

## 版本

- v1.0.0 (2026-06-25): 初始版本，框架搭建
