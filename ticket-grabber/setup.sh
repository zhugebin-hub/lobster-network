#!/bin/bash
# 大麦抢票助手 - Ubuntu 一键安装脚本
# 在 Ubuntu VM 中运行: bash setup.sh

set -e

echo "======================================"
echo "🎫 大麦抢票助手 - 安装脚本"
echo "======================================"

# 检查是否是 Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo "⚠️  检测到非 Ubuntu 系统，但继续安装..."
fi

# 1. 安装系统依赖
echo ""
echo "📦 安装系统依赖..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv xvfb curl

# 2. 创建虚拟环境
echo ""
echo "🐍 创建 Python 虚拟环境..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate

# 3. 安装 Python 包
echo ""
echo "📚 安装 Python 依赖..."
pip install --upgrade pip
pip install flask playwright

# 4. 安装 Playwright 浏览器
echo ""
echo "🌐 安装 Chromium 浏览器..."
playwright install chromium

# 5. 安装系统依赖（Playwright 需要）
echo ""
echo "🔧 安装 Playwright 系统依赖..."
playwright install-deps chromium

# 6. 完成
echo ""
echo "======================================"
echo "✅ 安装完成！"
echo "======================================"
echo ""
echo "📋 启动方式："
echo "   cd $SCRIPT_DIR"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 然后在浏览器打开: http://localhost:5000"
echo ""
echo "💡 提示："
echo "   - 如果 VM 没有桌面环境，需要安装 VNC 或远程桌面"
echo "   - 因为抢票需要显示浏览器窗口（手动登录大麦）"
echo ""
