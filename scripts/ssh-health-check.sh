#!/bin/bash
# ssh-health-check.sh - SSH通道健康检查脚本
# 定期检查各节点SSH连接状态

set -e

echo "============================================"
echo "🦞 小龙虾网络 SSH通道健康检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
echo ""

# 节点配置
declare -A NODES
NODES=(
    ["zhugema"]="172.24.57.34"
    ["xiaochen"]="121.43.80.231"
    ["zhuguxia"]="60.205.139.51"
)

# 检查各节点
for node in "${!NODES[@]}"; do
    ip="${NODES[$node]}"
    echo "🔍 检查 $node ($ip)..."
    
    if ssh -i ~/.ssh/id_rsa_hermes -o StrictHostKeyChecking=no -o ConnectTimeout=10 admin@$ip "echo '✅ 在线'; hostname; uptime" 2>/dev/null; then
        echo "  ✅ 连接成功"
    else
        echo "  ❌ 连接失败"
    fi
    echo ""
done

echo "============================================"
echo "✅ SSH通道健康检查完成"
echo "============================================"
