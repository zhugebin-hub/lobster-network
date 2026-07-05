"""
任务管理器
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.lobster_network.trading import TradingSystem


class TaskManager:
    """任务管理器"""

    def __init__(self, data_dir: str):
        self.trading = TradingSystem(data_dir=os.path.join(data_dir, "trading"))
        self.trading.load_data()

    def create(self, publisher_id: str, title: str, description: str, reward: float = 10.0, task_type: str = "labor") -> tuple:
        """创建任务"""
        return self.trading.publish_task(publisher_id, title, description, task_type, reward)

    def list(self, limit: int = 20) -> list:
        """列出任务"""
        return self.trading.get_pending_tasks(limit)

    def claim(self, task_id: str, node_id: str) -> tuple:
        """领取任务"""
        return self.trading.claim_task(task_id, node_id)

    def submit(self, task_id: str, result: str) -> tuple:
        """提交任务"""
        return self.trading.submit_task(task_id, result)

    def review(self, task_id: str, reviewer_id: str, approved: bool, feedback: str = "") -> tuple:
        """审核任务"""
        return self.trading.review_task(task_id, reviewer_id, approved, feedback)

    def get_stats(self) -> dict:
        """获取统计"""
        return self.trading.get_market_statistics()

    def save(self):
        """保存数据"""
        self.trading.save_data()