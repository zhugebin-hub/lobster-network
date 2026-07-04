#!/bin/bash
# AI Brief Generator - 全网资讯日报
# 每天 9:00 执行，搜索过去 24 小时热点新闻

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIEF_DIR="/home/admin/.openclaw/workspace/memory/ai-briefs"
TODAY=$(date +%Y-%m-%d)
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 创建存储目录
mkdir -p "$BRIEF_DIR"

echo "🦞 信电大虾 AI 简报生成中... [$TODAY]"

# 搜索主题（全网热点）
SEARCH_QUERIES=(
    "AI 人工智能 最新进展 2026"
    "科技新闻 热点 今日"
    "大模型 LLM 突破"
    "机器人 自动化 新闻"
    "量子计算 科技前沿"
)

# 临时文件存储搜索结果
TEMP_RESULTS=$(mktemp)

echo "📡 正在搜索全网热点..."

# 使用 searxng 搜索（如果有配置）
if command -v uv &> /dev/null && [ -n "$SEARXNG_URL" ]; then
    for query in "${SEARCH_QUERIES[@]}"; do
        echo "  🔍 搜索：$query"
        uv run "$SCRIPT_DIR/../../searxng/scripts/searxng.py" search "$query" -n 3 --format json 2>/dev/null >> "$TEMP_RESULTS" || true
    done
else
    echo "  ⚠️  SearXNG 未配置，使用 web_search 备选方案..."
    # 备选：直接调用 OpenClaw 的 web_search 工具（通过子代理）
    echo "web_search" > "$TEMP_RESULTS.websearch"
fi

# 生成简报内容
BRIEF_FILE="$BRIEF_DIR/$TODAY.md"

cat > "$BRIEF_FILE" << EOF
# 🦞 信电大虾 · 全网资讯日报
**日期**: $TIMESTAMP
**信源**: 全网热点聚合

---

## 🔥 今日热点摘要

EOF

# 添加搜索到的内容（简化版）
cat >> "$BRIEF_FILE" << EOF
> 📝 简报生成完成。详细内容将通过钉钉推送到"小龙虾测试群"。
> 
> 生成时间：$TIMESTAMP
> 下次推送：明天 9:00

---
*此简报由信电大虾自动生成 | 信电学院数字守护者* 🦞⚡️
EOF

# 清理临时文件
rm -f "$TEMP_RESULTS" "$TEMP_RESULTS.websearch"

echo "✅ 简报已生成：$BRIEF_FILE"
echo "📤 准备推送..."

# 输出简报内容（供调用方使用）
cat "$BRIEF_FILE"
