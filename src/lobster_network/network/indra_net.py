"""
因陀罗网拓扑实现
全互联的网络结构，每个节点映照所有节点
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

# 使用相对导入以支持从任意目录运行
try:
    from ..lobster_network import LobsterNetwork
    from ..node import Node
except ImportError:
    # 如果相对导入失败，尝试绝对导入（用于某些特殊场景）
    from lobster_network.lobster_network import LobsterNetwork
    from lobster_network.node import Node


@dataclass
class IndraNetNode:
    """因陀罗网节点"""
    node_id: str
    name: str
    node_type: str
    perspective: str
    knowledge_base: str
    connections: Set[str] = field(default_factory=set)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_connection(self, node_id: str) -> None:
        """添加连接"""
        self.connections.add(node_id)
        self.last_updated = datetime.now().isoformat()
    
    def remove_connection(self, node_id: str) -> None:
        """移除连接"""
        self.connections.discard(node_id)
        self.last_updated = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type,
            "perspective": self.perspective,
            "knowledge_base": self.knowledge_base,
            "connections": list(self.connections),
            "last_updated": self.last_updated,
        }


class IndraNet:
    """因陀罗网（全互联拓扑）"""
    
    def __init__(self):
        """初始化因陀罗网"""
        self.nodes: Dict[str, IndraNetNode] = {}
        self.network = LobsterNetwork()
    
    def add_node(self, node: IndraNetNode) -> None:
        """
        添加节点（自动全互联）
        
        Args:
            node: 节点对象
        """
        self.nodes[node.node_id] = node
        
        # 转换为LobsterNetwork节点
        lobster_node = Node(
            node_id=node.node_id,
            name=node.name,
            node_type=node.node_type,
            perspective=node.perspective,
            knowledge_base=node.knowledge_base,
        )
        self.network.add_node(lobster_node)
        
        # 自动与所有现有节点建立连接
        for existing_id in self.nodes:
            if existing_id != node.node_id:
                self.nodes[existing_id].add_connection(node.node_id)
                node.add_connection(existing_id)
    
    def remove_node(self, node_id: str) -> None:
        """
        移除节点
        
        Args:
            node_id: 节点ID
        """
        if node_id in self.nodes:
            # 移除与其他节点的连接
            for other_id, other_node in self.nodes.items():
                if other_id != node_id:
                    other_node.remove_connection(node_id)
            
            del self.nodes[node_id]
            self.network.remove_node(node_id)
    
    def get_node(self, node_id: str) -> Optional[IndraNetNode]:
        """
        获取节点
        
        Args:
            node_id: 节点ID
        
        Returns:
            Optional[IndraNetNode]: 节点对象
        """
        return self.nodes.get(node_id)
    
    def get_connections(self, node_id: str) -> Set[str]:
        """
        获取节点的连接列表
        
        Args:
            node_id: 节点ID
        
        Returns:
            Set[str]: 连接节点ID列表
        """
        node = self.nodes.get(node_id)
        return node.connections if node else set()
    
    def get_topology(self) -> Dict:
        """
        获取网络拓扑
        
        Returns:
            Dict: 网络拓扑信息
        """
        return {
            node_id: node.to_dict()
            for node_id, node in self.nodes.items()
        }
    
    def dialogue(self, node_a_id: str, node_b_id: str, trigger: str = "") -> Dict:
        """
        触发两个节点之间的对话
        
        Args:
            node_a_id: 节点A ID
            node_b_id: 节点B ID
            trigger: 触发事件描述
        
        Returns:
            Dict: 对话结果
        """
        # 检查连接是否存在
        if node_b_id not in self.nodes.get(node_a_id, IndraNetNode("", "", "", "", "")).connections:
            raise ValueError(f"节点 {node_a_id} 和 {node_b_id} 之间没有连接")
        
        # 触发对话
        result = self.network.dialogue(node_a_id, node_b_id, trigger)
        
        return result.to_dict()
    
    def get_statistics(self) -> Dict:
        """
        获取网络统计信息
        
        Returns:
            Dict: 统计信息
        """
        total_connections = sum(len(node.connections) for node in self.nodes.values())
        max_possible_connections = len(self.nodes) * (len(self.nodes) - 1)
        
        return {
            "total_nodes": len(self.nodes),
            "total_connections": total_connections,
            "max_possible_connections": max_possible_connections,
            "connectivity_ratio": total_connections / max_possible_connections if max_possible_connections > 0 else 0,
            "emergence_statistics": self.network.get_emergence_statistics(),
        }
    
    def export_topology(self) -> str:
        """
        导出网络拓扑为JSON字符串
        
        Returns:
            str: JSON字符串
        """
        import json
        return json.dumps(self.get_topology(), ensure_ascii=False, indent=2)
