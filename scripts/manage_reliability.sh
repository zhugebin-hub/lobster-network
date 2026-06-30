#!/bin/bash
# 小龙虾网络 - 围棋学习可靠性保障脚本
# 功能：启动/停止/重启/状态检查所有后台进程
# 用法: ./manage_reliability.sh [start|stop|restart|status]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="/tmp/lobster-network"
mkdir -p "$LOG_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 进程列表（带类型：daemon=守护进程, once=单次运行）
PROCESSES=(
    "sync_reminder:daemon:python3 $SCRIPT_DIR/core/sync_reminder.py run"
    "time_protection:daemon:python3 $SCRIPT_DIR/core/time_protection_v2.py daemon"
    "message_poller_xiaochen:once:python3 $SCRIPT_DIR/core/phase3_message_poller.py poll --student xiaochen"
    "message_poller_zhuguxia:once:python3 $SCRIPT_DIR/core/phase3_message_poller.py poll --student zhuguxia"
    "message_poller_qoder:once:python3 $SCRIPT_DIR/core/phase3_message_poller.py poll --student qoder"
)

# 启动进程
start_process() {
    local name=$1
    local type=$2
    local cmd=$3
    
    if [ "$type" = "once" ]; then
        # 单次运行：直接执行
        echo -e "${GREEN}🔄 $name 执行中...${NC}"
        $cmd >> "$LOG_DIR/${name}.log" 2>&1
        echo -e "${GREEN}✅ $name 执行完成${NC}"
        return 0
    fi
    
    # 守护进程：后台运行
    if pgrep -f "${name}" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  $name 已在运行 (PID: $(pgrep -f "$name" | head -1))${NC}"
        return 0
    fi
    
    nohup $cmd > "$LOG_DIR/${name}.log" 2>&1 &
    local pid=$!
    echo $pid > "$LOG_DIR/${name}.pid"
    echo -e "${GREEN}✅ $name 已启动 (PID: $pid)${NC}"
}

# 停止进程
stop_process() {
    local name=$1
    
    if pgrep -f "$name" > /dev/null 2>&1; then
        pkill -f "$name"
        rm -f "$LOG_DIR/${name}.pid"
        echo -e "${YELLOW}⏹️  $name 已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  $name 未运行${NC}"
    fi
}

# 检查进程状态
check_process() {
    local name=$1
    local cmd=""
    
    case $name in
        sync_reminder) cmd="sync_reminder.py" ;;
        time_protection) cmd="time_protection_v2.py" ;;
        message_poller_xiaochen) cmd="phase3_message_poller.py poll --student xiaochen" ;;
        message_poller_zhuguxia) cmd="phase3_message_poller.py poll --student zhuguxia" ;;
        message_poller_qoder) cmd="phase3_message_poller.py poll --student qoder" ;;
    esac
    
    if [ -n "$cmd" ]; then
        local pid=$(pgrep -f "$cmd" 2>/dev/null | grep -v $$ | head -1)
        if [ -n "$pid" ]; then
            local uptime=$(ps -o etime= -p $pid 2>/dev/null | tr -d ' ')
            echo -e "${GREEN}✅ $name (PID: $pid, 运行: $uptime)${NC}"
            return 0
        fi
    fi
    
    echo -e "${RED}❌ $name (未运行)${NC}"
    return 1
}

# 启动所有进程
start_all() {
    echo "🚀 启动所有小龙虾网络进程..."
    echo ""
    
    for proc in "${PROCESSES[@]}"; do
        local name="${proc%%:*}"
        local rest="${proc#*:}"
        local type="${rest%%:*}"
        local cmd="${rest#*:}"
        start_process "$name" "$type" "$cmd"
    done
    
    echo ""
    echo "✅ 所有进程启动完成"
    echo ""
    show_status
}

# 停止所有进程
stop_all() {
    echo "⏹️  停止所有小龙虾网络进程..."
    echo ""
    
    for proc in "${PROCESSES[@]}"; do
        local name="${proc%%:*}"
        stop_process "$name"
    done
    
    echo ""
    echo "✅ 所有进程已停止"
}

# 重启所有进程
restart_all() {
    echo "🔄 重启所有小龙虾网络进程..."
    echo ""
    stop_all
    echo ""
    sleep 2
    start_all
}

# 显示所有进程状态
show_status() {
    echo "📊 小龙虾网络进程状态:"
    echo ""
    
    local running=0
    local total=${#PROCESSES[@]}
    
    for proc in "${PROCESSES[@]}"; do
        local name="${proc%%:*}"
        if check_process "$name"; then
            ((running++))
        fi
    done
    
    echo ""
    echo "📈 运行状态: $running/$total"
    
    if [ $running -eq $total ]; then
        echo -e "${GREEN}✅ 所有进程正常运行${NC}"
    elif [ $running -gt 0 ]; then
        echo -e "${YELLOW}⚠️  部分进程未运行${NC}"
    else
        echo -e "${RED}❌ 所有进程未运行${NC}"
    fi
}

# 主函数
case "${1:-status}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        restart_all
        ;;
    status)
        show_status
        ;;
    *)
        echo "用法: $0 [start|stop|restart|status]"
        exit 1
        ;;
esac
