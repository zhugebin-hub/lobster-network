#!/bin/bash
# 🦞 小龙虾网络 · 防火墙配置脚本
# 功能：开放 8001/8002 端口，配置频率限制

set -e

echo "🦞 小龙虾网络 · 防火墙配置脚本"
echo "================================"

# 检查权限
if [ "$EUID" -ne 0 ]; then 
  echo "❌ 请使用 sudo 运行此脚本"
  exit 1
fi

# 检查 firewalld
if ! command -v firewall-cmd &> /dev/null; then
  echo "❌ 未找到 firewall-cmd，请先安装 firewalld"
  exit 1
fi

# 开放端口
echo "🔓 开放 8001 端口 (动态注册 API)..."
firewall-cmd --permanent --add-port=8001/tcp

echo "🔓 开放 8002 端口 (主备同步)..."
firewall-cmd --permanent --add-port=8002/tcp

# 配置频率限制
echo "⚡ 配置频率限制 (30次/分钟)..."
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port protocol="tcp" port="8001" limit value="30/m" accept'
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port protocol="tcp" port="8002" limit value="30/m" accept'

# 重载防火墙
echo "🔄 重载防火墙配置..."
firewall-cmd --reload

# 验证
echo "✅ 验证端口开放状态..."
firewall-cmd --list-ports | grep -q "8001/tcp" && echo "   ✅ 8001/tcp 已开放"
firewall-cmd --list-ports | grep -q "8002/tcp" && echo "   ✅ 8002/tcp 已开放"

echo ""
echo "🎉 防火墙配置完成！"
echo "📋 下一步："
echo "   1. 在阿里云控制台放行 8001/8002 端口"
echo "   2. 启动动态注册服务: python3 lobster_join_api.py --port=8001 --role=primary"
echo "   3. 启动主备同步: python3 registry_sync.py --peer=http://60.205.139.51:8002 --interval=300"
