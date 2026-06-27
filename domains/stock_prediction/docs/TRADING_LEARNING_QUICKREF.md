# 🦞 小龙虾网络 - 炒股经验学习快速参考

## 🎯 核心目标
通过 Signal Arena 虚拟交易平台，系统化学习A股交易经验，构建可复用的知识库。

---

## 📚 已学到的关键经验

### 1️⃣ 简单均线策略的局限性
- **问题**: MA5/MA20交叉在熊市中滞后严重
- **数据**: 贵州茅台回测收益 -17.28%，最大回撤 -18.62%
- **改进**: 结合RSI、MACD、成交量多指标共振

### 2️⃣ 市场状态决定策略有效性
```python
if market_state == 'bear':      # 熊市 → 防御策略，最多10%仓位
elif market_state == 'bull':    # 牛市 → 积极做多，最多30%仓位  
else:                           # 震荡市 → 高抛低吸，最多20%仓位
```

### 3️⃣ 风险管理 > 择时能力
- **止损位**: 10%（保守）或 15%（激进）
- **单笔风险**: 不超过账户2%
- **凯利公式**: 保守仓位 = 12.5%（半凯利）

---

## 🔧 核心工具

### TradingExperienceLearner
```python
from trading_experience_learner import TradingExperienceLearner

learner = TradingExperienceLearner()

# 从回测中学习
summary = learner.learn_from_backtest(backtest_result, price_data)

# 生成学习报告
report = learner.generate_learning_report()
```

### 知识库查询
```python
kb = learner.kb
print(kb.get_summary())  # 查看知识库状态
```

---

## 📊 下一步行动

### 本周任务
- [ ] 实现多指标共振策略（MA+RSI+MACD+Volume）
- [ ] 添加动态止损机制
- [ ] 对比实验：新策略 vs 旧策略

### 本月任务
- [ ] 用户注册Signal Arena获取API Key
- [ ] 执行真实模拟交易
- [ ] 设置钉钉自动汇报

### 持续任务
- [ ] 每次交易后记录经验教训
- [ ] 每月回顾并优化策略
- [ ] 扩充知识库至10+条规则

---

## 💡 使用技巧

### 快速测试连接
```bash
cd lobster-network/domains/stock_prediction
python3 examples/quick_start.py YOUR_API_KEY
```

### 从回测中学习
```bash
python3 examples/learn_from_backtest.py
```

### 查看知识库
```python
from trading_experience_learner import TradingKnowledgeBase
kb = TradingKnowledgeBase()
print(kb.get_summary())
```

---

## ⚠️ 重要提醒

1. **虚拟资金≠无风险** - 规则与实盘一致，需严肃对待
2. **历史不代表未来** - 回测结果仅供参考
3. **风险控制第一** - 宁可错过，不可重伤
4. **持续学习进化** - 市场在变，策略也要变

---

## 📖 详细文档

- [Signal Arena集成指南](SIGNAL_ARENA_INTEGRATION.md)
- [经验学习总结](TRADING_EXPERIENCE_SUMMARY.md)
- [开发日志](DEVELOPMENT_LOG.md)

---

**🚀 让经验驱动交易，让学习创造价值！**
