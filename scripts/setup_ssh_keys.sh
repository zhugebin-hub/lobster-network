#!/bin/bash
# -*- coding: utf-8 -*-
"""
SSH密钥配置脚本
功能：为各服务器配置SSH密钥，实现相互通信
作者：诸葛马 (Hermes)
日期：2026-06-27
# 🦞 小龙虾网络 · SSH密钥配置脚本
# 用途: 配置服务器间SSH免密登录
# 版本: V1.0 | 日期: 2026-06-27
"""

set -e

echo "🦞 小龙虾网络 · SSH密钥配置"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# SSH配置
SSH_KEY="$HOME/.ssh/id_rsa_hermes"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o ConnectTimeout=5"

# 节点列表 (合并 main + master)
NODES=(
    "admin@47.93.6.57:诸葛马"
    "admin@60.205.139.51:诸葛虾"
    "admin@121.43.80.231:小陈"
)

echo "========================================"
echo "🔑 SSH密钥配置脚本"
echo "========================================"
echo ""

# 检查SSH密钥
if [ ! -f "$SSH_KEY" ]; then
    echo -e "${RED}✗ SSH密钥不存在: $SSH_KEY${NC}"
    echo "请先运行: ssh-keygen -t rsa -b 4096 -f $SSH_KEY -N ''"
    exit 1
fi

echo -e "${GREEN}✓ SSH密钥已找到: $SSH_KEY${NC}"
echo ""

# 获取公钥内容
PUBLIC_KEY=$(cat "${SSH_KEY}.pub")

# 配置每个节点
for node in "${NODES[@]}"; do
    IFS=':' read -r -a parts <<< "$node"
    server="${parts[0]}"
    name="${parts[1]}"
    
    echo -e "${YELLOW}► 配置 $name ($server)...${NC}"
    
    # 创建.ssh目录（如果不存在）
    ssh $SSH_OPTS "$server" "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
    
    # 添加公钥
    ssh $SSH_OPTS "$server" "echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys"
    ssh $SSH_OPTS "$server" "chmod 600 ~/.ssh/authorized_keys"
    
    echo -e "${GREEN}  ✓ $name 配置完成${NC}"
    echo ""
done

echo "========================================"
echo -e "${GREEN}✅ 所有节点SSH密钥配置完成！${NC}"
echo "========================================"
echo ""
echo "测试连接："
for node in "${NODES[@]}"; do
    IFS=':' read -r -a parts <<< "$node"
    server="${parts[0]}"
    name="${parts[1]}"
    
    echo -n "  $name ($server): "
    if ssh -o ConnectTimeout=3 -o BatchMode=yes "$server" "echo '✓'" 2>/dev/null; then
        echo -e "${GREEN}✓ 连接成功${NC}"
    else
        echo -e "${RED}✗ 连接失败${NC}"
    fi
done
