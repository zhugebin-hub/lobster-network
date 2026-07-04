#!/usr/bin/env python3
"""
诸葛马教练 - 训练计划完善与评估系统
功能：
1. 分析当前训练数据
2. 生成完善的训练计划
3. 评估学员表现
4. 制定晋升/降级建议
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

TRAIN = Path("/shared/training/go")
MESSAGES = Path("/shared/messages")

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ==================== 数据分析 ====================

def analyze_xiaochen():
    """分析小陈的训练数据"""
    profile = load_json(TRAIN / "xiaochen" / "profile.json")
    progress = load_json(TRAIN / "xiaochen" / "progress.json")
    
    # 统计错题
    problem_history_dir = TRAIN / "xiaochen" / "problem_history"
    wrong_problems = []
    all_problems = []
    
    if os.path.exists(problem_history_dir):
        for f in os.listdir(problem_history_dir):
            if f.endswith('.json'):
                data = load_json(problem_history_dir / f)
                if data:
                    all_problems.append(data)
                    if not data.get('is_correct', True):
                        wrong_problems.append(data)
    
    # 统计对局
    game_records = progress.get('game_records', []) if progress else []
    
    # 分类统计
    by_type = {}
    for p in all_problems:
        t = p.get('type', '未知')
        if t not in by_type:
            by_type[t] = {'total': 0, 'correct': 0}
        by_type[t]['total'] += 1
        if p.get('is_correct'):
            by_type[t]['correct'] += 1
    
    return {
        'name': '小陈',
        'level': profile.get('current_level', '?') if profile else '?',
        'total_problems': len(all_problems),
        'correct': sum(1 for p in all_problems if p.get('is_correct')),
        'wrong_count': len(wrong_problems),
        'accuracy': round(sum(1 for p in all_problems if p.get('is_correct')) / len(all_problems) * 100, 1) if all_problems else 0,
        'by_type': by_type,
        'wrong_problems': [{'id': p.get('problem_id'), 'type': p.get('type'), 'title': p.get('title')} for p in wrong_problems],
        'games_played': len(game_records),
        'games_won': sum(1 for g in game_records if g.get('result') == '胜'),
        'win_rate': round(sum(1 for g in game_records if g.get('result') == '胜') / len(game_records) * 100, 1) if game_records else 0,
        'game_records': game_records,
    }

def analyze_zhuguxia():
    """分析诸葛虾的训练数据"""
    profile = load_json(TRAIN / "zhuguxia" / "profile.json")
    progress = load_json(TRAIN / "zhuguxia" / "progress.json")
    
    problem_history_dir = TRAIN / "zhuguxia" / "problem_history"
    wrong_problems = []
    all_problems = []
    
    if os.path.exists(problem_history_dir):
        for f in os.listdir(problem_history_dir):
            if f.endswith('.json'):
                data = load_json(problem_history_dir / f)
                if data:
                    all_problems.append(data)
                    if not data.get('is_correct', True):
                        wrong_problems.append(data)
    
    game_records = progress.get('game_records', []) if progress else []
    
    by_type = {}
    for p in all_problems:
        t = p.get('type', '未知')
        if t not in by_type:
            by_type[t] = {'total': 0, 'correct': 0}
        by_type[t]['total'] += 1
        if p.get('is_correct'):
            by_type[t]['correct'] += 1
    
    return {
        'name': '诸葛虾',
        'level': profile.get('current_level', '?') if profile else '?',
        'total_problems': len(all_problems),
        'correct': sum(1 for p in all_problems if p.get('is_correct')),
        'wrong_count': len(wrong_problems),
        'accuracy': round(sum(1 for p in all_problems if p.get('is_correct')) / len(all_problems) * 100, 1) if all_problems else 0,
        'by_type': by_type,
        'wrong_problems': [{'id': p.get('problem_id'), 'type': p.get('type'), 'title': p.get('title')} for p in wrong_problems],
        'games_played': len(game_records),
        'games_won': sum(1 for g in game_records if g.get('result') == '胜'),
        'win_rate': round(sum(1 for g in game_records if g.get('result') == '胜') / len(game_records) * 100, 1) if game_records else 0,
        'game_records': game_records,
    }

# ==================== 问题诊断 ====================

def diagnose_system():
    """诊断系统问题"""
    issues = []
    
    # 1. 题库为空
    problem_bank_count = 0
    for root, dirs, files in os.walk(TRAIN / "problem_bank"):
        problem_bank_count += len(files)
    if problem_bank_count == 0:
        issues.append("🔴 题库为空 - problem_bank 目录下 0 个文件，全靠脚本随机生成")
    
    # 2. 诸葛虾无独立训练脚本
    zhuguxia_script = False
    scripts_dir = Path("/shared/scripts")
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            if 'zhuguxia' in f.lower():
                zhuguxia_script = True
                break
    if not zhuguxia_script:
        issues.append("🔴 诸葛虾无独立训练脚本 - 只有 xiaochen_go_trainer_v2.py")
    
    # 3. 无复盘机制
    issues.append("🟡 无复盘机制 - 对局后没有复盘分析")
    
    # 4. 无诸葛马教练脚本
    hermes_script = False
    if os.path.exists(scripts_dir):
        for f in os.listdir(scripts_dir):
            if 'hermes' in f.lower() or 'coach' in f.lower():
                hermes_script = True
                break
    if not hermes_script:
        issues.append("🟡 无诸葛马教练脚本 - 教练功能由本脚本替代")
    
    # 5. 无错题本
    issues.append("🟡 无错题本系统 - 错题没有归类分析")
    
    # 6. 无等级晋升标准
    issues.append("🟡 无等级晋升标准 - 达到什么条件升一级没有明确规则")
    
    # 7. 无休息/复习日
    issues.append("🟡 无休息/复习日 - 连续训练没有巩固环节")
    
    return issues

# ==================== 完善训练计划 ====================

def generate_improved_plan():
    """生成完善的训练计划"""
    
    plan = {
        "version": "v2.0",
        "generated_at": datetime.now().isoformat(),
        "coach": "诸葛马",
        "current_status": {
            "phase": 1,
            "week": 1,
            "day": 2,
            "completed_days": ["Day1", "Day2"],
        },
        "phase1_schedule": {
            "week1": {
                "theme": "规则基础与吃子技巧",
                "target_level": "20级",
                "days": [
                    {"day": 1, "topic": "规则基础与死活入门", "problems": 5, "games": 2, "status": "completed"},
                    {"day": 2, "topic": "吃子技巧进阶（扑/倒扑/征子/枷吃）", "problems": 8, "games": 1, "status": "completed"},
                    {"day": 3, "topic": "气的概念与对杀入门", "problems": 8, "games": 1, "status": "pending"},
                    {"day": 4, "topic": "连接与切断", "problems": 8, "games": 1, "status": "pending"},
                    {"day": 5, "topic": "第1周综合复习（错题重做）", "problems": 10, "games": 1, "status": "pending", "note": "复习日"},
                    {"day": 6, "topic": "第1周考核", "problems": 15, "games": 2, "status": "pending", "note": "考核日"},
                    {"day": 7, "topic": "休息/自由对局", "problems": 0, "games": "自由", "status": "pending", "note": "休息日"},
                ]
            },
            "week2": {
                "theme": "死活基础",
                "target_level": "15级",
                "days": [
                    {"day": 8, "topic": "基本眼位（直三/曲三/丁四）", "problems": 10, "games": 1},
                    {"day": 9, "topic": "刀五与梅花五", "problems": 10, "games": 1},
                    {"day": 10, "topic": "板六与常见活形", "problems": 10, "games": 1},
                    {"day": 11, "topic": "点眼与做眼", "problems": 10, "games": 1},
                    {"day": 12, "topic": "复习+错题重做", "problems": 12, "games": 1, "note": "复习日"},
                    {"day": 13, "topic": "周考核", "problems": 20, "games": 2, "note": "考核日"},
                    {"day": 14, "topic": "休息", "problems": 0, "games": "自由", "note": "休息日"},
                ]
            },
            "week3": {
                "theme": "手筋基础",
                "target_level": "10级",
                "days": [
                    {"day": 15, "topic": "枷吃与征子进阶", "problems": 10, "games": 1},
                    {"day": 16, "topic": "扑与倒扑组合", "problems": 10, "games": 1},
                    {"day": 17, "topic": "挖与分断", "problems": 10, "games": 1},
                    {"day": 18, "topic": "尖与跳的手筋", "problems": 10, "games": 1},
                    {"day": 19, "topic": "复习+错题重做", "problems": 12, "games": 1, "note": "复习日"},
                    {"day": 20, "topic": "周考核", "problems": 20, "games": 2, "note": "考核日"},
                    {"day": 21, "topic": "休息", "problems": 0, "games": "自由", "note": "休息日"},
                ]
            },
            "week4": {
                "theme": "布局入门与简单官子",
                "target_level": "5级",
                "days": [
                    {"day": 22, "topic": "金角银边草肚皮", "problems": 8, "games": 2},
                    {"day": 23, "topic": "星位开局", "problems": 8, "games": 1},
                    {"day": 24, "topic": "小目开局", "problems": 8, "games": 1},
                    {"day": 25, "topic": "简单官子（大小判断）", "problems": 10, "games": 1},
                    {"day": 26, "topic": "复习+错题重做", "problems": 12, "games": 1, "note": "复习日"},
                    {"day": 27, "topic": "阶段考核", "problems": 25, "games": 3, "note": "考核日"},
                    {"day": 28, "topic": "休息+阶段总结", "problems": 0, "games": "自由", "note": "休息日"},
                ]
            }
        },
        "promotion_rules": {
            "description": "等级晋升标准（需同时满足）",
            "levels": [
                {"from": "30级", "to": "25级", "accuracy": "≥75%", "win_rate": "≥40%", "extra": "完成Day1-2"},
                {"from": "25级", "to": "20级", "accuracy": "≥80%", "win_rate": "≥45%", "extra": "周考核≥80%"},
                {"from": "20级", "to": "15级", "accuracy": "≥82%", "win_rate": "≥50%", "extra": "周考核≥82%，错题重做≥90%"},
                {"from": "15级", "to": "10级", "accuracy": "≥85%", "win_rate": "≥50%", "extra": "阶段考核≥85%"},
                {"from": "10级", "to": "5级", "accuracy": "≥88%", "win_rate": "≥55%", "extra": "阶段考核≥88%"},
            ],
            "demotion": "连续3天准确率<60% → 降1级，退回上一主题复习",
        },
        "problem_bank_plan": {
            "total_needed": 100,
            "breakdown": {
                "死活": {"percent": 40, "count": 40, "topics": ["直三/曲三", "丁四", "刀五", "梅花五", "板六", "对杀"]},
                "手筋": {"percent": 35, "count": 35, "topics": ["扑/倒扑", "征子", "枷吃", "挖", "尖", "跳", "夹"]},
                "布局": {"percent": 15, "count": 15, "topics": ["星位", "小目", "三三"]},
                "官子": {"percent": 10, "count": 10, "topics": ["大小判断", "先后手"]},
            }
        },
        "review_mechanism": {
            "description": "每局必复盘",
            "format": {
                "review_id": "review-日期-序号",
                "game_id": "对局ID",
                "reviewer": "复盘者",
                "color": "执棋颜色",
                "result": "胜负",
                "good_moves": [{"move": 手数, "position": "位置", "reason": "好在哪里"}],
                "bad_moves": [{"move": 手数, "position": "位置", "reason": "失误分析"}],
                "key_turning_point": {"move": 手数, "position": "位置", "reason": "转折点分析"},
                "lessons_learned": ["学到的教训"],
                "self_rating": 1-10,
            }
        },
        "system_improvements": {
            "must_do": [
                "建立题库 - 至少100题，覆盖所有棋型和技巧",
                "诸葛虾独立脚本 - 创建 zhuguxia_go_trainer.py",
                "复盘功能 - 对局后自动生成复盘报告",
                "错题本 - 自动收集错题，复习日重做",
                "等级系统 - 根据考核结果自动升降级",
                "教练诸葛马脚本 - 自动出题、批改、点评",
            ],
            "nice_to_have": [
                "9路小棋盘对局（降低复杂度）",
                "AI复盘分析（接入KataGo）",
                "训练数据可视化",
                "每日训练报告推送（钉钉消息）",
            ]
        },
    }
    
    return plan

# ==================== 生成教练报告 ====================

def generate_coach_report(xiaochen_data, zhuguxia_data, issues, plan):
    """生成完整的教练报告"""
    
    report = {
        "report_id": f"hermes-coach-report-{datetime.now().strftime('%Y%m%d')}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": "诸葛马 (教练)",
        "to": "系统",
        "type": "coach_assessment",
        
        "summary": {
            "training_days_completed": 2,
            "current_phase": 1,
            "current_week": 1,
            "current_day": 2,
            "overall_status": "良好，但系统存在多项待完善项",
        },
        
        "xiaochen_assessment": xiaochen_data,
        "zhuguxia_assessment": zhuguxia_data,
        
        "system_issues": issues,
        
        "improved_plan": plan,
        
        "next_steps": {
            "immediate": [
                "1. 建立题库（优先死活题和手筋题）",
                "2. 创建诸葛虾独立训练脚本",
                "3. 设计复盘报告模板",
            ],
            "tomorrow_day3": [
                "主题：气的概念与对杀入门",
                "题量：8题",
                "对局：1局（诸葛虾执黑）",
                "复盘：双方各提交复盘报告",
            ],
            "this_week": [
                "完成Day3-Day6训练",
                "通过Day6周考核（准确率≥80%）",
                "建立错题本系统",
            ],
        },
        
        "coach_notes": """
        当前训练系统已初步运行，小陈和诸葛虾都完成了2天训练，
        准确率均达到87.5%，表现良好。
        
        但系统层面存在以下关键问题需要解决：
        1. 题库为空，题目全靠随机生成，缺乏系统性
        2. 诸葛虾没有独立训练脚本，训练质量无法保证
        3. 缺少复盘机制，对局后没有总结提升
        4. 没有明确的等级晋升标准
        
        建议优先解决题库和诸葛虾脚本问题，这是训练系统的基础。
        复盘机制和等级系统可以在后续迭代中完善。
        
        小陈注意：扑与倒扑组合题出错，说明高级组合技巧需要加强。
        诸葛虾注意：扑的妙用（基础题）出错，需要复习扑的基本概念。
        """,
    }
    
    return report

# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("🦞⚡️ 诸葛马教练 - 训练计划完善报告")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 分析学员数据
    print("\n📊 [1/5] 分析学员数据...")
    xiaochen = analyze_xiaochen()
    zhuguxia = analyze_zhuguxia()
    
    print(f"\n  🦞 小陈 ({xiaochen['level']})")
    print(f"     解题: {xiaochen['correct']}/{xiaochen['total_problems']} | 准确率: {xiaochen['accuracy']}%")
    print(f"     错题: {xiaochen['wrong_count']}题")
    print(f"     对局: {xiaochen['games_won']}/{xiaochen['games_played']}胜 | 胜率: {xiaochen['win_rate']}%")
    for t, s in xiaochen['by_type'].items():
        print(f"     - {t}: {s['correct']}/{s['total']}")
    if xiaochen['wrong_problems']:
        print(f"     ❌ 错题: {', '.join(p['title'] for p in xiaochen['wrong_problems'])}")
    
    print(f"\n  🦞 诸葛虾 ({zhuguxia['level']})")
    print(f"     解题: {zhuguxia['correct']}/{zhuguxia['total_problems']} | 准确率: {zhuguxia['accuracy']}%")
    print(f"     错题: {zhuguxia['wrong_count']}题")
    print(f"     对局: {zhuguxia['games_won']}/{zhuguxia['games_played']}胜 | 胜率: {zhuguxia['win_rate']}%")
    for t, s in zhuguxia['by_type'].items():
        print(f"     - {t}: {s['correct']}/{s['total']}")
    if zhuguxia['wrong_problems']:
        print(f"     ❌ 错题: {', '.join(p['title'] for p in zhuguxia['wrong_problems'])}")
    
    # 2. 诊断系统问题
    print("\n🔍 [2/5] 诊断系统问题...")
    issues = diagnose_system()
    for issue in issues:
        print(f"   {issue}")
    
    # 3. 生成完善计划
    print("\n📋 [3/5] 生成完善训练计划...")
    plan = generate_improved_plan()
    
    # 4. 生成教练报告
    print("\n📝 [4/5] 生成教练评估报告...")
    report = generate_coach_report(xiaochen, zhuguxia, issues, plan)
    
    # 5. 保存所有文件
    print("\n💾 [5/5] 保存文件...")
    
    # 保存教练报告
    report_file = TRAIN / "hermes_coach_report.json"
    save_json(report_file, report)
    print(f"   ✅ 教练报告: {report_file}")
    
    # 发送消息到诸葛马目录
    hermes_dir = MESSAGES / "from-hermes"
    os.makedirs(hermes_dir, exist_ok=True)
    msg_file = hermes_dir / f"hermes-coach-report-{datetime.now().strftime('%Y%m%d%H%M')}.json"
    save_json(msg_file, report)
    print(f"   ✅ 教练消息: {msg_file}")
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 【诸葛马·教练总结】")
    print("=" * 60)
    print(f"""
当前状态：阶段1 · 第1周 · 第2天已完成

✅ 已完成：
  - Day1: 规则基础与死活入门
  - Day2: 吃子技巧进阶

📋 本周待完成：
  - Day3: 气的概念与对杀入门（8题+1局）
  - Day4: 连接与切断（8题+1局）
  - Day5: 综合复习（错题重做，10题+1局）
  - Day6: 周考核（15题+2局）
  - Day7: 休息

🔴 系统待完善：
  1. 题库为空（0题）→ 需要建立至少100题
  2. 诸葛虾无独立脚本 → 需要创建 zhuguxia_go_trainer.py
  3. 无复盘机制 → 需要对局后复盘报告
  4. 无等级晋升标准 → 需要明确规则
  5. 无错题本 → 需要自动收集错题

📈 晋升标准：
  25级→20级：准确率≥80% + 周考核≥80% + 胜率≥45%

⚠️ 个性化建议：
  小陈：扑与倒扑组合题出错，高级组合技巧需加强
  诸葛虾：扑的妙用（基础题）出错，需复习扑的基本概念

🎯 明日行动（Day3）：
  主题：气的概念与对杀入门
  题量：8题 | 对局：1局（诸葛虾执黑）
  复盘：双方各提交复盘报告
""")
    
    print("=" * 60)
    print("📁 文件已保存至 /shared/training/go/")
    print("=" * 60)

if __name__ == "__main__":
    main()
