#!/bin/bash
# 小龙虾能力同步脚本 - 每30分钟执行一次
# 位置: /shared/capabilities/sync.sh

SHARED_CAP="/shared/capabilities"
WORKSPACE="/home/admin/.openclaw/workspace"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始同步..." >> "$SHARED_CAP/sync.log"

# 同步 MEMORY.md
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    cp "$WORKSPACE/MEMORY.md" "$SHARED_CAP/"
    echo "✅ MEMORY.md" >> "$SHARED_CAP/sync.log"
fi

# 同步 memory/ 目录（只同步新增和修改的文件）
if [ -d "$WORKSPACE/memory" ]; then
    for md_file in "$WORKSPACE/memory/"*.md; do
        if [ -f "$md_file" ]; then
            filename=$(basename "$md_file")
            if [ ! -f "$SHARED_CAP/memory/$filename" ] || [ "$md_file" -nt "$SHARED_CAP/memory/$filename" ]; then
                cp "$md_file" "$SHARED_CAP/memory/"
                echo "✅ memory/$filename" >> "$SHARED_CAP/sync.log"
            fi
        fi
    done
fi

# 同步 schedule-*.md
for schedule_file in "$WORKSPACE"/schedule-*.md; do
    if [ -f "$schedule_file" ]; then
        filename=$(basename "$schedule_file")
        cp "$schedule_file" "$SHARED_CAP/"
        echo "✅ $filename" >> "$SHARED_CAP/sync.log"
    fi
done

# 同步 schedule/ 目录
if [ -d "$WORKSPACE/schedule" ]; then
    cp -r "$WORKSPACE/schedule/"* "$SHARED_CAP/schedule/" 2>/dev/null
    echo "✅ schedule/" >> "$SHARED_CAP/sync.log"
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - 同步完成" >> "$SHARED_CAP/sync.log"
echo "---" >> "$SHARED_CAP/sync.log"
