#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL-Orchestrator 自主编排引擎 — 入口模块

基于简化 Q-Learning / DQN 实现任务分解、Agent 匹配与调度决策。

子模块：
- dqn_engine.py:   Q-Learning / DQN 决策引擎
- scheduler.py:    任务分解、Agent 匹配、执行监控、编排入口
- fitness_tracker.py: 自进化闭环（适应度追踪）

参考：自主编排引擎(RL-Orchestrator)算法预研技术方案
"""

from .dqn_engine import RLScheduler, DQNScheduler
from .scheduler import (
    TaskStatus,
    AgentType,
    AgentCard,
    SubTask,
    TaskDAG,
    TaskDecomposer,
    CapabilityMatcher,
    ExecutionMonitor,
    RLOrchestrator,
    create_default_agents,
)
from .fitness_tracker import SelfEvolutionLoop

__all__ = [
    "RLScheduler",
    "DQNScheduler",
    "TaskStatus",
    "AgentType",
    "AgentCard",
    "SubTask",
    "TaskDAG",
    "TaskDecomposer",
    "CapabilityMatcher",
    "ExecutionMonitor",
    "RLOrchestrator",
    "SelfEvolutionLoop",
    "create_default_agents",
]
