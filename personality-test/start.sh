#!/bin/bash

echo "🦞 性格测试应用 - 启动脚本"
echo "=========================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未检测到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本：$(node -v)"

# 初始化后端
echo ""
echo "📦 正在安装后端依赖..."
cd backend
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "🗄️  正在初始化数据库..."
npm run init-db

# 安装前端
echo ""
echo "📦 正在安装前端依赖..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "🚀 启动说明："
echo ""
echo "终端 1 - 启动后端："
echo "  cd backend"
echo "  npm start"
echo ""
echo "终端 2 - 启动前端："
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "然后访问：http://localhost:5173"
echo ""
