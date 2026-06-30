#!/bin/bash

# 学校食堂菜单管理系统 - 一键启动脚本 (Python 版)

echo "🍽️  学校食堂菜单管理系统 (Python 版)"
echo "================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到 Python3，请先安装 Python 3.8+"
    echo "   Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "   CentOS: sudo yum install python3 python3-pip"
    exit 1
fi

echo "✅ Python 版本：$(python3 --version)"

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
pip install -r requirements.txt -q

# 检查数据库
if [ ! -f "../database/canteen.db" ]; then
    echo "🗄️  初始化数据库..."
    python3 app.py init-db
fi

echo ""
echo "================================"
echo "🚀 启动服务..."
echo ""
echo "访问地址：http://localhost:5000"
echo "默认账号：admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================"
echo ""

# 启动服务
python3 app.py
