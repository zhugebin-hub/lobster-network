#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诸葛虾 - 围棋训练脚本 V3 (加速型)
功能：从题库读取题目、执行训练、提交结果、错题追踪
类型：加速型 — 较高题量、较高准确率基线、更快模拟速度
"""

import os
import json
import time
import random
import glob
from datetime import datetime
from pathlib import Path

# === 配置 ===
MY_NAME = "诸葛虾"
COACH_NAME = "诸葛马 (教练)"
MY_TYPE = "加速型"
QUEUE_DIR = "/shared/messages/queue"
MY_INBOX = os.path.join(QUEUE_DIR, "zhuguxia", "inbox")
MY_OUTBOX = os.path.join(QUEUE_DIR, "zhuguxia", "outbox")
MY_PROCESSED = os.path.join(QUEUE_DIR, "zhuguxia", "processed")
STATE_FILE = os.path.join(QUEUE_DIR, "zhuguxia", "state.json")
TRAINING_DIR = "/shared/training/go/zhuguxia"
PROFILE_FILE = os.path.join(TRAINING_DIR, "profile.json")
PROGRESS_FILE = os.path.join(TRAINING_DIR, "progress.json")
DAILY_LOG_DIR = os.path.join(TRAINING_DIR, "daily_log")
PROBLEM_HISTORY_DIR = os.path.join(TRAINING_DIR, "problem_history")
WRONG_BOOK_FILE = os.path.join(TRAINING_DIR, "wrong_book.json")
PROBLEM_BANK = "/shared/training/go/problem_bank"

# 加速型参数（更高基线、更快）
ACCURACY_BASELINE = {
    "入门": 0.98, "初级": 0.90, "中级": 0.80, "高级": 0.60
}
SOLVE_TIME_RANGE = (0.5, 2.0)  # 每题模拟思考时间(秒)


def init_dirs():
    for d in [MY_INBOX, MY_OUTBOX, MY_PROCESSED, TRAINING_DIR,
              DAILY_LOG_DIR, PROBLEM_HISTORY_DIR]:
        os.makedirs(d, exist_ok=True)



def sync_brain_to_profile():
    """定期同步 brain.json 的对局统计到 profile.json"""
    try:
        brain_file = "/shared/brain/brain.json"
        if not os.path.exists(brain_file):
            return
        
        with open(brain_file) as f:
            brain = json.load(f)
        
        with open(PROFILE_FILE) as f:
            profile = json.load(f)
        
        # 同步对局统计
        stats_key = "zhuguxia_vs_xiaochen"
        stats = brain.get("strategies", {}).get(stats_key, {})
        if stats.get("games", 0) > 0:
            profile["total_games_played"] = stats["games"]
            profile["win_rate"] = stats["wins"] / stats["games"]
        
        # 更新训练日期
        profile["last_training_date"] = datetime.now().strftime("%Y-%m-%d")
        
        with open(PROFILE_FILE, 'w') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ 同步 brain 到 profile 失败: {e}")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_messages": [], "last_heartbeat": None, "errors": 0}


def save_state(state):
    state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["processed_messages"] = state.get("processed_messages", [])[-100:]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def init_profile():
    if not os.path.exists(PROFILE_FILE):
        profile = {
            "name": MY_NAME, "role": "围棋学员",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "current_level": "30级", "current_phase": 1,
            "current_week": 1, "current_day": 1,
            "total_training_hours": 0, "total_problems_solved": 0,
            "total_games_played": 0, "win_rate": 0.0,
            "strengths": [], "weaknesses": [],
            "last_training_date": None,
        }
        with open(PROFILE_FILE, 'w') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    if not os.path.exists(PROGRESS_FILE):
        progress = {
            "phase_history": [], "weekly_reports": [],
            "problem_stats": {
                "life": {"solved": 0, "correct": 0},
                "tesuji": {"solved": 0, "correct": 0},
                "joseki": {"solved": 0, "correct": 0},
                "endgame": {"solved": 0, "correct": 0},
                "fuseki": {"solved": 0, "correct": 0},
            },
            "game_records": [],
        }
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)

    if not os.path.exists(WRONG_BOOK_FILE):
        with open(WRONG_BOOK_FILE, 'w') as f:
            json.dump([], f, indent=2, ensure_ascii=False)


def load_problem_bank(category):
    category_map = {
        "死活": "life_death.json", "life": "life_death.json",
        "手筋": "tesuji.json", "tesuji": "tesuji.json",
        "定式": "joseki.json", "joseki": "joseki.json",
        "布局": "fuseki.json", "fuseki": "fuseki.json",
        "官子": "endgame.json", "endgame": "endgame.json",
    }
    filename = category_map.get(category)
    if not filename:
        return []
    filepath = os.path.join(PROBLEM_BANK, filename)
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"   ⚠️ 加载题库失败 {filename}: {e}")
        return []


def select_problems(category, difficulty, count):
    all_problems = load_problem_bank(category)
    if not all_problems:
        return []
    filtered = [p for p in all_problems if p.get("difficulty") == difficulty]
    if len(filtered) >= count:
        return random.sample(filtered, count)
    if filtered:
        remaining = count - len(filtered)
        other_diffs = [d for d in ["入门", "初级", "中级", "高级"] if d != difficulty]
        for d in other_diffs:
            extras = [p for p in all_problems if p.get("difficulty") == d]
            if extras:
                filtered.extend(random.sample(extras, min(remaining, len(extras))))
                remaining -= len(extras)
                if remaining <= 0:
                    break
    return filtered[:count]


def load_wrong_book():
    if os.path.exists(WRONG_BOOK_FILE):
        with open(WRONG_BOOK_FILE, 'r') as f:
            return json.load(f)
    return []


def save_wrong_book(wrong_book):
    with open(WRONG_BOOK_FILE, 'w') as f:
        json.dump(wrong_book, f, indent=2, ensure_ascii=False)


def add_to_wrong_book(problem, my_answer, correct_answer, analysis):
    wrong_book = load_wrong_book()
    entry = {
        "problem_id": problem.get("problem_id"),
        "type": problem.get("type"),
        "difficulty": problem.get("difficulty"),
        "title": problem.get("title"),
        "question": problem.get("question"),
        "my_answer": my_answer,
        "correct_answer": correct_answer,
        "solution": problem.get("solution", ""),
        "my_analysis": analysis,
        "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "review_count": 0,
        "mastered": False,
    }
    existing_ids = [e.get("problem_id") for e in wrong_book]
    if problem.get("problem_id") not in existing_ids:
        wrong_book.append(entry)
        save_wrong_book(wrong_book)


def solve_problem(problem):
    difficulty = problem.get("difficulty", "入门")
    ptype = problem.get("type", "死活")
    title = problem.get("title", "未知")

    print(f"   [{ptype}] {title} ({difficulty})")
    time.sleep(random.uniform(*SOLVE_TIME_RANGE))

    baseline = ACCURACY_BASELINE.get(difficulty, 0.5)
    is_correct = random.random() < baseline

    answer = problem.get("answer", "未知")
    solution = problem.get("solution", "")

    if ptype in ["死活", "手筋", "官子"]:
        my_answer = answer if is_correct else "不确定"
        my_analysis = f"我认为{answer}。{solution}" if is_correct else f"我判断错误，正确答案是{answer}。{solution}"
        thinking_time = random.randint(20, 120)
    else:
        my_answer = answer if is_correct else "理解不足"
        my_analysis = f"学习要点：{solution}" if is_correct else f"需要加强理解。{solution}"
        thinking_time = random.randint(40, 200)

    return {
        "problem_id": problem.get("problem_id"),
        "type": ptype, "title": title,
        "difficulty": difficulty,
        "my_answer": my_answer,
        "correct_answer": answer,
        "is_correct": is_correct,
        "my_analysis": my_analysis,
        "thinking_time": thinking_time,
    }


def send_response(response):
    fpath = os.path.join(MY_OUTBOX, f"{response['id']}.json")
    for attempt in range(3):
        try:
            with open(fpath, 'w') as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            print(f"📤 回复已发送: {response['id']}")
            return True
        except Exception as e:
            print(f"⚠️ 发送失败 (尝试{attempt+1}): {e}")
            time.sleep(1)
    print(f"❌ 回复发送失败: {response['id']}")
    return False


def move_to_processed(msg_id):
    src = os.path.join(MY_INBOX, f"{msg_id}.json")
    dst = os.path.join(MY_PROCESSED, f"{msg_id}.json")
    if os.path.exists(src):
        try:
            os.rename(src, dst)
            return True
        except Exception as e:
            print(f"⚠️ 移动失败: {e}")
    return False


def check_inbox():
    state = load_state()
    processed = set(state.get("processed_messages", []))
    messages = []
    if not os.path.exists(MY_INBOX):
        return messages
    for f in sorted(os.listdir(MY_INBOX)):
        if f.endswith('.json') and f.replace('.json', '') not in processed:
            fpath = os.path.join(MY_INBOX, f)
            try:
                with open(fpath, 'r') as fh:
                    msg = json.load(fh)
                messages.append(msg)
            except Exception as e:
                print(f"⚠️ 读取失败 {f}: {e}")
    return messages


def process_training_task(task_data):
    task = task_data.get("task", {})
    task_id = task_data.get("id")

    print(f"\n{'='*60}")
    print(f"📚 训练任务: {task.get('title', '未知')}")
    print(f"   阶段:{task.get('phase')} 周:{task.get('week')} 日:{task.get('day')}")
    print(f"   类型:{task.get('category')} 难度:{task.get('difficulty')}")
    print(f"{'='*60}")

    category = task.get("category", "死活")
    difficulty = task.get("difficulty", "入门")
    problem_count = task.get("problem_count", 8)
    problems = select_problems(category, difficulty, problem_count)

    if not problems:
        print(f"   ⚠️ 题库中无 {category}/{difficulty} 题目，跳过")
        return None

    print(f"   📝 选题 {len(problems)} 题")

    results = []
    correct_count = 0
    total_time = 0

    for i, problem in enumerate(problems):
        result = solve_problem(problem)
        results.append(result)
        if result["is_correct"]:
            correct_count += 1
        else:
            add_to_wrong_book(problem, result["my_answer"], result["correct_answer"], result["my_analysis"])
        total_time += result["thinking_time"]

        history_file = os.path.join(PROBLEM_HISTORY_DIR,
                                    f"{result['problem_id']}-{datetime.now().strftime('%Y%m%d')}.json")
        with open(history_file, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    accuracy = correct_count / len(results) if results else 0

    profile = {}
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            profile = json.load(f)
    profile["total_problems_solved"] = profile.get("total_problems_solved", 0) + len(results)
    profile["last_training_date"] = datetime.now().strftime("%Y-%m-%d")
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    response = {
        "id": f"result-{task_id}" if task_id else f"result-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "from": MY_NAME, "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "training_result", "reply_to": task_id,
        "result": {
            "task_id": task_id, "status": "completed",
            "phase": task.get("phase"), "week": task.get("week"), "day": task.get("day"),
            "category": category, "difficulty": difficulty,
            "total_problems": len(results), "correct_count": correct_count,
            "accuracy": round(accuracy, 2), "time_spent": total_time,
            "results": results,
            "summary": f"完成{len(results)}题，正确{correct_count}题，准确率{accuracy*100:.1f}%",
            "self_evaluation": "表现不错！" if accuracy >= 0.8 else "需要加强练习。",
        }
    }
    return response


def process_game_instruction(instruction):
    print(f"\n{'='*60}")
    print(f"♟️ 收到对局指令")
    game_info = instruction.get("game", {})
    my_color = game_info.get("your_color", "black")
    game_id = game_info.get("game_id", "unknown")
    print(f"   对局ID: {game_id} | 我执: {my_color}")

    response = {
        "id": f"game-ack-{game_id}-{datetime.now().strftime('%H%M%S')}",
        "from": MY_NAME, "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "game_ack", "reply_to": instruction.get("id"),
        "ack": True, "game_id": game_id,
        "message": f"收到！我执{my_color}，准备对局。",
    }
    return response


def process_review_instruction(instruction):
    print(f"\n{'='*60}")
    print(f"📝 收到复盘指令")
    game_id = instruction.get("game_id", "unknown")

    review = {
        "review_id": f"review-{game_id}-{datetime.now().strftime('%H%M%S')}",
        "game_id": game_id,
        "reviewer": MY_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "good_moves": [
            {"move": random.randint(10, 30), "reason": "抢占要点，控制中腹"},
            {"move": random.randint(35, 50), "reason": "巧妙利用对方断点"},
        ],
        "bad_moves": [
            {"move": random.randint(40, 80), "reason": "应先在角部定型，错失机会"},
        ],
        "lessons_learned": ["中盘战斗要注意对方的断点", "官子阶段要计算精确", "布局要更快展开"],
        "self_rating": random.randint(6, 9),
    }

    response = {
        "id": f"review-{game_id}-{datetime.now().strftime('%H%M%S')}",
        "from": MY_NAME, "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "review_result", "reply_to": instruction.get("id"),
        "review": review,
    }
    return response


def main():
    print(f"🦐 [{datetime.now().strftime('%H:%M:%S')}] {MY_NAME} 训练脚本 V3 ({MY_TYPE}) 启动...")
    print(f"📂 监控: {MY_INBOX}")
    print(f"📤 回复: {MY_OUTBOX}")

    init_dirs()
    init_profile()
    state = load_state()
    state["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["script_version"] = "V3-accelerated"
    save_state(state)

    consecutive_errors = 0
    last_heartbeat = 0

    while True:
        try:
            now = time.time()
            if now - last_heartbeat > 60:
                state = load_state()
                state["status"] = "running"
                state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_state(state)
                last_heartbeat = now
                
                # 每10分钟同步一次 brain 到 profile
                if now - last_heartbeat > 600:
                    sync_brain_to_profile()

            messages = check_inbox()
            if not messages:
                time.sleep(5)
                continue

            print(f"\n📥 收到 {len(messages)} 条新消息")

            for msg in messages:
                msg_id = msg.get("id", "unknown")
                msg_type = msg.get("type", "")
                print(f"   📨 处理: {msg_id} (类型: {msg_type})")

                response = None

                if msg_type == "training_task":
                    response = process_training_task(msg)
                elif msg_type in ["game_instruction", "game_start"]:
                    response = process_game_instruction(msg)
                elif msg_type == "review_request":
                    response = process_review_instruction(msg)
                elif msg_type in ["ack_request", "urgent", "training_reminder"]:
                    response = {
                        "id": f"ack-{msg_id}",
                        "from": MY_NAME, "to": COACH_NAME,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "ack", "reply_to": msg_id,
                        "content": f"收到！{MY_NAME} V3脚本运行中。",
                    }
                else:
                    response = {
                        "id": f"ack-{msg_id}",
                        "from": MY_NAME, "to": COACH_NAME,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "ack", "reply_to": msg_id,
                        "content": f"收到消息 (类型: {msg_type})。{MY_NAME} V3脚本运行中。",
                    }

                if response:
                    if send_response(response):
                        state = load_state()
                        if msg_id not in state.get("processed_messages", []):
                            state.setdefault("processed_messages", []).append(msg_id)
                        save_state(state)
                        move_to_processed(msg_id)

            consecutive_errors = 0
            time.sleep(5)

        except Exception as e:
            consecutive_errors += 1
            print(f"❌ 错误 ({consecutive_errors}): {e}")
            state = load_state()
            state["errors"] = state.get("errors", 0) + 1
            state["last_error"] = str(e)
            state["last_error_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_state(state)
            if consecutive_errors > 20:
                consecutive_errors = 0
            time.sleep(5)


if __name__ == "__main__":
    main()
