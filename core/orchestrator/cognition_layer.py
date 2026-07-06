#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.2 — 认知-执行分离增强

显式分离 PlanningAgent 和 ExecutionAgent，实现认知-执行解耦：

核心设计：
- PlanningAgent: 意图理解 / 任务拆解 / 方案生成 (高灵活性，有不确定性)
- ExecutionAgent: 确定性执行 / 结果验证 / 异常上报 (确定性执行，可审计)
- PlanNode 树形结构: 根目标 → 子任务 → 原子操作
- 失败回滚: 子任务失败仅回滚该分支，非整棵计划树
- 不确定性标记: 每个 PlanNode 附带 confidence_score

参考：
- 智能体网络最新进展综述_2025-2026 — 2.2 四层架构「认知与执行分离」
- 四层架构实践
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("cognition_layer")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举定义
# ============================================================

class NodeStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class NodeType(str, Enum):
    ROOT_GOAL = "root_goal"       # 根目标
    SUBTASK = "subtask"           # 子任务
    ATOMIC_OP = "atomic_op"       # 原子操作（不可再分）
    DECISION = "decision"         # 决策节点
    PARALLEL = "parallel"         # 并行分支


class ExecutionStrategy(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    RETRY_ON_FAILURE = "retry_on_failure"


# ============================================================
# PlanNode — 计划树节点
# ============================================================

@dataclass
class PlanNode:
    """
    PlanNode — 计划树节点。

    每个节点包含：
    - 任务描述
    - 置信度分数（不确定性标记）
    - 依赖关系
    - 执行策略
    - 回滚信息
    """
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_id: Optional[str] = None
    node_type: NodeType = NodeType.SUBTASK
    description: str = ""
    status: NodeStatus = NodeStatus.PENDING
    confidence_score: float = 0.8          # 0~1，<0.5 标记为不确定
    children: List["PlanNode"] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # node_id 列表
    strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    assigned_agent: Optional[str] = None   # 分配的执行Agent
    max_retries: int = 2
    retry_count: int = 0
    timeout_sec: int = 300
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    error_info: Optional[Dict[str, Any]] = None
    checkpoint_data: Optional[Dict[str, Any]] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    def add_child(self, child: "PlanNode"):
        child.parent_id = self.node_id
        self.children.append(child)

    def find_node(self, node_id: str) -> Optional["PlanNode"]:
        """递归查找节点"""
        if self.node_id == node_id:
            return self
        for child in self.children:
            found = child.find_node(node_id)
            if found:
                return found
        return None

    def get_all_nodes(self) -> List["PlanNode"]:
        """展平获取所有节点"""
        nodes = [self]
        for child in self.children:
            nodes.extend(child.get_all_nodes())
        return nodes

    def get_failed_nodes(self) -> List["PlanNode"]:
        return [n for n in self.get_all_nodes() if n.status == NodeStatus.FAILED]

    def get_rollback_scope(self, failed_node_id: str) -> List[str]:
        """
        失败回滚范围：仅回滚失败节点所在分支，非整棵计划树。
        返回需要回滚的 node_id 列表。
        """
        failed_node = self.find_node(failed_node_id)
        if not failed_node:
            return []

        # 收集该节点及其下游所有待回滚节点
        scope = []
        nodes_to_collect = [failed_node]
        while nodes_to_collect:
            node = nodes_to_collect.pop(0)
            if node.status in (NodeStatus.FAILED, NodeStatus.RUNNING):
                scope.append(node.node_id)
                nodes_to_collect.extend(node.children)
        return scope

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "parent_id": self.parent_id,
            "node_type": self.node_type.value,
            "description": self.description,
            "status": self.status.value,
            "confidence_score": self.confidence_score,
            "children": [c.to_dict() for c in self.children],
            "dependencies": self.dependencies,
            "strategy": self.strategy.value,
            "assigned_agent": self.assigned_agent,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "timeout_sec": self.timeout_sec,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "error_info": self.error_info,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
            "tags": self.tags,
        }

    def to_summary(self) -> Dict[str, Any]:
        all_nodes = self.get_all_nodes()
        status_counts = {}
        for node in all_nodes:
            s = node.status.value
            status_counts[s] = status_counts.get(s, 0) + 1
        return {
            "root_node_id": self.node_id,
            "root_description": self.description,
            "total_nodes": len(all_nodes),
            "status_counts": status_counts,
            "avg_confidence": round(
                sum(n.confidence_score for n in all_nodes) / max(len(all_nodes), 1), 3
            ),
            "low_confidence_nodes": [
                {"node_id": n.node_id, "desc": n.description, "score": n.confidence_score}
                for n in all_nodes if n.confidence_score < 0.5
            ],
        }


# ============================================================
# PlanningAgent — 规划Agent
# ============================================================

class PlanningAgent:
    """
    PlanningAgent — 认知层规划Agent。

    职责：
    - 意图理解与澄清
    - 将用户意图分解为 PlanNode 树
    - 评估每个子任务的置信度
    - 生成候选执行方案
    """

    def __init__(self, max_depth: int = 5, min_confidence: float = 0.3):
        self.max_depth = max_depth
        self.min_confidence = min_confidence
        self._plan_history: List[PlanNode] = []
        logger.info("[PlanningAgent] 规划Agent已初始化")

    def decompose(self, intent: str, context: Dict[str, Any] = None) -> PlanNode:
        """
        将用户意图分解为任务计划树。

        参数:
            intent: 用户意图描述
            context: 上下文信息（约束/偏好/历史）

        返回:
            PlanNode 根节点，包含完整子树
        """
        root = PlanNode(
            node_type=NodeType.ROOT_GOAL,
            description=intent,
            confidence_score=self._estimate_confidence(intent, "root"),
        )

        # 基于意图拆解子任务
        subtasks = self._parse_intent(intent, context or {})
        for i, sub in enumerate(subtasks):
            child = self._build_subtask(sub, depth=1, context=context)
            root.add_child(child)

        self._plan_history.append(root)
        logger.info(
            f"[PlanningAgent] 意图分解完成: "
            f"'{intent[:50]}...' → {len(subtasks)} 个子任务"
        )
        return root

    def _parse_intent(self, intent: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析意图为子任务列表（基于规则 + 关键词）"""
        subtasks = []

        # 规则1: 分析类意图 → 数据收集 → 分析 → 报告
        analysis_keywords = ["分析", "评估", "研究", "review", "analyze"]
        if any(kw in intent for kw in analysis_keywords):
            subtasks.extend([
                {"description": "数据收集与预处理", "node_type": NodeType.SUBTASK, "confidence": 0.9},
                {"description": "核心分析计算", "node_type": NodeType.SUBTASK, "confidence": 0.75},
                {"description": "结果验证与报告生成", "node_type": NodeType.SUBTASK, "confidence": 0.85},
            ])

        # 规则2: 生成类意图 → 模板选择 → 内容生成 → 格式化 → 审核
        generate_keywords = ["生成", "创建", "编写", "写", "generate", "create"]
        if any(kw in intent for kw in generate_keywords):
            subtasks.extend([
                {"description": "模板/框架选择", "node_type": NodeType.SUBTASK, "confidence": 0.9},
                {"description": "核心内容生成", "node_type": NodeType.SUBTASK, "confidence": 0.7},
                {"description": "格式化与排版", "node_type": NodeType.SUBTASK, "confidence": 0.85},
                {"description": "质量审核与修正", "node_type": NodeType.SUBTASK, "confidence": 0.8},
            ])

        # 规则3: 搜索类意图 → 检索 → 筛选 → 整理
        search_keywords = ["搜索", "查找", "找", "搜索", "search", "find"]
        if any(kw in intent for kw in search_keywords):
            subtasks.extend([
                {"description": "多源检索", "node_type": NodeType.SUBTASK, "confidence": 0.85},
                {"description": "相关性筛选排序", "node_type": NodeType.SUBTASK, "confidence": 0.8},
                {"description": "结果整理汇总", "node_type": NodeType.SUBTASK, "confidence": 0.95},
            ])

        # 兜底: 至少一个子任务
        if not subtasks:
            subtasks.append({
                "description": intent,
                "node_type": NodeType.SUBTASK,
                "confidence": 0.6,
            })

        return subtasks

    def _build_subtask(self, spec: Dict[str, Any], depth: int,
                       context: Dict[str, Any] = None) -> PlanNode:
        """递归构建子任务节点"""
        node = PlanNode(
            node_type=spec.get("node_type", NodeType.SUBTASK),
            description=spec["description"],
            confidence_score=spec.get("confidence", 0.8),
        )

        # 递归: 如果深度未到上限且有子任务描述
        if depth < self.max_depth and "subtasks" in spec:
            for sub in spec.get("subtasks", []):
                child = self._build_subtask(sub, depth + 1, context)
                node.add_child(child)

        return node

    def _estimate_confidence(self, intent: str, role: str) -> float:
        """估算规划置信度"""
        # 简单启发式: 长度适中、有明确动词的意图置信度更高
        score = 0.7
        if 10 < len(intent) < 200:
            score += 0.1
        if any(kw in intent for kw in ["分析", "生成", "搜索", "整理"]):
            score += 0.1
        return min(1.0, score)

    def get_plan_history(self) -> List[PlanNode]:
        return self._plan_history


# ============================================================
# ExecutionAgent — 执行Agent
# ============================================================

class ExecutionAgent:
    """
    ExecutionAgent — 技能层执行Agent。

    职责：
    - 确定性执行 PlanNode
    - 结果验证
    - 异常检测与上报
    - 分支级回滚
    """

    def __init__(self, agent_id: str = "executor-001"):
        self.agent_id = agent_id
        self._executors: Dict[NodeType, Callable] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
        logger.info(f"[ExecutionAgent] 执行Agent '{agent_id}' 已初始化")

    def register_executor(self, node_type: NodeType, executor: Callable):
        """注册特定节点类型的执行器"""
        self._executors[node_type] = executor

    def execute_node(self, node: PlanNode, context: Dict[str, Any] = None) -> Tuple[bool, Dict[str, Any]]:
        """
        执行单个节点。

        返回: (success, result_dict)
        """
        node.status = NodeStatus.RUNNING
        node.started_at = datetime.now().isoformat()

        try:
            executor = self._executors.get(node.node_type)
            if executor:
                result = executor(node, context or {})
            else:
                # 默认执行：记录状态
                result = {"status": "executed", "node_id": node.node_id, "description": node.description}

            node.outputs = result
            node.status = NodeStatus.COMPLETED
            node.completed_at = datetime.now().isoformat()
            logger.debug(f"[ExecutionAgent] 节点 {node.node_id} 执行成功")
            return True, result

        except Exception as e:
            node.error_info = {"error": str(e), "timestamp": datetime.now().isoformat()}
            node.status = NodeStatus.FAILED
            node.completed_at = datetime.now().isoformat()
            logger.warning(f"[ExecutionAgent] 节点 {node.node_id} 执行失败: {e}")
            return False, {"error": str(e)}

    def execute_tree(self, root: PlanNode, context: Dict[str, Any] = None,
                     on_node_complete: Callable = None) -> Dict[str, Any]:
        """
        执行完整计划树（深度优先，先序）。

        特性：
        - 子任务失败仅回滚该分支
        - 并行节点收集所有结果后判定
        - 置信度 < 0.5 的节点标记为不确定并记录
        """
        results = {
            "root_node_id": root.node_id,
            "started_at": datetime.now().isoformat(),
            "nodes_executed": 0,
            "nodes_succeeded": 0,
            "nodes_failed": 0,
            "nodes_rolled_back": 0,
            "uncertain_nodes": [],
            "errors": [],
        }

        def _execute_recursive(node: PlanNode) -> bool:
            # 依赖检查
            for dep_id in node.dependencies:
                dep_node = root.find_node(dep_id)
                if dep_node and dep_node.status != NodeStatus.COMPLETED:
                    node.status = NodeStatus.SKIPPED
                    results["errors"].append({
                        "node_id": node.node_id,
                        "reason": f"依赖节点 {dep_id} 未完成"
                    })
                    return False

            # 低置信度标记
            if node.confidence_score < 0.5:
                results["uncertain_nodes"].append({
                    "node_id": node.node_id,
                    "description": node.description,
                    "confidence": node.confidence_score,
                })

            # 执行
            success, output = self.execute_node(node, context)
            results["nodes_executed"] += 1

            if success:
                results["nodes_succeeded"] += 1
                if on_node_complete:
                    on_node_complete(node)
            else:
                results["nodes_failed"] += 1
                # 回滚该分支
                rollback_ids = root.get_rollback_scope(node.node_id)
                for rb_id in rollback_ids:
                    rb_node = root.find_node(rb_id)
                    if rb_node:
                        rb_node.status = NodeStatus.ROLLED_BACK
                results["nodes_rolled_back"] += len(rollback_ids)
                results["errors"].append({
                    "node_id": node.node_id,
                    "error": node.error_info,
                    "rollback_scope": rollback_ids,
                })
                return False  # 分支失败，不继续处理子节点

            # 递归处理子节点
            for child in node.children:
                _execute_recursive(child)

            return True

        _execute_recursive(root)

        results["completed_at"] = datetime.now().isoformat()
        results["overall_success"] = results["nodes_failed"] == 0
        logger.info(
            f"[ExecutionAgent] 计划树执行完成: "
            f"{results['nodes_succeeded']}/{results['nodes_executed']} 成功, "
            f"{results['nodes_failed']} 失败, {results['nodes_rolled_back']} 回滚"
        )
        return results

    def save_checkpoint(self, node_id: str, data: Dict[str, Any]):
        self._checkpoints[node_id] = {
            "data": data,
            "saved_at": datetime.now().isoformat(),
        }

    def restore_checkpoint(self, node_id: str) -> Optional[Dict[str, Any]]:
        cp = self._checkpoints.get(node_id)
        return cp["data"] if cp else None


# ============================================================
# CognitionLayer — 认知-执行分离顶层协调器
# ============================================================

class CognitionLayer:
    """
    认知-执行分离顶层协调器。

    完整管线：
    1. PlanningAgent.decompose() → 生成 PlanNode 树
    2. ExecutionAgent.execute_tree() → 确定性执行
    3. 失败自动回滚（分支级）
    4. 输出执行报告
    """

    def __init__(self, max_depth: int = 5):
        self.planner = PlanningAgent(max_depth=max_depth)
        self.executor = ExecutionAgent()
        self._execution_log: List[Dict[str, Any]] = []

    def process(self, intent: str, context: Dict[str, Any] = None,
                exec_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        完整认知-执行管线。

        参数:
            intent: 用户意图
            context: 规划上下文（偏好/约束）
            exec_context: 执行上下文（环境/工具）

        返回:
            {
              "plan_summary": ...,
              "execution_result": ...,
              "overall_success": bool,
            }
        """
        # Phase 1: 规划
        plan_tree = self.planner.decompose(intent, context)

        # Phase 2: 执行
        exec_result = self.executor.execute_tree(plan_tree, exec_context)

        # Phase 3: 记录
        log_entry = {
            "intent": intent,
            "plan_summary": plan_tree.to_summary(),
            "execution_result": exec_result,
            "timestamp": datetime.now().isoformat(),
        }
        self._execution_log.append(log_entry)

        return {
            "plan_summary": plan_tree.to_summary(),
            "execution_result": exec_result,
            "overall_success": exec_result["overall_success"],
            "plan_tree": plan_tree.to_dict(),
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "planner_plans_generated": len(self.planner.get_plan_history()),
            "recent_executions": len(self._execution_log),
            "last_execution": self._execution_log[-1] if self._execution_log else None,
        }
