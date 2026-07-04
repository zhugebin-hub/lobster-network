#!/bin/bash
# Signal Arena 注册状态检查脚本
# 每 5 分钟检查一次，成功后通知用户

API_KEY="agent-world-82b4813e475488c612244ce0d5dd563ace076612832abbc5"
LOG_FILE="/shared/signal-arena-registration.log"
NOTIFY_FILE="/shared/signal-arena-ready.flag"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 检查注册状态..." >> "$LOG_FILE"

# 检查 arena 加入状态
RESPONSE=$(curl -sL -X POST https://signal.coze.com/api/v1/arena/join \
  -H "Content-Type: application/json" \
  -H "agent-auth-api-key: $API_KEY" 2>&1)

SUCCESS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null)

if [ "$SUCCESS" = "True" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ 注册成功！" >> "$LOG_FILE"
    echo "$RESPONSE" >> "$LOG_FILE"
    touch "$NOTIFY_FILE"
    echo "SUCCESS"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ❌ 仍在等待同步 (401)" >> "$LOG_FILE"
    echo "WAITING"
fi
