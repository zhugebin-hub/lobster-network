#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 验证器 (MCP Validator) - 小龙虾网络 V3.1
对接 MCP 工具链，实现训练中实时验证

功能:
- 训练时实时调用 validation_gate
- 事中纠正而非事后评估
- 验证结果反馈到训练管线
- 验证规则可配置
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    SKIP = "skip"


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    description: str = ""
    check_fn: Optional[Callable] = None       # 自定义检查函数
    min_score: float = 0.0                     # 最低分数
    required_fields: List[str] = field(default_factory=list)
    weight: float = 1.0                        # 权重
    enabled: bool = True

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "min_score": self.min_score,
            "required_fields": self.required_fields,
            "weight": self.weight,
            "enabled": self.enabled,
        }


@dataclass
class ValidationReport:
    """验证报告"""
    rule_name: str
    result: ValidationResult
    score: float = 0.0
    message: str = ""
    suggestions: List[str] = field(default_factory=list)
    duration_ms: float = 0.0
    checked_at: str = ""

    def __post_init__(self):
        if not self.checked_at:
            self.checked_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "rule_name": self.rule_name,
            "result": self.result.value,
            "score": round(self.score, 2),
            "message": self.message,
            "suggestions": self.suggestions,
            "duration_ms": round(self.duration_ms, 1),
            "checked_at": self.checked_at,
        }


@dataclass
class BatchValidationResult:
    """批量验证结果"""
    overall: ValidationResult = ValidationResult.PASS
    total_rules: int = 0
    passed: int = 0
    failed: int = 0
    warned: int = 0
    reports: List[ValidationReport] = field(default_factory=list)
    total_score: float = 0.0
    weighted_score: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "overall": self.overall.value,
            "total_rules": self.total_rules,
            "passed": self.passed,
            "failed": self.failed,
            "warned": self.warned,
            "total_score": round(self.total_score, 2),
            "weighted_score": round(self.weighted_score, 2),
            "reports": [r.to_dict() for r in self.reports],
        }


# ========== 内置验证规则 ==========

def _check_format(data: Dict, rule: ValidationRule) -> ValidationReport:
    """格式检查：验证必需字段"""
    start = time.time()
    missing = [f for f in rule.required_fields if f not in data]
    duration = (time.time() - start) * 1000

    if missing:
        return ValidationReport(
            rule_name=rule.name,
            result=ValidationResult.FAIL,
            score=0.0,
            message=f"缺少必需字段: {', '.join(missing)}",
            suggestions=[f"请补充字段: {f}" for f in missing],
            duration_ms=duration,
        )
    return ValidationReport(
        rule_name=rule.name,
        result=ValidationResult.PASS,
        score=1.0,
        message="格式检查通过",
        duration_ms=duration,
    )


def _check_score_threshold(data: Dict, rule: ValidationRule) -> ValidationReport:
    """分数阈值检查"""
    start = time.time()
    score = data.get("score", data.get("accuracy", data.get("correct_rate", 0)))
    duration = (time.time() - start) * 1000

    if isinstance(score, (int, float)):
        if score >= rule.min_score:
            return ValidationReport(
                rule_name=rule.name,
                result=ValidationResult.PASS,
                score=score,
                message=f"得分 {score} >= 阈值 {rule.min_score}",
                duration_ms=duration,
            )
        elif score >= rule.min_score * 0.7:
            return ValidationReport(
                rule_name=rule.name,
                result=ValidationResult.WARN,
                score=score,
                message=f"得分 {score} 接近阈值 {rule.min_score}",
                suggestions=["建议复习相关知识点"],
                duration_ms=duration,
            )
        else:
            return ValidationReport(
                rule_name=rule.name,
                result=ValidationResult.FAIL,
                score=score,
                message=f"得分 {score} < 阈值 {rule.min_score}",
                suggestions=["需要重点复习", "建议重新训练"],
                duration_ms=duration,
            )
    return ValidationReport(
        rule_name=rule.name,
        result=ValidationResult.SKIP,
        message="未找到分数字段",
        duration_ms=duration,
    )


def _check_completeness(data: Dict, rule: ValidationRule) -> ValidationReport:
    """完整性检查：训练数据是否完整"""
    start = time.time()
    issues = []

    # 检查训练记录基本结构
    if "questions" in data:
        q_list = data["questions"]
        if len(q_list) == 0:
            issues.append("题目列表为空")
        else:
            for i, q in enumerate(q_list):
                if not q.get("question") and not q.get("title"):
                    issues.append(f"第 {i+1} 题缺少题目内容")
                if "answer" not in q and "options" not in q:
                    issues.append(f"第 {i+1} 题缺少答案/选项")

    duration = (time.time() - start) * 1000

    if issues:
        return ValidationReport(
            rule_name=rule.name,
            result=ValidationResult.WARN,
            score=max(0, 1.0 - len(issues) * 0.1),
            message=f"发现 {len(issues)} 个完整性问题",
            suggestions=issues[:5],
            duration_ms=duration,
        )
    return ValidationReport(
        rule_name=rule.name,
        result=ValidationResult.PASS,
        score=1.0,
        message="完整性检查通过",
        duration_ms=duration,
    )


# ========== 默认规则集 ==========

DEFAULT_RULES: Dict[str, ValidationRule] = {
    "format_check": ValidationRule(
        name="format_check",
        description="格式检查：验证必需字段",
        check_fn=_check_format,
        required_fields=["questions", "student_id", "module"],
        weight=1.5,
    ),
    "score_threshold": ValidationRule(
        name="score_threshold",
        description="分数阈值检查",
        check_fn=_check_score_threshold,
        min_score=0.6,
        weight=2.0,
    ),
    "completeness": ValidationRule(
        name="completeness",
        description="完整性检查",
        check_fn=_check_completeness,
        weight=1.0,
    ),
}


class MCPValidator:
    """MCP 验证器"""

    def __init__(self, name: str = "default", rules: Optional[Dict[str, ValidationRule]] = None):
        self.name = name
        self.rules = rules or dict(DEFAULT_RULES)
        self._history: List[BatchValidationResult] = []
        logger.info(f"[MCP验证器:{self.name}] 初始化, 规则数: {len(self.rules)}")

    def add_rule(self, rule: ValidationRule):
        """添加验证规则"""
        self.rules[rule.name] = rule
        logger.info(f"[MCP验证器:{self.name}] 添加规则: {rule.name}")

    def remove_rule(self, name: str):
        """移除验证规则"""
        if name in self.rules:
            del self.rules[name]

    def validate(self, data: Dict, rule_names: Optional[List[str]] = None) -> BatchValidationResult:
        """执行验证"""
        target_rules = rule_names or list(self.rules.keys())
        result = BatchValidationResult()
        total_weight = 0.0
        weighted_sum = 0.0

        for name in target_rules:
            rule = self.rules.get(name)
            if not rule or not rule.enabled:
                continue

            start = time.time()

            if rule.check_fn:
                try:
                    report = rule.check_fn(data, rule)
                except Exception as e:
                    report = ValidationReport(
                        rule_name=name,
                        result=ValidationResult.SKIP,
                        message=f"验证异常: {e}",
                        duration_ms=(time.time() - start) * 1000,
                    )
            else:
                report = ValidationReport(
                    rule_name=name,
                    result=ValidationResult.SKIP,
                    message="无检查函数",
                )

            result.reports.append(report)
            result.total_rules += 1

            if report.result == ValidationResult.PASS:
                result.passed += 1
            elif report.result == ValidationResult.FAIL:
                result.failed += 1
            elif report.result == ValidationResult.WARN:
                result.warned += 1

            total_weight += rule.weight
            weighted_sum += report.score * rule.weight

        # 计算总分
        result.total_rules = len(result.reports)
        result.total_score = sum(r.score for r in result.reports) / len(result.reports) if result.reports else 0
        result.weighted_score = weighted_sum / total_weight if total_weight > 0 else 0

        # 判定总体结果
        if result.failed > 0:
            result.overall = ValidationResult.FAIL
        elif result.warned > 0:
            result.overall = ValidationResult.WARN
        else:
            result.overall = ValidationResult.PASS

        self._history.append(result)
        return result

    def get_history(self, count: int = 10) -> List[Dict]:
        """获取验证历史"""
        return [r.to_dict() for r in self._history[-count:]]

    def get_stats(self) -> Dict:
        """获取统计"""
        if not self._history:
            return {"total_validations": 0}
        total = len(self._history)
        passed = sum(1 for r in self._history if r.overall == ValidationResult.PASS)
        return {
            "total_validations": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1),
            "avg_score": round(sum(r.total_score for r in self._history) / total, 2),
            "rules": {k: v.to_dict() for k, v in self.rules.items()},
        }


# ========== 预定义验证器 ==========

# 训练结果验证器
training_validator = MCPValidator("training")

# 代码质量验证器
code_validator = MCPValidator("code", rules={
    "format_check": ValidationRule(
        name="format_check",
        description="代码格式检查",
        required_fields=["code", "language", "file_path"],
        weight=1.5,
    ),
    "completeness": ValidationRule(
        name="completeness",
        description="代码完整性检查",
        weight=1.0,
    ),
})

# 论文验证器
paper_validator = MCPValidator("paper", rules={
    "format_check": ValidationRule(
        name="format_check",
        description="论文格式检查",
        required_fields=["title", "abstract", "content", "references"],
        weight=2.0,
    ),
    "completeness": ValidationRule(
        name="completeness",
        description="论文完整性检查",
        weight=1.5,
    ),
    "score_threshold": ValidationRule(
        name="score_threshold",
        description="学术质量阈值",
        check_fn=_check_score_threshold,
        min_score=0.7,
        weight=2.0,
    ),
})


def validate_training(data: Dict) -> BatchValidationResult:
    """验证训练结果（便捷函数）"""
    return training_validator.validate(data)


def validate_code(data: Dict) -> BatchValidationResult:
    """验证代码质量（便捷函数）"""
    return code_validator.validate(data)
