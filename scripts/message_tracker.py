#!/usr/bin/env python3
"""
消息追踪器 (message_tracker.py)
功能：记录消息发送状态，支持去重检查
作者：小龙虾-诸葛虾 🦞
日期：2026-05-17
"""

import json
import time
from pathlib import Path
from datetime import datetime

class MessageTracker:
    def __init__(self, log_dir="/home/admin/.openclaw/data/message-tracker"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.sent_log = self.log_dir / "sent.jsonl"
        
    def track_sent(self, message_id: str, content: str, recipient: str, status: str = "sent"):
        """记录消息发送状态"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'message_id': message_id,
            'content_preview': content[:100],
            'recipient': recipient,
            'status': status,
            'retry_count': 0
        }
        
        with open(self.sent_log, 'a') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"📝 已追踪消息: {message_id} -> {recipient} ({status})")
    
    def get_recent_sends(self, minutes: int = 5) -> list:
        """获取最近 N 分钟发送的消息"""
        cutoff = time.time() - (minutes * 60)
        recent = []
        
        if not self.sent_log.exists():
            return []
        
        with open(self.sent_log, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    sent_time = datetime.fromisoformat(record['timestamp']).timestamp()
                    if sent_time > cutoff:
                        recent.append(record)
                except Exception:
                    pass
        
        return recent
    
    def check_duplicate_send(self, content: str, minutes: int = 5) -> bool:
        """检查最近 N 分钟是否发送过相同内容"""
        recent = self.get_recent_sends(minutes)
        content_preview = content[:100]
        
        for record in recent:
            if record.get('content_preview') == content_preview:
                return True
        
        return False

# 命令行接口
if __name__ == "__main__":
    import sys
    
    tracker = MessageTracker()
    
    if len(sys.argv) < 2:
        print("用法: python3 message_tracker.py <command> [args...]")
        print("  track_sent <message_id> <content> <recipient> [status]")
        print("  get_recent_sends [minutes]")
        print("  check_duplicate_send <content> [minutes]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "track_sent":
        if len(sys.argv) < 5:
            print("错误: track_sent 需要 message_id, content, recipient 参数")
            sys.exit(1)
        tracker.track_sent(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "sent")
        
    elif command == "get_recent_sends":
        minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        recent = tracker.get_recent_sends(minutes)
        print(f"📊 最近 {minutes} 分钟发送了 {len(recent)} 条消息:")
        for r in recent:
            print(f"  - {r['message_id']}: {r['content_preview'][:50]}... -> {r['recipient']}")
            
    elif command == "check_duplicate_send":
        if len(sys.argv) < 3:
            print("错误: check_duplicate_send 需要 content 参数")
            sys.exit(1)
        minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        is_dup = tracker.check_duplicate_send(sys.argv[2], minutes)
        print(f"🔍 重复检查: {'✅ 重复' if is_dup else '✅ 唯一'}")
        
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
