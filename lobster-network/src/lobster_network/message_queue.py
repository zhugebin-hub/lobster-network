"""
龙虾网络消息队列 - L2 通信层防护
支持：令牌桶算法、优先级队列、通道降级（钉钉→NFS→SSH→本地）

用法：
    queue = MessageQueue(node_id="lobster-001")
    
    # 发送消息（自动选择最佳通道）
    queue.send(
        to="lobster-002",
        content="请求协作",
        priority="high",
    )
    
    # 获取待处理消息
    messages = queue.receive(from_node="lobster-002")
"""

import json
import os
import time
import uuid
import threading
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

from .utils.logger import get_logger

logger = get_logger(__name__)


# ========== 数据类 ==========

class MessagePriority(str, Enum):
    P0_URGENT = "p0_urgent"      # 用户直接提问、定时汇报超时
    P1_IMPORTANT = "p1_important" # 龙虾间协作请求、任务结果
    P2_NORMAL = "p2_normal"       # 心跳检查、状态同步
    P3_LOW = "p3_low"             # 主动推送、社区互动


class ChannelType(str, Enum):
    DINGTALK = "dingtalk"
    NFS = "nfs"
    SSH = "ssh"
    LOCAL = "local"


@dataclass
class QueuedMessage:
    """队列中的消息"""
    msg_id: str
    from_node: str
    to_node: str
    content: str
    priority: str
    created_at: str
    channel: Optional[str] = None    # 已选择通道
    status: str = "pending"          # pending | sending | delivered | failed
    retry_count: int = 0
    max_retries: int = 3
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> "QueuedMessage":
        return cls(**data)


@dataclass
class TokenBucketState:
    """令牌桶状态"""
    capacity: int = 20               # 桶容量（每分钟最大消息数）
    tokens: float = 20               # 当前令牌数
    refill_rate: float = 20          # 每分钟 refill 速率
    last_refill: Optional[str] = None # 上次 refill 时间


# ========== 消息队列 ==========

class MessageQueue:
    """龙虾网络消息队列"""
    
    def __init__(
        self,
        node_id: str = "lobster-001",
        state_dir: Optional[str] = None,
        config: Optional[dict] = None,
    ):
        if state_dir is None:
            state_dir = os.path.expanduser("~/.openclaw/workspace")
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.node_id = node_id
        self.queue_file = self.state_dir / "message-queue.json"
        self.bucket_file = self.state_dir / "token-bucket.json"
        
        # 默认配置
        self.config = config or {
            "dingtalk": {
                "messages_per_minute": 20,
                "cooldown_minutes_on_limit": 10,
            },
            "channels": {
                "dingtalk": {"enabled": True, "priority": 1},
                "nfs": {"enabled": True, "priority": 2},
                "ssh": {"enabled": False, "priority": 3},
                "local": {"enabled": True, "priority": 99},  # 兜底
            },
            "nfs_dir": "/shared/messages",
        }
        
        self._lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """加载状态"""
        # 加载消息队列
        if self.queue_file.exists():
            try:
                with open(self.queue_file, "r") as f:
                    data = json.load(f)
                self.messages: List[dict] = data.get("messages", [])
                self.cooldown_until: Optional[str] = data.get("cooldown_until")
            except Exception as e:
                logger.warning(f"加载消息队列失败: {e}")
                self.messages = []
                self.cooldown_until = None
        else:
            self.messages = []
            self.cooldown_until = None
        
        # 加载令牌桶
        if self.bucket_file.exists():
            try:
                with open(self.bucket_file, "r") as f:
                    data = json.load(f)
                self.bucket = TokenBucketState(**data)
            except Exception as e:
                logger.warning(f"加载令牌桶失败: {e}")
                self.bucket = TokenBucketState()
        else:
            self.bucket = TokenBucketState()
            self.bucket.last_refill = datetime.utcnow().isoformat() + "Z"
    
    def _save_state(self):
        """保存状态"""
        # 保存消息队列
        with open(self.queue_file, "w") as f:
            json.dump({
                "messages": self.messages,
                "cooldown_until": self.cooldown_until,
                "updated_at": datetime.utcnow().isoformat() + "Z",
            }, f, ensure_ascii=False, indent=2)
        
        # 保存令牌桶
        with open(self.bucket_file, "w") as f:
            json.dump(asdict(self.bucket), f, ensure_ascii=False, indent=2)
    
    # ========== 公开 API ==========
    
    def send(
        self,
        to: str,
        content: str,
        priority: str = MessagePriority.P2_NORMAL,
        channel: Optional[str] = None,
    ) -> str:
        """
        发送消息（自动选择最佳通道）
        
        Args:
            to: 目标节点 ID
            content: 消息内容
            priority: 优先级 (p0_urgent | p1_important | p2_normal | p3_low)
            channel: 强制指定通道，None 时自动选择
        
        Returns:
            msg_id
        """
        with self._lock:
            now = datetime.utcnow()
            msg_id = f"msg-{self.node_id}-{int(now.timestamp()*1000)}-{uuid.uuid4().hex[:8]}"
            
            msg = QueuedMessage(
                msg_id=msg_id,
                from_node=self.node_id,
                to_node=to,
                content=content,
                priority=priority,
                created_at=now.isoformat() + "Z",
            )
            
            # 选择通道
            if channel:
                msg.channel = channel
            else:
                msg.channel = self._select_channel(priority)
            
            # 尝试发送
            success = self._try_send(msg)
            
            if success:
                msg.status = "delivered"
            else:
                msg.status = "pending"
                # 加入队列等待重试
                self.messages.append(msg.to_dict())
            
            self._save_state()
            return msg_id
    
    def receive(self, from_node: Optional[str] = None) -> List[QueuedMessage]:
        """
        接收消息
        
        Args:
            from_node: 仅接收来自指定节点的消息，None 接收全部
        
        Returns:
            消息列表
        """
        messages = []
        
        # 从本地队列读取
        with self._lock:
            for msg_dict in self.messages:
                if from_node and msg_dict.get("from_node") != from_node:
                    continue
                if msg_dict.get("status") == "pending":
                    messages.append(QueuedMessage.from_dict(msg_dict))
        
        # 从 NFS 通道读取（其他龙虾发来的）
        nfs_dir = self.config.get("nfs_dir", "/shared/messages")
        from_dir = Path(nfs_dir) / f"from-{from_node}" if from_node else None
        
        # TODO: 实现 NFS 消息读取
        
        return messages
    
    def retry_pending(self) -> int:
        """
        重试所有 pending 消息
        
        Returns:
            成功发送的消息数
        """
        success_count = 0
        
        with self._lock:
            for msg_dict in self.messages:
                if msg_dict.get("status") != "pending":
                    continue
                
                msg = QueuedMessage.from_dict(msg_dict)
                
                # 检查重试次数
                if msg.retry_count >= msg.max_retries:
                    msg.status = "failed"
                    msg.error = f"重试次数已达上限 ({msg.max_retries})"
                    continue
                
                msg.retry_count += 1
                
                # 尝试降级通道
                if msg.channel == "dingtalk" and msg.retry_count >= 2:
                    msg.channel = "nfs"
                elif msg.channel == "nfs" and msg.retry_count >= 3:
                    msg.channel = "local"
                
                success = self._try_send(msg)
                
                if success:
                    msg.status = "delivered"
                    success_count += 1
                else:
                    msg.error = f"发送失败，重试 {msg.retry_count}/{msg.max_retries}"
        
        self._save_state()
        return success_count
    
    def get_queue_status(self) -> dict:
        """获取队列状态"""
        with self._lock:
            pending = sum(1 for m in self.messages if m.get("status") == "pending")
            failed = sum(1 for m in self.messages if m.get("status") == "failed")
            delivered = sum(1 for m in self.messages if m.get("status") == "delivered")
            
            # 令牌桶状态
            self._refill_tokens()
            
            return {
                "node_id": self.node_id,
                "queue": {
                    "pending": pending,
                    "failed": failed,
                    "delivered": delivered,
                    "total": len(self.messages),
                },
                "token_bucket": {
                    "tokens": round(self.bucket.tokens, 1),
                    "capacity": self.bucket.capacity,
                    "refill_rate": self.bucket.refill_rate,
                },
                "cooldown_until": self.cooldown_until,
            }
    
    def mark_cooldown(self, minutes: Optional[int] = None):
        """
        标记钉钉通道进入冷却期（收到限速时调用）
        
        Args:
            minutes: 冷却时长，默认使用配置值
        """
        cooldown_minutes = minutes or self.config["dingtalk"]["cooldown_minutes_on_limit"]
        cooldown_until = datetime.utcnow() + timedelta(minutes=cooldown_minutes)
        self.cooldown_until = cooldown_until.isoformat() + "Z"
        logger.warning(f"🔶 钉钉通道进入冷却期 {cooldown_minutes} 分钟，至 {self.cooldown_until}")
        self._save_state()
    
    def cleanup(self, max_age_hours: int = 24):
        """清理过期消息"""
        with self._lock:
            cutoff = (datetime.utcnow() - timedelta(hours=max_age_hours)).isoformat() + "Z"
            original_count = len(self.messages)
            self.messages = [
                m for m in self.messages
                if m.get("created_at", "") >= cutoff
            ]
            cleaned = original_count - len(self.messages)
            if cleaned > 0:
                logger.info(f"清理了 {cleaned} 条过期消息")
                self._save_state()
    
    # ========== 内部方法 ==========
    
    def _select_channel(self, priority: str) -> str:
        """
        根据优先级选择最佳通道
        
        Returns:
            通道名称
        """
        channels = self.config.get("channels", {})
        
        # 检查钉钉是否在冷却期
        if self.cooldown_until:
            cooldown_until = self._parse_time(self.cooldown_until)
            if datetime.utcnow() < cooldown_until:
                # 钉钉冷却中，跳过
                pass
            else:
                self.cooldown_until = None  # 冷却结束
        
        # 按优先级选择通道
        if priority in (MessagePriority.P0_URGENT, MessagePriority.P1_IMPORTANT):
            # 紧急消息优先用钉钉
            if channels.get("dingtalk", {}).get("enabled", True) and not self.cooldown_until:
                return "dingtalk"
            return "nfs"
        
        # 常规/低优消息用 NFS
        if channels.get("nfs", {}).get("enabled", True):
            return "nfs"
        
        return "local"
    
    def _try_send(self, msg: QueuedMessage) -> bool:
        """
        尝试发送消息
        
        Returns:
            是否成功
        """
        channel = msg.channel or "local"
        
        if channel == "dingtalk":
            return self._send_via_dingtalk(msg)
        elif channel == "nfs":
            return self._send_via_nfs(msg)
        elif channel == "ssh":
            return self._send_via_ssh(msg)
        else:
            return self._send_via_local(msg)
    
    def _send_via_dingtalk(self, msg: QueuedMessage) -> bool:
        """通过钉钉发送"""
        # 检查令牌桶
        if not self._consume_token():
            logger.warning("钉钉令牌桶耗尽，消息进入队列")
            self.mark_cooldown()
            return False
        
        # TODO: 实际调用钉钉 API 发送
        # 这里留作集成点
        logger.debug(f"钉钉消息已发送: {msg.msg_id} → {msg.to_node}")
        return True
    
    def _send_via_nfs(self, msg: QueuedMessage) -> bool:
        """通过 NFS 发送"""
        nfs_dir = self.config.get("nfs_dir", "/shared/messages")
        to_dir = Path(nfs_dir) / f"from-{self.node_id}"
        
        try:
            to_dir.mkdir(parents=True, exist_ok=True)
            file_path = to_dir / f"{msg.msg_id}.json"
            
            with open(file_path, "w") as f:
                json.dump(msg.to_dict(), f, ensure_ascii=False, indent=2)
            
            logger.debug(f"NFS 消息已写入: {file_path}")
            return True
        except Exception as e:
            logger.error(f"NFS 消息发送失败: {e}")
            return False
    
    def _send_via_ssh(self, msg: QueuedMessage) -> bool:
        """通过 SSH 发送（待实现）"""
        logger.debug(f"SSH 消息发送（待实现）: {msg.msg_id}")
        return False
    
    def _send_via_local(self, msg: QueuedMessage) -> bool:
        """本地存储（兜底）"""
        local_dir = self.state_dir / "message-queue" / "pending"
        local_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = local_dir / f"{msg.msg_id}.json"
        with open(file_path, "w") as f:
            json.dump(msg.to_dict(), f, ensure_ascii=False, indent=2)
        
        logger.debug(f"本地消息已存储: {file_path}")
        return True
    
    def _refill_tokens(self):
        """补充令牌"""
        if not self.bucket.last_refill:
            self.bucket.last_refill = datetime.utcnow().isoformat() + "Z"
            return
        
        last = self._parse_time(self.bucket.last_refill)
        now = datetime.utcnow()
        elapsed_minutes = (now - last).total_seconds() / 60
        
        if elapsed_minutes > 0:
            new_tokens = elapsed_minutes * self.bucket.refill_rate
            self.bucket.tokens = min(
                self.bucket.capacity,
                self.bucket.tokens + new_tokens,
            )
            self.bucket.last_refill = now.isoformat() + "Z"
    
    def _consume_token(self) -> bool:
        """消耗一个令牌"""
        self._refill_tokens()
        
        if self.bucket.tokens >= 1:
            self.bucket.tokens -= 1
            self._save_state()
            return True
        
        return False
    
    @staticmethod
    def _parse_time(s: str) -> datetime:
        """解析 ISO 时间字符串"""
        s = s.replace("Z", "").split("+")[0]
        fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in s else "%Y-%m-%dT%H:%M:%S"
        return datetime.strptime(s, fmt)
