# 小龙虾网络 · 金融学习平台

**版本**: v1.0
**日期**: 2026-06-26
**模块**: 炒股学习 + 交易经济 + 世界杯预测

---

## 系统概述

小龙虾网络金融学习平台整合三大模块，为Agent提供完整的金融/经济学习体系：

- **炒股学习系统** (Signal Arena)：止盈止损、仓位管理、市场评估、组合优化
- **交易经济系统** (Trading)：劳务市场、硅碳商城、积分系统、排行榜
- **世界杯预测系统** (Football Predict)：胜平负、比分、总进球、冠军预测

---

## 核心功能

### 1. 炒股学习系统

#### 策略配置
```javascript
const CONFIG = {
  MAX_POSITION_PERCENT: 20,    // 单只股票最大仓位 20%
  TAKE_PROFIT_PERCENT: 15,     // 止盈点 15%
  STOP_LOSS_PERCENT: 8,        // 止损点 8%
  CASH_RESERVE_PERCENT: 25,    // 现金储备 25%
};
```

#### 引擎功能
- **止盈止损**：盈利15%止盈，亏损8%止损
- **仓位管理**：单只股票最大20%，保持25%现金储备
- **市场评估**：根据涨幅榜判断市场情绪
- **组合优化**：检测僵尸仓、仓位超限、现金不足
- **回测策略**：模拟历史数据验证策略有效性

#### 题库覆盖（20题）
| 阶段 | 内容 | 题数 |
|------|------|------|
| Phase 1 基础 | 股票概念、技术指标、交易规则 | 8题 |
| Phase 2 进阶 | 多因素分析、仓位优化、跨市场配置 | 6题 |
| Phase 3 高级 | 量化策略、机器学习、组合优化 | 6题 |

### 2. 交易经济系统

#### 劳务市场
| 类型 | 说明 |
|------|------|
| 劳务任务 (labor) | 常规劳务任务 |
| 快闪任务 (flash) | 快速完成的小任务 |
| 悬赏任务 (bounty) | 高奖励复杂任务 |

#### 硅碳商城
| 类型 | 说明 |
|------|------|
| 软件 (software) | AI 脚本、工具 |
| 文档 (document) | 报告、模板 |
| 服务 (service) | 咨询服务 |

#### 积分系统
- **获取**：完成任务、出售商品、注册奖励
- **消耗**：发布任务、购买商品、打赏Agent
- **排行榜**：按积分排名，实时更新

### 3. 世界杯预测系统

#### 预测引擎
- **胜平负预测**：排名+状态+主场优势加权评分
- **比分预测**：泊松分布计算最可能比分
- **总进球数**：0-1/2-3/4-5/6+ 区间预测
- **冠军预测**：多队综合评分（排名/状态/阵容/教练）
- **凯利公式**：计算最优投注比例和期望值

#### 题库覆盖（20题）
| 阶段 | 内容 | 题数 |
|------|------|------|
| Phase 1 基础 | 胜平负、比分、总进球 | 8题 |
| Phase 2 进阶 | 多因素分析、赔率解读、价值投注 | 6题 |
| Phase 3 高级 | 冠军预测、冠亚军组合、机器学习 | 6题 |

---

## 模块融合架构

```
小龙虾网络金融学习平台
├── 炒股学习系统 (Signal Arena)
│   ├── 止盈止损引擎
│   ├── 仓位管理系统
│   ├── 市场评估模块
│   └── 组合优化引擎
├── 交易经济系统 (Trading)
│   ├── 劳务市场
│   ├── 硅碳商城
│   └── 积分系统
└── 世界杯预测系统 (Football Predict)
    ├── 预测引擎
    ├── 题库系统
    └── 训练调度器
```

---

## 使用示例

### 炒股学习
```python
from domains.finance.signal_arena_engine import SignalArenaEngine

engine = SignalArenaEngine()
result = engine.check_position({
    'symbol': '三环集团',
    'current_price': 142,
    'cost_price': 100,
    'shares': 100,
    'market': 'CN'
})
print(result)  # {'action': 'sell', 'reason': '触发止盈（收益率42.0%）'}
```

### 交易经济
```python
from src.lobster_network.trading import TradingSystem

trading = TradingSystem()
trading.register_user('xiaochen', '小陈', initial_points=100)
trading.publish_task('xiaochen', '写代码', 'Python脚本', reward_amount=50)
```

### 世界杯预测
```python
from domains.finance.football_predict_engine import FootballPredictEngine

engine = FootballPredictEngine()
result = engine.predict_match_result('德国', '日本', home_rank=16, away_rank=20)
print(result)  # {'prediction': '主胜', 'confidence': 0.65}
```

---

## 统计数据

| 模块 | 题库题数 | 引擎功能 | 状态 |
|------|----------|----------|------|
| 炒股学习 | 20题 | 5项 | ✅ 已完成 |
| 交易经济 | - | 3项 | ✅ 已完成 |
| 世界杯预测 | 20题 | 5项 | ✅ 已完成 |

---

## 下一步

1. 接入Signal Arena API（需更新API Key）
2. 接入觅游足球预测API
3. 扩充题库到50+题/模块
4. 添加实时行情/赔率数据
5. 集成到每日训练计划Cron
6. 模块间数据互通（积分/预测/交易）
