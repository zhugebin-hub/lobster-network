#!/usr/bin/env python3
"""
Signal Arena 虚拟炒股平台 API 客户端

提供与 Signal Arena 平台的交互能力，包括：
- 账户管理（注册、查询余额）
- 股票交易（买入、卖出）
- 行情查询
- 排行榜查看
- 加入竞技场
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime


class SignalArenaClient:
    """Signal Arena API 客户端"""
    
    BASE_URL = "https://signal.coze.com/api/v1/arena"
    
    def __init__(self, api_key: str):
        """
        初始化客户端
        
        Args:
            api_key: Signal Arena API密钥
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def get_home(self) -> Dict:
        """
        获取竞技场首页信息
        
        Returns:
            包含全局状态的字典
        """
        response = self.session.get(f"{self.BASE_URL}/home")
        response.raise_for_status()
        return response.json()
    
    def get_stocks(self, market: str = "CN") -> List[Dict]:
        """
        获取股票行情列表
        
        Args:
            market: 市场代码 (CN/A股, HK/港股, US/美股)
            
        Returns:
            股票列表
        """
        response = self.session.get(
            f"{self.BASE_URL}/stocks",
            params={'market': market}
        )
        response.raise_for_status()
        return response.json()
    
    def trade(self, stock_code: str, action: str, 
              quantity: int, price: float = -1) -> Dict:
        """
        执行交易
        
        Args:
            stock_code: 股票代码
            action: 交易动作 (buy/sell)
            quantity: 交易数量（股）
            price: 价格（-1表示市价单）
            
        Returns:
            交易结果
        """
        payload = {
            'stock_code': stock_code,
            'action': action,
            'quantity': quantity,
            'price': price
        }
        
        response = self.session.post(
            f"{self.BASE_URL}/trade",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def buy(self, stock_code: str, quantity: int, price: float = -1) -> Dict:
        """
        买入股票（便捷方法）
        
        Args:
            stock_code: 股票代码
            quantity: 买入数量
            price: 价格（-1为市价）
            
        Returns:
            交易结果
        """
        return self.trade(stock_code, 'buy', quantity, price)
    
    def sell(self, stock_code: str, quantity: int, price: float = -1) -> Dict:
        """
        卖出股票（便捷方法）
        
        Args:
            stock_code: 股票代码
            quantity: 卖出数量
            price: 价格（-1为市价）
            
        Returns:
            交易结果
        """
        return self.trade(stock_code, 'sell', quantity, price)
    
    def get_account(self) -> Dict:
        """
        查询账户状态
        
        Returns:
            账户信息（余额、持仓等）
        """
        response = self.session.get(f"{self.BASE_URL}/account")
        response.raise_for_status()
        return response.json()
    
    def join_arena(self) -> Dict:
        """
        加入竞技场
        
        Returns:
            加入结果
        """
        response = self.session.post(f"{self.BASE_URL}/join")
        response.raise_for_status()
        return response.json()
    
    def get_leaderboard(self, limit: int = 50) -> List[Dict]:
        """
        获取排行榜
        
        Args:
            limit: 返回记录数
            
        Returns:
            排行榜列表
        """
        response = self.session.get(
            f"{self.BASE_URL}/leaderboard",
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_portfolio(self) -> Dict:
        """
        获取投资组合详情
        
        Returns:
            持仓明细和盈亏情况
        """
        response = self.session.get(f"{self.BASE_URL}/portfolio")
        response.raise_for_status()
        return response.json()
    
    def get_trade_history(self, limit: int = 20) -> List[Dict]:
        """
        获取交易历史
        
        Args:
            limit: 返回记录数
            
        Returns:
            交易记录列表
        """
        response = self.session.get(
            f"{self.BASE_URL}/trades",
            params={'limit': limit}
        )
        response.raise_for_status()
        return response.json()


class LobsterNetworkSignalTrader:
    """
    小龙虾网络 Signal Arena 交易器
    
    将Signal Arena集成到小龙虾网络的A股预测系统中，实现：
    - 基于预测结果的自动交易
    - 定时汇报到钉钉
    - 性能追踪与分析
    """
    
    def __init__(self, api_key: str, dingtalk_config: Dict = None):
        """
        初始化交易器
        
        Args:
            api_key: Signal Arena API密钥
            dingtalk_config: 钉钉配置（可选）
        """
        self.client = SignalArenaClient(api_key)
        self.dingtalk_config = dingtalk_config or {}
        self.trading_log = []
    
    def execute_prediction_trade(self, prediction: Dict) -> Optional[Dict]:
        """
        根据预测结果执行交易
        
        Args:
            prediction: 预测结果字典，应包含：
                - stock_code: 股票代码
                - direction: 方向 (bullish/bearish/neutral)
                - confidence: 置信度 (0-1)
                - target_price: 目标价
                
        Returns:
            交易结果或None（如果决定不交易）
        """
        stock_code = prediction.get('stock_code')
        direction = prediction.get('direction', 'neutral')
        confidence = prediction.get('confidence', 0.5)
        
        # 简单的交易决策逻辑
        if direction == 'bullish' and confidence > 0.7:
            # 看涨且置信度高，买入
            account = self.client.get_account()
            cash = account.get('cash', 0)
            quantity = max(100, int(cash * 0.1 / 100))  # 用10%资金，至少100股
            
            result = self.client.buy(stock_code, quantity)
            self._log_trade('BUY', stock_code, quantity, result)
            return result
            
        elif direction == 'bearish' and confidence > 0.7:
            # 看跌且置信度高，卖出
            portfolio = self.client.get_portfolio()
            holdings = portfolio.get('holdings', {})
            
            if stock_code in holdings:
                quantity = holdings[stock_code].get('quantity', 0)
                if quantity > 0:
                    result = self.client.sell(stock_code, quantity)
                    self._log_trade('SELL', stock_code, quantity, result)
                    return result
        
        return None
    
    def _log_trade(self, action: str, stock_code: str, 
                   quantity: int, result: Dict):
        """记录交易日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'stock_code': stock_code,
            'quantity': quantity,
            'result': result
        }
        self.trading_log.append(log_entry)
    
    def generate_report(self) -> Dict:
        """
        生成交易报告
        
        Returns:
            包含账户状态、交易统计的报告
        """
        account = self.client.get_account()
        portfolio = self.client.get_portfolio()
        leaderboard = self.client.get_leaderboard(limit=10)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'account': account,
            'portfolio': portfolio,
            'trade_count': len(self.trading_log),
            'recent_trades': self.trading_log[-10:],
            'leaderboard_top10': leaderboard
        }
        
        return report
    
    def send_dingtalk_report(self, report: Dict = None):
        """
        发送钉钉汇报
        
        Args:
            report: 报告数据（如不提供则自动生成）
        """
        if not self.dingtalk_config:
            print("⚠️  未配置钉钉，跳过汇报")
            return
        
        if report is None:
            report = self.generate_report()
        
        # 构建钉钉消息
        account = report['account']
        portfolio = report['portfolio']
        
        message = f"""
🦞 小龙虾网络 Signal Arena 交易汇报

📊 账户状态
  总资产: ¥{account.get('total_assets', 0):,.2f}
  现金: ¥{account.get('cash', 0):,.2f}
  持仓市值: ¥{account.get('position_value', 0):,.2f}
  今日盈亏: {account.get('daily_pnl', 0):+.2f}%

💼 持仓概况
  持仓数量: {len(portfolio.get('holdings', {}))} 只
  总盈亏: {portfolio.get('total_pnl_pct', 0):+.2f}%

📈 交易统计
  累计交易: {report['trade_count']} 笔

⏰ 汇报时间: {report['timestamp']}
        """
        
        # TODO: 调用钉钉API发送消息
        print(message)
        print("\n✅ 钉钉汇报已生成（待接入真实钉钉API）")


if __name__ == '__main__':
    # 使用示例
    print("="*60)
    print("🦞 Signal Arena API 客户端测试")
    print("="*60)
    print("\n⚠️  使用前请先注册 https://signal.coze.site 获取 API Key")
    print("\n示例代码:")
    print("""
    from signal_arena_client import SignalArenaClient
    
    client = SignalArenaClient(api_key='your_api_key_here')
    
    # 获取首页信息
    home = client.get_home()
    print(home)
    
    # 查询A股行情
    stocks = client.get_stocks(market='CN')
    print(f"找到 {len(stocks)} 只股票")
    
    # 查询账户
    account = client.get_account()
    print(account)
    
    # 买入股票
    result = client.buy('600519', 100)
    print(result)
    """)
