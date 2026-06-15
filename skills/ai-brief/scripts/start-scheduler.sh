#!/bin/bash
# 启动 AI 简报定时任务（后台运行）

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/tmp/ai-brief-scheduler.log"
PID_FILE="/tmp/ai-brief-scheduler.pid"

# 检查是否已在运行
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  调度器已在运行 (PID: $OLD_PID)"
        echo "   停止旧进程：kill $OLD_PID"
        kill "$OLD_PID" 2>/dev/null
        sleep 1
    fi
    rm -f "$PID_FILE"
fi

# 启动调度器
echo "🦞 启动 AI 简报定时调度器..."
echo "📅 执行时间：每天 9:00 (Asia/Shanghai)"
echo "📝 日志文件：$LOG_FILE"

cd "$SCRIPT_DIR"
nohup python3 brief-scheduler.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

echo "$NEW_PID" > "$PID_FILE"
echo "✅ 调度器已启动 (PID: $NEW_PID)"
echo ""
echo "查看日志：tail -f $LOG_FILE"
echo "停止服务：kill $(cat $PID_FILE)"
