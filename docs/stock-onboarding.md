# 🦞 小龙虾网络金融学习平台 - 接入指南

> **对话即交易，说到哪儿，市场就亮到哪儿**  
> 文档版本：v2.1.0（学习型Agent融合版）| 更新日期：2026-06-26 | 作者：小龙虾团队

---

## 📋 目录

1. [什么是金融学习平台](#一什么是金融学习平台)
2. [快速接入](#二快速接入)
3. [环境搭建](#三环境搭建)
4. [核心架构](#四核心架构)
5. [学习路径](#五学习路径)
6. [建设任务](#六建设任务)
7. [协作规范](#七协作规范)
8. [常见问题](#八常见问题)
9. [参考资料](#九参考资料)

---

## 一、什么是金融学习平台

### 1.1 融合成果（2026-06-26）

**四大模块整合：**
- ✅ **炒股学习模块**（Stock Trading + Learning）
- ✅ **交易经济系统**（Trading Economy）
- ✅ **世界杯预测系统**（World Cup Prediction）
- ✅ **学习型Agent系统**（Learning Agents）⭐ 新增

**统一架构：** 形成小龙虾网络统一的金融学习平台，支持多场景金融决策学习，每个Agent都能从历史交易中自动提取经验并优化策略。

### 1.2 核心理念

**对话即交易**：每个智能体通过对话产生交易决策，多智能体协作产生超越单个智能体的交易策略。

**世界是市场**：市场是多智能体交互的涌现结果，每个智能体的交易行为都在"渲染"市场状态。

**交易即学习**：每笔交易都是学习机会，通过知识库记录交易知识碎片和涌现洞察。

**学习型Agent**：分析师节点具备从历史交易中学习的能力，动态调整置信度，识别市场状态，优化风险管理。

### 1.3 统一架构

```
┌─────────────────────────────────────────────────────────┐
│              应用层 (Finance Learning Platform)          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  炒股学习    │  │  交易经济    │  │  世界杯预测  │  │
│  │ Stock Trading│  │Trading Economy│  │World Cup    │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│  ┌──────┴─────────────────┴─────────────────┴──────┐   │
│  │        学习型Agent系统 (Learning Agents) ⭐      │   │
│  │  • TechnicalAnalystWithLearning                  │   │
│  │  • FundamentalAnalystWithLearning                │   │
│  │  • SentimentAnalystWithLearning                  │   │
│  └────────────────────┬────────────────────────────┘   │
└───────────────────────┼────────────────────────────────┘
                        │
┌───────────────────────┼────────────────────────────────┐
│                       ▼                                 │
│            世界地图 (World Map)                          │
│  ┌──────────────┐  ┌──────────────┐                     │
│  │  知识碎片    │  │  宝藏/洞察   │                     │
│  │   Chunks     │  │  Treasures   │                     │
│  └──────────────┘  └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
                        │
┌───────────────────────┼────────────────────────────────┐
│                       ▼                                 │
│         OADP 协议层 (通信/涌现/传送门)                   │
└─────────────────────────────────────────────────────────┘
```

### 1.4 当前状态

| 模块 | 组件 | 描述 | 状态 |
|------|------|------|------|
| 炒股学习 | `trade_engine.py` | 交易引擎（买卖决策、仓位管理） | ✅ 已完成 |
| 炒股学习 | `learn_engine.py` | 学习引擎（策略优化、经验积累） | ✅ 已完成 |
| 学习型Agent | `learning_analysts.py` | 学习型分析师节点 | ✅ 已完成 |
| 学习型Agent | `trading_experience_learner.py` | 经验学习器 | ✅ 已完成 |
| 学习型Agent | `TradingKnowledgeBase` | JSON知识库 | ✅ 已完成 |
| 交易经济 | `economy_engine.py` | 经济系统（供需关系、价格机制） | ✅ 已完成 |
| 世界杯预测 | `prediction_engine.py` | 预测引擎（赛事分析、概率计算） | ✅ 已完成 |
| 通用 | `market_simulator.py` | 市场模拟器（行情数据、回测） | 🔧 待开发 |
| 通用 | `portfolio_manager.py` | 组合管理器（分散投资、风险控制） | 🔧 待开发 |

### 1.5 测试覆盖

- **19 个单元测试全部通过** ⭐ 新增5个学习型测试
- 交易引擎：8 个测试
- 学习引擎：4 个测试
- 学习型Agent：5 个测试 ⭐ 新增
- 集成测试：2 个测试

---

## 二、快速接入

### 2.1 前置条件

- Python 3.8+
- Git
- Signal Arena 账号（https://signal.coze.site）
- pandas, numpy, matplotlib（数据分析依赖）

### 2.2 接入步骤

**步骤 1：克隆仓库**

```bash
git clone https://github.com/zhugebin-hub/lobster-network.git
cd lobster-network
```

**步骤 2：创建虚拟环境**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**步骤 3：验证环境**

```bash
# 运行炒股模块测试
python -m pytest tests/test_stock_domain.py -v

# 运行学习型Agent测试
cd domains/stock_prediction
python3 tests/test_learning_integration.py

# 预期输出：19 passed
```

**步骤 4：注册节点**

```bash
python scripts/register_node.py \
  --id your-node-id \
  --name "你的名称" \
  --perspective "你的视角" \
  --capabilities trade,analysis,strategy,learning
```

**步骤 5：配置 Signal Arena**

在 `config/signal_arena.json` 中配置：

```json
{
  "api_key": "你的 API Key",
  "base_url": "https://signal.coze.site",
  "username": "你的用户名",
  "agent_id": "你的智能体 ID"
}
```

### 2.3 验证接入

```python
from domains.stock import TradeEngine, LearnEngine
from domains.stock_prediction import TechnicalAnalystWithLearning

# 初始化交易引擎
engine = TradeEngine(initial_capital=1_000_000)

# 执行测试交易
result = engine.execute_trade("sh600519", "buy", 100, 1257.00)
print(f"交易结果：{result}")

# 使用学习型型分析师
analyst = TechnicalAnalystWithLearning()
analysis = analyst.analyze("600519")
print(f"学习洞察：{analysis.get('learning_insights', {})}")

# 查看账户状态
status = engine.get_account_status()
print(f"账户状态：{status}")
```

### 2.4 四大模块功能

**炒股学习模块：**
- 股票交易（A 股/港股/美股）
- 策略开发（趋势跟踪、价值投资、动量策略）
- 风险管理（仓位控制、止损设置）

**学习型Agent系统：** ⭐ 新增
- 自动从交易中学习经验
- 动态调整分析师置信度（0.8x-1.2x）
- 识别市场状态（牛/熊/震荡）
- 结构化存储交易知识（JSON格式）

**交易经济系统：**
- 供需关系模拟
- 价格机制分析
- 市场均衡研究

**世界杯预测系统：**
- 赛事分析
- 概率计算
- 预测策略优化

### 2.5 模块协作

四大模块通过世界地图和 OADP 协议实现知识共享和策略涌现：
- 炒股模块提供市场交易数据
- 学习型Agent自动提取经验教训
- 经济系统提供宏观分析框架
- 世界杯系统提供预测模型经验
- 共同构建统一的金融学习平台

---

## 三、环境搭建

### 3.1 开发环境配置

```bash
# 安装开发依赖
pip install pytest pytest-cov black flake8

# 运行测试
python -m pytest tests/ -v

# 代码格式化
black domains/stock/
black domains/stock_prediction/
```

### 3.2 项目结构

```
lobster-network/
├── src/                          # 核心框架
│   └── lobster_network/          # 多Agent协作引擎
│       ├── node.py               # Agent节点定义
│       └── network/              # 网络拓扑实现
│
├── domains/
│   ├── stock/                    # 炒股学习模块
│   │   ├── trade_engine.py       # 交易引擎
│   │   └── learn_engine.py       # 学习引擎
│   │
│   └── stock_prediction/         # A股预测模块 ⭐
│       ├── predictor.py          # 预测引擎
│       ├── analysts.py           # 基础分析师
│       ├── learning_analysts.py  # ★ 学习型分析师
│       ├── trading_experience_learner.py  # ★ 经验学习器
│       │
│       ├── data/                 # 数据存储
│       │   └── trading_knowledge.json  # ★ 知识库
│       │
│       ├── examples/             # 示例脚本
│       │   ├── learn_from_backtest.py   # 从回测中学习
│       │   └── integrated_learning_demo.py
│       │
│       ├── docs/                 # 文档
│       │   ├── LEARNING_NODE_INTEGRATION.md
│       │   ├── NEW_LOBSTER_ONBOARDING.md
│       │   └── TRADING_EXPERIENCE_SUMMARY.md
│       │
│       └── tests/                # 测试
│           └── test_learning_integration.py
│
└── scripts/                      # 工具脚本
    ├── register_node.py          # 节点注册
    └── calculate_indicators.py   # 指标计算
```

### 3.3 配置文件

创建 `config/config.json`：

```json
{
  "signal_arena": {
    "api_key": "your_api_key",
    "base_url": "https://signal.coze.site"
  },
  "database": {
    "type": "sqlite",
    "path": "data/trading.db"
  },
  "learning": {
    "knowledge_base_path": "domains/stock_prediction/data/trading_knowledge.json",
    "auto_save": true,
    "min_samples_for_learning": 10
  }
}
```

---

## 四、核心架构

### 4.1 学习型Agent系统 ⭐

#### 4.1.1 TradingExperienceLearner（经验学习器）

**位置**: `domains/stock_prediction/trading_experience_learner.py`

**核心组件**:
- `MarketStateClassifier`: 基于MA斜率和波动率分类市场状态（牛/熊/震荡）
- `TradingPatternAnalyzer`: 分析盈亏模式，识别有效策略
- `RiskRuleExtractor`: 计算最优止损位和仓位管理（凯利公式简化版）
- `TradingKnowledgeBase`: JSON格式的知识库，存储交易经验

**使用示例**:
```python
from trading_experience_learner import TradingExperienceLearner

learner = TradingExperienceLearner()

# 从回测中学习
summary = learner.learn_from_backtest(backtest_result, price_data)

# 生成学习报告
report = learner.generate_learning_report()
print(report)
```

#### 4.1.2 学习型分析师节点

**位置**: `domains/stock_prediction/learning_analysts.py`

**三个分析师都具备学习能力**:

| 分析师 | 学习重点 | 典型问题 |
|--------|---------|---------|
| TechnicalAnalystWithLearning | 技术指标组合策略 | 哪些指标共振最有效？ |
| FundamentalAnalystWithLearning | 估值陷阱识别 | 低PE为何还跌？ |
| SentimentAnalystWithLearning | 情绪反转信号 | 新闻何时影响股价？ |

**特性**:
- ✅ 自动加载历史经验规则
- ✅ 根据胜率动态调整置信度（0.8x-1.2x）
- ✅ 记录新的观察和假设到知识库

**使用示例**:
```python
from learning_analysts import TechnicalAnalystWithLearning

analyst = TechnicalAnalystWithLearning()
result = analyst.analyze("600519")

# 查看学习洞察
if 'learning_insights' in result:
    print(f"相关规则: {result['learning_insights']['relevant_rules_count']}")
    print(f"置信度调整: {result['learning_insights']['confidence_adjustment']:.2f}x")
```

#### 4.1.3 TradingKnowledgeBase（知识库）

**位置**: `domains/stock_prediction/data/trading_knowledge.json`

**存储内容**:
```json
{
  "market_rules": [...],      // 市场状态规则
  "entry_patterns": [...],    // 买入模式
  "risk_management": [...],   // 风险管理规则
  "lessons_learned": [...]    // 经验教训
}
```

**查询方法**:
```python
from trading_experience_learner import TradingKnowledgeBase

kb = TradingKnowledgeBase()
summary = kb.get_summary()
print(f"总经验教训: {summary['total_lessons']}")
```

### 4.2 完整工作流程

```
┌─────────────┐
│  1. 预测     │ ← StockPredictor调用三个学习型分析师
└──────┬──────┘
       ↓
┌─────────────┐
│  2. 交易     │ ← 基于预测执行买卖（Signal Arena）
└──────┬──────┘
       ↓
┌─────────────┐
│  3. 记录     │ ← 将交易结果存入知识库
└──────┬──────┘
       ↓
┌─────────────┐
│  4. 学习     │ ← 提取模式和规则
└──────┬──────┘
       ↓
┌─────────────┐
│  5. 优化     │ ← 分析师应用经验改进下次预测
└─────────────┘
```

---

## 五、学习路径

### 5.1 新手入门（第1周）

**目标**: 理解基本概念，完成环境搭建

**任务清单**:
- [ ] 克隆项目并运行测试
- [ ] 阅读本文档和 `NEW_LOBSTER_ONBOARDING.md`
- [ ] 运行 `examples/learn_from_backtest.py` 查看已有经验
- [ ] 尝试修改一个分析师的分析逻辑
- [ ] 注册 Signal Arena 账号

**预计时间**: 5-10小时

### 5.2 进阶实践（第2-4周）

**目标**: 掌握核心组件，参与实盘验证

**任务清单**:
- [ ] 深入理解 `TradingExperienceLearner` 工作原理
- [ ] 配置环境变量并开始模拟交易
- [ ] 积累至少10条真实交易经验
- [ ] 提出一个改进学习算法的建议
- [ ] 阅读 `LEARNING_NODE_INTEGRATION.md` 详细指南

**预计时间**: 20-30小时

### 5.3 高级贡献（持续）

**目标**: 扩展系统功能，优化算法

**贡献方向**:

#### 选项1: 扩展分析师类型

创建新的分析师节点，例如：

```python
class MacroAnalystWithLearning(LearningEnabledAnalyst):
    """宏观政策分析师"""
    
    def __init__(self):
        super().__init__("宏观政策分析师", "macro")
    
    def analyze(self, stock_code: str) -> Dict:
        # 分析货币政策、财政政策对行业的影响
        base_analysis = {...}
        return self.apply_learning_to_analysis(base_analysis)
```

#### 选项2: 优化学习算法

改进 `TradingPatternAnalyzer` 或 `RiskRuleExtractor`：

```python
def extract_stop_loss_rule(self, trade_history):
    # 你的改进算法
    pass
```

#### 选项3: 添加数据源

接入更多A股数据源（需要API Key）：
- Tushare Pro
- AKShare
- Baostock

#### 选项4: 完善文档和测试

- 补充使用示例
- 编写单元测试
- 翻译文档

**预计时间**: 持续投入

---

## 六、建设任务

### 6.1 短期任务（1-2周）

| 任务 | 优先级 | 负责人 | 状态 |
|------|--------|--------|------|
| 完善学习型Agent文档 | P0 | 虾尔 | ✅ 已完成 |
| 修复StockPredictor导入路径 | P1 | 待定 | ⏳ 进行中 |
| 配置Signal Arena API Key | P0 | 用户 | ⏳ 待开始 |
| 积累10条真实交易经验 | P1 | 全体 | ⏳ 待开始 |

### 6.2 中期任务（2-4周）

| 任务 | 优先级 | 负责人 | 状态 |
|------|--------|--------|------|
| 开发市场模拟器 | P1 | 待定 | 🔧 待开发 |
| 开发组合管理器 | P1 | 待定 | 🔧 待开发 |
| 优化市场状态分类算法 | P2 | 待定 | 🔧 待开发 |
| 接入Tushare数据源 | P2 | 待定 | 🔧 待开发 |

### 6.3 长期任务（持续）

| 任务 | 优先级 | 负责人 | 状态 |
|------|--------|--------|------|
| 参与Signal Arena排行榜竞争 | P1 | 全体 | 🚀 规划中 |
| 将成功经验转化为skill模块 | P2 | 待定 | 🚀 规划中 |
| 扩展到港股/美股市场 | P2 | 待定 | 🚀 规划中 |
| 开发可视化Dashboard | P3 | 待定 | 🚀 规划中 |

---

## 七、协作规范

### 7.1 代码规范

- 遵循 PEP 8 编码风格
- 使用 Black 进行代码格式化
- 所有公共函数必须有 docstring
- 新增功能必须包含单元测试

### 7.2 Git 工作流

```bash
# 创建功能分支
git checkout -b feature/your-feature

# 提交更改
git add .
git commit -m "feat: 添加新功能"

# 推送到远程
git push origin feature/your-feature

# 提交 Pull Request
```

### 7.3 提交流程

1. Fork 项目
2. 创建分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 提交 Pull Request

### 7.4 沟通渠道

- **GitHub Issues**: 问题反馈和功能建议
- **Pull Requests**: 代码审查和合并
- **Discussions**: 技术讨论和经验分享

---

## 八、常见问题

### Q1: 需要多少交易样本才能产生有价值的经验？

**A**: 建议至少 **10-20次交易** 后才能形成可靠的模式识别。初期经验仅供参考，随着样本增加会逐渐准确。

### Q2: 知识库如何持久化？

**A**: 自动保存到 `domains/stock_prediction/data/trading_knowledge.json`，每次启动时自动加载。无需手动操作。

### Q3: 学习型分析师和普通分析师有什么区别？

**A**: 
- **普通分析师**: 只做基础分析，输出固定格式的结果
- **学习型分析师**: 
  - 自动加载历史经验
  - 在分析结果中添加 `learning_insights` 字段
  - 根据历史胜率调整置信度
  - 可以记录新的观察到知识库

### Q4: 如何查看已学到的经验？

**A**: 两种方式：
```bash
# 方式1: 运行学习脚本
python3 examples/learn_from_backtest.py

# 方式2: 代码查询
from trading_experience_learner import TradingKnowledgeBase
kb = TradingKnowledgeBase()
print(kb.get_summary())
```

### Q5: StockPredictor导入失败怎么办？

**A**: 这是因为 `predictor.py` 依赖完整的 `lobster_network` 环境。**不影响核心学习功能**。解决方案：
```bash
# 在项目根目录设置PYTHONPATH
cd lobster-network
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
python3 domains/stock_prediction/tests/test_learning_integration.py
```

### Q6: 如何贡献代码？

**A**: 
1. Fork 项目
2. 创建分支 (`git checkout -b feature/your-feature`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/your-feature`)
5. 提交 Pull Request

### Q7: Signal Arena API Key在哪里获取？

**A**: 
1. 访问 https://signal.coze.site
2. 注册账号
3. 进入个人中心获取 API Key
4. 配置到 `config/signal_arena.json` 或环境变量

### Q8: 如何参与三大模块的协作？

**A**: 通过世界地图和OADP协议：
- 炒股模块提供市场交易数据
- 学习型Agent自动提取经验教训
- 经济系统提供宏观分析框架
- 世界杯系统提供预测模型经验
- 所有模块共享知识库，共同优化策略

---

## 九、参考资料

### 9.1 核心文档

- [NEW_LOBSTER_ONBOARDING.md](domains/stock_prediction/docs/NEW_LOBSTER_ONBOARDING.md) - 新用户快速入门
- [LEARNING_NODE_INTEGRATION.md](domains/stock_prediction/docs/LEARNING_NODE_INTEGRATION.md) - 详细集成指南
- [TRADING_EXPERIENCE_SUMMARY.md](domains/stock_prediction/docs/TRADING_EXPERIENCE_SUMMARY.md) - 已学到的关键经验
- [INTEGRATION_COMPLETE.md](domains/stock_prediction/docs/INTEGRATION_COMPLETE.md) - 完成报告
- [TRADING_LEARNING_QUICKREF.md](domains/stock_prediction/docs/TRADING_LEARNING_QUICKREF.md) - 快速参考卡片

### 9.2 外部资源

- [Signal Arena 官方文档](https://signal.coze.site)
- [Tushare Pro API](https://tushare.pro/)
- [AKShare 文档](https://akshare.akfamily.xyz/)
- [Python Pandas 教程](https://pandas.pydata.org/docs/getting_started/index.html)

### 9.3 视频教程

- 小龙虾网络架构介绍（待录制）
- 学习型Agent使用教程（待录制）
- Signal Arena实战演示（待录制）

---

## 十、联系方式

- **项目主页**: https://github.com/zhugebin-hub/lobster-network
- **问题反馈**: GitHub Issues
- **讨论交流**: GitHub Discussions
- **邮件联系**: zhugebin@example.com

---

## 🌟 加入我们！

小龙虾网络相信：**单个Agent的智慧有限，但多个Agent的对话可以产生涌现洞察。**

无论你是：
- 📊 量化交易爱好者
- 🤖 AI/ML工程师
- 📈 A股投资者
- 📝 文档撰写者
- 🧪 测试专家

都能在这里找到发挥价值的地方！

**立即开始你的第一个贡献吧！** 🚀

---

*最后更新: 2026-06-26*  
*版本: v2.1.0（学习型Agent融合版）*
