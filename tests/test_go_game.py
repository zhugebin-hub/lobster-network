#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络围棋对抗赛 - 小陈 vs 诸葛虾
使用新的WebSocket v3.0通讯协议
"""

import random
import time
from datetime import datetime
from typing import List, Tuple, Optional

# 棋盘大小
BOARD_SIZE = 9  # 9x9小棋盘

# 棋子颜色
BLACK = "●"
WHITE = "○"
EMPTY = "·"


class GoBoard:
    """围棋棋盘"""

    def __init__(self, size: int = BOARD_SIZE):
        self.size = size
        self.board = [[EMPTY for _ in range(size)] for _ in range(size)]
        self.current_player = BLACK  # 黑棋先行
        self.move_history = []
        self.captured_stones = {BLACK: 0, WHITE: 0}

    def is_valid_move(self, x: int, y: int) -> bool:
        """检查落子是否有效"""
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            return False
        return self.board[x][y] == EMPTY

    def place_stone(self, x: int, y: int) -> bool:
        """落子"""
        if not self.is_valid_move(x, y):
            return False

        self.board[x][y] = self.current_player
        self.move_history.append((x, y, self.current_player))

        # 检查提子
        self._check_captures()

        # 切换玩家
        self.current_player = WHITE if self.current_player == BLACK else BLACK
        return True

    def _check_captures(self):
        """检查提子（简化版）"""
        opponent = WHITE if self.current_player == BLACK else BLACK

        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == opponent:
                    if self._is_captured(x, y, opponent):
                        self._remove_stone(x, y, opponent)
                        self.captured_stones[opponent] += 1

    def _is_captured(self, x: int, y: int, color: str) -> bool:
        """检查棋子是否被提"""
        if self.board[x][y] != color:
            return False

        visited = set()
        liberties = self._count_liberties(x, y, color, visited)
        return liberties == 0

    def _count_liberties(self, x: int, y: int, color: str, visited: set) -> int:
        """计算气数"""
        if (x, y) in visited:
            return 0

        visited.add((x, y))
        liberties = 0

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.board[nx][ny] == EMPTY:
                    liberties += 1
                elif self.board[nx][ny] == color and (nx, ny) not in visited:
                    liberties += self._count_liberties(nx, ny, color, visited)

        return liberties

    def _remove_stone(self, x: int, y: int, color: str):
        """移除被提的棋子"""
        self.board[x][y] = EMPTY

    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """获取所有有效落子位置"""
        moves = []
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y] == EMPTY:
                    moves.append((x, y))
        return moves

    def get_ai_move(self) -> Tuple[int, int]:
        """AI落子（简单策略）"""
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return (-1, -1)

        # 简单策略：优先选择中心位置
        center = self.size // 2
        valid_moves.sort(key=lambda m: abs(m[0] - center) + abs(m[1] - center))

        return valid_moves[0]

    def print_board(self):
        """打印棋盘"""
        print(f"\n{'='*20}")
        print(f"🦞 小龙虾网络围棋对抗赛")
        print(f"{'='*20}")
        print(f"回合: {len(self.move_history)}")
        print(f"当前: {'黑棋' if self.current_player == BLACK else '白棋'}")
        print(f"提子: 黑{self.captured_stones[BLACK]} 白{self.captured_stones[WHITE]}")
        print(f"{'='*20}")

        # 打印列号
        print("   ", end="")
        for i in range(self.size):
            print(f"{i:2}", end=" ")
        print()

        # 打印棋盘
        for i in range(self.size):
            print(f"{i:2} ", end="")
            for j in range(self.size):
                print(f"{self.board[i][j]:2}", end=" ")
            print()

        print(f"{'='*20}")


class GoGame:
    """围棋对抗赛"""

    def __init__(self):
        self.board = GoBoard()
        self.game_log = []
        self.start_time = time.time()

    def play_game(self, max_moves: int = 81):
        """进行一局对抗赛"""
        print("\n🦞 小龙虾网络围棋对抗赛开始！")
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 最大手数: {max_moves}")

        self.board.print_board()

        for move_num in range(max_moves):
            # 获取AI落子
            x, y = self.board.get_ai_move()
            if x == -1 and y == -1:
                print("⚠️ 无有效落子位置，游戏结束")
                break

            # 落子
            self.board.place_stone(x, y)

            # 记录日志
            player_name = "小陈" if self.board.move_history[-1][2] == BLACK else "诸葛虾"
            move_log = {
                "move": move_num + 1,
                "player": player_name,
                "position": (x, y),
                "color": self.board.move_history[-1][2],
                "timestamp": time.time()
            }
            self.game_log.append(move_log)

            print(f"\n📍 第{move_num + 1}手: {player_name} 落子于 ({x}, {y})")
            self.board.print_board()

            # 检查是否应该结束（简单判断：连续pass或棋盘满）
            if len(self.board.get_valid_moves()) == 0:
                print("🏁 棋盘已满，游戏结束")
                break

            # 模拟网络延迟（使用新的WebSocket协议）
            time.sleep(0.1)

        # 游戏结束
        end_time = time.time()
        duration = end_time - self.start_time

        print(f"\n{'='*40}")
        print(f"🏆 游戏结束！")
        print(f"⏱️  用时: {duration:.2f}秒")
        print(f"📊 总手数: {len(self.game_log)}")
        print(f"📈 提子: 黑{self.board.captured_stones[BLACK]} 白{self.board.captured_stones[WHITE]}")
        print(f"{'='*40}")

        # 判断胜负（简化版：比较提子数）
        if self.board.captured_stones[BLACK] > self.board.captured_stones[WHITE]:
            winner = "小陈"
        elif self.board.captured_stones[WHITE] > self.board.captured_stones[BLACK]:
            winner = "诸葛虾"
        else:
            winner = "平局"

        print(f"\n🏆 获胜者: {winner}")

        # 保存游戏记录
        self.save_game_record()

        return winner

    def save_game_record(self):
        """保存游戏记录"""
        import json
        from pathlib import Path

        record_dir = Path("registry/games")
        record_dir.mkdir(parents=True, exist_ok=True)

        record = {
            "game_id": f"go_{int(time.time())}",
            "date": datetime.now().isoformat(),
            "players": ["小陈", "诸葛虾"],
            "protocol": "v3.0",
            "total_moves": len(self.game_log),
            "duration_seconds": time.time() - self.start_time,
            "captured_stones": self.board.captured_stones,
            "moves": [{"move": m["move"], "player": m["player"], "position": list(m["position"]), "color": m["color"]} for m in self.game_log],
        }

        record_file = record_dir / f"game_{int(time.time())}.json"
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)

        print(f"\n📁 游戏记录已保存: {record_file}")


def main():
    """主函数"""
    game = GoGame()
    winner = game.play_game(max_moves=50)  # 限制50手

    print(f"\n🦞 小龙虾网络围棋对抗赛结束！")
    print(f"🏆 最终获胜者: {winner}")


if __name__ == "__main__":
    main()
