"""
龙虾网络统一限速器 - L1 模型层防护
支持：滚动窗口计数、五级降级、指数退避、自动恢复

用法：
    limiter = RateLimiter(node_id="lobster-001")
    
    # 调用前检查
    result = limiter.gate("cron")
    if not result.allowed:
        print(f"限速中，跳过: {result.reason}")
        exit(0)
    
    # 执行 LLM 调用...
    
    # 调用后记录
    limiter.record(tokens=3200, operation="chat")
    
    # 收到 429 时
    limiter.on_429("dashscope")
"""

import json
import os
import time
import random
import threading
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = None  # lazy init to avoid circular import

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


# ========== 数据类 ==========

@dataclass
class GateResult:
    """gate 检查结果"""
    allowed: bool
    tier: str
    reason: str
    wait_ms: int = 0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RequestRecord:
    """单次请求记录"""
    ts: str           # ISO 时间戳
    tokens: int       # 消耗 token 数
    operation: str    # 操作类型：chat | cron | heartbeat | spawn


@dataclass
class BackoffState:
    """退避状态"""
    consecutive_429s: int = 0
    last_backoff_ms: int = 0
    paused_until: Optional[str] = None  # ISO 时间戳
    last_429_at: Optional[str] = None


# ========== 限速等级 ==========

class RateTier:
    OK = "ok"
    CAUTIOUS = "cautious"
    THROTTLED = "throttled"
    CRITICAL = "critical"
    PAUSED = "paused"


# 操作优先级（决定哪些操作在降级时被跳过）
class OperationPriority:
    CHAT = 0          # 用户直接对话 - 最高优先级
    CRON_REPORT = 1   # 定时汇报
    CRON_CHECK = 2    # 定时检查
    HEARTBEAT = 3     # 心跳
    SPAWN = 4         # 子智能体
    BACKGROUND = 5    # 后台任务


# 等级 → 允许的操作（低于此优先级的操作被跳过）
TIER_ALLOWED_OPS = {
    RateTier.OK:        OperationPriority.BACKGROUND + 1,  # 全部允许
    RateTier.CAUTIOUS:  OperationPriority.CRON_CHECK + 1,  # 跳过后台检查
    RateTier.THROTTLED: OperationPriority.CRON_REPORT + 1, # 仅用户对话
    RateTier.CRITICAL:  OperationPriority.CHAT + 1,        # 仅紧急对话
    RateTier.PAUSED:    0,                                  # 全部暂停
}


# ========== 核心限速器 ==========

class RateLimiter:
    """龙虾网络统一限速器"""
    
    def __init__(
        self,
        node_id: str = "lobster-001",
        state_dir: Optional[str] = None,
        config: Optional[dict] = None,
    ):
        """
        Args:
            node_id: 龙虾节点 ID
            state_dir: 状态文件目录，默认 ~/.openclaw/workspace/
            config: 限速配置，默认使用内置保守配置
        """
        self.node_id = node_id
        
        if state_dir is None:
            state_dir = os.path.expanduser("~/.openclaw/workspace")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "rate-limit-state.json"
        
        # 默认配置（保守估计，留 20% 缓冲）
        self.config = config or {
            "requests_per_minute": 10,
            "requests_per_hour": 50,
            "tokens_per_day": 200000,
            "tier_thresholds": {
                "cautious": 0.70,
                "throttled": 0.85,
                "critical": 0.95,
            },
            "backoff": {
                "base_ms": 30000,       # 30 秒
                "max_ms": 3600000,      # 1 小时
                "jitter_pct": 0.3,
            },
            "window_minutes": 60,
        }
        
        # 加载或初始化状态
        self._lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """加载状态文件"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                self.requests: list = data.get("requests", [])
                self.backoff = BackoffState(**data.get("backoff", {}))
                self.tier: str = data.get("tier", RateTier.OK)
                _get_logger().info(f"限速器状态已加载: tier={self.tier}")
            except Exception as e:
                _get_logger().warning(f"加载状态文件失败，使用默认值: {e}")
                self.requests = []
                self.backoff = BackoffState()
                self.tier = RateTier.OK
        else:
            self.requests = []
            self.backoff = BackoffState()
            self.tier = RateTier.OK
    
    def _save_state(self):
        """保存状态文件"""
        data = {
            "node_id": self.node_id,
            "tier": self.tier,
            "requests": self.requests,
            "backoff": asdict(self.backoff),
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ========== 公开 API ==========
    
    def gate(self, operation: str = "chat") -> GateResult:
        """
        调用前检查 - 决定是否允许执行
        
        Args:
            operation: 操作类型 (chat | cron | heartbeat | spawn | background)
        
        Returns:
            GateResult(allowed, tier, reason, wait_ms)
        """
        with self._lock:
            now = datetime.utcnow()
            
            # 1. 检查是否处于暂停状态
            if self.backoff.paused_until:
                paused_until = self._parse_time(self.backoff.paused_until)
                if now < paused_until:
                    wait_ms = int((paused_until - now).total_seconds() * 1000)
                    return GateResult(
                        allowed=False,
                        tier=RateTier.PAUSED,
                        reason=f"退避中，恢复时间: {self.backoff.paused_until}",
                        wait_ms=wait_ms,
                    )
                else:
                    # 退避时间已过，自动恢复
                    _get_logger().info("退避时间已过，自动恢复到 cautious")
                    self.backoff.paused_until = None
                    self.tier = RateTier.CAUTIOUS
                    self._save_state()
            
            # 2. 检查操作优先级
            priority = self._get_priority(operation)
            max_priority = TIER_ALLOWED_OPS.get(self.tier, 0)
            if priority >= max_priority:
                return GateResult(
                    allowed=False,
                    tier=self.tier,
                    reason=f"tier={self.tier}，跳过优先级={priority}的操作({operation})",
                )
            
            # 3. 检查窗口限制
            self._cleanup_old_requests(now)
            
            requests_this_minute = self._count_in_window(now, minutes=1)
            requests_this_hour = self._count_in_window(now, minutes=60)
            tokens_this_day = self._count_tokens_today(now)
            
            # 4. 计算使用率
            max_rpm = self.config["requests_per_minute"]
            max_rph = self.config["requests_per_hour"]
            max_tpd = self.config["tokens_per_day"]
            
            rpm_pct = requests_this_minute / max_rpm if max_rpm > 0 else 0
            rph_pct = requests_this_hour / max_rph if max_rph > 0 else 0
            tpd_pct = tokens_this_day / max_tpd if max_tpd > 0 else 0
            
            usage_pct = max(rpm_pct, rph_pct, tpd_pct)
            
            # 5. 检查硬性限制
            if requests_this_minute >= max_rpm:
                return GateResult(
                    allowed=False,
                    tier=self.tier,
                    reason=f"每分钟请求已达上限 ({requests_this_minute}/{max_rpm})",
                    wait_ms=60000,
                )
            
            if requests_this_hour >= max_rph:
                return GateResult(
                    allowed=False,
                    tier=self.tier,
                    reason=f"每小时请求已达上限 ({requests_this_hour}/{max_rph})",
                    wait_ms=3600000,
                )
            
            if tokens_this_day >= max_tpd:
                return GateResult(
                    allowed=False,
                    tier=self.tier,
                    reason=f"每日 token 已达上限 ({tokens_this_day}/{max_tpd})",
                    wait_ms=86400000,
                )
            
            # 6. 更新 tier
            self._update_tier(usage_pct)
            
            # 7. 返回结果
            if self.tier == RateTier.CRITICAL:
                return GateResult(
                    allowed=True,
                    tier=self.tier,
                    reason=f"临界状态，使用率={usage_pct:.0%}，极简回复",
                )
            
            return GateResult(
                allowed=True,
                tier=self.tier,
                reason=f"允许，使用率={usage_pct:.0%}",
            )
    
    def record(self, tokens: int = 0, operation: str = "chat"):
        """
        调用后记录消耗
        
        Args:
            tokens: 消耗的 token 数
            operation: 操作类型
        """
        with self._lock:
            now = datetime.utcnow()
            self.requests.append(RequestRecord(
                ts=now.isoformat() + "Z",
                tokens=tokens,
                operation=operation,
            ))
            
            # 更新 tier
            self._cleanup_old_requests(now)
            tokens_this_day = self._count_tokens_today(now)
            max_tpd = self.config["tokens_per_day"]
            if max_tpd > 0:
                usage_pct = tokens_this_day / max_tpd
                self._update_tier(usage_pct)
            
            self._save_state()
    
    def on_429(self, provider: str = "unknown", retry_after_ms: Optional[int] = None):
        """
        收到 429 时的处理
        
        Args:
            provider: API 提供方 (dashscope | claude | openai | ...)
            retry_after_ms: 建议的等待时间（毫秒），None 时使用指数退避
        """
        with self._lock:
            now = datetime.utcnow()
            
            # 增加连续 429 计数
            self.backoff.consecutive_429s += 1
            self.backoff.last_429_at = now.isoformat() + "Z"
            
            # 计算退避时间
            if retry_after_ms:
                backoff_ms = retry_after_ms
            else:
                backoff_ms = self._calculate_backoff(self.backoff.consecutive_429s)
            
            self.backoff.last_backoff_ms = backoff_ms
            
            # 设置暂停时间
            paused_until = now + timedelta(milliseconds=backoff_ms)
            self.backoff.paused_until = paused_until.isoformat() + "Z"
            
            # 降级到 paused
            self.tier = RateTier.PAUSED
            
            _get_logger().warning(
                f"🛑 收到 429 (provider={provider}, consecutive={self.backoff.consecutive_429s}) "
                f"退避 {backoff_ms}ms，恢复时间: {self.backoff.paused_until}"
            )
            
            self._save_state()
    
    def get_status(self) -> dict:
        """获取当前限速状态"""
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
        """重置所有限速状态（紧急恢复用）"""
        with self._lock:
            self.requests = []
            self.backoff = BackoffState()
            self.tier = RateTier.OK
            self._save_state()
            _get_logger().info("限速器状态已重置")
    
    # ========== 内部方法 ==========
    
    def _calculate_backoff(self, consecutive_429s: int) -> int:
        """计算指数退避时间（毫秒），带抖动"""
        base = self.config["backoff"]["base_ms"]
        max_backoff = self.config["backoff"]["max_ms"]
        jitter_pct = self.config["backoff"]["jitter_pct"]
        
        backoff = min(base * (2 ** consecutive_429s), max_backoff)
        jitter = backoff * random.uniform(0, jitter_pct)
        return int(backoff + jitter)
    
    def _update_tier(self, usage_pct: float):
        """根据使用率更新 tier"""
        thresholds = self.config["tier_thresholds"]
        
        if usage_pct >= thresholds.get("critical", 0.95):
            self.tier = RateTier.CRITICAL
        elif usage_pct >= thresholds.get("throttled", 0.85):
            self.tier = RateTier.THROTTLED
        elif usage_pct >= thresholds.get("cautious", 0.70):
            self.tier = RateTier.CAUTIOUS
        else:
            self.tier = RateTier.OK
    
    def _cleanup_old_requests(self, now: datetime):
        """清理过期请求记录（保留 24 小时）"""
        cutoff = (now - timedelta(hours=24)).isoformat() + "Z"
        self.requests = [r for r in self.requests if r["ts"] >= cutoff if isinstance(r, dict) else r.ts >= cutoff]
    
    def _count_in_window(self, now: datetime, minutes: int) -> int:
        """统计时间窗口内的请求数"""
        cutoff = (now - timedelta(minutes=minutes)).isoformat() + "Z"
        count = 0
        for r in self.requests:
            ts = r["ts"] if isinstance(r, dict) else r.ts
            if ts >= cutoff:
                count += 1
        return count
    
    def _count_tokens_today(self, now: datetime) -> int:
        """统计今日 token 消耗"""
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
        total = 0
        for r in self.requests:
            ts = r["ts"] if isinstance(r, dict) else r.ts
            if ts >= today_start:
                tokens = r["tokens"] if isinstance(r, dict) else r.tokens
                total += tokens
        return total
    
    def _get_priority(self, operation: str) -> int:
        """获取操作优先级"""
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
    def _parse_time(s: str) -> datetime:
        """解析 ISO 时间字符串"""
        s = s.replace("Z", "").split("+")[0]
        fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in s else "%Y-%m-%dT%H:%M:%S"
        return datetime.strptime(s, fmt)
