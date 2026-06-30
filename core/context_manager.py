#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
上下文管理器 - 实现铁律一：上下文越少越好
功能：
1. 结构化上下文（任务类型、阶段、当前焦点）
2. 分段化上下文（系统约束/任务定义/当前状态/工具签名/历史摘要）
3. 可回放（每次上下文构造可重放、可 diff）
4. 可审计（保留来源链）

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from hashlib import md5

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
WORKSPACE_DIR = REPO_ROOT / ".shared" / "workspace"
CONTEXT_DIR = WORKSPACE_DIR / "context"
SCHEMA_FILE = CONTEXT_DIR / "schema.json"
CACHE_DIR = CONTEXT_DIR / "cache"
FILTERS_DIR = CONTEXT_DIR / "filters"


class ContextSchema:
    """上下文 Schema 定义"""
    
    def __init__(self):
        self.schema = {
            "system_constraint": {
                "description": "系统约束和规则",
                "max_length": 500,
                "required": True
            },
            "task_definition": {
                "description": "任务定义和目标",
                "max_length": 1000,
                "required": True
            },
            "current_state": {
                "description": "当前状态和进度",
                "max_length": 800,
                "required": True
            },
            "tool_signatures": {
                "description": "可用工具签名",
                "max_length": 600,
                "required": True
            },
            "history_summary": {
                "description": "历史摘要（最近 N 条）",
                "max_length": 400,
                "max_items": 3,
                "required": False
            }
        }
        
    def validate(self, context: Dict) -> bool:
        """验证上下文结构"""
        for key, config in self.schema.items():
            if config.get("required") and key not in context:
                return False
            
            # 检查长度限制
            if key in context:
                content = context[key]
                if isinstance(content, str) and len(content) > config.get("max_length", 9999):
                    return False
                    
        return True


class ContextFilter:
    """上下文过滤器 - 只加载相关上下文"""
    
    def __init__(self, schema: ContextSchema):
        self.schema = schema
        
    def filter(self, task: Dict, context_schema: Dict) -> Dict:
        """过滤上下文，只保留相关部分"""
        filtered = {}
        
        for key in context_schema:
            if key in task:
                filtered[key] = task[key]
                
        return filtered


class ContextManager:
    """上下文管理器"""
    
    def __init__(self):
        self.schema = ContextSchema()
        self.filter = ContextFilter(self.schema)
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def build_context(self, task: Dict) -> Dict:
        """构建结构化上下文"""
        # 1. 过滤相关上下文
        filtered = self.filter.filter(task, self.schema.schema)
        
        # 2. 分段化上下文
        structured = {
            "system_constraint": filtered.get("system_constraint", ""),
            "task_definition": filtered.get("task_definition", ""),
            "current_state": filtered.get("current_state", ""),
            "tool_signatures": filtered.get("tool_signatures", ""),
            "history_summary": filtered.get("history_summary", [])[:3]  # 只保留最近 3 条
        }
        
        # 3. 验证上下文
        if not self.schema.validate(structured):
            raise ValueError("上下文验证失败")
            
        # 4. 缓存上下文
        self._cache_context(task.get("task_id", "unknown"), structured)
        
        return structured
        
    def _cache_context(self, task_id: str, context: Dict):
        """缓存上下文"""
        cache_file = self.cache_dir / f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(context, f, indent=2, ensure_ascii=False)
            
    def get_context_history(self, task_id: str) -> List[Dict]:
        """获取上下文历史"""
        history = []
        for cache_file in sorted(self.cache_dir.glob(f"{task_id}_*.json")):
            with open(cache_file, 'r') as f:
                history.append(json.load(f))
        return history


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "build":
            # 构建上下文
            task_id = sys.argv[2] if len(sys.argv) > 2 else "test_task"
            manager = ContextManager()
            
            # 模拟任务
            task = {
                "task_id": task_id,
                "system_constraint": "训练任务必须在 24 小时内完成",
                "task_definition": "完成 Day 5 训练任务",
                "current_state": "Day 4 已完成，准确率 85%",
                "tool_signatures": "schedule_training, evaluate_performance",
                "history_summary": [
                    {"day": 3, "accuracy": 0.81},
                    {"day": 4, "accuracy": 0.85}
                ]
            }
            
            context = manager.build_context(task)
            print("=== 构建的上下文 ===")
            print(json.dumps(context, indent=2, ensure_ascii=False))
            
        elif command == "history":
            # 查看上下文历史
            task_id = sys.argv[2] if len(sys.argv) > 2 else "test_task"
            manager = ContextManager()
            history = manager.get_context_history(task_id)
            
            print(f"=== {task_id} 上下文历史 ===")
            for i, ctx in enumerate(history):
                print(f"\n--- 第{i+1}次 ---")
                print(json.dumps(ctx, indent=2, ensure_ascii=False))
                
        else:
            print(f"未知命令：{command}")
    else:
        print("=== 上下文管理器 ===")
        print("用法：")
        print("  python3 context_manager.py build [task_id]")
        print("  python3 context_manager.py history [task_id]")


if __name__ == "__main__":
    main()
