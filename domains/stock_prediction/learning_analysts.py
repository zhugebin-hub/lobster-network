#!/usr/bin/env python3
"""
学习型分析师节点 - 集成TradingExperienceLearner

三个分析师节点都具备从经验知识库中学习的能力：
- TechnicalAnalystWithLearning: 技术面分析师（学习技术指标组合策略）
- FundamentalAnalystWithLearning: 基本面分析师（学习估值陷阱识别）
- SentimentAnalystWithLearning: 情绪面分析师（学习情绪反转信号）
"""

from typing import Dict, List, Optional
from pathlib import Path
import sys

# 导入经验学习器
sys.path.insert(0, str(Path(__file__).parent))
from trading_experience_learner import TradingKnowledgeBase


class LearningEnabledAnalyst:
    """
    具备学习能力的分析师基类
    
    特性：
    1. 自动加载交易经验知识库
    2. 分析时参考历史经验教训
    3. 记录新的观察和假设到知识库
    """
    
    def __init__(self, name: str, specialty: str, knowledge_base_path: str = None):
        self.name = name
        self.specialty = specialty
        
        # 初始化知识库
        kb_path = knowledge_base_path or "domains/stock_prediction/data/trading_knowledge.json"
        self.kb = TradingKnowledgeBase(kb_path)
        
        # 加载相关经验规则
        self._load_relevant_rules()
    
    def _load_relevant_rules(self):
        """加载与当前分析师相关的经验规则"""
        self.relevant_rules = []
        
        # 根据分析师类型筛选相关规则
        for rule in self.kb.knowledge.get('market_rules', []):
            if rule.get('analyst_type') == self.specialty or rule.get('analyst_type') == 'all':
                self.relevant_rules.append(rule)
        
        for lesson in self.kb.knowledge.get('lessons_learned', []):
            if lesson.get('type', '').startswith(self.specialty):
                self.relevant_rules.append(lesson)
    
    def apply_learning_to_analysis(self, analysis_result: Dict) -> Dict:
        """
        将学习到的经验应用到分析结果中
        
        Args:
            analysis_result: 原始分析结果
            
        Returns:
            增强后的分析结果（包含经验建议）
        """
        enhanced = analysis_result.copy()
        
        # 添加经验建议
        if self.relevant_rules:
            enhanced['learning_insights'] = {
                'relevant_rules_count': len(self.relevant_rules),
                'key_lessons': [
                    rule.get('hypothesis', rule.get('observation', '')) 
                    for rule in self.relevant_rules[:3]  # 最多显示3条
                ],
                'confidence_adjustment': self._calculate_confidence_adjustment()
            }
        
        return enhanced
    
    def _calculate_confidence_adjustment(self) -> float:
        """
        根据历史经验计算置信度调整系数
        
        Returns:
            调整系数 (0.8-1.2)，基于历史胜率
        """
        lessons = self.kb.knowledge.get('lessons_learned', [])
        
        if not lessons:
            return 1.0  # 无历史数据，不调整
        
        # 统计成功/失败的经验
        successes = sum(1 for l in lessons if l.get('outcome') == 'success')
        total = len(lessons)
        
        if total == 0:
            return 1.0
        
        win_rate = successes / total
        
        # 胜率高则提高置信度，反之降低
        if win_rate > 0.6:
            return min(1.2, 1.0 + (win_rate - 0.5) * 0.4)
        elif win_rate < 0.4:
            return max(0.8, 1.0 - (0.5 - win_rate) * 0.4)
        else:
            return 1.0
    
    def record_observation(self, observation: Dict):
        """
        记录新的观察和假设到知识库
        
        Args:
            observation: 观察结果，包含：
                - type: 观察类型
                - context: 上下文
                - hypothesis: 假设
                - evidence: 证据
        """
        observation['analyst'] = self.name
        observation['specialty'] = self.specialty
        
        # 添加到知识库
        self.kb.add_lesson(observation)
        
        # 重新加载规则
        self._load_relevant_rules()


class TechnicalAnalystWithLearning(LearningEnabledAnalyst):
    """
    技术分析专家（带学习能力）
    
    学习重点：
    - 哪些技术指标组合最有效
    - 不同市场状态下的最佳参数
    - 假信号的识别模式
    """
    
    def __init__(self, knowledge_base_path: str = None):
        super().__init__("技术分析专家（学习型）", "technical", knowledge_base_path)
    
    def analyze(self, stock_code: str, period: str = "daily", 
                lookback_days: int = 60) -> Dict:
        """
        技术面分析（增强版）
        
        在基础分析之上，应用历史经验优化判断
        """
        # 基础技术分析
        base_analysis = {
            "analyst": self.name,
            "type": "technical",
            "stock_code": stock_code,
            "analysis_date": None,  # 待实现
            "trend": None,
            "support_levels": [],
            "resistance_levels": [],
            "indicators": {
                "ma_alignment": None,
                "macd_signal": None,
                "rsi_value": None,
                "volume_trend": None
            },
            "pattern_detected": [],
            "summary": "技术分析观点（待实现）"
        }
        
        # 应用学习到的经验
        enhanced_analysis = self.apply_learning_to_analysis(base_analysis)
        
        # 如果有相关经验，给出特别提示
        if self.relevant_rules:
            enhanced_analysis['special_notes'] = [
                f"⚠️ 历史经验提醒: {rule.get('hypothesis', '')}"
                for rule in self.relevant_rules
                if rule.get('type') == 'strategy_failure'
            ]
        
        return enhanced_analysis
    
    def learn_from_trade(self, trade_result: Dict):
        """
        从具体交易中学习
        
        Args:
            trade_result: 交易结果，包含入场信号、出场原因、盈亏等
        """
        observation = {
            'type': 'technical_pattern',
            'context': f"股票{trade_result.get('stock_code')}的技术交易",
            'hypothesis': trade_result.get('signal_description', ''),
            'evidence': {
                'entry_indicators': trade_result.get('entry_signals', []),
                'exit_reason': trade_result.get('exit_reason', ''),
                'profit': trade_result.get('profit', 0),
                'holding_days': trade_result.get('holding_days', 0)
            },
            'outcome': 'success' if trade_result.get('profit', 0) > 0 else 'failure'
        }
        
        self.record_observation(observation)


class FundamentalAnalystWithLearning(LearningEnabledAnalyst):
    """
    基本面分析专家（带学习能力）
    
    学习重点：
    - 估值陷阱识别（低PE但持续下跌）
    - 财务造假预警信号
    - 行业周期判断
    """
    
    def __init__(self, knowledge_base_path: str = None):
        super().__init__("基本面分析专家（学习型）", "fundamental", knowledge_base_path)
    
    def analyze(self, stock_code: str, quarter: str = "latest") -> Dict:
        """
        基本面分析（增强版）
        """
        base_analysis = {
            "analyst": self.name,
            "type": "fundamental",
            "stock_code": stock_code,
            "analysis_date": None,
            "valuation": {
                "pe_ratio": None,
                "pb_ratio": None,
                "ps_ratio": None,
                "peg_ratio": None
            },
            "profitability": {
                "roe": None,
                "roa": None,
                "gross_margin": None,
                "net_margin": None
            },
            "growth": {
                "revenue_growth": None,
                "profit_growth": None
            },
            "financial_health": {
                "debt_to_equity": None,
                "current_ratio": None,
                "cash_flow": None
            },
            "summary": "基本面分析观点（待实现）"
        }
        
        enhanced_analysis = self.apply_learning_to_analysis(base_analysis)
        
        # 检查是否有估值陷阱的历史经验
        valuation_traps = [
            r for r in self.relevant_rules 
            if 'valuation' in r.get('type', '').lower() or 'trap' in r.get('type', '').lower()
        ]
        
        if valuation_traps:
            enhanced_analysis['warning'] = "⚠️ 注意历史估值陷阱模式"
            enhanced_analysis['trap_patterns'] = [
                t.get('observation', '') for t in valuation_traps
            ]
        
        return enhanced_analysis
    
    def learn_from_earnings_report(self, report_data: Dict, price_reaction: Dict):
        """
        从财报发布后的股价反应中学习
        
        Args:
            report_data: 财报数据
            price_reaction: 股价反应（涨跌幅、成交量变化等）
        """
        observation = {
            'type': 'fundamental_surprise',
            'context': f"股票{report_data.get('stock_code')}的财报反应",
            'hypothesis': "市场对某类财务指标的反应模式",
            'evidence': {
                'eps_surprise': report_data.get('eps_surprise', 0),
                'revenue_surprise': report_data.get('revenue_surprise', 0),
                'price_change_pct': price_reaction.get('price_change', 0),
                'volume_change': price_reaction.get('volume_change', 0)
            },
            'outcome': 'predictable' if abs(price_reaction.get('price_change', 0)) < 0.03 else 'surprising'
        }
        
        self.record_observation(observation)


class SentimentAnalystWithLearning(LearningEnabledAnalyst):
    """
    市场情绪分析专家（带学习能力）
    
    学习重点：
    - 情绪极值反转信号
    - 新闻舆情与股价的相关性
    - 主力资金流向的领先性
    """
    
    def __init__(self, knowledge_base_path: str = None):
        super().__init__("市场情绪分析师（学习型）", "sentiment", knowledge_base_path)
    
    def analyze(self, stock_code: str, window_days: int = 7) -> Dict:
        """
        情绪面分析（增强版）
        """
        base_analysis = {
            "analyst": self.name,
            "type": "sentiment",
            "stock_code": stock_code,
            "analysis_date": None,
            "news_sentiment": {
                "score": None,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0
            },
            "social_sentiment": {
                "score": None,
                "trending_topics": []
            },
            "capital_flow": {
                "northbound_flow": None,
                "main_force_flow": None,
                "retail_flow": None
            },
            "sector_rotation": {
                "sector_strength": None,
                "relative_performance": None
            },
            "institutional_ratings": [],
            "summary": "情绪面分析观点（待实现）"
        }
        
        enhanced_analysis = self.apply_learning_to_analysis(base_analysis)
        
        # 检查情绪反转的历史模式
        reversal_patterns = [
            r for r in self.relevant_rules
            if 'reversal' in r.get('type', '').lower() or 'extreme' in r.get('type', '').lower()
        ]
        
        if reversal_patterns:
            enhanced_analysis['reversal_warning'] = "⚠️ 检测到可能的情绪极值反转信号"
            enhanced_analysis['historical_patterns'] = [
                p.get('observation', '') for p in reversal_patterns
            ]
        
        return enhanced_analysis
    
    def learn_from_news_impact(self, news_data: Dict, market_reaction: Dict):
        """
        从新闻对市场的实际影响中学习
        
        Args:
            news_data: 新闻数据（情感分数、传播范围等）
            market_reaction: 市场反应
        """
        observation = {
            'type': 'sentiment_impact',
            'context': f"新闻对股票{news_data.get('stock_code')}的影响",
            'hypothesis': "特定类型新闻的市场影响力",
            'evidence': {
                'news_sentiment_score': news_data.get('sentiment_score', 0),
                'news_reach': news_data.get('reach', 0),
                'price_impact_pct': market_reaction.get('price_change', 0),
                'impact_duration_hours': market_reaction.get('duration_hours', 0)
            },
            'outcome': 'strong_impact' if abs(market_reaction.get('price_change', 0)) > 0.05 else 'weak_impact'
        }
        
        self.record_observation(observation)


# 向后兼容：保留原有类名作为别名
TechnicalAnalyst = TechnicalAnalystWithLearning
FundamentalAnalyst = FundamentalAnalystWithLearning
SentimentAnalyst = SentimentAnalystWithLearning


if __name__ == '__main__':
    # 测试学习型分析师
    print("="*70)
    print("🦞 学习型分析师节点测试")
    print("="*70)
    
    # 创建技术分析师
    tech_analyst = TechnicalAnalystWithLearning()
    
    # 执行分析
    result = tech_analyst.analyze("600519")
    
    print(f"\n分析师: {result['analyst']}")
    print(f"股票: {result['stock_code']}")
    
    if 'learning_insights' in result:
        insights = result['learning_insights']
        print(f"\n📚 学习洞察:")
        print(f"  相关规则数: {insights['relevant_rules_count']}")
        print(f"  置信度调整: {insights['confidence_adjustment']:.2f}x")
        print(f"  关键教训:")
        for lesson in insights['key_lessons']:
            print(f"    - {lesson}")
    
    if 'special_notes' in result:
        print(f"\n⚠️  特别提示:")
        for note in result['special_notes']:
            print(f"  {note}")
    
    print("\n✅ 学习型分析师节点工作正常！")
