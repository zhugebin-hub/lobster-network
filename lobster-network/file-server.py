#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 龙虾池文件服务器 - 提供技能包下载
=====================================
使用方式：python3 file-server.py --port=9000
"""

import argparse
import http.server
import socketserver
import os
import json
from datetime import datetime

# 技能包路径
SKILL_PACKAGE = os.path.expanduser("~/.openclaw/workspace/lobster-network-skill.tar.gz")
INSTALL_SCRIPT = os.path.expanduser("~/.openclaw/workspace/lobster-network/install-lobster-skill.sh")

class LobsterFileHandler(http.server.SimpleHTTPRequestHandler):
    """自定义文件处理器，提供友好的下载页面"""
    
    def do_GET(self):
        if self.path == '/':
            self.send_index_page()
        elif self.path == '/health':
            self.send_health()
        elif self.path == '/api/info':
            self.send_api_info()
        else:
            super().do_GET()
    
    def send_index_page(self):
        """发送下载页面"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 龙虾池技能包下载</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #ff6b6b, #feca57); padding: 30px; border-radius: 10px; color: white; text-align: center; }}
        .file-list {{ margin: 30px 0; }}
        .file-item {{ background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ff6b6b; }}
        .file-name {{ font-size: 18px; font-weight: bold; color: #333; }}
        .file-size {{ color: #666; margin: 10px 0; }}
        .download-btn {{ display: inline-block; background: #ff6b6b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }}
        .download-btn:hover {{ background: #ee5a5a; }}
        .install-cmd {{ background: #2d3436; color: #feca57; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }}
        .status {{ background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦞 龙虾池技能包下载中心</h1>
        <p>Lobster Pool Skill Package Download</p>
    </div>
    
    <div class="status">
        ✅ 服务运行中 | 龙虾 ID: lobster-001 (调度中枢)
    </div>
    
    <div class="file-list">
        <h2>📦 可下载文件</h2>
        
        <div class="file-item">
            <div class="file-name">🦞 龙虾池技能包</div>
            <div class="file-size">文件名：lobster-network-skill.tar.gz | 大小：{self.get_file_size(SKILL_PACKAGE)}</div>
            <div class="file-size">内容：wrapper.py, 部署脚本，systemd 配置，完整文档 (SKILL.md, INSTALL.md, README.md 等)</div>
            <a href="/lobster-network-skill.tar.gz" class="download-btn">⬇️ 下载技能包</a>
        </div>
        
        <div class="file-item">
            <div class="file-name">🔧 一键安装脚本</div>
            <div class="file-size">文件名：install-lobster-skill.sh | 大小：{self.get_file_size(INSTALL_SCRIPT)}</div>
            <div class="file-size">用途：自动安装技能包、配置环境、启动服务</div>
            <a href="/install-lobster-skill.sh" class="download-btn">⬇️ 下载安装脚本</a>
        </div>
    </div>
    
    <div>
        <h2>🚀 快速安装命令</h2>
        <div class="install-cmd">
# 1. 下载技能包和安装脚本
wget http://{self.get_server_ip()}:9000/lobster-network-skill.tar.gz
wget http://{self.get_server_ip()}:9000/install-lobster-skill.sh

# 2. 添加执行权限
chmod +x install-lobster-skill.sh

# 3. 安装（替换为你的龙虾 ID 和端口）
bash install-lobster-skill.sh --lobster-id=lobster-002 --port=8002

# 4. 验证
curl http://127.0.0.1:8002/health
        </div>
    </div>
    
    <div style="margin-top: 30px; padding: 20px; background: #e3f2fd; border-radius: 8px;">
        <h3>📚 文档说明</h3>
        <p>技能包内包含完整文档：</p>
        <ul>
            <li><strong>INSTALL.md</strong> - 快速安装指南</li>
            <li><strong>README.md</strong> - 使用说明</li>
            <li><strong>DEPLOYMENT.md</strong> - 部署文档</li>
            <li><strong>SKILL.md</strong> - 技能说明</li>
            <li><strong>SHARE.md</strong> - 分享模板</li>
        </ul>
    </div>
    
    <footer style="margin-top: 50px; text-align: center; color: #666; padding: 20px; border-top: 1px solid #ddd;">
        🦞 龙虾池协作系统 | 有问题请在钉钉群「智能体小龙虾测试」提问
    </footer>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_health(self):
        """健康检查"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "status": "ok",
            "service": "lobster-file-server",
            "lobster_id": "lobster-001",
            "files": {
                "skill_package": os.path.exists(SKILL_PACKAGE),
                "install_script": os.path.exists(INSTALL_SCRIPT)
            },
            "timestamp": datetime.now().isoformat()
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def send_api_info(self):
        """API 信息"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {
            "service": "lobster-file-server",
            "version": "1.0.0",
            "endpoints": {
                "/": "下载页面（HTML）",
                "/health": "健康检查",
                "/api/info": "API 信息",
                "/lobster-network-skill.tar.gz": "技能包下载",
                "/install-lobster-skill.sh": "安装脚本下载"
            },
            "files": {
                "skill_package": {
                    "path": SKILL_PACKAGE,
                    "exists": os.path.exists(SKILL_PACKAGE),
                    "size": os.path.getsize(SKILL_PACKAGE) if os.path.exists(SKILL_PACKAGE) else 0
                },
                "install_script": {
                    "path": INSTALL_SCRIPT,
                    "exists": os.path.exists(INSTALL_SCRIPT),
                    "size": os.path.getsize(INSTALL_SCRIPT) if os.path.exists(INSTALL_SCRIPT) else 0
                }
            }
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def get_file_size(self, filepath):
        """获取文件大小（人类可读）"""
        if not os.path.exists(filepath):
            return "文件不存在"
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"
    
    def get_server_ip(self):
        """获取服务器 IP"""
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

def main():
    parser = argparse.ArgumentParser(description="🦞 龙虾池文件服务器")
    parser.add_argument('--port', type=int, default=9000, help='监听端口（默认：9000）')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址（默认：0.0.0.0）')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(SKILL_PACKAGE):
        print(f"❌ 技能包不存在：{SKILL_PACKAGE}")
        return
    
    if not os.path.exists(INSTALL_SCRIPT):
        print(f"❌ 安装脚本不存在：{INSTALL_SCRIPT}")
        return
    
    # 启动服务器
    with socketserver.TCPServer((args.host, args.port), LobsterFileHandler) as httpd:
        print(f"🦞 文件服务器启动成功！")
        print(f"📍 监听地址：http://{args.host}:{args.port}")
        print(f"📦 技能包：{SKILL_PACKAGE}")
        print(f"🔧 安装脚本：{INSTALL_SCRIPT}")
        print(f"")
        print(f"🌐 访问下载页面：http://localhost:{args.port}/")
        print(f"❤️  健康检查：http://localhost:{args.port}/health")
        print(f"")
        print(f"按 Ctrl+C 停止服务")
        httpd.serve_forever()

if __name__ == '__main__':
    main()
