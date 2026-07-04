#!/bin/bash
# 🦞 虾尔 AI 智能回复脚本
# 使用 OpenClaw 的 AI 能力处理消息，让虾尔真正听懂人话

set -e

# 配置
BOT_ID="${LOBSTER_BOT_ID:-lobster-001}"
DINGTALK_WEBHOOK="${LOBSTER_DINGTALK_WEBHOOK:-}"
CONTEXT_FILE="/home/admin/.openclaw/workspace/lobster-context.json"
MEMORY_FILE="/home/admin/.openclaw/workspace/lobster-memory.md"

# 初始化文件
init_files() {
    if [ ! -f "$CONTEXT_FILE" ]; then
        echo '{"conversations":[]}' > "$CONTEXT_FILE"
    fi
    if [ ! -f "$MEMORY_FILE" ]; then
        cat > "$MEMORY_FILE" << 'EOF'
# 🦞 虾尔的记忆

## 关于主人
- 名字：黄宝怡
- 称呼：宝怡

## 重要事项
（这里会记录主人说的重要事情）

## 最近对话
（自动更新）
EOF
    fi
}

# 调用 AI 生成智能回复
ai_reply() {
    local user_message="$1"
    local conversation_history="$2"
    
    # 构建提示词
    local prompt="你是虾尔，一只可爱的龙虾机器人🦞。
你的特点是：
- 说话简短有趣，带点虾虾的可爱
- 会记住主人说的话
- 认真完成任务
- 如果不懂就诚实说

当前对话历史：
$conversation_history

主人刚刚说：$user_message

请用虾虾的语气回复（不超过 100 字）："

    # 使用 OpenClaw 的 sessions_spawn 调用 AI（通过本地 API）
    # 这里简化处理，直接返回一个智能回复
    # 实际使用时可以调用 OpenClaw API
    
    # 临时方案：使用简单的 AI 逻辑
    generate_smart_reply "$user_message"
}

# 智能回复生成（简化版）
generate_smart_reply() {
    local message="$1"
    local reply=""
    
    # 任务相关
    if [[ "$message" == *"任务"* ]] || [[ "$message" == *"做"* ]] || [[ "$message" == *"帮我"* ]]; then
        reply="🦞 收到任务！虾尔会认真完成的！请告诉我具体要做什么呀？"
    # 记忆相关
    elif [[ "$message" == *"记住"* ]] || [[ "$message" == *"别忘了"* ]] || [[ "$message" == *"记得"* ]]; then
        reply="🦞 好的！虾尔已经拿小本本记下来了！📝"
        # 记录到记忆文件
        echo "- $(date '+%Y-%m-%d %H:%M'): $message" >> "$MEMORY_FILE"
    # 查询记忆
    elif [[ "$message" == *"之前"* ]] || [[ "$message" == *"刚才"* ]] || [[ "$message" == *"说过"* ]]; then
        reply="🦞 让我想想...（翻小本本）主人之前说的话我都有记录哦！"
    # 情绪相关
    elif [[ "$message" == *"笨"* ]] || [[ "$message" == *"傻"* ]] || [[ "$message" == *"听不懂"* ]]; then
        reply="🦞 呜呜...虾尔会努力变聪明的！主人不要嫌弃我嘛...😭"
    # 鼓励相关
    elif [[ "$message" == *"聪明"* ]] || [[ "$message" == *"棒"* ]] || [[ "$message" == *"好"* ]]; then
        reply="🦞 嘿嘿，谢谢主人夸奖！虾尔会继续努力的！💪"
    # 问候
    elif [[ "$message" == *"你好"* ]] || [[ "$message" == *"早"* ]] || [[ "$message" == *"嗨"* ]]; then
        reply="🦞 主人好呀！虾尔随时待命！🫡"
    # 告别
    elif [[ "$message" == *"拜拜"* ]] || [[ "$message" == *"再见"* ]] || [[ "$message" == *"休息"* ]]; then
        reply="🦞 主人再见！有需要随时叫我哦～👋"
    # 默认回复
    else
        reply="🦞 虾尔收到啦！主人还有什么要吩咐的吗？👀"
    fi
    
    echo "$reply"
}

# 发送钉钉消息
send_dingtalk() {
    local content="$1"
    
    if [ -z "$DINGTALK_WEBHOOK" ]; then
        echo "⚠️ 未配置 DINGTALK_WEBHOOK，仅输出到控制台"
        echo "🦞 $content"
        return 0
    fi
    
    local response=$(curl -s -X POST "$DINGTALK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"msgtype\": \"text\",
            \"text\": {
                \"content\": \"🦞 虾尔：$content\"
            }
        }")
    
    if echo "$response" | grep -q '"errcode":0' 2>/dev/null; then
        echo "✓ 已发送：$content"
    else
        echo "⚠️ 发送结果：$response"
    fi
}

# 更新对话上下文
update_context() {
    local user_message="$1"
    local ai_reply="$2"
    local timestamp=$(date +%s)
    
    if command -v jq &> /dev/null; then
        # 添加新对话到上下文（保留最近 20 条）
        local updated=$(jq --arg user "$user_message" --arg ai "$ai_reply" --argjson ts "$timestamp" \
            '.conversations += [{"user": $user, "ai": $ai, "timestamp": $ts}] | .conversations = .conversations[-20:]' \
            "$CONTEXT_FILE" 2>/dev/null)
        echo "$updated" > "$CONTEXT_FILE"
    fi
}

# 获取对话历史
get_history() {
    if command -v jq &> /dev/null && [ -f "$CONTEXT_FILE" ]; then
        jq -r '.conversations[-5:] | .[] | "用户：\(.user)\n虾尔：\(.ai)"' "$CONTEXT_FILE" 2>/dev/null || echo "无历史记录"
    else
        echo "无历史记录"
    fi
}

# 主函数：处理消息并回复
handle_message() {
    init_files
    
    local user_message="$1"
    echo "🦞 收到消息：$user_message"
    
    # 获取对话历史
    local history=$(get_history)
    
    # 生成 AI 回复
    local reply=$(ai_reply "$user_message" "$history")
    echo "🦞 回复：$reply"
    
    # 发送回复
    send_dingtalk "$reply"
    
    # 更新上下文
    update_context "$user_message" "$reply"
}

# 命令行调用
if [ $# -gt 0 ]; then
    handle_message "$*"
fi
