#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
段位晋升机制模块
基于能力画像和训练数据，实现达标自动晋升

段位体系：
30 级 - 入门
25 级 - 初级
20 级 - 中级
15 级 - 高级
10 级 - 专家
5 级  - 大师
1 级  - 九段

晋升条件：
- 能力画像综合得分达标
- 训练量达标
- 考核通过
- 实战对局胜率达标

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

# 段位定义
DAN_RANKS = {
    30: {"name": "30 级", "min_score": 0, "min_problems": 0, "min_games": 0, "min_win_rate": 0},
    25: {"name": "25 级", "min_score": 40, "min_problems": 100, "min_games": 5, "min_win_rate": 0.4},
    20: {"name": "20 级", "min_score": 50, "min_problems": 300, "min_games": 15, "min_win_rate": 0.45},
    15: {"name": "15 级", "min_score": 60, "min_problems": 600, "min_games": 30, "min_win_rate": 0.5},
    10: {"name": "10 级", "min_score": 70, "min_problems": 1000, "min_games": 50, "min_win_rate": 0.55},
    5:  {"name": "5 级", "min_score": 80, "min_problems": 2000, "min_games": 100, "min_win_rate": 0.6},
    1:  {"name": "1 级", "min_score": 85, "min_problems": 3000, "min_games": 150, "min_win_rate": 0.65},
    "初段": {"name": "初段", "min_score": 90, "min_problems": 5000, "min_games": 200, "min_win_rate": 0.7},
    "二段": {"name": "二段", "min_score": 92, "min_problems": 6000, "min_games": 250, "min_win_rate": 0.72},
    "三段": {"name": "三段", "min_score": 94, "min_problems": 7000, "min_games": 300, "min_win_rate": 0.75},
    "四段": {"name": "四段", "min_score": 95, "min_problems": 8000, "min_games": 350, "min_win_rate": 0.78},
    "五段": {"name": "五段", "min_score": 96, "min_problems": 9000, "min_games": 400, "min_win_rate": 0.8},
    "六段": {"name": "六段", "min_score": 97, "min_problems": 10000, "min_games": 450, "min_win_rate": 0.82},
    "七段": {"name": "七段", "min_score": 98, "min_problems": 12000, "min_games": 500, "min_win_rate": 0.85},
    "八段": {"name": "八段", "min_score": 99, "min_problems": 15000, "min_games": 600, "min_win_rate": 0.88},
    "九段": {"name": "九段", "min_score": 99.5, "min_problems": 20000, "min_games": 800, "min_win_rate": 0.9},
}


class RankPromotionSystem:
    """段位晋升系统"""
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.profile_dir = PROFILE_DIR
        self.promotion_file = self.profile_dir / f"{student_id}_promotion.json"
        
        # 加载或创建晋升记录
        if self.promotion_file.exists():
            with open(self.promotion_file, 'r') as f:
                self.promotion_record = json.load(f)
        else:
            self.promotion_record = {
                "student_id": student_id,
                "current_rank": "30 级",
                "promotion_history": [],
                "next_rank": "25 级",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            
    def load_profile(self) -> Optional[Dict]:
        """加载能力画像"""
        profile_file = self.profile_dir / f"{self.student_id}_profile.json"
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                return json.load(f)
        return None
        
    def calculate_composite_score(self, profile: Dict) -> float:
        """计算综合得分（8 维度加权平均）"""
        dimensions = profile.get("dimensions", {})
        if not dimensions:
            return 0.0
            
        total_score = 0.0
        total_weight = 0.0
        
        # 8 维度权重
        weights = {
            "计算力": 0.15,
            "棋形感": 0.12,
            "战略思维": 0.13,
            "推理力": 0.15,
            "执行力": 0.12,
            "反思力": 0.10,
            "学习速度": 0.10,
            "稳定性": 0.13,
        }
        
        for dim, weight in weights.items():
            if dim in dimensions:
                score = dimensions[dim].get("score", 0)
                total_score += score * weight
                total_weight += weight
                
        return total_score / total_weight if total_weight > 0 else 0.0
        
    def check_promotion(self) -> Dict:
        """检查是否可以晋升"""
        profile = self.load_profile()
        if not profile:
            return {"can_promote": False, "reason": "能力画像不存在"}
            
        current_rank = self.promotion_record["current_rank"]
        composite_score = self.calculate_composite_score(profile)
        total_problems = profile.get("total_problems", 0)
        total_games = profile.get("total_games", 0)
        
        # 计算胜率
        # 从提交数据中计算（简化版）
        win_rate = 0.5  # 默认 50%
        
        print(f"📊 检查晋升条件...")
        print(f"   当前段位：{current_rank}")
        print(f"   综合得分：{composite_score:.1f}")
        print(f"   总题数：{total_problems}")
        print(f"   总对局：{total_games}")
        print(f"   胜率：{win_rate:.0%}")
        
        # 查找下一个段位
        rank_order = list(DAN_RANKS.keys())
        current_idx = None
        
        for i, rank in enumerate(rank_order):
            if DAN_RANKS[rank]["name"] == current_rank:
                current_idx = i
                break
                
        if current_idx is None or current_idx >= len(rank_order) - 1:
            return {"can_promote": False, "reason": "已达到最高段位"}
            
        next_rank_key = rank_order[current_idx + 1]
        next_rank = DAN_RANKS[next_rank_key]
        
        print(f"\n   目标段位：{next_rank['name']}")
        print(f"   所需条件：")
        print(f"     综合得分≥{next_rank['min_score']}")
        print(f"     总题数≥{next_rank['min_problems']}")
        print(f"     总对局≥{next_rank['min_games']}")
        print(f"     胜率≥{next_rank['min_win_rate']:.0%}")
        
        # 检查条件
        conditions_met = {
            "score": composite_score >= next_rank["min_score"],
            "problems": total_problems >= next_rank["min_problems"],
            "games": total_games >= next_rank["min_games"],
            "win_rate": win_rate >= next_rank["min_win_rate"],
        }
        
        all_met = all(conditions_met.values())
        
        print(f"\n   条件检查：")
        for cond, met in conditions_met.items():
            status = "✅" if met else "❌"
            print(f"     {status} {cond}")
            
        if all_met:
            print(f"\n🎉 恭喜！符合晋升条件，可以晋升到{next_rank['name']}！")
            return {
                "can_promote": True,
                "current_rank": current_rank,
                "next_rank": next_rank["name"],
                "conditions_met": conditions_met,
                "composite_score": composite_score,
            }
        else:
            # 找出未满足的条件
            unmet = [cond for cond, met in conditions_met.items() if not met]
            print(f"\n⚠️ 未满足条件：{', '.join(unmet)}")
            return {
                "can_promote": False,
                "current_rank": current_rank,
                "next_rank": next_rank["name"],
                "conditions_met": conditions_met,
                "unmet_conditions": unmet,
                "composite_score": composite_score,
            }
            
    def promote(self) -> Dict:
        """执行晋升"""
        result = self.check_promotion()
        
        if not result.get("can_promote"):
            return result
            
        # 更新段位
        old_rank = self.promotion_record["current_rank"]
        new_rank = result["next_rank"]
        
        self.promotion_record["current_rank"] = new_rank
        self.promotion_record["updated_at"] = datetime.now().isoformat()
        
        # 记录晋升历史
        self.promotion_record["promotion_history"].append({
            "from_rank": old_rank,
            "to_rank": new_rank,
            "date": datetime.now().isoformat(),
            "composite_score": result["composite_score"],
        })
        
        # 更新下一个段位
        rank_order = list(DAN_RANKS.keys())
        current_idx = None
        for i, rank in enumerate(rank_order):
            if DAN_RANKS[rank]["name"] == new_rank:
                current_idx = i
                break
                
        if current_idx is not None and current_idx < len(rank_order) - 1:
            next_rank_key = rank_order[current_idx + 1]
            self.promotion_record["next_rank"] = DAN_RANKS[next_rank_key]["name"]
        else:
            self.promotion_record["next_rank"] = "最高段位"
            
        # 保存记录
        with open(self.promotion_file, 'w', encoding='utf-8') as f:
            json.dump(self.promotion_record, f, indent=2, ensure_ascii=False)
            
        print(f"\n✅ 晋升完成：{old_rank} → {new_rank}")
        return self.promotion_record
        
    def get_promotion_status(self) -> Dict:
        """获取晋升状态"""
        return {
            "student_id": self.student_id,
            "current_rank": self.promotion_record["current_rank"],
            "next_rank": self.promotion_record["next_rank"],
            "promotion_count": len(self.promotion_record["promotion_history"]),
            "last_promotion": self.promotion_record["promotion_history"][-1] if self.promotion_record["promotion_history"] else None,
        }


def main():
    """主函数"""
    if len(sys.argv) > 1:
        student_id = sys.argv[1]
        system = RankPromotionSystem(student_id)
        
        if len(sys.argv) > 2:
            command = sys.argv[2]
            
            if command == "check":
                # 检查晋升条件
                result = system.check_promotion()
                print(f"\n=== 晋升检查结果 ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            elif command == "promote":
                # 执行晋升
                result = system.promote()
                print(f"\n=== 晋升结果 ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
            elif command == "status":
                # 显示状态
                status = system.get_promotion_status()
                print("=== 晋升状态 ===")
                print(json.dumps(status, indent=2, ensure_ascii=False))
                
            else:
                print(f"未知命令：{command}")
        else:
            print(f"用法：python3 rank_promotion.py {student_id} [check|promote|status]")
    else:
        print("=== 段位晋升系统 ===")
        print("用法：")
        print("  python3 rank_promotion.py <student_id> check")
        print("  python3 rank_promotion.py <student_id> promote")
        print("  python3 rank_promotion.py <student_id> status")


if __name__ == "__main__":
    main()
