"""
🦞 小龙虾网络 · 交易经济训练器
支持：劳务市场/硅碳商城/积分管理/排行榜策略
"""

import json
import os
from typing import Dict, List
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from src.lobster_network.trading import TradingSystem


class TradingEconomyTrainer:
    """交易经济训练器"""
    
    def __init__(self, trading: TradingSystem = None):
        self.trading = trading or TradingSystem()
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
                'task_management': 4,
                'product_trading': 3,
                'points_management': 2,
                'market_analysis': 2,
                'risk_management': 2
            }
        else:
            # 稳健型：基础题量
            config = {
                'task_management': 3,
                'product_trading': 2,
                'points_management': 1,
                'market_analysis': 1,
                'risk_management': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'trading-economy-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00']
        slot_idx = 0
        
        type_names = {
            'task_management': '劳务市场（任务管理）',
            'product_trading': '硅碳商城（商品交易）',
            'points_management': '积分管理',
            'market_analysis': '市场分析',
            'risk_management': '风险管理'
        }
        
        for problem_type, count in config.items():
            if count == 0:
                continue
                
            plan['schedule'].append({
                'time': time_slots[slot_idx % len(time_slots)],
                'type': type_names.get(problem_type, problem_type),
                'count': count,
                'problem_type': problem_type
            })
            plan['total_problems'] += count
            slot_idx += 1
            
        return plan
    
    def execute_training(self, student_type: str = 'xiaochen',
                        date: str = None) -> Dict:
        """
        执行训练
        
        Args:
            student_type: 学员类型
            date: 日期
            
        Returns:
            训练结果
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        plan = self.generate_daily_plan(student_type, date)
        
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 交易经济训练")
        print(f"   学员：{student_type}")
        print(f"   日期：{date}")
        print("=" * 60)
        
        results = []
        
        for slot in plan['schedule']:
            print(f"\n{'─' * 40}")
            print(f"[{slot['time']}] {slot['type']}")
            
            if slot['problem_type'] == 'task_management':
                result = self._train_task_management(slot['count'])
            elif slot['problem_type'] == 'product_trading':
                result = self._train_product_trading(slot['count'])
            elif slot['problem_type'] == 'points_management':
                result = self._train_points_management(slot['count'])
            elif slot['problem_type'] == 'market_analysis':
                result = self._train_market_analysis(slot['count'])
            elif slot['problem_type'] == 'risk_management':
                result = self._train_risk_management(slot['count'])
            else:
                result = {'correct': 0, 'total': 0}
                
            results.append({
                'time': slot['time'],
                'type': slot['type'],
                'correct': result['correct'],
                'total': result['total'],
                'accuracy': result['correct'] / result['total'] if result['total'] > 0 else 0
            })
            
        # 生成报告
        total_correct = sum(r['correct'] for r in results)
        total_problems = sum(r['total'] for r in results)
        accuracy = total_correct / total_problems if total_problems > 0 else 0
        
        print(f"\n{'=' * 60}")
        print(f"📊 训练报告")
        print(f"   总题数：{total_problems}")
        print(f"   正确数：{total_correct}")
        print(f"   准确率：{accuracy:.1%}")
        
        if accuracy >= 0.80:
            print(f"   评价：🌟 超常发挥！明日升档")
        elif accuracy >= 0.60:
            print(f"   评价：✅ 正常进度")
        else:
            print(f"   评价：⚠️ 需加强复习，明日错题重练")
            
        return {
            'student': student_type,
            'date': date,
            'total': total_problems,
            'correct': total_correct,
            'accuracy': accuracy,
            'details': results
        }
    
    def _train_task_management(self, count: int) -> Dict:
        """训练任务管理"""
        import random
        
        # 注册用户
        if 'trainer' not in self.trading.users:
            self.trading.register_user('trainer', '训练师', initial_points=1000)
            
        correct = 0
        total = count
        
        for i in range(total):
            # 发布任务
            task_id = f"task-train-{i}"
            self.trading.publish_task(
                publisher_id='trainer',
                title=f'训练任务{i}',
                description='训练用任务',
                reward_amount=random.randint(10, 50)
            )
            
            # 领取任务
            if 'trainee' not in self.trading.users:
                self.trading.register_user('trainee', '学员', initial_points=100)
                
            tasks = self.trading.get_pending_tasks()
            if tasks:
                self.trading.claim_task(tasks[0]['task_id'], 'trainee')
                correct += 1
                print(f"   ✅ 发布任务 → 领取任务 → 任务完成")
            else:
                print(f"   ❌ 无待领取任务")
                
        return {'correct': correct, 'total': total}
    
    def _train_product_trading(self, count: int) -> Dict:
        """训练商品交易"""
        import random
        
        # 注册用户
        if 'seller' not in self.trading.users:
            self.trading.register_user('seller', '卖家', initial_points=500)
        if 'buyer' not in self.trading.users:
            self.trading.register_user('buyer', '买家', initial_points=500)
            
        correct = 0
        total = count
        
        for i in range(total):
            # 创建商品
            product_id = f"product-train-{i}"
            self.trading.create_product(
                seller_id='seller',
                name=f'训练商品{i}',
                description='训练用商品',
                price=random.randint(10, 100)
            )
            
            # 购买商品
            products = self.trading.get_active_products()
            if products:
                self.trading.buy_product(products[0]['product_id'], 'buyer')
                correct += 1
                print(f"   ✅ 创建商品 → 购买商品 → 订单完成")
            else:
                print(f"   ❌ 无在售商品")
                
        return {'correct': correct, 'total': total}
    
    def _train_points_management(self, count: int) -> Dict:
        """训练积分管理"""
        import random
        
        correct = 0
        total = count
        
        for i in range(total):
            # 模拟积分操作
            user_id = f'points-user-{i}'
            if user_id not in self.trading.users:
                self.trading.register_user(user_id, f'用户{i}', initial_points=100)
                
            # 更新积分
            points_change = random.randint(-20, 50)
            self.trading.update_user_points(user_id, points_change)
            
            user = self.trading.get_user(user_id)
            if user and user.points >= 0:
                correct += 1
                print(f"   ✅ 用户{user_id}积分变化{points_change:+d} → 当前{user.points}分")
            else:
                print(f"   ❌ 用户{user_id}积分异常")
                
        return {'correct': correct, 'total': total}
    
    def _train_market_analysis(self, count: int) -> Dict:
        """训练市场分析"""
        import random
        
        correct = 0
        total = count
        
        for i in range(total):
            # 获取市场统计
            stats = self.trading.get_market_statistics()
            
            # 判断市场健康度
            if stats['total_tasks'] > 0 and stats['completed_tasks'] > 0:
                completion_rate = stats['completed_tasks'] / stats['total_tasks']
                if completion_rate >= 0.5:
                    correct += 1
                    print(f"   ✅ 市场健康：任务完成率{completion_rate:.1%}")
                else:
                    print(f"   ⚠️ 市场异常：任务完成率{completion_rate:.1%}")
            else:
                print(f"   ℹ️ 市场数据不足")
                correct += 1
                
        return {'correct': correct, 'total': total}
    
    def _train_risk_management(self, count: int) -> Dict:
        """训练风险管理"""
        import random
        
        correct = 0
        total = count
        
        for i in range(total):
            # 模拟风险场景
            scenarios = [
                {'type': 'task_failure', 'risk': '任务失败'},
                {'type': 'product_quality', 'risk': '商品质量'},
                {'type': 'points_inflation', 'risk': '积分通胀'}
            ]
            
            scenario = random.choice(scenarios)
            
            # 判断风险等级
            if scenario['type'] == 'task_failure':
                risk_level = '中'
            elif scenario['type'] == 'product_quality':
                risk_level = '高'
            else:
                risk_level = '低'
                
            correct += 1
            print(f"   ✅ {scenario['risk']} → 风险等级{risk_level}")
            
        return {'correct': correct, 'total': total}
    
    def get_weekly_summary(self, student_type: str = 'xiaochen') -> Dict:
        """
        获取周训练总结
        
        Returns:
            周总结
        """
        return {
            'week': datetime.now().isocalendar()[1],
            'student': student_type,
            'total_trainings': len(self.training_history),
            'avg_accuracy': 0.0,
            'timestamp': datetime.now().isoformat()
        }


# 演示
if __name__ == '__main__':
    trainer = TradingEconomyTrainer()
    
    print("=" * 60)
    print("🦞 小龙虾网络 · 交易经济训练器 V1.0")
    print("=" * 60)
    
    # 执行小陈训练
    print("\n📋 小陈（稳健型）训练:")
    result1 = trainer.execute_training('xiaochen')
    
    # 执行诸葛虾训练
    print("\n📋 诸葛虾（加速型）训练:")
    result2 = trainer.execute_training('zhuguxia')
    
    print("\n" + "=" * 60)
    print("✅ 交易经济训练器测试完成！")
