#!/usr/bin/env python3
"""
重复消息监控脚本 (monitor_duplicates.py)
功能：检测重复发送，生成报告，触发告警
作者：小龙虾-诸葛虾 🦞
日期：2026-05-17
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

class DuplicateMonitor:
    def __init__(self, log_dir="/home/admin/.openclaw/data/message-tracker"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.sent_log = self.log_dir / "sent.jsonl"
        
    def detect_duplicates(self, window_minutes=5, threshold=3) -> list:
        """检测重复发送"""
        if not self.sent_log.exists():
            return []
        
        cutoff = time.time() - (window_minutes * 60)
        recent = []
        
        with open(self.sent_log, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    sent_time = datetime.fromisoformat(record['timestamp']).timestamp()
                    if sent_time > cutoff:
                        recent.append(record)
                except Exception:
                    pass
        
        # 按内容分组
        content_groups = {}
        for record in recent:
            preview = record.get('content_preview', '')
            if preview not in content_groups:
                content_groups[preview] = []
            content_groups[preview].append(record)
        
        # 找出重复的
        duplicates = []
        for content, records in content_groups.items():
            if len(records) >= threshold:
                duplicates.append({
                    'content': content,
                    'count': len(records),
                    'records': records,
                    'detected_at': datetime.now().isoformat()
                })
        
        return duplicates
    
    def generate_report(self) -> str:
        """生成监控报告"""
        duplicates = self.detect_duplicates()
        
        if not duplicates:
            return "✅ 无重复发送检测"
        
        report = f"🚨 检测到 {len(duplicates)} 组重复发送\n\n"
        
        for dup in duplicates:
            report += f"📝 内容：{dup['content'][:50]}...\n"
            report += f"🔢 发送次数：{dup['count']}\n"
            report += f"⏰ 检测时间：{dup['detected_at']}\n\n"
        
        return report
    
    def alert_if_needed(self):
        """触发告警"""
        duplicates = self.detect_duplicates()
        
        if duplicates:
            report = self.generate_report()
            print(report)
            
            # 可选：发送到钉钉/诸葛马
            # smart_send(report, "dingtalk:manager7550", "alert_duplicate")
            return True
        
        return False

# 定时运行
if __name__ == "__main__":
    monitor = DuplicateMonitor()
    has_duplicates = monitor.alert_if_needed()
    
    if has_duplicates:
        sys.exit(1)  # 有重复，返回非 0 状态码
    else:
        print("✅ 监控完成：无异常")
        sys.exit(0)
