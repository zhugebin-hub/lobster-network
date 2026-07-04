#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可观测性指标采集器 (Metrics Collector)

采集四类指标：
- Agent 指标：消息数、任务完成数、准确率、平均响应时间、活跃度
- 网络指标：消息吞吐量、活跃节点数、延迟分布、可用率
- 学习指标：解题数、正确率、对局数、等级变化
- 经济指标：LBC 余额、交易量、市场活跃度

支持：
- 1min / 5min / 15min 滚动窗口聚合
- Prometheus 格式导出
- 控制台 Rich 表格输出

参考：小龙虾网络第四阶段优化部署报告
"""

import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict, deque
from threading import Lock


# ============================================================
# 日志与存储
# ============================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("metrics_collector")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(DATA_DIR / "metrics.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_handler)


# ============================================================
# 数据模型
# ============================================================

@dataclass
class AgentMetrics:
    """Agent 指标快照"""
    agent_id: str
    messages_sent: int = 0
    messages_received: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_response_time_ms: float = 0.0
    response_count: int = 0
    last_active: str = ""
    sessions_count: int = 0

    @property
    def accuracy(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        return self.tasks_completed / max(total, 1)

    @property
    def avg_response_time_ms(self) -> float:
        return self.total_response_time_ms / max(self.response_count, 1)

    @property
    def activity_score(self) -> float:
        """活跃度 (0-1)：基于最近 24h 内的消息量估算"""
        return min(1.0, (self.messages_sent + self.messages_received) / 100.0)


@dataclass
class NetworkMetrics:
    """网络指标快照"""
    total_messages: int = 0
    active_nodes: int = 0
    total_nodes: int = 0
    latency_samples: List[float] = field(default_factory=list)
    uptime_seconds: float = 0.0
    downtime_seconds: float = 0.0

    @property
    def throughput_per_minute(self) -> float:
        return self.total_messages / max(self.uptime_seconds / 60.0, 1.0)

    @property
    def avg_latency_ms(self) -> float:
        if not self.latency_samples:
            return 0.0
        return sum(self.latency_samples) / len(self.latency_samples)

    @property
    def p95_latency_ms(self) -> float:
        if not self.latency_samples:
            return 0.0
        sorted_samples = sorted(self.latency_samples)
        idx = int(len(sorted_samples) * 0.95)
        return sorted_samples[min(idx, len(sorted_samples) - 1)]

    @property
    def availability(self) -> float:
        total = self.uptime_seconds + self.downtime_seconds
        return self.uptime_seconds / max(total, 1.0)


@dataclass
class LearningMetrics:
    """学习指标快照"""
    agent_id: str
    problems_attempted: int = 0
    problems_correct: int = 0
    games_played: int = 0
    games_won: int = 0
    current_level: int = 1
    level_changes: int = 0
    domain: str = ""

    @property
    def accuracy(self) -> float:
        return self.problems_correct / max(self.problems_attempted, 1)

    @property
    def win_rate(self) -> float:
        return self.games_won / max(self.games_played, 1)


@dataclass
class EconomyMetrics:
    """经济指标快照"""
    agent_id: str
    lbc_balance: float = 0.0
    total_earned: float = 0.0
    total_spent: float = 0.0
    transactions_count: int = 0
    market_listings: int = 0
    market_trades: int = 0


# ============================================================
# MetricsCollector 主类
# ============================================================

class MetricsCollector:
    """
    可观测性指标采集器

    用法:
        collector = MetricsCollector()
        collector.record_agent_message("xiaochen", "sent", latency_ms=45.0)
        collector.record_agent_task("qoder", success=True, response_time_ms=230.0)
        collector.record_learning("xiaochen", problems=10, correct=8, games=2, wins=1)
        collector.record_economy("qoder", balance=100.0, earned=15.0)

        print(collector.render_table())
        print(collector.export_prometheus())
    """

    def __init__(self):
        self._lock = Lock()

        # Agent 指标
        self.agents: Dict[str, AgentMetrics] = {}

        # 网络指标
        self.network = NetworkMetrics()
        self.network.uptime_seconds = 0.0
        self._start_time = time.time()

        # 学习指标
        self.learning: Dict[str, LearningMetrics] = {}

        # 经济指标
        self.economy: Dict[str, EconomyMetrics] = {}

        # 滚动窗口采样（用于延迟分布、吞吐量）
        self._latency_window_1m: deque = deque(maxlen=100)
        self._latency_window_5m: deque = deque(maxlen=500)
        self._latency_window_15m: deque = deque(maxlen=1500)

        # 分钟级吞吐量统计
        self._minute_message_counts: Dict[str, int] = {}

        logger.info("MetricsCollector 初始化完成")

    # ---- Agent 指标 ----

    def record_agent_message(self, agent_id: str, direction: str, latency_ms: float = 0.0):
        """记录 Agent 消息"""
        with self._lock:
            agent = self._ensure_agent(agent_id)
            if direction == "sent":
                agent.messages_sent += 1
            else:
                agent.messages_received += 1
            if latency_ms > 0:
                agent.total_response_time_ms += latency_ms
                agent.response_count += 1
            agent.last_active = datetime.now().isoformat()

            self.network.total_messages += 1
            self._add_latency(latency_ms)

            minute_key = datetime.now().strftime("%Y-%m-%d %H:%M")
            self._minute_message_counts[minute_key] = self._minute_message_counts.get(minute_key, 0) + 1

    def record_agent_task(self, agent_id: str, success: bool, response_time_ms: float = 0.0):
        """记录 Agent 任务完成"""
        with self._lock:
            agent = self._ensure_agent(agent_id)
            if success:
                agent.tasks_completed += 1
            else:
                agent.tasks_failed += 1
            if response_time_ms > 0:
                agent.total_response_time_ms += response_time_ms
                agent.response_count += 1
            agent.last_active = datetime.now().isoformat()

    def record_agent_session(self, agent_id: str):
        """记录 Agent 会话"""
        with self._lock:
            agent = self._ensure_agent(agent_id)
            agent.sessions_count += 1

    def _ensure_agent(self, agent_id: str) -> AgentMetrics:
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentMetrics(agent_id=agent_id)
        return self.agents[agent_id]

    # ---- 网络指标 ----

    def record_latency(self, latency_ms: float):
        """记录网络延迟"""
        with self._lock:
            self._add_latency(latency_ms)

    def record_node_event(self, online: bool):
        """记录节点上下线"""
        with self._lock:
            if online:
                self.network.active_nodes += 1
                self.network.total_nodes = max(self.network.total_nodes, self.network.active_nodes)
            else:
                self.network.active_nodes = max(0, self.network.active_nodes - 1)

    def _add_latency(self, latency_ms: float):
        if latency_ms > 0:
            self._latency_window_1m.append(latency_ms)
            self._latency_window_5m.append(latency_ms)
            self._latency_window_15m.append(latency_ms)

    # ---- 学习指标 ----

    def record_learning(
        self,
        agent_id: str,
        problems: int = 0,
        correct: int = 0,
        games: int = 0,
        wins: int = 0,
        domain: str = "",
    ):
        """记录学习活动"""
        with self._lock:
            if agent_id not in self.learning:
                self.learning[agent_id] = LearningMetrics(agent_id=agent_id, domain=domain)
            lm = self.learning[agent_id]
            lm.problems_attempted += problems
            lm.problems_correct += correct
            lm.games_played += games
            lm.games_won += wins
            if domain:
                lm.domain = domain

    def record_level_change(self, agent_id: str, from_level: int, to_level: int):
        """记录等级变化"""
        with self._lock:
            if agent_id not in self.learning:
                self.learning[agent_id] = LearningMetrics(agent_id=agent_id)
            lm = self.learning[agent_id]
            lm.current_level = to_level
            lm.level_changes += 1

    # ---- 经济指标 ----

    def record_economy(
        self,
        agent_id: str,
        balance: float = 0.0,
        earned: float = 0.0,
        spent: float = 0.0,
        transactions: int = 0,
    ):
        """记录经济活动"""
        with self._lock:
            if agent_id not in self.economy:
                self.economy[agent_id] = EconomyMetrics(agent_id=agent_id)
            em = self.economy[agent_id]
            em.lbc_balance = balance
            em.total_earned += earned
            em.total_spent += spent
            em.transactions_count += transactions

    def record_market_activity(self, agent_id: str, listing: bool = False, trade: bool = False):
        """记录市场活动"""
        with self._lock:
            if agent_id not in self.economy:
                self.economy[agent_id] = EconomyMetrics(agent_id=agent_id)
            em = self.economy[agent_id]
            if listing:
                em.market_listings += 1
            if trade:
                em.market_trades += 1

    # ---- 快照采集 ----

    def get_agent_snapshot(self, agent_id: str) -> Optional[dict]:
        """获取单个 Agent 指标快照"""
        agent = self.agents.get(agent_id)
        if not agent:
            return None
        return {
            "agent_id": agent.agent_id,
            "messages": {"sent": agent.messages_sent, "received": agent.messages_received},
            "tasks": {"completed": agent.tasks_completed, "failed": agent.tasks_failed},
            "accuracy": round(agent.accuracy, 3),
            "avg_response_time_ms": round(agent.avg_response_time_ms, 1),
            "activity_score": round(agent.activity_score, 3),
            "sessions": agent.sessions_count,
            "last_active": agent.last_active,
        }

    def get_network_snapshot(self) -> dict:
        """获取网络指标快照"""
        elapsed = time.time() - self._start_time
        self.network.uptime_seconds = elapsed

        return {
            "total_messages": self.network.total_messages,
            "active_nodes": self.network.active_nodes,
            "total_nodes": self.network.total_nodes,
            "throughput_per_min": round(self.network.throughput_per_minute, 2),
            "latency": {
                "avg_ms": round(self.network.avg_latency_ms, 1),
                "p95_ms": round(self.network.p95_latency_ms, 1),
            },
            "availability_pct": round(self.network.availability * 100, 2),
            "uptime_hours": round(elapsed / 3600.0, 1),
        }

    def get_learning_snapshot(self) -> List[dict]:
        """获取学习指标快照"""
        return [
            {
                "agent_id": lm.agent_id,
                "domain": lm.domain,
                "problems": f"{lm.problems_correct}/{lm.problems_attempted}",
                "accuracy": round(lm.accuracy, 3),
                "games": f"{lm.games_won}/{lm.games_played}",
                "win_rate": round(lm.win_rate, 3),
                "level": f"{lm.current_level} (changed {lm.level_changes}x)",
            }
            for lm in self.learning.values()
        ]

    def get_economy_snapshot(self) -> List[dict]:
        """获取经济指标快照"""
        return [
            {
                "agent_id": em.agent_id,
                "lbc_balance": round(em.lbc_balance, 2),
                "total_earned": round(em.total_earned, 2),
                "total_spent": round(em.total_spent, 2),
                "transactions": em.transactions_count,
                "market": f"listings={em.market_listings}/trades={em.market_trades}",
            }
            for em in self.economy.values()
        ]

    def get_aggregated_metrics(self) -> dict:
        """聚合所有指标（1min/5min/15min 窗口）"""
        return {
            "agent_count": len(self.agents),
            "network": self.get_network_snapshot(),
            "agents": [self.get_agent_snapshot(aid) for aid in self.agents],
            "learning": self.get_learning_snapshot(),
            "economy": self.get_economy_snapshot(),
            "rolling_windows": {
                "1min": {
                    "latency_avg_ms": round(sum(self._latency_window_1m) / max(len(self._latency_window_1m), 1), 1),
                    "sample_count": len(self._latency_window_1m),
                },
                "5min": {
                    "latency_avg_ms": round(sum(self._latency_window_5m) / max(len(self._latency_window_5m), 1), 1),
                    "sample_count": len(self._latency_window_5m),
                },
                "15min": {
                    "latency_avg_ms": round(sum(self._latency_window_15m) / max(len(self._latency_window_15m), 1), 1),
                    "sample_count": len(self._latency_window_15m),
                },
            },
        }

    # ---- 导出 ----

    def export_prometheus(self) -> str:
        """导出 Prometheus 格式指标"""
        lines = []
        lines.append("# HELP lobster_agent_messages_total Total agent messages")
        lines.append("# TYPE lobster_agent_messages_total counter")
        for agent in self.agents.values():
            lines.append(f'lobster_agent_messages_total{{agent="{agent.agent_id}",direction="sent"}} {agent.messages_sent}')
            lines.append(f'lobster_agent_messages_total{{agent="{agent.agent_id}",direction="received"}} {agent.messages_received}')

        lines.append("# HELP lobster_agent_tasks_total Total agent tasks")
        lines.append("# TYPE lobster_agent_tasks_total counter")
        for agent in self.agents.values():
            lines.append(f'lobster_agent_tasks_total{{agent="{agent.agent_id}",status="completed"}} {agent.tasks_completed}')
            lines.append(f'lobster_agent_tasks_total{{agent="{agent.agent_id}",status="failed"}} {agent.tasks_failed}')

        lines.append("# HELP lobster_network_messages_total Total network messages")
        lines.append("# TYPE lobster_network_messages_total counter")
        lines.append(f"lobster_network_messages_total {self.network.total_messages}")

        lines.append("# HELP lobster_network_active_nodes Current active nodes")
        lines.append("# TYPE lobster_network_active_nodes gauge")
        lines.append(f"lobster_network_active_nodes {self.network.active_nodes}")

        lines.append("# HELP lobster_learning_problems_total Total problems attempted")
        lines.append("# TYPE lobster_learning_problems_total counter")
        for lm in self.learning.values():
            lines.append(f'lobster_learning_problems_total{{agent="{lm.agent_id}"}} {lm.problems_attempted}')

        lines.append("# HELP lobster_economy_lbc_balance Current LBC balance")
        lines.append("# TYPE lobster_economy_lbc_balance gauge")
        for em in self.economy.values():
            lines.append(f'lobster_economy_lbc_balance{{agent="{em.agent_id}"}} {em.lbc_balance}')

        return "\n".join(lines)

    def render_table(self) -> str:
        """
        控制台仪表盘输出（无依赖纯文本表格）。
        如需 Rich 表格增强，可安装 `rich` 后自动启用。
        """
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console(width=120)
            output: List[str] = []

            # Agent 指标
            agent_table = Table(title="Agent Metrics", show_header=True)
            agent_table.add_column("Agent", style="cyan")
            agent_table.add_column("Msgs Sent/Recv")
            agent_table.add_column("Tasks OK/Fail")
            agent_table.add_column("Accuracy")
            agent_table.add_column("Avg RT (ms)")
            agent_table.add_column("Activity")
            for agent in self.agents.values():
                agent_table.add_row(
                    agent.agent_id,
                    f"{agent.messages_sent}/{agent.messages_received}",
                    f"{agent.tasks_completed}/{agent.tasks_failed}",
                    f"{agent.accuracy:.1%}",
                    f"{agent.avg_response_time_ms:.0f}",
                    f"{agent.activity_score:.2f}",
                )
            console.print(agent_table)

            # 学习指标
            if self.learning:
                learn_table = Table(title="Learning Metrics", show_header=True)
                learn_table.add_column("Agent")
                learn_table.add_column("Problems")
                learn_table.add_column("Accuracy")
                learn_table.add_column("Games")
                learn_table.add_column("Win Rate")
                learn_table.add_column("Level")
                for lm in self.learning.values():
                    learn_table.add_row(
                        lm.agent_id,
                        f"{lm.problems_correct}/{lm.problems_attempted}",
                        f"{lm.accuracy:.1%}",
                        f"{lm.games_won}/{lm.games_played}",
                        f"{lm.win_rate:.1%}",
                        str(lm.current_level),
                    )
                console.print(learn_table)

            # 经济指标
            if self.economy:
                econ_table = Table(title="Economy Metrics", show_header=True)
                econ_table.add_column("Agent")
                econ_table.add_column("LBC Balance")
                econ_table.add_column("Earned/Spent")
                econ_table.add_column("Trades")
                for em in self.economy.values():
                    econ_table.add_row(
                        em.agent_id,
                        f"{em.lbc_balance:.1f}",
                        f"+{em.total_earned:.1f}/-{em.total_spent:.1f}",
                        str(em.transactions_count),
                    )
                console.print(econ_table)

            return "Dashboard rendered successfully."

        except ImportError:
            return self._render_plain_table()

    def _render_plain_table(self) -> str:
        """纯文本表格（无 rich 依赖回退）"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"  Lobster Network Metrics Dashboard - {datetime.now().strftime('%H:%M:%S')}")
        lines.append("=" * 70)
        lines.append(f"  Network: {self.network.active_nodes}/{self.network.total_nodes} nodes | "
                     f"Messages: {self.network.total_messages} | "
                     f"Throughput: {self.network.throughput_per_minute:.1f}/min")
        lines.append("-" * 70)
        lines.append(f"  {'Agent':<12} {'Msgs':>8} {'Tasks':>8} {'Acc':>6} {'RT(ms)':>8} {'Active':>6}")
        lines.append("-" * 70)
        for agent in self.agents.values():
            lines.append(
                f"  {agent.agent_id:<12} {agent.messages_sent + agent.messages_received:>8} "
                f"{agent.tasks_completed:>4}/{agent.tasks_failed:<3} "
                f"{agent.accuracy:>5.1%} {agent.avg_response_time_ms:>8.0f} {agent.activity_score:>6.2f}"
            )
        lines.append("-" * 70)

        if self.learning:
            lines.append(f"  {'Learning':<12} {'Problems':>8} {'Acc':>6} {'Games':>8} {'WinRt':>6} {'Lv':>4}")
            lines.append("-" * 70)
            for lm in self.learning.values():
                lines.append(
                    f"  {lm.agent_id:<12} {lm.problems_correct:>4}/{lm.problems_attempted:<3} "
                    f"{lm.accuracy:>5.1%} {lm.games_won:>3}/{lm.games_played:<4} "
                    f"{lm.win_rate:>5.1%} {lm.current_level:>4}"
                )
            lines.append("-" * 70)

        if self.economy:
            lines.append(f"  {'Economy':<12} {'Balance':>8} {'Earned':>8} {'Spent':>8} {'Txns':>6}")
            lines.append("-" * 70)
            for em in self.economy.values():
                lines.append(
                    f"  {em.agent_id:<12} {em.lbc_balance:>8.1f} {em.total_earned:>+8.1f} "
                    f"{em.total_spent:>-8.1f} {em.transactions_count:>6}"
                )
            lines.append("-" * 70)

        lines.append("=" * 70)
        return "\n".join(lines)
