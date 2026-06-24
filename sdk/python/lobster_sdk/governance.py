"""
治理管理器
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.lobster_network.dao_governance import DAOGovernance
from src.lobster_network.token_economy import TokenEconomy


class GovernanceManager:
    """治理管理器"""

    def __init__(self, data_dir: str):
        self.token_economy = TokenEconomy(data_dir=os.path.join(data_dir, "token"))
        self.token_economy.load_data()
        self.dao = DAOGovernance(self.token_economy, data_dir=os.path.join(data_dir, "dao"))
        self.dao.load_data()

    def create_proposal(self, creator_id: str, title: str, description: str, proposal_type: str = "generic") -> tuple:
        """创建提案"""
        return self.dao.create_proposal(creator_id, title, description, proposal_type)

    def submit_proposal(self, proposal_id: str) -> tuple:
        """提交提案"""
        return self.dao.submit_proposal(proposal_id)

    def list(self, limit: int = 20) -> list:
        """列出提案"""
        return self.dao.get_active_proposals(limit)

    def vote(self, proposal_id: str, voter_id: str, option: str, reason: str = "") -> tuple:
        """投票"""
        return self.dao.vote(proposal_id, voter_id, option, reason)

    def check_result(self, proposal_id: str) -> tuple:
        """检查提案结果"""
        return self.dao.check_proposal_result(proposal_id)

    def execute(self, proposal_id: str) -> tuple:
        """执行提案"""
        return self.dao.execute_proposal(proposal_id)

    def get_stats(self) -> dict:
        """获取统计"""
        return self.dao.get_governance_statistics()

    def save(self):
        """保存数据"""
        self.dao.save_data()
        self.token_economy.save_data()