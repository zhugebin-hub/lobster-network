#!/usr/bin/env python3
"""诸葛斌 V4.0 CC消息ACK处理脚本"""

import json
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CC_TRACKING = os.path.join(PROJECT_ROOT, ".shared/messages/cc_tracking.json")
QUEUE_DIR = os.path.join(PROJECT_ROOT, ".shared/messages/queue")

def now_iso():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f+08:00")

def send_ack(tracking_id, msg_id, from_node):
    """发送ACK回执到诸葛马收件箱"""
    ack = {
        "type": "cc_ack",
        "ack_id": f"ack-zhugebin-{tracking_id}",
        "tracking_id": tracking_id,
        "original_msg_id": msg_id,
        "from": "zhugebin-001",
        "to": from_node,
        "status": "acknowledged",
        "message": f"诸葛斌已收到并确认消息: {msg_id}",
        "timestamp": now_iso(),
    }
    
    # 写入诸葛马收件箱
    target_inbox = os.path.join(QUEUE_DIR, from_node, "inbox")
    os.makedirs(target_inbox, exist_ok=True)
    
    ack_file = os.path.join(target_inbox, f"ack-zhugebin-{tracking_id}.json")
    with open(ack_file, "w") as f:
        json.dump(ack, f, ensure_ascii=False, indent=2)
    
    # 同时记录到自己的sent目录
    sent_dir = os.path.join(QUEUE_DIR, "zhugebin-001", "sent")
    os.makedirs(sent_dir, exist_ok=True)
    with open(os.path.join(sent_dir, f"ack-zhugebin-{tracking_id}.json"), "w") as f:
        json.dump(ack, f, ensure_ascii=False, indent=2)
    
    print(f"  ✅ ACK -> {from_node}: {tracking_id}")
    return ack

def update_cc_tracking(tracking_id, ack_node):
    """更新cc_tracking.json"""
    with open(CC_TRACKING, "r") as f:
        tracking = json.load(f)
    
    found = False
    for entry in tracking.get("pending", []):
        if entry["tracking_id"] == tracking_id:
            entry["acks_received"][ack_node] = {
                "timestamp": now_iso(),
                "status": "acknowledged"
            }
            if ack_node in entry.get("acks_pending", []):
                entry["acks_pending"].remove(ack_node)
            found = True
            break
    
    if not found:
        # Also check completed
        for entry in tracking.get("completed", []):
            if entry["tracking_id"] == tracking_id:
                entry["acks_received"][ack_node] = {
                    "timestamp": now_iso(),
                    "status": "acknowledged"
                }
                if ack_node in entry.get("acks_pending", []):
                    entry["acks_pending"].remove(ack_node)
                found = True
                break
    
    if found:
        with open(CC_TRACKING, "w") as f:
            json.dump(tracking, f, ensure_ascii=False, indent=2)
    
    return found

def main():
    print("🦞 诸葛斌 CC消息ACK处理")
    print("=" * 50)
    
    # 列出当前所有pending消息
    with open(CC_TRACKING, "r") as f:
        tracking = json.load(f)
    
    pending = tracking.get("pending", [])
    print(f"\n📋 当前 {len(pending)} 条待ACK消息\n")
    
    ack_count = 0
    
    for entry in pending:
        tracking_id = entry["tracking_id"]
        msg_id = entry["msg_id"]
        from_node = entry["from"]
        subject = entry.get("subject", "无主题")
        
        print(f"  📨 [{tracking_id}] {subject}")
        print(f"      发送者: {from_node} | 目标: {', '.join(entry.get('targets', []))}")
        
        # 诸葛斌对每条围棋/训练/验证相关消息都发送ACK
        is_relevant = any(kw in subject.lower() for kw in [
            "围棋", "go", "match", "训练", "verify", "验证", "v4.0", "同步", "同步完成"
        ])
        
        if is_relevant or from_node == "zhugema":
            send_ack(tracking_id, msg_id, from_node)
            update_cc_tracking(tracking_id, "zhugebin-001")
            ack_count += 1
        else:
            print(f"      ⏭️ 跳过（非相关消息）")
    
    print(f"\n✅ 完成: {ack_count} 条ACK已发送")
    print(f"📁 ACK记录: {QUEUE_DIR}/zhugebin-001/sent/")
    
    # 生成ACK报告
    report = {
        "report_id": f"zhugebin-ack-report-{int(datetime.now().timestamp())}",
        "node": "zhugebin-001",
        "acks_processed": ack_count,
        "timestamp": now_iso(),
        "status": "ACK处理完成"
    }
    
    routing_dir = os.path.join(PROJECT_ROOT, ".shared/messages/routing")
    os.makedirs(routing_dir, exist_ok=True)
    with open(os.path.join(routing_dir, f"zhugebin_ack_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"), "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    return ack_count

if __name__ == "__main__":
    main()
