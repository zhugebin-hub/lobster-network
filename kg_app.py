#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱应用 - 学术领域知识图谱构建与查询
作者：陈怡
日期：2026 年 4 月 2 日
"""

import json
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# ==================== 1. 数据结构定义 ====================

class Entity:
    """实体类 - 表示知识图谱中的节点"""
    def __init__(self, entity_id: str, name: str, entity_type: str, properties: dict = None):
        self.entity_id = entity_id
        self.name = name
        self.entity_type = entity_type  # 如：学者、大学、研究领域、论文
        self.properties = properties or {}
    
    def to_dict(self) -> dict:
        return {
            'entity_id': self.entity_id,
            'name': self.name,
            'entity_type': self.entity_type,
            'properties': self.properties
        }

class Relation:
    """关系类 - 表示知识图谱中的边"""
    def __init__(self, head_entity: str, relation_type: str, tail_entity: str, properties: dict = None):
        self.head_entity = head_entity
        self.relation_type = relation_type  # 如：毕业于、任职于、研究领域、发表论文
        self.tail_entity = tail_entity
        self.properties = properties or {}
    
    def to_dict(self) -> dict:
        return {
            'head_entity': self.head_entity,
            'relation_type': self.relation_type,
            'tail_entity': self.tail_entity,
            'properties': self.properties
        }

# ==================== 2. 知识图谱类 ====================

class KnowledgeGraph:
    """知识图谱类"""
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
        # 索引结构
        self.entity_by_type: Dict[str, Set[str]] = defaultdict(set)
        self.relations_by_head: Dict[str, List[Relation]] = defaultdict(list)
        self.relations_by_tail: Dict[str, List[Relation]] = defaultdict(list)
    
    def add_entity(self, entity: Entity):
        """添加实体"""
        self.entities[entity.entity_id] = entity
        self.entity_by_type[entity.entity_type].add(entity.entity_id)
        print(f"✓ 添加实体：{entity.name} ({entity.entity_type})")
    
    def add_relation(self, relation: Relation):
        """添加关系"""
        self.relations.append(relation)
        self.relations_by_head[relation.head_entity].append(relation)
        self.relations_by_tail[relation.tail_entity].append(relation)
        print(f"✓ 添加关系：{relation.head_entity} --[{relation.relation_type}]--> {relation.tail_entity}")
    
    def get_entity(self, entity_id: str) -> Entity:
        """获取实体"""
        return self.entities.get(entity_id)
    
    def get_neighbors(self, entity_id: str, direction: str = 'out') -> List[Relation]:
        """获取邻居节点（关系）"""
        if direction == 'out':
            return self.relations_by_head.get(entity_id, [])
        elif direction == 'in':
            return self.relations_by_tail.get(entity_id, [])
        else:
            return self.relations_by_head.get(entity_id, []) + self.relations_by_tail.get(entity_id, [])
    
    def query_by_type(self, entity_type: str) -> List[Entity]:
        """按类型查询实体"""
        return [self.entities[eid] for eid in self.entity_by_type.get(entity_type, set())]
    
    def query_relation_path(self, start_entity: str, end_entity: str, max_depth: int = 3) -> List[List[str]]:
        """查询两个实体之间的关系路径（BFS）"""
        from collections import deque
        
        queue = deque([(start_entity, [start_entity])])
        visited = {start_entity}
        paths = []
        
        while queue and len(paths) < 5:  # 最多返回 5 条路径
            current, path = queue.popleft()
            
            if current == end_entity:
                paths.append(path)
                continue
            
            if len(path) > max_depth:
                continue
            
            for relation in self.relations_by_head.get(current, []):
                next_entity = relation.tail_entity
                if next_entity not in visited:
                    visited.add(next_entity)
                    queue.append((next_entity, path + [next_entity]))
        
        return paths
    
    def get_statistics(self) -> dict:
        """获取图谱统计信息"""
        return {
            '实体总数': len(self.entities),
            '关系总数': len(self.relations),
            '实体类型分布': {k: len(v) for k, v in self.entity_by_type.items()},
            '平均关系数': len(self.relations) / len(self.entities) if self.entities else 0
        }
    
    def to_json(self) -> dict:
        """导出为 JSON"""
        return {
            'entities': [e.to_dict() for e in self.entities.values()],
            'relations': [r.to_dict() for r in self.relations]
        }

# ==================== 3. 示例数据构建 ====================

def build_academic_kg() -> KnowledgeGraph:
    """构建学术领域知识图谱"""
    kg = KnowledgeGraph()
    
    print("\n" + "="*60)
    print("正在构建学术领域知识图谱...")
    print("="*60 + "\n")
    
    # --- 添加学者实体 ---
    scholars = [
        Entity("S001", "吴恩达", "学者", {"国籍": "美国", "职位": "教授"}),
        Entity("S002", "李飞飞", "学者", {"国籍": "美国", "职位": "教授"}),
        Entity("S003", "Yann LeCun", "学者", {"国籍": "法国", "职位": "首席 AI 科学家"}),
        Entity("S004", "Geoffrey Hinton", "学者", {"国籍": "英国", "职位": "教授"}),
        Entity("S005", "周志华", "学者", {"国籍": "中国", "职位": "教授"}),
        Entity("S006", "马毅", "学者", {"国籍": "美国", "职位": "教授"}),
    ]
    
    # --- 添加大学实体 ---
    universities = [
        Entity("U001", "斯坦福大学", "大学", {"国家": "美国", "排名": "Top 5"}),
        Entity("U002", "加州大学伯克利分校", "大学", {"国家": "美国", "排名": "Top 10"}),
        Entity("U003", "纽约大学", "大学", {"国家": "美国", "排名": "Top 30"}),
        Entity("U004", "多伦多大学", "大学", {"国家": "加拿大", "排名": "Top 50"}),
        Entity("U005", "南京大学", "大学", {"国家": "中国", "排名": "Top 100"}),
    ]
    
    # --- 添加研究领域实体 ---
    fields = [
        Entity("F001", "深度学习", "研究领域", {"子领域": "神经网络"}),
        Entity("F002", "计算机视觉", "研究领域", {"子领域": "图像识别"}),
        Entity("F003", "自然语言处理", "研究领域", {"子领域": "语言理解"}),
        Entity("F004", "强化学习", "研究领域", {"子领域": "决策优化"}),
        Entity("F005", "机器学习", "研究领域", {"子领域": "模式识别"}),
    ]
    
    # --- 添加论文实体 ---
    papers = [
        Entity("P001", "ImageNet Classification with Deep Convolutional Neural Networks", "论文", {"年份": "2012", "引用": "100000+"}),
        Entity("P002", "Deep Learning", "论文", {"年份": "2015", "引用": "80000+"}),
        Entity("P003", "Attention Is All You Need", "论文", {"年份": "2017", "引用": "100000+"}),
    ]
    
    # 添加所有实体
    for entity in scholars + universities + fields + papers:
        kg.add_entity(entity)
    
    print("\n" + "-"*60)
    print("正在添加关系...")
    print("-"*60 + "\n")
    
    # --- 添加关系 ---
    relations = [
        # 学者 - 大学关系（任职于、毕业于）
        Relation("S001", "任职于", "U001", {"时间": "2002-至今"}),
        Relation("S002", "任职于", "U001", {"时间": "2009-至今"}),
        Relation("S003", "任职于", "U003", {"时间": "2003-至今"}),
        Relation("S004", "任职于", "U004", {"时间": "1987-至今"}),
        Relation("S005", "任职于", "U005", {"时间": "1996-至今"}),
        Relation("S006", "任职于", "U002", {"时间": "2002-至今"}),
        
        # 学者 - 研究领域关系
        Relation("S001", "研究领域", "F001", {}),
        Relation("S001", "研究领域", "F004", {}),
        Relation("S002", "研究领域", "F002", {}),
        Relation("S002", "研究领域", "F001", {}),
        Relation("S003", "研究领域", "F001", {}),
        Relation("S003", "研究领域", "F002", {}),
        Relation("S004", "研究领域", "F001", {}),
        Relation("S004", "研究领域", "F005", {}),
        Relation("S005", "研究领域", "F005", {}),
        Relation("S005", "研究领域", "F001", {}),
        Relation("S006", "研究领域", "F002", {}),
        
        # 学者 - 论文关系
        Relation("S002", "发表论文", "P001", {"作者顺序": "通讯作者"}),
        Relation("S003", "发表论文", "P002", {"作者顺序": "第一作者"}),
        Relation("S004", "发表论文", "P002", {"作者顺序": "第一作者"}),
        
        # 领域 - 领域关系（包含）
        Relation("F005", "包含子领域", "F001", {}),
        Relation("F001", "应用于", "F002", {}),
        Relation("F001", "应用于", "F003", {}),
    ]
    
    for relation in relations:
        kg.add_relation(relation)
    
    return kg

# ==================== 4. 查询与分析功能 ====================

def demo_queries(kg: KnowledgeGraph):
    """演示查询功能"""
    
    print("\n" + "="*60)
    print("知识图谱查询演示")
    print("="*60)
    
    # 查询 1：按类型查询
    print("\n【查询 1】查询所有学者：")
    print("-"*40)
    scholars = kg.query_by_type("学者")
    for s in scholars:
        print(f"  • {s.name} ({s.properties.get('国籍', '未知')})")
    
    # 查询 2：查询某实体的邻居
    print("\n【查询 2】吴恩达的相关关系：")
    print("-"*40)
    relations = kg.get_neighbors("S001", direction='out')
    for r in relations:
        tail_entity = kg.get_entity(r.tail_entity)
        print(f"  • {r.relation_type} → {tail_entity.name}")
    
    # 查询 3：查询关系路径
    print("\n【查询 3】吴恩达 到 计算机视觉 的关系路径：")
    print("-"*40)
    paths = kg.query_relation_path("S001", "F002")
    for i, path in enumerate(paths, 1):
        path_names = [kg.get_entity(eid).name for eid in path]
        print(f"  路径{i}: {' → '.join(path_names)}")
    
    # 查询 4：统计信息
    print("\n【查询 4】知识图谱统计信息：")
    print("-"*40)
    stats = kg.get_statistics()
    for k, v in stats.items():
        print(f"  • {k}: {v}")
    
    # 查询 5：共同研究领域
    print("\n【查询 5】研究深度学习的学者：")
    print("-"*40)
    dl_researchers = kg.relations_by_tail.get("F001", [])
    for r in dl_researchers:
        if r.relation_type == "研究领域":
            scholar = kg.get_entity(r.head_entity)
            print(f"  • {scholar.name} ({scholar.properties.get('职位', '未知')})")

# ==================== 5. 可视化输出 ====================

def export_to_json(kg: KnowledgeGraph, filepath: str):
    """导出为 JSON 文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(kg.to_json(), f, ensure_ascii=False, indent=2)
    print(f"\n✓ 知识图谱已导出到：{filepath}")

def generate_text_visualization(kg: KnowledgeGraph) -> str:
    """生成文本可视化"""
    lines = []
    lines.append("\n" + "="*60)
    lines.append("知识图谱可视化（文本形式）")
    lines.append("="*60)
    
    # 按类型分组显示
    for entity_type, entity_ids in kg.entity_by_type.items():
        lines.append(f"\n【{entity_type}】")
        for eid in entity_ids:
            entity = kg.get_entity(eid)
            lines.append(f"  ○ {entity.name}")
            
            # 显示该实体的出边
            for rel in kg.relations_by_head.get(eid, []):
                tail = kg.get_entity(rel.tail_entity)
                lines.append(f"    └─[{rel.relation_type}]→ {tail.name}")
    
    return "\n".join(lines)

# ==================== 6. 主程序 ====================

def main():
    """主程序"""
    print("\n" + "#"*60)
    print("#  知识图谱应用实验 - 学术领域知识图谱")
    print("#  作者：陈怡")
    print("#  日期：2026 年 4 月 2 日")
    print("#"*60)
    
    # 构建知识图谱
    kg = build_academic_kg()
    
    # 执行查询演示
    demo_queries(kg)
    
    # 文本可视化
    visualization = generate_text_visualization(kg)
    print(visualization)
    
    # 导出到 JSON
    export_to_json(kg, "/home/admin/.openclaw/workspace/kg_data.json")
    
    print("\n" + "="*60)
    print("实验完成！")
    print("="*60 + "\n")
    
    return kg

if __name__ == "__main__":
    kg = main()
