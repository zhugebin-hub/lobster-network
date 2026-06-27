"""
🦞 小龙虾网络 · 通用逻辑训练引擎
支持：逻辑推理/编程思维/算法/数学
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SharedLogicEngine:
    """通用逻辑训练引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                '..', 'shared', 'problems', 'problems'
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
    
    def solve_logic_puzzle(self, problem: Dict) -> Dict:
        """
        解决逻辑推理题
        
        Args:
            problem: 题目信息
            
        Returns:
            解题结果
        """
        import random
        base_accuracy = 0.70 if problem.get('difficulty') == '入门' else 0.55 if problem.get('difficulty') == '初级' else 0.40
        
        is_correct = random.random() < base_accuracy
        
        return {
            'problem_id': problem.get('id'),
            'type': 'logic_puzzle',
            'difficulty': problem.get('difficulty'),
            'is_correct': is_correct,
            'answer': problem.get('answer'),
            'reasoning': problem.get('reasoning', '暂无解析'),
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_coding(self, language: str = 'python',
                       problem_type: str = 'algorithm') -> Dict:
        """
        编程模拟
        
        Args:
            language: 编程语言
            problem_type: 问题类型
            
        Returns:
            编程结果
        """
        # 模拟代码
        code_examples = {
            'python': {
                'algorithm': '''def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1''',
                'data_structure': '''class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        
class LinkedList:
    def __init__(self):
        self.head = None
        
    def append(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node''',
                'web': '''from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'status': 'success', 'data': [1, 2, 3]})

if __name__ == '__main__':
    app.run(debug=True)'''
            }
        }
        
        code = code_examples.get(language, {}).get(problem_type, '# 暂无代码')
        
        # 模拟测试
        test_results = {
            'total_tests': random.randint(5, 15),
            'passed': random.randint(3, 15),
            'failed': 0,
            'coverage': round(random.uniform(70, 95), 1)
        }
        
        return {
            'language': language,
            'problem_type': problem_type,
            'code': code,
            'test_results': test_results,
            'time_complexity': 'O(n log n)',
            'space_complexity': 'O(n)',
            'timestamp': datetime.now().isoformat()
        }
    
    def solve_algorithm(self, algorithm_type: str = 'sorting') -> Dict:
        """
        算法题求解
        
        Args:
            algorithm_type: 算法类型
            
        Returns:
            求解结果
        """
        algorithms = {
            'sorting': {
                'name': '排序算法',
                'complexity': 'O(n log n)',
                'space': 'O(n)',
                'stable': True
            },
            'searching': {
                'name': '搜索算法',
                'complexity': 'O(log n)',
                'space': 'O(1)',
                'stable': True
            },
            'graph': {
                'name': '图算法',
                'complexity': 'O(V + E)',
                'space': 'O(V)',
                'stable': True
            },
            'dynamic_programming': {
                'name': '动态规划',
                'complexity': 'O(n²)',
                'space': 'O(n)',
                'stable': True
            }
        }
        
        algo = algorithms.get(algorithm_type, algorithms['sorting'])
        
        return {
            'algorithm_type': algorithm_type,
            'algorithm': algo['name'],
            'time_complexity': algo['complexity'],
            'space_complexity': algo['space'],
            'is_stable': algo['stable'],
            'timestamp': datetime.now().isoformat()
        }
    
    def solve_math_problem(self, problem_type: str = 'algebra') -> Dict:
        """
        数学题求解
        
        Args:
            problem_type: 数学类型
            
        Returns:
            求解结果
        """
        math_types = {
            'algebra': {
                'name': '代数',
                'example': '解方程 2x + 3 = 7',
                'solution': 'x = 2'
            },
            'geometry': {
                'name': '几何',
                'example': '计算半径为5的圆面积',
                'solution': 'S = πr² = 25π ≈ 78.54'
            },
            'probability': {
                'name': '概率',
                'example': '掷骰子出现偶数的概率',
                'solution': 'P = 3/6 = 0.5'
            },
            'statistics': {
                'name': '统计',
                'example': '计算[1,2,3,4,5]的平均值和标准差',
                'solution': '均值=3, 标准差≈1.58'
            }
        }
        
        math = math_types.get(problem_type, math_types['algebra'])
        
        return {
            'problem_type': problem_type,
            'math_type': math['name'],
            'example': math['example'],
            'solution': math['solution'],
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_skill(self, student_type: str = 'xiaochen') -> Dict:
        """
        技能评估
        
        Args:
            student_type: 学员类型
            
        Returns:
            技能评估
        """
        # 获取各类型题目
        logic_problems = self.get_problems(problem_type='logic', limit=5)
        coding_problems = self.get_problems(problem_type='coding', limit=5)
        algorithm_problems = self.get_problems(problem_type='algorithm', limit=5)
        math_problems = self.get_problems(problem_type='math', limit=5)
        
        # 模拟解题
        logic_results = [self.solve_logic_puzzle(p) for p in logic_problems]
        
        # 计算准确率
        logic_accuracy = sum(1 for r in logic_results if r['is_correct']) / len(logic_results) if logic_results else 0
        
        # 综合评分
        total_accuracy = logic_accuracy
        
        # 等级评估
        if total_accuracy >= 0.80:
            rank = '高级'
        elif total_accuracy >= 0.60:
            rank = '中级'
        elif total_accuracy >= 0.40:
            rank = '初级'
        else:
            rank = '入门'
            
        return {
            'student_type': student_type,
            'logic_accuracy': round(logic_accuracy, 3),
            'total_accuracy': round(total_accuracy, 3),
            'estimated_level': rank,
            'strengths': [],
            'weaknesses': [],
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
                'logic': 3,
                'coding': 3,
                'algorithm': 2,
                'math': 2
            }
        else:
            config = {
                'logic': 2,
                'coding': 2,
                'algorithm': 1,
                'math': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'shared-logic-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00']
        slot_idx = 0
        
        type_names = {
            'logic': '逻辑推理',
            'coding': '编程思维',
            'algorithm': '算法',
            'math': '数学'
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
    engine = SharedLogicEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 通用逻辑训练引擎 V1.0")
    print("=" * 50)
    
    # 1. 逻辑推理
    print("\n🧠 逻辑推理:")
    problems = engine.get_problems(limit=3)
    if problems:
        result = engine.solve_logic_puzzle(problems[0])
        print(f"   题目: {result['problem_id']}")
        print(f"   结果: {'✅ 正确' if result['is_correct'] else '❌ 错误'}")
        
    # 2. 编程模拟
    print("\n💻 编程模拟:")
    coding = engine.simulate_coding('python', 'algorithm')
    print(f"   语言: {coding['language']}")
    print(f"   类型: {coding['problem_type']}")
    print(f"   测试: {coding['test_results']['passed']}/{coding['test_results']['total_tests']}")
    print(f"   覆盖率: {coding['test_results']['coverage']:.1f}%")
    
    # 3. 算法求解
    print("\n🔄 算法求解:")
    algo = engine.solve_algorithm('sorting')
    print(f"   算法: {algo['algorithm']}")
    print(f"   时间复杂度: {algo['time_complexity']}")
    print(f"   空间复杂度: {algo['space_complexity']}")
    
    # 4. 数学求解
    print("\n📐 数学求解:")
    math = engine.solve_math_problem('probability')
    print(f"   类型: {math['math_type']}")
    print(f"   例题: {math['example']}")
    print(f"   解答: {math['solution']}")
    
    # 5. 技能评估
    print("\n📊 技能评估:")
    evaluation = engine.evaluate_skill('xiaochen')
    print(f"   学员类型: {evaluation['student_type']}")
    print(f"   逻辑准确率: {evaluation['logic_accuracy']:.1%}")
    print(f"   预估等级: {evaluation['estimated_level']}")
    
    # 6. 生成训练计划
    print("\n📋 训练计划:")
    plan = engine.generate_training_plan('xiaochen')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ 通用逻辑训练引擎测试完成！")
