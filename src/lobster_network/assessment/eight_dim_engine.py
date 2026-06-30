"""
8维度评估引擎 - Core Assessment Engine

核心功能:
1. 从训练记录中提取8维度得分
2. 结合 Clawvard 外部评估结果
3. 生成能力画像 (DimensionProfile)
4. 提供改进建议
5. 跨训练域聚合评估
"""

# from __future__ import annotations  # Python 3.6 不支持

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .dimensions import (
    DimensionProfile, DIMENSION_REGISTRY, DIMENSION_WEIGHTS,
    DIMENSION_DESCRIPTIONS, score_to_grade,
)


@dataclass
class AssessmentResult:
    """单次评估结果"""
    node_id: str
    domain: str
    timestamp: str
    profile: DimensionProfile
    source: str = "internal"  # internal / clawvard / hybrid
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "domain": self.domain,
            "timestamp": self.timestamp,
            "source": self.source,
            "profile": self.profile.to_dict(),
        }


# ── 维度评分器 ────────────────────────────────────────────

def _score_understanding(training_records: List[dict]) -> float:
    """理解力: 任务理解准确度，从对话记录中提取"""
    scores = []
    for r in training_records:
        if "task_completion" in r:
            scores.append(r["task_completion"])
        if "understanding_score" in r:
            scores.append(r["understanding_score"])
    return sum(scores) / max(len(scores), 1)


def _score_execution(training_records: List[dict]) -> float:
    """执行力: 代码/文档产出质量"""
    scores = []
    for r in training_records:
        if "output_quality" in r:
            scores.append(r["output_quality"])
        if "execution_score" in r:
            scores.append(r["execution_score"])
        if r.get("domain") == "go" and "problems_solved" in r:
            attempted = max(r.get("problems_attempted", 1), 1)
            scores.append(min(r["problems_solved"] / attempted, 1.0))
        if r.get("domain") == "ppt" and "pages_produced" in r:
            target = max(r.get("target_pages", 1), 1)
            scores.append(min(r["pages_produced"] / target, 1.0))
    return sum(scores) / max(len(scores), 1)


def _score_retrieval(training_records: List[dict]) -> float:
    """检索力: 信息获取效率"""
    scores = []
    for r in training_records:
        if "retrieval_accuracy" in r:
            scores.append(r["retrieval_accuracy"])
        if "search_success_rate" in r:
            scores.append(r["search_success_rate"])
    return sum(scores) / max(len(scores), 1)


def _score_reasoning(training_records: List[dict]) -> float:
    """推理力: 逻辑推理正确率"""
    scores = []
    for r in training_records:
        if "reasoning_accuracy" in r:
            scores.append(r["reasoning_accuracy"])
        if r.get("domain") == "go" and "win_rate" in r:
            scores.append(r["win_rate"])
        if "logic_score" in r:
            scores.append(r["logic_score"])
    return sum(scores) / max(len(scores), 1)


def _score_reflection(training_records: List[dict]) -> float:
    """反思力: 错误后的改进幅度"""
    scores = []
    for r in training_records:
        if "improvement_rate" in r:
            scores.append(r["improvement_rate"])
        if "reflection_score" in r:
            scores.append(r["reflection_score"])
        if "pre_score" in r and "post_score" in r:
            pre, post = r["pre_score"], r["post_score"]
            if post > pre:
                scores.append(min((post - pre) / max(pre, 0.01), 1.0))
    return sum(scores) / max(len(scores), 1)


def _score_tooling(training_records: List[dict]) -> float:
    """工具力: 工具使用正确性和效率"""
    scores = []
    for r in training_records:
        if "tool_usage_accuracy" in r:
            scores.append(r["tool_usage_accuracy"])
        if "tooling_score" in r:
            scores.append(r["tooling_score"])
        if r.get("domain") == "ppt" and "tool_proficiency" in r:
            scores.append(r["tool_proficiency"])
    return sum(scores) / max(len(scores), 1)


def _score_eq(training_records: List[dict]) -> float:
    """情商: 对话质量、协作表现"""
    scores = []
    for r in training_records:
        if "dialogue_quality" in r:
            scores.append(r["dialogue_quality"])
        if "collaboration_score" in r:
            scores.append(r["collaboration_score"])
        if "eq_score" in r:
            scores.append(r["eq_score"])
    return sum(scores) / max(len(scores), 1)


def _score_memory(training_records: List[dict]) -> float:
    """记忆力: 跨会话信息保持率"""
    scores = []
    for r in training_records:
        if "memory_retention" in r:
            scores.append(r["memory_retention"])
        if "cross_session_recall" in r:
            scores.append(r["cross_session_recall"])
        if "memory_score" in r:
            scores.append(r["memory_score"])
    return sum(scores) / max(len(scores), 1)


_SCORER_MAP = {
    "understanding": _score_understanding,
    "execution": _score_execution,
    "retrieval": _score_retrieval,
    "reasoning": _score_reasoning,
    "reflection": _score_reflection,
    "tooling": _score_tooling,
    "eq": _score_eq,
    "memory": _score_memory,
}


class DimensionScorer:
    """从训练记录中评估8维度"""

    @classmethod
    def score_all(cls, training_records: List[dict]) -> Dict[str, float]:
        """评估所有维度，返回 {dim_key: score}"""
        results = {}
        for dim, scorer in _SCORER_MAP.items():
            results[dim] = scorer(training_records)
        return results


# ── 改进建议生成器 ──────────────────────────────────────────

class ImprovementAdvisor:
    """基于8维度画像生成改进建议"""

    SUGGESTIONS: Dict[str, List[str]] = {
        "understanding": [
            "增加需求分析练习：在开始任务前先列出3个关键约束",
            "练习拆解复杂任务为子任务，验证理解是否完整",
        ],
        "execution": [
            "增加编码/文档产出练习，设定时间限制提高效率",
            "尝试从零开始构建项目，而非仅修改现有代码",
        ],
        "retrieval": [
            "练习从多个信息源交叉检索，验证信息一致性",
            "构建个人知识库，训练结构化检索能力",
        ],
        "reasoning": [
            "增加多步推理练习：围棋死活题、数学证明等",
            "练习反事实推理：如果条件改变，结论如何变化",
        ],
        "reflection": [
            "每次任务后写反思日志：做对了什么、哪里可以改进",
            "定期回顾过去的工作，识别重复出现的错误模式",
        ],
        "tooling": [
            "探索新工具和API，记录每个工具的最佳使用场景",
            "练习工具组合使用：将多个工具串联完成复杂任务",
        ],
        "eq": [
            "练习识别对话中的隐含意图和情绪信号",
            "增加协作场景练习：多人任务中的角色协调",
        ],
        "memory": [
            "练习信息压缩：将大量信息提炼为关键要点",
            "构建跨会话记忆体系，定期回顾和更新",
        ],
    }

    @classmethod
    def generate(cls, profile: DimensionProfile, top_n: int = 3) -> Dict[str, List[str]]:
        """为最弱的N个维度生成改进建议"""
        sorted_dims = sorted(profile.scores.items(), key=lambda x: x[1])
        weak_dims = [d for d, _ in sorted_dims[:top_n]]
        return {dim: cls.SUGGESTIONS.get(dim, []) for dim in weak_dims}


# ── 主引擎 ────────────────────────────────────────────────

class EightDimEngine:
    """
    8维度能力评估引擎

    用法:
        engine = EightDimEngine()

        # 方式1: 从训练记录评估
        result = engine.assess_from_records("xiaochen", "go", training_records)

        # 方式2: 从 Clawvard 成绩导入
        result = engine.assess_from_clawvard("qoder", clawvard_scores)

        # 方式3: 混合评估 (内部记录 + Clawvard)
        result = engine.assess_hybrid("qoder", "go", training_records, clawvard_scores)

        # 查看画像
        print(result.profile.summary())
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir) if data_dir else Path("/shared/training/8dim_engine")
        self.results_dir = self.data_dir / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def assess_from_records(
        self, node_id: str, domain: str, training_records: List[dict]
    ) -> AssessmentResult:
        """从训练记录评估8维度"""
        scores = DimensionScorer.score_all(training_records)
        profile = DimensionProfile(
            node_id=node_id, domain=domain, scores=scores,
        )
        # 生成改进建议
        profile.feedback = {}
        advisor_suggestions = ImprovementAdvisor.generate(profile)
        for dim, suggestions in advisor_suggestions.items():
            name = DIMENSION_DESCRIPTIONS[dim]["name_zh"]
            profile.feedback[dim] = f"{name}({scores[dim]:.0%}): " + "; ".join(suggestions)

        result = AssessmentResult(
            node_id=node_id,
            domain=domain,
            timestamp=datetime.now().isoformat(),
            profile=profile,
            source="internal",
            raw_data={"records_count": len(training_records)},
        )
        self._save_result(result)
        return result

    def assess_from_clawvard(
        self, node_id: str, clawvard_scores: Dict[str, float], domain: str = "general"
    ) -> AssessmentResult:
        """从 Clawvard 评估成绩导入"""
        # Clawvard 返回 0~1 的分数，直接使用
        profile = DimensionProfile(
            node_id=node_id, domain=domain, scores=clawvard_scores,
        )
        result = AssessmentResult(
            node_id=node_id,
            domain=domain,
            timestamp=datetime.now().isoformat(),
            profile=profile,
            source="clawvard",
            raw_data={"clawvard_scores": clawvard_scores},
        )
        self._save_result(result)
        return result

    def assess_hybrid(
        self,
        node_id: str,
        domain: str,
        training_records: List[dict],
        clawvard_scores: Dict[str, float],
        clawvard_weight: float = 0.6,
    ) -> AssessmentResult:
        """混合评估: 内部训练记录 + Clawvard 外部评估"""
        internal_scores = DimensionScorer.score_all(training_records)
        # 加权混合
        hybrid_scores = {}
        for dim in DIMENSION_REGISTRY:
            internal = internal_scores.get(dim, 0.0)
            external = clawvard_scores.get(dim, 0.0)
            if dim in clawvard_scores:
                hybrid_scores[dim] = external * clawvard_weight + internal * (1 - clawvard_weight)
            else:
                hybrid_scores[dim] = internal

        profile = DimensionProfile(
            node_id=node_id, domain=domain, scores=hybrid_scores,
        )
        # 改进建议
        profile.feedback = {}
        advisor_suggestions = ImprovementAdvisor.generate(profile)
        for dim, suggestions in advisor_suggestions.items():
            name = DIMENSION_DESCRIPTIONS[dim]["name_zh"]
            profile.feedback[dim] = f"{name}({hybrid_scores[dim]:.0%}): " + "; ".join(suggestions)

        result = AssessmentResult(
            node_id=node_id,
            domain=domain,
            timestamp=datetime.now().isoformat(),
            profile=profile,
            source="hybrid",
            raw_data={
                "internal_scores": internal_scores,
                "clawvard_scores": clawvard_scores,
                "clawvard_weight": clawvard_weight,
            },
        )
        self._save_result(result)
        return result

    def load_history(self, node_id: str) -> List[AssessmentResult]:
        """加载节点的历史评估记录"""
        results = []
        history_file = self.results_dir / f"{node_id}_history.json"
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data:
                profile = DimensionProfile(
                    node_id=entry["node_id"],
                    domain=entry["domain"],
                    scores=entry["scores"],
                    feedback=entry.get("feedback", {}),
                )
                results.append(AssessmentResult(
                    node_id=entry["node_id"],
                    domain=entry["domain"],
                    timestamp=entry["timestamp"],
                    profile=profile,
                    source=entry.get("source", "internal"),
                ))
        return results

    def compare_nodes(self, node_profiles: List[DimensionProfile]) -> Dict[str, Any]:
        """对比多个节点的能力画像"""
        comparison = {
            "nodes": [p.node_id for p in node_profiles],
            "dimensions": {},
        }
        for dim in DIMENSION_REGISTRY:
            dim_data = {}
            for p in node_profiles:
                dim_data[p.node_id] = p.scores.get(dim, 0.0)
            # 找出该维度最强/最弱节点
            best = max(dim_data, key=dim_data.get)
            worst = min(dim_data, key=dim_data.get)
            comparison["dimensions"][dim] = {
                "scores": dim_data,
                "best": best,
                "worst": worst,
                "avg": sum(dim_data.values()) / max(len(dim_data), 1),
            }
        return comparison

    def _save_result(self, result: AssessmentResult):
        """持久化评估结果"""
        history_file = self.results_dir / f"{result.node_id}_history.json"
        history = []
        if history_file.exists():
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        history.append(result.profile.to_dict() | {
            "timestamp": result.timestamp,
            "source": result.source,
        })
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
