#!/usr/bin/env python3
<<<<<<< HEAD
# -*- coding: utf-8 -*-
"""
熔断器 (Circuit Breaker) - 小龙虾网络 V3.1
保护外部 API 调用，防止雪崩效应

状态机: CLOSED -> OPEN -> HALF_OPEN -> CLOSED/OPEN
触发条件: 连续失败次数达到阈值
恢复策略: 指数退避 + 半开试探
"""

import time
import logging
import functools
from enum import Enum
from typing import Callable, Any, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"       # 正常通行
    OPEN = "open"           # 熔断中，拒绝请求
    HALF_OPEN = "half_open" # 半开试探，允许少量请求


@dataclass
class CircuitBreakerConfig:
    """熔断器配置"""
    failure_threshold: int = 5          # 连续失败多少次触发熔断
    success_threshold: int = 3          # 半开状态连续成功多少次恢复
    recovery_timeout: float = 60.0      # 熔断后等待多久进入半开（秒）
    half_open_max_calls: int = 3        # 半开状态最多允许多少并发试探
    excluded_exceptions: tuple = ()     # 不触发熔断的异常类型


@dataclass
class CircuitStats:
    """熔断器统计"""
    total_calls: int = 0
    total_successes: int = 0
    total_failures: int = 0
    total_rejections: int = 0           # 熔断中拒绝的次数
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    last_failure_time: Optional[float] = None
    last_state_change: Optional[float] = None
    state_transitions: list = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "total_calls": self.total_calls,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_rejections": self.total_rejections,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "last_failure_time": self.last_failure_time,
        }


class CircuitBreaker:
    """熔断器实现"""

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._half_open_calls = 0
        self._opened_at: Optional[float] = None
        logger.info(f"[熔断器:{self.name}] 初始化: threshold={self.config.failure_threshold}, "
                     f"recovery={self.config.recovery_timeout}s")

    def _transition(self, new_state: CircuitState):
        if self.state != new_state:
            old_state = self.state
            self.state = new_state
            self.stats.last_state_change = time.time()
            self.stats.state_transitions.append({
                "from": old_state.value,
                "to": new_state.value,
                "time": datetime.now().isoformat()
            })
            logger.info(f"[熔断器:{self.name}] 状态变更: {old_state.value} -> {new_state.value}")

    def _check_state_transition(self):
        """检查是否需要自动转换状态"""
        if self.state == CircuitState.OPEN and self._opened_at:
            elapsed = time.time() - self._opened_at
            if elapsed >= self.config.recovery_timeout:
                self._half_open_calls = 0
                self._transition(CircuitState.HALF_OPEN)

    def can_execute(self) -> bool:
        """判断是否可以执行请求"""
        self._check_state_transition()

        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            self.stats.total_rejections += 1
            return False
        elif self.state == CircuitState.HALF_OPEN:
            if self._half_open_calls < self.config.half_open_max_calls:
                self._half_open_calls += 1
                return True
            return False
        return False

    def record_success(self):
        """记录成功"""
        self.stats.total_calls += 1
        self.stats.total_successes += 1
        self.stats.consecutive_failures = 0
        self.stats.consecutive_successes += 1

        if self.state == CircuitState.HALF_OPEN:
            if self.stats.consecutive_successes >= self.config.success_threshold:
                self.stats.consecutive_successes = 0
                self._transition(CircuitState.CLOSED)
                logger.info(f"[熔断器:{self.name}] 恢复为 CLOSED，服务正常")

    def record_failure(self, exception: Optional[Exception] = None):
        """记录失败"""
        # 检查是否为排除的异常
        if self.config.excluded_exceptions and exception:
            if isinstance(exception, self.config.excluded_exceptions):
                return

        self.stats.total_calls += 1
        self.stats.total_failures += 1
        self.stats.consecutive_failures += 1
        self.stats.consecutive_successes = 0
        self.stats.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            # 半开状态任何失败直接回到 OPEN
            self._opened_at = time.time()
            self._transition(CircuitState.OPEN)
            logger.warning(f"[熔断器:{self.name}] 半开试探失败，重新 OPEN")
        elif self.state == CircuitState.CLOSED:
            if self.stats.consecutive_failures >= self.config.failure_threshold:
                self._opened_at = time.time()
                self._transition(CircuitState.OPEN)
                logger.error(f"[熔断器:{self.name}] 连续失败 {self.stats.consecutive_failures} 次，触发 OPEN 熔断")

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行受保护的函数调用"""
        if not self.can_execute():
            raise CircuitOpenError(
                f"[熔断器:{self.name}] 电路处于 {self.state.value} 状态，请求被拒绝"
            )

        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            raise

    async def execute_async(self, coro, *args, **kwargs) -> Any:
        """执行受保护的异步函数调用"""
        if not self.can_execute():
            raise CircuitOpenError(
                f"[熔断器:{self.name}] 电路处于 {self.state.value} 状态，请求被拒绝"
            )

        try:
            if callable(coro):
                result = await coro(*args, **kwargs)
            else:
                result = await coro
            self.record_success()
            return result
        except Exception as e:
            self.record_failure(e)
            raise

    def get_status(self) -> Dict:
        """获取熔断器状态"""
        self._check_state_transition()
        return {
            "name": self.name,
            "state": self.state.value,
            "stats": self.stats.to_dict(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
            }
        }

    def reset(self):
        """手动重置熔断器"""
        self.state = CircuitState.CLOSED
        self.stats = CircuitStats()
        self._half_open_calls = 0
        self._opened_at = None
        logger.info(f"[熔断器:{self.name}] 手动重置")


class CircuitOpenError(Exception):
    """熔断器打开时的异常"""
    pass


# ========== 装饰器 ==========

def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """熔断器装饰器"""
    breaker = CircuitBreaker(name, config)

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.execute_async(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return breaker.execute(func, *args, **kwargs)

        # 附加 breaker 实例以便外部访问状态
        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        wrapper.breaker = breaker
        return wrapper

    import asyncio
    return decorator


# ========== 预定义熔断器实例 ==========

# Signal Arena API 熔断器
signal_arena_breaker = CircuitBreaker(
    "signal_arena",
    CircuitBreakerConfig(failure_threshold=3, recovery_timeout=120)
)

# MeYo 社区 API 熔断器
meyo_breaker = CircuitBreaker(
    "meyo",
    CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60)
)

# 百炼 API 熔断器
bailian_breaker = CircuitBreaker(
    "bailian",
    CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30)
)

# 全局熔断器注册表
_breakers: Dict[str, CircuitBreaker] = {
    "signal_arena": signal_arena_breaker,
    "meyo": meyo_breaker,
    "bailian": bailian_breaker,
}


def get_breaker(name: str) -> CircuitBreaker:
    """获取或创建命名熔断器"""
    if name not in _breakers:
        _breakers[name] = CircuitBreaker(name)
    return _breakers[name]


def get_all_breakers_status() -> Dict:
    """获取所有熔断器状态"""
    return {name: b.get_status() for name, b in _breakers.items()}
=======
"""
🦞 小龙虾网络 · API 熔断器
版本: V1.0 | 日期: 2026-06-28
功能: 防止外部 API 故障导致系统雪崩，支持自动降级
"""
import time
import functools
import logging
from enum import Enum
from typing import Callable, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CircuitBreaker")

class CircuitState(Enum):
    CLOSED = "CLOSED"      # 正常通行
    OPEN = "OPEN"          # 熔断，拒绝请求
    HALF_OPEN = "HALF_OPEN" # 半开，试探性放行

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60, fallback_fn: Callable = None):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.fallback_fn = fallback_fn
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("⚡ 熔断器进入半开状态，尝试恢复...")
            else:
                logger.warning("🚫 熔断器处于开启状态，拒绝请求。")
                if self.fallback_fn:
                    return self.fallback_fn()
                raise Exception("Circuit Breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            logger.error(f"❌ API 调用失败: {e}")
            if self.fallback_fn:
                return self.fallback_fn()
            raise

    def on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"🔥 失败次数达到 {self.failure_threshold}，熔断器开启！")

def circuit_breaker(failure_threshold=5, recovery_timeout=60, fallback=None):
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, fallback)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
>>>>>>> fbc3017db51a546a289ef16bd15ae36823f768d7
