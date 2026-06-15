#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 龙虾池调度核心 - Lobster Pool Scheduler
=====================================
功能：作为龙虾池的中央调度器，接收其他龙虾的协作请求，转发给目标龙虾

使用方式：
    python3 lobster_scheduler.py --action=send --to=lobster-002 --msg="请求协作"
    python3 lobster_scheduler.py --action=check --pending  # 检查待处理请求
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

# ==================== 配置区 ====================
# 钉钉群配置（已配置）
DINGTALK_ACCESS_TOKEN = "e86678fcb138954f5c84df023eb424ae805f97e5c013889a8432aad8855fd719"
DINGTALK_SECRET = "SEC4e4e47b29c07e61ad2354a377c6ee747241f171107ffedd64c53af816ab21cd0"

# 龙虾池配置
LOBSTER_POOL_CONFIG = {
    "lobster-001": {"name": "小龙虾", "role": "scheduler", "status": "active"},
    "lobster-002": {"name": "虾尔 02", "role": "worker", "status": "pending"},
    "lobster-003": {"name": "虾尔 03", "role": "worker", "status": "pending"},
    # ... 其他龙虾
}

# 请求队列文件
PENDING_REQUESTS_FILE = os.path.expanduser("~/lobster-tasks/pending/requests.json")
RESPONSES_FILE = os.path.expanduser("~/lobster-tasks/done/responses.json")

# ==================== 日志配置 ====================
def setup_logger():
    logger = logging.getLogger("lobster-scheduler")
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('🦞 %(asctime)s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logger()

# ==================== 钉钉发送函数 ====================
def generate_sign(secret: str) -> tuple:
    """生成钉钉加签"""
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f'{timestamp}\n{secret}'
    hmac_code = hmac.new(secret.encode('utf-8'), string_to_sign.encode('utf-8'), digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return timestamp, sign

def send_to_dingtalk(msg: str, at_user_ids: list = None, at_mobiles: list = None, is_at_all: bool = False) -> dict:
    """发送消息到钉钉群"""
    timestamp, sign = generate_sign(DINGTALK_SECRET)
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_ACCESS_TOKEN}&timestamp={timestamp}&sign={sign}'
    
    body = {
        "at": {
            "isAtAll": is_at_all,
            "atUserIds": at_user_ids or [],
            "atMobiles": at_mobiles or []
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
            logger.info(f"✅ 消息发送成功")
            return {"success": True, "data": result}
        else:
            logger.error(f"❌ 钉钉返回错误：{result}")
            return {"success": False, "error": result}
    else:
        logger.error(f"❌ HTTP 错误：{resp.status_code} - {resp.text}")
        return {"success": False, "error": f"HTTP {resp.status_code}"}

def send_lobster_message(from_lobster: str, to_lobster: str, msg: str, intent: str = "general") -> dict:
    """
    发送龙虾间协作消息
    格式：[LOBSTER-MSG] from=lobster-001&to=lobster-002&intent=general&msg=xxx
    """
    formatted_msg = f"[LOBSTER-MSG] from={from_lobster}&to={to_lobster}&intent={intent}&msg={msg}"
    logger.info(f"📤 准备发送：{from_lobster} → {to_lobster}")
    return send_to_dingtalk(formatted_msg)

# ==================== 请求队列管理 ====================
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
        logger.warning(f"读取文件失败：{e}")
    return default or {}

def save_json_file(filepath: str, data: dict):
    """保存 JSON 文件"""
    ensure_dirs()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 已保存到：{filepath}")

def create_request(request_id: str, from_lobster: str, to_lobster: str, msg: str, intent: str = "general") -> dict:
    """创建协作请求"""
    requests_data = load_json_file(PENDING_REQUESTS_FILE, {"requests": []})
    
    request = {
        "id": request_id,
        "from": from_lobster,
        "to": to_lobster,
        "msg": msg,
        "intent": intent,
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    requests_data["requests"].append(request)
    save_json_file(PENDING_REQUESTS_FILE, requests_data)
    logger.info(f"📝 已创建请求：{request_id}")
    return request

def check_pending_requests() -> list:
    """检查待处理请求"""
    requests_data = load_json_file(PENDING_REQUESTS_FILE, {"requests": []})
    pending = [r for r in requests_data.get("requests", []) if r.get("status") == "pending"]
    return pending

# ==================== 主函数 ====================
def main():
    parser = argparse.ArgumentParser(description="🦞 龙虾池调度器")
    parser.add_argument('--action', required=True, choices=['send', 'check', 'create', 'status'],
                        help='操作类型')
    parser.add_argument('--from', dest='from_lobster', default='lobster-001',
                        help='源龙虾 ID')
    parser.add_argument('--to', dest='to_lobster', help='目标龙虾 ID')
    parser.add_argument('--msg', default='你好，我是小龙虾', help='消息内容')
    parser.add_argument('--intent', default='general', 
                        choices=['general', 'coordination', 'query', 'response'],
                        help='意图类型')
    parser.add_argument('--request-id', dest='request_id', help='请求 ID')
    
    args = parser.parse_args()
    
    if args.action == 'send':
        # 直接发送消息到钉钉群
        if not args.to_lobster:
            logger.error("❌ 需要指定 --to 参数")
            return
        result = send_lobster_message(args.from_lobster, args.to_lobster, args.msg, args.intent)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == 'create':
        # 创建协作请求（写入队列）
        if not args.to_lobster:
            logger.error("❌ 需要指定 --to 参数")
            return
        request_id = args.request_id or f"req_{int(time.time())}"
        request = create_request(request_id, args.from_lobster, args.to_lobster, args.msg, args.intent)
        print(json.dumps(request, ensure_ascii=False, indent=2))
        
    elif args.action == 'check':
        # 检查待处理请求
        pending = check_pending_requests()
        logger.info(f"📋 待处理请求：{len(pending)} 个")
        for req in pending:
            print(f"  - {req['id']}: {req['from']} → {req['to']} ({req['intent']})")
        print(json.dumps(pending, ensure_ascii=False, indent=2))
        
    elif args.action == 'status':
        # 显示龙虾池状态
        logger.info("🦞 龙虾池状态")
        print(json.dumps(LOBSTER_POOL_CONFIG, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
