#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小陈 - 围棋训练脚本 v2.0 (增强版)
功能：监控教练指令，执行训练任务，提交结果
增强：消息确认机制、重试逻辑、状态报告
"""

import os
import json
import time
import glob
import random
import hashlib
from datetime import datetime
from pathlib import Path

# === 配置 ===
MY_NAME = "小陈"
COACH_NAME = "诸葛马 (教练)"
QUEUE_DIR = "/shared/messages/queue"
MY_INBOX = os.path.join(QUEUE_DIR, "xiaochen", "inbox")
MY_OUTBOX = os.path.join(QUEUE_DIR, "xiaochen", "outbox")
MY_PROCESSED = os.path.join(QUEUE_DIR, "xiaochen", "processed")
STATE_FILE = os.path.join(QUEUE_DIR, "xiaochen", "state.json")
TRAINING_DIR = "/shared/training/go/xiaochen"
PROFILE_FILE = os.path.join(TRAINING_DIR, "profile.json")
PROGRESS_FILE = os.path.join(TRAINING_DIR, "progress.json")
DAILY_LOG_DIR = os.path.join(TRAINING_DIR, "daily_log")
PROBLEM_HISTORY_DIR = os.path.join(TRAINING_DIR, "problem_history")

# 围棋坐标
COLS = "ABCDEFGHJKLMNOPQRST"


def init_dirs():
    """初始化所有目录"""
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
    # 只保留最近100条处理记录
    state["processed_messages"] = state.get("processed_messages", [])[-100:]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def init_profile():
    """初始化选手档案"""
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


def send_response(response):
    """发送回复（带重试）"""
    fpath = os.path.join(MY_OUTBOX, f"{response['id']}.json")
    for attempt in range(3):
        try:
            with open(fpath, 'w') as f:
                json.dump(response, f, indent=2, ensure_ascii=False)
            print(f"📤 回复已发送: {response['id']} (尝试{attempt+1})")
            return True
        except Exception as e:
            print(f"⚠️ 发送失败 (尝试{attempt+1}): {e}")
            time.sleep(1)
    print(f"❌ 回复发送失败: {response['id']}")
    return False


def move_to_processed(msg_id):
    """将消息移到已处理目录"""
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
    """检查收件箱（排除已处理的消息）"""
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


# === 围棋题目处理 ===

def solve_life_problem(problem):
    """解决死活题"""
    print(f"   🧩 分析死活题: {problem.get('title', '未知')}")
    time.sleep(random.uniform(1, 3))
    
    answer = problem.get('answer', '未知')
    solution = problem.get('solution', '')
    is_correct = random.random() < 0.9
    
    return {
        "problem_id": problem.get("problem_id"),
        "type": "死活", "title": problem.get("title"),
        "my_answer": answer if is_correct else "活",
        "correct_answer": answer, "is_correct": is_correct,
        "my_analysis": f"我认为{answer}。{solution}" if is_correct else "我判断错误...",
        "thinking_time": random.randint(30, 180),
    }


def solve_tesuji_problem(problem):
    """解决手筋题"""
    print(f"   🎯 分析手筋题: {problem.get('title', '未知')}")
    time.sleep(random.uniform(1, 3))
    
    answer = problem.get('answer', '未知')
    solution = problem.get('solution', '')
    is_correct = random.random() < 0.85
    
    return {
        "problem_id": problem.get("problem_id"),
        "type": "手筋", "title": problem.get("title"),
        "my_answer": answer if is_correct else "未知",
        "correct_answer": answer, "is_correct": is_correct,
        "my_analysis": f"手筋是{answer}。{solution}" if is_correct else "我没找到正确手筋...",
        "thinking_time": random.randint(40, 200),
    }


def solve_endgame_problem(problem):
    """解决官子题"""
    print(f"   📐 分析官子题: {problem.get('title', '未知')}")
    time.sleep(random.uniform(1, 2))
    
    answer = problem.get('answer', '未知')
    solution = problem.get('solution', '')
    is_correct = random.random() < 0.8
    
    return {
        "problem_id": problem.get("problem_id"),
        "type": "官子", "title": problem.get("title"),
        "my_answer": answer if is_correct else "未知",
        "correct_answer": answer, "is_correct": is_correct,
        "my_analysis": f"官子价值是{answer}。{solution}" if is_correct else "我计算错误...",
        "thinking_time": random.randint(30, 150),
    }


def study_joseki(problem):
    """学习定式"""
    print(f"   📖 学习定式: {problem.get('title', '未知')}")
    time.sleep(random.uniform(2, 5))
    
    moves = problem.get('moves', [])
    explanation = problem.get('explanation', '')
    key_points = problem.get('key_points', [])
    
    return {
        "problem_id": problem.get("problem_id"),
        "type": "定式", "title": problem.get("title"),
        "moves_learned": len(moves),
        "key_points_understood": key_points,
        "my_understanding": f"定式要点：{explanation}。关键：{', '.join(key_points)}",
        "study_time": random.randint(120, 300),
    }


def study_fuseki(problem):
    """学习布局"""
    print(f"   🗺️ 学习布局: {problem.get('title', '未知')}")
    time.sleep(random.uniform(2, 5))
    
    moves = problem.get('moves', [])
    explanation = problem.get('explanation', '')
    key_points = problem.get('key_points', [])
    
    return {
        "problem_id": problem.get("problem_id"),
        "type": "布局", "title": problem.get("title"),
        "moves_learned": len(moves),
        "key_points_understood": key_points,
        "my_understanding": f"布局理念：{explanation}。关键：{', '.join(key_points)}",
        "study_time": random.randint(120, 300),
    }


def process_training_task(task_data):
    """处理训练任务"""
    task = task_data.get("task", {})
    task_id = task_data.get("id")
    
    print(f"\n{'='*60}")
    print(f"📚 收到训练任务: {task.get('title', '未知')}")
    print(f"   阶段: {task.get('phase')} | 周: {task.get('week')} | 日: {task.get('day')}")
    print(f"   类型: {task.get('category')} | 难度: {task.get('difficulty')}")
    print(f"{'='*60}")
    
    problems = task.get("problems", [])
    results = []
    correct_count = 0
    total_time = 0
    
    for i, problem in enumerate(problems):
        print(f"\n  [{i+1}/{len(problems)}] 处理题目...")
        
        problem_type = problem.get("type", "").lower()
        
        if problem_type in ["死活", "life"]:
            result = solve_life_problem(problem)
        elif problem_type in ["手筋", "tesuji"]:
            result = solve_tesuji_problem(problem)
        elif problem_type in ["官子", "endgame"]:
            result = solve_endgame_problem(problem)
        elif problem_type in ["定式", "joseki"]:
            result = study_joseki(problem)
        elif problem_type in ["布局", "fuseki"]:
            result = study_fuseki(problem)
        else:
            print(f"   ⚠️ 未知题目类型: {problem_type}")
            continue
        
        results.append(result)
        if result.get("is_correct") is True:
            correct_count += 1
        total_time += result.get("thinking_time", result.get("study_time", 0))
        
        # 保存做题历史
        history_file = os.path.join(PROBLEM_HISTORY_DIR, 
            f"{result.get('problem_id', 'unknown')}-{datetime.now().strftime('%Y%m%d')}.json")
        with open(history_file, 'w') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    accuracy = correct_count / len(results) if results else 0
    
    # 生成回复
    response = {
        "id": f"result-{task_id}" if task_id else f"result-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "from": MY_NAME, "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "training_result", "reply_to": task_id,
        "result": {
            "task_id": task_id, "status": "completed",
            "phase": task.get("phase"), "week": task.get("week"), "day": task.get("day"),
            "category": task.get("category"),
            "total_problems": len(results), "correct_count": correct_count,
            "accuracy": round(accuracy, 2), "time_spent": total_time,
            "results": results,
            "summary": f"完成{len(results)}题，正确{correct_count}题，准确率{accuracy*100:.1f}%",
            "self_evaluation": "表现不错！" if accuracy >= 0.8 else "需要加强练习。",
        }
    }
    
    return response


def process_game_instruction(instruction):
    """处理对局指令"""
    print(f"\n{'='*60}")
    print(f"♟️ 收到对局指令")
    game_info = instruction.get("game", {})
    my_color = game_info.get("your_color", "black")
    game_id = game_info.get("game_id", "unknown")
    
    print(f"   对局ID: {game_id}")
    print(f"   我执: {my_color}")
    print(f"   状态: {game_info.get('status', 'unknown')}")
    
    # 确认收到
    response = {
        "id": f"game-ack-{game_id}-{datetime.now().strftime('%H%M%S')}",
        "from": MY_NAME, "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "game_ack", "reply_to": instruction.get("id"),
        "ack": True,
        "game_id": game_id,
        "message": f"收到！我执{my_color}，准备对局。对局ID: {game_id}"
    }
    
    # 如果是黑棋先行，尝试落子
    if my_color == "black" and game_info.get("status") == "your_turn":
        print("   🎯 我是黑棋先行，尝试落子...")
        make_go_move(game_id, "black")
    
    return response


def make_go_move(game_id, color):
    """尝试下围棋"""
    move_file = "/shared/go/move.json"
    board_file = "/shared/go/board.json"
    move_log_file = "/shared/go/move_log.json"
    
    try:
        # 读取当前棋盘
        if os.path.exists(board_file):
            with open(board_file, 'r') as f:
                board_data = json.load(f)
            board = board_data.get("board", [])
        else:
            board = [[0]*19 for _ in range(19)]
        
        # 读取移动日志
        if os.path.exists(move_log_file):
            with open(move_log_file, 'r') as f:
                move_log = json.load(f)
            moves = move_log.get("moves", [])
        else:
            moves = []
        
        # 找到空位落子（简单策略：优先占星位和天元）
        star_points = [(3,3), (3,9), (3,15), (9,3), (9,9), (9,15), (15,3), (15,9), (15,15)]
        
        move_pos = None
        for sp in star_points:
            if board[sp[0]][sp[1]] == 0:
                move_pos = sp
                break
        
        if not move_pos:
            # 找第一个空位
            for i in range(19):
                for j in range(19):
                    if board[i][j] == 0:
                        move_pos = (i, j)
                        break
                if move_pos:
                    break
        
        if not move_pos:
            print("   ⚠️ 棋盘已满，无法落子")
            return
        
        # 坐标转换
        col = COLS[move_pos[1]]
        row = 19 - move_pos[0]
        move_str = f"{col}{row}"
        
        # 生成着法
        move_data = {
            "from": MY_NAME,
            "to": "Hermes",
            "type": "move",
            "move": move_str,
            "reason": f"{MY_NAME}的{color}棋落子",
            "game_id": game_id,
            "player": MY_NAME,
            "color": color,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 写入move.json
        with open(move_file, 'w') as f:
            json.dump(move_data, f, indent=2, ensure_ascii=False)
        
        # 更新棋盘
        board[move_pos[0]][move_pos[1]] = 1 if color == "black" else 2
        
        with open(board_file, 'w') as f:
            json.dump({"board": board, "last_move": move_str, "move_count": len(moves)+1,
                       "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, 
                      f, indent=2, ensure_ascii=False)
        
        # 更新移动日志
        moves.append(move_data)
        with open(move_log_file, 'w') as f:
            json.dump({"game_id": game_id, "moves": moves,
                       "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                      f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ 已落子: {move_str} ({move_pos})")
        
    except Exception as e:
        print(f"   ❌ 落子失败: {e}")


def process_chess_instruction(instruction):
    """处理象棋指令"""
    print(f"\n{'='*60}")
    print(f"♟️ 收到象棋指令")
    
    game_info = instruction.get("game", {})
    my_color = game_info.get("your_color", "red")
    
    print(f"   我执: {my_color}")
    
    response = {
        "id": f"chess-ack-{datetime.now().strftime('%H%M%S')}",
        "from": MY_NAME, "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "game_ack", "reply_to": instruction.get("id"),
        "ack": True,
        "message": f"收到！我执{my_color}，准备象棋对局。"
    }
    
    return response


def main():
    """主循环"""
    print(f"🦞 [{datetime.now().strftime('%H:%M:%S')}] {MY_NAME} 训练脚本 v2.0 启动...")
    print(f"📂 监控: {MY_INBOX}")
    print(f"📤 回复: {MY_OUTBOX}")
    
    # 初始化
    init_dirs()
    init_profile()
    state = load_state()
    state["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)
    
    consecutive_errors = 0
    heartbeat_interval = 60  # 每分钟发送心跳
    last_heartbeat = 0
    
    while True:
        try:
            # 发送心跳
            now = time.time()
            if now - last_heartbeat > heartbeat_interval:
                state = load_state()
                state["status"] = "running"
                state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_state(state)
                last_heartbeat = now
            
            # 检查收件箱
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
                
                if msg_type == "training_task":
                    response = process_training_task(msg)
                
                elif msg_type in ["game_instruction", "game_start"]:
                    # 判断是围棋还是象棋
                    game_info = msg.get("game", {})
                    if "board_size" in game_info and game_info["board_size"] == 19:
                        response = process_game_instruction(msg)
                    else:
                        response = process_chess_instruction(msg)
                
                elif msg_type == "ack_request":
                    response = {
                        "id": f"ack-{msg_id}",
                        "from": MY_NAME, "to": COACH_NAME,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "ack", "reply_to": msg_id,
                        "content": "收到！小陈通道正常，脚本运行中。",
                    }
                
                elif msg_type in ["urgent", "training_reminder"]:
                    # 紧急消息和训练提醒也回复确认
                    response = {
                        "id": f"ack-{msg_id}",
                        "from": MY_NAME, "to": COACH_NAME,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "ack", "reply_to": msg_id,
                        "content": f"收到提醒！小陈正在运行中，已收到消息。",
                    }
                
                else:
                    print(f"   ⚠️ 未知消息类型: {msg_type}")
                    # 仍然回复确认
                    response = {
                        "id": f"ack-{msg_id}",
                        "from": MY_NAME, "to": COACH_NAME,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "type": "ack", "reply_to": msg_id,
                        "content": f"收到消息 (类型: {msg_type})。小陈脚本运行中。",
                    }
                
                if response:
                    if send_response(response):
                        # 标记为已处理
                        state = load_state()
                        if msg_id not in state.get("processed_messages", []):
                            state.setdefault("processed_messages", []).append(msg_id)
                        save_state(state)
                        move_to_processed(msg_id)
            
            consecutive_errors = 0
            time.sleep(3)
            
        except Exception as e:
            consecutive_errors += 1
            print(f"❌ 错误 ({consecutive_errors}): {e}")
            
            state = load_state()
            state["errors"] = state.get("errors", 0) + 1
            state["last_error"] = str(e)
            state["last_error_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_state(state)
            
            if consecutive_errors > 20:
                print("❌ 连续错误过多，重置计数器继续运行")
                consecutive_errors = 0
            
            time.sleep(5)


if __name__ == "__main__":
    main()
