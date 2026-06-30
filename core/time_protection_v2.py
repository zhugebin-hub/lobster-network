#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V4.0 - 训练时间保护守护进程
功能：
1. 持续监控时间窗口，训练窗口自动阻止基础设施任务
2. 学员训练前自动检查时间保护
3. 违规任务自动拦截并通知
4. 支持强制模式（训练窗口完全禁止非训练任务）

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v2.0
"""

import json
import os
import time
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# ============================================================
# 配置
# ============================================================

class Config:
    """时间保护配置 v2.0"""
    
    # 训练窗口 (每天) - 强制保护
    TRAINING_WINDOWS = [
        {"start": 8, "end": 12, "name": "上午训练", "priority": "critical"},   # 08:00-12:00
        {"start": 14, "end": 18, "name": "下午训练", "priority": "critical"},  # 14:00-18:00
        {"start": 19, "end": 22, "name": "晚上训练", "priority": "high"},      # 19:00-22:00
    ]
    
    # 基础设施窗口
    INFRA_WINDOWS = [
        {"start": 0, "end": 8, "name": "深夜/清晨维护", "priority": "low"},      # 00:00-08:00
        {"start": 12, "end": 14, "name": "午间同步", "priority": "medium"},    # 12:00-14:00
        {"start": 22, "end": 24, "name": "晚间备份", "priority": "low"},       # 22:00-24:00
    ]
    
    # 任务优先级阈值
    PRIORITY_LEVELS = {
        "critical": 100,  # 紧急任务（永远允许）
        "training": 80,   # 训练任务
        "assessment": 60, # 评估/报告
        "infra": 40,      # 基础设施
        "background": 20, # 后台任务
    }
    
    # 学员训练时间
    STUDENTS = {
        "xiaochen": {"name": "小陈", "daily_hours": 4, "windows": [0, 1]},     # 上午+下午
        "zhuguxia": {"name": "诸葛虾", "daily_hours": 3, "windows": [0, 2]},   # 上午+晚上
        "qoder": {"name": "qoder", "daily_hours": 3, "windows": [1, 2]},       # 下午+晚上
        "xiaowei": {"name": "小薇", "daily_hours": 2, "windows": [0]},          # 仅上午
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    STATE_FILE = f"{SHARED_DIR}time_protection_state.json"
    LOG_FILE = f"{SHARED_DIR}time_protection_v2.log"
    BLOCK_FILE = f"{SHARED_DIR}blocked_tasks.json"  # 被拦截任务记录
    
    # 守护进程配置
    CHECK_INTERVAL = 60  # 每分钟检查一次
    DAEMON_PID_FILE = "/tmp/time_protection_v2.pid"


# ============================================================
# 时间保护引擎 v2.0
# ============================================================

class TimeProtectionEngineV2:
    """增强版时间保护引擎"""
    
    def __init__(self):
        self.config = Config()
        self._init_dirs()
        self._init_log()
    
    def _init_dirs(self):
        os.makedirs(os.path.dirname(self.config.SHARED_DIR), exist_ok=True)
    
    def _init_log(self):
        os.makedirs(os.path.dirname(self.config.LOG_FILE), exist_ok=True)
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)
        try:
            with open(self.config.LOG_FILE, "a") as f:
                f.write(log_line + "\n")
        except:
            pass
    
    def get_current_hour(self) -> int:
        """获取当前小时"""
        return datetime.now().hour
    
    def get_current_window(self) -> Optional[Dict]:
        """获取当前时间窗口"""
        current_hour = self.get_current_hour()
        
        # 检查训练窗口
        for window in self.config.TRAINING_WINDOWS:
            if window["start"] <= current_hour < window["end"]:
                return {
                    "type": "training",
                    "name": window["name"],
                    "priority": window["priority"],
                    "start": window["start"],
                    "end": window["end"],
                }
        
        # 检查基础设施窗口
        for window in self.config.INFRA_WINDOWS:
            if window["start"] <= current_hour < window["end"]:
                return {
                    "type": "infra",
                    "name": window["name"],
                    "priority": window["priority"],
                    "start": window["start"],
                    "end": window["end"],
                }
        
        return {"type": "unknown", "name": "未知时段", "priority": "low"}
    
    def can_run_task(self, task_type: str, task_priority: str = "infra") -> Dict:
        """
        判断是否可以运行任务（增强版）
        返回: {"allowed": bool, "reason": str, "window": dict, "next_allowed": str}
        """
        current_window = self.get_current_window()
        priority = self.config.PRIORITY_LEVELS.get(task_priority, 40)
        
        # 紧急任务永远允许
        if priority >= self.config.PRIORITY_LEVELS["critical"]:
            return {
                "allowed": True,
                "reason": "紧急任务，不受时间保护限制",
                "window": current_window,
                "next_allowed": "立即",
            }
        
        if current_window["type"] == "training":
            # 训练窗口：只允许训练任务和高优先级任务
            if task_type == "training" or priority >= self.config.PRIORITY_LEVELS["training"]:
                return {
                    "allowed": True,
                    "reason": f"训练窗口（{current_window['name']}），允许训练任务",
                    "window": current_window,
                    "next_allowed": "立即",
                }
            else:
                # 计算下一个允许窗口
                next_allowed = self._get_next_allowed_window(task_type)
                return {
                    "allowed": False,
                    "reason": f"训练窗口（{current_window['name']}），禁止{task_type}任务",
                    "window": current_window,
                    "next_allowed": next_allowed,
                }
        
        elif current_window["type"] == "infra":
            # 基础设施窗口：允许所有任务
            return {
                "allowed": True,
                "reason": f"基础设施窗口（{current_window['name']}），允许所有任务",
                "window": current_window,
                "next_allowed": "立即",
            }
        
        else:
            # 未知时段：允许medium及以上
            if priority >= self.config.PRIORITY_LEVELS["assessment"]:
                return {
                    "allowed": True,
                    "reason": "非训练/非基础设施时段，允许中优先级以上任务",
                    "window": current_window,
                    "next_allowed": "立即",
                }
            else:
                return {
                    "allowed": False,
                    "reason": "非训练/非基础设施时段，禁止低优先级任务",
                    "window": current_window,
                    "next_allowed": self._get_next_allowed_window(task_type),
                }
    
    def _get_next_allowed_window(self, task_type: str) -> str:
        """获取下一个允许运行任务的时间窗口"""
        current_hour = self.get_current_hour()
        
        if task_type == "training":
            # 训练任务：找下一个训练窗口
            for window in self.config.TRAINING_WINDOWS:
                if window["start"] > current_hour:
                    return f"今天 {window['start']:02d}:00 ({window['name']})"
            # 明天第一个训练窗口
            first = self.config.TRAINING_WINDOWS[0]
            return f"明天 {first['start']:02d}:00 ({first['name']})"
        else:
            # 基础设施任务：找下一个基础设施窗口
            for window in self.config.INFRA_WINDOWS:
                if window["start"] > current_hour:
                    return f"今天 {window['start']:02d}:00 ({window['name']})"
            first = self.config.INFRA_WINDOWS[0]
            return f"明天 {first['start']:02d}:00 ({first['name']})"
    
    def get_student_training_status(self, student_id: str) -> Dict:
        """获取学员当前训练状态"""
        student = self.config.STUDENTS.get(student_id)
        if not student:
            return {"error": f"学员{student_id}未配置"}
        
        current_window = self.get_current_window()
        can_train = current_window["type"] == "training"
        
        # 计算今日剩余训练时间
        trained_hours = 0
        if current_window["type"] == "training":
            current_hour = self.get_current_hour()
            for wi in student["windows"]:
                window = self.config.TRAINING_WINDOWS[wi]
                if window["start"] <= current_hour < window["end"]:
                    trained_hours = current_hour - window["start"]
        
        remaining = max(0, student["daily_hours"] - trained_hours)
        
        return {
            "student_id": student_id,
            "name": student["name"],
            "current_window": current_window,
            "can_train": can_train,
            "daily_target_hours": student["daily_hours"],
            "trained_hours": trained_hours,
            "remaining_hours": remaining,
            "progress_pct": round(trained_hours / student["daily_hours"] * 100, 1) if student["daily_hours"] > 0 else 0,
        }
    
    def block_task(self, task_type: str, task_priority: str, student_id: str = None) -> Dict:
        """拦截任务并记录"""
        decision = self.can_run_task(task_type, task_priority)
        
        if not decision["allowed"]:
            block_record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "task_type": task_type,
                "task_priority": task_priority,
                "student_id": student_id,
                "current_window": decision["window"],
                "reason": decision["reason"],
                "next_allowed": decision["next_allowed"],
            }
            
            # 写入拦截记录
            try:
                block_file = self.config.BLOCK_FILE
                blocks = []
                if os.path.exists(block_file):
                    with open(block_file) as f:
                        blocks = json.load(f)
                blocks.append(block_record)
                # 只保留最近100条
                blocks = blocks[-100:]
                with open(block_file, "w") as f:
                    json.dump(blocks, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            self._log("BLOCK", f"🚫 拦截任务: type={task_type}, priority={task_priority}, "
                       f"student={student_id}, reason={decision['reason']}")
        
        return decision


# ============================================================
# 守护进程
# ============================================================

class TimeProtectionDaemon:
    """时间保护守护进程"""
    
    def __init__(self):
        self.engine = TimeProtectionEngineV2()
        self.running = False
        self.config = Config()
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        self._log("INFO", f"收到信号 {signum}，停止守护进程")
        self.running = False
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def run(self):
        """运行守护进程"""
        self.running = True
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # 写入PID文件
        with open(self.config.DAEMON_PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        
        self._log("INFO", "🛡️ 训练时间保护守护进程 v2.0 启动")
        self._log("INFO", f"   检查间隔: {self.config.CHECK_INTERVAL}秒")
        self._log("INFO", f"   PID: {os.getpid()}")
        
        last_window = None
        
        while self.running:
            try:
                current_window = self.engine.get_current_window()
                
                # 窗口变化时通知
                if current_window != last_window:
                    self._log("INFO", f"🕐 时间窗口变化: {last_window} → {current_window}")
                    last_window = current_window
                    
                    # 更新状态文件
                    state = {
                        "current_window": current_window,
                        "last_check": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "students": {},
                    }
                    for student_id in self.config.STUDENTS:
                        state["students"][student_id] = self.engine.get_student_training_status(student_id)
                    
                    with open(self.config.STATE_FILE, "w") as f:
                        json.dump(state, f, ensure_ascii=False, indent=2)
                
                time.sleep(self.config.CHECK_INTERVAL)
                
            except Exception as e:
                self._log("ERROR", f"守护进程异常: {e}")
                time.sleep(5)
        
        # 清理
        try:
            os.remove(self.config.DAEMON_PID_FILE)
        except:
            pass
        self._log("INFO", "🛡️ 训练时间保护守护进程已停止")


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="训练时间保护机制 v2.0")
    parser.add_argument("action", choices=["check", "protect", "daemon", "status", "students"],
                       help="操作: check(检查) | protect(保护) | daemon(守护进程) | status(状态) | students(学员)")
    parser.add_argument("--student", type=str, help="学员ID")
    parser.add_argument("--task", type=str, default="training", help="任务类型")
    parser.add_argument("--priority", type=str, default="training", help="任务优先级")
    
    args = parser.parse_args()
    engine = TimeProtectionEngineV2()
    
    if args.action == "check":
        window = engine.get_current_window()
        print(json.dumps(window, ensure_ascii=False, indent=2))
    
    elif args.action == "protect":
        decision = engine.can_run_task(args.task, args.priority)
        print(json.dumps(decision, ensure_ascii=False, indent=2))
    
    elif args.action == "daemon":
        daemon = TimeProtectionDaemon()
        daemon.run()
    
    elif args.action == "status":
        window = engine.get_current_window()
        state_file = Config.STATE_FILE
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            print(json.dumps(state, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"current_window": window, "message": "守护进程未运行"}, 
                           ensure_ascii=False, indent=2))
    
    elif args.action == "students":
        if args.student:
            status = engine.get_student_training_status(args.student)
            print(json.dumps(status, ensure_ascii=False, indent=2))
        else:
            for student_id in Config.STUDENTS:
                status = engine.get_student_training_status(student_id)
                print(f"\n{'='*50}")
                print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
