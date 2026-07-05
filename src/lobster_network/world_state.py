"""
世界状态管理器
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .node import Node


@dataclass
class WorldState:
    """世界状态"""
    version: int
    loaded_chunks: List[Dict]
    unlocked_treasures: List[Dict]
    current_tasks: List[str]
    spawned_nodes: List[str]
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "version": self.version,
            "loaded_chunks": self.loaded_chunks,
            "unlocked_treasures": self.unlocked_treasures,
            "current_tasks": self.current_tasks,
            "spawned_nodes": self.spawned_nodes,
            "updated_at": self.updated_at,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class WorldStateManager:
    """世界状态管理器"""
    
    def __init__(self):
        """初始化世界状态管理器"""
        self.states: Dict[str, WorldState] = {}
    
    def get_state(self, node_id: str) -> WorldState:
        """
        获取节点的世界状态
        
        Args:
            node_id: 节点ID
        
        Returns:
            WorldState: 世界状态
        """
        if node_id not in self.states:
            self.states[node_id] = WorldState(
                version=0,
                loaded_chunks=[],
                unlocked_treasures=[],
                current_tasks=[],
                spawned_nodes=[],
            )
        return self.states[node_id]
    
    def update_state(
        self,
        node_id: str,
        chunk_id: Optional[str] = None,
        treasure_id: Optional[str] = None,
        task: Optional[str] = None,
        spawned_node: Optional[str] = None,
    ) -> WorldState:
        """
        更新节点的世界状态
        
        Args:
            node_id: 节点ID
            chunk_id: 加载的Chunk ID
            treasure_id: 解锁的宝藏ID
            task: 当前任务
            spawned_node: 新生成的节点ID
        
        Returns:
            WorldState: 更新后的世界状态
        """
        state = self.get_state(node_id)
        state.version += 1
        state.updated_at = datetime.now().isoformat()
        
        if chunk_id and chunk_id not in [c["chunk_id"] for c in state.loaded_chunks]:
            state.loaded_chunks.append({
                "chunk_id": chunk_id,
                "loaded_at": datetime.now().isoformat(),
            })
        
        if treasure_id and treasure_id not in [t["treasure_id"] for t in state.unlocked_treasures]:
            state.unlocked_treasures.append({
                "treasure_id": treasure_id,
                "unlocked_at": datetime.now().isoformat(),
            })
        
        if task and task not in state.current_tasks:
            state.current_tasks.append(task)
        
        if spawned_node and spawned_node not in state.spawned_nodes:
            state.spawned_nodes.append(spawned_node)
        
        return state
    
    def get_all_states(self) -> Dict[str, WorldState]:
        """获取所有节点的世界状态"""
        return self.states.copy()
    
    def export_states(self) -> str:
        """导出所有世界状态为JSON字符串"""
        return json.dumps(
            {node_id: state.to_dict() for node_id, state in self.states.items()},
            ensure_ascii=False,
            indent=2,
        )
