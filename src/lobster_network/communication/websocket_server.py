#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket实时通讯服务器 - 小龙虾网络v3.0
实现低延迟(<100ms)双向通讯、消息确认、心跳检测
"""

import asyncio
import json
import time
import uuid
import hashlib
import hmac
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
import websockets
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WebSocketMessage:
    """WebSocket消息 - v3.0增强版"""
    msg_id: str
    from_node: str
    to_node: str
    msg_type: str  # dialogue|training|heartbeat|register|confirm
    payload: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: int = 0  # 0=normal, 1=high, 2=critical
    ttl: int = 3600  # 消息存活时间（秒）
    retry_count: int = 0
    max_retries: int = 3
    confirmed: bool = False
    signature: str = ""  # 消息签名
    
    def to_dict(self) -> dict:
        return {
            "msg_id": self.msg_id,
            "from": self.from_node,
            "to": self.to_node,
            "type": self.msg_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "ttl": self.ttl,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "confirmed": self.confirmed,
            "signature": self.signature,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: dict) -> "WebSocketMessage":
        return cls(
            msg_id=data["msg_id"],
            from_node=data["from"],
            to_node=data["to"],
            msg_type=data["type"],
            payload=data.get("payload", {}),
            timestamp=data.get("timestamp", time.time()),
            priority=data.get("priority", 0),
            ttl=data.get("ttl", 3600),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            confirmed=data.get("confirmed", False),
            signature=data.get("signature", ""),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "WebSocketMessage":
        return cls.from_dict(json.loads(json_str))
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        return (time.time() - self.timestamp) > self.ttl
    
    def sign_message(self, secret_key: str) -> str:
        """对消息进行签名"""
        content = f"{self.msg_id}:{self.from_node}:{self.to_node}:{self.msg_type}:{json.dumps(self.payload, sort_keys=True)}"
        self.signature = hmac.new(secret_key.encode(), content.encode(), hashlib.sha256).hexdigest()
        return self.signature
    
    def verify_signature(self, secret_key: str) -> bool:
        """验证消息签名"""
        expected = self.sign_message(secret_key)
        return hmac.compare_digest(expected, self.signature)


class WebSocketServer:
    """WebSocket实时通讯服务器 - v3.0"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8765, secret_key: str = "lobster-secret"):
        """
        初始化WebSocket服务器
        
        Args:
            host: 服务器地址
            port: 服务器端口
            secret_key: 消息签名密钥
        """
        self.host = host
        self.port = port
        self.secret_key = secret_key
        
        # 节点连接管理
        self.connected_nodes: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.node_capabilities: Dict[str, List[str]] = {}
        self.node_last_heartbeat: Dict[str, float] = {}
        
        # 消息管理
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.pending_messages: Dict[str, WebSocketMessage] = {}  # 待确认消息
        self.processed_messages: Set[str] = set()  # 已处理消息ID
        
        # 性能监控
        self.stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_confirmed": 0,
            "avg_latency_ms": 0.0,
            "total_latency_ms": 0.0,
        }
        
        # 配置
        self.heartbeat_interval = 30  # 心跳间隔（秒）
        self.heartbeat_timeout = 90  # 心跳超时（秒）
        self.max_message_size = 1024 * 1024  # 最大消息大小（1MB）
        
    async def start(self):
        """启动WebSocket服务器"""
        logger.info(f"🦞 小龙虾网络 v3.0 WebSocket服务器启动: {self.host}:{self.port}")
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            max_size=self.max_message_size,
            ping_interval=self.heartbeat_interval,
            ping_timeout=self.heartbeat_timeout,
        ):
            logger.info(f"✅ 服务器已启动，等待节点连接...")
            
            # 启动后台任务
            await asyncio.gather(
                self.message_processor(),
                self.heartbeat_monitor(),
                self.stats_reporter(),
            )
    
    async def handle_client(self, websocket, path):
        """处理客户端连接"""
        node_id = None
        
        try:
            # 等待节点注册
            async for message in websocket:
                msg = WebSocketMessage.from_json(message)
                
                if msg.msg_type == "register":
                    # 节点注册
                    node_id = msg.from_node
                    self.connected_nodes[node_id] = websocket
                    self.node_capabilities[node_id] = msg.payload.get("capabilities", [])
                    self.node_last_heartbeat[node_id] = time.time()
                    
                    logger.info(f"📡 节点注册: {node_id} (能力: {self.node_capabilities[node_id]})")
                    
                    # 发送注册确认
                    confirm_msg = WebSocketMessage(
                        msg_id=str(uuid.uuid4()),
                        from_node="server",
                        to_node=node_id,
                        msg_type="confirm",
                        payload={"status": "registered", "server_time": time.time()},
                    )
                    confirm_msg.sign_message(self.secret_key)
                    await websocket.send(confirm_msg.to_json())
                    
                elif msg.msg_type == "heartbeat":
                    # 心跳更新
                    self.node_last_heartbeat[node_id] = time.time()
                    
                    # 发送心跳响应
                    heartbeat_resp = WebSocketMessage(
                        msg_id=str(uuid.uuid4()),
                        from_node="server",
                        to_node=node_id,
                        msg_type="heartbeat",
                        payload={"server_time": time.time(), "status": "alive"},
                    )
                    heartbeat_resp.sign_message(self.secret_key)
                    await websocket.send(heartbeat_resp.to_json())
                    
                elif msg.msg_type == "confirm":
                    # 消息确认
                    original_msg_id = msg.payload.get("original_msg_id")
                    if original_msg_id in self.pending_messages:
                        del self.pending_messages[original_msg_id]
                        self.stats["messages_confirmed"] += 1
                        logger.info(f"✅ 消息确认: {original_msg_id}")
                    
                else:
                    # 普通消息处理
                    await self.message_queue.put(msg)
                    self.stats["messages_received"] += 1
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"⚠️ 节点断开连接: {node_id}")
        except Exception as e:
            logger.error(f"❌ 处理客户端异常: {e}")
        finally:
            # 清理节点
            if node_id and node_id in self.connected_nodes:
                del self.connected_nodes[node_id]
                if node_id in self.node_capabilities:
                    del self.node_capabilities[node_id]
                if node_id in self.node_last_heartbeat:
                    del self.node_last_heartbeat[node_id]
                logger.info(f"🧹 节点清理完成: {node_id}")
    
    async def message_processor(self):
        """消息处理器 - 后台任务"""
        while True:
            try:
                msg = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # 验证消息签名
                if not msg.verify_signature(self.secret_key):
                    logger.warning(f"⚠️ 消息签名验证失败: {msg.msg_id}")
                    continue
                
                # 检查消息是否过期
                if msg.is_expired():
                    logger.warning(f"⚠️ 消息已过期: {msg.msg_id}")
                    continue
                
                # 检查消息是否已处理（去重）
                if msg.msg_id in self.processed_messages:
                    logger.info(f"ℹ️ 消息已处理，跳过: {msg.msg_id}")
                    continue
                
                # 路由消息到目标节点
                target_node = msg.to_node
                if target_node in self.connected_nodes:
                    try:
                        await self.connected_nodes[target_node].send(msg.to_json())
                        self.stats["messages_sent"] += 1
                        
                        # 记录待确认消息
                        self.pending_messages[msg.msg_id] = msg
                        self.processed_messages.add(msg.msg_id)
                        
                        logger.info(f"📤 消息已发送: {msg.msg_id} → {target_node}")
                        
                    except Exception as e:
                        logger.error(f"❌ 发送消息失败: {e}")
                        # 重试逻辑
                        if msg.retry_count < msg.max_retries:
                            msg.retry_count += 1
                            await self.message_queue.put(msg)
                            logger.info(f"🔄 消息重试: {msg.msg_id} (第{msg.retry_count}次)")
                else:
                    logger.warning(f"⚠️ 目标节点不存在: {target_node}")
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ 消息处理异常: {e}")
    
    async def heartbeat_monitor(self):
        """心跳监控器 - 检测节点健康状态"""
        while True:
            await asyncio.sleep(10)  # 每10秒检查一次
            
            now = time.time()
            dead_nodes = []
            
            for node_id, last_heartbeat in self.node_last_heartbeat.items():
                if now - last_heartbeat > self.heartbeat_timeout:
                    dead_nodes.append(node_id)
                    logger.warning(f"⚠️ 节点心跳超时: {node_id}")
            
            # 清理死亡节点
            for node_id in dead_nodes:
                if node_id in self.connected_nodes:
                    try:
                        await self.connected_nodes[node_id].close()
                    except:
                        pass
                    del self.connected_nodes[node_id]
                
                if node_id in self.node_capabilities:
                    del self.node_capabilities[node_id]
                if node_id in self.node_last_heartbeat:
                    del self.node_last_heartbeat[node_id]
                
                logger.info(f"🧹 死亡节点已清理: {node_id}")
    
    async def stats_reporter(self):
        """统计报告器 - 定期输出性能指标"""
        while True:
            await asyncio.sleep(60)  # 每分钟报告一次
            
            logger.info(f"📊 性能统计:")
            logger.info(f"  在线节点: {len(self.connected_nodes)}")
            logger.info(f"  消息发送: {self.stats['messages_sent']}")
            logger.info(f"  消息接收: {self.stats['messages_received']}")
            logger.info(f"  消息确认: {self.stats['messages_confirmed']}")
            logger.info(f"  待确认: {len(self.pending_messages)}")
            logger.info(f"  平均延迟: {self.stats['avg_latency_ms']:.2f}ms")
            
            # 重置统计
            self.stats = {
                "messages_sent": 0,
                "messages_received": 0,
                "messages_confirmed": 0,
                "avg_latency_ms": 0.0,
                "total_latency_ms": 0.0,
            }


async def main():
    """主函数"""
    server = WebSocketServer(
        host="0.0.0.0",
        port=8765,
        secret_key="lobster-network-v3-secret-key"
    )
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
