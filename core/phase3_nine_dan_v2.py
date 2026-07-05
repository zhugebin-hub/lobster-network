#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Phase 3 - 九段方案 v2.0
改进点：
1. 压缩前期（入门~10级从7周压缩到4周）
2. 动态调整（每2周评估，达标跳级，未达标延长）
3. 实战优先（减少纯题目量，增加对局+复盘比重）
4. 高级阶段具体化（七段以上增加AI对局分析、名局研究）

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v2.0
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

# ============================================================
# 配置
# ============================================================

class Config:
    """九段方案v2.0配置"""
    
    # 段位路径（优化后）
    RANK_PATH = {
        "入门": {
            "level": "30级",
            "duration_weeks": 1,  # 原2周→1周
            "skills": ["基本规则", "吃子技巧", "基本死活"],
            "problem_count": 50,   # 原100题→50题
            "game_count": 15,      # 原20局→15局
            "review_count": 5,     # 新增：复盘局数
            "target_accuracy": 0.85,
        },
        "15级": {
            "level": "15级",
            "duration_weeks": 1,   # 原2周→1周
            "skills": ["基本死活", "简单手筋", "基本定式"],
            "problem_count": 100,  # 原200题→100题
            "game_count": 25,      # 原30局→25局
            "review_count": 10,
            "target_accuracy": 0.80,
        },
        "10级": {
            "level": "10级",
            "duration_weeks": 2,   # 原3周→2周
            "skills": ["中级死活", "中级手筋", "常见定式", "基础布局"],
            "problem_count": 150,  # 原300题→150题
            "game_count": 35,      # 原40局→35局
            "review_count": 15,
            "target_accuracy": 0.75,
        },
        "5级": {
            "level": "5级",
            "duration_weeks": 3,   # 原3周→3周
            "skills": ["高级死活", "复杂手筋", "复杂定式", "布局理论"],
            "problem_count": 200,  # 原400题→200题
            "game_count": 45,      # 原50局→45局
            "review_count": 20,
            "target_accuracy": 0.70,
        },
        "1级": {
            "level": "1级",
            "duration_weeks": 3,   # 原4周→3周
            "skills": ["超高级死活", "高级手筋组合", "高级布局", "官子基础"],
            "problem_count": 250,  # 原500题→250题
            "game_count": 55,      # 原60局→55局
            "review_count": 25,
            "target_accuracy": 0.65,
        },
        "初段": {
            "level": "初段",
            "duration_weeks": 4,   # 原4周→4周
            "skills": ["职业级死活", "职业级手筋", "完整布局体系", "精确官子", "对局理论"],
            "problem_count": 300,  # 原600题→300题
            "game_count": 70,      # 原80局→70局
            "review_count": 35,    # AI复盘
            "target_accuracy": 0.60,
        },
        "二段": {
            "level": "二段",
            "duration_weeks": 4,   # 原4周→4周
            "skills": ["高级布局理论", "中盘战斗技巧", "官子精算", "AI复盘分析"],
            "problem_count": 350,
            "game_count": 85,
            "review_count": 40,
            "target_accuracy": 0.55,
        },
        "三段": {
            "level": "三段",
            "duration_weeks": 4,   # 原5周→4周
            "skills": ["战略布局", "战术组合", "深度计算力", "棋感培养"],
            "problem_count": 400,
            "game_count": 100,
            "review_count": 50,
            "target_accuracy": 0.50,
            "special_training": ["名局研究", "AI对局分析"],
        },
        "四段": {
            "level": "四段",
            "duration_weeks": 4,   # 原5周→4周
            "skills": ["开局理论体系", "中盘理论", "官子理论", "对局心理"],
            "problem_count": 450,
            "game_count": 120,
            "review_count": 60,
            "target_accuracy": 0.45,
            "special_training": ["比赛模拟", "限时对局"],
        },
        "五段": {
            "level": "五段",
            "duration_weeks": 5,   # 原6周→5周
            "skills": ["高级战略", "创造性下法", "模式识别", "用时管理"],
            "problem_count": 500,
            "game_count": 150,
            "review_count": 75,
            "target_accuracy": 0.40,
            "special_training": ["创造性训练", "高强度比赛", "教学能力"],
        },
        "六段": {
            "level": "六段",
            "duration_weeks": 5,   # 原6周→5周
            "skills": ["全面掌握", "个人风格形成", "教学能力", "深度分析能力"],
            "problem_count": 600,
            "game_count": 180,
            "review_count": 90,
            "target_accuracy": 0.35,
            "special_training": ["风格塑造", "教学相长", "AI创新下法"],
        },
        "七段": {
            "level": "七段",
            "duration_weeks": 5,   # 原7周→5周
            "skills": ["围棋哲学", "创新下法", "领导力", "指导能力"],
            "problem_count": 700,
            "game_count": 200,
            "review_count": 100,
            "target_accuracy": 0.30,
            "special_training": [
                "AI对局深度分析（每局AI胜率波动分析）",
                "名局研究（研究100局职业名局）",
                "创新下法实验（尝试AI新型下法）",
                "指导低段位学员（教学相长）",
            ],
        },
        "八段": {
            "level": "八段",
            "duration_weeks": 6,   # 原7周→6周
            "skills": ["大师级水平", "教学大师", "理论创新", "文化影响力"],
            "problem_count": 800,
            "game_count": 250,
            "review_count": 125,
            "target_accuracy": 0.25,
            "special_training": [
                "理论创新（提出新的围棋理论）",
                "文化传承（编写围棋教材）",
                "AI围棋研究（与AI共同研究新型下法）",
                "国际交流（参加国际围棋赛事）",
            ],
        },
        "九段": {
            "level": "九段",
            "duration_weeks": 6,   # 原8周→6周
            "skills": ["终极掌握", "哲学深度", "艺术表达", "传承与影响"],
            "problem_count": 1000,
            "game_count": 300,
            "review_count": 150,
            "target_accuracy": 0.20,
            "special_training": [
                "哲学+艺术+传承（围棋哲学体系）",
                "AI围棋巅峰对决（与最强AI对局）",
                "传承弟子（培养新学员）",
                "围棋文化遗产（留下围棋遗产）",
            ],
        },
    }
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "type": "稳健型",
            "current_rank": "30级",
            "target_rank": "九段",
            "strengths": ["基础扎实", "稳定性好", "累计对局量大"],
            "weaknesses": ["推理力不足", "高级题准确率低"],
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "type": "加速型",
            "current_rank": "25级",
            "target_rank": "九段",
            "strengths": ["入门题98%准确率", "解题速度快"],
            "weaknesses": ["反思力不足", "中级手筋需加强"],
        },
        "qoder": {
            "name": "qoder",
            "type": "实战型",
            "current_rank": "25级",
            "target_rank": "九段",
            "strengths": ["高级题准确率65%", "实战对局能力强"],
            "weaknesses": ["训练量偏少", "缺乏系统性"],
        },
    }


# ============================================================
# 九段方案生成器 v2.0
# ============================================================

class NineDanPlanV2:
    """九段方案生成器 v2.0"""
    
    def __init__(self):
        self.config = Config()
    
    def generate_plan(self, student_id: str) -> Dict:
        """生成学员九段方案"""
        student = self.config.STUDENTS[student_id]
        current_rank = student["current_rank"]
        
        # 找到当前段位在路径中的位置
        rank_list = list(self.config.RANK_PATH.keys())
        try:
            start_idx = rank_list.index(current_rank) if current_rank in rank_list else 0
        except ValueError:
            start_idx = 0
        
        # 生成方案
        plan = {
            "student_id": student_id,
            "student_name": student["name"],
            "student_type": student["type"],
            "current_rank": current_rank,
            "target_rank": "九段",
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "v2.0",
            "total_duration_weeks": 0,
            "total_problems": 0,
            "total_games": 0,
            "total_reviews": 0,
            "phases": [],
            "milestones": [],
            "dynamic_adjustment": {
                "evaluation_interval_weeks": 2,
                "promotion_rule": "达标跳级，未达标延长1周",
                "acceleration_rule": "连续2周达标，跳过当前阶段",
            },
        }
        
        current_week = 1
        
        for i in range(start_idx, len(rank_list)):
            stage_name = rank_list[i]
            stage_info = self.config.RANK_PATH[stage_name]
            
            phase = {
                "stage": stage_name,
                "level": stage_info["level"],
                "start_week": current_week,
                "end_week": current_week + stage_info["duration_weeks"] - 1,
                "duration_weeks": stage_info["duration_weeks"],
                "skills": stage_info["skills"],
                "problem_count": stage_info["problem_count"],
                "game_count": stage_info["game_count"],
                "review_count": stage_info["review_count"],
                "target_accuracy": stage_info["target_accuracy"],
                "special_training": stage_info.get("special_training", []),
            }
            
            plan["phases"].append(phase)
            plan["total_duration_weeks"] += stage_info["duration_weeks"]
            plan["total_problems"] += stage_info["problem_count"]
            plan["total_games"] += stage_info["game_count"]
            plan["total_reviews"] += stage_info["review_count"]
            
            # 设置里程碑
            if stage_name in ["10级", "1级", "初段", "三段", "五段", "七段", "九段"]:
                plan["milestones"].append({
                    "stage": stage_name,
                    "week": current_week + stage_info["duration_weeks"] - 1,
                    "description": f"达到{stage_name}水平",
                })
            
            current_week += stage_info["duration_weeks"]
        
        return plan
    
    def generate_markdown(self, plan: Dict) -> str:
        """生成Markdown格式方案"""
        md = []
        md.append(f"# 🏯 {plan['student_name']} 围棋九段学习方案 v2.0")
        md.append("")
        md.append(f"> 学员类型：{plan['student_type']}")
        md.append(f"> 当前段位：{plan['current_rank']}")
        md.append(f"> 目标段位：{plan['target_rank']}")
        md.append(f"> 总时长：{plan['total_duration_weeks']}周（v1.0: 66周 → v2.0: {plan['total_duration_weeks']}周）")
        md.append(f"> 总题量：{plan['total_problems']}题（v1.0: 12,000题）")
        md.append(f"> 总对局：{plan['total_games']}局（v1.0: 2,250局）")
        md.append(f"> 总复盘：{plan['total_reviews']}局（新增）")
        md.append(f"> 生成时间：{plan['generated_at']}")
        md.append("")
        
        # 学习路径概览
        md.append("## 📈 学习路径概览")
        md.append("")
        md.append("| 阶段 | 等级 | 周次 | 题量 | 对局 | 复盘 | 准确率 |")
        md.append("|------|------|------|------|------|------|--------|")
        
        for phase in plan["phases"]:
            md.append(f"| {phase['stage']} | {phase['level']} | "
                     f"W{phase['start_week']}-W{phase['end_week']} | "
                     f"{phase['problem_count']} | {phase['game_count']} | "
                     f"{phase['review_count']} | {phase['target_accuracy']:.0%} |")
        
        md.append("")
        
        # 动态调整机制
        md.append("## 🔄 动态调整机制")
        md.append("")
        md.append(f"- **评估周期**：每{plan['dynamic_adjustment']['evaluation_interval_weeks']}周评估一次")
        md.append(f"- **晋升规则**：{plan['dynamic_adjustment']['promotion_rule']}")
        md.append(f"- **加速规则**：{plan['dynamic_adjustment']['acceleration_rule']}")
        md.append("")
        
        # 里程碑
        md.append("## 🎯 里程碑")
        md.append("")
        for milestone in plan["milestones"]:
            md.append(f"- **第{milestone['week']}周**：达到{milestone['stage']} - {milestone['description']}")
        
        md.append("")
        
        # v2.0 改进说明
        md.append("## 📋 v2.0 改进说明")
        md.append("")
        md.append("| 改进项 | v1.0 | v2.0 | 说明 |")
        md.append("|--------|------|------|------|")
        md.append("| 入门~10级周期 | 7周 | 4周 | 压缩前期，快速升级 |")
        md.append("| 七段~九段周期 | 22周 | 17周 | 高级阶段具体化 |")
        md.append("| 总题量 | 12,000题 | 按需调整 | 减少纯题目量 |")
        md.append("| 复盘机制 | 无 | 每阶段强制复盘 | 新增AI复盘 |")
        md.append("| 动态调整 | 无 | 每2周评估 | 达标跳级/未达标延长 |")
        md.append("| 高级阶段 | 空洞 | 具体化 | AI对局分析+名局研究 |")
        
        md.append("")
        md.append("---")
        md.append(f"*方案由诸葛马 (Hermes) 九段方案 v2.0 自动生成*")
        
        return "\n".join(md)


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="九段方案 v2.0")
    parser.add_argument("action", choices=["generate", "summary"],
                       help="操作: generate(生成方案) | summary(方案总结)")
    parser.add_argument("--student", type=str, help="学员ID")
    
    args = parser.parse_args()
    generator = NineDanPlanV2()
    
    if args.action == "generate":
        if args.student:
            plan = generator.generate_plan(args.student)
            md = generator.generate_markdown(plan)
            print(md)
            
            # 保存方案
            output_dir = "/home/admin/lobster-network/docs/nine_dan_plan_v2"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存JSON
            json_file = os.path.join(output_dir, f"plan_{args.student}_{timestamp}.json")
            with open(json_file, "w") as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
            
            # 保存Markdown
            md_file = os.path.join(output_dir, f"plan_{args.student}_{timestamp}.md")
            with open(md_file, "w") as f:
                f.write(md)
            
            print(f"\n📝 方案已保存: {json_file}, {md_file}")
        else:
            # 生成所有学员方案
            for student_id in generator.config.STUDENTS:
                plan = generator.generate_plan(student_id)
                md = generator.generate_markdown(plan)
                print(f"\n{'='*60}")
                print(f"📝 {generator.config.STUDENTS[student_id]['name']} 九段方案 v2.0")
                print(f"   总时长：{plan['total_duration_weeks']}周")
                print(f"   总题量：{plan['total_problems']}题")
                print(f"   总对局：{plan['total_games']}局")
                print(f"   总复盘：{plan['total_reviews']}局")
    
    elif args.action == "summary":
        print("九段方案 v2.0 改进总结：")
        print("1. 压缩前期：入门~10级从7周压缩到4周")
        print("2. 动态调整：每2周评估，达标跳级，未达标延长")
        print("3. 实战优先：减少纯题目量，增加对局+复盘比重")
        print("4. 高级阶段具体化：七段以上增加AI对局分析、名局研究")


if __name__ == "__main__":
    main()
