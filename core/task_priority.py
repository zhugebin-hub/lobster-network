#!/usr/bin/env python3
"""
任务优先级管理器 - 小龙虾网络V3.1
高/中/低优先级分类，确保关键任务优先执行
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# 优先级定义
PRIORITY_CRITICAL = "critical"  # 🔴 紧急 - 立即执行
PRIORITY_HIGH = "high"          # 🟠 高 - 今天完成
PRIORITY_MEDIUM = "medium"      # 🟡 中 - 本周完成
PRIORITY_LOW = "low"            # 🟢 低 - 按需完成

# 任务类型优先级映射
TASK_PRIORITY_MAP = {
    "training_report": PRIORITY_HIGH,
    "sync_request": PRIORITY_MEDIUM,
    "feedback_request": PRIORITY_MEDIUM,
    "status_update": PRIORITY_LOW,
    "general": PRIORITY_LOW,
    "go_training": PRIORITY_HIGH,
    "network_training": PRIORITY_MEDIUM,
    "poster_training": PRIORITY_MEDIUM,
    "ai_ml_training": PRIORITY_MEDIUM,
    "cybersecurity_training": PRIORITY_LOW,
    "data_structure_training": PRIORITY_LOW,
    "cc_broadcast": PRIORITY_HIGH,
    "ack_request": PRIORITY_HIGH,
    "reminder": PRIORITY_LOW,
    "error_alert": PRIORITY_CRITICAL,
    "system_maintenance": PRIORITY_MEDIUM,
}

# 超时配置（小时）
PRIORITY_TIMEOUTS = {
    PRIORITY_CRITICAL: 1,
    PRIORITY_HIGH: 8,
    PRIORITY_MEDIUM: 24,
    PRIORITY_LOW: 72,
}


@dataclass
class TaskPriority:
    """任务优先级"""
    task_id: str
    task_type: str
    priority: str
    created_at: str = ""
    deadline: str = ""
    assigned_to: str = ""
    status: str = "pending"  # pending/processing/completed/failed

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.deadline:
            timeout_hours = PRIORITY_TIMEOUTS.get(self.priority, 24)
            deadline = datetime.now() + timedelta(hours=timeout_hours)
            self.deadline = deadline.isoformat()


class TaskPriorityManager:
    """任务优先级管理器"""

    def __init__(self, storage_dir: str = "/shared/training/go"):
        self.storage_dir = Path(storage_dir)
        self.priority_file = self.storage_dir / "task_priorities.json"
        self._tasks: Dict[str, TaskPriority] = {}
        self._load()

    def classify_task(self, task_type: str, task_id: str, assigned_to: str = "") -> TaskPriority:
        """分类任务优先级"""
        priority = TASK_PRIORITY_MAP.get(task_type, PRIORITY_MEDIUM)
        task = TaskPriority(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            assigned_to=assigned_to,
        )
        self._tasks[task_id] = task
        self._save()
        return task

    def get_pending_tasks(self, student: Optional[str] = None) -> List[TaskPriority]:
        """获取待处理任务（按优先级排序）"""
        tasks = [t for t in self._tasks.values() if t.status == "pending"]
        if student:
            tasks = [t for t in tasks if not t.assigned_to or t.assigned_to == student]
        # 按优先级排序
        priority_order = {
            PRIORITY_CRITICAL: 0,
            PRIORITY_HIGH: 1,
            PRIORITY_MEDIUM: 2,
            PRIORITY_LOW: 3,
        }
        tasks.sort(key=lambda t: priority_order.get(t.priority, 2))
        return tasks

    def update_task_status(self, task_id: str, status: str):
        """更新任务状态"""
        if task_id in self._tasks:
            self._tasks[task_id].status = status
            self._save()

    def get_overdue_tasks(self) -> List[TaskPriority]:
        """获取逾期任务"""
        now = datetime.now()
        overdue = []
        for task in self._tasks.values():
            if task.status in ("pending", "processing"):
                deadline = datetime.fromisoformat(task.deadline)
                if now > deadline:
                    overdue.append(task)
        return overdue

    def get_stats(self) -> Dict:
        """获取统计"""
        total = len(self._tasks)
        by_priority = {}
        by_status = {}
        for task in self._tasks.values():
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
            by_status[task.status] = by_status.get(task.status, 0) + 1
        return {
            "total": total,
            "by_priority": by_priority,
            "by_status": by_status,
            "overdue": len(self.get_overdue_tasks()),
        }

    def _save(self):
        """持久化"""
        try:
            data = {
                "saved_at": datetime.now().isoformat(),
                "tasks": {k: v.__dict__ for k, v in self._tasks.items()},
            }
            with open(self.priority_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[任务优先级] 保存失败: {e}")

    def _load(self):
        """加载"""
        try:
            if self.priority_file.exists():
                with open(self.priority_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for k, v in data.get("tasks", {}).items():
                    self._tasks[k] = TaskPriority(**v)
        except Exception as e:
            print(f"[任务优先级] 加载失败: {e}")


# 便捷函数
def classify_and_send(task_type: str, task_id: str, assigned_to: str = ""):
    """分类并发送任务"""
    manager = TaskPriorityManager()
    return manager.classify_task(task_type, task_id, assigned_to)


if __name__ == "__main__":
    manager = TaskPriorityManager()
    print(json.dumps(manager.get_stats(), ensure_ascii=False, indent=2))
