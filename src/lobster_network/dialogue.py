"""
对话引擎
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from .node import Node


@dataclass
class DialogueResult:
    """对话结果"""
    dialogue_id: str
    participants: List[str]
    input_context: Dict[str, str]
    emergence_score: float
    new_insight: str
    new_world_state: Dict
    treasure_unlocked: Optional[str] = None
    next_action: str = "continue"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "dialogue_id": self.dialogue_id,
            "participants": self.participants,
            "input_context": self.input_context,
            "emergence_score": self.emergence_score,
            "new_insight": self.new_insight,
            "new_world_state": self.new_world_state,
            "treasure_unlocked": self.treasure_unlocked,
            "next_action": self.next_action,
            "timestamp": self.timestamp,
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class DialogueEngine:
    """对话引擎"""
    
    def __init__(self, emergence_threshold: float = 0.5):
        """
        初始化对话引擎
        
        Args:
            emergence_threshold: 涌现阈值，超过此值触发宝藏渲染
        """
        self.emergence_threshold = emergence_threshold
        self.dialogue_history: List[DialogueResult] = []
    
    def dialogue(
        self,
        node_a: Node,
        node_b: Node,
        trigger: str = "",
    ) -> DialogueResult:
        """
        触发两个节点之间的对话
        
        Args:
            node_a: 节点A
            node_b: 节点B
            trigger: 触发事件描述
        
        Returns:
            DialogueResult: 对话结果
        """
        # 生成对话ID
        dialogue_id = f"dialogue-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 收集输入上下文
        input_context = {
            node_a.node_id: f"视角: {node_a.seed['perspective']}, 知识: {node_a.seed['knowledge_base']}",
            node_b.node_id: f"视角: {node_b.seed['perspective']}, 知识: {node_b.seed['knowledge_base']}",
        }
        
        # 计算涌现值
        emergence_score = self._calculate_emergence(node_a, node_b)
        
        # 生成新见解
        new_insight = self._generate_insight(node_a, node_b, emergence_score)
        
        # 更新世界状态
        new_world_state = {
            "version": max(node_a.current_world["version"], node_b.current_world["version"]) + 1,
            "loaded_chunks": list(set(
                [c["chunk_id"] for c in node_a.current_world["loaded_chunks"]] +
                [c["chunk_id"] for c in node_b.current_world["loaded_chunks"]]
            )),
        }
        
        # 检查是否解锁宝藏
        treasure_unlocked = None
        if emergence_score > self.emergence_threshold:
            treasure_unlocked = f"treasure-{dialogue_id}"
            node_a.update_world(treasure_id=treasure_unlocked)
            node_b.update_world(treasure_id=treasure_unlocked)
        
        # 创建对话结果
        result = DialogueResult(
            dialogue_id=dialogue_id,
            participants=[node_a.node_id, node_b.node_id],
            input_context=input_context,
            emergence_score=emergence_score,
            new_insight=new_insight,
            new_world_state=new_world_state,
            treasure_unlocked=treasure_unlocked,
        )
        
        # 记录历史
        self.dialogue_history.append(result)
        
        return result
    
    def _calculate_emergence(self, node_a: Node, node_b: Node) -> float:
        """
        计算涌现值
        
        Args:
            node_a: 节点A
            node_b: 节点B
        
        Returns:
            float: 涌现值 (0-1)
        """
        # 视角差异度
        perspective_distance = self._perspective_distance(node_a, node_b)
        
        # 知识互补性
        knowledge_complementarity = self._knowledge_complementarity(node_a, node_b)
        
        # 对话深度（初始为1）
        dialogue_depth = 1.0
        
        # 输出新颖度（初始为0.5）
        novelty_of_output = 0.5
        
        # 综合计算
        emergence_score = (
            perspective_distance * 0.3 +
            knowledge_complementarity * 0.3 +
            dialogue_depth * 0.2 +
            novelty_of_output * 0.2
        )
        
        return min(max(emergence_score, 0.0), 1.0)
    
    def _perspective_distance(self, node_a: Node, node_b: Node) -> float:
        """计算视角差异度"""
        if node_a.seed["perspective"] == node_b.seed["perspective"]:
            return 0.0
        return 1.0
    
    def _knowledge_complementarity(self, node_a: Node, node_b: Node) -> float:
        """计算知识互补性"""
        if node_a.seed["knowledge_base"] == node_b.seed["knowledge_base"]:
            return 0.0
        return 1.0
    
    def _generate_insight(self, node_a: Node, node_b: Node, emergence_score: float) -> str:
        """
        生成新见解
        
        Args:
            node_a: 节点A
            node_b: 节点B
            emergence_score: 涌现值
        
        Returns:
            str: 新见解
        """
        if emergence_score > 0.7:
            return f"{node_a.name}的{node_a.seed['perspective']}视角与{node_b.name}的{node_b.seed['perspective']}视角碰撞，产生高价值新见解"
        elif emergence_score > 0.4:
            return f"{node_a.name}的{node_a.seed['perspective']}视角与{node_b.name}的{node_b.seed['perspective']}视角碰撞，产生中等价值新见解"
        else:
            return f"{node_a.name}的{node_a.seed['perspective']}视角与{node_b.name}的{node_b.seed['perspective']}视角碰撞，产生低价值新见解"
