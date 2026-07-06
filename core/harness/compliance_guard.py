#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.2 — 安全合规层 (EU AI Act + CuP)

企业安全策略过滤 + 操作审计日志 + 风险分级过滤 + 合规报告生成。

核心能力：
- 企业安全策略过滤（参考IBM CuP指标准则）
- 操作审计日志 (Audit Trail): 谁/何时/做了什么/决策依据
- 风险分级过滤: 高风险操作(金融/法律/医疗)需人工确认
- 合规报告生成器: 输出审计报告JSON

参考：
- IBM CuP 指标 — 企业安全策略过滤
- EU AI Act 2026.8 全面实施要求
- 智能体网络最新进展综述_2025-2026 — 6.4 安全与治理
"""

import json
import uuid
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("compliance_guard")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举定义
# ============================================================

class RiskCategory(str, Enum):
    """EU AI Act 风险分类"""
    MINIMAL = "minimal"
    LIMITED = "limited"
    HIGH = "high"
    UNACCEPTABLE = "unacceptable"


class OperationCategory(str, Enum):
    """操作类别"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    CONFIGURE = "configure"
    FINANCIAL = "financial"
    LEGAL = "legal"
    MEDICAL = "medical"
    PII_ACCESS = "pii_access"


class ComplianceStatus(str, Enum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"
    FLAGGED = "flagged"


# ============================================================
# 数据模型
# ============================================================

@dataclass
class AuditEntry:
    """单条审计日志"""
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    actor: str = ""                              # 谁（agent/node/user）
    operation: str = ""                          # 做了什么
    resource: str = ""                           # 操作对象
    decision_basis: str = ""                     # 决策依据
    risk_category: RiskCategory = RiskCategory.MINIMAL
    compliance_status: ComplianceStatus = ComplianceStatus.ALLOWED
    result: str = ""                             # 结果
    metadata: Dict[str, Any] = field(default_factory=dict)
    signature: str = ""                          # 防篡改签名

    def compute_signature(self, secret: str = "lobster-compliance"):
        """计算防篡改哈希签名"""
        payload = f"{self.entry_id}|{self.timestamp}|{self.actor}|{self.operation}|{self.resource}|{self.decision_basis}"
        self.signature = hashlib.sha256(
            (payload + secret).encode("utf-8")
        ).hexdigest()[:16]

    def verify(self, secret: str = "lobster-compliance") -> bool:
        expected = hashlib.sha256(
            (f"{self.entry_id}|{self.timestamp}|{self.actor}|{self.operation}|{self.resource}|{self.decision_basis}" + secret).encode("utf-8")
        ).hexdigest()[:16]
        return self.signature == expected

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "operation": self.operation,
            "resource": self.resource,
            "decision_basis": self.decision_basis,
            "risk_category": self.risk_category.value,
            "compliance_status": self.compliance_status.value,
            "result": self.result,
            "metadata": self.metadata,
            "signature": self.signature,
        }


@dataclass
class ComplianceReport:
    """合规报告"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    period_start: str = ""
    period_end: str = ""
    total_operations: int = 0
    blocked_operations: int = 0
    reviewed_operations: int = 0
    flagged_operations: int = 0
    risk_distribution: Dict[str, int] = field(default_factory=dict)
    category_distribution: Dict[str, int] = field(default_factory=dict)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    eu_ai_act_compliance_score: float = 0.0   # 0~100
    cup_score: float = 0.0                     # CuP 指标 0~100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at,
            "period_start": self.period_start,
            "period_end": self.period_end,
            "total_operations": self.total_operations,
            "blocked_operations": self.blocked_operations,
            "reviewed_operations": self.reviewed_operations,
            "flagged_operations": self.flagged_operations,
            "risk_distribution": self.risk_distribution,
            "category_distribution": self.category_distribution,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "eu_ai_act_compliance_score": self.eu_ai_act_compliance_score,
            "cup_score": self.cup_score,
        }


# ============================================================
# 企业安全策略 — IBM CuP 指标
# ============================================================

class EnterpriseSecurityPolicy:
    """
    企业安全策略过滤（参考 IBM CuP 指标准则）。

    CuP 核心发现：顶尖 Web Agent 任务成功率 90%+，
    但满足企业安全策略后仅 ~62%；38% 成功率通过违规操作实现。
    """

    # CuP 策略规则库
    DEFAULT_RULES = {
        "financial_transaction": {
            "risk": RiskCategory.HIGH,
            "require_review": True,
            "max_amount_lbc": 50.0,
            "allowed_actors": ["qoder", "hermes"],
        },
        "legal_document": {
            "risk": RiskCategory.HIGH,
            "require_review": True,
            "allowed_actors": ["qoder"],
            "require_legal_disclaimer": True,
        },
        "medical_advice": {
            "risk": RiskCategory.UNACCEPTABLE,
            "require_review": True,
            "require_human_override": True,
            "allowed_actors": [],
        },
        "pii_access": {
            "risk": RiskCategory.HIGH,
            "require_review": True,
            "require_audit_log": True,
            "data_retention_hours": 24,
        },
        "system_config_change": {
            "risk": RiskCategory.LIMITED,
            "require_review": False,
            "allowed_actors": ["qoder", "hermes"],
        },
        "external_api_call": {
            "risk": RiskCategory.LIMITED,
            "require_review": False,
            "allowed_domains": [
                "api.openai.com", "api.anthropic.com",
                "generativelanguage.googleapis.com",
            ],
        },
        "bulk_delete": {
            "risk": RiskCategory.HIGH,
            "require_review": True,
            "max_files": 50,
            "allowed_actors": ["qoder"],
        },
        "code_execution": {
            "risk": RiskCategory.LIMITED,
            "require_review": False,
            "sandbox_required": True,
            "max_runtime_sec": 300,
        },
    }

    def __init__(self, custom_rules: Dict[str, Any] = None):
        self.rules = {**self.DEFAULT_RULES, **(custom_rules or {})}

    def evaluate(self, operation: OperationCategory, actor: str,
                 resource: str = "", context: Dict[str, Any] = None) -> Tuple[ComplianceStatus, str]:
        """
        评估操作合规性。

        返回: (ComplianceStatus, decision_basis)
        """
        context = context or {}
        rule_key = self._map_operation_to_rule(operation)

        if rule_key not in self.rules:
            return ComplianceStatus.ALLOWED, "无匹配规则，默认允许"

        rule = self.rules[rule_key]

        # 不可接受风险 → 直接阻塞
        if rule["risk"] == RiskCategory.UNACCEPTABLE:
            return ComplianceStatus.BLOCKED, (
                f"操作 '{operation.value}' 属于不可接受风险 (EU AI Act)，已阻塞"
            )

        # 检查执行者白名单
        allowed_actors = rule.get("allowed_actors", [])
        if allowed_actors and actor not in allowed_actors:
            return ComplianceStatus.BLOCKED, (
                f"执行者 '{actor}' 不在白名单 {allowed_actors} 中"
            )

        # 高风险操作 → 需人工审核
        if rule.get("require_review", False):
            return ComplianceStatus.NEEDS_REVIEW, (
                f"操作 '{operation.value}' 风险等级={rule['risk'].value}，需人工审核"
            )

        # 限定域检查
        if "allowed_domains" in rule:
            domain = context.get("domain", "")
            if domain and domain not in rule["allowed_domains"]:
                return ComplianceStatus.BLOCKED, f"域名 '{domain}' 不在允许列表中"

        # 金额限制
        if "max_amount_lbc" in rule:
            amount = context.get("amount", 0)
            if amount > rule["max_amount_lbc"]:
                return ComplianceStatus.NEEDS_REVIEW, (
                    f"金额 {amount} LBC 超过上限 {rule['max_amount_lbc']} LBC"
                )

        # 批量操作限制
        if "max_files" in rule:
            file_count = context.get("file_count", 0)
            if file_count > rule["max_files"]:
                return ComplianceStatus.NEEDS_REVIEW, (
                    f"文件数 {file_count} 超过上限 {rule['max_files']}"
                )

        return ComplianceStatus.ALLOWED, f"通过 CuP 策略检查（{rule_key}）"

    def _map_operation_to_rule(self, op: OperationCategory) -> str:
        mapping = {
            OperationCategory.FINANCIAL: "financial_transaction",
            OperationCategory.LEGAL: "legal_document",
            OperationCategory.MEDICAL: "medical_advice",
            OperationCategory.PII_ACCESS: "pii_access",
            OperationCategory.CONFIGURE: "system_config_change",
            OperationCategory.EXECUTE: "code_execution",
            OperationCategory.DELETE: "bulk_delete",
        }
        return mapping.get(op, "external_api_call")


# ============================================================
# AuditTrail — 操作审计日志
# ============================================================

class AuditTrail:
    """
    操作审计日志 — 谁/何时/做了什么/决策依据。

    特性：
    - 防篡改签名
    - 按时间/操作者/风险等级查询
    - 定期归档
    """

    def __init__(self, log_dir: Optional[Path] = None, max_entries: int = 50000):
        self._entries: List[AuditEntry] = []
        self._max_entries = max_entries
        self._log_dir = log_dir or Path(__file__).resolve().parent / "logs"
        self._log_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[AuditTrail] 审计日志已初始化，目录={self._log_dir}")

    def record(self, actor: str, operation: str, resource: str,
               decision_basis: str, risk_category: RiskCategory,
               compliance_status: ComplianceStatus, result: str = "",
               metadata: Dict[str, Any] = None) -> AuditEntry:
        """记录一条审计日志"""
        entry = AuditEntry(
            actor=actor,
            operation=operation,
            resource=resource,
            decision_basis=decision_basis,
            risk_category=risk_category,
            compliance_status=compliance_status,
            result=result,
            metadata=metadata or {},
        )
        entry.compute_signature()
        self._entries.append(entry)

        # FIFO 淘汰
        if len(self._entries) > self._max_entries:
            self.archive()

        logger.debug(f"[AuditTrail] {actor} | {operation} | {resource} | {compliance_status.value}")
        return entry

    def query(self, actor: str = None, operation: str = None,
              risk_category: RiskCategory = None,
              status: ComplianceStatus = None,
              time_start: str = None, time_end: str = None,
              limit: int = 100) -> List[AuditEntry]:
        """多维度查询审计日志"""
        results = self._entries

        if actor:
            results = [e for e in results if e.actor == actor]
        if operation:
            results = [e for e in results if operation.lower() in e.operation.lower()]
        if risk_category:
            results = [e for e in results if e.risk_category == risk_category]
        if status:
            results = [e for e in results if e.compliance_status == status]
        if time_start:
            results = [e for e in results if e.timestamp >= time_start]
        if time_end:
            results = [e for e in results if e.timestamp <= time_end]

        return results[-limit:]

    def get_violations(self) -> List[AuditEntry]:
        """获取所有违规记录"""
        return [
            e for e in self._entries
            if e.compliance_status in (ComplianceStatus.BLOCKED, ComplianceStatus.FLAGGED)
        ]

    def archive(self):
        """归档旧日志到磁盘"""
        if len(self._entries) <= self._max_entries:
            return
        overflow = len(self._entries) - self._max_entries
        archive_entries = self._entries[:overflow]
        self._entries = self._entries[overflow:]

        archive_path = self._log_dir / f"audit_archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        with open(archive_path, "w", encoding="utf-8") as f:
            for entry in archive_entries:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        logger.info(f"[AuditTrail] 已归档 {len(archive_entries)} 条审计日志 → {archive_path}")

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._entries)
        return {
            "total_entries": total,
            "violations": len(self.get_violations()),
            "blocked_pct": round(
                sum(1 for e in self._entries if e.compliance_status == ComplianceStatus.BLOCKED) / max(total, 1) * 100, 2
            ),
            "needs_review_pct": round(
                sum(1 for e in self._entries if e.compliance_status == ComplianceStatus.NEEDS_REVIEW) / max(total, 1) * 100, 2
            ),
        }


# ============================================================
# RiskClassifier — 风险分级过滤
# ============================================================

class RiskClassifier:
    """
    风险分级过滤器。

    三级分类：
    - 高风险 (HIGH/UNACCEPTABLE): 金融/法律/医疗 → 强制人工确认
    - 受限风险 (LIMITED): 配置变更/代码执行 → 需审批
    - 最小风险 (MINIMAL): 只读/搜索 → 自动放行
    """

    # 操作→风险映射表
    RISK_MAP = {
        "financial": RiskCategory.HIGH,
        "legal": RiskCategory.HIGH,
        "medical": RiskCategory.UNACCEPTABLE,
        "pii": RiskCategory.HIGH,
        "delete_bulk": RiskCategory.HIGH,
        "configure_system": RiskCategory.LIMITED,
        "code_execution": RiskCategory.LIMITED,
        "api_external": RiskCategory.LIMITED,
        "file_write": RiskCategory.LIMITED,
        "file_read": RiskCategory.MINIMAL,
        "search": RiskCategory.MINIMAL,
        "status_query": RiskCategory.MINIMAL,
    }

    def classify(self, operation: str, context: Dict[str, Any] = None) -> RiskCategory:
        """分类操作风险等级"""
        context = context or {}

        # 直接匹配
        for key, risk in self.RISK_MAP.items():
            if key in operation.lower():
                return risk

        # 上下文增强
        if context.get("amount", 0) > 100:
            return RiskCategory.HIGH
        if context.get("file_count", 0) > 50:
            return RiskCategory.HIGH

        return RiskCategory.LIMITED

    def needs_human_review(self, risk: RiskCategory) -> bool:
        """判断是否需要人工审核"""
        return risk in (RiskCategory.HIGH, RiskCategory.UNACCEPTABLE)


# ============================================================
# ComplianceReportGenerator — 合规报告生成器
# ============================================================

class ComplianceReportGenerator:
    """
    合规报告生成器。

    基于审计日志生成结构化 JSON 报告，包含：
    - 操作统计与风险分布
    - EU AI Act 合规评分
    - CuP 指标评分
    - 违规明细与改进建议
    """

    def __init__(self, audit_trail: AuditTrail, policy: EnterpriseSecurityPolicy):
        self.audit = audit_trail
        self.policy = policy

    def generate(self, period_start: str = None, period_end: str = None) -> ComplianceReport:
        """生成合规报告"""
        entries = self.audit._entries
        if period_start:
            entries = [e for e in entries if e.timestamp >= period_start]
        if period_end:
            entries = [e for e in entries if e.timestamp <= period_end]

        report = ComplianceReport(
            period_start=period_start or "N/A",
            period_end=period_end or "N/A",
        )

        # 统计
        report.total_operations = len(entries)
        for entry in entries:
            if entry.compliance_status == ComplianceStatus.BLOCKED:
                report.blocked_operations += 1
            elif entry.compliance_status == ComplianceStatus.NEEDS_REVIEW:
                report.reviewed_operations += 1
            elif entry.compliance_status == ComplianceStatus.FLAGGED:
                report.flagged_operations += 1

            # 风险分布
            risk_key = entry.risk_category.value
            report.risk_distribution[risk_key] = report.risk_distribution.get(risk_key, 0) + 1

            # 操作类别分布
            report.category_distribution[entry.operation] = \
                report.category_distribution.get(entry.operation, 0) + 1

        # 违规明细
        violations = self.audit.get_violations()
        report.violations = [
            {
                "actor": v.actor,
                "operation": v.operation,
                "reason": v.decision_basis,
                "timestamp": v.timestamp,
            }
            for v in violations[-20:]  # 最近20条
        ]

        # EU AI Act 合规评分（简化版）
        report.eu_ai_act_compliance_score = self._compute_eu_score(report)

        # CuP 指标评分
        report.cup_score = self._compute_cup_score(report)

        # 建议
        report.recommendations = self._generate_recommendations(report)

        return report

    def _compute_eu_score(self, report: ComplianceReport) -> float:
        """EU AI Act 合规评分（0~100）"""
        if report.total_operations == 0:
            return 100.0

        base_score = 100.0
        # 每次阻塞 -2 分
        base_score -= report.blocked_operations * 2
        # 每次标记 -1 分
        base_score -= report.flagged_operations * 1
        # 不可接受风险出现 -10 分
        unacceptable = report.risk_distribution.get("unacceptable", 0)
        base_score -= unacceptable * 10
        # 高风险占比 >20% 额外扣分
        high_risk = report.risk_distribution.get("high", 0)
        if report.total_operations > 0 and high_risk / report.total_operations > 0.2:
            base_score -= 10

        return max(0.0, round(base_score, 1))

    def _compute_cup_score(self, report: ComplianceReport) -> float:
        """CuP 指标评分 — 衡量合规操作占比"""
        if report.total_operations == 0:
            return 100.0
        allowed = report.total_operations - report.blocked_operations
        return round((allowed / report.total_operations) * 100, 1)

    def _generate_recommendations(self, report: ComplianceReport) -> List[str]:
        recs = []
        if report.blocked_operations > 5:
            recs.append("建议审查高频阻塞操作，优化安全策略规则粒度")
        if report.flagged_operations > 10:
            recs.append("标记操作数量偏高，建议加强操作前合规预检")
        if report.risk_distribution.get("unacceptable", 0) > 0:
            recs.append("检测到不可接受风险操作，建议立即排查并加强访问控制")
        if report.eu_ai_act_compliance_score < 70:
            recs.append("EU AI Act 合规评分偏低 (<70)，建议进行全面合规审计")
        if report.cup_score < 62:
            recs.append("CuP 评分低于 62%，接近企业安全策略基线，需优化安全护栏")
        if not recs:
            recs.append("当前合规状态良好，继续保持定期审计")
        return recs


# ============================================================
# ComplianceGuard — 顶层协调器
# ============================================================

class ComplianceGuard:
    """
    安全合规层顶层协调器。

    整合：
    - EnterpriseSecurityPolicy: CuP 策略过滤
    - AuditTrail: 操作审计日志
    - RiskClassifier: 风险分级
    - ComplianceReportGenerator: 合规报告
    """

    def __init__(self, log_dir: Optional[Path] = None,
                 custom_policy_rules: Dict[str, Any] = None):
        self.policy = EnterpriseSecurityPolicy(custom_policy_rules)
        self.audit = AuditTrail(log_dir)
        self.risk_classifier = RiskClassifier()
        self.report_generator = ComplianceReportGenerator(self.audit, self.policy)
        logger.info("[ComplianceGuard] 安全合规层已初始化")

    def guard(self, actor: str, operation: str, resource: str,
              context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        合规检查主入口。

        流程:
        1. 风险分级
        2. CuP 策略过滤
        3. 记录审计日志
        4. 返回合规判定

        返回: {"allowed": bool, "status": str, "risk": str, "decision_basis": str}
        """
        context = context or {}

        # 1. 风险分级
        risk = self.risk_classifier.classify(operation, context)

        # 2. 策略评估
        op_cat = self._infer_operation_category(operation, context)
        status, basis = self.policy.evaluate(op_cat, actor, resource, context)

        # 3. 高风险强制确认
        if self.risk_classifier.needs_human_review(risk) and status != ComplianceStatus.BLOCKED:
            status = ComplianceStatus.NEEDS_REVIEW
            basis = f"高风险操作 ({risk.value})，需人工确认"

        # 4. 记录审计日志
        self.audit.record(
            actor=actor,
            operation=operation,
            resource=resource,
            decision_basis=basis,
            risk_category=risk,
            compliance_status=status,
            result="blocked" if status == ComplianceStatus.BLOCKED else "allowed",
            metadata={"risk": risk.value, "context": context},
        )

        return {
            "allowed": status == ComplianceStatus.ALLOWED,
            "status": status.value,
            "risk": risk.value,
            "decision_basis": basis,
        }

    def _infer_operation_category(self, operation: str,
                                   context: Dict[str, Any]) -> OperationCategory:
        op_lower = operation.lower()
        if any(kw in op_lower for kw in ("payment", "transfer", "financial", "money")):
            return OperationCategory.FINANCIAL
        if any(kw in op_lower for kw in ("legal", "contract", "lawsuit")):
            return OperationCategory.LEGAL
        if any(kw in op_lower for kw in ("medical", "diagnosis", "drug")):
            return OperationCategory.MEDICAL
        if any(kw in op_lower for kw in ("pii", "personal_data", "ssn")):
            return OperationCategory.PII_ACCESS
        if any(kw in op_lower for kw in ("delete", "remove", "erase")):
            return OperationCategory.DELETE
        if any(kw in op_lower for kw in ("execute", "run", "script")):
            return OperationCategory.EXECUTE
        if any(kw in op_lower for kw in ("config", "setting", "configure")):
            return OperationCategory.CONFIGURE
        return OperationCategory.READ

    def generate_report(self, period_start: str = None,
                        period_end: str = None) -> ComplianceReport:
        """生成合规报告"""
        return self.report_generator.generate(period_start, period_end)

    def get_status(self) -> Dict[str, Any]:
        return {
            "audit_stats": self.audit.get_stats(),
            "policy_rules_count": len(self.policy.rules),
        }
