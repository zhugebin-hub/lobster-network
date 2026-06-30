#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workspace 状态管理器 - 实现铁律三：状态要写文件，不要塞上下文
功能：
1. 统一 Workspace 结构
2. 状态文件化（state.json, progress.json, result.json）
3. 事务锁机制（lock 文件 + 断点续传）
4. 操作可审计（history 目录）

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
import fcntl
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from hashlib import md5

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
WORKSPACE_DIR = REPO_ROOT / ".shared" / "workspace"
AGENTS_DIR = WORKSPACE_DIR / "agents"
TASKS_DIR = WORKSPACE_DIR / "tasks"
LOCKS_DIR = WORKSPACE_DIR / "locks"


class WorkspaceManager:
    """Workspace 管理器"""
    
    def __init__(self):
        self.workspace_dir = WORKSPACE_DIR
        self.agents_dir = AGENTS_DIR
        self.tasks_dir = TASKS_DIR
        self.locks_dir = LOCKS_DIR
        
        # 确保目录存在
        self._ensure_directories()
        
    def _ensure_directories(self):
        """确保目录结构存在"""
        dirs = [
            self.workspace_dir,
            self.agents_dir / "orchestrator",
            self.agents_dir / "training",
            self.agents_dir / "communication",
            self.tasks_dir,
            self.locks_dir / "rpa",
            self.locks_dir / "training",
            self.locks_dir / "communication"
        ]
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
            
    def get_agent_state(self, agent_name: str) -> Dict:
        """获取 Agent 状态"""
        state_file = self.agents_dir / agent_name / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
        
    def update_agent_state(self, agent_name: str, state: Dict):
        """更新 Agent 状态"""
        state_dir = self.agents_dir / agent_name
        state_dir.mkdir(parents=True, exist_ok=True)
        
        state_file = state_dir / "state.json"
        state["updated_at"] = datetime.now().isoformat()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            
    def create_task(self, task_id: str, task_data: Dict) -> Dict:
        """创建任务"""
        task_dir = self.tasks_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建任务文件
        task_file = task_dir / "state.json"
        task_data["task_id"] = task_id
        task_data["created_at"] = datetime.now().isoformat()
        task_data["status"] = "created"
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, indent=2, ensure_ascii=False)
            
        # 创建进度文件
        progress_file = task_dir / "progress.json"
        progress_data = {
            "task_id": task_id,
            "steps": [],
            "current_step": 0,
            "total_steps": task_data.get("total_steps", 0),
            "created_at": datetime.now().isoformat()
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
            
        return task_data
        
    def update_task_progress(self, task_id: str, step: str, status: str = "completed"):
        """更新任务进度"""
        task_dir = self.tasks_dir / task_id
        progress_file = task_dir / "progress.json"
        
        if not progress_file.exists():
            return
            
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            
        progress["steps"].append({
            "step": step,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        progress["current_step"] = len(progress["steps"])
        progress["updated_at"] = datetime.now().isoformat()
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
            
    def complete_task(self, task_id: str, result: Dict):
        """完成任务"""
        task_dir = self.tasks_dir / task_id
        result_file = task_dir / "result.json"
        
        result["task_id"] = task_id
        result["completed_at"] = datetime.now().isoformat()
        result["status"] = "completed"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            
        # 更新任务状态
        state_file = task_dir / "state.json"
        with open(state_file, 'r') as f:
            state = json.load(f)
            
        state["status"] = "completed"
        state["completed_at"] = datetime.now().isoformat()
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
            
    def acquire_lock(self, lock_type: str, lock_id: str) -> bool:
        """获取事务锁"""
        lock_dir = self.locks_dir / lock_type
        lock_dir.mkdir(parents=True, exist_ok=True)
        
        lock_file = lock_dir / f"{lock_id}.lock"
        
        # 检查锁是否已存在
        if lock_file.exists():
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
                
            # 检查锁是否过期（30 分钟）
            lock_time_str = lock_data.get("created_at", datetime.now().isoformat())
            # Python 3.6 兼容
            try:
                lock_time = datetime.fromisoformat(lock_time_str)
            except AttributeError:
                lock_time = datetime.strptime(lock_time_str, "%Y-%m-%dT%H:%M:%S.%f")
                
            if (datetime.now() - lock_time).total_seconds() > 1800:
                # 锁已过期，强制释放
                self.release_lock(lock_type, lock_id)
            else:
                return False
                
        # 创建锁
        lock_data = {
            "lock_id": lock_id,
            "lock_type": lock_type,
            "created_at": datetime.now().isoformat(),
            "status": "acquired"
        }
        
        with open(lock_file, 'w', encoding='utf-8') as f:
            json.dump(lock_data, f, indent=2, ensure_ascii=False)
            
        return True
        
    def release_lock(self, lock_type: str, lock_id: str):
        """释放事务锁"""
        lock_dir = self.locks_dir / lock_type
        lock_file = lock_dir / f"{lock_id}.lock"
        
        if lock_file.exists():
            # 更新锁状态
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
                
            lock_data["status"] = "released"
            lock_data["released_at"] = datetime.now().isoformat()
            
            with open(lock_file, 'w', encoding='utf-8') as f:
                json.dump(lock_data, f, indent=2, ensure_ascii=False)
                
    def get_task_history(self, task_id: str) -> List[Dict]:
        """获取任务历史"""
        task_dir = self.tasks_dir / task_id
        history = []
        
        # 读取状态文件
        state_file = task_dir / "state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                history.append({"type": "state", "data": json.load(f)})
                
        # 读取进度文件
        progress_file = task_dir / "progress.json"
        if progress_file.exists():
            with open(progress_file, 'r') as f:
                history.append({"type": "progress", "data": json.load(f)})
                
        # 读取结果文件
        result_file = task_dir / "result.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                history.append({"type": "result", "data": json.load(f)})
                
        return history


class TransactionManager:
    """事务管理器 - 实现断点续传"""
    
    def __init__(self, workspace: WorkspaceManager):
        self.workspace = workspace
        
    def begin_transaction(self, transaction_type: str, transaction_id: str) -> bool:
        """开始事务"""
        # 获取锁
        return self.workspace.acquire_lock(transaction_type, transaction_id)
        
    def commit_transaction(self, transaction_type: str, transaction_id: str, result: Dict):
        """提交事务"""
        # 更新进度
        self.workspace.update_task_progress(transaction_id, "commit", "completed")
        
        # 完成任务
        self.workspace.complete_task(transaction_id, result)
        
        # 释放锁
        self.workspace.release_lock(transaction_type, transaction_id)
        
    def rollback_transaction(self, transaction_type: str, transaction_id: str, error: str):
        """回滚事务"""
        # 更新进度
        self.workspace.update_task_progress(transaction_id, f"rollback: {error}", "failed")
        
        # 释放锁
        self.workspace.release_lock(transaction_type, transaction_id)
        
    def check_transaction_status(self, transaction_type: str, transaction_id: str) -> Dict:
        """检查事务状态"""
        lock_dir = self.workspace.locks_dir / transaction_type
        lock_file = lock_dir / f"{transaction_id}.lock"
        
        if not lock_file.exists():
            return {"status": "no_lock", "transaction_id": transaction_id}
            
        with open(lock_file, 'r') as f:
            lock_data = json.load(f)
            
        return {
            "status": lock_data.get("status", "unknown"),
            "transaction_id": transaction_id,
            "created_at": lock_data.get("created_at"),
            "released_at": lock_data.get("released_at")
        }


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        workspace = WorkspaceManager()
        
        if command == "test_workspace":
            # 测试 Workspace 功能
            print("=== Workspace 测试 ===")
            
            # 1. 创建任务
            task_data = {
                "task_type": "training",
                "student_id": "xiaochen",
                "day": 5,
                "problem_count": 100,
                "game_count": 10,
                "total_steps": 5
            }
            
            task = workspace.create_task("task_001", task_data)
            print(f"创建任务：{task['task_id']}")
            
            # 2. 更新进度
            workspace.update_task_progress("task_001", "step_1", "completed")
            workspace.update_task_progress("task_001", "step_2", "completed")
            print("更新进度：step_1, step_2")
            
            # 3. 完成任务
            result = {
                "accuracy": 0.85,
                "rating": "A",
                "feedback": "表现优秀"
            }
            workspace.complete_task("task_001", result)
            print("完成任务")
            
            # 4. 获取历史
            history = workspace.get_task_history("task_001")
            print(f"\n任务历史：{len(history)} 条记录")
            for record in history:
                print(f"  - {record['type']}: {record['data'].get('status', 'N/A')}")
                
        elif command == "test_transaction":
            # 测试事务管理
            print("=== 事务管理测试 ===")
            tm = TransactionManager(workspace)
            
            # 1. 开始事务
            success = tm.begin_transaction("training", "txn_001")
            print(f"开始事务：{success}")
            
            # 2. 检查状态
            status = tm.check_transaction_status("training", "txn_001")
            print(f"事务状态：{status['status']}")
            
            # 3. 提交事务
            result = {"status": "success", "data": "test"}
            tm.commit_transaction("training", "txn_001", result)
            print("提交事务")
            
            # 4. 检查状态
            status = tm.check_transaction_status("training", "txn_001")
            print(f"事务状态：{status['status']}")
            
        else:
            print(f"未知命令：{command}")
    else:
        print("=== Workspace 状态管理器 ===")
        print("用法：")
        print("  python3 workspace_manager.py test_workspace")
        print("  python3 workspace_manager.py test_transaction")


if __name__ == "__main__":
    main()
