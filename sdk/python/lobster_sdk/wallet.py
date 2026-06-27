"""
钱包管理器
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.lobster_network.token_economy import TokenEconomy


class WalletManager:
    """钱包管理器"""

    def __init__(self, data_dir: str):
        self.token_economy = TokenEconomy(data_dir=os.path.join(data_dir, "token"))
        self.token_economy.load_data()

    def create(self, node_id: str) -> tuple:
        """创建钱包"""
        return self.token_economy.create_wallet(node_id)

    def balance(self, node_id: str) -> float:
        """获取余额"""
        return self.token_economy.get_balance(node_id)

    def transfer(self, from_node: str, to_node: str, amount: float) -> tuple:
        """转账"""
        return self.token_economy.transfer(from_node, to_node, amount)

    def stake(self, node_id: str, amount: float) -> tuple:
        """质押"""
        return self.token_economy.stake(node_id, amount)

    def unstake(self, node_id: str, amount: float) -> tuple:
        """解除质押"""
        return self.token_economy.unstake(node_id, amount)

    def mine(self, node_id: str, emergence_score: float = 0.5) -> tuple:
        """挖矿"""
        return self.token_economy.mine_block(node_id, emergence_score)

    def get_stats(self) -> dict:
        """获取统计"""
        return self.token_economy.get_blockchain_info()

    def save(self):
        """保存数据"""
        self.token_economy.save_data()