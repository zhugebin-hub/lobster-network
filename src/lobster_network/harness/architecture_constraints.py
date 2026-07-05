"""
Architecture Constraints — 架构约束

铁律四: 能写成 Linter 的约束，别停留在文档。

每条约束:
1. 必须对应一个真实失败案例
2. 必须是机器可强制执行的
3. 违规时有明确的错误信息和修复建议

参考: 悟空AI招聘的合规Linter设计
"""

import json
import re
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class Severity(Enum):
    FATAL = "fatal"       # 阻断执行
    ERROR = "error"       # 标记失败
    WARN = "warn"         # 仅警告
    INFO = "info"         # 记录日志


@dataclass
class LinterViolation:
    """Linter 违规记录"""
    rule_id: str
    severity: Severity
    message: str
    file_path: str = ""
    line_number: int = 0
    snippet: str = ""
    fix_suggestion: str = ""
    failure_case: str = ""  # 导致这条规则的真实失败案例


@dataclass
class Constraint:
    """
    架构约束 — 可执行的规则。

    每条约束必须有:
    - id: 唯一标识
    - description: 约束描述
    - check: 检查函数，返回 (通过, 违规列表)
    - failure_case: 来源的真实失败案例
    - severity: 违规严重程度
    """
    id: str
    description: str
    failure_case: str          # 真实失败案例
    severity: Severity = Severity.ERROR
    check: Optional[Callable] = None
    check_pattern: str = ""    # 正则检查模式
    auto_fix: Optional[Callable] = None  # 自动修复函数

    def validate(self, content: str, context: Dict[str, Any] = None) -> List[LinterViolation]:
        """检查是否违规"""
        violations = []

        # 模式检查
        if self.check_pattern:
            pattern = re.compile(self.check_pattern, re.MULTILINE)
            matches = list(pattern.finditer(content))
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                violations.append(LinterViolation(
                    rule_id=self.id,
                    severity=self.severity,
                    message=self.description,
                    snippet=match.group()[:100],
                    line_number=line_num,
                    fix_suggestion=f"匹配模式: {self.check_pattern}",
                    failure_case=self.failure_case,
                ))

        # 自定义检查函数
        if self.check:
            try:
                result = self.check(content, context or {})
                if isinstance(result, list):
                    violations.extend(result)
                elif not result:
                    violations.append(LinterViolation(
                        rule_id=self.id,
                        severity=self.severity,
                        message=self.description,
                        failure_case=self.failure_case,
                    ))
            except Exception as e:
                violations.append(LinterViolation(
                    rule_id=self.id,
                    severity=Severity.WARN,
                    message=f"约束检查失败: {e}",
                    failure_case=self.failure_case,
                ))

        return violations


class LinterConstraint(Constraint):
    """
    Linter 级约束 — 机器强制执行，不依赖自然语言。

    铁律四落地: 能写成 Linter 的约束，别停留在文档。
    """
    def __init__(self, id: str, description: str, failure_case: str,
                 check_fn: Callable = None, **kwargs):
        super().__init__(
            id=id,
            description=description,
            failure_case=failure_case,
            severity=kwargs.get('severity', Severity.ERROR),
            check=check_fn,
            check_pattern=kwargs.get('check_pattern', ''),
        )


class ConstraintEngine:
    """
    约束引擎 — 管理所有架构约束。

    用法:
        engine = ConstraintEngine()

        # 注册约束 (来自真实失败案例)
        engine.register(LinterConstraint(
            id="no-passive-offer",
            description="禁止主动向候选人发Offer",
            failure_case="2026-03: Agent在对话中主动承诺薪资，引发合规风险",
            check_pattern=r"我们决定录取|正式Offer|薪资.*$"  # 实际应更精确
        ))

        # 检查
        violations = engine.check_file("output.txt")
        if engine.has_fatal(violations):
            print("阻断执行")
    """

    def __init__(self, constraints_dir: str = ""):
        self.constraints: Dict[str, Constraint] = {}
        self.constraints_dir = constraints_dir
        self._execution_log: List[Dict] = []

    def register(self, constraint: Constraint):
        """注册约束"""
        self.constraints[constraint.id] = constraint

    def unregister(self, constraint_id: str):
        """移除约束"""
        self.constraints.pop(constraint_id, None)

    def check_content(self, content: str, context: Dict[str, Any] = None) -> List[LinterViolation]:
        """检查内容是否违反所有约束"""
        all_violations = []
        for cid, constraint in self.constraints.items():
            violations = constraint.validate(content, context or {})
            all_violations.extend(violations)

        self._execution_log.append({
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "constraints_count": len(self.constraints),
            "violations_count": len(all_violations),
            "content_length": len(content),
        })

        return all_violations

    def check_file(self, file_path: str, context: Dict[str, Any] = None) -> List[LinterViolation]:
        """检查文件是否违反约束"""
        if not os.path.exists(file_path):
            return [LinterViolation(
                rule_id="file-exists",
                severity=Severity.ERROR,
                message=f"文件不存在: {file_path}",
                file_path=file_path,
            )]

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        violations = self.check_content(content, context or {})
        for v in violations:
            v.file_path = file_path

        return violations

    def check_workspace(self, workspace_dir: str, pattern: str = "*.md") -> Dict[str, List[LinterViolation]]:
        """检查工作空间中的所有文件"""
        import glob
        results = {}
        for file_path in glob.glob(os.path.join(workspace_dir, "**", pattern), recursive=True):
            violations = self.check_file(file_path)
            if violations:
                results[file_path] = violations
        return results

    def has_fatal(self, violations: List[LinterViolation]) -> bool:
        """是否存在致命违规"""
        return any(v.severity == Severity.FATAL for v in violations)

    def has_errors(self, violations: List[LinterViolation]) -> bool:
        """是否存在错误级别违规"""
        return any(v.severity in (Severity.FATAL, Severity.ERROR) for v in violations)

    def format_report(self, violations: List[LinterViolation]) -> str:
        """格式化违规报告"""
        if not violations:
            return "✅ 无违规"

        lines = ["## Linter 约束报告", ""]
        by_severity = {}
        for v in violations:
            by_severity.setdefault(v.severity, []).append(v)

        for sev in [Severity.FATAL, Severity.ERROR, Severity.WARN, Severity.INFO]:
            items = by_severity.get(sev, [])
            if not items:
                continue

            lines.append(f"### {sev.value.upper()} ({len(items)} 条)")
            for v in items:
                lines.append(f"- [{v.rule_id}] {v.message}")
                if v.file_path:
                    lines.append(f"  文件: {v.file_path}:{v.line_number}")
                if v.failure_case:
                    lines.append(f"  来源案例: {v.failure_case}")
                if v.snippet:
                    lines.append(f"  匹配: `{v.snippet}`")
                if v.fix_suggestion:
                    lines.append(f"  修复: {v.fix_suggestion}")
                lines.append("")

        return "\n".join(lines)

    def list_constraints(self) -> List[Dict]:
        """列出所有约束"""
        return [{
            "id": c.id,
            "description": c.description,
            "failure_case": c.failure_case,
            "severity": c.severity.value,
        } for c in self.constraints.values()]

    def get_execution_log(self) -> List[Dict]:
        return self._execution_log


# ============================================================
# 小龙虾网络 预定义约束模板
# ============================================================

def build_lobster_constraints() -> ConstraintEngine:
    """
    构建小龙虾网络的默认约束集。

    每条约束对应一个真实失败案例。
    """
    engine = ConstraintEngine()

    # 约束1: 不允许裸 except
    engine.register(LinterConstraint(
        id="no-bare-except",
        description="禁止使用裸 except:，必须指定异常类型",
        failure_case="2026-06: sync_manager.py 多处裸 except 捕获 KeyboardInterrupt",
        check_pattern=r"^\s*except\s*:",
        severity=Severity.ERROR,
    ))

    # 约束2: 不允许 StrictHostKeyChecking=no
    engine.register(LinterConstraint(
        id="no-weak-ssh",
        description="禁止使用 StrictHostKeyChecking=no，改用 accept-new",
        failure_case="2026-06: SSH通道配置 MITM 风险",
        check_pattern=r"StrictHostKeyChecking\s*=\s*no",
        severity=Severity.FATAL,
    ))

    # 约束3: Agent数量不超过3个 (铁律二)
    engine.register(LinterConstraint(
        id="max-3-agents",
        description="Agent 数量不应超过 3 个，Skill 可以无限加",
        failure_case="悟空AI: 堆到第6个Agent时编排层开始'选错Agent'",
        severity=Severity.WARN,
    ))

    # 约束4: 不允许硬编码密码/密钥
    engine.register(LinterConstraint(
        id="no-hardcoded-secrets",
        description="禁止硬编码密码、API密钥、Token",
        failure_case="安全审计: 多处脚本硬编码认证信息",
        check_pattern=r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]{8,}",
        severity=Severity.FATAL,
    ))

    # 约束5: SSH密钥权限检查
    engine.register(LinterConstraint(
        id="ssh-key-permissions",
        description="SSH密钥文件权限应为 600",
        failure_case="诸葛虾: authorized_keys 权限 644 导致 SSH 忽略",
        check_fn=lambda content, ctx: _check_ssh_permissions(ctx),
        severity=Severity.ERROR,
    ))

    # 约束6: datetime.utcnow 已弃用
    engine.register(LinterConstraint(
        id="no-deprecated-utcnow",
        description="datetime.utcnow() 已弃用，改用 datetime.now()",
        failure_case="2026-06: Python 3.12+ 弃用 utcnow 导致测试失败",
        check_pattern=r"datetime\.utcnow\(\)",
        severity=Severity.WARN,
    ))

    return engine


def _check_ssh_permissions(ctx: Dict[str, Any]) -> List[LinterViolation]:
    """检查 SSH 密钥权限"""
    violations = []
    ssh_dir = os.path.expanduser("~/.ssh")
    if not os.path.exists(ssh_dir):
        return violations

    for fname in os.listdir(ssh_dir):
        fpath = os.path.join(ssh_dir, fname)
        if fname.startswith(".") or os.path.isdir(fpath):
            continue
        mode = os.stat(fpath).st_mode & 0o777
        if mode != 0o600:
            violations.append(LinterViolation(
                rule_id="ssh-key-permissions",
                severity=Severity.ERROR,
                message=f"SSH 密钥权限不安全: {fpath} (当前: {oct(mode)}, 期望: 0o600)",
                file_path=fpath,
                fix_suggestion=f"chmod 600 {fpath}",
                failure_case="诸葛虾: authorized_keys 权限 644 导致 SSH 忽略",
            ))

    return violations
