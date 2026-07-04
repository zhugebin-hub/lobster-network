#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对局选手模块 (Go Match Player)
===============================
让 xiaochen / zhuguxia / qoder 的训练器能真正参与对弈：
- 读取当前盘面（通过 go_match_engine）
- 基于学员水平做落子决策（调用各 trainer 策略）
- 落子理由生成
- 错误处理（认输、超时）
"""

import os
import sys
import json
import random
import time
from datetime import datetime
from typing import Optional, Tuple, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.engine.go_match_engine import get_engine, GoMatchEngine, COL_LETTERS


class GoMatchPlayer:
    """
    对局选手 — 封装学员的落子决策逻辑

    策略层级（模拟不同水平的棋力）：
    - 入门 (beginner)  : 随机合法落子，偶尔打出坏手
    - 初级 (elementary): 优先占空角 → 占边 → 随机，坏手率低
    - 中级 (intermediate): 角→边→中腹顺序，带基本征子意识
    - 高级 (advanced)  : 角→边→中腹，偶尔手筋感，低坏手率
    """

    LEVEL_ORDER = {"入门": 0, "初级": 1, "中级": 2, "高级": 3,
                   "30级": 0, "20级": 0, "10级": 1, "1级": 2, "初段": 3}

    # 各水平参数
    LEVEL_PARAMS = {
        "入门": {"blunder_rate": 0.30, "think_time": (0.8, 1.5), "strategy": "random"},
        "初级": {"blunder_rate": 0.15, "think_time": (0.5, 1.2), "strategy": "corner_edge"},
        "中级": {"blunder_rate": 0.08, "think_time": (0.3, 0.8), "strategy": "corner_edge_center"},
        "高级": {"blunder_rate": 0.03, "think_time": (0.2, 0.5), "strategy": "advanced"},
    }

    def __init__(self, player_id: str, level: str = "初级",
                 player_type: str = "稳健型",
                 engine: GoMatchEngine = None):
        """
        参数:
            player_id: 学员标识 (xiaochen/zhuguxia/qoder)
            level: 棋力等级 (入门/初级/中级/高级)
            player_type: 学员类型 (稳健型/加速型/实战型)
            engine: 对局引擎实例，不传使用全局单例
        """
        self.player_id = player_id
        self.level = level
        self.player_type = player_type
        self.engine = engine or get_engine()

        # 从等级解析参数
        params = self.LEVEL_PARAMS.get(level, self.LEVEL_PARAMS["初级"])
        self.blunder_rate = params["blunder_rate"]
        self.think_time = params["think_time"]
        self.strategy = params["strategy"]

        # 胜负记录
        self.games_played = 0
        self.wins = 0
        self.losses = 0
        self.current_match_id: Optional[str] = None

    def decide_move(self, match_id: str) -> dict:
        """
        对当前盘面做出落子决策。

        返回:
            {
                "coord": "Q4" | "pass" | "resign",
                "thinking_time": 0.5,
                "reason": "占空角（星位）",
                "valid": bool,
            }
        """
        self.current_match_id = match_id
        board_info = self.engine.get_board(match_id)

        if "error" in board_info:
            return {"coord": "pass", "thinking_time": 0, "reason": "盘面读取失败", "valid": False}

        if board_info["status"] != "playing":
            return {"coord": "pass", "thinking_time": 0, "reason": "对局已结束", "valid": False}

        # 模拟思考时间
        t = random.uniform(*self.think_time)
        time.sleep(min(t, 0.3))  # 上限 300ms，防止测试太慢

        # 判断是否超时认输
        my_time_used = (board_info.get("black_time_used", 0)
                        if board_info["current_player"] == board_info.get("black_id")
                        else board_info.get("white_time_used", 0))
        if my_time_used > 10 * 60:  # 10 分钟超时
            return {"coord": "resign", "thinking_time": t, "reason": "超时认输", "valid": True}

        # 偶尔打出坏手
        if random.random() < self.blunder_rate and board_info["move_number"] > 4:
            prob = random.random()
            if prob < 0.4:
                return {"coord": "pass", "thinking_time": t, "reason": "判断失误，选择虚手", "valid": True}
            elif prob < 0.7:
                return {"coord": "resign", "thinking_time": t, "reason": "心态崩溃，选择认输", "valid": True}

        # 按策略选点
        move = self._select_move(board_info)
        return move

    def _select_move(self, board_info: dict) -> dict:
        """根据策略选择落子位置"""
        board_size = board_info["board_size"]

        if self.strategy == "random":
            return self._random_move(board_info)

        elif self.strategy in ("corner_edge", "corner_edge_center", "advanced"):
            # 优先占空角
            corners = [(0, 0), (0, board_size - 1),
                       (board_size - 1, 0), (board_size - 1, board_size - 1)]
            # 星位常见落子
            star_points = self._get_star_points(board_size)
            # 检查是否在开局阶段
            if board_info["move_number"] < 8:
                # 优先选空角
                empty_corners = [c for c in star_points if self._is_empty(board_info, c)]
                if empty_corners:
                    pick = random.choice(empty_corners)
                    return self._format_move(pick, "占角位")

            # 中盘阶段 — 找边缘空位
            candidates = self._get_empty_positions(board_info)
            if not candidates:
                return {"coord": "pass", "thinking_time": random.uniform(*self.think_time),
                        "reason": "无合法位置", "valid": True}

            # 按距离中心排序（角 > 边 > 中心）
            center = board_size / 2
            scored = []
            for (r, c) in candidates:
                dist_corner = min(r, board_size - 1 - r, c, board_size - 1 - c)
                dist_center = abs(r - center) + abs(c - center)
                # 优先级：角区 > 边区 > 中腹
                if dist_corner <= 3:
                    score = 100 - dist_corner
                elif dist_corner <= 6:
                    score = 50 - dist_corner
                else:
                    score = 10
                score += random.uniform(0, 5)
                if self.strategy == "advanced":
                    # 高级策略加一点手筋感（相邻已有己方棋子加权）
                    score += self._adjacency_bonus(board_info, r, c)
                scored.append((score, r, c))

            scored.sort(key=lambda x: -x[0])
            pick = scored[0]
            return self._format_move((pick[1], pick[2]),
                                     f"中盘选点 (score={pick[0]:.1f})")

    def _random_move(self, board_info: dict) -> dict:
        """随机合法落子"""
        candidates = self._get_empty_positions(board_info)
        if not candidates:
            return {"coord": "pass", "thinking_time": random.uniform(*self.think_time),
                    "reason": "无合法位置", "valid": True}
        pick = random.choice(candidates)
        return self._format_move(pick, "随机选点")

    def _get_star_points(self, board_size: int) -> List[Tuple[int, int]]:
        """返回星位列表"""
        if board_size == 19:
            return [(3, 3), (3, 9), (3, 15),
                    (9, 3), (9, 9), (9, 15),
                    (15, 3), (15, 9), (15, 15)]
        elif board_size == 9:
            return [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]
        else:
            return [(3, 3), (3, board_size - 4),
                    (board_size - 4, 3), (board_size - 4, board_size - 4),
                    (board_size // 2, board_size // 2)]

    def _is_empty(self, board_info: dict, pos: Tuple[int, int]) -> bool:
        """检查指定位置是否为空"""
        r, c = pos
        board = self._get_board_array(board_info)
        return board[r][c] == 0

    def _get_empty_positions(self, board_info: dict) -> List[Tuple[int, int]]:
        """获取所有空位"""
        board = self._get_board_array(board_info)
        size = board_info["board_size"]
        return [(r, c) for r in range(size) for c in range(size) if board[r][c] == 0]

    def _get_board_array(self, board_info: dict) -> list:
        """从 board_info 提取二维数组"""
        # board_info 可能包含 "board" 字段，也可能是从 engine state 来的
        # 如果 board_info 没有直接 board，通过 engine 获取
        if "board" in board_info:
            return board_info["board"]
        # reload from engine
        mid = board_info.get("match_id", self.current_match_id)
        if mid:
            state = self.engine._load_match(mid)
            if state:
                return state["board"]
        # fallback: 返回空 19x19
        return [[0] * 19 for _ in range(19)]

    def _adjacency_bonus(self, board_info: dict, r: int, c: int) -> float:
        """计算与已方棋子相邻的加权"""
        board = self._get_board_array(board_info)
        # 确定我方颜色
        my_color = 1  # 简化：通过 match 判断
        bonus = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                if board[nr][nc] == my_color:
                    bonus += 3
                elif board[nr][nc] != 0:
                    bonus += 1  # 靠近对手也加分（战斗）
        return bonus

    def _format_move(self, pos: Tuple[int, int], reason: str) -> dict:
        r, c = pos
        coord = f"{COL_LETTERS[c]}{r + 1}"
        return {
            "coord": coord,
            "thinking_time": random.uniform(*self.think_time),
            "reason": reason,
            "valid": True,
        }

    def record_result(self, won: bool):
        """记录对局结果"""
        self.games_played += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1

    @property
    def win_rate(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

    def summary(self) -> dict:
        return {
            "player_id": self.player_id,
            "level": self.level,
            "strategy": self.strategy,
            "games": self.games_played,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": round(self.win_rate, 3),
        }


# ====== 工厂 ======

def create_player(player_id: str) -> GoMatchPlayer:
    """
    根据学员 ID 创建匹配的对局选手。

    等级映射:
        xiaochen  → 中级 (1级)
        zhuguxia → 高级 (初段)
        qoder     → 中级 (实战型)
    """
    mapping = {
        "xiaochen": ("中级", "稳健型"),
        "zhuguxia": ("高级", "加速型"),
        "qoder": ("中级", "实战型"),
    }
    level, ptype = mapping.get(player_id, ("初级", "稳健型"))
    return GoMatchPlayer(player_id=player_id, level=level, player_type=ptype)


# ====== 快速测试 ======
if __name__ == "__main__":
    engine = get_engine()
    result = engine.start_match("xiaochen", "zhuguxia")
    mid = result["match_id"]

    player_black = create_player("xiaochen")
    player_white = create_player("zhuguxia")

    for i in range(20):
        board_info = engine.get_board(mid)
        if board_info.get("status") != "playing":
            break
        cp = board_info["current_player"]
        p = player_black if cp == board_info["black_id"] else player_white
        move = p.decide_move(mid)
        if move["coord"] == "resign":
            print(f"{p.player_id} 认输!")
            engine.resign(mid, p.player_id)
            break
        r = engine.submit_move(mid, p.player_id, move["coord"])
        if not r["valid"]:
            print(f"  Invalid: {r['message']}, trying pass")
            engine.submit_move(mid, p.player_id, "pass")
        else:
            print(f"  {p.player_id}({p.level}) → {move['coord']} [{move['reason']}]")

    print(engine.render_board(mid))
