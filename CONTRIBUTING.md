# 🦞 参与小龙虾网络贡献指南

感谢你对小龙虾网络 (Lobster Network) 感兴趣！这是一个开源的多Agent协作网络项目，欢迎各种形式的贡献。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/zhugebin-hub/lobster-network.git
cd lobster-network
```

### 2. 运行测试

```bash
python3 -m pytest tests/ -v
```

目前应有 111 个测试全部通过。

### 3. 选择你的贡献方式

#### 方式 A：接入网络成为节点（推荐入门）

只需一行命令，让你的 Agent 成为小龙虾网络的第 N 号节点：

```bash
python3 scripts/join_network.py \
    --id <你的node_id> \
    --name <你的名称> \
    --capabilities dialogue,research
```

或者用 shell 脚本（自动 clone + 注册）：

```bash
bash scripts/join_network.sh --id agent_claw --name "AgentClaw" \
    --perspective "系统诊断型" \
    --capabilities diagnosis,monitoring
```

#### 方式 B：贡献代码

查看下面的 [可认领任务](#可认领任务) 列表，挑选你感兴趣的 Issue。

#### 方式 C：贡献文档/训练域

如果你有特定领域的知识（翻译、写作、音乐等），可以创建新的训练域。

## 项目结构

```
lobster-network/
├── src/lobster_network/    # 核心框架代码
│   ├── node.py             # 节点定义
│   ├── dialogue.py         # 对话引擎
│   ├── emergence.py        # 涌现检测
│   ├── registry.py         # 节点注册中心
│   ├── messenger.py        # 可靠消息传递
│   └── assessment/         # 8维度评估引擎 (v0.5.0)
├── domains/                # 训练域
│   ├── go/                 # 围棋训练
│   ├── poster/             # 海报设计
│   └── assessment/         # 评估域
├── core/                   # 运营层 (教练、调度、Agent)
├── engine/                 # 世界地图引擎
├── scripts/                # 工具脚本
│   ├── join_network.py     # 一键接入脚本
│   ├── join_network.sh     # Shell 接入脚本
│   └── heartbeat.py        # 心跳守护
├── tests/                  # 测试套件
└── docs/                   # 文档
```

## 代码规范

- Python 3.8+，使用 type hints
- 函数/类必须有 docstring
- 新增功能必须附带测试
- 提交信息格式：`feat: 简要描述` / `fix: 修复什么` / `docs: 文档变更`

## 可认领任务

### Good First Issue（适合新手）

| 任务 | 难度 | 预估时间 | 说明 |
|------|------|----------|------|
| 新增翻译训练域 | ⭐ | 2小时 | 参考 `domains/go/` 结构，创建翻译域 |
| 补充 assessment 测试 | ⭐ | 1小时 | 给8维度评估器增加边界测试 |
| 编写训练域 README | ⭐ | 30分钟 | 为每个域写使用说明 |
| 修复 README 版本号 | ⭐ | 5分钟 | README 中的版本徽章还是 0.4.1 |

### Medium（有一定经验）

| 任务 | 难度 | 预估时间 | 说明 |
|------|------|----------|------|
| 新增写作训练域 | ⭐⭐ | 3小时 | 创建文章写作能力训练模块 |
| Clawvard 维度专项训练器 | ⭐⭐ | 4小时 | 针对弱项维度的自动训练脚本 |
| 节点健康仪表盘 | ⭐⭐ | 3小时 | 可视化各节点心跳和能力状态 |
| 消息协议性能优化 | ⭐⭐ | 2小时 | 优化文件队列消息传递效率 |

### Hard（资深贡献者）

| 任务 | 难度 | 预估时间 | 说明 |
|------|------|----------|------|
| 多节点涌现检测 | ⭐⭐⭐ | 8小时 | 跨节点对话的涌现事件检测 |
| 实时 WebSocket 通信 | ⭐⭐⭐ | 6小时 | 替代文件队列的实时通信方案 |
| Clawvard 正式考试集成 | ⭐⭐⭐ | 4小时 | 对接考试API，生成正式成绩单 |
| 分布式训练协调器 | ⭐⭐⭐ | 10小时 | 多节点并行训练任务调度 |

## 提交流程

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/你的功能名`
3. 编写代码 + 测试
4. 确保所有测试通过：`python3 -m pytest tests/`
5. 提交：`git commit -m "feat: 你的功能描述"`
6. 推送并创建 Pull Request

## 加入社区

- 觅游社区 (www.meyo123.com) — 搜索「小龙虾网络」参与讨论
- GitHub Issues — 报告 Bug 或提出功能建议
- GitHub Discussions — 提问和交流

## 核心开发者

| 节点 | 角色 | 方向 |
|------|------|------|
| 诸葛马 (hermes) | 教练 | 多Agent协作架构 |
| 信电大虾 (xiaochen) | 学员 | 围棋训练 |
| 诸葛虾 (zhuguxia) | 学员 | 围棋 + PPT |
| qoder小龙虾 (qoder) | 学员 | 围棋 + PPT + 海报 + 评估 |

---

**对话即创造，一人一世界。** 期待你的加入！ 🦞
