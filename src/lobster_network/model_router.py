#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型路由器 (Model Router) - 小龙虾网络 V3.1
难度感知路由，按题目难度选择最经济的模型

功能:
- 入门/初级题 → qwen-turbo (低成本)
- 中级题 → qwen-plus (中等成本)
- 高级/复杂题 → qwen-max (高推理)
- 预估 API 成本降低 50%
"""

import logging
import time
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Difficulty(Enum):
    BEGINNER = "beginner"       # 入门
    EASY = "easy"              # 初级
    MEDIUM = "medium"          # 中级
    HARD = "hard"              # 高级
    EXPERT = "expert"          # 专家


class ModelTier(Enum):
    TURBO = "qwen-turbo"       # 低成本, 快速
    PLUS = "qwen-plus"         # 中等成本, 平衡
    MAX = "qwen-max"           # 高成本, 强推理


@dataclass
class ModelConfig:
    """模型配置"""
    model_id: str
    display_name: str
    tier: ModelTier
    cost_per_1k_tokens: float    # 每千 token 成本（元）
    max_context: int              # 最大上下文长度
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "model_id": self.model_id,
            "display_name": self.display_name,
            "tier": self.tier.value,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "max_context": self.max_context,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


@dataclass
class RoutingDecision:
    """路由决策"""
    selected_model: str
    difficulty: str
    reason: str
    estimated_cost: float = 0.0
    alternatives: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "selected_model": self.selected_model,
            "difficulty": self.difficulty,
            "reason": self.reason,
            "estimated_cost": round(self.estimated_cost, 4),
            "alternatives": self.alternatives,
        }


@dataclass
class CostStats:
    """成本统计"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    by_model: Dict[str, Dict] = field(default_factory=dict)
    savings_vs_max: float = 0.0   # 相比全用 max 节省的费用

    def to_dict(self) -> Dict:
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_requests,
            "total_cost": round(self.total_cost, 4),
            "by_model": self.by_model,
            "savings_vs_max": round(self.savings_vs_max, 4),
        }


# ========== 模型注册表 ==========

MODEL_REGISTRY: Dict[str, ModelConfig] = {
    "qwen-turbo": ModelConfig(
        model_id="qwen-turbo",
        display_name="通义千问-Turbo",
        tier=ModelTier.TURBO,
        cost_per_1k_tokens=0.003,
        max_context=8192,
        strengths=["快速响应", "低成本", "基础问答", "简单推理"],
        weaknesses=["复杂推理", "长文本", "多步骤任务"],
    ),
    "qwen-plus": ModelConfig(
        model_id="qwen-plus",
        display_name="通义千问-Plus",
        tier=ModelTier.PLUS,
        cost_per_1k_tokens=0.02,
        max_context=131072,
        strengths=["平衡性能", "中等推理", "代码生成", "文本理解"],
        weaknesses=["极端复杂推理"],
    ),
    "qwen-max": ModelConfig(
        model_id="qwen-max",
        display_name="通义千问-Max",
        tier=ModelTier.MAX,
        cost_per_1k_tokens=0.12,
        max_context=32768,
        strengths=["最强推理", "复杂分析", "数学计算", "创意写作"],
        weaknesses=["成本高", "响应慢"],
    ),
    "qwen3-max": ModelConfig(
        model_id="qwen3-max",
        display_name="通义千问3-Max",
        tier=ModelTier.MAX,
        cost_per_1k_tokens=0.12,
        max_context=131072,
        strengths=["最新模型", "超长上下文", "最强推理"],
        weaknesses=["成本高"],
    ),
}

# 难度 → 模型映射
DIFFICULTY_MAP = {
    Difficulty.BEGINNER: ModelTier.TURBO,
    Difficulty.EASY: ModelTier.TURBO,
    Difficulty.MEDIUM: ModelTier.PLUS,
    Difficulty.HARD: ModelTier.MAX,
    Difficulty.EXPERT: ModelTier.MAX,
}

# 成本系数（相对 qwen-max 为 1.0）
COST_RATIO = {
    ModelTier.TURBO: 0.025,   # max 的 2.5%
    ModelTier.PLUS: 0.167,    # max 的 16.7%
    ModelTier.MAX: 1.0,
}


class ModelRouter:
    """模型路由器"""

    def __init__(self, name: str = "default", budget_mode: str = "balanced"):
        """
        Args:
            name: 路由器名称
            budget_mode: 预算模式
                - aggressive: 激进省钱，尽可能用 turbo
                - balanced: 平衡（默认）
                - conservative: 保守，更多用 plus/max
        """
        self.name = name
        self.budget_mode = budget_mode
        self._stats = CostStats()
        self._history: List[RoutingDecision] = []

        logger.info(f"[模型路由:{self.name}] 初始化, 预算模式: {budget_mode}")

    def _detect_difficulty(self, question: str, metadata: Optional[Dict] = None) -> Difficulty:
        """检测题目难度"""
        # 1. 优先使用元数据中的难度标记
        if metadata:
            diff = metadata.get("difficulty", metadata.get("level", "")).lower()
            if diff in ("beginner", "入门"):
                return Difficulty.BEGINNER
            elif diff in ("easy", "初级", "简单"):
                return Difficulty.EASY
            elif diff in ("medium", "中级", "中等"):
                return Difficulty.MEDIUM
            elif diff in ("hard", "高级", "困难"):
                return Difficulty.HARD
            elif diff in ("expert", "专家", "极难"):
                return Difficulty.EXPERT

        # 2. 基于题目特征启发式判断
        score = 0
        q_lower = question.lower()

        # 长度因素
        if len(question) > 500:
            score += 2
        elif len(question) > 200:
            score += 1

        # 关键词因素
        hard_keywords = ["证明", "推导", "分析", "设计", "优化", "对比", "评估",
                         "complex", "analyze", "design", "optimize", "prove"]
        easy_keywords = ["什么是", "定义", "选择", "填空", "what is", "which"]

        for kw in hard_keywords:
            if kw in q_lower:
                score += 1
        for kw in easy_keywords:
            if kw in q_lower:
                score -= 1

        # 数学/代码因素
        if any(c in question for c in ['∑', '∫', '√', '≤', '≥', '≠']):
            score += 2
        if '```' in question or 'def ' in q_lower or 'class ' in q_lower:
            score += 1

        # 映射到难度等级
        if score <= 0:
            return Difficulty.BEGINNER
        elif score <= 2:
            return Difficulty.EASY
        elif score <= 4:
            return Difficulty.MEDIUM
        elif score <= 6:
            return Difficulty.HARD
        else:
            return Difficulty.EXPERT

    def _apply_budget_mode(self, tier: ModelTier, difficulty: Difficulty) -> ModelTier:
        """根据预算模式调整"""
        if self.budget_mode == "aggressive":
            # 降级：max → plus, plus → turbo
            if tier == ModelTier.MAX:
                return ModelTier.PLUS
            elif tier == ModelTier.PLUS and difficulty != Difficulty.MEDIUM:
                return ModelTier.TURBO
        elif self.budget_mode == "conservative":
            # 升级：turbo → plus, plus → max（仅高级以上）
            if tier == ModelTier.TURBO and difficulty == Difficulty.EASY:
                return ModelTier.PLUS
            elif tier == ModelTier.PLUS and difficulty == Difficulty.HARD:
                return ModelTier.MAX
        return tier

    def route(self, question: str, metadata: Optional[Dict] = None,
              required_model: Optional[str] = None) -> RoutingDecision:
        """路由决策"""
        if required_model and required_model in MODEL_REGISTRY:
            config = MODEL_REGISTRY[required_model]
            return RoutingDecision(
                selected_model=required_model,
                difficulty="specified",
                reason=f"强制指定模型: {config.display_name}",
                estimated_cost=config.cost_per_1k_tokens,
            )

        difficulty = self._detect_difficulty(question, metadata)
        tier = DIFFICULTY_MAP[difficulty]
        tier = self._apply_budget_mode(tier, difficulty)

        # 选择该档次的最佳模型
        candidates = [m for m in MODEL_REGISTRY.values() if m.tier == tier]
        if not candidates:
            candidates = list(MODEL_REGISTRY.values())
        selected = candidates[0]

        # 备选方案
        alternatives = [m.model_id for m in candidates[1:]]
        if tier != ModelTier.TURBO:
            turbo = MODEL_REGISTRY.get("qwen-turbo")
            if turbo:
                alternatives.append(turbo.model_id)
        if tier != ModelTier.MAX:
            max_model = MODEL_REGISTRY.get("qwen-max")
            if max_model:
                alternatives.append(max_model.model_id)

        decision = RoutingDecision(
            selected_model=selected.model_id,
            difficulty=difficulty.value,
            reason=f"难度={difficulty.value}, 档位={tier.value}, "
                   f"成本={selected.cost_per_1k_tokens}元/千token",
            estimated_cost=selected.cost_per_1k_tokens,
            alternatives=alternatives[:2],
        )

        self._history.append(decision)
        self._stats.total_requests += 1

        # 记录按模型统计
        model_key = selected.model_id
        if model_key not in self._stats.by_model:
            self._stats.by_model[model_key] = {"count": 0, "cost": 0.0}
        self._stats.by_model[model_key]["count"] += 1
        self._stats.by_model[model_key]["cost"] = round(
            self._stats.by_model[model_key]["cost"] + selected.cost_per_1k_tokens, 4
        )

        # 计算节省（假设全用 max）
        max_cost = MODEL_REGISTRY["qwen-max"].cost_per_1k_tokens
        self._stats.savings_vs_max = round(
            self._stats.savings_vs_max + (max_cost - selected.cost_per_1k_tokens), 4
        )

        logger.info(f"[模型路由:{self.name}] {difficulty.value} → {selected.model_id} "
                     f"(省 {selected.cost_per_1k_tokens/max_cost*100:.0f}% 成本)")

        return decision

    def batch_route(self, questions: List[Dict]) -> List[RoutingDecision]:
        """批量路由"""
        return [self.route(q.get("question", ""), q) for q in questions]

    def get_stats(self) -> Dict:
        """获取统计"""
        return self._stats.to_dict()

    def get_recommendation(self) -> Dict:
        """获取优化建议"""
        stats = self._stats.to_dict()
        suggestions = []

        if stats["total_requests"] == 0:
            return {"suggestions": ["暂无数据，请先进行路由"]}

        # 分析各模型使用比例
        total = stats["total_requests"]
        for model_id, data in stats.get("by_model", {}).items():
            ratio = data["count"] / total * 100
            tier = MODEL_REGISTRY.get(model_id, ModelConfig(model_id, "", ModelTier.TURBO, 0, 0)).tier
            if tier == ModelTier.MAX and ratio > 50:
                suggestions.append(f"⚠️ {model_id} 使用比例过高 ({ratio:.0f}%)，建议将简单题目路由到 turbo")
            elif tier == ModelTier.TURBO and ratio < 20:
                suggestions.append(f"💡 {model_id} 使用不足 ({ratio:.0f}%)，更多简单题可以用它")

        if stats["savings_vs_max"] > 0:
            suggestions.append(f"✅ 已节省 {stats['savings_vs_max']:.4f} 元（相比全用 max）")

        return {
            "stats": stats,
            "budget_mode": self.budget_mode,
            "suggestions": suggestions,
        }


# ========== 预定义路由器 ==========

# 默认路由器（平衡模式）
default_router = ModelRouter("default", budget_mode="balanced")

# 省钱路由器（激进模式）
budget_router = ModelRouter("budget", budget_mode="aggressive")

# 质量路由器（保守模式）
quality_router = ModelRouter("quality", budget_mode="conservative")

_routers: Dict[str, ModelRouter] = {
    "default": default_router,
    "budget": budget_router,
    "quality": quality_router,
}


def get_router(name: str = "default") -> ModelRouter:
    """获取路由器"""
    return _routers.get(name, default_router)


def route_question(question: str, metadata: Optional[Dict] = None,
                   router_name: str = "default") -> RoutingDecision:
    """路由题目（便捷函数）"""
    router = get_router(router_name)
    return router.route(question, metadata)
