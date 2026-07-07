#!/usr/bin/env python3
"""
小龙虾网络 MQTT 核心客户端 v1.0
===============================
基于 paho-mqtt 的轻量 MQTT 通信层，为围棋训练和对局提供底层支撑。

核心能力：
  - 自动连接/重连 (指数退避)
  - 发布/订阅 (QoS 1)
  - 心跳检测 (遗嘱消息)
  - 消息序列化/反序列化 (统一 JSON 格式)
  - 在线节点感知

依赖：pip install paho-mqtt
"""

import json
import time
import uuid
import threading
import logging
from typing import Optional, Callable, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

import paho.mqtt.client as mqtt

logger = logging.getLogger("lobster.mqtt")


# ==================== 常量 ====================

class TopicPrefix:
    """主题前缀（围棋专用）"""
    ROOT = "lobster/go"
    SYSTEM = f"{ROOT}/system"
    HEARTBEAT = f"{SYSTEM}/heartbeat"
    ANNOUNCE = f"{SYSTEM}/announce"
    STATUS_REQUEST = f"{SYSTEM}/status/request"


class Topic:
    """主题构建工具"""
    @staticmethod
    def training_task(node_id: str) -> str:
        return f"{TopicPrefix.ROOT}/{node_id}/training/task"

    @staticmethod
    def training_result(node_id: str) -> str:
        return f"{TopicPrefix.ROOT}/{node_id}/training/result"

    @staticmethod
    def training_status(node_id: str) -> str:
        return f"{TopicPrefix.ROOT}/{node_id}/training/status"

    @staticmethod
    def match_move(match_id: str) -> str:
        return f"{TopicPrefix.ROOT}/matches/{match_id}/move"

    @staticmethod
    def match_status(match_id: str) -> str:
        return f"{TopicPrefix.ROOT}/matches/{match_id}/status"

    @staticmethod
    def match_chat(match_id: str) -> str:
        return f"{TopicPrefix.ROOT}/matches/{match_id}/chat"


class MessageType(str, Enum):
    TRAINING_TASK = "training_task"
    TRAINING_RESULT = "training_result"
    TRAINING_STATUS = "training_status"
    MATCH_MOVE = "match_move"
    MATCH_STATUS = "match_status"
    MATCH_CHAT = "match_chat"
    HEARTBEAT = "heartbeat"
    ANNOUNCE = "announce"
    STATUS_REQUEST = "status_request"
    STATUS_RESPONSE = "status_response"


# ==================== 数据类 ====================

@dataclass
class LobsterMessage:
    """统一消息格式，与现有文件系统消息队列兼容"""
    msg_id: str
    type: str                       # MessageType 值
    from_node: str
    to_node: str                    # 目标节点，"*" 表示广播
    timestamp: str
    payload: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, data: str) -> "LobsterMessage":
        d = json.loads(data) if isinstance(data, str) else data
        return cls(**d)

    @classmethod
    def create(
        cls,
        msg_type: str,
        from_node: str,
        to_node: str,
        payload: dict,
    ) -> "LobsterMessage":
        return cls(
            msg_id=f"mqtt-{from_node}-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}",
            type=msg_type,
            from_node=from_node,
            to_node=to_node,
            timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            payload=payload,
        )


@dataclass
class NodeStatus:
    """在线节点信息"""
    node_id: str
    status: str                     # online | offline
    last_seen: str
    role: str                       # coach | agent | hybrid
    level: Optional[str] = None     # 围棋等级（如有）


# ==================== MQTT 客户端 ====================

class LobsterMQTTClient:
    """小龙虾网络 MQTT 客户端"""

    def __init__(
        self,
        node_id: str,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        role: str = "agent",
        level: Optional[str] = None,
        keepalive: int = 60,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.node_id = node_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.role = role
        self.level = level
        self.keepalive = keepalive

        # 回调注册表
        self._handlers: Dict[str, List[Callable]] = {}
        self._default_handler: Optional[Callable] = None

        # 在线节点缓存
        self.online_nodes: Dict[str, NodeStatus] = {}
        self._nodes_lock = threading.Lock()

        # 连接状态
        self._connected = threading.Event()
        self._running = False
        self._reconnect_thread: Optional[threading.Thread] = None

        # 构建 MQTT 客户端
        self._client = mqtt.Client(
            client_id=f"lobster-{node_id}-{uuid.uuid4().hex[:6]}",
            protocol=mqtt.MQTTv5,
        )
        if username and password:
            self._client.username_pw_set(username, password)

        # 设置遗嘱消息：异常断线时 Broker 自动发布
        self._client.will_set(
            TopicPrefix.HEARTBEAT,
            payload=json.dumps({
                "node_id": node_id,
                "status": "offline",
                "source": "lwt",
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            }),
            qos=1,
            retain=False,
        )

        # 注册 MQTT 回调
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

    # ==================== 公开 API ====================

    def connect(self) -> bool:
        """连接 Broker（阻塞，自动重试）"""
        logger.info(f"🦞 [{self.node_id}] 正在连接 MQTT Broker {self.broker_host}:{self.broker_port}...")
        try:
            self._client.connect(self.broker_host, self.broker_port, self.keepalive)
            self._running = True
            self._client.loop_start()
            # 等待连接成功
            if self._connected.wait(timeout=10):
                logger.info(f"🦞 [{self.node_id}] MQTT 连接成功 ✓")
                return True
            else:
                logger.error(f"🦞 [{self.node_id}] MQTT 连接超时")
                return False
        except Exception as e:
            logger.error(f"🦞 [{self.node_id}] MQTT 连接失败: {e}")
            return False

    def connect_async(self):
        """异步连接（不阻塞）"""
        self._running = True
        self._client.connect_async(self.broker_host, self.broker_port, self.keepalive)
        self._client.loop_start()

    def disconnect(self):
        """主动断开"""
        self._running = False
        # 发布主动离线消息
        self._publish_heartbeat("offline", "agent")
        time.sleep(0.5)
        self._client.loop_stop()
        self._client.disconnect()
        logger.info(f"🦞 [{self.node_id}] MQTT 已断开")

    def is_connected(self) -> bool:
        return self._connected.is_set()

    # -- 发布 --

    def publish_training_task(self, to_node: str, payload: dict) -> str:
        """发送训练任务（教练→学员）"""
        return self._publish_msg(
            MessageType.TRAINING_TASK, to_node, payload,
            topic=Topic.training_task(to_node),
        )

    def publish_training_result(self, to_node: str, payload: dict) -> str:
        """提交训练结果（学员→教练）"""
        return self._publish_msg(
            MessageType.TRAINING_RESULT, to_node, payload,
            topic=Topic.training_result(self.node_id),
        )

    def publish_training_status(self, to_node: str, payload: dict) -> str:
        """更新训练状态"""
        return self._publish_msg(
            MessageType.TRAINING_STATUS, to_node, payload,
            topic=Topic.training_status(self.node_id),
        )

    def publish_match_move(self, match_id: str, to_node: str, payload: dict) -> str:
        """落子"""
        return self._publish_msg(
            MessageType.MATCH_MOVE, to_node, payload,
            topic=Topic.match_move(match_id),
        )

    def publish_match_status(self, match_id: str, to_node: str, payload: dict) -> str:
        """对局状态变更"""
        return self._publish_msg(
            MessageType.MATCH_STATUS, to_node, payload,
            topic=Topic.match_status(match_id),
        )

    def publish_match_chat(self, match_id: str, to_node: str, payload: dict) -> str:
        """对局聊天"""
        return self._publish_msg(
            MessageType.MATCH_CHAT, to_node, payload,
            topic=Topic.match_chat(match_id),
        )

    def publish_announce(self, message: str) -> str:
        """广播公告"""
        return self._publish_msg(
            MessageType.ANNOUNCE, "*",
            {"message": message},
            topic=TopicPrefix.ANNOUNCE,
        )

    def request_status(self) -> str:
        """请求所有节点上报状态"""
        return self._publish_msg(
            MessageType.STATUS_REQUEST, "*",
            {"requester": self.node_id},
            topic=TopicPrefix.STATUS_REQUEST,
        )

    # -- 订阅 --

    def subscribe_training(self):
        """订阅本节点训练主题"""
        self._subscribe(Topic.training_task(self.node_id))
        logger.info(f"🦞 [{self.node_id}] 已订阅训练主题")

    def subscribe_matches(self):
        """订阅所有对局主题"""
        self._subscribe(f"{TopicPrefix.ROOT}/matches/+/move")
        self._subscribe(f"{TopicPrefix.ROOT}/matches/+/status")
        self._subscribe(f"{TopicPrefix.ROOT}/matches/+/chat")
        logger.info(f"🦞 [{self.node_id}] 已订阅对局主题")

    def subscribe_system(self):
        """订阅系统主题"""
        self._subscribe(TopicPrefix.HEARTBEAT)
        self._subscribe(TopicPrefix.ANNOUNCE)
        self._subscribe(TopicPrefix.STATUS_REQUEST)
        logger.info(f"🦞 [{self.node_id}] 已订阅系统主题")

    def subscribe_all(self):
        """一键订阅围棋训练所需全部主题"""
        self.subscribe_training()
        self.subscribe_matches()
        self.subscribe_system()

    # -- 回调注册 --

    def on(self, msg_type: str):
        """装饰器：注册消息处理回调"""
        def decorator(func: Callable):
            self._handlers.setdefault(msg_type, []).append(func)
            return func
        return decorator

    def on_any(self, func: Callable):
        """注册默认消息处理器（未匹配到类型的消息走这里）"""
        self._default_handler = func
        return func

    # -- 查询 --

    def get_online_nodes(self) -> List[NodeStatus]:
        """获取在线节点列表"""
        with self._nodes_lock:
            return list(self.online_nodes.values())

    def get_online_coaches(self) -> List[str]:
        """获取在线教练"""
        with self._nodes_lock:
            return [
                n.node_id for n in self.online_nodes.values()
                if n.role == "coach" and n.status == "online"
            ]

    def get_online_agents(self) -> List[str]:
        """获取在线学员"""
        with self._nodes_lock:
            return [
                n.node_id for n in self.online_nodes.values()
                if n.role in ("agent", "hybrid") and n.status == "online"
            ]

    # ==================== 内部方法 ====================

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        """连接成功回调"""
        if reason_code == 0:
            self._connected.set()
        else:
            logger.error(f"🦞 [{self.node_id}] 连接失败: reason_code={reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        """断开回调"""
        self._connected.clear()
        if self._running:
            logger.warning(f"🦞 [{self.node_id}] MQTT 断开 (reason={reason_code})，将自动重连...")
            # paho-mqtt 自带自动重连，这里做日志即可

    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            payload_str = msg.payload.decode("utf-8")
            message = LobsterMessage.from_json(payload_str)
        except Exception as e:
            logger.warning(f"🦞 [{self.node_id}] 消息解析失败: {e}, raw={msg.payload[:100]}")
            return

        # 心跳消息特殊处理
        if message.type == MessageType.HEARTBEAT:
            self._handle_heartbeat(message)
            return

        # 状态响应
        if message.type == MessageType.STATUS_RESPONSE:
            self._handle_status_response(message)
            return

        # 分发到注册的处理器
        handlers = self._handlers.get(message.type, [])
        if handlers:
            for handler in handlers:
                try:
                    handler(message)
                except Exception as e:
                    logger.error(f"🦞 [{self.node_id}] 消息处理器异常: {e}", exc_info=True)
        elif self._default_handler:
            try:
                self._default_handler(message)
            except Exception as e:
                logger.error(f"🦞 [{self.node_id}] 默认处理器异常: {e}", exc_info=True)

    def _publish_heartbeat(self, status: str, source: str):
        """发布心跳"""
        payload = json.dumps({
            "node_id": self.node_id,
            "status": status,
            "source": source,
            "role": self.role,
            "level": self.level,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        })
        self._client.publish(TopicPrefix.HEARTBEAT, payload, qos=1)
        self._client.publish(
            f"{TopicPrefix.ROOT}/{self.node_id}/status",
            payload, qos=1, retain=True,
        )

    def _handle_heartbeat(self, message: LobsterMessage):
        """处理心跳消息"""
        node_id = message.payload.get("node_id")
        status = message.payload.get("status", "unknown")

        with self._nodes_lock:
            if node_id:
                self.online_nodes[node_id] = NodeStatus(
                    node_id=node_id,
                    status=status,
                    last_seen=message.timestamp,
                    role=message.payload.get("role", "unknown"),
                    level=message.payload.get("level"),
                )

    def _handle_status_response(self, message: LobsterMessage):
        """处理状态响应（与心跳合并）"""
        self._handle_heartbeat(message)

    def _publish_msg(
        self,
        msg_type: str,
        to_node: str,
        payload: dict,
        topic: str,
    ) -> str:
        """统一发布方法"""
        message = LobsterMessage.create(
            msg_type=msg_type,
            from_node=self.node_id,
            to_node=to_node,
            payload=payload,
        )
        self._client.publish(topic, message.to_json(), qos=1)
        logger.debug(f"🦞 [{self.node_id}] → {to_node} [{msg_type}] msg_id={message.msg_id}")
        return message.msg_id

    def _subscribe(self, topic: str):
        """订阅主题"""
        self._client.subscribe(topic, qos=1)

    # ==================== 心跳循环（独立线程） ====================

    def start_heartbeat(self, interval: int = 30):
        """启动心跳线程"""
        def heartbeat_loop():
            self._publish_heartbeat("online", "agent")
            while self._running:
                time.sleep(interval)
                if self._connected.is_set():
                    self._publish_heartbeat("online", "agent")

        t = threading.Thread(target=heartbeat_loop, daemon=True, name="lobster-heartbeat")
        t.start()
        logger.info(f"🦞 [{self.node_id}] 心跳线程已启动 (间隔 {interval}s)")
        return t


# ==================== 便捷工厂 ====================

def create_coach_client(
    coach_id: str,
    broker_host: str = "localhost",
    broker_port: int = 1883,
) -> LobsterMQTTClient:
    """创建教练客户端"""
    return LobsterMQTTClient(
        node_id=coach_id,
        broker_host=broker_host,
        broker_port=broker_port,
        role="coach",
    )


def create_student_client(
    student_id: str,
    level: str,
    broker_host: str = "localhost",
    broker_port: int = 1883,
) -> LobsterMQTTClient:
    """创建学员客户端"""
    return LobsterMQTTClient(
        node_id=student_id,
        broker_host=broker_host,
        broker_port=broker_port,
        role="agent",
        level=level,
    )
