#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 消息路由器 (Task Router)
负责 MQTT 消息路由、主题匹配与分发。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import re
from typing import Dict, List, Callable, Optional

class TaskRouter:
    """消息路由器"""
    
    def __init__(self):
        self.routes: Dict[str, Callable] = {}
        self.wildcards: List[tuple] = []  # (pattern, handler)
        
    def route(self, topic: str, payload: dict):
        """路由消息到对应处理器"""
        # 精确匹配
        if topic in self.routes:
            self.routes[topic](topic, payload)
            return True
            
        # 通配符匹配
        for pattern, handler in self.wildcards:
            if re.match(pattern, topic):
                handler(topic, payload)
                return True
                
        print(f"⚠️ 未找到路由处理器: {topic}")
        return False
        
    def add_route(self, topic: str, handler: Callable):
        """添加精确路由"""
        self.routes[topic] = handler
        print(f"🔗 路由已注册: {topic}")
        
    def add_wildcard_route(self, pattern: str, handler: Callable):
        """添加通配符路由"""
        # 转换 MQTT 通配符为正则
        regex = pattern.replace("+", "[^/]+").replace("#", ".*")
        self.wildcards.append((f"^{regex}$", handler))
        print(f"🔗 通配符路由已注册: {pattern}")
        
    def remove_route(self, topic: str):
        """移除路由"""
        if topic in self.routes:
            del self.routes[topic]
            print(f"🔌 路由已移除: {topic}")

# 示例用法
if __name__ == "__main__":
    router = TaskRouter()
    
    def handle_status(topic, data):
        print(f"📡 处理状态消息: {data.get('node_id')} -> {data.get('status')}")
        
    def handle_task(topic, data):
        print(f"📋 处理任务消息: {data.get('task_id')} -> {data.get('status')}")
        
    router.add_route("lobster/nodes/status", handle_status)
    router.add_wildcard_route("lobster/tasks/+/update", handle_task)
    
    # 测试路由
    router.route("lobster/nodes/status", {"node_id": "qoder", "status": "online"})
    router.route("lobster/tasks/TASK_001/update", {"task_id": "TASK_001", "status": "completed"})
    
    print("\n✅ 路由器测试完成")
