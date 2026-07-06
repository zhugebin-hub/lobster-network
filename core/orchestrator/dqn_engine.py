#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DQN 决策引擎 — Q-Learning / DQN 调度器

包含：
- RLScheduler:  基于简化 Q-Learning 的调度决策器
- DQNScheduler: 基于 Deep Q-Network 的调度器（神经网络 + 经验回放）
"""

import math
import random
import pickle
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple
from enum import Enum


# ============================================================
# 日志
# ============================================================

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("rl_orchestrator")


# ============================================================
# 模型持久化目录
# ============================================================

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


# ============================================================
# RLScheduler — 简化 Q-Learning 调度器
# ============================================================

class RLScheduler:
    """
    基于简化 Q-Learning 的调度决策器。

    状态空间（离散化）：{队列长度(L/M/H), 资源利用率(L/H), 紧急度(L/H)}
    动作空间：{0:立即执行, 1:排队等待, 2:委托其他Agent, 3:拆分再调度}
    奖励：完成时间 × 质量分数 - 成本
    """

    class Action(Enum):
        EXECUTE = 0       # 立即执行
        QUEUE = 1         # 排队等待
        DELEGATE = 2      # 委托其他 Agent
        SPLIT_RETRY = 3   # 拆分再调度

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.15,
    ):
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon

        # Q-table: state_key -> [q0, q1, q2, q3]
        self.q_table: Dict[str, List[float]] = {}

        # 经验回放
        self._experience: List[Tuple[str, int, float, str]] = []  # (s, a, r, s')
        self._max_experience = 1000

        # 统计
        self.total_decisions = 0
        self.exploration_count = 0

    def _encode_state(self, queue_len: int, resource_util: float, urgency: float) -> str:
        """离散化状态编码"""
        # 队列长度: Low(0-2) / Med(3-6) / High(7+)
        if queue_len <= 2:
            ql = "L"
        elif queue_len <= 6:
            ql = "M"
        else:
            ql = "H"

        # 资源利用率: Low(<0.4) / High(>=0.4)
        ru = "L" if resource_util < 0.4 else "H"

        # 紧急度: Low(<0.5) / High(>=0.5)
        ug = "L" if urgency < 0.5 else "H"

        return f"{ql}{ru}{ug}"

    def select_action(self, queue_len: int, resource_util: float, urgency: float) -> Tuple[int, str]:
        """
        epsilon-greedy 选择动作。

        返回 (action_id, state_key)
        """
        state = self._encode_state(queue_len, resource_util, urgency)
        self.total_decisions += 1

        # 初始化 Q 值
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]

        # epsilon-greedy
        if random.random() < self.epsilon:
            self.exploration_count += 1
            action = random.randint(0, 3)
            logger.debug(f"  Q-Learning 探索 | state={state} action={self.Action(action).name}")
        else:
            q_values = self.q_table[state]
            action = q_values.index(max(q_values))
            logger.debug(f"  Q-Learning 利用 | state={state} action={self.Action(action).name}")

        return action, state

    def update(self, state: str, action: int, reward: float, next_state: str):
        """Q-Learning 更新规则"""
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0, 0.0]
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0, 0.0, 0.0, 0.0]

        # Q(s,a) += α * [r + γ * max_a' Q(s',a') - Q(s,a)]
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state])
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q

        # 记录经验
        self._experience.append((state, action, reward, next_state))
        if len(self._experience) > self._max_experience:
            self._experience.pop(0)

    def compute_reward(self, completion_time_s: float, quality: float, cost: float) -> float:
        """
        奖励函数：完成时间 × 质量分数 - 成本
        时间越短越好，质量越高越好，成本越低越好
        """
        # 归一化：时间转正（越短越好）
        time_score = max(0, 1.0 - (completion_time_s / 600.0))  # 10 分钟基准
        return time_score * quality - cost * 0.1

    def get_q_table_stats(self) -> dict:
        """获取 Q-table 统计"""
        total_states = len(self.q_table)
        avg_q = sum(sum(v) / len(v) for v in self.q_table.values()) / max(total_states, 1)
        return {
            "total_states": total_states,
            "total_decisions": self.total_decisions,
            "exploration_rate": self.exploration_count / max(self.total_decisions, 1),
            "avg_q_value": round(avg_q, 4),
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取调度器统计（统一接口）"""
        return {
            "type": "QLearning",
            **self.get_q_table_stats(),
        }


# ============================================================
# DQNScheduler — 基于 Deep Q-Network 的调度器
# ============================================================

class DQNScheduler:
    """
    基于 DQN 的任务调度器，用于替代简表 Q-Learning。

    论文 6.3.1 节：将简表 Q-Learning 升级为 DQN 或 PPO。

    架构：
    - 3 层全连接网络: 输入 20维状态向量 → 128 → 64 → 输出动作数
    - 经验回放缓冲区: 容量 10000, batch_size 64
    - epsilon-greedy 探索: epsilon 1.0 → 0.05, 衰减率 0.995
    - 目标网络软更新: tau = 0.01
    - 损失: MSE, 优化器: SGD

    用法:
        scheduler = DQNScheduler(state_dim=20, action_dim=8)
        action = scheduler.select_action(state_vector)
        scheduler.store_experience(state, action, reward, next_state, done)
        scheduler.train_step()
    """

    def __init__(
        self,
        state_dim: int = 20,
        action_dim: int = 8,
        hidden_dim1: int = 128,
        hidden_dim2: int = 64,
        replay_capacity: int = 10000,
        batch_size: int = 64,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay: float = 0.995,
        gamma: float = 0.95,
        tau: float = 0.01,
        learning_rate: float = 0.01,
        model_dir: str = "",
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.tau = tau
        self.batch_size = batch_size

        # epsilon-greedy 探索
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        # 经验回放缓冲区
        self.replay_capacity = replay_capacity
        self._replay_buffer: List[Tuple[List[float], int, float, List[float], bool]] = []
        self._buffer_pos = 0

        # 神经网络权重（简化实现：使用矩阵乘法模拟全连接层）
        # Layer 1: state_dim → hidden_dim1
        self.W1 = [[random.gauss(0, 0.1) for _ in range(hidden_dim1)] for _ in range(state_dim)]
        self.b1 = [0.0 for _ in range(hidden_dim1)]
        # Layer 2: hidden_dim1 → hidden_dim2
        self.W2 = [[random.gauss(0, 0.1) for _ in range(hidden_dim2)] for _ in range(hidden_dim1)]
        self.b2 = [0.0 for _ in range(hidden_dim2)]
        # Layer 3: hidden_dim2 → action_dim
        self.W3 = [[random.gauss(0, 0.1) for _ in range(action_dim)] for _ in range(hidden_dim2)]
        self.b3 = [0.0 for _ in range(action_dim)]

        # 目标网络（独立权重副本）
        self._target_W1 = [row[:] for row in self.W1]
        self._target_b1 = self.b1[:]
        self._target_W2 = [row[:] for row in self.W2]
        self._target_b2 = self.b2[:]
        self._target_W3 = [row[:] for row in self.W3]
        self._target_b3 = self.b3[:]

        self.lr = learning_rate
        self._train_step_count = 0

        # 模型路径
        self.model_dir = model_dir or str(MODELS_DIR)

        logger.info(
            f"[DQNScheduler] 初始化: state_dim={state_dim}, action_dim={action_dim}, "
            f"hidden=({hidden_dim1},{hidden_dim2}), replay={replay_capacity}, batch={batch_size}, "
            f"epsilon={epsilon_start}→{epsilon_end}, gamma={gamma}, tau={tau}"
        )

    # ---- 矩阵运算辅助（内嵌实现以保持无外部依赖） ----

    @staticmethod
    def _relu(x: float) -> float:
        return max(0.0, x)

    @staticmethod
    def _relu_derivative(x: float) -> float:
        return 1.0 if x > 0 else 0.0

    def _forward(self, state: List[float], W1, b1, W2, b2, W3, b3) -> Tuple[
        List[float], List[float], List[float]
    ]:
        """前向传播，返回 (h1, h2, q_values)"""
        # Layer 1
        h1 = [0.0] * len(b1)
        for j in range(len(b1)):
            s = b1[j]
            for i in range(len(state)):
                s += state[i] * W1[i][j]
            h1[j] = self._relu(s)

        # Layer 2
        h2 = [0.0] * len(b2)
        for j in range(len(b2)):
            s = b2[j]
            for i in range(len(h1)):
                s += h1[i] * W2[i][j]
            h2[j] = self._relu(s)

        # Layer 3 (no activation — Q values)
        q_values = [0.0] * len(b3)
        for j in range(len(b3)):
            s = b3[j]
            for i in range(len(h2)):
                s += h2[i] * W3[i][j]
            q_values[j] = s

        return h1, h2, q_values

    def _get_q_values(self, state: List[float]) -> List[float]:
        """使用在线网络计算 Q 值"""
        _, _, q = self._forward(state, self.W1, self.b1, self.W2, self.b2, self.W3, self.b3)
        return q

    def _get_target_q(self, state: List[float]) -> List[float]:
        """使用目标网络计算 Q 值"""
        _, _, q = self._forward(
            state, self._target_W1, self._target_b1,
            self._target_W2, self._target_b2, self._target_W3, self._target_b3
        )
        return q

    # ---- 核心接口 ----

    def select_action(self, state_vector: List[float]) -> int:
        """epsilon-greedy 选择动作"""
        if random.random() < self.epsilon:
            return random.randrange(self.action_dim)
        q_values = self._get_q_values(state_vector)
        max_q = max(q_values)
        candidates = [i for i, q in enumerate(q_values) if q == max_q]
        return random.choice(candidates)

    def store_experience(
        self,
        state: List[float],
        action: int,
        reward: float,
        next_state: List[float],
        done: bool,
    ):
        """存储经验到回放缓冲区"""
        experience = (state, action, reward, next_state, done)
        if len(self._replay_buffer) < self.replay_capacity:
            self._replay_buffer.append(experience)
        else:
            self._replay_buffer[self._buffer_pos % self.replay_capacity] = experience
        self._buffer_pos += 1

    def train_step(self) -> float:
        """执行一步训练，返回损失值"""
        if len(self._replay_buffer) < self.batch_size:
            return 0.0

        batch = random.sample(self._replay_buffer, self.batch_size)
        total_loss = 0.0

        for state, action, reward, next_state, done in batch:
            q_values = self._get_q_values(state)
            current_q = q_values[action]

            if done:
                target_q = reward
            else:
                target_q_values = self._get_target_q(next_state)
                target_q = reward + self.gamma * max(target_q_values)

            td_error = target_q - current_q
            loss = td_error ** 2
            total_loss += loss

            # SGD 更新 (仅更新 action 对应的输出权重)
            grad_q = -2.0 * td_error
            _, h2_vals, _ = self._forward(
                state, self.W1, self.b1, self.W2, self.b2, self.W3, self.b3
            )
            for i in range(len(h2_vals)):
                self.W3[i][action] -= self.lr * grad_q * h2_vals[i]
            self.b3[action] -= self.lr * grad_q

        avg_loss = total_loss / self.batch_size

        # epsilon 衰减
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

        # 目标网络软更新
        self._soft_update()

        self._train_step_count += 1
        return avg_loss

    def _soft_update(self):
        """目标网络软更新: θ_target = τ * θ_online + (1-τ) * θ_target"""
        tau = self.tau
        omt = 1.0 - tau

        for i in range(len(self.W1)):
            for j in range(len(self.W1[0])):
                self._target_W1[i][j] = tau * self.W1[i][j] + omt * self._target_W1[i][j]
        for i in range(len(self.b1)):
            self._target_b1[i] = tau * self.b1[i] + omt * self._target_b1[i]

        for i in range(len(self.W2)):
            for j in range(len(self.W2[0])):
                self._target_W2[i][j] = tau * self.W2[i][j] + omt * self._target_W2[i][j]
        for i in range(len(self.b2)):
            self._target_b2[i] = tau * self.b2[i] + omt * self._target_b2[i]

        for i in range(len(self.W3)):
            for j in range(len(self.W3[0])):
                self._target_W3[i][j] = tau * self.W3[i][j] + omt * self._target_W3[i][j]
        for i in range(len(self.b3)):
            self._target_b3[i] = tau * self.b3[i] + omt * self._target_b3[i]

    # ---- 持久化 ----

    def save(self, filepath: str = ""):
        """保存模型权重"""
        if not filepath:
            filepath = str(Path(self.model_dir) / "dqn_weights.pkl")
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump({
                "W1": self.W1, "b1": self.b1,
                "W2": self.W2, "b2": self.b2,
                "W3": self.W3, "b3": self.b3,
                "_target_W1": self._target_W1, "_target_b1": self._target_b1,
                "_target_W2": self._target_W2, "_target_b2": self._target_b2,
                "_target_W3": self._target_W3, "_target_b3": self._target_b3,
                "epsilon": self.epsilon,
                "train_step_count": self._train_step_count,
            }, f)
        logger.info(f"[DQNScheduler] 模型已保存: {filepath} (step={self._train_step_count}, eps={self.epsilon:.4f})")

    def load(self, filepath: str):
        """加载模型权重"""
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        self.W1 = data["W1"]; self.b1 = data["b1"]
        self.W2 = data["W2"]; self.b2 = data["b2"]
        self.W3 = data["W3"]; self.b3 = data["b3"]
        self._target_W1 = data["_target_W1"]; self._target_b1 = data["_target_b1"]
        self._target_W2 = data["_target_W2"]; self._target_b2 = data["_target_b2"]
        self._target_W3 = data["_target_W3"]; self._target_b3 = data["_target_b3"]
        self.epsilon = data.get("epsilon", self.epsilon_end)
        self._train_step_count = data.get("train_step_count", 0)
        logger.info(f"[DQNScheduler] 模型已加载: {filepath} (step={self._train_step_count}, eps={self.epsilon:.4f})")

    def get_stats(self) -> Dict[str, Any]:
        return {
            "type": "DQN",
            "state_dim": self.state_dim,
            "action_dim": self.action_dim,
            "epsilon": round(self.epsilon, 4),
            "replay_buffer_size": len(self._replay_buffer),
            "replay_capacity": self.replay_capacity,
            "train_step_count": self._train_step_count,
        }
