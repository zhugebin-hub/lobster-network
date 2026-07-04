#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋教练调度器 V4（自适应版）
V3 基础上增加：
1. 错题本复习机制（每3天自动插入错题重做）
2. 动态难度调整（连续2天准确率>90%升档，<70%降档复习）
3. 差异化调度（小陈侧重死活补强，诸葛虾侧重中级进阶）
4. 队列健康检查（自动清理过期消息）
"""

import os
import json
import time
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# === 配置 ===
COACH_NAME = "诸葛马 (教练)"
QUEUE_DIR = "/shared/messages/queue"
TRAINING_DIR = "/shared/training/go"
STATUS_FILE = os.path.join(TRAINING_DIR, "status.json")
PROBLEM_BANK = os.path.join(TRAINING_DIR, "problem_bank")
MATCHES_DIR = os.path.join(TRAINING_DIR, "matches")
LOG_FILE = os.path.join(TRAINING_DIR, "dispatcher.log")

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
}

# === V4 自适应训练计划 ===
# 基于当前进度（Day 3）继续，增加错题复习日和动态难度
# 2026-06-30 补充 Day 3-16 计划
DAILY_PLAN_V4 = {
    # Day 3: 扑与倒扑辨析（小陈推理力专项）
    3: {"topic": "扑与倒扑辨析", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "手筋", "difficulty": "初级", "count": 5}},
    
    # Day 4: 对抗赛准备 + 专项突破
    4: {"topic": "对抗赛准备 + 专项突破", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "match_day": True},
    
    # Day 5: 征子路线判断（推理力强化）
    5: {"topic": "征子路线判断", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "手筋", "difficulty": "中级", "count": 5}},
    
    # Day 6: 错题复习日（V4 新增）
    6: {"topic": "错题复习 + 手筋巩固", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 7: 第 1 周考核（综合）
    7: {"topic": "第 1 周考核", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "中级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 8: 休息 + 阶段总结
    8: {"topic": "休息 + 阶段总结", "tasks": [], "review_wrong_book": False},
    
    # Day 9: 第 2 周开始 - 死活专项
    9: {"topic": "初级死活强化", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "死活", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "死活", "difficulty": "初级", "count": 5}},
    
    # Day 10: 中级死活进阶
    10: {"topic": "中级死活进阶", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "死活", "difficulty": "中级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "zhuguxia_extra": {"category": "死活", "difficulty": "中级", "count": 5}},
    
    # Day 11: 错题复习日
    11: {"topic": "错题复习 + 死活实战", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 12: 手筋与死活综合
    12: {"topic": "手筋与死活综合", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "手筋", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ], "review_wrong_book": False},
    
    # Day 13: 定式入门
    13: {"topic": "定式入门", "tasks": [
        {"category": "定式", "difficulty": "入门", "count_steady": 5, "count_fast": 8},
        {"category": "定式", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False},
    
    # Day 14: 定式进阶
    14: {"topic": "定式进阶", "tasks": [
        {"category": "定式", "difficulty": "入门", "count_steady": 4, "count_fast": 6},
        {"category": "定式", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False},
    
    # Day 15: 第 2 周考核（综合）
    15: {"topic": "第 2 周考核", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "定式", "difficulty": "入门", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 16: 休息 + 阶段总结
    16: {"topic": "休息 + 阶段总结", "tasks": [], "review_wrong_book": False},
    
    # Day 17: 挖与分断（原计划）
    17: {"topic": "挖与分断", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False},
    
    # Day 18: 尖与跳的手筋 + 小陈错题补强
    18: {"topic": "尖与跳的手筋", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "死活", "difficulty": "初级", "count": 3}},
    
    # Day 19: 错题复习日（V4新增）
    19: {"topic": "错题复习+手筋进阶", "tasks": [
        {"category": "手筋", "difficulty": "中级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 20: 尖与跳进阶 + 死活专项
    20: {"topic": "尖跳进阶+死活专项", "tasks": [
        {"category": "手筋", "difficulty": "中级", "count_steady": 5, "count_fast": 8},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "死活", "difficulty": "初级", "count": 4}},
    
    # Day 21: 周考核（综合）
    21: {"topic": "第3周考核", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "中级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 22: 休息
    22: {"topic": "休息", "tasks": [], "review_wrong_book": False},
    
    # Day 23: 第4周开始 - 布局入门
    23: {"topic": "金角银边草肚皮", "tasks": [
        {"category": "布局", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "布局", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ], "review_wrong_book": False},
    
    # Day 24: 星位开局
    24: {"topic": "星位开局", "tasks": [
        {"category": "定式", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "布局", "difficulty": "初级", "count_steady": 2, "count_fast": 3},
    ], "review_wrong_book": False},
    
    # Day 25: 小目开局
    25: {"topic": "小目开局", "tasks": [
        {"category": "定式", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "定式", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ], "review_wrong_book": False},
    
    # Day 26: 错题复习日
    26: {"topic": "错题复习+布局实战", "tasks": [
        {"category": "布局", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 27: 简单官子
    27: {"topic": "简单官子", "tasks": [
        {"category": "官子", "difficulty": "入门", "count_steady": 5, "count_fast": 8},
        {"category": "官子", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False},
    
    # Day 28: 阶段考核
    28: {"topic": "第一阶段考核", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
        {"category": "布局", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
        {"category": "官子", "difficulty": "入门", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 29: 休息+阶段总结
    29: {"topic": "休息+阶段总结", "tasks": [], "review_wrong_book": False},
    
    # Day 30: 第二阶段开始 - 段位基础
    30: {"topic": "中盘战斗入门", "tasks": [
        {"category": "死活", "difficulty": "中级", "count_steady": 4, "count_fast": 6},
        {"category": "手筋", "difficulty": "中级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False},
    
    # Day 31: 对杀技巧
    31: {"topic": "对杀技巧", "tasks": [
        {"category": "死活", "difficulty": "中级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False},
    
    # Day 32: 错题复习
    32: {"topic": "错题复习+对杀实战", "tasks": [
        {"category": "死活", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 33: 攻守要点
    33: {"topic": "攻守要点", "tasks": [
        {"category": "手筋", "difficulty": "中级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False},
    
    # Day 34: 中级考核
    34: {"topic": "第2阶段考核", "tasks": [
        {"category": "死活", "difficulty": "中级", "count_steady": 6, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 6, "count_fast": 8},
        {"category": "手筋", "difficulty": "高级", "count_steady": 2, "count_fast": 4},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 35: 休息
    35: {"topic": "休息", "tasks": [], "review_wrong_book": False},
}


def log(msg):
    """写入日志"""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    except:
        pass


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
    except:
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


def load_wrong_book(player_key):
    wb_path = PLAYERS[player_key]["wrong_book"]
    if os.path.exists(wb_path):
        try:
            with open(wb_path, 'r') as f:
                return json.load(f)
        except:
            return []
    return []


def load_brain_day(player_key: str) -> int:
    """从 brain.json 读取指定学员的当前训练 day"""
    brain_paths = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "brain.json"),
        os.path.join(TRAINING_DIR, "brain.json"),
    ]
    for bp in brain_paths:
        if os.path.exists(bp):
            try:
                with open(bp, 'r') as f:
                    brain = json.load(f)
                tp = brain.get("training_progress", {}).get(player_key, {})
                day = tp.get("day")
                if day is not None:
                    return day
            except Exception:
                continue
    return None


def load_status():
    # 优先从 STATUS_FILE 读取
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass

    # fallback: 从 brain.json 读取最新 day（取各学员最大值）
    day_from_brain = None
    for pk in ["xiaochen", "zhuguxia", "qoder"]:
        d = load_brain_day(pk)
        if d is not None:
            day_from_brain = max(day_from_brain or 0, d)

    default_day = day_from_brain if day_from_brain else 17

    return {
        "phase": 1, "week": 3, "day": default_day,
        "topic": DAILY_PLAN_V4.get(default_day, {}).get("topic", "挖与分断"),
        "started_at": None, "completed_at": None,
        "players": {}, "game_result": {},
        "next_day_topic": DAILY_PLAN_V4.get(default_day + 1, {}).get("topic", "未知"),
        "v4_deployed": datetime.now().isoformat(),
        "brain_sync": True if day_from_brain else False,
    }


def save_status(status):
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)


def load_profile(player_key):
    p_path = PLAYERS[player_key]["profile"]
    if os.path.exists(p_path):
        try:
            with open(p_path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_profile(player_key, profile):
    with open(PLAYERS[player_key]["profile"], 'w') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)


def get_recent_accuracy(player_key, days=3):
    """获取最近N天的平均准确率"""
    history_dir = PLAYERS[player_key]["problem_history"]
    if not os.path.exists(history_dir):
        return None
    
    cutoff = datetime.now() - timedelta(days=days)
    correct = 0
    total = 0
    
    for fn in os.listdir(history_dir):
        if not fn.endswith('.json'):
            continue
        fpath = os.path.join(history_dir, fn)
        try:
            with open(fpath, 'r') as f:
                rec = json.load(f)
            # 从文件名提取日期
            parts = fn.replace('.json', '').split('-')
            if len(parts) >= 3:
                date_str = parts[-1]
                try:
                    rec_date = datetime.strptime(date_str, '%Y%m%d')
                    if rec_date >= cutoff:
                        total += 1
                        if rec.get("is_correct", False):
                            correct += 1
                except:
                    pass
        except:
            continue
    
    return correct / total if total > 0 else None


def clean_queue(player_key, max_age_hours=48):
    """清理过期队列消息"""
    inbox = PLAYERS[player_key]["inbox"]
    cleaned = 0
    if not os.path.exists(inbox):
        return 0
    
    cutoff = time.time() - (max_age_hours * 3600)
    for fn in os.listdir(inbox):
        if not fn.endswith('.json'):
            continue
        fpath = os.path.join(inbox, fn)
        try:
            if os.path.getmtime(fpath) < cutoff:
                # 读取消息判断是否已处理
                with open(fpath, 'r') as f:
                    msg = json.load(f)
                msg_id = msg.get("id", fn.replace('.json', ''))
                # 检查是否已在 processed 中
                processed_dir = PLAYERS[player_key]["processed"]
                processed_file = os.path.join(processed_dir, f"{msg_id}.json")
                if os.path.exists(processed_file):
                    os.remove(fpath)
                    cleaned += 1
                    log(f"  🧹 清理 {PLAYERS[player_key]['name']} 过期消息: {fn}")
        except:
            pass
    
    return cleaned


def send_to_inbox(player_key, message):
    player = PLAYERS[player_key]
    os.makedirs(player["inbox"], exist_ok=True)
    fpath = os.path.join(player["inbox"], f"{message['id']}.json")
    
    # 如果已存在同名文件，跳过（避免重复）
    if os.path.exists(fpath):
        log(f"  ⏭️ 跳过已存在的消息: {message['id']}")
        return False
    
    with open(fpath, 'w') as f:
        json.dump(message, f, indent=2, ensure_ascii=False)
    log(f"  📬 已发送至 {player['name']} inbox: {message['id']}")
    return True


def create_training_task(day_info, player_key, is_fast=False):
    player = PLAYERS[player_key]
    status = load_status()
    day = status["day"]
    task_id = f"go-train-v4-{datetime.now().strftime('%Y%m%d')}-{player_key[:3]}-{day:02d}"

    problems = []
    for task in day_info["tasks"]:
        count = task["count_fast"] if is_fast else task["count_steady"]
        selected = select_problems(task["category"], task["difficulty"], count)
        problems.extend(selected)

    # 小陈额外补强题
    if not is_fast and "xiaochen_extra" in day_info and player_key == "xiaochen":
        extra = day_info["xiaochen_extra"]
        extra_problems = select_problems(extra["category"], extra["difficulty"], extra["count"])
        problems.extend(extra_problems)
        log(f"  💪 {player['name']} 额外补强: {extra['category']}/{extra['difficulty']} ×{extra['count']}")

    # 错题复习
    if day_info.get("review_wrong_book"):
        wrong_book = load_wrong_book(player_key)
        review_count = day_info.get("review_count_fast" if is_fast else "review_count_steady", 4)
        if wrong_book:
            # 优先选择未掌握的错题
            unmastered = [w for w in wrong_book if not w.get("mastered", False)]
            if unmastered:
                review_problems = random.sample(unmastered, min(review_count, len(unmastered)))
                for wp in review_problems:
                    problems.append({
                        "problem_id": wp.get("problem_id", f"review-{wp.get('title','')}"),
                        "type": wp.get("type", "死活"),
                        "difficulty": wp.get("difficulty", "初级"),
                        "title": f"[复习]{wp.get('title','')}",
                        "question": wp.get("question", ""),
                        "answer": wp.get("correct_answer", ""),
                        "solution": wp.get("solution", ""),
                        "is_review": True,
                    })
                log(f"  🔄 {player['name']} 错题复习: {len(review_problems)}题")

    if not problems:
        log(f"  ⚠️ {player['name']} Day{day} 无可用题目")
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
            "day": day,
            "category": problems[0].get("type", "死活"),
            "difficulty": problems[0].get("difficulty", "入门"),
            "title": day_info["topic"],
            "description": f"第{status['week']}周 Day{day}训练 (V4自适应)",
            "problems": problems,
            "problem_count": len(problems),
            "time_limit": 70 if is_fast else 60,
            "min_accuracy": 0.8,
            "version": "V4",
        }
    }


def create_game_instruction(day, player_key, color):
    player = PLAYERS[player_key]
    status = load_status()
    game_id = f"go-game-v4-{datetime.now().strftime('%Y%m%d')}-{day:02d}"

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
                    log(f"  ✅ 收到 {player['name']} 训练结果: {result.get('result', {}).get('summary', '')}")
                elif result.get("type") == "review_result":
                    log(f"  📝 收到 {player['name']} 复盘报告")
                # 处理后移入 processed
                processed_dir = player["processed"]
                os.makedirs(processed_dir, exist_ok=True)
                msg_id = result.get("id", f.replace('.json', ''))
                dst = os.path.join(processed_dir, f)
                if not os.path.exists(dst):
                    shutil.move(fpath, dst)
            except Exception as e:
                log(f"  ⚠️ 处理结果失败 {f}: {e}")


def check_adaptive_adjustment(player_key):
    """检查是否需要动态调整难度"""
    profile = load_profile(player_key)
    recent_acc = get_recent_accuracy(player_key, days=3)
    
    if recent_acc is None:
        return None
    
    adjustments = []
    
    if recent_acc > 0.90:
        adjustments.append(f"📈 {profile.get('name', player_key)} 近3天平均准确率{recent_acc*100:.0f}%，建议提升难度")
    elif recent_acc < 0.70:
        adjustments.append(f"📉 {profile.get('name', player_key)} 近3天平均准确率{recent_acc*100:.0f}%，建议降档复习")
    
    return adjustments


def dispatch_day():
    """分发今日训练任务"""
    status = load_status()
    day = status.get("day", 17)
    
    if day not in DAILY_PLAN_V4:
        log(f"⚠️ Day {day} 不在计划中，使用默认训练内容")
        day_info = {"topic": f"Day {day} 训练", "tasks": [], "review_wrong_book": False}
    else:
        day_info = DAILY_PLAN_V4[day]
    
    status["day"] = day
    status["topic"] = day_info["topic"]
    status["version"] = "V4"
    
    log(f"\n{'='*60}")
    log(f"🐴 教练调度 V4 - Day {day}: {day_info['topic']}")
    log(f"{'='*60}")
    
    # 动态难度调整检查
    for pk in PLAYERS:
        adjustments = check_adaptive_adjustment(pk)
        if adjustments:
            for adj in adjustments:
                log(f"  {adj}")
    
    # 队列健康检查
    log("\n🧹 队列健康检查:")
    for pk in PLAYERS:
        cleaned = clean_queue(pk)
        log(f"  {PLAYERS[pk]['name']}: 清理 {cleaned} 条过期消息")
    
    # 处理待提交结果
    log("\n📥 处理学员提交结果:")
    process_results()
    
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
        
        # 对局指令（非休息日、非纯复习日）
        if not day_info.get("exam_day") and day % 7 != 0:
            game_id = f"go-game-v4-{datetime.now().strftime('%Y%m%d')}-{day:02d}"
            color_xc = "black" if day % 2 == 1 else "white"
            color_zgx = "white" if day % 2 == 1 else "black"
            
            send_to_inbox("xiaochen", create_game_instruction(day, "xiaochen", color_xc))
            send_to_inbox("zhuguxia", create_game_instruction(day, "zhuguxia", color_zgx))
            
            time.sleep(0.5)
            send_to_inbox("xiaochen", create_review_request(game_id, "xiaochen"))
            send_to_inbox("zhuguxia", create_review_request(game_id, "zhuguxia"))
    
    # 更新状态
    status["started_at"] = datetime.now().isoformat()
    status["next_day_topic"] = DAILY_PLAN_V4.get(day + 1, {}).get("topic", "未知")
    
    # 计算周次
    if day <= 7:
        status["week"] = 1
    elif day <= 14:
        status["week"] = 2
    elif day <= 22:
        status["week"] = 3
    elif day <= 29:
        status["week"] = 4
    else:
        status["week"] = (day - 1) // 7 + 1
    
    save_status(status)
    
    # 推进到下一天（修复：原代码未递增 day，导致每次 cron 重复处理同一天）
    next_day = day + 1
    if next_day in DAILY_PLAN_V4:
        status["day"] = next_day
        status["topic"] = DAILY_PLAN_V4[next_day]["topic"]
        status["started_at"] = datetime.now().isoformat()
        status["next_day_topic"] = DAILY_PLAN_V4.get(next_day + 1, {}).get("topic", "未知")
        
        # 重新计算周次
        if next_day <= 7:
            status["week"] = 1
        elif next_day <= 14:
            status["week"] = 2
        elif next_day <= 22:
            status["week"] = 3
        elif next_day <= 29:
            status["week"] = 4
        else:
            status["week"] = (next_day - 1) // 7 + 1
        
        save_status(status)
        log(f"📅 已推进到下一天: Day {next_day} - {status['topic']}")
    else:
        log(f"⚠️ Day {next_day} 不在计划中，保持当前 day={day}")
    
    log(f"\n📊 状态已更新: Phase {status['phase']}, Week {status['week']}, Day {day}")
    log(f"✅ 调度完成。下一天: Day {day + 1} - {status.get('next_day_topic', '未知')}")
    
    return day


def main():
    log(f"🐴 围棋教练调度器 V4 启动")
    log(f"📂 题库: {PROBLEM_BANK}")
    log(f"📊 状态: {STATUS_FILE}")
    
    # 显示学员状态摘要
    for pk, player in PLAYERS.items():
        profile = load_profile(pk)
        wrong_book = load_wrong_book(pk)
        recent_acc = get_recent_accuracy(pk, days=3)
        log(f"\n👤 {player['name']} ({player['type']}):")
        log(f"   总做题: {profile.get('total_problems_solved', 0)}")
        log(f"   错题本: {len(wrong_book)}题")
        log(f"   最后训练: {profile.get('last_training_date', '无')}")
        if recent_acc:
            log(f"   近3天准确率: {recent_acc*100:.1f}%")
    
    # 执行调度
    dispatch_day()
    
    log(f"\n🏁 V4 调度完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
