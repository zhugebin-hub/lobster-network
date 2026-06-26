"""
🦞 小龙虾网络 · 围棋训练引擎
支持：死活题/手筋/官子/实战对局模拟
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class GoTrainingEngine:
    """围棋训练引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                'problems', 'go'
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
    
    def solve_life_and_death(self, problem: Dict) -> Dict:
        """
        解决死活题
        
        Args:
            problem: 题目信息
            
        Returns:
            解题结果
        """
        # 模拟解题
        import random
        base_accuracy = 0.70 if problem.get('difficulty') == '入门' else 0.55 if problem.get('difficulty') == '初级' else 0.40
        
        is_correct = random.random() < base_accuracy
        
        return {
            'problem_id': problem.get('id'),
            'type': 'life_and_death',
            'difficulty': problem.get('difficulty'),
            'is_correct': is_correct,
            'answer': problem.get('answer'),
            'reasoning': problem.get('reasoning', '暂无解析'),
            'timestamp': datetime.now().isoformat()
        }
    
    def solve_tesuji(self, problem: Dict) -> Dict:
        """
        解决手筋题
        
        Args:
            problem: 题目信息
            
        Returns:
            解题结果
        """
        import random
        base_accuracy = 0.65 if problem.get('difficulty') == '入门' else 0.50 if problem.get('difficulty') == '初级' else 0.35
        
        is_correct = random.random() < base_accuracy
        
        return {
            'problem_id': problem.get('id'),
            'type': 'tesuji',
            'difficulty': problem.get('difficulty'),
            'is_correct': is_correct,
            'answer': problem.get('answer'),
            'reasoning': problem.get('reasoning', '暂无解析'),
            'timestamp': datetime.now().isoformat()
        }
    
    def solve_yose(self, problem: Dict) -> Dict:
        """
        解决官子题
        
        Args:
            problem: 题目信息
            
        Returns:
            解题结果
        """
        import random
        base_accuracy = 0.60 if problem.get('difficulty') == '入门' else 0.45 if problem.get('difficulty') == '初级' else 0.30
        
        is_correct = random.random() < base_accuracy
        
        return {
            'problem_id': problem.get('id'),
            'type': 'yose',
            'difficulty': problem.get('difficulty'),
            'is_correct': is_correct,
            'answer': problem.get('answer'),
            'reasoning': problem.get('reasoning', '暂无解析'),
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_game(self, player_level: str = '入门', 
                      opponent_level: str = '初级') -> Dict:
        """
        模拟实战对局
        
        Args:
            player_level: 玩家水平
            opponent_level: 对手水平
            
        Returns:
            对局结果
        """
        # 计算胜率
        level_map = {'入门': 1, '初级': 2, '中级': 3, '高级': 4}
        player_rank = level_map.get(player_level, 1)
        opponent_rank = level_map.get(opponent_level, 2)
        
        win_rate = 0.5 + (player_rank - opponent_rank) * 0.15
        win_rate = max(0.1, min(0.9, win_rate))
        
        # 模拟结果
        import random
        is_win = random.random() < win_rate
        
        return {
            'player_level': player_level,
            'opponent_level': opponent_level,
            'win_rate': round(win_rate, 3),
            'is_win': is_win,
            'result': '胜' if is_win else '负',
            'moves': random.randint(150, 300),
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_skill(self, student_type: str = 'xiaochen') -> Dict:
        """
        评估技能水平
        
        Args:
            student_type: 学员类型（xiaochen稳健型 / zhuguxia加速型）
            
        Returns:
            技能评估
        """
        # 获取各类型题目
        life_problems = self.get_problems(problem_type='life_and_death', limit=5)
        tesuji_problems = self.get_problems(problem_type='tesuji', limit=5)
        yose_problems = self.get_problems(problem_type='yose', limit=5)
        
        # 模拟解题
        life_results = [self.solve_life_and_death(p) for p in life_problems]
        tesuji_results = [self.solve_tesuji(p) for p in tesuji_problems]
        yose_results = [self.solve_yose(p) for p in yose_problems]
        
        # 计算准确率
        life_accuracy = sum(1 for r in life_results if r['is_correct']) / len(life_results) if life_results else 0
        tesuji_accuracy = sum(1 for r in tesuji_results if r['is_correct']) / len(tesuji_results) if tesuji_results else 0
        yose_accuracy = sum(1 for r in yose_results if r['is_correct']) / len(yose_results) if yose_results else 0
        
        # 综合评分
        total_accuracy = (life_accuracy + tesuji_accuracy + yose_accuracy) / 3
        
        # 等级评估
        if total_accuracy >= 0.80:
            rank = '初段'
        elif total_accuracy >= 0.60:
            rank = '5级'
        elif total_accuracy >= 0.40:
            rank = '10级'
        else:
            rank = '20级'
            
        return {
            'student_type': student_type,
            'life_accuracy': round(life_accuracy, 3),
            'tesuji_accuracy': round(tesuji_accuracy, 3),
            'yose_accuracy': round(yose_accuracy, 3),
            'total_accuracy': round(total_accuracy, 3),
            'estimated_rank': rank,
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
                'life_and_death': 5,
                'tesuji': 4,
                'yose': 3,
                'game': 2
            }
        else:
            config = {
                'life_and_death': 3,
                'tesuji': 3,
                'yose': 2,
                'game': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'go-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00']
        slot_idx = 0
        
        for problem_type, count in config.items():
            if count == 0:
                continue
                
            if problem_type == 'game':
                plan['schedule'].append({
                    'time': time_slots[slot_idx % len(time_slots)],
                    'type': '实战对局',
                    'count': count,
                    'description': f'与{student_type}水平对手对局'
                })
            else:
                problems = self.get_problems(problem_type=problem_type, limit=count)
                plan['schedule'].append({
                    'time': time_slots[slot_idx % len(time_slots)],
                    'type': problem_type,
                    'count': len(problems),
                    'problems': problems
                })
                
            plan['total_problems'] += count
            slot_idx += 1
            
        return plan


# 演示
if __name__ == '__main__':
    engine = GoTrainingEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 围棋训练引擎 V1.0")
    print("=" * 50)
    
    # 1. 获取题目
    print("\n📚 获取题目:")
    problems = engine.get_problems(limit=5)
    print(f"   获取 {len(problems)} 题")
    
    # 2. 解决死活题
    print("\n🔴 死活题解题:")
    if problems:
        result = engine.solve_life_and_death(problems[0])
        print(f"   题目: {result['problem_id']}")
        print(f"   结果: {'✅ 正确' if result['is_correct'] else '❌ 错误'}")
        print(f"   答案: {result['answer']}")
        
    # 3. 模拟对局
    print("\n⚔️ 模拟对局:")
    game = engine.simulate_game('入门', '初级')
    print(f"   玩家水平: {game['player_level']}")
    print(f"   对手水平: {game['opponent_level']}")
    print(f"   胜率: {game['win_rate']:.1%}")
    print(f"   结果: {game['result']} ({game['moves']}手)")
    
    # 4. 技能评估
    print("\n📊 技能评估:")
    evaluation = engine.evaluate_skill('xiaochen')
    print(f"   学员类型: {evaluation['student_type']}")
    print(f"   死活准确率: {evaluation['life_accuracy']:.1%}")
    print(f"   手筋准确率: {evaluation['tesuji_accuracy']:.1%}")
    print(f"   官子准确率: {evaluation['yose_accuracy']:.1%}")
    print(f"   综合准确率: {evaluation['total_accuracy']:.1%}")
    print(f"   预估等级: {evaluation['estimated_rank']}")
    
    # 5. 生成训练计划
    print("\n📋 训练计划:")
    plan = engine.generate_training_plan('xiaochen')
    print(f"   日期: {plan['date']}")
    print(f"   总题数: {plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ 围棋训练引擎测试完成！")
