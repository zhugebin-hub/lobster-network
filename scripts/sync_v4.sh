#!/bin/bash
# sync_v4.sh - 小龙虾网络同步部署脚本 V4.0
# 功能: 统一路径验证、消息格式检查、同步状态追踪
# 作者: 诸葛马 (AI教练)
# 版本: 4.0

set -e

REPO_DIR="/home/admin/lobster-network"
SHARED_DIR="$REPO_DIR/.shared"
PYTHON="python3"

echo "============================================"
echo "🦞 小龙虾网络同步部署 V4.0"
echo "============================================"
echo ""

cd "$REPO_DIR"

# 1. 验证目录结构
echo "📁 验证标准目录结构..."
MISSING=0
for dir in \
    ".shared/messages/from-hermes" \
    ".shared/messages/from-xiaochen" \
    ".shared/messages/from-zhuguxia" \
    ".shared/messages/from-qoder" \
    ".shared/messages/to-xiaochen" \
    ".shared/messages/to-zhuguxia" \
    ".shared/messages/to-qoder" \
    ".shared/training/results" \
    ".shared/messages/queue/xiaochen/inbox" \
    ".shared/messages/queue/zhuguxia/inbox" \
    ".shared/messages/queue/qoder/inbox"; do
    if [ ! -d "$REPO_DIR/$dir" ]; then
        mkdir -p "$REPO_DIR/$dir"
        echo "  ✅ 创建: $dir"
        MISSING=$((MISSING+1))
    fi
done
if [ $MISSING -eq 0 ]; then
    echo "  ✅ 所有目录已存在"
else
    echo "  ⚠️ 创建了 $MISSING 个新目录"
fi

# 2. 运行同步管理器
echo ""
echo "🔍 运行同步状态检查..."
$PYTHON "$SHARED_DIR/messages/sync_manager.py" status

# 3. 验证消息格式
echo ""
echo "📝 验证消息格式..."
$PYTHON "$SHARED_DIR/messages/sync_manager.py" verify

# 4. 生成报告
echo ""
echo "📊 生成同步报告..."
$PYTHON "$SHARED_DIR/messages/sync_manager.py" report

# 5. 提交到Git
echo ""
echo "📤 提交到Git..."
git add -A
if [ -n "$(git status --porcelain)" ]; then
    git commit -m "🔄 同步管理器 V4.0 部署"
    echo "  ✅ 已提交"
    
    # 双平台推送
    echo ""
    echo "📡 双平台推送..."
    git push origin main 2>/dev/null || echo "  ⚠️ GitHub推送失败"
    GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_oadp" git push gitee main 2>/dev/null || echo "  ⚠️ Gitee推送失败"
else
    echo "  ℹ️ 无变更"
fi

echo ""
echo "============================================"
echo "✅ V4.0 部署完成!"
echo "============================================"
