#!/usr/bin/env python3
"""
A股预测模块完整回测演示

使用真实历史数据对均线交叉策略进行回测验证
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from domains.stock_prediction.trainers import StockPredictionTrainer


def run_backtest_demo():
    """运行回测演示"""
    
    print("="*70)
    print("🦞 小龙虾网络 - A股预测模块回测演示")
    print("="*70)
    
    # 创建训练器
    trainer = StockPredictionTrainer()
    
    # 定义要回测的股票列表
    stock_codes = ['600519', '000858', '600036']
    
    # 定义回测时间范围（使用我们获取的数据范围）
    start_date = '2026-02-01'
    end_date = '2026-06-25'
    
    print(f"\n回测配置:")
    print(f"  股票代码: {', '.join(stock_codes)}")
    print(f"  时间范围: {start_date} ~ {end_date}")
    print(f"  策略: 均线交叉 (MA5/MA20)")
    print(f"  初始资金: ¥100,000")
    
    # 执行回测
    results = trainer.backtest(
        stock_codes=stock_codes,
        start_date=start_date,
        end_date=end_date,
        strategy_params={
            'short_window': 5,
            'long_window': 20,
            'initial_capital': 100000.0
        }
    )
    
    # 生成详细报告
    print("\n" + "="*70)
    print("📊 回测详细报告")
    print("="*70)
    
    for i, result in enumerate(results['individual_results'], 1):
        print(f"\n{i}. {result['stock_name']} ({result['stock_code']})")
        print("-" * 60)
        print(f"   策略: {result['strategy']}")
        print(f"   初始资金: ¥{result['initial_capital']:,.2f}")
        print(f"   最终权益: ¥{result['final_equity']:,.2f}")
        print(f"   总收益率: {result['total_return']:+.2f}%")
        print(f"   年化收益: {result['annualized_return']:+.2f}%")
        print(f"   最大回撤: {result['max_drawdown']:.2f}%")
        print(f"   夏普比率: {result['sharpe_ratio']:.2f}")
        print(f"   胜率: {result['win_rate']:.1f}%")
        print(f"   交易次数: {result['total_trades']}")
        
        if result['trades']:
            print(f"\n   最近交易:")
            for trade in result['trades'][:5]:
                action_icon = "🟢" if trade['action'] == 'BUY' else "🔴"
                print(f"     {action_icon} {trade['date'].strftime('%m-%d')} "
                      f"{trade['action']:4s} @ ¥{trade['price']:.2f} "
                      f"x {trade['shares']}股")
    
    print("\n" + "="*70)
    print("📈 综合表现")
    print("="*70)
    print(f"  测试股票数: {results['stock_count']}")
    print(f"  平均收益率: {results['average_return']:+.2f}%")
    print(f"  平均夏普比率: {results['average_sharpe']:.2f}")
    print(f"  平均最大回撤: {results['average_max_drawdown']:.2f}%")
    
    # 投资建议
    print("\n" + "="*70)
    print("💡 投资建议")
    print("="*70)
    
    avg_return = results['average_return']
    avg_sharpe = results['average_sharpe']
    avg_drawdown = results['average_max_drawdown']
    
    if avg_return > 10 and avg_sharpe > 1.0:
        print("  ✅ 策略表现优秀，建议继续优化并实盘测试")
    elif avg_return > 0:
        print("  ⚠️  策略略有盈利，但需要进一步优化参数")
    else:
        print("  ❌ 策略亏损，建议重新设计或调整参数")
    
    if abs(avg_drawdown) > 20:
        print("  ⚠️  注意：最大回撤较大，需加强风险控制")
    
    print("\n" + "="*70)
    print("✅ 回测完成！")
    print("="*70)
    
    return results


if __name__ == '__main__':
    try:
        results = run_backtest_demo()
    except Exception as e:
        print(f"\n❌ 回测失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
