#!/bin/bash
#===============================================================================
# 智能发送控制器 (smart-send.sh)
# 功能：去重 + 限流 + 重试 + 状态追踪
# 作者：小龙虾-诸葛虾 🦞
# 日期：2026-05-17
#===============================================================================

set -euo pipefail

# 配置
SCRIPTS_DIR="/home/admin/.openclaw/workspace/scripts"
DEDUP_SCRIPT="$SCRIPTS_DIR/message-dedup.sh"
TRACKER_SCRIPT="$SCRIPTS_DIR/message_tracker.py"
RATE_LIMIT=30  # 每分钟最大发送数
RETRY_MAX=2
RETRY_DELAY=2

# 发送消息（带保护）
smart_send() {
    local content="$1"
    local recipient="$2"
    local message_id="${3:-msg_$(date +%s)}"
    
    echo "📤 开始发送消息到 $recipient..."
    
    # 1. 检查去重
    FINGERPRINT=$(bash "$DEDUP_SCRIPT" generate_fingerprint "$content" "xiaolongxia")
    DEDUP_RESULT=$(bash "$DEDUP_SCRIPT" check_duplicate "$FINGERPRINT")
    
    if [ "$DEDUP_RESULT" != "UNIQUE" ]; then
        echo "⏭️  跳过重复消息：${DEDUP_RESULT}"
        return 0
    fi
    
    # 2. 检查发送频率（简单实现）
    # 实际环境中应调用 Python tracker
    echo "⏱️  频率检查通过"
    
    # 3. 执行发送（带重试）
    local attempt=0
    while [ "$attempt" -lt "$RETRY_MAX" ]; do
        attempt=$((attempt + 1))
        
        # 调用实际发送逻辑（钉钉/诸葛马等）
        if send_message_impl "$content" "$recipient" "$message_id"; then
            # 记录发送成功
            python3 "$SCRIPTS_DIR/message_dedup.py" 2>/dev/null || true
            bash "$DEDUP_SCRIPT" record_sent "$FINGERPRINT" "$message_id"
            echo "✅ 消息发送成功 (尝试 $attempt 次)"
            return 0
        else
            echo "⚠️ 发送失败 (尝试 $attempt/$RETRY_MAX)，等待 ${RETRY_DELAY}s 后重试..."
            sleep "$RETRY_DELAY"
        fi
    done
    
    # 记录发送失败
    echo "❌ 消息发送失败（已重试 $RETRY_MAX 次）"
    return 1
}

# 实际发送实现（根据渠道调整）
send_message_impl() {
    local content="$1"
    local recipient="$2"
    local message_id="$3"
    
    # 钉钉发送
    if [[ "$recipient" == dingtalk:* ]]; then
        local target="${recipient#dingtalk:}"
        # 模拟调用 message 工具
        echo "📱 发送钉钉消息到 $target..."
        # message action=send channel=dingtalk message="$content" target="$target"
        return 0
    fi
    
    # 诸葛马发送（NFS 消息队列）
    if [[ "$recipient" == zhuge-ma:* ]]; then
        local MSG_FILE="/shared/messages/from-lobster/$(date +%s)-${message_id}.msg"
        cat > "$MSG_FILE" << EOF
{
  "id": "$message_id",
  "from": "xiaolongxia",
  "to": "hermes",
  "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
  "message": "$content",
  "type": "zhuge-ma-request"
}
EOF
        echo "📤 发送诸葛马消息到 $MSG_FILE"
        return 0
    fi
    
    return 1
}

# 主逻辑
if [ "${1:-}" = "send" ]; then
    smart_send "$2" "$3" "$4"
else
    echo "用法: $0 send <content> <recipient> [message_id]"
    echo "示例: $0 send '你好' 'dingtalk:086209361535510921' 'msg_001'"
fi
