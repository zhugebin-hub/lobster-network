#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六学员适应度曲线追踪 — 自进化闭环

包含：
- SelfEvolutionLoop: 接收涌现检测器的输出事件，将涌现事件转化为
  额外奖励信号反馈至 RL 调度器，实现「检测→反馈→优化」闭环。
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# 日志
# ============================================================

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("rl_orchestrator")


# ============================================================
# SelfEvolutionLoop — 自进化闭环
# ============================================================

class SelfEvolutionLoop:
    """
    自进化闭环控制器。

    论文 6.3.2 节：接收涌现检测器的输出事件，将涌现事件转化为
    额外奖励信号反馈至 RL 调度器，实现「检测→反馈→优化」闭环。

    用法:
        evo = SelfEvolutionLoop(scheduler)
        evo.on_emergence(emergence_event)
        evo.get_evolution_trajectory()
    """

    REWARD_MAP = {
        "new_knowledge": 0.30,
        "new_strategy": 0.25,
        "new_connection": 0.20,
        "new_metaphor": 0.15,
    }

    def __init__(self, scheduler=None, log_path: str = ""):
        self._scheduler = scheduler
        self._evolution_log: List[Dict[str, Any]] = []
        self._total_emergence_reward = 0.0
        self._emergence_count = 0

        if not log_path:
            log_path = str(LOG_DIR / "evolution_log.json")
        self._log_path = log_path

        logger.info("[SelfEvolutionLoop] 自进化闭环已启用")

    def on_emergence(self, event) -> float:
        """接收涌现事件并转化为奖励信号"""
        category = getattr(event, 'category', None)
        if category is None:
            return 0.0

        cat_str = category.value if hasattr(category, 'value') else str(category)
        reward = self.REWARD_MAP.get(cat_str, 0.0)
        self._total_emergence_reward += reward
        self._emergence_count += 1

        entry = {
            "event_id": getattr(event, 'event_id', 'unknown'),
            "timestamp": getattr(event, 'timestamp', ''),
            "category": cat_str,
            "emergence_value": getattr(event, 'emergence_value', 0.0),
            "reward": reward,
            "cumulative_reward": self._total_emergence_reward,
        }
        self._evolution_log.append(entry)

        if self._scheduler and hasattr(self._scheduler, 'inject_extra_reward'):
            self._scheduler.inject_extra_reward(reward)

        logger.info(
            f"[SelfEvolutionLoop] 涌现→奖励: {cat_str} → +{reward:.2f} "
            f"(累计: {self._total_emergence_reward:.2f})"
        )

        if len(self._evolution_log) % 10 == 0:
            self._persist()

        return reward

    def _persist(self):
        """持久化进化轨迹"""
        try:
            with open(self._log_path, "w", encoding="utf-8") as f:
                json.dump({
                    "total_events": self._emergence_count,
                    "total_reward": round(self._total_emergence_reward, 4),
                    "trajectory": self._evolution_log,
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"[SelfEvolutionLoop] 持久化失败: {e}")

    def get_evolution_trajectory(self) -> Dict[str, Any]:
        """获取完整进化轨迹"""
        self._persist()
        return {
            "total_events": self._emergence_count,
            "total_reward": round(self._total_emergence_reward, 4),
            "trajectory": self._evolution_log,
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计摘要"""
        category_counts: Dict[str, int] = {}
        for entry in self._evolution_log:
            cat = entry.get("category", "unknown")
            category_counts[cat] = category_counts.get(cat, 0) + 1

        return {
            "total_emergence_events": self._emergence_count,
            "total_emergence_reward": round(self._total_emergence_reward, 4),
            "by_category": category_counts,
            "recent_events": self._evolution_log[-10:] if self._evolution_log else [],
        }
