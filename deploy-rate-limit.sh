#!/bin/bash
#===============================================================================
# OpenClaw API 限流与重试一键部署脚本
# 功能：通过 Nginx 反向代理实现 DashScope API 限流、排队、自动重试
# 作者：小龙虾-诸葛虾 🦞
# 日期：2026-05-17
#===============================================================================

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info()  { echo -e "${BLUE}[INFO]${NC} $1"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 配置变量
NGINX_PROXY_PORT=18080
DASHSCOPE_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
LOCAL_PROXY_URL="http://127.0.0.1:${NGINX_PROXY_PORT}/compatible-mode/v1"
RATE_LIMIT="25r/m"
BURST_SIZE=3
OPENCLAW_CONFIG="/home/admin/.openclaw/openclaw.json"
NGINX_CONF="/etc/nginx/conf.d/dashscope-proxy.conf"

echo ""
echo "=============================================="
echo "  OpenClaw API 限流与重试部署脚本"
echo "  作者：小龙虾-诸葛虾 🦞"
echo "  日期：2026-05-17"
echo "=============================================="
echo ""

# 检查 root 权限
if [ "$EUID" -ne 0 ]; then
    log_warn "当前非 root 用户，部分操作可能需要 sudo 权限"
    SUDO="sudo"
else
    SUDO=""
fi

# 步骤 1：检查 Nginx 是否安装
log_info "步骤 1/6：检查 Nginx 安装状态..."
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1 | cut -d'/' -f2)
    log_ok "Nginx 已安装 (版本: $NGINX_VERSION)"
else
    log_warn "Nginx 未安装，开始安装..."
    if [ -f /etc/redhat-release ]; then
        $SUDO yum install -y nginx
    elif [ -f /etc/debian_version ]; then
        $SUDO apt update && $SUDO apt install -y nginx
    else
        log_error "不支持的操作系统，请手动安装 Nginx"
        exit 1
    fi
    log_ok "Nginx 安装完成"
fi

# 步骤 2：创建 Nginx 代理配置
log_info "步骤 2/6：创建 Nginx 代理配置..."
cat > /tmp/dashscope-proxy.conf << EOF
# 全局限流区：每分钟 ${RATE_LIMIT} 请求
# 使用 \$server_name 作为 key，因为请求全来自 127.0.0.1
limit_req_zone \$server_name zone=dashscope_limit:10m rate=${RATE_LIMIT};

server {
    listen ${NGINX_PROXY_PORT};
    server_name localhost;

    location /compatible-mode/v1/ {
        # 限流策略：允许突发 ${BURST_SIZE} 个请求，超出则返回 429
        limit_req zone=dashscope_limit burst=${BURST_SIZE} nodelay;
        limit_req_status 429;
        limit_req_log_level warn;

        # 代理到真实 DashScope 地址
        proxy_pass ${DASHSCOPE_BASE_URL}/;
        
        # 透传关键 Header
        proxy_set_header Host dashscope.aliyuncs.com;
        proxy_set_header Authorization \$http_authorization;
        proxy_set_header Content-Type application/json;
        proxy_set_header User-Agent "OpenClaw-Proxy/1.0";

        # 超时设置（大模型生成耗时较长）
        proxy_connect_timeout 10s;
        proxy_read_timeout 180s;
        proxy_send_timeout 180s;

        # 自动重试机制（仅针对 5xx 和超时，避免 429 死循环）
        proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
        proxy_next_upstream_tries 2;
        proxy_next_upstream_timeout 30s;

        # SSL 代理支持
        proxy_ssl_server_name on;
        proxy_ssl_protocols TLSv1.2 TLSv1.3;
        proxy_ssl_verify off;
    }

    # 健康检查端点
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }
}
EOF

$SUDO cp /tmp/dashscope-proxy.conf "$NGINX_CONF"
$SUDO rm -f /tmp/dashscope-proxy.conf
log_ok "Nginx 配置已创建: $NGINX_CONF"

# 步骤 3：测试并重载 Nginx
log_info "步骤 3/6：测试 Nginx 配置并重启..."
if $SUDO nginx -t 2>&1; then
    log_ok "Nginx 配置测试通过"
    $SUDO systemctl restart nginx
    $SUDO systemctl enable nginx
    log_ok "Nginx 已启动并设置为开机自启"
else
    log_error "Nginx 配置测试失败，请检查配置"
    exit 1
fi

# 步骤 4：修改 OpenClaw 配置指向本地代理
log_info "步骤 4/6：修改 OpenClaw 配置..."

# 备份原配置
BACKUP_FILE="${OPENCLAW_CONFIG}.bak.$(date +%Y%m%d_%H%M%S)"
cp "$OPENCLAW_CONFIG" "$BACKUP_FILE"
log_ok "原配置已备份: $BACKUP_FILE"

# 使用 Python 修改 JSON 配置
python3 << PYEOF
import json
import sys

config_path = "$OPENCLAW_CONFIG"

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # 修改 bailian provider 的 baseUrl
    if 'models' in config and 'providers' in config['models'] and 'bailian' in config['models']['providers']:
        old_url = config['models']['providers']['bailian'].get('baseUrl', 'N/A')
        config['models']['providers']['bailian']['baseUrl'] = "$LOCAL_PROXY_URL"
        print(f"  baseUrl: {old_url} -> $LOCAL_PROXY_URL")
    else:
        print("  ⚠️  未找到 bailian provider 配置")
    
    # 优化模型 maxTokens（避免单次请求过大）
    models_adjusted = 0
    if 'models' in config and 'providers' in config['models'] and 'bailian' in config['models']['providers']:
        for model in config['models']['providers']['bailian']['models']:
            if 'maxTokens' in model and model['maxTokens'] > 32768:
                old_tokens = model['maxTokens']
                model['maxTokens'] = 32768
                print(f"  {model['id']}: maxTokens {old_tokens} -> 32768")
                models_adjusted += 1
    
    if models_adjusted > 0:
        print(f"  已调整 {models_adjusted} 个模型的 maxTokens")
    
    # 保存配置
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("  ✅ OpenClaw 配置已保存")

except Exception as e:
    print(f"  ❌ 配置修改失败: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

# 步骤 5：设置环境变量
log_info "步骤 5/6：配置环境变量..."

ENV_FILE="/home/admin/.openclaw/.env"
cat > "$ENV_FILE" << EOF
# OpenClaw 限流与重试环境变量
# 生成时间：$(date '+%Y-%m-%d %H:%M:%S')

# 网关超时设置（秒）
export OPENCLAW_GATEWAY_TIMEOUT=120

# 内部消息队列大小（防止并发打满）
export OPENCLAW_QUEUE_SIZE=10

# 日志级别（降低 I/O 压力）
export OPENCLAW_LOG_LEVEL=warn

# DashScope 重试配置（部分插件支持）
export OPENCLAW_DASHSCOPE_RETRY_COUNT=2
export OPENCLAW_DASHSCOPE_RETRY_DELAY=1000

# 代理地址（供参考）
export DASHSCOPE_PROXY_URL="$LOCAL_PROXY_URL"
EOF

# 添加到 bashrc
if ! grep -q "OPENCLAW_GATEWAY_TIMEOUT" /home/admin/.bashrc 2>/dev/null; then
    echo "" >> /home/admin/.bashrc
    echo "# OpenClaw 环境变量" >> /home/admin/.bashrc
    echo "source /home/admin/.openclaw/.env" >> /home/admin/.bashrc
    log_ok "环境变量已添加到 .bashrc"
fi

# 立即生效
source "$ENV_FILE"
log_ok "环境变量已加载"

# 步骤 6：重启 OpenClaw
log_info "步骤 6/6：重启 OpenClaw Gateway..."
if openclaw gateway restart 2>&1; then
    sleep 3
    if openclaw gateway status 2>&1 | grep -q "running"; then
        log_ok "OpenClaw Gateway 重启成功"
    else
        log_warn "OpenClaw Gateway 状态未知，请手动检查"
    fi
else
    log_error "OpenClaw Gateway 重启失败，请检查日志"
    log_info "查看日志: tail -f /tmp/openclaw/openclaw-*.log"
fi

# 验证部署
echo ""
echo "=============================================="
echo "  部署验证"
echo "=============================================="

# 检查 Nginx 代理
log_info "检查 Nginx 代理状态..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:${NGINX_PROXY_PORT}/health 2>/dev/null | grep -q "200"; then
    log_ok "Nginx 代理运行正常 (端口: ${NGINX_PROXY_PORT})"
else
    log_warn "Nginx 代理健康检查失败，请检查配置"
fi

# 检查 OpenClaw 状态
log_info "检查 OpenClaw 状态..."
if openclaw gateway status 2>&1 | grep -q "running"; then
    log_ok "OpenClaw Gateway 运行正常"
else
    log_warn "OpenClaw Gateway 未运行"
fi

# 显示配置摘要
echo ""
echo "=============================================="
echo "  配置摘要"
echo "=============================================="
echo -e "  ${GREEN}Nginx 代理端口:${NC}    ${NGINX_PROXY_PORT}"
echo -e "  ${GREEN}限流速率:${NC}          ${RATE_LIMIT}"
echo -e "  ${GREEN}突发大小:${NC}          ${BURST_SIZE}"
echo -e "  ${GREEN}OpenClaw 配置:${NC}     ${OPENCLAW_CONFIG}"
echo -e "  ${GREEN}Nginx 配置:${NC}        ${NGINX_CONF}"
echo -e "  ${GREEN}环境变量文件:${NC}      ${ENV_FILE}"
echo -e "  ${GREEN}配置备份:${NC}          ${BACKUP_FILE}"
echo ""

# 测试命令提示
echo "=============================================="
echo "  测试命令"
echo "=============================================="
echo ""
echo "# 测试 Nginx 限流（连续发送 10 个请求）："
echo "for i in {1..10}; do"
echo "  curl -s -o /dev/null -w \"%{http_code}\\n\" http://127.0.0.1:${NGINX_PROXY_PORT}/compatible-mode/v1/models \\"
echo "    -H \"Authorization: Bearer sk-test\""
echo "done"
echo ""
echo "# 查看 Nginx 限流日志："
echo "sudo tail -f /var/log/nginx/error.log | grep \"limiting\""
echo ""
echo "# 查看 OpenClaw 日志："
echo "tail -f /tmp/openclaw/openclaw-*.log | grep -i \"rate\\|retry\\|timeout\""
echo ""
echo "# 恢复原配置（如需回滚）："
echo "cp ${BACKUP_FILE} ${OPENCLAW_CONFIG}"
echo "openclaw gateway restart"
echo ""
echo "=============================================="
echo -e "  ${GREEN}✅ 部署完成！${NC}"
echo "=============================================="
