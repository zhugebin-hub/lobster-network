#!/bin/bash
# 新生选寝系统 - 开机自启脚本
# 放到 crontab: @reboot /home/admin/.openclaw/workspace/dormitory_system/startup.sh

set -e

APP_DIR="/home/admin/.openclaw/workspace/dormitory_system"
LOG="$APP_DIR/logs/startup.log"

mkdir -p "$APP_DIR/logs"

echo "[$(date)] 启动新生选寝系统..." >> "$LOG"

cd "$APP_DIR"

# 检查端口是否已被占用
if lsof -i :8765 >/dev/null 2>&1; then
    echo "[$(date)] 端口 8765 已被占用，跳过启动" >> "$LOG"
    exit 0
fi

# 安装依赖
if ! python3 -c "import openpyxl" 2>/dev/null; then
    echo "[$(date)] 安装 openpyxl..." >> "$LOG"
    pip3 install openpyxl >> "$LOG" 2>&1
fi

# 启动服务
nohup python3 "$APP_DIR/server.py" >> "$LOG" 2>&1 &
echo $! > "$APP_DIR/.server.pid"

sleep 2

if kill -0 $(cat "$APP_DIR/.server.pid") 2>/dev/null; then
    echo "[$(date)] ✅ 服务已启动 (PID: $(cat $APP_DIR/.server.pid))" >> "$LOG"
else
    echo "[$(date)] ❌ 启动失败" >> "$LOG"
fi
