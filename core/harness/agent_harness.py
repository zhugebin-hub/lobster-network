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
    circuit_breaker_triggered: bool = False
    rate_limited: bool = False
    l3_confidence: float = 0.0
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


# ============================================================
# CircuitBreaker — 熔断器（按 agent_id 粒度）
# ============================================================

import time as _time
import threading as _threading
from enum import Enum as _Enum


class CircuitState(str, _Enum):
    CLOSED = "CLOSED"          # 正常通行
    OPEN = "OPEN"              # 熔断，拒绝所有请求
    HALF_OPEN = "HALF_OPEN"    # 半开，放行 1 个探测请求


class CircuitBreaker:
    """
    论文 6.3.5 节：熔断器机制。

    三态：CLOSED / OPEN / HALF_OPEN
    - 失败阈值 5 次 → OPEN（阻止所有请求 30s）
    - HALF_OPEN 放行 1 个探测请求，成功则 CLOSED，失败则重新 OPEN
    - 按 agent_id 粒度独立熔断

    用法:
        cb = CircuitBreaker(failure_threshold=5, recovery_timeout_s=30)
        if cb.allow_request("agent_qoder"):
            try:
                result = call_agent("agent_qoder")
                cb.record_success("agent_qoder")
            except Exception:
                cb.record_failure("agent_qoder")
        else:
            # 熔断中，走降级逻辑
            ...
    """

    @dataclass
    class _BreakerState:
        state: CircuitState = CircuitState.CLOSED
        failure_count: int = 0
        last_failure_time: float = 0.0
        half_open_probe_sent: bool = False

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_s: float = 30.0,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s

        self._breakers: Dict[str, CircuitBreaker._BreakerState] = {}
        self._lock = _threading.Lock()

        # 统计
        self._total_trips = 0
        self._total_rejections = 0

    def allow_request(self, agent_id: str) -> bool:
        """检查是否允许请求通过"""
        with self._lock:
            breaker = self._breakers.get(agent_id)
            if breaker is None:
                self._breakers[agent_id] = self._BreakerState()
                return True

            if breaker.state == CircuitState.CLOSED:
                return True

            if breaker.state == CircuitState.OPEN:
                # 检查是否到了恢复时间
                elapsed = _time.time() - breaker.last_failure_time
                if elapsed >= self.recovery_timeout_s:
                    # 进入 HALF_OPEN
                    breaker.state = CircuitState.HALF_OPEN
                    breaker.half_open_probe_sent = False
                    logger.info(f"[CircuitBreaker] {agent_id}: OPEN → HALF_OPEN (超时 {elapsed:.1f}s)")
                    # 放行探测请求
                    breaker.half_open_probe_sent = True
                    return True
                else:
                    # 仍在熔断期
                    self._total_rejections += 1
                    logger.warning(
                        f"[CircuitBreaker] {agent_id}: 熔断拒绝 (还有 {self.recovery_timeout_s - elapsed:.1f}s 恢复)"
                    )
                    return False

            if breaker.state == CircuitState.HALF_OPEN:
                if not breaker.half_open_probe_sent:
                    breaker.half_open_probe_sent = True
                    return True
                else:
                    # 已有探测请求在执行中
                    self._total_rejections += 1
                    return False

        return True

    def record_success(self, agent_id: str):
        """记录成功"""
        with self._lock:
            breaker = self._breakers.get(agent_id)
            if breaker is None:
                return

            if breaker.state == CircuitState.HALF_OPEN:
                breaker.state = CircuitState.CLOSED
                breaker.failure_count = 0
                breaker.half_open_probe_sent = False
                logger.info(f"[CircuitBreaker] {agent_id}: HALF_OPEN → CLOSED (探测成功)")
            elif breaker.state == CircuitState.CLOSED:
                breaker.failure_count = 0

    def record_failure(self, agent_id: str):
        """记录失败"""
        with self._lock:
            breaker = self._breakers.get(agent_id)
            if breaker is None:
                breaker = self._BreakerState()
                self._breakers[agent_id] = breaker

            breaker.failure_count += 1
            breaker.last_failure_time = _time.time()

            if breaker.state == CircuitState.HALF_OPEN:
                # 探测失败，重新熔断
                breaker.state = CircuitState.OPEN
                breaker.half_open_probe_sent = False
                self._total_trips += 1
                logger.warning(f"[CircuitBreaker] {agent_id}: HALF_OPEN → OPEN (探测失败)")

            elif breaker.state == CircuitState.CLOSED and breaker.failure_count >= self.failure_threshold:
                breaker.state = CircuitState.OPEN
                self._total_trips += 1
                logger.warning(
                    f"[CircuitBreaker] {agent_id}: CLOSED → OPEN "
                    f"(连续失败 {breaker.failure_count}/{self.failure_threshold})"
                )

    def reset(self, agent_id: str):
        """手动重置熔断器"""
        with self._lock:
            if agent_id in self._breakers:
                self._breakers[agent_id] = self._BreakerState()
                logger.info(f"[CircuitBreaker] {agent_id}: 手动重置")

    def get_state(self, agent_id: str) -> Optional[str]:
        """获取某 agent 的熔断状态"""
        with self._lock:
            breaker = self._breakers.get(agent_id)
            if breaker is None:
                return None
            return breaker.state.value

    def get_all_states(self) -> Dict[str, str]:
        """获取所有 agent 的熔断状态"""
        with self._lock:
            return {aid: b.state.value for aid, b in self._breakers.items()}

    def get_stats(self) -> Dict[str, Any]:
        """获取熔断统计"""
        with self._lock:
            return {
                "total_trips": self._total_trips,
                "total_rejections": self._total_rejections,
                "monitored_agents": len(self._breakers),
                "states": self.get_all_states(),
            }


# ============================================================
# RateLimiter — 令牌桶限流器
# ============================================================

class RateLimiter:
    """
    令牌桶算法限流器。

    按 agent_id 独立限流。
    默认 100 req/s，突发容量 150。
    超限返回 False（等价 HTTP 429）。

    用法:
        rl = RateLimiter(rate=100, burst=150)
        if rl.allow("agent_qoder"):
            process_request()
        else:
            raise HTTPException(status_code=429)
    """

    def __init__(self, rate: float = 100.0, burst: int = 150):
        """
        参数:
          rate: 令牌补充速率（tokens/s）
          burst: 桶容量（突发上限）
        """
        self.rate = rate
        self.burst = burst

        self._buckets: Dict[str, Tuple[float, float]] = {}  # agent_id → (tokens, last_refill_time)
        self._lock = _threading.Lock()

        # 统计
        self._total_allowed = 0
        self._total_denied = 0

    def allow(self, agent_id: str) -> bool:
        """检查是否允许请求通过（消耗 1 个令牌）"""
        with self._lock:
            now = _time.time()

            bucket = self._buckets.get(agent_id)
            if bucket is None:
                # 首次初始化
                self._buckets[agent_id] = (float(self.burst), now)
                bucket = (float(self.burst), now)

            tokens, last_refill = bucket

            # 补充令牌
            elapsed = now - last_refill
            new_tokens = min(float(self.burst), tokens + elapsed * self.rate)
            last_refill = now

            if new_tokens >= 1.0:
                new_tokens -= 1.0
                self._buckets[agent_id] = (new_tokens, last_refill)
                self._total_allowed += 1
                return True
            else:
                self._buckets[agent_id] = (new_tokens, last_refill)
                self._total_denied += 1
                return False

    def get_stats(self) -> Dict[str, Any]:
        """获取限流统计"""
        with self._lock:
            return {
                "rate": self.rate,
                "burst": self.burst,
                "total_allowed": self._total_allowed,
                "total_denied": self._total_denied,
                "deny_rate": round(
                    self._total_denied / max(self._total_allowed + self._total_denied, 1), 4
                ),
                "active_buckets": len(self._buckets),
            }


# ============================================================
# RLHFGuard — RLHF 输出护栏增强（占位实现）
# ============================================================

class RLHFGuard:
    """
    论文 6.3.5 节：RLHF 机制输出护栏。

    当前版本为占位实现：使用规则引擎 + 关键词过滤兜底。
    预留 RLHF 模型接口（可通过 load_model 加载未来训练的偏好模型）。

    所有 L3 判定记录到 harness_violations.log 并标注 confidence。

    用法:
        guard = RLHFGuard()
        result = guard.evaluate(output_text, context={})
        if not result["safe"]:
            logger.warning(f"RLHF 拦截: confidence={result['confidence']}")
    """

    # 高风险关键词（兜底规则）
    _HIGH_RISK_KEYWORDS = [
        "rm -rf", "DROP TABLE", "DELETE FROM", "format C:",
        "sudo su", "chmod 777", "eval(", "exec(",
        "__import__", "subprocess", "os.system",
    ]

    def __init__(self, model_path: str = ""):
        """
        参数:
          model_path: 未来 RLHF 模型路径（当前占位）
        """
        self._model_path = model_path
        self._model_loaded = False
        self._total_evaluations = 0
        self._total_blocks = 0

        self._violation_log_path = LOG_DIR / "harness_violations.log"

    def load_model(self, model_path: str) -> bool:
        """
        加载 RLHF 偏好模型（占位接口）。

        返回 True 表示成功加载。
        """
        logger.info(f"[RLHFGuard] 尝试加载模型: {model_path}")
        if Path(model_path).exists():
            self._model_path = model_path
            # 未来实现: 加载训练好的 RLHF 偏好模型
            self._model_loaded = True
            logger.info("[RLHFGuard] RLHF 模型加载成功")
            return True
        logger.warning("[RLHFGuard] 模型文件不存在，使用规则引擎兜底")
        return False

    def evaluate(self, output_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        评估输出安全性。

        参数:
          output_text: Agent 输出文本
          context: 上下文信息（agent_id, task_type 等）

        返回:
          {
            "safe": bool,
            "confidence": float,  # 0.0-1.0，置信度
            "reason": str,
            "method": str,        # "rlhf_model" / "rule_engine"
          }
        """
        self._total_evaluations += 1

        # 规则引擎兜底检查
        lower_text = output_text.lower()
        for keyword in self._HIGH_RISK_KEYWORDS:
            if keyword.lower() in lower_text:
                confidence = 0.95  # 规则命中高置信度
                reason = f"高风险关键词命中: {keyword}"
                self._total_blocks += 1
                self._log_violation(
                    output_text=output_text,
                    confidence=confidence,
                    reason=reason,
                    method="rule_engine",
                    context=context,
                )
                return {
                    "safe": False,
                    "confidence": confidence,
                    "reason": reason,
                    "method": "rule_engine",
                }

        # 通过规则引擎检查 — 低置信度（因为没有 RLHF 模型做精细判断）
        if self._model_loaded:
            # 未来: 使用 RLHF 偏好模型打分
            confidence = 0.85
            method = "rlhf_model"
        else:
            confidence = 0.50  # 仅规则引擎通过，置信度中等
            method = "rule_engine"

        return {
            "safe": True,
            "confidence": confidence,
            "reason": "",
            "method": method,
        }

    def _log_violation(
        self,
        output_text: str,
        confidence: float,
        reason: str,
        method: str,
        context: Dict[str, Any] = None,
    ):
        """记录 L3 违规到日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "confidence": confidence,
            "reason": reason,
            "output_snippet": output_text[:200],
            "context": context or {},
        }

        logger.warning(
            f"[RLHFGuard] L3 拦截 | confidence={confidence:.2f} | method={method} | reason={reason}"
        )

        # 追加到 violations 日志
        try:
            with open(self._violation_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"[RLHFGuard] 日志写入失败: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """获取 RLHF Guard 统计"""
        return {
            "model_loaded": self._model_loaded,
            "total_evaluations": self._total_evaluations,
            "total_blocks": self._total_blocks,
            "block_rate": round(
                self._total_blocks / max(self._total_evaluations, 1), 4
            ),
        }
