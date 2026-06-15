#!/bin/bash
# 小龙虾-诸葛马双向同步脚本（SSH/rsync 版本）
# 替代 NFS，通过 SSH 加密通道实现双向同步
# 位置: /home/admin/.openclaw/workspace/skills/xiaolongxia-hermes-sync/scripts/rsync-sync.sh

set -e

HERMES_HOST="admin@47.93.6.57"
LOCAL_SHARED="/shared"
REMOTE_SHARED="/shared"
LOG_FILE="$LOCAL_SHARED/capabilities/sync.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

RSYNC="rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update"

log "=== 开始双向同步 ==="

# 1. 本地 → Hermes：同步 capabilities（本地为主，小龙虾维护）
log "→ 同步 capabilities (本地 → Hermes)"
rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update --delete \
    "$LOCAL_SHARED/capabilities/" \
    "$HERMES_HOST:$REMOTE_SHARED/capabilities/" \
    >> "$LOG_FILE" 2>&1

# 2. 本地 → Hermes：同步 messages/from-lobster（小龙虾发出的消息）
log "→ 同步 messages/from-lobster (本地 → Hermes)"
rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update \
    "$LOCAL_SHARED/messages/from-lobster/" \
    "$HERMES_HOST:$REMOTE_SHARED/messages/from-lobster/" \
    >> "$LOG_FILE" 2>&1

# 3. Hermes → 本地：同步 skills-all（Hermes 为主，诸葛马维护）
log "← 同步 skills-all (Hermes → 本地)"
rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update \
    "$HERMES_HOST:$REMOTE_SHARED/skills-all/" \
    "$LOCAL_SHARED/skills-all/" \
    >> "$LOG_FILE" 2>&1

# 4. 本地 → Hermes：同步 research-paper（本地为主）
log "→ 同步 research-paper (本地 → Hermes)"
rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update \
    "$LOCAL_SHARED/research-paper/" \
    "$HERMES_HOST:$REMOTE_SHARED/research-paper/" \
    >> "$LOG_FILE" 2>&1

# 5. Hermes → 本地：同步 messages/from-hermes（诸葛马回复的消息）
log "← 同步 messages/from-hermes (Hermes → 本地)"
rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update \
    "$HERMES_HOST:$REMOTE_SHARED/messages/from-hermes/" \
    "$LOCAL_SHARED/messages/from-hermes/" \
    >> "$LOG_FILE" 2>&1

# 6. Hermes → 本地：同步 capabilities/memory（诸葛马可能更新的日记）
log "← 同步 capabilities/memory (Hermes → 本地)"
rsync -e 'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10' -avz --update \
    "$HERMES_HOST:$REMOTE_SHARED/capabilities/memory/" \
    "$LOCAL_SHARED/capabilities/memory/" \
    >> "$LOG_FILE" 2>&1

log "✅ 双向同步完成"

# 统计
echo "  本地 messages/from-lobster: $(ls $LOCAL_SHARED/messages/from-lobster/ 2>/dev/null | wc -l) 个文件" >> "$LOG_FILE"
echo "  本地 messages/from-hermes: $(ls $LOCAL_SHARED/messages/from-hermes/ 2>/dev/null | wc -l) 个文件" >> "$LOG_FILE"
echo "  本地 skills-all: $(ls $LOCAL_SHARED/skills-all/ 2>/dev/null | wc -l) 个技能" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"
