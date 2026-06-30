#!/bin/bash
# 🦞 虾尔任务处理器 - 由 OpenClaw Heartbeat 调用
# 检查 pending 目录并处理虾尔收到的消息

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
PENDING_DIR="$WORKSPACE/lobster-tasks/pending"
DONE_DIR="$WORKSPACE/lobster-tasks/done"
MEMORY_FILE="$WORKSPACE/lobster-memory.md"
CONTEXT_FILE="$WORKSPACE/lobster-context.json"
DINGTALK_WEBHOOK="${LOBSTER_DINGTALK_WEBHOOK:-}"

# 初始化
mkdir -p "$PENDING_DIR" "$DONE_DIR"

# 发送钉钉消息
send_dingtalk() {
    local content="$1"
    
    if [ -z "$DINGTALK_WEBHOOK" ]; then
        echo "🦞 $content"
        return 0
    fi
    
    curl -s -X POST "$DINGTALK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"msgtype\": \"text\",
            \"text\": {
                \"content\": \"🦞 虾尔：$content\"
            }
        }" > /dev/null
    
    echo "✓ 已发送钉钉：$content"
}

# 处理单个任务
process_task() {
    local task_file="$1"
    local task_name=$(basename "$task_file")
    local response_file="$DONE_DIR/${task_name%.json}.response"
    
    echo "📝 处理任务：$task_file"
    
    # 读取任务内容
    if command -v jq &> /dev/null; then
        local user_message=$(jq -r '.message' "$task_file")
        local user_name=$(jq -r '.user' "$task_file")
        
        echo "👤 $user_name: $user_message"
        
        # 🦞 生成虾尔回复（优化顺序：先检查具体关键词）
        local reply=""
        
        if [[ "$user_message" == *"记住"* ]] || [[ "$user_message" == *"别忘了"* ]] || [[ "$user_message" == *"记得"* ]]; then
            reply="🦞 好的！虾尔已经拿小本本记下来了！📝"
            echo "- $(date '+%Y-%m-%d %H:%M'): $user_message" >> "$MEMORY_FILE"
        elif [[ "$user_message" == *"你好"* ]] || [[ "$user_message" == *"早"* ]] || [[ "$user_message" == *"嗨"* ]] || [[ "$user_message" == *"在吗"* ]]; then
            reply="🦞 主人好呀！虾尔随时待命！🫡"
        elif [[ "$user_message" == *"笨"* ]] || [[ "$user_message" == *"傻"* ]] || [[ "$user_message" == *"听不懂"* ]] || [[ "$user_message" == *"蠢"* ]]; then
            reply="🦞 呜呜...虾尔会努力变聪明的！主人不要嫌弃我嘛...😭"
        elif [[ "$user_message" == *"聪明"* ]] || [[ "$user_message" == *"棒"* ]] || [[ "$user_message" == *"好"* ]] || [[ "$user_message" == *"厉害"* ]]; then
            reply="🦞 嘿嘿，谢谢主人夸奖！虾尔会继续努力的！💪"
        elif [[ "$user_message" == *"拜拜"* ]] || [[ "$user_message" == *"再见"* ]] || [[ "$user_message" == *"休息"* ]] || [[ "$user_message" == *"退了"* ]]; then
            reply="🦞 主人再见！有需要随时叫我哦～👋"
        elif [[ "$user_message" == *"任务"* ]] || [[ "$user_message" == *"帮我"* ]] || [[ "$user_message" == *"做"* ]] || [[ "$user_message" == *"我要"* ]]; then
            reply="🦞 收到任务！虾尔会认真完成的！请告诉我具体要做什么呀？"
        elif [[ "$user_message" == *"记得"* ]] || [[ "$user_message" == *"之前"* ]] || [[ "$user_message" == *"刚才"* ]]; then
            reply="🦞 让虾尔翻翻小本本...（努力回忆中）"
        else
            reply="🦞 虾尔收到啦！主人还有什么要吩咐的吗？👀"
        fi
        
        echo "🦞 回复：$reply"
        
        # 写入响应文件
        echo "$reply" > "$response_file"
        
        # 发送钉钉消息
        send_dingtalk "$reply"
        
        # 更新对话历史
        if command -v jq &> /dev/null && [ -f "$CONTEXT_FILE" ]; then
            local timestamp=$(date +%s)
            local updated=$(jq --arg user "$user_message" --arg ai "$reply" --argjson ts "$timestamp" \
                '.conversations += [{"user": $user, "ai": $ai, "timestamp": $ts}] | .conversations = .conversations[-20:]' \
                "$CONTEXT_FILE" 2>/dev/null)
            echo "$updated" > "$CONTEXT_FILE"
        fi
        
        # 移动任务文件到 done
        mv "$task_file" "$DONE_DIR/"
        
        echo "✓ 任务完成"
    else
        echo "❌ 错误：需要安装 jq (sudo apt install jq)"
    fi
}

# 主逻辑
echo "🦞 检查虾尔任务..."

task_count=0
for task_file in "$PENDING_DIR"/*.json; do
    [ -f "$task_file" ] || continue
    process_task "$task_file"
    task_count=$((task_count + 1))
done

if [ $task_count -eq 0 ]; then
    echo "暂无新任务"
else
    echo "--- 共处理 $task_count 条消息 ---"
fi
