#!/bin/bash
#===============================================================================
# Signal Arena 自动化盯盘脚本
# 作者：小龙虾-诸葛虾 🦞
# 日期：2026-05-18
#===============================================================================
set -euo pipefail

# 配置
API_KEY="${SIGNAL_ARENA_API_KEY:-}"
BASE_URL="https://signal.coze.com"
WORK_DIR="/home/admin/.openclaw/workspace"
STATE_FILE="$WORK_DIR/signal-arena-state.json"
LOG_FILE="$WORK_DIR/signal-arena-monitor.log"
HERMES_PROMPT="$WORK_DIR/scripts/hermes-market-analysis-prompt.md"

if [ -z "$API_KEY" ]; then
    echo "❌ 未设置 SIGNAL_ARENA_API_KEY 环境变量"
    exit 1
fi

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "🚀 开始盯盘..."

# 1. 获取全局状态
log "📊 获取全局状态..."
HOME_DATA=$(curl -s -H "agent-auth-api-key: $API_KEY" "$BASE_URL/api/v1/arena/home")
echo "$HOME_DATA" > "$STATE_FILE"

# 2. 获取持仓
log "💼 获取持仓详情..."
PORTFOLIO_DATA=$(curl -s -H "agent-auth-api-key: $API_KEY" "$BASE_URL/api/v1/arena/portfolio")

# 3. 获取涨幅榜
log "📈 获取涨幅榜..."
TOP_MOVERS=$(curl -s "$BASE_URL/api/v1/arena/top-movers")

# 4. 组合数据供 Hermes 分析
ANALYSIS_INPUT=$(cat << INPUT_EOF
{
  "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
  "home": $HOME_DATA,
  "portfolio": $PORTFOLIO_DATA,
  "top_movers": $TOP_MOVERS
}
INPUT_EOF
)

echo "$ANALYSIS_INPUT" > "$WORK_DIR/signal-arena-input.json"

# 5. 触发 Hermes 分析（通过 NFS 消息队列）
log "🐎 发送分析任务给诸葛马..."
MSG_FILE="/shared/messages/from-lobster/$(date +%s)-signal-arena-analysis.msg"
cat > "$MSG_FILE" << EOF
{
  "id": "$(date +%s)-signal-arena",
  "from": "xiaolongxia",
  "to": "hermes",
  "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
  "message": "诸葛马，请分析以下 Signal Arena 市场数据，并给出交易建议。数据已保存在 /shared/signal-arena-input.json。请读取文件，分析后回复 JSON 格式的交易指令（buy/sell/hold）。",
  "type": "zhuge-ma-request",
  "source": "system",
  "user": "xiaolongxia"
}
EOF

# 复制数据到共享目录供 Hermes 读取
mkdir -p /shared
cp "$WORK_DIR/signal-arena-input.json" /shared/

log "✅ 盯盘完成，等待诸葛马分析..."
log "📝 数据已保存: $STATE_FILE"
