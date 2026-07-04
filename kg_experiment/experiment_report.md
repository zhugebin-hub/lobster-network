# 大数据与知识图谱实验报告

**实验名称：** 基于医疗领域的知识图谱构建与应用

**学生姓名：** 陈政道

**实验日期：** 2026 年 4 月 5 日

**实验平台：** Python 3.x + D3.js

---

## 一、实验目的

1. 理解知识图谱的基本概念和结构
2. 掌握知识图谱的构建方法和技术
3. 实现简单的实体识别和关系抽取功能
4. 完成知识图谱的可视化展示
5. 探索知识图谱在实际场景中的应用

---

## 二、实验环境

### 2.1 硬件环境

| 项目 | 配置 |
|------|------|
| 服务器 | 阿里云 ECS |
| 操作系统 | Linux 5.10.134-19.2.al8.x86_64 |
| 内存 | 8GB |
| 存储 | 50GB |

### 2.2 软件环境

| 项目 | 版本 |
|------|------|
| Python | 3.x |
| D3.js | v7 |
| 浏览器 | Chrome/Edge |

### 2.3 开发工具

- 代码编辑器：VS Code
- 版本控制：Git
- 数据处理：Python 标准库

---

## 三、实验原理

### 3.1 知识图谱概述

知识图谱（Knowledge Graph）是一种结构化的语义知识库，用于描述现实世界中的实体、概念及其关系。它以图的形式组织知识，其中：

- **节点（Node）**：表示实体或概念
- **边（Edge）**：表示实体之间的关系

### 3.2 知识图谱的构成要素

1. **实体（Entity）**：客观存在并可相互区分的事物
2. **关系（Relation）**：实体之间的语义联系
3. **属性（Property）**：实体的特征描述

### 3.3 技术架构

```
┌─────────────────────────────────────┐
│           应用层                      │
│   智能问答 | 推荐系统 | 语义搜索      │
├─────────────────────────────────────┤
│           查询层                      │
│   SPARQL | Cypher | 自定义查询引擎   │
├─────────────────────────────────────┤
│           存储层                      │
│   Neo4j | RDF | JSON/图数据库        │
├─────────────────────────────────────┤
│           构建层                      │
│   实体识别 | 关系抽取 | 知识融合      │
├─────────────────────────────────────┤
│           数据层                      │
│   结构化数据 | 半结构化 | 非结构化    │
└─────────────────────────────────────┘
```

---

## 四、实验内容

### 4.1 知识图谱构建

#### 4.1.1 领域选择

本次实验选择**医疗领域**作为知识图谱的应用场景，原因如下：

1. 医疗领域数据结构化程度高
2. 实体和关系定义清晰
3. 具有实际应用价值
4. 便于演示知识图谱的核心功能

#### 4.1.2 实体设计

设计以下 6 类实体：

| 实体类型 | 数量 | 示例 |
|---------|------|------|
| 疾病 | 3 | 糖尿病、高血压、冠心病 |
| 症状 | 5 | 多饮、多食、多尿、头痛、胸痛 |
| 药品 | 4 | 二甲双胍、胰岛素、硝苯地平、阿司匹林 |
| 检查 | 4 | 空腹血糖、糖化血红蛋白、血压测量、心电图 |
| 科室 | 2 | 内分泌科、心血管科 |
| 医生 | 2 | 张医生、李医生 |

#### 4.1.3 关系设计

设计以下 5 类关系：

| 关系类型 | 含义 | 示例 |
|---------|------|------|
| has_symptom | 疾病具有症状 | 糖尿病 → 多饮 |
| treated_by | 疾病被药品治疗 | 糖尿病 → 二甲双胍 |
| requires_test | 疾病需要检查 | 糖尿病 → 空腹血糖 |
| belongs_to_dept | 疾病属于科室 | 糖尿病 → 内分泌科 |
| has_doctor | 科室有医生 | 内分泌科 → 张医生 |

### 4.2 核心功能实现

#### 4.2.1 知识图谱类

```python
class KnowledgeGraph:
    def __init__(self, name):
        self.name = name
        self.entities = {}  # 实体集合
        self.relations = []  # 关系集合
        self.properties = {}  # 实体属性
    
    def add_entity(self, entity_id, entity_type, name, description):
        """添加实体"""
        self.entities[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "description": description
        }
    
    def add_relation(self, from_entity, relation_type, to_entity):
        """添加关系"""
        self.relations.append({
            "from": from_entity,
            "type": relation_type,
            "to": to_entity
        })
```

#### 4.2.2 查询引擎

实现以下查询功能：

1. **根据疾病查找症状**
2. **根据疾病查找药品**
3. **根据疾病查找科室**
4. **实体路径查询**

```python
def find_symptoms_by_disease(self, disease_name):
    """根据疾病查找症状"""
    disease_id = self._find_entity_by_name(disease_name, "疾病")
    symptoms = []
    for rel in self.kg.relations:
        if rel["from"] == disease_id and rel["type"] == "has_symptom":
            symptom = self.kg.entities.get(rel["to"])
            if symptom:
                symptoms.append(symptom["name"])
    return symptoms
```

#### 4.2.3 文本处理与实体识别

实现简单的基于词典的实体识别：

```python
def extract_entities(self, text):
    """从文本中提取实体"""
    found_entities = []
    for name, eid in self.entity_names.items():
        if name in text:
            entity = self.kg.entities[eid]
            found_entities.append({
                "name": name,
                "type": entity["type"],
                "id": eid
            })
    return found_entities
```

#### 4.2.4 症状分析与疾病推测

根据患者描述的症状，推测可能的疾病：

```python
def suggest_diseases(self, symptoms):
    """根据症状推测可能的疾病"""
    disease_scores = {}
    for symptom in symptoms:
        symptom_id = symptom["id"]
        for rel in self.kg.relations:
            if rel["to"] == symptom_id and rel["type"] == "has_symptom":
                disease_id = rel["from"]
                disease_scores[disease_id] = disease_scores.get(disease_id, 0) + 1
    return sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
```

### 4.3 可视化实现

使用 D3.js 实现力导向图可视化：

```javascript
const simulation = d3.forceSimulation(data.nodes)
    .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));
```

---

## 五、实验结果

### 5.1 知识图谱统计

| 指标 | 数值 |
|------|------|
| 实体总数 | 20 |
| 关系总数 | 18 |
| 实体类型 | 6 |
| 关系类型 | 5 |

### 5.2 实体类型分布

```
疾病：3    症状：5    药品：4
检查：4    科室：2    医生：2
```

### 5.3 关系类型分布

```
has_symptom: 5     treated_by: 4
requires_test: 4   belongs_to_dept: 3
has_doctor: 2
```

### 5.4 功能测试结果

#### 测试 1：糖尿病查询

```
疾病：糖尿病
  症状：多饮，多食，多尿
  药品：二甲双胍 (用法：500mg bid), 胰岛素 (用法：遵医嘱)
  科室：内分泌科
```

#### 测试 2：实体识别

```
患者描述：患者最近出现多饮、多尿症状，伴有头痛，怀疑有糖尿病或高血压

识别实体：
  - 糖尿病 (疾病)
  - 高血压 (疾病)
  - 多饮 (症状)
  - 多尿 (症状)
  - 头痛 (症状)

识别症状：多饮，多尿，头痛

可能疾病：
  - 糖尿病 (匹配度 2)
  - 高血压 (匹配度 1)
```

### 5.5 可视化展示

生成了交互式知识图谱可视化页面，包含：

1. **力导向网络图** - 展示实体和关系的空间分布
2. **统计面板** - 显示图谱的基本统计信息
3. **图例** - 不同颜色代表不同实体类型
4. **实体列表** - 表格形式展示所有实体信息
5. **交互功能** - 节点拖拽、悬停提示

---

## 六、实验心得

### 6.1 技术收获

1. **理解了知识图谱的核心概念**
   - 实体、关系、属性的三元组模型
   - 图结构的数据组织方式
   - 知识表示与推理的基本原理

2. **掌握了知识图谱构建流程**
   - 领域建模与本体设计
   - 数据采集与清洗
   - 实体识别与关系抽取
   - 知识存储与查询

3. **学习了可视化技术**
   - D3.js 力导向图布局
   - 交互式图表设计
   - 数据驱动的可视化方法

### 6.2 实践体会

1. **知识图谱的价值**
   - 结构化知识便于机器理解
   - 支持复杂的关系查询
   - 可实现智能推理和应用

2. **构建的挑战**
   - 实体对齐和消歧困难
   - 关系抽取需要大量标注数据
   - 知识更新和维护成本高

3. **应用场景广阔**
   - 智能问答系统
   - 个性化推荐
   - 语义搜索
   - 决策支持

### 6.3 改进方向

1. **扩展实体和关系**
   - 增加更多疾病种类
   - 添加药物相互作用关系
   - 引入基因和生物标志物

2. **改进识别算法**
   - 使用深度学习模型（如 BERT）
   - 实现上下文感知的实体识别
   - 支持模糊匹配和同义词

3. **增强查询功能**
   - 支持 SPARQL 查询语言
   - 实现图神经网络推理
   - 添加自然语言查询接口

4. **优化可视化**
   - 支持大规模图谱渲染
   - 添加时间维度展示
   - 实现多层次钻取分析

---

## 七、参考资料

1. 刘峤等。知识图谱构建技术综述 [J]. 计算机研究与发展，2016.
2. 赵军。知识图谱 [M]. 北京：清华大学出版社，2018.
3. D3.js 官方文档。https://d3js.org/
4. Neo4j 图数据库。https://neo4j.com/
5. 阿里云天池数据集。https://tianchi.aliyun.com/dataset/

---

## 八、附录

### 附录 A：核心代码文件

| 文件名 | 说明 |
|--------|------|
| kg_main.py | 知识图谱主程序 |
| visualization.html | 可视化页面 |
| knowledge_graph.json | 知识图谱数据 |
| visualization_data.json | 可视化数据 |
| statistics.json | 统计数据 |

### 附录 B：运行说明

```bash
# 1. 进入实验目录
cd /home/admin/.openclaw/workspace/kg_experiment

# 2. 运行主程序
python3 kg_main.py

# 3. 打开可视化页面
# 在浏览器中打开 visualization.html
```

### 附录 C：实验截图

（见可视化页面 visualization.html）

---

**报告完成时间：** 2026 年 4 月 5 日

**指导教师：** _______________

**成绩：** _______________
