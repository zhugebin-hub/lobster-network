#!/bin/bash
#===============================================================================
# 直接通道轮询脚本
# 功能：监控 to-zhuguxia/ 目录，处理小陈的消息
#===============================================================================
set -euo pipefail

TO_DIR="/shared/messages/to-zhuguxia"
COMM_DIR="/shared/messages/comm"
LOG_FILE="/shared/messages/direct-poll.log"
STATE_FILE="/shared/messages/.direct-poll-state.json"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 处理小陈的消息
process_xiaochen_msg() {
    local msg_file="$1"
    local fname=$(basename "$msg_file")
    
    # 读取消息
    local msg_type=$(python3 -c "
import json
with open('$msg_file') as f:
    data = json.load(f)
print(data.get('type', 'unknown'))
" 2>/dev/null)
    
    local msg_content=$(python3 -c "
import json
with open('$msg_file') as f:
    data = json.load(f)
print(data.get('message', '')[:200])
" 2>/dev/null)
    
    log "📩 小陈消息: $fname (type=$msg_type)"
    log "   内容: $msg_content"
    
    # 归档
    mkdir -p /shared/messages/archive/direct
    cp "$msg_file" /shared/messages/archive/direct/ 2>/dev/null
    
    # 更新状态
    python3 -c "
import json
state_file = '$STATE_FILE'
try:
    with open(state_file) as f:
        state = json.load(f)
except:
    state = {'processed': [], 'last_poll': ''}
state['processed'] = state.get('processed', [])
state['processed'].append('$fname')
state['processed'] = state['processed'][-500:]
state['last_poll'] = '$(date '+%Y-%m-%d %H:%M:%S')'
with open(state_file, 'w') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)
" 2>/dev/null
}

# 主函数
main() {
    mkdir -p "$TO_DIR" "$COMM_DIR"
    
    # 初始化状态
    if [ ! -f "$STATE_FILE" ]; then
        echo '{"processed": [], "last_poll": ""}' > "$STATE_FILE"
    fi
    
    # 检查新消息
    local new_msgs=$(ls -t "$TO_DIR"/*.json 2>/dev/null | head -10)
    local count=0
    
    if [ -n "$new_msgs" ]; then
        while IFS= read -r msg_file; do
            local fname=$(basename "$msg_file")
            local processed=$(python3 -c "
import json
try:
    with open('$STATE_FILE') as f:
        state = json.load(f)
    print('1' if '$fname' in state.get('processed', []) else '0')
except:
    print('0')
" 2>/dev/null)
            
            if [ "$processed" = "0" ]; then
                process_xiaochen_msg "$msg_file"
                count=$((count + 1))
            fi
        done <<< "$new_msgs"
    fi
    
    if [ $count -gt 0 ]; then
        log "📊 本次处理 $count 条小陈消息"
    fi
}

main "$@"
