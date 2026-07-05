#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋教练调度器 V6.0 - 深夜特训版 (Nocturnal Mode)
核心时段: 00:00 - 06:00 (北京时间)
模式: 无休 / 极限算力压榨
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
STATUS_FILE = os.path.join(TRAINING_DIR, "status_v6.json")
PROBLEM_BANK = os.path.join(TRAINING_DIR, "problem_bank")
LOG_FILE = os.path.join(TRAINING_DIR, "dispatcher_v6.log")

PLAYERS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "inbox": os.path.join(QUEUE_DIR, "xiaochen", "inbox"),
        "outbox": os.path.join(QUEUE_DIR, "xiaochen", "outbox"),
        "processed": os.path.join(QUEUE_DIR, "xiaochen", "processed"),
        "profile": os.path.join(TRAINING_DIR, "xiaochen", "profile.json"),
        "wrong_book": os.path.join(TRAINING_DIR, "xiaochen", "wrong_book.json"),
        "problem_history": os.path.join(TRAINING_DIR, "xiaochen", "problem_history"),
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "inbox": os.path.join(QUEUE_DIR, "zhuguxia", "inbox"),
        "outbox": os.path.join(QUEUE_DIR, "zhuguxia", "outbox"),
        "processed": os.path.join(QUEUE_DIR, "zhuguxia", "processed"),
        "profile": os.path.join(TRAINING_DIR, "zhuguxia", "profile.json"),
        "wrong_book": os.path.join(TRAINING_DIR, "zhuguxia", "wrong_book.json"),
        "problem_history": os.path.join(TRAINING_DIR, "zhuguxia", "problem_history"),
    },
    "qoder": {
        "name": "qoder",
        "type": "实战型",
        "inbox": os.path.join(QUEUE_DIR, "qoder", "inbox"),
        "outbox": os.path.join(QUEUE_DIR, "qoder", "outbox"),
        "processed": os.path.join(QUEUE_DIR, "qoder", "processed"),
        "profile": os.path.join(TRAINING_DIR, "qoder", "profile.json"),
        "wrong_book": os.path.join(TRAINING_DIR, "qoder", "wrong_book.json"),
        "problem_history": os.path.join(TRAINING_DIR, "qoder", "problem_history"),
    },
}

# === V6.0 深夜特训时间表 ===
NOCTURNAL_SCHEDULE = {
    "00:00-01:30": {
        "name": "极限死活",
        "tasks": [
            {"category": "死活", "difficulty": "高级", "count_steady": 100, "count_fast": 120, "count_qoder": 80},
        ],
        "intensity": "🔥🔥🔥🔥🔥",
        "penalty": "错1题加练10题",
    },
    "01:30-02:30": {
        "name": "AI定式库导入",
        "tasks": [
            {"category": "定式", "difficulty": "高级", "count_steady": 20, "count_fast": 25, "count_qoder": 15},
        ],
        "intensity": "📚📚",
        "focus": "Star Point, 3-3 invasion",
    },
    "02:30-04:30": {
        "name": "19路盘深夜实战",
        "tasks": [
            {"category": "对局", "difficulty": "实战", "count_steady": 2, "count_fast": 2, "count_qoder": 2},
        ],
        "intensity": "♟️♟️♟️♟️",
        "rule": "连续2盘，输棋方加赛",
    },
    "04:30-05:30": {
        "name": "AI深度复盘",
        "tasks": [
            {"category": "复盘", "difficulty": "深度", "count_steady": 1, "count_fast": 1, "count_qoder": 1},
        ],
        "intensity": "🤖🤖🤖",
        "focus": "找出恶手，理解AI胜率波动",
    },
    "05:30-06:00": {
        "name": "归档&错题重练",
        "tasks": [
            {"category": "错题", "difficulty": "综合", "count_steady": 50, "count_fast": 60, "count_qoder": 40},
        ],
        "intensity": "📂",
        "focus": "存入错题本，准备迎接日出",
    },
}

def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def load_profile(player_key):
    """加载学员档案"""
    profile_file = PLAYERS[player_key]["profile"]
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def create_training_task(time_slot, player_key):
    """创建训练任务"""
    slot_info = NOCTURNAL_SCHEDULE[time_slot]
    task_id = f"v6-{time_slot.replace(':', '')}-{player_key}-{datetime.now().strftime('%Y%m%d%H%M')}"
    
    task = {
        "id": task_id,
        "type": "nocturnal_training",
        "time_slot": time_slot,
        "slot_name": slot_info["name"],
        "intensity": slot_info["intensity"],
        "player": player_key,
        "tasks": [],
    }
    
    for task_def in slot_info["tasks"]:
        count = task_def.get(f"count_{player_key}", task_def.get("count_steady", 5))
        task["tasks"].append({
            "category": task_def["category"],
            "difficulty": task_def["difficulty"],
            "count": count,
        })
    
    return task

def send_to_inbox(player_key, task):
    """发送任务到收件箱"""
    inbox = PLAYERS[player_key]["inbox"]
    os.makedirs(inbox, exist_ok=True)
    
    task_file = os.path.join(inbox, f"{task['id']}.json")
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2, ensure_ascii=False)
    
    log(f"  📬 已发送至 {PLAYERS[player_key]['name']} inbox: {task['id']}")

def main():
    log(f"🐴 围棋教练调度器 V6.0 (深夜特训版) 启动")
    log(f"📂 题库: {PROBLEM_BANK}")
    log(f"📊 状态: {STATUS_FILE}")
    
    current_time = datetime.now().strftime("%H:%M")
    log(f"⏰ 当前时间: {current_time}")
    
    # 确定当前时段
    time_slot = None
    for slot_time in NOCTURNAL_SCHEDULE:
        start, end = slot_time.split("-")
        if start <= current_time < end:
            time_slot = slot_time
            break
    
    if not time_slot:
        log(f"⚠️ 当前时间 {current_time} 不在深夜特训时段内 (00:00-06:00)")
        log("💤 系统休眠中...")
        return
    
    slot_info = NOCTURNAL_SCHEDULE[time_slot]
    log(f"\n{'='*60}")
    log(f"🌙 深夜特训 - 时段: {time_slot} | {slot_info['name']}")
    log(f"🔥 强度: {slot_info['intensity']}")
    log(f"{'='*60}")
    
    # 为每个学员创建任务
    for player_key in PLAYERS:
        profile = load_profile(player_key)
        log(f"\n👤 {PLAYERS[player_key]['name']} ({PLAYERS[player_key]['type']}):")
        log(f"   等级: {profile.get('current_level', '未知')}")
        log(f"   解题: {profile.get('total_problems_solved', 0)}")
        
        task = create_training_task(time_slot, player_key)
        send_to_inbox(player_key, task)
    
    log(f"\n🏁 V6.0 深夜特训调度完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
