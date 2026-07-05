#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Phase 3 - 段位晋升机制
功能：
1. 基于训练数据自动评估段位晋升条件
2. 达标自动晋升，未达标延长训练
3. 晋升考核（理论+实战）
4. 晋升历史记录

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# ============================================================
# 配置
# ============================================================

class Config:
    """段位晋升配置"""
    
    # 段位体系
    RANKS = [
        "30级", "25级", "20级", "15级", "10级", "5级", "1级",
        "初段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"
    ]
    
    # 晋升条件
    PROMOTION_CRITERIA = {
        "30级→25级": {
            "min_accuracy": 0.80,
            "min_win_rate": 0.45,
            "min_problems": 100,
            "min_games": 20,
            "required_modules": ["基本规则", "吃子技巧", "基本死活"],
            "description": "入门→基础：掌握基本规则和吃子技巧",
        },
        "25级→20级": {
            "min_accuracy": 0.75,
            "min_win_rate": 0.50,
            "min_problems": 300,
            "min_games": 50,
            "required_modules": ["基本死活", "简单手筋", "基本定式"],
            "description": "基础→中级：掌握基本死活和简单手筋",
        },
        "20级→15级": {
            "min_accuracy": 0.75,
            "min_win_rate": 0.50,
            "min_problems": 600,
            "min_games": 100,
            "required_modules": ["中级死活", "中级手筋", "常见定式"],
            "description": "中级：掌握中级死活和常见定式",
        },
        "15级→10级": {
            "min_accuracy": 0.70,
            "min_win_rate": 0.55,
            "min_problems": 1000,
            "min_games": 200,
            "required_modules": ["高级死活", "复杂手筋", "布局理论"],
            "description": "进阶：掌握高级死活和布局理论",
        },
        "10级→5级": {
            "min_accuracy": 0.65,
            "min_win_rate": 0.55,
            "min_problems": 2000,
            "min_games": 400,
            "required_modules": ["超高级死活", "高级手筋", "官子基础"],
            "description": "高级：掌握超高级死活和官子",
        },
        "5级→1级": {
            "min_accuracy": 0.60,
            "min_win_rate": 0.60,
            "min_problems": 3000,
            "min_games": 600,
            "required_modules": ["职业级死活", "职业级手筋", "完整布局"],
            "description": "专家级：掌握职业级技能",
        },
        "1级→初段": {
            "min_accuracy": 0.55,
            "min_win_rate": 0.60,
            "min_problems": 5000,
            "min_games": 1000,
            "required_modules": ["综合训练", "实战对局", "AI复盘"],
            "description": "业余初段：具备完整对局能力",
        },
    }
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "current_rank": "30级",
            "target_rank": "25级",
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "current_rank": "25级",
            "target_rank": "20级",
        },
        "qoder": {
            "name": "qoder",
            "current_rank": "25级",
            "target_rank": "20级",
        },
    }
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    PROMOTION_DIR = f"{SHARED_DIR}promotions/"
    PROFILE_DIR = f"{SHARED_DIR}profiles/"


# ============================================================
# 段位晋升引擎
# ============================================================

class PromotionEngine:
    """段位晋升引擎"""
    
    def __init__(self):
        self.config = Config()
        self._init_dirs()
    
    def _init_dirs(self):
        os.makedirs(self.config.PROMOTION_DIR, exist_ok=True)
    
    # --- 核心：评估晋升条件 ---
    
    def evaluate_promotion(self, student_id: str, training_data: Dict) -> Dict:
        """
        评估学员是否满足晋升条件
        
        training_data 格式:
        {
            "accuracy": 0.85,
            "win_rate": 0.60,
            "total_problems": 500,
            "total_games": 100,
            "completed_modules": ["基本规则", "吃子技巧", "基本死活"],
            "recent_performance": [...],  # 最近训练记录
        }
        """
        student = self.config.STUDENTS[student_id]
        current_rank = student["current_rank"]
        target_rank = student["target_rank"]
        
        # 查找晋升条件
        criteria_key = f"{current_rank}→{target_rank}"
        criteria = self.config.PROMOTION_CRITERIA.get(criteria_key)
        
        if not criteria:
            return {
                "student_id": student_id,
                "status": "no_criteria",
                "message": f"未找到{current_rank}→{target_rank}的晋升条件",
            }
        
        # 评估各项条件
        results = {
            "student_id": student_id,
            "student_name": student["name"],
            "current_rank": current_rank,
            "target_rank": target_rank,
            "criteria": criteria,
            "evaluations": {},
            "overall_passed": False,
            "promotion_date": None,
        }
        
        # 1. 准确率
        accuracy = training_data.get("accuracy", 0)
        accuracy_passed = accuracy >= criteria["min_accuracy"]
        results["evaluations"]["accuracy"] = {
            "current": accuracy,
            "required": criteria["min_accuracy"],
            "passed": accuracy_passed,
            "gap": round(criteria["min_accuracy"] - accuracy, 3),
        }
        
        # 2. 胜率
        win_rate = training_data.get("win_rate", 0)
        win_rate_passed = win_rate >= criteria["min_win_rate"]
        results["evaluations"]["win_rate"] = {
            "current": win_rate,
            "required": criteria["min_win_rate"],
            "passed": win_rate_passed,
            "gap": round(criteria["min_win_rate"] - win_rate, 3),
        }
        
        # 3. 题目数
        total_problems = training_data.get("total_problems", 0)
        problems_passed = total_problems >= criteria["min_problems"]
        results["evaluations"]["total_problems"] = {
            "current": total_problems,
            "required": criteria["min_problems"],
            "passed": problems_passed,
            "gap": criteria["min_problems"] - total_problems,
        }
        
        # 4. 对局数
        total_games = training_data.get("total_games", 0)
        games_passed = total_games >= criteria["min_games"]
        results["evaluations"]["total_games"] = {
            "current": total_games,
            "required": criteria["min_games"],
            "passed": games_passed,
            "gap": criteria["min_games"] - total_games,
        }
        
        # 5. 必修模块
        completed_modules = training_data.get("completed_modules", [])
        required_modules = criteria["required_modules"]
        missing_modules = [m for m in required_modules if m not in completed_modules]
        modules_passed = len(missing_modules) == 0
        results["evaluations"]["required_modules"] = {
            "completed": completed_modules,
            "required": required_modules,
            "missing": missing_modules,
            "passed": modules_passed,
        }
        
        # 总体评估
        all_passed = all(
            ev.get("passed", False) 
            for ev in results["evaluations"].values()
        )
        results["overall_passed"] = all_passed
        
        if all_passed:
            results["promotion_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results["status"] = "promoted"
            results["message"] = f"🎉 恭喜{student['name']}晋升为{target_rank}！"
        else:
            results["status"] = "not_ready"
            failed_count = sum(1 for ev in results["evaluations"].values() if not ev.get("passed", False))
            results["message"] = f"尚未达到晋升条件，还有{failed_count}项未达标"
        
        return results
    
    # --- 晋升执行 ---
    
    def execute_promotion(self, student_id: str, evaluation: Dict) -> Dict:
        """执行晋升"""
        if not evaluation.get("overall_passed", False):
            return {"status": "error", "message": "晋升条件未满足"}
        
        student = self.config.STUDENTS[student_id]
        old_rank = student["current_rank"]
        new_rank = student["target_rank"]
        
        # 更新学员段位
        student["current_rank"] = new_rank
        # 设置下一个目标
        current_idx = self.config.RANKS.index(old_rank)
        if current_idx + 2 < len(self.config.RANKS):
            student["target_rank"] = self.config.RANKS[current_idx + 2]
        else:
            student["target_rank"] = "九段"
        
        # 保存晋升记录
        promotion_record = {
            "student_id": student_id,
            "student_name": student["name"],
            "old_rank": old_rank,
            "new_rank": new_rank,
            "promotion_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "evaluation": evaluation,
        }
        
        record_file = os.path.join(
            self.config.PROMOTION_DIR,
            f"promotion_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(record_file, "w") as f:
            json.dump(promotion_record, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "message": f"✅ {student['name']} 从{old_rank}晋升为{new_rank}",
            "record": promotion_record,
        }
    
    # --- 晋升历史 ---
    
    def get_promotion_history(self, student_id: str) -> List[Dict]:
        """获取晋升历史"""
        history = []
        promotion_dir = self.config.PROMOTION_DIR
        
        for filename in sorted(os.listdir(promotion_dir)):
            if filename.startswith(f"promotion_{student_id}_"):
                filepath = os.path.join(promotion_dir, filename)
                try:
                    with open(filepath) as f:
                        record = json.load(f)
                    history.append(record)
                except:
                    continue
        
        return history
    
    # --- 晋升报告 ---
    
    def generate_promotion_report(self, student_id: str, evaluation: Dict) -> str:
        """生成晋升评估报告（Markdown）"""
        student = self.config.STUDENTS[student_id]
        
        md = []
        md.append(f"# 🏅 {student['name']} 晋升评估报告")
        md.append(f"\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append(f"> 当前段位：{evaluation['current_rank']}")
        md.append(f"> 目标段位：{evaluation['target_rank']}")
        md.append("")
        
        # 评估结果
        md.append("## 📊 评估结果")
        md.append("")
        
        if evaluation["overall_passed"]:
            md.append(f"🎉 **评估通过！{student['name']} 已晋升为{evaluation['target_rank']}！**")
        else:
            md.append(f"⚠️ **评估未通过**，还有改进空间")
        
        md.append("")
        md.append("| 评估项 | 当前值 | 要求值 | 状态 |")
        md.append("|--------|--------|--------|------|")
        
        for key, ev in evaluation.get("evaluations", {}).items():
            status = "✅" if ev.get("passed", False) else "❌"
            
            if key == "accuracy":
                md.append(f"| 准确率 | {ev['current']:.1%} | {ev['required']:.1%} | {status} |")
            elif key == "win_rate":
                md.append(f"| 胜率 | {ev['current']:.1%} | {ev['required']:.1%} | {status} |")
            elif key == "total_problems":
                md.append(f"| 题目数 | {ev['current']} | {ev['required']} | {status} |")
            elif key == "total_games":
                md.append(f"| 对局数 | {ev['current']} | {ev['required']} | {status} |")
            elif key == "required_modules":
                md.append(f"| 必修模块 | {len(ev['completed'])}/{len(ev['required'])} | {len(ev['required'])} | {status} |")
                if ev.get("missing"):
                    md.append(f"\n  **缺失模块**：{', '.join(ev['missing'])}")
        
        md.append("")
        
        # 改进建议
        if not evaluation["overall_passed"]:
            md.append("## 💡 改进建议")
            md.append("")
            
            for key, ev in evaluation.get("evaluations", {}).items():
                if not ev.get("passed", False):
                    if "gap" in ev:
                        gap = ev["gap"]
                        if key == "accuracy":
                            md.append(f"- **准确率**：当前{ev['current']:.1%}，需提升{gap:.1%}达到{ev['required']:.1%}")
                        elif key == "win_rate":
                            md.append(f"- **胜率**：当前{ev['current']:.1%}，需提升{gap:.1%}达到{ev['required']:.1%}")
                        elif key == "total_problems":
                            md.append(f"- **题目数**：当前{ev['current']}，还需完成{gap}题")
                        elif key == "total_games":
                            md.append(f"- **对局数**：当前{ev['current']}，还需完成{gap}局")
                        elif key == "required_modules" and ev.get("missing"):
                            md.append(f"- **必修模块**：还需完成{', '.join(ev['missing'])}")
            
            md.append("")
        
        md.append("---")
        md.append(f"*报告由诸葛马 (Hermes) 段位晋升系统 v1.0 自动生成*")
        
        return "\n".join(md)


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="段位晋升机制")
    parser.add_argument("action", choices=["evaluate", "promote", "history", "report"],
                       help="操作: evaluate(评估) | promote(晋升) | history(历史) | report(报告)")
    parser.add_argument("--student", type=str, required=True, help="学员ID")
    parser.add_argument("--training-data", type=str, help="训练数据文件（用于evaluate）")
    
    args = parser.parse_args()
    engine = PromotionEngine()
    
    if args.action == "evaluate":
        if args.training_data and os.path.exists(args.training_data):
            with open(args.training_data) as f:
                training_data = json.load(f)
            evaluation = engine.evaluate_promotion(args.student, training_data)
            print(json.dumps(evaluation, ensure_ascii=False, indent=2))
        else:
            print("❌ 请提供有效的训练数据文件")
    
    elif args.action == "promote":
        # 需要先评估
        print("❌ 请先运行 evaluate 评估晋升条件")
    
    elif args.action == "history":
        history = engine.get_promotion_history(args.student)
        print(json.dumps(history, ensure_ascii=False, indent=2))
    
    elif args.action == "report":
        print("❌ 请先运行 evaluate 生成评估结果")


if __name__ == "__main__":
    main()
