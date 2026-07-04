#!/bin/bash
# 🦞 批量部署 10 个龙虾节点
# ================================
# 使用方式：./batch-deploy.sh

set -e

echo "🦞 批量部署龙虾池 10 个节点"
echo "=========================================="
echo ""

# 龙虾配置（根据实际情况修改 IP 和端口）
declare -A LOBSTERS=(
    ["lobster-001"]="127.0.0.1:8001"  # 本地（小龙虾，调度中枢）
    ["lobster-002"]="192.168.1.102:8002"
    ["lobster-003"]="192.168.1.103:8003"
    ["lobster-004"]="192.168.1.104:8004"
    ["lobster-005"]="192.168.1.105:8005"
    ["lobster-006"]="192.168.1.106:8006"
    ["lobster-007"]="192.168.1.107:8007"
    ["lobster-008"]="192.168.1.108:8008"
    ["lobster-009"]="192.168.1.109:8009"
    ["lobster-010"]="192.168.1.110:8010"
)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📋 龙虾节点列表:"
for id in "${!LOBSTERS[@]}"; do
    echo "   $id → ${LOBSTERS[$id]}"
done
echo ""

# 本地部署 lobster-001
echo "🚀 部署本地节点 (lobster-001)..."
cd "$SCRIPT_DIR"
bash deploy.sh --lobster-id=lobster-001 --port=8001

echo ""
echo "=========================================="
echo "📋 远程部署说明"
echo "=========================================="
echo ""
echo "对于其他 9 个节点，请在对应服务器上执行："
echo ""

for id in "${!LOBSTERS[@]}"; do
    if [ "$id" != "lobster-001" ]; then
        ip=$(echo "${LOBSTERS[$id]}" | cut -d: -f1)
        port=$(echo "${LOBSTERS[$id]}" | cut -d: -f2)
        echo "# $id ($ip:$port)"
        echo "scp $SCRIPT_DIR/deploy.sh $SCRIPT_DIR/wrapper.py $SCRIPT_DIR/lobster-wrapper@.service $ip:~/lobster-network/"
        echo "ssh $ip 'cd ~/lobster-network && bash deploy.sh --lobster-id=$id --port=$port'"
        echo ""
    fi
done

echo ""
echo "=========================================="
echo "✅ 本地部署完成！"
echo "=========================================="
echo ""
echo "下一步:"
echo "1. 验证本地节点：curl http://127.0.0.1:8001/health"
echo "2. 在其他 9 台服务器上执行上述命令"
echo "3. 更新 lobster_scheduler.py 中的 LOBSTER_POOL_CONFIG"
echo ""
