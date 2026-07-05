#!/usr/bin/env python3
"""
论文学习训练器 V1
Paper Learning Trainer for Lobster Network

功能:
  - 查看各节点论文训练状态
  - 分配每日阅读/写作任务
  - 提交精读笔记
  - 管理间隔复习计划
  - 生成训练周报

用法:
  python3 paper_trainer.py --action status
  python3 paper_trainer.py --node qoder --action assign --day 1
  python3 paper_trainer.py --node xiaochen --action submit --paper "paper_id"
  python3 paper_trainer.py --node zhuguxia --action review-schedule
  python3 paper_trainer.py --action weekly-report
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# ── 路径配置 ──────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PAPER_DIR = REPO_ROOT / "domains" / "paper"
STUDENT_DIR = PAPER_DIR / "student_data"
PROBLEM_BANK = PAPER_DIR / "problem_bank"

NODES = ["qoder", "xiaochen", "zhuguxia"]

# ── 学员初始数据 ──────────────────────────────────────
INITIAL_PROFILES = {
    "qoder": {
        "name": "qoder小龙虾",
        "level": "六段",
        "target_level": "八段",
        "start_day": 1,
        "current_day": 1,
        "papers_read": 0,
        "papers_target": 15,
        "notes_completed": 0,
        "words_written": 0,
        "words_target": 50000,
        "review_queue": [],
        "exercises_done": [],
        "training_mode": "sprint",  # 冲刺型
        "specialty": "system_architecture",
        "weakness": "experiment_design",
    },
    "xiaochen": {
        "name": "小陈",
        "level": "二段",
        "target_level": "五段",
        "start_day": 1,
        "current_day": 1,
        "papers_read": 0,
        "papers_target": 10,
        "notes_completed": 0,
        "words_written": 0,
        "words_target": 30000,
        "review_queue": [],
        "exercises_done": [],
        "training_mode": "steady",  # 稳扎稳打型
        "specialty": "data_analysis",
        "weakness": "academic_writing",
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "level": "二段",
        "target_level": "五段",
        "start_day": 1,
        "current_day": 1,
        "papers_read": 0,
        "papers_target": 10,
        "notes_completed": 0,
        "words_written": 0,
        "words_target": 30000,
        "review_queue": [],
        "exercises_done": [],
        "training_mode": "balanced",  # 速度深度平衡型
        "specialty": "rapid_prototyping",
        "weakness": "deep_analysis",
    },
}

# ── 间隔复习规则 ──────────────────────────────────────
REVIEW_INTERVALS = {
    "R1": 1,   # 1 天后
    "R2": 3,   # 3 天后
    "R3": 7,   # 7 天后
    "R4": 14,  # 14 天后
}

GRADUATION_THRESHOLD = 4  # 4 轮全通过 → 归入已掌握


# ── 状态管理 ──────────────────────────────────────────

def load_profile(node_id: str) -> dict:
    """加载学员档案，不存在则初始化"""
    profile_path = STUDENT_DIR / node_id / "profile.json"
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 初始化
    profile = INITIAL_PROFILES.get(node_id)
    if not profile:
        print(f"[ERROR] 未知节点: {node_id}")
        sys.exit(1)
    profile["node_id"] = node_id
    profile["created_at"] = datetime.now().isoformat()
    profile["updated_at"] = datetime.now().isoformat()
    save_profile(node_id, profile)
    return profile


def save_profile(node_id: str, profile: dict):
    """保存学员档案"""
    student_path = STUDENT_DIR / node_id
    student_path.mkdir(parents=True, exist_ok=True)
    profile["updated_at"] = datetime.now().isoformat()
    with open(student_path / "profile.json", "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def load_notes(node_id: str) -> list:
    """加载精读笔记列表"""
    notes_path = STUDENT_DIR / node_id / "notes.json"
    if notes_path.exists():
        with open(notes_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_notes(node_id: str, notes: list):
    """保存精读笔记列表"""
    student_path = STUDENT_DIR / node_id
    student_path.mkdir(parents=True, exist_ok=True)
    with open(student_path / "notes.json", "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


# ── 核心功能 ──────────────────────────────────────────

def show_status():
    """显示所有节点的论文训练状态"""
    print("=" * 60)
    print("  小龙虾网络 · 论文学习训练状态")
    print(f"  更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    for node_id in NODES:
        profile = load_profile(node_id)
        notes = load_notes(node_id)
        mastered = sum(1 for n in notes if n.get("status") == "mastered")
        in_progress = sum(1 for n in notes if n.get("status") == "in_progress")

        read_pct = (profile["papers_read"] / profile["papers_target"] * 100
                     if profile["papers_target"] > 0 else 0)
        write_pct = (profile["words_written"] / profile["words_target"] * 100
                      if profile["words_target"] > 0 else 0)

        print(f"\n--- {profile['name']} ({node_id}) ---")
        print(f"  段位: {profile['level']} → 目标 {profile['target_level']}")
        print(f"  训练天数: Day {profile['current_day']}/15")
        print(f"  论文阅读: {profile['papers_read']}/{profile['papers_target']}"
              f" ({read_pct:.0f}%)")
        print(f"  精读笔记: {profile['notes_completed']} 完成,"
              f" {mastered} 已掌握, {in_progress} 复习中")
        print(f"  写作字数: {profile['words_written']}/{profile['words_target']}"
              f" ({write_pct:.0f}%)")
        print(f"  训练模式: {profile['training_mode']}")
        print(f"  强项: {profile['specialty']}")
        print(f"  弱项: {profile['weakness']}")

    print("\n" + "=" * 60)


def assign_task(node_id: str, day: int):
    """分配当日训练任务"""
    profile = load_profile(node_id)
    profile["current_day"] = day
    save_profile(node_id, profile)

    # 加载练习题库
    reading_ex = []
    writing_ex = []
    rb_path = PROBLEM_BANK / "reading_exercises.json"
    wb_path = PROBLEM_BANK / "writing_exercises.json"
    if rb_path.exists():
        with open(rb_path, "r", encoding="utf-8") as f:
            reading_ex = json.load(f).get("exercises", [])
    if wb_path.exists():
        with open(wb_path, "r", encoding="utf-8") as f:
            writing_ex = json.load(f).get("exercises", [])

    # 根据段位推荐练习
    level_map = {"初段": 1, "二段": 2, "三段": 3, "四段": 4, "五段": 5,
                 "六段": 6, "七段": 7, "八段": 8, "九段": 9}
    current_level = level_map.get(profile["level"], 1)

    # 筛选合适难度的练习
    difficulty_map = {1: "初段", 2: "二段", 3: "三段", 4: "四段",
                      5: "五段", 6: "六段", 7: "七段", 8: "八段", 9: "九段"}
    target_diff = difficulty_map.get(current_level, "初段")

    suitable_reading = [e for e in reading_ex
                        if e["difficulty"] == target_diff
                        and e["id"] not in profile.get("exercises_done", [])]
    suitable_writing = [e for e in writing_ex
                        if e["difficulty"] == target_diff
                        and e["id"] not in profile.get("exercises_done", [])]

    print(f"\n[Day {day}] {profile['name']} 今日任务分配:")
    print("-" * 40)

    # 阅读任务
    if suitable_reading:
        task = suitable_reading[0]
        print(f"\n  阅读练习 [{task['id']}]: {task['title']}")
        print(f"  难度: {task['difficulty']} | 限时: {task['time_limit_min']} 分钟")
        print(f"  说明: {task['instruction'][:80]}...")
    else:
        print("\n  阅读练习: 暂无匹配难度的新练习，建议复习已有练习")

    # 写作任务
    if suitable_writing:
        task = suitable_writing[0]
        print(f"\n  写作练习 [{task['id']}]: {task['title']}")
        print(f"  难度: {task['difficulty']} | 限时: {task['time_limit_min']} 分钟")
        print(f"  说明: {task['instruction'][:80]}...")
    else:
        print("\n  写作练习: 暂无匹配难度的新练习")

    # 复习提醒
    notes = load_notes(node_id)
    today = datetime.now().date()
    due_reviews = []
    for note in notes:
        for r_key, r_data in note.get("reviews", {}).items():
            if r_data.get("planned_date") and not r_data.get("completed"):
                planned = datetime.fromisoformat(r_data["planned_date"]).date()
                if planned <= today:
                    due_reviews.append((note["paper_title"], r_key))

    if due_reviews:
        print(f"\n  复习提醒 ({len(due_reviews)} 项待复习):")
        for title, r_key in due_reviews:
            print(f"    - {title} [{r_key}]")

    print()
    return True


def submit_note(node_id: str, paper_id: str):
    """提交精读笔记"""
    profile = load_profile(node_id)
    notes = load_notes(node_id)
    today = datetime.now().date().isoformat()

    # 创建笔记记录
    note = {
        "id": paper_id,
        "paper_title": paper_id,  # 实际使用中传入论文标题
        "submitted_at": datetime.now().isoformat(),
        "submitted_by": node_id,
        "score": None,  # Hermes 评审后填写
        "status": "in_progress",  # in_progress → mastered
        "reviews": {},
    }

    # 计算复习日期
    for r_key, interval_days in REVIEW_INTERVALS.items():
        planned = datetime.now() + timedelta(days=interval_days)
        note["reviews"][r_key] = {
            "planned_date": planned.date().isoformat(),
            "completed": False,
            "remembered": None,
        }

    notes.append(note)
    save_notes(node_id, notes)

    # 更新档案
    profile["papers_read"] += 1
    profile["notes_completed"] += 1
    save_profile(node_id, profile)

    print(f"\n[OK] {profile['name']} 已提交精读笔记: {paper_id}")
    print(f"  累计阅读: {profile['papers_read']} 篇")
    print(f"  复习计划:")
    for r_key, r_data in note["reviews"].items():
        print(f"    {r_key}: {r_data['planned_date']}")
    print()
    return True


def show_review_schedule(node_id: str):
    """显示间隔复习计划"""
    profile = load_profile(node_id)
    notes = load_notes(node_id)
    today = datetime.now().date()

    print(f"\n{profile['name']} 间隔复习计划")
    print("-" * 50)

    if not notes:
        print("  暂无精读笔记，无需复习。")
        print()
        return

    upcoming = []
    overdue = []
    completed_all = []

    for note in notes:
        for r_key in ["R1", "R2", "R3", "R4"]:
            r_data = note["reviews"].get(r_key, {})
            if r_data.get("completed"):
                continue
            if not r_data.get("planned_date"):
                continue
            planned = datetime.fromisoformat(r_data["planned_date"]).date()
            entry = {
                "paper": note["paper_title"],
                "review": r_key,
                "planned": planned.isoformat(),
                "days_delta": (planned - today).days,
            }
            if entry["days_delta"] < 0:
                overdue.append(entry)
            else:
                upcoming.append(entry)

    if overdue:
        print(f"\n  逾期未复习 ({len(overdue)} 项):")
        for e in sorted(overdue, key=lambda x: x["days_delta"]):
            print(f"    [{e['review']}] {e['paper']}"
                  f" — 逾期 {abs(e['days_delta'])} 天")

    if upcoming:
        print(f"\n  待复习 ({len(upcoming)} 项):")
        for e in sorted(upcoming, key=lambda x: x["days_delta"]):
            if e["days_delta"] == 0:
                label = "今天"
            elif e["days_delta"] == 1:
                label = "明天"
            else:
                label = f"{e['days_delta']} 天后"
            print(f"    [{e['review']}] {e['paper']} — {label} ({e['planned']})")

    mastered_count = sum(1 for n in notes if n.get("status") == "mastered")
    print(f"\n  已掌握: {mastered_count}/{len(notes)} 篇")
    print()


def weekly_report():
    """生成周报"""
    print("=" * 60)
    print("  小龙虾网络 · 论文学习训练周报")
    print(f"  生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)

    total_read = 0
    total_notes = 0
    total_words = 0

    for node_id in NODES:
        profile = load_profile(node_id)
        notes = load_notes(node_id)
        mastered = sum(1 for n in notes if n.get("status") == "mastered")

        total_read += profile["papers_read"]
        total_notes += profile["notes_completed"]
        total_words += profile["words_written"]

        print(f"\n  {profile['name']}:")
        print(f"    段位: {profile['level']} (Day {profile['current_day']}/15)")
        print(f"    本周阅读: {profile['papers_read']} 篇")
        print(f"    精读笔记: {profile['notes_completed']} 篇 ({mastered} 已掌握)")
        print(f"    写作字数: {profile['words_written']}")

        # 更新字数（模拟：实际应从提交的文件统计）
        save_profile(node_id, profile)

    print(f"\n  全网络汇总:")
    print(f"    论文阅读: {total_read} 篇")
    print(f"    精读笔记: {total_notes} 篇")
    print(f"    写作字数: {total_words} 字")
    print("\n" + "=" * 60)


# ── 主入口 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="小龙虾网络 · 论文学习训练器 V1")
    parser.add_argument("--action", required=True,
                        choices=["status", "assign", "submit",
                                 "review-schedule", "weekly-report"],
                        help="执行动作")
    parser.add_argument("--node", default=None,
                        help="目标节点 (qoder/xiaochen/zhuguxia)")
    parser.add_argument("--day", type=int, default=1,
                        help="训练天数 (assign 时使用)")
    parser.add_argument("--paper", default=None,
                        help="论文标识 (submit 时使用)")

    args = parser.parse_args()

    if args.action == "status":
        show_status()
    elif args.action == "assign":
        if not args.node:
            for n in NODES:
                assign_task(n, args.day)
        else:
            assign_task(args.node, args.day)
    elif args.action == "submit":
        if not args.node:
            print("[ERROR] submit 需要指定 --node")
            sys.exit(1)
        if not args.paper:
            print("[ERROR] submit 需要指定 --paper")
            sys.exit(1)
        submit_note(args.node, args.paper)
    elif args.action == "review-schedule":
        if not args.node:
            for n in NODES:
                show_review_schedule(n)
        else:
            show_review_schedule(args.node)
    elif args.action == "weekly-report":
        weekly_report()


if __name__ == "__main__":
    main()
