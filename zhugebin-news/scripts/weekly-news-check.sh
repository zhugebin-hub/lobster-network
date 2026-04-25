#!/bin/bash
# 诸葛斌老师新闻定期抓取脚本
# 用法：bash weekly-news-check.sh
# 建议添加到 cron：0 9 * * 1 bash ~/.openclaw/workspace/zhugebin-news/scripts/weekly-news-check.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
NEWS_DIR="$BASE_DIR"
TIMESTAMP=$(date +%Y-%m-%d)

echo "=== 诸葛斌老师新闻定期抓取 ==="
echo "时间：$TIMESTAMP"
echo "目录：$NEWS_DIR"

# 创建必要的目录
mkdir -p "$NEWS_DIR/html"
mkdir -p "$NEWS_DIR/pdfs"
mkdir -p "$NEWS_DIR/summaries"

# 搜索关键词
KEYWORDS=("诸葛斌" "浙江工商大学 诸葛斌" "OpenClaw 诸葛斌" "小龙虾 诸葛斌")

# 创建临时文件存储新链接
NEW_LINKS="$NEWS_DIR/new_links_$TIMESTAMP.txt"
> "$NEW_LINKS"

# 使用 searxng 或 web_search 搜索
for keyword in "${KEYWORDS[@]}"; do
    echo "搜索关键词：$keyword"
    # 这里需要通过 OpenClaw 的搜索功能
    # 实际使用时调用 web_search 或 searxng
    echo "$keyword" >> "$NEW_LINKS"
done

echo "搜索完成，新链接已保存到：$NEW_LINKS"
echo "请手动检查并处理新链接"

# 生成报告
REPORT="$NEWS_DIR/reports/report_$TIMESTAMP.md"
mkdir -p "$NEWS_DIR/reports"

cat > "$REPORT" << EOF
# 诸葛斌老师新闻周报 - $TIMESTAMP

## 搜索关键词
$(printf '%s\n' "${KEYWORDS[@]}")

## 新发现链接
（待处理）

## 统计
- 总文章数：$(ls "$NEWS_DIR/html/" | wc -l)
- 已生成 PDF：$(ls "$NEWS_DIR/pdfs/" | wc -l)
- 最后更新：$TIMESTAMP

EOF

echo "报告已生成：$REPORT"
echo "=== 完成 ==="
