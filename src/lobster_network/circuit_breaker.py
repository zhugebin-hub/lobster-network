#!/usr/bin/env python3
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
