#!/bin/bash
# Mac/Linux 一键启动脚本

echo "========================================"
echo "     学校排课系统 - 一键启动"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3！"
    echo ""
    echo "请安装 Python3:"
    echo "  Mac: brew install python3"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[✓] Python 已安装"
python3 --version
echo ""

# 检查 Flask
if ! python3 -c "import flask" &> /dev/null; then
    echo "[提示] 正在安装依赖包 (首次运行需要)..."
    echo ""
    pip3 install flask flask-cors
    if [ $? -ne 0 ]; then
        echo "[错误] 安装依赖失败！"
        echo "请手动运行：pip3 install flask flask-cors"
        exit 1
    fi
    echo "[✓] 依赖包安装完成"
    echo ""
else
    echo "[✓] 依赖包已安装"
    echo ""
fi

# 创建数据目录
mkdir -p data

# 启动服务
echo "========================================"
echo "     正在启动排课系统..."
echo "========================================"
echo ""
echo "📱 浏览器访问地址:"
echo "   http://localhost:5000"
echo ""
echo "⚠️  请勿关闭此窗口！"
echo "   按 Ctrl+C 可停止服务"
echo ""
echo "========================================"
echo ""

python3 app.py
