#!/usr/bin/env python3
"""
事务管理器
基于 Agent Harness工程实践设计（借鉴悟空 AI 招聘经验）

引入强制性的事务文件：
- RPA 开始写 lock 文件
- 每完成一条追加进度
- 结束标记 done
- 任何中断下次启动时读 lock 文件从断点续传
"""

import json
import os
import time
import fcntl
from pathlib import Path
from typing import Dict, Optional


class TransactionLock:
    """
    事务锁
    确保同一时间只有一个 Agent 操作同一资源
    """
    
    def __init__(self, workspace_dir: str, resource_id: str):
        self.workspace_dir = Path(workspace_dir) / "locks"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.resource_id = resource_id
        self.lock_file = self.workspace_dir / f"{resource_id}.lock"
        self.lock_fd = None
    
    def acquire(self, timeout: int = 300) -> bool:
        """
        获取锁
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            bool: 是否成功获取锁
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                self.lock_fd = open(self.lock_file, 'w')
                fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                
                # 写入锁信息
                lock_info = {
                    "resource_id": self.resource_id,
                    "acquired_at": time.time(),
                    "pid": os.getpid()
                }
                self.lock_fd.write(json.dumps(lock_info, ensure_ascii=False, indent=2))
                self.lock_fd.flush()
                
                print(f"[TransactionLock] 锁已获取: {self.resource_id}")
                return True
                
            except (IOError, OSError):
                time.sleep(1)
        
        print(f"[TransactionLock] 获取锁超时: {self.resource_id}")
        return False
    
    def release(self):
        """释放锁"""
        if self.lock_fd:
            fcntl.flock(self.lock_fd.fileno(), fcntl.LOCK_UN)
            self.lock_fd.close()
            self.lock_fd = None
            
            # 删除锁文件
            if self.lock_file.exists():
                self.lock_file.unlink()
            
            print(f"[TransactionLock] 锁已释放: {self.resource_id}")
    
    def __enter__(self):
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class TransactionProgress:
    """
    事务进度跟踪
    记录每一步的完成情况，支持断点续传
    """
    
    def __init__(self, workspace_dir: str, transaction_id: str):
        self.workspace_dir = Path(workspace_dir) / "transactions"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.transaction_id = transaction_id
        self.progress_file = self.workspace_dir / f"{transaction_id}_progress.json"
        
        # 加载已有进度
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """加载进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "transaction_id": self.transaction_id,
                "status": "pending",
                "steps": [],
                "created_at": time.time(),
                "updated_at": time.time()
            }
    
    def _save_progress(self):
        """保存进度"""
        self.progress["updated_at"] = time.time()
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, ensure_ascii=False, indent=2)
    
    def start(self):
        """开始事务"""
        self.progress["status"] = "running"
        self._save_progress()
        print(f"[TransactionProgress] 事务 {self.transaction_id} 已开始")
    
    def complete_step(self, step_id: str, result: Dict = None):
        """
        完成步骤
        
        Args:
            step_id: 步骤 ID
            result: 步骤结果
        """
        step_record = {
            "step_id": step_id,
            "status": "completed",
            "completed_at": time.time(),
            "result": result
        }
        
        # 检查步骤是否已存在
        existing_step = next((s for s in self.progress["steps"] if s["step_id"] == step_id), None)
        if existing_step:
            existing_step.update(step_record)
        else:
            self.progress["steps"].append(step_record)
        
        self._save_progress()
        print(f"[TransactionProgress] 步骤 {step_id} 已完成")
    
    def fail_step(self, step_id: str, error: str):
        """
        步骤失败
        
        Args:
            step_id: 步骤 ID
            error: 错误信息
        """
        step_record = {
            "step_id": step_id,
            "status": "failed",
            "failed_at": time.time(),
            "error": error
        }
        
        # 检查步骤是否已存在
        existing_step = next((s for s in self.progress["steps"] if s["step_id"] == step_id), None)
        if existing_step:
            existing_step.update(step_record)
        else:
            self.progress["steps"].append(step_record)
        
        self.progress["status"] = "failed"
        self._save_progress()
        print(f"[TransactionProgress] 步骤 {step_id} 失败: {error}")
    
    def complete(self):
        """完成事务"""
        self.progress["status"] = "completed"
        self.progress["completed_at"] = time.time()
        self._save_progress()
        print(f"[TransactionProgress] 事务 {self.transaction_id} 已完成")
    
    def get_last_completed_step(self) -> Optional[str]:
        """获取最后完成的步骤 ID"""
        completed_steps = [s for s in self.progress["steps"] if s.get("status") == "completed"]
        if completed_steps:
            return completed_steps[-1]["step_id"]
        return None
    
    def get_resume_from(self) -> Optional[str]:
        """获取断点续传起点"""
        last_step = self.get_last_completed_step()
        if last_step:
            # 返回下一步
            try:
                step_num = int(last_step.split("_")[-1])
                return f"step_{step_num + 1}"
            except (ValueError, IndexError):
                return None
        return None
    
    def get_status(self) -> str:
        """获取事务状态"""
        return self.progress.get("status", "pending")


class TransactionManager:
    """
    事务管理器
    管理事务锁和进度跟踪
    """
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
        
        self.workspace_dir = Path(workspace_dir)
    
    def create_lock(self, resource_id: str) -> TransactionLock:
        """创建事务锁"""
        return TransactionLock(str(self.workspace_dir), resource_id)
    
    def create_progress(self, transaction_id: str) -> TransactionProgress:
        """创建进度跟踪"""
        return TransactionProgress(str(self.workspace_dir), transaction_id)
    
    def execute_with_transaction(self, transaction_id: str, steps: list) -> Dict:
        """
        带事务执行步骤
        
        Args:
            transaction_id: 事务 ID
            steps: 步骤列表，每个步骤是 {"step_id": str, "action": callable}
            
        Returns:
            Dict: 执行结果
        """
        progress = self.create_progress(transaction_id)
        
        # 检查断点续传
        resume_from = progress.get_resume_from()
        start_index = 0
        if resume_from:
            print(f"[TransactionManager] 断点续传，从 {resume_from} 开始")
            for i, step in enumerate(steps):
                if step["step_id"] == resume_from:
                    start_index = i
                    break
        
        # 开始事务
        progress.start()
        
        # 执行步骤
        results = []
        for i, step in enumerate(steps):
            if i < start_index:
                continue
            
            step_id = step["step_id"]
            action = step["action"]
            
            try:
                # 获取锁
                lock = self.create_lock(f"{transaction_id}_{step_id}")
                with lock:
                    # 执行动作
                    result = action()
                    progress.complete_step(step_id, result)
                    results.append({"step_id": step_id, "status": "success", "result": result})
            except Exception as e:
                progress.fail_step(step_id, str(e))
                results.append({"step_id": step_id, "status": "failed", "error": str(e)})
                break
        
        # 完成事务
        if all(r["status"] == "success" for r in results):
            progress.complete()
        
        return {
            "transaction_id": transaction_id,
            "status": progress.get_status(),
            "results": results
        }


if __name__ == "__main__":
    # 测试事务管理器
    manager = TransactionManager()
    
    # 定义步骤
    def step1():
        print("  执行步骤 1...")
        time.sleep(1)
        return {"message": "步骤 1 完成"}
    
    def step2():
        print("  执行步骤 2...")
        time.sleep(1)
        return {"message": "步骤 2 完成"}
    
    def step3():
        print("  执行步骤 3...")
        time.sleep(1)
        return {"message": "步骤 3 完成"}
    
    steps = [
        {"step_id": "step_1", "action": step1},
        {"step_id": "step_2", "action": step2},
        {"step_id": "step_3", "action": step3}
    ]
    
    # 执行事务
    print("\n=== 执行事务 ===")
    result = manager.execute_with_transaction("test_transaction_001", steps)
    print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试断点续传（模拟中断后继续）
    print("\n=== 测试断点续传 ===")
    result = manager.execute_with_transaction("test_transaction_001", steps)
    print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
EOF

echo "事务管理器已创建"