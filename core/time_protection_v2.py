#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间保护模块 V2
确保训练任务在指定时间窗口内执行，防止被其他任务挤占

功能：
1. 检查当前时间是否在训练窗口内
2. 验证训练任务是否按时执行
3. 超时自动提醒/清理
4. 训练时间统计与报告

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
TRAINING_DIR = REPO_ROOT / ".shared" / "training" / "go"
STATUS_FILE = TRAINING_DIR / "status.json"


class TimeProtectionV2:
    """时间保护 V2"""
    
    # 训练时间窗口配置
    TRAINING_WINDOWS = {
        "morning": {"start": "07:00", "end": "09:00", "description": "早晨训练窗口"},
        "afternoon": {"start": "14:00", "end": "16:00", "description": "下午训练窗口"},
        "evening": {"start": "20:00", "end": "22:00", "description": "晚间训练窗口"},
    }
    
    # 任务超时配置
    TIMEOUT_CONFIG = {
        "problem_solving": {"hours": 4, "description": "解题超时时间"},
        "game_play": {"hours": 2, "description": "对局超时时间"},
        "review": {"hours": 6, "description": "复盘超时时间"},
    }
    
    def __init__(self):
        self.training_dir = TRAINING_DIR
        self.status_file = STATUS_FILE
        
    def check_training_window(self) -> Dict:
        """检查当前时间是否在训练窗口内"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        active_window = None
        for window_name, window_config in self.TRAINING_WINDOWS.items():
            if window_config["start"] <= current_time <= window_config["end"]:
                active_window = window_name
                break
                
        return {
            "current_time": current_time,
            "in_training_window": active_window is not None,
            "active_window": active_window,
            "window_description": self.TRAINING_WINDOWS.get(active_window, {}).get("description", "无"),
            "all_windows": self.TRAINING_WINDOWS,
        }
        
    def check_task_timeout(self, task_file: Path) -> Dict:
        """检查任务是否超时"""
        if not task_file.exists():
            return {"exists": False, "timeout": False}
            
        # 获取文件修改时间
        mtime = os.path.getmtime(task_file)
        task_time = datetime.fromtimestamp(mtime)
        now = datetime.now()
        age_hours = (now - task_time).total_seconds() / 3600
        
        # 判断是否超时
        timeout = False
        timeout_type = None
        
        for task_type, config in self.TIMEOUT_CONFIG.items():
            if age_hours > config["hours"]:
                timeout = True
                timeout_type = task_type
                break
                
        return {
            "exists": True,
            "file": task_file.name,
            "task_time": task_time.isoformat(),
            "age_hours": round(age_hours, 2),
            "timeout": timeout,
            "timeout_type": timeout_type,
        }
        
    def check_all_tasks_timeout(self) -> Dict:
        """检查所有任务超时状态"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": 0,
            "timeout_tasks": 0,
            "tasks": [],
        }
        
        # 检查 inbox 中的任务
        queue_dir = REPO_ROOT / "lobster-data" / "messages" / "queue"
        for student_id in ["xiaochen", "zhuguxia", "qoder"]:
            inbox_dir = queue_dir / student_id / "inbox"
            if inbox_dir.exists():
                for task_file in inbox_dir.glob("*.json"):
                    task_result = self.check_task_timeout(task_file)
                    task_result["student_id"] = student_id
                    results["tasks"].append(task_result)
                    results["total_tasks"] += 1
                    if task_result.get("timeout"):
                        results["timeout_tasks"] += 1
                        
        return results
        
    def generate_time_report(self) -> Dict:
        """生成训练时间报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "training_window": self.check_training_window(),
            "task_timeout": self.check_all_tasks_timeout(),
            "recommendations": [],
        }
        
        # 生成建议
        window = report["training_window"]
        if not window["in_training_window"]:
            report["recommendations"].append("⚠️ 当前不在训练窗口内，建议等待下一个窗口")
            
        timeout_stats = report["task_timeout"]
        if timeout_stats["timeout_tasks"] > 0:
            report["recommendations"].append(
                f"⚠️ 有 {timeout_stats['timeout_tasks']} 个任务超时，建议清理或催办"
            )
            
        if not report["recommendations"]:
            report["recommendations"].append("✅ 训练时间状态正常")
            
        return report
        
    def check_status(self):
        """检查并显示状态"""
        print("=== 时间保护 V2 状态检查 ===\n")
        
        # 1. 训练窗口检查
        window = self.check_training_window()
        print(f"🕐 当前时间：{window['current_time']}")
        print(f"📅 训练窗口：{'✅ 在窗口内' if window['in_training_window'] else '❌ 不在窗口内'}")
        if window["active_window"]:
            print(f"   窗口：{window['window_description']}")
        print()
        
        # 2. 任务超时检查
        timeout = self.check_all_tasks_timeout()
        print(f"📊 任务统计：")
        print(f"   总任务：{timeout['total_tasks']}")
        print(f"   超时任务：{timeout['timeout_tasks']}")
        
        if timeout["timeout_tasks"] > 0:
            print(f"\n   ⚠️ 超时任务详情：")
            for task in timeout["tasks"]:
                if task.get("timeout"):
                    print(f"   - {task['student_id']}/{task['file']}: 超时 {task['age_hours']:.1f}小时 ({task['timeout_type']})")
        print()
        
        # 3. 建议
        report = self.generate_time_report()
        print(f"💡 建议：")
        for rec in report["recommendations"]:
            print(f"   {rec}")
            
        return report


def main():
    """主函数"""
    protector = TimeProtectionV2()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            # 检查状态
            protector.check_status()
            
        elif command == "window":
            # 检查训练窗口
            window = protector.check_training_window()
            print("=== 训练窗口检查 ===")
            print(f"当前时间：{window['current_time']}")
            print(f"在窗口内：{window['in_training_window']}")
            if window["active_window"]:
                print(f"窗口：{window['window_description']}")
                
        elif command == "timeout":
            # 检查任务超时
            timeout = protector.check_all_tasks_timeout()
            print("=== 任务超时检查 ===")
            print(f"总任务：{timeout['total_tasks']}")
            print(f"超时任务：{timeout['timeout_tasks']}")
            
        elif command == "report":
            # 生成报告
            report = protector.generate_time_report()
            print("=== 训练时间报告 ===")
            print(json.dumps(report, indent=2, ensure_ascii=False))
            
        else:
            print(f"未知命令：{command}")
            print("可用命令：check, window, timeout, report")
    else:
        print("=== 时间保护 V2 ===")
        print("用法：")
        print("  python3 time_protection_v2.py check")
        print("  python3 time_protection_v2.py window")
        print("  python3 time_protection_v2.py timeout")
        print("  python3 time_protection_v2.py report")


if __name__ == "__main__":
    main()
