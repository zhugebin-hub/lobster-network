#!/bin/bash
# 双平台推送脚本 - GitHub + Gitee
# 用法: bash scripts/dual-push.sh

cd /home/admin/.openclaw/workspace/lobster-network

echo "=== 双平台推送开始 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改，自动提交..."
    git add -A
    git commit -m "🦞 自动提交 $(date '+%Y-%m-%d %H:%M:%S')"
fi

# 推送到GitHub (使用HTTPS + PAT)
echo "📤 推送到GitHub..."
git push origin master 2>&1
GH_STATUS=$?

# 推送到Gitee (使用SSH)
echo "📤 推送到Gitee..."
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519" git push gitee master 2>&1
GITEE_STATUS=$?

echo ""
echo "=== 推送结果 ==="
if [ $GH_STATUS -eq 0 ]; then
    echo "✅ GitHub: 成功"
else
    echo "❌ GitHub: 失败"
fi

if [ $GITEE_STATUS -eq 0 ]; then
    echo "✅ Gitee: 成功"
else
    echo "❌ Gitee: 失败"
fi

echo ""
echo "=== 当前状态 ==="
git log --oneline -3
echo ""
echo "双平台推送完成！🦞"
