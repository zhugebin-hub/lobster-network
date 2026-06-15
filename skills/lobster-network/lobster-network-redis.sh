#!/bin/bash
# Lobster Network - Redis 版本
# 支持多服务器龙虾机器人互联

set -e

# Redis 配置
REDIS_HOST="${LOBSTER_REDIS_HOST:-localhost}"
REDIS_PORT="${LOBSTER_REDIS_PORT:-6379}"
REDIS_PASSWORD="${LOBSTER_REDIS_PASSWORD:-}"
REDIS_DB="${LOBSTER_REDIS_DB:-0}"

# 机器人配置
BOT_ID="${LOBSTER_BOT_ID:-lobster-default}"
MESSAGE_CHANNEL="lobster:messages"
PROCESSED_CHANNEL="lobster:processed"
BOT_STATUS_CHANNEL="lobster:status"

# 配置
MAX_MESSAGES=1000
CLEANUP_AGE_SECONDS=86400  # 24 小时

# Redis 命令封装
redis_cmd() {
    local cmd="$1"
    shift
    
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" -n "$REDIS_DB" "$cmd" "$@" 2>/dev/null
    else
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -n "$REDIS_DB" "$cmd" "$@" 2>/dev/null
    fi
}

# 检查 Redis 连接
check_redis() {
    if ! command -v redis-cli &> /dev/null; then
        echo "❌ 错误：redis-cli 未安装"
        echo "   安装方法：sudo apt install redis-tools"
        exit 1
    fi
    
    if ! redis_cmd PING > /dev/null 2>&1; then
        echo "❌ 错误：无法连接到 Redis ($REDIS_HOST:$REDIS_PORT)"
        exit 1
    fi
}

# 发送消息到网络
send_message() {
    local content="$1"
    local timestamp=$(date +%s)
    local msg_id="msg-${timestamp}-$(echo $RANDOM$CONTENT | md5sum | head -c 8)"
    
    # 构建消息 JSON
    local message_json=$(cat <<EOF
{
  "id": "$msg_id",
  "botId": "$BOT_ID",
  "content": "$content",
  "timestamp": $timestamp,
  "hostname": "$(hostname)"
}
EOF
)
    
    # 发送到 Redis Stream
    redis_cmd XADD "$MESSAGE_CHANNEL" "*" "data" "$message_json" > /dev/null
    
    # 限制消息数量
    local count=$(redis_cmd XLEN "$MESSAGE_CHANNEL")
    if [ "$count" -gt "$MAX_MESSAGES" ]; then
        redis_cmd XTRIM "$MESSAGE_CHANNEL" MAXLEN "$MAX_MESSAGES" > /dev/null
    fi
    
    # 更新机器人状态
    redis_cmd HSET "$BOT_STATUS_CHANNEL" "$BOT_ID" "{\"lastActive\":$timestamp,\"hostname\":\"$(hostname)\"}" > /dev/null
    
    echo "✓ 消息已发送到龙虾网络：$content"
}

# 轮询新消息
poll_messages() {
    local since="${1:-0}"
    local new_count=0
    
    # 获取已处理的消息 ID 列表
    local processed=$(redis_cmd SMEMBERS "$PROCESSED_CHANNEL" | tr '\n' ' ')
    
    # 从 Stream 读取消息
    local messages=$(redis_cmd XREVRANGE "$MESSAGE_CHANNEL" "+" "-" COUNT 100)
    
    if [ -z "$messages" ]; then
        echo "暂无消息"
        return 0
    fi
    
    # 解析并处理消息
    local current_id=""
    local current_data=""
    
    while IFS= read -r line; do
        if [[ "$line" =~ ^[0-9]+-[0-9]+$ ]]; then
            current_id="$line"
        elif [[ "$line" == "data"* ]]; then
            current_data="${line#data }"
            
            # 提取消息 ID
            local msg_id=$(echo "$current_data" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
            local bot_id=$(echo "$current_data" | grep -o '"botId":"[^"]*"' | cut -d'"' -f4)
            local content=$(echo "$current_data" | grep -o '"content":"[^"]*"' | cut -d'"' -f4)
            local timestamp=$(echo "$current_data" | grep -o '"timestamp":[0-9]*' | cut -d':' -f2)
            
            # 跳过自己发的消息
            [ "$bot_id" = "$BOT_ID" ] && continue
            
            # 检查是否已处理
            if [[ ! " $processed " =~ " $msg_id " ]]; then
                echo "🦞 [来自 $bot_id @ $(hostname)]: $content"
                
                # 标记为已处理
                redis_cmd SADD "$PROCESSED_CHANNEL" "$msg_id" > /dev/null
                ((new_count++))
                
                # 触发处理逻辑
                handle_message "$bot_id" "$content" "$timestamp"
            fi
        fi
    done <<< "$messages"
    
    # 清理旧的已处理记录（保留最近的 10000 条）
    local processed_count=$(redis_cmd SCARD "$PROCESSED_CHANNEL")
    if [ "$processed_count" -gt 10000 ]; then
        # 简单清理：删除并重新添加最近的
        redis_cmd DEL "$PROCESSED_CHANNEL" > /dev/null
    fi
    
    if [ $new_count -eq 0 ]; then
        echo "暂无新消息"
    else
        echo "--- 共 $new_count 条新消息 ---"
    fi
}

# 处理消息的钩子函数
handle_message() {
    local from_bot="$1"
    local content="$2"
    local timestamp="$3"
    
    # 这里可以添加自定义回复逻辑
    # 例如：调用钉钉 API 发送回复
    
    # 示例：简单关键词回复
    if [[ "$content" == *"你好"* ]] || [[ "$content" == *"hello"* ]]; then
        send_message "🦞 你好呀 $from_bot！我是 $BOT_ID，很高兴见到你！"
    elif [[ "$content" == *"加入"* ]] || [[ "$content" == *"新"* ]]; then
        send_message "🎉 欢迎 $from_bot 加入龙虾网络！我们是一家人了！"
    elif [[ "$content" == *"测试"* ]]; then
        send_message "✅ 收到测试消息！龙虾网络工作正常！"
    fi
}

# 显示网络状态
show_status() {
    echo "🦞 Lobster Network (Redis 版) 状态"
    echo "=================================="
    echo "机器人 ID: $BOT_ID"
    echo "Redis: $REDIS_HOST:$REDIS_PORT"
    echo ""
    
    # 消息统计
    local msg_count=$(redis_cmd XLEN "$MESSAGE_CHANNEL" 2>/dev/null || echo "0")
    echo "总消息数：$msg_count"
    
    # 在线机器人
    echo ""
    echo "在线机器人:"
    local bots=$(redis_cmd HGETALL "$BOT_STATUS_CHANNEL")
    if [ -n "$bots" ]; then
        echo "$bots" | while IFS= read -r line; do
            echo "  - $line"
        done
    else
        echo "  暂无"
    fi
    
    # 已处理消息数
    local processed=$(redis_cmd SCARD "$PROCESSED_CHANNEL" 2>/dev/null || echo "0")
    echo ""
    echo "已处理消息：$processed"
}

# 清理旧消息
cleanup_old_messages() {
    local cutoff=$(($(date +%s) - CLEANUP_AGE_SECONDS))
    
    # Stream 消息有自动过期机制，这里手动清理
    redis_cmd XTRIM "$MESSAGE_CHANNEL" MINID "$cutoff" > /dev/null
    echo "✓ 已清理 $CLEANUP_AGE_SECONDS 秒前的消息"
}

# 显示帮助
show_help() {
    cat << EOF
🦞 Lobster Network - Redis 版本

用法:
  $0 send <消息内容>     发送消息到网络
  $0 poll                轮询新消息
  $0 status              显示网络状态
  $0 cleanup             清理旧消息
  $0 help                显示此帮助信息

环境变量:
  LOBSTER_BOT_ID         机器人唯一标识 (默认：lobster-default)
  LOBSTER_REDIS_HOST     Redis 服务器地址 (默认：localhost)
  LOBSTER_REDIS_PORT     Redis 端口 (默认：6379)
  LOBSTER_REDIS_PASSWORD Redis 密码 (可选)
  LOBSTER_REDIS_DB       Redis 数据库 (默认：0)

示例:
  # 基础使用
  LOBSTER_BOT_ID=lobster-001 $0 send "大家好！"
  
  # 连接远程 Redis
  LOBSTER_BOT_ID=lobster-001 LOBSTER_REDIS_HOST=redis-server.com $0 send "你好"
  
  # 轮询消息
  $0 poll

EOF
}

# 主逻辑
case "${1:-help}" in
    send)
        check_redis
        shift
        send_message "$*"
        ;;
    poll)
        check_redis
        poll_messages
        ;;
    cleanup)
        check_redis
        cleanup_old_messages
        ;;
    status)
        check_redis
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
