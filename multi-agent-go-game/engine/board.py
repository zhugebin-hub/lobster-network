"""
围棋棋盘引擎（9x9）
支持：落子、提子、劫争检测、气计算、棋盘序列化
"""

import json
from enum import Enum
from typing import List, Tuple, Optional, Set


class StoneColor(Enum):
    """棋子颜色"""
    EMPTY = 0
    BLACK = 1
    WHITE = 2


class Point:
    """棋盘坐标点"""
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
    
    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __repr__(self):
        return f"({self.row},{self.col})"
    
    def to_gtp(self) -> str:
        """转换为 GTP 坐标格式（如 D4）"""
        col_char = chr(ord('A') + self.col)
        if self.col >= 7:
            col_char = chr(ord('A') + self.col + 1)  # 跳过 I
        return f"{col_char}{9 - self.row}"
    
    @staticmethod
    def from_gtp(gtp: str) -> 'Point':
        """从 GTP 坐标格式解析"""
        col_char = gtp[0].upper()
        col = ord(col_char) - ord('A')
        if col_char > 'I':
            col -= 1
        row = 9 - int(gtp[1:])
        return Point(row, col)


class GoBoard:
    """9x9 围棋棋盘"""
    
    def __init__(self, size: int = 9):
        self.size = size
        self.grid = [[StoneColor.EMPTY for _ in range(size)] for _ in range(size)]
        self.current_player = StoneColor.BLACK
        self.move_history: List[Tuple[Optional[Point], StoneColor]] = []
        self.captures = {StoneColor.BLACK: 0, StoneColor.WHITE: 0}
        self.ko_point: Optional[Point] = None
        self.previous_hash: Optional[str] = None
    
    def get(self, p: Point) -> StoneColor:
        return self.grid[p.row][p.col]
    
    def set(self, p: Point, color: StoneColor):
        self.grid[p.row][p.col] = color
    
    def is_empty(self, p: Point) -> bool:
        return self.grid[p.row][p.col] == StoneColor.EMPTY
    
    def neighbors(self, p: Point) -> List[Point]:
        result = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = p.row + dr, p.col + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                result.append(Point(nr, nc))
        return result
    
    def get_group(self, p: Point) -> Tuple[List[Point], StoneColor]:
        color = self.grid[p.row][p.col]
        if color == StoneColor.EMPTY:
            return [], color
        
        group = []
        visited = set()
        stack = [p]
        
        while stack:
            curr = stack.pop()
            if curr in visited:
                continue
            visited.add(curr)
            group.append(curr)
            
            for neighbor in self.neighbors(curr):
                if self.grid[neighbor.row][neighbor.col] == color and neighbor not in visited:
                    stack.append(neighbor)
        
        return group, color
    
    def count_liberties(self, group: List[Point]) -> int:
        liberties = set()
        for p in group:
            for neighbor in self.neighbors(p):
                if self.grid[neighbor.row][neighbor.col] == StoneColor.EMPTY:
                    liberties.add(neighbor)
        return len(liberties)
    
    def remove_group(self, group: List[Point]):
        for p in group:
            self.grid[p.row][p.col] = StoneColor.EMPTY
    
    def board_hash(self) -> str:
        return "".join(str(cell.value) for row in self.grid for cell in row)
    
    def is_valid_move(self, p: Point, color: StoneColor) -> bool:
        if not (0 <= p.row < self.size and 0 <= p.col < self.size):
            return False
        if not self.is_empty(p):
            return False
        if self.ko_point and p == self.ko_point:
            return False
        
        # 模拟落子
        self.grid[p.row][p.col] = color
        opponent = StoneColor.WHITE if color == StoneColor.BLACK else StoneColor.BLACK
        
        captured_any = False
        for neighbor in self.neighbors(p):
            if self.grid[neighbor.row][neighbor.col] == opponent:
                group, _ = self.get_group(neighbor)
                if self.count_liberties(group) == 0:
                    captured_any = True
                    break
        
        if not captured_any:
            my_group, _ = self.get_group(p)
            if self.count_liberties(my_group) == 0:
                self.grid[p.row][p.col] = StoneColor.EMPTY
                return False
        
        self.grid[p.row][p.col] = StoneColor.EMPTY
        return True
    
    def place_stone(self, p: Point, color: StoneColor) -> List[Point]:
        if not self.is_valid_move(p, color):
            raise ValueError(f"非法落子: {p.to_gtp()}")
        
        self.previous_hash = self.board_hash()
        self.grid[p.row][p.col] = color
        opponent = StoneColor.WHITE if color == StoneColor.BLACK else StoneColor.BLACK
        
        captured = []
        for neighbor in self.neighbors(p):
            if self.grid[neighbor.row][neighbor.col] == opponent:
                group, _ = self.get_group(neighbor)
                if self.count_liberties(group) == 0:
                    captured.extend(group)
        
        if captured:
            self.remove_group(captured)
            self.captures[color] += len(captured)
            
            if len(captured) == 1:
                my_group, _ = self.get_group(p)
                if len(my_group) == 1 and self.count_liberties(my_group) == 1:
                    self.ko_point = captured[0]
                else:
                    self.ko_point = None
            else:
                self.ko_point = None
        else:
            self.ko_point = None
        
        self.move_history.append((p, color))
        self.current_player = opponent
        return captured
    
    def pass_move(self):
        self.previous_hash = self.board_hash()
        self.ko_point = None
        self.current_player = StoneColor.WHITE if self.current_player == StoneColor.BLACK else StoneColor.BLACK
        self.move_history.append((None, self.current_player))
    
    def get_valid_moves(self) -> List[Point]:
        valid = []
        for r in range(self.size):
            for c in range(self.size):
                p = Point(r, c)
                if self.is_valid_move(p, self.current_player):
                    valid.append(p)
        return valid
    
    def to_dict(self) -> dict:
        return {
            'size': self.size,
            'grid': [[cell.value for cell in row] for row in self.grid],
            'current_player': self.current_player.value,
            'move_count': len(self.move_history),
            'captures': {k.value: v for k, v in self.captures.items()},
            'ko_point': self.ko_point.to_gtp() if self.ko_point else None,
            'last_moves': [
                (pt.to_gtp() if pt else 'PASS', color.value)
                for pt, color in self.move_history[-10:]
            ]
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'GoBoard':
        board = GoBoard(data['size'])
        for r in range(data['size']):
            for c in range(data['size']):
                board.grid[r][c] = StoneColor(data['grid'][r][c])
        board.current_player = StoneColor(data['current_player'])
        board.captures = {StoneColor(int(k)): v for k, v in data['captures'].items()}
        if data.get('ko_point'):
            board.ko_point = Point.from_gtp(data['ko_point'])
        return board
    
    def display(self) -> str:
        """ASCII 显示棋盘"""
        lines = []
        cols = []
        for i in range(self.size):
            c = chr(ord('A') + i)
            if i >= 7:
                c = chr(ord('A') + i + 1)
            cols.append(c)
        lines.append("   " + " ".join(cols))
        
        for r in range(self.size):
            row_str = f"{9-r:2d} "
            for c in range(self.size):
                cell = self.grid[r][c]
                if cell == StoneColor.EMPTY:
                    row_str += " + "
                elif cell == StoneColor.BLACK:
                    row_str += " ● "
                else:
                    row_str += " ○ "
            lines.append(row_str)
        
        return "\n".join(lines)
    
    def display_with_last_move(self, last_move: Optional[Point] = None) -> str:
        """显示棋盘，标记最后落子位置"""
        lines = []
        cols = []
        for i in range(self.size):
            c = chr(ord('A') + i)
            if i >= 7:
                c = chr(ord('A') + i + 1)
            cols.append(c)
        lines.append("   " + " ".join(cols))
        
        for r in range(self.size):
            row_str = f"{9-r:2d} "
            for c in range(self.size):
                cell = self.grid[r][c]
                if last_move and r == last_move.row and c == last_move.col:
                    if cell == StoneColor.BLACK:
                        row_str += " ⬤ "  # 黑棋标记
                    else:
                        row_str += " ⬡ "  # 白棋标记
                elif cell == StoneColor.EMPTY:
                    row_str += " + "
                elif cell == StoneColor.BLACK:
                    row_str += " ● "
                else:
                    row_str += " ○ "
            lines.append(row_str)
        
        return "\n".join(lines)


if __name__ == '__main__':
    board = GoBoard(9)
    print("=== 初始棋盘 ===")
    print(board.display())
    
    p1 = Point.from_gtp("D4")
    board.place_stone(p1, StoneColor.BLACK)
    print("\n=== 黑 D4 ===")
    print(board.display())
    
    p2 = Point.from_gtp("Q6")
    board.place_stone(p2, StoneColor.WHITE)
    print("\n=== 白 Q6 ===")
    print(board.display())
    
    print(f"\n当前玩家：{'黑' if board.current_player == StoneColor.BLACK else '白'}")
    print(f"手数：{len(board.move_history)}")
    print(f"提子：黑{board.captures[StoneColor.BLACK]} 白{board.captures[StoneColor.WHITE]}")
