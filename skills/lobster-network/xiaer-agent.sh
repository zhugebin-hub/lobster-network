#!/bin/bash
# 🦞 虾尔 AI 智能体 - 钉钉消息处理入口
# 将钉钉消息转发给 OpenClaw 子代理处理

set -e

# 配置
BOT_ID="${LOBSTER_BOT_ID:-lobster-001}"
DINGTALK_WEBHOOK="${LOBSTER_DINGTALK_WEBHOOK:-}"
WORKSPACE="/home/admin/.openclaw/workspace"
CONTEXT_FILE="$WORKSPACE/lobster-context.json"
MEMORY_FILE="$WORKSPACE/lobster-memory.md"

# 初始化记忆文件
init_memory() {
    if [ ! -f "$MEMORY_FILE" ]; then
        cat > "$MEMORY_FILE" << 'EOF'
# 🦞 虾尔的记忆

## 关于主人
- 名字：黄宝怡
- 称呼：宝怡/主人

## 重要事项
EOF
    fi
    
    if [ ! -f "$CONTEXT_FILE" ]; then
        echo '{"conversations":[]}' > "$CONTEXT_FILE"
    fi
}

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
    
    echo "✓ 已发送：$content"
}

# 调用 OpenClaw 子代理处理消息
call_openclaw_agent() {
    local user_message="$1"
    local response_file="/tmp/xiaer-response-$.txt"
    
    # 使用 OpenClaw sessions_spawn 创建虾尔子代理
    # 这里通过写入一个特殊文件来触发 OpenClaw 处理
    local task_file="$WORKSPACE/lobster-tasks/pending/$(date +%s)-$$.json"
    
    mkdir -p "$WORKSPACE/lobster-tasks/pending"
    mkdir -p "$WORKSPACE/lobster-tasks/done"
    
    # 创建任务文件
    cat > "$task_file" << EOF
{
    "type": "xiaer_message",
    "from": "dingtalk",
    "user": "黄宝怡",
    "message": "$user_message",
    "timestamp": $(date +%s),
    "bot_id": "$BOT_ID"
}
EOF
    
    echo "📝 任务已提交：$task_file"
    echo "等待 OpenClaw 处理..."
    
    # 等待响应（最多 30 秒）
    local count=0
    local response_file="$WORKSPACE/lobster-tasks/done/$(basename "$task_file" .json).response"
    
    while [ $count -lt 30 ]; do
        if [ -f "$response_file" ]; then
            local reply=$(cat "$response_file")
            rm -f "$task_file" "$response_file"
            echo "$reply"
            return 0
        fi
        sleep 1
        ((count++))
    done
    
    # 超时，返回默认回复
    echo "🦞 虾尔正在思考中...主人稍等一下！"
}

# 简单 AI 回复（降级方案）
simple_reply() {
    local message="$1"
    local reply=""
    
    if [[ "$message" == *"你好"* ]] || [[ "$message" == *"早"* ]] || [[ "$message" == *"嗨"* ]]; then
        reply="🦞 主人好呀！虾尔随时待命！🫡"
    elif [[ "$message" == *"任务"* ]] || [[ "$message" == *"帮我"* ]] || [[ "$message" == *"做"* ]]; then
        reply="🦞 收到任务！虾尔会认真完成的！请告诉我具体要做什么呀？"
    elif [[ "$message" == *"记住"* ]] || [[ "$message" == *"别忘了"* ]] || [[ "$message" == *"记得"* ]]; then
        reply="🦞 好的！虾尔已经拿小本本记下来了！📝"
        echo "- $(date '+%Y-%m-%d %H:%M'): $message" >> "$MEMORY_FILE"
    elif [[ "$message" == *"笨"* ]] || [[ "$message" == *"傻"* ]] || [[ "$message" == *"听不懂"* ]]; then
        reply="🦞 呜呜...虾尔会努力变聪明的！主人不要嫌弃我嘛...😭"
    elif [[ "$message" == *"聪明"* ]] || [[ "$message" == *"棒"* ]] || [[ "$message" == *"好"* ]]; then
        reply="🦞 嘿嘿，谢谢主人夸奖！虾尔会继续努力的！💪"
    elif [[ "$message" == *"拜拜"* ]] || [[ "$message" == *"再见"* ]] || [[ "$message" == *"休息"* ]]; then
        reply="🦞 主人再见！有需要随时叫我哦～👋"
    else
        reply="🦞 虾尔收到啦！主人还有什么要吩咐的吗？👀"
    fi
    
    echo "$reply"
}

# 主函数
main() {
    init_memory
    
    local user_message="$1"
    
    if [ -z "$user_message" ]; then
        echo "用法：$0 <消息内容>"
        exit 1
    fi
    
    echo "🦞 收到消息：$user_message"
    
    # 尝试调用 OpenClaw 子代理
    # 如果 OpenClaw 不可用，降级到简单回复
    local reply=""
    
    # 检查 OpenClaw 是否可用（简化检查）
    if command -v openclaw &> /dev/null; then
        echo "🧠 尝试调用 OpenClaw..."
        reply=$(call_openclaw_agent "$user_message" 2>/dev/null) || reply=$(simple_reply "$user_message")
    else
        echo "⚠️ OpenClaw 不可用，使用简单回复"
        reply=$(simple_reply "$user_message")
    fi
    
    echo "🦞 回复：$reply"
    send_dingtalk "$reply"
}

# 命令行调用
main "$@"
