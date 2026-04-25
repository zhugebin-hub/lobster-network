#!/bin/bash
# 批量生成 PDF 脚本
# 用法：bash batch-generate-pdfs.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
NEWS_DIR="$BASE_DIR"
TIMESTAMP=$(date +%Y-%m-%d)

echo "=== 批量生成 PDF ==="
echo "时间：$TIMESTAMP"

# 检查 HTML 目录
HTML_DIR="$NEWS_DIR/html_compressed"
PDF_DIR="$NEWS_DIR/pdfs"

if [ ! -d "$HTML_DIR" ]; then
    echo "错误：HTML 目录不存在"
    exit 1
fi

mkdir -p "$PDF_DIR"

# 统计
TOTAL=$(ls "$HTML_DIR"/*.html 2>/dev/null | wc -l)
EXISTING=$(ls "$PDF_DIR"/*.pdf 2>/dev/null | wc -l)

echo "总 HTML 文件：$TOTAL"
echo "已有 PDF 文件：$EXISTING"

# 这里需要通过 OpenClaw 的 browser 工具来生成 PDF
# 实际使用时，这个脚本会调用 OpenClaw 的浏览器工具
echo "PDF 生成需要通过 OpenClaw 浏览器工具完成"
echo "请手动执行以下操作："
echo "1. 打开浏览器工具"
echo "2. 访问 http://localhost:8899/文件名.html"
echo "3. 导出 PDF 到 $PDF_DIR/"

echo "=== 完成 ==="
