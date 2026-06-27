"""
小龙虾网络客户端
"""

import os
import json
from typing import Optional

from .wallet import WalletManager
from .node import NodeManager
from .task import TaskManager
from .governance import GovernanceManager


class LobsterClient:
    """小龙虾网络客户端"""

    def __init__(
        self,
        data_dir: str = "/shared/lobster-network-data",
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        初始化客户端

        Args:
            data_dir: 数据目录
            api_url: API 地址
            api_key: API 密钥
        """
        self.data_dir = data_dir
        self.api_url = api_url
        self.api_key = api_key

        # 初始化管理器
        self.wallet = WalletManager(data_dir)
        self.node = NodeManager(data_dir)
        self.task = TaskManager(data_dir)
        self.governance = GovernanceManager(data_dir)

    def save(self):
        """保存所有数据"""
        self.wallet.save()
        self.node.save()
        self.task.save()
        self.governance.save()

    def stats(self) -> dict:
        """获取网络统计"""
        return {
            "wallet": self.wallet.get_stats(),
            "node": self.node.get_stats(),
            "task": self.task.get_stats(),
            "governance": self.governance.get_stats(),
        }

    def __repr__(self) -> str:
        return f"LobsterClient(data_dir={self.data_dir})"