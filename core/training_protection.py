#!/usr/bin/env python3
"""
小龙虾网络V3.0 - 训练时间保护机制
功能: 保护训练窗口，避免基础设施任务挤占
作者: 诸葛马 (AI教练)
版本: 1.0
"""

import json
import os
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ============================================================
# 配置
# ============================================================

class Config:
    """时间保护配置"""
    
    # 训练窗口 (每天)
    TRAINING_WINDOWS = {
        "morning": {"start": "08:00", "end": "12:00", "priority": "high"},
        "afternoon": {"start": "14:00", "end": "18:00", "priority": "high"},
        "evening": {"start": "19:00", "end": "22:00", "priority": "medium"}
    }
    
    # 基础设施窗口
    INFRA_WINDOWS = {
        "maintenance": {"start": "00:00", "end": "06:00", "priority": "low"},
        "sync": {"start": "12:00", "end": "14:00", "priority": "low"},
        "backup": {"start": "22:00", "end": "24:00", "priority": "low"}
    }
    
    # 任务优先级
    PRIORITY_LEVELS = {
        "critical": 100,    # 紧急任务
        "high": 80,         # 训练任务
        "medium": 60,       # 评估/报告
        "low": 40,          # 基础设施
        "background": 20    # 后台任务
    }
    
    # 学员训练时间
    STUDENT_TRAINING_HOURS = {
        "xiaochen": {"daily": 4, "windows": ["morning", "afternoon"]},
        "zhuguxia": {"daily": 3, "windows": ["morning", "evening"]},
        "qoder": {"daily": 3, "windows": ["afternoon", "evening"]},
        "xiaowei": {"daily": 2, "windows": ["morning"]}
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    RESULTS_DIR = f"{SHARED_DIR}results/"
    LOG_FILE = f"{SHARED_DIR}training_protection.log"


# ============================================================
# 时间保护引擎
# ============================================================

class TimeProtectionEngine:
    """时间保护引擎"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
    
    def is_training_window(self) -> bool:
        """当前是否在训练窗口"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for window_name, window in self.config.TRAINING_WINDOWS.items():
            if window["start"] <= current_time <= window["end"]:
                return True
        
        return False
    
    def is_infra_window(self) -> bool:
        """当前是否在基础设施窗口"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for window_name, window in self.config.INFRA_WINDOWS.items():
            if window["start"] <= current_time <= window["end"]:
                return True
        
        return False
    
    def can_run_task(self, task_priority: str) -> bool:
        """判断是否可以运行任务"""
        priority = self.config.PRIORITY_LEVELS.get(task_priority, 0)
        is_training = self.is_training_window()
        is_infra = self.is_infra_window()
        
        # 训练窗口：只允许high/critical任务
        if is_training:
            return priority >= self.config.PRIORITY_LEVELS["high"]
        
        # 基础设施窗口：允许所有任务
        if is_infra:
            return True
        
        # 其他时间：允许medium及以上
        return priority >= self.config.PRIORITY_LEVELS["medium"]
    
    def get_available_windows(self, student_id: str) -> List[Dict]:
        """获取学员可用训练窗口"""
        student_config = self.config.STUDENT_TRAINING_HOURS.get(student_id)
        if not student_config:
            return []
        
        available = []
        for window_name in student_config["windows"]:
            window = self.config.TRAINING_WINDOWS.get(window_name)
            if window:
                available.append({
                    "name": window_name,
                    "start": window["start"],
                    "end": window["end"],
                    "priority": window["priority"]
                })
        
        return available
    
    def protect_training(self, student_id: str, task_type: str = "training") -> Dict:
        """保护学员训练"""
        student_config = self.config.STUDENT_TRAINING_HOURS.get(student_id)
        if not student_config:
            return {"status": "unknown_student", "message": f"学员{student_id}未配置"}
        
        # 检查当前时间
        is_training = self.is_training_window()
        is_infra = self.is_infra_window()
        
        # 获取可用窗口
        available = self.get_available_windows(student_id)
        
        # 检查任务优先级
        can_run = self.can_run_task("high" if task_type == "training" else "medium")
        
        result = {
            "student_id": student_id,
            "task_type": task_type,
            "is_training_window": is_training,
            "is_infra_window": is_infra,
            "can_run": can_run,
            "available_windows": available,
            "daily_hours": student_config["daily"],
            "timestamp": datetime.now().isoformat()
        }
        
        # 记录日志
        if can_run:
            self.logger.info(f"✅ 学员{student_id} {task_type}任务允许运行")
        else:
            self.logger.warn(f"🚫 学员{student_id} {task_type}任务被保护机制阻止")
        
        return result


# ============================================================
# 任务调度器
# ============================================================

class TaskScheduler:
    """任务调度器 - 基于时间保护"""
    
    def __init__(self):
        self.protection = TimeProtectionEngine()
        self.logger = Logger()
    
    def schedule_training(self, student_id: str, task: Dict) -> Dict:
        """调度训练任务"""
        # 检查保护机制
        protection = self.protection.protect_training(student_id, "training")
        
        if not protection["can_run"]:
            return {
                "status": "blocked",
                "reason": "训练时间保护机制",
                "protection": protection
            }
        
        # 调度任务
        return {
            "status": "scheduled",
            "student_id": student_id,
            "task": task,
            "protection": protection
        }
    
    def schedule_infra(self, task_type: str) -> Dict:
        """调度基础设施任务"""
        # 检查是否在基础设施窗口
        is_infra = self.protection.is_infra_window()
        is_training = self.protection.is_training_window()
        
        if is_training:
            return {
                "status": "blocked",
                "reason": "训练窗口，基础设施任务暂停",
                "is_training_window": True
            }
        
        if not is_infra:
            return {
                "status": "deferred",
                "reason": "非基础设施窗口，任务延后",
                "next_infra_window": self.get_next_infra_window()
            }
        
        return {
            "status": "scheduled",
            "task_type": task_type
        }
    
    def get_next_infra_window(self) -> Dict:
        """获取下一个基础设施窗口"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for window_name, window in self.config.INFRA_WINDOWS.items():
            if window["start"] > current_time:
                return {
                    "name": window_name,
                    "start": window["start"],
                    "end": window["end"]
                }
        
        # 返回明天的第一个窗口
        return {
            "name": "maintenance",
            "start": "00:00",
            "end": "06:00",
            "date": "明天"
        }


# ============================================================
# 日志模块
# ============================================================

class Logger:
    """日志模块"""
    
    def __init__(self, log_file: str = Config.LOG_FILE):
        self.log_file = log_file
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    def info(self, message: str):
        self._log("INFO", message)
    
    def warn(self, message: str):
        self._log("WARN", message)
    
    def error(self, message: str):
        self._log("ERROR", message)
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}\n"
        
        print(log_line.strip())
        
        with open(self.log_file, "a") as f:
            f.write(log_line)


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="小龙虾网络V3.0 - 训练时间保护机制")
    parser.add_argument("action", choices=["check", "protect", "schedule", "status"],
                       help="操作: check(检查) | protect(保护) | schedule(调度) | status(状态)")
    parser.add_argument("--student", type=str, help="学员ID")
    parser.add_argument("--task", type=str, help="任务类型")
    
    args = parser.parse_args()
    
    protection = TimeProtectionEngine()
    scheduler = TaskScheduler()
    
    if args.action == "check":
        # 检查当前时间
        is_training = protection.is_training_window()
        is_infra = protection.is_infra_window()
        
        print(f"当前时间: {datetime.now().strftime('%H:%M')}")
        print(f"训练窗口: {'✅ 是' if is_training else '❌ 否'}")
        print(f"基础设施窗口: {'✅ 是' if is_infra else '❌ 否'}")
    
    elif args.action == "protect":
        # 保护学员训练
        if not args.student:
            print("错误: 需要指定 --student")
            return
        
        result = protection.protect_training(args.student, args.task or "training")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "schedule":
        # 调度任务
        if args.student:
            result = scheduler.schedule_training(args.student, {"type": args.task or "training"})
        else:
            result = scheduler.schedule_infra(args.task or "maintenance")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "status":
        # 系统状态
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        status = {
            "current_time": current_time,
            "is_training_window": protection.is_training_window(),
            "is_infra_window": protection.is_infra_window(),
            "students": {}
        }
        
        for student_id in Config.STUDENT_TRAINING_HOURS:
            windows = protection.get_available_windows(student_id)
            status["students"][student_id] = {
                "windows": windows,
                "daily_hours": Config.STUDENT_TRAINING_HOURS[student_id]["daily"]
            }
        
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
