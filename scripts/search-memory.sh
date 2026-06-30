#!/bin/bash
# OpenClaw 记忆搜索工具
# 支持关键词搜索、日期过滤、上下文显示

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 使用帮助
show_help() {
    cat << EOF
🔍 OpenClaw 记忆搜索工具

用法：$0 [选项] <关键词>

选项:
  -d, --date DATE     搜索指定日期的记忆 (格式：YYYY-MM-DD)
  -t, --type TYPE     搜索类型：memory(每日记忆) | long(长期记忆) | all(全部)
  -c, --context NUM   显示上下文行数 (默认：2)
  -l, --limit NUM     限制结果数量 (默认：20)
  -h, --help          显示帮助信息

示例:
  $0 "Hermes"                    # 搜索所有包含"Hermes"的记忆
  $0 -d 2026-04-19 "调研"        # 搜索指定日期的记忆
  $0 -t long "身份"              # 仅搜索长期记忆
  $0 -c 5 -l 10 "小龙虾"         # 显示 5 行上下文，限制 10 条结果

EOF
}

# 默认参数
CONTEXT_LINES=2
LIMIT=20
SEARCH_TYPE="all"
DATE_FILTER=""
QUERY=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--date)
            DATE_FILTER="$2"
            shift 2
            ;;
        -t|--type)
            SEARCH_TYPE="$2"
            shift 2
            ;;
        -c|--context)
            CONTEXT_LINES="$2"
            shift 2
            ;;
        -l|--limit)
            LIMIT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            QUERY="$1"
            shift
            ;;
    esac
done

# 检查查询词
if [ -z "$QUERY" ]; then
    echo -e "${RED}❌ 错误：请提供搜索关键词${NC}"
    echo ""
    show_help
    exit 1
fi

# 工作目录
WORKSPACE="$HOME/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🔍 搜索记忆：${YELLOW}$QUERY${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

RESULT_COUNT=0

# 搜索长期记忆
if [ "$SEARCH_TYPE" = "long" ] || [ "$SEARCH_TYPE" = "all" ]; then
    MEMORY_FILE="$WORKSPACE/MEMORY.md"
    if [ -f "$MEMORY_FILE" ]; then
        echo -e "${GREEN}📄 长期记忆 (MEMORY.md):${NC}"
        echo -e "─────────────────────────────────────"
        
        RESULTS=$(grep -n -C "$CONTEXT_LINES" "$QUERY" "$MEMORY_FILE" 2>/dev/null || true)
        if [ -n "$RESULTS" ]; then
            echo "$RESULTS" | head -n "$LIMIT"
            RESULT_COUNT=$((RESULT_COUNT + 1))
        else
            echo "  未找到匹配内容"
        fi
        echo ""
    fi
fi

# 搜索每日记忆
if [ "$SEARCH_TYPE" = "memory" ] || [ "$SEARCH_TYPE" = "all" ]; then
    if [ -d "$MEMORY_DIR" ]; then
        echo -e "${GREEN}📅 每日记忆:${NC}"
        echo -e "─────────────────────────────────────"
        
        if [ -n "$DATE_FILTER" ]; then
            # 搜索指定日期
            DATE_FILE="$MEMORY_DIR/$DATE_FILTER.md"
            if [ -f "$DATE_FILE" ]; then
                RESULTS=$(grep -n -C "$CONTEXT_LINES" "$QUERY" "$DATE_FILE" 2>/dev/null || true)
                if [ -n "$RESULTS" ]; then
                    echo "文件：$DATE_FILTER.md"
                    echo "$RESULTS" | head -n "$LIMIT"
                    RESULT_COUNT=$((RESULT_COUNT + 1))
                else
                    echo "  未找到匹配内容"
                fi
            else
                echo "  文件不存在：$DATE_FILTER.md"
            fi
        else
            # 搜索所有日期
            RESULTS=$(grep -r -n -C "$CONTEXT_LINES" "$QUERY" "$MEMORY_DIR" 2>/dev/null | head -n "$LIMIT" || true)
            if [ -n "$RESULTS" ]; then
                echo "$RESULTS"
                RESULT_COUNT=$((RESULT_COUNT + $(echo "$RESULTS" | grep -c "^" || echo "1")))
            else
                echo "  未找到匹配内容"
            fi
        fi
        echo ""
    fi
fi

# 搜索学习日志
LEARNINGS_FILE="$WORKSPACE/.learnings/LEARNINGS.md"
if [ -f "$LEARNINGS_FILE" ] && [ "$SEARCH_TYPE" = "all" ]; then
    echo -e "${GREEN}📚 学习日志 (LEARNINGS.md):${NC}"
    echo -e "─────────────────────────────────────"
    
    RESULTS=$(grep -n -C "$CONTEXT_LINES" "$QUERY" "$LEARNINGS_FILE" 2>/dev/null || true)
    if [ -n "$RESULTS" ]; then
        echo "$RESULTS" | head -n "$LIMIT"
        RESULT_COUNT=$((RESULT_COUNT + 1))
    else
        echo "  未找到匹配内容"
    fi
    echo ""
fi

# 总结
echo -e "${BLUE}================================${NC}"
if [ $RESULT_COUNT -gt 0 ]; then
    echo -e "${GREEN}✅ 找到 $RESULT_COUNT 个匹配的文件${NC}"
else
    echo -e "${YELLOW}⚠️  未找到匹配内容${NC}"
fi
echo -e "${BLUE}================================${NC}"
