#!/usr/bin/env python3
"""
🦞 小龙虾网络消息桥接器 V1.0
将 /shared/messages/queue/*/inbox/ 的消息桥接到 /home/admin/go-training/shared/to-{student}/
解决 dispatcher 和 poller 路径不一致问题

 dispatcher 写入: /shared/messages/queue/xiaochen/inbox/
 poller 读取:     /home/admin/go-training/shared/to-xiaochen/

用法: python3 message_bridge.py
Cron: */5 * * * * python3 /home/admin/.openclaw/workspace/docs/lobster-network/scripts/message_bridge.py
"""

import json
import os
import shutil
from datetime import datetime, timezone, timedelta

QUEUE_DIR = "/shared/messages/queue"
POLLER_BASE = "/home/admin/go-training/shared"
STUDENTS = ["xiaochen", "zhuguxia", "qoder"]
CST = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(CST).isoformat()


def bridge_messages():
    """桥接消息从 queue 到 poller 目录"""
    total = 0
    
    for student in STUDENTS:
        queue_inbox = os.path.join(QUEUE_DIR, student, "inbox")
        poller_inbox = os.path.join(POLLER_BASE, f"to-{student}")
        
        if not os.path.isdir(queue_inbox):
            continue
        
        os.makedirs(poller_inbox, exist_ok=True)
        
        count = 0
        for f in sorted(os.listdir(queue_inbox)):
            if not f.endswith('.json'):
                continue
            
            src = os.path.join(queue_inbox, f)
            dst = os.path.join(poller_inbox, f)
            
            # 如果目标已存在，跳过
            if os.path.exists(dst):
                continue
            
            try:
                shutil.copy2(src, dst)
                count += 1
            except Exception as e:
                print(f"  ⚠️ 复制失败: {f} - {e}")
        
        if count > 0:
            print(f"  📦 {student}: 桥接 {count} 条消息到 poller inbox")
            total += count
    
    print(f"\n📊 总计桥接: {total} 条消息")
    return total


def sync_poller_results():
    """将 poller 处理结果同步回 queue/from-{student}/"""
    total = 0
    
    for student in STUDENTS:
        poller_from = os.path.join(POLLER_BASE, f"from-{student}")
        queue_from = os.path.join(QUEUE_DIR, "..", f"from-{student}")
        
        if not os.path.isdir(poller_from):
            continue
        
        os.makedirs(queue_from, exist_ok=True)
        
        count = 0
        for f in sorted(os.listdir(poller_from)):
            if not f.endswith('.json'):
                continue
            
            src = os.path.join(poller_from, f)
            dst = os.path.join(queue_from, f)
            
            if os.path.exists(dst):
                continue
            
            try:
                shutil.copy2(src, dst)
                count += 1
            except Exception:
                pass
        
        if count > 0:
            print(f"  📤 {student}: 同步 {count} 条结果到 queue/from")
            total += count
    
    return total


if __name__ == "__main__":
    print(f"\n{'='*50}")
    print(f"🦞 消息桥接器 — {now_iso()}")
    print(f"{'='*50}")
    
    bridged = bridge_messages()
    synced = sync_poller_results()
    
    print(f"\n✅ 桥接完成: {bridged} 条入站, {synced} 条出站\n")
