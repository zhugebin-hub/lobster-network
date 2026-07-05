#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小薇 - 围棋训练脚本 V1 (基础型)
功能：从零基础开始系统学习围棋，7天速成30级→25级
类型：基础型 — 高优先级基础概念、循序渐进、每天复盘
"""

import os
import json
import time
import random
import glob
from datetime import datetime
from pathlib import Path

# === 配置 ===
MY_NAME = "小薇"
MY_NODE_ID = "xiaowei"
COACH_NAME = "诸葛马 (教练)"
MY_TYPE = "基础型"
START_LEVEL = "30k"
TARGET_LEVEL = "25k"
QUEUE_DIR = "/shared/messages/queue"
MY_INBOX = os.path.join(QUEUE_DIR, "xiaowei", "inbox")
MY_OUTBOX = os.path.join(QUEUE_DIR, "xiaowei", "outbox")
MY_PROCESSED = os.path.join(QUEUE_DIR, "xiaowei", "processed")
STATE_FILE = os.path.join(QUEUE_DIR, "xiaowei", "state.json")
TRAINING_DIR = "/shared/training/go/xiaowei"
PROFILE_FILE = os.path.join(TRAINING_DIR, "profile.json")
PROGRESS_FILE = os.path.join(TRAINING_DIR, "progress.json")
DAILY_LOG_DIR = os.path.join(TRAINING_DIR, "daily_log")
PROBLEM_HISTORY_DIR = os.path.join(TRAINING_DIR, "problem_history")
WRONG_BOOK_FILE = os.path.join(TRAINING_DIR, "wrong_book.json")
PROBLEM_BANK = "/shared/training/go/problem_bank"

# 基础型参数 — 入门者正确率偏低，更注重「理解」而非「速度」
ACCURACY_BASELINE = {
    "入门": 0.85,    # Day1-3 基础概念
    "初级": 0.70,    # Day4-5 简单死活/连接
    "中级": 0.50,    # Day6-7 定式/综合
    "高级": 0.25,    # 暂不涉及
}
SOLVE_TIME_RANGE = (2.0, 5.0)  # 每题模拟思考时间(秒)——新手要多想

# 围棋坐标
COLS = "ABCDEFGHJKLMNOPQRST"


def init_dirs():
    """初始化目录"""
    for d in [MY_INBOX, MY_OUTBOX, MY_PROCESSED, TRAINING_DIR,
              DAILY_LOG_DIR, PROBLEM_HISTORY_DIR]:
        os.makedirs(d, exist_ok=True)


def load_state():
    """加载状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_messages": [], "last_heartbeat": None, "errors": 0}


def save_state(state):
    """保存状态"""
    state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["processed_messages"] = state.get("processed_messages", [])[-100:]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def load_profile():
    """加载档案"""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return {
        "name": MY_NAME,
        "node_id": MY_NODE_ID,
        "type": MY_TYPE,
        "start_level": START_LEVEL,
        "target_level": TARGET_LEVEL,
        "total_problems_solved": 0,
        "total_correct": 0,
        "total_games": 0,
        "total_wins": 0,
        "streak": 0,
        "current_day": 0,
        "joined_at": datetime.now().strftime("%Y-%m-%d"),
        "last_training_date": None,
    }


def save_profile(profile):
    """保存档案"""
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def load_progress():
    """加载进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {
        "days_completed": [],
        "current_day": 1,
        "wrong_book": {},
        "skill_scores": {
            "吃子": 0, "死活": 0, "手筋": 0,
            "布局": 0, "定式": 0,
        },
        "daily_logs": {},
    }


def save_progress(progress):
    """保存进度"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def check_inbox():
    """检查收件箱"""
    messages = []
    if os.path.exists(MY_INBOX):
        for f in sorted(os.listdir(MY_INBOX)):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(MY_INBOX, f), 'r') as fp:
                        msg = json.load(fp)
                        msg['file'] = f
                        messages.append(msg)
                except:
                    pass
    return messages


def process_training_task(msg):
    """处理每日训练任务"""
    day = msg.get("day", 1)
    topic = msg.get("topic", "未知")
    problems = msg.get("problems", [])

    print(f"\n{'='*60}")
    print(f"🐚 小薇 · Day {day} 训练: {topic}")
    print(f"   级别: 30k → 25k | 类型: 基础型")
    print(f"   题目数: {len(problems)}")
    print(f"{'='*60}")

    correct = 0
    total = 0
    task_details = []
    wrong_ids = []

    for i, prob in enumerate(problems, 1):
        prob_id = prob.get("problem_id", f"p{i}")
        prob_type = prob.get("type", "未知")
        difficulty = prob.get("difficulty", "入门")
        title = prob.get("title", "未命名")

        # 模拟思考
        solve_time = random.uniform(*SOLVE_TIME_RANGE)
        time.sleep(solve_time * 0.01)

        # 根据难度和题型模拟正确率
        baseline = ACCURACY_BASELINE.get(difficulty, 0.6)
        # 基础型：实战题额外降低
        if prob_type == "实战":
            baseline *= 0.7
        is_correct = random.random() < baseline

        print(f"\n  [{i}/{len(problems)}] {prob_type} · {difficulty}")
        print(f"   题目: {title}")
        print(f"   {prob.get('description', '')[:80]}...")

        if is_correct:
            correct += 1
            print(f"   ✅ 正确！({solve_time:.1f}s)")
        else:
            wrong_ids.append(prob_id)
            print(f"   ❌ 错误（答案: {prob.get('answer', '?')})")
            print(f"   💡 解析: {prob.get('solution', '暂无')[:100]}...")

        total += 1
        task_details.append({
            "problem_id": prob_id,
            "type": prob_type,
            "difficulty": difficulty,
            "correct": is_correct,
            "solve_time": round(solve_time, 1),
        })

        # 更新技能分
        progress = load_progress()
        if prob_type in progress["skill_scores"]:
            delta = 1 if is_correct else -0.5
            progress["skill_scores"][prob_type] = max(0,
                progress["skill_scores"].get(prob_type, 0) + delta)

    # 汇总
    accuracy = correct / total if total > 0 else 0
    print(f"\n{'─'*60}")
    print(f"📊 Day {day} 训练结果")
    print(f"   正确: {correct}/{total} | 准确率: {accuracy:.1%}")
    print(f"   错题: {len(wrong_ids)} 题 — 已加入错题本")

    # 更新档案
    profile = load_profile()
    profile["total_problems_solved"] = profile.get("total_problems_solved", 0) + total
    profile["total_correct"] = profile.get("total_correct", 0) + correct
    profile["last_training_date"] = datetime.now().strftime("%Y-%m-%d")
    profile["current_day"] = day
    save_profile(profile)

    # 更新进度
    progress = load_progress()
    progress["current_day"] = day
    progress["daily_logs"][f"day{day}"] = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": topic,
        "total": total,
        "correct": correct,
        "accuracy": accuracy,
        "wrong_ids": wrong_ids,
    }
    for pid in wrong_ids:
        if pid not in progress["wrong_book"]:
            progress["wrong_book"][pid] = {"count": 0, "last_seen": None}
        progress["wrong_book"][pid]["count"] += 1
        progress["wrong_book"][pid]["last_seen"] = datetime.now().strftime("%Y-%m-%d")
    save_progress(progress)

    # 保存每日日志
    log_file = os.path.join(DAILY_LOG_DIR, f"day{day}_{datetime.now().strftime('%Y%m%d')}.json")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "day": day,
            "topic": topic,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "details": task_details,
            "wrong_ids": wrong_ids,
        }, f, indent=2, ensure_ascii=False)

    # 进度评价
    if accuracy >= 0.80:
        print(f"   🌟 评价: 超常发挥！基础扎实，继续保持")
    elif accuracy >= 0.60:
        print(f"   ✅ 评价: 正常进度，稳步前进")
    else:
        print(f"   ⚠️  评价: 建议复习今日错题，明日重做")

    return {
        "id": f"result-{msg['id']}",
        "from": MY_NODE_ID,
        "from_name": MY_NAME,
        "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "training_result",
        "reply_to": msg.get("id", ""),
        "result": {
            "day": day,
            "topic": topic,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "wrong_ids": wrong_ids,
            "skill_scores": progress.get("skill_scores", {}),
        },
    }


def submit_response(response):
    """提交响应"""
    response_file = os.path.join(MY_OUTBOX, f"{response['id']}.json")
    with open(response_file, 'w', encoding='utf-8') as f:
        json.dump(response, f, indent=2, ensure_ascii=False)
    print(f"📤 响应已提交: {response_file}")


def main():
    """主循环"""
    print(f"🐚 [{datetime.now().strftime('%H:%M:%S')}] {MY_NAME} (小薇) 训练脚本 v1.0 启动...")
    print(f"📍 级别: {START_LEVEL} → {TARGET_LEVEL} | 类型: {MY_TYPE}")
    print(f"📂 监控: {MY_INBOX}")
    print(f"📤 回复: {MY_OUTBOX}")
    print(f"📋 错题本: {WRONG_BOOK_FILE}")

    init_dirs()
    state = load_state()
    state["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)

    # 首次启动：初始化档案和进度
    profile = load_profile()
    save_profile(profile)

    progress = load_progress()
    save_progress(progress)

    print(f"\n📊 当前状态:")
    print(f"   已解决: {profile.get('total_problems_solved', 0)} 题")
    print(f"   准确率: {profile.get('total_correct', 0) / max(profile.get('total_problems_solved', 1), 1):.1%}" if profile.get('total_problems_solved') else "   准确率: 暂无数据（等待首次训练）")
    print(f"   当前Day: {progress.get('current_day', 1)}")
    print(f"   错题本: {len(progress.get('wrong_book', {}))} 题待复习")

    heartbeat_interval = 60
    last_heartbeat = 0

    while True:
        try:
            now = time.time()
            if now - last_heartbeat > heartbeat_interval:
                state = load_state()
                state["status"] = "running"
                state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_state(state)
                last_heartbeat = now

            messages = check_inbox()

            if not messages:
                time.sleep(3)
                continue

            print(f"\n📥 收到 {len(messages)} 条新消息")

            for msg in messages:
                msg_id = msg.get("id", "unknown")
                msg_type = msg.get("type", "")
                print(f"   📨 处理: {msg_id} (类型: {msg_type})")

                response = None

                if msg_type == "daily_training":
                    response = process_training_task(msg)

                if response:
                    submit_response(response)

                # 移动到 processed
                src_file = os.path.join(MY_INBOX, msg.get('file', ''))
                dst_file = os.path.join(MY_PROCESSED, msg.get('file', ''))
                if os.path.exists(src_file):
                    os.rename(src_file, dst_file)

                state = load_state()
                state["processed_messages"].append(msg_id)
                save_state(state)

        except Exception as e:
            print(f"❌ 错误: {e}")
            state = load_state()
            state["errors"] = state.get("errors", 0) + 1
            save_state(state)
            time.sleep(5)


if __name__ == "__main__":
    main()
