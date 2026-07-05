#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障容错模块 (Fault Tolerance)

提供系统级可靠性基础设施：
- @retry 装饰器：可配置重试、退避、异常类型过滤
- HealthChecker：周期性节点心跳检测、超时判定、自动下线
- GracefulDegradation：功能降级策略注册表，模块不可用时自动降级到备用方案

参考：小龙虾网络论文 第七章 未来工作方向
"""

import time
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from dataclasses import dataclass, field
from functools import wraps

logger = logging.getLogger("fault_tolerance")
logger.setLevel(logging.INFO)


# ============================================================
# @retry 装饰器
# ============================================================

def retry(
    max_retries: int = 3,
    backoff: float = 2.0,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
):
    """
    指数退避重试装饰器。

    参数:
        max_retries: 最大重试次数（不含首次尝试）
        backoff: 退避乘数
        initial_delay: 初始延迟（秒）
        max_delay: 最大延迟上限（秒）
        jitter: 是否添加 ±25% 随机抖动
        exceptions: 触发重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt >= max_retries:
                        logger.error(
                            f"[retry] {func.__name__} 失败，已达最大重试次数 {max_retries}: {e}"
                        )
                        raise

                    # 计算退避延迟
                    current_delay = min(delay, max_delay)
                    if jitter:
                        import random
                        jitter_factor = 1.0 + random.uniform(-0.25, 0.25)
                        current_delay *= jitter_factor

                    logger.warning(
                        f"[retry] {func.__name__} 失败 (第 {attempt + 1}/{max_retries} 次重试)，"
                        f"{current_delay:.1f}s 后重试: {e}"
                    )
                    time.sleep(current_delay)
                    delay *= backoff

            # 理论上不会到达这里
            if last_exception:
                raise last_exception
        return wrapper
    return decorator


# ============================================================
# HealthChecker — 节点心跳检测
# ============================================================

@dataclass
class NodeHealth:
    """节点健康状态"""
    node_id: str
    is_alive: bool = True
    last_heartbeat: datetime = field(default_factory=datetime.now)
    consecutive_failures: int = 0
    status: str = "healthy"  # healthy / degraded / offline


class HealthChecker:
    """
    周期性节点心跳检测器。

    用法:
        checker = HealthChecker(heartbeat_timeout_s=30, check_interval_s=5)
        checker.register_node("qoder")
        checker.register_node("xiaochen")
        checker.start()  # 后台线程

        # 下游定期汇报心跳
        checker.report_heartbeat("qoder")

        # 查看状态
        checker.get_health("qoder")
        checker.get_all_health()

        checker.stop()
    """

    def __init__(
        self,
        heartbeat_timeout_s: float = 30.0,
        check_interval_s: float = 5.0,
        max_consecutive_failures: int = 3,
    ):
        """
        参数:
            heartbeat_timeout_s: 心跳超时时间（秒），超时判定为离线
            check_interval_s: 检查间隔（秒）
            max_consecutive_failures: 连续失败多少次后判定离线
        """
        self.heartbeat_timeout_s = heartbeat_timeout_s
        self.check_interval_s = check_interval_s
        self.max_consecutive_failures = max_consecutive_failures

        self._nodes: Dict[str, NodeHealth] = {}
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # 回调：当节点下线/恢复时触发
        self._on_offline_callbacks: List[Callable[[str], None]] = []
        self._on_recovery_callbacks: List[Callable[[str], None]] = []

    def register_node(self, node_id: str):
        """注册需要监控的节点"""
        with self._lock:
            if node_id not in self._nodes:
                self._nodes[node_id] = NodeHealth(node_id=node_id)
                logger.info(f"[HealthChecker] 注册节点: {node_id}")

    def unregister_node(self, node_id: str):
        """取消注册节点"""
        with self._lock:
            self._nodes.pop(node_id, None)
            logger.info(f"[HealthChecker] 取消注册: {node_id}")

    def report_heartbeat(self, node_id: str):
        """汇报心跳（由下游定期调用）"""
        with self._lock:
            if node_id not in self._nodes:
                self._nodes[node_id] = NodeHealth(node_id=node_id)

            node = self._nodes[node_id]
            node.last_heartbeat = datetime.now()
            node.consecutive_failures = 0

            if node.status == "offline":
                old_status = node.status
                node.status = "healthy"
                node.is_alive = True
                logger.info(f"[HealthChecker] 节点恢复: {node_id}")
                self._fire_recovery(node_id)

    def on_offline(self, callback: Callable[[str], None]):
        """注册节点下线回调"""
        self._on_offline_callbacks.append(callback)

    def on_recovery(self, callback: Callable[[str], None]):
        """注册节点恢复回调"""
        self._on_recovery_callbacks.append(callback)

    def _fire_offline(self, node_id: str):
        for cb in self._on_offline_callbacks:
            try:
                cb(node_id)
            except Exception as e:
                logger.error(f"[HealthChecker] 下线回调异常: {e}")

    def _fire_recovery(self, node_id: str):
        for cb in self._on_recovery_callbacks:
            try:
                cb(node_id)
            except Exception as e:
                logger.error(f"[HealthChecker] 恢复回调异常: {e}")

    def get_health(self, node_id: str) -> Optional[NodeHealth]:
        """获取单个节点健康状态"""
        with self._lock:
            return self._nodes.get(node_id)

    def get_all_health(self) -> Dict[str, NodeHealth]:
        """获取所有节点健康状态"""
        with self._lock:
            return dict(self._nodes)

    def get_offline_nodes(self) -> List[str]:
        """获取当前离线节点列表"""
        with self._lock:
            return [nid for nid, nh in self._nodes.items() if nh.status == "offline"]

    def get_healthy_nodes(self) -> List[str]:
        """获取当前健康节点列表"""
        with self._lock:
            return [nid for nid, nh in self._nodes.items() if nh.is_alive]

    def _check_loop(self):
        """后台检查循环"""
        while self._running:
            with self._lock:
                now = datetime.now()
                for node_id, node in list(self._nodes.items()):
                    elapsed = (now - node.last_heartbeat).total_seconds()
                    if elapsed > self.heartbeat_timeout_s:
                        node.consecutive_failures += 1
                        if node.consecutive_failures >= self.max_consecutive_failures:
                            if node.status != "offline":
                                node.status = "offline"
                                node.is_alive = False
                                logger.warning(
                                    f"[HealthChecker] 节点离线: {node_id} "
                                    f"(连续 {node.consecutive_failures} 次超时, "
                                    f"上次心跳 {elapsed:.0f}s 前)"
                                )
                                self._fire_offline(node_id)
                        elif node.status != "degraded":
                            node.status = "degraded"
                            logger.info(f"[HealthChecker] 节点性能退化: {node_id}")

            time.sleep(self.check_interval_s)

    def start(self):
        """启动后台检测线程"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._check_loop, daemon=True, name="health-checker")
        self._thread.start()
        logger.info("[HealthChecker] 后台检测已启动")

    def stop(self):
        """停止后台检测"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.check_interval_s * 2)
            self._thread = None
        logger.info("[HealthChecker] 后台检测已停止")

    def get_health_report(self) -> Dict[str, Any]:
        """生成健康报告"""
        with self._lock:
            total = len(self._nodes)
            healthy = sum(1 for nh in self._nodes.values() if nh.is_alive)
            offline = total - healthy

            return {
                "timestamp": datetime.now().isoformat(),
                "total_nodes": total,
                "healthy": healthy,
                "offline": offline,
                "offline_nodes": [nid for nid, nh in self._nodes.items() if not nh.is_alive],
                "details": {
                    nid: {
                        "status": nh.status,
                        "last_heartbeat": nh.last_heartbeat.isoformat(),
                        "consecutive_failures": nh.consecutive_failures,
                    }
                    for nid, nh in self._nodes.items()
                },
            }


# ============================================================
# GracefulDegradation — 功能降级策略注册表
# ============================================================

class GracefulDegradation:
    """
    功能降级策略注册表。

    当某模块不可用时，自动降级到备用方案。

    用法:
        gd = GracefulDegradation()

        # 注册降级策略
        gd.register(
            module="rl_orchestrator",
            fallback=lambda task: static_scheduler.schedule(task),
            description="RL-Orchestrator 不可用时使用静态调度"
        )

        # 尝试执行
        result = gd.try_execute(
            module="rl_orchestrator",
            primary=lambda: rl_orch.orchestrate(task),
            task=task
        )
    """

    @dataclass
    class _FallbackEntry:
        fallback: Callable
        description: str = ""
        enabled: bool = True
        call_count: int = 0
        last_used: Optional[datetime] = None

    def __init__(self):
        self._strategies: Dict[str, GracefulDegradation._FallbackEntry] = {}
        self._lock = threading.Lock()

    def register(self, module: str, fallback: Callable, description: str = ""):
        """
        注册降级策略。

        参数:
            module: 模块标识符（如 "rl_orchestrator"）
            fallback: 降级函数，接收与主函数相同的参数
            description: 降级策略描述
        """
        with self._lock:
            self._strategies[module] = self._FallbackEntry(
                fallback=fallback,
                description=description,
            )
            logger.info(f"[GracefulDegradation] 注册降级策略: {module} -> {description}")

    def unregister(self, module: str):
        """取消注册"""
        with self._lock:
            self._strategies.pop(module, None)

    def disable(self, module: str):
        """禁用某降级策略（直接 fail-fast）"""
        with self._lock:
            if module in self._strategies:
                self._strategies[module].enabled = False

    def enable(self, module: str):
        """启用某降级策略"""
        with self._lock:
            if module in self._strategies:
                self._strategies[module].enabled = True

    def try_execute(
        self,
        module: str,
        primary: Callable,
        *args,
        **kwargs,
    ) -> Any:
        """
        尝试执行主函数，失败时降级到备用方案。

        参数:
            module: 模块标识符
            primary: 主函数
            *args, **kwargs: 传递给主函数和降级函数的参数

        返回:
            主函数或降级函数的返回值

        异常:
            主函数和降级函数都失败时，抛出最后一次异常
        """
        # 先尝试主函数
        try:
            return primary(*args, **kwargs)
        except Exception as e:
            logger.warning(f"[GracefulDegradation] 主模块 [{module}] 失败: {e}")

        # 降级
        with self._lock:
            strategy = self._strategies.get(module)

        if not strategy or not strategy.enabled:
            logger.error(f"[GracefulDegradation] [{module}] 无可用降级策略")
            raise RuntimeError(f"Module [{module}] failed and no fallback available")

        try:
            logger.info(f"[GracefulDegradation] [{module}] 降级执行: {strategy.description}")
            result = strategy.fallback(*args, **kwargs)
            with self._lock:
                strategy.call_count += 1
                strategy.last_used = datetime.now()
            return result
        except Exception as fallback_error:
            logger.error(f"[GracefulDegradation] [{module}] 降级也失败: {fallback_error}")
            raise RuntimeError(
                f"Both primary and fallback failed for module [{module}]: {fallback_error}"
            ) from fallback_error

    def get_strategies(self) -> Dict[str, dict]:
        """获取所有注册的降级策略"""
        with self._lock:
            return {
                module: {
                    "description": s.description,
                    "enabled": s.enabled,
                    "call_count": s.call_count,
                    "last_used": s.last_used.isoformat() if s.last_used else None,
                }
                for module, s in self._strategies.items()
            }

    def get_report(self) -> Dict[str, Any]:
        """生成降级策略报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_strategies": len(self._strategies),
            "strategies": self.get_strategies(),
        }
