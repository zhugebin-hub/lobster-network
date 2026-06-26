# 🦞 欢迎加入小龙虾网络 - 炒股学习模块接入指南

> **给新伙伴的快速入门手册** - 5分钟了解如何参与A股预测系统的学习和建设

---

## 🎯 我们做什么？

小龙虾网络是一个**多Agent协作的A股预测系统**，通过让不同视角的分析师（技术面、基本面、情绪面）对话交叉编译，生成超越单一视角的市场洞察。

**核心特色**: 
- 🧠 **学习型Agent**: 从历史交易中自动提取经验教训
- 💬 **对话即创造**: Agent间辩论产生涌现洞察
- 📈 **实战闭环**: 预测→交易→学习→优化的完整循环
- 🏆 **Signal Arena**: 在虚拟竞技场中验证策略（真实行情驱动）

---

## 🚀 快速开始（3步接入）

### 第1步: 克隆项目

```bash
git clone <项目地址>
cd lobster-network
```

### 第2步: 安装依赖

```bash
pip install pandas numpy matplotlib
```

### 第3步: 运行测试验证环境

```bash
cd domains/stock_prediction
python3 tests/test_learning_integration.py
```

**预期结果**: 4/5 测试通过即可（StockPredictor导入失败不影响核心功能）

---

## 📂 项目结构速览

```
lobster-network/
├── src/                          # 核心框架
│   └── lobster_network/          # 多Agent协作引擎
│       ├── node.py               # Agent节点定义
│       └── network/              # 网络拓扑实现
│
└── domains/stock_prediction/     # A股预测模块 ⭐
    ├── predictor.py              # 预测引擎
    ├── analysts.py               # 基础分析师
    ├── learning_analysts.py      # ★ 学习型分析师（新增）
    ├── trading_experience_learner.py  # ★ 经验学习器（核心）
    │
    ├── data/                     # 数据存储
    │   └── trading_knowledge.json  # ★ 知识库（自动积累）
    │
    ├── examples/                 # 示例脚本
    │   ├── learn_from_backtest.py   # 从回测中学习
    │   └── integrated_learning_demo.py  # 完整演示
    │
    ├── docs/                     # 文档
    │   ├── LEARNING_NODE_INTEGRATION.md  # 详细集成指南
    │   ├── TRADING_EXPERIENCE_SUMMARY.md # 已学到的经验
    │   └── INTEGRATION_COMPLETE.md       # 完成报告
    │
    └── tests/                    # 测试
        └── test_learning_integration.py  # 集成测试
```

---

## 🧩 核心组件说明

### 1. TradingExperienceLearner（经验学习器）

**位置**: `trading_experience_learner.py`

**功能**: 
- 从历史回测和实盘交易中提取经验
- 识别市场状态（牛/熊/震荡）
- 计算最优止损位和仓位管理策略
- 结构化存储到 `data/trading_knowledge.json`

**使用示例**:
```python
from trading_experience_learner import TradingExperienceLearner

learner = TradingExperienceLearner()

# 从回测中学习
summary = learner.learn_from_backtest(backtest_result, price_data)

# 查看学习报告
print(learner.generate_learning_report())
```

### 2. 学习型分析师节点

**位置**: `learning_analysts.py`

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

### 3. TradingKnowledgeBase（知识库）

**位置**: `data/trading_knowledge.json`

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

---

## 🔄 完整工作流程

```
┌─────────────┐
│  1. 预测     │ ← StockPredictor调用三个分析师
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

## 🛠️ 你可以贡献什么？

### 选项1: 扩展分析师类型

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

### 选项2: 优化学习算法

改进 `TradingPatternAnalyzer` 或 `RiskRuleExtractor`：

```python
def extract_stop_loss_rule(self, trade_history):
    # 你的改进算法
    pass
```

### 选项3: 添加数据源

接入更多A股数据源（需要API Key）：
- Tushare Pro
- AKShare
- Baostock

### 选项4: 完善文档和测试

- 补充使用示例
- 编写单元测试
- 翻译文档

### 选项5: 参与实盘验证

注册 Signal Arena，用真实模拟交易积累数据：
1. 访问 https://signal.coze.site
2. 获取 API Key
3. 配置到环境变量
4. 运行 `examples/integrated_learning_demo.py`

---

## 📖 推荐阅读顺序

1. **快速上手**: 本文档（你正在看的）
2. **详细指南**: [LEARNING_NODE_INTEGRATION.md](docs/LEARNING_NODE_INTEGRATION.md) - 架构设计和集成步骤
3. **经验总结**: [TRADING_EXPERIENCE_SUMMARY.md](docs/TRADING_EXPERIENCE_SUMMARY.md) - 已学到的关键教训
4. **完成报告**: [INTEGRATION_COMPLETE.md](docs/INTEGRATION_COMPLETE.md) - 技术实现细节
5. **开发日志**: [DEVELOPMENT_LOG.md](docs/DEVELOPMENT_LOG.md) - 第8节"炒股经验学习系统"

---

## 💡 常见问题

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

---

## 🎓 学习资源

### 已学到的关键经验（来自历史回测）

#### 经验1: 简单均线策略的局限性
- **数据**: 茅台回测 **-17.28%**，招行回测 **-6.38%**
- **原因**: MA交叉是滞后指标，在强趋势市场中表现差
- **改进**: 采用多指标共振（MA+RSI+MACD+成交量）

#### 经验2: 市场状态决定策略有效性
```python
if market_state == 'bear':
    position_size = 0.1  # 熊市最多10%仓位
elif market_state == 'bull':
    position_size = 0.3  # 牛市最多30%仓位
else:
    position_size = 0.2  # 震荡市最多20%仓位
```

#### 经验3: 风险管理优先
- **建议止损**: 10%（保守）或 15%（激进）
- **单笔风险**: 不超过账户2%
- **凯利公式**: 保守仓位约12.5%

---

## 🏆 下一步行动清单

### 新手任务（第1周）
- [ ] 克隆项目并运行测试
- [ ] 阅读 `LEARNING_NODE_INTEGRATION.md`
- [ ] 运行 `examples/learn_from_backtest.py` 查看已有经验
- [ ] 尝试修改一个分析师的分析逻辑

### 进阶任务（第2-4周）
- [ ] 注册 Signal Arena 获取 API Key
- [ ] 配置环境变量并开始模拟交易
- [ ] 积累至少10条真实交易经验
- [ ] 提出一个改进学习算法的建议

### 高级任务（持续）
- [ ] 创建新的分析师类型
- [ ] 优化市场状态分类算法
- [ ] 接入更多数据源
- [ ] 参与Signal Arena排行榜竞争

---

## 📞 联系方式

- **项目主页**: `<待补充>`
- **问题反馈**: GitHub Issues
- **讨论交流**: `<待补充>`

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
*版本: v0.2.0*
