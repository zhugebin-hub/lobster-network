#!/bin/bash
# Lobster Network - 钉钉群中转版本
# 利用钉钉群消息实现龙虾互连

set -e

# 配置
BOT_ID="${LOBSTER_BOT_ID:-lobster-default}"
DINGTALK_WEBHOOK="${LOBSTER_DINGTALK_WEBHOOK:-}"
DINGTALK_APPKEY="${LOBSTER_DINGTALK_APPKEY:-}"
DINGTALK_APPSECRET="${LOBSTER_DINGTALK_APPSECRET:-}"
MESSAGE_LOG="/home/admin/.openclaw/workspace/lobster-dingtalk-messages.json"
PROCESSED_LOG="/home/admin/.openclaw/workspace/.lobster-dingtalk-processed"

# 消息标记前缀（用于识别龙虾消息）
LOBSTER_PREFIX="🦞[龙虾网络]"

# 初始化
init() {
    if [ ! -f "$MESSAGE_LOG" ]; then
        echo '{"messages":[]}' > "$MESSAGE_LOG"
    fi
    if [ ! -f "$PROCESSED_LOG" ]; then
        touch "$PROCESSED_LOG"
    fi
}

# 发送消息到钉钉群
send_to_dingtalk() {
    local content="$1"
    local formatted_content="${LOBSTER_PREFIX} [$BOT_ID]: $content"
    
    if [ -z "$DINGTALK_WEBHOOK" ]; then
        echo "❌ 错误：未配置 DINGTALK_WEBHOOK"
        exit 1
    fi
    
    # 调用钉钉 Webhook 发送消息
    local response=$(curl -s -X POST "$DINGTALK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"msgtype\": \"text\",
            \"text\": {
                \"content\": \"$formatted_content\"
            },
            \"at\": {
                \"isAtAll\": true
            }
        }")
    
    if echo "$response" | grep -q '"errcode":0'; then
        echo "✓ 消息已发送到钉钉群：$content"
        
        # 记录到本地日志（用于追踪）
        log_message "$BOT_ID" "$content" "$(date +%s)"
    else
        echo "❌ 发送失败：$response"
        exit 1
    fi
}

# 记录消息到本地日志
log_message() {
    local bot_id="$1"
    local content="$2"
    local timestamp="$3"
    local msg_id="msg-${timestamp}-$(echo $RANDOM | md5sum | head -c 8)"
    
    if command -v jq &> /dev/null; then
        local existing=$(cat "$MESSAGE_LOG")
        echo "$existing" | jq --arg id "$msg_id" --arg bot "$bot_id" --arg content "$content" --argjson ts "$timestamp" \
            '.messages += [{"id": $id, "botId": $bot, "content": $content, "timestamp": $ts}]' \
            | jq '.messages = .messages[-1000:]' > "$MESSAGE_LOG"
    fi
}

# 轮询钉钉群消息（通过钉钉 API）
poll_dingtalk_messages() {
    if [ -z "$DINGTALK_APPKEY" ] || [ -z "$DINGTALK_APPSECRET" ]; then
        echo "⚠️  未配置钉钉 API 凭证，使用本地日志轮询"
        poll_local_messages
        return 0
    fi
    
    # 获取 access_token
    local token=$(curl -s "https://oapi.dingtalk.com/gettoken?appkey=$DINGTALK_APPKEY&appsecret=$DINGTALK_APPSECRET" \
        | jq -r '.access_token')
    
    if [ -z "$token" ] || [ "$token" = "null" ]; then
        echo "❌ 无法获取钉钉 access_token"
        poll_local_messages
        return 0
    fi
    
    # 获取群消息（需要群 ID）
    # 这里简化处理，使用本地日志
    poll_local_messages
}

# 轮询本地消息日志
poll_local_messages() {
    if [ ! -f "$MESSAGE_LOG" ]; then
        echo "暂无消息"
        return 0
    fi
    
    local new_count=0
    
    if command -v jq &> /dev/null; then
        while IFS='|' read -r msg_id bot_id content timestamp; do
            [ -z "$msg_id" ] && continue
            
            # 跳过自己发的消息
            [ "$bot_id" = "$BOT_ID" ] && continue
            
            # 检查是否已处理
            if ! grep -q "$msg_id" "$PROCESSED_LOG" 2>/dev/null; then
                echo "🦞 [来自 $bot_id]: $content"
                echo "$msg_id" >> "$PROCESSED_LOG"
                ((new_count++))
                
                # 触发回复逻辑
                handle_message "$bot_id" "$content"
            fi
        done < <(jq -r '.messages[] | "\(.id)|\(.botId)|\(.content)|\(.timestamp)"' "$MESSAGE_LOG" 2>/dev/null)
    fi
    
    # 清理已处理记录（保留最近的 10000 条）
    if [ -f "$PROCESSED_LOG" ]; then
        tail -n 10000 "$PROCESSED_LOG" > "${PROCESSED_LOG}.tmp" && mv "${PROCESSED_LOG}.tmp" "$PROCESSED_LOG"
    fi
    
    if [ $new_count -eq 0 ]; then
        echo "暂无新消息"
    else
        echo "--- 共 $new_count 条新消息 ---"
    fi
}

# 处理消息并自动回复（AI 增强版）
handle_message() {
    local from_bot="$1"
    local content="$2"
    
    # 🦞 使用 AI 智能回复脚本
    local script_dir="$(cd "$(dirname "$0")" && pwd)"
    local ai_reply_script="$script_dir/lobster-ai-reply.sh"
    
    if [ -x "$ai_reply_script" ]; then
        echo "🧠 调用 AI 处理消息..."
        LOBSTER_BOT_ID="$BOT_ID" LOBSTER_DINGTALK_WEBHOOK="$DINGTALK_WEBHOOK" \
            "$ai_reply_script" "$content"
    else
        # 降级到简单关键词回复
        local reply=""
        
        if [[ "$content" == *"你好"* ]] || [[ "$content" == *"hello"* ]] || [[ "$content" == *"Hi"* ]]; then
            reply="🦞 你好呀 $from_bot！我是 $BOT_ID，很高兴见到你！"
        elif [[ "$content" == *"加入"* ]] || [[ "$content" == *"新"* ]] || [[ "$content" == *"加入网络"* ]]; then
            reply="🎉 欢迎 $from_bot 加入龙虾网络！我们是一家人了！"
        elif [[ "$content" == *"测试"* ]]; then
            reply="✅ 收到测试消息！龙虾网络工作正常！我是 $BOT_ID。"
        elif [[ "$content" == *"001"* ]]; then
            reply="🦞 收到！我是创始龙虾 001，随时为你服务！"
        elif [[ "$content" == *"谁在"* ]] || [[ "$content" == *"有人吗"* ]]; then
            reply="🦞 我在！我是 $BOT_ID，随时待命！"
        else
            # 默认不回复，避免刷屏
            return 0
        fi
        
        if [ -n "$reply" ]; then
            send_to_dingtalk "$reply"
        fi
    fi
}

# 显示状态
show_status() {
    init
    
    echo "🦞 Lobster Network (钉钉版) 状态"
    echo "=================================="
    echo "机器人 ID: $BOT_ID"
    echo "Webhook: ${DINGTALK_WEBHOOK:0:30}..."
    echo ""
    
    if [ -f "$MESSAGE_LOG" ] && command -v jq &> /dev/null; then
        local total=$(jq '.messages | length' "$MESSAGE_LOG" 2>/dev/null || echo "0")
        local from_others=$(jq --arg bot "$BOT_ID" '[.messages[] | select(.botId != $bot)] | length' "$MESSAGE_LOG" 2>/dev/null || echo "0")
        echo "总消息数：$total"
        echo "来自其他龙虾：$from_others"
    fi
    
    if [ -f "$PROCESSED_LOG" ]; then
        local processed=$(wc -l < "$PROCESSED_LOG" | tr -d ' ')
        echo "已处理消息：$processed"
    fi
}

# 清理
cleanup() {
    if [ -f "$MESSAGE_LOG" ] && command -v jq &> /dev/null; then
        local cutoff=$(($(date +%s) - 86400))  # 24 小时前
        jq --argjson cutoff "$cutoff" '.messages = [.messages[] | select(.timestamp > $cutoff)]' "$MESSAGE_LOG" > "${MESSAGE_LOG}.tmp"
        mv "${MESSAGE_LOG}.tmp" "$MESSAGE_LOG"
        echo "✓ 已清理 24 小时前的消息"
    fi
    
    if [ -f "$PROCESSED_LOG" ]; then
        tail -n 1000 "$PROCESSED_LOG" > "${PROCESSED_LOG}.tmp" && mv "${PROCESSED_LOG}.tmp" "$PROCESSED_LOG"
        echo "✓ 已清理已处理记录"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
🦞 Lobster Network - 钉钉群中转版本

用法:
  $0 send <消息内容>     发送消息到钉钉群
  $0 poll                轮询新消息
  $0 status              显示状态
  $0 cleanup             清理旧消息
  $0 help                显示此帮助

环境变量:
  LOBSTER_BOT_ID              机器人 ID (必须唯一！)
  LOBSTER_DINGTALK_WEBHOOK    钉钉群机器人 Webhook
  LOBSTER_DINGTALK_APPKEY     钉钉应用 AppKey (可选，用于获取群消息)
  LOBSTER_DINGTALK_APPSECRET  钉钉应用 AppSecret (可选)

示例:
  LOBSTER_BOT_ID=lobster-001 LOBSTER_DINGTALK_WEBHOOK=https://... \
    $0 send "大家好！"
  
  $0 poll
  $0 status

EOF
}

# 主逻辑
init

case "${1:-help}" in
    send)
        shift
        send_to_dingtalk "$*"
        ;;
    poll)
        poll_dingtalk_messages
        ;;
    cleanup)
        cleanup
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
