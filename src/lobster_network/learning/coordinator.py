"""
学习协调器 - Learning Coordinator

Closes the loop between assessment and training:
1. Run 8-dimension assessment on training records after each round
2. Compare with previous assessment to measure progress
3. Generate adaptive training plans based on weak dimensions
4. Track cumulative learning state across rounds
5. Suggest cross-node collaborations based on complementary strengths

Usage:
    coordinator = LearningCoordinator()

    # Run a training round
    result = coordinator.run_training_round(
        node_id="xiaochen",
        domain="go",
        training_records=[{"task_completion": 0.8, "output_quality": 0.7, ...}],
    )
    print(result.progress_report.trend)
    print(result.next_plan.suggested_tasks)

    # Inspect cumulative state
    state = coordinator.get_learning_state("xiaochen")
    print(state.growth_trajectory)
"""

# from __future__ import annotations  # Python 3.6 不支持

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Optional

from ..assessment.dimensions import (
    DimensionProfile,
    DIMENSION_REGISTRY,
    DIMENSION_DESCRIPTIONS,
    DIMENSION_WEIGHTS,
)
from ..assessment.eight_dim_engine import EightDimEngine, AssessmentResult


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TrainingPlan:
    """Adaptive training plan generated from an assessment profile.

    Attributes:
        node_id: Target node.
        domain: Training domain (e.g. "go", "ppt", "poster").
        focus_dimensions: Dimension keys that need improvement, ordered
            weakest-first.
        difficulty: Overall difficulty level for the plan
            ("easy", "medium", or "hard").
        suggested_tasks: Human-readable task descriptions for the node to
            work on in the next training round.
    """

    node_id: str
    domain: str
    focus_dimensions: List[str] = field(default_factory=list)
    difficulty: str = "medium"
    suggested_tasks: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "domain": self.domain,
            "focus_dimensions": self.focus_dimensions,
            "difficulty": self.difficulty,
            "suggested_tasks": self.suggested_tasks,
        }


@dataclass
class ProgressReport:
    """Per-dimension improvement delta between two consecutive assessments.

    Attributes:
        node_id: Target node.
        dimension_deltas: Mapping of dimension key to score change
            (positive = improved, negative = declined).
        overall_improvement: Mean delta across all dimensions.
        trend: "improving" | "stable" | "declining".
    """

    node_id: str
    dimension_deltas: Dict[str, float] = field(default_factory=dict)
    overall_improvement: float = 0.0
    trend: str = "stable"

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "dimension_deltas": {k: round(v, 4) for k, v in self.dimension_deltas.items()},
            "overall_improvement": round(self.overall_improvement, 4),
            "trend": self.trend,
        }


@dataclass
class TrainingRoundResult:
    """Complete result of a single training round.

    Attributes:
        node_id: Target node.
        domain: Training domain.
        round_number: 1-based sequential round counter for this node+domain.
        assessment_result: The raw ``AssessmentResult`` from the engine.
        next_plan: Adaptive plan for the *next* round.
        progress_report: Delta compared to the previous round (empty deltas
            for the very first round).
    """

    node_id: str
    domain: str
    round_number: int
    assessment_result: AssessmentResult
    next_plan: TrainingPlan
    progress_report: ProgressReport

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "domain": self.domain,
            "round_number": self.round_number,
            "assessment_result": self.assessment_result.to_dict(),
            "next_plan": self.next_plan.to_dict(),
            "progress_report": self.progress_report.to_dict(),
        }


@dataclass
class LearningState:
    """Cumulative learning state for a node across all rounds.

    Attributes:
        node_id: Target node.
        total_rounds: Number of completed rounds (all domains combined).
        best_scores: Best score achieved per dimension across all rounds.
        growth_trajectory: List of weighted-total scores in chronological
            order (one entry per round).
        current_plan: Most recently generated ``TrainingPlan``.
    """

    node_id: str
    total_rounds: int = 0
    best_scores: Dict[str, float] = field(default_factory=dict)
    growth_trajectory: List[float] = field(default_factory=list)
    current_plan: Optional[TrainingPlan] = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "total_rounds": self.total_rounds,
            "best_scores": {k: round(v, 4) for k, v in self.best_scores.items()},
            "growth_trajectory": [round(s, 4) for s in self.growth_trajectory],
            "current_plan": self.current_plan.to_dict() if self.current_plan else None,
        }


@dataclass
class CollaborationSuggestion:
    """Recommendation that two nodes should collaborate.

    Attributes:
        node_a_id: First node.
        node_b_id: Second node.
        reason: Human-readable explanation of why this pairing is useful.
        expected_benefit_score: Estimated benefit in [0, 1]; higher means
            stronger complementarity.
    """

    node_a_id: str
    node_b_id: str
    reason: str
    expected_benefit_score: float

    def to_dict(self) -> dict:
        return {
            "node_a_id": self.node_a_id,
            "node_b_id": self.node_b_id,
            "reason": self.reason,
            "expected_benefit_score": round(self.expected_benefit_score, 4),
        }


# ---------------------------------------------------------------------------
# Task-template helpers (private)
# ---------------------------------------------------------------------------

_TASK_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "understanding": {
        "intensive": [
            "完成3道需求分析专项练习：先列出所有约束条件再动手",
            "拆解一个复杂任务为5个以上子任务，逐一验证理解是否完整",
        ],
        "varied": [
            "混合练习：交替进行需求分析和任务拆解",
            "尝试对同一任务写出3种不同理解，选择最合理的一种",
        ],
        "maintenance": [
            "每次任务开始前花1分钟确认关键约束",
        ],
    },
    "execution": {
        "intensive": [
            "限时编码练习：在30分钟内从零构建一个完整小项目",
            "完成一份完整技术文档，包含架构图和代码示例",
        ],
        "varied": [
            "交替进行编码和文档撰写练习",
            "尝试用不同语言/框架实现同一功能",
        ],
        "maintenance": [
            "保持每周至少一次完整项目输出",
        ],
    },
    "retrieval": {
        "intensive": [
            "多源交叉检索练习：对同一问题从3个信息源验证答案",
            "构建并维护结构化知识库，每天新增5条索引条目",
        ],
        "varied": [
            "混合检索练习：交替使用关键词搜索和语义搜索",
            "对已有知识库进行重新分类和标签整理",
        ],
        "maintenance": [
            "定期回顾知识库，删除过时条目",
        ],
    },
    "reasoning": {
        "intensive": [
            "每天完成5道多步推理题（围棋死活题、数学证明等）",
            "练习反事实推理：对已解决的问题改变一个条件重新推导",
        ],
        "varied": [
            "交替进行逻辑推理和因果分析练习",
            "尝试用归纳法和演绎法分别解决同一问题",
        ],
        "maintenance": [
            "每周完成一组推理练习保持手感",
        ],
    },
    "reflection": {
        "intensive": [
            "每次任务后写完整反思日志：做对了什么、哪里可以改进、下次策略",
            "回顾过去一周的所有工作，识别重复出现的错误模式并制定对策",
        ],
        "varied": [
            "交替进行自我评估和同伴互评",
            "对过去的反思日志进行二次反思，看是否有遗漏的改进点",
        ],
        "maintenance": [
            "保持每周写一次简要反思日志",
        ],
    },
    "tooling": {
        "intensive": [
            "探索3个新工具或API，各写一份最佳使用场景笔记",
            "练习工具组合使用：将多个工具串联完成一个复杂任务",
        ],
        "varied": [
            "交替使用不同工具完成同类任务，比较效率差异",
            "为一个常用工具编写使用指南",
        ],
        "maintenance": [
            "每月试用一个新工具并记录心得",
        ],
    },
    "eq": {
        "intensive": [
            "练习识别对话中的隐含意图：对10段对话标注情绪信号",
            "完成3个多人协作场景模拟练习，关注角色协调",
        ],
        "varied": [
            "交替进行共情练习和冲突调解练习",
            "对不同风格的对话样本进行回应练习",
        ],
        "maintenance": [
            "在日常对话中有意识地关注情绪信号",
        ],
    },
    "memory": {
        "intensive": [
            "信息压缩练习：将一篇长文提炼为5个关键要点",
            "构建跨会话记忆体系，建立索引并每天复习",
        ],
        "varied": [
            "交替进行短期记忆和长期记忆练习",
            "对已有记忆条目进行关联和重组",
        ],
        "maintenance": [
            "定期回顾和更新记忆体系",
        ],
    },
}

# Score-range thresholds used by the adaptive plan generator.
_LOW_THRESHOLD = 0.3
_MID_THRESHOLD = 0.6
_DIFFICULTY_LOW = 0.4
_DIFFICULTY_HIGH = 0.7

# Trend thresholds for ``measure_progress``.
_IMPROVING_THRESHOLD = 0.05
_DECLINING_THRESHOLD = -0.05


def _difficulty_band(score: float) -> str:
    """Map a dimension score to a difficulty label."""
    if score < _DIFFICULTY_LOW:
        return "easy"
    if score < _DIFFICULTY_HIGH:
        return "medium"
    return "hard"


def _intensity_key(score: float) -> str:
    """Map a dimension score to a task-intensity key."""
    if score < _LOW_THRESHOLD:
        return "intensive"
    if score < _MID_THRESHOLD:
        return "varied"
    return "maintenance"


# ---------------------------------------------------------------------------
# LearningCoordinator
# ---------------------------------------------------------------------------

class LearningCoordinator:
    """Closes the loop between assessment and training.

    After each training round:
    1. Run 8-dimension assessment on training records
    2. Compare with previous assessment to measure progress
    3. Generate adaptive training plan based on weak dimensions
    4. Track cumulative learning state

    All persistent state is delegated to the underlying
    :class:`EightDimEngine`; in-memory caches are maintained for fast
    look-ups of learning state and round counters.

    Args:
        data_dir: Optional root directory for assessment persistence.
            When *None* the engine default is used.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self._engine = EightDimEngine(data_dir=data_dir)
        self._data_dir = Path(data_dir) if data_dir else self._engine.data_dir

        # In-memory caches keyed by node_id.
        self._states: Dict[str, LearningState] = {}
        # Round counters keyed by (node_id, domain).
        self._round_counters: Dict[tuple, int] = {}

        # Restore round counters from persisted history when possible.
        self._bootstrap_counters()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_training_round(
        self,
        node_id: str,
        domain: str,
        training_records: List[dict],
    ) -> TrainingRoundResult:
        """Run one full assessment-training cycle.

        1. Assess the node from *training_records*.
        2. Compare with the immediately previous assessment (if any).
        3. Generate an adaptive plan for the next round.
        4. Update the cumulative :class:`LearningState`.

        Args:
            node_id: The node being trained.
            domain: Training domain (e.g. ``"go"``, ``"ppt"``).
            training_records: List of record dicts whose keys are
                recognised by :class:`DimensionScorer`.

        Returns:
            A :class:`TrainingRoundResult` bundling the assessment,
            progress report, and next plan.
        """
        counter_key = (node_id, domain)
        self._round_counters[counter_key] = self._round_counters.get(counter_key, 0) + 1
        round_number = self._round_counters[counter_key]

        # 1. Assess
        assessment = self._engine.assess_from_records(node_id, domain, training_records)
        current_profile = assessment.profile

        # 2. Measure progress against previous assessment
        history = self._engine.load_history(node_id)
        previous_profile: Optional[DimensionProfile] = None
        # The just-saved result is the last entry; the one before it is
        # the previous round.
        if len(history) >= 2:
            prev_entry = history[-2]
            previous_profile = prev_entry.profile

        progress = self.measure_progress(node_id, current_profile, previous_profile)

        # 3. Generate adaptive plan
        plan = self.generate_adaptive_plan(node_id, current_profile, history)

        # 4. Update learning state
        state = self._ensure_state(node_id)
        state.total_rounds += 1
        state.growth_trajectory.append(current_profile.weighted_total)
        for dim, score in current_profile.scores.items():
            if score > state.best_scores.get(dim, 0.0):
                state.best_scores[dim] = score
        state.current_plan = plan

        return TrainingRoundResult(
            node_id=node_id,
            domain=domain,
            round_number=round_number,
            assessment_result=assessment,
            next_plan=plan,
            progress_report=progress,
        )

    def generate_adaptive_plan(
        self,
        node_id: str,
        profile: DimensionProfile,
        history: Optional[List[AssessmentResult]] = None,
    ) -> TrainingPlan:
        """Create a training plan that targets the weakest dimensions.

        The plan always focuses on the **bottom 3** dimensions.  For each
        focused dimension the task intensity is chosen based on the
        current score:

        * score < 0.3 -- intensive practice, difficulty *easy*
        * 0.3 <= score < 0.6 -- varied practice, difficulty *medium*
        * score >= 0.6 -- maintenance tasks, difficulty *hard*

        Args:
            node_id: Target node.
            profile: The most recent :class:`DimensionProfile`.
            history: Optional historical assessments (reserved for
                future trend-aware logic).

        Returns:
            A :class:`TrainingPlan`.
        """
        # Bottom 3 dimensions (weakest first).
        sorted_dims = sorted(profile.scores.items(), key=lambda kv: kv[1])
        focus_dims = [dim for dim, _ in sorted_dims[:3]]

        tasks: List[str] = []
        difficulties: List[str] = []

        for dim in focus_dims:
            score = profile.scores.get(dim, 0.0)
            intensity = _intensity_key(score)
            dim_name = DIMENSION_DESCRIPTIONS.get(dim, {}).get("name_zh", dim)

            templates = _TASK_TEMPLATES.get(dim, {})
            chosen = templates.get(intensity, [])
            for t in chosen:
                tasks.append(f"[{dim_name}] {t}")

            difficulties.append(_difficulty_band(score))

        # Overall plan difficulty is the *easiest* band among focused dims
        # so that the node is not overwhelmed.
        if not difficulties:
            overall_difficulty = "medium"
        elif "easy" in difficulties:
            overall_difficulty = "easy"
        elif "medium" in difficulties:
            overall_difficulty = "medium"
        else:
            overall_difficulty = "hard"

        return TrainingPlan(
            node_id=node_id,
            domain=profile.domain,
            focus_dimensions=focus_dims,
            difficulty=overall_difficulty,
            suggested_tasks=tasks,
        )

    def measure_progress(
        self,
        node_id: str,
        current_profile: DimensionProfile,
        previous_profile: Optional[DimensionProfile],
    ) -> ProgressReport:
        """Compute per-dimension score deltas between two assessments.

        Args:
            node_id: Target node.
            current_profile: Latest assessment profile.
            previous_profile: Profile from the round immediately before,
                or *None* if this is the first round.

        Returns:
            A :class:`ProgressReport`.  When *previous_profile* is
            ``None`` all deltas are ``0.0`` and the trend is ``"stable"``.
        """
        if previous_profile is None:
            return ProgressReport(
                node_id=node_id,
                dimension_deltas={dim: 0.0 for dim in DIMENSION_REGISTRY},
                overall_improvement=0.0,
                trend="stable",
            )

        deltas: Dict[str, float] = {}
        for dim in DIMENSION_REGISTRY:
            cur = current_profile.scores.get(dim, 0.0)
            prev = previous_profile.scores.get(dim, 0.0)
            deltas[dim] = cur - prev

        overall = sum(deltas.values()) / max(len(deltas), 1)

        if overall > _IMPROVING_THRESHOLD:
            trend = "improving"
        elif overall < _DECLINING_THRESHOLD:
            trend = "declining"
        else:
            trend = "stable"

        return ProgressReport(
            node_id=node_id,
            dimension_deltas=deltas,
            overall_improvement=overall,
            trend=trend,
        )

    def get_learning_state(self, node_id: str) -> LearningState:
        """Return the cumulative learning state for *node_id*.

        If no rounds have been recorded yet an empty state is returned.
        """
        return self._ensure_state(node_id)

    def suggest_collaboration(
        self,
        profiles: Dict[str, DimensionProfile],
    ) -> List[CollaborationSuggestion]:
        """Suggest node pairs with complementary strengths.

        For every pair of nodes, a *benefit score* is computed as the sum
        of absolute per-dimension score differences where one node
        exceeds the ``0.6`` strength threshold and the other falls below
        the ``0.4`` weakness threshold.  Only pairs with a positive
        benefit are returned, sorted highest-first.

        Args:
            profiles: Mapping of ``node_id`` to
                :class:`DimensionProfile`.

        Returns:
            A list of :class:`CollaborationSuggestion`, possibly empty.
        """
        suggestions: List[CollaborationSuggestion] = []

        for (id_a, prof_a), (id_b, prof_b) in combinations(profiles.items(), 2):
            benefit = 0.0
            complementary_dims: List[str] = []

            for dim in DIMENSION_REGISTRY:
                sa = prof_a.scores.get(dim, 0.0)
                sb = prof_b.scores.get(dim, 0.0)

                # Count the dimension as complementary when one node is
                # clearly strong and the other is clearly weak.
                a_strong_b_weak = sa > _MID_THRESHOLD and sb < _DIFFICULTY_LOW
                b_strong_a_weak = sb > _MID_THRESHOLD and sa < _DIFFICULTY_LOW
                if a_strong_b_weak or b_strong_a_weak:
                    benefit += abs(sa - sb)
                    complementary_dims.append(dim)

            if benefit <= 0.0:
                continue

            # Cap the score at 1.0 for readability.
            normalised = min(benefit / max(len(DIMENSION_REGISTRY), 1), 1.0)

            dim_names = [
                DIMENSION_DESCRIPTIONS.get(d, {}).get("name_zh", d)
                for d in complementary_dims
            ]
            reason = (
                f"互补维度: {', '.join(dim_names)}。"
                f"{id_a} 和 {id_b} 在这些维度上互为强弱，协作可相互促进。"
            )

            suggestions.append(CollaborationSuggestion(
                node_a_id=id_a,
                node_b_id=id_b,
                reason=reason,
                expected_benefit_score=normalised,
            ))

        suggestions.sort(key=lambda s: s.expected_benefit_score, reverse=True)
        return suggestions

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_state(self, node_id: str) -> LearningState:
        """Return (and lazily create) the in-memory state for *node_id*."""
        if node_id not in self._states:
            self._states[node_id] = LearningState(node_id=node_id)
        return self._states[node_id]

    def _bootstrap_counters(self) -> None:
        """Pre-populate round counters from persisted engine history.

        This is a best-effort scan of the engine's results directory;
        failures are silently ignored so the coordinator can still be
        used in a fresh environment.
        """
        results_dir = self._engine.results_dir
        if not results_dir.exists():
            return

        for path in results_dir.iterdir():
            if not path.name.endswith("_history.json"):
                continue
            node_id = path.name[: -len("_history.json")]
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    entries = json.load(fh)
                # Group by domain to reconstruct per-domain counters.
                domain_counts: Dict[str, int] = {}
                for entry in entries:
                    d = entry.get("domain", "default")
                    domain_counts[d] = domain_counts.get(d, 0) + 1
                for domain, count in domain_counts.items():
                    self._round_counters[(node_id, domain)] = count
                # Rebuild a minimal learning state.
                state = self._ensure_state(node_id)
                state.total_rounds = len(entries)
                for entry in entries:
                    scores = entry.get("scores", {})
                    weighted = entry.get("weighted_total", 0.0)
                    state.growth_trajectory.append(weighted)
                    for dim, score in scores.items():
                        if score > state.best_scores.get(dim, 0.0):
                            state.best_scores[dim] = score
            except Exception:
                # Non-critical: the coordinator will work from scratch.
                pass
