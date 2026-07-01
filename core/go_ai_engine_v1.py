#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 - 轻量级围棋AI引擎
支持9x9和19x19，含完整规则（气/提子/禁着点/Ko）+ AI落子策略

作者：诸葛马 (Hermes)
日期：2026-07-01
版本：v1.0
"""

import random
import copy
from collections import deque

# ============================================================
# 棋盘常量
# ============================================================

# 坐标映射
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
# 围棋引擎
# ============================================================

class GoEngine:
    """围棋引擎 - 完整规则"""
    
    def __init__(self, size=19):
        self.size = size
        self.board = [[EMPTY]*size for _ in range(size)]
        self.current_player = BLACK  # 黑先
        self.komi = 7.5  # 中国规则
        self.move_history = []
        self.last_board_state = None  # Ko检测
        self.captures = {BLACK: 0, WHITE: 0}
    
    def coord_to_pos(self, coord):
        """坐标转位置: A1-T19"""
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
        """位置转坐标"""
        return f"{REV_COL_MAP[col]}{row+1}"
    
    def _get_neighbors(self, row, col):
        """获取相邻位置"""
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = row+dr, col+dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                neighbors.append((nr, nc))
        return neighbors
    
    def _get_group(self, row, col):
        """获取棋子组(连通块)"""
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
        """提子"""
        color = self.board[row][col]
        group, _ = self._get_group(row, col)
        for r, c in group:
            self.board[r][c] = EMPTY
        self.captures[color] += len(group)
        return len(group)
    
    def is_valid_move(self, row, col, color):
        """检查落子是否合法"""
        if self.board[row][col] != EMPTY:
            return False, "该位置已有棋子"
        
        # 临时落子
        self.board[row][col] = color
        
        # 检查是否能提对方子
        opponent = 3 - color
        can_capture = False
        for nr, nc in self._get_neighbors(row, col):
            if self.board[nr][nc] == opponent:
                _, libs = self._get_group(nr, nc)
                if libs == 0:
                    can_capture = True
                    break
        
        # 检查自己是否有气
        _, self_libs = self._get_group(row, col)
        
        # 恢复
        self.board[row][col] = EMPTY
        
        if self_libs == 0 and not can_capture:
            return False, "禁着点(无气且不能提子)"
        
        # Ko检测
        board_hash = self._board_hash()
        if self.last_board_state == board_hash:
            return False, "Ko禁着"
        
        return True, "合法"
    
    def _board_hash(self):
        """棋盘哈希(用于Ko检测)"""
        return tuple(tuple(row) for row in self.board)
    
    def place_stone(self, coord):
        """落子"""
        pos = self.coord_to_pos(coord)
        if pos is None:
            return {"ok": False, "error": f"无效坐标: {coord}"}
        row, col = pos
        
        color = self.current_player
        valid, msg = self.is_valid_move(row, col, color)
        if not valid:
            return {"ok": False, "error": msg}
        
        # 保存状态用于Ko检测
        self.last_board_state = self._board_hash()
        
        # 落子
        self.board[row][col] = color
        
        # 提对方子
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
        """AI自动落子"""
        color = self.current_player
        size = self.size
        
        # 根据棋盘大小选择策略
        if size == 9:
            return self._ai_move_9x9(color)
        else:
            return self._ai_move_19x19(color)
    
    def _ai_move_9x9(self, color):
        """9x9 AI策略"""
        valid_moves = []
        for r in range(self.size):
            for c in range(self.size):
                valid, _ = self.is_valid_move(r, c, color)
                if valid:
                    score = self._evaluate_move_9x9(r, c, color)
                    valid_moves.append((r, c, score))
        
        if not valid_moves:
            return {"ok": False, "error": "无合法着法"}
        
        # 按分数排序
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        
        # 选择前30%中随机一个（增加变化）
        top_n = max(1, len(valid_moves) // 3)
        chosen = random.choice(valid_moves[:top_n])
        
        return self.place_stone(self.pos_to_coord(chosen[0], chosen[1]))
    
    def _evaluate_move_9x9(self, row, col, color):
        """9x9着法评估"""
        score = 0
        
        # 中心偏好
        center = self.size // 2
        dist_center = abs(row - center) + abs(col - center)
        score += (self.size - dist_center) * 2
        
        # 星位偏好
        star_points = [(2,2), (2,6), (6,2), (6,6), (4,4)]
        if (row, col) in star_points:
            score += 15
        
        # 邻近己方棋子加分（配合）
        for nr, nc in self._get_neighbors(row, col):
            if self.board[nr][nc] == color:
                score += 5
            elif self.board[nr][nc] == 3 - color:
                score += 3  # 接触战
        
        # 避免贴边
        if row == 0 or row == self.size-1:
            score -= 3
        if col == 0 or col == self.size-1:
            score -= 3
        
        # 随机扰动
        score += random.uniform(-2, 2)
        
        return score
    
    def _ai_move_19x19(self, color):
        """19x19 AI策略"""
        valid_moves = []
        
        # 只评估有邻近棋子的位置（提高效率）
        candidate_set = set()
        
        if len(self.move_history) == 0:
            # 第一手：优先星位和三三
            star_points = [
                (3,3), (3,9), (3,15),   # 左
                (9,3), (9,9), (9,15),   # 中
                (15,3), (15,9), (15,15) # 右
            ]
            for r, c in star_points:
                valid, _ = self.is_valid_move(r, c, color)
                if valid:
                    candidate_set.add((r, c))
        else:
            # 找邻近已有棋子的空位
            for r in range(self.size):
                for c in range(self.size):
                    if self.board[r][c] != EMPTY:
                        for nr, nc in self._get_neighbors(r, c):
                            if self.board[nr][nc] == EMPTY:
                                candidate_set.add((nr, nc))
            
            # 如果没有候选（第一手特殊情况），用星位
            if not candidate_set:
                for r in range(self.size):
                    for c in range(self.size):
                        if self.board[r][c] == EMPTY:
                            candidate_set.add((r, c))
        
        for r, c in candidate_set:
            valid, _ = self.is_valid_move(r, c, color)
            if valid:
                score = self._evaluate_move_19x19(r, c, color)
                valid_moves.append((r, c, score))
        
        if not valid_moves:
            return {"ok": False, "error": "无合法着法"}
        
        valid_moves.sort(key=lambda x: x[2], reverse=True)
        
        # 选择前20%中随机
        top_n = max(1, len(valid_moves) // 5)
        chosen = random.choice(valid_moves[:top_n])
        
        return self.place_stone(self.pos_to_coord(chosen[0], chosen[1]))
    
    def _evaluate_move_19x19(self, row, col, color):
        """19x19着法评估"""
        score = 0
        
        # 开局阶段：优先角和边
        move_num = len(self.move_history)
        
        if move_num < 20:
            # 开局：角部优先 > 边 > 中腹
            if row < 4 or row > 14:
                score += 10
            if col < 4 or col > 14:
                score += 10
            # 星位
            star_points = [(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)]
            if (row, col) in star_points:
                score += 20
            # 三三
            san_san_points = [(2,2),(2,16),(16,2),(16,16)]
            if (row, col) in san_san_points:
                score += 15
        elif move_num < 60:
            # 中盘：接触战优先
            for nr, nc in self._get_neighbors(row, col):
                if self.board[nr][nc] != EMPTY:
                    score += 8
                    if self.board[nr][nc] == color:
                        score += 3  # 连接
                    else:
                        score += 5  # 攻击
        else:
            # 官子：逐步缩小
            for nr, nc in self._get_neighbors(row, col):
                if self.board[nr][nc] != EMPTY:
                    score += 5
        
        # 避免贴一线
        if row == 0 or row == self.size-1 or col == 0 or col == self.size-1:
            score -= 10
        
        # 避免贴二线（除非是角部）
        if row <= 1 or row >= self.size-2 or col <= 1 or col >= self.size-2:
            if not (row < 4 and col < 4):  # 角部除外
                score -= 3
        
        # 随机扰动
        score += random.uniform(-3, 3)
        
        return score
    
    def print_board(self):
        """打印棋盘"""
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
        """获取对局状态"""
        next_color = "黑" if self.current_player == BLACK else "白"
        return {
            "total_moves": len(self.move_history),
            "next_player": f"{next_color}方",
            "captures": self.captures,
            "board_size": self.size
        }


# ============================================================
# 主入口 - 测试
# ============================================================

if __name__ == "__main__":
    import sys
    
    size = 19
    if len(sys.argv) > 1:
        size = int(sys.argv[1])
    
    engine = GoEngine(size)
    print(f"🏁 围棋AI引擎 v1.0 ({size}x{size})")
    print()
    
    # 模拟AI对弈
    max_moves = 20 if size == 9 else 30
    for i in range(max_moves):
        result = engine.ai_move()
        if result["ok"]:
            m = result["move"]
            captures = m.get("captures", {})
            cap_str = ""
            if captures.get(BLACK, 0) + captures.get(WHITE, 0) > 0:
                cap_str = f" | 提子: 黑{captures.get(BLACK,0)} 白{captures.get(WHITE,0)}"
            print(f"第{m['move_num']}手: {m['player']} → {m['coord']}{cap_str}")
        else:
            print(f"❌ {result['error']}")
            break
    
    print("\n" + engine.print_board())
    print("\n" + str(engine.get_status()))
