#!/usr/bin/env python3
"""围棋正式落子处理器 - 19x19棋盘，中国规则"""

import json
import sys
import os
from datetime import datetime
from collections import deque

BOARD_FILE = '/shared/go/board.json'
MOVE_LOG = '/shared/go/move_log.json'
TIMER_FILE = '/shared/go/timer.json'
BROADCAST_DIR = '/shared/go/broadcasts'

os.makedirs(BROADCAST_DIR, exist_ok=True)

# 坐标映射（跳过I）
COL_MAP = {}
col_letters = 'ABCDEFGHJKLMNOPQRST'  # 跳过I
for i, c in enumerate(col_letters):
    COL_MAP[c] = i

ROW_MAP = {str(r): r-1 for r in range(1, 20)}

def parse_coord(coord):
    """解析坐标如 'Q4' -> (3, 16)"""
    coord = coord.upper().strip()
    if len(coord) < 2:
        return None
    
    # 找到第一个数字的位置
    num_start = 0
    for i, c in enumerate(coord):
        if c.isdigit():
            num_start = i
            break
    
    if num_start == 0:
        return None
    
    col_letter = coord[:num_start]
    row_str = coord[num_start:]
    
    col = COL_MAP.get(col_letter)
    row = ROW_MAP.get(row_str)
    
    if col is None or row is None:
        return None
    return (row, col)

def load_board():
    with open(BOARD_FILE, 'r') as f:
        return json.load(f)

def save_board(state):
    with open(BOARD_FILE, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_move_log():
    try:
        with open(MOVE_LOG, 'r') as f:
            return json.load(f)
    except:
        return []

def save_move_log(log):
    with open(MOVE_LOG, 'w') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def get_neighbors(row, col, size):
    """获取相邻位置"""
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < size and 0 <= nc < size:
            neighbors.append((nr, nc))
    return neighbors

def get_group(board, row, col, size):
    """获取同色棋子组及其气"""
    color = board[row][col]
    if color == 0:
        return [], set()
    
    group = []
    liberties = set()
    visited = set()
    queue = deque([(row, col)])
    
    while queue:
        r, c = queue.popleft()
        if (r, c) in visited:
            continue
        visited.add((r, c))
        group.append((r, c))
        
        for nr, nc in get_neighbors(r, c, size):
            if board[nr][nc] == 0:
                liberties.add((nr, nc))
            elif board[nr][nc] == color and (nr, nc) not in visited:
                queue.append((nr, nc))
    
    return group, liberties

def board_to_tuple(board, size):
    """将棋盘转为元组（用于哈希比较）"""
    return tuple(tuple(row) for row in board)

def validate_move(state, row, col, player):
    """验证落子是否合法"""
    board = state["board"]
    size = state["board_size"]
    current_player = state["current_player"]
    
    # 检查当前轮到谁
    if player != current_player:
        return False, f"当前轮到{'黑方' if current_player == 'black' else '白方'}落子"
    
    # 检查游戏状态
    if state["status"] != "playing":
        return False, "游戏已结束"
    
    # 检查位置是否为空
    if board[row][col] != 0:
        return False, "该位置已有棋子"
    
    # 检查打劫
    if state.get("ko_point") == (row, col):
        return False, "打劫点，不能立即回提"
    
    # 模拟落子
    new_board = [r[:] for r in board]
    new_board[row][col] = 1 if player == "black" else 2
    
    # 检查是否提走对方棋子
    opponent = 2 if player == "black" else 1
    captured_stones = []
    
    for nr, nc in get_neighbors(row, col, size):
        if new_board[nr][nc] == opponent:
            group, liberties = get_group(new_board, nr, nc, size)
            if len(liberties) == 0:
                captured_stones.extend(group)
    
    # 执行提子
    if captured_stones:
        for r, c in captured_stones:
            new_board[r][c] = 0
    
    # 检查自杀（落子后自身无气且没有提走对方）
    my_color = 1 if player == "black" else 2
    my_group, my_liberties = get_group(new_board, row, col, size)
    
    if len(my_liberties) == 0 and not captured_stones:
        return False, "禁着点（自杀）"
    
    # 检查全局同型（打劫）
    new_state_tuple = board_to_tuple(new_board, size)
    history = state.get("history", [])
    if history and new_state_tuple in history:
        return False, "全局同型（打劫）"
    
    return True, "合法", captured_stones, new_board

def execute_move(row, col, player, notation, captured_stones=None, new_board=None):
    """执行落子"""
    state = load_board()
    board = state["board"]
    size = state["board_size"]
    
    # 更新棋盘
    if new_board:
        state["board"] = new_board
    
    # 更新状态
    state["current_player"] = "white" if player == "black" else "black"
    state["move_number"] += 1
    state["pass_count"] = 0
    
    # 更新提子数
    if captured_stones:
        if player == "black":
            state["black_captures"] += len(captured_stones)
        else:
            state["white_captures"] += len(captured_stones)
    
    # 保存历史记录
    if "history" not in state:
        state["history"] = []
    state["history"].append(board_to_tuple(board, size))
    # 只保留最近20步
    state["history"] = state["history"][-20:]
    
    save_board(state)
    
    # 记录落子
    move_log = load_move_log()
    move_entry = {
        "number": state["move_number"],
        "player": player,
        "player_name": "小陈" if player == "black" else "诸葛虾",
        "coord": notation,
        "row": row,
        "col": col,
        "captured": len(captured_stones) if captured_stones else 0,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    move_log.append(move_entry)
    save_move_log(move_log)
    
    # 更新计时器
    try:
        timer = json.load(open(TIMER_FILE))
        timer["last_move_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timer["move_number"] = state["move_number"]
        timer["current_turn"] = state["current_player"]
        json.dump(timer, open(TIMER_FILE, 'w'), indent=2)
    except:
        pass
    
    return move_entry, captured_stones

def render_board(state):
    """渲染棋盘"""
    board = state["board"]
    size = state["board_size"]
    move_num = state["move_number"]
    current_player = state["current_player"]
    
    col_letters = 'ABCDEFGHJKLMNOPQRST'
    
    lines = []
    # 顶部列号
    header = "    " + " ".join(f"{c}" for c in col_letters[:size])
    lines.append(header)
    lines.append("  ┌" + "─" * (size * 2 + 1) + "┐")
    
    for row in range(size):
        row_str = f"{row+1:2d}│"
        for col in range(size):
            stone = board[row][col]
            if stone == 0:
                row_str += "・"
            elif stone == 1:
                row_str += "●"
            else:
                row_str += "○"
        row_str += "│"
        lines.append(row_str)
    
    lines.append("  └" + "─" * (size * 2 + 1) + "┘")
    
    turn_text = "⚫ 黑方（小陈）" if current_player == "black" else "⚪ 白方（诸葛虾）"
    lines.append(f"\n📢 第{move_num}手 · {turn_text}落子")
    
    if state["status"] == "ended":
        lines.append(f"\n🏁 游戏结束！")
    
    return "\n".join(lines)

def calculate_score(state):
    """计算领地（中国规则：子空皆地）"""
    board = state["board"]
    size = state["board_size"]
    
    black_stones = 0
    white_stones = 0
    black_territory = 0
    white_territory = 0
    
    visited = set()
    
    for row in range(size):
        for col in range(size):
            if board[row][col] == 1:
                black_stones += 1
            elif board[row][col] == 2:
                white_stones += 1
            elif board[row][col] == 0 and (row, col) not in visited:
                # BFS找空地区域
                region = []
                borders = set()
                queue = deque([(row, col)])
                
                while queue:
                    r, c = queue.popleft()
                    if (r, c) in visited:
                        continue
                    visited.add((r, c))
                    region.append((r, c))
                    
                    for nr, nc in get_neighbors(r, c, size):
                        if board[nr][nc] == 0 and (nr, nc) not in visited:
                            queue.append((nr, nc))
                        elif board[nr][nc] != 0:
                            borders.add(board[nr][nc])
                
                # 判断领地归属
                if len(borders) == 1:
                    if 1 in borders:
                        black_territory += len(region)
                    else:
                        white_territory += len(region)
    
    black_captures = state.get("black_captures", 0)
    white_captures = state.get("white_captures", 0)
    komi = state.get("komi", 7.5)
    
    # 中国规则：子空皆地
    black_total = black_stones + black_territory
    white_total = white_stones + white_territory + komi
    
    # 获胜线：黑方需超过185子（361/2 + 0.5 = 181，但中国规则是184.5）
    # 实际上中国规则黑方需185子获胜
    threshold = 185  # 黑方获胜线
    
    return {
        "black_stones": black_stones,
        "white_stones": white_stones,
        "black_territory": black_territory,
        "white_territory": white_territory,
        "black_captures": black_captures,
        "white_captures": white_captures,
        "komi": komi,
        "black_total": black_total,
        "white_total": white_total,
        "winner": "黑方（小陈）" if black_total > white_total else "白方（诸葛虾）"
    }

def main():
    if len(sys.argv) < 3:
        print("用法: process_go_move.py <coord> <player> [notation]")
        print("示例: process_go_move.py Q4 black 星位")
        sys.exit(1)
    
    coord_str = sys.argv[1]
    player = sys.argv[2]
    notation = sys.argv[3] if len(sys.argv) > 3 else coord_str
    
    # 处理pass
    if coord_str.lower() == "pass":
        state = load_board()
        state["pass_count"] = state.get("pass_count", 0) + 1
        
        if state["pass_count"] >= 2:
            state["status"] = "ended"
            score = calculate_score(state)
            result = {
                "valid": True,
                "message": "双方连续pass，游戏结束！",
                "score": score,
                "winner": score["winner"]
            }
        else:
            state["current_player"] = "white" if player == "black" else "black"
            state["move_number"] += 1
            result = {
                "valid": True,
                "message": f"{player} pass，轮到{'白方' if player == 'black' else '黑方'}"
            }
        
        save_board(state)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    
    pos = parse_coord(coord_str)
    
    if not pos:
        result = {"error": f"坐标格式错误: {coord_str}，如 Q4", "valid": False}
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)
    
    row, col = pos
    state = load_board()
    
    # 验证落子
    validation = validate_move(state, row, col, player)
    
    if not validation[0]:
        result = {"valid": False, "message": validation[1], "move_number": state["move_number"]}
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0)
    
    _, _, captured_stones, new_board = validation
    
    # 执行落子
    move_entry, captured = execute_move(row, col, player, notation, captured_stones, new_board)
    
    # 检查游戏是否结束（超过100手自动终局）
    state = load_board()
    if state["move_number"] >= 100:
        state["status"] = "ended"
        save_board(state)
        score = calculate_score(state)
        result = {
            "valid": True,
            "move": move_entry,
            "captured": len(captured) if captured else 0,
            "next_turn": state["current_player"],
            "move_number": state["move_number"],
            "game_ended": True,
            "score": score,
            "winner": score["winner"]
        }
    else:
        result = {
            "valid": True,
            "move": move_entry,
            "captured": len(captured) if captured else 0,
            "next_turn": state["current_player"],
            "move_number": state["move_number"]
        }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
