#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态能力画像模块
基于真实训练数据更新学员 8 维度能力得分

8 维度能力模型：
1. 计算力 - 解题准确率和思考时间
2. 棋形感 - 手筋题表现
3. 战略思维 - 对局表现
4. 推理力 - 复杂死活题表现
5. 执行力 - 任务完成率
6. 反思力 - 错题分析质量
7. 学习速度 - 进步曲线
8. 稳定性 - 表现波动

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import math

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
TRAINING_DIR = REPO_ROOT / ".shared" / "training" / "go"
QUEUE_DIR = REPO_ROOT / "lobster-data" / "messages" / "queue"
PROFILE_DIR = TRAINING_DIR / "profiles"

# 8 维度能力定义
DIMENSIONS = {
    "计算力": {
        "weight": 0.15,
        "data_sources": ["problem_accuracy", "thinking_time"],
        "description": "解题准确率和思考速度",
    },
    "棋形感": {
        "weight": 0.12,
        "data_sources": ["tesuji_accuracy", "tesuji_speed"],
        "description": "手筋识别和运用能力",
    },
    "战略思维": {
        "weight": 0.13,
        "data_sources": ["game_win_rate", "game_review_quality"],
        "description": "全局判断和战略规划能力",
    },
    "推理力": {
        "weight": 0.15,
        "data_sources": ["life_death_accuracy", "complex_problem_solving"],
        "description": "复杂死活题推理能力",
    },
    "执行力": {
        "weight": 0.12,
        "data_sources": ["task_completion_rate", "submission_timeliness"],
        "description": "任务完成率和及时性",
    },
    "反思力": {
        "weight": 0.10,
        "data_sources": ["wrong_book_analysis", "self_improvement"],
        "description": "错题分析和自我改进能力",
    },
    "学习速度": {
        "weight": 0.10,
        "data_sources": ["accuracy_improvement", "level_progression"],
        "description": "技能提升速度",
    },
    "稳定性": {
        "weight": 0.13,
        "data_sources": ["performance_consistency", "variance"],
        "description": "表现稳定性和一致性",
    },
}


class DynamicAbilityProfile:
    """动态能力画像"""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.training_dir = TRAINING_DIR
        self.profile_dir = PROFILE_DIR
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载或创建画像
        self.profile_file = self.profile_dir / f"{student_id}_profile.json"
        if self.profile_file.exists():
            with open(self.profile_file, 'r') as f:
                self.profile = json.load(f)
        else:
            self.profile = self._create_default_profile()
            
    def _create_default_profile(self) -> Dict:
        """创建默认画像"""
        return {
            "student_id": self.student_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "level": 30,  # 初始等级
            "total_problems": 0,
            "total_games": 0,
            "dimensions": {dim: {"score": 50, "history": []} for dim in DIMENSIONS},
            "training_history": [],
            "weaknesses": [],
            "strengths": [],
        }
        
    def load_submission_data(self) -> List[Dict]:
        """加载学员提交数据"""
        from_dir = self.training_dir / f"from-{self.student_id}"
        submissions = []
        
        if from_dir.exists():
            for sub_file in sorted(from_dir.glob("*.json")):
                try:
                    with open(sub_file, 'r') as f:
                        data = json.load(f)
                    data["_file"] = sub_file.name
                    submissions.append(data)
                except Exception as e:
                    print(f"⚠️ 加载 {sub_file.name} 失败：{e}")
                    
        return submissions
        
    def calculate_dimension_score(self, dimension: str, submissions: List[Dict]) -> float:
        """计算单个维度得分"""
        if not submissions:
            return 50.0  # 默认中等水平
            
        scores = []
        
        if dimension == "计算力":
            # 基于解题准确率和思考时间
            for sub in submissions:
                problems = sub.get("problems", [])
                # 兼容整数和列表格式
                if isinstance(problems, int):
                    continue  # 整数格式无法计算准确率
                if problems:
                    correct = sum(1 for p in problems if p.get("is_correct", False))
                    accuracy = correct / len(problems)
                    
                    # 思考时间越短越好
                    times = [p.get("thinking_time", 60) for p in problems if "thinking_time" in p]
                    avg_time = sum(times) / len(times) if times else 60
                    time_score = max(0, 100 - avg_time)  # 60 秒得 40 分
                    
                    scores.append(accuracy * 70 + time_score * 0.3)
                    
        elif dimension == "棋形感":
            # 基于手筋题表现
            for sub in submissions:
                problems = sub.get("problems", [])
                if isinstance(problems, int):
                    continue
                tesuji = [p for p in problems if p.get("category") == "手筋" or "手筋" in str(p.get("title", ""))]
                if tesuji:
                    correct = sum(1 for p in tesuji if p.get("is_correct", False))
                    scores.append(correct / len(tesuji) * 100)
                    
        elif dimension == "战略思维":
            # 基于对局表现
            for sub in submissions:
                games = sub.get("games", [])
                if isinstance(games, int):
                    continue
                if games:
                    wins = sum(1 for g in games if g.get("is_win", False))
                    scores.append(wins / len(games) * 100)
                    
        elif dimension == "推理力":
            # 基于复杂死活题表现
            for sub in submissions:
                problems = sub.get("problems", [])
                if isinstance(problems, int):
                    continue
                life_death = [p for p in problems if p.get("category") == "死活" or "死活" in str(p.get("title", ""))]
                if life_death:
                    correct = sum(1 for p in life_death if p.get("is_correct", False))
                    scores.append(correct / len(life_death) * 100)
                    
        elif dimension == "执行力":
            # 基于任务完成率
            total_tasks = len(submissions)
            completed = 0
            for s in submissions:
                problems = s.get("problems", [])
                if isinstance(problems, int):
                    if problems > 0:
                        completed += 1
                elif len(problems) > 0:
                    completed += 1
            if total_tasks > 0:
                scores.append(completed / total_tasks * 100)
                
        elif dimension == "反思力":
            # 基于错题分析质量
            for sub in submissions:
                problems = sub.get("problems", [])
                if isinstance(problems, int):
                    continue
                wrong = [p for p in problems if not p.get("is_correct", False)]
                if wrong:
                    # 检查是否有分析内容
                    analyzed = sum(1 for p in wrong if p.get("analysis") or p.get("thinking_process"))
                    scores.append(analyzed / len(wrong) * 100)
                    
        elif dimension == "学习速度":
            # 基于准确率进步曲线
            accuracies = []
            for sub in submissions:
                problems = sub.get("problems", [])
                if isinstance(problems, int):
                    continue
                if problems:
                    correct = sum(1 for p in problems if p.get("is_correct", False))
                    accuracies.append(correct / len(problems))
                    
            if len(accuracies) >= 2:
                # 计算进步趋势
                improvement = accuracies[-1] - accuracies[0]
                scores.append(max(0, min(100, 50 + improvement * 100)))
                
        elif dimension == "稳定性":
            # 基于表现波动
            accuracies = []
            for sub in submissions:
                problems = sub.get("problems", [])
                if isinstance(problems, int):
                    continue
                if problems:
                    correct = sum(1 for p in problems if p.get("is_correct", False))
                    accuracies.append(correct / len(problems))
                    
            if len(accuracies) >= 2:
                # 计算标准差（波动越小越稳定）
                mean = sum(accuracies) / len(accuracies)
                variance = sum((x - mean) ** 2 for x in accuracies) / len(accuracies)
                std_dev = math.sqrt(variance)
                # 标准差 0.1 得 50 分，0.2 得 20 分
                scores.append(max(0, min(100, 100 - std_dev * 400)))
                
        # 计算平均分
        if scores:
            return sum(scores) / len(scores)
        return 50.0
        
    def update_profile(self) -> Dict:
        """更新能力画像"""
        submissions = self.load_submission_data()
        
        print(f"📊 更新 {self.student_id} 能力画像...")
        print(f"   提交数据：{len(submissions)} 份")
        
        # 更新各维度得分
        for dimension in DIMENSIONS:
            score = self.calculate_dimension_score(dimension, submissions)
            
            # 更新画像
            self.profile["dimensions"][dimension]["score"] = round(score, 1)
            self.profile["dimensions"][dimension]["history"].append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "score": round(score, 1),
            })
            
            print(f"   {dimension}: {score:.1f}/100")
            
        # 更新统计（兼容整数和列表格式）
        total_problems = 0
        total_games = 0
        for s in submissions:
            problems = s.get("problems", [])
            games = s.get("games", [])
            if isinstance(problems, int):
                total_problems += problems
            else:
                total_problems += len(problems)
            if isinstance(games, int):
                total_games += games
            else:
                total_games += len(games)
        
        self.profile["total_problems"] = total_problems
        self.profile["total_games"] = total_games
        self.profile["updated_at"] = datetime.now().isoformat()
        
        # 识别优势和劣势
        dimension_scores = {dim: self.profile["dimensions"][dim]["score"] for dim in DIMENSIONS}
        sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1], reverse=True)
        
        self.profile["strengths"] = [d[0] for d in sorted_dims[:2]]
        self.profile["weaknesses"] = [d[0] for d in sorted_dims[-2:]]
        
        # 保存画像
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)
            
        print(f"   画像已保存：{self.profile_file}")
        return self.profile
        
    def get_profile_summary(self) -> Dict:
        """获取画像摘要"""
        summary = {
            "student_id": self.student_id,
            "level": self.profile.get("level", 30),
            "total_problems": self.profile.get("total_problems", 0),
            "total_games": self.profile.get("total_games", 0),
            "dimensions": {},
            "strengths": self.profile.get("strengths", []),
            "weaknesses": self.profile.get("weaknesses", []),
        }
        
        for dim in DIMENSIONS:
            score = self.profile["dimensions"][dim]["score"]
            summary["dimensions"][dim] = {
                "score": score,
                "level": self._score_to_level(score),
            }
            
        return summary
        
    def _score_to_level(self, score: float) -> str:
        """分数转等级"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "E"
            
    def generate_training_recommendations(self) -> List[Dict]:
        """生成训练建议"""
        recommendations = []
        
        # 基于劣势维度生成建议
        for dim in self.profile.get("weaknesses", []):
            if dim == "计算力":
                recommendations.append({
                    "dimension": "计算力",
                    "action": "增加基础题训练，限时解题",
                    "priority": "high",
                })
            elif dim == "棋形感":
                recommendations.append({
                    "dimension": "棋形感",
                    "action": "专项手筋训练，每日 20 题",
                    "priority": "high",
                })
            elif dim == "战略思维":
                recommendations.append({
                    "dimension": "战略思维",
                    "action": "增加对局数量，每局后写复盘",
                    "priority": "medium",
                })
            elif dim == "推理力":
                recommendations.append({
                    "dimension": "推理力",
                    "action": "复杂死活题分步推理训练",
                    "priority": "high",
                })
            elif dim == "执行力":
                recommendations.append({
                    "dimension": "执行力",
                    "action": "设置任务截止时间，超时自动提醒",
                    "priority": "high",
                })
            elif dim == "反思力":
                recommendations.append({
                    "dimension": "反思力",
                    "action": "错题必须写 4 步反思日志",
                    "priority": "medium",
                })
            elif dim == "学习速度":
                recommendations.append({
                    "dimension": "学习速度",
                    "action": "调整难度，保持 70-80% 准确率",
                    "priority": "medium",
                })
            elif dim == "稳定性":
                recommendations.append({
                    "dimension": "稳定性",
                    "action": "固定训练时间，减少波动",
                    "priority": "low",
                })
                
        return recommendations


def main():
    """主函数"""
    if len(sys.argv) > 1:
        student_id = sys.argv[1]
        profile = DynamicAbilityProfile(student_id)
        
        if len(sys.argv) > 2 and sys.argv[2] == "update":
            # 更新画像
            result = profile.update_profile()
            print("\n=== 画像更新完成 ===")
            
        elif len(sys.argv) > 2 and sys.argv[2] == "summary":
            # 显示摘要
            summary = profile.get_profile_summary()
            print("=== 能力画像摘要 ===")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            
        elif len(sys.argv) > 2 and sys.argv[2] == "recommend":
            # 生成建议
            recs = profile.generate_training_recommendations()
            print("=== 训练建议 ===")
            for rec in recs:
                print(f"- {rec['dimension']}: {rec['action']} (优先级：{rec['priority']})")
                
        else:
            print(f"用法：python3 dynamic_ability_profile.py {student_id} [update|summary|recommend]")
    else:
        print("=== 动态能力画像模块 ===")
        print("用法：")
        print("  python3 dynamic_ability_profile.py <student_id> update")
        print("  python3 dynamic_ability_profile.py <student_id> summary")
        print("  python3 dynamic_ability_profile.py <student_id> recommend")


if __name__ == "__main__":
    main()
