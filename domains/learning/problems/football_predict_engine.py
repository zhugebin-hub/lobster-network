"""
世界杯预测引擎
支持胜平负、比分、总进球数、冠军、冠亚军组合预测
"""

import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FootballPredictEngine:
    """世界杯预测引擎"""
    
    def __init__(self, problems_dir: str = None):
        """初始化引擎"""
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                'problems', 'football-predict'
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()
        
    def _load_problems(self):
        """加载各阶段题库"""
        for phase in ['phase1', 'phase2', 'phase3']:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, 'problems.json')
            if os.path.exists(problems_file):
                with open(problems_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.phases[phase] = data
                    
    def get_problems(self, phase: str = None, problem_type: str = None, 
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        """获取题目"""
        problems = []
        
        phases_to_check = [phase] if phase else list(self.phases.keys())
        
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]['problems']:
                # 过滤条件
                if problem_type and prob['type'] != problem_type:
                    continue
                if difficulty and prob['difficulty'] != difficulty:
                    continue
                problems.append(prob)
                
        return problems[:limit]
    
    def predict_match_result(self, home_team: str, away_team: str,
                            home_rank: int = None, away_rank: int = None,
                            home_form: str = None, away_form: str = None) -> Dict:
        """
        预测胜平负
        
        Args:
            home_team: 主队
            away_team: 客队
            home_rank: 主队世界排名
            away_rank: 客队世界排名
            home_form: 主队近期状态（W/D/L）
            away_form: 客队近期状态
            
        Returns:
            预测结果
        """
        # 基础评分
        home_score = 0.5
        away_score = 0.5
        draw_prob = 0.25
        
        # 排名因素
        if home_rank and away_rank:
            rank_diff = away_rank - home_rank
            home_score += rank_diff * 0.005  # 每差10名，+5%
            away_score -= rank_diff * 0.005
            
        # 状态因素
        if home_form:
            form_points = {'W': 3, 'D': 1, 'L': 0}
            home_points = sum(form_points.get(c, 0) for c in home_form if c in 'WDL')
            home_score += (home_points - 6) * 0.02  # 基准6分
            
        if away_form:
            form_points = {'W': 3, 'D': 1, 'L': 0}
            away_points = sum(form_points.get(c, 0) for c in away_form if c in 'WDL')
            away_score += (away_points - 6) * 0.02
            
        # 主场优势
        home_score += 0.10
        
        # 归一化
        total = max(home_score + away_score + draw_prob, 0.01)
        home_prob = home_score / total
        away_prob = away_score / total
        draw_prob = draw_prob / total
        
        # 决策
        if home_prob > away_prob and home_prob > draw_prob:
            result = "主胜"
            confidence = home_prob
        elif away_prob > home_prob and away_prob > draw_prob:
            result = "主负"
            confidence = away_prob
        else:
            result = "平局"
            confidence = draw_prob
            
        return {
            'match': f"{home_team} vs {away_team}",
            'prediction': result,
            'confidence': round(confidence, 3),
            'probabilities': {
                'home_win': round(home_prob, 3),
                'draw': round(draw_prob, 3),
                'away_win': round(away_prob, 3)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_score(self, home_team: str, away_team: str,
                     home_avg_goals: float = 1.5, away_avg_goals: float = 1.2,
                     home_concede: float = 1.0, away_concede: float = 1.0) -> Dict:
        """
        预测比分（泊松分布）
        
        Args:
            home_team: 主队
            away_team: 客队
            home_avg_goals: 主队场均进球
            away_avg_goals: 客队场均进球
            home_concede: 主队场均失球
            away_concede: 客队场均失球
            
        Returns:
            预测比分
        """
        import math
        
        # 计算期望进球
        home_lambda = (home_avg_goals + away_concede) / 2
        away_lambda = (away_avg_goals + home_concede) / 2
        
        # 泊松概率
        def poisson_prob(k, lam):
            return (lam ** k) * math.exp(-lam) / math.factorial(k)
        
        # 计算各比分概率
        score_probs = {}
        for home_goals in range(6):
            for away_goals in range(6):
                prob = poisson_prob(home_goals, home_lambda) * poisson_prob(away_goals, away_lambda)
                score_probs[f"{home_goals}-{away_goals}"] = prob
                
        # 排序
        sorted_scores = sorted(score_probs.items(), key=lambda x: x[1], reverse=True)
        
        # 前5个最可能比分
        top_scores = sorted_scores[:5]
        
        return {
            'match': f"{home_team} vs {away_team}",
            'predicted_score': top_scores[0][0],
            'confidence': round(top_scores[0][1], 3),
            'top_scores': [{'score': s, 'prob': round(p, 3)} for s, p in top_scores],
            'expected_goals': {
                'home': round(home_lambda, 2),
                'away': round(away_lambda, 2)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_total_goals(self, home_team: str, away_team: str,
                           home_avg_goals: float = 1.5, away_avg_goals: float = 1.2) -> Dict:
        """
        预测总进球数
        
        Returns:
            预测结果
        """
        total_lambda = home_avg_goals + away_avg_goals
        
        # 各区间概率
        import math
        def poisson_cdf(k, lam):
            return sum((lam ** i) * math.exp(-lam) / math.factorial(i) for i in range(k+1))
        
        probs = {
            '0-1': poisson_cdf(1, total_lambda),
            '2-3': poisson_cdf(3, total_lambda) - poisson_cdf(1, total_lambda),
            '4-5': poisson_cdf(5, total_lambda) - poisson_cdf(3, total_lambda),
            '6+': 1 - poisson_cdf(5, total_lambda)
        }
        
        # 最高概率区间
        best_range = max(probs.items(), key=lambda x: x[1])
        
        return {
            'match': f"{home_team} vs {away_team}",
            'prediction': best_range[0],
            'confidence': round(best_range[1], 3),
            'probabilities': {k: round(v, 3) for k, v in probs.items()},
            'expected_total': round(total_lambda, 2),
            'timestamp': datetime.now().isoformat()
        }
    
    def predict_champion(self, teams: List[Dict]) -> Dict:
        """
        预测冠军
        
        Args:
            teams: 球队列表，每队包含 name, rank, form, squad_depth 等
            
        Returns:
            预测冠军
        """
        scores = []
        for team in teams:
            score = 0.5  # 基础分
            
            # 排名分
            if 'rank' in team:
                score += max(0, (50 - team['rank']) * 0.005)
                
            # 状态分
            if 'form' in team:
                form_points = {'W': 3, 'D': 1, 'L': 0}
                points = sum(form_points.get(c, 0) for c in team['form'] if c in 'WDL')
                score += (points - 6) * 0.02
                
            # 阵容深度
            if 'squad_depth' in team:
                score += team['squad_depth'] * 0.1
                
            # 教练经验
            if 'coach_experience' in team:
                score += team['coach_experience'] * 0.05
                
            scores.append((team['name'], score))
            
        # 排序
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # 归一化
        total = sum(s for _, s in scores)
        probs = [(name, score/total) for name, score in scores]
        
        return {
            'predicted_champion': probs[0][0],
            'confidence': round(probs[0][1], 3),
            'top_teams': [{'team': n, 'prob': round(p, 3)} for n, p in probs[:8]],
            'timestamp': datetime.now().isoformat()
        }
    
    def expected_value(self, odds: float, my_prob: float) -> float:
        """
        计算期望值（凯利公式）
        
        Args:
            odds: 赔率
            my_prob: 我的预测概率
            
        Returns:
            期望值
        """
        return my_prob * odds - 1
    
    def kelly_criterion(self, odds: float, my_prob: float, 
                       bankroll: float = 1000) -> Dict:
        """
        凯利公式计算最优投注比例
        
        Args:
            odds: 赔率
            my_prob: 我的预测概率
            bankroll: 资金
            
        Returns:
            投注建议
        """
        # 隐含概率
        implied_prob = 1 / odds
        
        # 期望值
        ev = self.expected_value(odds, my_prob)
        
        # 凯利公式
        b = odds - 1
        q = 1 - my_prob
        kelly = (my_prob * b - q) / b if b > 0 else 0
        
        # 投注金额
        bet_amount = max(0, kelly * bankroll)
        
        return {
            'odds': odds,
            'my_prob': my_prob,
            'implied_prob': round(implied_prob, 3),
            'expected_value': round(ev, 3),
            'kelly_fraction': round(kelly, 3),
            'recommended_bet': round(bet_amount, 2),
            'should_bet': kelly > 0,
            'value_bet': ev > 0
        }


# 演示
if __name__ == '__main__':
    engine = FootballPredictEngine()
    
    print("=" * 50)
    print("🦞 小龙虾网络 - 世界杯预测引擎 V1.0")
    print("=" * 50)
    
    # 1. 胜平负预测
    print("\n📊 胜平负预测:")
    result = engine.predict_match_result(
        home_team="德国",
        away_team="日本",
        home_rank=16,
        away_rank=20,
        home_form="W-W-D-L-W",
        away_form="W-L-W-W-D"
    )
    print(f"   比赛：{result['match']}")
    print(f"   预测：{result['prediction']}")
    print(f"   置信度：{result['confidence']:.1%}")
    print(f"   概率：主胜 {result['probabilities']['home_win']:.1%} | 平 {result['probabilities']['draw']:.1%} | 主负 {result['probabilities']['away_win']:.1%}")
    
    # 2. 比分预测
    print("\n⚽ 比分预测:")
    score = engine.predict_score(
        home_team="德国",
        away_team="日本",
        home_avg_goals=2.1,
        away_avg_goals=1.4,
        home_concede=0.8,
        away_concede=1.1
    )
    print(f"   比赛：{score['match']}")
    print(f"   预测比分：{score['predicted_score']}")
    print(f"   置信度：{score['confidence']:.1%}")
    print(f"   期望进球：主队 {score['expected_goals']['home']} - 客队 {score['expected_goals']['away']}")
    print(f"   Top 3 比分：")
    for s in score['top_scores'][:3]:
        print(f"      {s['score']}: {s['prob']:.1%}")
    
    # 3. 总进球数预测
    print("\n🎯 总进球数预测:")
    total = engine.predict_total_goals(
        home_team="德国",
        away_team="日本",
        home_avg_goals=2.1,
        away_avg_goals=1.4
    )
    print(f"   比赛：{total['match']}")
    print(f"   预测区间：{total['prediction']}")
    print(f"   置信度：{total['confidence']:.1%}")
    print(f"   期望总进球：{total['expected_total']}")
    
    # 4. 冠军预测
    print("\n🏆 冠军预测:")
    teams = [
        {'name': '德国', 'rank': 16, 'form': 'W-W-D-L-W', 'squad_depth': 0.9, 'coach_experience': 0.8},
        {'name': '法国', 'rank': 4, 'form': 'W-W-W-D-W', 'squad_depth': 0.95, 'coach_experience': 0.7},
        {'name': '巴西', 'rank': 5, 'form': 'W-D-W-W-L', 'squad_depth': 0.92, 'coach_experience': 0.6},
        {'name': '阿根廷', 'rank': 3, 'form': 'W-W-L-W-D', 'squad_depth': 0.85, 'coach_experience': 0.9},
        {'name': '英格兰', 'rank': 8, 'form': 'W-D-W-W-W', 'squad_depth': 0.88, 'coach_experience': 0.7},
        {'name': '荷兰', 'rank': 7, 'form': 'W-W-W-D-W', 'squad_depth': 0.80, 'coach_experience': 0.8},
    ]
    champion = engine.predict_champion(teams)
    print(f"   预测冠军：{champion['predicted_champion']}")
    print(f"   置信度：{champion['confidence']:.1%}")
    print(f"   Top 3:")
    for t in champion['top_teams'][:3]:
        print(f"      {t['team']}: {t['prob']:.1%}")
    
    # 5. 凯利公式
    print("\n💰 凯利公式:")
    kelly = engine.kelly_criterion(odds=1.85, my_prob=0.60, bankroll=1000)
    print(f"   赔率：{kelly['odds']}")
    print(f"   我的概率：{kelly['my_prob']:.0%}")
    print(f"   期望值：{kelly['expected_value']:.3f}")
    print(f"   凯利比例：{kelly['kelly_fraction']:.1%}")
    print(f"   建议投注：¥{kelly['recommended_bet']:.0f}")
    print(f"   是否投注：{'✅ 是' if kelly['should_bet'] else '❌ 否'}")
    
    # 6. 加载题库
    print("\n📚 题库统计:")
    for phase, data in engine.phases.items():
        print(f"   {phase}: {data['name']} - {len(data['problems'])} 题")
        
    print("\n" + "=" * 50)
    print("✅ 预测引擎测试完成！")
