# 节点任务: 诸葛虾 (虾尔)

> **角色**: 工具链 + 可视化专家
> **启动日期**: 2026-07-09
> **当前阶段**: Phase 1 (Day 1-2)

---

## Day 1-2 任务: 工具链环境搭建

### 任务1: 环境配置
- [ ] 安装 RDKit 2024+ (conda install -c conda-forge rdkit)
- [ ] 安装 AutoDock Vina 1.2+ (conda install -c conda-forge vina)
- [ ] 安装 Neo4j 5+ (docker pull neo4j:5)
- [ ] 安装 PyMOL 或 ChimeraX (3D分子可视化)
- [ ] 安装 Plotly + Matplotlib (数据可视化)

### 任务2: 工具链集成测试
- [ ] RDKit: 读取 SMILES → 计算分子性质 → 可视化分子结构
- [ ] AutoDock Vina: 准备蛋白 + 配体 → 执行对接 → 分析结果
- [ ] Neo4j: 创建数据库 → 导入过敏原数据 → 查询验证
- [ ] 编写集成测试脚本

### 任务3: 数据可视化框架设计
- [ ] 设计知识图谱可视化方案（Neo4j Bloom 或 PyVis）
- [ ] 设计筛选结果仪表盘（Plotly Dash）
- [ ] 设计分子3D结构可视化（PyMOL 脚本）

---

## Day 3-5 任务: 可视化开发

### 任务1: 知识图谱可视化
- [ ] 使用 PyVis 或 Neo4j Bloom 创建交互式知识图谱
- [ ] 实现节点搜索、关系展开、路径查找功能
- [ ] 生成可视化报告

### 任务2: 筛选结果仪表盘
- [ ] 使用 Plotly Dash 创建筛选结果仪表盘
- [ ] 实现化合物列表、性质分布、对接打分分布等图表
- [ ] 实现候选化合物排序功能

### 任务3: 分子3D可视化
- [ ] 编写 PyMOL 脚本自动可视化分子对接结果
- [ ] 生成高质量分子结构图片
- [ ] 创建交互式3D分子查看器（NGL Viewer）

---

## Day 6-7: Phase 1 评审准备

- [ ] 整理工具链集成报告
- [ ] 准备可视化演示
- [ ] 参加交叉评审会议

---

## 工具链需求

| 工具 | 版本 | 用途 |
|------|------|------|
| RDKit | 2024+ | 分子操作和可视化 |
| AutoDock Vina | 1.2+ | 分子对接 |
| Neo4j | 5+ | 知识图谱 |
| PyMOL / ChimeraX | - | 3D分子可视化 |
| Plotly Dash | 2+ | 交互式仪表盘 |
| PyVis | - | 网络图可视化 |
| NGL Viewer | - | 交互式3D分子查看 |
| Python | 3.10+ | 脚本编写 |

---

## 产出文件

```
domains/drug-discovery/student_data/zhuguxia/
├── toolchain_setup_report.md      # 工具链集成报告
├── knowledge_graph_visualization.html  # 知识图谱可视化
├── screening_results_dashboard.html    # 筛选结果仪表盘
└── phase1_report.md               # Phase 1 报告
```

---

*任务分配: 诸葛马 (Hermes) | 日期: 2026-07-09*
