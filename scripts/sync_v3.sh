#!/bin/bash
# sync_v3.sh - V3.0组件验证脚本
# 功能: 测试MCP、向量记忆、A2A、联邦学习、经济系统
# 作者: 诸葛马 (AI教练)
# 版本: 1.1 (修复import路径)

set -e

echo "============================================"
echo "🧪 小龙虾网络V3.0 组件验证"
echo "============================================"

# 配置
REPO_DIR="/home/admin/lobster-network"
PYTHON="python3"
PASS=0
FAIL=0
TOTAL=5

cd "$REPO_DIR"

# 测试函数
test_module() {
    local module_name=$1
    local module_path=$2
    local test_func=$3
    
    echo ""
    echo "--------------------------------------------"
    echo "📦 测试模块: $module_name"
    echo "--------------------------------------------"
    
    # 使用正确的import路径 (hyphen -> underscore)
    local import_path=$(echo "$module_path" | sed 's/-/_/g')
    
    if $PYTHON -c "
import sys
sys.path.insert(0, '$REPO_DIR')
from $import_path.$module_name import $test_func
result = $test_func()
print(f'✅ {\"$module_name\"} 测试通过: {result}')
" 2>&1; then
        echo "✅ $module_name 测试通过"
        PASS=$((PASS+1))
    else
        echo "❌ $module_name 测试失败"
        FAIL=$((FAIL+1))
    fi
}

# 1. MCP服务器
test_module "mcp_server" "mcp" "test_mcp_server"

# 2. 向量记忆系统
test_module "vector_memory" "vector_memory" "test_vector_memory"

# 3. A2A协议
test_module "a2a_protocol" "a2a" "test_a2a_protocol"

# 4. 联邦学习系统
test_module "federated_learning" "federated_learning" "test_federated_learning"

# 5. 智能体经济系统
test_module "economy_system" "agent_economy" "test_agent_economy"

# 总结
echo ""
echo "============================================"
echo "📊 V3.0 测试总结"
echo "============================================"
echo "总测试数: $TOTAL"
echo "通过: $PASS"
echo "失败: $FAIL"
echo "通过率: $((PASS*100/TOTAL))%"
echo "============================================"

if [ $FAIL -eq 0 ]; then
    echo "✅ 全部测试通过！"
    exit 0
else
    echo "❌ 有 $FAIL 个测试失败"
    exit 1
fi
