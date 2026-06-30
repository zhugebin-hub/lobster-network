"""
节点能力发现协议 - Node Capability Discovery Protocol

实现节点之间的能力发现、知识共享、协同学习。

核心功能:
1. 广播能力 - 节点向网络广播自己的能力
2. 查询能力 - 根据任务需求查找最合适的节点
3. 知识共享 - 节点之间共享学习经验和评估结果
4. 协同学习 - 多个节点联合完成学习任务
"""

# from __future__ import annotations  # Python 3.6 不支持

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


@dataclass
class NodeCapability:
    """节点能力描述"""
    node_id: str
    name: str
    capabilities: List[str]
    knowledge_domains: List[str]
    eight_dim_scores: Dict[str, float]
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "knowledge_domains": self.knowledge_domains,
            "eight_dim_scores": self.eight_dim_scores,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NodeCapability":
        return cls(
            node_id=data["node_id"],
            name=data["name"],
            capabilities=data.get("capabilities", []),
            knowledge_domains=data.get("knowledge_domains", []),
            eight_dim_scores=data.get("eight_dim_scores", {}),
            last_updated=data.get("last_updated", datetime.now().isoformat()),
        )
    
    def matches_task(self, required_capabilities: List[str], knowledge_domain: str = "") -> float:
        """计算与任务的匹配度 (0~1)"""
        cap_match = 0.0
        if required_capabilities:
            matched = sum(1 for cap in required_capabilities if cap in self.capabilities)
            cap_match = matched / max(len(required_capabilities), 1)
        
        domain_match = 0.0
        if knowledge_domain:
            domain_match = 1.0 if knowledge_domain in self.knowledge_domains else 0.0
        
        dim_avg = sum(self.eight_dim_scores.values()) / max(len(self.eight_dim_scores), 1)
        
        final_score = cap_match * 0.4 + domain_match * 0.3 + dim_avg * 0.3
        return final_score


class CapabilityDiscovery:
    """节点能力发现协议实现"""
    
    def __init__(self, registry, messenger, node_id: str = "", data_dir: str = ""):
        self.registry = registry
        self.messenger = messenger
        self.node_id = node_id
        # 默认使用本地目录，而非 /shared
        default_dir = Path.home() / ".lobster-network" / "capabilities"
        self.data_dir = Path(data_dir) if data_dir else default_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, NodeCapability] = {}
    
    def announce_capabilities(self, capability: NodeCapability) -> None:
        """广播能力到网络"""
        self._cache[capability.node_id] = capability
        self._save_capability(capability)
        
        self.messenger.send(
            from_node=self.node_id,
            to_node="broadcast",
            msg_type="capability_announce",
            payload=capability.to_dict(),
        )
        print(f"✅ 能力已广播: {capability.node_id} - {capability.name}")
    
    def find_best_node_for_task(
        self,
        required_capabilities: List[str],
        knowledge_domain: str = "",
        top_n: int = 1,
    ) -> List[Tuple[str, float]]:
        """查找最适合任务的节点"""
        all_nodes = self.registry.list_nodes(status="active")
        
        candidates = []
        for node_info in all_nodes:
            node_id = node_info.node_id if hasattr(node_info, 'node_id') else node_info.get("node_id")
            if node_id == self.node_id:
                continue
            
            capability = self._load_capability(node_id)
            if capability is None:
                capability = self._create_temp_capability(node_info)
            
            candidates.append(capability)
        
        scored = []
        for cap in candidates:
            score = cap.matches_task(required_capabilities, knowledge_domain)
            scored.append((cap.node_id, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]
    
    def request_knowledge_sharing(
        self,
        target_node_id: str,
        topic: str,
        requester_id: str = "",
    ) -> Optional[dict]:
        """请求知识共享"""
        requester_id = requester_id or self.node_id
        
        msg_id = self.messenger.send(
            from_node=requester_id,
            to_node=target_node_id,
            msg_type="knowledge_share_request",
            payload={
                "topic": topic,
                "requester": requester_id,
                "timestamp": datetime.now().isoformat(),
            },
        )
        
        print(f"✅ 知识共享请求已发送: {requester_id} -> {target_node_id} (topic={topic})")
        return {"msg_id": msg_id, "status": "sent"}
    
    def _save_capability(self, capability: NodeCapability) -> None:
        """持久化能力描述"""
        file_path = self.data_dir / f"{capability.node_id}_capability.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(capability.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _load_capability(self, node_id: str) -> Optional[NodeCapability]:
        """加载能力描述"""
        file_path = self.data_dir / f"{node_id}_capability.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return NodeCapability.from_dict(data)
        except Exception as e:
            print(f"⚠️ 加载能力描述失败: {e}")
            return None
    
    def _create_temp_capability(self, node_info) -> NodeCapability:
        """从注册信息创建临时能力描述"""
        if hasattr(node_info, 'node_id'):
            return NodeCapability(
                node_id=node_info.node_id,
                name=node_info.name,
                capabilities=node_info.capabilities,
                knowledge_domains=[],
                eight_dim_scores={},
            )
        else:
            return NodeCapability(
                node_id=node_info.get("node_id", ""),
                name=node_info.get("name", ""),
                capabilities=node_info.get("capabilities", []),
                knowledge_domains=[],
                eight_dim_scores={},
            )


def test_discovery():
    """测试能力发现协议"""
    print("═══ 测试节点能力发现协议 ═══")
    
    class MockRegistry:
        def list_nodes(self, status="active"):
            return [
                {"node_id": "hermes", "name": "Hermes", "capabilities": ["coaching", "strategy"]},
                {"node_id": "openclaw", "name": "OpenClaw", "capabilities": ["dialogue", "research"]},
            ]
    
    class MockMessenger:
        def send(self, **kwargs):
            print(f"  [Mock] 发送消息: {kwargs.get('msg_type')} -> {kwargs.get('to_node')}")
            return f"msg_{int(time.time())}"
    
    registry = MockRegistry()
    messenger = MockMessenger()
    discovery = CapabilityDiscovery(registry, messenger, node_id="zhugebin-001")
    
    # 测试1: 广播能力
    print("\n1. 测试广播能力:")
    cap = NodeCapability(
        node_id="zhugebin-001",
        name="诸葛斌的工作助手",
        capabilities=["dialogue", "research", "code_generation", "teaching", "writing"],
        knowledge_domains=["python", "go", "ppt", "ai"],
        eight_dim_scores={
            "understanding": 0.85,
            "execution": 0.90,
            "reasoning": 0.80,
            "reflection": 0.75,
            "tooling": 0.88,
            "eq": 0.82,
            "memory": 0.78,
            "retrieval": 0.86,
        },
    )
    discovery.announce_capabilities(cap)
    
    # 测试2: 查找最适合的节点
    print("\n2. 测试查找最适合节点:")
    best_nodes = discovery.find_best_node_for_task(
        required_capabilities=["code_generation"],
        knowledge_domain="python",
        top_n=3,
    )
    print(f"   最适合的节点: {best_nodes}")
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    test_discovery()
