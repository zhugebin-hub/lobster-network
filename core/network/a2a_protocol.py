#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V5.2 — A2A 智能体间通信协议模块

基于 Google A2A (Agent-to-Agent) 协议规范实现：
- Agent Card 数据结构：描述 Agent 能力/接口/状态
- Task Object：任务描述/状态/结果
- Agent Registry：注册发现机制
- MessageRouter：跨Agent消息路由（点对点/广播/多播）

参考：
- Google A2A Protocol Specification
- 智能体网络最新进展综述_2025-2026 — 2.1 协议标准化
"""

import json
import time
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("a2a_protocol")
logger.setLevel(logging.INFO)


# ============================================================
# 枚举定义
# ============================================================

class AgentStatus(str, Enum):
    """Agent 运行状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


class TaskStatus(str, Enum):
    """Task 生命周期状态"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLED_BACK = "rolled_back"


class MessageType(str, Enum):
    """消息类型"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    HEARTBEAT = "heartbeat"
    BROADCAST = "broadcast"
    MULTICAST = "multicast"
    DISCOVERY = "discovery"
    CAPABILITY_QUERY = "capability_query"


class RouteMode(str, Enum):
    """路由模式"""
    POINT_TO_POINT = "point_to_point"
    BROADCAST = "broadcast"
    MULTICAST = "multicast"


# ============================================================
# 数据模型 — AgentCard
# ============================================================

@dataclass
class AgentCapability:
    """Agent 能力描述"""
    skill_id: str
    skill_name: str
    description: str
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    confidence_score: float = 1.0  # 能力置信度 0~1


@dataclass
class AgentCard:
    """
    Agent Card — 描述 Agent 的完整身份与能力。

    对应 Google A2A 协议中的 AgentCard 结构：
    - 身份信息（ID/名称/版本）
    - 能力清单（接口签名 + I/O Schema）
    - 运行时状态
    - 端点信息
    """
    agent_id: str
    display_name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[AgentCapability] = field(default_factory=list)
    status: AgentStatus = AgentStatus.ONLINE
    host: str = "localhost"
    port: int = 0
    protocol_version: str = "A2A/1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_heartbeat: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "version": self.version,
            "description": self.description,
            "capabilities": [
                {
                    "skill_id": c.skill_id,
                    "skill_name": c.skill_name,
                    "description": c.description,
                    "input_schema": c.input_schema,
                    "output_schema": c.output_schema,
                    "tags": c.tags,
                    "confidence_score": c.confidence_score,
                }
                for c in self.capabilities
            ],
            "status": self.status.value,
            "host": self.host,
            "port": self.port,
            "protocol_version": self.protocol_version,
            "metadata": self.metadata,
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentCard":
        caps = [
            AgentCapability(
                skill_id=c["skill_id"],
                skill_name=c["skill_name"],
                description=c["description"],
                input_schema=c.get("input_schema", {}),
                output_schema=c.get("output_schema", {}),
                tags=c.get("tags", []),
                confidence_score=c.get("confidence_score", 1.0),
            )
            for c in data.get("capabilities", [])
        ]
        return cls(
            agent_id=data["agent_id"],
            display_name=data["display_name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            capabilities=caps,
            status=AgentStatus(data.get("status", "online")),
            host=data.get("host", "localhost"),
            port=data.get("port", 0),
            protocol_version=data.get("protocol_version", "A2A/1.0"),
            metadata=data.get("metadata", {}),
            registered_at=data.get("registered_at", datetime.now().isoformat()),
            last_heartbeat=data.get("last_heartbeat", datetime.now().isoformat()),
        )

    def heartbeat(self):
        """更新心跳时间"""
        self.last_heartbeat = datetime.now().isoformat()

    def is_alive(self, timeout_sec: int = 90) -> bool:
        """检查 Agent 是否存活"""
        if self.status in (AgentStatus.OFFLINE, AgentStatus.MAINTENANCE):
            return False
        try:
            last = datetime.fromisoformat(self.last_heartbeat)
            return (datetime.now() - last).total_seconds() < timeout_sec
        except (ValueError, TypeError):
            return False


# ============================================================
# 数据模型 — TaskObject
# ============================================================

@dataclass
class TaskObject:
    """
    Task Object — A2A 协议任务单元。

    包含完整的任务描述、执行状态、中间产物和最终结果。
    支持子任务树形结构（parent_task_id / subtasks）。
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None          # agent_id
    created_by: Optional[str] = None            # agent_id
    parent_task_id: Optional[str] = None
    priority: int = 0                           # 0=最低, 10=最高
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: List[Dict[str, Any]] = field(default_factory=list)
    error_info: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    deadline: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    subtasks: List[str] = field(default_factory=list)  # task_id 列表
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "status": self.status.value,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "parent_task_id": self.parent_task_id,
            "priority": self.priority,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "intermediate_results": self.intermediate_results,
            "error_info": self.error_info,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "deadline": self.deadline,
            "metadata": self.metadata,
            "subtasks": self.subtasks,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskObject":
        return cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "pending")),
            assigned_to=data.get("assigned_to"),
            created_by=data.get("created_by"),
            parent_task_id=data.get("parent_task_id"),
            priority=data.get("priority", 0),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            intermediate_results=data.get("intermediate_results", []),
            error_info=data.get("error_info"),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            created_at=data.get("created_at", datetime.now().isoformat()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            deadline=data.get("deadline"),
            metadata=data.get("metadata", {}),
            subtasks=data.get("subtasks", []),
            tags=data.get("tags", []),
        )

    def start(self, assigned_to: str) -> "TaskObject":
        """标记任务开始执行"""
        self.status = TaskStatus.RUNNING
        self.assigned_to = assigned_to
        self.started_at = datetime.now().isoformat()
        return self

    def complete(self, outputs: Dict[str, Any] = None) -> "TaskObject":
        """标记任务完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now().isoformat()
        if outputs:
            self.outputs = outputs
        return self

    def fail(self, error: Dict[str, Any]) -> "TaskObject":
        """标记任务失败"""
        self.error_info = error
        if self.retry_count < self.max_retries:
            self.status = TaskStatus.PENDING
            self.retry_count += 1
            self.assigned_to = None
        else:
            self.status = TaskStatus.FAILED
        self.completed_at = datetime.now().isoformat()
        return self

    def cancel(self, reason: str = "") -> "TaskObject":
        """取消任务"""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now().isoformat()
        if reason:
            self.error_info = {"reason": reason}
        return self

    def add_intermediate_result(self, result: Dict[str, Any]):
        """追加中间产物"""
        self.intermediate_results.append({
            "timestamp": datetime.now().isoformat(),
            **result,
        })

    def add_subtask(self, task_id: str):
        """添加子任务"""
        if task_id not in self.subtasks:
            self.subtasks.append(task_id)


# ============================================================
# 数据模型 — Message
# ============================================================

@dataclass
class AgentMessage:
    """跨 Agent 通信消息"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    msg_type: MessageType = MessageType.TASK_REQUEST
    sender_id: str = ""
    target_ids: List[str] = field(default_factory=list)
    route_mode: RouteMode = RouteMode.POINT_TO_POINT
    payload: Dict[str, Any] = field(default_factory=dict)
    task_id: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl_sec: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "msg_type": self.msg_type.value,
            "sender_id": self.sender_id,
            "target_ids": self.target_ids,
            "route_mode": self.route_mode.value,
            "payload": self.payload,
            "task_id": self.task_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "ttl_sec": self.ttl_sec,
            "metadata": self.metadata,
        }

    def is_expired(self) -> bool:
        try:
            ts = datetime.fromisoformat(self.timestamp)
            return (datetime.now() - ts).total_seconds() > self.ttl_sec
        except (ValueError, TypeError):
            return True


# ============================================================
# AgentRegistry — 注册发现机制
# ============================================================

class AgentRegistry:
    """
    Agent Registry — 集中式注册发现中心。

    功能：
    - register: 注册 AgentCard
    - unregister: 注销 AgentCard
    - discover: 按能力标签发现 Agent
    - heartbeat: 心跳维持
    - gossip: 跨注册中心传播（预留）
    """

    def __init__(self, registry_id: str = "default"):
        self.registry_id = registry_id
        self._agents: Dict[str, AgentCard] = {}
        self._capability_index: Dict[str, Set[str]] = {}  # tag → agent_ids
        self._started_at = datetime.now().isoformat()
        logger.info(f"[AgentRegistry] 注册中心 '{registry_id}' 已初始化")

    def register(self, card: AgentCard) -> bool:
        """注册 Agent"""
        if card.agent_id in self._agents:
            existing = self._agents[card.agent_id]
            if existing.registered_at == card.registered_at:
                existing.heartbeat()
                return True
        card.heartbeat()
        card.registered_at = datetime.now().isoformat()
        self._agents[card.agent_id] = card
        # 重建能力索引
        for cap in card.capabilities:
            for tag in cap.tags:
                self._capability_index.setdefault(tag, set()).add(card.agent_id)
            self._capability_index.setdefault(cap.skill_id, set()).add(card.agent_id)
        logger.info(f"[AgentRegistry] Agent '{card.agent_id}' 已注册，能力数={len(card.capabilities)}")
        return True

    def unregister(self, agent_id: str) -> bool:
        """注销 Agent"""
        card = self._agents.pop(agent_id, None)
        if card:
            card.status = AgentStatus.OFFLINE
            # 清理能力索引
            for cap in card.capabilities:
                for tag in cap.tags:
                    agents = self._capability_index.get(tag, set())
                    agents.discard(agent_id)
                agents = self._capability_index.get(cap.skill_id, set())
                agents.discard(agent_id)
            logger.info(f"[AgentRegistry] Agent '{agent_id}' 已注销")
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[AgentCard]:
        """获取 AgentCard"""
        return self._agents.get(agent_id)

    def heartbeat(self, agent_id: str) -> bool:
        """处理心跳"""
        card = self._agents.get(agent_id)
        if card:
            card.heartbeat()
            return True
        return False

    def discover(self, capability_tags: List[str] = None,
                 status_filter: List[AgentStatus] = None) -> List[AgentCard]:
        """
        按能力标签 + 状态发现 Agent。

        参数:
            capability_tags: 能力标签列表（AND 逻辑 — 需全部满足）
            status_filter: 状态过滤器
        """
        result = list(self._agents.values())

        if capability_tags:
            tag_set = set(capability_tags)
            result = [
                a for a in result
                if all(
                    tag_set & {cap.skill_id for cap in a.capabilities}.union(
                        *(set(cap.tags) for cap in a.capabilities)
                    )
                    for _ in [1]  # 只需一次迭代做 check
                )
            ]
            # 更精确: 每个 a 的 capability tags 集合需包含所有要求的 tag
            result = [
                a for a in result
                if tag_set.issubset(
                    set.union(*[set(c.tags) | {c.skill_id} for c in a.capabilities])
                    if a.capabilities else set()
                )
            ]

        if status_filter:
            status_set = set(status_filter)
            result = [a for a in result if a.status in status_set]

        return result

    def list_online_agents(self) -> List[AgentCard]:
        """列出所有在线 Agent"""
        timeout = 90
        return [
            a for a in self._agents.values()
            if a.status == AgentStatus.ONLINE and a.is_alive(timeout)
        ]

    def get_capability_coverage(self) -> Dict[str, int]:
        """获取能力覆盖统计"""
        return {tag: len(agents) for tag, agents in self._capability_index.items()}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "registry_id": self.registry_id,
            "started_at": self._started_at,
            "agent_count": len(self._agents),
            "online_count": len(self.list_online_agents()),
            "capability_coverage": self.get_capability_coverage(),
            "agents": {aid: card.to_dict() for aid, card in self._agents.items()},
        }


# ============================================================
# MessageRouter — 跨Agent消息路由
# ============================================================

class MessageRouter:
    """
    MessageRouter — 跨 Agent 消息路由器。

    支持三种路由模式：
    - 点对点 (Point-to-Point): 精确投递到目标 Agent
    - 广播 (Broadcast): 发送到所有在线 Agent
    - 多播 (Multicast): 发送到符合能力标签的子集

    内置：
    - TTL 过期检测
    - 消息队列缓冲
    - 投递确认追踪
    """

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self._pending_queue: List[AgentMessage] = []
        self._delivery_log: List[Dict[str, Any]] = []
        self._max_log_size = 10000
        logger.info("[MessageRouter] 消息路由器已初始化")

    def route(self, message: AgentMessage) -> Dict[str, Any]:
        """
        路由消息到目标 Agent(s)。

        返回投递报告: { "sent_to": [...], "failed": [...], "queued": [...], "total_targets": N }
        """
        # TTL 检查
        if message.is_expired():
            logger.warning(f"[MessageRouter] 消息 {message.message_id} 已过期，丢弃")
            return {"sent_to": [], "failed": [], "queued": [], "total_targets": 0, "expired": True}

        # 解析目标列表
        targets = self._resolve_targets(message)
        if not targets:
            logger.warning(f"[MessageRouter] 消息 {message.message_id} 无可用目标")
            return {"sent_to": [], "failed": [], "queued": [], "total_targets": 0}

        sent, failed, queued = [], [], []

        for agent_id in targets:
            card = self.registry.get_agent(agent_id)
            if not card or not card.is_alive():
                # 离线：入队等待
                self._pending_queue.append(message)
                queued.append(agent_id)
                continue

            # 模拟投递
            try:
                self._deliver(agent_id, message)
                sent.append(agent_id)
            except Exception as e:
                logger.error(f"[MessageRouter] 投递到 {agent_id} 失败: {e}")
                failed.append({"agent_id": agent_id, "error": str(e)})

        # 记录投递日志
        self._record_delivery(message.message_id, sent, failed, queued)

        return {
            "message_id": message.message_id,
            "sent_to": sent,
            "failed": failed,
            "queued": queued,
            "total_targets": len(targets),
        }

    def _resolve_targets(self, message: AgentMessage) -> List[str]:
        """解析目标 Agent 列表"""
        if message.route_mode == RouteMode.POINT_TO_POINT:
            return message.target_ids
        elif message.route_mode == RouteMode.BROADCAST:
            return [a.agent_id for a in self.registry.list_online_agents()]
        elif message.route_mode == RouteMode.MULTICAST:
            # 从 payload 中提取能力标签
            tags = message.metadata.get("capability_tags", [])
            agents = self.registry.discover(capability_tags=tags)
            return [a.agent_id for a in agents]
        return []

    def _deliver(self, agent_id: str, message: AgentMessage):
        """实际投递逻辑（记录到日志）"""
        logger.debug(
            f"[MessageRouter] {message.msg_type.value} "
            f"{message.sender_id} → {agent_id}: {message.message_id}"
        )

    def _record_delivery(self, message_id: str, sent: List[str],
                         failed: List[Any], queued: List[str]):
        self._delivery_log.append({
            "message_id": message_id,
            "timestamp": datetime.now().isoformat(),
            "sent": sent,
            "failed": failed,
            "queued": queued,
        })
        if len(self._delivery_log) > self._max_log_size:
            self._delivery_log = self._delivery_log[-self._max_log_size:]

    def flush_queue(self) -> int:
        """重试投递待发送队列中的消息"""
        retry_count = 0
        remaining = []
        for msg in self._pending_queue:
            if not msg.is_expired():
                targets = self._resolve_targets(msg)
                online = [t for t in targets if self.registry.get_agent(t) and
                          self.registry.get_agent(t).is_alive()]
                for tid in online:
                    try:
                        self._deliver(tid, msg)
                        retry_count += 1
                    except Exception:
                        remaining.append(msg)
                        break
                else:
                    continue
            remaining.append(msg)
        self._pending_queue = remaining
        logger.info(f"[MessageRouter] 队列刷新: 重试投递 {retry_count} 条，剩余 {len(remaining)} 条")
        return retry_count

    def get_stats(self) -> Dict[str, Any]:
        return {
            "pending_queue_size": len(self._pending_queue),
            "total_deliveries": len(self._delivery_log),
            "queue_depth": len(self._pending_queue),
        }


# ============================================================
# A2AProtocol — 顶层协议协调器
# ============================================================

class A2AProtocol:
    """
    A2A Protocol 顶层协调器。

    整合 Registry + Router，提供一站式 A2A 通信能力：
    - 注册本地 Agent
    - 发现远程 Agent
    - 发送任务请求/广播/多播
    - 查询状态
    """

    def __init__(self, node_id: str = "lobster-node"):
        self.node_id = node_id
        self.registry = AgentRegistry(registry_id=node_id)
        self.router = MessageRouter(self.registry)
        self._local_card: Optional[AgentCard] = None
        logger.info(f"[A2AProtocol] A2A 协议栈已启动，节点={node_id}")

    def register_local_agent(self, card: AgentCard) -> bool:
        """注册本地 Agent 到注册中心"""
        self._local_card = card
        return self.registry.register(card)

    def get_local_card(self) -> Optional[AgentCard]:
        return self._local_card

    def send_task(self, task: TaskObject, target_agent_id: str) -> Dict[str, Any]:
        """发送任务到指定 Agent（点对点）"""
        msg = AgentMessage(
            msg_type=MessageType.TASK_REQUEST,
            sender_id=self.node_id,
            target_ids=[target_agent_id],
            route_mode=RouteMode.POINT_TO_POINT,
            payload={"task": task.to_dict()},
            task_id=task.task_id,
        )
        return self.router.route(msg)

    def broadcast(self, payload: Dict[str, Any],
                  msg_type: MessageType = MessageType.BROADCAST) -> Dict[str, Any]:
        """广播消息到所有在线 Agent"""
        msg = AgentMessage(
            msg_type=msg_type,
            sender_id=self.node_id,
            target_ids=[],
            route_mode=RouteMode.BROADCAST,
            payload=payload,
        )
        return self.router.route(msg)

    def multicast(self, capability_tags: List[str],
                  payload: Dict[str, Any]) -> Dict[str, Any]:
        """多播消息到具备特定能力的 Agent"""
        msg = AgentMessage(
            msg_type=MessageType.MULTICAST,
            sender_id=self.node_id,
            target_ids=[],
            route_mode=RouteMode.MULTICAST,
            metadata={"capability_tags": capability_tags},
            payload=payload,
        )
        return self.router.route(msg)

    def discover(self, capability_tags: List[str] = None) -> List[AgentCard]:
        """发现 Agent"""
        return self.registry.discover(capability_tags)

    def get_status(self) -> Dict[str, Any]:
        """获取 A2A 协议栈状态"""
        return {
            "node_id": self.node_id,
            "registry": self.registry.to_dict(),
            "router_stats": self.router.get_stats(),
            "local_agent": self._local_card.to_dict() if self._local_card else None,
        }

    def shutdown(self):
        """关闭协议栈"""
        if self._local_card:
            self.registry.unregister(self._local_card.agent_id)
        logger.info(f"[A2AProtocol] A2A 协议栈已关闭，节点={self.node_id}")
