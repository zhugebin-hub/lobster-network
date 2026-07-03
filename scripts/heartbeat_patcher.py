#!/usr/bin/env python3
"""
小龙虾网络注册中心心跳修复器
从实际进程状态反写 registry/nodes.json
解决"注册中心为空"问题

用法: python3 heartbeat_patcher.py
Cron: */30 * * * * cd /home/admin/.openclaw/workspace/docs/lobster-network && python3 scripts/heartbeat_patcher.py
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone, timedelta

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_FILE = os.path.join(BASE_DIR, "registry", "nodes.json")
LOG_DIR = os.path.join(BASE_DIR, "registry", "learning_sessions")
SHARED_MESSAGES = "/shared/messages"

# 时区
CST = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(CST).isoformat()


def check_process_running(names):
    """检查进程是否实际运行。names 可以是字符串或列表"""
    if isinstance(names, str):
        names = [names]
    for name in names:
        try:
            result = subprocess.run(
                ["pgrep", "-f", name],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return True, result.stdout.strip().split('\n')[0]
        except Exception:
            pass
    return False, None


def check_message_activity(node_id, max_hours=24):
    """检查节点最近是否有消息活动"""
    cutoff = datetime.now(CST).timestamp() - (max_hours * 3600)
    
    # 检查 from-<node> 目录
    from_dir = os.path.join(SHARED_MESSAGES, f"from-{node_id}")
    if os.path.isdir(from_dir):
        for f in os.listdir(from_dir):
            if f.endswith('.json'):
                fp = os.path.join(from_dir, f)
                try:
                    mtime = os.path.getmtime(fp)
                    if mtime > cutoff:
                        return True
                except Exception:
                    pass
    
    # 检查 queue 目录
    for queue_dir in [
        os.path.join(SHARED_MESSAGES, "queue", node_id),
        os.path.join(SHARED_MESSAGES, "queue", f"{node_id}-lobster"),
    ]:
        if os.path.isdir(queue_dir):
            for sub in ["inbox", "outbox"]:
                sd = os.path.join(queue_dir, sub)
                if os.path.isdir(sd):
                    for f in os.listdir(sd):
                        if f.endswith('.json'):
                            fp = os.path.join(sd, f)
                            try:
                                if os.path.getmtime(fp) > cutoff:
                                    return True
                            except Exception:
                                pass
    return False


def check_training_activity(node_id, max_hours=48):
    """检查节点最近是否有训练活动"""
    cutoff = datetime.now(CST).timestamp() - (max_hours * 3600)
    training_dir = f"/shared/training/go/from-{node_id}"
    if os.path.isdir(training_dir):
        for f in os.listdir(training_dir):
            if f.endswith('.json'):
                fp = os.path.join(training_dir, f)
                try:
                    if os.path.getmtime(fp) > cutoff:
                        return True
                except Exception:
                    pass
    return False


def determine_status(node_id, node_data):
    """根据实际状态判断节点状态"""
    # 特殊节点处理
    if node_id == "qoder":
        # qoder 有特殊进程
        running, pid = check_process_running(["qoder", "student_poller", "register_qoder"])
        if running:
            return "active", pid
        # 检查消息活动
        if check_message_activity(node_id, max_hours=72):
            return "active", "recent-messages"
        return "inactive", None
    
    if node_id == "xiaochen":
        # 小陈：检查 student_poller
        running, pid = check_process_running(["xiaochen", "student_poller"])
        if running:
            return "active", pid
        if check_training_activity(node_id) or check_message_activity(node_id, max_hours=48):
            return "active", "recent-activity"
        return "inactive", None
    
    if node_id == "zhuguxia":
        # 诸葛虾：远程节点，检查训练活动
        if check_training_activity(node_id, max_hours=72):
            return "active", "recent-training"
        if check_message_activity(node_id, max_hours=72):
            return "active", "recent-messages"
        return "inactive", None
    
    if node_id == "hermes":
        # 诸葛马：远程教练，检查消息
        if check_message_activity("hermes", max_hours=72):
            return "active", "recent-messages"
        return "inactive", None
    
    if node_id == "museum-001" or node_id == "lobster-001":
        # 院史馆/协议架构师：检查本地进程
        running, pid = check_process_running(["museum", "lobster", "protocol"])
        if running:
            return "active", pid
        return "inactive", None
    
    # 测试节点
    if node_id.startswith("test-node"):
        return "inactive", "test-only"
    
    return "unknown", None


def update_registry():
    """更新注册中心"""
    if not os.path.exists(REGISTRY_FILE):
        print(f"[{now_iso()}] ❌ 注册文件不存在: {REGISTRY_FILE}")
        return
    
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    now = now_iso()
    updated = 0
    active_count = 0
    inactive_count = 0
    
    print(f"\n{'='*60}")
    print(f"🦞 小龙虾网络注册中心心跳修复 — {now}")
    print(f"{'='*60}")
    
    for node in data.get("nodes", []):
        nid = node.get("node_id", "unknown")
        name = node.get("name", nid)
        old_status = node.get("status", "?")
        
        status, detail = determine_status(nid, node)
        
        if status != old_status:
            node["status"] = status
            updated += 1
        
        # 如果节点实际活跃，更新心跳时间
        if status == "active":
            node["last_heartbeat"] = now
            active_count += 1
            print(f"  ✅ {nid:20s} | {name:15s} | {status:8s} | {detail}")
        elif status == "inactive":
            inactive_count += 1
            print(f"  ⚪ {nid:20s} | {name:15s} | {status:8s} | {detail or 'no activity'}")
        else:
            print(f"  ❓ {nid:20s} | {name:15s} | {status:8s} | {detail or 'unknown'}")
    
    # 保存
    data["updated_at"] = now
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 结果汇总:")
    print(f"  总节点数: {len(data.get('nodes', []))}")
    print(f"  活跃节点: {active_count}")
    print(f"  非活跃节点: {inactive_count}")
    print(f"  状态变更: {updated}")
    print(f"{'='*60}\n")
    
    return {
        "total": len(data.get("nodes", [])),
        "active": active_count,
        "inactive": inactive_count,
        "updated": updated,
        "timestamp": now
    }


if __name__ == "__main__":
    result = update_registry()
    if result:
        sys.exit(0 if result["active"] > 0 else 1)
