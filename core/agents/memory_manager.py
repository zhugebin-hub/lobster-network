#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.2 — 记忆模型三层架构 (MemAct 风格)

实现三层记忆体系 + DCPO 风格自适应记忆管理：

三层结构：
- TaskState Layer (任务状态层): 当前进度/子步骤/中间产物 → 断点续跑
- LongTermContext Layer (长期语境层): 用户偏好/组织约束/历史项目/权限边界 → 减少重复解释
- BehaviorTrajectory Layer (行为轨迹层): 决策过程/所选路径/成败经验 → 自我进化

核心方法：
- Context Curation: 动态决定哪些记忆注入当前 prompt
- DCPO 风格自适应: 基于记忆重要性和任务相关性做记忆压缩

参考：
- MemAct Framework — Context Curation + DCPO Algorithm
- 智能体网络最新进展综述_2025-2026 — 6.3 记忆模型三层结构
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict

logger = logging.getLogger("memory_manager")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举与数据模型
# ============================================================

class MemoryLayer(str, Enum):
    TASK_STATE = "task_state"
    LONG_TERM_CONTEXT = "long_term_context"
    BEHAVIOR_TRAJECTORY = "behavior_trajectory"


class MemoryImportance(str, Enum):
    CRITICAL = "critical"     # 不可遗忘
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    TRANSIENT = "transient"   # 短期有用，可丢弃


@dataclass
class MemoryEntry:
    """通用记忆条目"""
    memory_id: str
    layer: MemoryLayer
    content: Dict[str, Any]
    importance: MemoryImportance = MemoryImportance.MEDIUM
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    ttl_sec: Optional[int] = None          # 过期时间（秒）
    embedding: Optional[List[float]] = None  # 向量嵌入（预留）
    metadata: Dict[str, Any] = field(default_factory=dict)

    def touch(self):
        self.last_accessed = datetime.now().isoformat()
        self.access_count += 1

    def is_expired(self) -> bool:
        if self.ttl_sec is None:
            return False
        try:
            created = datetime.fromisoformat(self.created_at)
            return (datetime.now() - created).total_seconds() > self.ttl_sec
        except (ValueError, TypeError):
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "layer": self.layer.value,
            "content": self.content,
            "importance": self.importance.value,
            "tags": self.tags,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "ttl_sec": self.ttl_sec,
            "metadata": self.metadata,
        }


# ============================================================
# TaskState Layer — 任务状态层
# ============================================================

class TaskStateLayer:
    """
    任务状态层：追踪当前任务的进度、子步骤和中间产物。

    核心能力：
    - 任务状态快照保存与恢复
    - 子步骤 DAG 追踪
    - 中间产物索引
    - 断点续跑支持
    """

    def __init__(self, max_entries: int = 1000):
        self._tasks: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._artifacts_index: Dict[str, List[str]] = {}  # task_id → artifact paths
        self._max_entries = max_entries
        self._checkpoint_dir: Optional[Path] = None

    def create_task(self, task_id: str, description: str,
                    subtasks: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """创建新任务状态"""
        state = {
            "task_id": task_id,
            "description": description,
            "status": "created",
            "progress_pct": 0.0,
            "current_step": None,
            "subtasks": subtasks or [],
            "completed_steps": [],
            "failed_steps": [],
            "artifacts": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._tasks[task_id] = state
        self._artifacts_index[task_id] = []
        logger.debug(f"[TaskState] 任务已创建: {task_id}")
        return state

    def update_progress(self, task_id: str, step: str,
                        result: Dict[str, Any] = None, success: bool = True) -> Dict[str, Any]:
        """更新任务进度"""
        task = self._tasks.get(task_id)
        if not task:
            raise KeyError(f"Task '{task_id}' not found")

        if success:
            task["completed_steps"].append({"step": step, "result": result, "time": datetime.now().isoformat()})
        else:
            task["failed_steps"].append({"step": step, "error": result, "time": datetime.now().isoformat()})

        task["current_step"] = step
        total = len(task["subtasks"]) + 1
        done = len(task["completed_steps"])
        task["progress_pct"] = min(100.0, (done / max(total, 1)) * 100)
        task["updated_at"] = datetime.now().isoformat()
        task["status"] = "running"

        return task

    def complete_task(self, task_id: str) -> Dict[str, Any]:
        """标记任务完成"""
        task = self._tasks.get(task_id)
        if task:
            task["status"] = "completed"
            task["progress_pct"] = 100.0
            task["updated_at"] = datetime.now().isoformat()
        return task

    def fail_task(self, task_id: str, error: str) -> Dict[str, Any]:
        """标记任务失败"""
        task = self._tasks.get(task_id)
        if task:
            task["status"] = "failed"
            task["error"] = error
            task["updated_at"] = datetime.now().isoformat()
        return task

    def register_artifact(self, task_id: str, artifact_path: str, artifact_type: str = "file"):
        """注册中间产物"""
        if task_id in self._artifacts_index:
            self._artifacts_index[task_id].append(artifact_path)
        if task_id in self._tasks:
            self._tasks[task_id].setdefault("artifacts", []).append({
                "path": artifact_path, "type": artifact_type,
                "timestamp": datetime.now().isoformat()
            })

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self._tasks.get(task_id)

    def get_artifacts(self, task_id: str) -> List[str]:
        return self._artifacts_index.get(task_id, [])

    def save_checkpoint(self, task_id: str) -> Optional[Path]:
        """保存任务断点"""
        if self._checkpoint_dir is None:
            return None
        task = self._tasks.get(task_id)
        if not task:
            return None
        cp_path = self._checkpoint_dir / f"{task_id}_checkpoint.json"
        cp_path.write_text(json.dumps(task, ensure_ascii=False, indent=2))
        return cp_path

    def restore_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """恢复任务断点"""
        if self._checkpoint_dir is None:
            return None
        cp_path = self._checkpoint_dir / f"{task_id}_checkpoint.json"
        if cp_path.exists():
            data = json.loads(cp_path.read_text(encoding="utf-8"))
            self._tasks[task_id] = data
            return data
        return None

    def set_checkpoint_dir(self, path: Path):
        self._checkpoint_dir = path
        path.mkdir(parents=True, exist_ok=True)

    def list_active_tasks(self) -> List[Dict[str, Any]]:
        return [
            t for t in self._tasks.values()
            if t["status"] in ("created", "running", "paused")
        ]

    def to_summary(self) -> Dict[str, Any]:
        return {
            "total_tasks": len(self._tasks),
            "active_tasks": len(self.list_active_tasks()),
            "completed_tasks": sum(1 for t in self._tasks.values() if t["status"] == "completed"),
        }


# ============================================================
# LongTermContext Layer — 长期语境层
# ============================================================

class LongTermContextLayer:
    """
    长期语境层：存储用户偏好、组织约束、历史项目和权限边界。

    核心能力：
    - 用户偏好学习与更新
    - 组织约束规则管理
    - 历史项目索引
    - 权限边界检查
    """

    def __init__(self):
        self._user_preferences: Dict[str, Any] = {}
        self._organization_constraints: List[Dict[str, Any]] = []
        self._history_projects: List[Dict[str, Any]] = []
        self._permission_boundaries: Dict[str, Any] = {}
        self._skills_inventory: Dict[str, int] = {}  # skill_id → usage_count

    # ── 用户偏好 ──

    def set_preference(self, key: str, value: Any):
        self._user_preferences[key] = {
            "value": value,
            "updated_at": datetime.now().isoformat(),
        }

    def get_preference(self, key: str, default: Any = None) -> Any:
        entry = self._user_preferences.get(key)
        return entry["value"] if entry else default

    def get_all_preferences(self) -> Dict[str, Any]:
        return {k: v["value"] for k, v in self._user_preferences.items()}

    # ── 组织约束 ──

    def add_constraint(self, constraint: Dict[str, Any]):
        """添加组织约束（如安全策略、合规要求）"""
        constraint["added_at"] = datetime.now().isoformat()
        self._organization_constraints.append(constraint)

    def get_constraints(self, category: str = None) -> List[Dict[str, Any]]:
        if category:
            return [c for c in self._organization_constraints if c.get("category") == category]
        return self._organization_constraints

    def check_constraint(self, action: str) -> Tuple[bool, Optional[str]]:
        """检查行为是否符合组织约束，返回 (允许, 拒绝理由)"""
        for c in self._organization_constraints:
            if c.get("action") == action and c.get("blocked", False):
                return False, c.get("reason", "组织策略禁止此操作")
        return True, None

    # ── 历史项目 ──

    def record_project(self, project: Dict[str, Any]):
        """记录已完成项目"""
        project["recorded_at"] = datetime.now().isoformat()
        self._history_projects.append(project)
        # 保留最近 200 个
        if len(self._history_projects) > 200:
            self._history_projects = self._history_projects[-200:]

    def find_similar_projects(self, keywords: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """基于关键词检索相似历史项目"""
        scored = []
        for proj in self._history_projects:
            desc = proj.get("description", "") + " ".join(proj.get("tags", []))
            score = sum(1 for kw in keywords if kw.lower() in desc.lower())
            if score > 0:
                scored.append((score, proj))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:top_k]]

    # ── 权限边界 ──

    def set_permission(self, resource: str, level: str, allowed_roles: List[str] = None):
        """
        设定权限边界。
        level: "public" / "restricted" / "private" / "admin_only"
        """
        self._permission_boundaries[resource] = {
            "level": level,
            "allowed_roles": allowed_roles or [],
            "set_at": datetime.now().isoformat(),
        }

    def check_permission(self, resource: str, role: str) -> bool:
        perm = self._permission_boundaries.get(resource)
        if not perm:
            return True  # 默认允许
        if perm["level"] == "public":
            return True
        return role in perm["allowed_roles"]

    # ── 技能清单 ──

    def increment_skill_usage(self, skill_id: str):
        self._skills_inventory[skill_id] = self._skills_inventory.get(skill_id, 0) + 1

    def get_top_skills(self, top_k: int = 10) -> List[Tuple[str, int]]:
        return sorted(self._skills_inventory.items(), key=lambda x: x[1], reverse=True)[:top_k]

    def to_summary(self) -> Dict[str, Any]:
        return {
            "preferences_count": len(self._user_preferences),
            "constraints_count": len(self._organization_constraints),
            "history_projects": len(self._history_projects),
            "permissions_count": len(self._permission_boundaries),
            "top_skills": self.get_top_skills(5),
        }


# ============================================================
# BehaviorTrajectory Layer — 行为轨迹层
# ============================================================

class BehaviorTrajectoryLayer:
    """
    行为轨迹层：记录决策过程、所选路径和成败经验。

    核心能力：
    - 决策路径追踪
    - 成功/失败模式挖掘
    - 经验回放提取
    - 自我进化反馈
    """

    def __init__(self, max_trajectories: int = 500):
        self._trajectories: List[Dict[str, Any]] = []
        self._success_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self._failure_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self._max_trajectories = max_trajectories

    def record_decision(self, context: Dict[str, Any], decision_path: List[str],
                        outcome: str, metrics: Dict[str, Any] = None):
        """
        记录一次完整决策轨迹。

        参数:
            context: 决策上下文（任务描述/目标/约束）
            decision_path: 决策步骤序列 ["step1", "step2", ...]
            outcome: 结果 "success" / "partial_success" / "failure"
            metrics: 量化指标 { "time_ms": 1200, "cost_lbc": 2.5, ... }
        """
        trajectory = {
            "trajectory_id": f"traj_{len(self._trajectories)}_{int(time.time())}",
            "context": context,
            "decision_path": decision_path,
            "outcome": outcome,
            "metrics": metrics or {},
            "recorded_at": datetime.now().isoformat(),
            "steps_count": len(decision_path),
        }
        self._trajectories.append(trajectory)

        # 挖掘模式
        self._extract_patterns(trajectory)

        # FIFO 淘汰
        if len(self._trajectories) > self._max_trajectories:
            self._trajectories = self._trajectories[-self._max_trajectories:]

    def _extract_patterns(self, trajectory: Dict[str, Any]):
        """从轨迹中提取成功/失败模式"""
        path_signature = " → ".join(trajectory["decision_path"])
        outcome = trajectory["outcome"]

        if outcome == "success":
            self._success_patterns.setdefault(path_signature, []).append({
                "trajectory_id": trajectory["trajectory_id"],
                "metrics": trajectory["metrics"],
                "context": {"task_type": trajectory["context"].get("task_type", "unknown")},
            })
        elif outcome == "failure":
            self._failure_patterns.setdefault(path_signature, []).append({
                "trajectory_id": trajectory["trajectory_id"],
                "metrics": trajectory["metrics"],
                "error": trajectory["context"].get("error", "unknown"),
            })

    def query_success_patterns(self, task_type: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """查询与任务类型匹配的成功模式"""
        scored = []
        for path, records in self._success_patterns.items():
            relevant = records if not task_type else [
                r for r in records if r.get("context", {}).get("task_type") == task_type
            ]
            if relevant:
                avg_time = sum(r["metrics"].get("time_ms", 0) for r in relevant) / max(len(relevant), 1)
                scored.append({
                    "path": path,
                    "frequency": len(relevant),
                    "avg_time_ms": avg_time,
                    "records": relevant[:3],
                })
        scored.sort(key=lambda x: x["frequency"], reverse=True)
        return scored[:top_k]

    def query_failure_patterns(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """查询高频失败模式"""
        scored = []
        for path, records in self._failure_patterns.items():
            scored.append({
                "path": path,
                "frequency": len(records),
                "common_errors": list(set(r.get("error", "unknown") for r in records)),
            })
        scored.sort(key=lambda x: x["frequency"], reverse=True)
        return scored[:top_k]

    def get_recent_trajectories(self, n: int = 20) -> List[Dict[str, Any]]:
        return self._trajectories[-n:]

    def get_success_rate(self, task_type: str = None) -> float:
        """计算成功率"""
        relevant = self._trajectories
        if task_type:
            relevant = [t for t in relevant if t.get("context", {}).get("task_type") == task_type]
        if not relevant:
            return 0.0
        successes = sum(1 for t in relevant if t["outcome"] == "success")
        return successes / len(relevant)

    def to_summary(self) -> Dict[str, Any]:
        return {
            "total_trajectories": len(self._trajectories),
            "success_patterns_count": len(self._success_patterns),
            "failure_patterns_count": len(self._failure_patterns),
            "overall_success_rate": self.get_success_rate(),
            "recent_10_success_rate": self.get_success_rate(),
        }


# ============================================================
# Context Curation — 上下文策展
# ============================================================

class ContextCurationEngine:
    """
    上下文策展引擎 — DCPO 风格自适应记忆管理。

    核心算法：
    1. 接收当前任务上下文
    2. 从三层记忆中检索相关记忆条目
    3. 按重要性 + 相关性 + 新鲜度评分
    4. 在 token 预算约束下选择最优子集注入 context
    """

    def __init__(self, task_state: TaskStateLayer,
                 long_term: LongTermContextLayer,
                 behavior: BehaviorTrajectoryLayer,
                 max_tokens: int = 4096):
        self.task_state = task_state
        self.long_term = long_term
        self.behavior = behavior
        self.max_tokens = max_tokens
        # DCPO 评分权重
        self.weights = {
            "importance": 0.45,
            "relevance": 0.35,
            "freshness": 0.10,
            "frequency": 0.10,
        }

    def curate(self, task_context: Dict[str, Any],
               token_budget: int = None) -> Dict[str, Any]:
        """
        策展：动态选择该注入当前 prompt 的记忆。

        返回：
        {
          "selected_memories": [...],       # 按优先级排序
          "budget_used_pct": 0.X,           # Token预算使用率
          "layers_covered": [...]            # 覆盖的层级
        }
        """
        budget = token_budget or self.max_tokens
        keywords = task_context.get("keywords", [])
        task_type = task_context.get("task_type", "general")

        # 1. 从各层检索候选记忆
        candidates: List[Tuple[float, Dict[str, Any]]] = []

        # TaskState: 当前活跃任务
        active_tasks = self.task_state.list_active_tasks()
        for task in active_tasks:
            score = self._score_entry(
                importance=MemoryImportance.CRITICAL,
                relevance=self._keyword_match(task.get("description", ""), keywords),
                created_at=task.get("created_at", ""),
                access_count=1,
            )
            candidates.append((score, {"layer": "task_state", "type": "active_task", "data": task}))

        # LongTermContext: 用户偏好 + 相似历史项目
        prefs = self.long_term.get_all_preferences()
        if prefs:
            score = self._score_entry(MemoryImportance.HIGH, 0.5, "", 1)
            candidates.append((score, {"layer": "long_term_context", "type": "preferences", "data": prefs}))

        similar_projects = self.long_term.find_similar_projects(keywords, top_k=3)
        for proj in similar_projects:
            score = self._score_entry(MemoryImportance.MEDIUM, 0.8,
                                      proj.get("recorded_at", ""), 1)
            candidates.append((score, {"layer": "long_term_context", "type": "similar_project", "data": proj}))

        # 组织约束
        constraints = self.long_term.get_constraints()
        for c in constraints:
            score = self._score_entry(MemoryImportance.HIGH, 0.3, c.get("added_at", ""), 1)
            candidates.append((score, {"layer": "long_term_context", "type": "constraint", "data": c}))

        # BehaviorTrajectory: 成功模式
        success_patterns = self.behavior.query_success_patterns(task_type, top_k=3)
        for pat in success_patterns:
            score = self._score_entry(MemoryImportance.HIGH, 0.9, "", pat["frequency"])
            candidates.append((score, {"layer": "behavior_trajectory", "type": "success_pattern", "data": pat}))

        # 2. 按评分排序
        candidates.sort(key=lambda x: x[0], reverse=True)

        # 3. Token预算裁剪
        selected = []
        budget_used = 0
        for score, entry in candidates:
            token_est = self._estimate_tokens(entry)
            if budget_used + token_est > budget:
                continue
            selected.append({"score": round(score, 3), **entry})
            budget_used += token_est

        return {
            "selected_memories": selected,
            "budget_used_pct": round(budget_used / budget, 3),
            "layers_covered": list(set(e["layer"] for e in selected)),
            "total_candidates": len(candidates),
        }

    def _score_entry(self, importance: MemoryImportance,
                     relevance: float, created_at: str,
                     access_count: int) -> float:
        """DCPO 风格评分"""
        imp_score = {
            MemoryImportance.CRITICAL: 1.0,
            MemoryImportance.HIGH: 0.8,
            MemoryImportance.MEDIUM: 0.5,
            MemoryImportance.LOW: 0.3,
            MemoryImportance.TRANSIENT: 0.1,
        }.get(importance, 0.5)

        freshness = 1.0
        if created_at:
            try:
                age_hours = (datetime.now() - datetime.fromisoformat(created_at)).total_seconds() / 3600
                freshness = max(0.1, 1.0 - age_hours / (24 * 7))  # 一周衰减
            except (ValueError, TypeError):
                pass

        freq_score = min(1.0, access_count / 20.0)

        return (
            self.weights["importance"] * imp_score +
            self.weights["relevance"] * relevance +
            self.weights["freshness"] * freshness +
            self.weights["frequency"] * freq_score
        )

    @staticmethod
    def _keyword_match(text: str, keywords: List[str]) -> float:
        if not keywords:
            return 0.5
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw.lower() in text_lower)
        return min(1.0, matches / max(len(keywords), 1))

    @staticmethod
    def _estimate_tokens(entry: Dict[str, Any]) -> int:
        """粗略估算 token 数（约 4 字符 = 1 token）"""
        data_str = json.dumps(entry.get("data", {}), ensure_ascii=False)
        return max(1, len(data_str) // 4)


# ============================================================
# MemoryManager — 顶层协调器
# ============================================================

class MemoryManager:
    """
    记忆管理器 — 三层架构统一入口。

    整合 TaskState / LongTermContext / BehaviorTrajectory 三层记忆，
    通过 ContextCuration 动态策展当前上下文。
    """

    def __init__(self, checkpoint_dir: Optional[Path] = None,
                 max_tokens: int = 4096):
        self.task_state = TaskStateLayer()
        self.long_term = LongTermContextLayer()
        self.behavior = BehaviorTrajectoryLayer()
        self.curation = ContextCurationEngine(
            self.task_state, self.long_term, self.behavior,
            max_tokens=max_tokens,
        )

        if checkpoint_dir:
            self.task_state.set_checkpoint_dir(checkpoint_dir)

        logger.info(f"[MemoryManager] 记忆管理器已初始化，三层架构就绪")

    def curate_for_task(self, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """为当前任务策展上下文"""
        return self.curation.curate(task_context)

    def record_success(self, task_context: Dict[str, Any],
                       decision_path: List[str], metrics: Dict[str, Any] = None):
        """记录成功经验"""
        self.behavior.record_decision(task_context, decision_path, "success", metrics)

    def record_failure(self, task_context: Dict[str, Any],
                       decision_path: List[str], error: str):
        """记录失败经验"""
        ctx = {**task_context, "error": error}
        self.behavior.record_decision(ctx, decision_path, "failure")

    def get_status(self) -> Dict[str, Any]:
        return {
            "task_state": self.task_state.to_summary(),
            "long_term_context": self.long_term.to_summary(),
            "behavior_trajectory": self.behavior.to_summary(),
        }

    def get_insights(self) -> Dict[str, Any]:
        """获取可操作的洞察"""
        return {
            "success_patterns": self.behavior.query_success_patterns(top_k=5),
            "failure_patterns": self.behavior.query_failure_patterns(top_k=5),
            "top_skills": self.long_term.get_top_skills(5),
            "active_tasks": len(self.task_state.list_active_tasks()),
            "overall_success_rate": self.behavior.get_success_rate(),
        }
