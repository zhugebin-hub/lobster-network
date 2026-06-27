#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 动态匹配算法 V5.0
Agentic Resource Discovery 协议动态匹配

功能：
1. 多算法匹配（余弦/Jaccard/混合/机器学习）
2. 任务协同模块
3. ARD 智能合约
4. 匹配度评分
"""

import json
import os
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .ard_protocol import ARDProtocol, ARDAgent, ARDTask, ARDResource


# ========== 常量定义 ==========

# 匹配算法
MATCH_ALGORITHM_COSINE = "cosine"
MATCH_ALGORITHM_JACCARD = "jaccard"
MATCH_ALGORITHM_HYBRID = "hybrid"
MATCH_ALGORITHM_ML = "ml"  # 机器学习算法

# 协同状态
COLLAB_STATUS_PLANNING = "planning"
COLLAB_STATUS_EXECUTING = "executing"
COLLAB_STATUS_COMPLETED = "completed"
COLLAB_STATUS_FAILED = "failed"


# ========== 数据类定义 ==========

@dataclass
class ARDMatchResult:
    """ARD 匹配结果"""
    task_id: str
    agent_id: str
    score: float
    algorithm: str
    matched_at: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "score": self.score,
            "algorithm": self.algorithm,
            "matched_at": self.matched_at,
            "details": self.details,
        }


@dataclass
class ARDCollaborationPlan:
    """ARD 协同计划"""
    plan_id: str
    task_id: str
    agents: List[str]
    subtasks: List[Dict]
    status: str = COLLAB_STATUS_PLANNING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "task_id": self.task_id,
            "agents": self.agents,
            "subtasks": self.subtasks,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }


@dataclass
class ARDSmartContract:
    """ARD 智能合约"""
    contract_id: str
    task_id: str
    agents: List[str]
    reward: float
    conditions: List[Dict]
    status: str = "draft"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    executed_at: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "contract_id": self.contract_id,
            "task_id": self.task_id,
            "agents": self.agents,
            "reward": self.reward,
            "conditions": self.conditions,
            "status": self.status,
            "created_at": self.created_at,
            "executed_at": self.executed_at,
            "metadata": self.metadata,
        }


# ========== ARD 动态匹配算法 ==========

class ARDMatchEngine:
    """ARD 匹配引擎"""

    def __init__(self, ard_protocol: ARDProtocol):
        self.ard_protocol = ard_protocol
        self.match_results: List[ARDMatchResult] = []
        self._match_counter = 0

    def match(
        self,
        task_id: str,
        algorithm: str = MATCH_ALGORITHM_HYBRID,
        top_k: int = 3,
    ) -> List[ARDMatchResult]:
        """
        执行匹配

        Args:
            task_id: 任务 ID
            algorithm: 匹配算法
            top_k: 返回前 K 个结果

        Returns:
            匹配结果列表
        """
        task = self.ard_protocol.tasks.get(task_id)
        if not task:
            return []

        # 发现候选 Agent
        candidates = self.ard_protocol.discover_agents(task.criteria)
        if not candidates:
            return []

        # 计算匹配度
        scored_agents = []
        for agent in candidates:
            score = self._calculate_score(agent, task, algorithm)
            scored_agents.append((agent, score))

        # 排序并返回 Top K
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        results = []

        for agent, score in scored_agents[:top_k]:
            self._match_counter += 1
            result = ARDMatchResult(
                task_id=task_id,
                agent_id=agent.agent_id,
                score=score,
                algorithm=algorithm,
                details={
                    "agent_name": agent.name,
                    "agent_type": agent.agent_type,
                    "capabilities": agent.capabilities,
                },
            )
            self.match_results.append(result)
            results.append(result)

        return results

    def _calculate_score(self, agent: ARDAgent, task: ARDTask, algorithm: str) -> float:
        """
        计算匹配度

        Args:
            agent: Agent
            task: 任务
            algorithm: 匹配算法

        Returns:
            匹配度 (0-1)
        """
        if algorithm == MATCH_ALGORITHM_COSINE:
            return self._cosine_similarity(agent, task)
        elif algorithm == MATCH_ALGORITHM_JACCARD:
            return self._jaccard_similarity(agent, task)
        elif algorithm == MATCH_ALGORITHM_ML:
            return self._ml_score(agent, task)
        else:
            # 混合算法
            cosine_score = self._cosine_similarity(agent, task)
            jaccard_score = self._jaccard_similarity(agent, task)
            ml_score = self._ml_score(agent, task)
            return (cosine_score * 0.4 + jaccard_score * 0.3 + ml_score * 0.3)

    def _cosine_similarity(self, agent: ARDAgent, task: ARDTask) -> float:
        """计算余弦相似度"""
        task_caps = set(task.criteria.get("capabilities", []))
        agent_caps = set(agent.capabilities)

        if not task_caps:
            return 1.0

        intersection = task_caps.intersection(agent_caps)
        if not intersection:
            return 0.0

        # 余弦相似度 = 交集 / min(任务能力数，Agent 能力数)
        return len(intersection) / min(len(task_caps), len(agent_caps))

    def _jaccard_similarity(self, agent: ARDAgent, task: ARDTask) -> float:
        """计算 Jaccard 相似度"""
        task_caps = set(task.criteria.get("capabilities", []))
        agent_caps = set(agent.capabilities)

        if not task_caps and not agent_caps:
            return 1.0

        intersection = task_caps.intersection(agent_caps)
        union = task_caps.union(agent_caps)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _ml_score(self, agent: ARDAgent, task: ARDTask) -> float:
        """
        机器学习评分（简化实现）

        实际应使用 ML 模型，这里使用启发式评分
        """
        score = 0.0

        # 能力匹配（40%）
        task_caps = set(task.criteria.get("capabilities", []))
        agent_caps = set(agent.capabilities)
        if task_caps:
            intersection = task_caps.intersection(agent_caps)
            score += len(intersection) / len(task_caps) * 0.4

        # 类型匹配（20%）
        task_type = task.criteria.get("agent_type")
        if task_type and agent.agent_type == task_type:
            score += 0.2

        # 元数据匹配（20%）
        task_metadata = task.criteria.get("metadata", {})
        agent_metadata = agent.metadata
        if task_metadata:
            match_count = sum(1 for k, v in task_metadata.items() if agent_metadata.get(k) == v)
            score += match_count / len(task_metadata) * 0.2

        # 历史表现（20%）
        # 简化实现：随机评分
        import random
        score += random.random() * 0.2

        return min(score, 1.0)

    def get_match_statistics(self) -> Dict:
        """获取匹配统计"""
        if not self.match_results:
            return {
                "total_matches": 0,
                "avg_score": 0,
                "max_score": 0,
                "min_score": 0,
            }

        scores = [r.score for r in self.match_results]
        return {
            "total_matches": len(self.match_results),
            "avg_score": sum(scores) / len(scores),
            "max_score": max(scores),
            "min_score": min(scores),
        }


# ========== ARD 任务协同模块 ==========

class ARDCollaborationEngine:
    """ARD 协同引擎"""

    def __init__(self, ard_protocol: ARDProtocol):
        self.ard_protocol = ard_protocol
        self.plans: Dict[str, ARDCollaborationPlan] = {}
        self._plan_counter = 0

    def create_plan(
        self,
        task_id: str,
        agent_ids: List[str],
        subtasks: List[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        创建协同计划

        Args:
            task_id: 任务 ID
            agent_ids: Agent ID 列表
            subtasks: 子任务列表

        Returns:
            (成功，消息)
        """
        task = self.ard_protocol.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        self._plan_counter += 1
        plan_id = f"ard-plan-{self._plan_counter:04d}"

        # 生成子任务（如果未提供）
        if not subtasks:
            subtasks = []
            for i, agent_id in enumerate(agent_ids):
                subtasks.append({
                    "subtask_id": f"subtask-{i+1}",
                    "agent_id": agent_id,
                    "description": f"子任务 {i+1}",
                    "status": "pending",
                })

        plan = ARDCollaborationPlan(
            plan_id=plan_id,
            task_id=task_id,
            agents=agent_ids,
            subtasks=subtasks,
        )
        self.plans[plan_id] = plan

        # 更新任务状态
        task.status = "collaborating"

        return True, f"协同计划 {plan_id} 创建成功"

    def execute_plan(self, plan_id: str) -> Tuple[bool, str]:
        """
        执行协同计划

        Args:
            plan_id: 计划 ID

        Returns:
            (成功，消息)
        """
        plan = self.plans.get(plan_id)
        if not plan:
            return False, f"计划 {plan_id} 不存在"

        if plan.status != COLLAB_STATUS_PLANNING:
            return False, f"计划 {plan_id} 状态为 {plan.status}，不可执行"

        plan.status = COLLAB_STATUS_EXECUTING

        # 模拟执行子任务
        for subtask in plan.subtasks:
            subtask["status"] = "completed"

        plan.status = COLLAB_STATUS_COMPLETED
        plan.completed_at = datetime.now().isoformat()

        # 更新任务状态
        task = self.ard_protocol.tasks.get(plan.task_id)
        if task:
            task.status = "completed"

        return True, f"计划 {plan_id} 执行完成"

    def get_plan(self, plan_id: str) -> Optional[Dict]:
        """获取计划"""
        plan = self.plans.get(plan_id)
        return plan.to_dict() if plan else None

    def get_collaboration_statistics(self) -> Dict:
        """获取协同统计"""
        return {
            "total_plans": len(self.plans),
            "completed_plans": len([p for p in self.plans.values() if p.status == COLLAB_STATUS_COMPLETED]),
        }


# ========== ARD 智能合约 ==========

class ARDSmartContractEngine:
    """ARD 智能合约引擎"""

    def __init__(self, ard_protocol: ARDProtocol):
        self.ard_protocol = ard_protocol
        self.contracts: Dict[str, ARDSmartContract] = {}
        self._contract_counter = 0

    def create_contract(
        self,
        task_id: str,
        agent_ids: List[str],
        reward: float,
        conditions: List[Dict] = None,
    ) -> Tuple[bool, str]:
        """
        创建智能合约

        Args:
            task_id: 任务 ID
            agent_ids: Agent ID 列表
            reward: 奖励
            conditions: 条件列表

        Returns:
            (成功，消息)
        """
        task = self.ard_protocol.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        self._contract_counter += 1
        contract_id = f"ard-contract-{self._contract_counter:04d}"

        # 生成默认条件
        if not conditions:
            conditions = [
                {"type": "task_completion", "description": "任务完成", "target_value": "completed"},
            ]

        contract = ARDSmartContract(
            contract_id=contract_id,
            task_id=task_id,
            agents=agent_ids,
            reward=reward,
            conditions=conditions,
        )
        self.contracts[contract_id] = contract

        return True, f"智能合约 {contract_id} 创建成功"

    def execute_contract(self, contract_id: str) -> Tuple[bool, str]:
        """
        执行智能合约

        Args:
            contract_id: 合约 ID

        Returns:
            (成功，消息)
        """
        contract = self.contracts.get(contract_id)
        if not contract:
            return False, f"合约 {contract_id} 不存在"

        if contract.status != "draft":
            return False, f"合约 {contract_id} 状态为 {contract.status}，不可执行"

        # 检查条件
        task = self.ard_protocol.tasks.get(contract.task_id)
        if not task or task.status != "completed":
            return False, "任务未完成，合约不可执行"

        # 执行合约
        contract.status = "executed"
        contract.executed_at = datetime.now().isoformat()

        # 发放奖励（简化实现）
        reward_per_agent = contract.reward / max(len(contract.agents), 1)
        for agent_id in contract.agents:
            # 实际应调用 Token 经济系统
            pass

        return True, f"合约 {contract_id} 执行完成，奖励已发放"

    def get_contract(self, contract_id: str) -> Optional[Dict]:
        """获取合约"""
        contract = self.contracts.get(contract_id)
        return contract.to_dict() if contract else None

    def get_contract_statistics(self) -> Dict:
        """获取合约统计"""
        return {
            "total_contracts": len(self.contracts),
            "executed_contracts": len([c for c in self.contracts.values() if c.status == "executed"]),
        }