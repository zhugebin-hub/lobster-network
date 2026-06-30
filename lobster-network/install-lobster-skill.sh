#!/bin/bash
# 🦞 龙虾池技能安装脚本
# ================================
# 使用方式：bash install-lobster-skill.sh --lobster-id=lobster-002 --port=8002

set -e

# ==================== 默认配置 ====================
LOBSTER_ID="lobster-002"
PORT=8002
INSTALL_DIR="$HOME/lobster-network"
SKILL_PACKAGE="$HOME/.openclaw/workspace/lobster-network-skill.tar.gz"

# ==================== 参数解析 ====================
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
        --package=*)
            SKILL_PACKAGE="${1#*=}"
            shift
            ;;
        -h|--help)
            echo "用法：$0 [选项]"
            echo "选项:"
            echo "  --lobster-id=lobster-002  龙虾 ID（默认：lobster-002）"
            echo "  --port=8002               监听端口（默认：8002）"
            echo "  --package=PATH            技能包路径（默认：~/lobster-network-skill.tar.gz）"
            echo "  -h, --help                显示帮助"
            exit 0
            ;;
        *)
            echo "未知选项：$1"
            exit 1
            ;;
    esac
done

echo "🦞 开始安装龙虾池技能"
echo "=========================================="
echo "   龙虾 ID: $LOBSTER_ID"
echo "   端口：$PORT"
echo "   技能包：$SKILL_PACKAGE"
echo ""

# ==================== 检查技能包 ====================
if [ ! -f "$SKILL_PACKAGE" ]; then
    echo "❌ 技能包不存在：$SKILL_PACKAGE"
    echo ""
    echo "请先从其他龙虾复制技能包，或从以下位置获取："
    echo "  - 小龙虾 (lobster-001): ~/.openclaw/workspace/lobster-network-skill.tar.gz"
    echo ""
    exit 1
fi
echo "✅ 技能包已找到"

# ==================== 检查依赖 ====================
echo ""
echo "📋 检查依赖..."

if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3"
    exit 1
fi
echo "✅ $(python3 --version)"

if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  安装 Flask..."
    pip3 install flask requests --user -q
    echo "✅ Flask 已安装"
else
    echo "✅ Flask 已安装"
fi

# ==================== 解压技能包 ====================
echo ""
echo "📦 解压技能包..."
mkdir -p "$INSTALL_DIR"
tar -xzf "$SKILL_PACKAGE" -C "$INSTALL_DIR" --strip-components=1
echo "✅ 技能包已解压到：$INSTALL_DIR"

# ==================== 创建目录 ====================
echo ""
echo "📁 创建目录..."
mkdir -p "$HOME/lobster-tasks/pending"
mkdir -p "$HOME/lobster-tasks/done"
mkdir -p "$HOME/lobster-tasks/logs"
echo "✅ 目录已创建"

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

echo "✅ 启动脚本已创建"

# ==================== 配置 systemd（可选） ====================
echo ""
echo "🔧 配置 systemd 服务..."

if [ $EUID -eq 0 ] || sudo -n true 2>/dev/null; then
    SERVICE_FILE="/etc/systemd/system/lobster-wrapper@.service"
    
    # 更新用户路径
    sed "s|/home/admin|$HOME|g" "$INSTALL_DIR/lobster-wrapper@.service" > /tmp/lobster-wrapper@.service
    sudo cp /tmp/lobster-wrapper@.service "$SERVICE_FILE"
    sudo systemctl daemon-reload
    sudo systemctl enable "lobster-wrapper@${LOBSTER_ID}.service" 2>/dev/null || true
    
    echo "✅ systemd 服务已配置"
    echo "   启动：sudo systemctl start lobster-wrapper@${LOBSTER_ID}.service"
    echo "   状态：sudo systemctl status lobster-wrapper@${LOBSTER_ID}.service"
else
    echo "⚠️  无 sudo 权限，跳过 systemd 配置"
    echo "   请使用 start.sh 手动启动"
fi

# ==================== 启动服务 ====================
echo ""
echo "🚀 启动服务..."
$INSTALL_DIR/start.sh

# ==================== 验证 ====================
echo ""
echo "📋 验证安装..."
sleep 2

if pgrep -f "wrapper.py.*$LOBSTER_ID" > /dev/null; then
    PID=$(pgrep -f "wrapper.py.*$LOBSTER_ID")
    echo "✅ 进程运行中 (PID: $PID)"
else
    echo "❌ 进程未运行"
fi

if command -v curl &> /dev/null; then
    sleep 1
    RESP=$(curl -s "http://127.0.0.1:$PORT/health" 2>/dev/null || echo "")
    if [ -n "$RESP" ]; then
        echo "✅ 健康检查通过：$RESP"
    else
        echo "⚠️  健康检查超时"
    fi
fi

# ==================== 完成 ====================
echo ""
echo "=========================================="
echo "🦞 安装完成！"
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
echo "API 端点:"
echo "  健康检查：curl http://127.0.0.1:$PORT/health"
echo "  接收请求：curl -X POST http://127.0.0.1:$PORT/invoke -H 'Content-Type: application/json' -d '{\"from\":\"lobster-001\",\"to\":\"$LOBSTER_ID\",\"msg\":\"test\"}'"
echo "  查看待办：curl http://127.0.0.1:$PORT/pending"
echo ""
echo "下一步:"
echo "  1. 确认钉钉群收到消息"
echo "  2. 等待小龙虾分配任务"
echo "  3. 查看日志：tail -f $HOME/lobster-tasks/logs/$LOBSTER_ID.log"
echo ""
