#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 v1.0 围棋九段学习方案
目标：将三位学员从当前水平提升至围棋九段

设计原则：
1. 系统性：覆盖围棋所有核心技能（死活、手筋、定式、布局、官子、对局）
2. 个性化：针对每位学员的短板定制训练
3. 渐进性：从入门到九段的完整路径
4. 实战性：大量对局+复盘+AI分析

段位标准（中国围棋协会）：
- 入门（30级）：基本规则、吃子技巧
- 15级：基本死活、简单手筋
- 10级：常见定式、简单布局
- 5级：中级死活、复杂手筋
- 1级：高级死活、布局理论
- 初段：完整对局能力、基础官子
- 二段~九段：逐步提升实战能力和理论水平

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

# ═══════════════════════════════════════════════════════════
# 围棋九段学习路径
# ═══════════════════════════════════════════════════════════

DAN_PATH = {
    "入门": {
        "level": "30级",
        "duration_weeks": 2,
        "skills": {
            "basic_rules": "基本规则（气、提子、禁着点）",
            "capture_techniques": "吃子技巧（征子、枷吃、扑、倒扑）",
            "basic_life_death": "基本死活（两眼活棋、直三、曲三）",
        },
        "training_focus": ["吃子技巧", "基本死活"],
        "problem_count": 100,
        "game_count": 20,
        "target_accuracy": 0.90,
    },
    "15级": {
        "level": "15级",
        "duration_weeks": 2,
        "skills": {
            "life_death": "基本死活（直四、曲四、刀五、花六）",
            "tesuji": "简单手筋（双打吃、倒扑、接不归）",
            "basic_joseki": "基本定式（星位、小目基础定式）",
        },
        "training_focus": ["死活", "手筋"],
        "problem_count": 200,
        "game_count": 30,
        "target_accuracy": 0.85,
    },
    "10级": {
        "level": "10级",
        "duration_weeks": 3,
        "skills": {
            "life_death": "中级死活（大猪嘴、小猪嘴、金柜角）",
            "tesuji": "中级手筋（跨、断、挖、靠）",
            "joseki": "常见定式（中国流、小林流）",
            "fuseki": "基础布局（三连星、中国流）",
        },
        "training_focus": ["死活", "手筋", "定式"],
        "problem_count": 300,
        "game_count": 40,
        "target_accuracy": 0.80,
    },
    "5级": {
        "level": "5级",
        "duration_weeks": 3,
        "skills": {
            "life_death": "高级死活（缓一气劫、紧气劫）",
            "tesuji": "复杂手筋（倒脱靴、黄莺扑蝶）",
            "joseki": "复杂定式（大雪崩、妖刀定式）",
            "fuseki": "布局理论（模样vs实地）",
        },
        "training_focus": ["死活", "手筋", "布局"],
        "problem_count": 400,
        "game_count": 50,
        "target_accuracy": 0.75,
    },
    "1级": {
        "level": "1级",
        "duration_weeks": 4,
        "skills": {
            "life_death": "超高级死活（万年劫、长生、双劫循环）",
            "tesuji": "高级手筋组合",
            "fuseki": "高级布局（宇宙流、三连星变型）",
            "endgame": "官子基础（先手官子、后手官子）",
        },
        "training_focus": ["死活", "布局", "官子"],
        "problem_count": 500,
        "game_count": 60,
        "target_accuracy": 0.70,
    },
    "初段": {
        "level": "初段",
        "duration_weeks": 4,
        "skills": {
            "life_death": "职业级死活",
            "tesuji": "职业级手筋",
            "fuseki": "完整布局体系",
            "endgame": "精确官子计算",
            "game_theory": "对局理论（中盘战斗、形势判断）",
        },
        "training_focus": ["综合训练", "实战对局"],
        "problem_count": 600,
        "game_count": 80,
        "target_accuracy": 0.65,
    },
    "二段": {
        "level": "二段",
        "duration_weeks": 4,
        "skills": {
            "advanced_fuseki": "高级布局理论",
            "middle_game": "中盘战斗技巧",
            "endgame": "官子精算",
            "review": "AI复盘分析",
        },
        "training_focus": ["实战对局", "复盘分析"],
        "problem_count": 700,
        "game_count": 100,
        "target_accuracy": 0.60,
    },
    "三段": {
        "level": "三段",
        "duration_weeks": 5,
        "skills": {
            "strategy": "战略布局",
            "tactics": "战术组合",
            "reading": "深度计算力",
            "intuition": "棋感培养",
        },
        "training_focus": ["高强度对局", "名局研究"],
        "problem_count": 800,
        "game_count": 120,
        "target_accuracy": 0.55,
    },
    "四段": {
        "level": "四段",
        "duration_weeks": 5,
        "skills": {
            "opening_theory": "开局理论体系",
            "middle_game_theory": "中盘理论",
            "endgame_theory": "官子理论",
            "psychology": "对局心理",
        },
        "training_focus": ["理论+实战", "比赛模拟"],
        "problem_count": 900,
        "game_count": 150,
        "target_accuracy": 0.50,
    },
    "五段": {
        "level": "五段",
        "duration_weeks": 6,
        "skills": {
            "advanced_strategy": "高级战略",
            "creative_play": "创造性下法",
            "pattern_recognition": "模式识别",
            "time_management": "用时管理",
        },
        "training_focus": ["创造性训练", "高强度比赛"],
        "problem_count": 1000,
        "game_count": 200,
        "target_accuracy": 0.45,
    },
    "六段": {
        "level": "六段",
        "duration_weeks": 6,
        "skills": {
            "mastery": "全面掌握",
            "style_development": "个人风格形成",
            "teaching": "教学能力",
            "analysis": "深度分析能力",
        },
        "training_focus": ["风格塑造", "教学相长"],
        "problem_count": 1200,
        "game_count": 250,
        "target_accuracy": 0.40,
    },
    "七段": {
        "level": "七段",
        "duration_weeks": 7,
        "skills": {
            "philosophy": "围棋哲学",
            "innovation": "创新下法",
            "leadership": "领导力",
            "mentorship": "指导能力",
        },
        "training_focus": ["哲学思考", "创新实践"],
        "problem_count": 1500,
        "game_count": 300,
        "target_accuracy": 0.35,
    },
    "八段": {
        "level": "八段",
        "duration_weeks": 7,
        "skills": {
            "mastery_level": "大师级水平",
            "teaching_mastery": "教学大师",
            "theory_innovation": "理论创新",
            "cultural_impact": "文化影响力",
        },
        "training_focus": ["理论创新", "文化传承"],
        "problem_count": 1800,
        "game_count": 350,
        "target_accuracy": 0.30,
    },
    "九段": {
        "level": "九段",
        "duration_weeks": 8,
        "skills": {
            "ultimate_mastery": "终极掌握",
            "philosophical_depth": "哲学深度",
            "artistic_expression": "艺术表达",
            "legacy": "传承与影响",
        },
        "training_focus": ["哲学+艺术+传承"],
        "problem_count": 2000,
        "game_count": 500,
        "target_accuracy": 0.25,
    },
}

# ═══════════════════════════════════════════════════════════
# 学员当前状态
# ═══════════════════════════════════════════════════════════

STUDENTS = {
    "qoder": {
        "name": "qoder（小龙虾）",
        "type": "实战型",
        "current_level": "25级",
        "target_dan": "九段",
        "accuracy_baseline": {"入门": 0.95, "初级": 0.85, "中级": 0.75, "高级": 0.65},
        "problem_count": 685,
        "win_rate": 0.86,
        "strengths": ["高级题准确率最高(65%)", "实战对局能力强", "注重质量"],
        "weaknesses": ["训练量偏少(685题)", "缺乏系统性训练计划"],
        "path": ["入门", "15级", "10级", "5级", "1级", "初段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"],
    },
    "xiaochen": {
        "name": "xiaochen（信电大虾）",
        "type": "稳健型",
        "current_level": "30级",
        "target_dan": "九段",
        "accuracy_baseline": {"入门": 0.90, "初级": 0.80, "中级": 0.70, "高级": 0.35},
        "problem_count": 10337,
        "win_rate": 0.75,
        "strengths": ["累计对局量最大(10,337局)", "基础扎实", "稳定性好"],
        "weaknesses": ["高级题准确率最低(35%)", "推理力不足", "倒扑/扑区分不清"],
        "path": ["入门", "15级", "10级", "5级", "1级", "初段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"],
    },
    "zhuguxia": {
        "name": "zhuguxia（诸葛虾）",
        "type": "加速型",
        "current_level": "25级",
        "target_dan": "九段",
        "accuracy_baseline": {"入门": 0.98, "初级": 0.90, "中级": 0.80, "高级": 0.60},
        "problem_count": 6868,
        "win_rate": 0.80,
        "strengths": ["入门题几乎不错(98%)", "解题速度最快", "又快又准"],
        "weaknesses": ["征子路线判断能力不足", "反思力维度可加强"],
        "path": ["入门", "15级", "10级", "5级", "1级", "初段", "二段", "三段", "四段", "五段", "六段", "七段", "八段", "九段"],
    },
}

# ═══════════════════════════════════════════════════════════
# 九段学习方案生成器
# ═══════════════════════════════════════════════════════════

def generate_dan_training_plan(student_id: str) -> Dict[str, Any]:
    """为每位学员生成完整的九段学习方案"""
    student = STUDENTS[student_id]
    
    plan = {
        "student_id": student_id,
        "student_name": student["name"],
        "student_type": student["type"],
        "current_level": student["current_level"],
        "target_level": "九段",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_duration_weeks": 0,
        "phases": [],
        "milestones": [],
        "training_modules": [],
        "evaluation_criteria": {},
    }
    
    # 计算总时长
    total_weeks = 0
    for stage in student["path"]:
        total_weeks += DAN_PATH[stage]["duration_weeks"]
    plan["total_duration_weeks"] = total_weeks
    
    # 生成每个阶段的学习计划
    current_week = 1
    for stage in student["path"]:
        stage_info = DAN_PATH[stage]
        phase = {
            "stage": stage,
            "level": stage_info["level"],
            "start_week": current_week,
            "end_week": current_week + stage_info["duration_weeks"] - 1,
            "duration_weeks": stage_info["duration_weeks"],
            "skills": stage_info["skills"],
            "training_focus": stage_info["training_focus"],
            "problem_count": stage_info["problem_count"],
            "game_count": stage_info["game_count"],
            "target_accuracy": stage_info["target_accuracy"],
            "custom_modules": [],
        }
        
        # 根据学员类型定制
        if student_id == "xiaochen":
            # 小陈需要加强推理力和高级题
            if stage in ["5级", "1级", "初段"]:
                phase["custom_modules"].append({
                    "name": "推理力强化训练",
                    "focus": "推理力",
                    "problems": stage_info["problem_count"] // 2,
                    "method": "分步推理：识别棋形→计算变化→验证结论",
                })
            if stage == "入门":
                phase["custom_modules"].append({
                    "name": "扑与倒扑专项辨析",
                    "focus": "理解力",
                    "problems": 30,
                    "method": "对比训练：扑 vs 倒扑 典型棋形对比",
                })
                
        elif student_id == "zhuguxia":
            # 诸葛虾需要加强反思力和征子路线
            if stage in ["15级", "10级"]:
                phase["custom_modules"].append({
                    "name": "征子路线专项突破",
                    "focus": "推理力",
                    "problems": 50,
                    "method": "征子路线判断：判断引征→计算路线→验证",
                })
            phase["custom_modules"].append({
                "name": "反思日志训练",
                "focus": "反思力",
                "problems": 0,
                "method": "每局后写反思：我的思路→正确思路→差距分析→改进策略",
            })
            
        elif student_id == "qoder":
            # qoder需要增加训练量和系统性
            phase["custom_modules"].append({
                "name": "速率套利训练",
                "focus": "执行力",
                "problems": stage_info["problem_count"],
                "method": "与zhuguxia配对：zhuguxia生成题，qoder解题",
            })
            if stage in ["10级", "5级", "1级"]:
                phase["custom_modules"].append({
                    "name": "系统性知识体系构建",
                    "focus": "理解力",
                    "problems": stage_info["problem_count"] // 2,
                    "method": "按围棋知识体系系统训练：死活→手筋→定式→布局→官子",
                })
        
        plan["phases"].append(phase)
        current_week += stage_info["duration_weeks"]
        
        # 设置里程碑
        if stage in ["1级", "初段", "三段", "五段", "七段", "九段"]:
            plan["milestones"].append({
                "stage": stage,
                "week": current_week - 1,
                "description": f"达到{stage}水平，完成{stage_info['problem_count']}题+{stage_info['game_count']}局",
            })
    
    # 评估标准
    plan["evaluation_criteria"] = {
        "problem_accuracy": "各阶段目标准确率",
        "game_win_rate": "对局胜率",
        "thinking_depth": "计算深度（步数）",
        "pattern_recognition": "模式识别速度",
        "reflection_quality": "反思日志质量",
        "teaching_ability": "教学能力（五段以上）",
    }
    
    return plan


# ═══════════════════════════════════════════════════════════
# 生成Markdown报告
# ═══════════════════════════════════════════════════════════

def format_plan_to_markdown(plan: Dict[str, Any]) -> str:
    """将学习方案格式化为Markdown"""
    md = []
    md.append(f"# 🏯 {plan['student_name']} 围棋九段学习方案")
    md.append("")
    md.append(f"> 学员类型：{plan['student_type']}")
    md.append(f"> 当前等级：{plan['current_level']}")
    md.append(f"> 目标等级：{plan['target_level']}")
    md.append(f"> 总时长：{plan['total_duration_weeks']}周")
    md.append(f"> 生成时间：{plan['generated_at']}")
    md.append("")
    
    # 学习路径概览
    md.append("## 📈 学习路径概览")
    md.append("")
    md.append("| 阶段 | 等级 | 周次 | 题量 | 对局数 | 目标准确率 |")
    md.append("|------|------|------|------|--------|------------|")
    for phase in plan["phases"]:
        md.append(f"| {phase['stage']} | {phase['level']} | W{phase['start_week']}-W{phase['end_week']} | {phase['problem_count']} | {phase['game_count']} | {phase['target_accuracy']:.0%} |")
    md.append("")
    
    # 详细阶段计划
    md.append("## 📚 详细阶段计划")
    md.append("")
    for phase in plan["phases"]:
        md.append(f"### {phase['stage']}（{phase['level']}）")
        md.append("")
        md.append(f"**时间**：第{phase['start_week']}-{phase['end_week']}周（{phase['duration_weeks']}周）")
        md.append("")
        md.append(f"**训练重点**：{', '.join(phase['training_focus'])}")
        md.append("")
        md.append(f"**技能要求**：")
        for skill_key, skill_desc in phase['skills'].items():
            md.append(f"- {skill_desc}")
        md.append("")
        md.append(f"**训练量**：{phase['problem_count']}题 + {phase['game_count']}局")
        md.append("")
        md.append(f"**目标准确率**：{phase['target_accuracy']:.0%}")
        md.append("")
        
        if phase['custom_modules']:
            md.append("**定制训练模块**：")
            md.append("")
            for module in phase['custom_modules']:
                md.append(f"- **{module['name']}**（{module['focus']}）：{module['method']}")
            md.append("")
    
    # 里程碑
    md.append("## 🎯 里程碑")
    md.append("")
    for milestone in plan["milestones"]:
        md.append(f"- **第{milestone['week']}周**：达到{milestone['stage']}水平 - {milestone['description']}")
    md.append("")
    
    # 评估标准
    md.append("## 📊 评估标准")
    md.append("")
    for criterion, description in plan["evaluation_criteria"].items():
        md.append(f"- {criterion}：{description}")
    md.append("")
    
    md.append("---")
    md.append(f"*方案由诸葛马 (Hermes) v1.0 自动生成*")
    
    return "\n".join(md)


# ═══════════════════════════════════════════════════════════
# 主执行流程
# ═══════════════════════════════════════════════════════════

def main():
    """生成三位学员的九段学习方案"""
    print("=" * 70)
    print("🏯 小龙虾网络 v1.0 — 围棋九段学习方案生成系统")
    print("=" * 70)
    print()
    
    plans = {}
    markdowns = {}
    
    for student_id in STUDENTS:
        student = STUDENTS[student_id]
        print(f"📝 生成 {student['name']} 的九段学习方案...")
        
        plan = generate_dan_training_plan(student_id)
        markdown = format_plan_to_markdown(plan)
        
        plans[student_id] = plan
        markdowns[student_id] = markdown
        
        print(f"  ✓ 总时长：{plan['total_duration_weeks']}周")
        print(f"  ✓ 阶段数：{len(plan['phases'])}个")
        print(f"  ✓ 里程碑：{len(plan['milestones'])}个")
        print()
    
    # 保存文件
    output_dir = "/home/admin/lobster-network/docs/nine_dan_plan"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for student_id, plan in plans.items():
        # 保存JSON
        json_path = os.path.join(output_dir, f"plan_{student_id}_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"  ✓ JSON: {json_path}")
        
        # 保存Markdown
        md_path = os.path.join(output_dir, f"plan_{student_id}_{timestamp}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdowns[student_id])
        print(f"  ✓ Markdown: {md_path}")
    
    # 生成综合对比报告
    comparison_path = os.path.join(output_dir, f"comparison_{timestamp}.md")
    with open(comparison_path, 'w', encoding='utf-8') as f:
        f.write(generate_comparison_markdown(plans))
    print(f"  ✓ 对比报告: {comparison_path}")
    
    print("\n" + "=" * 70)
    print("✅ 九段学习方案生成完成！")
    print("=" * 70)
    
    return plans, markdowns


def generate_comparison_markdown(plans: Dict[str, Dict[str, Any]]) -> str:
    """生成三位学员学习方案对比报告"""
    md = []
    md.append("# 🏯 三位学员九段学习方案对比")
    md.append("")
    
    # 对比表
    md.append("## 📊 方案对比")
    md.append("")
    md.append("| 学员 | 类型 | 当前等级 | 总周数 | 总题量 | 总局数 |")
    md.append("|------|------|----------|--------|--------|--------|")
    
    for student_id, plan in plans.items():
        total_problems = sum(p['problem_count'] for p in plan['phases'])
        total_games = sum(p['game_count'] for p in plan['phases'])
        md.append(f"| {plan['student_name']} | {plan['student_type']} | {plan['current_level']} | {plan['total_duration_weeks']} | {total_problems} | {total_games} |")
    
    md.append("")
    
    # 定制模块对比
    md.append("## 🎯 定制训练模块对比")
    md.append("")
    for student_id, plan in plans.items():
        md.append(f"### {plan['student_name']}")
        md.append("")
        for phase in plan['phases']:
            if phase['custom_modules']:
                md.append(f"**{phase['stage']}**：")
                for module in phase['custom_modules']:
                    md.append(f"- {module['name']}（{module['focus']}）：{module['method']}")
                md.append("")
    
    md.append("---")
    md.append("*对比报告由诸葛马 (Hermes) v1.0 自动生成*")
    
    return "\n".join(md)


if __name__ == "__main__":
    plans, markdowns = main()
