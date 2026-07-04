#!/bin/bash
# 新生选寝系统 - 每日定时汇报脚本
# 汇报时间：9:00 / 15:00 / 20:00 / 24:00
# 汇报方式：钉钉 Webhook

set -e

DORM_DIR="/home/admin/.openclaw/workspace/dormitory_system"
DINGTALK_WEBHOOK="${DORM_DINGTALK_WEBHOOK:-}"
API_BASE="http://127.0.0.1:8765/api"

# 读取 Token
TOKEN=""
TOKENS_FILE="$DORM_DIR/.api_tokens"
if [ -f "$TOKENS_FILE" ]; then
    TOKEN=$(grep -v '^#' "$TOKENS_FILE" | grep -v '^$' | head -1)
fi

AUTH_HEADER=""
if [ -n "$TOKEN" ]; then
    AUTH_HEADER="-H Authorization: Bearer $TOKEN"
fi

# 获取当前时段
HOUR=$(date +%H)
if [ "$HOUR" -lt 12 ]; then
    PERIOD="上午"
elif [ "$HOUR" -lt 18 ]; then
    PERIOD="下午"
elif [ "$HOUR" -lt 22 ]; then
    PERIOD="晚上"
else
    PERIOD="深夜"
fi

# 调用 demo API 获取统计
RESPONSE=$(curl -s "$API_BASE/demo" $AUTH_HEADER 2>/dev/null || echo '{"error":"服务不可用"}')

if echo "$RESPONSE" | python3 -c "import json,sys;d=json.load(sys.stdin);assert 'summary' in d" 2>/dev/null; then
    SUMMARY=$(echo "$RESPONSE" | python3 -c "
import json,sys
d=json.load(sys.stdin)
s=d['summary']
print(f\"总人数: {s['total_students']}人\")
print(f\"寝室数: {s['room_count']}间\")
print(f\"挂起: {s['suspended_count']}人\")
print(f\"冲突: {s['conflict_count']}间\")
print(f\"时间: {s['generated_at']}\")
")
    
    # 发送钉钉消息
    if [ -n "$DINGTALK_WEBHOOK" ]; then
        curl -s "$DINGTALK_WEBHOOK" \
          -H "Content-Type: application/json" \
          -d "{
            \"msgtype\": \"markdown\",
            \"markdown\": {
                \"title\": \"🦞 选寝系统${PERIOD}汇报\",
                \"text\": \"### 🦞 新生选寝系统 ${PERIOD}汇报\n\n${SUMMARY}\n\n> 汇报时间: $(date '+%Y-%m-%d %H:%M')\"
            }
        }" > /dev/null 2>&1
    fi
    
    echo "[$(date)] ${PERIOD}汇报: $SUMMARY" >> "$DORM_DIR/logs/report.log"
else
    echo "[$(date)] ${PERIOD}汇报: 服务不可用" >> "$DORM_DIR/logs/report.log"
fi
