# 🦞 小龙虾网络V5.1 - 多智能体协作系统

**基于 Agent Harness工程实践 + 可靠性/稳定性/算力优化升级**

---

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    小龙虾网络V5.1                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ 双阶段调度器  │    │ Sub-Agent    │    │ 事务管理器    │  │
│  │ (Initializer │    │ 管理器       │    │ (Lock + 断点  │  │
│  │  + Executor) │    │ (节点隔离)   │    │  续传)        │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐                      │
│  │ 硬护栏系统   │    │ 文档园丁     │                      │
│  │ (三层审核)   │    │ (定期清理)   │                      │
│  └──────────────┘    └──────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 核心优化（基于 V5.0）

### 1. 双阶段架构（Initializer + Executor）
- **Initializer：** 理解任务 → 制定计划 → 写入 plan.md → 退出
- **Executor：** 读取 plan.md → 按步执行 → 跨 Context Window 接力
- **优势：** 任务可跨多次会话延续，不依赖单一会话记忆

### 2. Sub-Agent 隔离
- 每个节点独立 Context Window
- 主 Agent 只接收结构化输出
- 避免上下文污染

### 3. 事务边界
- 引入 lock 文件机制
- 每完成一步追加进度
- 中断后读 lock 文件从断点续传

### 4. 硬护栏系统
- 第 1 层：白名单工具（限制可调用工具）
- 第 2 层：Linter 拦截（敏感词/合规检查）
- 第 3 层：第二个 Agent 审稿（独立 Context 审核）

### 5. 文档园丁
- 定期扫描过期文档
- 检测架构漂移
- 提交清理 PR
- 持续小额偿还技术债

---

## 📁 目录结构

```
lobster-network/
├── src/                      # 源代码
│   ├── main.py              # 集成入口
│   ├── dual_phase_scheduler.py  # 双阶段调度器
│   ├── sub_agent_manager.py     # Sub-Agent 管理器
│   ├── transaction_manager.py   # 事务管理器
│   ├── hard_guardrail.py        # 硬护栏系统
│   └── doc_gardener.py          # 文档园丁
├── workspace/                # 工作空间
│   ├── plans/               # 任务计划
│   ├── execution/           # 执行结果
│   ├── agents/              # Sub-Agent 上下文
│   ├── locks/               # 事务锁
│   └── transactions/        # 事务进度
├── docs/                    # 文档
└── README.md                # 本文档
```

---

## 🚀 快速开始

### 1. 初始化系统
```bash
cd /home/admin/.openclaw/workspace/lobster-network
python3 src/main.py
```

### 2. 调度任务
```python
from src.main import LobsterNetworkV41

network = LobsterNetworkV41()

# 调度训练任务
task = {
    "task_id": "training_001",
    "type": "training",
    "goal": "完成围棋 Day5 训练",
    "nodes": ["xiaochen", "zhuguxia", "qoder"],
    "params": {"day": 5, "subject": "go"}
}

result = network.schedule_task(task)
```

### 3. 分发到 Sub-Agent
```python
# 分发到训练协调器
result = network.dispatch_to_agent("training-coordinator", {
    "action": "distribute_training",
    "nodes": ["xiaochen", "zhuguxia", "qoder"],
    "day": 5
})
```

### 4. 内容审核
```python
# 硬护栏审核
result = network.validate_content("您好，请问有什么可以帮助您的？")
```

### 5. 文档清理
```python
# 扫描文档
status = network.scan_documents()

# 清理文档（模拟）
cleanup_result = network.cleanup_documents(dry_run=True)
```

---

## 📊 预期效果

| 指标 | V5.0 | V5.1（当前） |
|------|------|--------------|
| 任务成功率 | 60% | 85%+ |
| 上下文污染率 | 高 | 低 |
| 断点续传 | 无 | 支持 |
| 对外消息事故 | 每周 1-2 次 | 接近 0 |
| 节点协作效率 | 中 | 高 |

---

## 📚 相关文档

- [V5.1 优化方案](docs/optimization_report_v51.md)
- [Agent Harness工程实践](docs/给野马套上缰绳_Agent_Harness工程实践.docx)
- [多智能体协作框架成功案例](docs/多智能体协作框架在实际应用中的成功案例分析报告.pdf)

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

---

**版本：** V5.1
**更新日期：** 2026-07-07
**维护者：** 虾尔
