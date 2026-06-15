#!/bin/bash
#===============================================================================
# 双向通道健康检查脚本
# 功能：定期检查通道状态，异常时告警
#===============================================================================
set -euo pipefail

LOG_FILE="/shared/messages/health-check.log"
STATUS_FILE="/shared/messages/.channel-status.json"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查 NFS 挂载
check_nfs() {
    if mount | grep -q "/shared"; then
        echo "✅ NFS 挂载正常"
        return 0
    else
        echo "❌ NFS 挂载断开！"
        return 1
    fi
}

# 检查消息积压
check_queue() {
    local hermes_count=$(ls /shared/messages/from-hermes/*.msg 2>/dev/null | wc -l)
    local lobster_count=$(ls /shared/messages/from-lobster/*.msg 2>/dev/null | wc -l)
    local archive_count=$(ls /shared/messages/archive/*.msg 2>/dev/null | wc -l)
    
    echo "📊 from-hermes: $hermes_count | from-lobster: $lobster_count | archive: $archive_count"
    
    if [ $hermes_count -gt 100 ]; then
        echo "⚠️ 消息积压超过100条！"
    fi
}

# 检查 Handler v4 文件
check_handler() {
    if [ -f "/shared/zhuge-ma-handler-v4.py" ]; then
        local size=$(stat -c %s "/shared/zhuge-ma-handler-v4.py")
        echo "✅ Handler v4 已部署 ($size bytes)"
    else
        echo "❌ Handler v4 未找到！"
    fi
}

# 检查同步状态
check_sync() {
    local last_sync=$(tail -1 /shared/capabilities/sync.log 2>/dev/null | grep -oP '\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}' || echo "unknown")
    echo "🔄 最后同步: $last_sync"
}

# 生成状态报告
generate_report() {
    local report="═══════════════════════════════════════\n"
    report+="📊 双向通道健康报告\n"
    report+="═══════════════════════════════════════\n\n"
    report+="$(check_nfs)\n"
    report+="$(check_queue)\n"
    report+="$(check_handler)\n"
    report+="$(check_sync)\n"
    report+="\n═══════════════════════════════════════\n"
    
    echo -e "$report"
    log "$report"
}

# 主函数
main() {
    local report=$(generate_report)
    
    # 保存状态
    python3 -c "
import json
status = {
    'last_check': '$(date '+%Y-%m-%d %H:%M:%S')',
    'nfs_mounted': $(mount | grep -q '/shared' && echo 'True' || echo 'False'),
    'hermes_queue': $(ls /shared/messages/from-hermes/*.msg 2>/dev/null | wc -l),
    'lobster_queue': $(ls /shared/messages/from-lobster/*.msg 2>/dev/null | wc -l),
    'archive_count': $(ls /shared/messages/archive/*.msg 2>/dev/null | wc -l),
    'handler_v4_exists': $(test -f /shared/zhuge-ma-handler-v4.py && echo 'True' || echo 'False')
}
with open('$STATUS_FILE', 'w') as f:
    json.dump(status, f, indent=2, ensure_ascii=False)
" 2>/dev/null
    
    echo "$report"
}

main "$@"
