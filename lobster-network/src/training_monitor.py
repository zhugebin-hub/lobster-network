#!/usr/bin/env python3
"""
训练监控告警系统
增强功能：
- 实时训练活动监控
- 自动告警触发
- 告警历史追踪
- 通知机制（支持多种渠道）
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class TrainingMonitor:
    """训练监控告警系统"""
    
    def __init__(self, workspace_dir: str = "workspace", alert_threshold_hours: int = 24):
        self.workspace_dir = Path(workspace_dir) / "monitoring"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.alert_threshold = alert_threshold_hours * 3600  # 转换为秒
        self.alerts: List[Dict] = []
        self.alert_history_file = self.workspace_dir / "alert_history.json"
        self.monitoring_active = False
        self._monitor_thread = None
        
        # 加载历史告警
        self._load_alert_history()
        
        print(f"[TrainingMonitor] 初始化完成，告警阈值：{alert_threshold_hours} 小时")
    
    def start_monitoring(self, interval_seconds: int = 300):
        """启动监控"""
        if self.monitoring_active:
            print("[TrainingMonitor] 监控已在运行")
            return
        
        self.monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval_seconds,),
            daemon=True
        )
        self._monitor_thread.start()
        print(f"[TrainingMonitor] 监控已启动，间隔：{interval_seconds} 秒")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        print("[TrainingMonitor] 监控已停止")
    
    def check_training_activity(self, agent_id: str, last_activity_time: float) -> Optional[Dict]:
        """检查训练活动"""
        now = time.time()
        elapsed = now - last_activity_time
        
        if elapsed > self.alert_threshold:
            alert = {
                "agent_id": agent_id,
                "type": "training_stagnation",
                "elapsed_hours": elapsed / 3600,
                "threshold_hours": self.alert_threshold / 3600,
                "message": f"学员 {agent_id} 训练停滞 {elapsed/3600:.1f} 小时（阈值：{self.alert_threshold/3600} 小时）",
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "severity": "high" if elapsed > self.alert_threshold * 2 else "medium"
            }
            
            self.alerts.append(alert)
            self._save_alert(alert)
            self._notify_alert(alert)
            
            return alert
        
        return None
    
    def get_active_alerts(self) -> List[Dict]:
        """获取活跃告警"""
        return [a for a in self.alerts if not a.get("resolved", False)]
    
    def resolve_alert(self, alert_id: str):
        """解决告警"""
        for alert in self.alerts:
            if alert.get("id") == alert_id:
                alert["resolved"] = True
                alert["resolved_at"] = time.time()
                self._save_alert_history()
                print(f"[TrainingMonitor] 告警已解决：{alert_id}")
                return True
        return False
    
    def get_monitoring_status(self) -> Dict:
        """获取监控状态"""
        return {
            "monitoring_active": self.monitoring_active,
            "total_alerts": len(self.alerts),
            "active_alerts": len(self.get_active_alerts()),
            "alert_threshold_hours": self.alert_threshold / 3600,
            "last_check": self.alerts[-1].get("timestamp") if self.alerts else None
        }
    
    def _monitoring_loop(self, interval_seconds: int):
        """监控循环"""
        while self.monitoring_active:
            try:
                self._check_all_agents()
            except Exception as e:
                print(f"[TrainingMonitor] 监控循环错误：{e}")
            time.sleep(interval_seconds)
    
    def _check_all_agents(self):
        """检查所有学员"""
        # 这里应该从实际数据源获取学员活动信息
        # 目前使用模拟数据
        mock_agents = {
            "xiaochen": time.time() - 5 * 24 * 3600,  # 5 天前
            "zhuguxia": time.time() - 7 * 24 * 3600,   # 7 天前
            "qoder": time.time() - 3 * 24 * 3600       # 3 天前
        }
        
        for agent_id, last_activity in mock_agents.items():
            self.check_training_activity(agent_id, last_activity)
    
    def _notify_alert(self, alert: Dict):
        """通知告警"""
        # 这里可以集成多种通知渠道
        # 目前仅打印到控制台
        print(f"🚨 [告警] {alert['message']}")
        
        # 未来可扩展：
        # - 发送邮件
        # - 发送钉钉/企业微信消息
        # - 写入系统日志
    
    def _save_alert(self, alert: Dict):
        """保存告警"""
        alert["id"] = f"alert_{int(time.time())}_{len(self.alerts)}"
        self._save_alert_history()
    
    def _save_alert_history(self):
        """保存告警历史"""
        try:
            with open(self.alert_history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "alerts": self.alerts,
                    "last_update": time.time()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[TrainingMonitor] 保存告警历史失败：{e}")
    
    def _load_alert_history(self):
        """加载告警历史"""
        if self.alert_history_file.exists():
            try:
                with open(self.alert_history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alerts = data.get("alerts", [])
            except Exception as e:
                print(f"[TrainingMonitor] 加载告警历史失败：{e}")


# 测试代码
if __name__ == "__main__":
    print("=== 测试训练监控告警系统 ===")
    
    monitor = TrainingMonitor(alert_threshold_hours=24)
    
    # 测试告警触发
    alert = monitor.check_training_activity("test_agent", time.time() - 25 * 3600)
    if alert:
        print(f"触发告警：{alert['message']}")
    
    # 测试正常活动
    normal = monitor.check_training_activity("active_agent", time.time() - 1 * 3600)
    print(f"正常活动：{normal is None}")
    
    # 获取监控状态
    status = monitor.get_monitoring_status()
    print(f"监控状态：{status}")
    
    print("✅ 测试完成")