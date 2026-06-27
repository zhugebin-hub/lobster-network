#!/usr/bin/env python3
"""
学习型预测器集成示例

演示如何将TradingExperienceLearner与StockPredictor结合，
让分析师节点从历史交易经验中学习并优化预测。
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# 添加项目路径（从项目根目录）
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_experience_learner import TradingExperienceLearner
from predictor import StockPredictor


def simulate_trading_session(predictor: StockPredictor, learner: TradingExperienceLearner):
    """
    模拟一次完整的交易会话：预测 → 交易 → 学习
    
    Args:
        predictor: 股票预测器
        learner: 经验学习器
    """
    print("\n" + "="*70)
    print("🦞 模拟交易会话")
    print("="*70)
    
    # 1. 生成预测
    stock_code = "600519"
    stock_name = "贵州茅台"
    
    print(f"\n📊 步骤1: 对 {stock_name}({stock_code}) 进行预测...")
    prediction = predictor.predict(stock_code, stock_name, days_ahead=5)
    
    # 2. 模拟基于预测的交易决策
    final_pred = prediction['final_prediction']
    direction = final_pred.get('direction', 'neutral')
    confidence = final_pred.get('confidence', 0.5)
    
    print(f"\n💡 步骤2: 根据预测做出交易决策...")
    print(f"   方向: {direction}")
    print(f"   置信度: {confidence:.1%}")
    
    # 模拟交易结果（这里用随机数据模拟）
    trade_result = {
        'stock_code': stock_code,
        'action': 'buy' if direction == 'bullish' else ('sell' if direction == 'bearish' else 'hold'),
        'entry_price': 1450.0,
        'exit_price': 1480.0 if direction == 'bullish' else 1420.0,
        'profit_pct': 0.02 if direction == 'bullish' else -0.02,
        'holding_days': 3,
        'market_state': 'bear',  # 假设当前是熊市
        'signal_description': f"基于{direction}信号，置信度{confidence:.0%}"
    }
    
    print(f"   执行操作: {trade_result['action']}")
    print(f"   盈亏: {trade_result['profit_pct']:+.2%}")
    
    # 3. 记录交易到学习器
    print(f"\n🧠 步骤3: 将交易经验记录到知识库...")
    
    observation = {
        'type': 'prediction_outcome',
        'context': f"{stock_name}的{direction}预测验证",
        'hypothesis': f"当预测为{direction}且置信度>{confidence:.0%}时",
        'evidence': {
            'prediction_direction': direction,
            'prediction_confidence': confidence,
            'actual_return': trade_result['profit_pct'],
            'holding_period': trade_result['holding_days'],
            'market_condition': trade_result['market_state']
        },
        'outcome': 'success' if trade_result['profit_pct'] > 0 else 'failure'
    }
    
    learner.kb.add_lesson(observation)
    print(f"   ✅ 已记录交易经验")
    
    # 4. 分析历史模式
    print(f"\n📈 步骤4: 分析历史交易模式...")
    kb_summary = learner.kb.get_summary()
    print(f"   知识库状态:")
    print(f"     - 市场规则: {kb_summary['total_market_rules']} 条")
    print(f"     - 买入模式: {kb_summary['total_entry_patterns']} 个")
    print(f"     - 风险规则: {kb_summary['total_risk_rules']} 条")
    print(f"     - 经验教训: {kb_summary['total_lessons']} 条")
    
    return trade_result


def demonstrate_learning_cycle():
    """演示完整的学习循环"""
    print("="*70)
    print("🦞 小龙虾网络 - 学习型炒股系统演示")
    print("="*70)
    
    # 初始化组件
    learner = TradingExperienceLearner()
    predictor = StockPredictor(emergence_threshold=0.6)
    
    print("\n✅ 系统初始化完成")
    print(f"   - 预测器: StockPredictor (涌现阈值=0.6)")
    print(f"   - 学习器: TradingExperienceLearner")
    
    # 运行多次模拟交易以积累知识
    num_sessions = 3
    results = []
    
    for i in range(num_sessions):
        print(f"\n{'='*70}")
        print(f"🔄 第 {i+1}/{num_sessions} 次交易会话")
        result = simulate_trading_session(predictor, learner)
        results.append(result)
    
    # 生成最终学习报告
    print("\n" + "="*70)
    print("📊 学习总结报告")
    print("="*70)
    
    report = learner.generate_learning_report()
    print(report)
    
    # 统计分析结果
    profitable = sum(1 for r in results if r['profit_pct'] > 0)
    total = len(results)
    avg_return = np.mean([r['profit_pct'] for r in results])
    
    print(f"\n📈 交易统计:")
    print(f"   总交易数: {total}")
    print(f"   盈利次数: {profitable}")
    print(f"   胜率: {profitable/total:.1%}")
    print(f"   平均收益: {avg_return:+.2%}")
    
    print(f"\n💡 下一步建议:")
    print(f"   1. 继续积累更多交易样本以提升学习质量")
    print(f"   2. 根据知识库中的经验优化预测策略")
    print(f"   3. 接入Signal Arena真实API进行实盘测试")
    
    return results


if __name__ == '__main__':
    try:
        results = demonstrate_learning_cycle()
        print("\n✅ 演示完成！")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
