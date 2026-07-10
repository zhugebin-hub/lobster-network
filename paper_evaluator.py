#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 多维度评估器 (Multi-Dimensional Evaluator)
支持学术规范、创新性、逻辑性、深度评估，并扩展药物研发域专属维度。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class EvaluationResult:
    """评估结果"""
    eval_id: str
    target_id: str
    domain: str  # general, drug, go
    scores: Dict[str, float]
    weighted_score: float
    feedback: str
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class PaperEvaluator:
    """多维度评估器"""
    
    # 基础维度权重 (通用)
    GENERAL_WEIGHTS = {
        "norm": 0.20,      # 学术规范
        "innovation": 0.25, # 创新性
        "logic": 0.25,     # 逻辑性
        "depth": 0.30      # 深度
    }
    
    # 药物域扩展维度权重
    DRUG_WEIGHTS = {
        "norm": 0.15,
        "innovation": 0.20,
        "logic": 0.20,
        "depth": 0.15,
        "clinical_feasibility": 0.15,  # 临床可行性
        "oit_safety": 0.10,            # OIT 安全性
        "statistical_power": 0.05      # 统计学效力
    }
    
    def __init__(self, base_dir: str = "/home/admin/lobster-network/shared/evaluations"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
        self.history: List[EvaluationResult] = []
        self._load()
        print(f"📊 多维度评估器初始化: {base_dir}")
        
    def _load(self):
        history_file = os.path.join(self.base_dir, "eval_history.json")
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                data = json.load(f)
                self.history = [EvaluationResult(**item) for item in data]
                
    def _save(self):
        history_file = os.path.join(self.base_dir, "eval_history.json")
        with open(history_file, 'w') as f:
            json.dump([e.__dict__ for e in self.history], f, ensure_ascii=False, indent=2)
            
    def evaluate(self, target_id: str, domain: str, scores: Dict[str, float], feedback: str) -> EvaluationResult:
        """执行评估"""
        weights = self.DRUG_WEIGHTS if domain == "drug" else self.GENERAL_WEIGHTS
        
        # 计算加权分
        weighted_score = 0.0
        for dim, weight in weights.items():
            if dim in scores:
                weighted_score += scores[dim] * weight
                
        result = EvaluationResult(
            eval_id=f"EVAL_{len(self.history)+1:03d}",
            target_id=target_id,
            domain=domain,
            scores=scores,
            weighted_score=round(weighted_score, 2),
            feedback=feedback
        )
        self.history.append(result)
        self._save()
        print(f"✅ 评估完成: {target_id} [{domain}] 加权分: {weighted_score:.2f}")
        return result
        
    def get_detailed_feedback(self, eval_id: str) -> Dict[str, Any]:
        """获取详细反馈"""
        for e in self.history:
            if e.eval_id == eval_id:
                return {
                    "eval_id": e.eval_id,
                    "domain": e.domain,
                    "scores": e.scores,
                    "weighted_score": e.weighted_score,
                    "feedback": e.feedback,
                    "timestamp": e.timestamp
                }
        return {}
        
    def generate_report(self) -> Dict[str, Any]:
        """生成评估报告"""
        domain_stats = {}
        for e in self.history:
            if e.domain not in domain_stats:
                domain_stats[e.domain] = {"count": 0, "avg_score": 0.0, "scores": []}
            domain_stats[e.domain]["count"] += 1
            domain_stats[e.domain]["scores"].append(e.weighted_score)
            
        for d in domain_stats:
            scores = domain_stats[d]["scores"]
            domain_stats[d]["avg_score"] = round(sum(scores) / len(scores), 2) if scores else 0
            
        return {
            "total_evaluations": len(self.history),
            "domain_stats": domain_stats,
            "recent_evaluations": [e.__dict__ for e in self.history[-5:]]
        }

# 示例用法
if __name__ == "__main__":
    evaluator = PaperEvaluator()
    
    # 通用论文评估
    evaluator.evaluate(
        target_id="PAPER_GO_001",
        domain="general",
        scores={"norm": 8.5, "innovation": 9.0, "logic": 8.8, "depth": 8.2},
        feedback="围棋布局理论扎实，创新点明确，逻辑严密。"
    )
    
    # 药物域评估 (新增维度)
    evaluator.evaluate(
        target_id="PAPER_DRUG_001",
        domain="drug",
        scores={
            "norm": 8.8,
            "innovation": 9.2,
            "logic": 8.5,
            "depth": 8.9,
            "clinical_feasibility": 8.7,  # 临床可行性
            "oit_safety": 9.0,            # OIT 安全性
            "statistical_power": 8.5      # 统计学效力
        },
        feedback="耐虾肽-1 结构优化合理，临床转化路径清晰。OIT 方案安全性高，统计学效力充足。建议补充长期毒性数据。"
    )
    
    # 生成报告
    report = evaluator.generate_report()
    print("\n📊 评估报告:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    
    print("\n✅ 多维度评估器测试完成")
