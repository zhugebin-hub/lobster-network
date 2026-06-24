#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 协议集成模块 V5.0
Agentic Resource Discovery 协议实现

功能：
1. Agent 发现（本地 + 远程）
2. 资源发现（API/技能/工作流）
3. 动态匹配（基于任务标准）
4. 任务协同（跨平台协作）
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ========== 常量定义 ==========

# ARD 协议版本
ARD_VERSION = "1.0"

# Agent 类型
AGENT_TYPE_GENERAL = "general"       # 通用 Agent
AGENT_TYPE_SPECIALIZED = "specialized" # 专用 Agent
AGENT_TYPE_COORDINATOR = "coordinator" # 协调 Agent

# 资源类型
RESOURCE_TYPE_API = "api"            # API 资源
RESOURCE_TYPE_SKILL = "skill"        # 技能资源
RESOURCE_TYPE_WORKFLOW = "workflow"  # 工作流资源
RESOURCE_TYPE_DATA = "data"          # 数据资源

# 匹配算法
MATCH_ALGORITHM_COSINE = "cosine"    # 余弦相似度
MATCH_ALGORITHM_JACCARD = "jaccard"  # Jaccard 相似度
MATCH_ALGORITHM_HYBRID = "hybrid"    # 混合算法


# ========== 数据类定义 ==========

@dataclass
class ARDAgent:
    """ARD Agent"""
    agent_id: str
    name: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    protocol: str = "ard"
    version: str = ARD_VERSION
    metadata: Dict = field(default_factory=dict)
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "capabilities": self.capabilities,
            "endpoint": self.endpoint,
            "protocol": self.protocol,
            "version": self.version,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
        }


@dataclass
class ARDResource:
    """ARD 资源"""
    resource_id: str
    name: str
    resource_type: str
    description: str
    endpoint: str
    provider_id: str
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "type": self.resource_type,
            "description": self.description,
            "endpoint": self.endpoint,
            "provider_id": self.provider_id,
            "metadata": self.metadata,
            "created_at": self.created_at,
        }


@dataclass
class ARDTask:
    """ARD 任务"""
    task_id: str
    title: str
    description: str
    criteria: Dict
    reward: float
    status: str = "pending"
    matched_agents: List[str] = field(default_factory=list)
    collaboration_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "criteria": self.criteria,
            "reward": self.reward,
            "status": self.status,
            "matched_agents": self.matched_agents,
            "collaboration_id": self.collaboration_id,
            "created_at": self.created_at,
        }


@dataclass
class ARDCollaboration:
    """ARD 协同任务"""
    collaboration_id: str
    task_id: str
    agents: List[str]
    status: str = "active"
    progress: float = 0.0
    emergence_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "collaboration_id": self.collaboration_id,
            "task_id": self.task_id,
            "agents": self.agents,
            "status": self.status,
            "progress": self.progress,
            "emergence_score": self.emergence_score,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


# ========== ARD 协议系统 ==========

class ARDProtocol:
    """ARD 协议系统"""

    def __init__(self, data_dir: str = "/shared/lobster-network-data/ard"):
        self.data_dir = data_dir
        self.agents: Dict[str, ARDAgent] = {}
        self.resources: Dict[str, ARDResource] = {}
        self.tasks: Dict[str, ARDTask] = {}
        self.collaborations: Dict[str, ARDCollaboration] = {}
        self._agent_counter = 0
        self._resource_counter = 0
        self._task_counter = 0
        self._collaboration_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== Agent 发现 ==========

    def register_agent(
        self,
        name: str,
        agent_type: str = AGENT_TYPE_GENERAL,
        capabilities: List[str] = None,
        endpoint: str = "",
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """
        注册 Agent

        Args:
            name: Agent 名称
            agent_type: Agent 类型
            capabilities: 能力列表
            endpoint: 端点地址
            metadata: 元数据

        Returns:
            (成功，消息)
        """
        self._agent_counter += 1
        agent_id = f"ard-agent-{self._agent_counter:04d}"

        agent = ARDAgent(
            agent_id=agent_id,
            name=name,
            agent_type=agent_type,
            capabilities=capabilities or [],
            endpoint=endpoint,
            metadata=metadata or {},
        )
        self.agents[agent_id] = agent

        return True, f"Agent {name} 注册成功 (ID: {agent_id})"

    def discover_agents(self, criteria: Dict) -> List[ARDAgent]:
        """
        发现符合标准的 Agent

        Args:
            criteria: 发现标准（类型/能力/位置等）

        Returns:
            符合条件的 Agent 列表
        """
        results = []

        for agent in self.agents.values():
            # 检查类型匹配
            if "type" in criteria and agent.agent_type != criteria["type"]:
                continue

            # 检查能力匹配
            if "capabilities" in criteria:
                required_caps = set(criteria["capabilities"])
                agent_caps = set(agent.capabilities)
                if not required_caps.issubset(agent_caps):
                    continue

            # 检查元数据匹配
            if "metadata" in criteria:
                for key, value in criteria["metadata"].items():
                    if agent.metadata.get(key) != value:
                        continue

            results.append(agent)

        return results

    # ========== 资源发现 ==========

    def register_resource(
        self,
        name: str,
        resource_type: str,
        description: str,
        endpoint: str,
        provider_id: str,
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """
        注册资源

        Args:
            name: 资源名称
            resource_type: 资源类型
            description: 资源描述
            endpoint: 端点地址
            provider_id: 提供者 ID
            metadata: 元数据

        Returns:
            (成功，消息)
        """
        self._resource_counter += 1
        resource_id = f"ard-resource-{self._resource_counter:04d}"

        resource = ARDResource(
            resource_id=resource_id,
            name=name,
            resource_type=resource_type,
            description=description,
            endpoint=endpoint,
            provider_id=provider_id,
            metadata=metadata or {},
        )
        self.resources[resource_id] = resource

        return True, f"资源 {name} 注册成功 (ID: {resource_id})"

    def discover_resources(self, resource_type: str, criteria: Dict = None) -> List[ARDResource]:
        """
        发现资源

        Args:
            resource_type: 资源类型
            criteria: 发现标准

        Returns:
            资源列表
        """
        results = []

        for resource in self.resources.values():
            # 检查类型匹配
            if resource.resource_type != resource_type:
                continue

            # 检查标准匹配
            if criteria:
                match = True
                for key, value in criteria.items():
                    if resource.metadata.get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            results.append(resource)

        return results

    # ========== 动态匹配 ==========

    def match_agents(
        self,
        task_id: str,
        match_algorithm: str = MATCH_ALGORITHM_HYBRID,
    ) -> Tuple[bool, str, List[str]]:
        """
        动态匹配最优 Agent

        Args:
            task_id: 任务 ID
            match_algorithm: 匹配算法

        Returns:
            (成功，消息，匹配的 Agent ID 列表)
        """
        task = self.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在", []

        # 发现候选 Agent
        candidates = self.discover_agents(task.criteria)
        if not candidates:
            return False, "无匹配 Agent", []

        # 计算匹配度
        scored_agents = []
        for agent in candidates:
            score = self._calculate_match_score(agent, task, match_algorithm)
            scored_agents.append((agent.agent_id, score))

        # 排序并返回 Top 3
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        matched_agents = [agent_id for agent_id, score in scored_agents[:3]]

        # 更新任务
        task.matched_agents = matched_agents
        task.status = "matched"

        return True, f"匹配成功，找到 {len(matched_agents)} 个 Agent", matched_agents

    def _calculate_match_score(
        self,
        agent: ARDAgent,
        task: ARDTask,
        algorithm: str,
    ) -> float:
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
        else:
            # 混合算法
            cosine_score = self._cosine_similarity(agent, task)
            jaccard_score = self._jaccard_similarity(agent, task)
            return (cosine_score + jaccard_score) / 2

    def _cosine_similarity(self, agent: ARDAgent, task: ARDTask) -> float:
        """计算余弦相似度"""
        # 简化实现：基于能力匹配
        task_capabilities = set(task.criteria.get("capabilities", []))
        agent_capabilities = set(agent.capabilities)

        if not task_capabilities:
            return 1.0

        intersection = task_capabilities.intersection(agent_capabilities)
        if not intersection:
            return 0.0

        return len(intersection) / min(len(task_capabilities), len(agent_capabilities))

    def _jaccard_similarity(self, agent: ARDAgent, task: ARDTask) -> float:
        """计算 Jaccard 相似度"""
        task_capabilities = set(task.criteria.get("capabilities", []))
        agent_capabilities = set(agent.capabilities)

        if not task_capabilities and not agent_capabilities:
            return 1.0

        intersection = task_capabilities.intersection(agent_capabilities)
        union = task_capabilities.union(agent_capabilities)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    # ========== 任务协同 ==========

    def create_task(
        self,
        title: str,
        description: str,
        criteria: Dict,
        reward: float = 10.0,
    ) -> Tuple[bool, str]:
        """
        创建 ARD 任务

        Args:
            title: 任务标题
            description: 任务描述
            criteria: 任务标准
            reward: 任务奖励

        Returns:
            (成功，消息)
        """
        self._task_counter += 1
        task_id = f"ard-task-{self._task_counter:04d}"

        task = ARDTask(
            task_id=task_id,
            title=title,
            description=description,
            criteria=criteria,
            reward=reward,
        )
        self.tasks[task_id] = task

        return True, f"任务 {title} 创建成功 (ID: {task_id})"

    def create_collaboration(
        self,
        task_id: str,
        agent_ids: List[str],
    ) -> Tuple[bool, str]:
        """
        创建协同任务

        Args:
            task_id: 任务 ID
            agent_ids: Agent ID 列表

        Returns:
            (成功，消息)
        """
        task = self.tasks.get(task_id)
        if not task:
            return False, f"任务 {task_id} 不存在"

        self._collaboration_counter += 1
        collaboration_id = f"ard-collab-{self._collaboration_counter:04d}"

        collaboration = ARDCollaboration(
            collaboration_id=collaboration_id,
            task_id=task_id,
            agents=agent_ids,
        )
        self.collaborations[collaboration_id] = collaboration

        # 更新任务
        task.collaboration_id = collaboration_id
        task.status = "collaborating"

        return True, f"协同任务 {collaboration_id} 创建成功"

    def update_collaboration_progress(
        self,
        collaboration_id: str,
        progress: float,
        emergence_score: float = 0.0,
    ) -> Tuple[bool, str]:
        """
        更新协同进度

        Args:
            collaboration_id: 协同任务 ID
            progress: 进度 (0-1)
            emergence_score: 涌现值

        Returns:
            (成功，消息)
        """
        collaboration = self.collaborations.get(collaboration_id)
        if not collaboration:
            return False, f"协同任务 {collaboration_id} 不存在"

        collaboration.progress = progress
        collaboration.emergence_score = emergence_score

        if progress >= 1.0:
            collaboration.status = "completed"
            collaboration.completed_at = datetime.now().isoformat()

            # 更新任务状态
            task = self.tasks.get(collaboration.task_id)
            if task:
                task.status = "completed"

        return True, f"协同进度已更新: {progress:.0%}"

    # ========== 查询功能 ==========

    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """获取 Agent"""
        agent = self.agents.get(agent_id)
        return agent.to_dict() if agent else None

    def get_resource(self, resource_id: str) -> Optional[Dict]:
        """获取资源"""
        resource = self.resources.get(resource_id)
        return resource.to_dict() if resource else None

    def get_task(self, task_id: str) -> Optional[Dict]:
        """获取任务"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_collaboration(self, collaboration_id: str) -> Optional[Dict]:
        """获取协同任务"""
        collaboration = self.collaborations.get(collaboration_id)
        return collaboration.to_dict() if collaboration else None

    def get_ard_statistics(self) -> Dict:
        """获取 ARD 统计"""
        return {
            "total_agents": len(self.agents),
            "total_resources": len(self.resources),
            "total_tasks": len(self.tasks),
            "total_collaborations": len(self.collaborations),
            "completed_collaborations": len([c for c in self.collaborations.values() if c.status == "completed"]),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "agents": {aid: a.to_dict() for aid, a in self.agents.items()},
            "resources": {rid: r.to_dict() for rid, r in self.resources.items()},
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()},
            "collaborations": {cid: c.to_dict() for cid, c in self.collaborations.items()},
            "counters": {
                "agent": self._agent_counter,
                "resource": self._resource_counter,
                "task": self._task_counter,
                "collaboration": self._collaboration_counter,
            },
        }
        with open(os.path.join(self.data_dir, "ard_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "ard_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.agents = {aid: ARDAgent(**a) for aid, a in data.get("agents", {}).items()}
            self.resources = {rid: ARDResource(**r) for rid, r in data.get("resources", {}).items()}
            self.tasks = {tid: ARDTask(**t) for tid, t in data.get("tasks", {}).items()}
            self.collaborations = {cid: ARDCollaboration(**c) for cid, c in data.get("collaborations", {}).items()}

            counters = data.get("counters", {})
            self._agent_counter = counters.get("agent", 0)
            self._resource_counter = counters.get("resource", 0)
            self._task_counter = counters.get("task", 0)
            self._collaboration_counter = counters.get("collaboration", 0)

            return True
        return False