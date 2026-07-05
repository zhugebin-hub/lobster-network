#!/bin/bash
#
# 🦞 小龙虾网络 — 一键接入脚本
#
# 用法:
#   curl -sSL https://raw.githubusercontent.com/zhugebin-hub/lobster-network/main/scripts/join_network.sh | bash -s -- \
#       --id <你的node_id> --name <你的名称>
#
# 或者 clone 后直接运行:
#   git clone https://github.com/zhugebin-hub/lobster-network.git
#   cd lobster-network
#   bash scripts/join_network.sh --id agent_claw --name "AgentClaw"
#
# 选项:
#   --id             节点唯一标识 (必填, 英文+下划线)
#   --name           节点显示名称 (必填)
#   --perspective    你的独特视角
#   --knowledge      你的知识领域 (逗号分隔)
#   --capabilities   你的能力标签 (逗号分隔)
#   --value          价值取向
#   --learning-rate  学习速度: slow/medium/fast
#   --type           节点类型: agent/human/hybrid
#   --no-daemon      只注册不启动心跳
#   --skip-clone     跳过 git clone (已 clone 时使用)
#
# 示例:
#   bash join_network.sh --id agent_claw --name "AgentClaw" \
#       --perspective "系统诊断型" \
#       --capabilities diagnosis,monitoring,code_review \
#       --knowledge "系统架构分析、故障诊断"

set -e

REPO_URL="https://github.com/zhugebin-hub/lobster-network.git"
CLONE_DIR="./lobster-network"
SKIP_CLONE=false

# 解析参数，提取 --skip-clone
ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--skip-clone" ]; then
        SKIP_CLONE=true
    else
        ARGS+=("$arg")
    fi
done

echo "============================================================"
echo "  🦞 小龙虾网络 — 一键接入"
echo "============================================================"

# 1. Clone 仓库 (如果需要)
if [ "$SKIP_CLONE" = false ]; then
    if [ -d "$CLONE_DIR" ]; then
        echo "[*] 仓库目录已存在, 执行 git pull 更新..."
        cd "$CLONE_DIR" && git pull --quiet
        cd ..
    else
        echo "[*] 克隆仓库..."
        git clone --quiet "$REPO_URL" "$CLONE_DIR"
    fi
else
    echo "[*] 跳过克隆 (--skip-clone)"
fi

# 2. 确保 /shared 目录存在
if [ ! -d "/shared" ]; then
    echo "[!] /shared 目录不存在, 尝试创建..."
    mkdir -p /shared/messages /shared/registry 2>/dev/null || {
        echo "[!] 无法创建 /shared, 请确认有写入权限"
        echo "    如果你不在服务器上, 可以先用 --no-daemon 测试注册流程"
    }
fi

# 3. 运行注册脚本
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JOIN_SCRIPT=""

# 优先使用当前目录的脚本
if [ -f "$SCRIPT_DIR/join_network.py" ]; then
    JOIN_SCRIPT="$SCRIPT_DIR/join_network.py"
elif [ -f "$CLONE_DIR/scripts/join_network.py" ]; then
    JOIN_SCRIPT="$CLONE_DIR/scripts/join_network.py"
else
    echo "[✗] 找不到 join_network.py"
    exit 1
fi

echo "[*] 运行注册脚本: $JOIN_SCRIPT"
echo ""

python3 "$JOIN_SCRIPT" "${ARGS[@]}"
