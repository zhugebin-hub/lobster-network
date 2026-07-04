#!/usr/bin/env python3
"""
信电学院 AI 知识问答系统 - 钉钉机器人对接层
接收钉钉消息 → 调用 QA 系统 → 返回答案
"""

import json
import os
import sys
import time
import hmac
import hashlib
import base64
import requests
from typing import Dict, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# 添加智能体层到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'agent-layer'))
from main import XindianQASystem


class DingTalkBot:
    """钉钉机器人"""
    
    def __init__(self, config_path: str = None):
        """初始化"""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dingtalk_config.json')
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.app_key = self.config['dingtalk']['app_key']
        self.app_secret = self.config['dingtalk']['app_secret']
        self.robot_code = self.config['dingtalk']['robot_code']
        
        # 初始化 QA 系统
        qa_config = os.path.expanduser(self.config['qa_system']['config_path'])
        self.qa_system = XindianQASystem(qa_config)
        
        # 访问令牌缓存
        self._access_token = None
        self._token_expire = 0
        
        print(f"✅ 钉钉机器人初始化成功")
        print(f"   AppKey: {self.app_key}")
    
    def get_access_token(self) -> str:
        """获取访问令牌"""
        now = time.time()
        if self._access_token and now < self._token_expire - 300:
            return self._access_token
        
        url = "https://api.dingtalk.com/v1.0/oauth/accessToken"
        payload = {
            "appKey": self.app_key,
            "appSecret": self.app_secret
        }
        
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            self._access_token = data['accessToken']
            self._token_expire = now + data.get('expireIn', 7200)
            return self._access_token
        
        raise Exception(f"获取 access_token 失败: {resp.text}")
    
    def get_auth_code(self, data: Dict) -> str:
        """从消息中提取认证码（用于用户识别）"""
        sender_id = data.get('senderId', '')
        sender_nick = data.get('senderNick', '')
        conversation_id = data.get('conversationId', '')
        return f"{sender_id}_{conversation_id}"
    
    def process_message(self, data: Dict) -> Dict:
        """
        处理钉钉消息
        
        Args:
            data: 钉钉消息数据
            
        Returns:
            回复数据
        """
        # 解析消息内容
        msg_type = data.get('msgtype', '')
        if msg_type != 'text':
            return {'text': {'content': '暂只支持文本消息'}, 'msgtype': 'text'}
        
        text_content = data.get('text', {}).get('content', '').strip()
        if not text_content:
            return {'text': {'content': '请输入您的问题'}, 'msgtype': 'text'}
        
        # 获取用户标识
        auth_code = self.get_auth_code(data)
        session_id = data.get('conversationId', 'default')
        user_id = data.get('senderId', 'anonymous')
        
        # 调用 QA 系统
        try:
            result = self.qa_system.process_query(text_content, session_id, user_id)
            answer = result['answer']
            
            # 截断过长的回答
            max_len = self.config['qa_system'].get('max_answer_length', 2000)
            if len(answer) > max_len:
                answer = answer[:max_len] + '\n\n（回答过长，已截断）'
            
            return {
                'text': {'content': answer},
                'msgtype': 'text'
            }
        except Exception as e:
            print(f"❌ QA 系统异常: {e}")
            return {
                'text': {'content': f'抱歉，系统出现错误：{str(e)}'},
                'msgtype': 'text'
            }
    
    def send_reply(self, outgoing_id: str, reply_data: Dict):
        """
        发送回复（通过钉钉 Outgoing API）
        
        Args:
            outgoing_id: 消息 ID
            reply_data: 回复数据
        """
        # 钉钉 Outgoing 模式直接返回 JSON 即可
        # 如果需要主动推送，使用以下 API：
        pass


class DingTalkHandler(BaseHTTPRequestHandler):
    """钉钉 Webhook 处理器"""
    
    def do_POST(self):
        """处理 POST 请求"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            print(f"📨 收到消息: {data.get('msgtype')} - {data.get('text', {}).get('content', '')}")
            
            # 处理消息
            reply = self.server.bot.process_message(data)
            
            # 返回回复
            response = json.dumps(reply, ensure_ascii=False)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ 处理消息异常: {e}")
            error_reply = json.dumps({
                'text': {'content': f'系统错误：{str(e)}'},
                'msgtype': 'text'
            }, ensure_ascii=False)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(error_reply.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(config: Dict = None):
    """启动 HTTP 服务器"""
    if config is None:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dingtalk_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    bot = DingTalkBot()
    server_config = config.get('server', {})
    
    server = HTTPServer(
        (server_config.get('host', '0.0.0.0'), server_config.get('port', 8900)),
        DingTalkHandler
    )
    server.bot = bot
    
    print(f"🚀 钉钉机器人服务已启动: {server_config.get('host', '0.0.0.0')}:{server_config.get('port', 8900)}")
    print(f"   Webhook 路径: {server_config.get('webhook_path', '/webhook/dingtalk')}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        server.shutdown()


if __name__ == '__main__':
    run_server()
