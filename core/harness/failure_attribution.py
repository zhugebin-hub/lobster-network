#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.2 - 失败自动归因模块 (Who&When 风格)

基于 Who&When (ICML 2025 Spotlight) 方法论实现多维度失败归因。

核心能力：
- 多维度归因: 定位失败责任Agent和决定性错误步骤
- 归因维度: Agent选择 / 工具调用 / 参数传递 / 时序依赖 / 环境状态
- 归因报告 + 改进建议生成
- 集成到 Fault Tolerance 降级链路

参考：
- Who&When: 自动化失败归因 - ICML 2025 Spotlight (PSU, Duke, Google DeepMind)
- 智能体网络最新进展综述_2025-2026 - 3.1 论文矩阵
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("failure_attribution")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举定义
# ============================================================

class AttributionDimension(str, Enum):
    AGENT_SELECTION = "agent_selection"
    TOOL_CALL = "tool_call"
    PARAMETER_PASSING = "parameter_passing"
    TIMING_DEPENDENCY = "timing_dependency"
    ENVIRONMENT_STATE = "environment_state"
    CAPABILITY_MISMATCH = "capability_mismatch"
    COMMUNICATION_FAILURE = "communication_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    EXTERNAL_DEPENDENCY = "external_dependency"


class FailureType(str, Enum):
    EXECUTION_ERROR = "execution_error"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_LIMIT = "resource_limit"
    DATA_CORRUPTION = "data_corruption"
    CONFIG_ERROR = "config_error"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


class AttributionConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


# ============================================================
# 数据模型
# ============================================================

@dataclass
class FailureStep:
    """失败步骤 - 单步执行失败的完整记录"""
    step_id: str
    sequence_number: int
    agent_id: str
    operation: str
    tool_used: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_state: Dict[str, Any] = field(default_factory=dict)
    output_state: Dict[str, Any] = field(default_factory=dict)
    error_type: FailureType = FailureType.UNKNOWN
    error_message: str = ""
    stack_trace: Optional[str] = None
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    retry_count: int = 0
    upstream_deps: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttributionResult:
    """归因结果 - 定位到具体责任Agent和决定性错误步骤"""
    attribution_id: str
    responsible_agent: str
    decisive_step: str
    primary_dimension: AttributionDimension
    secondary_dimensions: List[AttributionDimension] = field(default_factory=list)
    confidence: AttributionConfidence = AttributionConfidence.MEDIUM
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    root_cause: str = ""
    impact_scope: str = ""
    suggested_fix: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "attribution_id": self.attribution_id,
            "responsible_agent": self.responsible_agent,
            "decisive_step": self.decisive_step,
            "primary_dimension": self.primary_dimension.value,
            "secondary_dimensions": [d.value for d in self.secondary_dimensions],
            "confidence": self.confidence.value,
            "evidence": self.evidence,
            "root_cause": self.root_cause,
            "impact_scope": self.impact_scope,
            "suggested_fix": self.suggested_fix,
            "timestamp": self.timestamp,
        }


@dataclass
class AttributionReport:
    """归因报告"""
    report_id: str
    session_id: str
    total_steps: int
    failed_steps: int
    attributed_count: int
    attributions: List[AttributionResult]
    summary: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "session_id": self.session_id,
            "total_steps": self.total_steps,
            "failed_steps": self.failed_steps,
            "attributed_count": self.attributed_count,
            "attributions": [a.to_dict() for a in self.attributions],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "generated_at": self.generated_at,
        }


# ============================================================
# FailureAnalyzer - 失败分析器
# ============================================================

class FailureAnalyzer:
    """
    失败分析器 - 从原始错误信息中提取归因线索。

    按五大维度分析失败步骤：
    1. Agent选择: 是否选对Agent处理该任务
    2. 工具调用: 工具是否可用、参数是否正确
    3. 参数传递: 上下游参数传递是否一致
    4. 时序依赖: 依赖步骤是否正常完成
    5. 环境状态: 运行时环境是否健康
    """

    ERROR_PATTERNS = {
        AttributionDimension.AGENT_SELECTION: [
            "not authorized", "permission denied", "insufficient capability",
            "wrong agent", "agent mismatch", "not trained for",
        ],
        AttributionDimension.TOOL_CALL: [
            "tool not found", "command not found", "invalid tool",
            "tool timeout", "tool crashed", "api error",
        ],
        AttributionDimension.PARAMETER_PASSING: [
            "missing argument", "invalid parameter", "type error",
            "wrong type", "argument error", "unexpected keyword",
            "key error", "attribute error",
        ],
        AttributionDimension.TIMING_DEPENDENCY: [
            "not ready", "dependency failed", "prerequisite not met",
            "waiting for", "deadlock", "race condition",
            "upstream task", "previous step",
        ],
        AttributionDimension.ENVIRONMENT_STATE: [
            "out of memory", "disk full", "connection refused",
            "network unreachable", "host not found", "resource exhausted",
            "file not found", "no space left",
        ],
        AttributionDimension.CAPABILITY_MISMATCH: [
            "not implemented", "unsupported", "capability missing",
            "no such method", "model not loaded",
        ],
        AttributionDimension.COMMUNICATION_FAILURE: [
            "timeout", "connection error", "message lost",
            "broadcast failed", "unreachable",
        ],
        AttributionDimension.RESOURCE_EXHAUSTION: [
            "rate limit", "quota exceeded", "token limit",
            "too many requests", "throttled",
        ],
        AttributionDimension.EXTERNAL_DEPENDENCY: [
            "api unavailable", "service down", "external error",
            "third party", "provider error",
        ],
    }

    def analyze(self, failed_steps: List[FailureStep],
                all_steps: List[FailureStep] = None) -> List[AttributionResult]:
        """分析失败步骤并生成归因结果"""
        all_steps = all_steps or failed_steps
        results = []

        for step in failed_steps:
            primary_dim, confidence = self._classify_by_error_patterns(step)
            secondary = self._find_secondary_dimensions(step, all_steps)

            decisive_step = step.step_id
            if primary_dim == AttributionDimension.TIMING_DEPENDENCY and step.upstream_deps:
                decisive_step = step.upstream_deps[-1]

            responsible = step.agent_id
            evidence = self._gather_evidence(step, primary_dim, all_steps)
            root_cause = self._describe_root_cause(step, primary_dim)
            impact = self._assess_impact(step, all_steps)
            fix = self._suggest_fix(step, primary_dim)

            result = AttributionResult(
                attribution_id=f"attr_{step.step_id}_{int(datetime.now().timestamp())}",
                responsible_agent=responsible,
                decisive_step=decisive_step,
                primary_dimension=primary_dim,
                secondary_dimensions=secondary,
                confidence=confidence,
                evidence=evidence,
                root_cause=root_cause,
                impact_scope=impact,
                suggested_fix=fix,
            )
            results.append(result)

        return results

    def _classify_by_error_patterns(self, step: FailureStep) -> Tuple[AttributionDimension, AttributionConfidence]:
        """基于错误关键词分类"""
        error_lower = step.error_message.lower()
        scores: Dict[AttributionDimension, int] = {}

        for dim, patterns in self.ERROR_PATTERNS.items():
            match_count = sum(1 for p in patterns if p.lower() in error_lower)
            if match_count > 0:
                scores[dim] = match_count

        if not scores:
            return AttributionDimension.PARAMETER_PASSING, AttributionConfidence.LOW

        best_dim = max(scores, key=scores.get)
        max_matches = scores[best_dim]

        if max_matches >= 3:
            conf = AttributionConfidence.HIGH
        elif max_matches >= 2:
            conf = AttributionConfidence.MEDIUM
        else:
            conf = AttributionConfidence.LOW

        return best_dim, conf

    def _find_secondary_dimensions(self, step: FailureStep,
                                    all_steps: List[FailureStep]) -> List[AttributionDimension]:
        """查找次要归因维度"""
        secondary = []

        # 检查参数传递链
        if step.parameters:
            for other in all_steps:
                if other.step_id != step.step_id and other.agent_id != step.agent_id:
                    if other.parameters and step.parameters == other.parameters:
                        secondary.append(AttributionDimension.PARAMETER_PASSING)
                        break

        # 检查环境状态线索
        env_hints = ["memory", "disk", "network", "connection", "timeout"]
        if any(h in step.error_message.lower() for h in env_hints):
            if AttributionDimension.ENVIRONMENT_STATE not in secondary:
                secondary.append(AttributionDimension.ENVIRONMENT_STATE)

        # 检查重试次数过多
        if step.retry_count >= 3:
            secondary.append(AttributionDimension.RESOURCE_EXHAUSTION)

        # 运行时长过长
        if step.duration_ms > 30000:
            secondary.append(AttributionDimension.TIMING_DEPENDENCY)

        return secondary[:3]

    def _gather_evidence(self, step: FailureStep, primary_dim: AttributionDimension,
                         all_steps: List[FailureStep]) -> List[Dict[str, Any]]:
        """收集证据链"""
        evidence = []
        evidence.append({
            "type": "error_context",
            "step_id": step.step_id,
            "agent": step.agent_id,
            "operation": step.operation,
            "error": step.error_message[:200],
        })

        # 相关上游步骤
        for other in all_steps:
            if other.step_id in step.upstream_deps:
                evidence.append({
                    "type": "upstream_step",
                    "step_id": other.step_id,
                    "agent": other.agent_id,
                    "status": "failed" if other.error_message else "success",
                })

        # 工具信息
        if step.tool_used:
            evidence.append({
                "type": "tool_usage",
                "tool": step.tool_used,
                "parameters_keys": list(step.parameters.keys())[:10] if step.parameters else [],
            })

        return evidence

    def _describe_root_cause(self, step: FailureStep,
                              primary_dim: AttributionDimension) -> str:
        """描述根因"""
        templates = {
            AttributionDimension.AGENT_SELECTION:
                f"Agent '{step.agent_id}' 被选中的能力与操作 '{step.operation}' 所需能力不匹配",
            AttributionDimension.TOOL_CALL:
                f"工具 '{step.tool_used or 'unknown'}' 在操作 '{step.operation}' 中调用失败",
            AttributionDimension.PARAMETER_PASSING:
                f"操作 '{step.operation}' 的参数传递存在类型或值错误",
            AttributionDimension.TIMING_DEPENDENCY:
                f"操作 '{step.operation}' 的上游依赖未能按时完成",
            AttributionDimension.ENVIRONMENT_STATE:
                f"运行时环境状态异常导致操作 '{step.operation}' 失败",
            AttributionDimension.CAPABILITY_MISMATCH:
                f"Agent '{step.agent_id}' 缺少执行 '{step.operation}' 的必要能力",
            AttributionDimension.COMMUNICATION_FAILURE:
                f"Agent间通信失败影响操作 '{step.operation}'",
            AttributionDimension.RESOURCE_EXHAUSTION:
                f"资源配额耗尽导致操作 '{step.operation}' 无法完成",
            AttributionDimension.EXTERNAL_DEPENDENCY:
                f"外部服务不可用导致操作 '{step.operation}' 失败",
        }
        return templates.get(primary_dim, f"操作 '{step.operation}' 执行失败: {step.error_message[:100]}")

    def _assess_impact(self, step: FailureStep,
                       all_steps: List[FailureStep]) -> str:
        """评估影响范围"""
        downstream = [s for s in all_steps if step.step_id in s.upstream_deps]
        if len(downstream) >= 3:
            return f"高影响: 导致 {len(downstream)} 个下游步骤受阻"
        elif downstream:
            return f"中影响: {len(downstream)} 个下游步骤受影响"
        return "低影响: 无下游依赖"

    def _suggest_fix(self, step: FailureStep,
                     primary_dim: AttributionDimension) -> str:
        """生成修复建议"""
        suggestions = {
            AttributionDimension.AGENT_SELECTION:
                f"建议将 '{step.operation}' 重新分配给具备匹配能力的Agent",
            AttributionDimension.TOOL_CALL:
                f"检查工具 '{step.tool_used}' 的可用性并验证参数格式",
            AttributionDimension.PARAMETER_PASSING:
                "对输入参数增加类型校验和前置断言",
            AttributionDimension.TIMING_DEPENDENCY:
                "增加上游步骤超时检测，失败时启用备选路径",
            AttributionDimension.ENVIRONMENT_STATE:
                "触发健康检查并尝试环境自愈恢复",
            AttributionDimension.CAPABILITY_MISMATCH:
                f"为Agent '{step.agent_id}' 注册必要能力或选择替代Agent",
            AttributionDimension.COMMUNICATION_FAILURE:
                "启用A2A协议重试机制并检查消息队列状态",
            AttributionDimension.RESOURCE_EXHAUSTION:
                "降低并发度并启用速率限制器",
            AttributionDimension.EXTERNAL_DEPENDENCY:
                "启用外部服务降级策略或本地缓存兜底",
        }
        return suggestions.get(primary_dim, "人工排查具体错误并制定修复方案")


# ============================================================
# FailureAttribution - 顶层协调器
# ============================================================

class FailureAttribution:
    """
    失败自动归因顶层协调器。

    完整管线：
    1. 收集失败步骤
    2. FailureAnalyzer 多维度归因分析
    3. 生成 AttributionReport
    4. 上报到 Fault Tolerance 降级链路
    """

    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.analyzer = FailureAnalyzer()
        self._all_steps: List[FailureStep] = []
        self._failed_steps: List[FailureStep] = []
        self._attribution_history: List[AttributionReport] = []
        logger.info(f"[FailureAttribution] 失败归因模块已初始化, session={self.session_id}")

    def record_step(self, step: FailureStep):
        """记录执行步骤"""
        self._all_steps.append(step)
        if step.error_message:
            self._failed_steps.append(step)

    def record_execution(self, agent_id: str, step_id: str, operation: str,
                         success: bool, error_message: str = "",
                         tool_used: str = None, parameters: Dict = None,
                         duration_ms: float = 0.0, upstream_deps: List[str] = None):
        """便捷记录执行结果"""
        step = FailureStep(
            step_id=step_id,
            sequence_number=len(self._all_steps) + 1,
            agent_id=agent_id,
            operation=operation,
            tool_used=tool_used,
            parameters=parameters or {},
            error_message=error_message,
            error_type=FailureType.EXECUTION_ERROR if error_message else FailureType.UNKNOWN,
            upstream_deps=upstream_deps or [],
            duration_ms=duration_ms,
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
        )
        self.record_step(step)
        return step

    def attribute(self) -> AttributionReport:
        """执行归因分析并生成报告"""
        if not self._failed_steps:
            report = AttributionReport(
                report_id=f"report_{self.session_id}_{int(datetime.now().timestamp())}",
                session_id=self.session_id,
                total_steps=len(self._all_steps),
                failed_steps=0,
                attributed_count=0,
                attributions=[],
                summary={"status": "all_passed", "message": "无失败步骤"},
                recommendations=["继续保持当前执行模式"],
            )
            self._attribution_history.append(report)
            return report

        # 归因分析
        attributions = self.analyzer.analyze(self._failed_steps, self._all_steps)

        # 统计
        dim_counts: Dict[str, int] = {}
        agent_failures: Dict[str, int] = {}
        for attr in attributions:
            dim_counts[attr.primary_dimension.value] = dim_counts.get(attr.primary_dimension.value, 0) + 1
            agent_failures[attr.responsible_agent] = agent_failures.get(attr.responsible_agent, 0) + 1

        # 生成建议
        recommendations = self._generate_recommendations(attributions, agent_failures)

        report = AttributionReport(
            report_id=f"report_{self.session_id}_{int(datetime.now().timestamp())}",
            session_id=self.session_id,
            total_steps=len(self._all_steps),
            failed_steps=len(self._failed_steps),
            attributed_count=len(attributions),
            attributions=attributions,
            summary={
                "dimension_distribution": dim_counts,
                "agent_failure_distribution": agent_failures,
                "avg_confidence": sum(
                    1.0 if a.confidence == AttributionConfidence.HIGH else
                    0.7 if a.confidence == AttributionConfidence.MEDIUM else 0.4
                    for a in attributions
                ) / max(len(attributions), 1),
            },
            recommendations=recommendations,
        )
        self._attribution_history.append(report)
        logger.info(
            f"[FailureAttribution] 归因完成: {len(attributions)} 个失败步骤已归因, "
            f"主要维度={max(dim_counts, key=dim_counts.get) if dim_counts else 'N/A'}"
        )
        return report

    def _generate_recommendations(self, attributions: List[AttributionResult],
                                   agent_failures: Dict[str, int]) -> List[str]:
        """生成系统级改进建议"""
        recs = []
        for attr in attributions:
            if attr.suggested_fix not in recs:
                recs.append(attr.suggested_fix)

        # 高频失败 Agent
        worst_agent = max(agent_failures, key=agent_failures.get) if agent_failures else None
        if worst_agent and agent_failures[worst_agent] >= 3:
            recs.append(f"Agent '{worst_agent}' 失败次数过高 ({agent_failures[worst_agent]}次), 建议进行能力审计或临时降级")

        # 整体失败率
        total = len(self._all_steps)
        failed = len(self._failed_steps)
        if total > 0 and failed / total > 0.3:
            recs.append(f"整体失败率 {failed/total:.0%} 偏高, 建议暂停并排查系统性问题")

        return list(set(recs))

    def get_status(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "total_steps": len(self._all_steps),
            "failed_steps": len(self._failed_steps),
            "failure_rate": round(
                len(self._failed_steps) / max(len(self._all_steps), 1), 3
            ),
            "reports_generated": len(self._attribution_history),
            "last_report": self._attribution_history[-1].to_dict() if self._attribution_history else None,
        }

    def reset(self, new_session_id: str = None):
        """重置会话"""
        self.session_id = new_session_id or str(uuid.uuid4())
        self._all_steps.clear()
        self._failed_steps.clear()
        logger.info(f"[FailureAttribution] 会话已重置: {self.session_id}")
