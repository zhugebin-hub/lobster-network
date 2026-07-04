# 🐚 多智能体协作围棋对弈系统

## 概述

基于 NFS 共享目录通信的多智能体协作围棋对弈 Demo。

**参与者：**
- 🦞 虾尔（lobster-001）- 执黑，运行于 iZ2zeetm9awnkwdni43joiZ
- 🐴 诸葛马（Hermes）- 执白，运行于 iZ2zeckfeiop1os2jkyy94Z

**通信方式：** NFS 共享目录 `/shared/messages/`

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    NFS 共享目录 (/shared)                     │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │  from-lobster/      │    │  from-hermes/       │         │
│  │  (虾尔→诸葛马)       │    │  (诸葛马→虾尔)       │         │
│  └─────────────────────┘    └─────────────────────┘         │
│  ┌─────────────────────────────────────────────────┐        │
│  │  go-game/                                       │        │
│  │    board.json     (棋盘状态)                      │        │
│  │    move-queue/    (待处理棋步)                    │        │
│  │    game-log.json  (对弈日志)                      │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│   虾尔 (OpenClaw) │          │  诸葛马 (Hermes)  │
│                  │          │                  │
│  go_engine.py    │          │  go_engine.py    │
│  agent.py        │          │  agent.py        │
│  strategy.py     │          │  strategy.py     │
└──────────────────┘          └──────────────────┘
```

## 快速开始

```bash
# 1. 初始化游戏
python3 scripts/init_game.py

# 2. 虾尔落子（黑方）
python3 scripts/make_move.py --agent lobster --move D4

# 3. 查看棋盘
python3 scripts/show_board.py

# 4. 诸葛马落子（白方，通过NFS消息）
# 诸葛马读取 /shared/go-game/board.json，计算棋步，写入 /shared/messages/from-hermes/
```

## 文件结构

```
multi-agent-go-game/
├── engine/              # 围棋引擎
│   ├── board.py         # 棋盘表示和规则
│   ├── move.py          # 棋步验证
│   └── scorer.py        # 胜负判定
├── strategies/          # 策略模块
│   ├── base.py          # 基础策略接口
│   ├── simple.py        # 简单策略（随机+基础评估）
│   └── territorial.py   # 实地策略
├── communication/       # 通信模块
│   ├── nfs_bus.py       # NFS 消息总线
│   └── protocol.py      # 消息协议
├── game-state/          # 游戏状态
├── docs/                # 文档
├── scripts/             # 脚本
│   ├── init_game.py     # 初始化游戏
│   ├── make_move.py     # 落子
│   └── show_board.py    # 显示棋盘
└── README.md
```

## 技术栈

- **语言：** Python 3
- **通信：** NFS 共享目录（文件消息）
- **协议：** JSON 格式消息
- **棋盘：** 9x9 围棋（简化版）

## 消息协议

```json
{
  "type": "go_move",
  "from": "lobster-001",
  "to": "hermes",
  "game_id": "go-game-20260603",
  "move": {
    "color": "black",
    "position": "D4",
    "move_number": 1,
    "timestamp": 1717400000
  },
  "board_hash": "abc123..."
}
```

## 状态

- [x] 围棋引擎（棋盘、规则、提子）
- [x] NFS 通信层
- [x] 策略模块
- [x] 游戏脚本
- [ ] 与诸葛马联调测试
