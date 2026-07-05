#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋教练调度器 V3
功能：根据教学方案自动出题、分发训练任务、组织对局、批改结果
"""

import os
import json
import time
import random
from datetime import datetime
from pathlib import Path

# === 配置 ===
COACH_NAME = "诸葛马 (教练)"
QUEUE_DIR = "/shared/messages/queue"
TRAINING_DIR = "/shared/training/go"
STATUS_FILE = os.path.join(TRAINING_DIR, "status.json")
PLAN_FILE = os.path.join(TRAINING_DIR, "GO_TRAINING_PLAN_V3.md")
PROBLEM_BANK = os.path.join(TRAINING_DIR, "problem_bank")
MATCHES_DIR = os.path.join(TRAINING_DIR, "matches")

PLAYERS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "inbox": os.path.join(QUEUE_DIR, "xiaochen", "inbox"),
        "outbox": os.path.join(QUEUE_DIR, "xiaochen", "outbox"),
        "processed": os.path.join(QUEUE_DIR, "xiaochen", "processed"),
        "profile": os.path.join(TRAINING_DIR, "xiaochen", "profile.json"),
        "daily_log": os.path.join(TRAINING_DIR, "xiaochen", "daily_log"),
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "inbox": os.path.join(QUEUE_DIR, "zhuguxia", "inbox"),
        "outbox": os.path.join(QUEUE_DIR, "zhuguxia", "outbox"),
        "processed": os.path.join(QUEUE_DIR, "zhuguxia", "processed"),
        "profile": os.path.join(TRAINING_DIR, "zhuguxia", "profile.json"),
        "daily_log": os.path.join(TRAINING_DIR, "zhuguxia", "daily_log"),
    },
}

# 每日训练计划（按天数）
DAILY_PLAN = {
    1: {"topic": "规则基础与死活入门", "tasks": [
        {"category": "死活", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
        {"category": "手筋", "difficulty": "入门", "count_steady": 2, "count_fast": 3},
    ]},
    2: {"topic": "吃子技巧进阶", "tasks": [
        {"category": "手筋", "difficulty": "入门", "count_steady": 5, "count_fast": 8},
    ]},
    3: {"topic": "气的概念与对杀入门", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "手筋", "difficulty": "入门", "count_steady": 2, "count_fast": 3},
    ]},
    4: {"topic": "连接与切断", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "死活", "difficulty": "初级", "count_steady": 2, "count_fast": 3},
    ]},
    5: {"topic": "第1周综合复习", "tasks": [
        {"category": "死活", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
        {"category": "手筋", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
    ]},
    6: {"topic": "第1周考核", "tasks": [
        {"category": "死活", "difficulty": "入门", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "入门", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ]},
    7: {"topic": "休息/自由对局", "tasks": []},
}

# 周计划扩展（Day8-28）
WEEK2_PLAN = {
    8: {"topic": "基本眼位（直三/曲三/丁四）", "tasks": [
        {"category": "死活", "difficulty": "入门", "count_steady": 5, "count_fast": 8},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ]},
    9: {"topic": "刀五与梅花五", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
    ]},
    10: {"topic": "板六与常见活形", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "死活", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
    ]},
    11: {"topic": "点眼与做眼", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ]},
    12: {"topic": "复习+错题重做", "tasks": [
        {"category": "死活", "difficulty": "入门", "count_steady": 4, "count_fast": 6},
        {"category": "手筋", "difficulty": "入门", "count_steady": 4, "count_fast": 6},
    ]},
    13: {"topic": "周考核", "tasks": [
        {"category": "死活", "difficulty": "入门", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "入门", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ]},
    14: {"topic": "休息", "tasks": []},
}

WEEK3_PLAN = {
    15: {"topic": "枷吃与征子进阶", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ]},
    16: {"topic": "扑与倒扑组合", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ]},
    17: {"topic": "挖与分断", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ]},
    18: {"topic": "尖与跳的手筋", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ]},
    19: {"topic": "复习+错题重做", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "手筋", "difficulty": "中级", "count_steady": 4, "count_fast": 6},
    ]},
    20: {"topic": "周考核", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "中级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ]},
    21: {"topic": "休息", "tasks": []},
}

WEEK4_PLAN = {
    22: {"topic": "金角银边草肚皮", "tasks": [
        {"category": "布局", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "布局", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ]},
    23: {"topic": "星位开局", "tasks": [
        {"category": "定式", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "布局", "difficulty": "初级", "count_steady": 2, "count_fast": 3},
    ]},
    24: {"topic": "小目开局", "tasks": [
        {"category": "定式", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "定式", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ]},
    25: {"topic": "简单官子（大小判断）", "tasks": [
        {"category": "官子", "difficulty": "入门", "count_steady": 5, "count_fast": 8},
    ]},
    26: {"topic": "复习+错题重做", "tasks": [
        {"category": "布局", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
        {"category": "定式", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
        {"category": "官子", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
    ]},
    27: {"topic": "阶段考核", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "布局", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
        {"category": "官子", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
    ]},
    28: {"topic": "休息+阶段总结", "tasks": []},
}

ALL_DAILY_PLAN = {}
ALL_DAILY_PLAN.update(DAILY_PLAN)
ALL_DAILY_PLAN.update(WEEK2_PLAN)
ALL_DAILY_PLAN.update(WEEK3_PLAN)
ALL_DAILY_PLAN.update(WEEK4_PLAN)


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
        print(f"⚠️ 加载题库失败 {filename}: {e}")
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


def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    return {
        "phase": 1, "week": 1, "day": 3,
        "topic": "气的概念与对杀入门",
        "started_at": None, "completed_at": None,
        "players": {}, "game_result": {},
        "next_day_topic": "连接与切断",
    }


def save_status(status):
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def send_to_inbox(player_key, message):
    player = PLAYERS[player_key]
    os.makedirs(player["inbox"], exist_ok=True)
    fpath = os.path.join(player["inbox"], f"{message['id']}.json")
    with open(fpath, 'w') as f:
        json.dump(message, f, indent=2, ensure_ascii=False)
    print(f"  📬 已发送至 {player['name']} inbox: {message['id']}")


def create_training_task(day_info, player_key, is_fast=False):
    """创建训练任务消息"""
    player = PLAYERS[player_key]
    status = load_status()

    task_id = f"go-train-v3-{datetime.now().strftime('%Y%m%d')}-{player_key[:3]}-{status['day']:02d}"

    problems = []
    for task in day_info["tasks"]:
        count = task["count_fast"] if is_fast else task["count_steady"]
        selected = select_problems(task["category"], task["difficulty"], count)
        problems.extend(selected)

    if not problems:
        print(f"  ⚠️ {player['name']} Day{status['day']} 无可用题目")
        return None

    return {
        "id": task_id,
        "from": COACH_NAME,
        "to": player["name"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "training_task",
        "priority": "high",
        "task": {
            "phase": status["phase"],
            "week": status["week"],
            "day": status["day"],
            "category": problems[0].get("type", "死活"),
            "difficulty": problems[0].get("difficulty", "入门"),
            "title": day_info["topic"],
            "description": f"第{status['week']}周 Day{status['day']}训练",
            "problems": problems,
            "problem_count": len(problems),
            "time_limit": 70 if is_fast else 60,
            "min_accuracy": 0.8,
        }
    }


def create_game_instruction(day, player_key, color):
    """创建对局指令"""
    player = PLAYERS[player_key]
    status = load_status()
    game_id = f"go-game-v3-{datetime.now().strftime('%Y%m%d')}-{day:02d}"

    return {
        "id": f"go-game-{game_id}-{player_key[:3]}",
        "from": COACH_NAME,
        "to": player["name"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "game_instruction",
        "game": {
            "game_id": game_id,
            "day": day,
            "phase": status["phase"],
            "week": status["week"],
            "your_color": color,
            "opponent": "诸葛虾" if player_key == "xiaochen" else "小陈",
            "board_size": 9,
            "status": "your_turn" if color == "black" else "waiting",
        }
    }


def create_review_request(game_id, player_key):
    """创建复盘指令"""
    player = PLAYERS[player_key]
    return {
        "id": f"go-review-{game_id}-{player_key[:3]}",
        "from": COACH_NAME,
        "to": player["name"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "review_request",
        "game_id": game_id,
        "instruction": f"请对今日对局进行复盘分析",
    }


def process_results():
    """处理学员提交的结果"""
    for player_key, player in PLAYERS.items():
        outbox = player["outbox"]
        if not os.path.exists(outbox):
            continue
        for f in sorted(os.listdir(outbox)):
            if not f.endswith('.json'):
                continue
            fpath = os.path.join(outbox, f)
            try:
                with open(fpath, 'r') as fh:
                    result = json.load(fh)
                if result.get("type") == "training_result":
                    print(f"  ✅ 收到 {player['name']} 训练结果: {result['result'].get('summary', '')}")
                elif result.get("type") == "review_result":
                    print(f"  📝 收到 {player['name']} 复盘报告")
            except Exception as e:
                print(f"  ⚠️ 处理结果失败 {f}: {e}")


def dispatch_day(day):
    """分发某一天的训练任务"""
    status = load_status()
    status["day"] = day

    if day in ALL_DAILY_PLAN:
        day_info = ALL_DAILY_PLAN[day]
        status["topic"] = day_info["topic"]
    else:
        status["topic"] = f"第{day}天训练"
        day_info = {"topic": status["topic"], "tasks": []}

    print(f"\n{'='*60}")
    print(f"🐴 教练调度 - Day {day}: {status['topic']}")
    print(f"{'='*60}")

    # 分发训练任务
    if day_info["tasks"]:
        # 小陈（稳健型）
        task_xc = create_training_task(day_info, "xiaochen", is_fast=False)
        if task_xc:
            send_to_inbox("xiaochen", task_xc)

        # 诸葛虾（加速型）
        task_zgx = create_training_task(day_info, "zhuguxia", is_fast=True)
        if task_zgx:
            send_to_inbox("zhuguxia", task_zgx)

        # 对局指令（非休息日）
        if day % 7 != 0:
            game_id = f"go-game-v3-{datetime.now().strftime('%Y%m%d')}-{day:02d}"
            send_to_inbox("xiaochen", create_game_instruction(day, "xiaochen", "black" if day % 2 == 1 else "white"))
            send_to_inbox("zhuguxia", create_game_instruction(day, "zhuguxia", "white" if day % 2 == 1 else "black"))

            # 复盘指令
            time.sleep(1)
            send_to_inbox("xiaochen", create_review_request(game_id, "xiaochen"))
            send_to_inbox("zhuguxia", create_review_request(game_id, "zhuguxia"))

    # 更新状态
    status["started_at"] = datetime.now().isoformat()
    status["next_day_topic"] = ALL_DAILY_PLAN.get(day + 1, {}).get("topic", "未知")

    # 计算周次
    if day <= 7:
        status["week"] = 1
    elif day <= 14:
        status["week"] = 2
    elif day <= 21:
        status["week"] = 3
    else:
        status["week"] = 4

    save_status(status)
    print(f"\n📊 状态已更新: Phase {status['phase']}, Week {status['week']}, Day {day}")


def main():
    print(f"🐴 [{datetime.now().strftime('%H:%M:%S')}] 围棋教练调度器 V3 启动")
    print(f"📂 题库: {PROBLEM_BANK}")
    print(f"📊 状态: {STATUS_FILE}")

    # 检查是否有待处理的结果
    print("\n📥 检查学员提交结果...")
    process_results()

    # 获取当前天数
    status = load_status()
    current_day = status.get("day", 3)

    # 分发今日任务
    dispatch_day(current_day)

    print(f"\n✅ 调度完成。下一天: Day {current_day + 1} - {status.get('next_day_topic', '未知')}")


if __name__ == "__main__":
    main()
