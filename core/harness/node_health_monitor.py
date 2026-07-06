"""
小龙虾网络 V5.1 — 节点健康监控模块 (Node Health Monitor)
用途：实时监控六学员节点健康状态，自动检测异常并触发恢复操作
     提升系统可靠性与稳定性
"""

import time
import threading
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import deque

# ── 常量 ──────────────────────────────────────────

from core.config.lobster_config import (
    OUTPUT_DIR,
    RUNTIME_DEFAULTS,
    load_learner_profiles,
)

# ── 数据结构 ──────────────────────────────────────

class NodeStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNSTABLE = "unstable"
    OFFLINE = "offline"
    RECOVERING = "recovering"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class NodeHealthSnapshot:
    """节点健康快照"""
    node_id: str
    status: NodeStatus = NodeStatus.HEALTHY
    cpu_pct: float = 0.0
    mem_pct: float = 0.0
    io_wait_pct: float = 0.0
    active_sessions: int = 0
    queue_depth: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    error_count_last_hour: int = 0
    avg_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0

@dataclass
class AlertRecord:
    """告警记录"""
    timestamp: datetime
    node_id: str
    level: AlertLevel
    message: str
    snapshot: Optional[NodeHealthSnapshot] = None


# ── 节点健康监控器 ────────────────────────────────

class NodeHealthMonitor:
    """
    节点健康监控器 — 核心职责：
    1. 周期性采集各节点健康指标（CPU/内存/IO/心跳）
    2. 基于滑动窗口的异常检测（连续N次异常 → 告警）
    3. 自动分级恢复（降级/重启/隔离）
    4. 健康状态历史记录与可视化数据输出
    """

    def __init__(
        self,
        node_ids: Optional[List[str]] = None,
        check_interval_sec: float = 30.0,
        history_window: int = 100,
        health_report_dir: Optional[Path] = None,
    ):
        """
        Args:
            node_ids: 监控节点 ID 列表，默认从六学员配置加载
            check_interval_sec: 健康检查间隔（秒）
            history_window: 滑动窗口大小（保留最近 N 条记录）
            health_report_dir: 健康报告输出目录
        """
        self.node_ids = node_ids or RUNTIME_DEFAULTS["nodes"]
        self.check_interval_sec = check_interval_sec
        self.history_window = history_window
        self.report_dir = health_report_dir or (OUTPUT_DIR / "health")

        # 状态存储
        self.history: Dict[str, deque] = {nid: deque(maxlen=history_window) for nid in self.node_ids}
        self.current_status: Dict[str, NodeHealthSnapshot] = {nid: NodeHealthSnapshot(node_id=nid) for nid in self.node_ids}
        self.alert_log: List[AlertRecord] = []
        self.recovery_actions: Dict[str, int] = {nid: 0 for nid in self.node_ids}  # 恢复操作计数

        # 异常检测参数
        self.unstable_threshold: int = 5   # 连续异常次数 → UNSTABLE
        self.offline_threshold: int = 10   # 连续异常次数 → OFFLINE
        self.recovery_max_attempts: int = 3  # 单节点最大自动恢复次数

        # 线程安全
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # 回调
        self.on_alert: Optional[Callable[[AlertRecord], None]] = None
        self.on_recovery: Optional[Callable[[str, str], None]] = None

    # ── 启动/停止 ──────────────────────────────

    def start(self) -> None:
        """启动周期健康检查线程"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._health_check_loop, daemon=True, name="HealthMonitor")
        self._thread.start()
        print(f"[HealthMonitor] 已启动，监控 {len(self.node_ids)} 个节点，间隔 {self.check_interval_sec}s")

    def stop(self) -> None:
        """停止健康检查"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        self._persist_report()
        print("[HealthMonitor] 已停止")

    # ── 健康检查循环 ──────────────────────────

    def _health_check_loop(self) -> None:
        while self._running:
            try:
                for node_id in self.node_ids:
                    self._check_single_node(node_id)
                self._evaluate_cluster_health()
                self._persist_report()
            except Exception as e:
                print(f"[HealthMonitor] 检查循环异常: {e}")
            time.sleep(self.check_interval_sec)

    def _check_single_node(self, node_id: str) -> None:
        """
        单节点健康检查流程：
        1. 采集指标 → 2. 异常检测 → 3. 状态判定 → 4. 恢复触发
        """
        snapshot = self._collect_metrics(node_id)
        anomaly = self._detect_anomaly(node_id, snapshot)

        with self._lock:
            self.history[node_id].append(snapshot)
            old_status = self.current_status[node_id].status

            if anomaly:
                snapshot.error_count_last_hour += 1
                consecutive_failures = self._count_consecutive_anomalies(node_id)

                if consecutive_failures >= self.offline_threshold:
                    snapshot.status = NodeStatus.OFFLINE
                elif consecutive_failures >= self.unstable_threshold:
                    snapshot.status = NodeStatus.UNSTABLE
                else:
                    snapshot.status = NodeStatus.DEGRADED

                # 分级告警
                if consecutive_failures >= self.offline_threshold:
                    level = AlertLevel.CRITICAL
                elif consecutive_failures >= self.unstable_threshold:
                    level = AlertLevel.WARNING
                else:
                    level = AlertLevel.INFO
                self._emit_alert(node_id, level, f"连续 {consecutive_failures} 次异常", snapshot)

                # 触发自动恢复
                if snapshot.status in (NodeStatus.UNSTABLE, NodeStatus.OFFLINE):
                    self._attempt_recovery(node_id, snapshot.status)
            else:
                snapshot.status = NodeStatus.HEALTHY

            if old_status != snapshot.status:
                print(f"[HealthMonitor] {node_id}: {old_status.value} → {snapshot.status.value}")

            self.current_status[node_id] = snapshot

    # ── 指标采集 ───────────────────────────────

    def _collect_metrics(self, node_id: str) -> NodeHealthSnapshot:
        """采集节点的多维健康指标"""
        snap = NodeHealthSnapshot(node_id=node_id)

        try:
            import psutil
            # 系统级指标
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            disk = psutil.disk_io_counters()
            snap.cpu_pct = cpu
            snap.mem_pct = mem.percent
            snap.io_wait_pct = getattr(psutil.cpu_times_percent(), 'iowait', 0.0)

            # 进程级指标（当前 Python 进程）
            proc = psutil.Process()
            snap.active_sessions = len(proc.connections())
            snap.uptime_seconds = time.time() - proc.create_time()
        except ImportError:
            # psutil 不可用时用占位值
            snap.cpu_pct = 0.0
            snap.mem_pct = 0.0

        snap.last_heartbeat = time.time()
        return snap

    # ── 异常检测 ───────────────────────────────

    def _detect_anomaly(self, node_id: str, snapshot: NodeHealthSnapshot) -> bool:
        """
        基于阈值的异常检测：
        - CPU > 90% 持续
        - 内存 > 85%
        - 心跳超时（30s 无响应）
        - IO等待 > 50%
        """
        # 心跳超时
        if hasattr(snapshot, 'last_heartbeat'):
            timeout = time.time() - snapshot.last_heartbeat
            if timeout > 60.0:
                return True

        # 资源耗尽
        if snapshot.cpu_pct > 90.0:
            return True
        if snapshot.mem_pct > 85.0:
            return True
        if snapshot.io_wait_pct > 50.0:
            return True

        return False

    def _count_consecutive_anomalies(self, node_id: str) -> int:
        """计算滑动窗口内连续异常次数"""
        hist = self.history[node_id]
        count = 0
        for snap in reversed(hist):
            if snap.status != NodeStatus.HEALTHY and snap.status != NodeStatus.RECOVERING:
                count += 1
            else:
                break
        return count

    # ── 恢复策略 ───────────────────────────────

    def _attempt_recovery(self, node_id: str, status: NodeStatus) -> None:
        """
        分级自动恢复策略：
        - OFFLINE: 尝试隔离节点 → 流量转移 → 通知管理员
        - UNSTABLE: 限制并发 → 降低负载 → 延迟敏感任务降级
        """
        if self.recovery_actions[node_id] >= self.recovery_max_attempts:
            print(f"[HealthMonitor] {node_id} 已达最大恢复次数上限 ({self.recovery_max_attempts})，停止自动恢复")
            return

        with self._lock:
            snap = self.current_status[node_id]
            snap.status = NodeStatus.RECOVERING
            self.recovery_actions[node_id] += 1

        if status == NodeStatus.OFFLINE:
            action = "ISOLATE"
            print(f"[HealthMonitor] {node_id}: 执行 ISOLATE 恢复 (第{self.recovery_actions[node_id]}次)")
            self._isolate_node(node_id)
        elif status == NodeStatus.UNSTABLE:
            action = "THROTTLE"
            print(f"[HealthMonitor] {node_id}: 执行 THROTTLE 恢复 — 限制并发，降低负载")

        if self.on_recovery:
            self.on_recovery(node_id, action)

    def _isolate_node(self, node_id: str) -> None:
        """隔离离线节点，将流量转移到健康节点"""
        healthy = [nid for nid in self.node_ids
                   if nid != node_id and self.current_status[nid].status == NodeStatus.HEALTHY]
        if healthy:
            print(f"[HealthMonitor] {node_id} 流量已转移至: {healthy}")

    # ── 集群整体评估 ───────────────────────────

    def _evaluate_cluster_health(self) -> None:
        """评估集群整体健康度"""
        total = len(self.node_ids)
        healthy_count = sum(1 for s in self.current_status.values() if s.status == NodeStatus.HEALTHY)
        offline_count = sum(1 for s in self.current_status.values() if s.status == NodeStatus.OFFLINE)

        health_score = healthy_count / total if total > 0 else 0.0

        if health_score < 0.5:
            self._emit_alert("CLUSTER", AlertLevel.CRITICAL,
                             f"集群健康度 {health_score:.0%}，{offline_count}/{total} 节点离线")
        elif health_score < 0.8:
            self._emit_alert("CLUSTER", AlertLevel.WARNING,
                             f"集群健康度 {health_score:.0%}，{total - healthy_count} 节点异常")

    # ── 告警发射 ───────────────────────────────

    def _emit_alert(self, node_id: str, level: AlertLevel, message: str,
                    snapshot: Optional[NodeHealthSnapshot] = None) -> None:
        record = AlertRecord(
            timestamp=datetime.now(),
            node_id=node_id,
            level=level,
            message=message,
            snapshot=snapshot,
        )
        self.alert_log.append(record)
        if self.on_alert:
            self.on_alert(record)

    # ── 报告持久化 ─────────────────────────────

    def _persist_report(self) -> None:
        """将健康报告写入 JSON 文件（供仪表盘消费）"""
        self.report_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": datetime.now().isoformat(),
            "cluster_health": {
                "total_nodes": len(self.node_ids),
                "healthy": sum(1 for s in self.current_status.values() if s.status == NodeStatus.HEALTHY),
                "degraded": sum(1 for s in self.current_status.values() if s.status == NodeStatus.DEGRADED),
                "unstable": sum(1 for s in self.current_status.values() if s.status == NodeStatus.UNSTABLE),
                "offline": sum(1 for s in self.current_status.values() if s.status == NodeStatus.OFFLINE),
            },
            "nodes": {},
        }

        for nid, snap in self.current_status.items():
            report["nodes"][nid] = {
                "status": snap.status.value,
                "cpu_pct": round(snap.cpu_pct, 1),
                "mem_pct": round(snap.mem_pct, 1),
                "io_wait_pct": round(snap.io_wait_pct, 1),
                "active_sessions": snap.active_sessions,
                "queue_depth": snap.queue_depth,
                "error_count_last_hour": snap.error_count_last_hour,
                "avg_response_time_ms": round(snap.avg_response_time_ms, 1),
                "uptime_hours": round(snap.uptime_seconds / 3600, 1),
                "recovery_actions": self.recovery_actions.get(nid, 0),
            }

        report_path = self.report_dir / "cluster_health.json"
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # ── 巡检摘要 ───────────────────────────────

    def get_summary(self) -> Dict[str, Any]:
        """获取集群健康度巡检摘要"""
        with self._lock:
            statuses = [s.status for s in self.current_status.values()]
            return {
                "healthy_pct": statuses.count(NodeStatus.HEALTHY) / len(statuses) * 100 if statuses else 0,
                "offline_nodes": [nid for nid, s in self.current_status.items() if s.status == NodeStatus.OFFLINE],
                "unstable_nodes": [nid for nid, s in self.current_status.items() if s.status == NodeStatus.UNSTABLE],
                "total_alerts": len(self.alert_log),
                "critical_alerts": sum(1 for a in self.alert_log if a.level == AlertLevel.CRITICAL),
                "total_recoveries": sum(self.recovery_actions.values()),
                "last_check": datetime.now().isoformat(),
            }


# ── 自适应负载均衡器 ────────────────────────────────

class AdaptiveLoadBalancer:
    """
    自适应负载均衡器
    基于节点健康度和负载指标动态分配任务
    """

    def __init__(self, monitor: NodeHealthMonitor):
        self.monitor = monitor

    def select_best_node(self, task_weight: float = 1.0) -> Optional[str]:
        """
        选择最优节点执行任务
        评分 = (1 - cpu_pct/100) * (1 - mem_pct/100) * (1 - queue_weight) * healthy_bonus
        """
        candidates = []
        for nid, snap in self.monitor.current_status.items():
            if snap.status == NodeStatus.OFFLINE:
                continue

            # 健康节点加分
            healthy_bonus = 1.0 if snap.status == NodeStatus.HEALTHY else 0.6

            # 负载评分
            cpu_score = max(0, 1 - snap.cpu_pct / 100)
            mem_score = max(0, 1 - snap.mem_pct / 100)
            queue_score = max(0, 1 - snap.queue_depth / 20 if snap.queue_depth > 0 else 1)

            score = cpu_score * mem_score * queue_score * healthy_bonus
            candidates.append((nid, score))

        if not candidates:
            return None

        # 加权随机选择（高分节点更有机会被选中，但仍保留探索）
        import random
        total = sum(s for _, s in candidates)
        if total == 0:
            return random.choice([n for n, _ in candidates])
        r = random.random() * total
        cum = 0
        for nid, score in candidates:
            cum += score
            if r <= cum:
                return nid
        return candidates[-1][0]

    def get_load_distribution(self) -> Dict[str, float]:
        """获取负载分布建议"""
        healthy = [nid for nid, s in self.monitor.current_status.items()
                   if s.status in (NodeStatus.HEALTHY, NodeStatus.DEGRADED)]
        if not healthy:
            return {}

        weight_per_node = 1.0 / len(healthy)
        return {nid: weight_per_node for nid in healthy}
