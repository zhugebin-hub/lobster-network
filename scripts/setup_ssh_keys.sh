#!/bin/bash
# -*- coding: utf-8 -*-
"""
SSH密钥配置脚本
功能：为各服务器配置SSH密钥，实现相互通信

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# SSH配置
SSH_KEY="$HOME/.ssh/id_rsa_hermes"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o ConnectTimeout=5"

# 服务器列表
SERVERS=(
    "admin@183.134.108.26:诸葛虾"
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
echo "公钥内容: $PUBLIC_KEY"
echo ""

# 配置各服务器
for SERVER_INFO in "${SERVERS[@]}"; do
    SERVER=$(echo $SERVER_INFO | cut -d: -f1)
    NAME=$(echo $SERVER_INFO | cut -d: -f2)
    
    echo "========================================"
    echo "📡 配置 $NAME ($SERVER)"
    echo "========================================"
    
    # 测试连接
    if ssh $SSH_OPTS $SERVER "echo '连接成功'" 2>/dev/null; then
        echo -e "${GREEN}✓ $NAME 连接成功${NC}"
    else
        echo -e "${YELLOW}⚠ $NAME 连接失败，需要手动配置${NC}"
        echo ""
        echo "请在 $NAME 服务器上执行："
        echo "  mkdir -p ~/.ssh"
        echo "  echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys"
        echo "  chmod 600 ~/.ssh/authorized_keys"
        echo ""
        continue
    fi
    
    # 配置authorized_keys
    ssh $SSH_OPTS $SERVER "
        mkdir -p ~/.ssh
        if ! grep -q '$PUBLIC_KEY' ~/.ssh/authorized_keys 2>/dev/null; then
            echo '$PUBLIC_KEY' >> ~/.ssh/authorized_keys
        fi
        chmod 600 ~/.ssh/authorized_keys
        echo '✓ authorized_keys配置完成'
    "
    
    # 验证配置
    if ssh $SSH_OPTS $SERVER "echo '验证成功'" 2>/dev/null; then
        echo -e "${GREEN}✓ $NAME SSH配置完成${NC}"
    else
        echo -e "${RED}✗ $NAME SSH配置失败${NC}"
    fi
    
    echo ""
done

echo "========================================"
echo "✅ SSH密钥配置完成"
echo "========================================"
