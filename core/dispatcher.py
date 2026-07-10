#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 任务调度器 (Task Dispatcher)
负责任务分发、状态跟踪与资源协调。原 1088 行 paper_coach_dispatcher.py 已拆分至此。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

from .router import TaskRouter
from .task_queue import TaskQueue

@dataclass
class Task:
    """任务实体"""
    task_id: str
    title: str
    domain: str
    priority: str = "normal"
    status: str = "pending"  # pending, assigned, in_progress, completed, failed
    assignee: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)

class TaskDispatcher:
    """任务调度器核心"""
    
    def __init__(self, base_dir: str = "/home/admin/lobster-network/shared/dispatcher"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        
        self.queue = TaskQueue()
        self.router = TaskRouter()
        self.tasks: Dict[str, Task] = {}
        
        self._load()
        print(f"📦 任务调度器初始化: {base_dir}")
        
    def _load(self):
        """加载持久化任务"""
        task_file = os.path.join(self.base_dir, "tasks.json")
        if os.path.exists(task_file):
            with open(task_file, 'r') as f:
                data = json.load(f)
                self.tasks = {tid: Task(**t) for tid, t in data.items()}
                
    def _save(self):
        """持久化任务"""
        task_file = os.path.join(self.base_dir, "tasks.json")
        with open(task_file, 'w') as f:
            json.dump({tid: t.to_dict() for tid, t in self.tasks.items()}, f, ensure_ascii=False, indent=2)
            
    def create_task(self, title: str, domain: str, priority: str = "normal", metadata: Dict = None) -> str:
        """创建新任务"""
        task_id = f"TASK_{len(self.tasks)+1:03d}_{int(time.time())}"
        task = Task(task_id=task_id, title=title, domain=domain, priority=priority, metadata=metadata or {})
        self.tasks[task_id] = task
        self.queue.enqueue(task_id, priority)
        self._save()
        print(f"🆕 任务已创建: {task_id} [{domain}/{priority}]")
        return task_id
        
    def assign_task(self, task_id: str, assignee: str) -> bool:
        """分配任务"""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.assignee = assignee
        task.status = "assigned"
        task.updated_at = datetime.now().isoformat()
        self._save()
        print(f"👤 任务已分配: {task_id} -> {assignee}")
        return True
        
    def update_status(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        if task_id not in self.tasks:
            return False
        self.tasks[task_id].status = status
        self.tasks[task_id].updated_at = datetime.now().isoformat()
        self._save()
        print(f"🔄 任务状态更新: {task_id} -> {status}")
        return True
        
    def get_pending_tasks(self, domain: Optional[str] = None) -> List[Task]:
        """获取待处理任务"""
        tasks = [t for t in self.tasks.values() if t.status == "pending"]
        if domain:
            tasks = [t for t in tasks if t.domain == domain]
        return sorted(tasks, key=lambda x: x.priority, reverse=True)
        
    def get_report(self) -> Dict[str, Any]:
        """生成调度报告"""
        status_counts = {}
        for t in self.tasks.values():
            status_counts[t.status] = status_counts.get(t.status, 0) + 1
            
        return {
            "total_tasks": len(self.tasks),
            "status_distribution": status_counts,
            "queue_length": self.queue.size(),
            "recent_tasks": [t.to_dict() for t in list(self.tasks.values())[-5:]]
        }

# 示例用法
if __name__ == "__main__":
    dispatcher = TaskDispatcher()
    
    # 创建任务
    t1 = dispatcher.create_task("台风巴威路径预测", "typhoon", "high", {"target": "bavi"})
    t2 = dispatcher.create_task("耐虾肽-1 结构优化", "drug", "normal", {"compound": "bavi_peptide_1"})
    t3 = dispatcher.create_task("围棋布局评估", "go", "low", {"board": "9x9"})
    
    # 分配任务
    dispatcher.assign_task(t1, "node_met")
    dispatcher.assign_task(t2, "node_ocean")
    
    # 更新状态
    dispatcher.update_status(t1, "in_progress")
    
    # 获取报告
    report = dispatcher.get_report()
    print("\n📊 调度报告:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    print("\n✅ 任务调度器测试完成")
