#!/usr/bin/env python3
"""
A股预测训练器 - 基于历史数据的模型训练与回测

提供策略优化、参数调优和性能评估功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class StockPredictionTrainer:
    """A股预测训练器
    
    功能:
    - 历史数据回测
    - 策略参数优化
    - 模型性能评估
    - 过拟合检测
    """
    
    def __init__(self, predictor=None):
        """
        初始化训练器
        
        Args:
            predictor: StockPredictor实例（可选）
        """
        self.predictor = predictor
        self.training_history = []
        
    def load_stock_data(self, csv_file: str) -> pd.DataFrame:
        """加载股票CSV数据"""
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # 转换数值列
        numeric_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 删除空值行
        df = df.dropna(subset=['close'])
        
        return df
    
    def backtest_ma_strategy(self, df: pd.DataFrame, 
                             short_window: int = 5, 
                             long_window: int = 20,
                             initial_capital: float = 100000.0,
                             start_date: str = None,
                             end_date: str = None) -> Dict:
        """
        均线交叉策略回测
        
        Args:
            df: 股票数据DataFrame（完整数据，用于计算指标）
            short_window: 短期均线周期
            long_window: 长期均线周期
            initial_capital: 初始资金
            start_date: 回测开始日期（可选）
            end_date: 回测结束日期（可选）
            
        Returns:
            回测结果字典
        """
        # 先计算所有技术指标（使用完整数据）
        df['ma_short'] = df['close'].rolling(window=short_window).mean()
        df['ma_long'] = df['close'].rolling(window=long_window).mean()
        
        # 生成交易信号
        df['signal'] = 0
        df.loc[df['ma_short'] > df['ma_long'], 'signal'] = 1  # 金叉买入
        df.loc[df['ma_short'] < df['ma_long'], 'signal'] = -1  # 死叉卖出
        
        # 计算每日持仓变化
        df['position'] = df['signal'].diff()
        
        # 如果指定了时间范围，则过滤
        if start_date and end_date:
            df_trade = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()
        else:
            df_trade = df.copy()
        
        # 模拟交易
        capital = initial_capital
        shares = 0
        trades = []
        equity_curve = [initial_capital]
        
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            # 买入信号
            if row['position'] == 1 and capital > 0:
                shares_to_buy = int(capital / row['close'])
                if shares_to_buy > 0:
                    cost = shares_to_buy * row['close']
                    capital -= cost
                    shares += shares_to_buy
                    trades.append({
                        'date': row['date'],
                        'action': 'BUY',
                        'price': float(row['close']),
                        'shares': shares_to_buy,
                        'capital_remaining': float(capital)
                    })
            
            # 卖出信号
            elif row['position'] == -1 and shares > 0:
                revenue = shares * row['close']
                capital += revenue
                trades.append({
                    'date': row['date'],
                    'action': 'SELL',
                    'price': float(row['close']),
                    'shares': shares,
                    'capital_remaining': float(capital)
                })
                shares = 0
            
            # 记录权益曲线
            current_equity = capital + (shares * row['close'])
            equity_curve.append(current_equity)
        
        # 计算绩效指标
        final_equity = capital + (shares * df.iloc[-1]['close'])
        total_return = (final_equity - initial_capital) / initial_capital * 100
        
        # 计算最大回撤
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.cummax()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        # 计算胜率
        winning_trades = [t for t in trades if t['action'] == 'SELL' and 
                         t['price'] > next((prev_t['price'] for prev_t in reversed(trades) 
                                          if prev_t['action'] == 'BUY' and prev_t['date'] < t['date']), 0)]
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        win_rate = len(winning_trades) / len(sell_trades) * 100 if sell_trades else 0
        
        # 计算夏普比率（简化版）
        daily_returns = pd.Series(equity_curve).pct_change().dropna()
        sharpe_ratio = (daily_returns.mean() / daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0
        
        return {
            'strategy': f'MA Cross ({short_window}/{long_window})',
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'annualized_return': total_return / (len(df) / 252),
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'total_trades': len([t for t in trades if t['action'] == 'BUY']),
            'trades': trades[:10],  # 只返回前10笔交易
            'equity_curve': equity_curve[-10:]  # 只返回最后10个点
        }
    
    def backtest(self, stock_codes: List[str], 
                 start_date: str, end_date: str,
                 strategy_params: Dict = None) -> Dict:
        """
        回测指定策略在历史数据上的表现
        
        Args:
            stock_codes: 股票代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            strategy_params: 策略参数配置
            
        Returns:
            回测结果
        """
        print(f"\n📊 开始回测")
        print(f"股票数量: {len(stock_codes)}")
        print(f"时间区间: {start_date} ~ {end_date}")
        
        data_dir = Path(__file__).parent.parent / 'data'
        all_results = []
        
        for code in stock_codes:
            # 查找对应的CSV文件
            csv_files = list(data_dir.glob(f"{code}_*.csv"))
            if not csv_files:
                print(f"⚠️  未找到股票 {code} 的数据文件")
                continue
            
            csv_file = csv_files[0]
            print(f"\n处理股票: {csv_file.name}")
            
            # 加载数据（不过滤时间，先用完整数据计算指标）
            df = self.load_stock_data(str(csv_file))
            
            if len(df) < 30:
                print(f"⚠️  数据不足，跳过")
                continue
            
            # 执行回测（在backtest_ma_strategy内部会处理时间过滤）
            result = self.backtest_ma_strategy(df, start_date=start_date, end_date=end_date)
            result['stock_code'] = code
            result['stock_name'] = csv_file.stem.replace(f"{code}_", "")
            all_results.append(result)
            
            print(f"  总收益: {result['total_return']:.2f}%")
            print(f"  最大回撤: {result['max_drawdown']:.2f}%")
            print(f"  夏普比率: {result['sharpe_ratio']:.2f}")
        
        # 汇总结果
        if all_results:
            avg_return = np.mean([r['total_return'] for r in all_results])
            avg_sharpe = np.mean([r['sharpe_ratio'] for r in all_results])
            avg_drawdown = np.mean([r['max_drawdown'] for r in all_results])
        else:
            avg_return = avg_sharpe = avg_drawdown = 0
        
        results = {
            "stock_count": len(all_results),
            "average_return": avg_return,
            "average_sharpe": avg_sharpe,
            "average_max_drawdown": avg_drawdown,
            "individual_results": all_results
        }
        
        print(f"\n{'='*60}")
        print(f"回测完成！共测试 {len(all_results)} 只股票")
        print(f"平均收益率: {avg_return:.2f}%")
        print(f"平均夏普比率: {avg_sharpe:.2f}")
        print(f"平均最大回撤: {avg_drawdown:.2f}%")
        print(f"{'='*60}")
        
        return results
    
    def optimize_parameters(self, param_grid: Dict,
                           validation_period: int = 30) -> Dict:
        """
        网格搜索最优参数组合
        
        Args:
            param_grid: 参数网格，如 {'short_window': [5, 10, 15], 'long_window': [20, 30, 60]}
            validation_period: 验证期天数
            
        Returns:
            最优参数及性能
        """
        print(f"\n🔧 开始参数优化")
        print(f"参数组合数: {self._count_combinations(param_grid)}")
        
        # TODO: 实现完整的网格搜索
        best_params = {}
        best_performance = {}
        
        return {
            "best_params": best_params,
            "best_performance": best_performance,
            "all_results": []
        }
    
    def evaluate_model(self, predictions: List[Dict], 
                      actual_prices: List[Dict]) -> Dict:
        """
        评估预测模型的性能指标
        
        Args:
            predictions: 预测结果列表
            actual_prices: 实际价格列表
            
        Returns:
            评估指标
        """
        if not predictions or not actual_prices:
            return {}
        
        pred_prices = [p.get('predicted_price', 0) for p in predictions]
        actual_vals = [a.get('actual_price', 0) for a in actual_prices]
        
        pred_array = np.array(pred_prices)
        actual_array = np.array(actual_vals)
        
        # 计算各种误差指标
        mae = np.mean(np.abs(pred_array - actual_array))
        mse = np.mean((pred_array - actual_array) ** 2)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((actual_array - pred_array) / actual_array)) * 100
        
        # 方向准确率
        pred_direction = np.diff(pred_array) > 0
        actual_direction = np.diff(actual_array) > 0
        direction_accuracy = np.mean(pred_direction == actual_direction) * 100
        
        # R²分数
        ss_res = np.sum((actual_array - pred_array) ** 2)
        ss_tot = np.sum((actual_array - np.mean(actual_array)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            "mae": float(mae),
            "mse": float(mse),
            "rmse": float(rmse),
            "mape": float(mape),
            "direction_accuracy": float(direction_accuracy),
            "r_squared": float(r_squared)
        }
    
    def _count_combinations(self, param_grid: Dict) -> int:
        """计算参数组合总数"""
        count = 1
        for values in param_grid.values():
            count *= len(values) if isinstance(values, list) else 1
        return count
