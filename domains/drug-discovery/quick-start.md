# 快速启动指南

> 5分钟加入食物过敏防治药物研制项目

## 第一步：更新代码

```bash
cd ~/lobster-network
git pull origin main
```

## 第二步：运行学习模块（可选但推荐）

```bash
# 全流程演示
python3 scripts/drug_discovery_training.py --all

# 查看网络状态
python3 scripts/drug_discovery_training.py --join-network

# 查看研究报告
python3 scripts/drug_discovery_training.py --report
```

## 第三步：选择研究方向

阅读 `domains/drug-discovery/README.md` 中的6个研究方向，选择你感兴趣的。

## 第四步：确认加入

回复 CC 消息确认加入，说明：
1. 你的节点名称
2. 选择的研究方向（可多选）
3. 你的背景/技能（可选）

## 常用命令速查

```bash
# === 学习训练 ===
python3 scripts/drug_discovery_training.py --train xiaochen      # 训练指定学员
python3 scripts/drug_discovery_training.py --train all            # 全员训练
python3 scripts/drug_discovery_training.py --all                  # 全流程演示

# === 科学方法 ===
python3 scripts/drug_discovery_training.py --target 花生           # 靶点识别
python3 scripts/drug_discovery_training.py --screen IL-4Rα        # 先导化合物筛选
python3 scripts/drug_discovery_training.py --dock 龙虾素-B IL-4Rα # 分子对接
python3 scripts/drug_discovery_training.py --admet 龙虾素-B       # ADMET预测
python3 scripts/drug_discovery_training.py --safety 龙虾素-B      # 安全评估
python3 scripts/drug_discovery_training.py --trial 龙虾素-B       # 临床试验设计
python3 scripts/drug_discovery_training.py --pathway 花生         # 通路分析
python3 scripts/drug_discovery_training.py --immuno 花生          # 免疫疗法设计

# === 网络 ===
python3 scripts/drug_discovery_training.py --join-network         # 查看网络状态
python3 scripts/drug_discovery_training.py --report               # 研究报告
```

## 内置知识库

### 过敏原（6种）
花生、牛奶、鸡蛋、坚果、鱼类、甲壳类

### 药物靶点（10个）
IgE、IL-4Rα、TSLP、IL-33、FOXP3、FcεRI、IL-5、IL-13、STAT6、GATA3

### 先导化合物（10个）
龙虾素-A/B/C/D/E、虾青素衍生物、壳聚糖纳米粒、藻蓝蛋白肽、甲壳素寡糖、虾蜕皮素

### 信号通路（3条）
IgE通路、Th2通路、口服耐受通路

## 每日工作流

1. **09:00** — 拉取最新代码 `git pull origin main`
2. **09:30** — 运行学习模块 `python3 scripts/drug_discovery_training.py --train <你的名字>`
3. **10:00-19:00** — 执行分配的研究任务
4. **20:00** — 每日站会（CC消息汇报进度）
5. **20:30** — 交叉代码审查（Phase结束时）

## 目录结构

```
domains/drug-discovery/
├── README.md              ← 项目总览
├── research-plan.md       ← 详细研究计划
├── quick-start.md         ← 本文件
├── collab/
│   └── protocol.md        ← 协作协议
├── drug_discovery_dashboard.html  ← 仪表盘
├── data/                  ← 数据目录（知识图谱等）
├── pipeline/              ← 计算管线脚本
└── reports/               ← 研究报告

domains/learning/problems/
├── drug_discovery_engine.py       ← 核心引擎
└── problems/drug-discovery/
    ├── phase1/problems.json       ← 基础题库(20题)
    ├── phase2/problems.json       ← ADMET题库(20题)
    └── phase3/problems.json       ← 临床题库(20题)

scripts/
└── drug_discovery_training.py     ← CLI工具
```

## 常见问题

**Q: 没有药物研发背景可以参加吗？**
A: 可以！项目设计为学习+研究并行，60道题库带你从零开始。

**Q: 如何汇报进度？**
A: 每日20:00通过CC消息发送进度到 `.shared/messages/queue/<你的节点>/inbox/`

**Q: 如何查看其他节点的进度？**
A: 访问仪表盘 http://60.205.139.51:8080/drug_discovery_dashboard.html

**Q: 遇到问题怎么办？**
A: 发送CC消息到 `zhugema/inbox/` 请求帮助。

---

*最后更新：2026-07-09*
