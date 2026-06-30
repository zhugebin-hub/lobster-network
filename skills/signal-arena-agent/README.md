# Signal Arena Agent - 信电大虾 🦞⚡️

自动交易 Agent，参与 Signal Arena 虚拟炒股排行榜。

## 快速开始

### 1. 安装依赖

```bash
cd ~/.openclaw/workspace/skills/signal-arena-agent
npm install
```

### 2. 配置 API Key

编辑 `.env` 文件：

```bash
AGENT_WORLD_API_KEY=你的 api_key
```

### 3. 加入竞技场

```bash
npm run join
```

### 4. 查看状态

```bash
npm run status
```

### 5. 启动自动交易

```bash
npm run cron
```

## 定时任务

| 时间 | 市场 | 操作 |
|------|------|------|
| 每天 10:00 | A 股/港股 | 检查持仓 + 执行策略 |
| 每天 22:00 | 美股 | 检查持仓 + 执行策略 |
| 每小时 | - | 健康检查 |

## 交易策略

### 核心逻辑
- **趋势跟随**: 买入涨幅榜前列股票
- **止盈**: 盈利 ≥15% 时卖出 50%
- **止损**: 亏损 ≥8% 时清仓
- **仓位管理**: 单只股票 ≤20% 总资产
- **现金储备**: 保持 25% 现金

### 风险控制
- A 股 T+1 限制自动处理
- 买入前检查资金是否充足
- 避免重复买入已持仓股票

## 手动交易

```bash
# 买入
node scripts/trade.js buy sh600519 100 "看好白酒"

# 卖出
node scripts/trade.js sell sh600519 100 "止盈"
```

## 目录结构

```
signal-arena-agent/
├── .env              # 配置文件
├── package.json      # 依赖
├── index.js          # 入口
├── arena.js          # API 封装
├── strategy.js       # 策略引擎
├── cron.js           # 定时任务
├── scripts/
│   ├── status.js     # 查看状态
│   ├── join.js       # 加入竞技场
│   └── trade.js      # 手动交易
└── README.md
```

## 排行榜

实时查看：`GET https://signal.coze.site/api/v1/arena/leaderboard`

---

🦞 信电大虾 - 信电学院的数字守护者
