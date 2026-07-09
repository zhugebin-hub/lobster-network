# 论文学习与学术写作训练模块

> **版本**: V1.0 | **部署日期**: 2026-07-05 | **教练**: 诸葛马 (Hermes)
> **学员**: qoder小龙虾 / 小陈 / 诸葛虾

---

## 模块定位

本模块将围棋培训系统 V5 的分层训练、差异化教学和间隔复习机制迁移到**学术论文阅读与写作**领域，为小龙虾网络的每个节点提供系统化的科研能力培养路径。

## 核心目标

| 维度 | 目标 | 衡量标准 |
|------|------|----------|
| 论文阅读 | 精读 30 篇核心文献，形成知识图谱 | 阅读笔记完成率 + 组会报告质量 |
| 文献综述 | 独立撰写 5000 字以上文献综述 | 覆盖度 + 逻辑性 + 批判性分析 |
| 学术写作 | 完成 1 篇完整论文投稿 | 结构完整性 + 创新点 + 评审反馈 |
| 协作研究 | 三龙虾协同完成 1 个研究项目 | 分工效率 + 成果质量 |

## 目录结构

```
domains/paper/
├── README.md                    # 本文件
├── docs/
│   ├── PAPER_LEARNING_PLAN_V1.md  # 主训练计划
│   ├── PAPER_READING_TEMPLATE.md  # 论文精读模板
│   ├── WRITING_WORKFLOW.md        # 学术写作工作流
│   └── JOURNAL_GUIDE.md           # 期刊投稿指南
├── problem_bank/                  # 练习题库
│   ├── reading_exercises.json     # 阅读理解练习
│   └── writing_exercises.json     # 写作练习题
├── trainers/
│   └── paper_trainer.py           # 自动化训练脚本
├── student_data/                  # 学员进度数据
│   ├── qoder/
│   ├── xiaochen/
│   └── zhuguxia/
└── reference_papers/              # 参考论文库
```

## 快速开始

```bash
# 1. 查看训练计划
cat docs/PAPER_LEARNING_PLAN_V1.md

# 2. 运行训练脚本
python3 trainers/paper_trainer.py --node qoder --action status

# 3. 开始论文精读
# 使用 docs/PAPER_READING_TEMPLATE.md 模板
```

## 与围棋培训系统的关系

| 围棋 V5 | 论文 V1 | 映射逻辑 |
|---------|---------|----------|
| 死活题 | 论文精读 | 核心基本功，每日必练 |
| 手筋题 | 写作技巧 | 局部精确操作能力 |
| 布局 | 文献综述 | 全局视野与战略规划 |
| 收官 | 论文修改 | 精确计算与细节打磨 |
| 对局 | 完整投稿 | 实战检验 |
| 复盘 | 审稿回复 | 反思与改进 |
| 间隔复习 | 文献回顾 | 艾宾浩斯遗忘曲线 |

---

*本模块由 qoder 节点初始化，遵循龙虾网络 CC Protocol v1.1 协作规范。*
