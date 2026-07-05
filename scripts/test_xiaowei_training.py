#!/usr/bin/env python3
"""
小薇围棋训练 · 本地模拟测试
模拟7天完整训练流程，不依赖网络消息队列
"""

import json
import sys
import os
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PROBLEM_DIR = os.path.join(os.path.dirname(__file__), "..", "domains", "go", "problem_bank")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "registry", "training_results", "xiaowei")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 基础型准确率基线
ACCURACY = {"入门": 0.85, "初级": 0.70, "中级": 0.50, "高级": 0.25}

TOTAL_PROBLEMS = 0
TOTAL_CORRECT = 0
WRONG_BOOK = {}
SKILL_SCORES = {"基本概念": 0, "吃子": 0, "死活": 0, "连接": 0, "分断": 0, "定式": 0, "实战": 0, "综合": 0}
ALL_RESULTS = []

def load_problems(day):
    """加载当日题库"""
    path = os.path.join(PROBLEM_DIR, f"day{day}_problems.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            return data.get("problems", []), data.get("topic", "未知")
    return [], "未知"

def run_training(day):
    """执行当天训练"""
    global TOTAL_PROBLEMS, TOTAL_CORRECT

    problems, topic = load_problems(day)
    if not problems:
        print(f"  ⚠️  Day {day} 题库未找到")
        return None

    print(f"\n{'='*60}")
    print(f"🐚 小薇 · Day {day}: {topic}")
    print(f"{'='*60}")

    correct = 0
    total = 0
    wrong_ids = []

    for i, p in enumerate(problems, 1):
        pid = p.get("problem_id", f"p{i}")
        ptype = p.get("type", "未知")
        diff = p.get("difficulty", "入门")
        title = p.get("title", "")

        baseline = ACCURACY.get(diff, 0.6)
        is_correct = random.random() < baseline

        status = "✅" if is_correct else "❌"
        print(f"  [{i:2d}/{len(problems)}] {status} {ptype:6s} | {diff:4s} | {title}")

        if is_correct:
            correct += 1
            if ptype in SKILL_SCORES:
                SKILL_SCORES[ptype] += 1
        else:
            wrong_ids.append(pid)
            if ptype in SKILL_SCORES:
                SKILL_SCORES[ptype] = max(0, SKILL_SCORES[ptype] - 0.5)
            if pid not in WRONG_BOOK:
                WRONG_BOOK[pid] = {"count": 0, "first_seen_day": day}
            WRONG_BOOK[pid]["count"] += 1
            WRONG_BOOK[pid]["last_day"] = day

        total += 1

    accuracy = correct / total if total > 0 else 0
    TOTAL_PROBLEMS += total
    TOTAL_CORRECT += correct

    result = {
        "day": day, "topic": topic, "total": total,
        "correct": correct, "accuracy": round(accuracy, 3),
        "wrong_ids": wrong_ids,
    }
    ALL_RESULTS.append(result)

    # 评价
    if accuracy >= 0.80:
        emoji = "🌟"
        comment = "超常发挥！"
    elif accuracy >= 0.60:
        emoji = "✅"
        comment = "正常进度"
    else:
        emoji = "⚠️"
        comment = "需加强复习"

    print(f"  {'─'*56}")
    print(f"  {emoji} 结果: {correct}/{total} | 准确率: {accuracy:.1%} | {comment}")
    return result

def print_summary():
    """打印7天总结"""
    print(f"\n{'='*60}")
    print(f"📊 小薇 · 7天速成训练总结")
    print(f"   日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"   学员: 小薇 (xiaowei) | 类型: 基础型")
    print(f"   目标: 30k → 25k")
    print(f"{'='*60}")

    print(f"\n📈 逐日统计:")
    print(f"   {'Day':<6} {'主题':<20} {'正确/总数':<10} {'准确率'}")
    print(f"   {'─'*50}")
    for r in ALL_RESULTS:
        bar = "█" * int(r["accuracy"] * 20)
        print(f"   Day {r['day']:<3} {r['topic']:<20} {r['correct']}/{r['total']:<7}  {r['accuracy']:.0%} {bar}")

    overall = TOTAL_CORRECT / TOTAL_PROBLEMS if TOTAL_PROBLEMS > 0 else 0
    print(f"\n📊 整体: {TOTAL_CORRECT}/{TOTAL_PROBLEMS} = {overall:.1%}")

    print(f"\n🎯 技能分布:")
    for skill, score in sorted(SKILL_SCORES.items(), key=lambda x: -x[1]):
        bar = "▓" * max(int(score), 0) + "░" * max(int(20 - score), 0)
        print(f"   {skill:8s} {score:5.1f} {bar}")

    print(f"\n📋 错题本: {len(WRONG_BOOK)} 题待复习")
    if WRONG_BOOK:
        for pid, info in sorted(WRONG_BOOK.items(), key=lambda x: -x[1]["count"])[:5]:
            print(f"   - {pid}: 错{info['count']}次 (首次: Day{info.get('first_seen_day', '?')})")

    # 升级判定
    print(f"\n🏆 升级评估:")
    if overall >= 0.70:
        print(f"   ✅ 通过！小薇已达到25级水平")
        print(f"   建议：下周进入25级常规训练（与三龙虾团队并轨）")
    elif overall >= 0.60:
        print(f"   ⚠️  接近通过，建议复习错题后重新评估")
    else:
        print(f"   ❌ 未通过，需要额外2-3天强化训练")

    # 保存报告
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "student": "xiaowei",
        "name": "小薇",
        "type": "基础型",
        "total_problems": TOTAL_PROBLEMS,
        "total_correct": TOTAL_CORRECT,
        "overall_accuracy": round(overall, 3),
        "daily_results": ALL_RESULTS,
        "skill_scores": SKILL_SCORES,
        "wrong_book": WRONG_BOOK,
        "passed": overall >= 0.65,
    }
    report_path = os.path.join(OUTPUT_DIR, "7day_summary.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n💾 报告已保存: {report_path}")

    return report


def main():
    print("🐚 小薇围棋训练 · 7天速成全模拟")
    print("═" * 60)

    for day in range(1, 8):
        run_training(day)

    report = print_summary()
    return report


if __name__ == "__main__":
    main()
