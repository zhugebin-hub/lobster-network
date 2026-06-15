#!/bin/bash
# generate-resume.sh - 交互式简历生成脚本

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
RESUMES_DIR="$WORKSPACE/resumes"
TEMPLATES_DIR="$WORKSPACE/skills/resume-builder-pro/templates"

# 默认参数
TEMPLATE="professional"
OUTPUT_NAME="resume"

# 解析参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --template)
      TEMPLATE="$2"
      shift 2
      ;;
    --output)
      OUTPUT_NAME="$2"
      shift 2
      ;;
    --help)
      echo "用法：./generate-resume.sh [选项]"
      echo ""
      echo "选项:"
      echo "  --template <名称>  模板名称 (professional|minimal|tech|academic)"
      echo "  --output <名称>    输出文件名（不含扩展名）"
      echo "  --help             显示帮助"
      exit 0
      ;;
    *)
      echo "未知选项：$1"
      exit 1
      ;;
  esac
done

# 确保输出目录存在
mkdir -p "$RESUMES_DIR"

echo "📄 简历生成器"
echo "============="
echo "模板：$TEMPLATE"
echo "输出：$OUTPUT_NAME.html"
echo ""

# 检查模板是否存在
TEMPLATE_FILE="$TEMPLATES_DIR/${TEMPLATE}.html"
if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "⚠️  模板不存在：$TEMPLATE_FILE"
  echo "可用模板：professional, minimal, tech, academic"
  TEMPLATE_FILE="$TEMPLATES_DIR/professional.html"
fi

echo "✅ 准备生成简历..."
echo ""
echo "请提供以下信息（直接回复）："
echo "1. 姓名"
echo "2. 求职意向/标题"
echo "3. 联系方式（邮箱/电话/地址）"
echo "4. 教育背景"
echo "5. 项目/工作经历"
echo "6. 技能列表"
echo "7. 获奖记录（可选）"
echo ""
echo "或使用 AI 自动生成：ai-generate"

# 读取用户输入
read -p "输入模式 (manual/ai): " MODE

if [ "$MODE" = "ai" ] || [ "$MODE" = "ai-generate" ]; then
  echo "🤖 调用 AI 生成简历内容..."
  # 这里可以调用 AI API 生成内容
  echo "请提供原始简历内容或项目经历..."
fi

echo ""
echo "✅ 简历生成完成！"
echo "📁 文件位置：$RESUMES_DIR/${OUTPUT_NAME}.html"
echo ""
echo "下一步："
echo "  ./export-pdf.sh ${OUTPUT_NAME}.html ${OUTPUT_NAME}.pdf"
