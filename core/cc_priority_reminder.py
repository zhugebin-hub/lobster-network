#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CC 协议优先级催办器 - 小龙虾网络V3.1
自动检测 pending 消息，按优先级催办，超时自动清理

功能:
- 按优先级分类 pending 消息
- 截止前 1 小时发送催办
- 超时自动标记 timeout_no_ack
- 生成催办报告
"""

import json
import os
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
SHARED_DIR = REPO_ROOT / ".shared" / "messages"
TRACKING_FILE = SHARED_DIR / "cc_tracking.json"

# 优先级定义
PRIORITY_CRITICAL = "critical"
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# 催办策略（小时）
REMINDER_STRATEGY = {
    PRIORITY_CRITICAL: {"remind_before": 0.5, "auto_cleanup": True},   # 截止前30分钟催办，超时自动清理
    PRIORITY_HIGH: {"remind_before": 1.0, "auto_cleanup": True},       # 截止前1小时催办，超时自动清理
    PRIORITY_MEDIUM: {"remind_before": 2.0, "auto_cleanup": False},    # 截止前2小时催办，不自动清理
    PRIORITY_LOW: {"remind_before": 4.0, "auto_cleanup": False},       # 截止前4小时催办，不自动清理
}


class CCPriorityReminder:
    """CC 优先级催办器"""

    def __init__(self, tracking_file: Optional[str] = None):
        self.tracking_file = Path(tracking_file) if tracking_file else TRACKING_FILE
        self._data: Dict = {}
        self._load()

    def _load(self):
        """加载 cc_tracking.json"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception as e:
                logger.warning(f"[CC催办] 加载失败: {e}")
                self._data = {"pending": [], "completed": []}
        else:
            self._data = {"pending": [], "completed": []}

    def _save(self):
        """保存 cc_tracking.json"""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[CC催办] 保存失败: {e}")

    def classify_priority(self, item: Dict) -> str:
        """分类消息优先级"""
        category = item.get("category", "general").lower()
        subject = item.get("subject", "").lower()

        if "critical" in subject or "emergency" in subject:
            return PRIORITY_CRITICAL
        elif category in ("training_report", "ack_request", "sync_request"):
            return PRIORITY_HIGH
        elif category in ("feedback_request", "status_update"):
            return PRIORITY_MEDIUM
        else:
            return PRIORITY_LOW

    def check_and_remind(self) -> Dict:
        """检查并催办"""
        now = datetime.now()
        results = {
            "checked_at": now.isoformat(),
            "pending_count": len(self._data.get("pending", [])),
            "reminders_sent": [],
            "cleaned_up": [],
            "alerts": [],
        }

        new_pending = []
        for item in self._data.get("pending", []):
            tid = item.get("tracking_id", "")
            deadline_str = item.get("ack_deadline", "")
            pend_nodes = item.get("acks_pending", [])

            if not deadline_str or not pend_nodes:
                new_pending.append(item)
                continue

            try:
                deadline = datetime.fromisoformat(deadline_str[:19])
            except:
                new_pending.append(item)
                continue

            time_left = (deadline - now).total_seconds() / 3600  # 小时
            priority = self.classify_priority(item)
            strategy = REMINDER_STRATEGY.get(priority, REMINDER_STRATEGY[PRIORITY_LOW])

            # 催办逻辑
            if time_left <= strategy["remind_before"] and time_left > 0:
                results["reminders_sent"].append({
                    "tracking_id": tid,
                    "priority": priority,
                    "pending_nodes": pend_nodes,
                    "time_left_hours": round(time_left, 2),
                })
                logger.info(f"[CC催办] 发送催办: {tid} (优先级:{priority}, 剩余:{time_left:.2f}h)")

            # 超时清理逻辑
            elif time_left <= 0 and strategy["auto_cleanup"]:
                item["status"] = "timeout_no_ack"
                item["noted_at"] = now.isoformat()
                self._data["completed"].append(item)
                results["cleaned_up"].append(tid)
                logger.info(f"[CC催办] 自动清理超时: {tid}")
            else:
                new_pending.append(item)

        self._data["pending"] = new_pending
        self._save()

        results["remaining_pending"] = len(new_pending)
        results["total_completed"] = len(self._data["completed"])
        return results

    def get_pending_summary(self) -> List[Dict]:
        """获取 pending 摘要"""
        summary = []
        for item in self._data.get("pending", []):
            priority = self.classify_priority(item)
            summary.append({
                "tracking_id": item.get("tracking_id", ""),
                "subject": item.get("subject", "")[:50],
                "priority": priority,
                "pending_nodes": item.get("acks_pending", []),
                "deadline": item.get("ack_deadline", "")[:19],
            })
        # 按优先级排序
        priority_order = {PRIORITY_CRITICAL: 0, PRIORITY_HIGH: 1, PRIORITY_MEDIUM: 2, PRIORITY_LOW: 3}
        summary.sort(key=lambda x: priority_order.get(x["priority"], 3))
        return summary


# 便捷函数
def run_cc_reminder() -> Dict:
    """运行 CC 催办检查"""
    checker = CCPriorityReminder()
    return checker.check_and_remind()


def get_pending_summary() -> List[Dict]:
    """获取 pending 摘要"""
    checker = CCPriorityReminder()
    return checker.get_pending_summary()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    result = run_cc_reminder()
    print(json.dumps(result, ensure_ascii=False, indent=2))
