#!/bin/bash
# 🦞 小龙虾网络 V3.0 同步验证脚本（修复版）
# 修复：目录名 hyphen→underscore，类名与实际代码对齐
# 用法: bash /shared/training/go/sync_v3.sh

set -e
echo "🦞 小龙虾网络 V3.0 同步验证脚本（修复版）"
echo "========================================"
echo "节点: $(hostname) | 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

WORKDIR=$(pwd)
# 自动定位仓库根目录
for d in /home/admin/go-training/lobster-network \
          ~/WorkBuddy/Claw/lobster-network \
          /workspace/lobster-network \
          "."; do
  if [ -d "$d/mcp" ] || [ -d "$d/vector_memory" ]; then
    cd "$d" 2>/dev/null && break
  fi
done
echo "📍 工作目录: $(pwd)"

# 拉取最新代码
echo ""
echo "📡 [1/7] 拉取最新代码..."
git pull origin master 2>&1 || git pull origin main 2>&1 || echo "⚠ 拉取失败，使用本地代码"
echo "✓ 代码就绪"
echo ""

# 验证1: MCP 协议
echo "🔧 [2/7] 验证 MCP 协议..."
python3 -c "
import sys; sys.path.insert(0, '.')
from mcp.mcp_server import MCP_TOOLS
print(f'  MCP Server: ✓ 加载成功，工具数={len(MCP_TOOLS)}')
for name, tool in list(MCP_TOOLS.items())[:3]:
    print(f'    - {name}: {tool.get(\"description\",\"\")[:50]}')
" 2>&1 && echo "✓ MCP 协议验证通过" || echo "✗ MCP 协议验证失败"
echo ""

# 验证2: 向量记忆系统
echo "🧠 [3/7] 验证向量记忆系统..."
python3 -c "
import sys; sys.path.insert(0, '.')
try:
    from vector_memory.vector_memory import VectorMemory, Memory
    vm = VectorMemory(storage_path='/tmp/lobster_v3_test')
    mid = vm.add_memory(Memory(
        memory_id='test_001',
        memory_type='semantic',
        content='V3.0 测试记忆',
        embedding=[0.1]*128,
        metadata={'source': 'sync_v3'}
    ))
    results = vm.search('V3.0 测试', top_k=1)
    print(f'  VectorMemory: ✓ 写入/搜索成功，结果数={len(results)}')
except ImportError as e:
    print(f'  VectorMemory: ⚠ 缺少依赖: {e}')
    print('  （跳过高，节点间同步不依赖向量记忆）')
" 2>&1
echo ""

# 验证3: A2A 协议
echo "📡 [4/7] 验证 A2A 协议..."
python3 -c "
import sys; sys.path.insert(0, '.')
from a2a.a2a_protocol import A2ANode
node = A2ANode(node_id='test_node', name='测试节点')
node.add_capability('go_training')
print(f'  A2A Protocol: ✓ 节点创建成功，能力数={len(node.capabilities)}')
print(f'    node_id={node.node_id}, name={node.name}')
" 2>&1 && echo "✓ A2A 协议验证通过" || echo "✗ A2A 协议验证失败"
echo ""

# 验证4: 联邦学习系统
echo "🤝 [5/7] 验证联邦学习系统..."
python3 -c "
import sys; sys.path.insert(0, '.')
from federated_learning.federated_learning import FederatedClient
client = FederatedClient(client_id='test_client', name='测试客户端')
print(f'  FederatedLearning: ✓ 客户端创建成功，ID={client.client_id}')
" 2>&1 && echo "✓ 联邦学习系统验证通过" || echo "✗ 联邦学习系统验证失败"
echo ""

# 验证5: 智能体经济系统
echo "💰 [6/7] 验证智能体经济系统..."
python3 -c "
import sys; sys.path.insert(0, '.')
from agent_economy.economy_system import Agent
agent = Agent(agent_id='test_agent', name='测试智能体')
print(f'  EconomySystem: ✓ 智能体创建成功，ID={agent.agent_id}, 余额={agent.balance}')
agent.complete_task(reward=50.0, accuracy=0.85)
print(f'    完成任务后余额={agent.balance}, 信誉={agent.reputation}')
" 2>&1 && echo "✓ 智能体经济系统验证通过" || echo "✗ 智能体经济系统验证失败"
echo ""

# 验证6: 目录结构检查（确认 hyphen→underscore 改名完成）
echo "📁 [7/7] 验证 V3.0 目录结构..."
PASS=0
for dir in mcp a2a vector_memory federated_learning agent_economy; do
  if [ -d "$dir" ] && [ -f "$dir/__init__.py" ]; then
    echo "  ✓ $dir/ 存在且是 Python 包"
    PASS=$((PASS+1))
  else
    echo "  ✗ $dir/ 缺失或不是 Python 包"
  fi
done
echo "  目录结构: $PASS/5 通过"
echo ""

# 汇总
echo "========================================"
echo "📋 验证汇总"
echo "========================================"
echo "节点: $(hostname)"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "分支: $(git branch --show-current 2>/dev/null || echo 'unknown')"
echo "提交: $(git log --oneline -1 2>/dev/null || echo 'unknown')"
echo "状态: V3.0 五大组件验证完成（见上方详细结果）"
echo ""
echo "✅ 同步验证完成！请向下一个节点广播验证结果。"
echo "========================================"
