#!/bin/bash
<<<<<<< HEAD
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
=======
# SSH健康检查 - 每30分钟检查各节点连通性

LOG="/home/admin/.openclaw/workspace/reports/ssh-health-$(date +%Y%m%d).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] SSH健康检查开始" >> $LOG

# 检查小陈
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no admin@121.43.80.231 "echo OK" >/dev/null 2>&1; then
    echo "[$TIMESTAMP] 小陈(121.43.80.231): 在线" >> $LOG
else
    echo "[$TIMESTAMP] 小陈(121.43.80.231): 离线" >> $LOG
fi

# 检查诸葛虾
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no admin@60.205.139.51 "echo OK" >/dev/null 2>&1; then
    echo "[$TIMESTAMP] 诸葛虾(60.205.139.51): 在线" >> $LOG
else
    echo "[$TIMESTAMP] 诸葛虾(60.205.139.51): 离线" >> $LOG
fi

# 检查诸葛马
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no admin@172.24.57.34 "echo OK" >/dev/null 2>&1; then
    echo "[$TIMESTAMP] 诸葛马(172.24.57.34): 在线" >> $LOG
else
    echo "[$TIMESTAMP] 诸葛马(172.24.57.34): 离线" >> $LOG
fi

echo "[$TIMESTAMP] SSH健康检查完成" >> $LOG
>>>>>>> fbc3017db51a546a289ef16bd15ae36823f768d7
