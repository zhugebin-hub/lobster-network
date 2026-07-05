"""
8维度能力评估引擎 - Eight Dimension Assessment Engine
参考 Clawvard School 8维度评估体系构建

维度:
- Understanding (理解力)
- Execution (执行力)
- Retrieval (检索力)
- Reasoning (推理力)
- Reflection (反思力)
- Tooling (工具力)
- EQ (情商)
- Memory (记忆力)

用法:
    from domains.assessment import EightDimEngine, DimensionProfile

    engine = EightDimEngine()
    profile = engine.assess("go", student_node)
    print(profile.radar_chart())
"""

from .dimensions import (
    Dimension, DimensionProfile, DIMENSION_REGISTRY,
    DIMENSION_DESCRIPTIONS, DIMENSION_WEIGHTS,
)
from .eight_dim_engine import EightDimEngine, AssessmentResult
from .clawvard_bridge import ClawvardBridge, PracticeSession

__all__ = [
    "EightDimEngine", "AssessmentResult",
    "Dimension", "DimensionProfile", "DIMENSION_REGISTRY",
    "DIMENSION_DESCRIPTIONS", "DIMENSION_WEIGHTS",
    "ClawvardBridge", "PracticeSession",
]
