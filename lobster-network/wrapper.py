#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 龙虾池 Wrapper - Lobster Pool HTTP Wrapper
==========================================
功能：为 OpenClaw 实例提供 HTTP 接口，接收调度请求并转发到钉钉群

部署方式：
    python3 wrapper.py --port=8001 --lobster-id=lobster-002
"""

import argparse
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json
import os
from datetime import datetime
from flask import Flask, request, jsonify

# ==================== 配置区 ====================
# 钉钉群配置
DINGTALK_ACCESS_TOKEN = "e86678fcb138954f5c84df023eb424ae805f97e5c013889a8432aad8855fd719"
DINGTALK_SECRET = "SEC4e4e47b29c07e61ad2354a377c6ee747241f171107ffedd64c53af816ab21cd0"

# 请求队列文件
PENDING_REQUESTS_FILE = os.path.expanduser("~/lobster-tasks/pending/requests.json")
RESPONSES_FILE = os.path.expanduser("~/lobster-tasks/done/responses.json")

# ==================== Flask 应用 ====================
app = Flask(__name__)

# ==================== 日志配置 ====================
def setup_logger(lobster_id: str):
    logger = logging.getLogger(f"wrapper-{lobster_id}")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(f'🦞 %(asctime)s [{lobster_id}] %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

# ==================== 工具函数 ====================
def generate_sign(secret: str) -> tuple:
    """生成钉钉加签"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign

def send_to_dingtalk(msg: str, at_user_ids: list = None, is_at_all: bool = False) -> dict:
    """发送消息到钉钉群"""
    timestamp, sign = generate_sign(DINGTALK_SECRET)
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_ACCESS_TOKEN}&timestamp={timestamp}&sign={sign}'
    
    body = {
        "at": {
            "isAtAll": is_at_all,
            "atUserIds": at_user_ids or []
        },
        "text": {
            "content": msg
        },
        "msgtype": "text"
    }
    
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, json=body, headers=headers, timeout=10)
    
    if resp.status_code == 200:
        result = resp.json()
        if result.get("errcode") == 0:
            return {"success": True, "data": result}
        else:
            return {"success": False, "error": result}
    else:
        return {"success": False, "error": f"HTTP {resp.status_code}"}

def ensure_dirs():
    """确保目录存在"""
    os.makedirs(os.path.dirname(PENDING_REQUESTS_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(RESPONSES_FILE), exist_ok=True)

def load_json_file(filepath: str, default: dict = None) -> dict:
    """加载 JSON 文件"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.warning(f"读取文件失败：{e}")
    return default or {"requests": [], "responses": []}

def save_json_file(filepath: str, data: dict):
    """保存 JSON 文件"""
    ensure_dirs()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==================== API 路由 ====================
@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "lobster_id": app.config['LOBSTER_ID']})

@app.route('/invoke', methods=['POST'])
def invoke():
    """
    接收协作请求
    格式：{"from": "lobster-001", "to": "lobster-002", "msg": "xxx", "intent": "coordination"}
    """
    data = request.json
    logger = app.config['LOGGER']
    lobster_id = app.config['LOBSTER_ID']
    
    if not data:
        return jsonify({"error": "no json"}), 400
    
    from_lobster = data.get('from', 'unknown')
    to_lobster = data.get('to', lobster_id)
    msg = data.get('msg', '')
    intent = data.get('intent', 'general')
    request_id = data.get('request_id', f"req_{int(time.time())}")
    
    logger.info(f"📥 收到请求：{from_lobster} → {to_lobster} ({intent})")
    
    # 1. 写入请求队列
    requests_data = load_json_file(PENDING_REQUESTS_FILE)
    req = {
        "id": request_id,
        "from": from_lobster,
        "to": to_lobster,
        "msg": msg,
        "intent": intent,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "received_at": time.time()
    }
    requests_data["requests"].append(req)
    save_json_file(PENDING_REQUESTS_FILE, requests_data)
    
    # 2. 发送到钉钉群（广播）
    formatted_msg = f"[LOBSTER-MSG] from={from_lobster}&to={to_lobster}&intent={intent}&msg={msg}"
    result = send_to_dingtalk(formatted_msg)
    
    if result.get("success"):
        logger.info(f"✅ 已转发到钉钉群：{request_id}")
        return jsonify({
            "status": "ok",
            "request_id": request_id,
            "dingtalk": "sent"
        })
    else:
        logger.error(f"❌ 钉钉发送失败：{result}")
        return jsonify({
            "status": "ok",  # 请求已接收，但钉钉发送失败
            "request_id": request_id,
            "dingtalk": "failed",
            "error": result.get("error")
        }), 200

@app.route('/response', methods=['POST'])
def response():
    """
    提交响应结果
    格式：{"request_id": "req_xxx", "from": "lobster-002", "to": "lobster-001", "result": "xxx"}
    """
    data = request.json
    logger = app.config['LOGGER']
    
    if not data:
        return jsonify({"error": "no json"}), 400
    
    request_id = data.get('request_id')
    from_lobster = data.get('from', app.config['LOBSTER_ID'])
    to_lobster = data.get('to', 'lobster-001')
    result = data.get('result', '')
    status = data.get('status', 'completed')
    
    logger.info(f"📤 提交响应：{request_id} {from_lobster} → {to_lobster}")
    
    # 1. 更新请求状态
    requests_data = load_json_file(PENDING_REQUESTS_FILE)
    for req in requests_data.get("requests", []):
        if req["id"] == request_id:
            req["status"] = status
            req["completed_at"] = datetime.now().isoformat()
            break
    save_json_file(PENDING_REQUESTS_FILE, requests_data)
    
    # 2. 写入响应文件
    responses_data = load_json_file(RESPONSES_FILE)
    resp = {
        "request_id": request_id,
        "from": from_lobster,
        "to": to_lobster,
        "result": result,
        "status": status,
        "created_at": datetime.now().isoformat()
    }
    responses_data["responses"].append(resp)
    save_json_file(RESPONSES_FILE, responses_data)
    
    # 3. 发送到钉钉群
    formatted_msg = f"[LOBSTER-RESP] id={request_id}&from={from_lobster}&to={to_lobster}&status={status}&result={result}"
    send_to_dingtalk(formatted_msg)
    
    logger.info(f"✅ 响应已提交：{request_id}")
    return jsonify({"status": "ok"})

@app.route('/pending', methods=['GET'])
def get_pending():
    """获取待处理请求"""
    requests_data = load_json_file(PENDING_REQUESTS_FILE)
    pending = [r for r in requests_data.get("requests", []) if r.get("status") == "pending"]
    return jsonify({"pending": pending, "count": len(pending)})

@app.route('/status', methods=['GET'])
def get_status():
    """获取当前状态"""
    requests_data = load_json_file(PENDING_REQUESTS_FILE)
    responses_data = load_json_file(RESPONSES_FILE)
    
    all_requests = requests_data.get("requests", [])
    pending = [r for r in all_requests if r.get("status") == "pending"]
    completed = [r for r in all_requests if r.get("status") == "completed"]
    
    return jsonify({
        "lobster_id": app.config['LOBSTER_ID'],
        "pending_count": len(pending),
        "completed_count": len(completed),
        "total_responses": len(responses_data.get("responses", []))
    })

# ==================== 主函数 ====================
def main():
    parser = argparse.ArgumentParser(description="🦞 龙虾池 Wrapper")
    parser.add_argument('--port', type=int, default=8001, help='监听端口')
    parser.add_argument('--lobster-id', dest='lobster_id', default='lobster-002', help='龙虾 ID')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址')
    
    args = parser.parse_args()
    
    # 配置 Flask 应用
    app.config['LOBSTER_ID'] = args.lobster_id
    app.config['LOGGER'] = setup_logger(args.lobster_id)
    
    logger = app.config['LOGGER']
    logger.info(f"🚀 Wrapper 启动：{args.lobster_id} 监听 {args.host}:{args.port}")
    logger.info(f"📁 请求队列：{PENDING_REQUESTS_FILE}")
    logger.info(f"📁 响应文件：{RESPONSES_FILE}")
    
    # 确保目录存在
    ensure_dirs()
    
    # 启动 Flask
    app.run(host=args.host, port=args.port, debug=False, threaded=True)

if __name__ == '__main__':
    main()
