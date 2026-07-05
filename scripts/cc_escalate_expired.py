#!/usr/bin/env python3
"""
CC消息超时自动升级脚本
检查cc_tracking.json中超过ack_deadline的消息，自动从pending移至escalated
"""
import os
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent)
TRACKING_FILE = f'{BASE_DIR}/.shared/messages/cc_tracking.json'

def parse_iso(s):
    """解析ISO时间字符串（兼容带时区和不带时区）"""
    s_clean = s.replace("Z", "").split("+")[0]
    fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in s_clean else "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(s_clean, fmt)

def main():
    if not os.path.exists(TRACKING_FILE):
        print(f"Tracking file not found: {TRACKING_FILE}")
        return
    
    with open(TRACKING_FILE) as f:
        tracking = json.load(f)
    
    now = datetime.now()
    pending = tracking.get('pending', [])
    escalated = tracking.get('escalated', [])
    completed = tracking.get('completed', [])
    
    still_pending = []
    newly_escalated = []
    
    for entry in pending:
        deadline_str = entry.get('ack_deadline', '')
        if not deadline_str:
            still_pending.append(entry)
            continue
        
        try:
            deadline = parse_iso(deadline_str)
            if now > deadline:
                # 超时，升级
                entry['escalated_at'] = now.isoformat()
                entry['escalation_reason'] = f"ACK超时: {len(entry.get('acks_pending', []))} 个节点未确认"
                newly_escalated.append(entry)
            else:
                still_pending.append(entry)
        except (ValueError, TypeError):
            still_pending.append(entry)
    
    tracking['pending'] = still_pending
    tracking['escalated'] = escalated + newly_escalated
    
    # 原子写入
    tmp_path = TRACKING_FILE + '.tmp'
    with open(tmp_path, 'w') as f:
        json.dump(tracking, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, TRACKING_FILE)
    
    print(f"📊 CC消息超时检查完成:")
    print(f"  Pending: {len(still_pending)}")
    print(f"  Completed: {len(completed)}")
    print(f"  Escalated: {len(tracking['escalated'])} (新增 {len(newly_escalated)})")
    
    if newly_escalated:
        print(f"\n⚠️ 新升级的超时消息:")
        for entry in newly_escalated:
            print(f"  - {entry['msg_id']}: {entry['subject']}")
            print(f"    未确认节点: {entry.get('acks_pending', [])}")

if __name__ == '__main__':
    main()
