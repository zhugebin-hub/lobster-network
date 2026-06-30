#!/bin/bash
# 启动 OpenClaw 信息速递监控器（后台运行）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/openclaw-monitor.log"
PID_FILE="/tmp/openclaw-monitor.pid"

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  监控器已在运行 (PID: $OLD_PID)"
        echo "   停止旧进程：kill $OLD_PID"
        kill "$OLD_PID" 2>/dev/null
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# 启动监控器
echo "🦞 启动 OpenClaw 信息速递监控器..."
echo "⏰ 执行频率：每 12 小时"
echo "📝 日志文件：$LOG_FILE"

cd "$SCRIPT_DIR"
nohup python3 monitor-scheduler.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

echo "$NEW_PID" > "$PID_FILE"
echo "✅ 监控器已启动 (PID: $NEW_PID)"
echo ""
echo "查看日志：tail -f $LOG_FILE"
echo "停止服务：kill $(cat $PID_FILE)"
