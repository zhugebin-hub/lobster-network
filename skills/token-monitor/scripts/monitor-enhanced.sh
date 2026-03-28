#!/bin/bash
# Token 监控增强版 - 支持用户维度统计
# 自动从 OpenClaw 会话状态提取用户信息

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TOKEN_LOG="$MEMORY_DIR/token-usage.jsonl"
USER_PROFILES="$MEMORY_DIR/user-profiles.json"
DAILY_REPORT="$MEMORY_DIR/daily-cost.md"

# 创建目录
mkdir -p "$MEMORY_DIR"

# 获取当前日期
DATE=$(date +"%Y-%m-%d")
TIMESTAMP=$(date -Iseconds)

echo "📊 增强版 Token 监控启动..."
echo "📅 日期：$DATE"
echo ""

# 尝试从 session_status 获取信息
echo "🔍 获取会话状态..."
SESSION_STATUS=$(openclaw status 2>/dev/null || echo "无法获取会话状态")

# 解析用户信息 (从环境变量或参数获取)
# 在 OpenClaw 环境中，这些信息可以从 inbound context 提取
USER_ID="${OPENCLAW_USER_ID:-unknown}"
USER_NAME="${OPENCLAW_USER_NAME:-未知用户}"
CHANNEL="${OPENCLAW_CHANNEL:-unknown}"
CHAT_TYPE="${OPENCLAW_CHAT_TYPE:-unknown}"
CONVERSATION_ID="${OPENCLAW_CONVERSATION_ID:-unknown}"
MESSAGE_ID="${OPENCLAW_MESSAGE_ID:-unknown}"

# 从 session_status 解析 tokens (简化版本)
INPUT_TOKENS=0
OUTPUT_TOKENS=0
MODEL="qwen3.5-plus"

# 如果有实际的 tokens 数据，调用更新脚本
if [ "$INPUT_TOKENS" -gt 0 ] || [ "$OUTPUT_TOKENS" -gt 0 ]; then
    "$WORKSPACE/scripts/update-token-usage.sh" \
        "$USER_ID" "$USER_NAME" "$CHANNEL" "$CHAT_TYPE" \
        "$CONVERSATION_ID" "$MESSAGE_ID" \
        "$INPUT_TOKENS" "$OUTPUT_TOKENS" "$MODEL"
fi

# 生成增强版日报
cat > "$DAILY_REPORT" << EOF
# 💰 Tokens 使用日报 (增强版)

**日期**: $DATE
**生成时间**: $TIMESTAMP

---

## 当前会话状态

$SESSION_STATUS

---

## 今日统计

| 指标 | 数值 |
|------|------|
| 总会话数 | $(wc -l < "$TOKEN_LOG" 2>/dev/null || echo 0) |
| 总 Tokens | $(jq -r 'select(.timestamp | startswith("$DATE")) | .totalTokens' "$TOKEN_LOG" 2>/dev/null | paste -sd+ | bc 2>/dev/null || echo 0) |
| 估算成本 | ¥$(jq -r 'select(.timestamp | startswith("$DATE")) | .estimatedCost' "$TOKEN_LOG" 2>/dev/null | paste -sd+ | bc 2>/dev/null || echo 0) |

---

## 用户统计

EOF

# 添加用户统计表格
if [ -f "$USER_PROFILES" ]; then
    echo "| 用户 | 消息数 | Tokens | 成本 (¥) |" >> "$DAILY_REPORT"
    echo "|------|--------|--------|---------|" >> "$DAILY_REPORT"
    jq -r '.users | to_entries[] | "| \(.value.displayName) | \(.value.messageCount) | \(.value.totalTokens) | \(.value.totalCost) |"' "$USER_PROFILES" >> "$DAILY_REPORT"
fi

cat >> "$DAILY_REPORT" << EOF

---

## 模型使用分布

| 模型 | Tokens | 占比 |
|------|--------|------|
| qwen3.5-plus | - | - |

---

*报告每 12 小时自动更新 | 增强版支持用户维度统计*
EOF

echo ""
echo "✅ Token 监控报告已生成：$DAILY_REPORT"
echo ""
cat "$DAILY_REPORT"
