#!/usr/bin/env python3
"""
A股预测模块使用示例

演示如何使用小龙虾网络的A股预测功能
"""

import sys
import os

# 添加项目路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from domains.stock_prediction import StockPredictor
from domains.stock_prediction.trainers import StockPredictionTrainer


def example_basic_prediction():
    """基础预测示例"""
    print("="*60)
    print("示例1: 基础股票预测")
    print("="*60)
    
    # 创建预测器
    predictor = StockPredictor(emergence_threshold=0.6)
    
    # 对贵州茅台进行预测
    result = predictor.predict(
        stock_code="600519",
        stock_name="贵州茅台",
        days_ahead=5
    )
    
    return result


def example_with_trainer():
    """带训练器的预测示例"""
    print("\n" + "="*60)
    print("示例2: 使用训练器进行回测")
    print("="*60)
    
    # 创建预测器和训练器
    predictor = StockPredictor()
    trainer = StockPredictionTrainer(predictor)
    
    # 回测多只股票
    stock_codes = ["600519", "000858", "600036"]
    backtest_result = trainer.backtest(
        stock_codes=stock_codes,
        start_date="2025-01-01",
        end_date="2025-06-01"
    )
    
    print(f"\n回测结果:")
    print(f"  总交易数: {backtest_result['total_trades']}")
    print(f"  胜率: {backtest_result['win_rate']:.1%}")
    print(f"  总收益: {backtest_result['total_return']:.2%}")
    
    return backtest_result


def example_parameter_optimization():
    """参数优化示例"""
    print("\n" + "="*60)
    print("示例3: 参数优化")
    print("="*60)
    
    predictor = StockPredictor()
    trainer = StockPredictionTrainer(predictor)
    
    # 定义参数网格
    param_grid = {
        'emergence_threshold': [0.5, 0.6, 0.7],
        'lookback_days': [30, 60, 90]
    }
    
    optimization_result = trainer.optimize_parameters(param_grid)
    
    print(f"\n最优参数: {optimization_result['best_params']}")
    
    return optimization_result


if __name__ == "__main__":
    print("🦞 小龙虾网络 - A股预测模块使用示例\n")
    
    # 运行示例
    try:
        example_basic_prediction()
        # example_with_trainer()  # 需要真实数据
        # example_parameter_optimization()  # 需要真实数据
        
        print("\n✅ 示例运行完成")
        print("\n⚠️  注意: 当前为框架版本，需要接入真实数据源后才能获得实际预测结果")
        print("   请参考 docs/README.md 了解待实现功能清单")
        
    except Exception as e:
        print(f"\n❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()
