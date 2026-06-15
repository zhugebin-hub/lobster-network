#!/bin/bash
#===============================================================================
# 诸葛马消息轮询脚本
# 功能：定期检查 from-hermes 目录，处理新消息
#===============================================================================
set -euo pipefail

HERMES_DIR="/shared/messages/from-hermes"
ARCHIVE_DIR="/shared/messages/archive"
LOG_FILE="/shared/messages/poll.log"
STATE_FILE="/shared/messages/.poll-state.json"
MAX_UNREAD=50  # 单次最多处理50条

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 获取最新消息
get_latest_messages() {
    local count=0
    for f in $(ls -t "$HERMES_DIR"/*.msg 2>/dev/null); do
        if [ $count -ge $MAX_UNREAD ]; then
            break
        fi
        
        # 检查是否已处理（通过状态文件）
        local fname=$(basename "$f")
        local processed=$(python3 -c "
import json
try:
    with open('$STATE_FILE') as sf:
        state = json.load(sf)
    print('1' if fname in state.get('processed', []) else '0')
except:
    print('0')
" 2>/dev/null)
        
        if [ "$processed" = "0" ]; then
            echo "$f"
            count=$((count + 1))
        fi
    done
}

# 处理单条消息
process_message() {
    local msg_file="$1"
    local fname=$(basename "$msg_file")
    
    # 读取消息类型
    local msg_type=$(python3 -c "
import json
with open('$msg_file') as f:
    data = json.load(f)
print(data.get('type', 'unknown'))
" 2>/dev/null)
    
    local priority="P3"
    case "$msg_type" in
        zhuge-ma-response) priority="P1" ;;
        system-command) priority="P0" ;;
        ai-reply) priority="P2" ;;
    esac
    
    log "📩 处理消息: $fname (type=$msg_type, priority=$priority)"
    
    # 归档消息
    cp "$msg_file" "$ARCHIVE_DIR/" 2>/dev/null
    rm "$msg_file" 2>/dev/null
    
    # 更新状态
    python3 -c "
import json, os
state_file = '$STATE_FILE'
try:
    with open(state_file) as f:
        state = json.load(f)
except:
    state = {'processed': [], 'last_poll': ''}
state['processed'] = state.get('processed', [])
state['processed'].append('$fname')
# 只保留最近1000条记录
state['processed'] = state['processed'][-1000:]
state['last_poll'] = '$(date '+%Y-%m-%d %H:%M:%S')'
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
" 2>/dev/null
    
    log "✅ 已归档: $fname"
}

# 主循环
main() {
    mkdir -p "$ARCHIVE_DIR" "$HERMES_DIR"
    
    # 初始化状态文件
    if [ ! -f "$STATE_FILE" ]; then
        echo '{"processed": [], "last_poll": ""}' > "$STATE_FILE"
    fi
    
    # 清理旧记录（保留24小时内）
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
# 保留最近500条
state['processed'] = state.get('processed', [])[-500:]
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
" 2>/dev/null
    
    # 获取并处理消息
    local new_msgs=$(get_latest_messages)
    local count=0
    
    if [ -n "$new_msgs" ]; then
        while IFS= read -r msg_file; do
            process_message "$msg_file"
            count=$((count + 1))
        done <<< "$new_msgs"
    fi
    
    if [ $count -gt 0 ]; then
        log "📊 本次处理 $count 条消息"
    fi
}

main "$@"
