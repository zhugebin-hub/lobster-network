#!/bin/bash
# 🦞 小龙虾网络 V3.0 同步验证脚本
# 用途: 拉取最新代码 + 验证五大核心组件
# 版本: V3.0 | 日期: 2026-06-28
# 用法: bash /shared/training/go/sync_v3.sh

set -e
echo "🦞 小龙虾网络 V3.0 同步验证脚本"
echo "========================================"
echo "节点: $(hostname) | 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 拉取最新代码
echo "📡 [1/6] 拉取最新代码..."
cd /home/admin/go-training/lobster-network 2>/dev/null || \
cd ~/WorkBuddy/Claw/lobster-network 2>/dev/null || \
cd /workspace/lobster-network 2>/dev/null || \
{ echo "✗ 找不到仓库目录"; exit 1; }

git pull origin master 2>&1 || git pull origin main 2>&1 || echo "⚠ 拉取失败，使用本地代码"
echo "✓ 代码就绪"
echo ""

# 2. 测试 MCP 协议
echo "🔧 [2/6] 测试 MCP 协议 (mcp/mcp_server.py)..."
python3 -c "
import sys; sys.path.insert(0, '.')
from mcp.mcp_server import MCPServer, MCPTool
server = MCPServer()
tools = server.list_tools()
print(f'  MCP Server: ✓ 加载成功，工具数={len(tools)}')
for t in tools[:3]:
    print(f'    - {t.name}: {t.description[:50]}')
" 2>&1 && echo "✓ MCP 协议测试通过" || echo "✗ MCP 协议测试失败"
echo ""

# 3. 测试向量记忆系统
echo "🧠 [3/6] 测试向量记忆系统 (vector-memory/vector_memory.py)..."
python3 -c "
import sys; sys.path.insert(0, '.')
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
" 2>&1 && echo "✓ 向量记忆系统测试通过" || echo "✗ 向量记忆系统测试失败"
echo ""

# 4. 测试 A2A 协议
echo "📡 [4/6] 测试 A2A 协议 (a2a/a2a_protocol.py)..."
python3 -c "
import sys; sys.path.insert(0, '.')
from a2a.a2a_protocol import A2AProtocol, A2AMessage
proto = A2AProtocol(node_id='test_node')
msg = proto.create_message(target='peer', payload={'cmd': 'ping'})
print(f'  A2A Protocol: ✓ 消息创建成功，msg_id={msg.msg_id[:16]}...')
" 2>&1 && echo "✓ A2A 协议测试通过" || echo "✗ A2A 协议测试失败"
echo ""

# 5. 测试联邦学习系统
echo "🤝 [5/6] 测试联邦学习系统 (federated-learning/federated_learning.py)..."
python3 -c "
import sys; sys.path.insert(0, '.')
from federated_learning.federated_learning import FederatedLearning, ClientUpdate
fl = FederatedLearning(model_dim=64)
update = ClientUpdate(client_id='test_client', weights=[0.1]*64, num_samples=100)
global_model = fl.aggregate([update])
print(f'  FederatedLearning: ✓ 聚合成功，模型维度={len(global_model)}')
" 2>&1 && echo "✓ 联邦学习系统测试通过" || echo "✗ 联邦学习系统测试失败"
echo ""

# 6. 测试智能体经济系统
echo "💰 [6/6] 测试智能体经济系统 (agent-economy/economy_system.py)..."
python3 -c "
import sys; sys.path.insert(0, '.')
from agent_economy.economy_system import EconomySystem, Transaction
es = EconomySystem()
tx = Transaction(sender='node_A', receiver='node_B', amount=10.0, tx_type='reward')
txid = es.submit_transaction(tx)
balance = es.get_balance('node_B')
print(f'  EconomySystem: ✓ 交易提交成功，node_B余额={balance} 龙虾币')
" 2>&1 && echo "✓ 智能体经济系统测试通过" || echo "✗ 智能体经济系统测试失败"
echo ""

# 汇总
echo "========================================"
echo "📋 验证汇总"
echo "========================================"
echo "节点: $(hostname)"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "分支: $(git branch --show-current)"
echo "提交: $(git log --oneline -1)"
echo "状态: V3.0 五大组件验证完成"
echo ""
echo "✅ 同步验证完成！请向下一个节点广播验证结果。"
echo "========================================"
