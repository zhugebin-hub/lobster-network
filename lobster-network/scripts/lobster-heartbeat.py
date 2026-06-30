#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 - 心跳管理
========================
功能：
1. 节点定期发送心跳到调度节点
2. 调度节点检测离线节点
3. 离线节点自动告警

用法：
    # 作为 cron 任务运行（每 30 秒）
    python3 lobster-heartbeat.py send
    
    # 调度节点运行离线检测（每 2 分钟）
    python3 lobster-heartbeat.py check
"""

import json
import os
import time
import requests
import sys
from datetime import datetime

# ==================== 配置 ====================
LOBSTER_ID = os.environ.get('LOBSTER_ID', 'lobster-001')
SCHEDULER_URL = os.environ.get('SCHEDULER_URL', 'http://127.0.0.1:8001')
NODES_FILE = os.path.expanduser("~/.openclaw/workspace/lobster-network/nodes.json")
HEARTBEAT_STATE_FILE = os.path.expanduser("~/.openclaw/workspace/lobster-network/heartbeat-state.json")
ALERTS_DIR = os.path.expanduser("~/.openclaw/workspace/lobster-network/alerts/")

# 离线阈值：2 分钟未收到心跳 = 离线
OFFLINE_THRESHOLD = 120  # 秒


def ensure_dirs():
    """确保目录存在"""
    os.makedirs(os.path.dirname(NODES_FILE), exist_ok=True)
    os.makedirs(ALERTS_DIR, exist_ok=True)


def load_nodes():
    """加载节点列表"""
    try:
        if os.path.exists(NODES_FILE):
            with open(NODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"nodes": [], "next_id": 5}


def save_nodes(data):
    """保存节点列表"""
    ensure_dirs()
    with open(NODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_heartbeat_state():
    """加载心跳状态"""
    try:
        if os.path.exists(HEARTBEAT_STATE_FILE):
            with open(HEARTBEAT_STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"last_heartbeat": 0, "consecutive_failures": 0}


def save_heartbeat_state(state):
    """保存心跳状态"""
    with open(HEARTBEAT_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_heartbeat():
    """
    节点发送心跳到调度节点
    作为 cron 任务每 30 秒运行一次
    """
    state = load_heartbeat_state()
    
    # 检查是否到了发送时间（避免重复发送）
    now = time.time()
    if now - state.get('last_heartbeat', 0) < 25:  # 至少间隔 25 秒
        return {"status": "skipped", "reason": "too_soon"}
    
    try:
        resp = requests.post(
            f"{SCHEDULER_URL}/heartbeat",
            json={
                "lobster_id": LOBSTER_ID,
                "timestamp": now,
                "status": "ok",
                "version": "2.0.0"
            },
            timeout=10
        )
        
        if resp.status_code == 200:
            state['last_heartbeat'] = now
            state['consecutive_failures'] = 0
            state['last_success'] = now
            save_heartbeat_state(state)
            print(f"✅ 心跳发送成功：{LOBSTER_ID}")
            return {"status": "ok"}
        else:
            raise Exception(f"HTTP {resp.status_code}")
            
    except Exception as e:
        state['consecutive_failures'] = state.get('consecutive_failures', 0) + 1
        state['last_error'] = str(e)
        state['last_error_at'] = datetime.now().isoformat()
        save_heartbeat_state(state)
        
        print(f"❌ 心跳发送失败：{LOBSTER_ID} - {e}")
        
        # 连续失败 3 次以上，发送告警
        if state['consecutive_failures'] >= 3:
            send_alert("P1", f"节点 {LOBSTER_ID} 心跳连续失败 {state['consecutive_failures']} 次")
        
        return {"status": "error", "error": str(e)}


def check_offline_nodes():
    """
    调度节点检查离线节点
    作为 cron 任务每 2 分钟运行一次
    """
    nodes_data = load_nodes()
    now = time.time()
    offline_nodes = []
    
    for node in nodes_data.get('nodes', []):
        lobster_id = node.get('lobster_id')
        last_hb = node.get('last_heartbeat', 0)
        current_status = node.get('status', 'unknown')
        
        # 跳过已经离线的节点
        if current_status == 'offline':
            continue
        
        # 检查是否超时
        if now - last_hb > OFFLINE_THRESHOLD:
            node['status'] = 'offline'
            node['offline_at'] = datetime.now().isoformat()
            offline_nodes.append(lobster_id)
            print(f"⚠️ 节点 {lobster_id} 离线（最后心跳：{int(now - last_hb)}秒前）")
            
            # 发送告警
            send_alert("P1", f"节点 {lobster_id} 离线（最后心跳：{int(now - last_hb)}秒前）")
    
    if offline_nodes:
        save_nodes(nodes_data)
        print(f"📊 离线节点：{', '.join(offline_nodes)}")
    else:
        print("✅ 所有节点在线")
    
    return {"offline_nodes": offline_nodes, "total": len(nodes_data.get('nodes', []))}


def send_alert(level, message):
    """发送告警通知"""
    ensure_dirs()
    
    alert = {
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "source": "heartbeat-monitor"
    }
    
    # 写入告警文件
    alert_file = os.path.join(ALERTS_DIR, f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(alert_file, 'w', encoding='utf-8') as f:
        json.dump(alert, f, ensure_ascii=False, indent=2)
    
    # P0/P1 发送到钉钉
    if level in ['P0', 'P1']:
        try:
            # 调用 wrapper 的钉钉发送
            resp = requests.post(
                f"{SCHEDULER_URL}/alert",
                json={"level": level, "message": message},
                timeout=10
            )
            print(f"📢 告警已发送：[{level}] {message}")
        except Exception as e:
            print(f"⚠️ 告警发送失败：{e}")


def get_network_status():
    """获取网络状态摘要"""
    nodes_data = load_nodes()
    now = time.time()
    
    online = []
    offline = []
    busy = []
    
    for node in nodes_data.get('nodes', []):
        lobster_id = node.get('lobster_id')
        last_hb = node.get('last_heartbeat', 0)
        status = node.get('status', 'unknown')
        
        if status == 'online':
            online.append(lobster_id)
        elif status == 'offline':
            offline.append(lobster_id)
        elif status == 'busy':
            busy.append(lobster_id)
        elif now - last_hb > OFFLINE_THRESHOLD:
            offline.append(lobster_id)
        else:
            online.append(lobster_id)
    
    return {
        "total": len(nodes_data.get('nodes', [])),
        "online": len(online),
        "offline": len(offline),
        "busy": len(busy),
        "online_nodes": online,
        "offline_nodes": offline
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 lobster-heartbeat.py [send|check|status]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'send':
        result = send_heartbeat()
        sys.exit(0 if result.get('status') == 'ok' else 1)
        
    elif command == 'check':
        result = check_offline_nodes()
        sys.exit(0)
        
    elif command == 'status':
        status = get_network_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
        sys.exit(0)
        
    else:
        print(f"未知命令：{command}")
        sys.exit(1)
