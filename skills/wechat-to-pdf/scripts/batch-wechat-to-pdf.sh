#!/bin/bash
# 批量处理微信公众号文章转 PDF
# 用法：bash batch-wechat-to-pdf.sh

set -e

# 新闻链接列表
URLS=(
    "https://mp.weixin.qq.com/s/-JU5G9GoygeiGI8S_fHq_Q"
    "https://mp.weixin.qq.com/s/s_8FnG6BjpkCi9OnUsUJTw"
    "https://mp.weixin.qq.com/s/yCObYePPWFiuoAQDiIr1yQ"
    "https://mp.weixin.qq.com/s/cRe5Uz2-nXC35lyMNcugIQ"
    "https://mp.weixin.qq.com/s/DiGmRJRpnyn3MFqVDHNX_A"
    "https://mp.weixin.qq.com/s/ae8zHwJgDr6d-PWWNQQ_RQ"
    "https://mp.weixin.qq.com/s/Q_SxNRaZaAiSZBByFlxo7A"
    "https://mp.weixin.qq.com/s/n24Gr6P6isRynqAh1-hmBQ"
    "https://mp.weixin.qq.com/s/aBtAbWruUoX0_zgmG365wg"
    "https://mp.weixin.qq.com/s/jtTJYFMwUQNEa728aIYhZA"
    "https://mp.weixin.qq.com/s/3AwNLhTldBdWEiQXL6i-vA"
    "https://mp.weixin.qq.com/s/tGad_FyIZ5hhpO8rdBuUkA"
    "https://mp.weixin.qq.com/s/mOnapGBdhkPfkEl-4v7-Mg"
)

# 标题映射
TITLES=(
    "信息与电子工程学院举办拥抱AI+时代教学开放周活动"
    "数智赋能智启未来-特级管理会计师MAPA数智化管理会计创新研讨会在杭州顺利举办"
    "解锁AI新生产力-浙青创小龙虾AI数字员工主题分享会圆满落幕"
    "深化教育数字化转型赋能优学在嘉提质升级-2026年度嘉兴市教育系统首席信息官CIO培训班圆满举办"
    "AI助理赋能智慧图书馆-图书馆馆员学堂第二十二期开讲"
    "我院学子荣获首届阿里小龙虾大会黑客松勇士称号"
    "2025年度高光-教学提质攀新高成果硬核耀全年"
    "快乐校园青年爱学习-第九期博研人才研究生干部培训班开班仪式暨第一次课程培训"
    "研会星空夜话-拥抱AI+时代赋能未来课堂"
    "讲座报名-诸葛斌教授讲授人工智能Deepseek及其操作实战"
    "教师教学发展中心举办Deepseek在教学科研中的应用教学沙龙"
    "新书速递-袁非牛等著数字人文AI情感分析与文化生成"
    "AI执笔绘学术新章-浙江工商大学研究生DeepSeek课程圆满结课"
)

SKILL_DIR="/home/admin/.openclaw/workspace/skills/wechat-to-pdf"
OUTPUT_DIR="/home/admin/.openclaw/workspace/zhugebin-news/pdfs-v2"
TEMP_BASE="/tmp/wechat_batch"

mkdir -p "$OUTPUT_DIR"
mkdir -p "$TEMP_BASE"

echo "微信公众号文章批量转 PDF"
echo "输出目录：$OUTPUT_DIR"
echo "=========================="

for i in "${!URLS[@]}"; do
    URL="${URLS[$i]}"
    TITLE="${TITLES[$i]}"
    INDEX=$((i + 1))
    
    echo ""
    echo "[$INDEX/${#URLS[@]}] 处理：$TITLE"
    echo "URL: $URL"
    
    TEMP_DIR="$TEMP_BASE/$INDEX"
    mkdir -p "$TEMP_DIR"
    mkdir -p "$TEMP_DIR/images"
    
    # 步骤 1：抓取 HTML
    echo "  步骤 1/5：抓取 HTML 源码..."
    curl -s -L \
        -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36" \
        -H "Accept: text/html" \
        -H "Accept-Language: zh-CN,zh;q=0.9" \
        "$URL" > "$TEMP_DIR/raw.html"
    
    if [ ! -s "$TEMP_DIR/raw.html" ]; then
        echo "  ❌ 错误：无法获取 HTML"
        continue
    fi
    
    echo "  HTML 大小：$(wc -c < "$TEMP_DIR/raw.html") bytes"
    
    # 步骤 2：提取正文和图片
    echo "  步骤 2/5：提取正文和图片..."
    python3 "$SKILL_DIR/scripts/extract_wechat.py" "$TEMP_DIR/raw.html" "$TEMP_DIR"
    
    # 步骤 3：生成自包含 HTML
    echo "  步骤 3/5：生成自包含 HTML..."
    python3 "$SKILL_DIR/scripts/generate_html.py" "$TEMP_DIR/content.html" "$TEMP_DIR/images" "$TEMP_DIR/final.html"
    
    # 步骤 4：使用 Playwright 生成 PDF
    echo "  步骤 4/5：生成 PDF..."
    python3 -c "
import asyncio
from playwright.async_api import async_playwright
import os

async def generate_pdf():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'file://$TEMP_DIR/final.html', wait_until='networkidle', timeout=30000)
        await page.wait_for_timeout(2000)
        await page.pdf(
            path='$OUTPUT_DIR/$TITLE.pdf',
            format='A4',
            print_background=True,
            margin={'top': '15mm', 'bottom': '15mm', 'left': '15mm', 'right': '15mm'}
        )
        await browser.close()
        print(f'  PDF 已保存：$OUTPUT_DIR/$TITLE.pdf')

asyncio.run(generate_pdf())
"
    
    # 延迟避免被限制
    sleep 3
done

echo ""
echo "=========================="
echo "批量处理完成！"
echo "输出目录：$OUTPUT_DIR"
echo ""
ls -lh "$OUTPUT_DIR"/*.pdf 2>/dev/null || echo "未找到 PDF 文件"
