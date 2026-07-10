#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 A2A (Agent-to-Agent) 协议实现
基于 Anthropic MCP & Google A2A 规范，实现智能体间标准化能力发现、调用与结果交换。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import json
import uuid
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime

@dataclass
class AgentCapability:
    """智能体能力描述 (Skill Description Language - SDL)"""
    name: str
    version: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    prerequisites: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    author: str = "unknown"
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

@dataclass
class A2AMessage:
    """A2A 标准消息信封"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    sender: str = ""
    receiver: str = ""
    method: str = "invoke"  # invoke, result, error, discover, register
    params: Dict[str, Any] = field(default_factory=dict)
    result: Any = None
    error: Optional[str] = None
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        return {k: v for k, v in d.items() if v is not None}
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class A2AProtocol:
    """A2A 协议核心处理器"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.capabilities: Dict[str, AgentCapability] = {}
        self.registry: Dict[str, List[AgentCapability]] = {}  # 远程智能体注册表
        
    def register_capability(self, cap: AgentCapability):
        """注册本地能力"""
        self.capabilities[cap.name] = cap
        print(f"✅ 能力已注册: {cap.name} v{cap.version}")
        
    def discover(self, target_node: str, capability_name: Optional[str] = None) -> A2AMessage:
        """发现远程智能体能力"""
        msg = A2AMessage(
            sender=self.node_id,
            receiver=target_node,
            method="discover",
            params={"capability": capability_name}
        )
        print(f"🔍 发送能力发现请求至 {target_node}: {capability_name or 'ALL'}")
        return msg
        
    def invoke(self, target_node: str, capability_name: str, params: Dict[str, Any]) -> A2AMessage:
        """调用远程智能体能力"""
        if capability_name not in self.capabilities:
            return A2AMessage(sender=self.node_id, receiver=target_node, method="error", error=f"Capability {capability_name} not found")
            
        msg = A2AMessage(
            sender=self.node_id,
            receiver=target_node,
            method="invoke",
            params={"capability": capability_name, "args": params}
        )
        print(f"🚀 调用远程能力: {target_node}/{capability_name}")
        return msg
        
    def handle_message(self, msg: A2AMessage) -> Optional[A2AMessage]:
        """处理接收到的 A2A 消息"""
        if msg.receiver != self.node_id:
            return None
            
        if msg.method == "discover":
            caps = list(self.capabilities.values())
            if msg.params.get("capability"):
                caps = [c for c in caps if c.name == msg.params["capability"]]
            return A2AMessage(
                sender=self.node_id,
                receiver=msg.sender,
                method="result",
                result=[c.to_dict() for c in caps],
                correlation_id=msg.id
            )
            
        elif msg.method == "invoke":
            cap_name = msg.params.get("capability")
            args = msg.params.get("args", {})
            if cap_name in self.capabilities:
                # 模拟执行 (实际应路由到具体业务逻辑)
                print(f"⚙️ 执行能力: {cap_name} 参数: {args}")
                return A2AMessage(
                    sender=self.node_id,
                    receiver=msg.sender,
                    method="result",
                    result={"status": "success", "data": f"Executed {cap_name} with {args}"},
                    correlation_id=msg.id
                )
            else:
                return A2AMessage(
                    sender=self.node_id,
                    receiver=msg.sender,
                    method="error",
                    error=f"Capability {cap_name} not found",
                    correlation_id=msg.id
                )
        return None

# 示例用法
if __name__ == "__main__":
    node_a = A2AProtocol("node_a")
    node_b = A2AProtocol("node_b")
    
    # A 注册能力
    cap = AgentCapability(
        name="drug_screening",
        version="1.0",
        description="虚拟筛选化合物",
        input_schema={"compound_id": "string", "target": "string"},
        output_schema={"score": "float", "status": "string"},
        author="qoder"
    )
    node_a.register_capability(cap)
    
    # B 发现 A 的能力
    discover_msg = node_b.discover("node_a", "drug_screening")
    print(f"\n📨 B->A: {discover_msg.to_json()}")
    
    # A 处理发现请求
    reply_a = node_a.handle_message(discover_msg)
    print(f"\n📨 A->B: {reply_a.to_json()}")
    
    # B 调用 A 的能力
    invoke_msg = node_b.invoke("node_a", "drug_screening", {"compound_id": "C001", "target": "IL-4Ra"})
    print(f"\n📨 B->A: {invoke_msg.to_json()}")
    
    # A 处理调用请求
    result_a = node_a.handle_message(invoke_msg)
    print(f"\n📨 A->B: {result_a.to_json()}")
