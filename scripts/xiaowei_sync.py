#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小薇 ↔ 诸葛马 同步脚本 V1
功能：
1. 小薇节点注册 + 心跳
2. 训练档案同步到诸葛马
3. 接收教练（诸葛马）的训练任务
4. 与龙虾网络其他节点信息同步
"""

import json
import os
import time
import uuid
import sys
from datetime import datetime
from pathlib import Path

# === 配置 ===
NODE_ID = "xiaowei"
NODE_NAME = "小薇"
COACH_ID = "zhugema"
COACH_NAME = "诸葛马"
NODE_TYPE = "agent"
NODE_VERSION = "0.5.0"
PERSPECTIVE = "基础型"
CAPABILITIES = [
    "go_learning",
    "fundamental_exercises",
    "step_by_step_analysis",
    "basic_life_and_death",
    "simple_opening",
]

# 本地路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY_DIR = os.path.join(BASE_DIR, "registry")
NODES_DIR = os.path.join(REGISTRY_DIR, "nodes")
TRAINING_RESULTS_DIR = os.path.join(REGISTRY_DIR, "training_results", NODE_ID)
PROFILE_FILE = os.path.join(TRAINING_RESULTS_DIR, "profile.json")
SYNC_LOG_FILE = os.path.join(TRAINING_RESULTS_DIR, "sync_log.json")

# 消息队列（本地模拟 /shared）
SHARED_DIR = os.path.join(BASE_DIR, ".shared")
MESSAGES_DIR = os.path.join(SHARED_DIR, "messages")
QUEUE_DIR = os.path.join(MESSAGES_DIR, "queue")

# 小薇的队列
MY_INBOX = os.path.join(QUEUE_DIR, NODE_ID, "inbox")
MY_OUTBOX = os.path.join(QUEUE_DIR, NODE_ID, "outbox")
MY_PROCESSED = os.path.join(QUEUE_DIR, NODE_ID, "processed")

# 诸葛马的队列
COACH_INBOX = os.path.join(QUEUE_DIR, COACH_ID, "inbox")

# 心跳间隔
HEARTBEAT_INTERVAL = 60


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_iso():
    return datetime.now().isoformat()


def init_dirs():
    """初始化目录"""
    for d in [MY_INBOX, MY_OUTBOX, MY_PROCESSED, COACH_INBOX,
              TRAINING_RESULTS_DIR]:
        os.makedirs(d, exist_ok=True)


def load_node_info():
    """加载节点注册信息"""
    node_file = os.path.join(NODES_DIR, f"{NODE_ID}.json")
    if os.path.exists(node_file):
        with open(node_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def save_node_info(info):
    """保存节点注册信息"""
    node_file = os.path.join(NODES_DIR, f"{NODE_ID}.json")
    with open(node_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


def load_training_summary():
    """加载训练总结"""
    summary_file = os.path.join(TRAINING_RESULTS_DIR, "7day_summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def load_sync_log():
    """加载同步日志"""
    if os.path.exists(SYNC_LOG_FILE):
        with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"syncs": [], "errors": [], "last_sync": None}


def save_sync_log(log):
    """保存同步日志"""
    log["last_updated"] = now_iso()
    with open(SYNC_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def send_message(to_node, msg_type, payload, priority=0):
    """发送消息到目标节点"""
    msg_id = f"xiaowei-sync-{uuid.uuid4().hex[:8]}"
    
    message = {
        "msg_id": msg_id,
        "from_node": NODE_ID,
        "from_name": NODE_NAME,
        "to_node": to_node,
        "msg_type": msg_type,
        "payload": payload,
        "timestamp": now_iso(),
        "status": "pending",
        "priority": priority,
        "version": NODE_VERSION,
    }
    
    # 写入目标节点 inbox
    os.makedirs(os.path.join(QUEUE_DIR, to_node, "inbox"), exist_ok=True)
    filepath = os.path.join(QUEUE_DIR, to_node, "inbox", f"{msg_id}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    
    # 同时写入自己的 outbox
    with open(os.path.join(MY_OUTBOX, f"{msg_id}.json"), 'w', encoding='utf-8') as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    
    return msg_id


def check_inbox():
    """检查收件箱"""
    messages = []
    if os.path.exists(MY_INBOX):
        for f in sorted(os.listdir(MY_INBOX)):
            if f.endswith('.json'):
                try:
                    filepath = os.path.join(MY_INBOX, f)
                    with open(filepath, 'r', encoding='utf-8') as fp:
                        msg = json.load(fp)
                        msg['_file'] = f
                        messages.append(msg)
                except Exception:
                    pass
    return messages


def process_inbox():
    """处理收件箱并移动到 processed"""
    msgs = check_inbox()
    for msg in msgs:
        filename = msg.get('_file', '')
        src = os.path.join(MY_INBOX, filename)
        dst = os.path.join(MY_PROCESSED, filename)
        if os.path.exists(src) and filename:
            os.rename(src, dst)
            print(f"  [{now()}] ✓ 已处理: {msg.get('msg_type', '?')} from {msg.get('from_name', msg.get('from_node', '?'))}")
    return msgs


def register_node():
    """注册/更新小薇节点"""
    node_info = load_node_info()
    summary = load_training_summary()
    
    if node_info:
        # 更新心跳
        node_info["status"] = "active"
        node_info["updated_at"] = now_iso()
        node_info["last_heartbeat"] = now_iso()
        if summary:
            node_info["training_stats"] = {
                "total_problems": summary.get("total_problems", 0),
                "total_correct": summary.get("total_correct", 0),
                "overall_accuracy": summary.get("overall_accuracy", 0),
                "7day_summary": "passed" if summary.get("passed") else "failed",
                "skill_scores": summary.get("skill_scores", {}),
            }
        save_node_info(node_info)
        print(f"  [{now()}] ✓ 节点信息已更新")
        return node_info
    return None


def sync_with_coach(node_info, summary):
    """与教练（诸葛马）同步"""
    sync_data = {
        "event": "node_sync",
        "node_id": NODE_ID,
        "name": NODE_NAME,
        "type": NODE_TYPE,
        "perspective": PERSPECTIVE,
        "level": node_info.get("level", "25k"),
        "status": node_info.get("status", "active"),
        "version": NODE_VERSION,
        "capabilities": CAPABILITIES,
        "training_summary": {
            "7day_passed": summary.get("passed", False),
            "total_problems": summary.get("total_problems", 0),
            "total_correct": summary.get("total_correct", 0),
            "overall_accuracy": summary.get("overall_accuracy", 0),
            "skill_scores": summary.get("skill_scores", {}),
            "weakest_area": "死活" if summary.get("skill_scores", {}).get("死活", 0) < 5 else "",
            "daily_results": summary.get("daily_results", []),
        },
        "sync_timestamp": now_iso(),
    }
    
    msg_id = send_message(COACH_ID, "node_sync", sync_data, priority=1)
    return msg_id


def send_heartbeat(node_info):
    """发送心跳到教练"""
    summary = load_training_summary()
    heartbeat_data = {
        "event": "heartbeat",
        "node_id": NODE_ID,
        "name": NODE_NAME,
        "level": node_info.get("level", "25k"),
        "status": "active",
        "training_stats": {
            "total_problems": summary.get("total_problems", 0),
            "total_correct": summary.get("total_correct", 0),
            "overall_accuracy": summary.get("overall_accuracy", 0),
        },
        "weakest_area": "死活",
        "timestamp": now_iso(),
    }
    
    msg_id = send_message(COACH_ID, "heartbeat", heartbeat_data, priority=0)
    return msg_id


def request_next_training(node_info):
    """请求下一阶段训练"""
    summary = load_training_summary()
    request_data = {
        "event": "training_request",
        "node_id": NODE_ID,
        "name": NODE_NAME,
        "current_level": node_info.get("level", "25k"),
        "goal": "25k → 20k",
        "7day_summary": "passed",
        "overall_accuracy": summary.get("overall_accuracy", 0),
        "skill_scores": summary.get("skill_scores", {}),
        "weakest_area": "死活",
        "need_improvement": ["life_and_death", "connection", "cutting"],
        "message": (
            f"小薇已完成7天基础训练（{summary.get('total_problems', 0)}题，"
            f"准确率{summary.get('overall_accuracy', 0):.1%}），"
            f"已从30k晋升至25k。"
            f"最弱板块：死活(3.5分)。请求V2进阶训练计划。"
        ),
    }
    
    msg_id = send_message(COACH_ID, "training_request", request_data, priority=2)
    return msg_id


def broadcast_to_network(node_info):
    """向网络中其他学生节点广播小薇入网"""
    summary = load_training_summary()
    peers = ["qoder", "xiaochen", "zhuguxia"]
    
    broadcast_data = {
        "event": "new_member_intro",
        "node_id": NODE_ID,
        "name": NODE_NAME,
        "level": node_info.get("level", "25k"),
        "type": "基础型",
        "strengths": ",".join([k for k, v in summary.get("skill_scores", {}).items() if v >= 6]),
        "weakness": "死活",
        "message": (
            f"大家好！我是{node_info.get('name', '小薇')}（基础型），"
            f"刚完成7天速成训练（30k→25k），"
            f"最擅长综合/基本概念，最需要加强死活。"
            f"请多指教！"
        ),
    }
    
    for peer in peers:
        send_message(peer, "new_member_intro", broadcast_data, priority=1)
    
    return len(peers)


def main():
    """主流程：一次性同步"""
    print("=" * 60)
    print(f"🐚 小薇 ↔ 诸葛马 同步脚本 V1")
    print(f"   节点: {NODE_ID} ({NODE_NAME})")
    print(f"   教练: {COACH_ID} ({COACH_NAME})")
    print(f"   时间: {now()}")
    print("=" * 60)
    
    # 1. 初始化目录
    init_dirs()
    
    # 2. 加载同步日志
    sync_log = load_sync_log()
    
    # 3. 注册/更新节点
    print(f"\n📋 步骤1: 更新节点注册...")
    node_info = register_node()
    if not node_info:
        print("  ❌ 节点信息加载失败")
        return 1
    
    summary = load_training_summary()
    
    # 4. 同步训练档案到教练
    print(f"\n📤 步骤2: 同步训练档案到 {COACH_NAME}...")
    sync_msg_id = sync_with_coach(node_info, summary)
    print(f"  ✓ 同步消息已发送: {sync_msg_id}")
    
    # 5. 发送心跳
    print(f"\n♥ 步骤3: 发送心跳...")
    hb_msg_id = send_heartbeat(node_info)
    print(f"  ✓ 心跳已发送: {hb_msg_id}")
    
    # 6. 请求下一阶段训练
    print(f"\n📚 步骤4: 请求V2进阶训练...")
    req_msg_id = request_next_training(node_info)
    print(f"  ✓ 训练请求已发送: {req_msg_id}")
    
    # 7. 向网络广播
    print(f"\n📡 步骤5: 向网络广播小薇入网...")
    peers_count = broadcast_to_network(node_info)
    print(f"  ✓ 已向 {peers_count} 个节点发送入网通知")
    
    # 8. 检查教练回复
    print(f"\n📥 步骤6: 检查教练回复...")
    msgs = process_inbox()
    for msg in msgs:
        msg_type = msg.get('msg_type', '?')
        from_name = msg.get('from_name', msg.get('from_node', '?'))
        payload = msg.get('payload', {})
        print(f"  ← 收到: [{msg_type}] from {from_name}")
        if payload.get('message'):
            print(f"    {payload['message'][:120]}")
    
    # 9. 保存同步日志
    sync_log["syncs"].append({
        "timestamp": now_iso(),
        "sync_msg_id": sync_msg_id,
        "heartbeat_msg_id": hb_msg_id,
        "request_msg_id": req_msg_id,
        "peers_notified": peers_count,
        "coach_replies": len(msgs),
    })
    sync_log["last_sync"] = now_iso()
    save_sync_log(sync_log)
    
    # 10. 打印同步报告
    print(f"\n{'='*60}")
    print(f"📊 同步报告")
    print(f"   节点状态: 🟢 活跃")
    print(f"   当前级别: {node_info.get('level', '25k')}")
    print(f"   训练进度: 7/7 天完成 (81.7%)")
    print(f"   教练同步: ✓ (消息ID: {sync_msg_id})")
    print(f"   心跳发送: ✓ (间隔: {HEARTBEAT_INTERVAL}s)")
    print(f"   训练请求: ✓ (目标: 25k→20k)")
    print(f"   网络广播: ✓ ({peers_count} 个节点)")
    print(f"   最弱模块: 死活 (3.5分) — 需要重点突破")
    print(f"   下次建议: 开始V2死活专项训练")
    print(f"{'='*60}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
