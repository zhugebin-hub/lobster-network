#!/usr/bin/env python3
"""
从历史回测中学习炒股经验

分析之前的回测结果，提取可复用的交易规则和风险管理原则
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from trading_experience_learner import TradingExperienceLearner


def load_backtest_results():
    """加载之前的回测结果"""
    # 模拟之前回测的数据（基于DEVELOPMENT_LOG.md中的记录）
    backtest_data = {
        '600519': {
            'total_return': -0.1728,
            'max_drawdown': -0.1862,
            'sharpe_ratio': -2.43,
            'trade_count': 1,
            'win_rate': 0.0,  # 1次交易全部亏损
            'market_state': 'bear'  # 下跌趋势
        },
        '000858': {
            'total_return': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'trade_count': 0,
            'win_rate': 0.0,
            'market_state': 'sideways'
        },
        '600036': {
            'total_return': -0.0638,
            'max_drawdown': -0.0969,
            'sharpe_ratio': -1.13,
            'trade_count': 1,
            'win_rate': 0.0,
            'market_state': 'bear'
        }
    }
    
    return backtest_data


def analyze_stock_data(stock_code: str):
    """分析单只股票的历史数据"""
    # 使用正确的相对路径（从项目根目录）
    base_path = Path(__file__).parent.parent.parent.parent
    
    if stock_code == '600519':
        data_path = base_path / 'domains' / 'stock_prediction' / 'data' / '600519_贵州茅台.csv'
    elif stock_code == '000858':
        data_path = base_path / 'domains' / 'stock_prediction' / 'data' / '000858_五粮液.csv'
    elif stock_code == '600036':
        data_path = base_path / 'domains' / 'stock_prediction' / 'data' / '600036_招商银行.csv'
    else:
        return None
    
    if not data_path.exists():
        print(f"⚠️  数据文件不存在: {data_path}")
        return None
    
    df = pd.read_csv(data_path)
    return df


def main():
    """主函数"""
    print("="*70)
    print("🦞 小龙虾网络 - 从历史回测中学习炒股经验")
    print("="*70)
    
    # 初始化学习器
    learner = TradingExperienceLearner()
    
    # 加载回测结果
    backtest_results = load_backtest_results()
    
    print("\n📊 分析各股票回测结果...\n")
    
    for stock_code, result in backtest_results.items():
        print(f"{'─'*70}")
        print(f"📈 {stock_code} 回测分析")
        print(f"{'─'*70}")
        
        # 加载价格数据
        df = analyze_stock_data(stock_code)
        
        if df is not None and len(df) > 0:
            # 从回测中学习
            learning_summary = learner.learn_from_backtest(result, df)
            
            print(f"\n市场状态: {learning_summary['market_state']}")
            print(f"总收益: {result['total_return']:.2%}")
            print(f"最大回撤: {result['max_drawdown']:.2%}")
            print(f"夏普比率: {result['sharpe_ratio']:.2f}")
            print(f"交易次数: {result['trade_count']}")
            
            if result['total_return'] < 0:
                print(f"\n⚠️  策略表现不佳，已记录经验教训")
            
            print(f"💡 止损建议: {learning_summary.get('lessons_count', 0)} 条新规则")
        
        print()
    
    # 生成学习报告
    print("\n" + "="*70)
    report = learner.generate_learning_report()
    print(report)
    
    # 总结关键洞察
    print("\n" + "="*70)
    print("🎯 关键洞察总结")
    print("="*70)
    
    insights = [
        "1. 简单均线交叉策略在熊市/震荡市中表现较差",
        "2. MA20滞后性导致入场过晚，需要更早的信号确认",
        "3. 单一指标容易产生假信号，需要多指标共振",
        "4. 风险管理比择时更重要 - 即使方向正确也可能因回撤过大而失败",
        "5. 不同市场状态需要不同的策略参数"
    ]
    
    for insight in insights:
        print(f"  {insight}")
    
    print("\n" + "="*70)
    print("✅ 经验已保存到知识库: domains/stock_prediction/data/trading_knowledge.json")
    print("="*70)


if __name__ == '__main__':
    main()
