#!/bin/bash
# OpenClaw 学习记录添加工具
# 快速添加学习记录到 LEARNINGS.md

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 工作目录
WORKSPACE="$HOME/.openclaw/workspace"
LEARNINGS_FILE="$WORKSPACE/.learnings/LEARNINGS.md"

# 显示帮助
show_help() {
    cat << EOF
📝 OpenClaw 学习记录添加工具

用法：$0 [选项] <学习内容>

选项:
  -t, --type TYPE      记录类型：learning | error | feature (默认：learning)
  -p, --priority PRI   优先级：low | medium | high | critical (默认：medium)
  -a, --area AREA      领域：docs | infra | teaching | skill (默认：docs)
  -s, --source SOURCE  来源：task | user | error | research (默认：task)
  -f, --file FILE      相关文件路径
  -g, --tag TAG        标签（可重复使用）
  -h, --help           显示帮助信息

示例:
  $0 "完成了 Hermes 调研"
  $0 -t error "API 调用失败" -p high
  $0 -t feature "需要语义搜索" -a infra
  $0 "教学需求分析完成" -a teaching -f teaching-automation-requirements.md

EOF
}

# 生成 ID
generate_id() {
    local type="$1"
    local date=$(date +%Y%m%d)
    local random=$(head /dev/urandom | tr -dc 'A-Z0-9' | head -c 3)
    echo "${type}-${date}-${random}"
}

# 默认参数
TYPE="learning"
PRIORITY="medium"
AREA="docs"
SOURCE="task"
FILES=""
TAGS=""
CONTENT=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TYPE="$2"
            shift 2
            ;;
        -p|--priority)
            PRIORITY="$2"
            shift 2
            ;;
        -a|--area)
            AREA="$2"
            shift 2
            ;;
        -s|--source)
            SOURCE="$2"
            shift 2
            ;;
        -f|--file)
            if [ -n "$FILES" ]; then
                FILES="$FILES, $2"
            else
                FILES="$2"
            fi
            shift 2
            ;;
        -g|--tag)
            if [ -n "$TAGS" ]; then
                TAGS="$TAGS, $2"
            else
                TAGS="$2"
            fi
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            CONTENT="$1"
            shift
            ;;
    esac
done

# 检查内容
if [ -z "$CONTENT" ]; then
    echo -e "${RED}❌ 错误：请提供学习内容${NC}"
    echo ""
    show_help
    exit 1
fi

# 确保目录存在
mkdir -p "$(dirname "$LEARNINGS_FILE")"

# 创建文件（如果不存在）
if [ ! -f "$LEARNINGS_FILE" ]; then
    cat > "$LEARNINGS_FILE" << 'EOF'
# Learnings Log

> OpenClaw 自改进学习日志
> 创建时间：$(date +%Y-%m-%d)

---

## 学习记录

EOF
fi

# 生成 ID
case $TYPE in
    learning)
        ID=$(generate_id "LRN")
        SECTION="## 学习记录"
        ;;
    error)
        ID=$(generate_id "ERR")
        SECTION="## 错误记录"
        ;;
    feature)
        ID=$(generate_id "FEAT")
        SECTION="## 功能请求"
        ;;
    *)
        ID=$(generate_id "LRN")
        SECTION="## 学习记录"
        ;;
esac

# 时间戳
TIMESTAMP=$(date -Iseconds)

# 创建临时文件
TEMP_FILE=$(mktemp)

# 读取原文件
IN_SECTION=false
SECTION_FOUND=false

while IFS= read -r line || [ -n "$line" ]; do
    echo "$line" >> "$TEMP_FILE"
    
    # 检查是否到达目标章节
    if [[ "$line" == "$SECTION" ]]; then
        SECTION_FOUND=true
        IN_SECTION=true
        continue
    fi
    
    # 如果是新章节的开始，且我们在目标章节中，插入新记录
    if [[ "$line" == "## "* ]] && [ "$IN_SECTION" = true ] && [[ "$line" != "$SECTION" ]]; then
        # 插入新记录
        cat >> "$TEMP_FILE" << EOF

### [$ID] $CONTENT

**Logged**: $TIMESTAMP
**Priority**: $PRIORITY
**Status**: pending
**Area**: $AREA

### Summary
$CONTENT

### Details
待补充详细信息...

### Suggested Action
待补充建议操作...

### Metadata
- Source: $SOURCE
$(if [ -n "$FILES" ]; then echo "- Related Files: $FILES"; fi)
$(if [ -n "$TAGS" ]; then echo "- Tags: $TAGS"; fi)

---

EOF
        IN_SECTION=false
    fi
done < "$LEARNINGS_FILE"

# 如果章节不存在或文件末尾，追加到文件末尾
if [ "$SECTION_FOUND" = false ] || [ "$IN_SECTION" = true ]; then
    # 添加章节（如果不存在）
    if [ "$SECTION_FOUND" = false ]; then
        echo "" >> "$TEMP_FILE"
        echo "$SECTION" >> "$TEMP_FILE"
        echo "" >> "$TEMP_FILE"
    fi
    
    # 添加新记录
    cat >> "$TEMP_FILE" << EOF

### [$ID] $CONTENT

**Logged**: $TIMESTAMP
**Priority**: $PRIORITY
**Status**: pending
**Area**: $AREA

### Summary
$CONTENT

### Details
待补充详细信息...

### Suggested Action
待补充建议操作...

### Metadata
- Source: $SOURCE
$(if [ -n "$FILES" ]; then echo "- Related Files: $FILES"; fi)
$(if [ -n "$TAGS" ]; then echo "- Tags: $TAGS"; fi)

---

EOF
fi

# 替换原文件
mv "$TEMP_FILE" "$LEARNINGS_FILE"

# 显示结果
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ 学习记录已添加${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${CYAN}记录 ID:${NC} $ID"
echo -e "${CYAN}类型:${NC} $TYPE"
echo -e "${CYAN}优先级:${NC} $PRIORITY"
echo -e "${CYAN}领域:${NC} $AREA"
echo -e "${CYAN}内容:${NC} $CONTENT"
echo ""
echo -e "${YELLOW}📝 文件位置:${NC}"
echo "  $LEARNINGS_FILE"
echo ""
echo -e "${YELLOW}💡 下一步:${NC}"
echo "  1. 编辑文件补充详细信息"
echo "  2. 任务完成后更新状态为 resolved"
echo "  3. 如适用，promote 到 MEMORY.md 或其他文档"
echo ""
echo -e "${BLUE}================================${NC}"
