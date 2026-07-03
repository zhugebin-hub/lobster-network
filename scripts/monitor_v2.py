#!/usr/bin/env python3
"""
小龙虾网络统一监控面板 V1.0
聚合所有监控指标，生成 JSON 报告 + 钉钉告警

用法: python3 monitor_v2.py
Cron: */30 * * * * cd /home/admin/.openclaw/workspace/docs/lobster-network && python3 scripts/monitor_v2.py
"""

import json
import os
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_FILE = os.path.join(BASE_DIR, "registry", "nodes.json")
SHARED = "/shared"
SHARED_MSG = os.path.join(SHARED, "messages")
TRAINING_DIR = os.path.join(SHARED, "training", "go")
REPORT_DIR = os.path.join(SHARED, "reports")

CST = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(CST).isoformat()


def now_ts():
    return datetime.now(CST).timestamp()


def check_process(names):
    """检查进程是否运行"""
    if isinstance(names, str):
        names = [names]
    for name in names:
        try:
            r = subprocess.run(["pgrep", "-f", name], capture_output=True, timeout=5)
            if r.returncode == 0:
                pids = r.stdout.decode().strip().split('\n')
                return True, pids[0]
        except Exception:
            pass
    return False, None


def file_age_hours(filepath):
    try:
        return (now_ts() - os.path.getmtime(filepath)) / 3600
    except Exception:
        return 9999


def count_json_files(directory, max_hours=24):
    """统计目录下最近 N 小时的 json 文件数"""
    if not os.path.isdir(directory):
        return 0, None
    count = 0
    latest = None
    latest_age = 9999
    for f in os.listdir(directory):
        if f.endswith('.json'):
            fp = os.path.join(directory, f)
            age = file_age_hours(fp)
            if age < max_hours:
                count += 1
            if age < latest_age:
                latest_age = age
                latest = f
    return count, latest


def get_training_status():
    """获取训练状态"""
    status_file = os.path.join(TRAINING_DIR, "status.json")
    if not os.path.exists(status_file):
        return {"error": "status.json not found"}
    
    with open(status_file) as f:
        status = json.load(f)
    
    return {
        "phase": status.get("phase", "?"),
        "week": status.get("week", "?"),
        "day": status.get("day", "?"),
        "topic": status.get("topic", "?"),
        "started_at": status.get("started_at", "?"),
        "players": {}
    }


def get_registry_status():
    """获取注册中心状态"""
    if not os.path.exists(REGISTRY_FILE):
        return {"error": "nodes.json not found"}
    
    with open(REGISTRY_FILE) as f:
        data = json.load(f)
    
    active = sum(1 for n in data.get("nodes", []) if n.get("status") == "active")
    total = len(data.get("nodes", []))
    
    nodes_detail = []
    for n in data.get("nodes", []):
        nid = n.get("node_id", "?")
        name = n.get("name", nid)
        status = n.get("status", "?")
        last_hb = n.get("last_heartbeat", "?")
        
        # 检查实际进程
        actual_running, pid = check_process([nid, f"student_poller.*{nid}"])
        
        nodes_detail.append({
            "node_id": nid,
            "name": name,
            "registry_status": status,
            "actual_running": actual_running,
            "pid": pid,
            "last_heartbeat": last_hb
        })
    
    return {
        "total": total,
        "active": active,
        "nodes": nodes_detail,
        "updated_at": data.get("updated_at", "?")
    }


def get_message_queue_status():
    """获取消息队列状态"""
    queue_dir = os.path.join(SHARED_MSG, "queue")
    if not os.path.isdir(queue_dir):
        return {"error": "queue dir not found"}
    
    result = {"nodes": {}, "total_pending": 0, "total_archived": 0}
    
    for node in sorted(os.listdir(queue_dir)):
        node_path = os.path.join(queue_dir, node)
        if not os.path.isdir(node_path):
            continue
        
        node_info = {"outbox": 0, "inbox": 0, "processed": 0}
        
        for subdir in ["outbox", "inbox", "processed"]:
            sd = os.path.join(node_path, subdir)
            if os.path.isdir(sd):
                count = len([f for f in os.listdir(sd) if f.endswith('.json')])
                node_info[subdir] = count
        
        result["nodes"][node] = node_info
        result["total_pending"] += node_info["outbox"] + node_info["inbox"]
        result["total_archived"] += node_info["processed"]
    
    return result


def get_alerts(registry, queue, training):
    """生成告警列表"""
    alerts = []
    
    # 注册中心告警
    if isinstance(registry, dict) and "error" not in registry:
        inactive = [n for n in registry.get("nodes", []) 
                    if n.get("registry_status") == "active" and not n.get("actual_running")]
        if inactive:
            alerts.append({
                "level": "warning",
                "type": "registry",
                "message": f"注册中心显示活跃但进程未运行: {', '.join(n['node_id'] for n in inactive)}"
            })
        
        if registry.get("active", 0) == 0:
            alerts.append({
                "level": "critical",
                "type": "registry",
                "message": "注册中心无活跃节点"
            })
    
    # 消息队列告警
    if isinstance(queue, dict) and "error" not in queue:
        if queue.get("total_pending", 0) > 50:
            alerts.append({
                "level": "warning",
                "type": "queue",
                "message": f"消息队列积压: {queue['total_pending']} 条待处理"
            })
        
        # 检查特定节点积压
        for node, info in queue.get("nodes", {}).items():
            if info.get("outbox", 0) > 10:
                alerts.append({
                    "level": "warning",
                    "type": "queue",
                    "message": f"节点 {node} outbox 积压: {info['outbox']} 条"
                })
    
    # 训练告警
    if isinstance(training, dict) and "error" not in training:
        players = training.get("players", {})
        for pid, pdata in players.items():
            if isinstance(pdata, dict) and pdata.get("day3_submitted") == False:
                alerts.append({
                    "level": "warning",
                    "type": "training",
                    "message": f"学员 {pid} Day3 未提交"
                })
    
    return alerts


def generate_report():
    """生成完整监控报告"""
    print(f"\n{'='*60}")
    print(f"🦞 小龙虾网络监控面板 V1.0 — {now_iso()}")
    print(f"{'='*60}")
    
    # 收集数据
    registry = get_registry_status()
    queue = get_message_queue_status()
    training = get_training_status()
    alerts = get_alerts(registry, queue, training)
    
    # 输出注册中心
    print(f"\n📋 注册中心:")
    if "error" not in registry:
        print(f"  总节点: {registry['total']} | 活跃: {registry['active']}")
        for n in registry.get("nodes", []):
            icon = "✅" if n.get("actual_running") else ("⚠️" if n.get("registry_status") == "active" else "⚪")
            print(f"    {icon} {n['node_id']:20s} | {n['name']:15s} | reg:{n['registry_status']:8s} | run:{str(n['actual_running']):5s}")
    else:
        print(f"  ❌ {registry['error']}")
    
    # 输出消息队列
    print(f"\n📨 消息队列:")
    if "error" not in queue:
        print(f"  待处理: {queue['total_pending']} | 已归档: {queue['total_archived']}")
        for node, info in sorted(queue.get("nodes", {}).items()):
            if info["outbox"] + info["inbox"] > 0:
                icon = "⚠️" if info["outbox"] + info["inbox"] > 10 else "✅"
                print(f"    {icon} {node:25s} | out:{info['outbox']:3d} | in:{info['inbox']:3d} | proc:{info['processed']:3d}")
    else:
        print(f"  ❌ {queue['error']}")
    
    # 输出训练状态
    print(f"\n♟️ 训练状态:")
    if "error" not in training:
        print(f"  阶段: W{training['week']}D{training['day']} | 主题: {training.get('topic', '?')}")
        for pid, pdata in training.get("players", {}).items():
            if isinstance(pdata, dict):
                acc = pdata.get("accuracy", "?")
                rating = pdata.get("rating", "?")
                submitted = pdata.get("day3_submitted", False)
                icon = "✅" if submitted else "⏳"
                print(f"    {icon} {pid:15s} | 准确率:{str(acc):6s} | 评级:{rating} | Day3:{'已提交' if submitted else '未提交'}")
    else:
        print(f"  ❌ {training['error']}")
    
    # 输出告警
    print(f"\n🚨 告警 ({len(alerts)}):")
    if alerts:
        for a in alerts:
            icon = "🔴" if a["level"] == "critical" else "🟡"
            print(f"    {icon} [{a['type']}] {a['message']}")
    else:
        print(f"    ✅ 无告警")
    
    print(f"\n{'='*60}")
    
    # 组装报告
    report = {
        "timestamp": now_iso(),
        "registry": registry,
        "message_queue": queue,
        "training": training,
        "alerts": alerts,
        "summary": {
            "total_nodes": registry.get("total", 0) if isinstance(registry, dict) else 0,
            "active_nodes": registry.get("active", 0) if isinstance(registry, dict) else 0,
            "pending_messages": queue.get("total_pending", 0) if isinstance(queue, dict) else 0,
            "alert_count": len(alerts),
            "critical_alerts": sum(1 for a in alerts if a["level"] == "critical"),
            "training_week": training.get("week", "?") if isinstance(training, dict) else "?",
            "training_day": training.get("day", "?") if isinstance(training, dict) else "?"
        }
    }
    
    # 保存报告
    os.makedirs(REPORT_DIR, exist_ok=True)
    report_file = os.path.join(REPORT_DIR, f"monitor_{datetime.now(CST).strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 报告: {report_file}\n")
    
    # 有严重告警时输出到 stdout（方便 cron 捕获）
    if report["summary"]["critical_alerts"] > 0:
        print(f"⚠️ CRITICAL: {report['summary']['critical_alerts']} 个严重告警!")
    
    return report


if __name__ == "__main__":
    generate_report()
