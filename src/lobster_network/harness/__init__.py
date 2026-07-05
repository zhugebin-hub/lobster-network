"""
Harness Engineering — 小龙虾网络驾驭工程模块

基于阿里云开发者《给野马套上缰绳：Agent Harness 工程实践》，
融合 Mitchell Hashimoto 的 Harness Engineering 理念：

"每当你发现 Agent 犯了一个错，就花时间工程化一个解，让它将来不再犯同样的错。"

核心公式: Agent = Model + Harness
- Model: 负责推理
- Harness: 负责工具系统、上下文管理、权限控制、反馈回路、记忆与协作

四条反直觉铁律:
1. 上下文越少越好 — 稀缺资源要精挑
2. 专才 Agent 永远赢过通才 Agent — 2-3个Agent + 无限Skill
3. 状态要写文件，不要塞上下文 — Workspace 是"Agent的Git仓库"
4. 能写成 Linter 的约束，别停留在文档 — 机器强制 > 人力记忆

六种工程模式:
1. 双阶段架构 (Init + Exec)
2. 工具签名即文档
3. Sub-Agent 隔离
4. 上下游反压
5. 智能体审智能体
6. 熵管理与文档园丁

四根 Harness 护栏:
- Context Engineering（上下文工程）
- Architecture Constraints（架构约束）
- Feedback Loop（反馈回路）
- Entropy Management（熵管理）
"""

from .context_engineering import ContextBuilder, ContextSlot, context_for_task
from .architecture_constraints import Constraint, ConstraintEngine, LinterConstraint
from .feedback_loop import FeedbackLoop, AgentReviewer, FailureAnalyzer
from .entropy_manager import EntropyManager, DocGardener, DriftDetector
from .workspace import Workspace, WorkspaceFile, RpaLock
from .dual_stage import DualStageExecutor, InitStage, ExecStage
from .patterns import (
    HarnessPattern,
    DualStagePattern,
    ToolSignaturePattern,
    SubAgentIsolationPattern,
    BackpressurePattern,
    AgentReviewPattern,
    EntropyManagementPattern,
    apply_pattern,
    ALL_PATTERNS,
)

__all__ = [
    # 上下文工程
    "ContextBuilder", "ContextSlot", "context_for_task",
    # 架构约束
    "Constraint", "ConstraintEngine", "LinterConstraint",
    # 反馈回路
    "FeedbackLoop", "AgentReviewer", "FailureAnalyzer",
    # 熵管理
    "EntropyManager", "DocGardener", "DriftDetector",
    # 工作空间
    "Workspace", "WorkspaceFile", "RpaLock",
    # 双阶段架构
    "DualStageExecutor", "InitStage", "ExecStage",
    # 工程模式
    "HarnessPattern", "DualStagePattern", "ToolSignaturePattern",
    "SubAgentIsolationPattern", "BackpressurePattern",
    "AgentReviewPattern", "EntropyManagementPattern",
    "apply_pattern",
]
