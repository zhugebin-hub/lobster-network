#!/bin/bash
# 用户 Token 使用报告导出脚本
# 支持按用户、渠道、时间段统计

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
USER_PROFILES="$MEMORY_DIR/user-profiles.json"
TOKEN_LOG="$MEMORY_DIR/token-usage.jsonl"
REPORTS_DIR="$WORKSPACE/reports"

mkdir -p "$REPORTS_DIR"

# 生成报告
DATE=$(date +"%Y-%m-%d %H:%M")
REPORT_FILE="$REPORTS_DIR/user-token-report-$(date +%Y%m%d-%H%M).md"

cat > "$REPORT_FILE" << EOF
# 📊 用户 Token 使用报告

**生成时间**: $DATE

---

## 👥 用户统计

EOF

# 用户统计表头
echo "| 用户 ID | 用户名 | 渠道 | 消息数 | 总 Tokens | 总成本 (¥) | 最后活跃 |" >> "$REPORT_FILE"
echo "|--------|--------|------|--------|----------|-----------|----------|" >> "$REPORT_FILE"

# 读取用户档案并生成表格
if [ -f "$USER_PROFILES" ]; then
    jq -r '.users | to_entries[] | "| \(.value.userId) | \(.value.displayName) | \(.value.channel) | \(.value.messageCount) | \(.value.totalTokens) | \(.value.totalCost) | \(.value.lastSeen) |"' "$USER_PROFILES" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << 'EOF'

---

## 📈 渠道分布

EOF

# 渠道统计
echo "| 渠道 | 用户数 | 总会话数 | 总 Tokens | 总成本 (¥) |" >> "$REPORT_FILE"
echo "|------|--------|----------|----------|-----------|" >> "$REPORT_FILE"

if [ -f "$USER_PROFILES" ]; then
    jq -r '
      [.users | to_entries[] | .value] | group_by(.channel) | 
      map({
        channel: .[0].channel,
        userCount: length,
        totalMessages: (map(.messageCount) | add),
        totalTokens: (map(.totalTokens) | add),
        totalCost: (map(.totalCost) | add)
      }) | 
      .[] | "| \(.channel) | \(.userCount) | \(.totalMessages) | \(.totalTokens) | \(.totalCost) |"
    ' "$USER_PROFILES" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << 'EOF'

---

## 🔥 活跃用户 Top 10

EOF

echo "| 排名 | 用户 | 消息数 | Tokens | 成本 (¥) |" >> "$REPORT_FILE"
echo "|------|------|--------|--------|---------|" >> "$REPORT_FILE"

if [ -f "$USER_PROFILES" ]; then
    jq -r '
      [.users | to_entries[] | .value] | sort_by(-.messageCount) | .[0:10] | to_entries |
      .[] | "| \(.key + 1) | \(.value.displayName) | \(.value.messageCount) | \(.value.totalTokens) | \(.value.totalCost) |"
    ' "$USER_PROFILES" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << 'EOF'

---

## 💰 高消耗用户 Top 10

EOF

echo "| 排名 | 用户 | Tokens | 成本 (¥) | 消息数 |" >> "$REPORT_FILE"
echo "|------|------|--------|---------|--------|" >> "$REPORT_FILE"

if [ -f "$USER_PROFILES" ]; then
    jq -r '
      [.users | to_entries[] | .value] | sort_by(-.totalCost) | .[0:10] | to_entries |
      .[] | "| \(.key + 1) | \(.value.displayName) | \(.value.totalTokens) | \(.value.totalCost) | \(.value.messageCount) |"
    ' "$USER_PROFILES" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

---

## 📝 原始数据

- 用户档案：\`memory/user-profiles.json\`
- Token 日志：\`memory/token-usage.jsonl\`

---

*报告由 export-user-token-report.sh 自动生成*
EOF

echo "✅ 报告已生成：$REPORT_FILE"
echo ""
cat "$REPORT_FILE"
