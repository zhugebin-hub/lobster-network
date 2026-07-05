#!/bin/bash
# 🦞 小龙虾网络 - 学员训练结果提交脚本
# 用法: ./submit_result.sh <student_id> <day> <result_file>
# 示例: ./submit_result.sh xiaochen 3 day3_result.json

set -e

STUDENT_ID=$1
DAY=$2
RESULT_FILE=$3

if [ -z "$STUDENT_ID" ] || [ -z "$DAY" ] || [ -z "$RESULT_FILE" ]; then
    echo "用法: $0 <student_id> <day> <result_file>"
    echo "示例: $0 xiaochen 3 day3_result.json"
    exit 1
fi

# 诸葛马服务器配置
HERMES_HOST="172.24.57.34"
HERMES_USER="admin"
RESULTS_DIR="/home/admin/lobster-network/docs/training_results"

# 提交结果
echo "📤 提交训练结果..."
echo "   学员: $STUDENT_ID"
echo "   天数: Day $DAY"
echo "   文件: $RESULT_FILE"

scp "$RESULT_FILE" "${HERMES_USER}@${HERMES_HOST}:${RESULTS_DIR}/${STUDENT_ID}_day${DAY}_$(basename $RESULT_FILE)"

if [ $? -eq 0 ]; then
    echo "✅ 提交成功！"
    echo "   结果已保存到: ${RESULTS_DIR}/${STUDENT_ID}_day${DAY}_$(basename $RESULT_FILE)"
else
    echo "❌ 提交失败，请检查网络连接和权限"
    exit 1
fi
