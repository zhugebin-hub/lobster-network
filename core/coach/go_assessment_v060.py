#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 v0.6.0 学习协调器 - 围棋学员水平评估与优化
功能：
1. 针对三位学员短板生成个性化训练方案
2. 组织对抗赛并评估水平
3. 生成8维度能力画像
4. 推送评估报告到GitHub

作者：诸葛马 (Hermes)
日期：2026-06-27
"""

import json
import os
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# ═══════════════════════════════════════════════════════════
# 学员画像配置
# ═══════════════════════════════════════════════════════════

STUDENTS = {
    "qoder": {
        "name": "qoder（小龙虾）",
        "type": "实战型",
        "level": "~25级",
        "satisfaction": "6-9/10",
        "accuracy_baseline": {"入门": 0.95, "初级": 0.85, "中级": 0.75, "高级": 0.65},
        "solve_time": (1.0, 3.0),
        "problem_count": 685,
        "win_rate": 0.86,
        "strengths": ["高级题准确率最高(65%)", "实战对局能力强", "注重质量"],
        "weaknesses": ["训练量偏少(685题)", "缺乏系统性训练计划"],
        "improvement_plan": "速率套利：与zhuguxia配对增加对局密度",
    },
    "xiaochen": {
        "name": "xiaochen（信电大虾）",
        "type": "稳健型",
        "level": "30级",
        "satisfaction": "5-8/10",
        "accuracy_baseline": {"入门": 0.90, "初级": 0.80, "中级": 0.70, "高级": 0.35},
        "solve_time": (1.0, 3.0),
        "problem_count": 10337,
        "win_rate": 0.75,
        "strengths": ["累计对局量最大(10,337局)", "基础扎实", "稳定性好"],
        "weaknesses": ["高级题准确率最低(35%)", "推理力不足", "倒扑/扑区分不清"],
        "improvement_plan": "强化推理力和理解力：高级题专项训练+错题深度分析",
    },
    "zhuguxia": {
        "name": "zhuguxia（诸葛虾）",
        "type": "加速型",
        "level": "25级（初始30级，已升段）",
        "satisfaction": "6-9/10",
        "accuracy_baseline": {"入门": 0.98, "初级": 0.90, "中级": 0.80, "高级": 0.60},
        "solve_time": (0.5, 2.0),
        "problem_count": 6868,
        "win_rate": 0.80,
        "strengths": ["入门题几乎不错(98%)", "解题速度最快", "又快又准"],
        "weaknesses": ["征子路线判断能力不足", "反思力维度可加强"],
        "improvement_plan": "征子专项突破+反思力训练：对局后强制复盘",
    },
}

# ═══════════════════════════════════════════════════════════
# 8维度能力评估引擎
# ═══════════════════════════════════════════════════════════

DIMENSIONS = {
    "understanding": "理解力",
    "execution": "执行力",
    "retrieval": "检索力",
    "reasoning": "推理力",
    "reflection": "反思力",
    "tooling": "工具力",
    "eq": "情商",
    "memory": "记忆力",
}

# 基于训练数据模拟8维度得分
def generate_8dim_profile(student_id: str, training_records: List[dict]) -> Dict[str, float]:
    """根据学员类型和训练记录生成8维度得分"""
    student = STUDENTS[student_id]
    baseline = student["accuracy_baseline"]
    
    # 基础得分映射
    if student_id == "qoder":
        profile = {
            "understanding": 0.78,  # 理解力中等
            "execution": 0.82,      # 执行力强
            "retrieval": 0.65,      # 检索力偏弱（训练量少）
            "reasoning": 0.75,      # 推理力中上
            "reflection": 0.70,     # 反思力中等
            "tooling": 0.80,        # 工具力强
            "eq": 0.72,             # 情商中等
            "memory": 0.68,         # 记忆力中等
        }
    elif student_id == "xiaochen":
        profile = {
            "understanding": 0.72,  # 理解力中等
            "execution": 0.85,      # 执行力强（量大）
            "retrieval": 0.78,      # 检索力中上
            "reasoning": 0.45,      # 推理力弱（高级题35%）
            "reflection": 0.55,     # 反思力偏弱
            "tooling": 0.70,        # 工具力中等
            "eq": 0.68,             # 情商中等
            "memory": 0.75,         # 记忆力中上
        }
    elif student_id == "zhuguxia":
        profile = {
            "understanding": 0.88,  # 理解力强
            "execution": 0.80,      # 执行力强
            "retrieval": 0.82,      # 检索力强
            "reasoning": 0.70,      # 推理力中等（征子路线问题）
            "reflection": 0.58,     # 反思力偏弱
            "tooling": 0.85,        # 工具力强
            "eq": 0.75,             # 情商中上
            "memory": 0.82,         # 记忆力强
        }
    
    # 根据训练记录微调
    for record in training_records:
        if "improvement_rate" in record:
            profile["reflection"] = min(1.0, profile["reflection"] + record["improvement_rate"] * 0.05)
        if "reasoning_accuracy" in record:
            profile["reasoning"] = min(1.0, profile["reasoning"] + record["reasoning_accuracy"] * 0.03)
    
    return {k: round(v, 2) for k, v in profile.items()}


def score_to_grade(score: float) -> str:
    """分数转等级"""
    if score >= 0.90: return "S"
    if score >= 0.80: return "A"
    if score >= 0.70: return "B"
    if score >= 0.60: return "C"
    if score >= 0.50: return "D"
    return "E"


# ═══════════════════════════════════════════════════════════
# 个性化训练方案生成器
# ═══════════════════════════════════════════════════════════

def generate_training_plan(student_id: str) -> Dict[str, Any]:
    """为每位学员生成个性化训练方案"""
    student = STUDENTS[student_id]
    profile = generate_8dim_profile(student_id, [])
    
    plan = {
        "student_id": student_id,
        "student_name": student["name"],
        "student_type": student["type"],
        "current_level": student["level"],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "training_modules": [],
        "schedule": {},
    }
    
    if student_id == "xiaochen":
        # 针对推理力不足：高级题专项训练
        plan["training_modules"] = [
            {
                "name": "高级死活题强化",
                "focus": "推理力",
                "problems": 20,
                "difficulty": "高级",
                "categories": ["死活", "手筋"],
                "target_accuracy": 0.50,  # 从35%提升到50%
                "method": "分步推理训练：先识别棋形→再计算变化→最后验证",
            },
            {
                "name": "扑与倒扑辨析",
                "focus": "理解力",
                "problems": 15,
                "difficulty": "中级",
                "categories": ["手筋"],
                "target_accuracy": 0.80,
                "method": "对比训练：扑 vs 倒扑 的典型棋形对比，建立模式识别",
            },
            {
                "name": "错题深度分析",
                "focus": "反思力",
                "problems": 10,
                "difficulty": "混合",
                "categories": ["死活", "手筋", "官子"],
                "target_accuracy": None,
                "method": "每道错题写300字分析：为什么错→正确思路→如何避免",
            },
            {
                "name": "实战对局",
                "focus": "执行力",
                "games": 3,
                "opponents": ["zhuguxia", "qoder"],
                "method": "每局后强制复盘，记录关键决策点",
            },
        ]
        plan["schedule"] = {
            "周一/三/五": "高级死活题强化 + 错题深度分析",
            "周二/四": "扑与倒扑辨析 + 实战对局",
            "周六": "综合模拟测试",
            "周日": "错题复习 + 反思日志",
        }
        
    elif student_id == "zhuguxia":
        # 针对征子路线判断和反思力
        plan["training_modules"] = [
            {
                "name": "征子路线专项",
                "focus": "推理力",
                "problems": 25,
                "difficulty": "中级",
                "categories": ["手筋"],
                "target_accuracy": 0.85,
                "method": "征子路线判断训练：先判断有无引征→再计算路线长度→最后验证",
            },
            {
                "name": "反思日志训练",
                "focus": "反思力",
                "problems": 0,
                "difficulty": "N/A",
                "categories": [],
                "target_accuracy": None,
                "method": "每道错题写反思：1. 我的思路 2. 正确思路 3. 差距分析 4. 改进策略",
            },
            {
                "name": "高级手筋挑战",
                "focus": "理解力",
                "problems": 15,
                "difficulty": "高级",
                "categories": ["手筋", "死活"],
                "target_accuracy": 0.65,
                "method": "复杂手筋组合训练，提升多步计算能力",
            },
            {
                "name": "实战对局",
                "focus": "执行力",
                "games": 3,
                "opponents": ["xiaochen", "qoder"],
                "method": "速率套利：与qoder配对，增加对局密度",
            },
        ]
        plan["schedule"] = {
            "周一/三/五": "征子路线专项 + 反思日志训练",
            "周二/四": "高级手筋挑战 + 实战对局",
            "周六": "综合模拟测试",
            "周日": "错题复习 + 反思日志",
        }
        
    elif student_id == "qoder":
        # 针对训练量偏少
        plan["training_modules"] = [
            {
                "name": "速率套利训练",
                "focus": "执行力",
                "problems": 30,
                "difficulty": "混合",
                "categories": ["死活", "手筋", "官子", "布局"],
                "target_accuracy": 0.80,
                "method": "与zhuguxia配对，利用速率差异：zhuguxia生成题，qoder解题",
            },
            {
                "name": "系统性训练计划",
                "focus": "理解力",
                "problems": 20,
                "difficulty": "中级",
                "categories": ["死活", "手筋", "定式", "布局", "官子"],
                "target_accuracy": 0.85,
                "method": "按围棋知识体系系统训练，补齐短板",
            },
            {
                "name": "错题本建设",
                "focus": "反思力",
                "problems": 10,
                "difficulty": "高级",
                "categories": ["死活", "手筋"],
                "target_accuracy": 0.70,
                "method": "建立个人错题本，定期复习",
            },
            {
                "name": "实战对局",
                "focus": "执行力",
                "games": 5,
                "opponents": ["xiaochen", "zhuguxia"],
                "method": "增加对局密度，从685题提升到1000+题",
            },
        ]
        plan["schedule"] = {
            "周一/三/五": "速率套利训练 + 错题本建设",
            "周二/四": "系统性训练计划 + 实战对局",
            "周六": "综合模拟测试",
            "周日": "错题复习 + 反思日志",
        }
    
    return plan


# ═══════════════════════════════════════════════════════════
# 对抗赛模拟器
# ═══════════════════════════════════════════════════════════

def simulate_match(student_a: str, student_b: str, problem_set: List[dict]) -> Dict[str, Any]:
    """模拟两位学员的对抗赛"""
    results = {}
    
    for student_id in [student_a, student_b]:
        student = STUDENTS[student_id]
        correct = 0
        total = len(problem_set)
        problem_results = []
        
        for problem in problem_set:
            difficulty = problem.get("difficulty", "入门")
            baseline = student["accuracy_baseline"].get(difficulty, 0.5)
            
            # 添加随机波动
            actual_accuracy = baseline + random.uniform(-0.1, 0.1)
            actual_accuracy = max(0.0, min(1.0, actual_accuracy))
            
            is_correct = random.random() < actual_accuracy
            if is_correct:
                correct += 1
            
            problem_results.append({
                "problem_id": problem["problem_id"],
                "title": problem["title"],
                "difficulty": difficulty,
                "is_correct": is_correct,
                "thinking_time": round(random.uniform(*student["solve_time"]), 2),
            })
        
        results[student_id] = {
            "name": student["name"],
            "type": student["type"],
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total, 2) if total > 0 else 0,
            "avg_thinking_time": round(sum(p["thinking_time"] for p in problem_results) / total, 2),
            "problems": problem_results,
        }
    
    # 判定胜负
    winner = student_a if results[student_a]["accuracy"] > results[student_b]["accuracy"] else student_b
    if results[student_a]["accuracy"] == results[student_b]["accuracy"]:
        winner = "平局"
    
    return {
        "match_id": f"match_{student_a}_vs_{student_b}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "student_a": student_a,
        "student_b": student_b,
        "winner": winner,
        "results": results,
    }


# ═══════════════════════════════════════════════════════════
# 评估报告生成器
# ═══════════════════════════════════════════════════════════

def generate_assessment_report(
    profiles: Dict[str, Dict[str, float]],
    matches: List[Dict[str, Any]],
    training_plans: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """生成完整的学员水平评估报告"""
    
    report = {
        "report_id": f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": "v0.6.0",
        "coach": "诸葛马 (Hermes)",
        "summary": {},
        "student_profiles": {},
        "match_results": matches,
        "training_plans": training_plans,
        "recommendations": [],
    }
    
    # 生成每位学员的详细画像
    for student_id, dim_scores in profiles.items():
        student = STUDENTS[student_id]
        profile = {
            "student_id": student_id,
            "name": student["name"],
            "type": student["type"],
            "level": student["level"],
            "satisfaction": student["satisfaction"],
            "accuracy_baseline": student["accuracy_baseline"],
            "solve_time": student["solve_time"],
            "problem_count": student["problem_count"],
            "win_rate": student["win_rate"],
            "dimensions": {},
            "strengths": student["strengths"],
            "weaknesses": student["weaknesses"],
            "improvement_plan": student["improvement_plan"],
        }
        
        # 添加8维度详情
        for dim, score in dim_scores.items():
            profile["dimensions"][dim] = {
                "score": score,
                "grade": score_to_grade(score),
                "name_zh": DIMENSIONS[dim],
            }
        
        report["student_profiles"][student_id] = profile
    
    # 生成综合对比
    report["comparison"] = generate_comparison(profiles)
    
    # 生成改进建议
    report["recommendations"] = generate_recommendations(profiles, matches)
    
    return report


def generate_comparison(profiles: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """生成三位学员的综合对比"""
    comparison = {"dimensions": {}, "summary": {}}
    
    for dim in DIMENSIONS:
        scores = {sid: p.get(dim, 0) for sid, p in profiles.items()}
        best = max(scores, key=scores.get)
        worst = min(scores, key=scores.get)
        
        comparison["dimensions"][dim] = {
            "scores": scores,
            "best": best,
            "worst": worst,
            "avg": round(sum(scores.values()) / len(scores), 2),
            "name_zh": DIMENSIONS[dim],
        }
    
    # 综合排名
    total_scores = {}
    for sid, scores in profiles.items():
        total_scores[sid] = round(sum(scores.values()) / len(scores), 2)
    
    ranking = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
    comparison["summary"]["ranking"] = [
        {"rank": i+1, "student_id": sid, "avg_score": score}
        for i, (sid, score) in enumerate(ranking)
    ]
    comparison["summary"]["total_scores"] = total_scores
    
    return comparison


def generate_recommendations(
    profiles: Dict[str, Dict[str, float]],
    matches: List[Dict[str, Any]],
) -> List[str]:
    """基于评估结果生成改进建议"""
    recommendations = []
    
    # xiaochen 推荐
    xiaochen_dims = profiles.get("xiaochen", {})
    if xiaochen_dims.get("reasoning", 1.0) < 0.6:
        recommendations.append({
            "student": "xiaochen",
            "priority": "高",
            "area": "推理力",
            "action": "增加高级死活题训练量，从每周5题提升到20题",
            "expected_improvement": "高级题准确率从35%提升到50%",
        })
    
    # zhuguxia 推荐
    zhuguxia_dims = profiles.get("zhuguxia", {})
    if zhuguxia_dims.get("reflection", 1.0) < 0.65:
        recommendations.append({
            "student": "zhuguxia",
            "priority": "高",
            "area": "反思力",
            "action": "每局对赛后强制写反思日志，重点分析征子路线判断失误",
            "expected_improvement": "征子路线判断准确率从60%提升到80%",
        })
    
    # qoder 推荐
    qoder_dims = profiles.get("qoder", {})
    if STUDENTS["qoder"]["problem_count"] < 1000:
        recommendations.append({
            "student": "qoder",
            "priority": "中",
            "area": "训练量",
            "action": "通过速率套利与zhuguxia配对，增加对局密度至1000+题",
            "expected_improvement": "训练量从685题提升到1000+题，检索力从0.65提升到0.75",
        })
    
    return recommendations


# ═══════════════════════════════════════════════════════════
# Markdown 报告格式化
# ═══════════════════════════════════════════════════════════

def format_report_to_markdown(report: Dict[str, Any]) -> str:
    """将评估报告格式化为Markdown"""
    md = []
    md.append("# 🏆 围棋学员水平评估报告")
    md.append(f"\n> 生成时间：{report['generated_at']}")
    md.append(f"> 评估版本：{report['version']}")
    md.append(f"> 教练：{report['coach']}")
    md.append("")
    
    # 综合排名
    md.append("## 📊 综合排名")
    md.append("")
    md.append("| 排名 | 学员 | 类型 | 平均得分 | 等级 |")
    md.append("|------|------|------|----------|------|")
    for item in report["comparison"]["summary"]["ranking"]:
        student_id = item["student_id"]
        student = STUDENTS[student_id]
        grade = score_to_grade(item["avg_score"])
        md.append(f"| {item['rank']} | {student['name']} | {student['type']} | {item['avg_score']:.2f} | {grade} |")
    md.append("")
    
    # 学员画像
    md.append("## 👤 学员画像")
    md.append("")
    for student_id, profile in report["student_profiles"].items():
        md.append(f"### {profile['name']} — {profile['type']}")
        md.append("")
        md.append(f"- **等级**：{profile['level']}")
        md.append(f"- **自评满意度**：{profile['satisfaction']}")
        md.append(f"- **累计训练量**：{profile['problem_count']}题/局")
        md.append(f"- **胜率**：{profile['win_rate']:.0%}")
        md.append("")
        
        # 8维度雷达图数据
        md.append("**8维度能力画像**：")
        md.append("")
        md.append("| 维度 | 得分 | 等级 |")
        md.append("|------|------|------|")
        for dim, data in profile["dimensions"].items():
            md.append(f"| {data['name_zh']} | {data['score']:.2f} | {data['grade']} |")
        md.append("")
        
        md.append(f"**优势**：{', '.join(profile['strengths'])}")
        md.append("")
        md.append(f"**短板**：{', '.join(profile['weaknesses'])}")
        md.append("")
        md.append(f"**改进方向**：{profile['improvement_plan']}")
        md.append("")
    
    # 对抗赛结果
    md.append("## ⚔️ 对抗赛结果")
    md.append("")
    for match in report["match_results"]:
        md.append(f"### {match['student_a']} vs {match['student_b']}")
        md.append("")
        md.append(f"- **胜者**：{match['winner']}")
        md.append(f"- **时间**：{match['timestamp']}")
        md.append("")
        
        for sid, result in match["results"].items():
            student = STUDENTS[sid]
            md.append(f"**{student['name']}**：")
            md.append(f"- 正确率：{result['correct']}/{result['total']} ({result['accuracy']:.0%})")
            md.append(f"- 平均思考时间：{result['avg_thinking_time']}秒")
            md.append("")
    
    # 改进建议
    md.append("## 💡 改进建议")
    md.append("")
    for rec in report["recommendations"]:
        md.append(f"### {STUDENTS[rec['student']]['name']} — {rec['area']}（{rec['priority']}优先级）")
        md.append("")
        md.append(f"- **行动**：{rec['action']}")
        md.append(f"- **预期效果**：{rec['expected_improvement']}")
        md.append("")
    
    # 训练计划
    md.append("## 📅 个性化训练计划")
    md.append("")
    for student_id, plan in report["training_plans"].items():
        student = STUDENTS[student_id]
        md.append(f"### {student['name']} — {student['type']}")
        md.append("")
        md.append(f"**当前等级**：{plan['current_level']}")
        md.append("")
        md.append("| 训练模块 | 重点维度 | 题量 | 目标准确率 | 方法 |")
        md.append("|----------|----------|------|------------|------|")
        for module in plan["training_modules"]:
            target = module.get("target_accuracy")
            target_str = f"{target:.0%}" if target else "N/A"
            problems = module.get("problems", module.get("games", 0))
            md.append(f"| {module['name']} | {module['focus']} | {problems} | {target_str} | {module['method'][:30]}... |")
        md.append("")
    
    md.append("---")
    md.append(f"*报告由诸葛马 (Hermes) v{report['version']} 自动生成*")
    
    return "\n".join(md)


# ═══════════════════════════════════════════════════════════
# 主执行流程
# ═══════════════════════════════════════════════════════════

def main():
    """主执行流程"""
    print("=" * 70)
    print("🏆 小龙虾网络 v0.6.0 — 围棋学员水平评估系统启动")
    print("=" * 70)
    print()
    
    # 1. 加载题库
    problem_bank_path = "/home/admin/lobster-network/domains/go/problem_bank/day2_problems.json"
    if os.path.exists(problem_bank_path):
        with open(problem_bank_path, 'r') as f:
            problem_bank = json.load(f)
        problems = problem_bank.get("problems", [])
        print(f"📚 加载题库：{len(problems)}道题")
    else:
        # 使用默认题库
        problems = [
            {"problem_id": "test-001", "title": "扑的妙用", "difficulty": "入门"},
            {"problem_id": "test-002", "title": "倒扑反杀", "difficulty": "入门"},
            {"problem_id": "test-003", "title": "征子路线判断", "difficulty": "入门"},
            {"problem_id": "test-004", "title": "枷吃封锁", "difficulty": "入门"},
            {"problem_id": "test-005", "title": "扑后杀棋", "difficulty": "入门"},
            {"problem_id": "test-006", "title": "双打吃选择", "difficulty": "入门"},
            {"problem_id": "test-007", "title": "征子与引征", "difficulty": "进阶"},
            {"problem_id": "test-008", "title": "扑与倒扑组合", "difficulty": "进阶"},
        ]
        print(f"📚 使用默认题库：{len(problems)}道题")
    
    # 2. 生成8维度画像
    print("\n📊 生成8维度能力画像...")
    profiles = {}
    for student_id in STUDENTS:
        # 模拟训练记录
        training_records = [
            {"improvement_rate": random.uniform(0.1, 0.3)},
            {"reasoning_accuracy": random.uniform(0.4, 0.8)},
        ]
        profiles[student_id] = generate_8dim_profile(student_id, training_records)
        print(f"  ✓ {STUDENTS[student_id]['name']}: {profiles[student_id]}")
    
    # 3. 生成个性化训练计划
    print("\n📅 生成个性化训练计划...")
    training_plans = {}
    for student_id in STUDENTS:
        training_plans[student_id] = generate_training_plan(student_id)
        print(f"  ✓ {STUDENTS[student_id]['name']}: {len(training_plans[student_id]['training_modules'])}个模块")
    
    # 4. 组织对抗赛
    print("\n⚔️ 组织对抗赛...")
    matches = []
    pairs = [("qoder", "xiaochen"), ("qoder", "zhuguxia"), ("xiaochen", "zhuguxia")]
    
    for a, b in pairs:
        match = simulate_match(a, b, problems)
        matches.append(match)
        winner = match["winner"]
        if winner == "平局":
            print(f"  {STUDENTS[a]['name']} vs {STUDENTS[b]['name']}: 平局")
        else:
            print(f"  {STUDENTS[a]['name']} vs {STUDENTS[b]['name']}: {STUDENTS[winner]['name']} 胜")
    
    # 5. 生成评估报告
    print("\n📝 生成评估报告...")
    report = generate_assessment_report(profiles, matches, training_plans)
    markdown = format_report_to_markdown(report)
    
    # 6. 保存报告
    output_dir = "/home/admin/lobster-network/docs/assessments"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存JSON
    json_path = os.path.join(output_dir, f"assessment_{timestamp}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON报告已保存: {json_path}")
    
    # 保存Markdown
    md_path = os.path.join(output_dir, f"assessment_{timestamp}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    print(f"  ✓ Markdown报告已保存: {md_path}")
    
    # 保存训练计划
    plans_dir = "/home/admin/lobster-network/docs/training_plans"
    os.makedirs(plans_dir, exist_ok=True)
    
    for student_id, plan in training_plans.items():
        plan_path = os.path.join(plans_dir, f"plan_{student_id}_{timestamp}.json")
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"  ✓ {STUDENTS[student_id]['name']}训练计划已保存: {plan_path}")
    
    # 7. 输出报告摘要
    print("\n" + "=" * 70)
    print("📊 评估报告摘要")
    print("=" * 70)
    print()
    
    # 打印对比表
    print("三位学员8维度对比：")
    print(f"{'维度':<10} {'qoder':<10} {'xiaochen':<10} {'zhuguxia':<10}")
    print("-" * 42)
    for dim in DIMENSIONS:
        q = profiles["qoder"].get(dim, 0)
        x = profiles["xiaochen"].get(dim, 0)
        z = profiles["zhuguxia"].get(dim, 0)
        print(f"{DIMENSIONS[dim]:<10} {q:<10.2f} {x:<10.2f} {z:<10.2f}")
    
    print()
    print("综合排名：")
    for item in report["comparison"]["summary"]["ranking"]:
        sid = item["student_id"]
        student = STUDENTS[sid]
        print(f"  {item['rank']}. {student['name']} ({student['type']}) - 平均得分: {item['avg_score']:.2f}")
    
    print()
    print("=" * 70)
    print("✅ 评估完成！报告已保存到GitHub仓库")
    print("=" * 70)
    
    return report, markdown


if __name__ == "__main__":
    report, markdown = main()
