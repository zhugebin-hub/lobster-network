# A股预测学习模块

## 模块概述

基于小龙虾网络"对话即创造"理论的A股市场预测系统，通过多Agent交叉编译生成超越单一视角的市场洞察，并集成Signal Arena虚拟炒股平台实现自动交易。

## 架构设计

```
stock_prediction/
├── __init__.py              # 模块入口
├── predictor.py             # 核心预测引擎
├── analysts.py              # 分析师节点（技术/基本/情绪）
├── signal_arena_client.py   # Signal Arena API客户端
├── trainers/                # 训练器子模块
│   ├── __init__.py          # 回测框架与绩效评估
│   └── [trainer implementations]
├── examples/                # 使用示例
│   ├── basic_usage.py       # 基础用法
│   ├── run_backtest.py      # 回测演示
│   ├── signal_arena_report.py  # 定时汇报
│   └── quick_start.py       # 快速开始测试
├── data/                    # 数据存储
│   ├── 600519_贵州茅台.csv
│   ├── 000858_五粮液.csv
│   └── 600036_招商银行.csv
└── docs/                    # 文档
    ├── README.md            # 本文档
    ├── DEVELOPMENT_LOG.md   # 开发日志
    └── SIGNAL_ARENA_INTEGRATION.md  # Signal Arena集成指南
```

## 核心组件

### 1. StockPredictor (预测器)

整合三个分析师Agent的视角，通过对话产生涌现洞察：

- **技术面分析师**: K线形态、均线系统、技术指标
- **基本面分析师**: 财务报表、估值模型、行业地位  
- **情绪面分析师**: 新闻舆情、资金流向、板块轮动

### 2. 对话交叉编译机制

利用小龙虾网络的`dialogue()`方法，让不同视角的Agent进行深度对话，当认知差异超过阈值时触发"涌现"，解锁单人无法得出的新见解。

## 使用示例

```python
from lobster_network.domains.stock_prediction import StockPredictor

# 创建预测器
predictor = StockPredictor(emergence_threshold=0.6)

# 对贵州茅台进行5天预测
result = predictor.predict(
    stock_code="600519",
    stock_name="贵州茅台",
    days_ahead=5
)

# 查看结果
print(f"目标价位: {result['final_prediction']['target_price_range']}")
print(f"置信度: {result['final_prediction']['confidence']:.1%}")
print(f"建议操作: {result['final_prediction']['recommendation']}")
```

## 已完成功能

### 数据接入层 ✅
- ✅ 接入vertical-query技能获取A股历史K线数据
- ✅ 历史K线数据获取与存储（JSON转CSV）
- ✅ 技术指标计算脚本（MA、MACD、RSI、布林带）

### Signal Arena集成 ✅
- ✅ 完整API客户端封装 (signal_arena_client.py)
- ✅ 核心接口：home/stocks/trade/account/portfolio/leaderboard
- ✅ LobsterNetworkSignalTrader自动交易器
- ✅ 定时汇报脚本 (signal_arena_report.py)
- ✅ 快速开始测试脚本 (quick_start.py)
- ✅ 详细集成指南 (SIGNAL_ARENA_INTEGRATION.md)

## 待实现功能

### 数据接入层
- [ ] 实时A股行情接口
- [ ] 财务报表数据接口
- [ ] 新闻舆情数据源
- [ ] 资金流向数据

### 分析引擎
- [ ] K线形态识别算法
- [ ] 财务比率自动计算
- [ ] NLP情感分析模型
- [ ] 估值模型实现

### 训练器模块
- [ ] 策略优化器
- [ ] 参数调优工具
- [ ] 多策略回测框架

### 预测输出
- [ ] 目标价位区间计算
- [ ] 置信度量化模型
- [ ] 风险提示系统
- [ ] 止损止盈点建议

## 集成到小龙虾网络

在`lobster-network/domains/__init__.py`中注册本模块：

```python
from .stock_prediction import StockPredictor

__all__ = [
    # ... existing exports
    "StockPredictor",
]
```

## 开发路线图

**Phase 1 - 基础框架** ✅ 已完成
- ✅ 模块结构搭建
- ✅ 核心类定义
- ✅ Signal Arena API集成
- ✅ 数据接口对接（历史K线）
- ✅ 回测框架实现

**Phase 2 - 分析能力** ⏳ 进行中
- ✅ 技术指标计算脚本
- [ ] K线形态识别算法
- [ ] 基本面分析逻辑
- [ ] 情绪分析模型
- [ ] 实时行情接入

**Phase 3 - 预测优化**
- [ ] 机器学习模型集成
- [ ] 策略优化器
- [ ] 参数调优工具
- [ ] 多策略回测框架

**Phase 4 - 生产部署**
- [ ] 实时监控
- [ ] 自动化钉钉报告
- [ ] 风险预警系统
- [ ] 定时任务配置

## 注意事项

⚠️ **免责声明**: 本模块仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。

⚠️ **数据准确性**: 预测结果依赖于输入数据的质量和分析模型的准确性，实际使用时请确保数据源的可靠性。
