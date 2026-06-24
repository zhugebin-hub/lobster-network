"""
节点注册中心 V2

功能：
- 节点注册 / 注销 / 查询
- 心跳监控与存活检测
- 节点元数据管理
- 注册冲突检测
- 自动清理超时节点
"""

import json
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field

from .node import Node

# ========== 工具函数（Python 3.6 兼容） ==========

def _parse_iso(s: str) -> datetime:
    """解析 ISO 格式时间字符串（兼容 Python 3.6）"""
    # Python 3.7+ 有 fromisoformat，3.6 需要手动处理
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        pass
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


# ========== 常量 ==========

DEFAULT_HEARTBEAT_INTERVAL = 30  # 秒
DEFAULT_HEARTBEAT_TIMEOUT = 90   # 秒（3次心跳未收到视为离线）

# 节点状态
STATUS_REGISTERING = "registering"
STATUS_ACTIVE = "active"
STATUS_IDLE = "idle"
STATUS_OFFLINE = "offline"
STATUS_SUSPENDED = "suspended"


@dataclass
class NodeRegistration:
    """节点注册信息"""
    node_id: str
    name: str
    node_type: str
    perspective: str
    knowledge_base: str
    value_orientation: str = ""
    learning_rate: str = "medium"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    # 注册状态
    status: str = STATUS_REGISTERING
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_heartbeat: Optional[str] = None
    heartbeat_count: int = 0

    # 网络信息
    host: str = ""
    port: int = 0
    ssh_enabled: bool = False

    # 协议版本
    protocol_version: str = "2.0"

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "type": self.node_type,
            "perspective": self.perspective,
            "knowledge_base": self.knowledge_base,
            "value_orientation": self.value_orientation,
            "learning_rate": self.learning_rate,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "status": self.status,
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat,
            "heartbeat_count": self.heartbeat_count,
            "host": self.host,
            "port": self.port,
            "ssh_enabled": self.ssh_enabled,
            "protocol_version": self.protocol_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NodeRegistration":
        return cls(
            node_id=data["node_id"],
            name=data["name"],
            node_type=data.get("type", "agent"),
            perspective=data.get("perspective", ""),
            knowledge_base=data.get("knowledge_base", ""),
            value_orientation=data.get("value_orientation", ""),
            learning_rate=data.get("learning_rate", "medium"),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {}),
            status=data.get("status", STATUS_REGISTERING),
            registered_at=data.get("registered_at", datetime.now().isoformat()),
            last_heartbeat=data.get("last_heartbeat"),
            heartbeat_count=data.get("heartbeat_count", 0),
            host=data.get("host", ""),
            port=data.get("port", 0),
            ssh_enabled=data.get("ssh_enabled", False),
            protocol_version=data.get("protocol_version", "2.0"),
        )

    def is_alive(self, timeout: int = DEFAULT_HEARTBEAT_TIMEOUT) -> bool:
        """检查节点是否存活"""
        if self.status in (STATUS_OFFLINE, STATUS_SUSPENDED):
            return False
        if not self.last_heartbeat:
            return False
        try:
            last = _parse_iso(self.last_heartbeat)
            return datetime.now() - last < timedelta(seconds=timeout)
        except (ValueError, TypeError):
            return False


class NodeRegistry:
    """节点注册中心"""

    def __init__(self, heartbeat_timeout: int = DEFAULT_HEARTBEAT_TIMEOUT):
        self.registrations: Dict[str, NodeRegistration] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self._register_log: List[Dict] = []

    # ========== 注册 / 注销 ==========

    def register(
        self,
        node: Node,
        host: str = "",
        port: int = 0,
        ssh_enabled: bool = False,
        metadata: Dict = None,
    ) -> tuple:
        """
        注册节点

        Returns:
            (success: bool, message: str)
        """
        # 检查重复注册
        if node.node_id in self.registrations:
            existing = self.registrations[node.node_id]
            if existing.status == STATUS_ACTIVE:
                return False, f"节点 {node.node_id} 已注册且处于活跃状态"
            # 离线节点重新注册，覆盖
            self._log_event("RE-REGISTER", node.node_id, "覆盖离线节点")

        reg = NodeRegistration(
            node_id=node.node_id,
            name=node.name,
            node_type=node.type,
            perspective=node.seed.get("perspective", ""),
            knowledge_base=node.seed.get("knowledge_base", ""),
            value_orientation=node.seed.get("value_orientation", ""),
            learning_rate=node.seed.get("learning_rate", "medium"),
            capabilities=node.capabilities,
            metadata=metadata or {},
            host=host,
            port=port,
            ssh_enabled=ssh_enabled,
            status=STATUS_ACTIVE,
            last_heartbeat=datetime.now().isoformat(),
            heartbeat_count=1,
        )
        self.registrations[node.node_id] = reg
        self._log_event("REGISTER", node.node_id, f"{node.name} ({node.type})")
        return True, f"节点 {node.node_id} 注册成功"

    def deregister(self, node_id: str, reason: str = "") -> tuple:
        """
        注销节点

        Returns:
            (success: bool, message: str)
        """
        if node_id not in self.registrations:
            return False, f"节点 {node_id} 未注册"

        reg = self.registrations[node_id]
        reg.status = STATUS_OFFLINE
        self._log_event("DEREGISTER", node_id, reason or "主动注销")
        return True, f"节点 {node_id} 已注销"

    def suspend(self, node_id: str, reason: str = "") -> tuple:
        """暂停节点（保留注册信息）"""
        if node_id not in self.registrations:
            return False, f"节点 {node_id} 未注册"
        self.registrations[node_id].status = STATUS_SUSPENDED
        self._log_event("SUSPEND", node_id, reason)
        return True, f"节点 {node_id} 已暂停"

    def resume(self, node_id: str) -> tuple:
        """恢复暂停的节点"""
        if node_id not in self.registrations:
            return False, f"节点 {node_id} 未注册"
        self.registrations[node_id].status = STATUS_ACTIVE
        self.registrations[node_id].last_heartbeat = datetime.now().isoformat()
        self.registrations[node_id].heartbeat_count += 1
        self._log_event("RESUME", node_id)
        return True, f"节点 {node_id} 已恢复"

    # ========== 心跳 ==========

    def heartbeat(self, node_id: str, status: Dict = None) -> tuple:
        """
        处理节点心跳

        Returns:
            (success: bool, message: str)
        """
        if node_id not in self.registrations:
            return False, f"节点 {node_id} 未注册"

        reg = self.registrations[node_id]
        if reg.status == STATUS_OFFLINE:
            return False, f"节点 {node_id} 已注销"

        reg.last_heartbeat = datetime.now().isoformat()
        reg.heartbeat_count += 1
        if reg.status != STATUS_SUSPENDED:
            reg.status = STATUS_ACTIVE
        if status:
            reg.metadata.update(status)

        return True, "心跳正常"

    # ========== 查询 ==========

    def get_registration(self, node_id: str) -> Optional[NodeRegistration]:
        """获取节点注册信息"""
        return self.registrations.get(node_id)

    def get_active_nodes(self) -> List[NodeRegistration]:
        """获取所有活跃节点"""
        return [
            r for r in self.registrations.values()
            if r.status == STATUS_ACTIVE and r.is_alive(self.heartbeat_timeout)
        ]

    def get_node_ids_by_type(self, node_type: str) -> List[str]:
        """按类型获取节点 ID"""
        return [
            r.node_id for r in self.get_active_nodes()
            if r.node_type == node_type
        ]

    def get_node_ids_by_capability(self, capability: str) -> List[str]:
        """按能力获取节点 ID"""
        return [
            r.node_id for r in self.get_active_nodes()
            if capability in r.capabilities
        ]

    # ========== 健康检查 ==========

    def check_health(self) -> Dict[str, List[str]]:
        """
        检查所有节点健康状态

        Returns:
            {
                "alive": [...],
                "dead": [...],
                "suspended": [...],
                "offline": [...],
            }
        """
        result = {"alive": [], "dead": [], "suspended": [], "offline": []}
        for reg in self.registrations.values():
            if reg.status == STATUS_OFFLINE:
                result["offline"].append(reg.node_id)
            elif reg.status == STATUS_SUSPENDED:
                result["suspended"].append(reg.node_id)
            elif reg.is_alive(self.heartbeat_timeout):
                result["alive"].append(reg.node_id)
            else:
                result["dead"].append(reg.node_id)
        return result

    def cleanup_dead_nodes(self, timeout: int = None) -> List[str]:
        """
        清理超时未心跳的节点

        Returns:
            被清理的节点 ID 列表
        """
        if timeout is None:
            timeout = self.heartbeat_timeout

        cleaned = []
        for node_id, reg in list(self.registrations.items()):
            if reg.status in (STATUS_OFFLINE, STATUS_SUSPENDED):
                continue
            if not reg.is_alive(timeout):
                reg.status = STATUS_OFFLINE
                cleaned.append(node_id)
                self._log_event("CLEANUP", node_id, "心跳超时自动下线")
        return cleaned

    # ========== 统计 ==========

    def get_statistics(self) -> Dict:
        """获取注册中心统计"""
        health = self.check_health()
        return {
            "total_registered": len(self.registrations),
            "alive": len(health["alive"]),
            "dead": len(health["dead"]),
            "suspended": len(health["suspended"]),
            "offline": len(health["offline"]),
            "by_type": self._count_by_type(),
            "heartbeat_timeout": self.heartbeat_timeout,
        }

    def _count_by_type(self) -> Dict[str, int]:
        counts = {}
        for reg in self.registrations.values():
            if reg.status == STATUS_ACTIVE:
                counts[reg.node_type] = counts.get(reg.node_type, 0) + 1
        return counts

    def get_registry_snapshot(self) -> Dict:
        """获取注册中心完整快照"""
        return {
            "nodes": {
                nid: reg.to_dict()
                for nid, reg in self.registrations.items()
            },
            "statistics": self.get_statistics(),
            "snapshot_time": datetime.now().isoformat(),
        }

    def export_registry(self) -> str:
        """导出注册中心为 JSON"""
        return json.dumps(self.get_registry_snapshot(), ensure_ascii=False, indent=2)

    # ========== 日志 ==========

    def _log_event(self, event: str, node_id: str, detail: str = ""):
        self._register_log.append({
            "event": event,
            "node_id": node_id,
            "detail": detail,
            "timestamp": datetime.now().isoformat(),
        })

    def get_register_log(self, limit: int = 50) -> List[Dict]:
        """获取注册日志"""
        return self._register_log[-limit:]
