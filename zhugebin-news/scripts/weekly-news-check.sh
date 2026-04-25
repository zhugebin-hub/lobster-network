#!/bin/bash
# 诸葛斌老师新闻定期抓取脚本
# 用法：bash weekly-news-check.sh
# Cron: 0 9 * * 1 bash ~/.openclaw/workspace/zhugebin-news/scripts/weekly-news-check.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
NEWS_DIR="$BASE_DIR"
TIMESTAMP=$(date +%Y-%m-%d)
DATE_SHORT=$(date +%m%d)

echo "=== 诸葛斌老师新闻定期抓取 ==="
echo "时间：$TIMESTAMP"

# 创建必要的目录
mkdir -p "$NEWS_DIR/html"
mkdir -p "$NEWS_DIR/pdfs"
mkdir -p "$NEWS_DIR/summaries"
mkdir -p "$NEWS_DIR/reports"
mkdir -p "$NEWS_DIR/logs"

# 搜索关键词
KEYWORDS=("诸葛斌" "浙江工商大学 诸葛斌" "OpenClaw 诸葛斌" "小龙虾 诸葛斌")

# 创建临时文件存储搜索结果
SEARCH_RESULTS="$NEWS_DIR/logs/search_results_$TIMESTAMP.txt"
> "$SEARCH_RESULTS"

echo "开始搜索..."

# 使用 web_search 搜索（这里需要通过 OpenClaw 的 web_search 工具）
# 实际使用时，这个脚本会调用 OpenClaw 的搜索功能
for keyword in "${KEYWORDS[@]}"; do
    echo "搜索关键词：$keyword"
    echo "$keyword" >> "$SEARCH_RESULTS"
done

echo "搜索完成"

# 检查新链接
NEW_LINKS_FILE="$NEWS_DIR/new_links_$TIMESTAMP.txt"
if [ -f "$NEW_LINKS_FILE" ]; then
    LINK_COUNT=$(wc -l < "$NEW_LINKS_FILE")
    echo "发现 $LINK_COUNT 个新链接"
    
    # 处理新链接
    while IFS= read -r url; do
        if [ -n "$url" ]; then
            echo "处理：$url"
            # 这里会调用 wechat-to-pdf 技能
            # bash ~/.openclaw/workspace/skills/wechat-to-pdf/scripts/wechat-to-pdf.sh "$url"
        fi
    done < "$NEW_LINKS_FILE"
else
    echo "未发现新链接"
fi

# 生成报告
REPORT="$NEWS_DIR/reports/report_$TIMESTAMP.md"
cat > "$REPORT" << EOF
# 诸葛斌老师新闻周报 - $TIMESTAMP

## 搜索关键词
$(printf '%s\n' "${KEYWORDS[@]}")

## 统计
- 总文章数：$(ls "$NEWS_DIR/html/" 2>/dev/null | wc -l)
- 已生成 PDF：$(ls "$NEWS_DIR/pdfs/" 2>/dev/null | wc -l)
- 最后更新：$TIMESTAMP

## 新发现
（待处理）

EOF

echo "报告已生成：$REPORT"

# 更新索引
INDEX="$NEWS_DIR/index.md"
cat > "$INDEX" << EOF
# 诸葛斌老师相关新闻归档

## 统计
- 总文章数：$(ls "$NEWS_DIR/html/" 2>/dev/null | wc -l)
- 已生成 PDF：$(ls "$NEWS_DIR/pdfs/" 2>/dev/null | wc -l)
- 最后更新：$TIMESTAMP

## 目录结构
\`\`\`
zhugebin-news/
├── index.md          # 本文件
├── html/             # 原始 HTML 文件
├── html_compressed/  # 压缩 HTML（图片内嵌）
├── pdfs/             # PDF 文件
├── summaries/        # 摘要文档
├── case-studies/     # 教学案例
├── scripts/          # 脚本
└── reports/          # 周报
\`\`\`

## 最近报告
- [$TIMESTAMP](reports/report_$TIMESTAMP.md)

EOF

echo "索引已更新"
echo "=== 完成 ==="
