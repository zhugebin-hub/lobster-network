"""
简单围棋策略
基于启发式规则的落子选择
"""

import random
from typing import List, Tuple, Optional
from engine.board import GoBoard, Point, StoneColor


class SimpleStrategy:
    """简单围棋策略"""
    
    def __init__(self, color: StoneColor):
        self.color = color
        self.opponent = StoneColor.WHITE if color == StoneColor.BLACK else StoneColor.BLACK
    
    def evaluate_move(self, board: GoBoard, p: Point) -> float:
        """
        评估落子价值
        返回评分（越高越好）
        """
        score = 0.0
        
        # 1. 中心偏好（天元附近更好）
        center_row, center_col = 4, 4
        dist_to_center = abs(p.row - center_row) + abs(p.col - center_col)
        score += (8 - dist_to_center) * 0.1
        
        # 2. 边线惩罚（避免太靠边）
        if p.row == 0 or p.row == board.size - 1 or p.col == 0 or p.col == board.size - 1:
            score -= 1.0
        
        # 3. 邻近已有棋子（连子更好）
        for neighbor in board.neighbors(p):
            if board.get(neighbor) == self.color:
                score += 2.0
            elif board.get(neighbor) == self.opponent:
                score += 1.0
        
        # 4. 对角位置评估
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = p.row + dr, p.col + dc
            if 0 <= nr < board.size and 0 <= nc < board.size:
                if board.get(Point(nr, nc)) == self.color:
                    score += 0.5  # 小飞/大飞形状
        
        # 5. 气数评估
        # 模拟落子
        board.set(p, self.color)
        
        # 获取新组
        group, _ = board.get_group(p)
        liberties = board.count_liberties(group)
        
        # 气数越多越好
        score += liberties * 0.5
        
        # 6. 提子价值
        for neighbor in board.neighbors(p):
            if board.get(neighbor) == self.opponent:
                neighbor_group, _ = board.get_group(neighbor)
                if board.count_liberties(neighbor_group) == 1:
                    score += 10.0  # 可以提子！
        
        # 7. 避免自杀
        if liberties == 0:
            score -= 100.0
        
        # 8. 模式匹配（简单形状识别）
        # 检查是否形成好形状（如跳、飞、镇等）
        pattern_score = self._evaluate_pattern(board, p)
        score += pattern_score
        
        # 恢复棋盘
        board.set(p, StoneColor.EMPTY)
        
        # 9. 随机性（增加多样性）
        score += random.uniform(-0.3, 0.3)
        
        return score
    
    def _evaluate_pattern(self, board: GoBoard, p: Point) -> float:
        """评估形状"""
        score = 0.0
        
        # 检查是否有相邻的同色棋子形成好形状
        adjacent_same = 0
        adjacent_opp = 0
        
        for neighbor in board.neighbors(p):
            if board.get(neighbor) == self.color:
                adjacent_same += 1
            elif board.get(neighbor) == self.opponent:
                adjacent_opp += 1
        
        # 好形状：有1-2个相邻同色棋子
        if 1 <= adjacent_same <= 2:
            score += 1.0
        
        # 避免被包围
        if adjacent_opp >= 3:
            score -= 2.0
        
        return score
    
    def select_move(self, board: GoBoard) -> Optional[Point]:
        """
        选择最佳落子位置
        """
        valid_moves = board.get_valid_moves()
        
        if not valid_moves:
            return None
        
        # 评估所有合法落子
        best_move = None
        best_score = float('-inf')
        
        for p in valid_moves:
            score = self.evaluate_move(board, p)
            if score > best_score:
                best_score = score
                best_move = p
        
        return best_move
    
    def should_pass(self, board: GoBoard) -> bool:
        """
        判断是否应该 pass
        """
        # 简单策略：总是落子，不 pass
        return False


if __name__ == '__main__':
    from engine.board import GoBoard, Point, StoneColor
    
    board = GoBoard(9)
    strategy = SimpleStrategy(StoneColor.BLACK)
    
    print("=== 简单策略测试 ===")
    print(board.display())
    
    # 测试评估
    p = Point.from_gtp("D4")
    score = strategy.evaluate_move(board, p)
    print(f"\nD4 评分: {score:.2f}")
    
    # 选择落子
    move = strategy.select_move(board)
    if move:
        print(f"选择落子: {move.to_gtp()}")
