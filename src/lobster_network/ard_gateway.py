#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 ARD 网关 V5.0
Agentic Resource Discovery 协议网关

功能：
1. ARD 协议解析/封装
2. 跨平台 Agent 通信
3. ARD 消息路由
4. 协议转换（ARD ↔ 小龙虾协议）
"""

import json
import os
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .ard_protocol import ARDProtocol, ARDAgent, ARDResource


# ========== 常量定义 ==========

# ARD 网关版本
ARD_GATEWAY_VERSION = "1.0"

# ARD 消息类型
ARD_MSG_TYPE_DISCOVER = "discover"           # 发现请求
ARD_MSG_TYPE_REGISTER = "register"           # 注册请求
ARD_MSG_TYPE_MATCH = "match"                 # 匹配请求
ARD_MSG_TYPE_COLLABORATE = "collaborate"     # 协同请求
ARD_MSG_TYPE_RESPONSE = "response"           # 响应消息
ARD_MSG_TYPE_ERROR = "error"                 # 错误消息

# ARD 协议版本
ARD_PROTOCOL_VERSION = "1.0"


# ========== 数据类定义 ==========

@dataclass
class ARDMessage:
    """ARD 消息"""
    message_id: str
    msg_type: str
    sender_id: str
    receiver_id: str
    payload: Dict
    protocol_version: str = ARD_PROTOCOL_VERSION
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    signature: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "message_id": self.message_id,
            "type": self.msg_type,
            "sender": self.sender_id,
            "receiver": self.receiver_id,
            "payload": self.payload,
            "protocol_version": self.protocol_version,
            "timestamp": self.timestamp,
            "signature": self.signature,
        }

    def sign(self, private_key: str) -> str:
        """签名消息"""
        data = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        self.signature = hashlib.sha256(f"{data}:{private_key}".encode()).hexdigest()
        return self.signature

    def verify(self, public_key: str) -> bool:
        """验证消息签名"""
        if not self.signature:
            return False
        data = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        expected_signature = hashlib.sha256(f"{data}:{public_key}".encode()).hexdigest()
        return self.signature == expected_signature


@dataclass
class ARDEndpoint:
    """ARD 端点"""
    endpoint_id: str
    name: str
    url: str
    protocol: str = "ard"
    version: str = ARD_PROTOCOL_VERSION
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"
    last_heartbeat: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "endpoint_id": self.endpoint_id,
            "name": self.name,
            "url": self.url,
            "protocol": self.protocol,
            "version": self.version,
            "capabilities": self.capabilities,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "metadata": self.metadata,
        }


# ========== ARD 网关 ==========

class ARDGateway:
    """ARD 网关"""

    def __init__(self, ard_protocol: ARDProtocol, data_dir: str = "/shared/lobster-network-data/ard-gateway"):
        self.ard_protocol = ard_protocol
        self.data_dir = data_dir
        self.endpoints: Dict[str, ARDEndpoint] = {}
        self.message_queue: List[ARDMessage] = []
        self._endpoint_counter = 0
        self._message_counter = 0

        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)

    # ========== 端点管理 ==========

    def register_endpoint(
        self,
        name: str,
        url: str,
        capabilities: List[str] = None,
        protocol: str = "ard",
        metadata: Dict = None,
    ) -> Tuple[bool, str]:
        """
        注册 ARD 端点

        Args:
            name: 端点名称
            url: 端点 URL
            capabilities: 能力列表
            protocol: 协议类型
            metadata: 元数据

        Returns:
            (成功，消息)
        """
        self._endpoint_counter += 1
        endpoint_id = f"ard-endpoint-{self._endpoint_counter:04d}"

        endpoint = ARDEndpoint(
            endpoint_id=endpoint_id,
            name=name,
            url=url,
            protocol=protocol,
            capabilities=capabilities or [],
            metadata=metadata or {},
        )
        self.endpoints[endpoint_id] = endpoint

        return True, f"端点 {name} 注册成功 (ID: {endpoint_id})"

    def heartbeat(self, endpoint_id: str) -> Tuple[bool, str]:
        """
        端点心跳

        Args:
            endpoint_id: 端点 ID

        Returns:
            (成功，消息)
        """
        endpoint = self.endpoints.get(endpoint_id)
        if not endpoint:
            return False, f"端点 {endpoint_id} 不存在"

        endpoint.last_heartbeat = datetime.now().isoformat()
        endpoint.status = "active"

        return True, f"端点 {endpoint.name} 心跳正常"

    def get_active_endpoints(self) -> List[ARDEndpoint]:
        """获取活跃端点"""
        return [ep for ep in self.endpoints.values() if ep.status == "active"]

    # ========== 消息处理 ==========

    def send_message(
        self,
        msg_type: str,
        sender_id: str,
        receiver_id: str,
        payload: Dict,
        private_key: str = "",
    ) -> Tuple[bool, str]:
        """
        发送 ARD 消息

        Args:
            msg_type: 消息类型
            sender_id: 发送方 ID
            receiver_id: 接收方 ID
            payload: 消息载荷
            private_key: 私钥（用于签名）

        Returns:
            (成功，消息)
        """
        self._message_counter += 1
        message_id = f"ard-msg-{self._message_counter:06d}"

        message = ARDMessage(
            message_id=message_id,
            msg_type=msg_type,
            sender_id=sender_id,
            receiver_id=receiver_id,
            payload=payload,
        )

        # 签名消息
        if private_key:
            message.sign(private_key)

        # 添加到消息队列
        self.message_queue.append(message)

        return True, f"消息 {message_id} 发送成功"

    def receive_message(self, message_id: str) -> Optional[ARDMessage]:
        """
        接收 ARD 消息

        Args:
            message_id: 消息 ID

        Returns:
            消息对象
        """
        for message in self.message_queue:
            if message.message_id == message_id:
                return message
        return None

    def process_message(self, message: ARDMessage) -> Tuple[bool, str]:
        """
        处理 ARD 消息

        Args:
            message: 消息对象

        Returns:
            (成功，消息)
        """
        if message.msg_type == ARD_MSG_TYPE_DISCOVER:
            return self._process_discover(message)
        elif message.msg_type == ARD_MSG_TYPE_REGISTER:
            return self._process_register(message)
        elif message.msg_type == ARD_MSG_TYPE_MATCH:
            return self._process_match(message)
        elif message.msg_type == ARD_MSG_TYPE_COLLABORATE:
            return self._process_collaborate(message)
        else:
            return False, f"未知消息类型: {message.msg_type}"

    def _process_discover(self, message: ARDMessage) -> Tuple[bool, str]:
        """处理发现请求"""
        criteria = message.payload.get("criteria", {})
        resource_type = message.payload.get("resource_type")

        if resource_type:
            # 发现资源
            resources = self.ard_protocol.discover_resources(resource_type, criteria)
            result = [r.to_dict() for r in resources]
        else:
            # 发现 Agent
            agents = self.ard_protocol.discover_agents(criteria)
            result = [a.to_dict() for a in agents]

        # 发送响应
        response_payload = {
            "request_id": message.message_id,
            "result": result,
            "count": len(result),
        }
        self.send_message(
            msg_type=ARD_MSG_TYPE_RESPONSE,
            sender_id="gateway",
            receiver_id=message.sender_id,
            payload=response_payload,
        )

        return True, f"发现请求处理完成，找到 {len(result)} 个结果"

    def _process_register(self, message: ARDMessage) -> Tuple[bool, str]:
        """处理注册请求"""
        register_type = message.payload.get("type")
        data = message.payload.get("data", {})

        if register_type == "agent":
            # 注册 Agent
            ok, msg = self.ard_protocol.register_agent(
                name=data.get("name", ""),
                agent_type=data.get("agent_type", "general"),
                capabilities=data.get("capabilities", []),
                endpoint=data.get("endpoint", ""),
                metadata=data.get("metadata", {}),
            )
        elif register_type == "resource":
            # 注册资源
            ok, msg = self.ard_protocol.register_resource(
                name=data.get("name", ""),
                resource_type=data.get("resource_type", ""),
                description=data.get("description", ""),
                endpoint=data.get("endpoint", ""),
                provider_id=data.get("provider_id", ""),
                metadata=data.get("metadata", {}),
            )
        else:
            return False, f"未知注册类型: {register_type}"

        # 发送响应
        response_payload = {
            "request_id": message.message_id,
            "success": ok,
            "message": msg,
        }
        self.send_message(
            msg_type=ARD_MSG_TYPE_RESPONSE,
            sender_id="gateway",
            receiver_id=message.sender_id,
            payload=response_payload,
        )

        return ok, msg

    def _process_match(self, message: ARDMessage) -> Tuple[bool, str]:
        """处理匹配请求"""
        task_id = message.payload.get("task_id")
        match_algorithm = message.payload.get("match_algorithm", "hybrid")

        if not task_id:
            return False, "缺少 task_id"

        ok, msg, matched_agents = self.ard_protocol.match_agents(task_id, match_algorithm)

        # 发送响应
        response_payload = {
            "request_id": message.message_id,
            "success": ok,
            "message": msg,
            "matched_agents": matched_agents,
        }
        self.send_message(
            msg_type=ARD_MSG_TYPE_RESPONSE,
            sender_id="gateway",
            receiver_id=message.sender_id,
            payload=response_payload,
        )

        return ok, msg

    def _process_collaborate(self, message: ARDMessage) -> Tuple[bool, str]:
        """处理协同请求"""
        task_id = message.payload.get("task_id")
        agent_ids = message.payload.get("agent_ids", [])

        if not task_id or not agent_ids:
            return False, "缺少 task_id 或 agent_ids"

        ok, msg = self.ard_protocol.create_collaboration(task_id, agent_ids)

        # 发送响应
        response_payload = {
            "request_id": message.message_id,
            "success": ok,
            "message": msg,
        }
        self.send_message(
            msg_type=ARD_MSG_TYPE_RESPONSE,
            sender_id="gateway",
            receiver_id=message.sender_id,
            payload=response_payload,
        )

        return ok, msg

    # ========== 协议转换 ==========

    def convert_to_ard(self, lobster_message: Dict) -> ARDMessage:
        """
        小龙虾消息转换为 ARD 消息

        Args:
            lobster_message: 小龙虾消息

        Returns:
            ARD 消息
        """
        msg_type = lobster_message.get("type", "discover")
        payload = lobster_message.get("payload", {})

        return ARDMessage(
            message_id=lobster_message.get("msg_id", str(uuid.uuid4())),
            msg_type=msg_type,
            sender_id=lobster_message.get("from_node", ""),
            receiver_id=lobster_message.get("to_node", ""),
            payload=payload,
        )

    def convert_from_ard(self, ard_message: ARDMessage) -> Dict:
        """
        ARD 消息转换为小龙虾消息

        Args:
            ard_message: ARD 消息

        Returns:
            小龙虾消息
        """
        return {
            "msg_id": ard_message.message_id,
            "from_node": ard_message.sender_id,
            "to_node": ard_message.receiver_id,
            "type": ard_message.msg_type,
            "payload": ard_message.payload,
            "timestamp": ard_message.timestamp,
        }

    # ========== 查询功能 ==========

    def get_endpoint(self, endpoint_id: str) -> Optional[Dict]:
        """获取端点"""
        endpoint = self.endpoints.get(endpoint_id)
        return endpoint.to_dict() if endpoint else None

    def get_all_endpoints(self) -> List[Dict]:
        """获取所有端点"""
        return [ep.to_dict() for ep in self.endpoints.values()]

    def get_message_queue(self, limit: int = 20) -> List[Dict]:
        """获取消息队列"""
        return [msg.to_dict() for msg in self.message_queue[-limit:]]

    def get_gateway_statistics(self) -> Dict:
        """获取网关统计"""
        return {
            "total_endpoints": len(self.endpoints),
            "active_endpoints": len(self.get_active_endpoints()),
            "total_messages": len(self.message_queue),
            "ard_statistics": self.ard_protocol.get_ard_statistics(),
        }

    # ========== 持久化 ==========

    def save_data(self):
        """保存数据"""
        data = {
            "endpoints": {eid: ep.to_dict() for eid, ep in self.endpoints.items()},
            "message_queue": [msg.to_dict() for msg in self.message_queue],
            "counters": {
                "endpoint": self._endpoint_counter,
                "message": self._message_counter,
            },
        }
        with open(os.path.join(self.data_dir, "gateway_data.json"), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_data(self):
        """加载数据"""
        data_file = os.path.join(self.data_dir, "gateway_data.json")
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.endpoints = {eid: ARDEndpoint(**ep) for eid, ep in data.get("endpoints", {}).items()}
            self.message_queue = [ARDMessage(**msg) for msg in data.get("message_queue", [])]

            counters = data.get("counters", {})
            self._endpoint_counter = counters.get("endpoint", 0)
            self._message_counter = counters.get("message", 0)

            return True
        return False