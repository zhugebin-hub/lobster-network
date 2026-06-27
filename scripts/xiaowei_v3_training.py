#!/usr/bin/env python3
"""小薇 V3 强化训练模拟 (23k → 20k)"""
import json, random, os, sys
from datetime import datetime

def load_problems(day):
    path = f"domains/go/problem_bank/day{day}_problems.json"
    with open(path) as f:
        return json.load(f)

def simulate_solve(problem, improved={"连接": 0.15, "实战": 0.15, "死活": 0.05}):
    """模拟答题，考虑 V3 的针对性强化"""
    base_map = {"初级": 0.50, "中级": 0.30, "高级": 0.10}
    base = base_map.get(problem["difficulty"], 0.30)

    # V3 强化加成
    bonus = 0
    ptype = problem["type"]
    if ptype in improved:
        bonus = improved[ptype]
    elif "连接" in ptype:
        bonus = 0.15
    elif "实战" in ptype:
        bonus = 0.15

    # 错题回顾更容易
    if problem["id"].startswith("review-"):
        bonus += 0.25

    return random.random() < (base + bonus), random.uniform(1, 4)

def main():
    results = {"total": 0, "correct": 0, "days": []}
    skill_scores_v3 = {"连接": 0, "连接分断综合": 0, "实战": 0, "官子": 0, "全局": 0, "综合": 0}
    skill_counts = {"连接": 0, "连接分断综合": 0, "实战": 0, "官子": 0, "全局": 0, "综合": 0}
    wrong_book = {}

    print("=" * 60)
    print("🐚 小薇 V3 强化训练 (23k → 20k)")
    print("=" * 60)

    for day in range(15, 22):
        data = load_problems(day)
        correct = 0
        total = len(data["problems"])
        day_wrong = []

        for p in data["problems"]:
            ok, t = simulate_solve(p)
            if ok:
                correct += 1
            else:
                day_wrong.append(p["id"])
                wrong_book[p["id"]] = wrong_book.get(p["id"], 0) + 1

            # Track skill scores
            stype = p["type"]
            sk = skill_scores_v3.get(stype)
            if sk is not None:
                skill_scores_v3[stype] += (1 if ok else 0)
                skill_counts[stype] += 1
            else:
                # Map to closest
                for k in skill_scores_v3:
                    if k in stype or stype in k:
                        skill_scores_v3[k] += (1 if ok else 0)
                        skill_counts[k] += 1
                        break

        acc = correct / total
        passed = acc >= data["pass_threshold"]
        icon = "✅" if passed else "❌"
        bar_len = int(acc * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)

        print(f"  Day {day} {data['topic']:<18} {bar} {acc:.0%} {icon}")
        if day_wrong:
            print(f"    错题: {', '.join(day_wrong[:5])}")
            if len(day_wrong) > 5:
                print(f"          ... 等 {len(day_wrong)} 题")

        results["total"] += total
        results["correct"] += correct
        results["days"].append({
            "day": day, "topic": data["topic"],
            "total": total, "correct": correct,
            "accuracy": acc, "passed": passed,
            "wrong_ids": day_wrong
        })

    # Calculate skill scores (max 10)
    for k in skill_scores_v3:
        if skill_counts[k] > 0:
            skill_scores_v3[k] = round(skill_scores_v3[k] / skill_counts[k] * 10, 1)
        else:
            skill_scores_v3[k] = 0

    overall_acc = results["correct"] / results["total"]
    passed_days = sum(1 for d in results["days"] if d["passed"])

    print("\n" + "=" * 60)
    print("📊 V3 训练总结")
    print(f"  题目: {results['total']}  正确: {results['correct']}  准确率: {overall_acc:.1%}")
    print(f"  通过天数: {passed_days}/{len(results['days'])}")
    print(f"  错题本新增: {len(wrong_book)} 题")

    print("\n📊 V3 技能得分:")
    for sk, score in sorted(skill_scores_v3.items(), key=lambda x: -x[1]):
        bar_len = int(score)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        print(f"  {sk:<12} {bar} {score:.1f}")

    # Check promotion
    conn_score = skill_scores_v3.get("连接", 0)
    fight_score = skill_scores_v3.get("实战", 0)
    all_passed = all(d["passed"] for d in results["days"])
    day21_acc = results["days"][-1]["accuracy"]
    day21_passed = day21_acc >= 0.80

    print("\n🎯 20k 晋升条件:")
    print(f"  全部天数通过? {all_passed} {'✅' if all_passed else '❌'}")
    print(f"  连接 ≥ 7.0?   {conn_score:.1f} {'✅' if conn_score >= 7.0 else '❌'}")
    print(f"  实战 ≥ 7.0?   {fight_score:.1f} {'✅' if fight_score >= 7.0 else '❌'}")
    print(f"  Day21 ≥ 80%?  {day21_acc:.1%} {'✅' if day21_passed else '❌'}")
    promoted = all_passed and conn_score >= 7.0 and fight_score >= 7.0 and day21_passed
    print(f"\n  🏆 晋升 20k: {'✅ 成功！' if promoted else '❌ 未达标'}")

    if not promoted:
        fail_reasons = []
        if not all_passed: fail_reasons.append("有天数未通过")
        if conn_score < 7.0: fail_reasons.append(f"连接({conn_score}) < 7.0")
        if fight_score < 7.0: fail_reasons.append(f"实战({fight_score}) < 7.0")
        if not day21_passed: fail_reasons.append(f"毕业考({day21_acc:.1%}) < 80%")
        print(f"  原因: {'; '.join(fail_reasons)}")

    # Save results
    summary = {
        "version": "V3",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "student": "xiaowei",
        "start_level": "23k",
        "target_level": "20k",
        "promoted": promoted,
        "total_problems": results["total"],
        "total_correct": results["correct"],
        "overall_accuracy": round(overall_acc, 4),
        "cumulative_total": 116 + results["total"],
        "cumulative_correct": 82 + results["correct"],
        "cumulative_accuracy": round((82 + results["correct"]) / (116 + results["total"]), 4),
        "daily_results": results["days"],
        "skill_scores_v3": skill_scores_v3,
        "promotion_checks": {
            "all_days_passed": all_passed,
            "connection_score": conn_score,
            "fight_score": fight_score,
            "day21_passed": day21_passed
        },
        "wrong_book_v3": wrong_book
    }
    os.makedirs("registry/training_results/xiaowei", exist_ok=True)
    with open("registry/training_results/xiaowei/v3_summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n📁 结果已保存: registry/training_results/xiaowei/v3_summary.json")

    return summary

if __name__ == "__main__":
    s = main()
    sys.exit(0 if s["promoted"] else 1)
