#!/bin/bash
# Token 消耗日报 - 每日统计并推送

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKER_DIR="/home/admin/.openclaw/workspace/skills/token-tracker-v2"
BUDGET_DIR="/home/admin/.openclaw/workspace/skills/token-budget-monitor"
WORKSPACE="/home/admin/.openclaw/workspace"

# 推送目标（多群）
TARGET_GROUPS=(
    "cidrMRsnzVf/TnyxtvMp9MnrQ=="
    "cid2Qfigiuz0ILMHMkqbw7D0A=="
)

echo "📊 生成 Token 消耗日报..."

# 获取今日统计
cd "$TRACKER_DIR"
TODAY_OUTPUT=$(npm run token:today 2>&1 | grep -A 20 "今日 Token")

# 获取本周统计
WEEK_OUTPUT=$(npm run token:w 2>&1 | grep -A 20 "本周 Token")

# 获取预算状态
cd "$BUDGET_DIR"
BUDGET_STATUS=$(cat config.json | grep -A 5 "dailyLimit")

# 生成报告
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
REPORT="📊 **Token 消耗日报**
**生成时间**: $TIMESTAMP

---

## 今日统计
\`\`\`
$TODAY_OUTPUT
\`\`\`

## 本周统计
\`\`\`
$WEEK_OUTPUT
\`\`\`

## 预算配置
- **每日限额**: 200,000 tokens
- **告警阈值**: 80%
- **当前模型**: dashscope-coding/qwen3.5-plus

---

## 💡 节省建议
- 使用 memory_search 避免重复搜索
- 合并多个工具调用
- 减少不必要的日志输出
- 定期清理历史记录

---
*信电大虾自动生成* 🦞⚡️"

# 推送到多个群
for channel_id in "${TARGET_GROUPS[@]}"; do
    echo "📤 推送到 $channel_id..."
    openclaw message send --channel dingtalk --target "$channel_id" --message "$REPORT"
done

echo "✅ Token 日报推送完成！"
