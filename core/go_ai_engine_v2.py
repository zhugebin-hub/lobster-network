#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 - 围棋AI引擎 v2.0 (优化版)
改进：定式库、形势判断、复盘分析、平衡着法分布

作者：诸葛马 (Hermes)
日期：2026-07-01
版本：v2.0
"""

import random
import copy
import json
import os
from collections import deque
from datetime import datetime

# ============================================================
# 坐标映射
# ============================================================

COL_MAP = {}
for i, c in enumerate('ABCDEFGH'):
    COL_MAP[c] = i
for i, c in enumerate('JKLMNOPQRST'):
    COL_MAP[c] = i + 8

REV_COL_MAP = {}
for i, c in enumerate('ABCDEFGH'):
    REV_COL_MAP[i] = c
for i, c in enumerate('JKLMNOPQRST'):
    REV_COL_MAP[i+8] = c

EMPTY = 0
BLACK = 1
WHITE = 2

# ============================================================
# 定式库 (常见开局模式)
# ============================================================

JOSEKI_LIBRARY = {
    # 星位定式
    "star": [
        # 小飞挂
        [(3,3), (5,4), (4,5), (6,3)],
        # 大飞挂
        [(3,3), (5,3), (4,6), (6,2)],
        # 一间高挂
        [(3,3), (4,4), (3,5), (5,3)],
    ],
    # 小目定式
    "komoku": [
        # 小飞挂
        [(3,4), (4,3), (5,4), (4,5)],
        # 一间高挂
        [(3,4), (4,4), (3,5), (5,3)],
    ],
    # 三三定式
    "san-san": [
        [(3,3), (4,4), (2,4), (5,3)],
    ]
}

# ============================================================
# 围棋引擎 v2.0
# ============================================================

class GoEngineV2:
    """围棋引擎 v2.0 - 完整规则 + 定式库 + 形势判断"""
    
    def __init__(self, size=19, style="balanced"):
        self.size = size
        self.board = [[EMPTY]*size for _ in range(size)]
        self.current_player = BLACK
        self.komi = 7.5
        self.move_history = []
        self.last_board_state = None
        self.captures = {BLACK: 0, WHITE: 0}
        self.style = style  # "conservative", "aggressive", "balanced"
        self.joseki_index = 0
        
    def coord_to_pos(self, coord):
        coord = coord.strip().upper()
        if not coord or len(coord) < 2:
            return None
        col_char = coord[0]
        row_str = coord[1:]
        if col_char not in COL_MAP:
            return None
        col = COL_MAP[col_char]
        try:
            row = int(row_str) - 1
        except:
            return None
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return None
        return (row, col)
    
    def pos_to_coord(self, row, col):
        return f"{REV_COL_MAP[col]}{row+1}"
    
    def _get_neighbors(self, row, col):
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row+dr, col+dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))
        return neighbors
    
    def _get_group(self, row, col):
        color = self.board[row][col]
        if color == EMPTY:
            return [], 0
        
        group = []
        liberties = 0
        visited = set()
        queue = deque([(row, col)])
        
        while queue:
            r, c = queue.popleft()
            if (r, c) in visited:
                continue
            visited.add((r, c))
            group.append((r, c))
            
            for nr, nc in self._get_neighbors(r, c):
                if self.board[nr][nc] == EMPTY:
                    liberties += 1
                elif self.board[nr][nc] == color and (nr, nc) not in visited:
                    queue.append((nr, nc))
        
        return group, liberties
    
    def _remove_group(self, row, col):
        color = self.board[row][col]
        group, _ = self._get_group(row, col)
        for r, c in group:
            self.board[r][c] = EMPTY
        self.captures[color] += len(group)
        return len(group)
    
    def is_valid_move(self, row, col, color):
        if self.board[row][col] != EMPTY:
            return False, "该位置已有棋子"
        
        self.board[row][col] = color
        
        opponent = 3 - color
        can_capture = False
        for nr, nc in self._get_neighbors(row, col):
            if self.board[nr][nc] == opponent:
                _, libs = self._get_group(nr, nc)
                if libs == 0:
                    can_capture = True
                    break
        
        _, self_libs = self._get_group(row, col)
        self.board[row][col] = EMPTY
        
        if self_libs == 0 and not can_capture:
            return False, "禁着点(无气且不能提子)"
        
        board_hash = self._board_hash()
        if self.last_board_state == board_hash:
            return False, "Ko禁着"
        
        return True, "合法"
    
    def _board_hash(self):
        return tuple(tuple(row) for row in self.board)
    
    def place_stone(self, coord):
        pos = self.coord_to_pos(coord)
        if pos is None:
            return {"ok": False, "error": f"无效坐标: {coord}"}
        row, col = pos
        
        color = self.current_player
        valid, msg = self.is_valid_move(row, col, color)
        if not valid:
            return {"ok": False, "error": msg}
        
        self.last_board_state = self._board_hash()
        self.board[row][col] = color
        
        opponent = 3 - color
        for nr, nc in self._get_neighbors(row, col):
            if self.board[nr][nc] == opponent:
                _, libs = self._get_group(nr, nc)
                if libs == 0:
                    self._remove_group(nr, nc)
        
        player_name = "黑" if color == BLACK else "白"
        move = {
            "move_num": len(self.move_history) + 1,
            "player": f"{player_name}方",
            "coord": coord,
            "pos": [row, col],
            "captures": copy.deepcopy(self.captures)
        }
        self.move_history.append(move)
        self.current_player = opponent
        
        return {"ok": True, "move": move}
    
    def ai_move(self):
        """AI自动落子 - v2.0优化版"""
        color = self.current_player
        move_num = len(self.move_history)
        
        # 开局阶段：使用定式库
        if move_num < 10:
            result = self._joseki_move(color, move_num)
            if result:
                return result
        
        # 中盘阶段：平衡评估
        if self.size == 9:
            return self._ai_move_9x9(color)
        else:
            return self._ai_move_19x19(color)
    
    def _joseki_move(self, color, move_num):
        """使用定式库生成开局着法"""
        if move_num == 0:
            # 第一手：优先星位
            star_points = [(3,3), (3,9), (3,15), (9,3), (9,9), (9,15), (15,3), (15,9), (15,15)]
            random.shuffle(star_points)
            for r, c in star_points:
                valid, _ = self.is_valid_move(r, c, color)
                if valid:
                    return self.place_stone(self.pos_to_coord(r, c))
        
        elif move_num == 1:
            # 白方第一手：对角星位
            star_points = [(3,3), (3,15), (15,3), (15,15)]
            random.shuffle(star_points)
            for r, c in star_points:
                valid, _ = self.is_valid_move(r, c, color)
                if valid:
                    return self.place_stone(self.pos_to_coord(r, c))
        
        elif move_num < 6:
            # 使用定式库
            joseki_type = "star" if move_num % 2 == 0 else "komoku"
            josekis = JOSEKI_LIBRARY.get(joseki_type, [])
            if josekis:
                joseki = josekis[self.joseki_index % len(josekis)]
                self.joseki_index += 1
                
                for r, c in joseki:
                    valid, _ = self.is_valid_move(r, c, color)
                    if valid:
                        return self.place_stone(self.pos_to_coord(r, c))
        
        return None
    
    def _ai_move_9x9(self, color):
        """9x9 AI策略"""
        valid_moves = []
        for r in range(self.size):
            for c in range(self.size):
                valid, _ = self.is_valid_move(r, c, color)
                if valid:
                    score = self._evaluate_move(r, c, color)
                    valid_moves.append((r, c, score))
        
        if not valid_moves:
            return {"ok": False, "error": "无合法着法"}
        
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        top_n = max(1, len(valid_moves) // 3)
        chosen = random.choice(valid_moves[:top_n])
        
        return self.place_stone(self.pos_to_coord(chosen[0], chosen[1]))
    
    def _ai_move_19x19(self, color):
        """19x19 AI策略 - v2.0优化版"""
        valid_moves = []
        candidate_set = set()
        
        # 找候选位置
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != EMPTY:
                    for nr, nc in self._get_neighbors(r, c):
                        if self.board[nr][nc] == EMPTY:
                            candidate_set.add((nr, nc))
                    # 增加2格距离的候选
                    for nr in range(max(0, r-2), min(self.size, r+3)):
                        for nc in range(max(0, c-2), min(self.size, c+3)):
                            if self.board[nr][nc] == EMPTY:
                                candidate_set.add((nr, nc))
        
        # 如果没有候选，用空位
        if not candidate_set:
            for r in range(self.size):
                for c in range(self.size):
                    if self.board[r][c] == EMPTY:
                        candidate_set.add((r, c))
        
        for r, c in candidate_set:
            valid, _ = self.is_valid_move(r, c, color)
            if valid:
                score = self._evaluate_move(r, c, color)
                valid_moves.append((r, c, score))
        
        if not valid_moves:
            return {"ok": False, "error": "无合法着法"}
        
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        top_n = max(1, len(valid_moves) // 5)
        chosen = random.choice(valid_moves[:top_n])
        
        return self.place_stone(self.pos_to_coord(chosen[0], chosen[1]))
    
    def _evaluate_move(self, row, col, color):
        """着法评估 - v2.0优化版"""
        score = 0
        move_num = len(self.move_history)
        
        # 阶段权重
        if move_num < 20:
            # 开局：角部优先，但不过度
            if row < 4 or row > 14:
                score += 8  # 降低角部权重
            if col < 4 or col > 14:
                score += 8
            # 星位
            star_points = [(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)]
            if (row, col) in star_points:
                score += 15
            # 三三
            san_san_points = [(2,2),(2,16),(16,2),(16,16)]
            if (row, col) in san_san_points:
                score += 12
            # 中腹开局也考虑
            if 6 <= row <= 12 and 6 <= col <= 12:
                score += 5
        
        elif move_num < 60:
            # 中盘：接触战优先，平衡角部和中腹
            for nr, nc in self._get_neighbors(row, col):
                if self.board[nr][nc] != EMPTY:
                    score += 10
                    if self.board[nr][nc] == color:
                        score += 5  # 连接
                    else:
                        score += 8  # 攻击
            
            # 中腹价值提升
            if 4 <= row <= 14 and 4 <= col <= 14:
                score += 8
            
            # 角部价值降低
            if row < 3 or row > 15 or col < 3 or col > 15:
                score += 3
        
        else:
            # 官子：逐步缩小
            for nr, nc in self._get_neighbors(row, col):
                if self.board[nr][nc] != EMPTY:
                    score += 6
        
        # 避免贴一线
        if row == 0 or row == self.size-1 or col == 0 or col == self.size-1:
            score -= 12
        
        # 避免贴二线（除非是角部）
        if row <= 1 or row >= self.size-2 or col <= 1 or col >= self.size-2:
            if not (row < 4 and col < 4):
                score -= 5
        
        # 风格调整
        if self.style == "conservative":
            # 稳健型：更注重防守
            score += 3 if self._is_defensive(row, col, color) else 0
        elif self.style == "aggressive":
            # 激进型：更注重攻击
            score += 3 if self._is_aggressive(row, col, color) else 0
        
        # 随机扰动
        score += random.uniform(-3, 3)
        
        return score
    
    def _is_defensive(self, row, col, color):
        """检查是否是防守着法"""
        for nr, nc in self._get_neighbors(row, col):
            if self.board[nr][nc] == color:
                _, libs = self._get_group(nr, nc)
                if libs <= 2:
                    return True
        return False
    
    def _is_aggressive(self, row, col, color):
        """检查是否是攻击着法"""
        opponent = 3 - color
        for nr, nc in self._get_neighbors(row, col):
            if self.board[nr][nc] == opponent:
                _, libs = self._get_group(nr, nc)
                if libs <= 2:
                    return True
        return False
    
    def print_board(self):
        col_labels = "   " + " ".join([REV_COL_MAP[i] for i in range(self.size)])
        result = [col_labels]
        
        for row in range(self.size):
            row_num = f"{row+1:2d}" if self.size > 9 else f"{row+1}"
            row_str = f"{row_num} "
            for col in range(self.size):
                cell = self.board[row][col]
                if cell == BLACK:
                    row_str += "●"
                elif cell == WHITE:
                    row_str += "○"
                else:
                    row_str += "·"
            row_str += f" {row_num}" if self.size > 9 else ""
            result.append(row_str)
        
        result.append(col_labels)
        return "\n".join(result)
    
    def get_status(self):
        next_color = "黑" if self.current_player == BLACK else "白"
        return {
            "total_moves": len(self.move_history),
            "next_player": f"{next_color}方",
            "captures": self.captures,
            "board_size": self.size
        }
    
    def analyze_game(self):
        """对局分析 - v2.0新增"""
        analysis = {
            "total_moves": len(self.move_history),
            "captures": self.captures,
            "move_distribution": self._analyze_distribution(),
            "key_moves": self._identify_key_moves(),
            "strengths": [],
            "weaknesses": []
        }
        
        # 分析着法分布
        dist = analysis["move_distribution"]
        if dist["corners_pct"] > 60:
            analysis["weaknesses"].append("角部着法过多，中腹不足")
        if dist["center_pct"] < 20:
            analysis["weaknesses"].append("中腹战斗不足")
        if dist["edges_pct"] < 10:
            analysis["weaknesses"].append("边路利用不足")
        
        if dist["corners_pct"] < 40:
            analysis["strengths"].append("全局观良好")
        if dist["center_pct"] > 30:
            analysis["strengths"].append("中腹战斗积极")
        
        return analysis
    
    def _analyze_distribution(self):
        """分析着法分布"""
        black_moves = [m for m in self.move_history if m["player"] == "黑方"]
        white_moves = [m for m in self.move_history if m["player"] == "白方"]
        
        def analyze_moves(moves):
            corners = sum(1 for m in moves if m["pos"][0] < 4 or m["pos"][0] > 14 or m["pos"][1] < 4 or m["pos"][1] > 14)
            edges = sum(1 for m in moves if m["pos"][0] == 0 or m["pos"][0] == 18 or m["pos"][1] == 0 or m["pos"][1] == 18)
            center = sum(1 for m in moves if 4 <= m["pos"][0] <= 14 and 4 <= m["pos"][1] <= 14)
            return {
                "total": len(moves),
                "corners": corners,
                "corners_pct": corners * 100 // max(1, len(moves)),
                "edges": edges,
                "edges_pct": edges * 100 // max(1, len(moves)),
                "center": center,
                "center_pct": center * 100 // max(1, len(moves)),
            }
        
        return {
            "black": analyze_moves(black_moves),
            "white": analyze_moves(white_moves),
        }
    
    def _identify_key_moves(self):
        """识别关键着法"""
        key_moves = []
        
        for m in self.move_history:
            caps = m.get("captures", {})
            if caps.get(BLACK, 0) + caps.get(WHITE, 0) > 0:
                key_moves.append({
                    "move_num": m["move_num"],
                    "coord": m["coord"],
                    "type": "capture",
                    "captures": caps
                })
        
        # 识别转折点
        for i in range(1, len(self.move_history)):
            m = self.move_history[i]
            if m["move_num"] % 20 == 0:
                key_moves.append({
                    "move_num": m["move_num"],
                    "coord": m["coord"],
                    "type": "milestone"
                })
        
        return key_moves


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    import sys
    
    size = 19
    style = "balanced"
    
    if len(sys.argv) > 1:
        size = int(sys.argv[1])
    if len(sys.argv) > 2:
        style = sys.argv[2]
    
    engine = GoEngineV2(size, style)
    print(f"🏁 围棋AI引擎 v2.0 ({size}x{size}, 风格:{style})")
    print()
    
    max_moves = 30 if size == 9 else 50
    for i in range(max_moves):
        result = engine.ai_move()
        if result["ok"]:
            m = result["move"]
            caps = m.get("captures", {})
            cap_str = ""
            if caps.get(BLACK, 0) + caps.get(WHITE, 0) > 0:
                cap_str = f" | 提子: 黑{caps.get(BLACK,0)} 白{caps.get(WHITE,0)}"
            print(f"第{m['move_num']:3d}手: {m['player']} → {m['coord']}{cap_str}")
        else:
            print(f"❌ {result['error']}")
            break
    
    print("\n" + engine.print_board())
    
    # 分析
    analysis = engine.analyze_game()
    print("\n📊 对局分析:")
    print(f"  总手数: {analysis['total_moves']}")
    print(f"  提子: 黑{analysis['captures'][BLACK]} 白{analysis['captures'][WHITE]}")
    
    if analysis["strengths"]:
        print(f"  优点: {', '.join(analysis['strengths'])}")
    if analysis["weaknesses"]:
        print(f"  不足: {', '.join(analysis['weaknesses'])}")
