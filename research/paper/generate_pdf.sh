#!/bin/bash
# PDF 生成脚本
# 使用浏览器打印功能生成 PDF

cd /home/admin/.openclaw/workspace/research/paper

echo "📄 正在生成 PDF..."
echo ""
echo "方法 1：使用 Chrome/Chromium 命令行"
if command -v google-chrome &> /dev/null; then
    google-chrome --headless --disable-gpu --print-to-pdf=paper_draft_v1.pdf --print-to-pdf-no-header paper_draft_v1.html
    echo "✅ Chrome 生成完成：paper_draft_v1.pdf"
elif command -v chromium &> /dev/null; then
    chromium --headless --disable-gpu --print-to-pdf=paper_draft_v1.pdf --print-to-pdf-no-header paper_draft_v1.html
    echo "✅ Chromium 生成完成：paper_draft_v1.pdf"
else
    echo "⚠️  未找到 Chrome/Chromium"
    echo ""
    echo "方法 2：手动从 HTML 打印"
    echo "1. 用浏览器打开：paper_draft_v1.html"
    echo "2. 按 Ctrl+P (或 Cmd+P)"
    echo "3. 选择'另存为 PDF'"
    echo "4. 保存为 paper_draft_v1.pdf"
    echo ""
    echo "方法 3：使用 Overleaf"
    echo "1. 访问 https://www.overleaf.com"
    echo "2. 上传 paper_v1.tex 和 references.bib"
    echo "3. 点击 Recompile 生成 PDF"
fi

echo ""
echo "当前可用文件："
ls -lh paper_draft_v1.md paper_v1.tex paper_draft_v1.html 2>/dev/null
