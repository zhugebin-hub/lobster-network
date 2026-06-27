#!/bin/bash
# ============================================================
# 小龙虾网络V3.0 - 学员自动化提交脚本
# 功能: 自动拉取任务、提交结果、同步进度
# 用法: bash setup_submission.sh <student_id> [mode]
# 模式: github (默认) | ssh | ws
# ============================================================

set -e

# 配置
STUDENT_ID="${1:-}"
MODE="${2:-github}"
REPO_URL="https://github.com/zhugebin-hub/lobster-network.git"
LOCAL_DIR="$HOME/lobster-network"
RESULTS_DIR="$LOCAL_DIR/docs/training/results"
LOG_FILE="$HOME/.lobster_submission.log"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE" >&2
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查参数
if [ -z "$STUDENT_ID" ]; then
    echo "用法: bash setup_submission.sh <student_id> [mode]"
    echo "模式: github (默认) | ssh | ws"
    echo "示例: bash setup_submission.sh qoder github"
    exit 1
fi

log "🦞 小龙虾网络V3.0 - 学员提交脚本"
log "学员ID: $STUDENT_ID"
log "提交模式: $MODE"

# ============================================================
# 模式1: GitHub 同步
# ============================================================
setup_github() {
    log "📦 配置 GitHub 同步模式..."
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        error "git 未安装，请先安装 git"
        exit 1
    fi
    
    # 克隆或更新仓库
    if [ ! -d "$LOCAL_DIR/.git" ]; then
        log "📥 克隆仓库..."
        git clone "$REPO_URL" "$LOCAL_DIR"
    else
        log "🔄 更新仓库..."
        cd "$LOCAL_DIR"
        git pull origin main
    fi
    
    # 配置 git 用户
    cd "$LOCAL_DIR"
    git config user.name "$STUDENT_ID"
    git config user.email "${STUDENT_ID}@lobster-network.ai"
    
    # 创建结果目录
    mkdir -p "$RESULTS_DIR"
    
    # 配置 PAT (如果需要)
    if [ -n "$GITHUB_PAT" ]; then
        log "🔑 配置 GitHub PAT..."
        git remote set-url origin "https://${GITHUB_PAT}@github.com/zhugebin-hub/lobster-network.git"
    fi
    
    log "✅ GitHub 同步配置完成"
}

# ============================================================
# 模式2: SSH 推送
# ============================================================
setup_ssh() {
    log "🔐 配置 SSH 推送模式..."
    
    # 检查 SSH
    if ! command -v ssh &> /dev/null; then
        error "ssh 未安装"
        exit 1
    fi
    
    # 生成 SSH 密钥 (如果不存在)
    if [ ! -f "$HOME/.ssh/id_rsa" ]; then
        log "🔑 生成 SSH 密钥..."
        ssh-keygen -t rsa -b 4096 -f "$HOME/.ssh/id_rsa" -N "" -q
        log "📋 请将公钥添加到教练服务器:"
        cat "$HOME/.ssh/id_rsa.pub"
    fi
    
    # 测试连接
    log "🔗 测试 SSH 连接..."
    ssh -o ConnectTimeout=5 -o BatchMode=yes admin@47.93.6.57 "echo 'SSH连接成功'" || {
        warn "SSH 连接失败，请检查密钥配置"
    }
    
    # 创建提交脚本
    cat > "$HOME/submit_results.sh" << 'EOF'
#!/bin/bash
# 自动提交结果到教练服务器
RESULTS_DIR="$HOME/lobster-network/docs/training/results"
STUDENT_ID="${1:-}"
DATE=$(date '+%Y%m%d')

if [ -z "$STUDENT_ID" ]; then
    echo "用法: bash submit_results.sh <student_id>"
    exit 1
fi

# 打包结果
cd "$RESULTS_DIR"
tar czf "/tmp/results_${STUDENT_ID}_${DATE}.tar.gz" "${STUDENT_ID}_"* 2>/dev/null || {
    echo "没有找到结果文件"
    exit 1
}

# 上传到教练服务器
scp "/tmp/results_${STUDENT_ID}_${DATE}.tar.gz" admin@47.93.6.57:/home/admin/go-training/shared/results/

# 清理
rm -f "/tmp/results_${STUDENT_ID}_${DATE}.tar.gz"

echo "✅ 结果已提交: ${STUDENT_ID}_${DATE}"
EOF
    
    chmod +x "$HOME/submit_results.sh"
    
    log "✅ SSH 推送配置完成"
    log "📝 使用方法: bash ~/submit_results.sh $STUDENT_ID"
}

# ============================================================
# 模式3: WebSocket 实时提交
# ============================================================
setup_ws() {
    log "📡 配置 WebSocket 实时模式..."
    
    # 检查 Python
    if ! command -p python3 &> /dev/null; then
        error "python3 未安装"
        exit 1
    fi
    
    # 安装依赖
    pip3 install websocket-client requests -q
    
    # 创建 WebSocket 提交脚本
    cat > "$HOME/ws_submit.py" << 'EOF'
#!/usr/bin/env python3
"""WebSocket 实时提交脚本"""

import json
import time
import websocket
import sys
import os

WS_URL = "ws://47.93.6.57:8199"
STUDENT_ID = sys.argv[1] if len(sys.argv) > 1 else "unknown"

def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "task":
        print(f"📥 收到任务: {data.get('title')}")
        # 执行训练...
        # 提交结果...

def on_error(ws, error):
    print(f"❌ 连接错误: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"🔌 连接关闭: {close_status_code}")

def on_open(ws):
    print(f"✅ 已连接到教练服务器")
    # 发送学员信息
    ws.send(json.dumps({
        "type": "register",
        "student_id": STUDENT_ID,
        "timestamp": time.time()
    }))

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
EOF
    
    chmod +x "$HOME/ws_submit.py"
    
    log "✅ WebSocket 实时模式配置完成"
    log "📝 使用方法: python3 ~/ws_submit.py $STUDENT_ID"
}

# ============================================================
# 创建训练提交模板
# ============================================================
create_template() {
    log "📄 创建训练提交模板..."
    
    mkdir -p "$RESULTS_DIR"
    
    cat > "$RESULTS_DIR/${STUDENT_ID}_day3_template.json" << EOF
{
    "student_id": "$STUDENT_ID",
    "day": 3,
    "date": "$(date '+%Y-%m-%d')",
    "problems": [
        {
            "id": "problem-001",
            "title": "题目名称",
            "difficulty": "初级/中级/高级",
            "is_correct": true,
            "thinking_time": 30,
            "reflection": "解题思路"
        }
    ],
    "games": [
        {
            "id": "game-001",
            "opponent": "对手名称",
            "color": "black/white",
            "is_win": true,
            "moves": 120
        }
    ],
    "reflection": "今日训练总结",
    "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
    
    log "✅ 模板已创建: $RESULTS_DIR/${STUDENT_ID}_day3_template.json"
}

# ============================================================
# 创建定时同步任务
# ============================================================
setup_cron() {
    log "⏰ 配置定时同步任务..."
    
    CRON_CMD="*/30 * * * * cd $LOCAL_DIR && git pull origin main && git add -A && git commit -m 'auto: 训练进度更新' && git push origin main"
    
    # 检查是否已存在
    if crontab -l 2>/dev/null | grep -q "lobster-network"; then
        warn "定时任务已存在，跳过"
    else
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        log "✅ 定时任务已添加 (每30分钟同步)"
    fi
}

# ============================================================
# 主流程
# ============================================================
main() {
    case "$MODE" in
        github)
            setup_github
            create_template
            setup_cron
            ;;
        ssh)
            setup_ssh
            create_template
            ;;
        ws)
            setup_ws
            create_template
            ;;
        *)
            error "未知模式: $MODE"
            echo "支持的模式: github | ssh | ws"
            exit 1
            ;;
    esac
    
    log "🎉 配置完成！"
    log "📁 结果目录: $RESULTS_DIR"
    log "📝 日志文件: $LOG_FILE"
}

main
