"""
围棋棋手模块
定义不同风格的AI棋手
"""

import random
from typing import List, Tuple, Optional
from engine.board import GoBoard, Point, StoneColor


class GoPlayer:
    """围棋棋手基类"""
    
    def __init__(self, name: str, color: StoneColor):
        self.name = name
        self.color = color
        self.opponent = StoneColor.WHITE if color == StoneColor.BLACK else StoneColor.BLACK
        self.wins = 0
        self.losses = 0
        self.draws = 0
    
    def evaluate_move(self, board: GoBoard, p: Point) -> float:
        """评估落子价值（子类可重写）"""
        score = 0.0
        
        # 中心偏好
        center_row, center_col = 4, 4
        dist_to_center = abs(p.row - center_row) + abs(p.col - center_col)
        score += (8 - dist_to_center) * 0.1
        
        # 边线惩罚
        if p.row == 0 or p.row == board.size - 1 or p.col == 0 or p.col == board.size - 1:
            score -= 1.0
        
        # 邻近棋子
        for neighbor in board.neighbors(p):
            if board.get(neighbor) == self.color:
                score += 2.0
            elif board.get(neighbor) == self.opponent:
                score += 1.0
        
        # 模拟落子
        board.set(p, self.color)
        group, _ = board.get_group(p)
        liberties = board.count_liberties(group)
        score += liberties * 0.5
        
        # 提子价值
        for neighbor in board.neighbors(p):
            if board.get(neighbor) == self.opponent:
                neighbor_group, _ = board.get_group(neighbor)
                if board.count_liberties(neighbor_group) == 1:
                    score += 10.0
        
        # 自杀惩罚
        if liberties == 0:
            score -= 100.0
        
        board.set(p, StoneColor.EMPTY)
        
        # 随机性
        score += random.uniform(-0.3, 0.3)
        
        return score
    
    def select_move(self, board: GoBoard) -> Optional[Point]:
        """选择落子位置"""
        valid_moves = board.get_valid_moves()
        
        if not valid_moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        for p in valid_moves:
            score = self.evaluate_move(board, p)
            if score > best_score:
                best_score = score
                best_move = p
        
        return best_move
    
    def record_win(self):
        self.wins += 1
    
    def record_loss(self):
        self.losses += 1
    
    def record_draw(self):
        self.draws += 1
    
    def get_stats(self) -> dict:
        return {
            'name': self.name,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'total_games': self.wins + self.losses + self.draws,
            'win_rate': self.wins / max(1, self.wins + self.losses + self.draws) * 100
        }


class AggressivePlayer(GoPlayer):
    """激进型棋手 - 喜欢进攻"""
    
    def __init__(self):
        super().__init__("激进型棋手", StoneColor.BLACK)
    
    def evaluate_move(self, board: GoBoard, p: Point) -> float:
        score = super().evaluate_move(board, p)
        
        # 增加攻击性评分
        board.set(p, self.color)
        for neighbor in board.neighbors(p):
            if board.get(neighbor) == self.opponent:
                neighbor_group, _ = board.get_group(neighbor)
                if board.count_liberties(neighbor_group) <= 2:
                    score += 5.0  # 攻击弱棋
        board.set(p, StoneColor.EMPTY)
        
        return score


class DefensivePlayer(GoPlayer):
    """防守型棋手 - 喜欢防守"""
    
    def __init__(self):
        super().__init__("防守型棋手", StoneColor.WHITE)
    
    def evaluate_move(self, board: GoBoard, p: Point) -> float:
        score = super().evaluate_move(board, p)
        
        # 增加防守性评分
        board.set(p, self.color)
        group, _ = board.get_group(p)
        liberties = board.count_liberties(group)
        if liberties >= 3:
            score += 3.0  # 确保气数充足
        board.set(p, StoneColor.EMPTY)
        
        return score


class BalancedPlayer(GoPlayer):
    """平衡型棋手 - 攻守平衡"""
    
    def __init__(self):
        super().__init__("平衡型棋手", StoneColor.BLACK)


class RandomPlayer(GoPlayer):
    """随机型棋手 - 随机落子"""
    
    def __init__(self):
        super().__init__("随机型棋手", StoneColor.WHITE)
    
    def select_move(self, board: GoBoard) -> Optional[Point]:
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return None
        return random.choice(valid_moves)


class StarPlayer(GoPlayer):
    """星位型棋手 - 喜欢占星位"""
    
    def __init__(self):
        super().__init__("星位型棋手", StoneColor.BLACK)
        self.star_points = [
            Point(3, 3), Point(3, 6), Point(6, 3), Point(6, 6),  # 四星
            Point(4, 4)  # 天元
        ]
    
    def evaluate_move(self, board: GoBoard, p: Point) -> float:
        score = super().evaluate_move(board, p)
        
        # 星位偏好
        for sp in self.star_points:
            if p == sp:
                score += 3.0
                break
        
        return score


def create_players() -> List[GoPlayer]:
    """创建所有棋手"""
    return [
        AggressivePlayer(),
        DefensivePlayer(),
        BalancedPlayer(),
        RandomPlayer(),
        StarPlayer()
    ]


if __name__ == '__main__':
    from engine.board import GoBoard, Point, StoneColor
    
    board = GoBoard(9)
    players = create_players()
    
    print("=== 棋手列表 ===")
    for player in players:
        print(f"{player.name} ({'黑' if player.color == StoneColor.BLACK else '白'})")
    
    print("\n=== 测试棋手策略 ===")
    for player in players:
        move = player.select_move(board)
        if move:
            print(f"{player.name} 选择: {move.to_gtp()}")
        else:
            print(f"{player.name} 无合法落子")
