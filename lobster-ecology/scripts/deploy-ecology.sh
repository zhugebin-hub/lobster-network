#!/bin/bash

# 🦞 小龙虾生态网络 - 一键部署脚本
# 
# 使用方法:
#   在目标小龙虾服务器上运行:
#   curl -sL http://<router-ip>:8080/join.sh | bash
# 
# 或直接复制此脚本到服务器执行

set -e

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║     🦞  小龙虾生态网络  -  一键部署                  ║"
echo "║                                                      ║"
echo "║     版本: 1.0.0                                      ║"
echo "║     日期: 2026-06-12                                 ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# ============ 配置 ============

ECOSYSTEM_VERSION="1.0.0"
SHARED_DIR="/shared/ecology"
INSTALL_DIR="$HOME/.openclaw/workspace/lobster-ecology"
ROUTER_HOST="${ROUTER_HOST:-172.24.57.34}"
ROUTER_PORT="${ROUTER_PORT:-8081}"

# ============ 检查环境 ============

echo "📌 步骤 1/5: 检查环境..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js 18+"
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js: $NODE_VERSION"

# 检查 NFS 挂载
if [ ! -d "/shared" ]; then
    echo "⚠️  NFS 共享目录未挂载"
    echo "   尝试挂载: mount -t nfs 172.24.57.34:/shared /shared"
    sudo mount -t nfs 172.24.57.34:/shared /shared 2>/dev/null || {
        echo "⚠️  自动挂载失败，请手动挂载 NFS"
    }
fi

# 创建生态目录
mkdir -p "$SHARED_DIR"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/router"

echo "✅ 目录准备完成"
echo ""

# ============ 下载核心文件 ============

echo "📌 步骤 2/5: 下载核心文件..."

# 下载接入脚本
echo "   - 下载接入脚本..."
curl -s "http://${ROUTER_HOST}:${ROUTER_PORT}/scripts/join-ecology.js" \
  -o "$INSTALL_DIR/scripts/join-ecology.js" 2>/dev/null || {
    echo "   ⚠️  无法从路由服务器下载，使用本地版本"
    # 如果本地已有则跳过
    if [ ! -f "$INSTALL_DIR/scripts/join-ecology.js" ]; then
        echo "   ❌ 本地也没有接入脚本，请从路由服务器获取"
        exit 1
    fi
}

echo "✅ 核心文件下载完成"
echo ""

# ============ 安装依赖 ============

echo "📌 步骤 3/5: 安装依赖..."

cd "$INSTALL_DIR"

# 创建 package.json (如果不存在)
if [ ! -f "package.json" ]; then
    npm init -y > /dev/null 2>&1
fi

# 安装 MCP SDK
npm install @modelcontextprotocol/sdk express 2>/dev/null || {
    echo "⚠️  npm 安装失败，尝试继续..."
}

echo "✅ 依赖安装完成"
echo ""

# ============ 运行接入向导 ============

echo "📌 步骤 4/5: 运行接入向导..."

# 生成小龙虾信息
LOBSTER_ID="lobster-$(hostname | md5sum | head -c 6)"
LOBSTER_NAME="小龙虾-$(hostname)"
SERVER_IP=$(hostname -I | awk '{print $1}')
CAPABILITIES="personal_assistant"
PLATFORMS="dingtalk"

echo "   小龙虾ID: $LOBSTER_ID"
echo "   小龙虾名称: $LOBSTER_NAME"
echo "   服务器IP: $SERVER_IP"
echo ""

# 运行接入
node "$INSTALL_DIR/scripts/join-ecology.js" \
  --id "$LOBSTER_ID" \
  --name "$LOBSTER_NAME" \
  --ip "$SERVER_IP" \
  --capabilities "$CAPABILITIES" \
  --platforms "$PLATFORMS" \
  --router "$ROUTER_HOST:$ROUTER_PORT"

echo ""

# ============ 配置开机启动 ============

echo "📌 步骤 5/5: 配置开机启动..."

# 创建 systemd 服务 (如果有权限)
if command -v systemctl &> /dev/null; then
    SERVICE_FILE="/etc/systemd/system/lobster-ecology.service"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Lobster Ecology Client
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/node $INSTALL_DIR/scripts/heartbeat.js
Restart=always
RestartSec=30
Environment=NODE_ENV=production
Environment=ROUTER_HOST=$ROUTER_HOST
Environment=ROUTER_PORT=$ROUTER_PORT

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable lobster-ecology 2>/dev/null || true
    systemctl start lobster-ecology 2>/dev/null || true
    
    echo "✅ systemd 服务已配置"
else
    echo "⚠️  无 systemd 权限，请手动启动心跳服务"
    echo "   命令: node $INSTALL_DIR/scripts/heartbeat.js &"
fi

echo ""

# ============ 完成 ============

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║     🦞  小龙虾生态网络 - 部署完成!                   ║"
echo "║                                                      ║"
echo "║  小龙虾ID:    $LOBSTER_ID                            ║"
echo "║  配置文件:    $INSTALL_DIR/lobster-config.json       ║"
echo "║  日志目录:    $INSTALL_DIR/logs/                     ║"
echo "║                                                      ║"
echo "║  查看状态:    node $INSTALL_DIR/scripts/status.js    ║"
echo "║  查看日志:    tail -f $INSTALL_DIR/logs/ecology.log  ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "欢迎加入小龙虾生态网络! 🦞🦞🦞"
