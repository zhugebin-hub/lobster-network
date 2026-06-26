#!/bin/bash
# 🦞 小龙虾网络 · 一键部署脚本
# 功能：防火墙配置 + 服务启动 + 健康检查 + 注册测试

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REGISTRY_DIR="$PROJECT_DIR/registry"
API_SCRIPT="$SCRIPT_DIR/lobster_join_api.py"
SYNC_SCRIPT="$SCRIPT_DIR/registry_sync.py"
LOG_DIR="/tmp/lobster-network"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "未找到 python3，请先安装 Python 3.6+"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        log_error "未找到 curl，请先安装 curl"
        exit 1
    fi
    
    # 检查 requests 库
    if ! python3 -c "import requests" &> /dev/null; then
        log_warn "未找到 requests 库，正在安装..."
        pip3 install requests
    fi
    
    log_success "依赖检查完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    if command -v firewall-cmd &> /dev/null; then
        if [ "$EUID" -eq 0 ]; then
            firewall-cmd --permanent --add-port=8001/tcp 2>/dev/null || true
            firewall-cmd --permanent --add-port=8002/tcp 2>/dev/null || true
            firewall-cmd --reload 2>/dev/null || true
            log_success "防火墙已开放 8001/8002 端口"
        else
            log_warn "需要 root 权限配置防火墙，请手动执行:"
            log_info "sudo firewall-cmd --permanent --add-port=8001/tcp"
            log_info "sudo firewall-cmd --permanent --add-port=8002/tcp"
            log_info "sudo firewall-cmd --reload"
        fi
    else
        log_warn "未找到 firewall-cmd，跳过防火墙配置"
    fi
}

# 创建日志目录
create_log_dir() {
    mkdir -p "$LOG_DIR"
    log_success "日志目录已创建: $LOG_DIR"
}

# 启动动态注册服务
start_registry_service() {
    local port=$1
    local role=$2
    local peer=$3
    
    log_info "启动动态注册服务 (端口: $port, 角色: $role)..."
    
    # 检查是否已运行
    local pid=$(pgrep -f "lobster_join_api.py.*--port=$port" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        log_warn "服务已在运行 (PID: $pid)，先停止..."
        kill $pid 2>/dev/null || true
        sleep 2
    fi
    
    # 启动服务
    local cmd="python3 $API_SCRIPT --port=$port --role=$role"
    if [ -n "$peer" ]; then
        cmd="$cmd --peer=$peer"
    fi
    
    nohup $cmd > "$LOG_DIR/registry-$port.log" 2>&1 &
    local new_pid=$!
    echo $new_pid > "$LOG_DIR/registry-$port.pid"
    
    sleep 3
    
    # 验证启动
    if ps -p $new_pid > /dev/null 2>&1; then
        log_success "服务启动成功 (PID: $new_pid)"
    else
        log_error "服务启动失败，请查看日志: $LOG_DIR/registry-$port.log"
        return 1
    fi
}

# 启动主备同步
start_sync_service() {
    local peer=$1
    local interval=${2:-300}
    
    log_info "启动主备同步服务..."
    
    # 检查是否已运行
    local pid=$(pgrep -f "registry_sync.py" 2>/dev/null || true)
    if [ -n "$pid" ]; then
        log_warn "同步服务已在运行 (PID: $pid)，先停止..."
        kill $pid 2>/dev/null || true
        sleep 2
    fi
    
    # 启动服务
    nohup python3 $SYNC_SCRIPT --peer=$peer --interval=$interval > "$LOG_DIR/sync.log" 2>&1 &
    local new_pid=$!
    echo $new_pid > "$LOG_DIR/sync.pid"
    
    sleep 3
    
    # 验证启动
    if ps -p $new_pid > /dev/null 2>&1; then
        log_success "同步服务启动成功 (PID: $new_pid)"
    else
        log_error "同步服务启动失败，请查看日志: $LOG_DIR/sync.log"
        return 1
    fi
}

# 健康检查
health_check() {
    local port=$1
    local host=${2:-"127.0.0.1"}
    
    log_info "健康检查 (http://$host:$port/api/v1/health)..."
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "http://$host:$port/api/v1/health" 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        log_success "健康检查通过"
        return 0
    else
        log_error "健康检查失败 (HTTP $response)"
        return 1
    fi
}

# 注册测试
test_registration() {
    local port=$1
    local host=${2:-"127.0.0.1"}
    
    log_info "测试注册功能 (http://$host:$port/api/v1/register)..."
    
    local response=$(curl -s -X POST "http://$host:$port/api/v1/register" \
        -H "Content-Type: application/json" \
        -d '{"node_id":"test-node-'"$(date +%s)"'","name":"测试节点","type":"agent","capabilities":["test"]}' 2>/dev/null)
    
    if echo "$response" | grep -q "注册成功\|节点已更新"; then
        log_success "注册测试通过"
        return 0
    else
        log_error "注册测试失败: $response"
        return 1
    fi
}

# 显示状态
show_status() {
    log_info "服务状态:"
    echo "----------------------------------------"
    
    # 检查注册服务
    for port in 8001 8002; do
        local pid=$(cat "$LOG_DIR/registry-$port.pid" 2>/dev/null || true)
        if [ -n "$pid" ] && ps -p $pid > /dev/null 2>&1; then
            echo -e "  🟢 注册服务 (端口 $port): 运行中 (PID: $pid)"
        else
            echo -e "  🔴 注册服务 (端口 $port): 未运行"
        fi
    done
    
    # 检查同步服务
    local sync_pid=$(cat "$LOG_DIR/sync.pid" 2>/dev/null || true)
    if [ -n "$sync_pid" ] && ps -p $sync_pid > /dev/null 2>&1; then
        echo -e "  🟢 同步服务: 运行中 (PID: $sync_pid)"
    else
        echo -e "  🔴 同步服务: 未运行"
    fi
    
    echo "----------------------------------------"
    echo "  📁 日志目录: $LOG_DIR"
    echo "  📄 注册表: $REGISTRY_DIR/nodes.json"
    echo "----------------------------------------"
}

# 主函数
main() {
    echo "🦞 小龙虾网络 · 一键部署脚本"
    echo "================================"
    
    # 解析参数
    local role="primary"
    local port=8001
    local peer=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --role)
                role="$2"
                shift 2
                ;;
            --port)
                port="$2"
                shift 2
                ;;
            --peer)
                peer="$2"
                shift 2
                ;;
            --help)
                echo "用法: $0 [--role primary|backup] [--port PORT] [--peer URL]"
                echo "示例:"
                echo "  $0 --role primary --port 8001"
                echo "  $0 --role backup --port 8002 --peer http://47.93.6.57:8001"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行部署
    check_dependencies
    setup_firewall
    create_log_dir
    
    # 启动服务
    start_registry_service $port $role "$peer"
    
    if [ -n "$peer" ]; then
        start_sync_service "$peer" 300
    fi
    
    # 健康检查
    sleep 2
    health_check $port
    test_registration $port
    
    # 显示状态
    echo ""
    show_status
    
    echo ""
    log_success "部署完成！"
    echo ""
    echo "📋 常用命令:"
    echo "  查看日志: tail -f $LOG_DIR/registry-$port.log"
    echo "  查看状态: curl http://127.0.0.1:$port/api/v1/nodes"
    echo "  健康检查: curl http://127.0.0.1:$port/api/v1/health"
    echo "  停止服务: kill \$(cat $LOG_DIR/registry-$port.pid)"
    echo ""
}

main "$@"
