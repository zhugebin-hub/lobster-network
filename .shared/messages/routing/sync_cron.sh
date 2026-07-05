#!/bin/bash
# CC消息路由同步cronjob - 每2小时运行
# 职责: 检查超时告警 + 同步到GitHub

set -e
cd /home/admin/lobster-network

echo "=== CC路由同步 $(date) ==="

# 1. 检查超时
python3 .shared/messages/routing/routing.py check-timeouts 2>/dev/null

# 2. 提交到GitHub
git add .shared/messages/routing/
git add .shared/messages/queue/*/inbox/cc-*.json 2>/dev/null || true
git commit -m "📡 CC路由同步: $(date +%Y%m%d_%H%M)" 2>/dev/null || true
git push origin main 2>/dev/null || true

echo "✅ CC路由同步完成"
