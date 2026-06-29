#!/usr/bin/env python3
"""
动态切片调度器 (Dynamic Slicing Queue)
部署在诸葛马服务器上，管理任务优先级
V4.0 Phase 2 - 对标华为网络智能
"""
import json
import os
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from queue import PriorityQueue

class TaskPriority:
    CRITICAL = 0   # 围棋对局、紧急任务
    HIGH = 1       # 训练任务（2小时内ACK）
    MEDIUM = 2     # 训练报告（4小时内提交）
    LOW = 3        # 一般通知（24小时内）

class DynamicSlicingQueue:
    def __init__(self, training_dir="/home/admin/go-training/shared/"):
        self.training_dir = Path(training_dir)
        self.from_hermes_dir = self.training_dir / "from-hermes"
        self.results_dir = self.training_dir / "results"
        self.twins_dir = self.training_dir / "twins"
        self.queue_file = self.training_dir / "slice_queue.json"
        self.vip_queue = []    # VIP 切片
        self.normal_queue = [] # 普通切片
        self.stats = {
            "vip_processed": 0,
            "normal_processed": 0,
            "vip_pending": 0,
            "normal_pending": 0,
            "last_run": None
        }
    
    def classify_task(self, filename):
        """根据文件名分类任务优先级"""
        name = filename.lower()
        
        # VIP 切片：围棋对局、紧急任务
        if "go_match" in name or "match" in name:
            return "vip", TaskPriority.CRITICAL
        if "critical" in name or "urgent" in name:
            return "vip", TaskPriority.CRITICAL
        if "day" in name and "redistribute" in name:
            return "vip", TaskPriority.HIGH
        if "notification" in name:
            return "vip", TaskPriority.HIGH
        
        # 普通切片：日常训练、CC同步
        if "cc" in name or "ack" in name or "sync" in name:
            return "normal", TaskPriority.LOW
        if "reminder" in name:
            return "normal", TaskPriority.LOW
        if "day" in name:
            return "normal", TaskPriority.MEDIUM
        
        # 默认普通
        return "normal", TaskPriority.MEDIUM
    
    def scan_messages(self):
        """扫描 from-hermes/ 目录，分类到 VIP/普通切片"""
        self.vip_queue = []
        self.normal_queue = []
        
        if not self.from_hermes_dir.exists():
            return
        
        for f in sorted(self.from_hermes_dir.iterdir()):
            if f.is_file() and f.suffix == ".json":
                slice_type, priority = self.classify_task(f.name)
                task = {
                    "filename": f.name,
                    "path": str(f),
                    "priority": priority,
                    "slice": slice_type,
                    "size": f.stat().st_size,
                    "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                }
                
                if slice_type == "vip":
                    self.vip_queue.append(task)
                else:
                    self.normal_queue.append(task)
        
        self.stats["vip_pending"] = len(self.vip_queue)
        self.stats["normal_pending"] = len(self.normal_queue)
    
    def get_next_task(self):
        """获取下一个任务（VIP 优先）"""
        if self.vip_queue:
            return self.vip_queue.pop(0)
        if self.normal_queue:
            return self.normal_queue.pop(0)
        return None
    
    def process_task(self, task):
        """处理单个任务"""
        try:
            with open(task["path"]) as f:
                data = json.load(f)
            
            task_type = data.get("type", "unknown")
            student = data.get("student", "unknown")
            
            # 检查学生是否已读（从文件名提取学生ID）
            student_from_file = None
            for sid in ["zhuguxia", "xiaochen", "qoder", "xiaowei"]:
                if sid in task["filename"]:
                    student_from_file = sid
                    break
            
            twin_file = self.twins_dir / f"node_twin_{student_from_file or student}.json"
            if twin_file.exists():
                try:
                    with open(twin_file) as f:
                        twin = json.load(f)
                    
                    # 更新学生消息已读计数
                    twin["messages_read"] = twin.get("messages_read", 0) + 1
                    twin["last_message_read"] = datetime.now().isoformat()
                    
                    with open(twin_file, "w") as f:
                        json.dump(twin, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"  更新孪生文件失败: {e}")
            
            if task["slice"] == "vip":
                self.stats["vip_processed"] += 1
            else:
                self.stats["normal_processed"] += 1
            
            return True
        except Exception as e:
            print(f"处理任务失败 {task['filename']}: {e}")
            return False
    
    def run_once(self):
        """执行一次完整调度"""
        print(f"\n[{datetime.now().isoformat()}] 动态切片调度开始")
        
        # 1. 扫描消息
        self.scan_messages()
        print(f"  VIP切片: {len(self.vip_queue)} 个任务")
        print(f"  普通切片: {len(self.normal_queue)} 个任务")
        
        # 2. 处理任务（VIP 优先）
        processed = 0
        while True:
            task = self.get_next_task()
            if not task:
                break
            
            success = self.process_task(task)
            if success:
                processed += 1
                print(f"  ✅ 处理: {task['filename']} ({task['slice']})")
        
        # 3. 保存统计
        self.stats["last_run"] = datetime.now().isoformat()
        with open(self.queue_file, "w") as f:
            json.dump(self.stats, f, indent=2)
        
        print(f"  本次处理: {processed} 个任务")
        print(f"  累计VIP: {self.stats['vip_processed']}, 普通: {self.stats['normal_processed']}")
    
    def run(self):
        """主循环 - 每30分钟执行一次"""
        print("动态切片调度器启动")
        while True:
            try:
                self.run_once()
            except Exception as e:
                print(f"调度异常: {e}")
            time.sleep(1800)  # 30分钟

if __name__ == "__main__":
    scheduler = DynamicSlicingQueue()
    scheduler.run()
