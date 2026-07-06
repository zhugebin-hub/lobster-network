#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资源管理器 (Resource Manager)

提升算力利用效率的基础设施：
- ConnectionPool: MQTT/HTTP 连接池
- TaskBatcher: 任务批处理器
- LRUCache: Agent Card 缓存、能力画像缓存

参考：小龙虾网络论文 6.1 系统局限性、6.3 未来工作方向
"""

import time
import threading
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Callable, Dict, Generic, List, Optional, Tuple, TypeVar
from dataclasses import dataclass, field

logger = logging.getLogger("resource_manager")
logger.setLevel(logging.INFO)

T = TypeVar("T")


# ============================================================
# ConnectionPool — MQTT/HTTP 连接池
# ============================================================

@dataclass
class _PooledConnection:
    conn_id: str
    created_at: float
    last_used: float
    in_use: bool = False


class ConnectionPool:
    """
    连接池 — 管理 MQTT/HTTP 长连接。

    用法:
        pool = ConnectionPool(max_connections=20, idle_timeout_s=300)

        # 获取连接
        conn_id = pool.acquire()
        try:
            # 使用连接...
            pass
        finally:
            pool.release(conn_id)
    """

    def __init__(
        self,
        max_connections: int = 20,
        idle_timeout_s: float = 300.0,
        connection_factory: Optional[Callable[[], str]] = None,
    ):
        """
        参数:
            max_connections: 最大连接数
            idle_timeout_s: 空闲超时（秒），超时自动回收
            connection_factory: 连接创建工厂函数（返回连接ID）
        """
        self.max_connections = max_connections
        self.idle_timeout_s = idle_timeout_s
        self._factory = connection_factory or (lambda: f"conn-{id(self)}-{time.time()}")

        self._pool: List[_PooledConnection] = []
        self._lock = threading.Lock()
        self._counter = 0

        # 后台回收线程
        self._running = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop, daemon=True, name="conn-pool-cleanup"
        )
        self._cleanup_thread.start()

    def acquire(self, timeout_s: float = 10.0) -> str:
        """
        获取一个可用连接。

        如果池中有空闲连接直接返回；如果没有空闲且未达到上限则新建；
        如果已达上限且全部在使用中则等待。
        """
        deadline = time.time() + timeout_s

        while time.time() < deadline:
            with self._lock:
                # 先找空闲连接
                for conn in self._pool:
                    if not conn.in_use:
                        # 检查是否超时
                        if time.time() - conn.last_used < self.idle_timeout_s:
                            conn.in_use = True
                            conn.last_used = time.time()
                            logger.debug(f"[ConnectionPool] 复用连接: {conn.conn_id}")
                            return conn.conn_id

                # 清理已超时连接
                self._pool = [
                    c for c in self._pool
                    if c.in_use or (time.time() - c.last_used < self.idle_timeout_s)
                ]

                # 如果未达上限，新建连接
                if len(self._pool) < self.max_connections:
                    conn_id = self._factory()
                    self._counter += 1
                    conn = _PooledConnection(
                        conn_id=conn_id,
                        created_at=time.time(),
                        last_used=time.time(),
                        in_use=True,
                    )
                    self._pool.append(conn)
                    logger.info(f"[ConnectionPool] 新建连接 {conn_id} (池容量: {len(self._pool)}/{self.max_connections})")
                    return conn_id

            # 等待 100ms 后重试
            time.sleep(0.1)

        raise TimeoutError(
            f"[ConnectionPool] 获取连接超时 ({timeout_s}s)，"
            f"当前池: {len(self._pool)}/{self.max_connections}"
        )

    def release(self, conn_id: str):
        """释放连接回池"""
        with self._lock:
            for conn in self._pool:
                if conn.conn_id == conn_id:
                    conn.in_use = False
                    conn.last_used = time.time()
                    logger.debug(f"[ConnectionPool] 释放连接: {conn_id}")
                    return
        logger.warning(f"[ConnectionPool] 连接 {conn_id} 不在池中")

    def _cleanup_loop(self):
        """后台清理过期连接"""
        while self._running:
            time.sleep(30)  # 每 30s 检查一次
            with self._lock:
                now = time.time()
                before = len(self._pool)
                self._pool = [
                    c for c in self._pool
                    if c.in_use or (now - c.last_used < self.idle_timeout_s)
                ]
                removed = before - len(self._pool)
                if removed > 0:
                    logger.info(f"[ConnectionPool] 清理 {removed} 个空闲连接")

    def get_stats(self) -> Dict[str, Any]:
        """获取连接池统计"""
        with self._lock:
            total = len(self._pool)
            in_use = sum(1 for c in self._pool if c.in_use)
            return {
                "total_connections": total,
                "in_use": in_use,
                "idle": total - in_use,
                "max_connections": self.max_connections,
                "utilization_pct": round(in_use / max(self.max_connections, 1) * 100, 1),
            }

    def shutdown(self):
        """关闭连接池"""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
        logger.info("[ConnectionPool] 已关闭")


# ============================================================
# TaskBatcher — 任务批处理器
# ============================================================

class TaskBatcher(Generic[T]):
    """
    任务批处理器 — 按时间窗口或条数攒批。

    用法:
        def process_batch(items: List[str]) -> List[str]:
            return [f"processed: {item}" for item in items]

        batcher = TaskBatcher(
            batch_size=50,
            time_window_s=0.1,
            processor=process_batch,
        )
        batcher.start()

        # 添加任务（不会立即处理）
        batcher.add("task_1")
        batcher.add("task_2")

        # 手动触发
        results = batcher.flush()

        batcher.stop()
    """

    def __init__(
        self,
        batch_size: int = 50,
        time_window_s: float = 0.1,
        processor: Optional[Callable[[List[T]], List[Any]]] = None,
        max_queue_size: int = 10000,
    ):
        """
        参数:
            batch_size: 攒批条数阈值
            time_window_s: 时间窗口（秒），窗口到期自动攒批
            processor: 批处理函数
            max_queue_size: 最大队列长度
        """
        self.batch_size = batch_size
        self.time_window_s = time_window_s
        self.processor = processor or (lambda items: items)
        self.max_queue_size = max_queue_size

        self._queue: List[T] = []
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # 统计
        self._total_processed = 0
        self._total_batches = 0
        self._total_dropped = 0

    def add(self, item: T):
        """添加任务到批处理队列"""
        with self._lock:
            if len(self._queue) >= self.max_queue_size:
                self._total_dropped += 1
                logger.warning(f"[TaskBatcher] 队列已满 ({self.max_queue_size})，丢弃任务")
                return
            self._queue.append(item)

        # 如果达到批量阈值，触发处理
        if len(self._queue) >= self.batch_size:
            self.flush()

    def flush(self) -> List[Any]:
        """立即清空队列并处理"""
        with self._lock:
            if not self._queue:
                return []
            batch = list(self._queue)
            self._queue.clear()

        try:
            results = self.processor(batch)
            self._total_processed += len(batch)
            self._total_batches += 1
            logger.debug(f"[TaskBatcher] 处理批次 #{self._total_batches}: {len(batch)} 条")
            return results
        except Exception as e:
            logger.error(f"[TaskBatcher] 批处理失败: {e}")
            raise

    def _timer_loop(self):
        """后台定时刷新循环"""
        while self._running:
            time.sleep(self.time_window_s)
            with self._lock:
                if self._queue:
                    try:
                        batch = list(self._queue)
                        self._queue.clear()
                    except Exception:
                        continue

                    try:
                        self.processor(batch)
                        self._total_processed += len(batch)
                        self._total_batches += 1
                    except Exception as e:
                        logger.error(f"[TaskBatcher] 定时批处理失败: {e}")

    def start(self):
        """启动后台定时批处理"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._timer_loop, daemon=True, name="task-batcher")
        self._thread.start()
        logger.info(f"[TaskBatcher] 已启动 (batch={self.batch_size}, window={self.time_window_s}s)")

    def stop(self):
        """停止批处理器（自动 flush 剩余任务）"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.time_window_s * 3)
            self._thread = None

        # 处理剩余任务
        remaining = self.flush()
        if remaining:
            logger.info(f"[TaskBatcher] 停止时处理剩余 {len(remaining)} 条任务")

        logger.info(f"[TaskBatcher] 已停止 (累计: {self._total_processed} 条, {self._total_batches} 批)")

    def get_stats(self) -> Dict[str, Any]:
        """获取批处理统计"""
        with self._lock:
            return {
                "queue_size": len(self._queue),
                "total_processed": self._total_processed,
                "total_batches": self._total_batches,
                "total_dropped": self._total_dropped,
                "batch_size": self.batch_size,
                "time_window_s": self.time_window_s,
            }


# ============================================================
# LRUCache — 带 TTL 的 LRU 缓存
# ============================================================

class LRUCache(Generic[T]):
    """
    LRU 缓存 — 用于 Agent Card 缓存、能力画像缓存。

    用法:
        cache = LRUCache[str](capacity=1000, ttl_s=600)

        cache.put("agent_qoder", agent_card_json)
        card = cache.get("agent_qoder")

        stats = cache.get_stats()
    """

    @dataclass
    class _CacheEntry:
        value: Any
        created_at: float
        last_accessed: float

    def __init__(self, capacity: int = 1000, ttl_s: float = 600.0):
        """
        参数:
            capacity: 最大缓存条目数
            ttl_s: 缓存过期时间（秒）
        """
        self.capacity = capacity
        self.ttl_s = ttl_s

        self._cache: OrderedDict = OrderedDict()
        self._lock = threading.Lock()

        # 统计
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._expirations = 0

    def get(self, key: str) -> Optional[T]:
        """获取缓存值，不存在或已过期返回 None"""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None

            # 检查 TTL
            if time.time() - entry.created_at > self.ttl_s:
                self._cache.pop(key, None)
                self._expirations += 1
                self._misses += 1
                return None

            # 移动到末尾（LRU 最近使用）
            self._cache.move_to_end(key)
            entry.last_accessed = time.time()
            self._hits += 1
            return entry.value

    def put(self, key: str, value: T):
        """写入缓存"""
        with self._lock:
            # 如果已存在，更新
            if key in self._cache:
                self._cache.move_to_end(key)

            now = time.time()
            self._cache[key] = self._CacheEntry(
                value=value,
                created_at=now,
                last_accessed=now,
            )

            # 淘汰最久未使用的
            while len(self._cache) > self.capacity:
                oldest_key, _ = self._cache.popitem(last=False)
                self._evictions += 1
                logger.debug(f"[LRUCache] 淘汰: {oldest_key}")

            logger.debug(f"[LRUCache] put: {key} (共 {len(self._cache)}/{self.capacity})")

    def invalidate(self, key: str):
        """主动失效某缓存项"""
        with self._lock:
            self._cache.pop(key, None)
            logger.debug(f"[LRUCache] invalidate: {key}")

    def invalidate_pattern(self, pattern: str):
        """按前缀模式失效"""
        with self._lock:
            to_remove = [k for k in self._cache if k.startswith(pattern)]
            for k in to_remove:
                self._cache.pop(k, None)
            if to_remove:
                logger.debug(f"[LRUCache] invalidate_pattern '{pattern}': {len(to_remove)} 条")

    def clear(self):
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._expirations = 0
            logger.info("[LRUCache] 已清空")

    def contains(self, key: str) -> bool:
        """检查 key 是否存在且未过期"""
        return self.get(key) is not None

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / max(total_requests, 1)

            return {
                "size": len(self._cache),
                "capacity": self.capacity,
                "ttl_s": self.ttl_s,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "evictions": self._evictions,
                "expirations": self._expirations,
            }


class ResourceManager:
    """资源管理聚合门面，统一暴露连接池 + 任务批处理 + LRU 缓存"""

    def __init__(self):
        self.pool = ConnectionPool(max_connections=10)
        self.batcher = TaskBatcher(batch_size=50, time_window_s=5.0)
        self.cache = LRUCache[str](capacity=1000, ttl_s=300)

    def get_stats(self):
        return {
            "pool": self.pool.get_stats(),
            "batcher": self.batcher.get_stats() if hasattr(self.batcher, 'get_stats') else {},
            "cache": self.cache.stats(),
        }

    def shutdown(self):
        self.pool.shutdown()
        if hasattr(self.batcher, 'flush'):
            self.batcher.flush()


def get_resource_manager() -> ResourceManager:
    """工厂函数：返回 ResourceManager 聚合实例"""
    return ResourceManager()
