#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · A2A协议实现
版本: V1.0 | 日期: 2026-06-27
功能: Agent-to-Agent通信协议，支持节点发现、消息路由、能力协商
"""

import json
import os
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

class A2ANode:
    """A2A节点"""
    
    def __init__(self, node_id: str, name: str, node_type: str = "agent"):
        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.capabilities = []
        self.endpoints = {}
        self.status = "active"
        self.registered_at = datetime.now().isoformat()
        self.last_heartbeat = datetime.now().isoformat()
    
    def add_capability(self, capability: str):
        """添加能力"""
        if capability not in self.capabilities:
            self.capabilities.append(capability)
    
    def add_endpoint(self, protocol: str, url: str):
        """添加端点"""
        self.endpoints[protocol] = url
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "type": self.node_type,
            "capabilities": self.capabilities,
            "endpoints": self.endpoints,
            "status": self.status,
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat
        }

class A2AMessage:
    """A2A消息"""
    
    def __init__(self, from_node: str, to_node: str, message_type: str, payload: Dict):
        self.message_id = str(uuid.uuid4())
        self.from_node = from_node
        self.to_node = to_node
        self.message_type = message_type
        self.payload = payload
        self.timestamp = datetime.now().isoformat()
        self.status = "pending"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "message_id": self.message_id,
            "from": self.from_node,
            "to": self.to_node,
            "type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "status": self.status
        }

class A2AServer:
    """A2A服务器"""
    
    def __init__(self, storage_path: str = "/shared/training/go/a2a"):
        self.storage_path = storage_path
        self.nodes = {}
        self.messages = []
        self._ensure_storage()
        self._load_data()
    
    def _ensure_storage(self):
        """确保存储目录存在"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_data(self):
        """加载数据"""
        nodes_path = os.path.join(self.storage_path, "nodes.json")
        if os.path.exists(nodes_path):
            with open(nodes_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for node_data in data:
                    node = A2ANode(
                        node_data["node_id"],
                        node_data["name"],
                        node_data.get("type", "agent")
                    )
                    node.capabilities = node_data.get("capabilities", [])
                    node.endpoints = node_data.get("endpoints", {})
                    node.status = node_data.get("status", "active")
                    node.registered_at = node_data.get("registered_at", "")
                    node.last_heartbeat = node_data.get("last_heartbeat", "")
                    self.nodes[node.node_id] = node
    
    def _save_data(self):
        """保存数据"""
        nodes_path = os.path.join(self.storage_path, "nodes.json")
        nodes_data = [node.to_dict() for node in self.nodes.values()]
        with open(nodes_path, "w", encoding="utf-8") as f:
            json.dump(nodes_data, f, ensure_ascii=False, indent=2)
    
    def register_node(self, node: A2ANode) -> bool:
        """注册节点"""
        if node.node_id in self.nodes:
            return False
        
        self.nodes[node.node_id] = node
        self._save_data()
        return True
    
    def discover_nodes(self, capability: str = None, node_type: str = None) -> List[Dict]:
        """发现节点"""
        results = []
        for node in self.nodes.values():
            if node.status != "active":
                continue
            
            if capability and capability not in node.capabilities:
                continue
            
            if node_type and node.node_type != node_type:
                continue
            
            results.append(node.to_dict())
        
        return results
    
    def send_message(self, message: A2AMessage) -> bool:
        """发送消息"""
        if message.to_node not in self.nodes:
            return False
        
        if self.nodes[message.to_node].status != "active":
            return False
        
        message.status = "sent"
        self.messages.append(message)
        return True
    
    def get_messages(self, node_id: str) -> List[Dict]:
        """获取消息"""
        results = []
        for message in self.messages:
            if message.to_node == node_id and message.status == "sent":
                results.append(message.to_dict())
        return results
    
    def heartbeat(self, node_id: str) -> bool:
        """心跳检测"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = datetime.now().isoformat()
            self._save_data()
            return True
        return False
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": sum(1 for n in self.nodes.values() if n.status == "active"),
            "total_messages": len(self.messages),
            "nodes": {nid: node.to_dict() for nid, node in self.nodes.items()}
        }

if __name__ == "__main__":
    # 测试A2A协议
    server = A2AServer()
    
    print("🦞 A2A协议测试")
    print(f"   存储路径: {server.storage_path}")
    
    # 创建节点
    print("\n📝 创建节点...")
    hermes = A2ANode("hermes", "诸葛马", "coach")
    hermes.add_capability("training-design")
    hermes.add_capability("task-dispatch")
    hermes.add_endpoint("ssh", "http://47.93.6.57:8001")
    
    xiaochen = A2ANode("xiaochen", "小陈", "agent")
    xiaochen.add_capability("go-training")
    xiaochen.add_capability("stock-trading")
    xiaochen.add_endpoint("ssh", "http://121.43.80.231:8001")
    
    zhuguxia = A2ANode("zhuguxia", "诸葛虾", "agent")
    zhuguxia.add_capability("go-training")
    zhuguxia.add_endpoint("ssh", "http://60.205.139.51:8001")
    
    qoder = A2ANode("qoder", "qoder小龙虾", "agent")
    qoder.add_capability("go-training")
    qoder.add_capability("code-quality")
    qoder.add_endpoint("github", "https://github.com/zhugebin-hub/lobster-network")
    
    # 注册节点
    server.register_node(hermes)
    server.register_node(xiaochen)
    server.register_node(zhuguxia)
    server.register_node(qoder)
    print(f"   已注册4个节点")
    
    # 发现节点
    print("\n🔍 发现节点...")
    training_nodes = server.discover_nodes(capability="go-training")
    print(f"   找到 {len(training_nodes)} 个围棋训练节点")
    
    # 发送消息
    print("\n📤 发送消息...")
    message = A2AMessage("hermes", "xiaochen", "training_task", {
        "task_id": "task-001",
        "topic": "基础死活形状识别",
        "problems": 25
    })
    server.send_message(message)
    print(f"   消息已发送: {message.message_id}")
    
    # 获取消息
    print("\n📥 获取消息...")
    messages = server.get_messages("xiaochen")
    print(f"   找到 {len(messages)} 条消息")
    
    # 心跳检测
    print("\n💓 心跳检测...")
    server.heartbeat("xiaochen")
    server.heartbeat("zhuguxia")
    print(f"   心跳已更新")
    
    # 状态
    print("\n📊 状态:")
    status = server.get_status()
    print(f"   总节点: {status['total_nodes']}")
    print(f"   活跃节点: {status['active_nodes']}")
    print(f"   总消息: {status['total_messages']}")
    
    print("\n✅ A2A协议测试完成")
