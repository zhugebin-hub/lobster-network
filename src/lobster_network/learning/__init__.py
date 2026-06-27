"""
学习模块 - Learning Module

Closes the assessment-training feedback loop:
- Run 8-dimension assessments after each training round
- Measure per-dimension progress between rounds
- Generate adaptive training plans targeting weak dimensions
- Track cumulative learning state
- Suggest cross-node collaborations based on complementary strengths

Usage:
    from lobster_network.learning import LearningCoordinator, TrainingPlan

    coordinator = LearningCoordinator()
    result = coordinator.run_training_round("xiaochen", "go", records)
"""

from .coordinator import (
    LearningCoordinator,
    TrainingRoundResult,
    TrainingPlan,
    ProgressReport,
    LearningState,
    CollaborationSuggestion,
)

__all__ = [
    "LearningCoordinator",
    "TrainingRoundResult",
    "TrainingPlan",
    "ProgressReport",
    "LearningState",
    "CollaborationSuggestion",
]
