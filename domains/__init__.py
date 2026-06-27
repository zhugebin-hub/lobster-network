#!/usr/bin/env python3
"""
小龙虾网络 - 领域模块注册

导出所有可用的领域模块
"""

# 围棋训练系统
try:
    from .go.trainers import *
except ImportError:
    pass

# 海报设计系统
try:
    from .poster.generator import *
except ImportError:
    pass

# A股预测系统
try:
    from .stock_prediction import StockPredictor
    from .stock_prediction.analysts import (
        TechnicalAnalyst,
        FundamentalAnalyst, 
        SentimentAnalyst
    )
    from .stock_prediction.trainers import StockPredictionTrainer
except ImportError:
    pass

__all__ = [
    # Go domain
    # Poster domain
    # Stock prediction domain
    "StockPredictor",
    "TechnicalAnalyst",
    "FundamentalAnalyst",
    "SentimentAnalyst", 
    "StockPredictionTrainer",
]
