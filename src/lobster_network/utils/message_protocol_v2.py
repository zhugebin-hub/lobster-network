"""
消息协议定义 - 增强版 v2.0
添加重试、确认、去重、持久化、心跳检测
"""

import json
import os
import time
import uuid
import hashlib
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
import threading


@dataclass
class Message:
    """小龙虾网络消息 - 增强版"""
    msg_id: str
    from_node: str
    to_node: str
    msg_type: str  # dialogue_trigger|training_task|emergence_report|heartbeat|register|confirm
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    payload: Dict = field(default_factory=dict)
    reply_to: Optional[str] = None
    priority: int = 0  # 0=normal, 1=high, 2=critical
    ttl: int = 3600  # 消息存活时间（秒）
    retry_count: int = 0
    max_retries: int = 3
    confirmed: bool = False
    confirmed_at: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "msg_id": self.msg_id,
            "from": self.from_node,
            "to": self.to_node,
            "type": self.msg_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "reply_to": self.reply_to,
            "priority": self.priority,
            "ttl": self.ttl,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "confirmed": self.confirmed,
            "confirmed_at": self.confirmed_at,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """从字典创建消息"""
        return cls(
            msg_id=data["msg_id"],
            from_node=data["from"],
            to_node=data["to"],
            msg_type=data["type"],
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            payload=data.get("payload", {}),
            reply_to=data.get("reply_to"),
            priority=data.get("priority", 0),
            ttl=data.get("ttl", 3600),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            confirmed=data.get("confirmed", False),
            confirmed_at=data.get("confirmed_at"),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """从JSON字符串创建消息"""
        return cls.from_dict(json.loads(json_str))
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        try:
            created = self._parse_timestamp(self.timestamp)
            if created is None:
                return False
            return (datetime.now() - created).total_seconds() > self.ttl
        except Exception:
            return False
    
    def _parse_timestamp(self, ts: str):
        """解析时间戳，兼容多种格式"""
        if not ts:
            return None
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(ts, fmt)
            except ValueError:
                continue
        # Python 3.7+ fallback
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            return None
    
    def get_content_hash(self) -> str:
        """获取消息内容哈希（用于去重，排除时间戳和msg_id）"""
        content = f"{self.from_node}:{self.to_node}:{self.msg_type}:{json.dumps(self.payload, sort_keys=True)}:{self.reply_to}"
        return hashlib.md5(content.encode()).hexdigest()


class MessageProtocol:
    """消息协议处理器 - 增强版"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        初始化消息协议
        
        Args:
            storage_dir: 消息持久化目录
        """
        self.message_history: List[Message] = []
        self.pending_messages: Dict[str, Message] = {}  # 待确认消息
        self.processed_hashes: Set[str] = set()  # 已处理消息哈希（去重）
        self.storage_dir = None
        self._lock = threading.Lock()
        
        if storage_dir:
            self.storage_dir = Path(storage_dir)
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._load_persisted_messages()
    
    def create_message(
        self,
        from_node: str,
        to_node: str,
        msg_type: str,
        payload: Dict,
        reply_to: Optional[str] = None,
        priority: int = 0,
        ttl: int = 3600,
        max_retries: int = 3,
    ) -> Message:
        """
        创建消息
        
        Args:
            from_node: 发送节点
            to_node: 接收节点
            msg_type: 消息类型
            payload: 消息载荷
            reply_to: 回复的消息ID
            priority: 优先级 (0=normal, 1=high, 2=critical)
            ttl: 消息存活时间（秒）
        
        Returns:
            Message: 消息对象
        """
        # 生成唯一消息ID（使用UUID避免冲突）
        msg_id = f"msg-{uuid.uuid4().hex[:12]}"
        
        message = Message(
            msg_id=msg_id,
            from_node=from_node,
            to_node=to_node,
            msg_type=msg_type,
            payload=payload,
            reply_to=reply_to,
            priority=priority,
            ttl=ttl,
        )
        
        with self._lock:
            # 记录内容哈希用于统计（不拦截，允许同内容多消息）
            content_hash = message.get_content_hash()
            self.processed_hashes.add(content_hash)
            
            self.message_history.append(message)
            self.pending_messages[msg_id] = message
        
        # 持久化
        if self.storage_dir:
            self._persist_message(message)
        
        return message
    
    def confirm_message(self, msg_id: str) -> bool:
        """
        确认消息已接收
        
        Args:
            msg_id: 消息ID
        
        Returns:
            bool: 是否成功确认
        """
        with self._lock:
            if msg_id in self.pending_messages:
                msg = self.pending_messages[msg_id]
                msg.confirmed = True
                msg.confirmed_at = datetime.now().isoformat()
                del self.pending_messages[msg_id]
                
                # 记录内容哈希用于去重
                self.processed_hashes.add(msg.get_content_hash())
                
                # 持久化确认状态
                if self.storage_dir:
                    self._persist_message(msg)
                
                return True
        return False
    
    def get_unconfirmed_messages(self) -> List[Message]:
        """获取所有未确认的消息"""
        with self._lock:
            return list(self.pending_messages.values())
    
    def get_expired_messages(self) -> List[Message]:
        """获取所有过期消息"""
        with self._lock:
            return [m for m in self.pending_messages.values() if m.is_expired()]
    
    def retry_message(self, msg_id: str) -> Optional[Message]:
        """
        重试发送消息
        
        Args:
            msg_id: 消息ID
        
        Returns:
            Optional[Message]: 重试的消息，如果达到最大重试次数返回None
        """
        with self._lock:
            if msg_id in self.pending_messages:
                msg = self.pending_messages[msg_id]
                if msg.retry_count < msg.max_retries - 1:  # 修正：使用 max_retries - 1
                    msg.retry_count += 1
                    msg.timestamp = datetime.now().isoformat()
                    
                    if self.storage_dir:
                        self._persist_message(msg)
                    
                    return msg
                else:
                    # 达到最大重试次数，丢弃
                    del self.pending_messages[msg_id]
                    return None
        return None
    
    def validate_message(self, message: Message) -> bool:
        """
        验证消息
        
        Args:
            message: 消息对象
        
        Returns:
            bool: 是否有效
        """
        required_fields = ["msg_id", "from", "to", "type", "timestamp", "payload"]
        
        data = message.to_dict()
        for field_name in required_fields:
            if field_name not in data:
                return False
        
        # 检查是否过期
        if message.is_expired():
            return False
        
        return True
    
    def get_messages(
        self,
        from_node: Optional[str] = None,
        to_node: Optional[str] = None,
        msg_type: Optional[str] = None,
        confirmed: Optional[bool] = None,
    ) -> List[Message]:
        """
        获取消息列表
        
        Args:
            from_node: 发送节点过滤
            to_node: 接收节点过滤
            msg_type: 消息类型过滤
            confirmed: 确认状态过滤
        
        Returns:
            List[Message]: 消息列表
        """
        messages = self.message_history
        
        if from_node:
            messages = [m for m in messages if m.from_node == from_node]
        if to_node:
            messages = [m for m in messages if m.to_node == to_node]
        if msg_type:
            messages = [m for m in messages if m.msg_type == msg_type]
        if confirmed is not None:
            messages = [m for m in messages if m.confirmed == confirmed]
        
        return messages
    
    def get_statistics(self) -> Dict:
        """
        获取消息统计信息
        
        Returns:
            Dict: 统计信息
        """
        type_counts = {}
        priority_counts = {0: 0, 1: 0, 2: 0}
        
        for msg in self.message_history:
            type_counts[msg.msg_type] = type_counts.get(msg.msg_type, 0) + 1
            priority_counts[msg.priority] = priority_counts.get(msg.priority, 0) + 1
        
        return {
            "total_messages": len(self.message_history),
            "pending_messages": len(self.pending_messages),
            "confirmed_messages": len([m for m in self.message_history if m.confirmed]),
            "type_counts": type_counts,
            "priority_counts": priority_counts,
            "dedup_hashes": len(self.processed_hashes),
        }
    
    def cleanup_expired(self) -> int:
        """
        清理过期消息
        
        Returns:
            int: 清理的消息数量
        """
        cleaned = 0
        with self._lock:
            expired = [msg_id for msg_id, msg in self.pending_messages.items() if msg.is_expired()]
            for msg_id in expired:
                del self.pending_messages[msg_id]
                cleaned += 1
        return cleaned
    
    def _persist_message(self, message: Message) -> None:
        """持久化消息到文件"""
        if not self.storage_dir:
            return
        
        try:
            filename = f"{message.msg_id}.json"
            filepath = self.storage_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(message.to_json())
        except Exception as e:
            print(f"持久化消息失败: {e}")
    
    def _load_persisted_messages(self) -> None:
        """从文件加载持久化消息"""
        if not self.storage_dir or not self.storage_dir.exists():
            return
        
        try:
            for filepath in self.storage_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    message = Message.from_dict(data)
                    self.message_history.append(message)
                    if not message.confirmed:
                        self.pending_messages[message.msg_id] = message
                except Exception as e:
                    print(f"加载消息失败 {filepath}: {e}")
        except Exception as e:
            print(f"加载持久化消息失败: {e}")
