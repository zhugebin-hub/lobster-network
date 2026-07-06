#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.2 — 动态团队架构搜索 (MaAS 风格)

基于任务难度动态选择Agent子团队，使用 DQN 学习最优团队组合策略。

核心概念（参考 MaAS ICML 2025 Oral）：
- Agentic Supernet: 大团队作为"超网"，按任务难度动态剪裁
- 性能/成本双目标优化: 性能 +11.82%，成本降至 45%
- TeamConfig: bitmap 编码选中哪些 Agent
- DQN: 学习最优团队组合策略

架构：
    Task → Difficulty Analyzer → DQN Policy Network → TeamConfig → Execution
"""

import json
import math
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger("dynamic_team_selector")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举与数据模型
# ============================================================

class TaskDifficulty(str, Enum):
    TRIVIAL = "trivial"       # 原子操作，1个Agent足够
    SIMPLE = "simple"         # 简单任务，2-3个Agent
    MODERATE = "moderate"     # 中等复杂，3-5个Agent
    COMPLEX = "complex"       # 复杂跨域，5-8个Agent
    EXPERT = "expert"         # 专家级，全团队


@dataclass
class AgentProfile:
    """Agent 能力画像"""
    agent_id: str
    name: str
    capabilities: List[str]         # 能力标签
    cost_per_task_lbc: float = 1.0  # 单位任务成本
    success_rate: float = 0.8       # 历史成功率
    avg_latency_ms: float = 1000.0  # 平均延迟
    specialization_score: Dict[str, float] = field(default_factory=dict)  # 领域专精度

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "cost_per_task_lbc": self.cost_per_task_lbc,
            "success_rate": self.success_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "specialization_score": self.specialization_score,
        }


@dataclass
class TeamConfig:
    """
    TeamConfig — bitmap 编码团队配置。

    bitmap: 长度为 N 的列表，每位 0/1 表示选中该 Agent。
    同时记录性能/成本预估。
    """
    bitmap: List[int]                    # [1, 0, 1, 1, 0, 0, ...]
    selected_agents: List[str]           # 选中的 agent_id 列表
    estimated_cost: float = 0.0
    estimated_success_rate: float = 0.0
    estimated_latency_ms: float = 0.0
    composite_score: float = 0.0         # 综合评分（性能+成本加权）

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bitmap": self.bitmap,
            "selected_agents": self.selected_agents,
            "estimated_cost": round(self.estimated_cost, 2),
            "estimated_success_rate": round(self.estimated_success_rate, 3),
            "estimated_latency_ms": round(self.estimated_latency_ms, 1),
            "composite_score": round(self.composite_score, 3),
        }


# ============================================================
# DifficultyAnalyzer — 任务难度分析器
# ============================================================

class DifficultyAnalyzer:
    """
    任务难度分析器 — 基于多维度特征判定难度等级。

    特征：
    - 任务领域跨度
    - 所需工具数量
    - 历史相似任务复杂度
    - 依赖链深度
    """

    # 难度关键词库
    DIFFICULTY_KEYWORDS = {
        TaskDifficulty.TRIVIAL: [
            "查询", "读取", "列表", "查看", "get", "list", "read",
        ],
        TaskDifficulty.SIMPLE: [
            "整理", "分类", "搜索", "汇总", "sort", "classify", "summarize",
        ],
        TaskDifficulty.MODERATE: [
            "分析", "生成", "转换", "计算", "analyze", "generate", "convert",
        ],
        TaskDifficulty.COMPLEX: [
            "优化", "重构", "设计", "架构", "optimize", "refactor", "design",
            "多Agent", "协作", "multi-agent",
        ],
        TaskDifficulty.EXPERT: [
            "训练", "调优", "安全审计", "合规", "train", "fine-tune",
            "security", "compliance", "production",
        ],
    }

    def analyze(self, task_description: str,
                context: Dict[str, Any] = None) -> Tuple[TaskDifficulty, Dict[str, Any]]:
        """
        分析任务难度。

        返回: (难度等级, 特征向量)
        """
        task_lower = task_description.lower()
        context = context or {}

        # 特征1: 关键词匹配
        scores = {}
        for level, keywords in self.DIFFICULTY_KEYWORDS.items():
            match_count = sum(1 for kw in keywords if kw.lower() in task_lower)
            scores[level] = min(5, match_count)

        # 特征2: 上下文信号
        feature_vector = {
            "task_length": len(task_description),
            "domain_count": context.get("domain_count", 1),
            "estimated_steps": context.get("estimated_steps", 1),
            "dependency_depth": context.get("dependency_depth", 0),
            "requires_human_review": context.get("requires_human_review", False),
        }

        # 综合判定
        max_score_level = max(scores, key=scores.get)
        max_score = scores[max_score_level]

        if feature_vector["requires_human_review"]:
            difficulty = TaskDifficulty.EXPERT
        elif feature_vector["estimated_steps"] > 10 or feature_vector["dependency_depth"] > 3:
            difficulty = TaskDifficulty.COMPLEX
        elif max_score >= 3:
            difficulty = max_score_level
        elif feature_vector["estimated_steps"] > 5:
            difficulty = TaskDifficulty.MODERATE
        elif feature_vector["estimated_steps"] > 2:
            difficulty = TaskDifficulty.SIMPLE
        else:
            difficulty = TaskDifficulty.TRIVIAL

        logger.debug(
            f"[DifficultyAnalyzer] 任务难度={difficulty.value}, "
            f"关键词匹配={scores}, 特征={feature_vector}"
        )
        return difficulty, feature_vector


# ============================================================
# DQN Policy Network — 强化学习团队选择
# ============================================================

class DQNTeamPolicy:
    """
    DQN 学习的团队组合策略网络（简化版）。

    状态空间: TaskDifficulty + 特征向量 → 编码为固定维度
    动作空间: TeamConfig bitmap (2^N 种可能组合)
    奖励: composite_score = alpha * success_rate - beta * cost

    使用 epsilon-greedy 探索 + experience replay。
    """

    def __init__(self, agent_pool: List[AgentProfile],
                 learning_rate: float = 0.01,
                 discount_factor: float = 0.95,
                 epsilon: float = 0.15,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        self.agent_pool = agent_pool
        self.num_agents = len(agent_pool)
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min

        # Q-table: state_hash → { action_tuple → q_value }
        self._q_table: Dict[str, Dict[Tuple[int, ...], float]] = {}
        self._replay_buffer: deque = deque(maxlen=1000)
        self._train_steps: int = 0
        logger.info(f"[DQNTeamPolicy] DQN 策略初始化, Agent池={self.num_agents}")

    def select_team(self, difficulty: TaskDifficulty,
                    feature_vector: Dict[str, Any]) -> TeamConfig:
        """
        epsilon-greedy 选择团队配置。
        """
        state_hash = self._hash_state(difficulty, feature_vector)

        if random.random() < self.epsilon:
            # 探索：随机选择
            bitmap = self._random_bitmap(difficulty)
        else:
            # 利用：选 Q 值最高的
            bitmap = self._greedy_bitmap(state_hash)

        return self._bitmap_to_config(bitmap)

    def learn(self, difficulty: TaskDifficulty, feature_vector: Dict[str, Any],
              bitmap: List[int], reward: float, next_diff: TaskDifficulty = None):
        """
        Q-learning 更新。

        Q(s, a) ← Q(s, a) + α * [r + γ * max_a' Q(s', a') - Q(s, a)]
        """
        state_hash = self._hash_state(difficulty, feature_vector)
        action_key = tuple(bitmap)

        # 当前 Q 值
        current_q = self._q_table.setdefault(state_hash, {}).get(action_key, 0.0)

        # 下一状态最大 Q 值
        if next_diff:
            next_hash = self._hash_state(next_diff, feature_vector)
            next_max = max(self._q_table.get(next_hash, {}).values(), default=0.0)
        else:
            next_max = 0.0

        # Q-learning 更新
        new_q = current_q + self.lr * (reward + self.gamma * next_max - current_q)
        self._q_table[state_hash][action_key] = new_q

        # epsilon 衰减
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self._train_steps += 1

        # 经验回放
        self._replay_buffer.append({
            "state": state_hash, "action": action_key,
            "reward": reward, "next_state": next_diff.value if next_diff else None,
        })

    def replay(self, batch_size: int = 32):
        """经验回放训练"""
        if len(self._replay_buffer) < batch_size:
            return
        batch = random.sample(list(self._replay_buffer), batch_size)
        for exp in batch:
            state_hash = exp["state"]
            action_key = exp["action"]
            reward = exp["reward"]

            next_max = 0.0
            if exp["next_state"]:
                next_hash = self._hash_state(TaskDifficulty(exp["next_state"]), {})
                next_max = max(self._q_table.get(next_hash, {}).values(), default=0.0)

            current_q = self._q_table.setdefault(state_hash, {}).get(action_key, 0.0)
            self._q_table[state_hash][action_key] = \
                current_q + self.lr * (reward + self.gamma * next_max - current_q)

    def _random_bitmap(self, difficulty: TaskDifficulty) -> List[int]:
        """按难度随机生成 bitmap"""
        sizes = {
            TaskDifficulty.TRIVIAL: (1, 1),
            TaskDifficulty.SIMPLE: (1, 3),
            TaskDifficulty.MODERATE: (2, 5),
            TaskDifficulty.COMPLEX: (4, 8),
            TaskDifficulty.EXPERT: (self.num_agents // 2, self.num_agents),
        }
        lo, hi = sizes.get(difficulty, (1, self.num_agents))
        target_size = random.randint(lo, min(hi, self.num_agents))

        # 随机选择 target_size 个 Agent
        indices = random.sample(range(self.num_agents), target_size)
        bitmap = [1 if i in indices else 0 for i in range(self.num_agents)]
        return bitmap

    def _greedy_bitmap(self, state_hash: str) -> List[int]:
        """选 Q 值最高的 bitmap"""
        q_values = self._q_table.get(state_hash, {})
        if not q_values:
            # 无记录，返回全选
            return [1] * self.num_agents

        best_action = max(q_values, key=q_values.get)
        return list(best_action)

    def _bitmap_to_config(self, bitmap: List[int]) -> TeamConfig:
        """将 bitmap 转为 TeamConfig"""
        selected = [self.agent_pool[i].agent_id for i, b in enumerate(bitmap) if b == 1]
        if not selected:
            # 至少选一个
            selected = [self.agent_pool[0].agent_id]
            bitmap[0] = 1

        # 性能/成本预估
        total_cost = sum(
            self.agent_pool[i].cost_per_task_lbc
            for i, b in enumerate(bitmap) if b
        )
        avg_success = sum(
            self.agent_pool[i].success_rate
            for i, b in enumerate(bitmap) if b
        ) / max(len(selected), 1)
        avg_latency = sum(
            self.agent_pool[i].avg_latency_ms
            for i, b in enumerate(bitmap) if b
        ) / max(len(selected), 1)

        # 复合评分: 性能 α=0.55, 成本 β=0.45
        alpha, beta = 0.55, 0.45
        cost_norm = total_cost / (self.num_agents * 5.0)  # 归一化
        composite = alpha * avg_success - beta * min(cost_norm, 1.0)

        return TeamConfig(
            bitmap=bitmap,
            selected_agents=selected,
            estimated_cost=total_cost,
            estimated_success_rate=avg_success,
            estimated_latency_ms=avg_latency,
            composite_score=max(0.0, composite),
        )

    @staticmethod
    def _hash_state(difficulty: TaskDifficulty,
                    feature_vector: Dict[str, Any]) -> str:
        """状态哈希（简化版）"""
        fv_bits = (
            f"{min(feature_vector.get('estimated_steps', 1), 15)}_"
            f"{min(feature_vector.get('domain_count', 1), 5)}_"
            f"{min(feature_vector.get('dependency_depth', 0), 5)}"
        )
        return f"{difficulty.value}|{fv_bits}"

    def get_stats(self) -> Dict[str, Any]:
        return {
            "train_steps": self._train_steps,
            "epsilon": round(self.epsilon, 4),
            "q_table_size": sum(len(v) for v in self._q_table.values()),
            "replay_buffer_size": len(self._replay_buffer),
        }


# ============================================================
# DynamicTeamSelector — 顶层协调器
# ============================================================

class DynamicTeamSelector:
    """
    动态团队架构搜索 (MaAS 风格)。

    完整管线：
    1. DifficultyAnalyzer 分析任务难度
    2. DQNTeamPolicy 选择最优团队 bitmap
    3. 产生 TeamConfig 输出
    4. 根据实际执行结果反馈 reward 进行学习

    预期效果（参考 MaAS 论文指标）：
    - 性能 +11.82%（vs 全量团队）
    - 成本 -55%（vs 全量团队）
    """

    def __init__(self, agent_pool: List[AgentProfile] = None,
                 learning_rate: float = 0.01):
        # 默认 Agent 池
        if agent_pool is None:
            agent_pool = self._default_agent_pool()

        self.agent_pool = agent_pool
        self.analyzer = DifficultyAnalyzer()
        self.policy = DQNTeamPolicy(agent_pool, learning_rate=learning_rate)
        self._selection_history: List[Dict[str, Any]] = []
        logger.info(f"[DynamicTeamSelector] 动态团队选择器已初始化, Agent池={len(agent_pool)}")

    @staticmethod
    def _default_agent_pool() -> List[AgentProfile]:
        """默认 Agent 池（对应小龙虾网络节点）"""
        return [
            AgentProfile("qoder", "Qoder", ["planning", "writing", "orchestration"],
                         cost_per_task_lbc=3.0, success_rate=0.85,
                         specialization_score={"paper": 0.95, "orchestration": 0.90}),
            AgentProfile("xiaochen", "XiaoChen", ["analysis", "coding", "data"],
                         cost_per_task_lbc=2.0, success_rate=0.82,
                         specialization_score={"code": 0.88, "data": 0.85}),
            AgentProfile("zhuguxia", "Zhuguxia", ["research", "literature", "analysis"],
                         cost_per_task_lbc=2.5, success_rate=0.80,
                         specialization_score={"research": 0.92, "literature": 0.90}),
            AgentProfile("hermes", "Hermes", ["infrastructure", "deployment", "security"],
                         cost_per_task_lbc=5.0, success_rate=0.90,
                         specialization_score={"infrastructure": 0.95, "security": 0.88}),
            AgentProfile("xiaowei", "XiaoWei", ["review", "verification", "quality"],
                         cost_per_task_lbc=1.5, success_rate=0.78,
                         specialization_score={"review": 0.85, "qa": 0.82}),
            AgentProfile("lobster-001", "Lobster-001", ["learning", "training", "optimization"],
                         cost_per_task_lbc=4.0, success_rate=0.75,
                         specialization_score={"rl": 0.90, "training": 0.85}),
            AgentProfile("museum-001", "Museum-001", ["knowledge", "retrieval", "archive"],
                         cost_per_task_lbc=1.0, success_rate=0.88,
                         specialization_score={"knowledge": 0.95, "retrieval": 0.92}),
        ]

    def select_team(self, task_description: str,
                    context: Dict[str, Any] = None) -> TeamConfig:
        """
        为给定任务选择最优 Agent 子团队。

        参数:
            task_description: 任务描述
            context: 额外上下文（预估步骤数、领域数等）

        返回:
            TeamConfig 含 bitmap + 成本/性能预估
        """
        # 1. 难度分析
        difficulty, features = self.analyzer.analyze(task_description, context)

        # 2. DQN 选择
        config = self.policy.select_team(difficulty, features)

        # 3. 基于难度修正
        config = self._refine_by_difficulty(config, difficulty)

        # 4. 记录
        record = {
            "task": task_description,
            "difficulty": difficulty.value,
            "config": config.to_dict(),
            "timestamp": datetime.now().isoformat(),
        }
        self._selection_history.append(record)

        logger.info(
            f"[DynamicTeamSelector] 任务难度={difficulty.value}, "
            f"选择 {len(config.selected_agents)}/{len(self.agent_pool)} 个Agent, "
            f"预估成本={config.estimated_cost:.1f} LBC, "
            f"预估成功率={config.estimated_success_rate:.2%}"
        )
        return config

    def _refine_by_difficulty(self, config: TeamConfig,
                               difficulty: TaskDifficulty) -> TeamConfig:
        """基于难度精细化修正团队规模"""
        max_sizes = {
            TaskDifficulty.TRIVIAL: 2,
            TaskDifficulty.SIMPLE: 3,
            TaskDifficulty.MODERATE: 5,
            TaskDifficulty.COMPLEX: 7,
            TaskDifficulty.EXPERT: len(self.agent_pool),
        }
        max_size = max_sizes.get(difficulty, len(self.agent_pool))

        if len(config.selected_agents) > max_size:
            # 裁剪：保留 bitmap 前 max_size 个选中项
            kept = 0
            for i in range(len(config.bitmap)):
                if config.bitmap[i]:
                    if kept < max_size:
                        kept += 1
                    else:
                        config.bitmap[i] = 0
            config.selected_agents = [
                self.agent_pool[i].agent_id
                for i, b in enumerate(config.bitmap) if b
            ]

        return config

    def give_feedback(self, task_description: str, actual_success: bool,
                      actual_cost: float, actual_latency_ms: float):
        """
        根据实际执行结果反馈 reward。

        奖励函数:
        - 成功: +1.0（reward cap=1.0）
        - 失败: -0.5
        - 成本节约: +0.3 * (full_cost - actual_cost)/full_cost
        - 延迟惩罚: -0.2 * (actual_latency / target_latency)
        """
        # 分析难度
        difficulty, features = self.analyzer.analyze(task_description, {})

        # 构建奖励
        success_reward = 1.0 if actual_success else -0.5

        full_pool_cost = sum(a.cost_per_task_lbc for a in self.agent_pool)
        cost_saving = (full_pool_cost - actual_cost) / max(full_pool_cost, 0.01)
        cost_reward = 0.3 * cost_saving

        target_latency = 5000  # ms
        latency_penalty = -0.2 * (actual_latency_ms / target_latency)

        reward = success_reward + cost_reward + latency_penalty
        reward = max(-1.0, min(1.0, reward))  # 裁剪

        # 最近的 selection record
        if self._selection_history:
            last_config = self._selection_history[-1].get("config", {})
            bitmap = last_config.get("bitmap", [])
            self.policy.learn(difficulty, features, bitmap, reward)

        logger.info(
            f"[DynamicTeamSelector] 反馈: success={actual_success}, "
            f"cost={actual_cost:.1f}, reward={reward:.3f}"
        )

    def get_status(self) -> Dict[str, Any]:
        return {
            "agent_pool_size": len(self.agent_pool),
            "policy_stats": self.policy.get_stats(),
            "selection_count": len(self._selection_history),
            "recent_selections": self._selection_history[-5:],
        }

    def get_agent_pool(self) -> List[AgentProfile]:
        return self.agent_pool
