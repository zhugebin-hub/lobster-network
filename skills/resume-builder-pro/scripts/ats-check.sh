#!/bin/bash
# ats-check.sh - ATS 兼容性检查脚本

set -e

RESUME_FILE="$1"

if [ -z "$RESUME_FILE" ]; then
  echo "用法：./ats-check.sh <resume.html|resume.md>"
  exit 1
fi

if [ ! -f "$RESUME_FILE" ]; then
  echo "❌ 文件不存在：$RESUME_FILE"
  exit 1
fi

echo "🔍 ATS 兼容性检查"
echo "================="
echo "文件：$RESUME_FILE"
echo ""

SCORE=0
TOTAL=10

# 检查项 1：标准章节标题
echo "□ 检查章节标题..."
if grep -qE "(教育背景|工作经历|项目经历|技术技能|获奖记录)" "$RESUME_FILE"; then
  echo "  ✅ 包含标准章节标题"
  SCORE=$((SCORE + 1))
else
  echo "  ⚠️  建议使用标准章节标题（教育背景、工作经历等）"
fi

# 检查项 2：无表格布局
echo "□ 检查表格布局..."
if grep -q "<table" "$RESUME_FILE"; then
  echo "  ⚠️  检测到表格布局，ATS 可能无法解析"
else
  echo "  ✅ 无表格布局"
  SCORE=$((SCORE + 1))
fi

# 检查项 3：联系方式
echo "□ 检查联系方式..."
if grep -qE "(📧|📱|@|[0-9]{11})" "$RESUME_FILE"; then
  echo "  ✅ 包含联系方式"
  SCORE=$((SCORE + 1))
else
  echo "  ⚠️  建议添加邮箱和电话"
fi

# 检查项 4：量化成果
echo "□ 检查量化成果..."
if grep -qE "([0-9]+%|[0-9]+ 万|\$[0-9]+|[0-9]+ 人)" "$RESUME_FILE"; then
  echo "  ✅ 包含量化数据"
  SCORE=$((SCORE + 1))
else
  echo "  ⚠️  建议添加量化成果（百分比、金额、人数等）"
fi

# 检查项 5：动词开头
echo "□ 检查主动语态..."
if grep -qE "(设计 | 开发 | 领导 | 实现 | 优化 | 提升)" "$RESUME_FILE"; then
  echo "  ✅ 使用主动语态动词"
  SCORE=$((SCORE + 1))
else
  echo "  ⚠️  建议使用动词开头（设计、开发、领导等）"
fi

# 检查项 6：关键词密度
echo "□ 检查关键词..."
KEYWORDS=("AI" "Python" "Java" "Agent" "开发")
FOUND=0
for kw in "${KEYWORDS[@]}"; do
  if grep -q "$kw" "$RESUME_FILE"; then
    FOUND=$((FOUND + 1))
  fi
done
if [ $FOUND -ge 3 ]; then
  echo "  ✅ 关键词密度合理 ($FOUND/${#KEYWORDS[@]})"
  SCORE=$((SCORE + 1))
else
  echo "  ⚠️  关键词较少 ($FOUND/${#KEYWORDS[@]})"
fi

# 检查项 7：PDF 可解析
echo "□ 检查输出格式..."
if [[ "$RESUME_FILE" == *.pdf ]]; then
  echo "  ℹ️  PDF 文件，请确保是文本可选格式（非扫描图片）"
  SCORE=$((SCORE + 1))
else
  echo "  ✅ HTML 格式，可转换为 PDF"
  SCORE=$((SCORE + 1))
fi

# 检查项 8：长度控制
echo "□ 检查简历长度..."
WORD_COUNT=$(wc -w < "$RESUME_FILE")
if [ $WORD_COUNT -lt 2000 ]; then
  echo "  ✅ 长度适中 ($WORD_COUNT 词)"
  SCORE=$((SCORE + 1))
else
  echo "  ⚠️  内容可能过长 ($WORD_COUNT 词)，建议精简"
fi

# 检查项 9：无第一人称
echo "□ 检查人称代词..."
if grep -qE "（我 | 我）" "$RESUME_FILE"; then
  echo "  ⚠️  检测到第一人称，建议移除"
else
  echo "  ✅ 无第一人称代词"
  SCORE=$((SCORE + 1))
fi

# 检查项 10：文件格式
echo "□ 检查文件命名..."
if [[ "$RESUME_FILE" =~ [姓名].*\.pdf ]]; then
  echo "  ✅ 文件命名规范"
  SCORE=$((SCORE + 1))
else
  echo "  ℹ️  建议命名：姓名_岗位_简历.pdf"
  SCORE=$((SCORE + 1))
fi

echo ""
echo "================="
echo "得分：$SCORE/$TOTAL"
echo ""

if [ $SCORE -ge 8 ]; then
  echo "✅ ATS 兼容性优秀！"
elif [ $SCORE -ge 6 ]; then
  echo "👍 ATS 兼容性良好，建议优化扣分项"
else
  echo "⚠️  ATS 兼容性需改进，请参考上述建议"
fi
