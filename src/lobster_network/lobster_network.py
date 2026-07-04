"""
小龙虾网络主类 V2 — 集成注册中心

新增：
- 节点注册/注销生命周期管理
- 心跳监控
- 健康检查
- 注册中心集成
"""

import json
from typing import Dict, List, Optional
from datetime import datetime

from .node import Node
from .dialogue import DialogueEngine, DialogueResult
from .emergence import EmergenceDetector
from .world_state import WorldStateManager
from .node_registry import NodeRegistry, NodeRegistration


class LobsterNetwork:
    """小龙虾网络（因陀罗网拓扑）V2"""

    def __init__(
        self,
        emergence_threshold: float = 0.5,
        heartbeat_timeout: int = 90,
    ):
        self.nodes: Dict[str, Node] = {}
        self.dialogue_engine = DialogueEngine(emergence_threshold=emergence_threshold)
        self.emergence_detector = EmergenceDetector(threshold=emergence_threshold)
        self.world_state_manager = WorldStateManager()

        # 注册中心
        self.registry = NodeRegistry(heartbeat_timeout=heartbeat_timeout)

    # ========== 节点注册（V2 推荐路径） ==========

    def register_node(
        self,
        node: Node,
        host: str = "",
        port: int = 0,
        ssh_enabled: bool = False,
        metadata: Dict = None,
    ) -> tuple:
        """
        注册节点（V2 推荐路径）

        同时注册到网络内部和注册中心。

        Returns:
            (success: bool, message: str)
        """
        # 注册到注册中心
        reg_ok, reg_msg = self.registry.register(
            node, host=host, port=port, ssh_enabled=ssh_enabled, metadata=metadata
        )
        if not reg_ok:
            return False, reg_msg

        # 注册到网络内部
        self.nodes[node.node_id] = node
        self.world_state_manager.get_state(node.node_id)

        return True, reg_msg

    def deregister_node(self, node_id: str, reason: str = "") -> tuple:
        """注销节点"""
        # 从注册中心注销
        reg_ok, reg_msg = self.registry.deregister(node_id, reason)
        if not reg_ok:
            return False, reg_msg

        # 从网络内部移除
        if node_id in self.nodes:
            del self.nodes[node_id]

        return True, reg_msg

    def node_heartbeat(self, node_id: str, status: Dict = None) -> tuple:
        """节点心跳"""
        return self.registry.heartbeat(node_id, status)

    def suspend_node(self, node_id: str, reason: str = "") -> tuple:
        """暂停节点"""
        ok, msg = self.registry.suspend(node_id, reason)
        return ok, msg

    def resume_node(self, node_id: str) -> tuple:
        """恢复节点"""
        ok, msg = self.registry.resume(node_id)
        return ok, msg

    # ========== 兼容旧接口 ==========

    def add_node(self, node: Node) -> None:
        """添加节点（兼容旧接口，自动注册）"""
        self.nodes[node.node_id] = node
        self.world_state_manager.get_state(node.node_id)
        # 也注册到注册中心
        self.registry.register(node)

    def remove_node(self, node_id: str) -> None:
        """移除节点（兼容旧接口）"""
        if node_id in self.nodes:
            del self.nodes[node_id]
        self.registry.deregister(node_id, "remove_node")

    def get_node(self, node_id: str) -> Optional[Node]:
        """获取节点"""
        return self.nodes.get(node_id)

    # ========== 对话（不变） ==========

    def dialogue(self, node_a_id: str, node_b_id: str, trigger: str = "") -> DialogueResult:
        """触发两个节点之间的对话"""
        node_a = self.nodes.get(node_a_id)
        node_b = self.nodes.get(node_b_id)

        if not node_a or not node_b:
            raise ValueError(f"节点不存在: {node_a_id} 或 {node_b_id}")

        result = self.dialogue_engine.dialogue(node_a, node_b, trigger)

        event = self.emergence_detector.detect(result)

        if event:
            self.world_state_manager.update_state(node_a_id, treasure_id=event.treasure_unlocked)
            self.world_state_manager.update_state(node_b_id, treasure_id=event.treasure_unlocked)

        return result

    # ========== 健康检查 ==========

    def health_check(self) -> Dict:
        """综合健康检查"""
        registry_health = self.registry.check_health()
        network_nodes = set(self.nodes.keys())
        registry_nodes = set(self.registry.registrations.keys())

        # 不一致检测
        in_network_not_registry = network_nodes - registry_nodes
        in_registry_not_network = registry_nodes - network_nodes

        return {
            "registry": registry_health,
            "network_node_count": len(self.nodes),
            "inconsistencies": {
                "in_network_not_registry": list(in_network_not_registry),
                "in_registry_not_network": list(in_registry_not_network),
            },
            "timestamp": datetime.now().isoformat(),
        }

    def cleanup_dead_nodes(self) -> List[str]:
        """清理心跳超时的节点"""
        dead = self.registry.cleanup_dead_nodes()
        for node_id in dead:
            self.nodes.pop(node_id, None)
        return dead

    # ========== 统计 ==========

    def get_emergence_statistics(self) -> Dict:
        """获取涌现统计信息"""
        return self.emergence_detector.get_statistics()

    def get_network_topology(self) -> Dict:
        """获取网络拓扑"""
        return {
            node_id: {
                "name": node.name,
                "type": node.type,
                "perspective": node.seed["perspective"],
                "world_version": node.current_world["version"],
            }
            for node_id, node in self.nodes.items()
        }

    def get_registry_snapshot(self) -> Dict:
        """获取注册中心快照"""
        return self.registry.get_registry_snapshot()

    def get_statistics(self) -> Dict:
        """综合统计"""
        return {
            "network": {
                "total_nodes": len(self.nodes),
                "active_dialogues": len(self.dialogue_engine.dialogue_history),
            },
            "registry": self.registry.get_statistics(),
            "emergence": self.get_emergence_statistics(),
        }

    # ========== 导出 ==========

    def export_network_state(self) -> str:
        """导出网络状态为 JSON"""
        return json.dumps({
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "registry": self.registry.get_registry_snapshot(),
            "emergence_statistics": self.get_emergence_statistics(),
            "world_states": json.loads(self.world_state_manager.export_states()),
            "exported_at": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2)
