#!/usr/bin/env python3
# 知识图谱构建脚本
import json
import os
from datetime import datetime

def build_knowledge_graph():
    """构建过敏原-靶点-药物知识图谱"""
    kg = {
        "metadata": {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "nodes": 0,
            "edges": 0
        },
        "allergens": [],
        "targets": [],
        "drugs": [],
        "relationships": []
    }
    
    # 添加过敏原节点
    allergens = ["花生", "牛奶", "鸡蛋", "坚果", "鱼类", "甲壳类", "大豆", "小麦"]
    for allergen in allergens:
        kg["allergens"].append({
            "id": f"allergen_{allergen}",
            "name": allergen,
            "type": "allergen"
        })
        kg["metadata"]["nodes"] += 1
    
    # 添加靶点节点
    targets = ["IL-4Rα", "IgE", "TSLP", "IL-33", "FOXP3", "FcεRI", "IL-5", "IL-13", "STAT6", "GATA3"]
    for target in targets:
        kg["targets"].append({
            "id": f"target_{target}",
            "name": target,
            "type": "target"
        })
        kg["metadata"]["nodes"] += 1
    
    # 添加药物节点
    drugs = ["奥马珠单抗", "度普利尤单抗", "特泽佩鲁单抗", "Etokimab", "美泊利珠单抗", "来瑞珠单抗"]
    for drug in drugs:
        kg["drugs"].append({
            "id": f"drug_{drug}",
            "name": drug,
            "type": "drug"
        })
        kg["metadata"]["nodes"] += 1
    
    # 添加关系
    relationships = [
        {"source": "allergen_花生", "target": "target_IgE", "type": "induces"},
        {"source": "target_IgE", "target": "drug_奥马珠单抗", "type": "targeted_by"},
        {"source": "allergen_牛奶", "target": "target_IL-4Rα", "type": "induces"},
        {"source": "target_IL-4Rα", "target": "drug_度普利尤单抗", "type": "targeted_by"}
    ]
    kg["relationships"] = relationships
    kg["metadata"]["edges"] = len(relationships)
    
    # 保存
    output_path = "/home/admin/lobster-network/domains/drug-discovery/data/knowledge_graph_v1.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(kg, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 知识图谱已构建: {output_path}")
    print(f"   节点数: {kg['metadata']['nodes']}")
    print(f"   关系数: {kg['metadata']['edges']}")

if __name__ == "__main__":
    build_knowledge_graph()
