#!/bin/bash

echo "🦞 性格测试应用 - 一键部署脚本"
echo "=============================="

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未检测到 Node.js，请先安装 Node.js"
    exit 1
fi

echo "✅ Node.js 版本：$(node -v)"

# 安装后端
echo ""
echo "📦 正在安装后端依赖..."
cd backend
npm install

echo "🗄️  正在初始化数据库..."
npm run init-db

# 安装前端
echo ""
echo "📦 正在安装前端依赖..."
cd ../frontend
npm install

echo ""
echo "✅ 部署完成！"
echo ""
echo "🚀 启动服务："
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
