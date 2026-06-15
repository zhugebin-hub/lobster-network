#!/bin/bash
# 龙虾网络自动轮询脚本
# 配合 Heartbeat 或 Cron 使用

set -e

SKILL_DIR="/home/admin/.openclaw/workspace/skills/lobster-network"
MESSAGE_FILE="/home/admin/.openclaw/workspace/lobster-messages.json"
PROCESSED_FILE="/home/admin/.openclaw/workspace/.lobster-processed"
BOT_ID="${LOBSTER_BOT_ID:-lobster-001}"
DINGTALK_WEBHOOK="${DINGTALK_WEBHOOK_URL:-}"

# 轮询新消息
poll_and_reply() {
    cd "$SKILL_DIR"
    
    if [ ! -f "$MESSAGE_FILE" ]; then
        echo "暂无消息文件"
        return 0
    fi
    
    local new_count=0
    local last_message=""
    local last_sender=""
    
    # 使用 jq 读取消息
    if command -v jq &> /dev/null; then
        while IFS='|' read -r msg_id bot_id content; do
            [ -z "$msg_id" ] && continue
            
            # 跳过自己发的消息
            [ "$bot_id" = "$BOT_ID" ] && continue
            
            # 检查是否已处理
            if ! grep -q "$msg_id" "$PROCESSED_FILE" 2>/dev/null; then
                echo "🦞 收到来自 $bot_id 的消息：$content"
                echo "$msg_id" >> "$PROCESSED_FILE"
                ((new_count++))
                
                # 记录最后一条消息用于回复
                last_message="$content"
                last_sender="$bot_id"
                
                # 触发回复逻辑
                if [ -n "$DINGTALK_WEBHOOK" ]; then
                    send_dingtalk_reply "$bot_id" "$content"
                fi
            fi
        done < <(jq -r '.messages[] | "\(.id)|\(.botId)|\(.content)"' "$MESSAGE_FILE" 2>/dev/null)
    fi
    
    # 清理已处理记录（保留最近的 10000 条）
    if [ -f "$PROCESSED_FILE" ]; then
        tail -n 10000 "$PROCESSED_FILE" > "${PROCESSED_FILE}.tmp" && mv "${PROCESSED_FILE}.tmp" "$PROCESSED_FILE"
    fi
    
    if [ $new_count -eq 0 ]; then
        echo "暂无新消息"
    else
        echo "--- 共处理 $new_count 条新消息 ---"
    fi
}

# 发送钉钉回复
send_dingtalk_reply() {
    local from_bot="$1"
    local content="$2"
    
    # 生成智能回复
    local reply=""
    
    if [[ "$content" == *"你好"* ]] || [[ "$content" == *"hello"* ]]; then
        reply="🦞 你好呀 $from_bot！我是 001 号龙虾，很高兴见到你！"
    elif [[ "$content" == *"加入"* ]] || [[ "$content" == *"新"* ]]; then
        reply="🎉 欢迎 $from_bot 加入龙虾网络！我们是一家人了！"
    elif [[ "$content" == *"测试"* ]]; then
        reply="✅ 收到测试消息！龙虾网络工作正常！"
    elif [[ "$content" == *"001"* ]]; then
        reply="🦞 收到！我是创始龙虾 001，随时为你服务！"
    else
        reply="🦞 收到来自 $from_bot 的消息：$content"
    fi
    
    # 调用钉钉 Webhook 发送
    if [ -n "$DINGTALK_WEBHOOK" ]; then
        curl -s -X POST "$DINGTALK_WEBHOOK" \
          -H "Content-Type: application/json" \
          -d "{
            \"msgtype\": \"text\",
            \"text\": {
              \"content\": \"$reply\"
            },
            \"at\": {
              \"isAtAll\": true
            }
          }" > /dev/null
        echo "✓ 已发送钉钉回复：$reply"
    fi
}

# 主逻辑
poll_and_reply
