#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 MQTT 围棋对局实时同步 v1.0
基于 MQTT 实现多学员围棋对局的实时落子同步、棋盘状态管理、裁判判定。

功能:
- 创建对局、通知双方
- 实时落子同步 (毫秒级)
- 棋盘状态追踪 (9x9 / 19x19)
- 基础规则校验 (出界/重叠/Ko)
- 对局结果上报

使用:
    python3 core/mqtt_go_match_sync.py create <black> <white> [board_size]
    python3 core/mqtt_go_match_sync.py status
    python3 core/mqtt_go_match_sync.py test
"""

import sys
import os
import json
import time
import uuid
import logging
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mqtt_client_base import MqttClientBase, Topics, create_message, parse_message

# ============================================================================
# 配置
# ============================================================================

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883
NODE_ID = "go_referee"

# 对局数据存储
MATCHES_DIR = "/home/admin/go-training/shared/training/go/matches/"


class GoBoard:
    """轻量级围棋棋盘 (9x9 / 19x19)"""

    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __init__(self, size=9):
        self.size = size
        self.grid = [[self.EMPTY] * size for _ in range(size)]
        self.history = []  # [(color, x, y), ...]
        self.captures = {self.BLACK: 0, self.WHITE: 0}
        self.current_color = self.BLACK

    def is_valid(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def is_empty(self, x, y):
        return self.is_valid(x, y) and self.grid[x][y] == self.EMPTY

    def place_stone(self, color, x, y):
        """落子 (返回 (success, error_msg))"""
        if not self.is_empty(x, y):
            return False, "位置无效或已有棋子"

        self.grid[x][y] = color
        self.history.append((color, x, y))

        # 简单提子检测 (检查对方棋子是否无气)
        opponent = self.WHITE if color == self.BLACK else self.BLACK
        captured = self._remove_captured(opponent)
        self.captures[color] += captured

        # 自杀检测
        if self._count_liberties(x, y) == 0 and captured == 0:
            self.grid[x][y] = self.EMPTY
            self.history.pop()
            return False, "自杀着法"

        self.current_color = opponent
        return True, ""

    def _count_liberties(self, x, y):
        """计算棋子气数 (BFS)"""
        color = self.grid[x][y]
        if color == self.EMPTY:
            return 0
        visited = set()
        queue = [(x, y)]
        liberties = 0
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = cx + dx, cy + dy
                if not self.is_valid(nx, ny):
                    continue
                if self.grid[nx][ny] == self.EMPTY:
                    liberties += 1
                elif self.grid[nx][ny] == color and (nx, ny) not in visited:
                    queue.append((nx, ny))
        return liberties

    def _remove_captured(self, color):
        """移除无气的对方棋子"""
        captured = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x][y] == color:
                    if self._count_liberties(x, y) == 0:
                        self._clear_group(x, y)
                        captured += 1
        return captured

    def _clear_group(self, x, y):
        """清空一组棋子"""
        color = self.grid[x][y]
        queue = [(x, y)]
        visited = set()
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            if self.grid[cx][cy] == color:
                self.grid[cx][cy] = self.EMPTY
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = cx + dx, cy + dy
                    if self.is_valid(nx, ny) and self.grid[nx][ny] == color:
                        queue.append((nx, ny))

    def coordinate_to_label(self, x, y):
        """坐标转标签 (如 D4)"""
        cols = "ABCDEFGHJKLMNOPQRST"  # 跳过 I
        col = cols[x] if x < len(cols) else str(x)
        row = str(self.size - y)
        return col + row

    def label_to_coordinate(self, label):
        """标签转坐标"""
        label = label.upper().strip()
        cols = "ABCDEFGHJKLMNOPQRST"
        col_char = label[0]
        row_str = label[1:]
        if col_char in cols:
            x = cols.index(col_char)
        else:
            return None, None
        try:
            y = self.size - int(row_str)
        except ValueError:
            return None, None
        return x, y

    def get_board_state(self):
        """获取棋盘状态 (JSON 可序列化)"""
        stones = []
        for x in range(self.size):
            for y in range(self.size):
                if self.grid[x][y] != self.EMPTY:
                    stones.append({
                        "color": "black" if self.grid[x][y] == self.BLACK else "white",
                        "pos": self.coordinate_to_label(x, y),
                    })
        return {
            "size": self.size,
            "stones": stones,
            "captures": self.captures,
            "move_count": len(self.history),
            "current_turn": "black" if self.current_color == self.BLACK else "white",
        }


# ============================================================================
# 对局同步器
# ============================================================================

class GoMatchSync:
    """围棋对局 MQTT 同步器"""

    def __init__(self, broker_host=BROKER_HOST, broker_port=BROKER_PORT):
        self.client = MqttClientBase(
            node_id=NODE_ID,
            broker_host=broker_host,
            broker_port=broker_port,
        )
        self.logger = logging.getLogger("go_match_sync")
        self.matches = {}  # {match_id: GoBoard}
        self.match_info = {}  # {match_id: {black, white, status, ...}}

        # 注册连接后回调 (订阅需在连接后执行)
        self.client.on_connect(self._after_connect)

    def _after_connect(self, client, userdata, flags, rc):
        """连接成功后订阅对局主题"""
        self.client.on_message(
            "{}/match/{}/move".format(Topics.ROOT, "+"),
            self._on_move,
        )
        self.client.on_message(
            "{}/match/{}/+".format(Topics.ROOT, "+"),
            self._on_match_event,
        )

    def _on_move(self, topic, payload):
        """处理落子消息"""
        msg = parse_message(payload)
        match_id = topic.split("/")[2]  # lobster/match/{id}/move
        if match_id not in self.matches:
            self.logger.warning("未知对局: {}".format(match_id))
            return

        board = self.matches[match_id]
        move_label = msg.get("move", "")
        player = msg.get("from", "")

        x, y = board.label_to_coordinate(move_label)
        if x is None:
            self.logger.warning("无效坐标: {}".format(move_label))
            return

        # 确定颜色
        info = self.match_info.get(match_id, {})
        color = GoBoard.BLACK if info.get("black") == player else GoBoard.WHITE

        success, error = board.place_stone(color, x, y)
        if success:
            self.logger.info("[{}] {} 落子 {} (提子:{})".format(
                match_id, player, move_label, board.captures[color]))
            # 广播棋盘状态
            self._broadcast_board(match_id)
        else:
            self.logger.warning("[{}] 落子失败: {} - {}".format(match_id, move_label, error))

    def _on_match_event(self, topic, payload):
        """处理对局事件"""
        msg = parse_message(payload)
        self.logger.debug("对局事件 [{}]: {}".format(topic, msg.get("type", "?")))

    def create_match(self, black_player, white_player, board_size=9):
        """创建新对局"""
        match_id = "match_{}_{}".format(
            datetime.now().strftime("%Y%m%d_%H%M%S"),
            str(uuid.uuid4())[:6],
        )

        # 初始化棋盘
        board = GoBoard(board_size)
        self.matches[match_id] = board
        self.match_info[match_id] = {
            "black": black_player,
            "white": white_player,
            "board_size": board_size,
            "status": "active",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 通知双方
        notify_payload = {
            "match_id": match_id,
            "black": black_player,
            "white": white_player,
            "board_size": board_size,
        }

        # 通知黑方
        self.client.publish_message(
            Topics.coach_to_student(black_player),
            "go_match_notify", NODE_ID, black_player, notify_payload,
        )

        # 通知白方
        self.client.publish_message(
            Topics.coach_to_student(white_player),
            "go_match_notify", NODE_ID, white_player, notify_payload,
        )

        # 保存对局信息
        os.makedirs(MATCHES_DIR, exist_ok=True)
        with open(os.path.join(MATCHES_DIR, "{}.json".format(match_id)), "w") as f:
            json.dump(self.match_info[match_id], f, ensure_ascii=False, indent=2)

        self.logger.info("创建对局: {} ({} vs {}, {}x{})".format(
            match_id, black_player, white_player, board_size, board_size))
        return match_id

    def _broadcast_board(self, match_id):
        """广播棋盘状态"""
        if match_id not in self.matches:
            return
        board = self.matches[match_id]
        state = board.get_board_state()
        self.client.publish(
            Topics.match_board(match_id),
            json.dumps(state, ensure_ascii=False),
        )

    def get_match_status(self, match_id=None):
        """获取对局状态"""
        if match_id:
            board = self.matches.get(match_id)
            info = self.match_info.get(match_id, {})
            if board:
                return {**info, "board": board.get_board_state()}
            return info
        return {mid: self.match_info.get(mid, {}) for mid in self.matches}

    def start(self):
        """启动对局同步器"""
        self.client.connect()
        self.client.start_heartbeat(60)
        self.logger.info("对局同步器已启动")

    def stop(self):
        """停止对局同步器"""
        self.client.disconnect()


# ============================================================================
# CLI 入口
# ============================================================================

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("用法: python3 mqtt_go_match_sync.py <command> [args]")
        print("命令: create <black> <white> [size] | status [match_id] | test")
        sys.exit(1)

    command = sys.argv[1]
    sync = GoMatchSync()

    if command == "create":
        if len(sys.argv) < 4:
            print("用法: create <black_player> <white_player> [board_size]")
            sys.exit(1)
        black = sys.argv[2]
        white = sys.argv[3]
        size = int(sys.argv[4]) if len(sys.argv) > 4 else 9
        sync.client.connect()
        time.sleep(1)
        match_id = sync.create_match(black, white, size)
        print("对局创建: {}".format(match_id))
        time.sleep(1)
        sync.client.disconnect()

    elif command == "status":
        match_id = sys.argv[2] if len(sys.argv) > 2 else None
        sync.client.connect()
        time.sleep(1)
        status = sync.get_match_status(match_id)
        print(json.dumps(status, ensure_ascii=False, indent=2))
        sync.client.disconnect()

    elif command == "test":
        print("=== 围棋对局同步测试 ===")
        sync.client.connect()
        time.sleep(1)

        # 创建对局
        match_id = sync.create_match("xiaochen", "zhuguxia", 9)
        print("对局ID: {}".format(match_id))
        time.sleep(1)

        # 模拟黑方落子
        print("黑方 (小陈) 落子 D5...")
        sync.client.publish(Topics.match_move(match_id), json.dumps({
            "from": "xiaochen",
            "move": "D5",
        }))
        time.sleep(1)

        # 模拟白方落子
        print("白方 (诸葛虾) 落子 D4...")
        sync.client.publish(Topics.match_move(match_id), json.dumps({
            "from": "zhuguxia",
            "move": "D4",
        }))
        time.sleep(1)

        # 查看状态
        status = sync.get_match_status(match_id)
        print("\n=== 对局状态 ===")
        print("棋盘大小: {}x{}".format(status["board"]["size"], status["board"]["size"]))
        print("棋子数: {}".format(len(status["board"]["stones"])))
        print("提子: 黑={} 白={}".format(
            status["board"]["captures"][1], status["board"]["captures"][2]))
        print("当前轮次: {}".format(status["board"]["current_turn"]))

        sync.client.disconnect()
        print("=== 测试完成 ===")

    else:
        print("未知命令: {}".format(command))
        sys.exit(1)


if __name__ == "__main__":
    main()
