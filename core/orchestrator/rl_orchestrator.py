#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL-Orchestrator 自主编排引擎

基于简化的 Q-Learning 实现任务分解、Agent 匹配与调度决策。

核心组件：
- TaskDecomposer:  任务递归分解为子任务 DAG（参考 RAD 三层）
- CapabilityMatcher: 基于 Agent Card 能力画像三维匹配
- RLScheduler:      简化 Q-Learning 调度决策
- ExecutionMonitor: 进度跟踪、异常检测、重调度触发

参考：自主编排引擎(RL-Orchestrator)算法预研技术方案
"""

import json
import math
import random
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# 日志
# ============================================================

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("rl_orchestrator")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(LOG_DIR / "orchestrator.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_handler)


# ============================================================
# 数据模型
# ============================================================

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"


class AgentType(str, Enum):
    COACH = "coach"        # 教练 hermes
    STUDENT = "student"    # 学生虾
    BUSINESS = "business"  # 业务虾
    ROUTER = "router"      # 路由虾


@dataclass
class AgentCard:
    """Agent 能力画像卡片"""
    agent_id: str
    agent_type: AgentType
    capabilities: List[str] = field(default_factory=list)
    cost: float = 1.0        # 成本（越低越好）
    speed: float = 1.0       # 速度（越高越好）
    quality: float = 0.8     # 质量（0-1，越高越好）
    available: bool = True
    max_concurrent: int = 1
    current_load: int = 0

    def score(self) -> float:
        """综合能力分数"""
        return (self.quality * 0.5 + self.speed * 0.3 + (1.0 / max(self.cost, 0.1)) * 0.2)


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    name: str
    description: str
    required_capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)   # 前置子任务 ID
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    priority: int = 1               # 优先级 1-5，5 最高
    estimated_duration_s: float = 60.0
    result: Optional[str] = None


@dataclass
class TaskDAG:
    """任务 DAG"""
    root_task_id: str
    subtasks: Dict[str, SubTask] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_ready_tasks(self) -> List[SubTask]:
        """获取所有就绪任务（依赖已完成）"""
        ready = []
        for t in self.subtasks.values():
            if t.status != TaskStatus.PENDING:
                continue
            deps_met = all(
                self.subtasks[dep].status == TaskStatus.COMPLETED
                for dep in t.dependencies
                if dep in self.subtasks
            )
            if deps_met:
                ready.append(t)
        return ready


# ============================================================
# TaskDecomposer — 任务递归分解（RAD 三层）
# ============================================================

class TaskDecomposer:
    """
    任务分解器 — 参考 RAD（递归自主式分解）三层架构：
    1. 理解层：解析任务意图和复杂度
    2. 分解层：生成子任务 DAG
    3. 验证层：检查依赖完整性和可行性
    """

    def __init__(self, max_depth: int = 3, max_subtasks: int = 20):
        self.max_depth = max_depth
        self.max_subtasks = max_subtasks

    def decompose(self, task_description: str, task_id_prefix: str = "T") -> TaskDAG:
        """
        将任务描述分解为子任务 DAG。

        分解策略（基于规则而非 LLM 调用，保证确定性）：
        - 按动词拆解：分析/搜索/生成/汇总/部署
        - 复杂任务拆分为：搜索 → 分析 → 生成 → 验证
        - 简单任务不拆分
        """
        logger.info(f"TaskDecomposer: 分解任务 [{task_id_prefix}] {task_description[:60]}...")

        dag = TaskDAG(root_task_id=f"{task_id_prefix}_root")
        desc_lower = task_description.lower()

        # 简单任务不拆分
        if self._is_simple(desc_lower):
            subtask = SubTask(
                task_id=f"{task_id_prefix}_0",
                name=task_description[:40],
                description=task_description,
                required_capabilities=["basic"],
            )
            dag.subtasks[subtask.task_id] = subtask
            logger.info(f"  简单任务，不拆分 -> {subtask.task_id}")
            return dag

        subtasks: List[SubTask] = []
        counter = 0

        # 搜索阶段
        if any(kw in desc_lower for kw in ["搜索", "查找", "找", "检索", "search", "find"]):
            sid = f"{task_id_prefix}_{counter}"
            subtasks.append(SubTask(
                task_id=sid, name="搜索与信息检索",
                description="检索相关信息", required_capabilities=["search", "retrieval"],
                dependencies=[], priority=4,
            ))
            counter += 1

        # 分析阶段
        if any(kw in desc_lower for kw in ["分析", "对比", "总结", "评估", "分析", "analyze", "compare"]):
            sid = f"{task_id_prefix}_{counter}"
            prev = [subtasks[-1].task_id] if subtasks else []
            subtasks.append(SubTask(
                task_id=sid, name="深度分析与推理",
                description="对检索结果进行深度分析", required_capabilities=["analysis", "reasoning"],
                dependencies=prev, priority=3,
            ))
            counter += 1

        # 生成阶段
        if any(kw in desc_lower for kw in ["生成", "写", "创建", "制作", "输出", "generate", "write", "create"]):
            sid = f"{task_id_prefix}_{counter}"
            prev = [subtasks[-1].task_id] if subtasks else []
            subtasks.append(SubTask(
                task_id=sid, name="内容生成与输出",
                description="生成最终交付物", required_capabilities=["generation", "writing"],
                dependencies=prev, priority=2,
            ))
            counter += 1

        # 验证阶段
        if any(kw in desc_lower for kw in ["验证", "测试", "检查", "校验", "validate", "test", "check"]):
            sid = f"{task_id_prefix}_{counter}"
            prev = [subtasks[-1].task_id] if subtasks else []
            subtasks.append(SubTask(
                task_id=sid, name="结果验证与校验",
                description="验证输出质量和正确性", required_capabilities=["validation"],
                dependencies=prev, priority=2,
            ))
            counter += 1

        # 兜底：至少一个子任务
        if not subtasks:
            subtasks.append(SubTask(
                task_id=f"{task_id_prefix}_0",
                name=task_description[:40],
                description=task_description,
                required_capabilities=["basic"],
            ))

        for st in subtasks:
            dag.subtasks[st.task_id] = st

        logger.info(f"  分解为 {len(subtasks)} 个子任务")
        return dag

    def _is_simple(self, desc_lower: str) -> bool:
        """判断是否简单任务"""
        complex_indicators = [
            "分析", "对比", "评估", "汇总", "整理", "多", "批量",
            "analyze", "compare", "evaluate", "batch", "multiple",
        ]
        return not any(ind in desc_lower for ind in complex_indicators)


# ============================================================
# CapabilityMatcher — Agent 能力匹配
# ============================================================

class CapabilityMatcher:
    """
    能力匹配器 — 基于 Agent Card 的三维能力画像匹配

    画像维度：
    - cost：成本
    - speed：速度
    - quality：质量
    """

    def __init__(self, agent_registry: Optional[List[AgentCard]] = None):
        self.agents: Dict[str, AgentCard] = {}
        if agent_registry:
            for agent in agent_registry:
                self.register(agent)

    def register(self, agent: AgentCard):
        """注册 Agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"CapabilityMatcher: 注册 Agent [{agent.agent_id}] 类型={agent.agent_type.value} 分={agent.score():.2f}")

    def unregister(self, agent_id: str):
        """注销 Agent"""
        self.agents.pop(agent_id, None)

    def match(self, subtask: SubTask, top_k: int = 3) -> List[Tuple[AgentCard, float]]:
        """
        为子任务匹配最合适的 Agent。

        返回 [(AgentCard, match_score), ...] 按分数降序。
        """
        candidates = []
        for agent in self.agents.values():
            if not agent.available:
                continue
            if agent.current_load >= agent.max_concurrent:
                continue

            # 能力覆盖度
            capability_match = self._capability_overlap(agent.capabilities, subtask.required_capabilities)

            # 综合匹配分数
            match_score = agent.score() * capability_match

            # 负载惩罚
            load_penalty = 1.0 - 0.15 * agent.current_load
            match_score *= load_penalty

            candidates.append((agent, match_score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:top_k]

    def _capability_overlap(self, agent_caps: List[str], required_caps: List[str]) -> float:
        """计算能力覆盖度（Jaccard-like）"""
        if not required_caps:
            return 1.0
        agent_set = set(c.lower() for c in agent_caps)
        required_set = set(c.lower() for c in required_caps)
        overlap = len(agent_set & required_set)
        return overlap / len(required_set) if required_set else 1.0

    def assign(self, subtask: SubTask, agent_id: str) -> bool:
        """分配 Agent 给子任务"""
        if agent_id not in self.agents:
            return False
        agent = self.agents[agent_id]
        if agent.current_load >= agent.max_concurrent:
            return False
        subtask.assigned_agent = agent_id
        agent.current_load += 1
        logger.info(f"  分配: [{subtask.task_id}] -> Agent [{agent_id}] (负载 {agent.current_load}/{agent.max_concurrent})")
        return True

    def release(self, agent_id: str):
        """释放 Agent 负载"""
        if agent_id in self.agents:
            self.agents[agent_id].current_load = max(0, self.agents[agent_id].current_load - 1)


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


# ============================================================
# ExecutionMonitor — 执行监控
# ============================================================

class ExecutionMonitor:
    """
    执行监控器 — 跟踪进度、检测异常、触发重调度
    """

    def __init__(self, max_retries: int = 2, timeout_s: float = 300.0):
        self.max_retries = max_retries
        self.timeout_s = timeout_s
        self._task_attempts: Dict[str, int] = {}
        self._task_start_times: Dict[str, float] = {}
        self._events: List[dict] = []

    def start_task(self, task_id: str):
        """记录任务开始"""
        self._task_start_times[task_id] = datetime.now().timestamp()
        self._task_attempts[task_id] = self._task_attempts.get(task_id, 0) + 1
        self._log_event("task_start", task_id, f"尝试 {self._task_attempts[task_id]}")

    def check_timeout(self, task_id: str) -> bool:
        """检查是否超时"""
        if task_id not in self._task_start_times:
            return False
        elapsed = datetime.now().timestamp() - self._task_start_times[task_id]
        return elapsed > self.timeout_s

    def can_retry(self, task_id: str) -> bool:
        """检查是否可重试"""
        return self._task_attempts.get(task_id, 0) < (self.max_retries + 1)

    def mark_completed(self, task_id: str, result: Optional[str] = None):
        """标记任务完成"""
        elapsed = 0.0
        if task_id in self._task_start_times:
            elapsed = datetime.now().timestamp() - self._task_start_times.pop(task_id)
        self._log_event("task_completed", task_id, f"耗时 {elapsed:.1f}s")
        logger.info(f"  ExecutionMonitor: [{task_id}] 完成 ({elapsed:.1f}s)")

    def mark_failed(self, task_id: str, error: str):
        """标记任务失败"""
        self._log_event("task_failed", task_id, error)
        logger.warning(f"  ExecutionMonitor: [{task_id}] 失败 - {error}")

    def mark_delegated(self, task_id: str, target_agent: str):
        """标记任务委托"""
        self._log_event("task_delegated", task_id, f"-> {target_agent}")
        if task_id in self._task_start_times:
            del self._task_start_times[task_id]

    def get_progress(self, dag: TaskDAG) -> dict:
        """获取 DAG 执行进度"""
        total = len(dag.subtasks)
        completed = sum(1 for t in dag.subtasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in dag.subtasks.values() if t.status == TaskStatus.FAILED)
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": total - completed - failed,
            "progress_pct": round(completed / total * 100, 1) if total else 0,
        }

    def _log_event(self, event_type: str, task_id: str, detail: str):
        self._events.append({
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "task_id": task_id,
            "detail": detail,
        })

    def get_events(self, last_n: int = 50) -> List[dict]:
        return self._events[-last_n:]


# ============================================================
# RLOrchestrator 主类
# ============================================================

class RLOrchestrator:
    """
    自主编排引擎主控制器。

    编排流程：
    任务进入 → Decomposer分解 → Matcher匹配Agent → Scheduler决策
    → 执行 → Monitor监控 → 完成/失败 → 更新Q-table

    用法:
        orch = RLOrchestrator()
        orch.register_agent(AgentCard(...))
        result = orch.orchestrate("分析这份报告并生成PPT")
    """

    def __init__(self):
        self.decomposer = TaskDecomposer()
        self.matcher = CapabilityMatcher()
        self.scheduler = RLScheduler()
        self.monitor = ExecutionMonitor()
        self.current_dag: Optional[TaskDAG] = None

    def register_agent(self, agent: AgentCard):
        """注册 Agent"""
        self.matcher.register(agent)

    def register_agents(self, agents: List[AgentCard]):
        """批量注册 Agent"""
        for agent in agents:
            self.matcher.register(agent)

    def orchestrate(self, task_description: str) -> Dict[str, Any]:
        """
        编排执行一个任务。

        返回执行结果汇总。
        """
        logger.info(f"{'='*50}")
        logger.info(f"RLOrchestrator: 开始编排 [{task_description[:60]}...]")

        # Phase 1: 分解
        dag = self.decomposer.decompose(task_description)
        self.current_dag = dag

        # Phase 2: 为每个子任务匹配 Agent
        assignments = {}
        for st in dag.subtasks.values():
            candidates = self.matcher.match(st, top_k=3)
            if candidates:
                best_agent, score = candidates[0]
                self.matcher.assign(st, best_agent.agent_id)
                assignments[st.task_id] = {
                    "agent": best_agent.agent_id,
                    "score": round(score, 3),
                    "alternatives": [(a.agent_id, round(s, 3)) for a, s in candidates[1:]],
                }
                logger.info(f"  [{st.task_id}] -> {best_agent.agent_id} (score={score:.3f})")
            else:
                logger.warning(f"  [{st.task_id}] 无可用 Agent")

        # Phase 3: 调度决策
        queue_len = len(dag.get_ready_tasks())
        resource_util = sum(a.current_load / max(a.max_concurrent, 1) for a in self.matcher.agents.values()) / max(len(self.matcher.agents), 1)
        urgency = self._estimate_urgency(dag)

        action, state = self.scheduler.select_action(queue_len, resource_util, urgency)
        action_name = RLScheduler.Action(action).name

        # Phase 4: 模拟执行（标记为 complete，真实场景由外部循环驱动）
        for st in dag.subtasks.values():
            if st.assigned_agent:
                st.status = TaskStatus.COMPLETED
                self.monitor.mark_completed(st.task_id)

        progress = self.monitor.get_progress(dag)
        q_stats = self.scheduler.get_q_table_stats()

        result = {
            "task": task_description,
            "dag": {
                "root_id": dag.root_task_id,
                "subtask_count": len(dag.subtasks),
                "subtasks": [
                    {
                        "id": st.task_id,
                        "name": st.name,
                        "assigned_agent": st.assigned_agent,
                        "status": st.status.value,
                    }
                    for st in dag.subtasks.values()
                ],
            },
            "scheduling": {
                "state": state,
                "action": action_name,
                "queue_len": queue_len,
                "resource_util": round(resource_util, 3),
                "urgency": round(urgency, 3),
            },
            "progress": progress,
            "q_table_stats": q_stats,
        }

        logger.info(f"编排完成: {progress['completed']}/{progress['total']} 完成")
        return result

    def _estimate_urgency(self, dag: TaskDAG) -> float:
        """估算任务紧急度（0-1）"""
        pending = sum(1 for t in dag.subtasks.values() if t.status == TaskStatus.PENDING)
        total = len(dag.subtasks)
        if total == 0:
            return 0.0
        return pending / total

    def update_reward(self, state: str, action: int, completion_time_s: float, quality: float, cost: float, next_state: str):
        """更新 Q-table（任务完成后调用）"""
        reward = self.scheduler.compute_reward(completion_time_s, quality, cost)
        self.scheduler.update(state, action, reward, next_state)
        logger.info(f"Q-table 更新: reward={reward:.3f}")

    def release_all(self):
        """释放所有 Agent 负载"""
        for agent_id in self.matcher.agents:
            self.matcher.release(agent_id)

    def get_events(self) -> List[dict]:
        return self.monitor.get_events()


# ============================================================
# 内置 Agent 注册表
# ============================================================

def create_default_agents() -> List[AgentCard]:
    """创建小龙虾网络默认 Agent 卡片"""
    return [
        AgentCard(
            agent_id="xiaochen",
            agent_type=AgentType.STUDENT,
            capabilities=["basic", "learning", "go", "analysis"],
            cost=0.5, speed=0.7, quality=0.75,
        ),
        AgentCard(
            agent_id="zhuguxia",
            agent_type=AgentType.STUDENT,
            capabilities=["basic", "learning", "go", "generation"],
            cost=0.5, speed=0.8, quality=0.8,
        ),
        AgentCard(
            agent_id="qoder",
            agent_type=AgentType.STUDENT,
            capabilities=["basic", "teaching", "go", "analysis"],
            cost=0.5, speed=0.6, quality=0.85,
        ),
        AgentCard(
            agent_id="hermes",
            agent_type=AgentType.COACH,
            capabilities=["coaching", "analysis", "reasoning", "generation", "validation", "research"],
            cost=1.0, speed=0.9, quality=0.95,
            max_concurrent=3,
        ),
        AgentCard(
            agent_id="zhugema",
            agent_type=AgentType.ROUTER,
            capabilities=["routing", "orchestration", "matching", "search", "retrieval"],
            cost=0.8, speed=0.85, quality=0.9,
            max_concurrent=5,
        ),
    ]
