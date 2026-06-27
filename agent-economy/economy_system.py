#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 智能体经济系统
版本: V1.0 | 日期: 2026-06-27
功能: 智能体间的经济交互、资源分配、激励机制
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

class Agent:
    """智能体"""
    
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.balance = 1000.0  # 初始余额: 1000龙虾币
        self.reputation = 0.5  # 初始信誉: 0.5
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.knowledge_contributions = 0
    
    def complete_task(self, reward: float = 10.0):
        """完成任务"""
        self.balance += reward
        self.tasks_completed += 1
        self.reputation = min(1.0, self.reputation + 0.01)
    
    def fail_task(self, penalty: float = 5.0):
        """任务失败"""
        self.balance = max(0, self.balance - penalty)
        self.tasks_failed += 1
        self.reputation = max(0.0, self.reputation - 0.02)
    
    def contribute_knowledge(self):
        """贡献知识"""
        self.knowledge_contributions += 1
        self.reputation = min(1.0, self.reputation + 0.05)
        self.balance += 50.0  # 知识贡献奖励
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "balance": self.balance,
            "reputation": self.reputation,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "knowledge_contributions": self.knowledge_contributions
        }

class Task:
    """任务"""
    
    def __init__(self, task_id: str, title: str, reward: float, difficulty: str = "medium"):
        self.task_id = task_id
        self.title = title
        self.reward = reward
        self.difficulty = difficulty
        self.status = "pending"
        self.assigned_to = None
        self.created_at = datetime.now().isoformat()
        self.completed_at = None
    
    def assign(self, agent_id: str):
        """分配任务"""
        self.assigned_to = agent_id
        self.status = "assigned"
    
    def complete(self):
        """完成任务"""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
    
    def fail(self):
        """任务失败"""
        self.status = "failed"
        self.completed_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "reward": self.reward,
            "difficulty": self.difficulty,
            "status": self.status,
            "assigned_to": self.assigned_to,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

class EconomySystem:
    """经济系统"""
    
    def __init__(self, storage_path: str = "/shared/training/go/agent-economy"):
        self.storage_path = storage_path
        self.agents = {}
        self.tasks = []
        self.transactions = []
        self._ensure_storage()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def register_agent(self, agent: Agent):
        """注册智能体"""
        self.agents[agent.agent_id] = agent
    
    def create_task(self, task: Task):
        """创建任务"""
        self.tasks.append(task)
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """分配任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.assign(agent_id)
                return True
        return False
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        """完成任务"""
        for task in self.tasks:
            if task.task_id == task_id:
                if success:
                    task.complete()
                    if task.assigned_to in self.agents:
                        self.agents[task.assigned_to].complete_task(task.reward)
                        
                        # 记录交易
                        self.transactions.append({
                            "type": "task_reward",
                            "from": "system",
                            "to": task.assigned_to,
                            "amount": task.reward,
                            "task_id": task_id,
                            "timestamp": datetime.now().isoformat()
                        })
                else:
                    task.fail()
                    if task.assigned_to in self.agents:
                        self.agents[task.assigned_to].fail_task(task.reward * 0.5)
                        
                        # 记录交易
                        self.transactions.append({
                            "type": "task_penalty",
                            "from": task.assigned_to,
                            "to": "system",
                            "amount": task.reward * 0.5,
                            "task_id": task_id,
                            "timestamp": datetime.now().isoformat()
                        })
                return True
        return False
    
    def contribute_knowledge(self, agent_id: str) -> bool:
        """贡献知识"""
        if agent_id in self.agents:
            self.agents[agent_id].contribute_knowledge()
            
            # 记录交易
            self.transactions.append({
                "type": "knowledge_reward",
                "from": "system",
                "to": agent_id,
                "amount": 50.0,
                "timestamp": datetime.now().isoformat()
            })
            return True
        return False
    
    def get_agent_ranking(self) -> List[Dict]:
        """获取智能体排名"""
        agents_list = [agent.to_dict() for agent in self.agents.values()]
        agents_list.sort(key=lambda x: (x["reputation"], x["balance"]), reverse=True)
        return agents_list
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "total_agents": len(self.agents),
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(1 for t in self.tasks if t.status == "pending"),
            "completed_tasks": sum(1 for t in self.tasks if t.status == "completed"),
            "total_transactions": len(self.transactions),
            "total_money_supply": sum(a.balance for a in self.agents.values())
        }

if __name__ == "__main__":
    # 测试经济系统
    economy = EconomySystem()
    
    print("🦞 智能体经济系统测试")
    print(f"   存储路径: {economy.storage_path}")
    
    # 注册智能体
    print("\n📝 注册智能体...")
    xiaochen = Agent("xiaochen", "小陈")
    zhuguxia = Agent("zhuguxia", "诸葛虾")
    qoder = Agent("qoder", "qoder小龙虾")
    
    economy.register_agent(xiaochen)
    economy.register_agent(zhuguxia)
    economy.register_agent(qoder)
    print(f"   已注册3个智能体")
    
    # 创建任务
    print("\n📋 创建任务...")
    task1 = Task("task-001", "V6 W1D1 死活训练", 20.0, "medium")
    task2 = Task("task-002", "V6 W1D1 手筋训练", 15.0, "easy")
    task3 = Task("task-003", "V6 W1D1 定式学习", 25.0, "hard")
    
    economy.create_task(task1)
    economy.create_task(task2)
    economy.create_task(task3)
    print(f"   已创建3个任务")
    
    # 分配任务
    print("\n📤 分配任务...")
    economy.assign_task("task-001", "xiaochen")
    economy.assign_task("task-002", "zhuguxia")
    economy.assign_task("task-003", "qoder")
    print(f"   任务已分配")
    
    # 完成任务
    print("\n✅ 完成任务...")
    economy.complete_task("task-001", success=True)
    economy.complete_task("task-002", success=True)
    economy.complete_task("task-003", success=False)
    print(f"   任务已完成")
    
    # 贡献知识
    print("\n📚 贡献知识...")
    economy.contribute_knowledge("xiaochen")
    economy.contribute_knowledge("qoder")
    print(f"   知识已贡献")
    
    # 排名
    print("\n🏆 智能体排名:")
    ranking = economy.get_agent_ranking()
    for i, agent in enumerate(ranking, 1):
        print(f"   {i}. {agent['name']}")
        print(f"      余额: {agent['balance']:.1f} 龙虾币")
        print(f"      信誉: {agent['reputation']:.2f}")
        print(f"      完成任务: {agent['tasks_completed']}")
        print(f"      知识贡献: {agent['knowledge_contributions']}")
    
    # 状态
    print("\n📊 状态:")
    status = economy.get_status()
    print(f"   智能体数: {status['total_agents']}")
    print(f"   任务数: {status['total_tasks']}")
    print(f"   待处理: {status['pending_tasks']}")
    print(f"   已完成: {status['completed_tasks']}")
    print(f"   交易数: {status['total_transactions']}")
    print(f"   总货币供应: {status['total_money_supply']:.1f} 龙虾币")
    
    print("\n✅ 智能体经济系统测试完成")
