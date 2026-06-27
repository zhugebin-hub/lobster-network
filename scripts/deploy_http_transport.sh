#!/bin/bash
# -*- coding: utf-8 -*-
"""
v0.6.0 HTTP传输层部署脚本
功能：在各服务器上部署HTTP传输层服务

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
HTTP_PORT=8199
SERVICE_NAME="lobster-http-transport"
WORK_DIR="/home/admin/lobster-network"

echo "========================================"
echo "🌐 v0.6.0 HTTP传输层部署脚本"
echo "========================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python3未安装${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python3已安装: $(python3 --version)${NC}"
echo ""

# 检查端口是否可用
if lsof -Pi :$HTTP_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠ 端口 $HTTP_PORT 已被占用${NC}"
    echo "请先停止占用该端口的服务"
    exit 1
fi

echo -e "${GREEN}✓ 端口 $HTTP_PORT 可用${NC}"
echo ""

# 创建HTTP传输服务
cat > /tmp/http_transport_service.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.6.0 HTTP传输层服务
功能：提供节点间实时通信能力

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

import json
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
from typing import Dict, List, Any

# 配置
PORT = 8199
DATA_DIR = "/home/admin/lobster-network/data/http_transport"
NODE_ID = os.environ.get("NODE_ID", "unknown")
NODE_NAME = os.environ.get("NODE_NAME", "unknown")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class TransportHandler(BaseHTTPRequestHandler):
    """HTTP传输处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == "/api/v1/heartbeat":
            self._handle_heartbeat()
        elif self.path == "/api/v1/discover":
            self._handle_discover()
        elif self.path.startswith("/api/v1/receive"):
            self._handle_receive()
        else:
            self._send_response(404, {"error": "Not found"})
    
    def do_POST(self):
        """处理POST请求"""
        if self.path == "/api/v1/send":
            self._handle_send()
        else:
            self._send_response(404, {"error": "Not found"})
    
    def _handle_heartbeat(self):
        """处理心跳请求"""
        response = {
            "node_id": NODE_ID,
            "node_name": NODE_NAME,
            "status": "online",
            "timestamp": datetime.now().isoformat(),
        }
        self._send_response(200, response)
    
    def _handle_discover(self):
        """处理节点发现请求"""
        nodes_file = os.path.join(DATA_DIR, "nodes.json")
        if os.path.exists(nodes_file):
            with open(nodes_file, 'r') as f:
                nodes = json.load(f)
        else:
            nodes = []
        self._send_response(200, {"nodes": nodes})
    
    def _handle_send(self):
        """处理消息发送请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data.decode('utf-8'))
        
        # 保存消息
        messages_file = os.path.join(DATA_DIR, "messages.json")
        messages = []
        if os.path.exists(messages_file):
            with open(messages_file, 'r') as f:
                messages = json.load(f)
        
        message["received_at"] = datetime.now().isoformat()
        message["from_node"] = NODE_ID
        messages.append(message)
        
        with open(messages_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        self._send_response(200, {"status": "received", "message_id": message.get("id")})
    
    def _handle_receive(self):
        """处理消息接收请求"""
        messages_file = os.path.join(DATA_DIR, "messages.json")
        if os.path.exists(messages_file):
            with open(messages_file, 'r') as f:
                messages = json.load(f)
        else:
            messages = []
        
        self._send_response(200, {"messages": messages})
    
    def _send_response(self, status_code, data):
        """发送HTTP响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[{datetime.now().isoformat()}] {format % args}")

def main():
    """启动HTTP服务器"""
    server = HTTPServer(('0.0.0.0', PORT), TransportHandler)
    print(f"🌐 HTTP传输层服务启动: http://0.0.0.0:{PORT}")
    print(f"📡 节点ID: {NODE_ID}")
    print(f"📡 节点名称: {NODE_NAME}")
    print(f"📂 数据目录: {DATA_DIR}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务停止")
        server.shutdown()

if __name__ == "__main__":
    main()
EOF

# 创建systemd服务文件
cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=Lobster Network HTTP Transport Service
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${WORK_DIR}
Environment=NODE_ID=$(hostname)
Environment=NODE_NAME=$(hostname)
ExecStart=/usr/bin/python3 /tmp/http_transport_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 安装服务
echo "📦 安装HTTP传输层服务..."
sudo cp /tmp/${SERVICE_NAME}.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

# 等待服务启动
sleep 3

# 检查服务状态
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo -e "${GREEN}✓ HTTP传输层服务已启动${NC}"
    echo -e "${GREEN}  地址: http://0.0.0.0:${HTTP_PORT}${NC}"
    echo -e "${GREEN}  节点ID: $(hostname)${NC}"
else
    echo -e "${RED}✗ HTTP传输层服务启动失败${NC}"
    echo "请检查日志: sudo journalctl -u ${SERVICE_NAME} -n 50"
    exit 1
fi

# 测试服务
echo ""
echo "🧪 测试服务..."
RESPONSE=$(curl -s http://localhost:${HTTP_PORT}/api/v1/heartbeat)
echo "  心跳响应: $RESPONSE"

echo ""
echo "========================================"
echo "✅ HTTP传输层部署完成"
echo "========================================"
echo ""
echo "📋 管理命令："
echo "  启动服务: sudo systemctl start ${SERVICE_NAME}"
echo "  停止服务: sudo systemctl stop ${SERVICE_NAME}"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"
echo "  查看状态: sudo systemctl status ${SERVICE_NAME}"
echo "  查看日志: sudo journalctl -u ${SERVICE_NAME} -f"
