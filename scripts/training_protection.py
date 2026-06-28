#!/usr/bin/env python3
"""
小龙虾网络 训练时间保护机制
功能：确保训练任务在保护窗口内优先执行，暂停基础设施任务
"""

import json
import os
from datetime import datetime, time
from pathlib import Path

class TrainingProtectionManager:
    """训练时间保护管理器"""
    
    def __init__(self):
        self.config = {
            "protection_windows": [
                {"start": "09:00", "end": "11:00", "priority": "high"},   # 上午训练窗口
                {"start": "14:00", "end": "16:00", "priority": "high"},   # 下午训练窗口
                {"start": "19:00", "end": "21:00", "priority": "medium"}, # 晚上训练窗口
            ],
            "suspended_tasks": [
                "cc_route_patrol",      # CC路由巡检
                "sync_v3",              # V3.0同步
                "infrastructure_update", # 基础设施更新
                "batch_ack",            # 批量ACK
            ],
            "protected_tasks": [
                "go_training",          # 围棋训练
                "network_protocol",     # 网络协议学习
                "stock_prediction",     # 炒股预测
                "assessment",           # 评估测试
            ]
        }
    
    def is_in_protection_window(self):
        """检查当前时间是否在保护窗口内"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        for window in self.config["protection_windows"]:
            if window["start"] <= current_time <= window["end"]:
                return True, window["priority"]
        
        return False, None
    
    def should_suspend_task(self, task_name):
        """判断任务是否应该被暂停"""
        in_window, priority = self.is_in_protection_window()
        
        if not in_window:
            return False
        
        # 高优先级窗口暂停所有非保护任务
        if priority == "high":
            return task_name in self.config["suspended_tasks"]
        
        # 中优先级窗口只暂停低优先级任务
        elif priority == "medium":
            return task_name in ["cc_route_patrol", "batch_ack"]
        
        return False
    
    def get_training_schedule(self):
        """获取训练日程表"""
        schedule = {
            "daily": {
                "morning": {"time": "09:00-11:00", "tasks": ["go_training", "assessment"]},
                "afternoon": {"time": "14:00-16:00", "tasks": ["network_protocol", "stock_prediction"]},
                "evening": {"time": "19:00-21:00", "tasks": ["go_training", "review"]},
            },
            "weekly": {
                "monday_friday": ["go_training", "network_protocol"],
                "saturday": ["assessment", "review"],
                "sunday": ["free_training", "exploration"],
            }
        }
        return schedule
    
    def generate_protection_report(self):
        """生成保护机制报告"""
        in_window, priority = self.is_in_protection_window()
        schedule = self.get_training_schedule()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_status": "保护中" if in_window else "正常",
            "priority": priority or "无",
            "schedule": schedule,
            "suspended_tasks": self.config["suspended_tasks"] if in_window else [],
            "protected_tasks": self.config["protected_tasks"],
        }
        
        return report

def main():
    """主函数"""
    manager = TrainingProtectionManager()
    report = manager.generate_protection_report()
    
    print("🛡️ 训练时间保护机制报告")
    print("=" * 50)
    print(f"当前状态: {report['current_status']}")
    print(f"优先级: {report['priority']}")
    print(f"暂停任务: {', '.join(report['suspended_tasks']) if report['suspended_tasks'] else '无'}")
    print("\n📅 训练日程:")
    for period, info in report['schedule']['daily'].items():
        print(f"  {period}: {info['time']} - {', '.join(info['tasks'])}")
    
    # 保存报告
    report_path = Path("/home/admin/lobster-network/docs/training_protection_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 报告已保存: {report_path}")

if __name__ == "__main__":
    main()
