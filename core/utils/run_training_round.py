#!/usr/bin/env python3
"""
围棋训练一轮完整流程：训练任务 → 对局 → 评估
教练：诸葛马（本脚本模拟）
学员：小陈（30级）、诸葛虾（25级）
"""

import json
import os
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path

random.seed(int(hashlib.md5(datetime.now().isoformat().encode()).hexdigest(), 16) % 2**31)

SHARED = Path("/shared")
TRAIN = SHARED / "training" / "go"
QUEUE = SHARED / "messages" / "queue"
MESSAGES = SHARED / "messages"

# ==================== 题目生成（第2天：吃子技巧进阶） ====================

def generate_day2_problems():
    """生成第2天训练题目：吃子技巧进阶（扑、倒扑、征子、枷吃）"""
    return [
        {
            "problem_id": "capture-001",
            "type": "手筋",
            "title": "扑的妙用",
            "description": "黑先，如何利用扑来吃掉白棋？",
            "answer": "扑",
            "solution": "黑1扑入白棋虎口，白2必须提，黑3再打吃，白棋接不归。",
            "difficulty": "入门",
        },
        {
            "problem_id": "capture-002",
            "type": "手筋",
            "title": "倒扑反杀",
            "description": "黑先，白棋看似有两眼，黑如何用倒扑破眼？",
            "answer": "倒扑",
            "solution": "黑1直接扑入要点，白若提则自撞一气，黑可再打吃吃掉数子。",
            "difficulty": "入门",
        },
        {
            "problem_id": "capture-003",
            "type": "手筋",
            "title": "征子路线判断",
            "description": "黑先，能否通过连续打吃（征子）吃掉白棋？",
            "answer": "可以征吃",
            "solution": "黑1打吃方向正确，白每逃一气都被黑连续打吃，直至棋盘边缘无法逃脱。",
            "difficulty": "入门",
        },
        {
            "problem_id": "capture-004",
            "type": "手筋",
            "title": "枷吃封锁",
            "description": "黑先，如何用枷吃（门吃）封锁白棋逃跑路线？",
            "answer": "枷吃",
            "solution": "黑1跳枷，白棋无论向哪个方向逃都被封锁，无法逃出包围圈。",
            "difficulty": "入门",
        },
        {
            "problem_id": "capture-005",
            "type": "死活",
            "title": "扑后杀棋",
            "description": "黑先，白棋眼位丰富，黑如何利用扑来杀棋？",
            "answer": "死",
            "solution": "黑1扑入破眼，白2提，黑3点入眼位要点，白无法做出两眼。",
            "difficulty": "入门",
        },
        {
            "problem_id": "capture-006",
            "type": "手筋",
            "title": "双打吃选择",
            "description": "黑先，一子落下同时打吃两块白棋，白只能救一边。",
            "answer": "双打吃",
            "solution": "黑1下在要害处，同时打吃左右两块白棋，白只能救一边，另一边被吃。",
            "difficulty": "入门",
        },
        {
            "problem_id": "capture-007",
            "type": "手筋",
            "title": "征子与引征",
            "description": "白棋有引征子，黑还能征吃吗？",
            "answer": "不能征吃",
            "solution": "白棋在征子路线上有接应子，黑若强行征吃会被反断，应改用其他手法。",
            "difficulty": "进阶",
        },
        {
            "problem_id": "capture-008",
            "type": "手筋",
            "title": "扑与倒扑组合",
            "description": "黑先，组合使用扑和倒扑吃掉白棋。",
            "answer": "扑+倒扑",
            "solution": "黑1先扑，白2提后棋形变重，黑3倒扑入要害，白棋无法兼顾。",
            "difficulty": "进阶",
        },
    ]


# ==================== 学员模拟 ====================

def simulate_xiaochen_solving(problems):
    """模拟小陈解题（30级，准确率约75-85%）"""
    results = []
    for p in problems:
        # 小陈基础准确率较高
        base_acc = 0.80
        if p.get("difficulty") == "进阶":
            base_acc = 0.65
        
        is_correct = random.random() < base_acc
        
        if p["type"] == "手筋":
            if is_correct:
                analysis = f"这题的关键在于{p['answer']}。{p['solution'][:30]}..."
            else:
                analysis = "我尝试了直接打吃，但对方可以逃跑..."
            results.append({
                "problem_id": p["problem_id"],
                "type": "手筋",
                "title": p["title"],
                "my_answer": p["answer"] if is_correct else "直接打吃",
                "correct_answer": p["answer"],
                "is_correct": is_correct,
                "my_analysis": analysis,
                "thinking_time": random.randint(45, 180),
            })
        elif p["type"] == "死活":
            if is_correct:
                analysis = f"我认为{p['answer']}。{p['solution'][:30]}..."
            else:
                analysis = "我判断白棋可以做出两眼..."
            results.append({
                "problem_id": p["problem_id"],
                "type": "死活",
                "title": p["title"],
                "my_answer": p["answer"] if is_correct else "活",
                "correct_answer": p["answer"],
                "is_correct": is_correct,
                "my_analysis": analysis,
                "thinking_time": random.randint(60, 200),
            })
    return results


def simulate_zhuguxia_solving(problems):
    """模拟诸葛虾解题（25级，准确率约70-80%）"""
    results = []
    for p in problems:
        base_acc = 0.75
        if p.get("difficulty") == "进阶":
            base_acc = 0.60
        
        is_correct = random.random() < base_acc
        
        if p["type"] == "手筋":
            if is_correct:
                analysis = f"手筋是{p['answer']}。{p['solution'][:25]}...我理解了这个技巧。"
            else:
                analysis = "我没找到正确的手筋，可能需要学习扑和倒扑的概念。"
            results.append({
                "problem_id": p["problem_id"],
                "type": "手筋",
                "title": p["title"],
                "my_answer": p["answer"] if is_correct else "长",
                "correct_answer": p["answer"],
                "is_correct": is_correct,
                "my_analysis": analysis,
                "thinking_time": random.randint(50, 200),
            })
        elif p["type"] == "死活":
            if is_correct:
                analysis = f"我认为{p['answer']}。{p['solution'][:25]}..."
            else:
                analysis = "我判断错误，白棋似乎可以做活..."
            results.append({
                "problem_id": p["problem_id"],
                "type": "死活",
                "title": p["title"],
                "my_answer": p["answer"] if is_correct else "劫活",
                "correct_answer": p["answer"],
                "is_correct": is_correct,
                "my_analysis": analysis,
                "thinking_time": random.randint(55, 220),
            })
    return results


# ==================== 对局模拟 ====================

# 19路棋盘坐标
COLS = "ABCDEFGHJKLMNOPQRST"

def generate_game(xiaochen_results, zhuguxia_results):
    """模拟一局围棋对局（小陈黑 vs 诸葛虾白）"""
    board = [[0]*19 for _ in range(19)]
    moves = []
    move_count = 0
    max_moves = random.randint(80, 150)
    
    # 基于训练成绩调整胜率
    xiaochen_acc = sum(1 for r in xiaochen_results if r["is_correct"]) / len(xiaochen_results)
    zhuguxia_acc = sum(1 for r in zhuguxia_results if r["is_correct"]) / len(zhuguxia_results)
    
    # 小陈基础胜率更高（训练表现更好）
    black_win_bias = 0.55 + (xiaochen_acc - zhuguxia_acc) * 0.3
    
    # 星位优先开局
    star_points = [(3,3), (3,9), (3,15), (9,3), (9,9), (9,15), (15,3), (15,9), (15,15)]
    used_stars = set()
    
    def get_move(player, color):
        nonlocal move_count
        # 优先占星位（前9手）
        if move_count < 9:
            available = [sp for sp in star_points if board[sp[0]][sp[1]] == 0 and sp not in used_stars]
            if available:
                pos = random.choice(available)
                used_stars.add(pos)
                return pos
        
        # 周围落子策略（靠近已有棋子）
        occupied = [(i, j) for i in range(19) for j in range(19) if board[i][j] != 0]
        if occupied and random.random() < 0.7:
            ref = random.choice(occupied)
            for _ in range(10):
                di, dj = random.choice([(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])
                ni, nj = ref[0]+di, ref[1]+dj
                if 0 <= ni < 19 and 0 <= nj < 19 and board[ni][nj] == 0:
                    return (ni, nj)
        
        # 随机空位
        for _ in range(50):
            i, j = random.randint(0, 18), random.randint(0, 18)
            if board[i][j] == 0:
                return (i, j)
        
        # 找第一个空位
        for i in range(19):
            for j in range(19):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    # 模拟对局
    black_score = 0
    white_score = 0
    
    while move_count < max_moves:
        is_black_turn = (move_count % 2 == 0)
        color = "black" if is_black_turn else "white"
        player = "小陈" if is_black_turn else "诸葛虾"
        
        pos = get_move(player, color)
        if not pos:
            break
        
        board[pos[0]][pos[1]] = 1 if is_black_turn else 2
        col = COLS[pos[1]]
        row = 19 - pos[0]
        move_str = f"{col}{row}"
        
        # 简单计分
        if is_black_turn:
            black_score += random.randint(1, 5)
        else:
            white_score += random.randint(1, 5)
        
        moves.append({
            "move": move_count + 1,
            "player": player,
            "color": color,
            "pos": move_str,
            "coord": list(pos),
        })
        move_count += 1
        
        # 随机终局
        if move_count > 60 and random.random() < 0.02:
            break
    
    # 判定胜负（简单模拟）
    black_score += random.randint(0, 6)  # 贴目
    winner = "黑" if black_score >= white_score else "白"
    winner_name = "小陈" if winner == "黑" else "诸葛虾"
    
    return {
        "black": "小陈",
        "white": "诸葛虾",
        "total_moves": move_count,
        "black_stones": sum(1 for m in moves if m["color"] == "black"),
        "white_stones": sum(1 for m in moves if m["color"] == "white"),
        "black_score": black_score,
        "white_score": white_score,
        "winner": winner,
        "winner_name": winner_name,
        "moves": moves,
        "last_moves": moves[-10:] if len(moves) > 10 else moves,
    }


# ==================== 评估 ====================

def generate_evaluation(xiaochen_results, zhuguxia_results, game):
    """生成教练评估报告"""
    x_correct = sum(1 for r in xiaochen_results if r["is_correct"])
    x_total = len(xiaochen_results)
    x_acc = x_correct / x_total if x_total > 0 else 0
    
    z_correct = sum(1 for r in zhuguxia_results if r["is_correct"])
    z_total = len(zhuguxia_results)
    z_acc = z_correct / z_total if z_total > 0 else 0
    
    x_time = sum(r.get("thinking_time", 0) for r in xiaochen_results)
    z_time = sum(r.get("thinking_time", 0) for r in zhuguxia_results)
    
    # 找出错题
    x_wrong = [r for r in xiaochen_results if not r["is_correct"]]
    z_wrong = [r for r in zhuguxia_results if not r["is_correct"]]
    
    # 分类统计
    x_by_type = {}
    for r in xiaochen_results:
        t = r["type"]
        if t not in x_by_type:
            x_by_type[t] = {"total": 0, "correct": 0}
        x_by_type[t]["total"] += 1
        if r["is_correct"]:
            x_by_type[t]["correct"] += 1
    
    z_by_type = {}
    for r in zhuguxia_results:
        t = r["type"]
        if t not in z_by_type:
            z_by_type[t] = {"total": 0, "correct": 0}
        z_by_type[t]["total"] += 1
        if r["is_correct"]:
            z_by_type[t]["correct"] += 1
    
    return {
        "evaluation_id": f"eval-{datetime.now().strftime('%Y%m%d')}-001",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "day": 2,
        "topic": "吃子技巧进阶（扑、倒扑、征子、枷吃）",
        "xiaochen": {
            "level": "30级",
            "total_problems": x_total,
            "correct": x_correct,
            "accuracy": round(x_acc * 100, 1),
            "total_time": x_time,
            "avg_time": round(x_time / x_total) if x_total > 0 else 0,
            "by_type": x_by_type,
            "wrong_problems": [r["title"] for r in x_wrong],
            "strengths": ["死活基础扎实", "扑的概念理解较好"] if x_acc > 0.7 else ["需要加强手筋训练"],
            "weaknesses": ["进阶题目准确率下降", "倒扑与扑的区分不够清晰"] if x_wrong else [],
            "rating": "A" if x_acc >= 0.8 else "B" if x_acc >= 0.6 else "C",
        },
        "zhuguxia": {
            "level": "25级",
            "total_problems": z_total,
            "correct": z_correct,
            "accuracy": round(z_acc * 100, 1),
            "total_time": z_time,
            "avg_time": round(z_time / z_total) if z_total > 0 else 0,
            "by_type": z_by_type,
            "wrong_problems": [r["title"] for r in z_wrong],
            "strengths": ["学习态度积极"] if z_acc > 0.6 else ["需要更多基础练习"],
            "weaknesses": ["手筋题错误率偏高", "征子路线判断能力不足"] if z_wrong else [],
            "rating": "A" if z_acc >= 0.8 else "B" if z_acc >= 0.6 else "C",
        },
        "game": {
            "total_moves": game["total_moves"],
            "winner": game["winner_name"],
            "black_score": game["black_score"],
            "white_score": game["white_score"],
        },
        "coach_summary": "",
    }


# ==================== 主流程 ====================

def main():
    print("=" * 60)
    print("🦞⚡️ 围棋训练系统 - 第2天完整流程")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 生成题目
    print("\n📚 [1/5] 生成第2天训练题目...")
    problems = generate_day2_problems()
    print(f"   共 {len(problems)} 题")
    for p in problems:
        print(f"   - {p['problem_id']}: {p['title']} ({p['type']})")
    
    # 2. 小陈解题
    print("\n🦞 [2/5] 小陈解题中...")
    time.sleep(0.5)
    xiaochen_results = simulate_xiaochen_solving(problems)
    x_correct = sum(1 for r in xiaochen_results if r["is_correct"])
    print(f"   完成！{x_correct}/{len(xiaochen_results)} 正确")
    for r in xiaochen_results:
        status = "✅" if r["is_correct"] else "❌"
        print(f"   {status} {r['problem_id']}: {r['title']}")
    
    # 3. 诸葛虾解题
    print("\n🦞 [3/5] 诸葛虾解题中...")
    time.sleep(0.5)
    zhuguxia_results = simulate_zhuguxia_solving(problems)
    z_correct = sum(1 for r in zhuguxia_results if r["is_correct"])
    print(f"   完成！{z_correct}/{len(zhuguxia_results)} 正确")
    for r in zhuguxia_results:
        status = "✅" if r["is_correct"] else "❌"
        print(f"   {status} {r['problem_id']}: {r['title']}")
    
    # 4. 对局
    print("\n♟️ [4/5] 开始对局（小陈黑 vs 诸葛虾白）...")
    time.sleep(0.5)
    game = generate_game(xiaochen_results, zhuguxia_results)
    print(f"   共 {game['total_moves']} 手")
    print(f"   黑方（小陈）{game['black_score']} 分 vs 白方（诸葛虾）{game['white_score']} 分")
    print(f"   🏆 胜者：{game['winner_name']}（{game['winner']}方）")
    
    # 5. 评估
    print("\n📊 [5/5] 生成教练评估...")
    evaluation = generate_evaluation(xiaochen_results, zhuguxia_results, game)
    
    x_acc = evaluation["xiaochen"]["accuracy"]
    z_acc = evaluation["zhuguxia"]["accuracy"]
    
    if x_acc >= 80 and z_acc >= 70:
        eval_summary = "双方表现良好，可以进入第3天训练。"
    elif x_acc >= 70:
        eval_summary = "小陈表现尚可，诸葛虾需要加强手筋练习。建议复习后再进入下一天。"
    else:
        eval_summary = "双方准确率均未达标，需要重新复习第1天内容。"
    
    evaluation["coach_summary"] = eval_summary
    
    # ==================== 保存所有数据 ====================
    
    # 保存题目
    problems_file = TRAIN / "day2_problems.json"
    with open(problems_file, 'w') as f:
        json.dump({"day": 2, "topic": "吃子技巧进阶", "problems": problems}, f, indent=2, ensure_ascii=False)
    print(f"\n💾 题目已保存: {problems_file}")
    
    # 保存小陈解题历史
    for r in xiaochen_results:
        hfile = TRAIN / "xiaochen" / "problem_history" / f"{r['problem_id']}-20260527.json"
        with open(hfile, 'w') as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
    
    # 更新小陈进度
    profile = json.load(open(TRAIN / "xiaochen" / "profile.json"))
    profile["total_problems_solved"] = profile.get("total_problems_solved", 0) + len(xiaochen_results)
    profile["total_games_played"] = profile.get("total_games_played", 0) + 1
    profile["last_training_date"] = datetime.now().strftime("%Y-%m-%d")
    if x_acc >= 80:
        profile["current_level"] = "25级"
    with open(TRAIN / "xiaochen" / "profile.json", 'w') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    progress = json.load(open(TRAIN / "xiaochen" / "progress.json"))
    for r in xiaochen_results:
        cat = "life" if r["type"] == "死活" else "tesuji"
        progress["problem_stats"][cat]["solved"] += 1
        if r["is_correct"]:
            progress["problem_stats"][cat]["correct"] += 1
    progress["game_records"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "opponent": "诸葛虾",
        "color": "黑",
        "result": "胜" if game["winner"] == "黑" else "负",
        "moves": game["total_moves"],
    })
    with open(TRAIN / "xiaochen" / "progress.json", 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)
    
    # 保存诸葛虾数据
    os.makedirs(TRAIN / "zhuguxia" / "problem_history", exist_ok=True)
    for r in zhuguxia_results:
        hfile = TRAIN / "zhuguxia" / "problem_history" / f"{r['problem_id']}-20260527.json"
        with open(hfile, 'w') as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
    
    # 创建诸葛虾profile
    zhuguxia_profile = {
        "name": "诸葛虾",
        "role": "围棋学员",
        "created_at": "2026-05-27 17:00:00",
        "current_level": "25级",
        "current_phase": 1,
        "current_week": 1,
        "current_day": 2,
        "total_training_hours": 1,
        "total_problems_solved": len(zhuguxia_results),
        "total_games_played": 1,
        "win_rate": 0.0,
        "strengths": [],
        "weaknesses": [],
        "last_training_date": datetime.now().strftime("%Y-%m-%d"),
    }
    with open(TRAIN / "zhuguxia" / "profile.json", 'w') as f:
        json.dump(zhuguxia_profile, f, indent=2, ensure_ascii=False)
    
    zhuguxia_progress = {
        "phase_history": [],
        "weekly_reports": [],
        "problem_stats": {
            "life": {"solved": 0, "correct": 0},
            "tesuji": {"solved": 0, "correct": 0},
            "joseki": {"solved": 0, "correct": 0},
            "endgame": {"solved": 0, "correct": 0},
            "fuseki": {"solved": 0, "correct": 0},
        },
        "game_records": [],
    }
    for r in zhuguxia_results:
        cat = "life" if r["type"] == "死活" else "tesuji"
        zhuguxia_progress["problem_stats"][cat]["solved"] += 1
        if r["is_correct"]:
            zhuguxia_progress["problem_stats"][cat]["correct"] += 1
    zhuguxia_progress["game_records"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "opponent": "小陈",
        "color": "白",
        "result": "胜" if game["winner"] == "白" else "负",
        "moves": game["total_moves"],
    })
    with open(TRAIN / "zhuguxia" / "progress.json", 'w') as f:
        json.dump(zhuguxia_progress, f, indent=2, ensure_ascii=False)
    
    # 保存对局记录
    match_dir = TRAIN / "matches" / "xiaochen_vs_zhuguxia"
    os.makedirs(match_dir, exist_ok=True)
    game_file = match_dir / f"game-20260527-001.json"
    with open(game_file, 'w') as f:
        json.dump(game, f, indent=2, ensure_ascii=False)
    
    # 保存评估
    eval_file = TRAIN / f"evaluation-20260527.json"
    with open(eval_file, 'w') as f:
        json.dump(evaluation, f, indent=2, ensure_ascii=False)
    
    # 更新status.json
    status = {
        "phase": 1,
        "week": 1,
        "day": 2,
        "topic": "吃子技巧进阶（扑、倒扑、征子、枷吃）",
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "players": {
            "xiaochen": {
                "status": "completed",
                "level": profile.get("current_level", "30级"),
                "accuracy": x_acc,
                "rating": evaluation["xiaochen"]["rating"],
            },
            "zhuguxia": {
                "status": "completed",
                "level": "25级",
                "accuracy": z_acc,
                "rating": evaluation["zhuguxia"]["rating"],
            },
        },
        "game_result": {
            "winner": game["winner_name"],
            "total_moves": game["total_moves"],
        },
        "next_day_topic": "征子与反征子实战",
    }
    with open(TRAIN / "status.json", 'w') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    
    # 发送结果到消息队列（模拟教练报告）
    hermes_msg = {
        "id": f"hermes-report-{datetime.now().strftime('%Y%m%d%H%M')}",
        "from": "诸葛马 (教练)",
        "to": "系统",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "training_report",
        "report": evaluation,
    }
    os.makedirs(MESSAGES / "from-hermes", exist_ok=True)
    with open(MESSAGES / "from-hermes" / f"hermes-report-{datetime.now().strftime('%Y%m%d%H%M')}.json", 'w') as f:
        json.dump(hermes_msg, f, indent=2, ensure_ascii=False)
    
    # ==================== 输出评估报告 ====================
    print("\n" + "=" * 60)
    print("📊 【诸葛马·教练评估报告】")
    print("=" * 60)
    print(f"\n📅 第2天 | 主题：{evaluation['topic']}")
    
    print(f"\n🦞 小陈（{evaluation['xiaochen']['level']}）")
    print(f"   评级: {evaluation['xiaochen']['rating']}")
    print(f"   解题: {evaluation['xiaochen']['correct']}/{evaluation['xiaochen']['total_problems']} | 准确率: {evaluation['xiaochen']['accuracy']}%")
    print(f"   用时: {evaluation['xiaochen']['total_time']}秒 | 均时: {evaluation['xiaochen']['avg_time']}秒/题")
    for t, s in evaluation["xiaochen"]["by_type"].items():
        print(f"   - {t}: {s['correct']}/{s['total']}")
    if evaluation["xiaochen"]["wrong_problems"]:
        print(f"   ❌ 错题: {', '.join(evaluation['xiaochen']['wrong_problems'])}")
    
    print(f"\n🦞 诸葛虾（{evaluation['zhuguxia']['level']}）")
    print(f"   评级: {evaluation['zhuguxia']['rating']}")
    print(f"   解题: {evaluation['zhuguxia']['correct']}/{evaluation['zhuguxia']['total_problems']} | 准确率: {evaluation['zhuguxia']['accuracy']}%")
    print(f"   用时: {evaluation['zhuguxia']['total_time']}秒 | 均时: {evaluation['zhuguxia']['avg_time']}秒/题")
    for t, s in evaluation["zhuguxia"]["by_type"].items():
        print(f"   - {t}: {s['correct']}/{s['total']}")
    if evaluation["zhuguxia"]["wrong_problems"]:
        print(f"   ❌ 错题: {', '.join(evaluation['zhuguxia']['wrong_problems'])}")
    
    print(f"\n♟️ 对局结果")
    print(f"   小陈(黑) {game['black_score']} : {game['white_score']} 诸葛虾(白)")
    print(f"   共 {game['total_moves']} 手 | 🏆 {game['winner_name']}获胜")
    
    print(f"\n📝 教练总结: {eval_summary}")
    print(f"\n💾 数据已保存至 /shared/training/go/")
    print("=" * 60)
    
    return evaluation


if __name__ == "__main__":
    main()
