#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
周对抗赛 V2 (Weekly Tournament V2)
==================================
改进：用真实对局引擎 (GoMatchEngine) 替换随机模拟。

变更：
- 不再用评分差+random模拟，改为调用 go_match_engine 进行真正的对局
- 每盘对局让两位学员的 go_match_player 交替落子
- 记录完整棋谱到 SGF 格式
- 对局超时保护（每方 10 分钟）
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime
from typing import List, Dict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.engine.go_match_engine import get_engine, GoMatchEngine
from domains.go.trainers.go_match_player import create_player, GoMatchPlayer

# ====== 配置 ======
try:
    from config.lobster_config import config
    QUEUE_DIR = config.queue_dir
    TOURNAMENT_DIR = config.tournament_dir
    TRAINING_DIR = config.training_dir
    LOG_FILE = os.path.join(TOURNAMENT_DIR, "tournament.log")
except ImportError:
    BASE = os.environ.get("LOBSTER_HOME", os.path.expanduser("~/.lobster-network"))
    QUEUE_DIR = os.path.join(BASE, "shared", "messages", "queue")
    TOURNAMENT_DIR = os.path.join(BASE, "shared", "training", "go", "tournament")
    TRAINING_DIR = os.path.join(BASE, "shared", "training", "go")
    LOG_FILE = os.path.join(TOURNAMENT_DIR, "tournament.log")

PLAYERS = {
    "xiaochen": {"name": "小陈", "type": "稳健型", "level": "中级"},
    "zhuguxia": {"name": "诸葛虾", "type": "加速型", "level": "高级"},
    "qoder": {"name": "qoder", "type": "实战型", "level": "中级"},
}

MATCHUPS = [
    ("xiaochen", "zhuguxia"),
    ("zhuguxia", "qoder"),
    ("qoder", "xiaochen"),
]

TIME_LIMIT_SECONDS = 600
MAX_MOVES = 200
MAX_PASSES = 3


def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def run_match(engine, black_player, white_player, week_number, match_index):
    black_id = black_player.player_id
    white_id = white_player.player_id
    black_name = PLAYERS[black_id]["name"]
    white_name = PLAYERS[white_id]["name"]

    match_id = f"week{week_number}_{black_id}_vs_{white_id}-{uuid.uuid4().hex[:8]}"

    engine.start_match(
        black_id=black_id, white_id=white_id,
        board_size=19, komi=7.5,
        time_limit_seconds=TIME_LIMIT_SECONDS,
        match_id=match_id,
    )
    log(f"\n  ⚔️ {black_name} (黑) vs {white_name} (白)")

    consecutive_passes = 0
    move_count = 0
    winner_id = None
    win_reason = "unknown"

    while move_count < MAX_MOVES:
        board_info = engine.get_board(match_id)
        if board_info.get("status") != "playing":
            break

        current_color = board_info["current_player"]
        cp = black_player if current_color == "black" else white_player
        move = cp.decide_move(match_id)

        if move.get("coord") == "resign":
            winner_id = white_id if cp.player_id == black_id else black_id
            win_reason = "对手认输"
            engine.resign(match_id, cp.player_id)
            log(f"     {cp.player_id} 认输!")
            break

        if move.get("coord") == "pass":
            consecutive_passes += 1
        else:
            consecutive_passes = 0

        r = engine.submit_move(match_id, cp.player_id, move["coord"])
        if not r.get("valid"):
            engine.submit_move(match_id, cp.player_id, "pass")
            consecutive_passes += 1

        move_count = r.get("move_number", move_count + 1)

        if r.get("game_over"):
            winner_id = r.get("winner")
            win_reason = "正常终局"
            if r.get("score"):
                s = r["score"]
                log(f"     比分: 黑 {s.get('black_total')} - {s.get('white_total')} 白")
            break

        if consecutive_passes >= MAX_PASSES:
            state = engine._load_match(match_id)
            if state and state.get("status") == "playing":
                score, winner_id = engine._end_game(state)
                state["status"] = "ended"
                engine._save_match(state)
                win_reason = "强制终局 (连续 pass)"
            break

    if winner_id is None:
        state = engine._load_match(match_id)
        if state and state.get("status") == "playing":
            score, winner_id = engine._end_game(state)
            win_reason = "手数上限终局"
            state["status"] = "ended"
            engine._save_match(state)

    sgf = engine.get_sgf(match_id)
    engine.close_match(match_id)

    winner_name = PLAYERS.get(winner_id, {}).get("name", str(winner_id)) if winner_id else "平局"

    log(f"     结果: {winner_name} 胜 ({win_reason}), {move_count}手")

    return {
        "match_id": match_id,
        "black_id": black_id, "black_name": black_name,
        "white_id": white_id, "white_name": white_name,
        "winner_id": winner_id, "winner_name": winner_name,
        "win_reason": win_reason, "total_moves": move_count,
        "sgf_saved": len(sgf) > 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def save_sgf_files(match_results):
    sgf_dir = os.path.join(TOURNAMENT_DIR, "sgf")
    os.makedirs(sgf_dir, exist_ok=True)
    engine = get_engine()
    for mr in match_results:
        sgf = engine.get_sgf(mr["match_id"])
        if sgf:
            path = os.path.join(sgf_dir, f"{mr['match_id']}.sgf")
            with open(path, "w") as f:
                f.write(sgf)
            mr["sgf_path"] = path


def generate_ranking(match_results, players_map):
    wins = {p: 0 for p in players_map}
    losses = {p: 0 for p in players_map}
    base_scores = {"xiaochen": 1200, "zhuguxia": 1350, "qoder": 1150}

    for mr in match_results:
        winner = mr["winner_id"]
        if winner and winner in wins:
            wins[winner] += 1
        loser = mr["black_id"] if mr["winner_id"] == mr["white_id"] else mr["white_id"]
        if loser in losses:
            losses[loser] += 1

    rankings = []
    for pid, info in players_map.items():
        total = base_scores.get(pid, 1000) + wins[pid] * 100 - losses[pid] * 50
        rankings.append({
            "player": info["name"], "type": info["type"],
            "key": pid, "base_score": base_scores.get(pid, 1000),
            "wins": wins[pid], "losses": losses[pid],
            "total_score": round(total, 1),
        })
    rankings.sort(key=lambda x: x["total_score"], reverse=True)
    for i, r in enumerate(rankings):
        r["rank"] = i + 1
    return rankings


def save_results(match_results, rankings, week_number):
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
    log(f"\n  📊 结果已保存: {output_file}")
    return output_file


def notify_players(match_results, rankings):
    for pk in PLAYERS:
        inbox = os.path.join(QUEUE_DIR, pk, "inbox")
        os.makedirs(inbox, exist_ok=True)
        player_matches = [m for m in match_results
                          if m["black_id"] == pk or m["white_id"] == pk]
        player_rank = next((r for r in rankings if r["key"] == pk), None)
        rank_text = f"第{player_rank['rank']}名" if player_rank else "未知"
        notification = {
            "id": f"tournament_notify_{pk}_{datetime.now().strftime('%Y%m%d%H%M')}",
            "type": "tournament_result",
            "message": f"本周对抗赛结果已公布，你排名{rank_text}",
            "matches": player_matches,
            "ranking": player_rank,
            "timestamp": datetime.now().isoformat(),
        }
        nf = os.path.join(inbox, f"tournament_{pk}_{datetime.now().strftime('%Y%m%d%H%M')}.json")
        with open(nf, "w", encoding="utf-8") as f:
            json.dump(notification, f, indent=2, ensure_ascii=False)
        log(f"  📬 已通知 {PLAYERS[pk]['name']}")


def run_tournament(week_number=None):
    if week_number is None:
        week_number = datetime.now().isocalendar()[1]

    log(f"\n{'='*60}")
    log(f"🏆 周对抗赛 V2 - 第{week_number}周 (真实对局引擎)")
    log(f"{'='*60}")

    engine = get_engine()
    players = {pid: create_player(pid) for pid in PLAYERS}

    match_results = []
    for i, (p1, p2) in enumerate(MATCHUPS):
        try:
            result = run_match(engine, players[p1], players[p2], week_number, i)
            match_results.append(result)
            winner_id = result["winner_id"]
            if winner_id:
                players[winner_id].record_result(True)
                loser = p1 if winner_id == p2 else p2
                players[loser].record_result(False)
        except Exception as e:
            log(f"  ❌ 对局异常: {e}")

    save_sgf_files(match_results)
    rankings = generate_ranking(match_results, PLAYERS)

    log(f"\n{'='*60}")
    log(f"📊 第{week_number}周排名榜")
    log(f"{'='*60}")
    for r in rankings:
        medal = ["", "🥇", "🥈", "🥉"][r["rank"]] if r["rank"] <= 3 else ""
        log(f"  {medal} 第{r['rank']}名: {r['player']} ({r['type']}) "
            f"— {r['total_score']}分 (胜{r['wins']}/负{r['losses']})")

    output_file = save_results(match_results, rankings, week_number)
    notify_players(match_results, rankings)

    log(f"\n🏁 第{week_number}周对抗赛完成")
    log(f"\n📈 选手统计:")
    for pid, player in players.items():
        s = player.summary()
        log(f"  {pid}: {s['games']}局 胜{s['wins']} 负{s['losses']} 胜率{s['win_rate']}")

    return output_file


if __name__ == "__main__":
    import sys
    week = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_tournament(week)
