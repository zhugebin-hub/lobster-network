"""
智能体经济系统 - Agent Economy System
支持代币经济、任务市场、声誉系统、资源分配
"""

import json
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    PAYMENT = "payment"
    REWARD = "reward"
    PENALTY = "penalty"
    STAKING = "staking"
    DELEGATION = "delegation"


@dataclass
class Agent:
    """智能体"""
    agent_id: str
    name: str
    balance: float = 100.0  # 初始余额
    reputation: float = 5.0  # 初始声誉
    skills: List[str] = field(default_factory=list)
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Transaction:
    """交易记录"""
    tx_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    from_agent: str = ""
    to_agent: str = ""
    amount: float = 0.0
    tx_type: str = TransactionType.PAYMENT.value
    description: str = ""
    timestamp: float = field(default_factory=time.time)
    status: str = "completed"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Task:
    """任务"""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    title: str = ""
    description: str = ""
    reward: float = 0.0
    required_skills: List[str] = field(default_factory=list)
    assignee: Optional[str] = None
    status: str = "open"  # open, assigned, completed, failed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AgentEconomy:
    """智能体经济系统"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.transactions: List[Transaction] = []
        self.tasks: Dict[str, Task] = {}
        self.total_supply: float = 0.0
        self.transaction_fee: float = 0.01  # 1%手续费
        self.min_reputation: float = 1.0
        
    def register_agent(self, agent: Agent) -> bool:
        """注册智能体"""
        if agent.agent_id in self.agents:
            return False
        self.agents[agent.agent_id] = agent
        self.total_supply += agent.balance
        return True
    
    def transfer(self, from_agent: str, to_agent: str, amount: float, description: str = "") -> Optional[Transaction]:
        """转账"""
        if from_agent not in self.agents or to_agent not in self.agents:
            return None
        if self.agents[from_agent].balance < amount:
            return None
        
        fee = amount * self.transaction_fee
        net_amount = amount - fee
        
        self.agents[from_agent].balance -= amount
        self.agents[to_agent].balance += net_amount
        
        tx = Transaction(
            from_agent=from_agent,
            to_agent=to_agent,
            amount=amount,
            tx_type=TransactionType.PAYMENT.value,
            description=description
        )
        self.transactions.append(tx)
        return tx
    
    def create_task(self, task: Task) -> str:
        """创建任务"""
        self.tasks[task.task_id] = task
        return task.task_id
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """分配任务"""
        if task_id not in self.tasks:
            return False
        if agent_id not in self.agents:
            return False
        
        task = self.tasks[task_id]
        if task.status != "open":
            return False
        
        # 检查技能匹配
        if task.required_skills:
            agent_skills = set(self.agents[agent_id].skills)
            required = set(task.required_skills)
            if not required.issubset(agent_skills):
                return False
        
        task.assignee = agent_id
        task.status = "assigned"
        return True
    
    def complete_task(self, task_id: str) -> Optional[Transaction]:
        """完成任务"""
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        if task.status != "assigned" or not task.assignee:
            return None
        
        # 发放奖励
        reward_tx = Transaction(
            from_agent="system",
            to_agent=task.assignee,
            amount=task.reward,
            tx_type=TransactionType.REWARD.value,
            description=f"完成任务: {task.title}"
        )
        
        if "system" in self.agents:
            self.agents["system"].balance -= task.reward
        
        self.agents[task.assignee].balance += task.reward
        self.agents[task.assignee].reputation += 0.1
        
        task.status = "completed"
        task.completed_at = datetime.now().isoformat()
        self.transactions.append(reward_tx)
        
        return reward_tx
    
    def fail_task(self, task_id: str) -> bool:
        """任务失败"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status != "assigned":
            return False
        
        if task.assignee:
            self.agents[task.assignee].reputation -= 0.5
        
        task.status = "failed"
        return True
    
    def get_agent_balance(self, agent_id: str) -> Optional[float]:
        """获取余额"""
        if agent_id in self.agents:
            return self.agents[agent_id].balance
        return None
    
    def get_agent_reputation(self, agent_id: str) -> Optional[float]:
        """获取声誉"""
        if agent_id in self.agents:
            return self.agents[agent_id].reputation
        return None
    
    def get_transaction_history(self, agent_id: str) -> List[Dict]:
        """获取交易历史"""
        history = [tx.to_dict() for tx in self.transactions 
                   if tx.from_agent == agent_id or tx.to_agent == agent_id]
        return history
    
    def get_economy_stats(self) -> Dict:
        """获取经济统计"""
        balances = [a.balance for a in self.agents.values()]
        reputations = [a.reputation for a in self.agents.values()]
        
        return {
            "total_agents": len(self.agents),
            "total_supply": self.total_supply,
            "total_transactions": len(self.transactions),
            "avg_balance": sum(balances) / len(balances) if balances else 0,
            "avg_reputation": sum(reputations) / len(reputations) if reputations else 0,
            "tasks_open": len([t for t in self.tasks.values() if t.status == "open"]),
            "tasks_completed": len([t for t in self.tasks.values() if t.status == "completed"])
        }
    
    def simulate_economy(self, num_agents: int = 3, num_tasks: int = 5) -> Dict:
        """模拟经济运行"""
        # 注册智能体
        for i in range(num_agents):
            agent = Agent(
                agent_id=f"agent-{i}",
                name=f"Agent-{i}",
                balance=100.0 + i * 10,
                skills=["go-training", "poster-design"] if i < 2 else ["stock-prediction"]
            )
            self.register_agent(agent)
        
        # 创建任务
        for i in range(num_tasks):
            task = Task(
                title=f"训练任务-{i}",
                description=f"第{i}个训练任务",
                reward=10.0 + i * 2,
                required_skills=["go-training"] if i % 2 == 0 else ["poster-design"]
            )
            self.create_task(task)
        
        # 分配和完成任务
        completed = 0
        for task_id, task in self.tasks.items():
            if task.required_skills:
                for agent_id, agent in self.agents.items():
                    if set(task.required_skills).issubset(set(agent.skills)):
                        if self.assign_task(task_id, agent_id):
                            if self.complete_task(task_id):
                                completed += 1
                            break
        
        return {
            "agents": num_agents,
            "tasks": num_tasks,
            "completed": completed,
            "stats": self.get_economy_stats()
        }


# 测试函数
def test_agent_economy():
    """测试智能体经济系统"""
    economy = AgentEconomy()
    
    # 注册智能体
    agent1 = Agent("agent-1", "Agent-1", balance=200.0, skills=["go-training"])
    agent2 = Agent("agent-2", "Agent-2", balance=150.0, skills=["poster-design"])
    
    assert economy.register_agent(agent1) == True
    assert economy.register_agent(agent2) == True
    assert economy.register_agent(agent1) == False  # 重复注册
    
    # 转账
    tx = economy.transfer("agent-1", "agent-2", 50.0, "训练费用")
    assert tx is not None
    assert economy.get_agent_balance("agent-1") == 150.0
    assert economy.get_agent_balance("agent-2") == 199.5  # 扣除1%手续费
    
    # 创建任务
    task = Task(title="围棋训练", reward=20.0, required_skills=["go-training"])
    task_id = economy.create_task(task)
    assert task_id != ""
    
    # 分配任务
    assert economy.assign_task(task_id, "agent-1") == True
    assert economy.assign_task(task_id, "agent-2") == False  # 技能不匹配
    
    # 完成任务
    reward_tx = economy.complete_task(task_id)
    assert reward_tx is not None
    assert reward_tx.amount == 20.0
    assert economy.get_agent_reputation("agent-1") == 5.1
    
    # 交易历史
    history = economy.get_transaction_history("agent-1")
    assert len(history) == 2  # 转账+奖励
    
    # 经济统计
    stats = economy.get_economy_stats()
    assert stats["total_agents"] == 2
    assert stats["tasks_completed"] == 1
    
    # 模拟经济
    sim = economy.simulate_economy(num_agents=2, num_tasks=3)
    assert sim["agents"] == 2
    assert sim["tasks"] == 3
    
    return {
        "status": "passed",
        "tests_run": 12,
        "details": {
            "agent_registration": True,
            "transfer": True,
            "transaction_fee": True,
            "task_creation": True,
            "task_assignment": True,
            "skill_matching": True,
            "task_completion": True,
            "reward_distribution": True,
            "reputation_update": True,
            "transaction_history": True,
            "economy_stats": True,
            "simulation": True
        }
    }


if __name__ == "__main__":
    result = test_agent_economy()
    print(json.dumps(result, indent=2, ensure_ascii=False))
