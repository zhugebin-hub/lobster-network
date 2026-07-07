#!/bin/bash
# 🦞 小龙虾网络双平台推送脚本
# 用法: bash scripts/dual_push.sh "commit message"

REPO="/home/admin/.openclaw/workspace/lobster-network"
cd $REPO || exit 1

COMMIT_MSG="${1:-auto push}"

# 提交变更
echo "📝 提交变更..."
git add -A
git commit -m "$COMMIT_MSG" 2>&1

# 拉取远程更新
echo "📥 拉取远程更新..."
git pull origin main --no-rebase --no-edit 2>&1

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main 2>&1
if [ $? -eq 0 ]; then
    echo "✅ GitHub推送成功"
else
    echo "❌ GitHub推送失败，重试中..."
    sleep 5
    git push origin main 2>&1
fi

# 推送到Gitee
echo "📤 推送到Gitee..."
git push gitee main 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Gitee推送成功"
else
    echo "❌ Gitee推送失败，请检查SSH密钥配置"
    echo "💡 配置方法: ssh-keygen -t ed25519 -C 'gitee@lobster-network'"
    echo "💡 将公钥添加到Gitee账户设置"
fi

echo "🎉 双平台推送完成！"
