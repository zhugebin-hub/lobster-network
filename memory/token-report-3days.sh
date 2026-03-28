#!/bin/bash

# Token 使用报告脚本 - 最近 3 天
# 输出按会话/用户分组的 token 消耗统计

SESSIONS_DIR="/home/admin/.openclaw/agents/main/sessions"
OUTPUT_FILE="/home/admin/.openclaw/workspace/memory/token-report-3days.md"

# 获取 3 天前的时间戳
THREE_DAYS_AGO=$(date -d "3 days ago" +%s 2>/dev/null || date -v-3d +%s 2>/dev/null)

echo "# 📊 Token 使用报告 - 最近 3 天" > "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 临时文件存储统计数据
TEMP_FILE=$(mktemp)

# 遍历所有 session 文件
for session_file in "$SESSIONS_DIR"/*.jsonl; do
    [ -f "$session_file" ] || continue
    
    # 检查文件修改时间是否在 3 天内
    file_mtime=$(stat -c %Y "$session_file" 2>/dev/null || stat -f %m "$session_file" 2>/dev/null)
    [ -z "$file_mtime" ] && continue
    
    if [ "$file_mtime" -ge "$THREE_DAYS_AGO" ]; then
        # 提取 token 使用数据
        grep -o '"usage":{[^}]*}' "$session_file" 2>/dev/null | while read -r usage; do
            input=$(echo "$usage" | grep -o '"input":[0-9]*' | cut -d: -f2)
            output=$(echo "$usage" | grep -o '"output":[0-9]*' | cut -d: -f2)
            total=$(echo "$usage" | grep -o '"totalTokens":[0-9]*' | cut -d: -f2)
            
            [ -n "$total" ] && echo "$total $input $output $session_file" >> "$TEMP_FILE"
        done
    fi
done

# 汇总统计
echo "## 📈 总体统计" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

total_all=0
input_all=0
output_all=0
session_count=0

while read -r line; do
    total=$(echo "$line" | awk '{print $1}')
    input=$(echo "$line" | awk '{print $2}')
    output=$(echo "$line" | awk '{print $3}')
    
    total_all=$((total_all + total))
    input_all=$((input_all + input))
    output_all=$((output_all + output))
    session_count=$((session_count + 1))
done < "$TEMP_FILE"

echo "| 指标 | 数值 |" >> "$OUTPUT_FILE"
echo "|------|------|" >> "$OUTPUT_FILE"
echo "| **总会话数** | $session_count |" >> "$OUTPUT_FILE"
echo "| **总输入 Tokens** | $(printf "%'d" $input_all) |" >> "$OUTPUT_FILE"
echo "| **总输出 Tokens** | $(printf "%'d" $output_all) |" >> "$OUTPUT_FILE"
echo "| **总 Tokens** | $(printf "%'d" $total_all) |" >> "$OUTPUT_FILE"

# 估算成本 (qwen3.5-plus: ¥0.004/1K input, ¥0.012/1K output)
cost_input=$(echo "scale=2; $input_all * 0.004 / 1000" | bc)
cost_output=$(echo "scale=2; $output_all * 0.012 / 1000" | bc)
cost_total=$(echo "scale=2; $cost_input + $cost_output" | bc)

echo "| **估算成本 (¥)** | ¥$cost_total |" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 按会话分组统计
echo "## 📋 会话详情 (Top 20)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "| 会话 ID | 总 Tokens | 输入 | 输出 | 估算成本 (¥) |" >> "$OUTPUT_FILE"
echo "|---------|----------|------|------|-------------|" >> "$OUTPUT_FILE"

# 按会话文件汇总
declare -A session_totals
declare -A session_inputs
declare -A session_outputs

for session_file in "$SESSIONS_DIR"/*.jsonl; do
    [ -f "$session_file" ] || continue
    
    file_mtime=$(stat -c %Y "$session_file" 2>/dev/null || stat -f %m "$session_file" 2>/dev/null)
    [ -z "$file_mtime" ] && continue
    
    if [ "$file_mtime" -ge "$THREE_DAYS_AGO" ]; then
        session_id=$(basename "$session_file" .jsonl)
        
        file_total=0
        file_input=0
        file_output=0
        
        while read -r usage; do
            input=$(echo "$usage" | grep -o '"input":[0-9]*' | cut -d: -f2)
            output=$(echo "$usage" | grep -o '"output":[0-9]*' | cut -d: -f2)
            total=$(echo "$usage" | grep -o '"totalTokens":[0-9]*' | cut -d: -f2)
            
            [ -n "$input" ] && file_input=$((file_input + input))
            [ -n "$output" ] && file_output=$((file_output + output))
            [ -n "$total" ] && file_total=$((file_total + total))
        done < <(grep -o '"usage":{[^}]*}' "$session_file" 2>/dev/null)
        
        if [ "$file_total" -gt 0 ]; then
            session_totals["$session_id"]=$file_total
            session_inputs["$session_id"]=$file_input
            session_outputs["$session_id"]=$file_output
        fi
    fi
done

# 排序并输出 Top 20
for session_id in "${!session_totals[@]}"; do
    total=${session_totals[$session_id]}
    input=${session_inputs[$session_id]}
    output=${session_outputs[$session_id]}
    cost=$(echo "scale=2; $input * 0.004 / 1000 + $output * 0.012 / 1000" | bc)
    echo "$total|$session_id|$input|$output|$cost"
done | sort -t'|' -k1 -rn | head -20 | while IFS='|' read -r total session_id input output cost; do
    echo "| ${session_id:0:20}... | $(printf "%'d" $total) | $(printf "%'d" $input) | $(printf "%'d" $output) | ¥$cost |" >> "$OUTPUT_FILE"
done

# 清理
rm -f "$TEMP_FILE"

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "*报告生成完成*" >> "$OUTPUT_FILE"

cat "$OUTPUT_FILE"
