#!/bin/bash
# 🦞 龙虾池 Wrapper 一键部署脚本
# =================================
# 使用方式：./deploy.sh --lobster-id=lobster-002 --port=8002

set -e

# ==================== 参数解析 ====================
LOBSTER_ID="lobster-002"
PORT=8002
INSTALL_DIR="$HOME/lobster-network"
SERVICE_NAME="lobster-wrapper"

while [[ $# -gt 0 ]]; do
    case $1 in
        --lobster-id=*)
            LOBSTER_ID="${1#*=}"
            shift
            ;;
        --port=*)
            PORT="${1#*=}"
            shift
            ;;
        --install-dir=*)
            INSTALL_DIR="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "用法：$0 [选项]"
            echo "选项:"
            echo "  --lobster-id=lobster-002  龙虾 ID（默认：lobster-002）"
            echo "  --port=8002               监听端口（默认：8002）"
            echo "  --install-dir=PATH        安装目录（默认：~/lobster-network）"
            echo "  -h, --help                显示帮助"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            exit 1
            ;;
    esac
done

echo "🦞 开始部署龙虾池 Wrapper"
echo "   龙虾 ID: $LOBSTER_ID"
echo "   端口：$PORT"
echo "   安装目录：$INSTALL_DIR"
echo ""

# ==================== 检查依赖 ====================
echo "📋 检查依赖..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION"

# 检查 Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  未找到 Flask，正在安装..."
    pip3 install flask requests --user -q
    echo "✅ Flask 已安装"
else
    echo "✅ Flask 已安装"
fi

# ==================== 创建目录 ====================
echo ""
echo "📁 创建目录..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$HOME/lobster-tasks/pending"
mkdir -p "$HOME/lobster-tasks/done"
mkdir -p "$HOME/lobster-tasks/logs"

# ==================== 复制文件 ====================
echo ""
echo "📦 复制文件..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cp "$SCRIPT_DIR/wrapper.py" "$INSTALL_DIR/wrapper.py"
chmod +x "$INSTALL_DIR/wrapper.py"
echo "✅ wrapper.py 已复制"

# ==================== 创建启动脚本 ====================
echo ""
echo "🔧 创建启动脚本..."
cat > "$INSTALL_DIR/start.sh" << EOF
#!/bin/bash
cd $INSTALL_DIR
nohup python3 wrapper.py --lobster-id=$LOBSTER_ID --port=$PORT > $HOME/lobster-tasks/logs/$LOBSTER_ID.log 2>&1 &
echo \$! > $INSTALL_DIR/wrapper.pid
echo "✅ Wrapper 已启动 (PID: \$!)"
EOF
chmod +x "$INSTALL_DIR/start.sh"

cat > "$INSTALL_DIR/stop.sh" << EOF
#!/bin/bash
if [ -f "$INSTALL_DIR/wrapper.pid" ]; then
    kill \$(cat $INSTALL_DIR/wrapper.pid) 2>/dev/null || true
    rm -f $INSTALL_DIR/wrapper.pid
    echo "✅ Wrapper 已停止"
else
    pkill -f "wrapper.py.*$LOBSTER_ID" 2>/dev/null || true
    echo "✅ Wrapper 已停止（通过进程名）"
fi
EOF
chmod +x "$INSTALL_DIR/stop.sh"

cat > "$INSTALL_DIR/restart.sh" << EOF
#!/bin/bash
$INSTALL_DIR/stop.sh
sleep 2
$INSTALL_DIR/start.sh
EOF
chmod +x "$INSTALL_DIR/restart.sh"

# ==================== 创建 systemd 服务 ====================
echo ""
echo "🔧 创建 systemd 服务..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}@.service"

# 检查是否需要 sudo
if [ $EUID -ne 0 ]; then
    echo "⚠️  需要 sudo 权限创建 systemd 服务"
    echo "   请输入密码或手动复制以下配置："
    echo ""
    SUDO_CMD="sudo"
else
    SUDO_CMD=""
fi

cat << EOF | $SUDO_CMD tee "$SERVICE_FILE" > /dev/null
[Unit]
Description=Lobster Pool Wrapper - %i
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/wrapper.py --lobster-id=%i --port=8001
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

# 日志
StandardOutput=append:$HOME/lobster-tasks/logs/%i.log
StandardError=append:$HOME/lobster-tasks/logs/%i.error.log

[Install]
WantedBy=multi-user.target
EOF

echo "✅ systemd 服务已创建：$SERVICE_FILE"

# ==================== 启用服务 ====================
echo ""
echo "🚀 启用服务..."
$SUDO_CMD systemctl daemon-reload
$SUDO_CMD systemctl enable "${SERVICE_NAME}@${LOBSTER_ID}.service" 2>/dev/null || true
$SUDO_CMD systemctl start "${SERVICE_NAME}@${LOBSTER_ID}.service" 2>/dev/null || {
    echo "⚠️  systemd 启动失败，使用后台方式启动..."
    $INSTALL_DIR/start.sh
}

# ==================== 验证 ====================
echo ""
echo "📋 验证部署..."
sleep 2

# 检查进程
if pgrep -f "wrapper.py.*$LOBSTER_ID" > /dev/null; then
    PID=$(pgrep -f "wrapper.py.*$LOBSTER_ID")
    echo "✅ 进程运行中 (PID: $PID)"
else
    echo "❌ 进程未运行，请检查日志"
    echo "   日志：$HOME/lobster-tasks/logs/$LOBSTER_ID.log"
fi

# 检查端口
if command -v curl &> /dev/null; then
    sleep 1
    RESP=$(curl -s "http://127.0.0.1:$PORT/health" 2>/dev/null || echo "")
    if [ -n "$RESP" ]; then
        echo "✅ 健康检查通过：$RESP"
    else
        echo "⚠️  健康检查超时，请稍后手动验证"
    fi
fi

# ==================== 完成 ====================
echo ""
echo "=========================================="
echo "🦞 部署完成！"
echo "=========================================="
echo ""
echo "龙虾 ID:    $LOBSTER_ID"
echo "监听端口：$PORT"
echo "安装目录：$INSTALL_DIR"
echo ""
echo "管理命令:"
echo "  启动：$INSTALL_DIR/start.sh"
echo "  停止：$INSTALL_DIR/stop.sh"
echo "  重启：$INSTALL_DIR/restart.sh"
echo "  日志：tail -f $HOME/lobster-tasks/logs/$LOBSTER_ID.log"
echo ""
echo "systemd 管理:"
echo "  启动：sudo systemctl start ${SERVICE_NAME}@${LOBSTER_ID}.service"
echo "  停止：sudo systemctl stop ${SERVICE_NAME}@${LOBSTER_ID}.service"
echo "  状态：sudo systemctl status ${SERVICE_NAME}@${LOBSTER_ID}.service"
echo ""
echo "API 端点:"
echo "  健康检查：curl http://127.0.0.1:$PORT/health"
echo "  接收请求：curl -X POST http://127.0.0.1:$PORT/invoke -H 'Content-Type: application/json' -d '{\"from\":\"lobster-001\",\"to\":\"$LOBSTER_ID\",\"msg\":\"test\"}'"
echo "  查看待办：curl http://127.0.0.1:$PORT/pending"
echo ""
