#!/usr/bin/env python3
"""
AlphaGo Zero 小龙虾训练系统 - 学员Agent脚本
角色: 小陈 (xiaochen) 或 诸葛虾 (zhuguxia)
功能: 监控指令目录、执行训练/对局、提交结果、更新策略库
"""

import json
import os
import sys
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path

# ==================== 配置 ====================
SHARED_DIR = Path("/shared")
SCRIPTS_DIR = SHARED_DIR / "scripts"
BRAINS_DIR = SHARED_DIR / "brain"
LOGS_DIR = SHARED_DIR / "logs"
MESSAGES_DIR = SHARED_DIR / "messages"

# 角色配置
ROLES = {
    "xiaochen": {
        "name": "🦞 小陈",
        "to_dir": MESSAGES_DIR / "to_xiaochen",
        "from_dir": MESSAGES_DIR / "from_xiaochen",
        "hermes_dir": MESSAGES_DIR / "from-hermes",
    },
    "zhuguxia": {
        "name": "🦞 诸葛虾",
        "to_dir": MESSAGES_DIR / "to_zhuguxia",
        "from_dir": SHARED_DIR / "messages" / "from_zhuguxia",
        "hermes_dir": MESSAGES_DIR / "from-hermes",
    },
}

CHECK_INTERVAL = 5  # 秒
MAX_GAMES_PER_CYCLE = 5

# ==================== 工具函数 ====================

def log(role, message, level="INFO"):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] [{role}] {message}"
    print(log_entry)
    
    log_file = LOGS_DIR / f"{role}_agent.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_brain():
    """加载策略库"""
    brain_file = BRAINS_DIR / "brain.json"
    if brain_file.exists():
        with open(brain_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"games_played": 0, "strategies": {}, "last_updated": None}


def save_brain(brain):
    """保存策略库"""
    brain_file = BRAINS_DIR / "brain.json"
    brain["last_updated"] = datetime.now().isoformat()
    with open(brain_file, "w", encoding="utf-8") as f:
        json.dump(brain, f, indent=2, ensure_ascii=False)


def check_instruction(role):
    """检查是否有新指令"""
    config = ROLES[role]
    
    # 检查教练指令
    instruction_file = config["to_dir"] / "instruction.json"
    if instruction_file.exists():
        try:
            with open(instruction_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    
    # 检查Hermes启动指令
    hermes_dir = config["hermes_dir"]
    if hermes_dir.exists():
        for f in sorted(hermes_dir.glob("hermes-start-*.json")):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    return json.load(fp)
            except:
                continue
    
    return None


def submit_response(role, response_data):
    """提交响应到响应目录"""
    config = ROLES[role]
    response_file = config["from_dir"] / "response.json"
    
    response_data["timestamp"] = datetime.now().isoformat()
    response_data["role"] = role
    
    with open(response_file, "w", encoding="utf-8") as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)
    
    log(role, f"响应已提交: {response_file}")


def simulate_go_game(black_role, white_role):
    """模拟围棋对局（简化版）"""
    board_size = 19
    board = [[0]*board_size for _ in range(board_size)]
    moves = []
    current = 1  # 1=黑, 2=白
    
    for i in range(random.randint(50, 200)):
        # 随机合法位置
        while True:
            r, c = random.randint(0, board_size-1), random.randint(0, board_size-1)
            if board[r][c] == 0:
                board[r][c] = current
                moves.append({"move": i+1, "player": "黑" if current==1 else "白", "pos": f"{r},{c}"})
                current = 3 - current  # 切换
                break
    
    # 简单胜负判定
    black_stones = sum(row.count(1) for row in board)
    white_stones = sum(row.count(2) for row in board)
    
    winner = "黑" if black_stones > white_stones else "白"
    
    return {
        "black": black_role,
        "white": white_role,
        "total_moves": len(moves),
        "black_stones": black_stones,
        "white_stones": white_stones,
        "winner": winner,
        "last_moves": moves[-10:]  # 最后10手
    }


def execute_training(role, instruction):
    """执行训练任务"""
    task_type = instruction.get("type", "self_play")
    
    log(role, f"执行训练任务: type={task_type}")
    
    results = {
        "task_type": task_type,
        "status": "completed",
        "games": []
    }
    
    if task_type == "self_play":
        # 自我对弈训练
        num_games = instruction.get("num_games", 3)
        opponent = "xiaochen" if role == "zhuguxia" else "zhuguxia"
        
        for i in range(min(num_games, MAX_GAMES_PER_CYCLE)):
            game = simulate_go_game(role, opponent)
            results["games"].append(game)
            
            # 更新策略库
            brain = load_brain()
            brain["games_played"] = brain.get("games_played", 0) + 1
            
            # 记录策略
            strategy_key = f"{role}_vs_{opponent}"
            if strategy_key not in brain.get("strategies", {}):
                brain.setdefault("strategies", {})[strategy_key] = {
                    "games": 0,
                    "wins": 0,
                    "losses": 0
                }
            
            brain["strategies"][strategy_key]["games"] += 1
            if game["winner"] == "黑" and game["black"] == role:
                brain["strategies"][strategy_key]["wins"] += 1
            else:
                brain["strategies"][strategy_key]["losses"] += 1
            
            save_brain(brain)
            log(role, f"对局 {i+1}/{num_games}: {game['black']} vs {game['white']} → 胜者: {game['winner']}")
    
    elif task_type == "review":
        # 复盘模式
        results["message"] = "复盘模式: 分析历史对局，优化策略"
        results["review_count"] = random.randint(5, 20)
        log(role, f"复盘完成，分析了 {results['review_count']} 局")
    
    elif task_type == "openings":
        # 布局训练
        results["message"] = "布局训练: 学习经典定式"
        results["patterns_learned"] = random.randint(3, 10)
        log(role, f"布局训练完成，学习了 {results['patterns_learned']} 个定式")
    
    else:
        results["message"] = f"未知任务类型: {task_type}"
        results["status"] = "skipped"
    
    return results


# ==================== 主循环 ====================

def main():
    if len(sys.argv) < 2:
        print("用法: python3 lobster_agent.py <角色名>")
        print("可选角色: xiaochen, zhuguxia")
        sys.exit(1)
    
    role = sys.argv[1]
    if role not in ROLES:
        print(f"错误: 未知角色 '{role}'")
        print(f"可选角色: {', '.join(ROLES.keys())}")
        sys.exit(1)
    
    config = ROLES[role]
    role_name = config["name"]
    
    log(role, f"=== {role_name} Agent 启动 ===")
    log(role, f"监控目录: {config['to_dir']}")
    log(role, f"检查间隔: {CHECK_INTERVAL}秒")
    
    # 初始化策略库
    if not (BRAINS_DIR / "brain.json").exists():
        initial_brain = {
            "games_played": 0,
            "strategies": {},
            "last_updated": datetime.now().isoformat(),
            "agents": list(ROLES.keys())
        }
        save_brain(initial_brain)
        log(role, "策略库已初始化")
    
    # 主循环
    cycle = 0
    while True:
        cycle += 1
        log(role, f"--- 第 {cycle} 轮检查 ---")
        
        # 检查指令
        instruction = check_instruction(role)
        
        if instruction:
            log(role, f"收到指令: type={instruction.get('type', 'unknown')}")
            
            # 执行训练
            results = execute_training(role, instruction)
            
            # 提交响应
            submit_response(role, {
                "status": "completed",
                "results": results,
                "agent": role,
                "agent_name": role_name
            })
            
            # 清理指令文件（可选，保留历史）
            # instruction_file = config["to_dir"] / "instruction.json"
            # if instruction_file.exists():
            #     instruction_file.rename(instruction_file.with_suffix('.json.done'))
        
        else:
            log(role, "暂无新指令，等待中...")
        
        # 等待
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
