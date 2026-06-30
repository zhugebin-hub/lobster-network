#!/bin/bash
# OpenClaw 记忆管理工具
# 支持状态查看、去重、归档、清理等功能

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
MEMORY_DIR="$WORKSPACE/memory"
LEARNINGS_DIR="$WORKSPACE/.learnings"
ARCHIVE_DIR="$WORKSPACE/memory-archive"

# 显示帮助
show_help() {
    cat << EOF
📊 OpenClaw 记忆管理工具

用法：$0 <命令> [选项]

命令:
  status              查看记忆状态统计
  dedup               执行去重操作（检查重复内容）
  archive             归档旧记忆（>30 天）
  clean               清理临时文件和缓存
  recent              显示最近的记忆文件
  search <关键词>     快速搜索记忆

选项:
  -h, --help          显示帮助信息
  -n, --dry-run       空运行（不实际执行）

示例:
  $0 status                      # 查看记忆状态
  $0 dedup -n                    # 去重检查（不实际执行）
  $0 archive                     # 归档旧记忆
  $0 search "Hermes"             # 搜索记忆

EOF
}

# 查看记忆状态
show_status() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}📊 OpenClaw 记忆状态${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    # 长期记忆
    MEMORY_FILE="$WORKSPACE/MEMORY.md"
    if [ -f "$MEMORY_FILE" ]; then
        LINES=$(wc -l < "$MEMORY_FILE")
        SIZE=$(du -h "$MEMORY_FILE" | cut -f1)
        echo -e "${CYAN}📄 长期记忆 (MEMORY.md):${NC}"
        echo "  行数：$LINES"
        echo "  大小：$SIZE"
        echo "  路径：$MEMORY_FILE"
    else
        echo -e "${YELLOW}⚠️  长期记忆文件不存在${NC}"
    fi
    echo ""
    
    # 每日记忆
    if [ -d "$MEMORY_DIR" ]; then
        FILE_COUNT=$(ls "$MEMORY_DIR"/*.md 2>/dev/null | wc -l)
        TOTAL_SIZE=$(du -sh "$MEMORY_DIR" 2>/dev/null | cut -f1)
        LATEST=$(ls -t "$MEMORY_DIR"/*.md 2>/dev/null | head -1)
        
        echo -e "${CYAN}📅 每日记忆:${NC}"
        echo "  文件数量：$FILE_COUNT"
        echo "  总大小：$TOTAL_SIZE"
        echo "  最新文件：${LATEST:-无}"
        echo "  路径：$MEMORY_DIR"
    else
        echo -e "${YELLOW}⚠️  每日记忆目录不存在${NC}"
    fi
    echo ""
    
    # 学习日志
    LEARNINGS_FILE="$LEARNINGS_DIR/LEARNINGS.md"
    if [ -f "$LEARNINGS_FILE" ]; then
        LINES=$(wc -l < "$LEARNINGS_FILE")
        SIZE=$(du -h "$LEARNINGS_FILE" | cut -f1)
        echo -e "${CYAN}📚 学习日志 (LEARNINGS.md):${NC}"
        echo "  行数：$LINES"
        echo "  大小：$SIZE"
    else
        echo -e "${YELLOW}⚠️  学习日志文件不存在${NC}"
    fi
    echo ""
    
    # 待处理学习
    if [ -f "$LEARNINGS_FILE" ]; then
        PENDING=$(grep -c "Status\*\*: pending" "$LEARNINGS_FILE" 2>/dev/null || echo "0")
        RESOLVED=$(grep -c "Status\*\*: resolved" "$LEARNINGS_FILE" 2>/dev/null || echo "0")
        echo -e "${CYAN}📋 学习状态统计:${NC}"
        echo "  待处理：$PENDING"
        echo "  已解决：$RESOLVED"
    fi
    echo ""
    
    # 工作区总大小
    TOTAL_SIZE=$(du -sh "$WORKSPACE" 2>/dev/null | cut -f1)
    echo -e "${CYAN}💾 工作区总大小:${NC}"
    echo "  $TOTAL_SIZE ($WORKSPACE)"
    echo ""
    
    echo -e "${BLUE}================================${NC}"
}

# 显示最近的记忆文件
show_recent() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}📅 最近的记忆文件${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    if [ -d "$MEMORY_DIR" ]; then
        echo -e "${CYAN}每日记忆 (最新 10 个):${NC}"
        ls -lht "$MEMORY_DIR"/*.md 2>/dev/null | head -10
    else
        echo "  每日记忆目录不存在"
    fi
    echo ""
}

# 去重检查
dedup_check() {
    DRY_RUN="$1"
    
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🔄 记忆去重检查${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}🔍 空运行模式（不会实际修改文件）${NC}"
        echo ""
    fi
    
    # 检查重复行
    echo -e "${CYAN}检查重复内容...${NC}"
    
    if [ -d "$MEMORY_DIR" ]; then
        DUPLICATES=$(cat "$MEMORY_DIR"/*.md 2>/dev/null | sort | uniq -d | wc -l)
        echo "  发现重复行：$DUPLICATES"
        
        if [ "$DUPLICATES" -gt 0 ] && [ "$DRY_RUN" != "true" ]; then
            echo -e "${YELLOW}⚠️  建议手动检查和清理重复内容${NC}"
        fi
    fi
    
    echo ""
    echo -e "${GREEN}✅ 去重检查完成${NC}"
}

# 归档旧记忆
archive_old() {
    DRY_RUN="$1"
    DAYS_OLD=${2:-30}
    
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}📦 归档旧记忆${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}🔍 空运行模式（不会实际移动文件）${NC}"
        echo ""
    fi
    
    # 创建归档目录
    if [ ! -d "$ARCHIVE_DIR" ]; then
        if [ "$DRY_RUN" != "true" ]; then
            mkdir -p "$ARCHIVE_DIR"
            echo -e "${GREEN}✅ 创建归档目录：$ARCHIVE_DIR${NC}"
        else
            echo "  将创建归档目录：$ARCHIVE_DIR"
        fi
    fi
    
    # 查找旧文件
    if [ -d "$MEMORY_DIR" ]; then
        echo -e "${CYAN}查找 ${DAYS_OLD} 天前的记忆文件...${NC}"
        
        OLD_FILES=$(find "$MEMORY_DIR" -name "*.md" -type f -mtime +$DAYS_OLD 2>/dev/null | wc -l)
        echo "  发现旧文件：$OLD_FILES 个"
        
        if [ "$OLD_FILES" -gt 0 ]; then
            echo ""
            echo -e "${YELLOW}即将归档的文件:${NC}"
            find "$MEMORY_DIR" -name "*.md" -type f -mtime +$DAYS_OLD 2>/dev/null | head -10
            
            if [ "$DRY_RUN" != "true" ]; then
                echo ""
                echo -e "${YELLOW}⚠️  实际归档功能待实现${NC}"
                echo "  建议：手动移动文件到 $ARCHIVE_DIR"
            fi
        else
            echo -e "${GREEN}✅ 没有需要归档的文件${NC}"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}================================${NC}"
}

# 清理临时文件
clean_temp() {
    DRY_RUN="$1"
    
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🧹 清理临时文件${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}🔍 空运行模式（不会实际删除文件）${NC}"
        echo ""
    fi
    
    # 查找临时文件
    TEMP_PATTERNS=(
        "*.tmp"
        "*.bak"
        "*.swp"
        "*~"
    )
    
    TOTAL_CLEANED=0
    
    for pattern in "${TEMP_PATTERNS[@]}"; do
        COUNT=$(find "$WORKSPACE" -name "$pattern" -type f 2>/dev/null | wc -l)
        if [ "$COUNT" -gt 0 ]; then
            echo "  发现 $pattern: $COUNT 个"
            TOTAL_CLEANED=$((TOTAL_CLEANED + COUNT))
            
            if [ "$DRY_RUN" != "true" ]; then
                find "$WORKSPACE" -name "$pattern" -type f -delete 2>/dev/null || true
            fi
        fi
    done
    
    echo ""
    if [ "$TOTAL_CLEANED" -gt 0 ]; then
        if [ "$DRY_RUN" = "true" ]; then
            echo -e "${YELLOW}⚠️  将清理 $TOTAL_CLEANED 个临时文件${NC}"
        else
            echo -e "${GREEN}✅ 已清理 $TOTAL_CLEANED 个临时文件${NC}"
        fi
    else
        echo -e "${GREEN}✅ 没有需要清理的临时文件${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}================================${NC}"
}

# 主程序
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    COMMAND="$1"
    shift
    
    DRY_RUN="false"
    
    # 检查空运行选项
    for arg in "$@"; do
        if [ "$arg" = "-n" ] || [ "$arg" = "--dry-run" ]; then
            DRY_RUN="true"
        fi
    done
    
    case $COMMAND in
        status)
            show_status
            ;;
        recent)
            show_recent
            ;;
        dedup)
            dedup_check "$DRY_RUN"
            ;;
        archive)
            archive_old "$DRY_RUN"
            ;;
        clean)
            clean_temp "$DRY_RUN"
            ;;
        search)
            if [ -n "$2" ]; then
                "$WORKSPACE/scripts/search-memory.sh" "$2"
            else
                echo -e "${RED}❌ 错误：请提供搜索关键词${NC}"
                exit 1
            fi
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}❌ 未知命令：$COMMAND${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
