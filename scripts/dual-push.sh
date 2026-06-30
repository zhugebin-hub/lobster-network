#!/bin/bash
# 双远程推送脚本
# 分别推送到 GitHub 和 Gitee，一个失败不影响另一个

echo "🦞 小龙虾网络 - 双远程推送"
echo "=========================="

# 推送到 Gitee (SSH, 稳定)
echo "📤 推送到 Gitee..."
git push gitee main 2>&1
GITEE_STATUS=$?

# 推送到 GitHub (HTTPS, 可能超时)
echo "📤 推送到 GitHub..."
GIT_HTTP_LOW_SPEED_LIMIT=0 \
GIT_HTTP_LOW_SPEED_TIME=30 \
git push origin main 2>&1
GITHUB_STATUS=$?

echo ""
echo "=========================="
echo "📊 推送结果:"
if [ $GITEE_STATUS -eq 0 ]; then
  echo "  ✅ Gitee: 成功"
else
  echo "  ❌ Gitee: 失败"
fi

if [ $GITHUB_STATUS -eq 0 ]; then
  echo "  ✅ GitHub: 成功"
else
  echo "  ⚠️ GitHub: 超时/失败 (网络问题)"
fi
