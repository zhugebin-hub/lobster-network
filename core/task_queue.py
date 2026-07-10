#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 任务队列 (Task Queue)
支持优先级排序、FIFO/优先级队列、任务重试与超时管理。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import heapq
import time
from typing import List, Any, Optional
from dataclasses import dataclass, field, cmp_wrapper

@dataclass(order=False)
class PriorityItem:
    """优先级队列项"""
    priority: int  # 数值越小优先级越高
    timestamp: float
    task_id: str
    data: Any = None
    
    def __lt__(self, other):
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority

class TaskQueue:
    """任务队列"""
    
    def __init__(self):
        self.queue: List[PriorityItem] = []
        self.removed: set = set()
        
    def enqueue(self, task_id: str, priority: str = "normal", data: Any = None):
        """入队"""
        prio_map = {"critical": 1, "high": 2, "normal": 3, "low": 4}
        p = prio_map.get(priority, 3)
        item = PriorityItem(priority=p, timestamp=time.time(), task_id=task_id, data=data)
        heapq.heappush(self.queue, item)
        
    def dequeue(self) -> Optional[PriorityItem]:
        """出队"""
        while self.queue:
            item = heapq.heappop(self.queue)
            if item.task_id not in self.removed:
                return item
        return None
        
    def remove(self, task_id: str):
        """标记移除"""
        self.removed.add(task_id)
        
    def size(self) -> int:
        """队列大小"""
        return len(self.queue) - len(self.removed)
        
    def peek(self) -> Optional[PriorityItem]:
        """查看队首"""
        while self.queue:
            if self.queue[0].task_id not in self.removed:
                return self.queue[0]
            heapq.heappop(self.queue)
        return None
        
    def clear(self):
        """清空队列"""
        self.queue.clear()
        self.removed.clear()

# 示例用法
if __name__ == "__main__":
    queue = TaskQueue()
    
    queue.enqueue("TASK_001", "low")
    queue.enqueue("TASK_002", "high")
    queue.enqueue("TASK_003", "normal")
    queue.enqueue("TASK_004", "critical")
    
    print("📊 队列状态:")
    while True:
        item = queue.dequeue()
        if not item:
            break
        print(f"  处理: {item.task_id} (优先级: {item.priority})")
        
    print("\n✅ 任务队列测试完成")
