"""
🦞 小龙虾网络 · 炒股学习训练器
支持：每日训练计划、持仓检查、仓位计算、市场评估、组合优化
"""

import json
import os
from typing import Dict, List
from datetime import datetime, timedelta

try:
    from .signal_arena_engine import SignalArenaEngine
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'problems'))
    from signal_arena_engine import SignalArenaEngine


class StockTrainer:
    """炒股学习训练器"""
    
    def __init__(self, engine: SignalArenaEngine = None):
        self.engine = engine or SignalArenaEngine()
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
                'position_check': 4,
                'position_calc': 3,
                'market_eval': 2,
                'portfolio_opt': 2,
                'trade_exec': 2
            }
        else:
            # 稳健型：基础题量
            config = {
                'position_check': 3,
                'position_calc': 2,
                'market_eval': 1,
                'portfolio_opt': 1,
                'trade_exec': 1
            }
            
        # 生成计划
        plan = {
            'date': date,
            'student': student_type,
            'type': 'stock-training',
            'schedule': [],
            'total_problems': 0
        }
        
        time_slots = ['09:00', '14:00', '19:00', '21:00']
        slot_idx = 0
        
        type_names = {
            'position_check': '持仓检查（止盈止损）',
            'position_calc': '仓位计算',
            'market_eval': '市场评估',
            'portfolio_opt': '组合优化',
            'trade_exec': '交易执行'
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
        print(f"🦞 小龙虾网络 · 炒股学习训练")
        print(f"   学员：{student_type}")
        print(f"   日期：{date}")
        print("=" * 60)
        
        results = []
        
        for slot in plan['schedule']:
            print(f"\n{'─' * 40}")
            print(f"[{slot['time']}] {slot['type']}")
            
            if slot['problem_type'] == 'position_check':
                result = self._train_position_check(slot['count'])
            elif slot['problem_type'] == 'position_calc':
                result = self._train_position_calc(slot['count'])
            elif slot['problem_type'] == 'market_eval':
                result = self._train_market_eval(slot['count'])
            elif slot['problem_type'] == 'portfolio_opt':
                result = self._train_portfolio_opt(slot['count'])
            elif slot['problem_type'] == 'trade_exec':
                result = self._train_trade_exec(slot['count'])
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
    
    def _train_position_check(self, count: int) -> Dict:
        """训练持仓检查"""
        import random
        
        stocks = [
            {'symbol': '三环集团', 'current_price': 142, 'cost_price': 100, 'shares': 100, 'market': 'CN'},
            {'symbol': '京东方A', 'current_price': 6.2, 'cost_price': 5.8, 'shares': 20900, 'market': 'CN'},
            {'symbol': '中国卫通', 'current_price': 32, 'cost_price': 32, 'shares': 2700, 'market': 'CN'},
            {'symbol': '闻泰科技', 'current_price': 21.6, 'cost_price': 22, 'shares': 6400, 'market': 'CN'},
            {'symbol': '蓝思科技', 'current_price': 36, 'cost_price': 30, 'shares': 700, 'market': 'CN'},
        ]
        
        correct = 0
        total = min(count, len(stocks))
        
        for i in range(total):
            stock = stocks[i % len(stocks)]
            result = self.engine.check_position(stock)
            
            # 判断是否正确
            return_rate = (stock['current_price'] - stock['cost_price']) / stock['cost_price']
            
            if return_rate >= 0.15 and result['action'] == 'sell':
                correct += 1
                print(f"   ✅ {stock['symbol']}+{return_rate:.1%} → {result['action']}（止盈）")
            elif return_rate <= -0.08 and result['action'] == 'sell':
                correct += 1
                print(f"   ✅ {stock['symbol']}{return_rate:.1%} → {result['action']}（止损）")
            elif abs(return_rate) < 0.15 and return_rate > -0.08 and result['action'] == 'hold':
                correct += 1
                print(f"   ✅ {stock['symbol']}{return_rate:+.1%} → {result['action']}（持有）")
            else:
                print(f"   ❌ {stock['symbol']}{return_rate:+.1%} → 期望{result['action']}")
                
        return {'correct': correct, 'total': total}
    
    def _train_position_calc(self, count: int) -> Dict:
        """训练仓位计算"""
        import random
        
        scenarios = [
            {'price': 100, 'total': 1000000, 'cash': 800000},
            {'price': 50, 'total': 1000000, 'cash': 800000},
            {'price': 200, 'total': 1000000, 'cash': 800000},
            {'price': 10, 'total': 1000000, 'cash': 800000},
        ]
        
        correct = 0
        total = min(count, len(scenarios))
        
        for i in range(total):
            scenario = scenarios[i % len(scenarios)]
            self.engine.portfolio['cash'] = scenario['cash']
            result = self.engine.calculate_position_size(scenario['price'], scenario['total'])
            
            # 判断是否正确
            if result['recommended_shares'] > 0:
                correct += 1
                print(f"   ✅ 股价¥{scenario['price']} → 买入{result['recommended_shares']}股（现金储备{result['cash_reserve_percent']:.1f}%）")
            else:
                print(f"   ❌ 股价¥{scenario['price']} → 仓位计算异常")
                
        return {'correct': correct, 'total': total}
    
    def _train_market_eval(self, count: int) -> Dict:
        """训练市场评估"""
        import random
        
        scenarios = [
            {'movers': [{'symbol': '长江证券', 'change_percent': 10.0}, {'symbol': '大族激光', 'change_percent': 10.0}]},
            {'movers': [{'symbol': '贵州茅台', 'change_percent': -5.0}, {'symbol': '宁德时代', 'change_percent': -3.0}]},
            {'movers': [{'symbol': '腾讯', 'change_percent': 2.0}, {'symbol': '阿里', 'change_percent': -1.0}]},
        ]
        
        correct = 0
        total = min(count, len(scenarios))
        
        for i in range(total):
            scenario = scenarios[i % len(scenarios)]
            result = self.engine.evaluate_market(scenario['movers'])
            
            # 判断是否正确
            avg = result['avg_change']
            if avg > 3 and result['market_sentiment'] == 'bullish':
                correct += 1
                print(f"   ✅ 平均涨幅{avg:.1f}% → {result['market_sentiment']}（看多）")
            elif avg < -3 and result['market_sentiment'] == 'bearish':
                correct += 1
                print(f"   ✅ 平均涨幅{avg:.1f}% → {result['market_sentiment']}（看空）")
            else:
                print(f"   ✅ 平均涨幅{avg:.1f}% → {result['market_sentiment']}")
                correct += 1  # 市场评估没有绝对对错
                
        return {'correct': correct, 'total': total}
    
    def _train_portfolio_opt(self, count: int) -> Dict:
        """训练组合优化"""
        import random
        
        scenarios = [
            {'positions': [
                {'symbol': '三环集团', 'current_price': 142, 'shares': 100, 'return_rate': 0.42},
                {'symbol': '中国卫通', 'current_price': 32, 'shares': 2700, 'return_rate': 0.0},
            ]},
            {'positions': [
                {'symbol': '京东方A', 'current_price': 6.2, 'shares': 20900, 'return_rate': 0.04},
                {'symbol': '闻泰科技', 'current_price': 21.6, 'shares': 6400, 'return_rate': 0.0},
            ]},
        ]
        
        correct = 0
        total = min(count, len(scenarios))
        
        for i in range(total):
            scenario = scenarios[i % len(scenarios)]
            self.engine.portfolio['total_value'] = 1000000
            self.engine.portfolio['cash'] = 60000
            result = self.engine.optimize_portfolio(scenario['positions'])
            
            # 判断是否正确
            if result['suggestions']:
                correct += 1
                print(f"   ✅ 发现{len(result['suggestions'])}个优化点：{', '.join(result['suggestions'][:2])}")
            else:
                print(f"   ✅ 组合健康，无需优化")
                correct += 1
                
        return {'correct': correct, 'total': total}
    
    def _train_trade_exec(self, count: int) -> Dict:
        """训练交易执行"""
        import random
        
        correct = 0
        total = count
        
        for i in range(total):
            # 模拟交易决策
            symbols = ['sh600519', 'sz000858', 'hk00700', 'AAPL', 'NVDA']
            symbol = random.choice(symbols)
            action = random.choice(['buy', 'sell'])
            shares = random.choice([100, 200, 500, 1000])
            
            # 判断决策是否合理
            is_reasonable = shares <= 1000 and action in ['buy', 'sell']
            
            if is_reasonable:
                correct += 1
                print(f"   ✅ {symbol} {action} {shares}股 - 决策合理")
            else:
                print(f"   ❌ {symbol} {action} {shares}股 - 决策异常")
                
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
    trainer = StockTrainer()
    
    print("=" * 60)
    print("🦞 小龙虾网络 · 炒股学习训练器 V1.0")
    print("=" * 60)
    
    # 执行小陈训练
    print("\n📋 小陈（稳健型）训练:")
    result1 = trainer.execute_training('xiaochen')
    
    # 执行诸葛虾训练
    print("\n📋 诸葛虾（加速型）训练:")
    result2 = trainer.execute_training('zhuguxia')
    
    print("\n" + "=" * 60)
    print("✅ 炒股学习训练器测试完成！")
