#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
九段方案 V2.0
压缩前期、动态调整、实战优先

核心改进：
1. 压缩前期：减少基础训练天数，快速进入实战
2. 动态调整：基于能力画像实时调整训练内容
3. 实战优先：增加对局比例，以战代练

训练周期：14 天 → 7 天（压缩 50%）
对局比例：20% → 40%（提升 100%）
动态调整：每日基于能力画像更新训练计划

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
TRAINING_DIR = REPO_ROOT / ".shared" / "training" / "go"
PROFILE_DIR = TRAINING_DIR / "profiles"


class NineDanPlanV2:
    """九段方案 V2.0"""
    
    # 训练阶段定义（压缩版）
    PHASES = {
        "phase1": {
            "name": "基础强化",
            "days": [1, 2],
            "focus": "快速掌握基础，进入实战",
            "problem_ratio": 0.6,  # 60% 题目
            "game_ratio": 0.4,     # 40% 对局
        },
        "phase2": {
            "name": "专项突破",
            "days": [3, 4, 5],
            "focus": "针对弱点专项训练",
            "problem_ratio": 0.5,
            "game_ratio": 0.5,
        },
        "phase3": {
            "name": "实战考核",
            "days": [6, 7],
            "focus": "以战代练，考核晋升",
            "problem_ratio": 0.3,
            "game_ratio": 0.7,
        },
    }
    
    # 每日训练量配置
    DAILY_TRAINING = {
        "xiaochen": {
            "base_problems": 80,   # 基础题量（压缩）
            "base_games": 8,       # 基础对局（提升）
            "focus": "推理力 + 实战",
        },
        "zhuguxia": {
            "base_problems": 100,
            "base_games": 10,
            "focus": "反思力 + 实战",
        },
        "qoder": {
            "base_problems": 60,
            "base_games": 6,
            "focus": "基础积累 + 实战",
        },
    }
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.profile_dir = PROFILE_DIR
        
    def load_profile(self) -> Optional[Dict]:
        """加载能力画像"""
        profile_file = self.profile_dir / f"{self.student_id}_profile.json"
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                return json.load(f)
        return None
        
    def generate_dynamic_plan(self, day: int) -> Dict:
        """生成动态训练计划（基于能力画像）"""
        profile = self.load_profile()
        
        # 确定当前阶段
        phase = None
        for phase_key, phase_config in self.PHASES.items():
            if day in phase_config["days"]:
                phase = phase_config
                break
                
        if not phase:
            return {"error": "超出训练周期"}
            
        # 获取学员配置
        student_config = self.DAILY_TRAINING.get(self.student_id, self.DAILY_TRAINING["xiaochen"])
        
        # 基础训练量
        base_problems = student_config["base_problems"]
        base_games = student_config["base_games"]
        
        # 根据阶段调整比例
        problem_count = int(base_problems * phase["problem_ratio"])
        game_count = int(base_games * phase["game_ratio"])
        
        # 基于能力画像动态调整
        adjustments = []
        if profile:
            weaknesses = profile.get("weaknesses", [])
            strengths = profile.get("strengths", [])
            
            # 弱点强化
            for weakness in weaknesses:
                if weakness == "推理力":
                    problem_count += 20
                    adjustments.append(f"推理力薄弱，增加 20 题")
                elif weakness == "计算力":
                    problem_count += 15
                    adjustments.append(f"计算力薄弱，增加 15 题")
                elif weakness == "战略思维":
                    game_count += 3
                    adjustments.append(f"战略思维薄弱，增加 3 局")
                elif weakness == "稳定性":
                    game_count += 2
                    adjustments.append(f"稳定性薄弱，增加 2 局")
                    
            # 优势保持
            for strength in strengths:
                if strength in weaknesses:
                    adjustments.append(f"{strength} 既是优势也是弱点，需平衡训练")
                    
        # 生成计划
        plan = {
            "student_id": self.student_id,
            "day": day,
            "phase": phase["name"],
            "focus": phase["focus"],
            "training": {
                "problems": problem_count,
                "games": game_count,
                "problem_ratio": phase["problem_ratio"],
                "game_ratio": phase["game_ratio"],
            },
            "adjustments": adjustments,
            "timestamp": datetime.now().isoformat(),
        }
        
        return plan
        
    def generate_full_plan(self) -> List[Dict]:
        """生成完整 7 天训练计划"""
        plans = []
        
        for day in range(1, 8):
            plan = self.generate_dynamic_plan(day)
            plans.append(plan)
            
        return plans
        
    def compare_with_v1(self) -> Dict:
        """与 V1 对比"""
        return {
            "comparison": {
                "training_days": {"v1": 14, "v2": 7, "improvement": "-50%"},
                "game_ratio": {"v1": "20%", "v2": "40%", "improvement": "+100%"},
                "dynamic_adjustment": {"v1": "无", "v2": "每日基于画像调整"},
                "problem_count": {"v1": 120, "v2": 80, "improvement": "-33%（但质量更高）"},
            },
            "key_improvements": [
                "压缩前期基础训练，快速进入实战",
                "对局比例提升 100%，以战代练",
                "每日基于能力画像动态调整训练内容",
                "弱点强化 + 优势保持双管齐下",
            ],
        }
        
    def get_training_recommendations(self) -> List[Dict]:
        """获取训练建议"""
        profile = self.load_profile()
        recommendations = []
        
        if not profile:
            return [{"message": "请先完成能力画像更新"}]
            
        # 基于弱点生成建议
        weaknesses = profile.get("weaknesses", [])
        for weakness in weaknesses:
            if weakness == "推理力":
                recommendations.append({
                    "dimension": "推理力",
                    "action": "每日增加 20 题复杂死活题，必须写分步推理",
                    "priority": "high",
                })
            elif weakness == "计算力":
                recommendations.append({
                    "dimension": "计算力",
                    "action": "限时解题训练，每日 15 题，限时 30 分钟",
                    "priority": "high",
                })
            elif weakness == "战略思维":
                recommendations.append({
                    "dimension": "战略思维",
                    "action": "增加对局数量，每局后写战略复盘",
                    "priority": "medium",
                })
            elif weakness == "稳定性":
                recommendations.append({
                    "dimension": "稳定性",
                    "action": "固定训练时间，减少波动，每日复盘",
                    "priority": "medium",
                })
                
        # 基于优势生成建议
        strengths = profile.get("strengths", [])
        for strength in strengths:
            recommendations.append({
                "dimension": strength,
                "action": f"保持{strength}优势，可作为专项突破方向",
                "priority": "low",
            })
            
        return recommendations


def main():
    """主函数"""
    if len(sys.argv) > 1:
        student_id = sys.argv[1]
        plan = NineDanPlanV2(student_id)
        
        if len(sys.argv) > 2:
            command = sys.argv[2]
            
            if command == "day":
                # 生成指定天数计划
                day = int(sys.argv[3]) if len(sys.argv) > 3 else 1
                result = plan.generate_dynamic_plan(day)
                print(f"=== Day {day} 训练计划 ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            elif command == "full":
                # 生成完整计划
                plans = plan.generate_full_plan()
                print("=== 九段方案 V2.0 - 完整 7 天计划 ===")
                for p in plans:
                    print(f"\nDay {p['day']}: {p['phase']}")
                    print(f"  题目：{p['training']['problems']}")
                    print(f"  对局：{p['training']['games']}")
                    if p.get('adjustments'):
                        print(f"  调整：{', '.join(p['adjustments'])}")
                        
            elif command == "compare":
                # 与 V1 对比
                comparison = plan.compare_with_v1()
                print("=== V1 vs V2 对比 ===")
                print(json.dumps(comparison, indent=2, ensure_ascii=False))
                
            elif command == "recommend":
                # 训练建议
                recs = plan.get_training_recommendations()
                print("=== 训练建议 ===")
                for rec in recs:
                    if "message" in rec:
                        print(f"- {rec['message']}")
                    else:
                        print(f"- {rec['dimension']}: {rec['action']} (优先级：{rec['priority']})")
                        
            else:
                print(f"未知命令：{command}")
        else:
            print(f"用法：python3 nine_dan_plan_v2.py {student_id} [day <n>|full|compare|recommend]")
    else:
        print("=== 九段方案 V2.0 ===")
        print("用法：")
        print("  python3 nine_dan_plan_v2.py <student_id> day <n>")
        print("  python3 nine_dan_plan_v2.py <student_id> full")
        print("  python3 nine_dan_plan_v2.py <student_id> compare")
        print("  python3 nine_dan_plan_v2.py <student_id> recommend")


if __name__ == "__main__":
    main()
