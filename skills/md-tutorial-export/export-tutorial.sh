#!/bin/bash
# MD Tutorial Export Script
# Usage: ./export-tutorial.sh <input-dir> [output-name]

set -e

INPUT_DIR="$1"
OUTPUT_NAME="${2:-tutorial-export}"

if [ -z "$INPUT_DIR" ]; then
  echo "Usage: $0 <input-dir> [output-name]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
TEMP_DIR="$WORKSPACE/$OUTPUT_NAME-temp"

echo "🦞 MD Tutorial Export"
echo "===================="
echo "Input: $INPUT_DIR"
echo "Output: $OUTPUT_NAME"
echo ""

# Step 1: Convert MD to HTML
echo "📄 Step 1: Converting Markdown to HTML..."
node "$SCRIPT_DIR/md2pdf.js" "$INPUT_DIR" "$TEMP_DIR"

# Step 2: Convert HTML to PDF
echo ""
echo "📋 Step 2: Generating PDFs with Chrome..."
cd "$TEMP_DIR"
for f in *.html; do
  pdf_name="${f%.html}.pdf"
  google-chrome --headless --disable-gpu \
    --print-to-pdf="$pdf_name" \
    --print-to-pdf-no-header \
    --print-to-pdf-no-footer \
    "file://$(pwd)/$f" 2>/dev/null
  echo "  ✓ $pdf_name"
done

# Step 3: Create ZIP
echo ""
echo "📦 Step 3: Creating ZIP package..."
zip "$OUTPUT_NAME-pdf.zip" *.pdf

# Cleanup temp files
cd "$WORKSPACE"
rm -rf "$TEMP_DIR"

echo ""
echo "✅ Done! Output: $WORKSPACE/$OUTPUT_NAME-pdf.zip"
echo ""
echo "To send via DingTalk:"
echo "  message action=send channel=dingtalk target=<chat-id> filePath=$WORKSPACE/$OUTPUT_NAME-pdf.zip"
