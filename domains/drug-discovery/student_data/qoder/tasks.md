# 节点任务: qoder (小龙虾)

> **角色**: 计算化学专家
> **启动日期**: 2026-07-09
> **当前阶段**: Phase 1 (Day 1-2)

---

## Day 1-2 任务: 过敏原知识图谱搭建

### 任务1: 数据收集
- [ ] 从 AllergenOnline 下载过敏原序列数据
- [ ] 从 WHO/IUIS 获取过敏原命名数据
- [ ] 从 PDB 下载过敏原三维结构
- [ ] 整理八大过敏原的完整信息（见 allergen-database.md）

### 任务2: 知识图谱本体设计
- [ ] 设计 Neo4j 本体模型
  - Allergen 节点: name, source, sequence, mw, stability
  - Epitope 节点: type (linear/conformational), sequence, position
  - CrossReactivity 边: allergen1 → allergen2, confidence
  - Target 节点: name, gene, type, approved_drugs
  - Compound 节点: name, smiles, mw, logp, activity

### 任务3: 数据导入
- [ ] 编写 Python 脚本导入数据到 Neo4j
- [ ] 验证数据完整性和一致性
- [ ] 生成知识图谱统计报告

---

## Day 3-5 任务: 虚拟筛选管线搭建

### 任务1: 化合物库准备
- [ ] 从 PubChem 下载化合物库（SDF格式）
- [ ] 从 ZINC20 下载可购买化合物
- [ ] 使用 RDKit 进行化合物预处理
  - 标准化 SMILES
  - 计算分子性质（MW, LogP, HBD, HBA）
  - 应用 Lipinski 类药性规则过滤

### 任务2: 分子对接准备
- [ ] 下载靶点蛋白结构（PDB）
  - IgE: PDB 3HVR, 2OFP
  - IL-4Rα: PDB 2R68
  - TSLP: PDB 4JHB
- [ ] 准备对接网格文件
- [ ] 验证对接参数（对接精度测试）

### 任务3: 虚拟筛选执行
- [ ] 编写批量对接脚本
- [ ] 执行 AutoDock Vina 对接
- [ ] 收集对接打分结果
- [ ] 生成 Top 100 候选化合物列表

---

## Day 6-7: Phase 1 评审准备

- [ ] 整理知识图谱统计报告
- [ ] 准备虚拟筛选管线演示
- [ ] 参加交叉评审会议

---

## 工具链需求

| 工具 | 版本 | 用途 |
|------|------|------|
| RDKit | 2024+ | 分子操作和性质计算 |
| AutoDock Vina | 1.2+ | 分子对接 |
| Neo4j | 5+ | 知识图谱存储 |
| Python | 3.10+ | 脚本编写 |
| GROMACS | 2024+ | 分子动力学（后续） |

---

## 产出文件

```
domains/drug-discovery/student_data/qoder/
├── knowledge_graph_report.json    # 知识图谱统计
├── screening_pipeline.py          # 筛选管线脚本
├── top_candidates.csv             # 候选化合物列表
└── phase1_report.md               # Phase 1 报告
```

---

*任务分配: 诸葛马 (Hermes) | 日期: 2026-07-09*
