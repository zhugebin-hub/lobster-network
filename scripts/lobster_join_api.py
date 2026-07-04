#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 动态注册 API (Primary/Backup)
支持：节点注册、心跳保活、健康检查、主备切换
"""

import json
import os
import sys
import time
import uuid
import argparse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

REGISTRY_DIR = os.path.join(os.path.dirname(__file__), '..', 'registry')
REGISTRY_FILE = os.path.join(REGISTRY_DIR, 'nodes.json')
HEARTBEAT_TIMEOUT = 600  # 10分钟无心跳视为离线
CHECK_INTERVAL = 300     # 5分钟检查一次心跳

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"version": "1.0.0", "updated_at": datetime.now().isoformat(), "nodes": []}

def save_registry(data):
    os.makedirs(REGISTRY_DIR, exist_ok=True)
    data['updated_at'] = datetime.now().isoformat()
    with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def heartbeat_checker(role, peer_url=None):
    """后台心跳检查与主备切换"""
    while True:
        time.sleep(CHECK_INTERVAL)
        registry = load_registry()
        now = datetime.now()
        updated = False
        
        for node in registry['nodes']:
            last_hb = datetime.fromisoformat(node.get('last_heartbeat', '2020-01-01T00:00:00'))
            if (now - last_hb).total_seconds() > HEARTBEAT_TIMEOUT:
                if node['status'] == 'active':
                    node['status'] = 'inactive'
                    updated = True
                    print(f"[{now.isoformat()}] ⚠️ 节点 {node['node_id']} 心跳超时，标记为 inactive")
                    
        if updated:
            save_registry(registry)
            
        # 主备切换逻辑
        if role == 'backup' and peer_url:
            try:
                resp = requests.get(f"{peer_url}/api/v1/health", timeout=10)
                if resp.status_code != 200:
                    print(f"[{now.isoformat()}] 🔄 Primary 不可达，Backup 准备升主")
                    # 实际升主逻辑需结合业务场景
            except Exception as e:
                print(f"[{now.isoformat()}] 🔄 Primary 连接失败: {e}")

class RegistryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/v1/nodes':
            registry = load_registry()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(registry, ensure_ascii=False).encode())
        elif self.path == '/api/v1/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "timestamp": datetime.now().isoformat()}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        if self.path == '/api/v1/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                node_data = json.loads(post_data)
                registry = load_registry()
                
                # 验证必填字段
                required = ['node_id', 'name', 'type']
                if not all(k in node_data for k in required):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "缺少必填字段: node_id, name, type"}).encode())
                    return
                    
                # 检查是否已存在
                for node in registry['nodes']:
                    if node['node_id'] == node_data['node_id']:
                        node.update(node_data)
                        node['last_heartbeat'] = datetime.now().isoformat()
                        node['status'] = 'active'
                        save_registry(registry)
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"message": "节点已更新", "node_id": node_data['node_id']}).encode())
                        return
                        
                # 新增节点
                node_data['registered_at'] = datetime.now().isoformat()
                node_data['last_heartbeat'] = datetime.now().isoformat()
                node_data['status'] = 'active'
                registry['nodes'].append(node_data)
                save_registry(registry)
                
                self.send_response(201)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"message": "注册成功", "node_id": node_data['node_id']}).encode())
                
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "JSON 格式错误"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {args[0]}")

def main():
    parser = argparse.ArgumentParser(description='🦞 小龙虾网络 · 动态注册 API')
    parser.add_argument('--port', type=int, default=8001, help='监听端口')
    parser.add_argument('--role', type=str, choices=['primary', 'backup'], default='primary', help='节点角色')
    parser.add_argument('--peer', type=str, default=None, help='对等节点 URL (仅 backup 需要)')
    args = parser.parse_args()
    
    import threading
    heartbeat_thread = threading.Thread(target=heartbeat_checker, args=(args.role, args.peer), daemon=True)
    heartbeat_thread.start()
    
    server = HTTPServer(('0.0.0.0', args.port), RegistryHandler)
    print(f"🦞 小龙虾网络 · 动态注册 API 已启动")
    print(f"   端口: {args.port}")
    print(f"   角色: {args.role}")
    print(f"   心跳间隔: {CHECK_INTERVAL}s")
    print(f"   超时阈值: {HEARTBEAT_TIMEOUT}s")
    print(f"   注册表: {REGISTRY_FILE}")
    print(f"   访问: http://0.0.0.0:{args.port}/api/v1/nodes")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        server.server_close()

if __name__ == '__main__':
    main()
