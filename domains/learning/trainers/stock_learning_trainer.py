#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 炒股学习训练器
版本: V1.0 | 日期: 2026-06-28
功能: 整合Signal Arena引擎和Stock Predict引擎，提供完整炒股学习训练
"""

import json
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'problems'))
from signal_arena_engine import SignalArenaEngine
from stock_predict_engine import StockPredictEngine


class StockLearningTrainer:
    """炒股学习训练器"""
    
    def __init__(self, student_id: str, student_type: str = "standard"):
        self.student_id = student_id
        self.student_type = student_type  # standard/accelerated
        self.arena_engine = SignalArenaEngine()
        self.predict_engine = StockPredictEngine()
        self.state_file = os.path.join(
            os.path.dirname(__file__), 'state', f'{student_id}_stock_learning_state.json'
        )
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """加载训练状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "student": self.student_id,
            "total_trainings": 0,
            "total_problems": 0,
            "total_correct": 0,
            "by_module": {
                "arena": {"total": 0, "correct": 0},
                "predict": {"total": 0, "correct": 0},
                "portfolio": {"total": 0, "correct": 0}
            },
            "by_phase": {
                "phase1": {"total": 0, "correct": 0},
                "phase2": {"total": 0, "correct": 0},
                "phase3": {"total": 0, "correct": 0}
            },
            "streak": 0,
            "last_training": None,
            "history": []
        }
    
    def _save_state(self):
        """保存训练状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def train_arena(self, count: int = 5) -> Dict:
        """Signal Arena实战训练"""
        problems = self.arena_engine.generate_problems(count)
        results = self._execute_training(problems, "arena")
        self._update_state(results, "arena")
        return results
    
    def train_predict(self, phase: str = "phase1", count: int = 5) -> Dict:
        """预测模型训练"""
        problems = self.predict_engine.get_problems(phase, count)
        results = self._execute_training(problems, "predict")
        self._update_state(results, "predict", phase)
        return results
    
    def train_portfolio(self, count: int = 3) -> Dict:
        """组合优化训练"""
        problems = self._generate_portfolio_problems(count)
        results = self._execute_training(problems, "portfolio")
        self._update_state(results, "portfolio")
        return results
    
    def _execute_training(self, problems: List[Dict], module: str) -> Dict:
        """执行训练"""
        results = {
            "student": self.student_id,
            "module": module,
            "timestamp": datetime.now().isoformat(),
            "problems": [],
            "total": len(problems),
            "correct": 0
        }
        
        for prob in problems:
            is_correct = self._simulate_answer(prob)
            result = {
                "problem_id": prob.get("id", ""),
                "type": prob.get("type", ""),
                "difficulty": prob.get("difficulty", ""),
                "is_correct": is_correct
            }
            results["problems"].append(result)
            
            if is_correct:
                results["correct"] += 1
        
        return results
    
    def _simulate_answer(self, problem: Dict) -> bool:
        """模拟答题"""
        import random
        if self.student_type == "accelerated":
            base_accuracy = 0.85
        else:
            base_accuracy = 0.70
        
        difficulty_factor = {
            "入门": 0.10,
            "初级": 0.05,
            "中级": 0.00,
            "高级": -0.10
        }
        
        acc = base_accuracy + difficulty_factor.get(problem.get("difficulty", ""), 0)
        return random.random() < acc
    
    def _generate_portfolio_problems(self, count: int) -> List[Dict]:
        """生成组合优化题目"""
        problems = []
        stocks = ["贵州茅台", "工商银行", "招商银行", "中国平安", "宁德时代"]
        
        for i in range(count):
            problem = {
                "id": f"portfolio-{i+1}",
                "type": "portfolio_optimization",
                "difficulty": "中级",
                "question": f"优化投资组合（第{i+1}题）",
                "context": {
                    "current_holdings": random.sample(stocks, 3),
                    "cash_ratio": random.uniform(0.05, 0.30),
                    "market_condition": random.choice(["bullish", "bearish", "neutral"])
                }
            }
            problems.append(problem)
        
        return problems
    
    def _update_state(self, results: Dict, module: str, phase: str = None):
        """更新训练状态"""
        self.state["total_trainings"] += 1
        self.state["total_problems"] += results["total"]
        self.state["total_correct"] += results["correct"]
        
        if module in self.state["by_module"]:
            self.state["by_module"][module]["total"] += results["total"]
            self.state["by_module"][module]["correct"] += results["correct"]
        
        if phase and phase in self.state["by_phase"]:
            self.state["by_phase"][phase]["total"] += results["total"]
            self.state["by_phase"][phase]["correct"] += results["correct"]
        
        self.state["last_training"] = datetime.now().isoformat()
        self.state["history"].append({
            "date": datetime.now().isoformat(),
            "module": module,
            "total": results["total"],
            "correct": results["correct"],
            "accuracy": results["correct"] / results["total"] if results["total"] > 0 else 0
        })
        
        self._save_state()
    
    def get_report(self) -> Dict:
        """生成学习报告"""
        accuracy = self.state["total_correct"] / self.state["total_problems"] if self.state["total_problems"] > 0 else 0
        
        return {
            "student": self.student_id,
            "total_trainings": self.state["total_trainings"],
            "total_problems": self.state["total_problems"],
            "total_correct": self.state["total_correct"],
            "accuracy": accuracy,
            "by_module": self.state["by_module"],
            "by_phase": self.state["by_phase"],
            "last_training": self.state["last_training"]
        }


import random

if __name__ == "__main__":
    print("🦞 炒股学习训练器测试")
    
    # 测试小陈
    xiaochen = StockLearningTrainer("xiaochen", "standard")
    
    print("\n📊 小陈训练:")
    result1 = xiaochen.train_predict("phase1", 5)
    print(f"   Phase1预测: {result1['correct']}/{result1['total']} ({result1['correct']/result1['total']*100:.1f}%)")
    
    result2 = xiaochen.train_arena(3)
    print(f"   Arena实战: {result2['correct']}/{result2['total']} ({result2['correct']/result2['total']*100:.1f}%)")
    
    result3 = xiaochen.train_portfolio(2)
    print(f"   组合优化: {result3['correct']}/{result3['total']} ({result3['correct']/result3['total']*100:.1f}%)")
    
    report = xiaochen.get_report()
    print(f"\n📈 小陈学习报告:")
    print(f"   总训练: {report['total_trainings']}次")
    print(f"   总题数: {report['total_problems']}")
    print(f"   总正确: {report['total_correct']}")
    print(f"   准确率: {report['accuracy']*100:.1f}%")
    
    print("\n✅ 炒股学习训练器测试完成")
