"""
消息协议定义 V2 — 增强版

新增：
- ACK/NACK 确认机制
- 消息 TTL 与优先级
- 消息完整性校验（SHA256）
- 节点注册/注销/心跳协议
- 消息去重与重试计数
- 协议版本协商
"""

import json
import hashlib
import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field


# ========== 工具函数（Python 3.6 兼容） ==========

def _parse_iso(s: str) -> datetime:
    """解析 ISO 格式时间字符串（兼容 Python 3.6）"""
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"无法解析时间: {s}")


# ========== 常量 ==========

PROTOCOL_VERSION = "2.0"
DEFAULT_TTL_SECONDS = 300  # 5分钟
MAX_RETRY_COUNT = 3

# 消息类型
MSG_TYPES = {
    # 注册协议
    "NODE_REGISTER",
    "NODE_REGISTER_ACK",
    "NODE_REGISTER_NACK",
    "NODE_DEREGISTER",
    "NODE_DEREGISTER_ACK",
    # 心跳协议
    "HEARTBEAT",
    "HEARTBEAT_ACK",
    # 业务消息
    "DIALOGUE_TRIGGER",
    "TRAINING_TASK",
    "EMERGENCE_REPORT",
    "DATA_REQUEST",
    "DATA_RESPONSE",
    "ERROR",
    # 控制消息
    "PING",
    "PONG",
    "ACK",
    "NACK",
}

# 优先级
PRIORITY_CRITICAL = 0
PRIORITY_HIGH = 1
PRIORITY_NORMAL = 2
PRIORITY_LOW = 3


@dataclass
class Message:
    """小龙虾网络消息 V2"""

    msg_id: str
    from_node: str
    to_node: str
    msg_type: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    payload: Dict = field(default_factory=dict)
    reply_to: Optional[str] = None
    ttl_seconds: int = DEFAULT_TTL_SECONDS
    priority: int = PRIORITY_NORMAL
    retry_count: int = 0
    protocol_version: str = PROTOCOL_VERSION
    checksum: Optional[str] = None

    # ---- 序列化 ----

    def to_dict(self) -> dict:
        """转换为字典"""
        d = {
            "msg_id": self.msg_id,
            "from": self.from_node,
            "to": self.to_node,
            "type": self.msg_type,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "reply_to": self.reply_to,
            "ttl_seconds": self.ttl_seconds,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "protocol_version": self.protocol_version,
        }
        if self.checksum:
            d["checksum"] = self.checksum
        return d

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    # ---- 反序列化 ----

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
            ttl_seconds=data.get("ttl_seconds", DEFAULT_TTL_SECONDS),
            priority=data.get("priority", PRIORITY_NORMAL),
            retry_count=data.get("retry_count", 0),
            protocol_version=data.get("protocol_version", PROTOCOL_VERSION),
            checksum=data.get("checksum"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """从 JSON 字符串创建消息"""
        return cls.from_dict(json.loads(json_str))

    # ---- 完整性校验 ----

    def compute_checksum(self) -> str:
        """计算消息体 SHA256 校验和"""
        raw = json.dumps(
            {
                "msg_id": self.msg_id,
                "from": self.from_node,
                "to": self.to_node,
                "type": self.msg_type,
                "timestamp": self.timestamp,
                "payload": self.payload,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def verify_checksum(self) -> bool:
        """校验消息完整性"""
        if not self.checksum:
            return True  # 旧版消息无校验和，默认通过
        return self.checksum == self.compute_checksum()

    def sign(self) -> str:
        """签名并返回校验和"""
        self.checksum = self.compute_checksum()
        return self.checksum

    # ---- TTL ----

    def is_expired(self) -> bool:
        """检查消息是否过期"""
        try:
            ts = _parse_iso(self.timestamp)
            expiry = ts + timedelta(seconds=self.ttl_seconds)
            return datetime.now() > expiry
        except (ValueError, TypeError):
            return False

    # ---- 重试 ----

    def can_retry(self) -> bool:
        """是否还可以重试"""
        return self.retry_count < MAX_RETRY_COUNT

    def increment_retry(self) -> None:
        """增加重试计数"""
        self.retry_count += 1


# ========== 工厂方法 ==========


class MessageFactory:
    """消息工厂 — 统一创建各类协议消息"""

    @staticmethod
    def create(
        from_node: str,
        to_node: str,
        msg_type: str,
        payload: Dict = None,
        reply_to: Optional[str] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        priority: int = PRIORITY_NORMAL,
    ) -> Message:
        """创建消息并自动签名"""
        msg = Message(
            msg_id=f"msg-{uuid.uuid4().hex[:12]}",
            from_node=from_node,
            to_node=to_node,
            msg_type=msg_type,
            payload=payload or {},
            reply_to=reply_to,
            ttl_seconds=ttl_seconds,
            priority=priority,
        )
        msg.sign()
        return msg

    @staticmethod
    def register(
        from_node: str,
        node_info: Dict,
    ) -> Message:
        """创建节点注册消息"""
        return MessageFactory.create(
            from_node=from_node,
            to_node="REGISTRY",  # 广播到注册中心
            msg_type="NODE_REGISTER",
            payload={
                "node_info": node_info,
                "protocol_version": PROTOCOL_VERSION,
            },
            priority=PRIORITY_CRITICAL,
            ttl_seconds=60,
        )

    @staticmethod
    def register_ack(msg_id: str, from_node: str, to_node: str, success: bool, reason: str = "") -> Message:
        """创建注册确认消息"""
        return MessageFactory.create(
            from_node=from_node,
            to_node=to_node,
            msg_type="NODE_REGISTER_ACK" if success else "NODE_REGISTER_NACK",
            payload={"success": success, "reason": reason},
            reply_to=msg_id,
            priority=PRIORITY_CRITICAL,
        )

    @staticmethod
    def deregister(from_node: str, reason: str = "") -> Message:
        """创建节点注销消息"""
        return MessageFactory.create(
            from_node=from_node,
            to_node="REGISTRY",
            msg_type="NODE_DEREGISTER",
            payload={"reason": reason},
            priority=PRIORITY_CRITICAL,
        )

    @staticmethod
    def heartbeat(from_node: str, status: Dict = None) -> Message:
        """创建心跳消息"""
        return MessageFactory.create(
            from_node=from_node,
            to_node="REGISTRY",
            msg_type="HEARTBEAT",
            payload={
                "status": status or {},
                "uptime_since": datetime.now().isoformat(),
            },
            priority=PRIORITY_HIGH,
            ttl_seconds=30,
        )

    @staticmethod
    def ack(msg_id: str, from_node: str, to_node: str) -> Message:
        """创建 ACK"""
        return MessageFactory.create(
            from_node=from_node,
            to_node=to_node,
            msg_type="ACK",
            payload={"acked_msg_id": msg_id},
            reply_to=msg_id,
        )

    @staticmethod
    def nack(msg_id: str, from_node: str, to_node: str, reason: str = "") -> Message:
        """创建 NACK"""
        return MessageFactory.create(
            from_node=from_node,
            to_node=to_node,
            msg_type="NACK",
            payload={"nacked_msg_id": msg_id, "reason": reason},
            reply_to=msg_id,
            priority=PRIORITY_HIGH,
        )

    @staticmethod
    def ping(from_node: str, to_node: str) -> Message:
        """创建 PING"""
        return MessageFactory.create(
            from_node=from_node,
            to_node=to_node,
            msg_type="PING",
            payload={},
        )

    @staticmethod
    def pong(msg_id: str, from_node: str, to_node: str) -> Message:
        """创建 PONG"""
        return MessageFactory.create(
            from_node=from_node,
            to_node=to_node,
            msg_type="PONG",
            payload={"ping_msg_id": msg_id},
            reply_to=msg_id,
        )


# ========== 协议处理器 ==========


class MessageProtocol:
    """消息协议处理器 V2"""

    def __init__(self):
        self.message_history: List[Message] = []
        self._seen_ids: set = set()  # 去重集合

    def create_message(
        self,
        from_node: str,
        to_node: str,
        msg_type: str,
        payload: Dict = None,
        reply_to: Optional[str] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        priority: int = PRIORITY_NORMAL,
    ) -> Message:
        """创建消息（兼容旧接口）"""
        return MessageFactory.create(
            from_node=from_node,
            to_node=to_node,
            msg_type=msg_type,
            payload=payload,
            reply_to=reply_to,
            ttl_seconds=ttl_seconds,
            priority=priority,
        )

    def validate_message(self, message: Message) -> tuple:
        """
        验证消息 V2 — 返回 (is_valid, reason)
        检查：必填字段、消息类型、协议版本、完整性、TTL、去重
        """
        # 必填字段
        required = ["msg_id", "from_node", "to_node", "msg_type", "timestamp"]
        for f in required:
            if not getattr(message, f, None):
                return False, f"缺少必填字段: {f}"

        # 消息类型
        if message.msg_type not in MSG_TYPES:
            return False, f"未知消息类型: {message.msg_type}"

        # 协议版本（仅警告，不拒绝）
        if message.protocol_version != PROTOCOL_VERSION:
            pass  # 记录日志但不拒绝

        # 完整性校验
        if message.checksum and not message.verify_checksum():
            return False, "消息校验和不匹配，可能已被篡改"

        # TTL
        if message.is_expired():
            return False, "消息已过期"

        # 去重
        if message.msg_id in self._seen_ids:
            return False, "消息重复"

        return True, "ok"

    def accept_message(self, message: Message) -> bool:
        """
        接收并验证消息，通过则记录并返回 True
        """
        valid, reason = self.validate_message(message)
        if not valid:
            return False
        self.message_history.append(message)
        self._seen_ids.add(message.msg_id)
        return True

    def get_messages(
        self,
        from_node: Optional[str] = None,
        to_node: Optional[str] = None,
        msg_type: Optional[str] = None,
    ) -> List[Message]:
        """获取消息列表"""
        messages = self.message_history
        if from_node:
            messages = [m for m in messages if m.from_node == from_node]
        if to_node:
            messages = [m for m in messages if m.to_node == to_node]
        if msg_type:
            messages = [m for m in messages if m.msg_type == msg_type]
        return messages

    def get_statistics(self) -> Dict:
        """获取消息统计信息"""
        type_counts = {}
        for msg in self.message_history:
            type_counts[msg.msg_type] = type_counts.get(msg.msg_type, 0) + 1
        return {
            "total_messages": len(self.message_history),
            "type_counts": type_counts,
            "protocol_version": PROTOCOL_VERSION,
        }

    def dedup_count(self) -> int:
        """去重集合大小"""
        return len(self._seen_ids)
