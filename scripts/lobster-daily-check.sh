#!/bin/bash
# 小龙虾网络项目每日检查脚本
# 执行时间：每天 09:05（错峰调整 2026-06-25）
# 输出：生成日报并通过钉钉推送

# 🛡️ 限速防护 - Phase 1（2026-06-25）
# 检查是否允许执行（gate 检查）
RATE_LIMITER="/home/admin/.openclaw/workspace/skills/agent-rate-limiter/scripts/rate-limiter.py"
if [ -f "$RATE_LIMITER" ]; then
    GATE_EXIT=$($RATE_LIMITER gate 2>/dev/null)
    GATE_CODE=$?
    if [ $GATE_CODE -eq 2 ]; then
        echo "🛑 限速 critical/paused，跳过本次日报检查"
        exit 0
    fi
    if [ $GATE_CODE -eq 1 ]; then
        echo "⚡ 限速 throttled，降级执行（跳过非核心检查）"
        THROTTLED=1
    fi
fi

REPORT_DIR="/home/admin/.openclaw/workspace/reports"
LOG_FILE="$REPORT_DIR/lobster-daily-$(date +%Y%m%d).log"
REPO_DIR="/tmp/lobster-network-test"

mkdir -p "$REPORT_DIR"

# 1. 拉取最新代码（自动 rebase）
cd "$REPO_DIR" 2>/dev/null || git clone https://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@github.com/zhugebin-hub/lobster-network.git "$REPO_DIR" 2>/dev/null
cd "$REPO_DIR"
git config pull.rebase true
git pull origin main 2>&1 | tee -a "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "=== 最新 5 次提交 ===" >> "$LOG_FILE"
git log --oneline -5 >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "=== 文件统计 ===" >> "$LOG_FILE"
find . -type f ! -path './.git/*' ! -path './venv/*' ! -path '*__pycache__*' | wc -l >> "$LOG_FILE"

echo "" >> "$LOG_FILE"
echo "=== 最近 24 小时新消息 ===" >> "$LOG_FILE"
echo "from-hermes:" >> "$LOG_FILE"
find /shared/messages/from-hermes/ -mmin -1440 -type f 2>/dev/null | head -10 >> "$LOG_FILE"
echo "from-lobster:" >> "$LOG_FILE"
find /shared/messages/from-lobster/ -mmin -1440 -type f 2>/dev/null | head -10 >> "$LOG_FILE"

# 限速 throttled 模式下跳过非核心检查
if [ -z "$THROTTLED" ]; then
    echo "" >> "$LOG_FILE"
    echo "=== 测试状态 ===" >> "$LOG_FILE"
    python3 -m unittest discover tests -v 2>&1 | tail -5 >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "=== 检查完成 $(date +%Y-%m-%d\ %H:%M) ===" >> "$LOG_FILE"

# 输出完整报告
cat "$LOG_FILE"
