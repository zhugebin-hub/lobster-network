"""
节点模型
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class Node:
    """认知编译系统节点"""
    
    def __init__(
        self,
        node_id: str,
        name: str,
        node_type: str = "agent",
        perspective: str = "",
        knowledge_base: str = "",
        value_orientation: str = "",
        learning_rate: str = "medium",
        capabilities: Optional[List[str]] = None,
    ):
        """
        初始化节点
        
        Args:
            node_id: 节点唯一标识
            name: 节点名称
            node_type: 节点类型 (human|agent|coach|student)
            perspective: 认知视角
            knowledge_base: 知识结构
            value_orientation: 价值取向
            learning_rate: 学习率 (high|medium|low)
            capabilities: 能力列表
        """
        self.node_id = node_id
        self.name = name
        self.type = node_type
        self.seed = {
            "perspective": perspective,
            "knowledge_base": knowledge_base,
            "value_orientation": value_orientation,
            "learning_rate": learning_rate,
        }
        self.capabilities = capabilities or []
        self.current_world = {"version": 0, "loaded_chunks": [], "unlocked_treasures": []}
        self.spawned_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "type": self.type,
            "seed": self.seed,
            "capabilities": self.capabilities,
            "current_world": self.current_world,
            "spawned_at": self.spawned_at,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Node":
        """从字典创建节点"""
        return cls(
            node_id=data["node_id"],
            name=data["name"],
            node_type=data.get("type", "agent"),
            perspective=data.get("seed", {}).get("perspective", ""),
            knowledge_base=data.get("seed", {}).get("knowledge_base", ""),
            value_orientation=data.get("seed", {}).get("value_orientation", ""),
            learning_rate=data.get("seed", {}).get("learning_rate", "medium"),
            capabilities=data.get("capabilities", []),
        )
    
    def update_world(self, chunk_id: str = None, treasure_id: str = None):
        """更新世界状态"""
        self.current_world["version"] += 1
        if chunk_id and chunk_id not in [c["chunk_id"] for c in self.current_world["loaded_chunks"]]:
            self.current_world["loaded_chunks"].append({
                "chunk_id": chunk_id,
                "loaded_at": datetime.now().isoformat(),
            })
        if treasure_id and treasure_id not in [t["treasure_id"] for t in self.current_world["unlocked_treasures"]]:
            self.current_world["unlocked_treasures"].append({
                "treasure_id": treasure_id,
                "unlocked_at": datetime.now().isoformat(),
            })
    
    def __repr__(self) -> str:
        return f"Node(id={self.node_id}, name={self.name}, type={self.type})"
