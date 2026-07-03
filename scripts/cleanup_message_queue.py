#!/usr/bin/env python3
"""
小龙虾网络消息队列清理器
- 扫描所有 queue 目录中的积压消息
- 超过 7 天的消息归档到 processed/
- 未处理的消息尝试转发或标记
- 生成清理报告

用法: python3 cleanup_message_queue.py
"""

import json
import os
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

SHARED_MESSAGES = "/shared/messages"
CST = timezone(timedelta(hours=8))
MAX_AGE_DAYS = 7


def now_iso():
    return datetime.now(CST).isoformat()


def file_age_hours(filepath):
    """计算文件年龄（小时）"""
    try:
        mtime = os.path.getmtime(filepath)
        age = datetime.now(CST).timestamp() - mtime
        return age / 3600
    except Exception:
        return 0


def cleanup_queue():
    """清理消息队列"""
    queue_dir = os.path.join(SHARED_MESSAGES, "queue")
    if not os.path.isdir(queue_dir):
        print(f"[{now_iso()}] ⚠️ 队列目录不存在: {queue_dir}")
        return
    
    stats = {
        "total_scanned": 0,
        "archived": 0,
        "processed": 0,
        "pending": 0,
        "errors": 0,
        "details": []
    }
    
    print(f"\n{'='*60}")
    print(f"🦞 小龙虾网络消息队列清理 — {now_iso()}")
    print(f"{'='*60}")
    
    # 扫描所有节点队列
    for node_queue in sorted(os.listdir(queue_dir)):
        node_path = os.path.join(queue_dir, node_queue)
        if not os.path.isdir(node_path):
            continue
        
        node_stats = {"node": node_queue, "outbox": 0, "inbox": 0, "archived": 0}
        
        # 处理 outbox
        outbox = os.path.join(node_path, "outbox")
        if os.path.isdir(outbox):
            for f in sorted(os.listdir(outbox)):
                if not f.endswith('.json'):
                    continue
                fp = os.path.join(outbox, f)
                stats["total_scanned"] += 1
                node_stats["outbox"] += 1
                
                age = file_age_hours(fp)
                if age > MAX_AGE_DAYS * 24:
                    # 归档旧消息
                    processed = os.path.join(node_path, "processed")
                    os.makedirs(processed, exist_ok=True)
                    try:
                        shutil.move(fp, os.path.join(processed, f))
                        stats["archived"] += 1
                        node_stats["archived"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                else:
                    stats["pending"] += 1
        
        # 处理 inbox
        inbox = os.path.join(node_path, "inbox")
        if os.path.isdir(inbox):
            for f in sorted(os.listdir(inbox)):
                if not f.endswith('.json'):
                    continue
                fp = os.path.join(inbox, f)
                stats["total_scanned"] += 1
                node_stats["inbox"] += 1
                
                age = file_age_hours(fp)
                if age > MAX_AGE_DAYS * 24:
                    processed = os.path.join(node_path, "processed")
                    os.makedirs(processed, exist_ok=True)
                    try:
                        shutil.move(fp, os.path.join(processed, f))
                        stats["archived"] += 1
                        node_stats["archived"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                else:
                    stats["pending"] += 1
        
        if node_stats["outbox"] > 0 or node_stats["inbox"] > 0:
            stats["details"].append(node_stats)
            status = "✅" if node_stats["outbox"] == 0 else "⚠️"
            print(f"  {status} {node_queue:25s} | outbox:{node_stats['outbox']:3d} | inbox:{node_stats['inbox']:3d} | 归档:{node_stats['archived']:3d}")
    
    # 清理 broadcast 目录
    broadcast = os.path.join(SHARED_MESSAGES, "broadcast")
    if os.path.isdir(broadcast):
        bc_count = 0
        for f in os.listdir(broadcast):
            if f.endswith('.json'):
                fp = os.path.join(broadcast, f)
                age = file_age_hours(fp)
                if age > 72:  # broadcast 保留 72 小时
                    try:
                        os.remove(fp)
                        bc_count += 1
                    except Exception:
                        pass
        if bc_count > 0:
            print(f"  📡 broadcast 清理: {bc_count} 条过期消息")
    
    # 清理 from-* 目录中的超旧文件（>30天）
    from_dirs = [d for d in os.listdir(SHARED_MESSAGES) if d.startswith("from-")]
    for fd in from_dirs:
        fd_path = os.path.join(SHARED_MESSAGES, fd)
        if not os.path.isdir(fd_path):
            continue
        cleaned = 0
        for f in os.listdir(fd_path):
            if f.endswith('.json'):
                fp = os.path.join(fd_path, f)
                age = file_age_hours(fp)
                if age > 720:  # 30 天
                    try:
                        os.remove(fp)
                        cleaned += 1
                    except Exception:
                        pass
        if cleaned > 0:
            print(f"  📁 {fd} 清理: {cleaned} 条超旧消息（>30天）")
    
    print(f"\n{'='*60}")
    print(f"📊 清理汇总:")
    print(f"  扫描总数: {stats['total_scanned']}")
    print(f"  已归档:   {stats['archived']}")
    print(f"  待处理:   {stats['pending']}")
    print(f"  错误:     {stats['errors']}")
    print(f"{'='*60}\n")
    
    # 保存报告
    report = {
        "timestamp": now_iso(),
        "stats": stats
    }
    report_dir = "/shared/reports"
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"queue_cleanup_{datetime.now(CST).strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告已保存: {report_file}")
    return stats


if __name__ == "__main__":
    cleanup_queue()
