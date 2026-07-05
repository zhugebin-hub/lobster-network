"""
8维度定义与评分体系 - Dimension Definitions & Scoring

每个维度包含:
- 名称 (中/英)
- 描述
- 默认权重
- 关联训练域
- 评分标准 (rubric)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json


# ── 维度枚举 ──────────────────────────────────────────────

DIMENSION_REGISTRY = [
    "understanding", "execution", "retrieval", "reasoning",
    "reflection", "tooling", "eq", "memory",
]

DIMENSION_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "understanding": {
        "name_zh": "理解力",
        "name_en": "Understanding",
        "desc": "准确理解任务需求、约束条件和隐含意图的能力",
        "icon": "🎯",
    },
    "execution": {
        "name_zh": "执行力",
        "name_en": "Execution",
        "desc": "将计划转化为高质量输出的能力，包括代码编写、文档撰写等",
        "icon": "⚡",
    },
    "retrieval": {
        "name_zh": "检索力",
        "name_en": "Retrieval",
        "desc": "从记忆、文档或外部资源中高效获取相关信息的能力",
        "icon": "🔍",
    },
    "reasoning": {
        "name_zh": "推理力",
        "name_en": "Reasoning",
        "desc": "逻辑分析、因果推断和多步推理的能力",
        "icon": "🧠",
    },
    "reflection": {
        "name_zh": "反思力",
        "name_en": "Reflection",
        "desc": "自我评估、识别不足并迭代改进的能力",
        "icon": "🪞",
    },
    "tooling": {
        "name_zh": "工具力",
        "name_en": "Tooling",
        "desc": "选择并有效使用工具、API和外部资源完成任务的能力",
        "icon": "🔧",
    },
    "eq": {
        "name_zh": "情商",
        "name_en": "EQ",
        "desc": "理解对话者意图、情绪和上下文，给出恰当回应的能力",
        "icon": "💬",
    },
    "memory": {
        "name_zh": "记忆力",
        "name_en": "Memory",
        "desc": "有效存储、组织和调用跨会话信息的能力",
        "icon": "📝",
    },
}

# 训练域 → 维度权重映射 (各域侧重不同维度)
DIMENSION_WEIGHTS: Dict[str, Dict[str, float]] = {
    "go": {
        "reasoning": 0.30, "execution": 0.20, "memory": 0.15,
        "retrieval": 0.10, "reflection": 0.10, "understanding": 0.10,
        "tooling": 0.03, "eq": 0.02,
    },
    "poster": {
        "execution": 0.25, "understanding": 0.20, "tooling": 0.15,
        "reasoning": 0.10, "reflection": 0.10, "retrieval": 0.10,
        "eq": 0.05, "memory": 0.05,
    },
    "ppt": {
        "execution": 0.25, "understanding": 0.15, "tooling": 0.20,
        "reasoning": 0.10, "reflection": 0.10, "retrieval": 0.10,
        "eq": 0.05, "memory": 0.05,
    },
    "default": {
        "understanding": 0.125, "execution": 0.125, "retrieval": 0.125,
        "reasoning": 0.125, "reflection": 0.125, "tooling": 0.125,
        "eq": 0.125, "memory": 0.125,
    },
}

# Clawvard 评级标准
GRADE_THRESHOLDS = [
    ("S", 0.95), ("A+", 0.90), ("A", 0.85), ("B+", 0.80),
    ("B", 0.70), ("C+", 0.60), ("C", 0.50), ("D", 0.35), ("F", 0.0),
]


def score_to_grade(score: float) -> str:
    """将分数(0~1)转换为评级"""
    for grade, threshold in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


@dataclass
class Dimension:
    """单个维度的定义"""
    key: str
    name_zh: str
    name_en: str
    desc: str
    icon: str = ""

    @classmethod
    def from_registry(cls, key: str) -> "Dimension":
        info = DIMENSION_DESCRIPTIONS[key]
        return cls(
            key=key,
            name_zh=info["name_zh"],
            name_en=info["name_en"],
            desc=info["desc"],
            icon=info.get("icon", ""),
        )


@dataclass
class DimensionProfile:
    """节点在8维度上的能力画像"""
    node_id: str
    domain: str
    scores: Dict[str, float] = field(default_factory=dict)  # dim_key → score (0~1)
    grades: Dict[str, str] = field(default_factory=dict)     # dim_key → grade
    weighted_total: float = 0.0
    overall_grade: str = ""
    feedback: Dict[str, str] = field(default_factory=dict)   # dim_key → feedback text

    def __post_init__(self):
        # 初始化缺失维度为0
        for dim in DIMENSION_REGISTRY:
            self.scores.setdefault(dim, 0.0)

        # 计算评级
        self.grades = {k: score_to_grade(v) for k, v in self.scores.items()}

        # 加权总分
        weights = DIMENSION_WEIGHTS.get(self.domain, DIMENSION_WEIGHTS["default"])
        self.weighted_total = sum(
            self.scores.get(k, 0.0) * w for k, w in weights.items()
        )
        self.overall_grade = score_to_grade(self.weighted_total)

    def radar_data(self) -> List[Dict[str, any]]:
        """生成雷达图数据 (适用于 matplotlib / plotly)"""
        return [
            {"dimension": DIMENSION_DESCRIPTIONS[d]["name_zh"], "score": self.scores.get(d, 0.0)}
            for d in DIMENSION_REGISTRY
        ]

    def strengths(self, top_n: int = 3) -> List[str]:
        """返回得分最高的N个维度"""
        sorted_dims = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return [DIMENSION_DESCRIPTIONS[d]["name_zh"] for d, _ in sorted_dims[:top_n]]

    def weaknesses(self, top_n: int = 3) -> List[str]:
        """返回得分最低的N个维度"""
        sorted_dims = sorted(self.scores.items(), key=lambda x: x[1])
        return [DIMENSION_DESCRIPTIONS[d]["name_zh"] for d, _ in sorted_dims[:top_n]]

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "domain": self.domain,
            "scores": self.scores,
            "grades": self.grades,
            "weighted_total": round(self.weighted_total, 4),
            "overall_grade": self.overall_grade,
            "strengths": self.strengths(),
            "weaknesses": self.weaknesses(),
            "feedback": self.feedback,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    def summary(self) -> str:
        """生成可读摘要"""
        lines = [
            f"═══ {self.node_id} 能力画像 ({self.domain}) ═══",
            f"总评: {self.overall_grade} ({self.weighted_total:.1%})",
            "",
        ]
        weights = DIMENSION_WEIGHTS.get(self.domain, DIMENSION_WEIGHTS["default"])
        for dim in DIMENSION_REGISTRY:
            info = DIMENSION_DESCRIPTIONS[dim]
            score = self.scores.get(dim, 0.0)
            grade = self.grades.get(dim, "-")
            weight = weights.get(dim, 0)
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            lines.append(f"  {info['icon']} {info['name_zh']: <4} [{bar}] {score:.0%} {grade} (权重{weight:.0%})")
        lines.append("")
        lines.append(f"强项: {', '.join(self.strengths())}")
        lines.append(f"待提升: {', '.join(self.weaknesses())}")
        return "\n".join(lines)
