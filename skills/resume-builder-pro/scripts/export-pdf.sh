#!/bin/bash
# export-pdf.sh - HTML 简历导出为 PDF

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# 默认参数
INPUT=""
OUTPUT=""
FORMAT="A4"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --input|-i)
      INPUT="$2"
      shift 2
      ;;
    --output|-o)
      OUTPUT="$2"
      shift 2
      ;;
    --format)
      FORMAT="$2"
      shift 2
      ;;
    --help)
      echo "用法：./export-pdf.sh [选项]"
      echo ""
      echo "选项:"
      echo "  --input, -i <文件>    输入 HTML 文件路径"
      echo "  --output, -o <文件>   输出 PDF 文件路径"
      echo "  --format <格式>       PDF 格式 (A4|Letter)"
      echo "  --help                显示帮助"
      exit 0
      ;;
    *)
      # 位置参数
      if [ -z "$INPUT" ]; then
        INPUT="$1"
      elif [ -z "$OUTPUT" ]; then
        OUTPUT="$1"
      fi
      shift
      ;;
  esac
done

# 检查输入文件
if [ -z "$INPUT" ] || [ ! -f "$INPUT" ]; then
  echo "❌ 错误：请输入有效的 HTML 文件路径"
  echo "用法：./export-pdf.sh resume.html output.pdf"
  exit 1
fi

# 默认输出文件名
if [ -z "$OUTPUT" ]; then
  OUTPUT="${INPUT%.html}.pdf"
fi

echo "📄 HTML → PDF 转换器"
echo "==================="
echo "输入：$INPUT"
echo "输出：$OUTPUT"
echo "格式：$FORMAT"
echo ""

# 检查 Node.js 和 Puppeteer
if ! command -v node &> /dev/null; then
  echo "❌ 错误：需要安装 Node.js"
  exit 1
fi

# 检查 Puppeteer 是否安装
if [ ! -d "$SKILL_DIR/node_modules/puppeteer" ]; then
  echo "📦 安装 Puppeteer..."
  cd "$SKILL_DIR"
  npm install puppeteer --save
fi

# 创建转换脚本
CONVERT_SCRIPT="$SKILL_DIR/scripts/convert-to-pdf.js"
cat > "$CONVERT_SCRIPT" << 'EOF'
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

const inputFile = process.argv[2];
const outputFile = process.argv[3];
const format = process.argv[4] || 'A4';

if (!inputFile || !outputFile) {
  console.error('用法：node convert-to-pdf.js <input.html> <output.pdf> [format]');
  process.exit(1);
}

if (!fs.existsSync(inputFile)) {
  console.error('错误：输入文件不存在 -', inputFile);
  process.exit(1);
}

(async () => {
  console.log('🚀 启动浏览器...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });
  
  console.log('📑 打开页面...');
  const page = await browser.newPage();
  await page.goto(`file://${path.resolve(inputFile)}`, { 
    waitUntil: 'load', 
    timeout: 60000 
  });
  
  console.log('📥 生成 PDF...');
  await page.pdf({
    path: outputFile,
    format: format,
    printBackground: true,
    margin: {
      top: '15mm',
      right: '15mm',
      bottom: '15mm',
      left: '15mm'
    }
  });
  
  await browser.close();
  console.log('✅ PDF 生成成功:', outputFile);
})();
EOF

# 执行转换
echo "🔄 转换中..."
node "$CONVERT_SCRIPT" "$INPUT" "$OUTPUT" "$FORMAT"

echo ""
echo "✅ 完成！"
echo "📁 PDF 位置：$OUTPUT"
