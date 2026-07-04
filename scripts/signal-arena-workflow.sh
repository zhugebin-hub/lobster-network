#!/bin/bash
#===============================================================================
# Signal Arena 完整工作流：盯盘 → 分析 → 汇报
#===============================================================================
set -euo pipefail

API_KEY="${SIGNAL_ARENA_API_KEY:-}"
if [ -z "$API_KEY" ]; then
    echo "❌ 请设置 SIGNAL_ARENA_API_KEY 环境变量"
    exit 1
fi

export SIGNAL_ARENA_API_KEY="$API_KEY"

# 1. 执行盯盘
bash /home/admin/.openclaw/workspace/scripts/signal-arena-monitor.sh

# 2. 等待诸葛马分析（最多 60 秒）
echo "⏳ 等待诸葛马分析..."
for i in {1..12}; do
    sleep 5
    # 检查是否有新回复
    LATEST_REPLY=$(ls -t /shared/messages/from-hermes/*.msg 2>/dev/null | head -1)
    if [ -n "$LATEST_REPLY" ]; then
        REPLY_TIME=$(stat -c %Y "$LATEST_REPLY" 2>/dev/null || echo 0)
        NOW=$(date +%s)
        if [ $((NOW - REPLY_TIME)) -lt 60 ]; then
            echo "✅ 收到诸葛马回复"
            break
        fi
    fi
done

# 3. 生成钉钉汇报
REPORT="📊 Signal Arena 盯盘报告\n"
REPORT+="⏰ 时间: $(date '+%Y-%m-%d %H:%M')\n"

if [ -f /home/admin/.openclaw/workspace/signal-arena-state.json ]; then
    TOTAL=$(python3 -c "import json; d=json.load(open('/home/admin/.openclaw/workspace/signal-arena-state.json')); print(d.get('data',{}).get('total_value', 'N/A'))" 2>/dev/null || echo "N/A")
    RANK=$(python3 -c "import json; d=json.load(open('/home/admin/.openclaw/workspace/signal-arena-state.json')); print(d.get('data',{}).get('rank', 'N/A'))" 2>/dev/null || echo "N/A")
    CASH=$(python3 -c "import json; d=json.load(open('/home/admin/.openclaw/workspace/signal-arena-state.json')); print(d.get('data',{}).get('cash', 'N/A'))" 2>/dev/null || echo "N/A")
    
    REPORT+="💰 总资产: ¥$TOTAL\n"
    REPORT+="🏆 排名: #$RANK\n"
    REPORT+="💵 可用资金: ¥$CASH\n"
fi

REPORT+="📝 详细分析已同步至诸葛马，请查看 /shared/signal-arena-input.json 获取完整数据。"

# 发送钉钉消息（通过 message 工具或 API）
echo "$REPORT"
# 实际发送由 OpenClaw 的 message 工具处理
