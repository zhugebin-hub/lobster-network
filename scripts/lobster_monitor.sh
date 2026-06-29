#!/bin/bash
# 小龙虾网络 V4.0 监控脚本
# 每5分钟执行，检查关键指标

LOG_DIR="/home/admin/.openclaw/workspace/logs"
ALERT_DIR="/home/admin/.openclaw/workspace/alerts"
mkdir -p "$LOG_DIR" "$ALERT_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H:%M:%S)
ALERTS=()

# 1. 检查数字孪生文件是否更新（过去10分钟内）
TWIN_FILE="/tmp/node_twin_zhuguxia.json"
if [ -f "$TWIN_FILE" ]; then
    # 检查文件修改时间
    AGE_MIN=$(( ($(date +%s) - $(stat -c %Y "$TWIN_FILE")) / 60 ))
    if [ "$AGE_MIN" -gt 10 ]; then
        ALERTS+=("[$TIMESTAMP] ALERT: 数字孪生文件过期 (${AGE_MIN}分钟)")
    fi
else
    ALERTS+=("[$TIMESTAMP] ALERT: 数字孪生文件不存在")
fi

# 2. 检查诸葛马负载
LOAD=$(ssh -o ConnectTimeout=5 admin@47.93.6.57 "cat /proc/loadavg | cut -d' ' -f1" 2>/dev/null)
if [ -n "$LOAD" ]; then
    LOAD_INT=${LOAD%.*}
    if [ "$LOAD_INT" -gt 15 ]; then
        ALERTS+=("[$TIMESTAMP] ALERT: 诸葛马负载过高: $LOAD")
    fi
fi

# 3. 检查本地磁盘
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 85 ]; then
    ALERTS+=("[$TIMESTAMP] ALERT: 磁盘使用率过高: ${DISK_USAGE}%")
fi

# 4. 检查数字孪生进程
if ! pgrep -f "node_digital_twin.py" > /dev/null 2>&1; then
    ALERTS+=("[$TIMESTAMP] ALERT: 数字孪生进程未运行")
fi

# 5. 检查诸葛马 twins 目录同步
HERMES_TWIN=$(ssh -o ConnectTimeout=5 admin@47.93.6.57 "ls -la /home/admin/go-training/shared/twins/node_twin_zhuguxia.json 2>/dev/null | awk '{print \$5, \$6, \$7, \$8}'" 2>/dev/null)
if [ -z "$HERMES_TWIN" ]; then
    ALERTS+=("[$TIMESTAMP] ALERT: 诸葛马端孪生文件缺失")
fi

# 输出结果
if [ ${#ALERTS[@]} -gt 0 ]; then
    for alert in "${ALERTS[@]}"; do
        echo "$alert" >> "$ALERT_DIR/monitor.log"
        echo "$alert"
    done
else
    echo "[$TIMESTAMP] OK - 所有指标正常 (磁盘:${DISK_USAGE}%)" >> "$LOG_DIR/monitor_$(date +%Y%m%d).log"
fi
