"""
节点注册中心 - 增强版 v2.0
实现节点注册、发现、心跳检测、健康检查、状态管理
"""

import json
import os
import time
import uuid
import threading
from typing import Dict, List, Optional, Set, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class NodeRegistration:
    """节点注册信息"""
    node_id: str
    name: str
    node_type: str  # agent|coach|student|service
    host: str
    port: int
    capabilities: List[str]
    registered_at: str
    last_heartbeat: str
    status: str = "active"  # active|inactive|dead
    metadata: Dict = field(default_factory=dict)
    version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "node_type": self.node_type,
            "host": self.host,
            "port": self.port,
            "capabilities": self.capabilities,
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat,
            "status": self.status,
            "metadata": self.metadata,
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NodeRegistration":
        return cls(
            node_id=data["node_id"],
            name=data["name"],
            node_type=data.get("node_type", "agent"),
            host=data.get("host", ""),
            port=data.get("port", 0),
            capabilities=data.get("capabilities", []),
            registered_at=data.get("registered_at", datetime.now().isoformat()),
            last_heartbeat=data.get("last_heartbeat", datetime.now().isoformat()),
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
            version=data.get("version", "1.0.0"),
        )


class NodeRegistry:
    """节点注册中心 - 增强版"""
    
    def __init__(
        self,
        heartbeat_timeout: int = 60,
        cleanup_interval: int = 30,
        storage_dir: Optional[str] = None,
    ):
        """
        初始化节点注册中心
        
        Args:
            heartbeat_timeout: 心跳超时时间（秒），超过此时间未收到心跳视为离线
            cleanup_interval: 清理间隔（秒）
            storage_dir: 持久化目录
        """
        self.nodes: Dict[str, NodeRegistration] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self.cleanup_interval = cleanup_interval
        self.storage_dir = Path(storage_dir) if storage_dir else None
        self._lock = threading.RLock()
        self._callbacks: Dict[str, List[Callable]] = {
            "register": [],
            "deregister": [],
            "heartbeat": [],
            "status_change": [],
        }
        self._running = False
        self._cleanup_thread: Optional[threading.Thread] = None
        
        # 加载持久化数据
        if self.storage_dir and self.storage_dir.exists():
            self._load_registry()
    
    def register(
        self,
        node_id: str,
        name: str,
        node_type: str = "agent",
        host: str = "",
        port: int = 0,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        注册节点
        
        Args:
            node_id: 节点ID
            name: 节点名称
            node_type: 节点类型
            host: 主机地址
            port: 端口
            capabilities: 能力列表
            metadata: 元数据
        
        Returns:
            bool: 是否注册成功
        """
        with self._lock:
            now = datetime.now().isoformat()
            
            # 检查是否已注册
            if node_id in self.nodes:
                existing = self.nodes[node_id]
                # 更新现有注册
                existing.name = name
                existing.node_type = node_type
                existing.host = host
                existing.port = port
                existing.capabilities = capabilities or existing.capabilities
                existing.metadata = metadata or existing.metadata
                existing.last_heartbeat = now
                existing.status = "active"
            else:
                # 新注册
                registration = NodeRegistration(
                    node_id=node_id,
                    name=name,
                    node_type=node_type,
                    host=host,
                    port=port,
                    capabilities=capabilities or [],
                    registered_at=now,
                    last_heartbeat=now,
                    metadata=metadata or {},
                )
                self.nodes[node_id] = registration
            
            # 触发回调
            self._trigger_callback("register", self.nodes[node_id])
            
            # 持久化
            self._persist_registry()
            
            return True
    
    def deregister(self, node_id: str) -> bool:
        """
        注销节点
        
        Args:
            node_id: 节点ID
        
        Returns:
            bool: 是否注销成功
        """
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                del self.nodes[node_id]
                self._trigger_callback("deregister", node)
                self._persist_registry()
                return True
            return False
    
    def heartbeat(self, node_id: str, metadata: Optional[Dict] = None) -> bool:
        """
        节点心跳
        
        Args:
            node_id: 节点ID
            metadata: 额外元数据
        
        Returns:
            bool: 心跳是否成功
        """
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.last_heartbeat = datetime.now().isoformat()
                node.status = "active"
                if metadata:
                    node.metadata.update(metadata)
                
                self._trigger_callback("heartbeat", node)
                return True
            return False
    
    def get_node(self, node_id: str) -> Optional[NodeRegistration]:
        """获取节点信息"""
        with self._lock:
            return self.nodes.get(node_id)
    
    def get_active_nodes(self) -> List[NodeRegistration]:
        """获取所有活跃节点"""
        with self._lock:
            return [n for n in self.nodes.values() if n.status == "active"]
    
    def get_nodes_by_type(self, node_type: str) -> List[NodeRegistration]:
        """按类型获取节点"""
        with self._lock:
            return [n for n in self.nodes.values() if n.node_type == node_type]
    
    def get_nodes_by_capability(self, capability: str) -> List[NodeRegistration]:
        """按能力获取节点"""
        with self._lock:
            return [n for n in self.nodes.values() if capability in n.capabilities]
    
    def get_inactive_nodes(self) -> List[NodeRegistration]:
        """获取离线节点"""
        with self._lock:
            return [n for n in self.nodes.values() if n.status != "active"]
    
    def get_registry_status(self) -> Dict:
        """获取注册中心状态"""
        with self._lock:
            active = len([n for n in self.nodes.values() if n.status == "active"])
            inactive = len([n for n in self.nodes.values() if n.status == "inactive"])
            dead = len([n for n in self.nodes.values() if n.status == "dead"])
            
            return {
                "total_nodes": len(self.nodes),
                "active_nodes": active,
                "inactive_nodes": inactive,
                "dead_nodes": dead,
                "heartbeat_timeout": self.heartbeat_timeout,
                "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            }
    
    def _parse_iso(self, s: str) -> Optional[datetime]:
        """兼容 Python 3.6 的 ISO 时间解析"""
        if not s:
            return None
        formats = [
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        return None

    def check_health(self) -> Dict:
        """
        检查所有节点健康状态
        
        Returns:
            Dict: 健康检查结果
        """
        with self._lock:
            now = datetime.now()
            unhealthy = []
            
            for node_id, node in self.nodes.items():
                last_hb = self._parse_iso(node.last_heartbeat)
                if last_hb is None:
                    continue
                elapsed = (now - last_hb).total_seconds()
                
                if elapsed > self.heartbeat_timeout * 2:
                    node.status = "dead"
                    unhealthy.append(node_id)
                    self._trigger_callback("status_change", node)
                elif elapsed > self.heartbeat_timeout:
                    node.status = "inactive"
                    unhealthy.append(node_id)
                    self._trigger_callback("status_change", node)
            
            return {
                "total": len(self.nodes),
                "healthy": len(self.nodes) - len(unhealthy),
                "unhealthy": len(unhealthy),
                "unhealthy_nodes": unhealthy,
            }
    
    def on(self, event: str, callback: Callable) -> None:
        """
        注册事件回调
        
        Args:
            event: 事件类型 (register|deregister|heartbeat|status_change)
            callback: 回调函数
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    def _trigger_callback(self, event: str, node: NodeRegistration) -> None:
        """触发回调"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(node)
            except Exception as e:
                print(f"回调执行失败 ({event}): {e}")
    
    def start_cleanup(self) -> None:
        """启动定期清理线程"""
        self._running = True
        self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleanup_thread.start()
    
    def stop_cleanup(self) -> None:
        """停止定期清理线程"""
        self._running = False
    
    def _cleanup_loop(self) -> None:
        """清理循环"""
        while self._running:
            try:
                self.check_health()
                self._persist_registry()
            except Exception as e:
                print(f"清理循环异常: {e}")
            time.sleep(self.cleanup_interval)
    
    def _persist_registry(self) -> None:
        """持久化注册表"""
        if not self.storage_dir:
            return
        
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            filepath = self.storage_dir / "registry.json"
            data = {nid: n.to_dict() for nid, n in self.nodes.items()}
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"持久化注册表失败: {e}")
    
    def _load_registry(self) -> None:
        """加载注册表"""
        if not self.storage_dir:
            return
        
        try:
            filepath = self.storage_dir / "registry.json"
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for node_id, node_data in data.items():
                    self.nodes[node_id] = NodeRegistration.from_dict(node_data)
        except Exception as e:
            print(f"加载注册表失败: {e}")
