"""
涌现检测器
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .node import Node
from .dialogue import DialogueResult


@dataclass
class EmergenceEvent:
    """涌现事件"""
    event_id: str
    dialogue_id: str
    participants: List[str]
    emergence_score: float
    new_insight: str
    treasure_unlocked: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class EmergenceDetector:
    """涌现检测器"""
    
    def __init__(self, threshold: float = 0.5):
        """
        初始化涌现检测器
        
        Args:
            threshold: 涌现阈值
        """
        self.threshold = threshold
        self.events: List[EmergenceEvent] = []
    
    def detect(self, dialogue_result: DialogueResult) -> Optional[EmergenceEvent]:
        """
        检测涌现事件
        
        Args:
            dialogue_result: 对话结果
        
        Returns:
            Optional[EmergenceEvent]: 涌现事件（如果检测到）
        """
        if dialogue_result.emergence_score > self.threshold:
            event = EmergenceEvent(
                event_id=f"event-{dialogue_result.dialogue_id}",
                dialogue_id=dialogue_result.dialogue_id,
                participants=dialogue_result.participants,
                emergence_score=dialogue_result.emergence_score,
                new_insight=dialogue_result.new_insight,
                treasure_unlocked=dialogue_result.treasure_unlocked,
            )
            self.events.append(event)
            return event
        return None
    
    def get_events(self, min_score: Optional[float] = None) -> List[EmergenceEvent]:
        """
        获取涌现事件列表
        
        Args:
            min_score: 最小涌现值过滤
        
        Returns:
            List[EmergenceEvent]: 涌现事件列表
        """
        if min_score is not None:
            return [e for e in self.events if e.emergence_score >= min_score]
        return self.events.copy()
    
    def get_statistics(self) -> Dict:
        """
        获取涌现统计信息
        
        Returns:
            Dict: 统计信息
        """
        if not self.events:
            return {
                "total_events": 0,
                "avg_emergence_score": 0.0,
                "max_emergence_score": 0.0,
                "treasures_unlocked": 0,
            }
        
        scores = [e.emergence_score for e in self.events]
        treasures = [e for e in self.events if e.treasure_unlocked]
        
        return {
            "total_events": len(self.events),
            "avg_emergence_score": sum(scores) / len(scores),
            "max_emergence_score": max(scores),
            "treasures_unlocked": len(treasures),
        }
