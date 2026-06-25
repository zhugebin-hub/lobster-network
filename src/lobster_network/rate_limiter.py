"""
龙虾网络统一限速器 - L1 模型层防护
支持：滚动窗口计数、五级降级、指数退避、自动恢复
"""

import json
import os
import time
import random
import threading
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = None

def _get_logger():
    global logger
    if logger is None:
        try:
            from .utils.logger import get_logger
            logger = get_logger(__name__)
        except ImportError:
            import logging
            logger = logging.getLogger(__name__)
    return logger


@dataclass
class GateResult:
    allowed: bool
    tier: str
    reason: str
    wait_ms: int = 0


@dataclass
class RequestRecord:
    ts: str
    tokens: int
    operation: str


@dataclass
class BackoffState:
    consecutive_429s: int = 0
    last_backoff_ms: int = 0
    paused_until: Optional[str] = None
    last_429_at: Optional[str] = None


class RateTier:
    OK = "ok"
    CAUTIOUS = "cautious"
    THROTTLED = "throttled"
    CRITICAL = "critical"
    PAUSED = "paused"


class OperationPriority:
    CHAT = 0
    CRON_REPORT = 1
    CRON_CHECK = 2
    HEARTBEAT = 3
    SPAWN = 4
    BACKGROUND = 5


TIER_ALLOWED_OPS = {
    RateTier.OK: OperationPriority.BACKGROUND + 1,
    RateTier.CAUTIOUS: OperationPriority.CRON_CHECK + 1,
    RateTier.THROTTLED: OperationPriority.CRON_REPORT + 1,
    RateTier.CRITICAL: OperationPriority.CHAT + 1,
    RateTier.PAUSED: 0,
}


class RateLimiter:
    def __init__(self, node_id="lobster-001", state_dir=None, config=None):
        self.node_id = node_id
        if state_dir is None:
            state_dir = os.path.expanduser("~/.openclaw/workspace")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "rate-limit-state.json"
        
        self.config = config or {
            "requests_per_minute": 10,
            "requests_per_hour": 50,
            "tokens_per_day": 200000,
            "tier_thresholds": {"cautious": 0.70, "throttled": 0.85, "critical": 0.95},
            "backoff": {"base_ms": 30000, "max_ms": 3600000, "jitter_pct": 0.3},
        }
        
        self._lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                self.requests = data.get("requests", [])
                self.backoff = BackoffState(**data.get("backoff", {}))
                self.tier = data.get("tier", RateTier.OK)
                _get_logger().info(f"限速器状态已加载: tier={self.tier}")
            except Exception as e:
                _get_logger().warning(f"加载状态文件失败: {e}")
                self.requests = []
                self.backoff = BackoffState()
                self.tier = RateTier.OK
        else:
            self.requests = []
            self.backoff = BackoffState()
            self.tier = RateTier.OK
    
    def _save_state(self):
        data = {
            "node_id": self.node_id,
            "tier": self.tier,
            "requests": self.requests,
            "backoff": asdict(self.backoff),
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def gate(self, operation="chat"):
        with self._lock:
            now = datetime.utcnow()
            
            if self.backoff.paused_until:
                paused_until = self._parse_time(self.backoff.paused_until)
                if now < paused_until:
                    wait_ms = int((paused_until - now).total_seconds() * 1000)
                    return GateResult(False, RateTier.PAUSED, f"退避中，恢复时间: {self.backoff.paused_until}", wait_ms)
                else:
                    _get_logger().info("退避时间已过，自动恢复到 cautious")
                    self.backoff.paused_until = None
                    self.tier = RateTier.CAUTIOUS
                    self._save_state()
            
            priority = self._get_priority(operation)
            max_priority = TIER_ALLOWED_OPS.get(self.tier, 0)
            if priority >= max_priority:
                return GateResult(False, self.tier, f"tier={self.tier}，跳过优先级={priority}的操作({operation})")
            
            self._cleanup_old_requests(now)
            requests_this_minute = self._count_in_window(now, minutes=1)
            requests_this_hour = self._count_in_window(now, minutes=60)
            tokens_this_day = self._count_tokens_today(now)
            
            max_rpm = self.config["requests_per_minute"]
            max_rph = self.config["requests_per_hour"]
            max_tpd = self.config["tokens_per_day"]
            
            rpm_pct = requests_this_minute / max_rpm if max_rpm > 0 else 0
            rph_pct = requests_this_hour / max_rph if max_rph > 0 else 0
            tpd_pct = tokens_this_day / max_tpd if max_tpd > 0 else 0
            usage_pct = max(rpm_pct, rph_pct, tpd_pct)
            
            if requests_this_minute >= max_rpm:
                return GateResult(False, self.tier, f"每分钟请求已达上限 ({requests_this_minute}/{max_rpm})", 60000)
            if requests_this_hour >= max_rph:
                return GateResult(False, self.tier, f"每小时请求已达上限 ({requests_this_hour}/{max_rph})", 3600000)
            if tokens_this_day >= max_tpd:
                return GateResult(False, self.tier, f"每日 token 已达上限 ({tokens_this_day}/{max_tpd})", 86400000)
            
            self._update_tier(usage_pct)
            
            if self.tier == RateTier.CRITICAL:
                return GateResult(True, self.tier, f"临界状态，使用率={usage_pct:.0%}，极简回复")
            
            return GateResult(True, self.tier, f"允许，使用率={usage_pct:.0%}")
    
    def record(self, tokens=0, operation="chat"):
        with self._lock:
            now = datetime.utcnow()
            record = RequestRecord(ts=now.isoformat() + "Z", tokens=tokens, operation=operation)
            self.requests.append(asdict(record))
            
            self._cleanup_old_requests(now)
            tokens_this_day = self._count_tokens_today(now)
            max_tpd = self.config["tokens_per_day"]
            if max_tpd > 0:
                usage_pct = tokens_this_day / max_tpd
                self._update_tier(usage_pct)
            
            self._save_state()
    
    def on_429(self, provider="unknown", retry_after_ms=None):
        with self._lock:
            now = datetime.utcnow()
            self.backoff.consecutive_429s += 1
            self.backoff.last_429_at = now.isoformat() + "Z"
            
            backoff_ms = retry_after_ms if retry_after_ms else self._calculate_backoff(self.backoff.consecutive_429s)
            self.backoff.last_backoff_ms = backoff_ms
            
            paused_until = now + timedelta(milliseconds=backoff_ms)
            self.backoff.paused_until = paused_until.isoformat() + "Z"
            self.tier = RateTier.PAUSED
            
            _get_logger().warning(f"收到 429 (provider={provider}, consecutive={self.backoff.consecutive_429s}) 退避 {backoff_ms}ms")
            self._save_state()
    
    def get_status(self):
        with self._lock:
            now = datetime.utcnow()
            self._cleanup_old_requests(now)
            requests_this_hour = self._count_in_window(now, minutes=60)
            requests_this_day = self._count_in_window(now, minutes=1440)
            tokens_this_day = self._count_tokens_today(now)
            max_tpd = self.config["tokens_per_day"]
            usage_pct = tokens_this_day / max_tpd if max_tpd > 0 else 0
            
            return {
                "node_id": self.node_id,
                "updated_at": now.isoformat() + "Z",
                "tier": self.tier,
                "usage_pct": round(usage_pct, 4),
                "requests_this_hour": requests_this_hour,
                "requests_this_day": requests_this_day,
                "tokens_this_day": tokens_this_day,
                "consecutive_429s": self.backoff.consecutive_429s,
                "last_429_at": self.backoff.last_429_at,
                "paused_until": self.backoff.paused_until,
            }
    
    def reset(self):
        with self._lock:
            self.requests = []
            self.backoff = BackoffState()
            self.tier = RateTier.OK
            self._save_state()
            _get_logger().info("限速器状态已重置")
    
    def _calculate_backoff(self, consecutive_429s):
        base = self.config["backoff"]["base_ms"]
        max_backoff = self.config["backoff"]["max_ms"]
        jitter_pct = self.config["backoff"]["jitter_pct"]
        backoff = min(base * (2 ** consecutive_429s), max_backoff)
        jitter = backoff * random.uniform(0, jitter_pct)
        return int(backoff + jitter)
    
    def _update_tier(self, usage_pct):
        thresholds = self.config["tier_thresholds"]
        if usage_pct >= thresholds.get("critical", 0.95):
            self.tier = RateTier.CRITICAL
        elif usage_pct >= thresholds.get("throttled", 0.85):
            self.tier = RateTier.THROTTLED
        elif usage_pct >= thresholds.get("cautious", 0.70):
            self.tier = RateTier.CAUTIOUS
        else:
            self.tier = RateTier.OK
    
    def _cleanup_old_requests(self, now):
        cutoff = (now - timedelta(hours=24)).isoformat() + "Z"
        self.requests = [r for r in self.requests if r["ts"] >= cutoff]
    
    def _count_in_window(self, now, minutes):
        cutoff = (now - timedelta(minutes=minutes)).isoformat() + "Z"
        return sum(1 for r in self.requests if r["ts"] >= cutoff)
    
    def _count_tokens_today(self, now):
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        return sum(r["tokens"] for r in self.requests if r["ts"] >= today_start)
    
    def _get_priority(self, operation):
        priority_map = {
            "chat": OperationPriority.CHAT,
            "cron_report": OperationPriority.CRON_REPORT,
            "cron": OperationPriority.CRON_CHECK,
            "heartbeat": OperationPriority.HEARTBEAT,
            "spawn": OperationPriority.SPAWN,
            "background": OperationPriority.BACKGROUND,
        }
        return priority_map.get(operation, OperationPriority.BACKGROUND)
    
    @staticmethod
    def _parse_time(s):
        s = s.replace("Z", "").split("+")[0]
        fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in s else "%Y-%m-%dT%H:%M:%S"
        return datetime.strptime(s, fmt)
