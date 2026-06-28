#!/bin/bash
# 双平台同步推送脚本
# 同时推送到GitHub和Gitee

set -e
cd /home/admin/lobster-network

echo "=== 双平台同步推送 $(date) ==="

# 1. 先pull最新代码（从GitHub）
echo "📥 从GitHub拉取最新代码..."
git pull origin main 2>/dev/null || echo "⚠️ GitHub pull失败，继续..."

# 2. 推送到GitHub
echo "📤 推送到GitHub..."
if git push origin main 2>/dev/null; then
    echo "✅ GitHub推送成功"
else
    echo "❌ GitHub推送失败"
fi

# 3. 推送到Gitee
echo "📤 推送到Gitee..."
if git push gitee main 2>/dev/null; then
    echo "✅ Gitee推送成功"
else
    echo "❌ Gitee推送失败（可能仓库未创建或认证失败）"
fi

echo "=== 同步完成 ==="
