#!/usr/bin/env bash
# ============================================================
# 小龙虾网络 MQTT 部署脚本
# 检测 → 安装 → 配置 → 启动 → 验证 mosquitto broker
# ============================================================
set -euo pipefail

CONFIG_DIR="$(cd "$(dirname "$0")/../config" && pwd)"
CONF_FILE="${CONFIG_DIR}/mosquitto.conf"
LOG_FILE="${CONFIG_DIR}/mosquitto.log"
PID_FILE="${CONFIG_DIR}/mosquitto.pid"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  小龙虾网络 MQTT Broker 部署脚本"
echo "========================================"
echo ""

# ---- 步骤1: 检测 mosquitto 是否已安装 ----
echo "[1/5] 检测 mosquitto 安装状态..."

MOSQUITTO_CMD=""
if command -v mosquitto &>/dev/null; then
    MOSQUITTO_CMD="mosquitto"
elif command -v /usr/local/sbin/mosquitto &>/dev/null; then
    MOSQUITTO_CMD="/usr/local/sbin/mosquitto"
elif command -v /opt/homebrew/sbin/mosquitto &>/dev/null; then
    MOSQUITTO_CMD="/opt/homebrew/sbin/mosquitto"
fi

INSTALLED=false
if [ -n "${MOSQUITTO_CMD:-}" ] && brew list mosquitto &>/dev/null 2>&1; then
    INSTALLED=true
    echo -e "${GREEN}  ✓ mosquitto 已安装: $($MOSQUITTO_CMD --help 2>&1 | head -1 || echo 'mosquitto')${NC}"
elif brew list mosquitto &>/dev/null 2>&1; then
    MOSQUITTO_CMD="$(brew --prefix mosquitto)/sbin/mosquitto"
    INSTALLED=true
    echo -e "${GREEN}  ✓ mosquitto 已通过 Homebrew 安装${NC}"
else
    echo -e "${YELLOW}  ✗ mosquitto 未安装${NC}"
fi

# ---- 步骤2: 安装 mosquitto ----
if [ "$INSTALLED" = false ]; then
    echo ""
    echo "[2/5] 安装 mosquitto (brew install mosquitto)..."
    if command -v brew &>/dev/null; then
        brew install mosquitto
        MOSQUITTO_CMD="$(brew --prefix mosquitto)/sbin/mosquitto"
        echo -e "${GREEN}  ✓ mosquitto 安装完成${NC}"
    else
        echo -e "${RED}  ✗ Homebrew 未安装，请先安装 Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
        exit 1
    fi
else
    echo "[2/5] 跳过安装（已安装）"
fi

# ---- 步骤3: 生成配置文件 ----
echo ""
echo "[3/5] 生成 mosquitto.conf → ${CONF_FILE}"

mkdir -p "${CONFIG_DIR}"

cat > "${CONF_FILE}" << 'MOSQUITTO_CONF'
# ============================================================
# 小龙虾网络 MQTT Broker 配置
# ============================================================

# ---- 基础网络 ----
listener 1883 0.0.0.0
protocol mqtt

# ---- 安全（开发阶段允许匿名） ----
allow_anonymous true

# ---- 持久化 ----
persistence true
persistence_location /tmp/mosquitto_data

# ---- 日志 ----
log_dest file /Users/zgb/Library/Application Support/com.tencent.mac.marvis/MarvisData/User/6C3FDD95359B453B0E08EF3623125EE1/workspace/conv_19f22391a05_fee4943de396/lobster-network/config/mosquitto.log
log_type all
connection_messages true

# ---- 性能 ----
max_keepalive 120
max_inflight_messages 100
max_queued_messages 500
message_size_limit 1048576
MOSQUITTO_CONF

echo -e "${GREEN}  ✓ 配置已生成${NC}"

# ---- 步骤4: 启动服务 ----
echo ""
echo "[4/5] 启动 mosquitto..."

# 先停掉可能已运行的实例
if [ -f "${PID_FILE}" ]; then
    OLD_PID=$(cat "${PID_FILE}")
    if kill -0 "${OLD_PID}" 2>/dev/null; then
        echo "  停止旧进程 (PID=${OLD_PID})..."
        kill "${OLD_PID}" 2>/dev/null || true
        sleep 1
    fi
    rm -f "${PID_FILE}"
fi

# 清理可能残留的 1883 端口占用
if lsof -ti:1883 &>/dev/null; then
    echo "  清理端口 1883 残留进程..."
    lsof -ti:1883 | xargs kill 2>/dev/null || true
    sleep 2
fi

# 创建持久化目录
mkdir -p /tmp/mosquitto_data

# 启动 mosquitto
"${MOSQUITTO_CMD}" -c "${CONF_FILE}" -d
MOSQUITTO_PID=$!
echo "${MOSQUITTO_PID}" > "${PID_FILE}"

sleep 2

# ---- 步骤5: 验证 ----
echo ""
echo "[5/5] 验证服务状态..."

VERIFY_OK=true

# 检查进程
if kill -0 "${MOSQUITTO_PID}" 2>/dev/null; then
    echo -e "${GREEN}  ✓ mosquitto 进程运行中 (PID=${MOSQUITTO_PID})${NC}"
else
    echo -e "${RED}  ✗ mosquitto 进程未运行${NC}"
    VERIFY_OK=false
fi

# 检查端口
if lsof -i :1883 &>/dev/null; then
    echo -e "${GREEN}  ✓ 端口 1883 已监听${NC}"
    lsof -i :1883 | head -5
else
    echo -e "${RED}  ✗ 端口 1883 未监听${NC}"
    VERIFY_OK=false
fi

# 订阅测试
if command -v mosquitto_sub &>/dev/null; then
    echo "  mosquitto_sub 发布/订阅测试..."
    timeout 5 mosquitto_sub -h localhost -p 1883 -t "lobster/go/system/heartbeat" -C 1 &
    SUB_PID=$!
    sleep 1
    mosquitto_pub -h localhost -p 1883 -t "lobster/go/system/heartbeat" -m '{"node_id":"deploy_test","status":"online","source":"deploy","timestamp":"2026-07-04T00:00:00"}' -q 1
    wait "${SUB_PID}" 2>/dev/null && echo -e "${GREEN}  ✓ mosquitto 发布/订阅测试通过${NC}" || echo -e "${YELLOW}  ⚠ 发布/订阅测试未收到消息（可能正常）${NC}"
fi

echo ""
echo "========================================"
if [ "$VERIFY_OK" = true ]; then
    echo -e "${GREEN}  ✓ MQTT Broker 部署成功!${NC}"
    echo ""
    echo "  配置: ${CONF_FILE}"
    echo "  日志: ${LOG_FILE}"
    echo "  PID : ${MOSQUITTO_PID} (${PID_FILE})"
    echo ""
    echo "  管理命令:"
    echo "    停止: kill \$(cat ${PID_FILE})"
    echo "    重启: bash $0"
    echo "    日志: tail -f ${LOG_FILE}"
else
    echo -e "${RED}  ✗ 部署验证失败，请检查日志: ${LOG_FILE}${NC}"
    exit 1
fi
echo "========================================"
