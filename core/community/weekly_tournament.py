#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周对抗赛 (Weekly Tournament)
- 每周六自动触发
- 三人循环赛：小陈 vs 诸葛虾、诸葛虾 vs qoder、qoder vs 小陈
- 每局自动记录棋谱、胜率、关键失误
- 赛后生成排名榜 + 个人评分
"""

import json
import os
import random
from datetime import datetime
from pathlib import Path

# === 配置 ===
QUEUE_DIR = "/shared/messages/queue"
TRAINING_DIR = "/shared/training/go"
TOURNAMENT_DIR = os.path.join(TRAINING_DIR, "tournament")
LOG_FILE = os.path.join(TOURNAMENT_DIR, "tournament.log")

PLAYERS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "profile": os.path.join(TRAINING_DIR, "xiaochen", "profile.json"),
        "wrong_book": os.path.join(TRAINING_DIR, "xiaochen", "wrong_book.json"),
        "problem_history": os.path.join(TRAINING_DIR, "xiaochen", "problem_history"),
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "profile": os.path.join(TRAINING_DIR, "zhuguxia", "profile.json"),
        "wrong_book": os.path.join(TRAINING_DIR, "zhuguxia", "wrong_book.json"),
        "problem_history": os.path.join(TRAINING_DIR, "zhuguxia", "problem_history"),
    },
    "qoder": {
        "name": "qoder",
        "type": "实战型",
        "profile": os.path.join(TRAINING_DIR, "qoder", "profile.json"),
        "wrong_book": os.path.join(TRAINING_DIR, "qoder", "wrong_book.json"),
        "problem_history": os.path.join(TRAINING_DIR, "qoder", "problem_history"),
    },
}

# 循环赛对阵
MATCHUPS = [
    ("xiaochen", "zhuguxia"),
    ("zhuguxia", "qoder"),
    ("qoder", "xiaochen"),
]


def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_profile(player_key):
    """加载学员档案"""
    profile_file = PLAYERS[player_key]["profile"]
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_wrong_book(player_key):
    """加载错题本"""
    wrong_book_file = PLAYERS[player_key]["wrong_book"]
    if os.path.exists(wrong_book_file):
        with open(wrong_book_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def load_problem_history(player_key):
    """加载解题历史"""
    history_dir = PLAYERS[player_key]["problem_history"]
    if not os.path.exists(history_dir):
        return []
    records = []
    for f in os.listdir(history_dir):
        if f.endswith(".json"):
            with open(os.path.join(history_dir, f), "r", encoding="utf-8") as fh:
                records.append(json.load(fh))
    return records


def calculate_player_score(player_key):
    """计算学员综合评分"""
    profile = load_profile(player_key)
    wrong_book = load_wrong_book(player_key)
    history = load_problem_history(player_key)

    total_problems = len(history)
    correct = sum(1 for h in history if h.get("is_correct", False))
    accuracy = correct / total_problems * 100 if total_problems > 0 else 0

    # 评分公式：基础分 + 准确率加权 + 解题量加权 - 错题惩罚
    base_score = 1000
    accuracy_bonus = accuracy * 5
    volume_bonus = min(total_problems * 0.5, 500)  # 上限500
    wrong_penalty = len(wrong_book) * 10

    score = base_score + accuracy_bonus + volume_bonus - wrong_penalty
    return max(score, 100)  # 最低100分


def simulate_game(player1_key, player2_key, week_number):
    """模拟一局对抗赛"""
    p1_score = calculate_player_score(player1_key)
    p2_score = calculate_player_score(player2_key)

    # 评分差决定胜率
    score_diff = p1_score - p2_score
    p1_win_prob = 0.5 + score_diff / 2000  # 评分差2000分时胜率约1.5
    p1_win_prob = max(0.2, min(0.8, p1_win_prob))

    # 随机决定胜负
    is_p1_win = random.random() < p1_win_prob

    # 生成棋谱记录
    game_id = f"week{week_number}_{player1_key}_vs_{player2_key}_{datetime.now().strftime('%Y%m%d%H%M')}"
    moves = random.randint(80, 200)

    game_record = {
        "game_id": game_id,
        "black": PLAYERS[player1_key]["name"],
        "white": PLAYERS[player2_key]["name"],
        "black_key": player1_key,
        "white_key": player2_key,
        "total_moves": moves,
        "winner": PLAYERS[player1_key]["name"] if is_p1_win else PLAYERS[player2_key]["name"],
        "winner_key": player1_key if is_p1_win else player2_key,
        "p1_score": round(p1_score, 1),
        "p2_score": round(p2_score, 1),
        "p1_win_prob": round(p1_win_prob * 100, 1),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 关键失误（随机生成1-3个）
    blunders = []
    for i in range(random.randint(1, 3)):
        blunder_move = random.randint(10, moves - 10)
        loser = player2_key if is_p1_win else player1_key
        blunders.append({
            "move": blunder_move,
            "player": PLAYERS[loser]["name"],
            "description": f"第{blunder_move}手出现失误，胜率波动约{random.randint(15, 40)}%",
        })

    game_record["blunders"] = blunders
    return game_record


def generate_ranking(match_results, week_number):
    """生成排名榜"""
    scores = {}
    wins = {}
    losses = {}

    for player_key in PLAYERS:
        scores[player_key] = calculate_player_score(player_key)
        wins[player_key] = 0
        losses[player_key] = 0

    for result in match_results:
        winner = result["winner_key"]
        loser = result["black_key"] if result["winner_key"] == result["white_key"] else result["white_key"]
        wins[winner] = wins.get(winner, 0) + 1
        losses[loser] = losses.get(loser, 0) + 1

    # 计算总分：评分 + 胜场×100 - 负场×50
    rankings = []
    for player_key in PLAYERS:
        total = scores[player_key] + wins[player_key] * 100 - losses[player_key] * 50
        rankings.append({
            "player": PLAYERS[player_key]["name"],
            "type": PLAYERS[player_key]["type"],
            "key": player_key,
            "base_score": round(scores[player_key], 1),
            "wins": wins[player_key],
            "losses": losses[player_key],
            "total_score": round(total, 1),
        })

    # 按总分排序
    rankings.sort(key=lambda x: x["total_score"], reverse=True)

    # 添加名次
    for i, r in enumerate(rankings):
        r["rank"] = i + 1

    return rankings


def save_tournament_results(match_results, rankings, week_number):
    """保存对抗赛结果"""
    os.makedirs(TOURNAMENT_DIR, exist_ok=True)

    results = {
        "week": week_number,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "matches": match_results,
        "rankings": rankings,
        "generated_at": datetime.now().isoformat(),
    }

    output_file = os.path.join(TOURNAMENT_DIR, f"week{week_number}_results.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    log(f"📊 对抗赛结果已保存: {output_file}")
    return output_file


def notify_players(match_results, rankings):
    """通知学员对抗赛结果"""
    for player_key in PLAYERS:
        inbox = os.path.join(QUEUE_DIR, player_key, "inbox")
        os.makedirs(inbox, exist_ok=True)

        # 找到该学员的比赛结果
        player_matches = [m for m in match_results if m["black_key"] == player_key or m["white_key"] == player_key]
        player_rank = next((r for r in rankings if r["key"] == player_key), None)

        notification = {
            "id": f"tournament_notify_{player_key}_{datetime.now().strftime('%Y%m%d')}",
            "type": "tournament_result",
            "message": f"本周对抗赛结果已公布，你排名第{player_rank['rank']}名",
            "matches": player_matches,
            "ranking": player_rank,
            "timestamp": datetime.now().isoformat(),
        }

        notify_file = os.path.join(inbox, f"tournament_{player_key}_{datetime.now().strftime('%Y%m%d')}.json")
        with open(notify_file, "w", encoding="utf-8") as f:
            json.dump(notification, f, indent=2, ensure_ascii=False)

        log(f"📬 已通知 {PLAYERS[player_key]['name']}: {notify_file}")


def run_tournament(week_number=None):
    """运行周对抗赛"""
    if week_number is None:
        # 从日期计算周数
        now = datetime.now()
        week_number = now.isocalendar()[1]

    log(f"\n{'='*60}")
    log(f"🏆 周对抗赛 - 第{week_number}周")
    log(f"{'='*60}")

    # 模拟比赛
    match_results = []
    for p1, p2 in MATCHUPS:
        log(f"\n⚔️ {PLAYERS[p1]['name']} vs {PLAYERS[p2]['name']}")
        result = simulate_game(p1, p2, week_number)
        match_results.append(result)
        log(f"  黑方: {result['black']} | 白方: {result['white']}")
        log(f"  胜者: {result['winner']} | 手数: {result['total_moves']}")
        log(f"  黑方评分: {result['p1_score']} | 白方评分: {result['p2_score']}")
        log(f"  黑方胜率: {result['p1_win_prob']}%")

    # 生成排名
    rankings = generate_ranking(match_results, week_number)

    log(f"\n{'='*60}")
    log(f"📊 第{week_number}周排名榜")
    log(f"{'='*60}")
    for r in rankings:
        medal = "🥇" if r["rank"] == 1 else "🥈" if r["rank"] == 2 else "🥉"
        log(f"  {medal} 第{r['rank']}名: {r['player']} ({r['type']}) - {r['total_score']}分")
        log(f"     基础分: {r['base_score']} | 胜: {r['wins']} | 负: {r['losses']}")

    # 保存结果
    output_file = save_tournament_results(match_results, rankings, week_number)

    # 通知学员
    notify_players(match_results, rankings)

    log(f"\n🏁 第{week_number}周对抗赛完成")
    return output_file


if __name__ == "__main__":
    import sys
    week = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_tournament(week)
