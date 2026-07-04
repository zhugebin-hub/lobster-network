#!/bin/bash
# Token 监控脚本 - 记录和分析 tokens 使用情况

WORKSPACE="/home/admin/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TOKEN_LOG="$MEMORY_DIR/token-usage.jsonl"
DAILY_REPORT="$MEMORY_DIR/daily-cost.md"

# 创建目录
mkdir -p "$MEMORY_DIR"

# 获取当前日期
DATE=$(date +"%Y-%m-%d")
TIMESTAMP=$(date -Iseconds)

# 使用 session_status 获取当前会话状态
echo "📊 获取当前会话状态..."
SESSION_STATUS=$(openclaw status 2>/dev/null || echo "无法获取会话状态")

# 生成报告
cat > "$DAILY_REPORT" << EOF
# 💰 Tokens 使用日报

**日期**: $DATE
**生成时间**: $TIMESTAMP

---

## 当前会话状态

$SESSION_STATUS

---

## 今日统计

| 指标 | 数值 |
|------|------|
| 总会话数 | - |
| 总 Tokens | - |
| 估算成本 | - |

---

## 模型使用分布

| 模型 | Tokens | 占比 |
|------|--------|------|
| qwen3.5-plus | - | - |

---

*报告每 12 小时自动更新*
EOF

echo "✅ Token 监控报告已生成：$DAILY_REPORT"
cat "$DAILY_REPORT"
