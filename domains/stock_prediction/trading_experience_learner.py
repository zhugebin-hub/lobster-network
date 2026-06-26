#!/usr/bin/env python3
"""
炒股经验学习器 - Trading Experience Learner

从历史回测和模拟交易中提取可复用的交易经验，构建结构化知识库。

核心功能：
1. 策略性能分析 - 识别成功/失败模式
2. 市场状态分类 - 牛市/熊市/震荡市特征
3. 风险规则提炼 - 止损、仓位管理原则
4. 经验知识存储 - 结构化的交易规则库
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
from pathlib import Path


class MarketStateClassifier:
    """市场状态分类器"""
    
    @staticmethod
    def classify_market(df: pd.DataFrame) -> str:
        """
        根据价格走势分类市场状态
        
        Returns:
            'bull' (牛市), 'bear' (熊市), 'sideways' (震荡市)
        """
        if len(df) < 20:
            return 'unknown'
        
        # 计算20日均线斜率
        ma20 = df['close'].rolling(20).mean().dropna()
        if len(ma20) < 10:
            return 'unknown'
        
        # 线性回归斜率
        x = np.arange(len(ma20))
        slope = np.polyfit(x, ma20.values, 1)[0]
        
        # 计算波动率
        returns = df['close'].pct_change().dropna()
        volatility = returns.std()
        
        # 分类逻辑
        if slope > 0.5:  # 明显上升趋势
            return 'bull'
        elif slope < -0.5:  # 明显下降趋势
            return 'bear'
        elif volatility < 0.02:  # 低波动
            return 'sideways'
        else:
            return 'volatile'


class TradingPatternAnalyzer:
    """交易模式分析器"""
    
    @staticmethod
    def analyze_win_patterns(trades: List[Dict]) -> Dict:
        """
        分析盈利交易的共同特征
        
        Args:
            trades: 交易记录列表，每个包含 entry_price, exit_price, 
                   holding_days, market_state, indicators等
            
        Returns:
            盈利模式总结
        """
        profitable = [t for t in trades if t.get('profit', 0) > 0]
        losing = [t for t in trades if t.get('profit', 0) <= 0]
        
        if not profitable:
            return {'status': 'no_profitable_trades'}
        
        # 统计特征
        avg_holding_profitable = np.mean([t.get('holding_days', 0) for t in profitable])
        avg_holding_losing = np.mean([t.get('holding_days', 0) for t in losing]) if losing else 0
        
        # 市场状态分布
        market_states = {}
        for t in profitable:
            state = t.get('market_state', 'unknown')
            market_states[state] = market_states.get(state, 0) + 1
        
        return {
            'total_profitable': len(profitable),
            'total_losing': len(losing),
            'win_rate': len(profitable) / max(len(trades), 1),
            'avg_profit_per_trade': np.mean([t.get('profit', 0) for t in profitable]),
            'avg_holding_days_profitable': round(avg_holding_profitable, 1),
            'avg_holding_days_losing': round(avg_holding_losing, 1),
            'best_market_states': market_states,
            'key_insights': []
        }
    
    @staticmethod
    def extract_entry_conditions(df: pd.DataFrame, signals: List[int]) -> Dict:
        """
        提取买入信号的技术指标特征
        
        Args:
            df: 包含技术指标的DataFrame
            signals: 买入信号索引列表（1表示买入）
            
        Returns:
            买入时的指标特征统计
        """
        if not signals:
            return {'status': 'no_signals'}
        
        signal_rows = df.iloc[signals]
        
        return {
            'count': len(signals),
            'avg_rsi': round(signal_rows.get('rsi', pd.Series()).mean(), 2) if 'rsi' in df.columns else None,
            'avg_macd': round(signal_rows.get('macd', pd.Series()).mean(), 4) if 'macd' in df.columns else None,
            'price_vs_ma20': round((signal_rows['close'] / signal_rows.get('ma20', signal_rows['close']) - 1).mean() * 100, 2) if 'ma20' in df.columns else None,
            'avg_volume_ratio': round(signal_rows['volume'].mean() / df['volume'].mean(), 2) if 'volume' in df.columns else None
        }


class RiskRuleExtractor:
    """风险规则提取器"""
    
    @staticmethod
    def calculate_optimal_stop_loss(equity_curve: pd.Series, 
                                   max_drawdown_tolerance: float = 0.15) -> Dict:
        """
        根据历史回撤数据计算最优止损位
        
        Args:
            equity_curve: 权益曲线
            max_drawdown_tolerance: 最大可承受回撤
            
        Returns:
            止损建议
        """
        # 计算滚动最大回撤
        rolling_max = equity_curve.expanding().max()
        drawdowns = (equity_curve - rolling_max) / rolling_max
        
        # 统计回撤分布
        significant_drawdowns = drawdowns[drawdowns < -0.05]  # 超过5%的回撤
        
        if len(significant_drawdowns) == 0:
            return {
                'recommended_stop_loss': 0.10,  # 默认10%
                'confidence': 'low',
                'reason': '历史数据中无显著回撤'
            }
        
        # 找到最常见的回撤幅度
        avg_significant_dd = abs(significant_drawdowns.mean())
        
        # 建议在平均显著回撤之前止损
        recommended = min(avg_significant_dd * 0.8, max_drawdown_tolerance)
        
        return {
            'recommended_stop_loss': round(recommended, 3),
            'avg_significant_drawdown': round(abs(avg_significant_dd), 3),
            'max_historical_drawdown': round(abs(drawdowns.min()), 3),
            'confidence': 'high' if len(significant_drawdowns) > 5 else 'medium',
            'sample_size': len(significant_drawdowns)
        }
    
    @staticmethod
    def suggest_position_sizing(account_value: float, 
                               volatility: float,
                               risk_per_trade: float = 0.02) -> Dict:
        """
        基于账户规模和波动率建议仓位
        
        Args:
            account_value: 账户总值
            volatility: 标的波动率（日收益率标准差）
            risk_per_trade: 单笔交易风险比例（默认2%）
            
        Returns:
            仓位建议
        """
        # 凯利公式简化版
        # 假设胜率55%，盈亏比1.5:1
        win_rate = 0.55
        win_loss_ratio = 1.5
        
        kelly_fraction = win_rate - (1 - win_rate) / win_loss_ratio
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # 限制在0-25%
        
        # 保守起见，使用半凯利
        conservative_kelly = kelly_fraction / 2
        
        # 基于波动率调整
        if volatility > 0.03:  # 高波动
            adjustment = 0.5
        elif volatility < 0.015:  # 低波动
            adjustment = 1.2
        else:
            adjustment = 1.0
        
        final_position = conservative_kelly * adjustment
        
        return {
            'kelly_fraction': round(kelly_fraction, 3),
            'conservative_position': round(conservative_kelly, 3),
            'volatility_adjusted': round(final_position, 3),
            'max_capital_to_risk': round(account_value * risk_per_trade, 2),
            'recommended_shares_pct': round(final_position * 100, 1)
        }


class TradingKnowledgeBase:
    """交易知识库"""
    
    def __init__(self, storage_path: str = "domains/stock_prediction/data/trading_knowledge.json"):
        self.storage_path = Path(storage_path)
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self) -> Dict:
        """加载已有知识"""
        if self.storage_path.exists():
            import json
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'market_rules': [],
            'entry_patterns': [],
            'exit_rules': [],
            'risk_management': [],
            'lessons_learned': []
        }
    
    def add_market_rule(self, rule: Dict):
        """添加市场状态规则"""
        rule['timestamp'] = datetime.now().isoformat()
        self.knowledge['market_rules'].append(rule)
        self._save()
    
    def add_entry_pattern(self, pattern: Dict):
        """添加买入模式"""
        pattern['timestamp'] = datetime.now().isoformat()
        self.knowledge['entry_patterns'].append(pattern)
        self._save()
    
    def add_risk_rule(self, rule: Dict):
        """添加风险管理规则"""
        rule['timestamp'] = datetime.now().isoformat()
        self.knowledge['risk_management'].append(rule)
        self._save()
    
    def add_lesson(self, lesson: Dict):
        """添加经验教训"""
        lesson['timestamp'] = datetime.now().isoformat()
        self.knowledge['lessons_learned'].append(lesson)
        self._save()
    
    def _save(self):
        """保存知识库"""
        import json
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def get_summary(self) -> Dict:
        """获取知识库摘要"""
        lessons = self.knowledge.get('lessons_learned', [])
        return {
            'total_market_rules': len(self.knowledge['market_rules']),
            'total_entry_patterns': len(self.knowledge['entry_patterns']),
            'total_risk_rules': len(self.knowledge['risk_management']),
            'total_lessons': len(lessons),
            'last_updated': lessons[-1].get('timestamp', 'N/A') if lessons else 'N/A'
        }


class TradingExperienceLearner:
    """
    炒股经验学习器
    
    主类，整合所有分析组件，从回测和交易中自动学习经验
    """
    
    def __init__(self, knowledge_base_path: str = None):
        self.market_classifier = MarketStateClassifier()
        self.pattern_analyzer = TradingPatternAnalyzer()
        self.risk_extractor = RiskRuleExtractor()
        self.kb = TradingKnowledgeBase(knowledge_base_path or 
                                      "domains/stock_prediction/data/trading_knowledge.json")
    
    def learn_from_backtest(self, backtest_result: Dict, 
                           price_data: pd.DataFrame) -> Dict:
        """
        从回测结果中学习经验
        
        Args:
            backtest_result: 回测结果字典
            price_data: 价格数据DataFrame
            
        Returns:
            学习到的经验总结
        """
        lessons = []
        
        # 1. 分析市场状态
        market_state = self.market_classifier.classify_market(price_data)
        lessons.append(f"测试期间市场状态: {market_state}")
        
        # 2. 分析策略表现
        total_return = backtest_result.get('total_return', 0)
        max_dd = backtest_result.get('max_drawdown', 0)
        sharpe = backtest_result.get('sharpe_ratio', 0)
        
        if total_return < 0:
            lesson = {
                'type': 'strategy_failure',
                'context': f"在市场状态'{market_state}'下",
                'observation': f"策略总收益{total_return:.2%}，最大回撤{abs(max_dd):.2%}",
                'hypothesis': "简单均线策略在趋势市中可能滞后，需要更早的信号确认",
                'action_item': "尝试结合RSI或MACD提前入场"
            }
            self.kb.add_lesson(lesson)
            lessons.append(f"⚠️ 策略失效: {lesson['hypothesis']}")
        
        # 3. 提取风险规则
        if 'equity_curve' in backtest_result:
            stop_loss_advice = self.risk_extractor.calculate_optimal_stop_loss(
                backtest_result['equity_curve']
            )
            self.kb.add_risk_rule({
                'rule_type': 'stop_loss',
                'advice': stop_loss_advice,
                'source': 'backtest_analysis'
            })
            lessons.append(f"💡 止损建议: {stop_loss_advice['recommended_stop_loss']:.1%}")
        
        # 4. 总结关键洞察
        summary = {
            'market_state': market_state,
            'performance': {
                'total_return': total_return,
                'max_drawdown': max_dd,
                'sharpe_ratio': sharpe
            },
            'lessons_count': len(lessons),
            'knowledge_base_status': self.kb.get_summary()
        }
        
        return summary
    
    def generate_learning_report(self) -> str:
        """生成学习报告"""
        kb_summary = self.kb.get_summary()
        
        report = f"""
🦞 小龙虾网络 - 炒股经验学习报告
{'='*60}

📚 知识库状态
  市场规则: {kb_summary['total_market_rules']} 条
  买入模式: {kb_summary['total_entry_patterns']} 个
  风险规则: {kb_summary['total_risk_rules']} 条
  经验教训: {kb_summary['total_lessons']} 条
  最后更新: {kb_summary['last_updated']}

💡 最新经验教训:
"""
        
        recent_lessons = self.kb.knowledge['lessons_learned'][-5:]
        for i, lesson in enumerate(recent_lessons, 1):
            report += f"  {i}. [{lesson.get('type', 'general')}] {lesson.get('hypothesis', 'N/A')}\n"
        
        report += f"\n{'='*60}\n"
        report += "继续通过回测和实盘交易积累更多经验！\n"
        
        return report


if __name__ == '__main__':
    # 示例：创建学习器并生成报告
    learner = TradingExperienceLearner()
    print(learner.generate_learning_report())
