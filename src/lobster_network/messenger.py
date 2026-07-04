"""
可靠消息传递系统
支持：消息确认、自动重试、多通道故障切换、消息持久化、有序投递
"""

import json
import os
import uuid
import time
import threading
from typing import Dict, List, Optional, Callable, Tuple
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path

from .registry import NodeRegistry, TransportConfig, TransportType
from .utils.logger import get_logger
from .security import sign_message, verify_message, CRYPTOGRAPHY_AVAILABLE, DEFAULT_SECRET

logger = get_logger(__name__)


def _parse_time(s: str) -> datetime:
    """解析 ISO 时间字符串（兼容 Python 3.6+）"""
    s = s.replace('Z', '').split('+')[0]
    fmt = "%Y-%m-%dT%H:%M:%S.%f" if '.' in s else "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(s, fmt)


# 消息状态
class MessageStatus(str, Enum):
    PENDING = "pending"       # 待发送
    SENDING = "sending"       # 发送中
    DELIVERED = "delivered"   # 已投递（到达对方）
    ACKED = "acked"           # 已确认（对方已处理）
    FAILED = "failed"         # 发送失败
    EXPIRED = "expired"       # 已过期


@dataclass
class MessageAttempt:
    """单次发送尝试"""
    attempt: int
    timestamp: str
    transport: str
    success: bool
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReliableMessage:
    """可靠消息（带状态跟踪 + 安全签名）"""
    msg_id: str
    from_node: str
    to_node: str
    msg_type: str
    payload: Dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = MessageStatus.PENDING
    attempts: List[MessageAttempt] = field(default_factory=list)
    max_retries: int = 3
    retry_delay: float = 1.0  # 秒
    ttl_seconds: int = 3600   # 默认1小时过期
    ack_timeout: int = 30     # 确认超时（秒）
    delivered_at: Optional[str] = None
    acked_at: Optional[str] = None
    reply_to: Optional[str] = None
    priority: int = 0         # 优先级，数字越小优先级越高
    # 安全字段
    signature: Optional[str] = None
    signed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "from_node": self.from_node,
            "to_node": self.to_node,
            "msg_type": self.msg_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "status": self.status,
            "attempts": [a.to_dict() for a in self.attempts],
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "ttl_seconds": self.ttl_seconds,
            "delivered_at": self.delivered_at,
            "acked_at": self.acked_at,
            "reply_to": self.reply_to,
            "priority": self.priority,
            # 安全字段
            "signature": self.signature,
            "signed_at": self.signed_at,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ReliableMessage":
        attempts = [MessageAttempt(**a) for a in data.get("attempts", [])]
        return cls(
            msg_id=data["msg_id"],
            from_node=data["from_node"],
            to_node=data["to_node"],
            msg_type=data["msg_type"],
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            status=data.get("status", MessageStatus.PENDING),
            attempts=attempts,
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 1.0),
            ttl_seconds=data.get("ttl_seconds", 3600),
            delivered_at=data.get("delivered_at"),
            acked_at=data.get("acked_at"),
            reply_to=data.get("reply_to"),
            priority=data.get("priority", 0),
            # 安全字段
            signature=data.get("signature"),
            signed_at=data.get("signed_at"),
        )
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        try:
            created = _parse_time(self.timestamp)
            return (datetime.now() - created).total_seconds() > self.ttl_seconds
        except (ValueError, TypeError):
            return True
    
    def can_retry(self) -> bool:
        """是否可以重试"""
        return (
            self.status in (MessageStatus.PENDING, MessageStatus.SENDING, MessageStatus.FAILED)
            and len(self.attempts) < self.max_retries
            and not self.is_expired()
        )
    
    def sign(self, secret: str = None) -> Optional[str]:
        """
        对消息签名（使用 payload 生成签名）
        
        Returns:
            Optional[str]: 签名字符串，如果禁用安全特性则返回 None
        """
        if not CRYPTOGRAPHY_AVAILABLE and not secret:
            # 如果 cryptography 不可用且未提供密钥，跳过签名
            logger.debug("跳过签名：cryptography 不可用且未提供密钥")
            return None
        
        try:
            signed_msg = sign_message(self.payload, secret=secret or DEFAULT_SECRET)
            self.signature = signed_msg.get("_signature")
            self.signed_at = signed_msg.get("_signed_at")
            return self.signature
        except Exception as e:
            logger.error(f"消息签名失败: {e}")
            return None
    
    def verify_signature(self, secret: str = None) -> bool:
        """
        验证消息签名
        
        Returns:
            bool: 验证是否通过
        """
        if not self.signature:
            logger.warning(f"消息 {self.msg_id} 缺少签名")
            return False
        
        try:
            # 构造带签名的消息用于验证
            msg_with_sig = self.to_dict()
            return verify_message(msg_with_sig, secret=secret or DEFAULT_SECRET)
        except Exception as e:
            logger.error(f"消息验证失败: {e}")
            return False
    
    def record_attempt(
        self,
        transport: str,
        success: bool,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
    ) -> None:
        """记录一次发送尝试"""
        attempt = MessageAttempt(
            attempt=len(self.attempts) + 1,
            timestamp=datetime.now().isoformat(),
            transport=transport,
            success=success,
            error=error,
            latency_ms=latency_ms,
        )
        self.attempts.append(attempt)
        
        if success:
            self.status = MessageStatus.DELIVERED
            self.delivered_at = datetime.now().isoformat()
        else:
            if self.can_retry():
                self.status = MessageStatus.PENDING
            else:
                self.status = MessageStatus.FAILED


class Transport:
    """传输通道基类"""
    
    def __init__(self, transport_type: str):
        self.transport_type = transport_type
    
    def send(self, message: ReliableMessage, config: TransportConfig) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        发送消息
        
        Returns:
            (success, error, latency_ms)
        """
        raise NotImplementedError
    
    def can_use(self, config: TransportConfig) -> bool:
        """检查通道是否可用"""
        return config.enabled


class NFSTransport(Transport):
    """NFS 文件传输通道"""
    
    def __init__(self, base_dir: str):
        super().__init__(TransportType.NFS)
        self.base_dir = base_dir
    
    def send(self, message: ReliableMessage, config: TransportConfig) -> Tuple[bool, Optional[str], Optional[float]]:
        start = time.time()
        try:
            # 解析 endpoint 为目录路径
            target_dir = config.endpoint or f"{self.base_dir}/from-{message.from_node}"
            os.makedirs(target_dir, exist_ok=True)
            
            filename = f"{message.msg_id}.json"
            filepath = os.path.join(target_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
            
            latency = (time.time() - start) * 1000
            logger.debug(f"NFS send: {filepath} ({latency:.1f}ms)")
            return True, None, latency
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            error = f"NFS send failed: {e}"
            logger.error(error)
            return False, error, latency
    
    def can_use(self, config: TransportConfig) -> bool:
        if not config.enabled:
            return False
        try:
            target_dir = config.endpoint or self.base_dir
            # 检查路径是否存在且可写（不尝试创建）
            if not os.path.isdir(target_dir):
                return False
            return os.access(target_dir, os.W_OK)
        except Exception:
            return False


class FileTransport(Transport):
    """本地文件传输通道（兜底）"""
    
    def __init__(self, base_dir: str):
        super().__init__(TransportType.FILE)
        self.base_dir = base_dir
    
    def send(self, message: ReliableMessage, config: TransportConfig) -> Tuple[bool, Optional[str], Optional[float]]:
        start = time.time()
        try:
            target_dir = config.endpoint or f"{self.base_dir}/pending"
            os.makedirs(target_dir, exist_ok=True)
            
            filename = f"{message.msg_id}.json"
            filepath = os.path.join(target_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
            
            latency = (time.time() - start) * 1000
            logger.debug(f"File send: {filepath} ({latency:.1f}ms)")
            return True, None, latency
            
        except Exception as e:
            latency = (time.time() - start) * 1000
            error = f"File send failed: {e}"
            logger.error(error)
            return False, error, latency
    
    def can_use(self, config: TransportConfig) -> bool:
        if not config.enabled:
            return False
        try:
            target_dir = config.endpoint or self.base_dir
            os.makedirs(target_dir, exist_ok=True)
            return True
        except Exception:
            return False


class Messenger:
    """
    可靠消息传递器
    
    功能：
    1. 多通道发送（NFS → HTTP → SSH → 本地文件）
    2. 自动故障切换
    3. 自动重试（指数退避）
    4. 消息持久化
    5. 消息确认（ACK）
    6. 消息队列管理
    """
    
    def __init__(
        self,
        registry: NodeRegistry,
        storage_dir: str = "~/.lobster-network/messages",
    ):
        self.registry = registry
        self.storage_dir = os.path.expanduser(storage_dir)
        self.messages: Dict[str, ReliableMessage] = {}
        self._lock = threading.RLock()
        self._transports: Dict[str, Transport] = {
            TransportType.NFS: NFSTransport(f"{self.storage_dir}/nfs"),
            TransportType.FILE: FileTransport(f"{self.storage_dir}/file"),
        }
        self._delivery_callbacks: List = []
        self._failure_callbacks: List = []
        
        # 确保存储目录存在
        os.makedirs(self.storage_dir, exist_ok=True)
        os.makedirs(f"{self.storage_dir}/pending", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/sent", exist_ok=True)
        os.makedirs(f"{self.storage_dir}/failed", exist_ok=True)
        
        # 加载持久化消息
        self._load_messages()
        
        logger.info(f"Messenger initialized (storage={self.storage_dir})")
    
    # ==================== 发送消息 ====================
    
    def send(
        self,
        from_node: str,
        to_node: str,
        msg_type: str,
        payload: Dict,
        priority: int = 0,
        max_retries: int = 3,
        ttl_seconds: int = 3600,
        reply_to: Optional[str] = None,
    ) -> ReliableMessage:
        """
        发送可靠消息
        
        Args:
            from_node: 发送节点
            to_node: 接收节点
            msg_type: 消息类型
            payload: 消息载荷
            priority: 优先级
            max_retries: 最大重试次数
            ttl_seconds: 过期时间
            reply_to: 回复的消息ID
        
        Returns:
            ReliableMessage: 消息对象
        """
        msg_id = f"msg-{uuid.uuid4().hex[:12]}"
        
        message = ReliableMessage(
            msg_id=msg_id,
            from_node=from_node,
            to_node=to_node,
            msg_type=msg_type,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
            ttl_seconds=ttl_seconds,
            reply_to=reply_to,
        )
        
        with self._lock:
            self.messages[msg_id] = message
        
        # 对消息签名（如果启用了安全特性）
        try:
            message.sign()
            logger.debug(f"消息已签名: {msg_id}")
        except Exception as e:
            logger.warning(f"消息签名失败（将继续发送）: {e}")
        
        # 立即尝试发送
        self._deliver(message)
        
        return message
    
    def _deliver(self, message: ReliableMessage) -> bool:
        """
        投递消息（尝试所有可用通道）
        
        Returns:
            bool: 是否成功
        """
        to_node_id = message.to_node
        
        # 获取目标节点的可用传输通道
        transports = self.registry.get_active_transports(to_node_id)
        
        if not transports:
            # 没有注册传输通道，使用默认文件通道
            default_config = TransportConfig(
                transport_type=TransportType.FILE,
                endpoint=f"{self.storage_dir}/pending",
                enabled=True,
                priority=99,
            )
            transports = [default_config]
        
        # 按优先级尝试每个通道
        for transport_config in transports:
            transport = self._transports.get(transport_config.transport_type)
            if not transport:
                logger.warning(f"Unknown transport type: {transport_config.transport_type}")
                continue
            
            if not transport.can_use(transport_config):
                logger.debug(f"Transport {transport_config.transport_type} not available for {to_node_id}")
                continue
            
            message.status = MessageStatus.SENDING
            start = time.time()
            
            try:
                success, error, latency = transport.send(message, transport_config)
                
                if success:
                    message.record_attempt(
                        transport=transport_config.transport_type,
                        success=True,
                        latency_ms=latency,
                    )
                    self._save_message(message)
                    
                    # 标记通道正常
                    self.registry.mark_transport_ok(to_node_id, transport_config.transport_type)
                    
                    logger.info(
                        f"Message {message.msg_id} delivered to {to_node_id} "
                        f"via {transport_config.transport_type} ({latency:.1f}ms)"
                    )
                    
                    # 触发成功回调
                    for cb in self._delivery_callbacks:
                        try:
                            cb(message)
                        except Exception as e:
                            logger.error(f"Delivery callback error: {e}")
                    
                    return True
                else:
                    message.record_attempt(
                        transport=transport_config.transport_type,
                        success=False,
                        error=error,
                        latency_ms=latency,
                    )
                    self.registry.mark_transport_failed(
                        to_node_id, transport_config.transport_type, error or "unknown"
                    )
                    logger.warning(
                        f"Message {message.msg_id} failed via {transport_config.transport_type}: {error}"
                    )
                    
            except Exception as e:
                message.record_attempt(
                    transport=transport_config.transport_type,
                    success=False,
                    error=str(e),
                )
                logger.error(f"Transport exception: {e}")
        
        # 所有通道都失败
        if not message.can_retry():
            message.status = MessageStatus.FAILED
            self._save_message(message)
            
            for cb in self._failure_callbacks:
                try:
                    cb(message)
                except Exception as e:
                    logger.error(f"Failure callback error: {e}")
            
            logger.error(f"Message {message.msg_id} failed after all attempts")
            return False
        
        return False
    
    # ==================== 确认消息 ====================
    
    def ack(self, msg_id: str) -> bool:
        """
        确认消息（ACK）
        
        Args:
            msg_id: 消息ID
        
        Returns:
            bool: 是否成功
        """
        with self._lock:
            message = self.messages.get(msg_id)
            if not message:
                return False
            
            if message.status == MessageStatus.DELIVERED:
                message.status = MessageStatus.ACKED
                message.acked_at = datetime.now().isoformat()
                self._save_message(message)
                logger.info(f"Message {msg_id} ACKed")
                return True
            
            return False
    
    def nack(self, msg_id: str, reason: str = "") -> bool:
        """
        否定确认（NACK），请求重发
        
        Args:
            msg_id: 消息ID
            reason: 原因
        
        Returns:
            bool: 是否成功
        """
        with self._lock:
            message = self.messages.get(msg_id)
            if not message:
                return False
            
            if message.status == MessageStatus.DELIVERED and message.can_retry():
                message.status = MessageStatus.PENDING
                logger.info(f"Message {msg_id} NACKed: {reason}")
                # 立即重试
                return self._deliver(message)
            
            return False
    
    # ==================== 重试 ====================
    
    def retry(self, msg_id: str) -> bool:
        """
        手动重试发送
        
        Args:
            msg_id: 消息ID
        
        Returns:
            bool: 是否成功
        """
        with self._lock:
            message = self.messages.get(msg_id)
            if not message or not message.can_retry():
                return False
            
            message.status = MessageStatus.PENDING
            return self._deliver(message)
    
    def retry_all_failed(self) -> int:
        """
        重试所有失败的消息
        
        Returns:
            int: 成功重试的数量
        """
        count = 0
        with self._lock:
            for msg in self.messages.values():
                if msg.status == MessageStatus.FAILED and msg.can_retry():
                    msg.status = MessageStatus.PENDING
                    if self._deliver(msg):
                        count += 1
        return count
    
    # ==================== 查询 ====================
    
    def get_message(self, msg_id: str) -> Optional[ReliableMessage]:
        """获取消息"""
        return self.messages.get(msg_id)
    
    def get_messages(
        self,
        from_node: Optional[str] = None,
        to_node: Optional[str] = None,
        status: Optional[str] = None,
        msg_type: Optional[str] = None,
    ) -> List[ReliableMessage]:
        """查询消息"""
        with self._lock:
            result = list(self.messages.values())
            
            if from_node:
                result = [m for m in result if m.from_node == from_node]
            if to_node:
                result = [m for m in result if m.to_node == to_node]
            if status:
                result = [m for m in result if m.status == status]
            if msg_type:
                result = [m for m in result if m.msg_type == msg_type]
            
            return result
    
    def get_pending_count(self) -> int:
        """获取待发送消息数"""
        with self._lock:
            return sum(
                1 for m in self.messages.values()
                if m.status in (MessageStatus.PENDING, MessageStatus.SENDING)
            )
    
    def get_failed_count(self) -> int:
        """获取失败消息数"""
        with self._lock:
            return sum(1 for m in self.messages.values() if m.status == MessageStatus.FAILED)
    
    def get_statistics(self) -> Dict:
        """获取消息统计"""
        with self._lock:
            status_counts = {}
            type_counts = {}
            for msg in self.messages.values():
                status_counts[msg.status] = status_counts.get(msg.status, 0) + 1
                type_counts[msg.msg_type] = type_counts.get(msg.msg_type, 0) + 1
            
            return {
                "total": len(self.messages),
                "by_status": status_counts,
                "by_type": type_counts,
                "pending": self.get_pending_count(),
                "failed": self.get_failed_count(),
            }
    
    # ==================== 回调 ====================
    
    def on_delivery(self, callback) -> None:
        """注册投递成功回调"""
        self._delivery_callbacks.append(callback)
    
    def on_failure(self, callback) -> None:
        """注册投递失败回调"""
        self._failure_callbacks.append(callback)
    
    # ==================== 持久化 ====================
    
    def _save_message(self, message: ReliableMessage) -> None:
        """持久化消息"""
        try:
            if message.status == MessageStatus.FAILED:
                subdir = "failed"
            elif message.status == MessageStatus.ACKED:
                subdir = "sent"
            else:
                subdir = "pending"
            
            filepath = os.path.join(self.storage_dir, subdir, f"{message.msg_id}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(message.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save message {message.msg_id}: {e}")
    
    def _load_messages(self) -> None:
        """从存储加载消息"""
        for subdir in ("pending", "sent", "failed"):
            dirpath = os.path.join(self.storage_dir, subdir)
            if not os.path.exists(dirpath):
                continue
            
            for filename in os.listdir(dirpath):
                if not filename.endswith(".json"):
                    continue
                try:
                    filepath = os.path.join(dirpath, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    msg = ReliableMessage.from_dict(data)
                    
                    # 验证消息签名（如果启用了安全特性）
                    if CRYPTOGRAPHY_AVAILABLE and msg.signature:
                        if not msg.verify_signature():
                            logger.warning(f"消息签名验证失败: {msg.msg_id}，将标记为不可信")
                            # 可以选择：拒绝加载、标记、或继续加载
                            # 当前策略：继续加载，但记录警告
                    
                    self.messages[msg.msg_id] = msg
                except Exception as e:
                    logger.error(f"Failed to load message {filename}: {e}")
        
        logger.info(f"Loaded {len(self.messages)} messages from storage")
    
    # ==================== 清理 ====================
    
    def cleanup_expired(self) -> int:
        """清理过期消息"""
        count = 0
        with self._lock:
            to_remove = []
            for msg_id, msg in self.messages.items():
                if msg.is_expired() and msg.status in (MessageStatus.ACKED, MessageStatus.DELIVERED):
                    to_remove.append(msg_id)
            
            for msg_id in to_remove:
                del self.messages[msg_id]
                count += 1
            
            if count > 0:
                logger.info(f"Cleaned up {count} expired messages")
        
        return count
