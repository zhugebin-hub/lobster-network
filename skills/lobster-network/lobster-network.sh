#!/bin/bash
# Lobster Network - 小龙虾机器人互联脚本
# 实现多个钉钉机器人之间的消息互通

set -e

# 配置
MESSAGE_FILE="${LOBSTER_MESSAGE_FILE:-$HOME/.openclaw/workspace/lobster-messages.json}"
BOT_ID="${LOBSTER_BOT_ID:-lobster-default}"
PROCESSED_FILE="${LOBSTER_PROCESSED_FILE:-$HOME/.openclaw/workspace/.lobster-processed}"
MAX_MESSAGES=1000
CLEANUP_AGE_HOURS=24

# 初始化消息文件
init_message_file() {
    if [ ! -f "$MESSAGE_FILE" ]; then
        echo '{"messages":[]}' > "$MESSAGE_FILE"
    fi
    if [ ! -f "$PROCESSED_FILE" ]; then
        touch "$PROCESSED_FILE"
    fi
}

# 发送消息到网络
send_message() {
    local content="$1"
    local timestamp=$(date +%s000)
    local msg_id="msg-${timestamp}-$(echo $RANDOM | md5sum | head -c 8)"
    
    # 读取现有消息
    local existing=$(cat "$MESSAGE_FILE")
    
    # 添加新消息（使用 jq 如果可用，否则用简单追加）
    if command -v jq &> /dev/null; then
        echo "$existing" | jq --arg id "$msg_id" --arg bot "$BOT_ID" --arg content "$content" --argjson ts "$timestamp" \
            '.messages += [{"id": $id, "botId": $bot, "content": $content, "timestamp": $ts, "processed": []}]' \
            | jq ".messages = .messages[-$MAX_MESSAGES:]" > "$MESSAGE_FILE"
    else
        # 简单实现：追加到文件
        echo "{\"id\":\"$msg_id\",\"botId\":\"$BOT_ID\",\"content\":\"$content\",\"timestamp\":$timestamp}" >> "${MESSAGE_FILE}.tmp"
        # 合并到主文件
        if [ -f "${MESSAGE_FILE}.tmp" ]; then
            cat "${MESSAGE_FILE}.tmp" >> "$MESSAGE_FILE"
            rm "${MESSAGE_FILE}.tmp"
        fi
    fi
    
    echo "✓ 消息已发送到龙虾网络: $content"
}

# 轮询新消息
poll_messages() {
    if [ ! -f "$MESSAGE_FILE" ]; then
        echo "暂无消息文件"
        return 0
    fi
    
    local new_count=0
    
    # 读取消息并检查是否已处理
    if command -v jq &> /dev/null; then
        local messages=$(jq -r '.messages[] | "\(.id)|\(.botId)|\(.content)"' "$MESSAGE_FILE" 2>/dev/null || echo "")
        
        while IFS='|' read -r msg_id bot_id content; do
            [ -z "$msg_id" ] && continue
            
            # 跳过自己发的消息
            [ "$bot_id" = "$BOT_ID" ] && continue
            
            # 检查是否已处理
            if ! grep -q "$msg_id" "$PROCESSED_FILE" 2>/dev/null; then
                echo "🦞 [来自 $bot_id]: $content"
                echo "$msg_id" >> "$PROCESSED_FILE"
                ((new_count++))
                
                # 这里可以触发自定义处理逻辑
                # 例如：调用钉钉 API 回复消息
                handle_message "$bot_id" "$content"
            fi
        done <<< "$messages"
    fi
    
    # 清理已处理记录（保留最近的）
    if [ -f "$PROCESSED_FILE" ]; then
        tail -n 10000 "$PROCESSED_FILE" > "${PROCESSED_FILE}.tmp" && mv "${PROCESSED_FILE}.tmp" "$PROCESSED_FILE"
    fi
    
    if [ $new_count -eq 0 ]; then
        echo "暂无新消息"
    else
        echo "--- 共 $new_count 条新消息 ---"
    fi
}

# 处理消息的钩子函数（可自定义）
handle_message() {
    local from_bot="$1"
    local content="$2"
    
    # 这里可以添加自定义逻辑
    # 例如：根据消息内容触发不同的回复
    # 或者调用钉钉 API 发送回复
    
    # 示例：简单的回声回复（实际使用时请禁用或修改）
    # send_message "收到来自 $from_bot 的消息：$content"
    
    return 0
}

# 清理旧消息
cleanup_old_messages() {
    if command -v jq &> /dev/null && [ -f "$MESSAGE_FILE" ]; then
        local cutoff=$(date -d "$CLEANUP_AGE_HOURS hours ago" +%s000 2>/dev/null || echo "0")
        jq --argjson cutoff "$cutoff" '.messages = [.messages[] | select(.timestamp > $cutoff)]' "$MESSAGE_FILE" > "${MESSAGE_FILE}.tmp"
        mv "${MESSAGE_FILE}.tmp" "$MESSAGE_FILE"
        echo "✓ 已清理 $CLEANUP_AGE_HOURS 小时前的消息"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
🦞 Lobster Network - 小龙虾机器人互联

用法:
  $0 send <消息内容>     发送消息到网络
  $0 poll                轮询新消息
  $0 cleanup             清理旧消息
  $0 status              显示网络状态
  $0 help                显示此帮助信息

环境变量:
  LOBSTER_BOT_ID         机器人唯一标识 (默认：lobster-default)
  LOBSTER_MESSAGE_FILE   消息文件路径 (默认：~/.openclaw/workspace/lobster-messages.json)

示例:
  $0 send "大家好，我是小龙虾 1 号"
  $0 poll
  LOBSTER_BOT_ID=lobster-001 $0 send "你好"

EOF
}

# 显示状态
show_status() {
    init_message_file
    
    echo "🦞 Lobster Network 状态"
    echo "------------------------"
    echo "机器人 ID: $BOT_ID"
    echo "消息文件：$MESSAGE_FILE"
    
    if [ -f "$MESSAGE_FILE" ] && command -v jq &> /dev/null; then
        local total=$(jq '.messages | length' "$MESSAGE_FILE" 2>/dev/null || echo "0")
        local from_others=$(jq --arg bot "$BOT_ID" '[.messages[] | select(.botId != $bot)] | length' "$MESSAGE_FILE" 2>/dev/null || echo "0")
        echo "总消息数：$total"
        echo "来自其他机器人：$from_others"
    fi
    
    if [ -f "$PROCESSED_FILE" ]; then
        local processed=$(wc -l < "$PROCESSED_FILE" | tr -d ' ')
        echo "已处理消息：$processed"
    fi
}

# 主逻辑
init_message_file

case "${1:-help}" in
    send)
        shift
        send_message "$*"
        ;;
    poll)
        poll_messages
        ;;
    cleanup)
        cleanup_old_messages
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "未知命令：$1"
        show_help
        exit 1
        ;;
esac
