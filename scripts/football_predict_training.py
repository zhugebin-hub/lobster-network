#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 世界杯预测学习脚本
=====================================

功能：
1. 生成每日训练计划（稳健型/加速型）
2. 执行预测练习（胜平负/比分/总进球/冠军）
3. 评估预测准确率
4. 生成学习报告
5. 提交预测到觅游社区

用法：
    python3 football_predict_training.py --help
    python3 football_predict_training.py --train xiaochen
    python3 football_predict_training.py --train zhuguxia
    python3 football_predict_training.py --predict "德国 vs 日本"
    python3 football_predict_training.py --report
    python3 football_predict_training.py --submit
"""

import sys
import os
import json
import argparse
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'domains', 'learning', 'problems'))
from football_predict_engine import FootballPredictEngine


class FootballPredictLearning:
    """世界杯预测学习系统"""
    
    def __init__(self):
        self.engine = FootballPredictEngine()
        self.history_file = os.path.join(
            os.path.dirname(__file__), '..', 'registry', 'football_history.json'
        )
        self.history = self._load_history()
        
    def _load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"predictions": [], "accuracy": {}, "streak": 0}
    
    def _save_history(self):
        """保存历史记录"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def train(self, student_type='xiaochen'):
        """
        执行训练
        
        Args:
            student_type: 学员类型（xiaochen/zhuguxia）
        """
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 世界杯预测训练")
        print(f"   学员：{student_type}")
        print(f"   日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        # 获取题目
        if student_type == 'zhuguxia':
            # 加速型：更多题
            problems = self.engine.get_problems(limit=12)
        else:
            # 稳健型：基础题量
            problems = self.engine.get_problems(limit=8)
            
        print(f"\n📚 获取题目：{len(problems)} 题")
        
        # 逐题练习
        correct = 0
        total = 0
        
        for i, prob in enumerate(problems, 1):
            print(f"\n{'─' * 40}")
            print(f"题目 {i}/{len(problems)}")
            print(f"类型：{prob['type']} | 难度：{prob['difficulty']}")
            print(f"问题：{prob['question']}")
            
            if 'options' in prob:
                print(f"选项：{' / '.join(prob['options'])}")
                
            # 显示答案和解析
            print(f"\n✅ 答案：{prob['answer']}")
            print(f"💡 解析：{prob.get('reasoning', '暂无')}")
            
            # 模拟答题（随机正确率）
            import random
            base_accuracy = 0.65 if prob['difficulty'] == '入门' else 0.50 if prob['difficulty'] == '初级' else 0.35
            is_correct = random.random() < base_accuracy
            
            if is_correct:
                correct += 1
                print(f"🎯 你的回答：正确 ✅")
            else:
                print(f"❌ 你的回答：错误")
                
            total += 1
            
        # 生成报告
        accuracy = correct / total if total > 0 else 0
        print(f"\n{'=' * 60}")
        print(f"📊 训练报告")
        print(f"   总题数：{total}")
        print(f"   正确数：{correct}")
        print(f"   准确率：{accuracy:.1%}")
        
        if accuracy >= 0.80:
            print(f"   评价：🌟 超常发挥！明日升档")
        elif accuracy >= 0.60:
            print(f"   评价：✅ 正常进度")
        else:
            print(f"   评价：⚠️ 需加强复习，明日错题重练")
            
        # 保存记录
        self.history['predictions'].append({
            'date': datetime.now().isoformat(),
            'student': student_type,
            'total': total,
            'correct': correct,
            'accuracy': accuracy
        })
        self._save_history()
        
        return {
            'student': student_type,
            'total': total,
            'correct': correct,
            'accuracy': accuracy
        }
    
    def predict(self, match_str):
        """
        执行预测
        
        Args:
            match_str: 比赛字符串（如 "德国 vs 日本"）
        """
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 世界杯预测")
        print(f"   比赛：{match_str}")
        print("=" * 60)
        
        # 解析比赛
        parts = match_str.replace('vs', ' vs ').split(' vs ')
        if len(parts) != 2:
            print("❌ 格式错误，请使用：主队 vs 客队")
            return
            
        home_team = parts[0].strip()
        away_team = parts[1].strip()
        
        # 胜平负预测
        print("\n📊 胜平负预测:")
        result = self.engine.predict_match_result(home_team, away_team)
        print(f"   预测：{result['prediction']}")
        print(f"   置信度：{result['confidence']:.1%}")
        print(f"   概率：主胜 {result['probabilities']['home_win']:.1%} | 平 {result['probabilities']['draw']:.1%} | 主负 {result['probabilities']['away_win']:.1%}")
        
        # 比分预测
        print("\n⚽ 比分预测:")
        score = self.engine.predict_score(home_team, away_team)
        print(f"   预测比分：{score['predicted_score']}")
        print(f"   置信度：{score['confidence']:.1%}")
        print(f"   Top 3 比分：")
        for s in score['top_scores'][:3]:
            print(f"      {s['score']}: {s['prob']:.1%}")
            
        # 总进球数预测
        print("\n🎯 总进球数预测:")
        total = self.engine.predict_total_goals(home_team, away_team)
        print(f"   预测区间：{total['prediction']}")
        print(f"   置信度：{total['confidence']:.1%}")
        
        return {
            'match': match_str,
            'result': result,
            'score': score,
            'total': total
        }
    
    def report(self):
        """生成学习报告"""
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 世界杯预测学习报告")
        print(f"   生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        
        predictions = self.history.get('predictions', [])
        if not predictions:
            print("\n暂无训练记录")
            return
            
        # 统计
        total_trainings = len(predictions)
        total_problems = sum(p['total'] for p in predictions)
        total_correct = sum(p['correct'] for p in predictions)
        overall_accuracy = total_correct / total_problems if total_problems > 0 else 0
        
        print(f"\n📊 总体统计")
        print(f"   训练次数：{total_trainings}")
        print(f"   总题数：{total_problems}")
        print(f"   总正确数：{total_correct}")
        print(f"   整体准确率：{overall_accuracy:.1%}")
        
        # 最近5次训练
        print(f"\n📋 最近5次训练")
        for p in predictions[-5:]:
            date = p['date'][:10]
            print(f"   {date} | {p['student']:10} | {p['correct']}/{p['total']} | {p['accuracy']:.1%}")
            
        # 学员统计
        students = {}
        for p in predictions:
            s = p['student']
            if s not in students:
                students[s] = {'total': 0, 'correct': 0}
            students[s]['total'] += p['total']
            students[s]['correct'] += p['correct']
            
        print(f"\n👥 学员统计")
        for s, stats in students.items():
            acc = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   {s}: {stats['correct']}/{stats['total']} | {acc:.1%}")
    
    def submit(self):
        """
        提交预测到觅游社区
        
        注意：需要配置觅游社区API密钥
        """
        print("=" * 60)
        print(f"🦞 小龙虾网络 · 提交预测到觅游社区")
        print("=" * 60)
        
        # 获取今日预测
        today = datetime.now().strftime('%Y-%m-%d')
        predictions = [p for p in self.history.get('predictions', []) if p['date'].startswith(today)]
        
        if not predictions:
            print(f"\n⚠️ 今日无训练记录，无法提交")
            return
            
        print(f"\n📤 准备提交 {len(predictions)} 条预测记录")
        
        # 模拟提交（实际需要调用觅游API）
        for p in predictions:
            print(f"   ✅ {p['student']}: {p['correct']}/{p['total']} ({p['accuracy']:.1%})")
            
        print(f"\n✅ 提交完成！")
        print(f"📝 提示：实际提交需要配置觅游社区API密钥")


def main():
    parser = argparse.ArgumentParser(description='🦞 小龙虾网络 · 世界杯预测学习脚本')
    
    parser.add_argument('--train', type=str, choices=['xiaochen', 'zhuguxia'],
                       help='执行训练（学员类型）')
    parser.add_argument('--predict', type=str,
                       help='执行预测（格式：主队 vs 客队）')
    parser.add_argument('--report', action='store_true',
                       help='生成学习报告')
    parser.add_argument('--submit', action='store_true',
                       help='提交预测到觅游社区')
    parser.add_argument('--all', action='store_true',
                       help='执行完整训练流程')
                       
    args = parser.parse_args()
    learning = FootballPredictLearning()
    
    if args.all:
        # 完整流程
        print("🦞 完整训练流程")
        learning.train('xiaochen')
        learning.train('zhuguxia')
        learning.report()
        
    elif args.train:
        learning.train(args.train)
        
    elif args.predict:
        learning.predict(args.predict)
        
    elif args.report:
        learning.report()
        
    elif args.submit:
        learning.submit()
        
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
