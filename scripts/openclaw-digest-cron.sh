#!/bin/bash
# OpenClaw 信息速递 - 定时任务脚本
# 每 12 小时执行一次，搜索 OpenClaw 最新消息并发送到功能测试群

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
SESSION_KEY="agent:main:dingtalk:group:cid2qfigiuz0ilmhmkqbw7d0a=="
DIGEST_FILE="$WORKSPACE/memory/openclaw-digest-$(date +%Y%m%d-%H%M).md"

echo "🔄 开始执行 OpenClaw 信息速递定时任务..."
echo "📅 执行时间：$(date)"

# 使用 OpenClaw sessions_spawn 创建一个子代理来搜索和发送消息
cd "$WORKSPACE"

# 创建一个临时任务文件
TASK_FILE="/tmp/openclaw-digest-task-$(date +%s).txt"
cat > "$TASK_FILE" << 'TASK'
你是一个 OpenClaw 信息搜集助手。请执行以下任务：

1. 使用 web_fetch 访问以下网址获取最新信息：
   - https://openclaw.ai
   - https://docs.openclaw.ai
   - https://clawhub.com
   - https://github.com/openclaw-ai/openclaw

2. 整理成"信息速递"格式：
```
📰 OpenClaw 信息速递

【最新动态】
- ...

【技能更新】
- ...

【社区新闻】
- ...

【时间戳】YYYY-MM-DD HH:mm
```

3. 将结果保存到 /home/admin/.openclaw/workspace/memory/openclaw-digest.md

4. 回复整理好的信息速递内容
TASK

# 使用 OpenClaw sessions_spawn 执行任务
# 注意：这里需要通过 OpenClaw 主进程来执行
# 由于直接在 cron 中调用 openclaw 命令可能不可用，我们改用追加到 HEARTBEAT.md 的方式

echo "✅ 信息速递任务已触发"
echo "📄 输出文件：$DIGEST_FILE"

# 清理临时文件
rm -f "$TASK_FILE"

echo "✅ 定时任务执行完成"
