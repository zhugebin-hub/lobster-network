"""
世界杯预测训练调度器
将预测题目集成到每日训练计划
"""

import json
import os
from typing import Dict, List
from datetime import datetime, timedelta

try:
    from .football_predict_engine import FootballPredictEngine
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'problems'))
    from football_predict_engine import FootballPredictEngine


class FootballPredictTrainer:
    """世界杯预测训练调度器"""
    
    def __init__(self, engine: FootballPredictEngine = None):
        self.engine = engine or FootballPredictEngine()
        self.training_history = []
        
    def generate_daily_plan(self, student_type: str = 'xiaochen',
                           date: str = None) -> Dict:
        """
        生成每日训练计划
        
        Args:
            student_type: 学员类型（xiaochen稳健型 / zhuguxia加速型）
            date: 日期
            
        Returns:
            训练计划
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # 根据学员类型配置题量
        if student_type == 'zhuguxia':
            # 加速型：更多题
            config = {
                'match_result': 4,
                'score': 3,
                'total_goals': 2,
                'multi_factor': 2,
                'champion': 1
            }
        else:
            # 稳健型：基础题量
            config = {
                'match_result': 3,
                'score': 2,
                'total_goals': 1,
                'multi_factor': 1,
                'champion': 0  # 稳健型不练冠军预测
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'football-predict',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00']
        slot_idx = 0
        
        for problem_type, count in config.items():
            if count == 0:
                continue
                
            problems = self.engine.get_problems(
                problem_type=problem_type,
                limit=count
            )
            
            if problems:
                plan['schedule'].append({
                    'time': time_slots[slot_idx % len(time_slots)],
                    'type': problem_type,
                    'count': len(problems),
                    'problems': problems
                })
                plan['total_problems'] += len(problems)
                slot_idx += 1
                
        return plan
    
    def evaluate_prediction(self, prediction: Dict, actual_result: Dict) -> Dict:
        """
        评估预测准确率
        
        Args:
            prediction: 预测结果
            actual_result: 实际结果
            
        Returns:
            评估结果
        """
        correct = prediction.get('prediction') == actual_result.get('result')
        
        return {
            'match': prediction.get('match'),
            'prediction': prediction.get('prediction'),
            'actual': actual_result.get('result'),
            'correct': correct,
            'confidence': prediction.get('confidence', 0),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_weekly_summary(self, student_type: str = 'xiaochen') -> Dict:
        """
        获取周训练总结
        
        Returns:
            周总结
        """
        # 统计本周预测
        week_problems = self.engine.get_problems(limit=20)
        
        return {
            'week': datetime.now().isocalendar()[1],
            'student': student_type,
            'total_problems': len(week_problems),
            'by_type': {},
            'by_difficulty': {},
            'accuracy': 0.0,
            'timestamp': datetime.now().isoformat()
        }


# 演示
if __name__ == '__main__':
    trainer = FootballPredictTrainer()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 世界杯预测训练调度器")
    print("=" * 50)
    
    # 生成小陈的训练计划
    print("\n📋 小陈（稳健型）每日训练计划:")
    plan = trainer.generate_daily_plan('xiaochen')
    print(f"   日期：{plan['date']}")
    print(f"   总题数：{plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    # 生成诸葛虾的训练计划
    print("\n📋 诸葛虾（加速型）每日训练计划:")
    plan = trainer.generate_daily_plan('zhuguxia')
    print(f"   日期：{plan['date']}")
    print(f"   总题数：{plan['total_problems']}")
    for slot in plan['schedule']:
        print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题")
        
    print("\n" + "=" * 50)
    print("✅ 训练调度器测试完成！")
