#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 主备同步脚本
功能：定时同步注册表、心跳检测、故障切换
"""

import json
import os
import time
import argparse
import requests
from datetime import datetime

REGISTRY_FILE = os.path.join(os.path.dirname(__file__), '..', 'registry', 'nodes.json')
SYNC_INTERVAL = 300  # 5分钟同步一次

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "1.0.0", "updated_at": datetime.now().isoformat(), "nodes": []}

def save_registry(data):
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    data['updated_at'] = datetime.now().isoformat()
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def sync_with_peer(peer_url):
    """与对等节点同步"""
    try:
        resp = requests.get(f"{peer_url}/api/v1/nodes", timeout=10)
        if resp.status_code == 200:
            peer_registry = resp.json()
            local_registry = load_registry()
            
            # 合并节点（以更新时间为准）
            local_nodes = {n['node_id']: n for n in local_registry.get('nodes', [])}
            peer_nodes = {n['node_id']: n for n in peer_registry.get('nodes', [])}
            
            merged = {}
            all_ids = set(list(local_nodes.keys()) + list(peer_nodes.keys()))
            
            for nid in all_ids:
                local = local_nodes.get(nid)
                peer = peer_nodes.get(nid)
                
                if not local:
                    merged[nid] = peer
                elif not peer:
                    merged[nid] = local
                else:
                    # 取最后心跳更新的版本
                    local_hb = local.get('last_heartbeat', '')
                    peer_hb = peer.get('last_heartbeat', '')
                    merged[nid] = peer if peer_hb > local_hb else local
                    
            local_registry['nodes'] = list(merged.values())
            save_registry(local_registry)
            print(f"[{datetime.now().isoformat()}] ✅ 同步完成，当前节点数: {len(merged)}")
        else:
            print(f"[{datetime.now().isoformat()}] ⚠️ 对等节点返回状态码: {resp.status_code}")
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] ❌ 同步失败: {e}")

def main():
    parser = argparse.ArgumentParser(description='🦞 小龙虾网络 · 主备同步')
    parser.add_argument('--peer', type=str, required=True, help='对等节点 URL (如 http://60.205.139.51:8002)')
    parser.add_argument('--interval', type=int, default=SYNC_INTERVAL, help='同步间隔(秒)')
    args = parser.parse_args()
    
    print(f"🦞 小龙虾网络 · 主备同步已启动")
    print(f"   对等节点: {args.peer}")
    print(f"   同步间隔: {args.interval}s")
    
    while True:
        sync_with_peer(args.peer)
        time.sleep(args.interval)

if __name__ == '__main__':
    main()
