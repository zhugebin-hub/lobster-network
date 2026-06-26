"""
🦞 小龙虾网络 · 数据结构训练引擎
支持：数组/链表/树/图/哈希表/排序/搜索
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class DataStructureEngine:
    """数据结构训练引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                '..', 'data_structure', 'problems', 'problems'
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()
        
    def _load_problems(self):
        """加载各阶段题库"""
        for phase in ['phase1', 'phase2', 'phase3']:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, 'problems.json')
            if os.path.exists(problems_file):
                with open(problems_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.phases[phase] = data
                    
    def get_problems(self, phase: str = None, problem_type: str = None, 
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        """获取题目"""
        problems = []
        phases_to_check = [phase] if phase else list(self.phases.keys())
        
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]['problems']:
                if problem_type and prob.get('type') != problem_type:
                    continue
                if difficulty and prob.get('difficulty') != difficulty:
                    continue
                problems.append(prob)
                
        return problems[:limit]
    
    def array_operations(self, arr: List[int] = None) -> Dict:
        """
        数组操作模拟
        
        Args:
            arr: 数组
            
        Returns:
            操作结果
        """
        if arr is None:
            arr = [random.randint(1, 100) for _ in range(10)]
            
        # 模拟操作
        operations = {
            'insert': {'index': random.randint(0, len(arr)), 'value': random.randint(1, 100)},
            'delete': {'index': random.randint(0, len(arr)-1)},
            'search': {'value': random.choice(arr)},
            'sort': {'method': random.choice(['quick_sort', 'merge_sort', 'heap_sort'])},
            'reverse': True
        }
        
        # 计算复杂度
        complexity = {
            'insert': 'O(n)',
            'delete': 'O(n)',
            'search': 'O(n)',
            'sort': 'O(n log n)',
            'reverse': 'O(n)'
        }
        
        return {
            'original_array': arr,
            'operations': operations,
            'time_complexity': complexity,
            'space_complexity': 'O(1)',
            'timestamp': datetime.now().isoformat()
        }
    
    def linked_list_operations(self, size: int = 5) -> Dict:
        """
        链表操作模拟
        
        Args:
            size: 链表大小
            
        Returns:
            操作结果
        """
        # 模拟链表
        values = [random.randint(1, 100) for _ in range(size)]
        
        operations = {
            'insert_head': random.randint(1, 100),
            'insert_tail': random.randint(1, 100),
            'insert_middle': {'index': random.randint(0, size), 'value': random.randint(1, 100)},
            'delete': {'index': random.randint(0, size-1)},
            'search': {'value': random.choice(values)},
            'reverse': True
        }
        
        complexity = {
            'insert_head': 'O(1)',
            'insert_tail': 'O(1)',
            'insert_middle': 'O(n)',
            'delete': 'O(n)',
            'search': 'O(n)',
            'reverse': 'O(n)'
        }
        
        return {
            'original_list': values,
            'operations': operations,
            'time_complexity': complexity,
            'space_complexity': 'O(1)',
            'timestamp': datetime.now().isoformat()
        }
    
    def tree_operations(self, tree_type: str = 'binary_search_tree') -> Dict:
        """
        树操作模拟
        
        Args:
            tree_type: 树类型
            
        Returns:
            操作结果
        """
        # 模拟树
        values = sorted([random.randint(1, 100) for _ in range(7)])
        
        operations = {
            'insert': random.randint(1, 100),
            'delete': random.choice(values),
            'search': random.choice(values),
            'traversal': random.choice(['preorder', 'inorder', 'postorder', 'level_order']),
            'height': random.randint(2, 5)
        }
        
        complexity = {
            'insert': 'O(log n)',
            'delete': 'O(log n)',
            'search': 'O(log n)',
            'traversal': 'O(n)',
            'height': 'O(log n)'
        }
        
        return {
            'tree_type': tree_type,
            'values': values,
            'operations': operations,
            'time_complexity': complexity,
            'space_complexity': 'O(n)',
            'timestamp': datetime.now().isoformat()
        }
    
    def graph_operations(self, graph_type: str = 'directed') -> Dict:
        """
        图操作模拟
        
        Args:
            graph_type: 图类型
            
        Returns:
            操作结果
        """
        # 模拟图
        vertices = random.randint(5, 10)
        edges = random.randint(8, 15)
        
        operations = {
            'add_vertex': vertices + 1,
            'add_edge': {'from': random.randint(0, vertices-1), 'to': random.randint(0, vertices-1)},
            'remove_edge': {'from': random.randint(0, vertices-1), 'to': random.randint(0, vertices-1)},
            'traversal': random.choice(['BFS', 'DFS']),
            'shortest_path': {'from': 0, 'to': vertices-1, 'algorithm': 'Dijkstra'},
            'topological_sort': graph_type == 'directed'
        }
        
        complexity = {
            'add_vertex': 'O(1)',
            'add_edge': 'O(1)',
            'remove_edge': 'O(E)',
            'traversal': 'O(V + E)',
            'shortest_path': 'O(E log V)',
            'topological_sort': 'O(V + E)'
        }
        
        return {
            'graph_type': graph_type,
            'vertices': vertices,
            'edges': edges,
            'operations': operations,
            'time_complexity': complexity,
            'space_complexity': 'O(V + E)',
            'timestamp': datetime.now().isoformat()
        }
    
    def hash_table_operations(self, size: int = 16) -> Dict:
        """
        哈希表操作模拟
        
        Args:
            size: 哈希表大小
            
        Returns:
            操作结果
        """
        # 模拟哈希表
        load_factor = round(random.uniform(0.5, 0.8), 2)
        collisions = random.randint(0, 5)
        
        operations = {
            'insert': {'key': f'key_{random.randint(1, 100)}', 'value': random.randint(1, 100)},
            'search': {'key': f'key_{random.randint(1, 100)}'},
            'delete': {'key': f'key_{random.randint(1, 100)}'},
            'resize': load_factor > 0.75,
            'hash_function': random.choice(['modulo', 'multiplicative', 'universal'])
        }
        
        complexity = {
            'insert': 'O(1) 平均 / O(n) 最坏',
            'search': 'O(1) 平均 / O(n) 最坏',
            'delete': 'O(1) 平均 / O(n) 最坏',
            'resize': 'O(n)'
        }
        
        return {
            'size': size,
            'load_factor': load_factor,
            'collisions': collisions,
            'operations': operations,
            'time_complexity': complexity,
            'space_complexity': 'O(n)',
            'timestamp': datetime.now().isoformat()
        }
    
    def sort_algorithm(self, arr: List[int] = None,
                      algorithm: str = 'quick_sort') -> Dict:
        """
        排序算法模拟
        
        Args:
            arr: 数组
            algorithm: 排序算法
            
        Returns:
            排序结果
        """
        if arr is None:
            arr = [random.randint(1, 100) for _ in range(10)]
            
        # 算法复杂度表
        complexity_map = {
            'bubble_sort': {'best': 'O(n)', 'average': 'O(n²)', 'worst': 'O(n²)', 'space': 'O(1)'},
            'selection_sort': {'best': 'O(n²)', 'average': 'O(n²)', 'worst': 'O(n²)', 'space': 'O(1)'},
            'insertion_sort': {'best': 'O(n)', 'average': 'O(n²)', 'worst': 'O(n²)', 'space': 'O(1)'},
            'quick_sort': {'best': 'O(n log n)', 'average': 'O(n log n)', 'worst': 'O(n²)', 'space': 'O(log n)'},
            'merge_sort': {'best': 'O(n log n)', 'average': 'O(n log n)', 'worst': 'O(n log n)', 'space': 'O(n)'},
            'heap_sort': {'best': 'O(n log n)', 'average': 'O(n log n)', 'worst': 'O(n log n)', 'space': 'O(1)'}
        }
        
        complexity = complexity_map.get(algorithm, complexity_map['quick_sort'])
        
        # 模拟排序
        sorted_arr = sorted(arr)
        comparisons = random.randint(len(arr), len(arr) ** 2)
        swaps = random.randint(0, len(arr) ** 2)
        
        return {
            'algorithm': algorithm,
            'original_array': arr,
            'sorted_array': sorted_arr,
            'comparisons': comparisons,
            'swaps': swaps,
            'time_complexity': complexity,
            'is_stable': algorithm in ['merge_sort', 'insertion_sort'],
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_training_plan(self, student_type: str = 'xiaochen',
                               date: str = None) -> Dict:
        """
        生成每日训练计划
        
        Args:
            student_type: 学员类型
            date: 日期
            
        Returns:
            训练计划
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # 根据学员类型配置题量
        if student_type == 'zhuguxia':
            config = {
                'array': 3,
                'linked_list': 3,
                'tree': 2,
                'graph': 2,
                'hash_table': 2
            }
        else:
            config = {
                'array': 2,
                'linked_list': 2,
                'tree': 1,
                'graph': 1,
                'hash_table': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'data-structure-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00', '22:00']
        slot_idx = 0
        
        type_names = {
            'array': '数组',
            'linked_list': '链表',
            'tree': '树',
            'graph': '图',
            'hash_table': '哈希表'
        }
        
        for problem_type, count in config.items():
            if count == 0:
                continue
                
            problems = self.get_problems(problem_type=problem_type, limit=count)
            plan['schedule'].append({
                'time': time_slots[slot_idx % len(time_slots)],
                'type': type_names.get(problem_type, problem_type),
                'count': len(problems),
                'problems': problems
            })
            plan['total_problems'] += len(problems)
            slot_idx += 1
            
        return plan


# 演示
if __name__ == '__main__':
    engine = DataStructureEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 数据结构训练引擎 V1.0")
    print("=" * 50)
    
    # 1. 数组操作
    print("\n📊 数组操作:")
    arr = engine.array_operations()
    print(f"   操作: {list(arr['operations'].keys())}")
    print(f"   时间复杂度: {arr['time_complexity']['sort']}")
    
    # 2. 链表操作
    print("\n🔗 链表操作:")
    ll = engine.linked_list_operations()
    print(f"   操作: {list(ll['operations'].keys())}")
    print(f"   插入头部: {ll['time_complexity']['insert_head']}")
    
    # 3. 树操作
    print("\n🌳 树操作:")
    tree = engine.tree_operations()
    print(f"   类型: {tree['tree_type']}")
    print(f"   操作: {list(tree['operations'].keys())}")
    print(f"   搜索: {tree['time_complexity']['search']}")
    
    # 4. 图操作
    print("\n🕸️ 图操作:")
    graph = engine.graph_operations()
    print(f"   类型: {graph['graph_type']}")
    print(f"   顶点: {graph['vertices']}, 边: {graph['edges']}")
    print(f"   遍历: {graph['time_complexity']['traversal']}")
    
    # 5. 哈希表操作
    print("\n📦 哈希表操作:")
    ht = engine.hash_table_operations()
    print(f"   大小: {ht['size']}")
    print(f"   负载因子: {ht['load_factor']}")
    print(f"   冲突: {ht['collisions']}")
    
    # 6. 排序算法
    print("\n🔄 排序算法:")
    sort = engine.sort_algorithm(algorithm='quick_sort')
    print(f"   算法: {sort['algorithm']}")
    print(f"   比较次数: {sort['comparisons']}")
    print(f"   交换次数: {sort['swaps']}")
    print(f"   平均复杂度: {sort['time_complexity']['average']}")
    
    # 7. 生成训练计划
    print("\n📋 训练计划:")
    plan = engine.generate_training_plan('xiaochen')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ 数据结构训练引擎测试完成！")
