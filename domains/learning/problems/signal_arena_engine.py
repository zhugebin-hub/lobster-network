"""
Signal Arena 炒股引擎
支持趋势跟随、止盈止损、仓位管理、跨市场配置
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class SignalArenaEngine:
    """Signal Arena 炒股引擎"""
    
    def __init__(self, config: Dict = None):
        """初始化引擎"""
        self.config = config or {
            'max_position_percent': 20,    # 单只股票最大仓位 20%
            'take_profit_percent': 15,     # 止盈点 15%
            'stop_loss_percent': 8,        # 止损点 8%
            'cash_reserve_percent': 25,    # 现金储备 25%
            'max_positions': 6,            # 最大持仓数
        }
        self.portfolio = {
            'cash': 1000000,
            'total_value': 1000000,
            'positions': [],
            'return_rate': 0.0,
        }
        
    def check_position(self, stock: Dict) -> Dict:
        """
        检查持仓，执行止盈止损
        
        Args:
            stock: 股票信息 {symbol, current_price, cost_price, shares, market}
            
        Returns:
            操作建议
        """
        current_price = stock['current_price']
        cost_price = stock['cost_price']
        shares = stock['shares']
        market = stock.get('market', 'CN')
        
        # 计算收益率
        return_rate = (current_price - cost_price) / cost_price
        
        # 止盈止损判断
        action = 'hold'
        reason = '持有不动'
        
        if return_rate >= self.config['take_profit_percent'] / 100:
            action = 'sell'
            reason = f'触发止盈（收益率{return_rate:.1%}）'
        elif return_rate <= -self.config['stop_loss_percent'] / 100:
            action = 'sell'
            reason = f'触发止损（收益率{return_rate:.1%}）'
        elif shares * current_price / self.portfolio['total_value'] > self.config['max_position_percent'] / 100:
            action = 'reduce'
            reason = f'仓位超限（占比{shares * current_price / self.portfolio["total_value"]:.1%}）'
            
        return {
            'symbol': stock['symbol'],
            'market': market,
            'current_price': current_price,
            'cost_price': cost_price,
            'shares': shares,
            'return_rate': round(return_rate, 4),
            'action': action,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }
    
    def calculate_position_size(self, stock_price: float, 
                                total_value: float = None) -> Dict:
        """
        计算买入仓位
        
        Args:
            stock_price: 股票价格
            total_value: 总资产
            
        Returns:
            仓位建议
        """
        if total_value is None:
            total_value = self.portfolio['total_value']
            
        # 最大单只仓位
        max_position_value = total_value * self.config['max_position_percent'] / 100
        max_shares = int(max_position_value / stock_price / 100) * 100  # 取整百股
        
        # 可用现金
        available_cash = self.portfolio['cash']
        cash_limited_shares = int(available_cash / stock_price / 100) * 100
        
        # 取较小值
        recommended_shares = min(max_shares, cash_limited_shares)
        
        # 现金储备检查
        cash_after_buy = available_cash - recommended_shares * stock_price
        cash_reserve = cash_after_buy / total_value if total_value > 0 else 0
        
        return {
            'stock_price': stock_price,
            'max_shares_by_position': max_shares,
            'max_shares_by_cash': cash_limited_shares,
            'recommended_shares': recommended_shares,
            'cash_after_buy': round(cash_after_buy, 2),
            'cash_reserve_percent': round(cash_reserve * 100, 1),
            'meets_reserve_requirement': cash_reserve >= self.config['cash_reserve_percent'] / 100,
            'timestamp': datetime.now().isoformat()
        }
    
    def evaluate_market(self, top_movers: List[Dict]) -> Dict:
        """
        评估市场环境
        
        Args:
            top_movers: 涨幅榜数据
            
        Returns:
            市场评估
        """
        if not top_movers:
            return {'market_sentiment': 'neutral', 'recommendation': '观望'}
            
        # 计算平均涨幅
        avg_change = sum(s.get('change_percent', 0) for s in top_movers) / len(top_movers)
        
        # 判断市场情绪
        if avg_change > 3:
            sentiment = 'bullish'
            recommendation = '可适度加仓'
        elif avg_change < -3:
            sentiment = 'bearish'
            recommendation = '减仓防守'
        else:
            sentiment = 'neutral'
            recommendation = '保持当前仓位'
            
        return {
            'market_sentiment': sentiment,
            'recommendation': recommendation,
            'avg_change': round(avg_change, 2),
            'top_movers_count': len(top_movers),
            'timestamp': datetime.now().isoformat()
        }
    
    def optimize_portfolio(self, positions: List[Dict]) -> Dict:
        """
        优化投资组合
        
        Args:
            positions: 当前持仓列表
            
        Returns:
            优化建议
        """
        total_value = self.portfolio['total_value']
        current_cash = self.portfolio['cash']
        
        # 统计
        position_count = len(positions)
        position_value = sum(p['shares'] * p['current_price'] for p in positions)
        cash_reserve = current_cash / total_value if total_value > 0 else 0
        
        # 优化建议
        suggestions = []
        
        if position_count > self.config['max_positions']:
            suggestions.append(f'持仓过多（{position_count}只），建议降至{self.config["max_positions"]}只以内')
            
        if cash_reserve < self.config['cash_reserve_percent'] / 100:
            suggestions.append(f'现金不足（{cash_reserve:.1%}），建议提升至{self.config["cash_reserve_percent"]}%')
            
        # 检查单只仓位
        for p in positions:
            weight = p['shares'] * p['current_price'] / total_value
            if weight > self.config['max_position_percent'] / 100:
                suggestions.append(f'{p["symbol"]}仓位过重（{weight:.1%}），建议减仓')
                
        # 检查僵尸仓
        zombie_stocks = [p for p in positions if abs(p.get('return_rate', 0)) < 0.01]
        if zombie_stocks:
            suggestions.append(f'发现{len(zombie_stocks)}只僵尸仓，建议清仓')
            
        return {
            'position_count': position_count,
            'position_value': round(position_value, 2),
            'cash_reserve': round(cash_reserve * 100, 1),
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
    
    def backtest_strategy(self, strategy: Dict, historical_data: List[Dict]) -> Dict:
        """
        回测策略
        
        Args:
            strategy: 策略配置
            historical_data: 历史数据
            
        Returns:
            回测结果
        """
        # 模拟回测
        initial_capital = 1000000
        capital = initial_capital
        trades = 0
        wins = 0
        losses = 0
        
        for day in historical_data:
            # 简化回测逻辑
            if day.get('buy_signal'):
                # 买入
                position_size = min(capital * 0.2, day['price'] * 1000)
                capital -= position_size
                trades += 1
                
            if day.get('sell_signal'):
                # 卖出
                return_rate = day.get('return_rate', 0)
                capital += position_size * (1 + return_rate)
                trades += 1
                if return_rate > 0:
                    wins += 1
                else:
                    losses += 1
                    
        final_return = (capital - initial_capital) / initial_capital
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
        
        return {
            'initial_capital': initial_capital,
            'final_capital': round(capital, 2),
            'total_return': round(final_return * 100, 2),
            'total_trades': trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate * 100, 1),
            'timestamp': datetime.now().isoformat()
        }


# 演示
if __name__ == '__main__':
    engine = SignalArenaEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - Signal Arena 炒股引擎 V1.0")
    print("=" * 50)
    
    # 1. 检查持仓
    print("\n📊 持仓检查:")
    stocks = [
        {'symbol': '三环集团', 'current_price': 142, 'cost_price': 100, 'shares': 100, 'market': 'CN'},
        {'symbol': '京东方A', 'current_price': 6.2, 'cost_price': 5.8, 'shares': 20900, 'market': 'CN'},
        {'symbol': '中国卫通', 'current_price': 32, 'cost_price': 32, 'shares': 2700, 'market': 'CN'},
    ]
    
    for stock in stocks:
        result = engine.check_position(stock)
        print(f"   {result['symbol']}: {result['action']} - {result['reason']} (收益率{result['return_rate']:.1%})")
        
    # 2. 计算仓位
    print("\n💰 仓位计算:")
    position = engine.calculate_position_size(stock_price=100, total_value=1000000)
    print(f"   股价: ¥{position['stock_price']}")
    print(f"   建议买入: {position['recommended_shares']}股")
    print(f"   买入后现金: ¥{position['cash_after_buy']:,.0f}")
    print(f"   现金储备: {position['cash_reserve_percent']:.1f}%")
    print(f"   符合储备要求: {'✅' if position['meets_reserve_requirement'] else '❌'}")
    
    # 3. 市场评估
    print("\n🌍 市场评估:")
    top_movers = [
        {'symbol': '长江证券', 'change_percent': 10.0},
        {'symbol': '大族激光', 'change_percent': 10.0},
        {'symbol': '士兰微', 'change_percent': 5.5},
    ]
    market = engine.evaluate_market(top_movers)
    print(f"   市场情绪: {market['market_sentiment']}")
    print(f"   建议: {market['recommendation']}")
    print(f"   平均涨幅: {market['avg_change']:.1f}%")
    
    # 4. 组合优化
    print("\n🔧 组合优化:")
    positions = [
        {'symbol': '三环集团', 'current_price': 142, 'shares': 100, 'return_rate': 0.42},
        {'symbol': '京东方A', 'current_price': 6.2, 'shares': 20900, 'return_rate': 0.04},
        {'symbol': '中国卫通', 'current_price': 32, 'shares': 2700, 'return_rate': 0.0},
        {'symbol': '闻泰科技', 'current_price': 21.6, 'shares': 6400, 'return_rate': 0.0},
    ]
    engine.portfolio['total_value'] = 1000000
    engine.portfolio['cash'] = 60000
    optimization = engine.optimize_portfolio(positions)
    print(f"   持仓数: {optimization['position_count']}")
    print(f"   现金储备: {optimization['cash_reserve']:.1f}%")
    print(f"   优化建议:")
    for s in optimization['suggestions']:
        print(f"      ⚠️ {s}")
        
    print("\n" + "=" * 50)
    print("✅ 炒股引擎测试完成！")
