#!/bin/bash
# 微信公众号文章转 PDF 主脚本
# 用法：bash wechat-to-pdf.sh "https://mp.weixin.qq.com/s/xxxxx"

set -e

# 检查参数
if [ -z "$1" ]; then
    echo "错误：请提供微信公众号文章链接"
    echo "用法：bash wechat-to-pdf.sh \"https://mp.weixin.qq.com/s/xxxxx\""
    exit 1
fi

URL="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMP_DIR="/tmp/wechat_pdf_$$"

# 创建临时目录
mkdir -p "$TEMP_DIR"
mkdir -p "$TEMP_DIR/images"

echo "开始处理微信公众号文章..."
echo "URL: $URL"

# 步骤 1：抓取 HTML 源码
echo "步骤 1/5：抓取 HTML 源码..."
curl -s -L \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
    -H "Accept: text/html" \
    -H "Accept-Language: zh-CN,zh;q=0.9" \
    "$URL" > "$TEMP_DIR/raw.html"

if [ ! -s "$TEMP_DIR/raw.html" ]; then
    echo "错误：无法获取 HTML 源码"
    exit 1
fi

echo "HTML 源码已保存：$(wc -c < "$TEMP_DIR/raw.html") bytes"

# 步骤 2：提取正文和图片
echo "步骤 2/5：提取正文和图片..."
python3 "$SCRIPT_DIR/extract_wechat.py" "$TEMP_DIR/raw.html" "$TEMP_DIR"

if [ ! -f "$TEMP_DIR/content.html" ]; then
    echo "错误：无法提取正文内容"
    exit 1
fi

echo "正文内容已提取"

# 步骤 3：生成自包含 HTML
echo "步骤 3/5：生成自包含 HTML..."
python3 "$SCRIPT_DIR/generate_html.py" "$TEMP_DIR/content.html" "$TEMP_DIR/images" "$TEMP_DIR/final.html"

if [ ! -f "$TEMP_DIR/final.html" ]; then
    echo "错误：无法生成 HTML"
    exit 1
fi

echo "HTML 已生成：$(wc -c < "$TEMP_DIR/final.html") bytes"

# 步骤 4：启动 HTTP 服务器
echo "步骤 4/5：启动 HTTP 服务器..."
cd "$TEMP_DIR"
python3 -m http.server 8899 &
SERVER_PID=$!
sleep 2

# 步骤 5：生成 PDF
echo "步骤 5/5：生成 PDF..."
# 这里需要调用 OpenClaw browser 工具
# 实际使用时需要通过 OpenClaw 的 browser 工具来生成 PDF

echo "PDF 生成中..."
echo "请使用 OpenClaw browser 工具访问 http://localhost:8899/final.html 并导出 PDF"

# 清理
echo "清理临时文件..."
# kill $SERVER_PID 2>/dev/null
# rm -rf "$TEMP_DIR"

echo "完成！"
echo "HTML 文件：$TEMP_DIR/final.html"
echo "PDF 文件：待生成"
