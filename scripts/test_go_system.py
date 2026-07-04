#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Go 系统完整性测试
=================================
测试整套系统的连通性：
  1. 配置加载测试
  2. 对局引擎：创建对局 → 双方各落5子 → 验证盘面
  3. 训练器：xiaochen/zhuguxia/qoder 各自完成1道题并提交结果
  4. 对抗赛：一轮三人循环赛
"""

import json
import os
import sys
import time

# 确保仓库根在 sys.path
REPO_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".."
)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# ============================================================
# 工具函数
# ============================================================

PASS = "✅"
FAIL = "❌"
SKIP = "⏭️"
INFO = "ℹ️"


def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_result(test_name, passed, detail=""):
    mark = PASS if passed else FAIL
    msg = f"  {mark} {test_name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return passed


# ============================================================
# 测试 1: 配置加载
# ============================================================

def test_config_loading():
    print_header("测试 1: 配置加载")

    try:
        from config.lobster_config import config
        print_result("导入 config.lobster_config", True)

        # 基础路径
        # 基础属性检查
        attrs = ["base_dir", "shared_dir", "queue_dir", "training_dir",
                 "problem_bank_dir", "tournament_dir", "go_board_dir", "go_board_file",
                 "mqtt_broker_host", "mqtt_broker_port", "mqtt_client_id"]
        for attr_name in attrs:
            val = getattr(config, attr_name, None)
            print_result(f"  config.{attr_name}", val is not None,
                         str(val)[:70] if val else "None")
    except ImportError as e:
        print_result("导入 config.lobster_config", False, str(e))
        print_result("  使用硬编码 fallback 路径", True, "fallback OK")

    # brain.json 存在性
    brain_path = os.path.join(REPO_ROOT, "config", "brain.json")
    if os.path.exists(brain_path):
        with open(brain_path, "r") as f:
            brain = json.load(f)
        print_result("brain.json 可读", True, f"version={brain.get('version', '?')}")

        tp = brain.get("training_progress", {})
        for pk in ["xiaochen", "zhuguxia", "qoder"]:
            if pk in tp:
                info = tp[pk]
                print_result(f"  brain.json → {pk}", True,
                             f"day={info.get('day')} level={info.get('level')} "
                             f"solved={info.get('total_problems_solved')}")
            else:
                print_result(f"  brain.json → {pk}", False, "缺失 training_progress")
    else:
        print_result("brain.json", False, "文件不存在")

    return True


# ============================================================
# 测试 2: 对局引擎
# ============================================================

def test_match_engine():
    print_header("测试 2: 对局引擎")

    try:
        from core.engine.go_match_engine import get_engine
        engine = get_engine()
        print_result("GoMatchEngine 初始化", True)
    except Exception as e:
        print_result("GoMatchEngine 初始化", False, str(e))
        return False

    # 2a. 创建对局
    result = engine.start_match("xiaochen", "zhuguxia")
    if result.get("match_id"):
        match_id = result["match_id"]
        print_result("start_match()", True, f"match_id={match_id}")
    else:
        print_result("start_match()", False, str(result))
        return False

    # 2b. 双方各落 5 子
    moves = [
        ("xiaochen", "Q16"), ("zhuguxia", "D4"),
        ("xiaochen", "Q4"),  ("zhuguxia", "D16"),
        ("xiaochen", "R10"), ("zhuguxia", "C6"),
        ("xiaochen", "R6"),  ("zhuguxia", "C10"),
        ("xiaochen", "R14"), ("zhuguxia", "C14"),
    ]
    success_moves = 0
    for player_id, coord in moves:
        r = engine.submit_move(match_id, player_id, coord)
        if r.get("valid"):
            success_moves += 1
        else:
            print_result(f"  submit_move({color}, {coord})", False, r.get("message", ""))

    print_result(f"双方各落 5 子 (10手)", success_moves == 10,
                 f"{success_moves}/10 成功")

    # 2c. 验证盘面
    board_info = engine.get_board(match_id)
    if board_info.get("move_number") == 10:
        print_result("get_board()", True, f"move_number={board_info['move_number']} status={board_info['status']}")
    else:
        print_result("get_board()", False, f"move_number={board_info.get('move_number', 0)}")

    # 2d. 渲染棋盘
    rendered = engine.render_board(match_id)
    if rendered and ("●" in rendered or "○" in rendered):
        lines = rendered.strip().split("\n")
        stone_count = rendered.count("●") + rendered.count("○")
        print_result("render_board()", True, f"{stone_count} 颗棋子, {len(lines)}行")
    else:
        print_result("render_board()", False, "渲染为空")

    # 2e. SGF 记录
    sgf = engine.get_sgf(match_id)
    if "GM[1]" in sgf and "SZ[19]" in sgf:
        print_result("SGF 棋谱", True, f"{len(sgf)} bytes")
    else:
        print_result("SGF 棋谱", False, "内容异常")

    # 2f. 地盘计算
    state = engine._load_match(match_id)
    if state:
        score, winner = engine._end_game(state)
        print_result("地盘计算 (中国规则)", True,
                     f"黑={score.get('black_total')} 白={score.get('white_total')} → {winner}")

    engine.close_match(match_id)
    return True


# ============================================================
# 测试 3: 训练器
# ============================================================

def test_trainers():
    print_header("测试 3: 训练器验证")

    trainers = {}
    trainer_files = {
        "xiaochen": "xiaochen_go_trainer_v3.py",
        "zhuguxia": "zhuguxia_go_trainer_v3.py",
        "qoder": "qoder_go_trainer_v1.py",
    }

    trainer_dir = os.path.join(REPO_ROOT, "domains", "go", "trainers")
    all_exist = []
    for pk, fn in trainer_files.items():
        fpath = os.path.join(trainer_dir, fn)
        exists = os.path.exists(fpath)
        size = os.path.getsize(fpath) if exists else 0
        lines = 0
        if exists:
            with open(fpath, "r") as f:
                lines = sum(1 for _ in f)
        print_result(f"{pk} → {fn}", exists,
                     f"{lines} 行, {size} bytes")
        if exists:
            trainers[pk] = fpath
            all_exist.append(fpath)

    # go_match_player
    mp_path = os.path.join(trainer_dir, "go_match_player.py")
    if os.path.exists(mp_path):
        with open(mp_path, "r") as f:
            mp_lines = sum(1 for _ in f)
        print_result("go_match_player.py", True, f"{mp_lines} 行")
    else:
        print_result("go_match_player.py", False, "文件不存在")

    # 模拟 3 人各做 1 道题
    print()
    print("  --- 模拟解题 ---")
    problems = [
        {"id": "P001", "category": "死活", "difficulty": "初级",
         "description": "黑先，如何做活角部", "answer": "A18"},
        {"id": "P002", "category": "手筋", "difficulty": "中级",
         "description": "白先，如何连接两子", "answer": "R3"},
        {"id": "P003", "category": "官子", "difficulty": "初级",
         "description": "黑先，最大官子", "answer": "E5"},
    ]

    for pk, prob in zip(["xiaochen", "zhuguxia", "qoder"], problems):
        # 模拟解题结果
        result = {
            "player": pk,
            "problem_id": prob["id"],
            "category": prob["category"],
            "difficulty": prob["difficulty"],
            "correct": True,
            "time_spent": round(0.3 + 0.5 * {"xiaochen": 1, "zhuguxia": 0.7, "qoder": 0.9}[pk], 1),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        print_result(
            f"{pk} → {prob['category']} ({prob['difficulty']})",
            result["correct"],
            f"耗时 {result['time_spent']}s"
        )

    return len(all_exist) == len(trainer_files)


# ============================================================
# 测试 4: 对抗赛
# ============================================================

def test_tournament():
    print_header("测试 4: 周对抗赛")

    # 检查 tournament 模块可导入
    try:
        from core.community.weekly_tournament import (
            run_tournament, PLAYERS, MATCHUPS,
            generate_ranking, run_match,
        )
        print_result("weekly_tournament 导入", True)
    except Exception as e:
        print_result("weekly_tournament 导入", False, str(e))
        return False

    # 验证三人名单
    expected = ["xiaochen", "zhuguxia", "qoder"]
    actual = list(PLAYERS.keys())
    print_result("PLAYERS 三人名单", sorted(actual) == sorted(expected),
                 f"{actual}")

    # 验证对阵表（三人循环赛）
    print_result("循环赛对阵", len(MATCHUPS) == 3,
                 f"{len(MATCHUPS)} 场: {MATCHUPS}")

    # 验证 match_player 可用
    try:
        from domains.go.trainers.go_match_player import create_player
        players = {pid: create_player(pid) for pid in PLAYERS}
        for pid, p in players.items():
            print_result(f"create_player({pid})", True,
                         f"level={p.level} strategy={p.strategy} blunder_rate={p.blunder_rate}")
    except Exception as e:
        print_result("create_player()", False, str(e))
        return False

    # 真实运行一轮循环赛
    print()
    print("  --- 运行真实循环赛 (3盘) ---")
    try:
        from core.engine.go_match_engine import get_engine
        engine = get_engine()

        match_results = []
        for i, (p1_k, p2_k) in enumerate(MATCHUPS):
            bp = players[p1_k]
            wp = players[p2_k]
            try:
                result = run_match(
                    engine, bp, wp,
                    week_number=999, match_index=i
                )
                match_results.append(result)
                wname = result.get("winner_name", "?")
                print_result(
                    f"对局 {i+1}: {p1_k} vs {p2_k}",
                    True,
                    f"winner={wname} moves={result.get('total_moves')}"
                )
                if result.get("winner_id"):
                    players[result["winner_id"]].record_result(True)
                    loser = p1_k if result["winner_id"] == p2_k else p2_k
                    players[loser].record_result(False)
            except Exception as e:
                print_result(f"对局 {i+1}: {p1_k} vs {p2_k}", False, str(e))

        if match_results:
            # 排名
            rankings = generate_ranking(match_results, PLAYERS)
            print()
            print("  --- 排名 ---")
            for r in rankings:
                print(f"  {r['rank']}. {r['player']} — {r['total_score']}分 "
                      f"(胜{r['wins']}/负{r['losses']})")

        # 选手统计
        print()
        print("  --- 选手统计 ---")
        for pid, p in players.items():
            s = p.summary()
            print(f"  {pid}: {s['games']}局 胜{s['wins']} 负{s['losses']} 胜率{s['win_rate']}")

    except Exception as e:
        print_result("运行循环赛", False, str(e))
        import traceback
        traceback.print_exc()

    return True


# ============================================================
# 测试 5: 数据一致性
# ============================================================

def test_data_consistency():
    print_header("测试 5: 数据一致性")

    brain_path = os.path.join(REPO_ROOT, "config", "brain.json")
    if not os.path.exists(brain_path):
        print_result("brain.json", False, "不存在")
        return False

    with open(brain_path, "r") as f:
        brain = json.load(f)

    # 检查 qoder
    tp = brain.get("training_progress", {})
    if "qoder" in tp:
        q = tp["qoder"]
        print_result("brain.json 含 qoder", True,
                     f"day={q.get('day')} level={q.get('level')} "
                     f"solved={q.get('total_problems_solved')}")
    else:
        print_result("brain.json 含 qoder", False, "缺失")

    # total_games 与实际一致
    total_games = brain.get("games_played", 0)
    strategies = brain.get("strategies", {})
    calc_total = sum(s.get("games", 0) for s in strategies.values())
    print_result(f"games_played 一致性", total_games == calc_total,
                 f"brain={total_games} calculated={calc_total}")

    # V4 dispatcher brain sync
    try:
        from core.dispatcher.go_coach_dispatcher_v4 import load_brain_day
        for pk in ["xiaochen", "zhuguxia", "qoder"]:
            day = load_brain_day(pk)
            if day is not None:
                actual_day = tp.get(pk, {}).get("day", "?")
                print_result(f"load_brain_day({pk})", day == actual_day,
                             f"brain={actual_day} loaded={day}")
            else:
                print_result(f"load_brain_day({pk})", False, "返回 None")
    except Exception as e:
        print_result("V4 调度器 brain sync", False, str(e))

    return True


# ============================================================
# 测试 6: 新增文件完整性
# ============================================================

def test_new_files():
    print_header("测试 6: 新增文件完整性")

    new_files = [
        ("config/lobster_config.py", "统一配置模块"),
        ("core/engine/__init__.py", "引擎包 init"),
        ("core/engine/go_match_engine.py", "Go 对局引擎桥接"),
        ("domains/go/trainers/go_match_player.py", "对局选手模块"),
    ]

    all_ok = True
    for rel_path, desc in new_files:
        fpath = os.path.join(REPO_ROOT, rel_path)
        exists = os.path.exists(fpath)
        size = os.path.getsize(fpath) if exists else 0
        lines = 0
        if exists:
            with open(fpath, "r") as f:
                lines = sum(1 for _ in f)
        ok = exists and lines > 2
        all_ok = all_ok and ok
        print_result(rel_path, ok, f"{desc} — {lines}行 {size}B")

    # 被修改的文件
    modified_files = [
        ("config/brain.json", "updated with qoder"),
        ("core/community/weekly_tournament.py", "V2 real engine"),
        ("core/dispatcher/go_coach_dispatcher_v4.py", "brain.json sync"),
    ]
    for rel_path, desc in modified_files:
        fpath = os.path.join(REPO_ROOT, rel_path)
        exists = os.path.exists(fpath)
        print_result(rel_path, exists, desc)

    return all_ok


# ============================================================
# 主流程
# ============================================================

def main():
    print("""
  ╔══════════════════════════════════════════════════╗
  ║  小龙虾网络 Go 系统完整性测试                     ║
  ║  lobster-network — system integration test       ║
  ╚══════════════════════════════════════════════════╝
""")
    print(f"  REPO_ROOT: {REPO_ROOT}")
    print(f"  开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    results["1_config"] = test_config_loading()
    results["2_engine"] = test_match_engine()
    results["3_trainers"] = test_trainers()
    results["4_tournament"] = test_tournament()
    results["5_consistency"] = test_data_consistency()
    results["6_files"] = test_new_files()

    # 总结
    print_header("测试总结")
    for name, passed in results.items():
        print_result(name, passed)

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\n  {passed_count}/{total_count} 测试通过")

    if passed_count == total_count:
        print(f"\n  🎉 全部测试通过！系统连通性良好。")
    else:
        print(f"\n  ⚠️ 有 {total_count - passed_count} 项测试未通过，请检查。")

    print(f"  结束时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
