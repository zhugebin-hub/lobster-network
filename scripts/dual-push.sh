#!/bin/bash
# 双平台同步推送脚本
# 同时推送到GitHub和Gitee

cd /home/admin/lobster-network

echo "📤 推送到GitHub..."
git push origin main

echo -e "\n📤 推送到Gitee..."
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_oadp -o StrictHostKeyChecking=no" git push gitee main

echo -e "\n✅ 双平台同步完成！"
