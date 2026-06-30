#!/bin/bash
# OpenClaw 网页端访问测试脚本

echo "=========================================="
echo "🌐 OpenClaw 网页端访问测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查网关状态
echo "1️⃣  检查 OpenClaw 网关状态..."
if openclaw gateway status > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 网关运行正常${NC}"
    openclaw gateway status | grep -E "(Gateway|Runtime|Dashboard)"
else
    echo -e "${RED}✗ 网关未运行${NC}"
    echo "   启动命令：openclaw gateway start"
    exit 1
fi
echo ""

# 2. 获取服务器 IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "2️⃣  服务器 IP: ${SERVER_IP}"
echo ""

# 3. 测试本地访问
echo "3️⃣  测试本地访问..."
LOCAL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11676/22131ecf/)
if [ "$LOCAL_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ 本地访问正常 (HTTP $LOCAL_STATUS)${NC}"
else
    echo -e "${RED}✗ 本地访问异常 (HTTP $LOCAL_STATUS)${NC}"
fi
echo ""

# 4. 测试局域网访问
echo "4️⃣  测试局域网访问..."
LAN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://${SERVER_IP}:11676/22131ecf/)
if [ "$LAN_STATUS" = "200" ]; then
    echo -e "${GREEN}✓ 局域网访问正常 (HTTP $LAN_STATUS)${NC}"
else
    echo -e "${YELLOW}⚠ 局域网访问异常 (HTTP $LAN_STATUS)${NC}"
    echo "   可能原因：防火墙阻止 / 绑定模式不是 LAN"
    echo "   解决方法："
    echo "   sudo ufw allow 11676/tcp"
    echo "   openclaw gateway config set gateway.bind=lan"
fi
echo ""

# 5. 显示访问地址
echo "=========================================="
echo "📍 访问地址"
echo "=========================================="
echo ""
echo "本机访问："
echo "  http://localhost:11676/22131ecf/"
echo ""
echo "局域网访问："
echo "  http://${SERVER_IP}:11676/22131ecf/"
echo ""
echo "带令牌访问："
echo "  http://${SERVER_IP}:11676/22131ecf/?token=728495fa554d2117e44dea4bfcf493d9"
echo ""

# 6. 二维码（可选）
echo "=========================================="
echo "📱 手机访问"
echo "=========================================="
echo ""
echo "1. 手机连接同一 WiFi"
echo "2. 浏览器访问：http://${SERVER_IP}:11676/22131ecf/"
echo "3. 或扫描二维码（需要安装 qrencode）："
echo ""
if command -v qrencode &> /dev/null; then
    qrencode -t ANSIUTF8 "http://${SERVER_IP}:11676/22131ecf/"
else
    echo "   [未安装 qrencode，跳过二维码显示]"
    echo "   安装：sudo apt install qrencode"
fi
echo ""

# 7. 常用命令
echo "=========================================="
echo "🔧 常用命令"
echo "=========================================="
echo ""
echo "查看状态：  openclaw gateway status"
echo "重启服务：  openclaw gateway restart"
echo "查看日志：  tail -f /tmp/openclaw/openclaw-*.log"
echo "修改配置：  openclaw gateway config set <配置项>=<值>"
echo ""

echo "=========================================="
echo "✅ 测试完成！"
echo "=========================================="
