#!/usr/bin/env python3
"""
🦞 小龙虾网络消息队列 V2 - 带 ACK 机制
解决文件轮询无确认的问题

架构:
  发送方 → 写入 /shared/messages/queue/{to}/inbox/{msg_id}.json
  接收方 → 读取 → 写 ACK 到 /shared/messages/queue/{to}/acked/{msg_id}.json
  发送方 → 轮询 acked/ 目录确认送达
  超时未 ACK → 自动重传（最多3次）

用法: python3 message_queue_v2.py --check   # 检查未确认消息并重传
      python3 message_queue_v2.py --send <from> <to> <type> <payload_json>
"""

import json
import os
import sys
import uuid
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

QUEUE_DIR = "/shared/messages/queue"
ACK_TIMEOUT_SECONDS = 300  # 5分钟超时
MAX_RETRIES = 3
CST = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(CST).isoformat()


def now_ts():
    return datetime.now(CST).timestamp()


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def send_message(from_node, to_node, msg_type, payload, priority="P2"):
    """发送消息（带重试计数）"""
    msg_id = f"{msg_type}-{from_node}-{int(now_ts())}-{uuid.uuid4().hex[:6]}"
    
    msg = {
        "msg_id": msg_id,
        "from": from_node,
        "to": to_node,
        "type": msg_type,
        "priority": priority,
        "payload": payload,
        "status": "pending",
        "sent_at": now_iso(),
        "retry_count": 0,
        "max_retries": MAX_RETRIES,
    }
    
    # 写入目标 inbox
    inbox_dir = os.path.join(QUEUE_DIR, to_node, "inbox")
    ensure_dir(inbox_dir)
    inbox_path = os.path.join(inbox_dir, f"{msg_id}.json")
    
    with open(inbox_path, 'w', encoding='utf-8') as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
    
    # 写入发送方 outbox（用于跟踪）
    outbox_dir = os.path.join(QUEUE_DIR, from_node, "outbox")
    ensure_dir(outbox_dir)
    outbox_path = os.path.join(outbox_dir, f"{msg_id}.json")
    
    with open(outbox_path, 'w', encoding='utf-8') as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
    
    print(f"  📤 [{msg_id}] {from_node} → {to_node} ({msg_type})")
    return msg_id


def check_acks(from_node):
    """检查发送方的未确认消息，处理 ACK 和重传"""
    outbox_dir = os.path.join(QUEUE_DIR, from_node, "outbox")
    acked_dir = os.path.join(QUEUE_DIR, from_node, "acked")
    ensure_dir(acked_dir)
    
    if not os.path.isdir(outbox_dir):
        return {"checked": 0, "acked": 0, "retried": 0, "failed": 0}
    
    stats = {"checked": 0, "acked": 0, "retried": 0, "failed": 0}
    
    for f in sorted(os.listdir(outbox_dir)):
        if not f.endswith('.json'):
            continue
        
        fp = os.path.join(outbox_dir, f)
        try:
            with open(fp, 'r') as fh:
                msg = json.load(fh)
        except Exception:
            continue
        
        stats["checked"] += 1
        msg_id = msg.get("msg_id", f)
        
        # 检查是否已 ACK
        ack_file = os.path.join(acked_dir, f)
        if os.path.exists(ack_file):
            msg["status"] = "acked"
            msg["acked_at"] = now_iso()
            with open(fp, 'w', encoding='utf-8') as fh:
                json.dump(msg, fh, ensure_ascii=False, indent=2)
            stats["acked"] += 1
            continue
        
        # 检查是否超时
        sent_at = msg.get("sent_at", "")
        try:
            sent_time = datetime.fromisoformat(sent_at.replace('+08:00', ''))
            age = (datetime.now(CST) - sent_time).total_seconds()
        except Exception:
            age = 9999
        
        if age > ACK_TIMEOUT_SECONDS:
            retries = msg.get("retry_count", 0)
            if retries >= MAX_RETRIES:
                msg["status"] = "failed"
                msg["failed_at"] = now_iso()
                with open(fp, 'w', encoding='utf-8') as fh:
                    json.dump(msg, fh, ensure_ascii=False, indent=2)
                stats["failed"] += 1
                print(f"  ❌ [{msg_id}] 超过最大重试次数 ({MAX_RETRIES})，标记为失败")
                continue
            
            # 重传：重新写入目标 inbox
            to_node = msg.get("to", "")
            if to_node:
                inbox_dir = os.path.join(QUEUE_DIR, to_node, "inbox")
                ensure_dir(inbox_dir)
                inbox_path = os.path.join(inbox_dir, f)
                
                msg["retry_count"] = retries + 1
                msg["last_retry"] = now_iso()
                msg["status"] = "retrying"
                
                with open(inbox_path, 'w', encoding='utf-8') as fh:
                    json.dump(msg, fh, ensure_ascii=False, indent=2)
                with open(fp, 'w', encoding='utf-8') as fh:
                    json.dump(msg, fh, ensure_ascii=False, indent=2)
                
                stats["retried"] += 1
                print(f"  🔄 [{msg_id}] 超时未 ACK，重传第 {retries + 1} 次 → {to_node}")
    
    return stats


def process_inbox(node_id):
    """处理接收方的 inbox，发送 ACK"""
    inbox_dir = os.path.join(QUEUE_DIR, node_id, "inbox")
    acked_dir = os.path.join(QUEUE_DIR, node_id, "acked")
    processed_dir = os.path.join(QUEUE_DIR, node_id, "processed")
    
    ensure_dir(acked_dir)
    ensure_dir(processed_dir)
    
    if not os.path.isdir(inbox_dir):
        return {"received": 0, "acked": 0}
    
    stats = {"received": 0, "acked": 0}
    
    for f in sorted(os.listdir(inbox_dir)):
        if not f.endswith('.json'):
            continue
        
        fp = os.path.join(inbox_dir, f)
        stats["received"] += 1
        
        # 发送 ACK
        ack = {
            "msg_id": f.replace('.json', ''),
            "from": node_id,
            "status": "acked",
            "acked_at": now_iso(),
        }
        
        ack_path = os.path.join(acked_dir, f)
        with open(ack_path, 'w', encoding='utf-8') as fh:
            json.dump(ack, fh, ensure_ascii=False, indent=2)
        
        # 移动到 processed
        processed_path = os.path.join(processed_dir, f)
        try:
            os.rename(fp, processed_path)
        except Exception:
            pass
        
        stats["acked"] += 1
    
    return stats


def run_check():
    """运行 ACK 检查和重传"""
    print(f"\n{'='*50}")
    print(f"🦞 消息队列 V2 ACK 检查 — {now_iso()}")
    print(f"{'='*50}")
    
    # 处理所有节点的 inbox（发送 ACK）
    print("\n📥 处理 inbox (发送 ACK):")
    for node in os.listdir(QUEUE_DIR):
        node_path = os.path.join(QUEUE_DIR, node)
        if not os.path.isdir(node_path):
            continue
        stats = process_inbox(node)
        if stats["received"] > 0:
            print(f"  ✅ {node}: 接收 {stats['received']} 条，发送 ACK {stats['acked']} 条")
    
    # 检查所有节点的 outbox（重传未 ACK 消息）
    print("\n📤 检查 outbox (重传未确认):")
    for node in os.listdir(QUEUE_DIR):
        node_path = os.path.join(QUEUE_DIR, node)
        if not os.path.isdir(node_path):
            continue
        stats = check_acks(node)
        if stats["checked"] > 0:
            print(f"  📊 {node}: 检查 {stats['checked']} | ACK {stats['acked']} | 重传 {stats['retried']} | 失败 {stats['failed']}")
    
    print(f"\n{'='*50}\n")


def run_send(from_node, to_node, msg_type, payload_str):
    """发送单条消息"""
    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        payload = {"text": payload_str}
    
    msg_id = send_message(from_node, to_node, msg_type, payload)
    print(f"\n✅ 消息已发送: {msg_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "--check":
        run_check()
    elif cmd == "--send" and len(sys.argv) >= 6:
        run_send(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print(__doc__)
        sys.exit(1)
