#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 龙虾网络自助加入 API - Lobster Network Auto-Join API
======================================================
功能：提供 HTTP 接口，让新龙虾节点自助加入龙虾网络

API 端点：
    POST /join - 自助加入龙虾网络
    GET  /config/<lobster_id> - 获取配置
    GET  /install/<lobster_id> - 下载安装脚本
    GET  /nodes - 查看所有已注册节点
    GET  /status - 查看龙虾网络状态

部署方式：
    python3 lobster_join_api.py --port=8001
"""

import argparse
import logging
import json
import os
import random
import string
from datetime import datetime
from flask import Flask, request, jsonify

# ==================== 配置区 ====================
LOBSTER_NETWORK_DIR = os.path.expanduser("~/.openclaw/workspace/lobster-network")
NODES_FILE = os.path.join(LOBSTER_NETWORK_DIR, "nodes.json")
CONFIG_DIR = os.path.join(LOBSTER_NETWORK_DIR, "configs")
INSTALL_DIR = os.path.join(LOBSTER_NETWORK_DIR, "installs")

# 端口范围
PORT_RANGE_START = 8001
PORT_RANGE_END = 8010

# ==================== Flask 应用 ====================
app = Flask(__name__)

# ==================== 日志配置 ====================
def setup_logger():
    logger = logging.getLogger("lobster-join-api")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('🦞 %(asctime)s [JOIN-API] %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

# ==================== 工具函数 ====================
def ensure_dirs():
    """确保目录存在"""
    os.makedirs(os.path.dirname(NODES_FILE), exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(INSTALL_DIR, exist_ok=True)

def load_nodes() -> dict:
    """加载节点列表"""
    try:
        if os.path.exists(NODES_FILE):
            with open(NODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"读取节点文件失败：{e}")
    return {"nodes": [], "next_id": 5}

def save_nodes(data: dict):
    """保存节点列表"""
    with open(NODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_lobster_id(nodes_data: dict) -> str:
    """生成新的龙虾 ID"""
    lobster_id = f"lobster-{nodes_data['next_id']:03d}"
    nodes_data['next_id'] += 1
    return lobster_id

def find_available_port(nodes_data: dict, preferred_port: int = None) -> int:
    """查找可用端口"""
    used_ports = [node.get('port', 0) for node in nodes_data['nodes']]
    
    # 如果指定了端口且未使用，优先使用
    if preferred_port and preferred_port not in used_ports:
        return preferred_port
    
    # 否则自动分配
    for port in range(PORT_RANGE_START, PORT_RANGE_END + 1):
        if port not in used_ports:
            return port
    
    # 如果都在使用，随机分配一个
    return random.randint(PORT_RANGE_START, PORT_RANGE_END)

def generate_config(lobster_id: str, port: int, name: str, ip: str, role: str) -> dict:
    """生成节点配置"""
    config = {
        "lobster": {
            "id": lobster_id,
            "name": name,
            "port": port,
            "role": role
        },
        "scheduler": {
            "id": "lobster-001",
            "url": f"http://47.93.6.57:8001"
        },
        "network": {
            "mode": "direct",
            "vpc": "172.24.56.0/24"
        },
        "created_at": datetime.now().isoformat()
    }
    return config

def generate_install_script(lobster_id: str, port: int) -> str:
    """生成安装脚本"""
    script = f"""#!/bin/bash
# 🦞 龙虾节点安装脚本 - {lobster_id}
# 生成时间：{datetime.now().isoformat()}

set -e

LOBSTER_ID="{lobster_id}"
LOBSTER_PORT={port}
LOBSTER_HOME="$HOME/lobster-network"

echo "🦞 开始安装龙虾节点 {lobster_id}..."

# 1. 创建目录
mkdir -p "$LOBSTER_HOME"
mkdir -p ~/lobster-tasks/pending
mkdir -p ~/lobster-tasks/done
mkdir -p ~/lobster-tasks/logs

# 2. 下载技能包
echo "📦 下载技能包..."
wget -q http://47.93.6.57:8001/skill/lobster-network-skill.tar.gz -O /tmp/lobster-network-skill.tar.gz
tar xzf /tmp/lobster-network-skill.tar.gz -C "$LOBSTER_HOME/"

# 3. 下载配置
echo "⚙️ 下载配置..."
wget -q http://47.93.6.57:8001/config/$LOBSTER_ID -O "$LOBSTER_HOME/config.yaml"

# 4. 安装依赖
echo "📚 安装依赖..."
pip3 install flask requests --user

# 5. 启动服务
echo "🚀 启动服务..."
cd "$LOBSTER_HOME"
nohup python3 wrapper.py --lobster-id=$LOBSTER_ID --port=$LOBSTER_PORT > ~/lobster-tasks/logs/$LOBSTER_ID.log 2>&1 &

# 6. 验证
echo "✅ 验证安装..."
sleep 2
curl -s http://127.0.0.1:$LOBSTER_PORT/health

echo ""
echo "🦞 龙虾节点 {lobster_id} 安装完成！"
echo "   健康检查：curl http://127.0.0.1:$LOBSTER_PORT/health"
echo "   查看日志：tail -f ~/lobster-tasks/logs/$LOBSTER_ID.log"
echo "   查看待办：curl http://127.0.0.1:$LOBSTER_PORT/pending"
"""
    return script

# ==================== API 端点 ====================

@app.route('/join', methods=['POST'])
def join():
    """自助加入龙虾网络"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "请求体不能为空"}), 400
        
        # 提取参数
        name = data.get('name', '未知节点')
        ip = data.get('ip', '未知 IP')
        preferred_port = data.get('port', None)
        role = data.get('role', 'worker')
        dingtalk_id = data.get('dingtalk_id', '')
        
        # 加载节点数据
        nodes_data = load_nodes()
        
        # 生成龙虾 ID
        lobster_id = generate_lobster_id(nodes_data)
        
        # 分配端口
        port = find_available_port(nodes_data, preferred_port)
        
        # 生成配置
        config = generate_config(lobster_id, port, name, ip, role)
        config['dingtalk_id'] = dingtalk_id
        
        # 保存配置
        config_file = os.path.join(CONFIG_DIR, f"{lobster_id}.json")
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 生成安装脚本
        install_script = generate_install_script(lobster_id, port)
        install_file = os.path.join(INSTALL_DIR, f"install-{lobster_id}.sh")
        with open(install_file, 'w', encoding='utf-8') as f:
            f.write(install_script)
        os.chmod(install_file, 0o755)
        
        # 添加到节点列表
        node_entry = {
            "lobster_id": lobster_id,
            "name": name,
            "ip": ip,
            "port": port,
            "role": role,
            "dingtalk_id": dingtalk_id,
            "status": "pending",
            "joined_at": datetime.now().isoformat()
        }
        nodes_data['nodes'].append(node_entry)
        save_nodes(nodes_data)
        
        logger.info(f"新节点加入：{lobster_id} ({name}) - IP: {ip}, 端口：{port}")
        
        # 返回响应
        return jsonify({
            "success": True,
            "lobster_id": lobster_id,
            "port": port,
            "config_url": f"http://47.93.6.57:8001/config/{lobster_id}",
            "install_url": f"http://47.93.6.57:8001/install/{lobster_id}",
            "install_command": f"wget http://47.93.6.57:8001/install/{lobster_id} && bash install-{lobster_id}.sh",
            "message": f"龙虾节点已注册，请执行安装命令"
        }), 200
        
    except Exception as e:
        logger.error(f"加入失败：{e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/config/<lobster_id>', methods=['GET'])
def get_config(lobster_id: str):
    """获取节点配置"""
    config_file = os.path.join(CONFIG_DIR, f"{lobster_id}.json")
    if not os.path.exists(config_file):
        return jsonify({"success": False, "error": "配置不存在"}), 404
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    return jsonify(config), 200

@app.route('/install/<lobster_id>', methods=['GET'])
def get_install_script(lobster_id: str):
    """下载安装脚本"""
    install_file = os.path.join(INSTALL_DIR, f"install-{lobster_id}.sh")
    if not os.path.exists(install_file):
        return jsonify({"success": False, "error": "安装脚本不存在"}), 404
    
    with open(install_file, 'r', encoding='utf-8') as f:
        script = f.read()
    
    return script, 200, {'Content-Type': 'text/bash'}

@app.route('/nodes', methods=['GET'])
def get_nodes():
    """查看所有已注册节点"""
    nodes_data = load_nodes()
    return jsonify(nodes_data), 200

@app.route('/status', methods=['GET'])
def get_status():
    """查看龙虾网络状态"""
    nodes_data = load_nodes()
    
    status = {
        "total_nodes": len(nodes_data['nodes']),
        "next_id": nodes_data['next_id'],
        "nodes": []
    }
    
    for node in nodes_data['nodes']:
        lobster_id = node['lobster_id']
        port = node['port']
        
        # 尝试健康检查
        try:
            import requests as req
            resp = req.get(f"http://{node['ip']}:{port}/health", timeout=5)
            if resp.status_code == 200:
                node['status'] = 'online'
            else:
                node['status'] = 'offline'
        except:
            node['status'] = 'offline'
        
        status['nodes'].append(node)
    
    return jsonify(status), 200

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "service": "lobster-join-api"}), 200

# ==================== 主函数 ====================
def main():
    parser = argparse.ArgumentParser(description='🦞 龙虾网络自助加入 API')
    parser.add_argument('--port', type=int, default=8001, help='监听端口')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='监听地址')
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    logger.info(f"🦞 龙虾网络自助加入 API 启动，监听 {args.host}:{args.port}")
    logger.info(f"📋 加入链接：http://{args.host}:{args.port}/join")
    
    app.run(host=args.host, port=args.port, debug=False)

if __name__ == '__main__':
    main()
