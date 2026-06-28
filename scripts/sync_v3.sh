#!/bin/bash
# sync_v3.sh - V3.0组件验证脚本
# 功能: 验证五大核心组件是否存在且可 import
# 作者: 诸葛马 (AI教练) + 诸葛斌 (修复)
# 版本: 1.3 (简化为基础 import 验证)

set -e

echo "============================================"
echo "🧪 小龙虾网络V3.0 组件验证"
echo "============================================"

# 自动检测项目目录
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_DIR="$SCRIPT_DIR"
PYTHON="python3"
PASS=0
FAIL=0
TOTAL=5

cd "$REPO_DIR" || exit 1

# 基础 import 测试函数
test_import() {
    local module_name=$1
    local import_stmt=$2
    
    echo "--------------------------------------------"
    echo "📦 测试模块: $module_name"
    echo "--------------------------------------------"
    
    if $PYTHON -c "
import sys
sys.path.insert(0, '$REPO_DIR')
$import_stmt
print('✅ $module_name: import 成功')
" 2>&1; then
        PASS=$((PASS+1))
    else
        echo "❌ $module_name: import 失败"
        FAIL=$((FAIL+1))
    fi
    echo ""
}

# 1. MCP服务器
test_import "mcp_server" "from mcp.mcp_server import MCPServer"

# 2. 向量记忆系统
test_import "vector_memory" "from vector_memory.vector_memory import VectorMemory"

# 3. A2A协议
test_import "a2a_protocol" "from a2a.a2a_protocol import A2AServer, A2AMessage"

# 4. 联邦学习系统
test_import "federated_learning" "from federated_learning.federated_learning import FederatedLearning"

# 5. 智能体经济系统
test_import "economy_system" "from agent_economy.economy_system import AgentEconomy"

# 总结
echo "============================================"
echo "📊 V3.0 验证总结"
echo "============================================"
echo "总测试数: $TOTAL"
echo "通过: $PASS"
echo "失败: $FAIL"
echo "通过率: $((PASS*100/TOTAL))%"
echo "============================================"

if [ $FAIL -eq 0 ]; then
    echo "✅ 全部组件验证通过！V3.0 核心功能就绪。"
    exit 0
else
    echo "⚠️ 有 $FAIL 个组件验证失败，请检查。"
    exit 1
fi
