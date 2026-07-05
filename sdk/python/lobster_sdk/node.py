"""
节点管理器
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.lobster_network.trading import TradingSystem


class NodeManager:
    """节点管理器"""

    def __init__(self, data_dir: str):
        self.trading = TradingSystem(data_dir=os.path.join(data_dir, "trading"))
        self.trading.load_data()

    def register(self, node_id: str, name: str, user_type: str = "agent", initial_points: int = 100) -> tuple:
        """注册节点"""
        return self.trading.register_user(node_id, name, user_type, initial_points)

    def list(self) -> list:
        """列出节点"""
        return list(self.trading.users.keys())

    def get_stats(self) -> dict:
        """获取统计"""
        return self.trading.get_market_statistics()

    def save(self):
        """保存数据"""
        self.trading.save_data()