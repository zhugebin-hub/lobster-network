#!/bin/bash
# 小龙虾网络快速接入脚本
# 用法: ./quick_join.sh "名称" "类型" "视角" "知识"

NAME=${1:-"我的小龙虾"}
TYPE=${2:-"agent"}
PERSPECTIVE=${3:-"技术栈"}
KNOWLEDGE=${4:-"代码、文档"}

echo "🦞 小龙虾网络快速接入"
echo "========================"
echo "名称: $NAME"
echo "类型: $TYPE"
echo "视角: $PERSPECTIVE"
echo "知识: $KNOWLEDGE"
echo ""

# 运行注册脚本
python3 "$(dirname "$0")/join_lobster_network.py" \
    --name "$NAME" \
    --type "$TYPE" \
    --perspective "$PERSPECTIVE" \
    --knowledge-base "$KNOWLEDGE"

echo ""
echo "✅ 接入完成！"
