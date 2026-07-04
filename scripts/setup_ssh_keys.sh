#!/bin/bash
# 🦞 小龙虾网络 · SSH密钥配置脚本
# 用途: 配置服务器间SSH免密登录
# 版本: V1.0 | 日期: 2026-06-27

set -e

echo "🦞 小龙虾网络 · SSH密钥配置"
echo "========================================"

# 节点列表
NODES=(
    "admin@47.93.6.57:诸葛马"
    "admin@183.134.108.26:诸葛虾"
    "admin@121.43.80.231:小陈"
)

# 检查SSH密钥
echo ""
echo "📋 检查SSH密钥..."
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "⚠️ 未找到SSH密钥，正在生成..."
    ssh-keygen -t ed25519 -C "lobster-network@$(hostname)" -f ~/.ssh/id_ed25519 -N ""
    echo "✅ SSH密钥已生成"
else
    echo "✅ SSH密钥已存在"
fi

# 显示公钥
echo ""
echo "🔑 你的公钥:"
cat ~/.ssh/id_ed25519.pub

# 配置SSH config
echo ""
echo "📝 配置SSH config..."
cat > ~/.ssh/config << 'EOF'
Host zhugeMa
    HostName 47.93.6.57
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    TCPKeepAlive yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host zhuguxia
    HostName 183.134.108.26
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    TCPKeepAlive yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host xiaochen
    HostName 121.43.80.231
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    TCPKeepAlive yes
    ServerAliveInterval 60
    ServerAliveCountMax 3

Host qoder
    HostName 192.168.1.161
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    TCPKeepAlive yes
    ServerAliveInterval 60
    ServerAliveCountMax 3
EOF
chmod 600 ~/.ssh/config
echo "✅ SSH config已配置"

# 分发公钥
echo ""
echo "📤 分发公钥到各节点..."
for node in "${NODES[@]}"; do
    IFS=':' read -r addr name <<< "$node"
    echo ""
    echo "🔹 配置 $name ($addr)..."
    
    # 复制公钥
    ssh-copy-id -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519.pub "$addr" 2>&1 || {
        echo "⚠️ 无法自动配置 $name，请手动复制公钥:"
        echo "   ssh-copy-id -i ~/.ssh/id_ed25519.pub $addr"
        continue
    }
    
    # 测试连接
    if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$addr" "echo '✅ 连接成功'" 2>/dev/null; then
        echo "✅ $name 配置成功"
    else
        echo "❌ $name 连接失败"
    fi
done

# 测试连通性
echo ""
echo "🧪 测试连通性..."
for node in "${NODES[@]}"; do
    IFS=':' read -r addr name <<< "$node"
    echo -n "  $name: "
    if ssh -o ConnectTimeout=10 "$addr" "echo '✅'" 2>/dev/null; then
        echo "✅ 可达"
    else
        echo "❌ 不可达"
    fi
done

echo ""
echo "========================================"
echo "✅ SSH密钥配置完成！"
echo ""
echo "📋 使用方法:"
echo "   ssh zhugeMa    # 连接到诸葛马"
echo "   ssh zhuguxia   # 连接到诸葛虾"
echo "   ssh xiaochen   # 连接到小陈"
echo "   ssh qoder      # 连接到qoder"
echo ""
echo "📁 共享目录:"
echo "   /home/admin/go-training/shared/"
