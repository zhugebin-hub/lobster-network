#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋对局引擎 (Go Match Engine)
=============================
封装 process_go_move.py 的完整 19x19 中国规则引擎为可直接调用的对局引擎。

路径策略：
- 不依赖 /shared/ 硬编码，所有持久化路径通过 LobsterConfig 统一管理
- 每局对局独立存储目录（match_storage/<match_id>/）

规则覆盖：
- 禁着点（自杀）
- 打劫检测（全局同型）
- BFS 找气 / 提子
- 中国规则领地计算（子空皆地 + 贴目 7.5）
- 超 100 手自动终局
- 双方连续 pass 终局
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime
from collections import deque
from pathlib import Path

# 将仓库根加入 sys.path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from config.lobster_config import config
except ImportError:
    # fallback: 直接用环境变量
    class _FallbackConfig:
        def __init__(self):
            self._base = os.environ.get("LOBSTER_HOME", os.path.join(str(Path.home()), ".lobster-network"))
        def engine_storage_dir(self):
            d = os.path.join(self._base, "shared", "training", "go", "engine")
            os.makedirs(d, exist_ok=True)
            return d
        def match_storage(self, mid):
            d = os.path.join(self.engine_storage_dir(), mid)
            os.makedirs(d, exist_ok=True)
            return d
        def match_board_file(self, mid): return os.path.join(self.match_storage(mid), "board.json")
        def match_move_log(self, mid): return os.path.join(self.match_storage(mid), "move_log.json")
        def match_timer_file(self, mid): return os.path.join(self.match_storage(mid), "timer.json")
        def match_sgf_file(self, mid): return os.path.join(self.match_storage(mid), "game.sgf")
        def match_meta_file(self, mid): return os.path.join(self.match_storage(mid), "meta.json")
    config = _FallbackConfig()


# ====== 棋盘常量 ======
COL_LETTERS = "ABCDEFGHJKLMNOPQRST"  # 跳过 I
COL_MAP = {c: i for i, c in enumerate(COL_LETTERS)}
ROW_MAP = {str(r): r - 1 for r in range(1, 20)}


def parse_coord(coord: str):
    """解析坐标如 'Q4' -> (row, col)，'pass' 返回 None"""
    coord = coord.upper().strip()
    if coord == "PASS" or coord == "":
        return None
    if len(coord) < 2:
        return None
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


def coord_to_notation(row: int, col: int) -> str:
    """将 (row, col) 转回坐标记法，如 (3, 16) -> 'Q4'"""
    return f"{COL_LETTERS[col]}{row + 1}"


def get_neighbors(row: int, col: int, size: int):
    """获取相邻四方向位置"""
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < size and 0 <= nc < size:
            neighbors.append((nr, nc))
    return neighbors


def get_group(board, row, col, size):
    """BFS 获取同色棋子组及其气"""
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
    """棋盘序列化为不可变 tuple，用于 hash 比较"""
    return tuple(tuple(row) for row in board)


class GoMatchEngine:
    """围棋对局引擎 — 支持创建、落子、查询、终局"""

    def __init__(self):
        self._matches = {}  # 内存缓存 match_id -> state

    # ==================== 对局管理 ====================

    def start_match(self, black_id: str, white_id: str,
                    board_size: int = 19,
                    komi: float = 7.5,
                    time_limit_seconds: int = 600,
                    match_id: str = None) -> dict:
        """
        创建一场新对局。

        参数:
            black_id: 黑方标识
            white_id: 白方标识
            board_size: 棋盘大小（默认 19）
            komi: 贴目（默认 7.5）
            time_limit_seconds: 每方用时（秒），默认 600（10 分钟）
            match_id: 可选，不传自动生成

        返回: {"match_id": ..., "board_state": ...}
        """
        if match_id is None:
            match_id = f"match-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"

        # 初始化棋盘
        board = [[0] * board_size for _ in range(board_size)]

        state = {
            "match_id": match_id,
            "black_id": black_id,
            "white_id": white_id,
            "board_size": board_size,
            "komi": komi,
            "board": board,
            "current_player": "black",
            "move_number": 0,
            "pass_count": 0,
            "black_captures": 0,
            "white_captures": 0,
            "status": "playing",
            "history": [],
            "ko_point": None,  # (row, col) or None
            "started_at": datetime.now().isoformat(),
            "time_limit_seconds": time_limit_seconds,
            "black_time_used": 0.0,   # 已用时间（秒）
            "white_time_used": 0.0,
            "last_move_time": None,
        }

        # 持久化
        self._save_match(state)
        self._matches[match_id] = state
        self._write_sgf_header(state)

        return {
            "match_id": match_id,
            "board_state": self._board_summary(state),
            "black_id": black_id,
            "white_id": white_id,
        }

    def submit_move(self, match_id: str, player_id: str, coord: str) -> dict:
        """
        提交一手落子。

        参数:
            match_id: 对局 ID
            player_id: 落子方标识
            coord: 坐标记法（如 'Q4'）或 'pass' 表示虚手

        返回: {
            "valid": bool,
            "message": str,
            "board_state": {...},
            "captured": int,
            "game_over": bool,
            "score": {...} | None,
            "winner": str | None,
        }
        """
        state = self._load_match(match_id)
        if state is None:
            return {"valid": False, "message": f"对局不存在: {match_id}"}

        if state["status"] != "playing":
            return {"valid": False, "message": "对局已结束", "game_over": True}

        # 确认是当前轮到的玩家
        expected = state["black_id"] if state["current_player"] == "black" else state["white_id"]
        if player_id != expected:
            return {"valid": False, "message": f"当前轮到 {expected} 落子"}

        # 处理 pass
        if coord.upper().strip() == "PASS" or coord.strip() == "":
            return self._handle_pass(state)

        pos = parse_coord(coord)
        if pos is None:
            return {"valid": False, "message": f"坐标格式错误: {coord}，示例: Q4"}

        row, col = pos
        board = state["board"]
        size = state["board_size"]
        player = state["current_player"]

        # 验证
        if board[row][col] != 0:
            return {"valid": False, "message": "该位置已有棋子"}

        if state.get("ko_point") == (row, col):
            return {"valid": False, "message": "打劫点，不能立即回提"}

        # 模拟落子
        color = 1 if player == "black" else 2
        new_board = [r[:] for r in board]
        new_board[row][col] = color

        # 检查提子
        opponent_color = 2 if player == "black" else 1
        captured_stones = []
        for nr, nc in get_neighbors(row, col, size):
            if new_board[nr][nc] == opponent_color:
                group, liberties = get_group(new_board, nr, nc, size)
                if len(liberties) == 0:
                    captured_stones.extend(group)

        if captured_stones:
            for r, c in captured_stones:
                new_board[r][c] = 0

        # 自杀检测
        my_group, my_liberties = get_group(new_board, row, col, size)
        if len(my_liberties) == 0 and not captured_stones:
            return {"valid": False, "message": "禁着点（自杀）"}

        # 全局同型检测
        new_state_tuple = board_to_tuple(new_board, size)
        history = state.get("history", [])
        if history and new_state_tuple in history:
            return {"valid": False, "message": "全局同型违反（打劫）"}

        # 通过验证，执行落子
        state["board"] = new_board
        state["current_player"] = "white" if player == "black" else "black"
        state["move_number"] += 1
        state["pass_count"] = 0

        if player == "black":
            state["black_captures"] += len(captured_stones)
        else:
            state["white_captures"] += len(captured_stones)

        # 更新打劫点
        state["ko_point"] = None
        if len(captured_stones) == 1:
            # 单子提，设置打劫点
            cr, cc = captured_stones[0]
            # 打劫点就是刚才提走的那颗子原来的位置
            if self._is_ko_candidate(state, cr, cc, player):
                state["ko_point"] = (cr, cc)

        # 更新历史（最近 20 步）
        state["history"].append(board_to_tuple(board, size))
        state["history"] = state["history"][-20:]

        # 时间更新（简化：不严格计时，记录间隔）
        now = datetime.now()
        if state.get("last_move_time"):
            elapsed = (now - state["last_move_time"]).total_seconds()
            if player == "black":
                state["black_time_used"] += elapsed
            else:
                state["white_time_used"] += elapsed
        state["last_move_time"] = now

        notation = coord.upper()
        move_entry = {
            "number": state["move_number"],
            "player": player,
            "player_id": player_id,
            "coord": notation,
            "row": row,
            "col": col,
            "captured": len(captured_stones),
            "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 写入 SGF
        self._append_sgf_move(state, notation)

        # 检查终局
        game_over = False
        score = None
        winner = None
        if state["move_number"] >= 100:
            game_over = True
        if game_over:
            state["status"] = "ended"
            score, winner = self._end_game(state)

        self._save_match(state)

        return {
            "valid": True,
            "message": f"{player} 落子 {notation}，第 {state['move_number']} 手",
            "board_state": self._board_summary(state),
            "captured": len(captured_stones),
            "move_number": state["move_number"],
            "next_player": state["current_player"]
                if state["current_player"] == "white" else state["current_player"],
            "game_over": game_over,
            "score": score,
            "winner": winner,
        }

    def get_board(self, match_id: str) -> dict:
        """获取当前盘面"""
        state = self._load_match(match_id)
        if state is None:
            return {"error": f"对局不存在: {match_id}"}
        return self._board_summary(state)

    def resign(self, match_id: str, player_id: str) -> dict:
        """一方认输"""
        state = self._load_match(match_id)
        if state is None:
            return {"valid": False, "message": f"对局不存在: {match_id}"}
        if state["status"] != "playing":
            return {"valid": False, "message": "对局已结束"}

        winner = state["white_id"] if player_id == state["black_id"] else state["black_id"]
        state["status"] = "ended"
        state["winner"] = winner
        state["ended_by"] = "resign"
        state["ended_at"] = datetime.now().isoformat()

        self._save_match(state)
        return {
            "valid": True,
            "message": f"{player_id} 认输",
            "winner": winner,
            "game_over": True,
        }

    def _handle_pass(self, state):
        player = state["current_player"]
        player_id = state["black_id"] if player == "black" else state["white_id"]
        state["pass_count"] += 1
        state["move_number"] += 1

        now = datetime.now()
        notation = "pass"
        self._append_sgf_move(state, notation)

        if state["pass_count"] >= 2:
            state["status"] = "ended"
            score, winner = self._end_game(state)
            self._save_match(state)
            return {
                "valid": True,
                "message": "双方连续 pass，游戏结束",
                "game_over": True,
                "score": score,
                "winner": winner,
            }

        state["current_player"] = "white" if player == "black" else "black"
        state["last_move_time"] = now
        self._save_match(state)

        return {
            "valid": True,
            "message": f"{player} pass",
            "move_number": state["move_number"],
            "next_player": state["current_player"],
            "game_over": False,
        }

    def _is_ko_candidate(self, state, row, col, player):
        """检查 (row,col) 是否为打劫候选点"""
        board = state["board"]
        size = state["board_size"]
        opp_color = 1 if player == "black" else 2

        # 如果在这个位置落子只提一子，且自身也只有这一子附近的 liberty
        new_board = [r[:] for r in board]
        new_board[row][col] = 1 if player == "black" else 2

        captured = []
        for nr, nc in get_neighbors(row, col, size):
            if new_board[nr][nc] == opp_color:
                g, libs = get_group(new_board, nr, nc, size)
                if len(libs) == 0:
                    captured.extend(g)

        if len(captured) != 1:
            return False

        # 提走后自身气数
        for cr, cc in captured:
            new_board[cr][cc] = 0

        my_color = 1 if player == "black" else 2
        _, my_libs = get_group(new_board, row, col, size)
        return len(my_libs) == 1

    def _end_game(self, state):
        """计算终局得分"""
        board = state["board"]
        size = state["board_size"]
        komi = state.get("komi", 7.5)

        black_stones = sum(row.count(1) for row in board)
        white_stones = sum(row.count(2) for row in board)

        visited = set()
        black_territory = 0
        white_territory = 0

        for r in range(size):
            for c in range(size):
                if board[r][c] == 0 and (r, c) not in visited:
                    region = []
                    borders = set()
                    queue = deque([(r, c)])
                    while queue:
                        cr, cc = queue.popleft()
                        if (cr, cc) in visited:
                            continue
                        visited.add((cr, cc))
                        region.append((cr, cc))
                        for nr, nc in get_neighbors(cr, cc, size):
                            if board[nr][nc] == 0 and (nr, nc) not in visited:
                                queue.append((nr, nc))
                            elif board[nr][nc] != 0:
                                borders.add(board[nr][nc])
                    if len(borders) == 1:
                        if 1 in borders:
                            black_territory += len(region)
                        else:
                            white_territory += len(region)

        black_total = black_stones + black_territory
        white_total = white_stones + white_territory + komi

        winner_id = state["black_id"] if black_total > white_total else state["white_id"]
        state["winner"] = winner_id
        state["ended_at"] = datetime.now().isoformat()
        state["ended_by"] = "move_limit" if state["move_number"] >= 100 else "pass"

        score = {
            "black_stones": black_stones,
            "white_stones": white_stones,
            "black_territory": black_territory,
            "white_territory": white_territory,
            "black_captures": state.get("black_captures", 0),
            "white_captures": state.get("white_captures", 0),
            "komi": komi,
            "black_total": black_total,
            "white_total": round(white_total, 1),
            "winner": state["black_id"] if black_total > white_total else state["white_id"],
        }
        return score, winner_id

    # ==================== 盘面摘要 ====================

    def _board_summary(self, state) -> dict:
        return {
            "match_id": state["match_id"],
            "board_size": state["board_size"],
            "move_number": state["move_number"],
            "current_player": state["current_player"],
            "status": state["status"],
            "black_id": state["black_id"],
            "white_id": state["white_id"],
            "black_captures": state["black_captures"],
            "white_captures": state["white_captures"],
            "komi": state.get("komi", 7.5),
            "black_time_used": state.get("black_time_used", 0),
            "white_time_used": state.get("white_time_used", 0),
        }

    # ==================== SGF ====================

    def _write_sgf_header(self, state):
        dt = datetime.now().strftime("%Y-%m-%d")
        sgf = f"(;GM[1]FF[4]SZ[{state['board_size']}]KM[{state.get('komi', 7.5)}]"
        sgf += f"PB[{state['black_id']}]PW[{state['white_id']}]"
        sgf += f"DT[{dt}]\n"
        with open(config.match_sgf_file(state["match_id"]), "w") as f:
            f.write(sgf)

    def _append_sgf_move(self, state, notation):
        if notation.lower() == "pass":
            sgf_move = ";[]"
        else:
            pos = parse_coord(notation)
            if pos:
                r, c = pos
                sgf_move = f";[{COL_LETTERS[c]}{COL_LETTERS[r]}]"
            else:
                sgf_move = f";[{notation}]"
        with open(config.match_sgf_file(state["match_id"]), "a") as f:
            f.write(sgf_move + "\n")

    def _close_sgf(self, state):
        with open(config.match_sgf_file(state["match_id"]), "a") as f:
            f.write(")\n")

    def get_sgf(self, match_id: str) -> str:
        """获取完整 SGF 棋谱内容"""
        path = config.match_sgf_file(match_id)
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read() + ")\n"
        return ""

    # ==================== 持久化 ====================

    def _save_match(self, state):
        mid = state["match_id"]
        self._matches[mid] = state
        board_data = {
            "match_id": mid,
            "board": state["board"],
            "board_size": state["board_size"],
            "current_player": state["current_player"],
            "move_number": state["move_number"],
            "pass_count": state["pass_count"],
            "black_captures": state["black_captures"],
            "white_captures": state["white_captures"],
            "status": state["status"],
            "history": state["history"],
            "ko_point": state["ko_point"],
            "last_move_time": str(state.get("last_move_time", "")),
        }
        with open(config.match_board_file(mid), "w") as f:
            json.dump(board_data, f, indent=2, ensure_ascii=False)

        meta = {k: v for k, v in state.items()
                if k not in ("board", "history")}
        with open(config.match_meta_file(mid), "w") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False, default=str)

    def _load_match(self, match_id: str) -> dict:
        if match_id in self._matches:
            return self._matches[match_id]
        bf = config.match_board_file(match_id)
        if not os.path.exists(bf):
            return None
        with open(bf, "r") as f:
            board_data = json.load(f)
        mf = config.match_meta_file(match_id)
        meta = {}
        if os.path.exists(mf):
            with open(mf, "r") as f:
                meta = json.load(f)
        state = {**meta, **board_data}
        self._matches[match_id] = state
        return state

    def close_match(self, match_id: str):
        """存档并清理"""
        state = self._load_match(match_id)
        if state:
            self._close_sgf(state)
        self._matches.pop(match_id, None)

    def render_board(self, match_id: str) -> str:
        """返回 Unicode 棋盘字符串"""
        state = self._load_match(match_id)
        if state is None:
            return "[对局不存在]"
        board = state["board"]
        size = state["board_size"]
        lines = []
        header = "    " + " ".join(COL_LETTERS[i] for i in range(size))
        lines.append(header)
        lines.append("  ┌" + "─" * (size * 2 + 1) + "┐")
        for r in range(size):
            row_str = f"{r+1:2d}│"
            for c in range(size):
                s = board[r][c]
                row_str += "●" if s == 1 else ("○" if s == 2 else "・")
            row_str += "│"
            lines.append(row_str)
        lines.append("  └" + "─" * (size * 2 + 1) + "┘")
        turn = "⚫ 黑方" if state["current_player"] == "black" else "⚪ 白方"
        lines.append(f"\n第{state['move_number']}手 · {turn}")
        if state["status"] == "ended":
            lines.append("游戏结束")
        return "\n".join(lines)


# ====== 全局单例 ======
_engine_instance = None


def get_engine() -> GoMatchEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = GoMatchEngine()
    return _engine_instance


# ====== 快速测试 ======
if __name__ == "__main__":
    engine = GoMatchEngine()
    result = engine.start_match("xiaochen", "zhuguxia", board_size=19)
    print(f"对局创建: {result['match_id']}")
    mid = result["match_id"]

    # 模拟几手
    moves = ["Q4", "D16", "Q16", "D4", "R10", "K10", "R14", "C6"]
    for i, mv in enumerate(moves):
        pid = "xiaochen" if i % 2 == 0 else "zhuguxia"
        r = engine.submit_move(mid, pid, mv)
        status = "OK" if r["valid"] else f"FAIL: {r['message']}"
        print(f"  {pid} -> {mv}: {status}")

    print(engine.render_board(mid))
