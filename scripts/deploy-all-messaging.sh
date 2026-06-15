#!/bin/bash
#===============================================================================
# 消息防重复与限流系统 - 一键部署脚本
# 作者：小龙虾-诸葛虾 🦞
# 日期：2026-05-17
#===============================================================================
set -euo pipefail

echo "🚀 开始部署消息防重复与限流系统..."

# 1. 创建目录
SCRIPTS_DIR="/home/admin/.openclaw/workspace/scripts"
DATA_DIR="/home/admin/.openclaw/data"
mkdir -p "$SCRIPTS_DIR" "$DATA_DIR/message-cache" "$DATA_DIR/message-tracker"
echo "✅ 目录结构已就绪"

# 2. 设置执行权限
chmod +x "$SCRIPTS_DIR"/message-dedup.sh \
         "$SCRIPTS_DIR"/smart-send.sh \
         "$SCRIPTS_DIR"/monitor_duplicates.py \
         "$SCRIPTS_DIR"/message_tracker.py 2>/dev/null || true
echo "✅ 脚本权限已设置"

# 3. 配置 Crontab（清理缓存 + 监控告警）
(crontab -l 2>/dev/null | grep -v "message-dedup\|monitor_duplicates" ; \
 echo "*/5 * * * * python3 $SCRIPTS_DIR/monitor_duplicates.py >> $DATA_DIR/message-tracker/monitor.log 2>&1" ; \
 echo "0 * * * * bash $SCRIPTS_DIR/message-dedup.sh cleanup >> $DATA_DIR/message-cache/cleanup.log 2>&1" \
) | crontab -
echo "✅ Crontab 定时任务已配置（每5分钟监控 + 每小时清理）"

# 4. 快速自测
echo "🧪 运行快速自测..."
python3 "$SCRIPTS_DIR/message_dedup.py"
echo "✅ 自测通过"

echo ""
echo "=============================================="
echo "  🎉 部署完成！"
echo "=============================================="
echo "📁 核心脚本："
echo "   • message-dedup.sh      (Bash 去重管理器)"
echo "   • message_dedup.py      (Python 去重模块)"
echo "   • smart-send.sh         (智能发送控制器)"
echo "   • message_tracker.py    (消息追踪器)"
echo "   • monitor_duplicates.py (重复消息监控)"
echo ""
echo "⚙️  定时任务："
echo "   • 每 5 分钟：监控重复发送并告警"
echo "   • 每 1 小时：清理过期缓存"
echo ""
echo "📝 使用示例："
echo "   bash $SCRIPTS_DIR/smart-send.sh send \"消息内容\" \"dingtalk:manager7550\" \"msg_001\""
echo "=============================================="
