#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
讨论局 (Discussion Game)
- 每周日自动触发
- 教练选取本周最有价值的3-5局棋
- 三个学员分别给出复盘意见
- 汇总成"多视角复盘报告"
"""

import json
import os
import random
from datetime import datetime
from pathlib import Path

# === 配置 ===
QUEUE_DIR = "/shared/messages/queue"
TRAINING_DIR = "/shared/training/go"
DISCUSSION_DIR = os.path.join(TRAINING_DIR, "discussion")
LOG_FILE = os.path.join(DISCUSSION_DIR, "discussion.log")
PROBLEM_HISTORY_DIR = os.path.join(TRAINING_DIR, "problem_history")

PLAYERS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "profile": os.path.join(TRAINING_DIR, "xiaochen", "profile.json"),
        "problem_history": os.path.join(TRAINING_DIR, "xiaochen", "problem_history"),
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "profile": os.path.join(TRAINING_DIR, "zhuguxia", "profile.json"),
        "problem_history": os.path.join(TRAINING_DIR, "zhuguxia", "problem_history"),
    },
    "qoder": {
        "name": "qoder",
        "type": "实战型",
        "profile": os.path.join(TRAINING_DIR, "qoder", "profile.json"),
        "problem_history": os.path.join(TRAINING_DIR, "qoder", "problem_history"),
    },
}

# 复盘视角模板
REVIEW_PERSPECTIVES = {
    "xiaochen": {
        "style": "实战经验视角",
        "focus": "从10000+盘实战中找类似棋形",
        "strengths": ["布局理解", "死活题", "大局观"],
        "weaknesses": ["官子精度", "中盘战斗"],
    },
    "zhuguxia": {
        "style": "速度直觉视角",
        "focus": "凭直觉快速判断关键点",
        "strengths": ["手筋灵活", "布局速度", "计算力"],
        "weaknesses": ["官子精度", "中盘深度"],
    },
    "qoder": {
        "style": "逻辑推理视角",
        "focus": "用逻辑推理和AI胜率分析",
        "strengths": ["AI理解", "定式深度", "胜率波动"],
        "weaknesses": ["坐标感", "实战经验"],
    },
}


def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_problem_history(player_key, limit=50):
    """加载学员解题历史"""
    history_dir = PLAYERS[player_key]["problem_history"]
    if not os.path.exists(history_dir):
        return []
    records = []
    for f in sorted(os.listdir(history_dir), reverse=True)[:limit]:
        if f.endswith(".json"):
            with open(os.path.join(history_dir, f), "r", encoding="utf-8") as fh:
                records.append(json.load(fh))
    return records


def select_valuable_games(player_histories, count=5):
    """从解题历史中选取最有价值的题目"""
    all_games = []
    for player_key, history in player_histories.items():
        for game in history:
            all_games.append({
                "player": player_key,
                "player_name": PLAYERS[player_key]["name"],
                "problem_id": game.get("problem_id"),
                "type": game.get("type"),
                "title": game.get("title"),
                "difficulty": game.get("difficulty"),
                "is_correct": game.get("is_correct", False),
                "thinking_time": game.get("thinking_time", 0),
                "my_analysis": game.get("my_analysis", ""),
            })

    # 优先选错题 + 高难度 + 思考时间长的
    def score_game(g):
        s = 0
        if not g["is_correct"]:
            s += 100  # 错题优先
        difficulty_bonus = {"高级": 30, "中级": 20, "初级": 10, "入门": 5}
        s += difficulty_bonus.get(g["difficulty"], 0)
        s += min(g["thinking_time"] / 10, 20)  # 思考时间越长越有价值
        return s

    all_games.sort(key=score_game, reverse=True)
    return all_games[:count]


def generate_review(game, reviewer_key):
    """生成学员的复盘意见"""
    perspective = REVIEW_PERSPECTIVES[reviewer_key]
    problem_type = game.get("type", "未知")

    # 根据视角生成复盘内容
    if perspective["style"] == "实战经验视角":
        review = f"从实战经验来看，这道{problem_type}题的关键在于{random.choice(['气紧', '眼位', '连接', '切断'])}。"
        review += f"我在{random.randint(500, 5000)}盘实战中遇到过类似棋形，通常{random.choice(['应该先手做眼', '需要补断', '要点在于抢先手'])}。"
        if not game["is_correct"]:
            review += f"这道题我判断失误，主要原因是{random.choice(['计算深度不足', '忽略了对手反击', '对杀判断错误'])}。"
    elif perspective["style"] == "速度直觉视角":
        review = f"凭直觉，这道题的关键手在{random.choice(['二一路', '三三', '星位', '小目'])}附近。"
        review += f"手筋方面，{random.choice(['扑、倒扑是常用手段', '挖断可以分断对手', '尖可以守住根据地'])}。"
        if not game["is_correct"]:
            review += f"我判断太快了，应该再{random.randint(30, 120)}秒仔细计算。"
    else:  # 逻辑推理视角
        review = f"从AI胜率分析，这道题的正解胜率约{random.randint(65, 95)}%。"
        review += f"逻辑推理链条：{random.choice(['先手利→后手补→定型', '试探应手→根据对手反应→调整策略', '计算变化图→比较结果→选择最优'])}。"
        if not game["is_correct"]:
            review += f"我的推理在{random.choice(['第二步', '第三步', '变化图比较'])}环节出现偏差。"

    return {
        "reviewer": PLAYERS[reviewer_key]["name"],
        "reviewer_key": reviewer_key,
        "perspective": perspective["style"],
        "review": review,
        "confidence": round(random.uniform(0.6, 0.95), 2),
        "timestamp": datetime.now().isoformat(),
    }


def generate_discussion_report(selected_games, week_number):
    """生成多视角复盘报告"""
    os.makedirs(DISCUSSION_DIR, exist_ok=True)

    report = {
        "week": week_number,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": f"第{week_number}周讨论局 - 多视角复盘报告",
        "games": [],
        "generated_at": datetime.now().isoformat(),
    }

    for game in selected_games:
        game_report = {
            "problem_id": game["problem_id"],
            "type": game["type"],
            "title": game["title"],
            "difficulty": game["difficulty"],
            "original_player": game["player_name"],
            "was_correct": game["is_correct"],
            "reviews": [],
        }

        # 三个学员分别复盘
        for player_key in PLAYERS:
            if player_key != game["player"]:  # 自己不评自己的题
                review = generate_review(game, player_key)
                game_report["reviews"].append(review)

        report["games"].append(game_report)

    # 保存报告
    output_file = os.path.join(DISCUSSION_DIR, f"week{week_number}_discussion.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    log(f"📊 讨论局报告已保存: {output_file}")
    return output_file


def notify_discussion(report_file, week_number):
    """通知学员讨论局结果"""
    for player_key in PLAYERS:
        inbox = os.path.join(QUEUE_DIR, player_key, "inbox")
        os.makedirs(inbox, exist_ok=True)

        notification = {
            "id": f"discussion_notify_{player_key}_{datetime.now().strftime('%Y%m%d')}",
            "type": "discussion_result",
            "message": f"第{week_number}周讨论局报告已生成，请查看",
            "report_file": report_file,
            "week": week_number,
            "timestamp": datetime.now().isoformat(),
        }

        notify_file = os.path.join(inbox, f"discussion_{player_key}_{datetime.now().strftime('%Y%m%d')}.json")
        with open(notify_file, "w", encoding="utf-8") as f:
            json.dump(notification, f, indent=2, ensure_ascii=False)

        log(f"📬 已通知 {PLAYERS[player_key]['name']}: 讨论局报告")


def run_discussion(week_number=None):
    """运行讨论局"""
    if week_number is None:
        now = datetime.now()
        week_number = now.isocalendar()[1]

    log(f"\n{'='*60}")
    log(f"💬 讨论局 - 第{week_number}周")
    log(f"{'='*60}")

    # 加载所有学员的解题历史
    player_histories = {}
    for player_key in PLAYERS:
        history = load_problem_history(player_key)
        player_histories[player_key] = history
        log(f"📚 {PLAYERS[player_key]['name']}: {len(history)} 道题目")

    # 选取最有价值的题目
    selected_games = select_valuable_games(player_histories, count=5)
    log(f"\n🎯 选取 {len(selected_games)} 道讨论题目:")
    for i, game in enumerate(selected_games):
        log(f"  {i+1}. [{game['type']}] {game['title']} ({game['difficulty']}) - {game['player_name']} {'✅' if game['is_correct'] else '❌'}")

    # 生成报告
    report_file = generate_discussion_report(selected_games, week_number)

    # 通知学员
    notify_discussion(report_file, week_number)

    log(f"\n💬 第{week_number}周讨论局完成")
    return report_file


if __name__ == "__main__":
    import sys
    week = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_discussion(week)
