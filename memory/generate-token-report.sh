#!/bin/bash
# Token 使用统计脚本 - 按会话/用户汇总

SESSIONS_DIR="/home/admin/.openclaw/agents/main/sessions"
OUTPUT_FILE="/home/admin/.openclaw/workspace/memory/token-report-detailed.md"

# 价格 (人民币 per 1K tokens)
INPUT_PRICE=0.004
OUTPUT_PRICE=0.012

echo "# 📊 Token 使用详细报告" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**生成时间**: $(date '+%Y-%m-%d %H:%M:%S') (Asia/Shanghai)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 临时文件存储汇总数据
TEMP_FILE=$(mktemp)

# 遍历所有会话文件
for session_file in "$SESSIONS_DIR"/*.jsonl; do
    if [ -f "$session_file" ]; then
        # 提取会话 ID
        session_id=$(basename "$session_file" .jsonl)
        
        # 尝试从文件中提取用户信息
        user_info=$(grep -o '"displayName":"[^"]*"' "$session_file" | head -1 | cut -d'"' -f4)
        if [ -z "$user_info" ]; then
            user_info="未知用户"
        fi
        
        # 统计 tokens
        total_input=$(grep -o '"input":[0-9]*' "$session_file" | awk -F: '{sum+=$2} END {print sum+0}')
        total_output=$(grep -o '"output":[0-9]*' "$session_file" | awk -F: '{sum+=$2} END {print sum+0}')
        total_tokens=$((total_input + total_output))
        
        # 计算成本 (人民币)
        input_cost=$(echo "scale=4; $total_input / 1000 * $INPUT_PRICE" | bc)
        output_cost=$(echo "scale=4; $total_output / 1000 * $OUTPUT_PRICE" | bc)
        total_cost=$(echo "scale=4; $input_cost + $output_cost" | bc)
        
        # 只输出有 token 使用的会话
        if [ "$total_tokens" -gt 0 ]; then
            echo "$user_info|$session_id|$total_input|$total_output|$total_tokens|$input_cost|$output_cost|$total_cost" >> "$TEMP_FILE"
        fi
    fi
done

# 按用户汇总
echo "## 📈 总体统计" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 计算总计
grand_input=$(awk -F'|' '{sum+=$3} END {print sum+0}' "$TEMP_FILE")
grand_output=$(awk -F'|' '{sum+=$4} END {print sum+0}' "$TEMP_FILE")
grand_total=$(awk -F'|' '{sum+=$5} END {print sum+0}' "$TEMP_FILE")
grand_cost=$(awk -F'|' '{sum+=$8} END {printf "%.4f", sum}' "$TEMP_FILE")

echo "| 指标 | 数值 |" >> "$OUTPUT_FILE"
echo "|------|------|" >> "$OUTPUT_FILE"
echo "| **总会话数** | $(wc -l < "$TEMP_FILE") |" >> "$OUTPUT_FILE"
echo "| **总输入 Tokens** | $(number_format $grand_input) |" >> "$OUTPUT_FILE"
echo "| **总输出 Tokens** | $(number_format $grand_output) |" >> "$OUTPUT_FILE"
echo "| **总 Tokens** | $(number_format $grand_total) |" >> "$OUTPUT_FILE"
echo "| **估算成本 (¥)** | ¥$grand_cost |" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 按用户分组统计
echo "## 👥 按用户统计" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| 用户 | 会话数 | 输入 Tokens | 输出 Tokens | 总 Tokens | 输入成本 (¥) | 输出成本 (¥) | 总成本 (¥) |" >> "$OUTPUT_FILE"
echo "|------|--------|-----------|-----------|-----------|-------------|-------------|------------|" >> "$OUTPUT_FILE"

awk -F'|' '
{
    user=$1
    users[user]++
    input[user]+=$3
    output[user]+=$4
    total[user]+=$5
    in_cost[user]+=$6
    out_cost[user]+=$7
    tot_cost[user]+=$8
}
END {
    for (u in users) {
        printf "| %s | %d | %d | %d | %d | ¥%.4f | ¥%.4f | ¥%.4f |\n", u, users[u], input[u], output[u], total[u], in_cost[u], out_cost[u], tot_cost[u]
    }
}' "$TEMP_FILE" | sort -t'|' -k5 -rn >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"

# 会话详情
echo "## 📋 会话详情 (Top 20)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| 用户 | 会话 ID | 总 Tokens | 输入 | 输出 | 成本 (¥) |" >> "$OUTPUT_FILE"
echo "|------|---------|----------|------|------|----------|" >> "$OUTPUT_FILE"

sort -t'|' -k5 -rn "$TEMP_FILE" | head -20 | awk -F'|' '{
    printf "| %s | %s | %d | %d | %d | ¥%.4f |\n", $1, $2, $5, $3, $4, $8
}' >> "$OUTPUT_FILE"

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*报告生成完成*" >> "$OUTPUT_FILE"

# 清理
rm -f "$TEMP_FILE"

echo "报告已生成：$OUTPUT_FILE"
