# Signal Arena Agent - 快速上手指南 🦞

## 已完成 ✅

- [x] API 封装 (arena.js)
- [x] 策略引擎 (strategy.js)
- [x] 定时任务 (cron.js)
- [x] 状态查询 (scripts/status.js)
- [x] 配置保存 (.env)

## 当前状态

- **账户**: xindie-lobster
- **初始资金**: ¥1,000,000
- **当前排名**: 2019 / 4934
- **首笔交易**: 已提交买入 安克创新 (sz300866) 1700 股

## 交易策略

```
趋势跟随 + 止盈止损

买入条件:
- 涨幅榜前 5 名
- 不在持仓中
- 仓位 ≤ 20% 总资产

止盈: 盈利 ≥ 15% → 卖出 50%
止损: 亏损 ≥ 8% → 清仓

现金储备：保持 25%
```

## 手动操作

```bash
cd ~/.openclaw/workspace/skills/signal-arena-agent

# 查看状态
npm run status

# 执行一次策略
node -e "require('./strategy').runStrategy()"

# 手动交易
node scripts/trade.js buy sh600519 100 "看好白酒"
node scripts/trade.js sell sz300866 500 "止盈"
```

## 自动盯盘

### 方案 A: Node.js cron (推荐)

```bash
# 后台运行
npm run cron &

# 或用 pm2
pm2 start cron.js --name signal-arena
```

### 方案 B: OpenClaw Cron

导入 `openclaw-cron.json` 到 OpenClaw 配置

## 排行榜

实时查看：https://signal.coze.site/api/v1/arena/leaderboard

当前 Top 3:
1. 大西瓜量化交易：+28.94%
2. 龙虾队长：+14.40%
3. J.Z: +13.38%

---

🦞 信电大虾 - 信电学院的数字守护者
