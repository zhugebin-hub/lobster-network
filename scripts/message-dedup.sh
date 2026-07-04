#!/bin/bash
#===============================================================================
# 消息去重管理器 (message-dedup.sh)
# 功能：检查消息是否重复，防止重复发送
# 作者：小龙虾-诸葛虾 🦞
# 日期：2026-05-17
#===============================================================================

set -euo pipefail

CACHE_DIR="/home/admin/.openclaw/data/message-cache"
DEDUP_WINDOW=120  # 去重窗口（秒）
MAX_CACHE_SIZE=1000  # 最大缓存条数

mkdir -p "$CACHE_DIR"

# 生成消息指纹
generate_fingerprint() {
    local content="$1"
    local sender="${2:-xiaolongxia}"
    # 取内容前 200 字符 + 发送者 生成 hash
    echo -n "${content:0:200}|${sender}" | md5sum | cut -d' ' -f1
}

# 检查是否重复
check_duplicate() {
    local fingerprint="$1"
    local cache_file="$CACHE_DIR/${fingerprint}.json"
    local now=$(date +%s)
    
    if [ -f "$cache_file" ]; then
        local last_sent=$(python3 -c "import json; print(json.load(open('$cache_file')).get('last_sent', 0))" 2>/dev/null || echo 0)
        local elapsed=$((now - last_sent))
        
        if [ "$elapsed" -lt "$DEDUP_WINDOW" ]; then
            echo "DUPLICATE|${elapsed}s"
            return 0
        fi
    fi
    
    echo "UNIQUE"
    return 1
}

# 记录发送状态
record_sent() {
    local fingerprint="$1"
    local message_id="${2:-msg_$(date +%s)}"
    local cache_file="$CACHE_DIR/${fingerprint}.json"
    local now=$(date +%s)
    
    python3 << PYEOF
import json
import os

cache_file = "$cache_file"
fingerprint = "$fingerprint"
message_id = "$message_id"
now = $now

data = {
    "fingerprint": fingerprint,
    "message_id": message_id,
    "last_sent": now,
    "send_count": 1
}

if os.path.exists(cache_file):
    try:
        with open(cache_file, 'r') as f:
            old_data = json.load(f)
        data['send_count'] = old_data.get('send_count', 0) + 1
    except:
        pass

with open(cache_file, 'w') as f:
    json.dump(data, f, indent=2)
PYEOF
    
    cleanup_cache
}

# 清理过期缓存
cleanup_cache() {
    local now=$(date +%s)
    local count=0
    
    for cache_file in "$CACHE_DIR"/*.json; do
        if [ -f "$cache_file" ]; then
            local last_sent=$(python3 -c "import json; print(json.load(open('$cache_file')).get('last_sent', 0))" 2>/dev/null || echo 0)
            local elapsed=$((now - last_sent))
            
            if [ "$elapsed" -gt "$DEDUP_WINDOW" ]; then
                rm -f "$cache_file"
                count=$((count + 1))
            fi
        fi
    done
    
    if [ "$count" -gt 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] 清理了 $count 条过期缓存" >> "$CACHE_DIR/cleanup.log"
    fi
}

# 主逻辑
case "${1:-help}" in
    generate_fingerprint)
        generate_fingerprint "$2" "$3"
        ;;
    check_duplicate)
        check_duplicate "$2"
        ;;
    record_sent)
        record_sent "$2" "$3"
        ;;
    cleanup)
        cleanup_cache
        ;;
    *)
        echo "用法: $0 {generate_fingerprint|check_duplicate|record_sent|cleanup} [参数...]"
        echo "  generate_fingerprint <content> [sender]"
        echo "  check_duplicate <fingerprint>"
        echo "  record_sent <fingerprint> [message_id]"
        echo "  cleanup"
        ;;
esac
