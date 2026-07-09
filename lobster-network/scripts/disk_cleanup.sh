#!/bin/bash
# 🦞 小龙虾网络磁盘清理脚本
# 用法: bash scripts/disk_cleanup.sh

echo "🧹 开始磁盘清理..."

# 清理30天前的临时文件
echo "📁 清理临时文件..."
find /tmp -name "lobster-*" -mtime +30 -delete 2>/dev/null
find /tmp -name "node-*" -mtime +7 -delete 2>/dev/null

# 清理日志文件（保留7天）
echo "📝 清理旧日志..."
find /home/admin/.openclaw/logs -name "*.log" -mtime +7 -delete 2>/dev/null
find /home/admin/.openclaw/workspace -name "*.log" -mtime +7 -delete 2>/dev/null

# 清理__pycache__
echo "🐍 清理Python缓存..."
find /home/admin/.openclaw/workspace -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# 清理node_modules中的.map文件
echo "📦 清理Source Maps..."
find /home/admin/.openclaw/workspace -name "*.map" -path "*/node_modules/*" -delete 2>/dev/null

# 检查磁盘使用率
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
echo "💾 当前磁盘使用率: ${USAGE}%"

if [ $USAGE -gt 85 ]; then
    echo "⚠️ 磁盘使用率 ${USAGE}%，超过阈值85%"
    echo "🔍 大文件扫描:"
    du -sh /home/admin/.openclaw/workspace/* 2>/dev/null | sort -rh | head -10
fi

echo "✅ 磁盘清理完成！"
