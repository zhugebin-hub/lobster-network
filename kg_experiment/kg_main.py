#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱构建与可视化实验
实验名称：基于医疗领域的知识图谱构建与应用
实验者：陈政道
日期：2026 年 4 月 5 日
"""

import json
import os
from datetime import datetime

# ==================== 第一部分：知识图谱数据定义 ====================

class KnowledgeGraph:
    """简单的知识图谱类"""
    
    def __init__(self, name="医疗知识图谱"):
        self.name = name
        self.entities = {}  # 实体集合
        self.relations = []  # 关系集合
        self.properties = {}  # 实体属性
        
    def add_entity(self, entity_id, entity_type, name, description=""):
        """添加实体"""
        self.entities[entity_id] = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "description": description
        }
        return entity_id
    
    def add_relation(self, from_entity, relation_type, to_entity):
        """添加关系"""
        self.relations.append({
            "from": from_entity,
            "type": relation_type,
            "to": to_entity
        })
        
    def add_property(self, entity_id, prop_name, prop_value):
        """添加实体属性"""
        if entity_id not in self.properties:
            self.properties[entity_id] = {}
        self.properties[entity_id][prop_name] = prop_value
        
    def query_by_type(self, entity_type):
        """按类型查询实体"""
        return [e for e in self.entities.values() if e["type"] == entity_type]
    
    def query_relations(self, entity_id):
        """查询实体的所有关系"""
        return [r for r in self.relations if r["from"] == entity_id or r["to"] == entity_id]
    
    def to_json(self):
        """导出为 JSON"""
        return {
            "name": self.name,
            "created_at": datetime.now().isoformat(),
            "entities": self.entities,
            "relations": self.relations,
            "properties": self.properties
        }


# ==================== 第二部分：构建医疗知识图谱 ====================

def build_medical_kg():
    """构建医疗领域知识图谱"""
    kg = KnowledgeGraph("医疗知识图谱")
    
    # --- 添加疾病实体 ---
    kg.add_entity("D001", "疾病", "糖尿病", "一种慢性代谢性疾病")
    kg.add_entity("D002", "疾病", "高血压", "血压持续升高的慢性疾病")
    kg.add_entity("D003", "疾病", "冠心病", "冠状动脉粥样硬化性心脏病")
    
    # --- 添加症状实体 ---
    kg.add_entity("S001", "症状", "多饮", "饮水量异常增多")
    kg.add_entity("S002", "症状", "多食", "食欲亢进")
    kg.add_entity("S003", "症状", "多尿", "排尿次数和尿量增多")
    kg.add_entity("S004", "症状", "头痛", "头部疼痛感")
    kg.add_entity("S005", "症状", "胸痛", "胸部疼痛或不适")
    
    # --- 添加药品实体 ---
    kg.add_entity("M001", "药品", "二甲双胍", "治疗 2 型糖尿病的一线药物")
    kg.add_entity("M002", "药品", "胰岛素", "调节血糖的激素类药物")
    kg.add_entity("M003", "药品", "硝苯地平", "钙通道阻滞剂，用于治疗高血压")
    kg.add_entity("M004", "药品", "阿司匹林", "抗血小板药物")
    
    # --- 添加检查项目实体 ---
    kg.add_entity("T001", "检查", "空腹血糖", "测量空腹状态下的血糖水平")
    kg.add_entity("T002", "检查", "糖化血红蛋白", "反映 2-3 个月平均血糖水平")
    kg.add_entity("T003", "检查", "血压测量", "测量收缩压和舒张压")
    kg.add_entity("T004", "检查", "心电图", "记录心脏电活动")
    
    # --- 添加科室实体 ---
    kg.add_entity("DEPT001", "科室", "内分泌科", "诊治内分泌系统疾病")
    kg.add_entity("DEPT002", "科室", "心血管科", "诊治心血管疾病")
    
    # --- 添加医生实体 ---
    kg.add_entity("DOC001", "医生", "张医生", "内分泌科主任医师")
    kg.add_entity("DOC002", "医生", "李医生", "心血管科副主任医师")
    
    # --- 建立关系 ---
    # 疾病 - 症状关系
    kg.add_relation("D001", "has_symptom", "S001")
    kg.add_relation("D001", "has_symptom", "S002")
    kg.add_relation("D001", "has_symptom", "S003")
    kg.add_relation("D002", "has_symptom", "S004")
    kg.add_relation("D003", "has_symptom", "S005")
    
    # 疾病 - 药品关系
    kg.add_relation("D001", "treated_by", "M001")
    kg.add_relation("D001", "treated_by", "M002")
    kg.add_relation("D002", "treated_by", "M003")
    kg.add_relation("D003", "treated_by", "M004")
    
    # 疾病 - 检查关系
    kg.add_relation("D001", "requires_test", "T001")
    kg.add_relation("D001", "requires_test", "T002")
    kg.add_relation("D002", "requires_test", "T003")
    kg.add_relation("D003", "requires_test", "T004")
    
    # 疾病 - 科室关系
    kg.add_relation("D001", "belongs_to_dept", "DEPT001")
    kg.add_relation("D002", "belongs_to_dept", "DEPT002")
    kg.add_relation("D003", "belongs_to_dept", "DEPT002")
    
    # 科室 - 医生关系
    kg.add_relation("DEPT001", "has_doctor", "DOC001")
    kg.add_relation("DEPT002", "has_doctor", "DOC002")
    
    # --- 添加实体属性 ---
    kg.add_property("D001", "icd10", "E14")
    kg.add_property("D001", "prevalence", "10.9%")
    kg.add_property("M001", "dosage", "500mg bid")
    kg.add_property("M001", "side_effects", "胃肠道反应")
    kg.add_property("T001", "normal_range", "3.9-6.1 mmol/L")
    kg.add_property("T003", "normal_range", "<140/90 mmHg")
    
    return kg


# ==================== 第三部分：知识图谱查询功能 ====================

class KGQueryEngine:
    """知识图谱查询引擎"""
    
    def __init__(self, kg):
        self.kg = kg
        
    def find_symptoms_by_disease(self, disease_name):
        """根据疾病查找症状"""
        disease_id = self._find_entity_by_name(disease_name, "疾病")
        if not disease_id:
            return []
        
        symptoms = []
        for rel in self.kg.relations:
            if rel["from"] == disease_id and rel["type"] == "has_symptom":
                symptom = self.kg.entities.get(rel["to"])
                if symptom:
                    symptoms.append(symptom["name"])
        return symptoms
    
    def find_medicines_by_disease(self, disease_name):
        """根据疾病查找药品"""
        disease_id = self._find_entity_by_name(disease_name, "疾病")
        if not disease_id:
            return []
        
        medicines = []
        for rel in self.kg.relations:
            if rel["from"] == disease_id and rel["type"] == "treated_by":
                medicine = self.kg.entities.get(rel["to"])
                if medicine:
                    med_name = medicine["name"]
                    # 获取药品属性
                    dosage = self.kg.properties.get(rel["to"], {}).get("dosage", "遵医嘱")
                    medicines.append(f"{med_name} (用法：{dosage})")
        return medicines
    
    def find_department_by_disease(self, disease_name):
        """根据疾病查找就诊科室"""
        disease_id = self._find_entity_by_name(disease_name, "疾病")
        if not disease_id:
            return None
        
        for rel in self.kg.relations:
            if rel["from"] == disease_id and rel["type"] == "belongs_to_dept":
                dept = self.kg.entities.get(rel["to"])
                if dept:
                    return dept["name"]
        return None
    
    def _find_entity_by_name(self, name, entity_type=None):
        """根据名称查找实体 ID"""
        for eid, entity in self.kg.entities.items():
            if entity["name"] == name:
                if entity_type is None or entity["type"] == entity_type:
                    return eid
        return None
    
    def query_path(self, from_name, to_name):
        """查询两个实体之间的路径"""
        from_id = self._find_entity_by_name(from_name)
        to_id = self._find_entity_by_name(to_name)
        
        if not from_id or not to_id:
            return None
        
        # 简单的 BFS 查找路径
        from collections import deque
        queue = deque([(from_id, [from_id])])
        visited = {from_id}
        
        while queue:
            current, path = queue.popleft()
            if current == to_id:
                return [self.kg.entities[eid]["name"] for eid in path]
            
            for rel in self.kg.relations:
                next_id = None
                if rel["from"] == current and rel["to"] not in visited:
                    next_id = rel["to"]
                elif rel["to"] == current and rel["from"] not in visited:
                    next_id = rel["from"]
                
                if next_id:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))
        
        return None


# ==================== 第四部分：文本处理与实体识别 ====================

class TextProcessor:
    """文本处理与简单实体识别"""
    
    def __init__(self, kg):
        self.kg = kg
        self.entity_names = {e["name"]: eid for eid, e in kg.entities.items()}
    
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
    
    def analyze_symptoms(self, patient_description):
        """分析患者描述中的症状"""
        entities = self.extract_entities(patient_description)
        symptoms = [e for e in entities if e["type"] == "症状"]
        return symptoms
    
    def suggest_diseases(self, symptoms):
        """根据症状推测可能的疾病"""
        disease_scores = {}
        
        for symptom in symptoms:
            symptom_id = symptom["id"]
            # 查找有该症状的疾病
            for rel in self.kg.relations:
                if rel["to"] == symptom_id and rel["type"] == "has_symptom":
                    disease_id = rel["from"]
                    disease_scores[disease_id] = disease_scores.get(disease_id, 0) + 1
        
        # 按匹配症状数排序
        sorted_diseases = sorted(disease_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for disease_id, score in sorted_diseases:
            disease = self.kg.entities.get(disease_id)
            if disease:
                results.append({
                    "disease": disease["name"],
                    "match_score": score
                })
        
        return results


# ==================== 第五部分：生成可视化数据 ====================

def generate_visualization_data(kg):
    """生成用于可视化的数据"""
    nodes = []
    links = []
    
    # 颜色映射
    color_map = {
        "疾病": "#ff6b6b",
        "症状": "#4ecdc4",
        "药品": "#45b7d1",
        "检查": "#96ceb4",
        "科室": "#ffeaa7",
        "医生": "#dfe6e9"
    }
    
    # 生成节点
    for eid, entity in kg.entities.items():
        nodes.append({
            "id": eid,
            "name": entity["name"],
            "type": entity["type"],
            "color": color_map.get(entity["type"], "#999999"),
            "description": entity["description"]
        })
    
    # 生成关系边
    for rel in kg.relations:
        links.append({
            "source": rel["from"],
            "target": rel["to"],
            "type": rel["type"]
        })
    
    return {"nodes": nodes, "links": links}


def generate_statistics(kg):
    """生成统计信息"""
    stats = {
        "total_entities": len(kg.entities),
        "total_relations": len(kg.relations),
        "entity_types": {},
        "relation_types": {}
    }
    
    # 统计实体类型
    for entity in kg.entities.values():
        etype = entity["type"]
        stats["entity_types"][etype] = stats["entity_types"].get(etype, 0) + 1
    
    # 统计关系类型
    for rel in kg.relations:
        rtype = rel["type"]
        stats["relation_types"][rtype] = stats["relation_types"].get(rtype, 0) + 1
    
    return stats


# ==================== 第六部分：主程序 ====================

def main():
    """主程序入口"""
    print("=" * 60)
    print("知识图谱构建与可视化实验")
    print("实验者：陈政道")
    print("日期：2026 年 4 月 5 日")
    print("=" * 60)
    print()
    
    # 1. 构建知识图谱
    print("【步骤 1】构建医疗知识图谱...")
    kg = build_medical_kg()
    print(f"✓ 实体数量：{len(kg.entities)}")
    print(f"✓ 关系数量：{len(kg.relations)}")
    print()
    
    # 2. 创建查询引擎
    print("【步骤 2】创建查询引擎...")
    query_engine = KGQueryEngine(kg)
    
    # 测试查询功能
    print("\n【查询测试】")
    disease = "糖尿病"
    print(f"\n疾病：{disease}")
    print(f"  症状：{', '.join(query_engine.find_symptoms_by_disease(disease))}")
    print(f"  药品：{', '.join(query_engine.find_medicines_by_disease(disease))}")
    print(f"  科室：{query_engine.find_department_by_disease(disease)}")
    
    # 3. 文本处理与实体识别
    print("\n【步骤 3】文本处理与实体识别...")
    text_processor = TextProcessor(kg)
    
    patient_text = "患者最近出现多饮、多尿症状，伴有头痛，怀疑有糖尿病或高血压"
    print(f"\n患者描述：{patient_text}")
    
    entities = text_processor.extract_entities(patient_text)
    print(f"识别实体：{[(e['name'], e['type']) for e in entities]}")
    
    symptoms = text_processor.analyze_symptoms(patient_text)
    print(f"识别症状：{[s['name'] for s in symptoms]}")
    
    suggestions = text_processor.suggest_diseases(symptoms)
    print(f"可能疾病：{[(s['disease'], '匹配度'+str(s['match_score'])) for s in suggestions]}")
    
    # 4. 生成可视化数据
    print("\n【步骤 4】生成可视化数据...")
    viz_data = generate_visualization_data(kg)
    print(f"✓ 节点数：{len(viz_data['nodes'])}")
    print(f"✓ 边数：{len(viz_data['links'])}")
    
    # 5. 生成统计信息
    print("\n【步骤 5】生成统计信息...")
    stats = generate_statistics(kg)
    print(f"实体类型分布：{stats['entity_types']}")
    print(f"关系类型分布：{stats['relation_types']}")
    
    # 6. 保存数据
    print("\n【步骤 6】保存实验数据...")
    
    # 保存知识图谱 JSON
    kg_data = kg.to_json()
    with open("knowledge_graph.json", "w", encoding="utf-8") as f:
        json.dump(kg_data, f, ensure_ascii=False, indent=2)
    print("✓ 知识图谱数据已保存：knowledge_graph.json")
    
    # 保存可视化数据
    with open("visualization_data.json", "w", encoding="utf-8") as f:
        json.dump(viz_data, f, ensure_ascii=False, indent=2)
    print("✓ 可视化数据已保存：visualization_data.json")
    
    # 保存统计数据
    with open("statistics.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print("✓ 统计数据已保存：statistics.json")
    
    print("\n" + "=" * 60)
    print("实验完成！")
    print("=" * 60)
    
    return kg, query_engine, text_processor, viz_data, stats


if __name__ == "__main__":
    main()
