#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Harness 安全护栏 — 三层硬护栏实现

L1 输入护栏：指令过滤 / 上下文裁剪 / 敏感信息脱敏
L2 执行护栏：操作白名单 / 资源配额 / 副作用检测
L3 输出护栏：内容审核 / 格式校验 / 长度限制

参考：
- 给野马套上缰绳_Agent_Harness工程实践（阿里云）
- 小龙虾网络_Harness_Engineering融合分析
"""

import json
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# 日志配置
# ============================================================

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("agent_harness")
logger.setLevel(logging.INFO)

_handler = logging.FileHandler(LOG_DIR / "harness_violations.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))
logger.addHandler(_handler)

# 同时输出到控制台
_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("[Harness] %(levelname)s - %(message)s"))
logger.addHandler(_console)


# ============================================================
# 数据模型
# ============================================================

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class GuardResult:
    """单层护栏结果"""
    passed: bool
    blocked_reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HarnessResult:
    """整体 Harness 结果"""
    passed: bool
    l1: GuardResult
    l2: GuardResult
    l3: GuardResult
    sanitized_input: Optional[str] = None
    sanitized_output: Optional[str] = None
    violations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# 规则加载
# ============================================================

def _load_rules() -> dict:
    """从 harness_rules.json 加载配置"""
    rules_path = Path(__file__).resolve().parent / "harness_rules.json"
    if rules_path.exists():
        with open(rules_path, "r", encoding="utf-8") as f:
            return json.load(f)
    logger.warning("harness_rules.json 未找到，使用内置默认规则")
    return _default_rules()


def _default_rules() -> dict:
    """内置默认规则（兜底）"""
    return {
        "l1_input_guard": {"enabled": True, "dangerous_commands": [], "context_max_chars": 16000, "sensitive_patterns": {}},
        "l2_execution_guard": {
            "enabled": True,
            "allowed_operations": [
                "search_file", "read_file", "write_file", "edit_file", "delete",
                "shell_executor", "python_executor",
                "dispatch_task", "use_skill",
                "web_fetch", "web_search",
                "read_text", "analyze_image",
                "create_scheduled_task", "modify_scheduled_task",
            ],
            "high_risk_operations": [],
            "quotas": {},
            "side_effect_patterns": {},
        },
        "l3_output_guard": {"enabled": True, "max_output_chars": 50000, "blocked_patterns": [], "required_schema_fields": []},
        "bypass": {"enabled": True, "authorized_roles": ["hermes"], "require_reason": True},
    }


# ============================================================
# L1 输入护栏 (Input Guard)
# ============================================================

class InputGuard:
    """
    L1 输入护栏
    - 指令过滤：拦截危险操作模式
    - 上下文裁剪：超长输入自动摘要压缩
    - 敏感信息脱敏：检测并屏蔽 API Key/Token/密码
    """

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.dangerous_commands = config.get("dangerous_commands", [])
        self.context_max_chars = config.get("context_max_chars", 16000)
        self.sensitive_patterns = config.get("sensitive_patterns", {})
        # 预编译敏感信息正则
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        for name, pattern in self.sensitive_patterns.items():
            try:
                self._compiled_patterns[name] = re.compile(pattern)
            except re.error:
                logger.warning(f"敏感模式编译失败 [{name}]: {pattern}")

    def guard(self, raw_input: str) -> GuardResult:
        """
        对原始输入执行 L1 护栏检查。

        返回 GuardResult:
          - passed=True: sanitized_input 已放入 details
          - passed=False: blocked_reason 说明拦截原因
        """
        if not self.enabled:
            return GuardResult(passed=True, details={"sanitized_input": raw_input})

        # ---- 1. 指令过滤 ----
        for cmd in self.dangerous_commands:
            if cmd.lower() in raw_input.lower():
                reason = f"L1 拦截：输入包含危险指令模式 [{cmd}]"
                logger.warning(reason)
                return GuardResult(passed=False, blocked_reason=reason)

        sanitized = raw_input

        # ---- 2. 敏感信息脱敏 ----
        detections = []
        for name, pattern in self._compiled_patterns.items():
            match = pattern.search(sanitized)
            if match:
                detections.append({"pattern": name, "match": match.group()[:40] + "..."})
                sanitized = pattern.sub(f"[REDACTED:{name}]", sanitized)

        if detections:
            logger.info(f"L1 脱敏：检测到 {len(detections)} 处敏感信息")

        # ---- 3. 上下文裁剪 ----
        if len(sanitized) > self.context_max_chars:
            # 保留首尾关键部分
            head = sanitized[: self.context_max_chars // 2]
            tail = sanitized[-(self.context_max_chars // 2):]
            sanitized = (
                head
                + f"\n\n[... 上下文裁剪：{len(raw_input) - self.context_max_chars} 字符已省略 ...]\n\n"
                + tail
            )
            logger.info(f"L1 裁剪：{len(raw_input)} -> {len(sanitized)} 字符")

        return GuardResult(
            passed=True,
            details={
                "sanitized_input": sanitized,
                "original_length": len(raw_input),
                "sanitized_length": len(sanitized),
                "redactions": detections,
                "trimmed": len(raw_input) > self.context_max_chars,
            },
        )


# ============================================================
# L2 执行护栏 (Execution Guard)
# ============================================================

class ExecutionGuard:
    """
    L2 执行护栏
    - 操作白名单：仅允许配置中注册的安全操作
    - 资源配额：超时 / token / 内存限制
    - 副作用检测：识别文件写入 / 网络请求 / 外部调用
    """

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.allowed_operations = set(config.get("allowed_operations", []))
        self.high_risk_operations = set(config.get("high_risk_operations", []))
        self.quotas = config.get("quotas", {})
        self.side_effect_patterns = config.get("side_effect_patterns", {})

        # 配额消耗追踪
        self._usage: Dict[str, float] = {"calls": 0, "tokens": 0, "execution_time_s": 0}

    def guard(self, operation: str, params: Optional[dict] = None) -> GuardResult:
        """
        对拟执行操作进行 L2 护栏检查。

        参数:
          operation: 工具/操作名称
          params: 操作参数（可选，用于副作用分析）

        返回 GuardResult:
          - passed=True: 操作允许，附带风险等级和剩余配额
          - passed=False: 操作被拦截
        """
        if not self.enabled:
            return GuardResult(passed=True, details={"risk_level": RiskLevel.LOW.value})

        # ---- 1. 操作白名单 ----
        if operation not in self.allowed_operations:
            reason = f"L2 拦截：操作 [{operation}] 不在白名单中"
            logger.warning(reason)
            return GuardResult(passed=False, blocked_reason=reason, details={"operation": operation})

        # ---- 2. 风险定级 ----
        if operation in self.high_risk_operations:
            risk_level = RiskLevel.HIGH
        else:
            # 副作用检测
            risk_level = self._detect_side_effects(operation, params)

        # ---- 3. 资源配额检查 ----
        quota_ok, quota_msg = self._check_quotas()
        if not quota_ok:
            logger.warning(f"L2 配额耗尽: {quota_msg}")
            return GuardResult(passed=False, blocked_reason=f"L2 拦截：{quota_msg}")

        return GuardResult(
            passed=True,
            details={
                "risk_level": risk_level.value,
                "quota_remaining": self._quota_remaining(),
            },
        )

    def _detect_side_effects(self, operation: str, params: Optional[dict]) -> RiskLevel:
        """检测副作用并返回风险等级"""
        file_write_ops = set(self.side_effect_patterns.get("file_write", []))
        network_ops = set(self.side_effect_patterns.get("network_request", []))
        external_ops = set(self.side_effect_patterns.get("external_call", []))

        if operation in external_ops:
            return RiskLevel.HIGH
        if operation in network_ops:
            return RiskLevel.MEDIUM
        if operation in file_write_ops:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _check_quotas(self) -> Tuple[bool, str]:
        """检查资源配额"""
        max_calls = self.quotas.get("max_concurrent_calls", 5)
        if self._usage["calls"] >= max_calls:
            return False, f"并发调用数超限 ({max_calls})"
        return True, "ok"

    def _quota_remaining(self) -> dict:
        return {
            "calls_remaining": self.quotas.get("max_concurrent_calls", 5) - self._usage["calls"],
            "tokens_remaining": self.quotas.get("max_tokens_per_call", 4096),
            "memory_mb_limit": self.quotas.get("max_memory_mb", 512),
            "timeout_seconds": self.quotas.get("max_timeout_seconds", 300),
        }

    def record_usage(self, calls: int = 0, tokens: int = 0):
        """记录实际消耗"""
        self._usage["calls"] += calls
        self._usage["tokens"] += tokens


# ============================================================
# L3 输出护栏 (Output Guard)
# ============================================================

class OutputGuard:
    """
    L3 输出护栏
    - 内容审核：过滤有害/违规/泄露内容
    - 格式校验：确保输出符合预期 schema
    - 长度限制：防止无限输出
    """

    def __init__(self, config: dict):
        self.enabled = config.get("enabled", True)
        self.max_output_chars = config.get("max_output_chars", 50000)
        self.blocked_patterns = config.get("blocked_patterns", [])
        self.required_schema_fields = config.get("required_schema_fields", [])
        # 预编译拦截正则
        self._compiled_patterns: List[re.Pattern] = []
        for pattern in self.blocked_patterns:
            try:
                self._compiled_patterns.append(re.compile(pattern))
            except re.error:
                logger.warning(f"输出拦截模式编译失败: {pattern}")

    def guard(self, raw_output: str) -> GuardResult:
        """
        对原始输出执行 L3 护栏检查。

        返回 GuardResult:
          - passed=True: sanitized_output 已放入 details
          - passed=False: blocked_reason 说明拦截原因
        """
        if not self.enabled:
            return GuardResult(passed=True, details={"sanitized_output": raw_output})

        issues = []

        # ---- 1. 内容审核 ----
        for pattern in self._compiled_patterns:
            matches = pattern.findall(raw_output)
            if matches:
                issues.append(f"检测到违规内容: {matches[0][:60]}...")
                # 用脱敏标记替换
                raw_output = pattern.sub("[BLOCKED]", raw_output)

        if issues:
            logger.warning(f"L3 内容审核：{len(issues)} 处违规")

        # ---- 2. 长度限制 ----
        sanitized = raw_output
        if len(sanitized) > self.max_output_chars:
            sanitized = sanitized[: self.max_output_chars]
            sanitized += f"\n\n[... 输出截断：已限制为 {self.max_output_chars} 字符 ...]"
            issues.append(f"输出超长 {len(raw_output)} -> {self.max_output_chars} 字符截断")

        # ---- 3. 格式校验 (可扩展) ----
        if self.required_schema_fields:
            try:
                data = json.loads(sanitized) if sanitized.strip().startswith("{") else None
                if data:
                    for field in self.required_schema_fields:
                        if field not in data:
                            issues.append(f"缺少必需字段: {field}")
            except json.JSONDecodeError:
                pass  # 非 JSON 输出，不做 schema 校验

        return GuardResult(
            passed=len([i for i in issues if "拦截" in i]) == 0,
            details={
                "sanitized_output": sanitized,
                "original_length": len(raw_output),
                "sanitized_length": len(sanitized),
                "issues": issues,
            },
        )


# ============================================================
# AgentHarness 主类
# ============================================================

class AgentHarness:
    """
    Agent 安全护栏主控制器 — 整合三层护栏

    用法:
        harness = AgentHarness()
        result = harness.guard(
            input_text="用户输入...",
            operation="write_file",
            output_text="Agent 输出..."
        )
        if result.passed:
            # 安全，继续执行
            ...
    """

    def __init__(self, rules_path: Optional[str] = None, bypass_role: Optional[str] = None):
        """
        初始化 Harness。

        参数:
          rules_path: 规则配置文件路径，默认从 harness_rules.json 加载
          bypass_role: 触发 bypass 的角色标识（如 "hermes"）
        """
        rules = _load_rules()
        self.l1 = InputGuard(rules.get("l1_input_guard", {}))
        self.l2 = ExecutionGuard(rules.get("l2_execution_guard", {}))
        self.l3 = OutputGuard(rules.get("l3_output_guard", {}))
        self.bypass_config = rules.get("bypass", {})
        self.bypass_role = bypass_role

        logger.info(f"AgentHarness 初始化完成 | bypass={'启用' if self._is_bypass() else '禁用'}")

    def _is_bypass(self) -> bool:
        """检查当前角色是否有 bypass 权限"""
        if not self.bypass_config.get("enabled", False):
            return False
        if not self.bypass_role:
            return False
        return self.bypass_role in self.bypass_config.get("authorized_roles", [])

    def guard(
        self,
        input_text: Optional[str] = None,
        operation: Optional[str] = None,
        output_text: Optional[str] = None,
    ) -> HarnessResult:
        """
        三合一护栏入口。

        参数:
          input_text: 用户/上游输入
          operation: 拟执行的操作名称
          output_text: Agent 拟输出的内容

        返回 HarnessResult，含三层各自结果和最终 passed 判定。
        """
        violations: List[str] = []
        sanitized_input = input_text
        sanitized_output = output_text

        # Bypass 模式
        if self._is_bypass():
            logger.info(f"[BYPASS] 教练 {self.bypass_role} 绕过全部护栏")
            return HarnessResult(
                passed=True,
                l1=GuardResult(passed=True),
                l2=GuardResult(passed=True),
                l3=GuardResult(passed=True),
                sanitized_input=input_text,
                sanitized_output=output_text,
            )

        # ---- L1 输入护栏 ----
        l1_result = GuardResult(passed=True)
        if input_text is not None:
            l1_result = self.l1.guard(input_text)
            if not l1_result.passed:
                violations.append(l1_result.blocked_reason)
            else:
                sanitized_input = l1_result.details.get("sanitized_input", input_text)

        # ---- L2 执行护栏 ----
        l2_result = GuardResult(passed=True)
        if operation is not None:
            l2_result = self.l2.guard(operation)
            if not l2_result.passed:
                violations.append(l2_result.blocked_reason)

        # ---- L3 输出护栏 ----
        l3_result = GuardResult(passed=True)
        if output_text is not None:
            l3_result = self.l3.guard(output_text)
            if not l3_result.passed:
                violations.append(l3_result.blocked_reason)
            else:
                sanitized_output = l3_result.details.get("sanitized_output", output_text)

        # 汇总
        passed = l1_result.passed and l2_result.passed and l3_result.passed

        result = HarnessResult(
            passed=passed,
            l1=l1_result,
            l2=l2_result,
            l3=l3_result,
            sanitized_input=sanitized_input,
            sanitized_output=sanitized_output,
            violations=violations,
        )

        # 记录违规事件
        if violations:
            logger.warning(f"护栏违规 ({len(violations)}): {'; '.join(violations)}")
        else:
            logger.debug("护栏检查全部通过")

        return result

    def guard_input(self, raw_input: str) -> GuardResult:
        """只执行 L1 输入护栏（便捷方法）"""
        return self.l1.guard(raw_input)

    def guard_execution(self, operation: str) -> GuardResult:
        """只执行 L2 执行护栏（便捷方法）"""
        return self.l2.guard(operation)

    def guard_output(self, raw_output: str) -> GuardResult:
        """只执行 L3 输出护栏（便捷方法）"""
        return self.l3.guard(raw_output)


# ============================================================
# 便捷工厂
# ============================================================

def create_harness(bypass_role: Optional[str] = None) -> AgentHarness:
    """工厂方法：创建 Harness 实例"""
    return AgentHarness(bypass_role=bypass_role)
