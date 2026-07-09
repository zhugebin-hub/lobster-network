#!/usr/bin/env python3
"""小龙虾网络 Dashboard 服务器 - 支持端口复用"""

import http.server
import socketserver
import os

PORT = 8080
HOST = "0.0.0.0"

# 切换到 web 目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 如果访问根路径，返回 index.html
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

with ReuseAddrTCPServer((HOST, PORT), MyHandler) as httpd:
    print(f" 小龙虾网络 Dashboard 服务器已启动")
    print(f"📍 监听地址：http://{HOST}:{PORT}")
    print(f" 入口页面：http://localhost:{PORT}/")
    print(f"📊 网络总览：http://localhost:{PORT}/dashboard.html")
    print(f"📚 学习项目：http://localhost:{PORT}/learning_dashboard.html")
    print(f"📈 运行监控：http://localhost:{PORT}/monitor_dashboard.html")
    print(f"📝 论文写作指挥中心：http://localhost:{PORT}/paper_dashboard.html")
    print(f"\n按 Ctrl+C 停止服务器")
    httpd.serve_forever()
