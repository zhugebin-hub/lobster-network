#!/usr/bin/env python3
"""
🦞 MCP Router Server 快速启动脚本
使用方式：
  python3 start_router.py
"""
import subprocess
import sys
import os

SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_router_server.py")
print(f"🦞 启动 MCP Router Server...")
print(f"   脚本: {SCRIPT}")
print(f"   数据库: /home/admin/.openclaw/workspace/lobster-ecosystem/router/router.db")
print()
print("💡 提示：作为 stdio MCP Server，需通过 MCP Client 连接使用")
print("   或使用 npx 启动: npx -y @modelcontextprotocol/server <path>")
print()

os.execv(sys.executable, [sys.executable, SCRIPT])
