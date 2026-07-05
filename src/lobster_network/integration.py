"""
龙虾网络集成层
将注册中心、可靠消息、龙虾网络核心整合在一起
"""

import os
from typing import Dict, List, Optional
from datetime import datetime

from src.lobster_network.registry import NodeRegistry, TransportConfig, TransportType, NodeStatus
from src.lobster_network.messenger import Messenger, ReliableMessage
from src.lobster_network.lobster_network import LobsterNetwork
from src.lobster_network.node import Node
from src.lobster_network.utils.logger import get_logger

logger = get_logger(__name__)


class LobsterNetworkWithRegistry:
    """
    带注册中心和可靠消息的龙虾网络
    
    整合：
    1. NodeRegistry — 节点注册、发现、心跳、健康检查
    2. Messenger — 可靠消息传递、自动重试、故障切换
    3. LobsterNetwork — 对话引擎、涌现检测、世界状态
    """
    
    def __init__(
        self,
        storage_dir: str = "~/.lobster-network",
        emergence_threshold: float = 0.5,
    ):
        self.storage_dir = os.path.expanduser(storage_dir)
        
        # 注册中心
        registry_path = f"{self.storage_dir}/registry.json"
        self.registry = NodeRegistry(storage_path=registry_path)
        
        # 可靠消息
        self.messenger = Messenger(
            registry=self.registry,
            storage_dir=f"{self.storage_dir}/messages",
        )
        
        # 龙虾网络核心
        self.network = LobsterNetwork(emergence_threshold=emergence_threshold)
        
        # 绑定消息回调
        self.messenger.on_delivery(self._on_message_delivered)
        self.messenger.on_failure(self._on_message_failed)
        
        logger.info(f"LobsterNetworkWithRegistry initialized (storage={self.storage_dir})")
    
    # ==================== 节点管理 ====================
    
    def register_node(
        self,
        node_id: str,
        name: str,
        node_type: str = "agent",
        perspective: str = "",
        knowledge_base: str = "",
        value_orientation: str = "",
        learning_rate: str = "medium",
        capabilities: Optional[List[str]] = None,
        transports: Optional[List[TransportConfig]] = None,
        metadata: Optional[Dict] = None,
        ttl_seconds: int = 300,
    ) -> Node:
        """
        注册节点（同时注册到注册中心和龙虾网络）
        
        Args:
            node_id: 节点唯一标识
            name: 节点名称
            node_type: 节点类型
            perspective: 认知视角
            knowledge_base: 知识库
            value_orientation: 价值取向
            learning_rate: 学习率
            capabilities: 能力列表
            transports: 传输通道配置
            metadata: 元数据
            ttl_seconds: 心跳超时时间
        
        Returns:
            Node: 龙虾网络节点
        """
        # 1. 注册到注册中心
        self.registry.register(
            node_id=node_id,
            name=name,
            node_type=node_type,
            capabilities=capabilities or [],
            transports=transports or [],
            metadata=metadata or {},
            ttl_seconds=ttl_seconds,
        )
        
        # 2. 添加到龙虾网络
        lobster_node = Node(
            node_id=node_id,
            name=name,
            node_type=node_type,
            perspective=perspective,
            knowledge_base=knowledge_base,
            value_orientation=value_orientation,
            learning_rate=learning_rate,
            capabilities=capabilities or [],
        )
        self.network.add_node(lobster_node)
        
        logger.info(f"Node registered: {node_id} ({name})")
        return lobster_node
    
    def unregister_node(self, node_id: str) -> bool:
        """注销节点"""
        self.registry.unregister(node_id)
        self.network.remove_node(node_id)
        logger.info(f"Node unregistered: {node_id}")
        return True
    
    def heartbeat(self, node_id: str, status: Optional[str] = None) -> bool:
        """节点心跳"""
        return self.registry.heartbeat(node_id, status)
    
    def is_alive(self, node_id: str) -> bool:
        """检查节点是否在线"""
        return self.registry.is_alive(node_id)
    
    def list_nodes(
        self,
        node_type: Optional[str] = None,
        status: Optional[str] = None,
        alive_only: bool = False,
    ) -> List:
        """列出节点"""
        return self.registry.list_nodes(node_type, status, alive_only)
    
    def health_check(self) -> Dict:
        """全量健康检查"""
        return self.registry.check_health()
    
    # ==================== 消息传递 ====================
    
    def send_message(
        self,
        from_node: str,
        to_node: str,
        msg_type: str,
        payload: Dict,
        priority: int = 0,
        max_retries: int = 3,
    ) -> ReliableMessage:
        """
        发送可靠消息
        
        Args:
            from_node: 发送节点
            to_node: 接收节点
            msg_type: 消息类型
            payload: 消息载荷
            priority: 优先级
            max_retries: 最大重试次数
        
        Returns:
            ReliableMessage: 消息对象
        """
        return self.messenger.send(
            from_node=from_node,
            to_node=to_node,
            msg_type=msg_type,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
        )
    
    def ack_message(self, msg_id: str) -> bool:
        """确认消息"""
        return self.messenger.ack(msg_id)
    
    def retry_message(self, msg_id: str) -> bool:
        """重试消息"""
        return self.messenger.retry(msg_id)
    
    def retry_all_failed(self) -> int:
        """重试所有失败消息"""
        return self.messenger.retry_all_failed()
    
    # ==================== 对话 ====================
    
    def dialogue(self, node_a_id: str, node_b_id: str, trigger: str = "") -> Dict:
        """
        触发对话
        
        Args:
            node_a_id: 节点A
            node_b_id: 节点B
            trigger: 触发事件
        
        Returns:
            Dict: 对话结果
        """
        # 检查节点是否在线
        if not self.is_alive(node_a_id):
            logger.warning(f"Node {node_a_id} may be offline")
        if not self.is_alive(node_b_id):
            logger.warning(f"Node {node_b_id} may be offline")
        
        # 执行对话
        result = self.network.dialogue(node_a_id, node_b_id, trigger)
        
        # 发送对话通知消息
        self.send_message(
            from_node=node_a_id,
            to_node=node_b_id,
            msg_type="dialogue_result",
            payload={
                "dialogue_id": result.dialogue_id,
                "trigger": trigger,
                "emergence_score": result.emergence_score,
                "new_insight": result.new_insight,
            },
            priority=1,
        )
        
        return result.to_dict()
    
    # ==================== 内部回调 ====================
    
    def _on_message_delivered(self, message: ReliableMessage) -> None:
        """消息投递成功回调"""
        logger.debug(f"Message delivered: {message.msg_id} → {message.to_node}")
    
    def _on_message_failed(self, message: ReliableMessage) -> None:
        """消息投递失败回调"""
        logger.error(f"Message failed: {message.msg_id} → {message.to_node}")
    
    # ==================== 统计 ====================
    
    def get_full_statistics(self) -> Dict:
        """获取完整统计信息"""
        return {
            "registry": self.registry.get_statistics(),
            "messenger": self.messenger.get_statistics(),
            "network": self.network.get_emergence_statistics(),
            "health": self.health_check(),
        }
    
    def export_state(self) -> str:
        """导出完整状态"""
        import json
        return json.dumps(self.get_full_statistics(), ensure_ascii=False, indent=2)
