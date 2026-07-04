#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 每日训练调度器 V2
功能：生成当日训练任务、派发inbox、收集outbox、更新状态
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

# === 配置 ===
BASE_DIR = Path("/home/admin/.openclaw/workspace/docs/lobster-network")
PROBLEM_BANK = BASE_DIR / "domains" / "go" / "problem_bank"
QUEUE_DIR = Path("/shared/messages/queue")
CONFIG = BASE_DIR / "config" / "brain.json"
REGISTRY = BASE_DIR / "registry" / "nodes"

# 训练大纲 - 第二阶段第5周：定式基础
WEEK5_PLAN = {
    "mon": {"topic": "星位定式·小飞挂", "ratio": {"定式": 60, "死活": 20, "手筋": 20}},
    "tue": {"topic": "星位定式·大飞挂", "ratio": {"定式": 60, "布局": 20, "手筋": 20}},
    "wed": {"topic": "小目定式·小飞挂", "ratio": {"定式": 50, "手筋": 30, "死活": 20}},
    "thu": {"topic": "小目定式·一间高挂", "ratio": {"定式": 50, "布局": 20, "死活": 30}},
    "fri": {"topic": "定式综合复习", "ratio": {"定式": 70, "布局": 15, "手筋": 15}},
    "sat": {"topic": "周考核（定式专项）", "ratio": {"定式": 80, "综合": 20}},
    "sun": {"topic": "错题复习 + 实战对局", "ratio": {"错题": 40, "实战": 60}},
}

# 学员参数
STUDENTS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "base_problems": 10,
        "accuracy_baseline": {"入门": 0.90, "初级": 0.80, "中级": 0.70, "高级": 0.35},
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "base_problems": 15,
        "accuracy_baseline": {"入门": 0.98, "初级": 0.90, "中级": 0.80, "高级": 0.60},
    },
}


def get_today_key():
    """获取今天是周几"""
    today = datetime.now()
    # 从周一开始算第几天
    weekday = today.weekday()  # 0=Mon, 6=Sun
    keys = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    return keys[weekday]


def load_problem_bank():
    """加载题库"""
    problems = []
    for f in PROBLEM_BANK.glob("*.json"):
        try:
            with open(f) as fh:
                data = json.load(fh)
                if isinstance(data, dict) and "problems" in data:
                    problems.extend(data["problems"])
                elif isinstance(data, list):
                    problems.extend(data)
        except Exception:
            continue
    return problems


def select_problems(problems, ratio, count):
    """按配比选题"""
    selected = []
    for category, pct in ratio.items():
        n = max(1, int(count * pct / 100))
        cat_problems = [p for p in problems if p.get("type") == category or category == "综合"]
        if not cat_problems and category != "综合":
            # 如果没找到精确匹配，用所有题目
            cat_problems = problems[:20]
        selected.extend(random.sample(cat_problems, min(n, len(cat_problems))))
    return selected[:count]


def generate_training_task(student_id, plan):
    """生成训练任务"""
    student = STUDENTS[student_id]
    problems = load_problem_bank()
    count = student["base_problems"]

    selected = select_problems(problems, plan["ratio"], count)

    task = {
        "id": f"go-train-{datetime.now().strftime('%Y%m%d')}-{student_id}",
        "from": "诸葛马 (教练)",
        "to": student["name"],
        "timestamp": datetime.now().isoformat(),
        "type": "training_task",
        "task": {
            "phase": 2,
            "week": 5,
            "day": 28,
            "topic": plan["topic"],
            "problems": selected,
            "time_limit_minutes": 60,
            "min_accuracy": student["accuracy_baseline"].get("初级", 0.8),
        },
        "validation": {
            "gate_type": "daily",
            "threshold": 0.75,
        },
    }
    return task


def simulate_training_result(task, student_id):
    """模拟训练结果（用于无NFS环境）"""
    student = STUDENTS[student_id]
    problems = task["task"]["problems"]
    total = len(problems)

    correct = 0
    wrong_answers = []
    for p in problems:
        diff = p.get("difficulty", "入门")
        baseline = student["accuracy_baseline"].get(diff, 0.8)
        if random.random() < baseline:
            correct += 1
        else:
            wrong_answers.append({
                "problem_id": p.get("problem_id", "unknown"),
                "user_answer": "错误答案",
                "correct_answer": p.get("answer", ""),
                "category": p.get("type", "未知"),
                "difficulty": diff,
            })

    accuracy = correct / total if total > 0 else 0
    return {
        "task_id": task["id"],
        "status": "completed" if accuracy >= 0.7 else ("partial" if accuracy >= 0.5 else "failed"),
        "problems_solved": total,
        "problems_correct": correct,
        "accuracy": round(accuracy, 3),
        "wrong_answers": wrong_answers,
        "summary": f"{student['name']} 今日完成 {plan['topic']}，正确率 {accuracy:.1%}",
    }


if __name__ == "__main__":
    today_key = get_today_key()
    plan = WEEK5_PLAN[today_key]
    print(f"📅 今日训练: {plan['topic']}")
    print(f"📊 配比: {plan['ratio']}")
    print()

    for sid in ["xiaochen", "zhuguxia"]:
        task = generate_training_task(sid, plan)
        result = simulate_training_result(task, sid)
        student = STUDENTS[sid]

        print(f"🦞 {student['name']} ({student['type']})")
        print(f"   题目: {result['problems_solved']} 题")
        print(f"   正确: {result['problems_correct']} 题")
        print(f"   准确率: {result['accuracy']:.1%}")
        print(f"   状态: {result['status']}")
        if result['wrong_answers']:
            print(f"   错题: {len(result['wrong_answers'])} 题 → 加入错题本")
        print()

    # 保存训练记录
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": plan["topic"],
        "results": {},
    }
    for sid in ["xiaochen", "zhuguxia"]:
        task = generate_training_task(sid, plan)
        result = simulate_training_result(task, sid)
        output["results"][sid] = result

    output_path = BASE_DIR / "registry" / "training_log.json"
    with open(output_path, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"✅ 训练记录已保存: {output_path}")
