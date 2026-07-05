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
        """
        估算任务紧急度（0-1），基于三个维度的加权计算：
        1. 未完成率：pending 子任务占比（权重 0.3）
        2. 优先级：最高优先级的归一化贡献（权重 0.3）
        3. 截止时间压力：最近截止时间距离现在的紧迫程度（权重 0.4）
        """
        total = len(dag.subtasks)
        if total == 0:
            return 0.0

        # 维度 1: 未完成率
        pending = sum(1 for t in dag.subtasks.values() if t.status == TaskStatus.PENDING)
        incomplete_ratio = pending / total

        # 维度 2: 优先级紧急度（取最高优先级归一化，5 为最高）
        max_priority = max((t.priority for t in dag.subtasks.values()), default=1)
        priority_urgency = max_priority / 5.0

        # 维度 3: 截止时间压力（无截止时间则返回 0）
        # 遍历 RUNNING/PENDING 子任务，取最早截止时间；无 deadline 信息时默认 0
        now_ts = datetime.now().timestamp()
        earliest_deadline = None
        for t in dag.subtasks.values():
            if t.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
                # deadline 不在 SubTask 字段中，通过 result 字段可能携带
                # 此处做防御性检查，若未来扩展 deadline 字段可直接生效
                dl = getattr(t, 'deadline', None)
                if dl:
                    dl_ts = dl.timestamp() if isinstance(dl, datetime) else float(dl)
                    if earliest_deadline is None or dl_ts < earliest_deadline:
                        earliest_deadline = dl_ts

        if earliest_deadline and earliest_deadline > now_ts:
            remaining = earliest_deadline - now_ts
            # 24h 内截止为最高紧急度 1.0，超过 7 天趋近于 0
            deadline_urgency = max(0.0, 1.0 - (remaining / (7 * 86400)))
        elif earliest_deadline and earliest_deadline <= now_ts:
            deadline_urgency = 1.0  # 已超期
        else:
            deadline_urgency = 0.0

        # 加权综合
        urgency = 0.3 * incomplete_ratio + 0.3 * priority_urgency + 0.4 * deadline_urgency
        return min(1.0, max(0.0, urgency))

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


# ============================================================
# DQNScheduler — 基于 Deep Q-Network 的调度器
# ============================================================

import pickle
import os as _os_module

# 确保 models 目录存在
MODELS_DIR = Path(__file__).resolve().parent / "models"
MODELS_DIR.mkdir(exist_ok=True)


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


# ============================================================
# SelfEvolutionLoop — 自进化闭环
# ============================================================

class SelfEvolutionLoop:
    """
    自进化闭环控制器。

    论文 6.3.2 节：接收涌现检测器的输出事件，将涌现事件转化为
    额外奖励信号反馈至 RL 调度器，实现「检测→反馈→优化」闭环。

    用法:
        evo = SelfEvolutionLoop(scheduler)
        evo.on_emergence(emergence_event)
        evo.get_evolution_trajectory()
    """

    REWARD_MAP = {
        "new_knowledge": 0.30,
        "new_strategy": 0.25,
        "new_connection": 0.20,
        "new_metaphor": 0.15,
    }

    def __init__(self, scheduler=None, log_path: str = ""):
        self._scheduler = scheduler
        self._evolution_log: List[Dict[str, Any]] = []
        self._total_emergence_reward = 0.0
        self._emergence_count = 0

        if not log_path:
            log_path = str(LOG_DIR / "evolution_log.json")
        self._log_path = log_path

        logger.info("[SelfEvolutionLoop] 自进化闭环已启用")

    def on_emergence(self, event) -> float:
        """接收涌现事件并转化为奖励信号"""
        category = getattr(event, 'category', None)
        if category is None:
            return 0.0

        cat_str = category.value if hasattr(category, 'value') else str(category)
        reward = self.REWARD_MAP.get(cat_str, 0.0)
        self._total_emergence_reward += reward
        self._emergence_count += 1

        entry = {
            "event_id": getattr(event, 'event_id', 'unknown'),
            "timestamp": getattr(event, 'timestamp', datetime.now().isoformat()),
            "category": cat_str,
            "emergence_value": getattr(event, 'emergence_value', 0.0),
            "reward": reward,
            "cumulative_reward": self._total_emergence_reward,
        }
        self._evolution_log.append(entry)

        if self._scheduler and hasattr(self._scheduler, 'inject_extra_reward'):
            self._scheduler.inject_extra_reward(reward)

        logger.info(
            f"[SelfEvolutionLoop] 涌现→奖励: {cat_str} → +{reward:.2f} "
            f"(累计: {self._total_emergence_reward:.2f})"
        )

        if len(self._evolution_log) % 10 == 0:
            self._persist()

        return reward

    def _persist(self):
        try:
            with open(self._log_path, "w", encoding="utf-8") as f:
                json.dump({
                    "total_events": self._emergence_count,
                    "total_reward": round(self._total_emergence_reward, 4),
                    "trajectory": self._evolution_log,
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[SelfEvolutionLoop] 持久化失败: {e}")

    def get_evolution_trajectory(self) -> Dict[str, Any]:
        self._persist()
        return {
            "total_events": self._emergence_count,
            "total_reward": round(self._total_emergence_reward, 4),
            "trajectory": self._evolution_log,
        }

    def get_stats(self) -> Dict[str, Any]:
        category_counts: Dict[str, int] = {}
        for entry in self._evolution_log:
            cat = entry.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_emergence_events": self._emergence_count,
            "total_emergence_reward": round(self._total_emergence_reward, 4),
            "by_category": category_counts,
            "recent_events": self._evolution_log[-10:] if self._evolution_log else [],
        }


# ============================================================
# RLOrchestratorV2 — 统一入口（支持 Q-Learning / DQN 双模式）
# ============================================================

class RLOrchestratorV2:
    """
    RL-Orchestrator V2 统一入口。

    整合 TaskDecomposer、CapabilityMatcher、调度器（QLearning/DQN）、
    ExecutionMonitor 四大组件，并提供 SelfEvolutionLoop 自进化能力。

    用法:
        orch = RLOrchestratorV2(scheduler_type="qlearning")
        result = orch.orchestrate(task_description)

        orch = RLOrchestratorV2(scheduler_type="dqn")
        orch.train_from_experience(state, action, reward, next_state, done)
    """

    def __init__(
        self,
        scheduler_type: str = "qlearning",
        agents: Optional[List[AgentCard]] = None,
        decomposition_depth: int = 3,
        state_dim: int = 20,
        action_dim: int = 8,
    ):
        self.scheduler_type = scheduler_type
        self.decomposer = TaskDecomposer(max_depth=decomposition_depth)
        self.matcher = CapabilityMatcher()
        self.monitor = ExecutionMonitor()

        agent_list = agents or create_default_agents()
        for agent in agent_list:
            self.matcher.register(agent)

        if scheduler_type == "dqn":
            self.scheduler = DQNScheduler(state_dim=state_dim, action_dim=action_dim)
        else:
            self.scheduler = RLScheduler()

        self.evolution = SelfEvolutionLoop(scheduler=self.scheduler)
        self._converged = False
        self._version = "v2"

        logger.info(
            f"[RLOrchestratorV2] 初始化: scheduler={scheduler_type}, "
            f"agents={len(agent_list)}, depth={decomposition_depth}"
        )

    def orchestrate(
        self,
        task_description: str,
        required_capabilities: Optional[List[str]] = None,
        priority: int = 3,
        max_concurrent: int = 5,
    ) -> Dict[str, Any]:
        """V2 编排入口"""
        dag = self.decomposer.decompose(
            task_description=task_description,
            required_capabilities=required_capabilities or ["basic"],
            priority=priority,
        )
        assignments = self.matcher.match_all(dag, max_concurrent=max_concurrent)

        queue = list(dag.subtasks.keys())
        queue_len = len(queue)

        state = f"pending_{min(queue_len, 10)}"
        if self.scheduler_type == "dqn":
            state_vector = self._state_to_vector(state)
            action = self.scheduler.select_action(state_vector)
            action_name = f"action_{action}"
        else:
            action, action_name = self.scheduler.decide(state, queue_len)
            action_name = f"action_{action} ({action_name})"

        for task_id, agent_id in assignments.items():
            self.matcher.assign(agent_id)
            self.monitor.record_start(task_id, agent_id)

        progress = {
            "total": len(dag.subtasks),
            "completed": 0,
            "running": len(assignments),
            "pending": len(dag.subtasks) - len(assignments),
            "failed": 0,
        }

        urgency = self._estimate_urgency_v2(dag)

        logger.info(
            f"[RLOrchestratorV2] 编排完成: {progress['completed']}/{progress['total']}, "
            f"action={action_name}, urgency={urgency:.3f}"
        )

        return {
            "orchestrator_version": self._version,
            "scheduler_type": self.scheduler_type,
            "task": {
                "root_id": dag.root_task_id,
                "subtasks": [
                    {"task_id": st.task_id, "name": st.name,
                     "assigned_agent": st.assigned_agent, "status": st.status.value}
                    for st in dag.subtasks.values()
                ],
            },
            "scheduling": {
                "state": state, "action": action_name,
                "queue_len": queue_len, "urgency": round(urgency, 3),
            },
            "progress": progress,
        }

    def _state_to_vector(self, state: str) -> List[float]:
        dim = self.scheduler.state_dim if hasattr(self.scheduler, 'state_dim') else 20
        vec = [0.0] * dim
        h = hash(state) % (dim - 1)
        vec[h] = 1.0
        vec[-1] = len(state) / 50.0
        return vec

    def _estimate_urgency_v2(self, dag: TaskDAG) -> float:
        total = len(dag.subtasks)
        if total == 0:
            return 0.0
        pending = sum(1 for t in dag.subtasks.values() if t.status == TaskStatus.PENDING)
        incomplete_ratio = pending / total
        max_priority = max((t.priority for t in dag.subtasks.values()), default=1)
        priority_urgency = max_priority / 5.0
        return min(1.0, max(0.0, 0.3 * incomplete_ratio + 0.3 * priority_urgency + 0.4 * 0.0))

    def on_emergence(self, event) -> float:
        return self.evolution.on_emergence(event)

    def train_from_experience(self, state, action, reward, next_state, done):
        if self.scheduler_type != "dqn":
            logger.warning("[RLOrchestratorV2] train_from_experience 仅 DQN 模式可用")
            return
        self.scheduler.store_experience(state, action, reward, next_state, done)
        loss = self.scheduler.train_step()
        if (self.scheduler._train_step_count % 100) == 0 and loss > 0:
            logger.info(
                f"[RLOrchestratorV2] train #{self.scheduler._train_step_count}, "
                f"loss={loss:.4f}, eps={self.scheduler.epsilon:.4f}"
            )

    def save(self):
        if self.scheduler_type == "dqn":
            self.scheduler.save()
        self.evolution._persist()
        logger.info("[RLOrchestratorV2] 状态已保存")

    def load(self, dqn_weights_path: str):
        if self.scheduler_type == "dqn":
            self.scheduler.load(dqn_weights_path)
        else:
            logger.warning("[RLOrchestratorV2] load 仅 DQN 模式可用")

    def get_stats(self) -> Dict[str, Any]:
        q_stats = self.scheduler.get_stats() if hasattr(self.scheduler, 'get_stats') else {}
        return {
            "version": self._version,
            "scheduler_type": self.scheduler_type,
            "scheduler": q_stats,
            "evolution": self.evolution.get_stats(),
            "agents_registered": len(self.matcher.agents),
        }

    def release_all(self):
        for agent_id in list(self.matcher.agents.keys()):
            self.matcher.release(agent_id)
