#!/usr/bin/env python3
"""
🦞 小龙虾网络 - A股预测学习模块

基于对话即创造理论的A股市场预测系统
通过多Agent交叉编译，生成超越单一视角的市场洞察

核心能力:
- 多维度市场分析（技术面、基本面、情绪面）
- 历史数据回测与模式识别
- 多Agent协作预测
- 涌现检测与宝藏解锁
- **交易经验学习**（新增）：从历史交易中自动提取可复用规则
"""

__version__ = "0.2.0"  # 升级版本号，标记学习型功能加入

from .predictor import StockPredictor
from .analysts import TechnicalAnalyst, FundamentalAnalyst, SentimentAnalyst

# 导入学习型分析师节点
try:
    from .learning_analysts import (
        TechnicalAnalystWithLearning,
        FundamentalAnalystWithLearning,
        SentimentAnalystWithLearning
    )
except ImportError:
    # 如果learning_analysts尚未创建，使用原始类作为后备
    TechnicalAnalystWithLearning = TechnicalAnalyst
    FundamentalAnalystWithLearning = FundamentalAnalyst
    SentimentAnalystWithLearning = SentimentAnalyst

# 导入经验学习器
try:
    from .trading_experience_learner import (
        TradingExperienceLearner,
        TradingKnowledgeBase,
        MarketStateClassifier,
        RiskRuleExtractor
    )
except ImportError:
    pass  # 可选组件，不影响基本功能

__all__ = [
    # 核心预测器
    "StockPredictor",
    
    # 基础分析师
    "TechnicalAnalyst",
    "FundamentalAnalyst", 
    "SentimentAnalyst",
    
    # 学习型分析师（新增）
    "TechnicalAnalystWithLearning",
    "FundamentalAnalystWithLearning",
    "SentimentAnalystWithLearning",
    
    # 经验学习组件（新增）
    "TradingExperienceLearner",
    "TradingKnowledgeBase",
    "MarketStateClassifier",
    "RiskRuleExtractor",
]
