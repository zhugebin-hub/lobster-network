#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涌现检测器 (Emergence Detector)

基于语义涌现度量模型：
- 涌现值 E = 视角差异度(Dp) × 知识互补性(Ck) × 对话深度(Dd)
- 触发阈值：E > 0.7 标记为涌现事件
- 事件分类：新知识/新策略/新连接/新隐喻
- 滑动窗口统计

参考：
- 小龙虾网络第四阶段优化部署报告
- v0.6.0 语义涌现引擎：E = 0.3Dp + 0.3Ck + 0.2Dd + 0.2No
"""

import json
import logging
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# 日志与存储
# ============================================================

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("emergence_detector")
logger.setLevel(logging.INFO)
_handler = logging.FileHandler(DATA_DIR / "emergence.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_handler)


# ============================================================
# 数据模型
# ============================================================

class EmergenceCategory(str, Enum):
    NEW_KNOWLEDGE = "new_knowledge"   # 新知识
    NEW_STRATEGY = "new_strategy"     # 新策略
    NEW_CONNECTION = "new_connection" # 新连接
    NEW_METAPHOR = "new_metaphor"     # 新隐喻


@dataclass
class EmergenceEvent:
    """涌现事件"""
    event_id: str
    timestamp: str
    category: EmergenceCategory
    emergence_value: float
    participants: List[str] = field(default_factory=list)
    description: str = ""
    context_snapshot: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# 涌现值计算
# ============================================================

def _compute_perspective_divergence(agent_a_view: set, agent_b_view: set) -> float:
    """
    视角差异度 Dp = 1 - Jaccard 相似度

    参数:
      agent_a_view: Agent A 使用的概念/关键词集合
      agent_b_view: Agent B 使用的概念/关键词集合
    """
    if not agent_a_view and not agent_b_view:
        return 0.0
    intersection = len(agent_a_view & agent_b_view)
    union = len(agent_a_view | agent_b_view)
    if union == 0:
        return 0.0
    jaccard = intersection / union
    return 1.0 - jaccard


def _compute_knowledge_complementarity(agent_a_knowledge: set, agent_b_knowledge: set) -> float:
    """
    知识互补性 Ck = 信息熵视角

    互补性 = (A独有知识量 + B独有知识量) / 总知识量
    越互补，值越高。
    """
    total = len(agent_a_knowledge | agent_b_knowledge)
    if total == 0:
        return 0.0
    unique_a = len(agent_a_knowledge - agent_b_knowledge)
    unique_b = len(agent_b_knowledge - agent_a_knowledge)
    return (unique_a + unique_b) / total


def _compute_dialogue_depth(turn_count: int, max_turns: int = 20) -> float:
    """
    对话深度 Dd = 非线性饱和函数

    Dd = 1 - e^(-turn_count / saturation)
    回合越多，深度越高，但边际递减。
    """
    saturation = max_turns / 3.0
    return 1.0 - math.exp(-turn_count / max(saturation, 1.0))


def _compute_output_novelty(new_concepts: set, historical_concepts: set) -> float:
    """
    输出新颖度 No = 新概念占比

    仅在 v0.6.0 增强模型（四因子）中使用。
    """
    if not new_concepts:
        return 0.0
    total = len(new_concepts | historical_concepts)
    if total == 0:
        return 0.0
    return len(new_concepts - historical_concepts) / total


def compute_emergence_v3(
    agent_a_view: set,
    agent_b_view: set,
    agent_a_knowledge: set,
    agent_b_knowledge: set,
    dialogue_turns: int,
) -> float:
    """
    v0.4.0 三因子模型：E = Dp × Ck × Dd
    """
    dp = _compute_perspective_divergence(agent_a_view, agent_b_view)
    ck = _compute_knowledge_complementarity(agent_a_knowledge, agent_b_knowledge)
    dd = _compute_dialogue_depth(dialogue_turns)
    return dp * ck * dd


def compute_emergence_v6(
    agent_a_view: set,
    agent_b_view: set,
    agent_a_knowledge: set,
    agent_b_knowledge: set,
    dialogue_turns: int,
    new_concepts: set,
    historical_concepts: set,
) -> float:
    """
    v0.6.0 四因子模型：E = 0.3Dp + 0.3Ck + 0.2Dd + 0.2No
    """
    dp = _compute_perspective_divergence(agent_a_view, agent_b_view)
    ck = _compute_knowledge_complementarity(agent_a_knowledge, agent_b_knowledge)
    dd = _compute_dialogue_depth(dialogue_turns)
    no = _compute_output_novelty(new_concepts, historical_concepts)
    return 0.3 * dp + 0.3 * ck + 0.2 * dd + 0.2 * no


# ============================================================
# EmergenceDetector 主类
# ============================================================

class EmergenceDetector:
    """
    涌现检测器

    用法:
        detector = EmergenceDetector(threshold=0.7)
        event = detector.detect(
            agent_a_view={"棋形", "厚势", "先手"},
            agent_b_view={"估值", "胜率", "搜索深度"},
            agent_a_knowledge={"围棋", "死活题"},
            agent_b_knowledge={"统计", "蒙特卡洛", "UCT"},
            dialogue_turns=8,
            participants=["xiaochen", "qoder"],
        )
    """

    def __init__(self, threshold: float = 0.7, use_v6_model: bool = True, window_hours: int = 1):
        """
        参数:
          threshold: 涌现阈值（默认 0.7）
          use_v6_model: 是否使用 v0.6.0 四因子模型
          window_hours: 滑动窗口大小（小时）
        """
        self.threshold = threshold
        self.use_v6_model = use_v6_model
        self.window_hours = window_hours

        # 历史概念库（用于新颖度计算）
        self._historical_concepts: set = set()

        # 事件存储
        self._events: List[EmergenceEvent] = []
        self._event_counter = 0

        # 窗口统计
        self._hourly_counts: Dict[str, int] = {}
        self._daily_counts: Dict[str, int] = {}

    def detect(
        self,
        agent_a_view: set,
        agent_b_view: set,
        agent_a_knowledge: set,
        agent_b_knowledge: set,
        dialogue_turns: int,
        participants: Optional[List[str]] = None,
        new_concepts: Optional[set] = None,
        description: str = "",
    ) -> Optional[EmergenceEvent]:
        """
        检测是否发生涌现。

        返回 EmergenceEvent 或 None。
        """
        if self.use_v6_model:
            nc = new_concepts or set()
            emergence_value = compute_emergence_v6(
                agent_a_view, agent_b_view,
                agent_a_knowledge, agent_b_knowledge,
                dialogue_turns,
                nc, self._historical_concepts,
            )
        else:
            emergence_value = compute_emergence_v3(
                agent_a_view, agent_b_view,
                agent_a_knowledge, agent_b_knowledge,
                dialogue_turns,
            )

        # 更新历史概念库
        if new_concepts:
            self._historical_concepts.update(new_concepts)

        # 判断是否触发
        if emergence_value < self.threshold:
            logger.debug(f"涌现值 {emergence_value:.3f} < 阈值 {self.threshold}，未触发")
            return None

        # 分类
        category = self._classify(agent_a_view, agent_b_view, agent_a_knowledge, agent_b_knowledge)

        self._event_counter += 1
        event = EmergenceEvent(
            event_id=f"EMG_{self._event_counter:04d}",
            timestamp=datetime.now().isoformat(),
            category=category,
            emergence_value=round(emergence_value, 4),
            participants=participants or [],
            description=description,
            context_snapshot={
                "agent_a_view": list(agent_a_view),
                "agent_b_view": list(agent_b_view),
                "dialogue_turns": dialogue_turns,
            },
        )

        self._events.append(event)
        self._record_window(event)
        self._persist(event)

        logger.info(
            f"涌现事件! E={emergence_value:.3f} 类别={category.value} "
            f"参与者={participants or ['unknown']}"
        )
        return event

    def _classify(
        self,
        agent_a_view: set,
        agent_b_view: set,
        agent_a_knowledge: set,
        agent_b_knowledge: set,
    ) -> EmergenceCategory:
        """分类涌现事件"""
        overlap_view = len(agent_a_view & agent_b_view)
        overlap_know = len(agent_a_knowledge & agent_b_knowledge)

        if overlap_view == 0 and overlap_know == 0:
            return EmergenceCategory.NEW_CONNECTION
        if overlap_know > 0 and overlap_view == 0:
            return EmergenceCategory.NEW_METAPHOR
        if overlap_view > 0 and overlap_know > 0:
            return EmergenceCategory.NEW_KNOWLEDGE
        return EmergenceCategory.NEW_STRATEGY

    def _record_window(self, event: EmergenceEvent):
        """记录到滑动窗口统计"""
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d %H:00")
        day_key = now.strftime("%Y-%m-%d")

        self._hourly_counts[hour_key] = self._hourly_counts.get(hour_key, 0) + 1
        self._daily_counts[day_key] = self._daily_counts.get(day_key, 0) + 1

        # 清理过期窗口
        cutoff_hour = (now - timedelta(hours=self.window_hours * 24)).strftime("%Y-%m-%d %H:00")
        self._hourly_counts = {k: v for k, v in self._hourly_counts.items() if k >= cutoff_hour}

    def _persist(self, event: EmergenceEvent):
        """持久化事件到 JSON"""
        events_file = DATA_DIR / "emergence_events.json"
        events_data = []
        if events_file.exists():
            try:
                with open(events_file, "r", encoding="utf-8") as f:
                    events_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                events_data = []

        events_data.append({
            "event_id": event.event_id,
            "timestamp": event.timestamp,
            "category": event.category.value,
            "emergence_value": event.emergence_value,
            "participants": event.participants,
            "description": event.description,
        })

        # 只保留最近 1000 条
        if len(events_data) > 1000:
            events_data = events_data[-1000:]

        with open(events_file, "w", encoding="utf-8") as f:
            json.dump(events_data, f, ensure_ascii=False, indent=2)

    # ---- 查询接口 ----

    def get_events(self, last_n: int = 50, category: Optional[EmergenceCategory] = None) -> List[EmergenceEvent]:
        """获取最近 N 个涌现事件"""
        result = self._events[-last_n:]
        if category:
            result = [e for e in result if e.category == category]
        return result

    def get_hourly_rate(self) -> float:
        """当前小时涌现率"""
        now = datetime.now()
        hour_key = now.strftime("%Y-%m-%d %H:00")
        return float(self._hourly_counts.get(hour_key, 0))

    def get_daily_rate(self) -> float:
        """今日涌现率"""
        day_key = datetime.now().strftime("%Y-%m-%d")
        return float(self._daily_counts.get(day_key, 0))

    def get_stats(self) -> dict:
        """统计概览"""
        total = len(self._events)
        categories = {}
        for e in self._events:
            categories[e.category.value] = categories.get(e.category.value, 0) + 1

        return {
            "total_events": total,
            "threshold": self.threshold,
            "model": "v6" if self.use_v6_model else "v3",
            "hourly_rate": self.get_hourly_rate(),
            "daily_rate": self.get_daily_rate(),
            "by_category": categories,
            "recent_events": [
                {"id": e.event_id, "timestamp": e.timestamp, "category": e.category.value, "value": e.emergence_value}
                for e in self._events[-10:]
            ],
        }
