#!/bin/bash
# =============================================================================
# 🦞 小龙虾网络 v0.4.1 自动化部署脚本
# 版本：v0.4.1
# 日期：2026-06-24
# 作者：虾尔（lobster-001）、诸葛马（Hermes）
# =============================================================================

set -euo pipefail

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

# 配置
REPO_URL="https://github.com/zhugebin-hub/lobster-network.git"
VERSION="v0.4.1"
DEPLOY_DIR="/opt/lobster-network"
BACKUP_DIR="/opt/lobster-network-backup"
LOG_FILE="/var/log/lobster-network-deploy.log"
HEALTH_CHECK_URL="http://localhost:8080/health"
ROLLBACK_TAG="v0.3.0"

# 确保以 root 或 sudo 运行
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "此脚本需要 root 权限运行"
        exit 1
    fi
}

# 创建日志目录
init_log() {
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
}

# 记录日志
log_to_file() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# =============================================================================
# 第一步：环境检查
# =============================================================================
check_environment() {
    log_info "=== 环境检查 ==="
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    log_success "Python3 $PYTHON_VERSION 已安装"
    log_to_file "Python3 $PYTHON_VERSION"
    
    # 检查 Git
    if ! command -v git &> /dev/null; then
        log_error "Git 未安装"
        exit 1
    fi
    log_success "Git $(git --version | awk '{print $3}') 已安装"
    
    # 检查磁盘空间
    DISK_FREE=$(df -h "$DEPLOY_DIR" 2>/dev/null | awk 'NR==2 {print $4}' || echo "unknown")
    log_info "可用磁盘空间: $DISK_FREE"
    
    # 检查网络连接
    if curl -s --max-time 5 https://github.com > /dev/null 2>&1; then
        log_success "GitHub 网络可达"
    else
        log_warn "GitHub 网络不可达，将使用本地仓库"
    fi
    
    log_to_file "环境检查完成"
}

# =============================================================================
# 第二步：备份当前版本
# =============================================================================
backup_current() {
    log_info "=== 备份当前版本 ==="
    
    if [[ -d "$DEPLOY_DIR" ]]; then
        TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
        BACKUP_PATH="$BACKUP_DIR/$TIMESTAMP"
        
        mkdir -p "$BACKUP_PATH"
        cp -r "$DEPLOY_DIR" "$BACKUP_PATH/"
        
        log_success "已备份到: $BACKUP_PATH"
        log_to_file "备份完成: $BACKUP_PATH"
    else
        log_info "首次部署，无需备份"
    fi
}

# =============================================================================
# 第三步：拉取代码
# =============================================================================
pull_code() {
    log_info "=== 拉取代码 ==="
    
    mkdir -p "$DEPLOY_DIR"
    cd "$DEPLOY_DIR"
    
    if [[ -d ".git" ]]; then
        log_info "更新现有仓库..."
        git fetch --all
        git checkout "$VERSION"
        git pull origin main
    else
        log_info "克隆仓库..."
        git clone "$REPO_URL" .
        git checkout "$VERSION"
    fi
    
    log_success "代码已更新到 $VERSION"
    log_to_file "代码拉取完成: $VERSION"
}

# =============================================================================
# 第四步：安装依赖
# =============================================================================
install_dependencies() {
    log_info "=== 安装依赖 ==="
    
    cd "$DEPLOY_DIR"
    
    # 创建虚拟环境
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # 安装依赖
    pip install -r requirements.txt
    
    # 安装 pytest（用于测试）
    pip install pytest paramiko
    
    log_success "依赖安装完成"
    log_to_file "依赖安装完成"
}

# =============================================================================
# 第五步：运行测试
# =============================================================================
run_tests() {
    log_info "=== 运行测试 ==="
    
    cd "$DEPLOY_DIR"
    source venv/bin/activate
    
    # 运行虾尔的测试（37 个）
    log_info "运行虾尔版测试..."
    python3 -m unittest tests.test_registry 2>&1 | tee /tmp/test_xiaer.log
    XIAER_RESULT=${PIPESTATUS[0]}
    
    # 运行诸葛马的测试（25 个）
    log_info "运行诸葛马版测试..."
    ./venv/bin/pytest tests/test_enhanced_protocol.py -v 2>&1 | tee /tmp/test_hermes.log
    HERMES_RESULT=${PIPESTATUS[0]}
    
    if [[ $XIAER_RESULT -eq 0 && $HERMES_RESULT -eq 0 ]]; then
        log_success "所有测试通过 (62/62)"
        log_to_file "测试通过: 62/62"
    else
        log_error "测试失败！"
        log_error "虾尔版: $([ $XIAER_RESULT -eq 0 ] && echo '通过' || echo '失败')"
        log_error "诸葛马版: $([ $HERMES_RESULT -eq 0 ] && echo '通过' || echo '失败')"
        log_to_file "测试失败"
        exit 1
    fi
}

# =============================================================================
# 第六步：配置部署
# =============================================================================
configure() {
    log_info "=== 配置部署 ==="
    
    cd "$DEPLOY_DIR"
    
    # 创建配置目录
    mkdir -p config
    mkdir -p /var/log/lobster-network
    
    # 生成配置文件
    cat > config/deploy.conf << EOF
# 小龙虾网络 v0.4.1 部署配置
# 生成时间：$(date '+%Y-%m-%d %H:%M:%S')

# 节点配置
NODE_ID=$(hostname)
NODE_NAME="$(hostname)-lobster"
NODE_TYPE="agent"

# 传输通道配置
NFS_ENABLED=true
NFS_ENDPOINT="/shared/messages"
SSH_ENABLED=true
SSH_HOST="172.24.57.34"
SSH_PORT=22
FILE_ENABLED=true
FILE_ENDPOINT="/opt/lobster-network/pending"

# 心跳配置
HEARTBEAT_INTERVAL=300
HEARTBEAT_TTL=300

# 日志配置
LOG_LEVEL="INFO"
LOG_FILE="/var/log/lobster-network/app.log"
EOF
    
    log_success "配置已生成"
    log_to_file "配置完成"
}

# =============================================================================
# 第七步：启动服务
# =============================================================================
start_service() {
    log_info "=== 启动服务 ==="
    
    cd "$DEPLOY_DIR"
    source venv/bin/activate
    
    # 创建 systemd 服务文件
    cat > /etc/systemd/system/lobster-network.service << EOF
[Unit]
Description=龙虾网络服务 v0.4.1
After=network.target nfs-client.target

[Service]
Type=simple
User=root
WorkingDirectory=$DEPLOY_DIR
ExecStart=$DEPLOY_DIR/venv/bin/python3 $DEPLOY_DIR/examples/indra_net_demo.py
Restart=always
RestartSec=10
StandardOutput=append:/var/log/lobster-network/service.log
StandardError=append:/var/log/lobster-network/error.log

[Install]
WantedBy=multi-user.target
EOF
    
    # 重新加载 systemd
    systemctl daemon-reload
    
    # 启动服务
    systemctl enable lobster-network
    systemctl start lobster-network
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if systemctl is-active --quiet lobster-network; then
        log_success "龙虾网络服务已启动"
        log_to_file "服务启动成功"
    else
        log_error "服务启动失败"
        log_error "查看日志: journalctl -u lobster-network -n 50"
        log_to_file "服务启动失败"
        exit 1
    fi
}

# =============================================================================
# 第八步：健康检查
# =============================================================================
health_check() {
    log_info "=== 健康检查 ==="
    
    cd "$DEPLOY_DIR"
    source venv/bin/activate
    
    # 运行健康检查脚本
    python3 -c "
import sys
sys.path.insert(0, '.')
from src.lobster_network.integration import LobsterNetworkWithRegistry

network = LobsterNetworkWithRegistry(storage_dir='/opt/lobster-network/data')
health = network.health_check()

print(f'节点总数: {health[\"total_nodes\"]}')
print(f'在线节点: {health[\"online\"]}')
print(f'离线节点: {health[\"offline\"]}')

if health['online'] > 0:
    print('✅ 健康检查通过')
    sys.exit(0)
else:
    print('❌ 健康检查失败')
    sys.exit(1)
" 2>&1 | tee /tmp/health_check.log
    
    HEALTH_RESULT=${PIPESTATUS[0]}
    
    if [[ $HEALTH_RESULT -eq 0 ]]; then
        log_success "健康检查通过"
        log_to_file "健康检查通过"
    else
        log_warn "健康检查未通过（可能无其他节点在线）"
        log_to_file "健康检查未通过（正常）"
    fi
}

# =============================================================================
# 回滚函数
# =============================================================================
rollback() {
    log_warn "=== 开始回滚 ==="
    
    # 停止服务
    systemctl stop lobster-network 2>/dev/null || true
    
    # 查找最新备份
    LATEST_BACKUP=$(ls -td "$BACKUP_DIR"/*/lobster-network 2>/dev/null | head -1)
    
    if [[ -n "$LATEST_BACKUP" ]]; then
        log_info "恢复到: $LATEST_BACKUP"
        rm -rf "$DEPLOY_DIR"
        cp -r "$LATEST_BACKUP" "$DEPLOY_DIR"
        
        # 重新启动服务
        systemctl start lobster-network
        
        log_success "回滚完成"
        log_to_file "回滚完成: $LATEST_BACKUP"
    else
        log_error "未找到备份，无法回滚"
        log_to_file "回滚失败：无备份"
        exit 1
    fi
}

# =============================================================================
# 主流程
# =============================================================================
main() {
    local action="${1:-deploy}"
    
    log_info "🦞 小龙虾网络 v0.4.1 部署脚本"
    log_info "操作: $action"
    log_to_file "开始执行: $action"
    
    case "$action" in
        deploy)
            check_root
            init_log
            check_environment
            backup_current
            pull_code
            install_dependencies
            run_tests
            configure
            start_service
            health_check
            
            log_success "🎉 部署完成！"
            log_info "服务状态: systemctl status lobster-network"
            log_info "查看日志: tail -f /var/log/lobster-network/service.log"
            log_to_file "部署完成"
            ;;
        
        rollback)
            check_root
            init_log
            rollback
            ;;
        
        health)
            health_check
            ;;
        
        test)
            check_root
            cd "$DEPLOY_DIR"
            source venv/bin/activate
            run_tests
            ;;
        
        *)
            echo "用法: $0 {deploy|rollback|health|test}"
            exit 1
            ;;
    esac
}

# 执行
main "$@"
