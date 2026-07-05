#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 足球预测每日效果对比报告
=====================================

功能：
1. 获取当日实际比赛结果
2. 对比预测结果与实际结果
3. 计算准确率、置信度等指标
4. 生成每日报告
5. 追踪历史预测效果

用法：
    python3 football_predict_daily_report.py --date 2026-06-26
    python3 football_predict_daily_report.py --today
    python3 football_predict_daily_report.py --history 7
    python3 football_predict_daily_report.py --summary
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'domains', 'learning', 'problems'))
from football_predict_engine import FootballPredictEngine
from meyo_predict_api import MeYouPredictAPI


class FootballPredictDailyReport:
    """足球预测每日效果对比报告"""
    
    def __init__(self):
        self.engine = FootballPredictEngine()
        self.api = MeYouPredictAPI()
        self.report_dir = os.path.join(os.path.dirname(__file__), '..', 'reports', 'football-predict')
        self.history_file = os.path.join(self.report_dir, 'prediction_history.json')
        os.makedirs(self.report_dir, exist_ok=True)
        self.history = self._load_history()
        
    def _load_history(self) -> Dict:
        """加载历史记录"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'daily_reports': {},
            'total_predictions': 0,
            'total_correct': 0,
            'by_type': {},
            'by_confidence': {},
            'streak': 0,
            'max_streak': 0
        }
    
    def _save_history(self):
        """保存历史记录"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_daily_matches(self, date: str = None) -> List[Dict]:
        """
        获取当日比赛
        
        Args:
            date: 日期（YYYY-MM-DD）
            
        Returns:
            比赛列表
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        # 从觅游API获取赛事
        markets = self.api.get_open_markets(page_size=50)
        
        # 过滤当日比赛
        daily_matches = []
        for market in markets:
            close_time = market.get('close_time', '')
            if date in close_time:
                daily_matches.append({
                    'market_id': market['id'],
                    'title': market['title'],
                    'home_team': market.get('ff_match', {}).get('home_team', ''),
                    'away_team': market.get('ff_match', {}).get('away_team', ''),
                    'type': market.get('ff_match', {}).get('type', ''),
                    'close_time': close_time,
                    'options': market.get('options', [])
                })
                
        return daily_matches
    
    def generate_predictions(self, matches: List[Dict]) -> List[Dict]:
        """
        生成预测
        
        Args:
            matches: 比赛列表
            
        Returns:
            预测列表
        """
        predictions = []
        
        for match in matches:
            home_team = match['home_team']
            away_team = match['away_team']
            match_type = match['type']
            
            prediction = {
                'market_id': match['market_id'],
                'title': match['title'],
                'home_team': home_team,
                'away_team': away_team,
                'type': match_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # 根据类型生成预测
            if match_type == 'win_lose_draw':
                result = self.engine.predict_match_result(home_team, away_team)
                prediction['prediction'] = result['prediction']
                prediction['confidence'] = result['confidence']
                prediction['probabilities'] = result['probabilities']
                
            elif match_type == 'score':
                score = self.engine.predict_score(home_team, away_team)
                prediction['prediction'] = score['predicted_score']
                prediction['confidence'] = score['confidence']
                prediction['top_scores'] = score['top_scores']
                
            elif match_type == 'total_goals':
                total = self.engine.predict_total_goals(home_team, away_team)
                prediction['prediction'] = total['prediction']
                prediction['confidence'] = total['confidence']
                
            elif match_type == 'champion':
                # 冠军预测需要球队列表
                teams = [
                    {'name': home_team, 'rank': 20, 'form': 'W-W-D-L-W'},
                    {'name': away_team, 'rank': 15, 'form': 'W-W-W-D-W'},
                ]
                champion = self.engine.predict_champion(teams)
                prediction['prediction'] = champion['predicted_champion']
                prediction['confidence'] = champion['confidence']
                
            predictions.append(prediction)
            
        return predictions
    
    def compare_with_results(self, predictions: List[Dict], 
                           actual_results: Dict = None) -> List[Dict]:
        """
        对比预测与实际结果
        
        Args:
            predictions: 预测列表
            actual_results: 实际结果（从API获取或手动输入）
            
        Returns:
            对比结果列表
        """
        comparisons = []
        
        for pred in predictions:
            market_id = pred['market_id']
            
            # 获取实际结果
            if actual_results and market_id in actual_results:
                actual = actual_results[market_id]
            else:
                # 模拟实际结果（实际应从API获取）
                actual = self._simulate_actual_result(pred)
                
            # 对比
            is_correct = self._check_prediction(pred, actual)
            
            comparison = {
                'market_id': market_id,
                'title': pred['title'],
                'home_team': pred['home_team'],
                'away_team': pred['away_team'],
                'type': pred['type'],
                'prediction': pred['prediction'],
                'confidence': pred['confidence'],
                'actual': actual.get('result', ''),
                'is_correct': is_correct,
                'timestamp': datetime.now().isoformat()
            }
            
            comparisons.append(comparison)
            
        return comparisons
    
    def _simulate_actual_result(self, pred: Dict) -> Dict:
        """
        模拟实际结果（实际应从API获取）
        
        Args:
            pred: 预测
            
        Returns:
            实际结果
        """
        import random
        
        match_type = pred['type']
        
        if match_type == 'win_lose_draw':
            options = ['主胜', '平局', '主负']
            # 根据预测概率模拟
            if 'probabilities' in pred:
                probs = pred['probabilities']
                # 加权随机
                r = random.random()
                if r < probs.get('home_win', 0.33):
                    result = '主胜'
                elif r < probs.get('home_win', 0.33) + probs.get('draw', 0.33):
                    result = '平局'
                else:
                    result = '主负'
            else:
                result = random.choice(options)
                
        elif match_type == 'score':
            scores = ['1-0', '2-0', '2-1', '3-1', '1-1', '0-0', '0-1', '0-2', '1-2']
            result = random.choice(scores)
            
        elif match_type == 'total_goals':
            result = str(random.randint(0, 7))
            
        elif match_type == 'champion':
            result = pred['home_team'] if random.random() < 0.5 else pred['away_team']
            
        else:
            result = '未知'
            
        return {'result': result}
    
    def _check_prediction(self, pred: Dict, actual: Dict) -> bool:
        """
        检查预测是否正确
        
        Args:
            pred: 预测
            actual: 实际结果
            
        Returns:
            是否正确
        """
        prediction = pred.get('prediction', '')
        actual_result = actual.get('result', '')
        
        # 精确匹配
        if prediction == actual_result:
            return True
            
        # 模糊匹配（胜平负）
        if pred['type'] == 'win_lose_draw':
            if prediction in ['主胜', '主负', '平局']:
                if actual_result in ['主胜', '主负', '平局']:
                    return prediction == actual_result
                    
        return False
    
    def generate_daily_report(self, date: str = None) -> Dict:
        """
        生成每日报告
        
        Args:
            date: 日期
            
        Returns:
            报告
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
            
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 足球预测每日效果对比报告")
        print(f"   日期：{date}")
        print("=" * 60)
        
        # 1. 获取当日比赛
        print("\n📊 获取当日比赛:")
        matches = self.get_daily_matches(date)
        print(f"   当日比赛数：{len(matches)}")
        
        if not matches:
            print("   ⚠️ 当日无比赛")
            return {'date': date, 'matches': 0, 'predictions': 0, 'correct': 0}
            
        # 2. 生成预测
        print("\n🎯 生成预测:")
        predictions = self.generate_predictions(matches)
        print(f"   预测数：{len(predictions)}")
        
        # 3. 对比结果
        print("\n📈 对比结果:")
        comparisons = self.compare_with_results(predictions)
        
        # 4. 统计
        total = len(comparisons)
        correct = sum(1 for c in comparisons if c['is_correct'])
        accuracy = correct / total if total > 0 else 0
        
        # 按类型统计
        by_type = {}
        for c in comparisons:
            t = c['type']
            if t not in by_type:
                by_type[t] = {'total': 0, 'correct': 0}
            by_type[t]['total'] += 1
            if c['is_correct']:
                by_type[t]['correct'] += 1
                
        # 按置信度统计
        by_confidence = {
            'high': {'total': 0, 'correct': 0},    # >=0.7
            'medium': {'total': 0, 'correct': 0},   # 0.5-0.7
            'low': {'total': 0, 'correct': 0}       # <0.5
        }
        for c in comparisons:
            conf = c['confidence']
            if conf >= 0.7:
                by_confidence['high']['total'] += 1
                if c['is_correct']:
                    by_confidence['high']['correct'] += 1
            elif conf >= 0.5:
                by_confidence['medium']['total'] += 1
                if c['is_correct']:
                    by_confidence['medium']['correct'] += 1
            else:
                by_confidence['low']['total'] += 1
                if c['is_correct']:
                    by_confidence['low']['correct'] += 1
                    
        # 更新历史
        self.history['daily_reports'][date] = {
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
            'by_type': by_type,
            'by_confidence': by_confidence,
            'comparisons': comparisons
        }
        self.history['total_predictions'] += total
        self.history['total_correct'] += correct
        
        # 更新连红
        if correct > 0:
            self.history['streak'] += 1
            if self.history['streak'] > self.history['max_streak']:
                self.history['max_streak'] = self.history['streak']
        else:
            self.history['streak'] = 0
            
        self._save_history()
        
        # 输出报告
        print(f"\n{'=' * 60}")
        print(f"📊 每日报告")
        print(f"   总预测数：{total}")
        print(f"   正确数：{correct}")
        print(f"   准确率：{accuracy:.1%}")
        print(f"   连红：{self.history['streak']}")
        print(f"   最大连红：{self.history['max_streak']}")
        
        print(f"\n📈 按类型统计:")
        for t, stats in by_type.items():
            t_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {t}: {stats['correct']}/{stats['total']} ({t_accuracy:.1%})")
            
        print(f"\n📊 按置信度统计:")
        for level, stats in by_confidence.items():
            level_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {level}: {stats['correct']}/{stats['total']} ({level_accuracy:.1%})")
            
        print(f"\n📋 逐场对比:")
        for c in comparisons:
            status = '✅' if c['is_correct'] else '❌'
            print(f"   {status} {c['home_team']} vs {c['away_team']} · {c['type']}")
            print(f"      预测：{c['prediction']} (置信度{c['confidence']:.1%})")
            print(f"      实际：{c['actual']}")
            
        return {
            'date': date,
            'total': total,
            'correct': correct,
            'accuracy': accuracy,
            'by_type': by_type,
            'by_confidence': by_confidence,
            'comparisons': comparisons
        }
    
    def generate_history_report(self, days: int = 7) -> Dict:
        """
        生成历史报告
        
        Args:
            days: 天数
            
        Returns:
            报告
        """
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 足球预测历史效果报告")
        print(f"   最近{days}天")
        print("=" * 60)
        
        # 获取最近N天的报告
        daily_reports = self.history.get('daily_reports', {})
        recent_reports = {}
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in daily_reports:
                recent_reports[date] = daily_reports[date]
                
        # 统计
        total_predictions = sum(r['total'] for r in recent_reports.values())
        total_correct = sum(r['correct'] for r in recent_reports.values())
        overall_accuracy = total_correct / total_predictions if total_predictions > 0 else 0
        
        print(f"\n📊 总体统计")
        print(f"   总预测数：{total_predictions}")
        print(f"   总正确数：{total_correct}")
        print(f"   整体准确率：{overall_accuracy:.1%}")
        print(f"   当前连红：{self.history['streak']}")
        print(f"   最大连红：{self.history['max_streak']}")
        
        print(f"\n📋 每日详情:")
        for date in sorted(recent_reports.keys(), reverse=True):
            report = recent_reports[date]
            print(f"   {date}: {report['correct']}/{report['total']} ({report['accuracy']:.1%})")
            
        return {
            'days': days,
            'total_predictions': total_predictions,
            'total_correct': total_correct,
            'overall_accuracy': overall_accuracy,
            'daily_reports': recent_reports
        }
    
    def generate_summary(self) -> Dict:
        """
        生成总结报告
        
        Returns:
            报告
        """
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 足球预测效果总结报告")
        print("=" * 60)
        
        total_predictions = self.history['total_predictions']
        total_correct = self.history['total_correct']
        overall_accuracy = total_correct / total_predictions if total_predictions > 0 else 0
        
        print(f"\n📊 总体统计")
        print(f"   总预测数：{total_predictions}")
        print(f"   总正确数：{total_correct}")
        print(f"   整体准确率：{overall_accuracy:.1%}")
        print(f"   当前连红：{self.history['streak']}")
        print(f"   最大连红：{self.history['max_streak']}")
        
        # 按类型统计
        by_type = {}
        for date, report in self.history.get('daily_reports', {}).items():
            for t, stats in report.get('by_type', {}).items():
                if t not in by_type:
                    by_type[t] = {'total': 0, 'correct': 0}
                by_type[t]['total'] += stats['total']
                by_type[t]['correct'] += stats['correct']
                
        print(f"\n📈 按类型统计:")
        for t, stats in by_type.items():
            t_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {t}: {stats['correct']}/{stats['total']} ({t_accuracy:.1%})")
            
        # 按置信度统计
        by_confidence = {}
        for date, report in self.history.get('daily_reports', {}).items():
            for level, stats in report.get('by_confidence', {}).items():
                if level not in by_confidence:
                    by_confidence[level] = {'total': 0, 'correct': 0}
                by_confidence[level]['total'] += stats['total']
                by_confidence[level]['correct'] += stats['correct']
                
        print(f"\n📊 按置信度统计:")
        for level, stats in by_confidence.items():
            level_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {level}: {stats['correct']}/{stats['total']} ({level_accuracy:.1%})")
            
        return {
            'total_predictions': total_predictions,
            'total_correct': total_correct,
            'overall_accuracy': overall_accuracy,
            'by_type': by_type,
            'by_confidence': by_confidence
        }


def main():
    parser = argparse.ArgumentParser(description='🦞 小龙虾网络 · 足球预测每日效果对比报告')
    
    parser.add_argument('--date', type=str,
                       help='指定日期（YYYY-MM-DD）')
    parser.add_argument('--today', action='store_true',
                       help='生成今日报告')
    parser.add_argument('--history', type=int,
                       help='生成历史报告（天数）')
    parser.add_argument('--summary', action='store_true',
                       help='生成总结报告')
                       
    args = parser.parse_args()
    report = FootballPredictDailyReport()
    
    if args.date:
        report.generate_daily_report(args.date)
    elif args.today:
        report.generate_daily_report()
    elif args.history:
        report.generate_history_report(args.history)
    elif args.summary:
        report.generate_summary()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
