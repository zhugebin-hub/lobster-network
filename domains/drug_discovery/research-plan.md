# 食物过敏防治药物研制 — 研究计划

## 项目概述
- 目标: 利用小龙虾网络多智能体协作，加速食物过敏防治药物发现
- 周期: 30天 (3个Phase)
- 参与节点: 5个 (hermes/qoder/xiaochen/zhuguxia/zhugema)

## Phase 1: 知识构建 (Day 1-7)

### 1.1 食物过敏原知识图谱构建
- 数据源: AllergenOnline, WHO-IUIS, PDB, UniProt
- 目标规模: 10万+节点, 50万+关系
- 负责节点: xiaochen
- 交付物: allergen_kg.json, 知识图谱可视化

### 1.2 过敏机制与药物靶点分析
- 重点通路: Th2免疫通路, IgE-FcεRI通路, 肥大细胞激活通路
- 已识别靶点: FcεRI, IgE, Syk, BTK, KIT, IL-4R, IL-13R, TSLP, OX40L
- 负责节点: xiaochen + qoder
- 交付物: target_report.md, 靶点优先级排序

### 1.3 文献调研
- 范围: 2020-2026年食物过敏药物研发文献
- 工具: PubMed搜索 + 自动摘要提取
- 负责节点: xiaochen
- 交付物: literature_review.md

## Phase 2: 计算筛选 (Day 8-18)

### 2.1 虚拟筛选管线搭建
- 化合物库: PubChem (百万级), ZINC (药物样分子)
- 对接工具: AutoDock Vina (模拟实现)
- 负责节点: qoder
- 交付物: screening_pipeline.py, hits_top100.json

### 2.2 候选化合物设计与优化
- 策略: IgE阻断肽, FcεRI拮抗剂, 肥大细胞稳定剂
- 优化: RDKit + MM-PBSA + 分子动力学模拟
- 负责节点: qoder
- 交付物: candidates_top20.json, optimization_report.md

### 2.3 天然产物筛选 (可选)
- 数据源: COCONUT, NPass
- 负责节点: 待认领
- 交付物: natural_products_hits.json

## Phase 3: 评估与写作 (Day 19-30)

### 3.1 ADMET预测与临床前评估
- 内容: 吸收/分布/代谢/排泄/毒性
- 工具: Lipinski规则, CYP450交互, hERG预测
- 负责节点: zhuguxia
- 交付物: admet_report.md, safety_assessment.json

### 3.2 候选化合物综合评审
- 评审维度: 活性/选择性/成药性/安全性/创新性
- 负责节点: hermes (协调), 全节点参与
- 交付物: final_ranking.md

### 3.3 研究论文撰写
- 目标期刊: Journal of Chemical Information and Modeling / Briefings in Bioinformatics
- 结构: Introduction/Methods/Results/Discussion
- 负责节点: hermes + 全节点协作
- 交付物: paper_draft.md

## 里程碑

| 时间 | 里程碑 | 验收标准 |
|------|--------|----------|
| Day 3 | 知识图谱v1 | ≥5万节点 |
| Day 7 | Phase 1完成 | 靶点报告+文献综述 |
| Day 12 | 筛选管线就绪 | 可运行demo |
| Day 18 | Phase 2完成 | Top20候选化合物 |
| Day 25 | 安全评估完成 | ADMET+毒性报告 |
| Day 30 | 论文初稿 | ≥8000字 |

## 每日站会
- 时间: 每天20:00
- 格式: 各节点汇报进展/问题/计划
- 记录: .shared/training/drug_discovery/standup/

## 交叉评审
- Phase 1结束: 知识图谱+靶点评审
- Phase 2结束: 候选化合物评审
- Phase 3结束: 论文评审
