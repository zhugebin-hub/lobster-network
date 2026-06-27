#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 · 海报设计训练引擎
版本: V1.0 | 日期: 2026-06-28
功能: HTML/CSS基础、海报设计进阶、PPT自动生成、设计评估
"""

import json
import os
import random
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class PosterEngine:
    """海报设计训练引擎"""
    
    def __init__(self, problem_dir: str = None):
        self.problem_dir = problem_dir or os.path.join(
            os.path.dirname(__file__), 'problems', 'poster-problems'
        )
        self.problems = self._load_problems()
        self.history = []
    
    def _load_problems(self) -> Dict:
        """加载题库"""
        problems = {"phase1": [], "phase2": [], "phase3": []}
        
        for phase in problems.keys():
            phase_dir = os.path.join(self.problem_dir, phase)
            if os.path.exists(phase_dir):
                problems_file = os.path.join(phase_dir, "problems.json")
                if os.path.exists(problems_file):
                    with open(problems_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        problems[phase] = data.get("problems", [])
        
        return problems
    
    def get_problems(self, phase: str = "phase1", count: int = 5) -> List[Dict]:
        """获取指定阶段的题目"""
        if phase not in self.problems:
            return []
        
        available = self.problems[phase]
        if len(available) <= count:
            return available.copy()
        
        return random.sample(available, count)
    
    def evaluate_design(self, design: Dict) -> Dict:
        """评估设计作品"""
        score = 0
        feedback = []
        
        # 评估维度
        dimensions = {
            "layout": {"weight": 0.25, "name": "布局"},
            "color": {"weight": 0.20, "name": "配色"},
            "typography": {"weight": 0.20, "name": "字体"},
            "content": {"weight": 0.20, "name": "内容"},
            "creativity": {"weight": 0.15, "name": "创意"}
        }
        
        for dim, config in dimensions.items():
            dim_score = design.get(dim, 0)
            weighted_score = dim_score * config["weight"]
            score += weighted_score
            
            if dim_score >= 0.8:
                feedback.append(f"✅ {config['name']}优秀 ({dim_score:.0%})")
            elif dim_score >= 0.6:
                feedback.append(f"⚠️ {config['name']}良好 ({dim_score:.0%})")
            else:
                feedback.append(f"❌ {config['name']}需改进 ({dim_score:.0%})")
        
        return {
            "total_score": score,
            "rating": self._get_rating(score),
            "feedback": feedback,
            "dimensions": dimensions
        }
    
    def _get_rating(self, score: float) -> str:
        """获取评级"""
        if score >= 0.9:
            return "S"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        else:
            return "D"
    
    def generate_ppt_outline(self, topic: str, sections: int = 5) -> Dict:
        """生成PPT大纲"""
        outline = {
            "title": topic,
            "sections": [],
            "total_slides": sections * 3  # 每节3页
        }
        
        for i in range(1, sections + 1):
            outline["sections"].append({
                "section": i,
                "title": f"第{i}部分：{topic}相关内容",
                "slides": [
                    {"slide": 1, "type": "标题页", "content": f"第{i}部分标题"},
                    {"slide": 2, "type": "内容页", "content": f"第{i}部分核心内容"},
                    {"slide": 3, "type": "总结页", "content": f"第{i}部分总结"}
                ]
            })
        
        return outline
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = sum(len(probs) for probs in self.problems.values())
        return {
            "total_problems": total,
            "by_phase": {k: len(v) for k, v in self.problems.items()},
            "training_sessions": len(self.history)
        }


if __name__ == "__main__":
    engine = PosterEngine()
    print("🦞 海报设计引擎测试")
    print(f"   题库: {engine.get_stats()}")
    
    # 测试评估
    test_design = {
        "layout": 0.85,
        "color": 0.90,
        "typography": 0.75,
        "content": 0.80,
        "creativity": 0.88
    }
    
    result = engine.evaluate_design(test_design)
    print(f"\n📊 设计评估:")
    print(f"   总分: {result['total_score']:.2f}")
    print(f"   评级: {result['rating']}")
    for fb in result['feedback']:
        print(f"   {fb}")
    
    print("\n✅ 海报设计引擎测试完成")
