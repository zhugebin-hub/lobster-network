#!/bin/bash
# OpenClaw 信息速递 - 每 12 小时自动搜索并发送最新消息
# 用于教材"信息速递"板块

WORKSPACE="/home/admin/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
DIGEST_FILE="$MEMORY_DIR/openclaw-digest.md"

# 创建记忆目录
mkdir -p "$MEMORY_DIR"

# 获取当前日期
DATE=$(date +"%Y-%m-%d %H:%M")

# 搜索 OpenClaw 最新消息
echo "🔍 搜索 OpenClaw 最新消息..."

# 使用 clawhub 获取最新技能更新
CLAWHUB_NEWS=$(clawhub explore --limit 5 2>/dev/null || echo "暂无更新")

# 搜索网络新闻
WEB_SEARCH_RESULTS=$(curl -s "https://api.search.brave.com/res/v1/web/search?q=OpenClaw+AI+framework+update&count=5" 2>/dev/null || echo "")

# 生成信息速递
cat > "$DIGEST_FILE" << EOF
# 📰 OpenClaw 信息速递

**生成时间**: $DATE

---

## 【最新动态】

正在搜索 OpenClaw 最新消息...

## 【技能更新】

$CLAWHUB_NEWS

## 【社区新闻】

正在搜集中...

## 【推荐阅读】

- OpenClaw 文档：https://docs.openclaw.ai
- 技能市场：https://clawhub.com
- 社区 Discord：https://discord.com/invite/clawd

---

*此信息速递每 12 小时自动更新*
EOF

echo "✅ 信息速递已生成：$DIGEST_FILE"
echo "📄 内容预览："
cat "$DIGEST_FILE"
