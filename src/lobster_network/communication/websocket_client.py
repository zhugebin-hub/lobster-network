#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket客户端 - 小龙虾网络v3.0
实现节点连接、消息发送/接收、心跳、自动重连
"""

import asyncio
import json
import time
import uuid
import hmac
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import websockets
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebSocketClientConfig:
    """客户端配置"""
    node_id: str
    server_uri: str = "ws://localhost:8765"
    secret_key: str = "lobster-network-v3-secret-key"
    capabilities: List[str] = field(default_factory=list)
    reconnect_interval: int = 5  # 重连间隔（秒）
    max_reconnect_attempts: int = 10  # 最大重连次数
    heartbeat_interval: int = 30  # 心跳间隔（秒）


class WebSocketClient:
    """WebSocket客户端 - v3.0"""
    
    def __init__(self, config: WebSocketClientConfig):
        """
        初始化WebSocket客户端
        
        Args:
            config: 客户端配置
        """
        self.config = config
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.is_connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_messages: Dict[str, dict] = {}  # 待确认消息
        self.reconnect_attempts = 0
        
    async def connect(self):
        """连接到服务器"""
        try:
            logger.info(f"📡 连接到服务器: {self.config.server_uri}")
            
            self.websocket = await websockets.connect(
                self.config.server_uri,
                max_size=1024 * 1024,  # 1MB
                ping_interval=30,
                ping_timeout=10,
            )
            
            self.is_connected = True
            self.reconnect_attempts = 0
            
            logger.info(f"✅ 连接成功: {self.config.node_id}")
            
            # 发送注册消息
            await self.register()
            
            # 启动后台任务
            await asyncio.gather(
                self.message_listener(),
                self.heartbeat_sender(),
                self.reconnect_monitor(),
            )
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            self.is_connected = False
            await self.handle_reconnect()
    
    async def register(self):
        """向服务器注册节点"""
        register_msg = {
            "msg_id": str(uuid.uuid4()),
            "from": self.config.node_id,
            "to": "server",
            "type": "register",
            "payload": {
                "capabilities": self.config.capabilities,
                "node_type": "agent",
                "registered_at": datetime.now().isoformat(),
            },
            "timestamp": time.time(),
            "priority": 0,
            "ttl": 3600,
            "retry_count": 0,
            "max_retries": 3,
            "confirmed": False,
            "signature": "",
        }
        
        # 签名
        content = f"{register_msg['msg_id']}:{register_msg['from']}:{register_msg['to']}:{register_msg['type']}:{json.dumps(register_msg['payload'], sort_keys=True)}:"
        register_msg["signature"] = hmac.new(
            self.config.secret_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        await self.websocket.send(json.dumps(register_msg, ensure_ascii=False))
        logger.info(f"📝 节点注册已发送: {self.config.node_id}")
    
    async def send_message(self, to_node: str, msg_type: str, payload: dict, priority: int = 0) -> str:
        """
        发送消息
        
        Args:
            to_node: 目标节点ID
            msg_type: 消息类型
            payload: 消息内容
            priority: 优先级 (0=normal, 1=high, 2=critical)
        
        Returns:
            str: 消息ID
        """
        if not self.is_connected:
            raise ConnectionError("未连接到服务器")
        
        msg_id = str(uuid.uuid4())
        timestamp = time.time()
        
        message = {
            "msg_id": msg_id,
            "from": self.config.node_id,
            "to": to_node,
            "type": msg_type,
            "payload": payload,
            "timestamp": timestamp,
            "priority": priority,
            "ttl": 3600,
            "retry_count": 0,
            "max_retries": 3,
            "confirmed": False,
            "signature": "",
        }
        
        # 签名
        content = f"{msg_id}:{self.config.node_id}:{to_node}:{msg_type}:{json.dumps(payload, sort_keys=True)}:"
        message["signature"] = hmac.new(
            self.config.secret_key.encode(),
            content.encode(),
            hashlib.sha256
        ).hexdigest()
        
        await self.websocket.send(json.dumps(message, ensure_ascii=False))
        
        # 记录待确认消息
        self.pending_messages[msg_id] = {
            "message": message,
            "sent_at": time.time(),
            "retry_count": 0,
        }
        
        logger.info(f"📤 消息已发送: {msg_id} → {to_node}")
        return msg_id
    
    async def message_listener(self):
        """消息监听器 - 接收服务器消息"""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                msg_type = data.get("type")
                
                if msg_type == "confirm":
                    # 注册确认
                    logger.info(f"✅ 注册确认: {data.get('payload', {}).get('status')}")
                    
                elif msg_type == "heartbeat":
                    # 心跳响应
                    pass
                    
                elif msg_type == "confirm":
                    # 消息确认
                    original_msg_id = data.get("payload", {}).get("original_msg_id")
                    if original_msg_id in self.pending_messages:
                        del self.pending_messages[original_msg_id]
                        logger.info(f"✅ 消息确认: {original_msg_id}")
                        
                else:
                    # 普通消息 - 调用处理器
                    if msg_type in self.message_handlers:
                        handler = self.message_handlers[msg_type]
                        await handler(data)
                    else:
                        logger.warning(f"⚠️ 未找到消息处理器: {msg_type}")
                        
        except websockets.exceptions.ConnectionClosed:
            logger.warning("⚠️ 连接已关闭")
            self.is_connected = False
            await self.handle_reconnect()
    
    async def heartbeat_sender(self):
        """心跳发送器 - 定期发送心跳"""
        while self.is_connected:
            try:
                heartbeat_msg = {
                    "msg_id": str(uuid.uuid4()),
                    "from": self.config.node_id,
                    "to": "server",
                    "type": "heartbeat",
                    "payload": {"timestamp": time.time()},
                    "timestamp": time.time(),
                    "priority": 0,
                    "ttl": 30,
                    "retry_count": 0,
                    "max_retries": 1,
                    "confirmed": False,
                    "signature": "",
                }
                
                # 签名
                content = f"{heartbeat_msg['msg_id']}:{self.config.node_id}:server:heartbeat:{json.dumps(heartbeat_msg['payload'], sort_keys=True)}:"
                heartbeat_msg["signature"] = hmac.new(
                    self.config.secret_key.encode(),
                    content.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                await self.websocket.send(json.dumps(heartbeat_msg, ensure_ascii=False))
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ 心跳发送失败: {e}")
                self.is_connected = False
                await self.handle_reconnect()
                break
    
    async def reconnect_monitor(self):
        """重连监控器 - 检测连接状态并自动重连"""
        while True:
            if not self.is_connected:
                logger.info(f"🔄 检测到连接断开，尝试重连...")
                await self.handle_reconnect()
            await asyncio.sleep(5)
    
    async def handle_reconnect(self):
        """处理重连"""
        if self.reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.error(f"❌ 达到最大重连次数，放弃重连")
            return
        
        self.reconnect_attempts += 1
        delay = self.config.reconnect_interval * self.reconnect_attempts
        
        logger.info(f"🔄 重连尝试 {self.reconnect_attempts}/{self.config.max_reconnect_attempts} (延迟{delay}秒)")
        await asyncio.sleep(delay)
        
        try:
            await self.connect()
        except Exception as e:
            logger.error(f"❌ 重连失败: {e}")
    
    def register_handler(self, msg_type: str, handler: Callable):
        """
        注册消息处理器
        
        Args:
            msg_type: 消息类型
            handler: 处理函数
        """
        self.message_handlers[msg_type] = handler
    
    async def close(self):
        """关闭连接"""
        self.is_connected = False
        if self.websocket:
            await self.websocket.close()
        logger.info(f"🔌 客户端已关闭: {self.config.node_id}")


async def main():
    """主函数 - 演示客户端使用"""
    config = WebSocketClientConfig(
        node_id="xiaochen",
        server_uri="ws://localhost:8765",
        secret_key="lobster-network-v3-secret-key",
        capabilities=["go_training", "network_communication", "problem_solving"],
    )
    
    client = WebSocketClient(config)
    
    # 注册消息处理器
    async def handle_training_task(data):
        logger.info(f"📥 收到训练任务: {data.get('payload')}")
        # 处理训练任务...
    
    client.register_handler("training_task", handle_training_task)
    
    # 连接服务器
    await client.connect()
    
    # 发送测试消息
    await client.send_message(
        to_node="zhuguxia",
        msg_type="dialogue_trigger",
        payload={"topic": "围棋定式", "content": "今天学习小目定式"},
        priority=1,
    )
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
