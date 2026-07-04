#!/bin/bash
# 诸葛马端部署脚本
# 在 Hermes 服务器上执行

echo "🐎 开始部署诸葛马端同步组件..."

# 1. 创建目录结构
mkdir -p /shared/capabilities/{memory,schedule}
mkdir -p /shared/skills-all
mkdir -p /shared/messages/{from-lobster,from-hermes,archive,ai-forward,ai-reply}
mkdir -p /shared/research-paper/{templates,students,projects,feedback,versions,logs,scripts}

echo "✅ 目录结构已创建"

# 2. 复制技能文件（如果尚未复制）
if [ ! -d "/shared/skills-all/research-paper-assistant" ]; then
    echo "⏳ 等待小龙虾同步技能文件..."
fi

# 3. 启动诸葛马 Handler
if ! pgrep -f "zhuge-ma-handler.py" > /dev/null; then
    echo "🚀 启动诸葛马 Handler..."
    nohup python3 /shared/zhuge-ma-handler.py > /shared/messages/zhuge-ma-hermes.log 2>&1 &
    echo "✅ Handler 已启动 (PID: $!)"
else
    echo "✅ Handler 已在运行"
fi

# 4. 配置 crontab
CRON_JOB="*/30 * * * * /shared/capabilities/sync.sh"
if ! crontab -l 2>/dev/null | grep -q "sync.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ 同步脚本已添加到 crontab"
else
    echo "✅ 同步脚本已在 crontab 中"
fi

echo "🎉 诸葛马端部署完成！"
echo ""
echo "📋 验证步骤："
echo "1. 检查 NFS 挂载：mount | grep nfs"
echo "2. 检查 Handler 进程：ps aux | grep zhuge-ma-handler"
echo "3. 检查消息队列：ls -la /shared/messages/from-lobster/"
echo "4. 检查同步状态：tail -20 /shared/capabilities/sync.log"
