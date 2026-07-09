# 新药创制科学智能体 — Scientific Agents for Drug Discovery

## 领域概述

**领域名称**: 新药创制科学智能体 (Scientific Agents for Drug Discovery)

**聚焦方向**: 食物过敏防治药物研制 (Food Allergy Prevention and Treatment Drug Development)

**架构基础**: 基于龙虾网络 (Lobster Network) V5.1 六层架构

---

## 架构设计

本领域采用龙虾网络 V5.1 六层架构，将食物过敏药物发现全流程分解为 6 个专业智能体协同工作：

### 六层架构映射

| 层次 | 角色 | 对应组件 |
|------|------|----------|
| L1 感知层 | 数据采集与知识获取 | LiteratureMiningAgent, AllergenTargetAgent |
| L2 理解层 | 靶点识别与验证 | AllergenTargetAgent |
| L3 推理层 | 化合物设计与筛选 | CompoundDesignAgent, VirtualScreeningAgent |
| L4 评估层 | 安全性与成药性评估 | AdmetPredictionAgent, ToxicityAssessmentAgent |
| L5 决策层 | 流水线编排与优化 | DrugDiscoveryPipeline |
| L6 执行层 | 实验验证与反馈 | 工作流闭环（hypothsis -> experiment -> analysis -> optimization）|

---

## 专业智能体

### 1. AllergenTargetAgent — 过敏原靶点发现智能体

- **职责**: 发掘和验证食物过敏治疗靶点
- **核心能力**: IgE 表位分析、FcepsilonRI 受体研究、肥大细胞激活通路解析
- **知识库**: 9 种主要食物过敏原（花生、牛奶、甲壳类、鸡蛋、鱼类、小麦、芝麻、桃子）
- **关键方法**: `discover_targets()`, `validate_target()`, `generate_hypothesis()`

### 2. CompoundDesignAgent — 化合物设计智能体

- **职责**: 设计靶向食物过敏通路的小分子和生物大分子
- **设计策略**:
  - IgE 阻断肽 (IgE blocking peptides)
  - FcepsilonRI 拮抗剂小分子
  - 肥大细胞稳定剂 (类色甘酸钠)
  - 口服免疫治疗佐剂
  - 益生菌代谢物模拟分子
- **关键方法**: `design_compound()`, `optimize_lead()`, `generate_analogs()`

### 3. VirtualScreeningAgent — 虚拟筛选智能体

- **职责**: 化合物库虚拟筛选与分子对接
- **打分函数**: 范德华力 + 静电作用 + 去溶剂化惩罚 + 构象熵
- **关键方法**: `screen_library()`, `dock()`, `rank_hits()`

### 4. AdmetPredictionAgent — ADMET 预测智能体

- **职责**: 预测吸收、分布、代谢、排泄、毒性属性
- **类药性规则**: Lipinski 五规则 (MW<500, LogP<5, HBD<=5, HBA<=10) + Veber 规则 (TPSA<140)
- **CYP 评估**: CYP3A4, CYP2D6, CYP2C9, CYP1A2, CYP2C19
- **关键方法**: `predict_admet()`, `predict_absorption()`, `predict_metabolism()`, `predict_toxicity_basic()`, `filter_drug_likeness()`

### 5. ToxicityAssessmentAgent — 毒性评估智能体

- **职责**: 综合毒性与安全性评估
- **评估维度**: hERG 通道阻断、急性毒性 LD50、脱靶效应、肝毒性
- **脱靶面板**: 10 个安全性相关靶点 (hERG, Nav1.5, 5-HT2B, D2, H1 等)
- **关键方法**: `assess_toxicity()`, `predict_herg()`, `predict_ld50()`, `check_off_target()`, `safety_report()`

### 6. LiteratureMiningAgent — 文献挖掘智能体

- **职责**: 挖掘食物过敏药物发现相关科学文献
- **策展文献**: 10 篇核心参考文献（涵盖 Omalizumab, Dupilumab, BTK 抑制剂等）
- **关键方法**: `search_papers()`, `extract_targets()`, `extract_compounds()`, `trend_analysis()`, `generate_review()`

---

## 知识库

### 过敏原靶点知识库 (`knowledge_base/allergen_targets.json`)

覆盖 9 种 WHO/IUIS 认证的主要食物过敏原和 9 个治疗靶点：

- **过敏原**: Ara h 1/2 (花生), Casein (牛奶), Tropomyosin (甲壳类), Ovalbumin (鸡蛋), Parvalbumin (鱼类), Gliadin (小麦), Ses i 1 (芝麻), Pru p 3 (桃子)
- **治疗靶点**: FcepsilonRI, IgE, Syk, BTK, KIT, IL-4R, IL-13R, TSLP, OX40L
- **通路**: 肥大细胞激活、Th2 极化、IgE 产生、口服免疫耐受

### 化合物知识库 (`knowledge_base/food_allergy_compounds.json`)

- **已上市药物**: Omalizumab (Xolair), Dupilumab (Dupixent), Palforzia (AR101), Viaskin Peanut (DBV712)
- **在研化合物**: BTK 抑制剂, Syk 抑制剂, JAK 抑制剂, CRTh2 拮抗剂
- **天然产物**: 槲皮素 (Quercetin), 白藜芦醇 (Resveratrol), 姜黄素 (Curcumin)

---

## 工作流程

### 药物发现流水线 (`workflows/drug_discovery_pipeline.py`)

```
Hypothesis (假说)
    |
    v
Target ID (靶点识别) --> Literature Review (文献综述)
    |
    v
Compound Design (化合物设计)
    |
    v
Virtual Screening (虚拟筛选)
    |
    v
ADMET Prediction (ADMET 预测)
    |
    v
Toxicity Assessment (毒性评估)
    |
    v
Report (研究报告) --> Optimization Loop (优化迭代)
```

### 闭环迭代

1. **假说生成**: 基于靶点发现和文献综述生成科学假说
2. **计算实验**: 化合物设计、虚拟筛选、ADMET/毒性预测
3. **结果分析**: 综合评估候选化合物的成药性
4. **策略优化**: 根据分析结果调整设计策略，进入下一轮迭代

---

## 目录结构

```
domains/drug_discovery/
├── README.md                           # 本文档
├── agents/
│   ├── __init__.py                     # 智能体模块导出
│   ├── allergen_target_agent.py        # 过敏原靶点发现智能体
│   ├── compound_design_agent.py        # 化合物设计智能体
│   ├── virtual_screening_agent.py      # 虚拟筛选智能体
│   ├── admet_agent.py                  # ADMET 预测智能体
│   ├── toxicity_agent.py              # 毒性评估智能体
│   └── literature_mining_agent.py     # 文献挖掘智能体
├── knowledge_base/
│   ├── allergen_targets.json          # 过敏原与靶点知识库
│   └── food_allergy_compounds.json    # 化合物知识库
├── workflows/
│   ├── __init__.py                    # 工作流模块导出
│   └── drug_discovery_pipeline.py     # 药物发现流水线
└── trainers/
    └── verify_agents.py               # 智能体验证脚本
```

---

## 快速开始

### 运行验证

```bash
# 验证所有智能体
python domains/drug_discovery/trainers/verify_agents.py --all

# 验证单个智能体
python domains/drug_discovery/trainers/verify_agents.py --agent target
python domains/drug_discovery/trainers/verify_agents.py --agent compound

# 运行迷你流水线
python domains/drug_discovery/trainers/verify_agents.py --pipeline
```

### 直接使用智能体

```python
from domains.drug_discovery.agents import AllergenTargetAgent, CompoundDesignAgent

# 靶点发现
target_agent = AllergenTargetAgent()
discovery = target_agent.discover_targets()
validation = target_agent.validate_target("FCE_RI")

# 化合物设计
design_agent = CompoundDesignAgent()
compound = design_agent.design_compound(
    {"target_id": "FCE_RI", "target_name": "FcepsilonRI"},
    "fcepsilonri_antagonist"
)
```

### 运行完整流水线

```python
from domains.drug_discovery.workflows import DrugDiscoveryPipeline

pipeline = DrugDiscoveryPipeline()
report = pipeline.run_pipeline("food allergy drug discovery")
```

---

## 技术特性

- **知识图谱嵌入**: RotatE 512 维概念嵌入用于靶点-过敏原关联分析
- **自包含运行**: 所有模块无需外部 API 调用即可运行演示和验证
- **结构化输出**: 所有智能体返回 JSON 格式结果，含置信度评分
- **日志系统**: 统一日志格式，支持文件和控制台输出
- **类型安全**: 全面使用 Python type hints 和 dataclasses
- **可复现性**: 使用确定性伪随机数生成器，结果可复现
