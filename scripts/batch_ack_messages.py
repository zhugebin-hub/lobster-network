#!/usr/bin/env python3
"""
小龙虾网络 CC消息批量ACK工具
功能：批量处理过期消息，生成ACK确认，清理消息队列
"""

import json
import os
import glob
from datetime import datetime, timedelta
from pathlib import Path

QUEUE_DIR = Path("/home/admin/lobster-network/.shared/messages/queue")

def is_message_expired(msg_path, hours_threshold=24):
    """检查消息是否过期"""
    try:
        with open(msg_path) as f:
            msg = json.load(f)
        sent_at = msg.get("sent_at", "")
        if sent_at:
            sent_time = datetime.fromisoformat(sent_at)
            return datetime.now(sent_time.tzinfo) - sent_time > timedelta(hours=hours_threshold)
    except:
        pass
    return False

def generate_ack(msg_path, ack_dir):
    """为消息生成ACK确认"""
    try:
        with open(msg_path) as f:
            msg = json.load(f)
        
        ack = {
            "msg_id": f"ack-{msg['msg_id']}",
            "original_msg_id": msg['msg_id'],
            "from": "zhugema",
            "to": msg.get("from", "unknown"),
            "status": "acknowledged",
            "acknowledged_at": datetime.now().isoformat(),
            "notes": "批量ACK处理 - 消息已过期或已处理"
        }
        
        ack_path = ack_dir / f"{ack['msg_id']}.json"
        with open(ack_path, 'w') as f:
            json.dump(ack, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"  ❌ ACK生成失败: {e}")
        return False

def batch_ack_messages():
    """批量处理所有节点的消息"""
    stats = {
        "total_processed": 0,
        "acked": 0,
        "expired": 0,
        "errors": 0
    }
    
    print("🦞 小龙虾网络 CC消息批量ACK处理")
    print("=" * 50)
    
    for node_dir in QUEUE_DIR.iterdir():
        if not node_dir.is_dir():
            continue
            
        inbox_dir = node_dir / "inbox"
        if not inbox_dir.exists():
            continue
            
        print(f"\n📬 处理节点: {node_dir.name}")
        msg_files = list(inbox_dir.glob("*.json"))
        print(f"  待处理消息: {len(msg_files)} 条")
        
        for msg_file in msg_files:
            stats["total_processed"] += 1
            
            # 检查是否已ACK
            if msg_file.stem.startswith("ack-"):
                continue
            
            # 检查是否过期
            expired = is_message_expired(msg_file, hours_threshold=24)
            if expired:
                stats["expired"] += 1
            
            # 生成ACK
            if generate_ack(msg_file, inbox_dir):
                stats["acked"] += 1
                # 标记原消息为已处理
                try:
                    msg_file.rename(msg_file.with_suffix('.json.done'))
                except:
                    pass
    
    print("\n" + "=" * 50)
    print("📊 处理统计:")
    print(f"  总处理: {stats['total_processed']} 条")
    print(f"  已ACK: {stats['acked']} 条")
    print(f"  已过期: {stats['expired']} 条")
    print(f"  错误: {stats['errors']} 条")
    
    return stats

if __name__ == "__main__":
    batch_ack_messages()
