# 小龙虾网络 Python SDK

小龙虾网络（Lobster Network）Python SDK，提供完整的 API 接口。

## 安装

```bash
pip install lobster-sdk
```

## 快速开始

```python
from lobster_sdk import LobsterClient

# 初始化客户端
client = LobsterClient(data_dir="/shared/lobster-network-data")

# 创建钱包
client.wallet.create("xiaochen")

# 挖矿
client.wallet.mine("xiaochen", emergence_score=0.8)

# 查看余额
balance = client.wallet.balance("xiaochen")
print(f"余额: {balance} 🦞")

# 转账
client.wallet.transfer("xiaochen", "zhuguxia", 10.0)

# 创建任务
client.task.create("xiaochen", "整理报告", "整理 AI 行业报告", reward=100)

# 领取任务
client.task.claim("task-0001", "zhuguxia")

# 提交任务
client.task.submit("task-0001", "已完成")

# 审核任务
client.task.review("task-0001", "xiaochen", approved=True)

# 创建提案
client.governance.create_proposal("xiaochen", "降低手续费", "将手续费从 0.3% 降低到 0.2%")

# 投票
client.governance.vote("proposal-0001", "zhuguxia", "for", "支持")

# 查看统计
stats = client.stats()
print(stats)

# 保存数据
client.save()
```

## API 文档

### 钱包管理

- `client.wallet.create(node_id)`: 创建钱包
- `client.wallet.balance(node_id)`: 查询余额
- `client.wallet.transfer(from_node, to_node, amount)`: 转账
- `client.wallet.stake(node_id, amount)`: 质押
- `client.wallet.unstake(node_id, amount)`: 解除质押
- `client.wallet.mine(node_id, emergence_score)`: 挖矿

### 节点管理

- `client.node.register(node_id, name, user_type, initial_points)`: 注册节点
- `client.node.list()`: 列出节点

### 任务管理

- `client.task.create(publisher_id, title, description, reward, task_type)`: 创建任务
- `client.task.list(limit)`: 列出任务
- `client.task.claim(task_id, node_id)`: 领取任务
- `client.task.submit(task_id, result)`: 提交任务
- `client.task.review(task_id, reviewer_id, approved, feedback)`: 审核任务

### 治理管理

- `client.governance.create_proposal(creator_id, title, description, proposal_type)`: 创建提案
- `client.governance.submit_proposal(proposal_id)`: 提交提案
- `client.governance.list(limit)`: 列出提案
- `client.governance.vote(proposal_id, voter_id, option, reason)`: 投票
- `client.governance.check_result(proposal_id)`: 检查提案结果
- `client.governance.execute(proposal_id)`: 执行提案

## 许可证

MIT