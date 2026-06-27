#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 海报设计训练器
版本: V1.0 | 日期: 2026-06-28
功能: 调度海报设计训练、评估设计作品、生成学习报告
"""

import json
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'problems'))
from poster_engine import PosterEngine


class PosterTrainer:
    """海报设计训练器"""
    
    def __init__(self, student_id: str, student_type: str = "standard"):
        self.student_id = student_id
        self.student_type = student_type  # standard/accelerated
        self.engine = PosterEngine()
        self.state_file = os.path.join(
            os.path.dirname(__file__), 'state', f'{student_id}_poster_state.json'
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
            "by_phase": {"phase1": {"total": 0, "correct": 0}, 
                        "phase2": {"total": 0, "correct": 0},
                        "phase3": {"total": 0, "correct": 0}},
            "by_type": {},
            "by_difficulty": {},
            "streak": 0,
            "last_training": None,
            "history": []
        }
    
    def _save_state(self):
        """保存训练状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def train(self, phase: str = "phase1", count: int = 5) -> Dict:
        """执行训练"""
        problems = self.engine.get_problems(phase, count)
        if not problems:
            return {"success": False, "message": f"Phase {phase} 无可用题目"}
        
        results = {
            "student": self.student_id,
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "problems": [],
            "total": len(problems),
            "correct": 0
        }
        
        for prob in problems:
            # 模拟答题（实际应由学员完成）
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
        
        # 更新状态
        self.state["total_trainings"] += 1
        self.state["total_problems"] += results["total"]
        self.state["total_correct"] += results["correct"]
        
        if phase in self.state["by_phase"]:
            self.state["by_phase"][phase]["total"] += results["total"]
            self.state["by_phase"][phase]["correct"] += results["correct"]
        
        self.state["last_training"] = datetime.now().isoformat()
        self.state["history"].append({
            "date": datetime.now().isoformat(),
            "total": results["total"],
            "correct": results["correct"],
            "accuracy": results["correct"] / results["total"] if results["total"] > 0 else 0
        })
        
        self._save_state()
        return results
    
    def _simulate_answer(self, problem: Dict) -> bool:
        """模拟答题（基于学员类型）"""
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
    
    def evaluate_design(self, design: Dict) -> Dict:
        """评估设计作品"""
        return self.engine.evaluate_design(design)
    
    def get_report(self) -> Dict:
        """生成学习报告"""
        accuracy = self.state["total_correct"] / self.state["total_problems"] if self.state["total_problems"] > 0 else 0
        
        return {
            "student": self.student_id,
            "total_trainings": self.state["total_trainings"],
            "total_problems": self.state["total_problems"],
            "total_correct": self.state["total_correct"],
            "accuracy": accuracy,
            "by_phase": self.state["by_phase"],
            "last_training": self.state["last_training"]
        }


import random

if __name__ == "__main__":
    print("🦞 海报设计训练器测试")
    
    # 测试小陈（稳健型）
    xiaochen = PosterTrainer("xiaochen", "standard")
    result1 = xiaochen.train("phase1", 5)
    print(f"\n📊 小陈 Phase1 训练:")
    print(f"   题数: {result1['total']}")
    print(f"   正确: {result1['correct']}")
    print(f"   准确率: {result1['correct']/result1['total']*100:.1f}%")
    
    # 测试诸葛虾（加速型）
    zhuguxia = PosterTrainer("zhuguxia", "accelerated")
    result2 = zhuguxia.train("phase2", 5)
    print(f"\n📊 诸葛虾 Phase2 训练:")
    print(f"   题数: {result2['total']}")
    print(f"   正确: {result2['correct']}")
    print(f"   准确率: {result2['correct']/result2['total']*100:.1f}%")
    
    print("\n✅ 海报设计训练器测试完成")
