#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能优化工具 - 节点通信优化 + 内存分析
"""

import os
import json
import time
import sys
import resource
from datetime import datetime
from pathlib import Path


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, name="default"):
        self.name = name
        self.metrics = {
            "start_time": time.time(),
            "operations": [],
            "memory_samples": []
        }

    def record_operation(self, op_name, duration, details=None):
        """记录操作性能"""
        self.metrics["operations"].append({
            "name": op_name,
            "duration": duration,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def sample_memory(self):
        """采样内存使用"""
        usage = resource.getrusage(resource.RUSAGE_SELF)
        sample = {
            "rss_mb": usage.ru_maxrss / 1024,  # Linux: KB
            "user_time": usage.ru_utime,
            "system_time": usage.ru_stime,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics["memory_samples"].append(sample)
        return sample

    def get_report(self):
        """生成性能报告"""
        elapsed = time.time() - self.metrics["start_time"]
        ops = self.metrics["operations"]

        report = {
            "monitor": self.name,
            "elapsed_seconds": round(elapsed, 3),
            "total_operations": len(ops),
            "avg_operation_ms": round(
                sum(o["duration"] for o in ops) / max(len(ops), 1) * 1000, 2
            ),
            "slowest_operation": max(ops, key=lambda x: x["duration"]) if ops else None,
            "memory_peak_mb": max(
                (s["rss_mb"] for s in self.metrics["memory_samples"]), default=0
            ),
            "operations_detail": ops
        }
        return report


class NodeOptimizer:
    """节点通信优化器"""

    def __init__(self, batch_size=10, cache_ttl=300):
        self.batch_size = batch_size
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.stats = {"hits": 0, "misses": 0, "saves": 0}

    def get_cached(self, key):
        """获取缓存"""
        if key in self.cache:
            data, ts = self.cache[key]
            if time.time() - ts < self.cache_ttl:
                self.stats["hits"] += 1
                return data
            else:
                del self.cache[key]
        self.stats["misses"] += 1
        return None

    def set_cached(self, key, value):
        """设置缓存"""
        self.cache[key] = (value, time.time())
        self.stats["saves"] += 1

    def batch_process(self, items, processor):
        """批量处理"""
        results = []
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            results.extend(processor(batch))
        return results

    def get_stats(self):
        """获取统计"""
        total = self.stats["hits"] + self.stats["misses"]
        return {
            **self.stats,
            "hit_rate": round(self.stats["hits"] / max(total, 1) * 100, 1),
            "cache_size": len(self.cache)
        }


def benchmark_problem_loading():
    """基准测试：题库加载"""
    monitor = PerformanceMonitor("problem_loading")
    problems_dir = os.path.join(os.path.dirname(__file__), "problems")

    monitor.sample_memory()
    start = time.time()

    all_problems = []
    if os.path.exists(problems_dir):
        for root, dirs, files in os.walk(problems_dir):
            for f in files:
                if f.endswith('.json'):
                    with open(os.path.join(root, f), 'r') as fp:
                        data = json.load(fp)
                        all_problems.extend(data.get("problems", []))

    elapsed = time.time() - start
    monitor.record_operation("load_all_problems", elapsed, {"count": len(all_problems)})
    monitor.sample_memory()

    report = monitor.get_report()
    print(f"\n📊 题库加载性能:")
    print(f"  题目数: {len(all_problems)}")
    print(f"  加载时间: {elapsed*1000:.1f}ms")
    print(f"  内存峰值: {report['memory_peak_mb']:.1f}MB")
    return report


def benchmark_scheduler():
    """基准测试：调度器"""
    monitor = PerformanceMonitor("scheduler")

    # 模拟生成30天计划
    start = time.time()
    for day in range(30):
        plan = {
            "day": day + 1,
            "problems": [f"p-{i}" for i in range(10)],
            "game": True,
            "review": True
        }
    elapsed = time.time() - start
    monitor.record_operation("generate_30days_plan", elapsed)
    monitor.sample_memory()

    report = monitor.get_report()
    print(f"\n📊 调度器性能:")
    print(f"  30天计划生成: {elapsed*1000:.1f}ms")
    print(f"  日均: {elapsed/30*1000:.2f}ms")
    return report


def benchmark_node_communication():
    """基准测试：节点通信"""
    monitor = PerformanceMonitor("node_comm")
    optimizer = NodeOptimizer(batch_size=5, cache_ttl=60)

    # 测试缓存命中率
    start = time.time()
    for i in range(100):
        key = f"problem-{i % 20}"  # 20个唯一key，循环访问
        cached = optimizer.get_cached(key)
        if cached is None:
            optimizer.set_cached(key, {"id": key, "data": "x" * 50})
    elapsed = time.time() - start

    monitor.record_operation("100_cache_ops", elapsed)
    stats = optimizer.get_stats()

    print(f"\n📊 节点通信优化:")
    print(f"  100次操作: {elapsed*1000:.1f}ms")
    print(f"  缓存命中率: {stats['hit_rate']}%")
    print(f"  缓存大小: {stats['cache_size']}")
    return stats


def run_all_benchmarks():
    """运行所有基准测试"""
    print("=" * 50)
    print("🦞 小龙虾网络 · 性能基准测试")
    print("=" * 50)

    benchmark_problem_loading()
    benchmark_scheduler()
    benchmark_node_communication()

    print("\n" + "=" * 50)
    print("✅ 基准测试完成")
    print("=" * 50)


if __name__ == "__main__":
    run_all_benchmarks()
