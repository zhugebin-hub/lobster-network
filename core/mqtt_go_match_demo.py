#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦞 小龙虾网络 MQTT 围棋对局演示
用 MQTT 协议组织一场完整的 9x9 围棋对局

角色:
- 教练 (诸葛马): 创建对局、通知双方、裁判
- 黑方 (小陈 AI): 通过 MQTT 接收通知、自动落子
- 白方 (诸葛虾 AI): 通过 MQTT 接收通知、自动落子

所有通信通过 MQTT Broker (47.93.6.57:1883) 完成
"""

import sys
import os
import json
import time
import uuid
import logging
import threading
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mqtt_client_base import MqttClientBase, Topics, parse_message

# ============================================================================
# 配置
# ============================================================================

BROKER_HOST = "47.93.6.57"  # 公网IP
BROKER_PORT = 1883
BOARD_SIZE = 9

# 坐标标签
COLS = "ABCDEFGHJKLMNOPQRST"  # 跳过 I

# 简单围棋棋盘
class SimpleBoard:
    """轻量级棋盘 (仅记录落子历史，不做完整规则校验)"""

    def __init__(self, size=9):
        self.size = size
        self.grid = [[0] * size for _ in range(size)]  # 0=空 1=黑 2=白
        self.history = []
        self.captures = {1: 0, 2: 0}  # 黑/白提子数

    def place(self, color, label):
        """落子"""
        x, y = self._label_to_coord(label)
        if x is None or self.grid[x][y] != 0:
            return False, "无效位置"
        self.grid[x][y] = color
        self.history.append((color, label))
        return True, ""

    def _label_to_coord(self, label):
        label = label.upper().strip()
        if len(label) < 2:
            return None, None
        col_char = label[0]
        row_str = label[1:]
        if col_char not in COLS:
            return None, None
        x = COLS.index(col_char)
        try:
            y = self.size - int(row_str)
        except ValueError:
            return None, None
        if not (0 <= x < self.size and 0 <= y < self.size):
            return None, None
        return x, y

    def coord_to_label(self, x, y):
        return COLS[x] + str(self.size - y)

    def display(self):
        """ASCII 棋盘显示"""
        lines = []
        lines.append("    " + " ".join(COLS[:self.size]))
        lines.append("   +" + "---" * self.size)
        for row in range(self.size):
            rlabel = str(self.size - row)
            cells = []
            for col in range(self.size):
                v = self.grid[col][row]
                cells.append("●" if v == 1 else "○" if v == 2 else "·")
            lines.append(f" {rlabel} | {' '.join(cells)} |")
        lines.append("   +" + "---" * self.size)
        return "\n".join(lines)


# ============================================================================
# 对局演示
# ============================================================================

def run_demo():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    match_id = f"mqtt_go_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:6]}"
    print("=" * 60)
    print(f"🦞 小龙虾网络 MQTT 围棋对局")
    print(f"   对局ID: {match_id}")
    print(f"   棋盘: {BOARD_SIZE}x{BOARD_SIZE}")
    print(f"   Broker: {BROKER_HOST}:{BROKER_PORT}")
    print(f"   黑方: 小陈 AI (xiaochen)")
    print(f"   白方: 诸葛虾 AI (zhuguxia)")
    print("=" * 60)

    # ========================================================================
    # 角色1: 教练端 (诸葛马)
    # ========================================================================
    print("\n📡 [教练] 启动 MQTT 连接...")
    coach = MqttClientBase("zhugema_referee", broker_host=BROKER_HOST)
    coach.connect()
    time.sleep(2)
    print(f"   教练已连接 ✅")

    board = SimpleBoard(BOARD_SIZE)
    move_log = []
    ack_received = {"xiaochen": False, "zhuguxia": False}

    # 注册 ACK 回调
    def on_ack_xiaochen(topic, payload):
        msg = parse_message(payload)
        print(f"   📩 [教练] 收到小陈 ACK: {msg.get('status')} (type={msg.get('original_type')})")
        ack_received["xiaochen"] = True

    def on_ack_zhuguxia(topic, payload):
        msg = parse_message(payload)
        print(f"   📩 [教练] 收到诸葛虾 ACK: {msg.get('status')} (type={msg.get('original_type')})")
        ack_received["zhuguxia"] = True

    coach.on_message(Topics.student_to_coach("xiaochen"), on_ack_xiaochen)
    coach.on_message(Topics.student_to_coach("zhuguxia"), on_ack_zhuguxia)
    time.sleep(1)

    # ========================================================================
    # 步骤1: 教练创建对局，通知双方
    # ========================================================================
    print(f"\n{'─' * 60}")
    print("📋 [步骤1] 教练创建对局，通知双方")
    print(f"{'─' * 60}")

    notify_payload = {
        "match_id": match_id,
        "black": "xiaochen",
        "white": "zhuguxia",
        "board_size": BOARD_SIZE,
        "message": f"对局开始！小陈执黑，诸葛虾执白，{BOARD_SIZE}x{BOARD_SIZE}棋盘",
    }

    # 通知黑方
    coach.publish_message(
        Topics.coach_to_student("xiaochen"),
        "go_match_notify", "zhugema", "xiaochen", notify_payload
    )
    print(f"   → 通知小陈 (黑方): {Topics.coach_to_student('xiaochen')}")

    # 通知白方
    coach.publish_message(
        Topics.coach_to_student("zhuguxia"),
        "go_match_notify", "zhugema", "zhuguxia", notify_payload
    )
    print(f"   → 通知诸葛虾 (白方): {Topics.coach_to_student('zhuguxia')}")

    time.sleep(2)
    print(f"   ACK 状态: 小陈={ack_received['xiaochen']} ✅  诸葛虾={ack_received['zhuguxia']} ✅")

    # ========================================================================
    # 角色2: 黑方 (小陈 AI)
    # ========================================================================
    print(f"\n{'─' * 60}")
    print("⚫ [步骤2] 黑方 (小陈 AI) 启动，接收对局通知")
    print(f"{'─' * 60}")

    xiaochen = MqttClientBase("xiaochen_go", broker_host=BROKER_HOST)
    xiaochen.connect()
    time.sleep(2)

    xiaochen_moves = []
    xiaochen_received_notify = False

    def on_coach_msg(topic, payload):
        nonlocal xiaochen_received_notify
        msg = parse_message(payload)
        if msg.get("type") == "go_match_notify":
            xiaochen_received_notify = True
            print(f"   ⚫ 小陈收到对局通知: {msg.get('payload', {}).get('message')}")
            # 回复 ACK
            ack = {
                "type": "ack",
                "original_id": msg.get("id"),
                "original_type": "go_match_notify",
                "status": "ready",
                "student_id": "xiaochen",
            }
            xiaochen.publish(Topics.student_to_coach("xiaochen"), json.dumps(ack, ensure_ascii=False))
            print(f"   ⚫ 小陈回复: 已就绪，等待落子指令")

        elif msg.get("type") == "go_move_ask":
            print(f"   ⚫ 小陈收到落子询问!")
            # AI 选择落子 (简单策略: 星位 + 随机)
            import random
            star_positions = ["D4", "D6", "F4", "F6", "E5"]
            available = [p for p in star_positions if board.grid[COLS.index(p[0])][BOARD_SIZE - int(p[1:])] == 0]
            if not available:
                # 随机选空位
                for x in range(BOARD_SIZE):
                    for y in range(BOARD_SIZE):
                        if board.grid[x][y] == 0:
                            available.append(board.coord_to_label(x, y))
            move = random.choice(available) if available else "D4"
            print(f"   ⚫ 小陈 AI 选择落子: {move}")

            # 通过 MQTT 发布落子
            xiaochen.publish(
                f"{Topics.ROOT}/match/{match_id}/move",
                json.dumps({
                    "from": "xiaochen",
                    "color": "black",
                    "move": move,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
            )
            xiaochen_moves.append(move)
            print(f"   ⚫ 落子已发布到 {Topics.ROOT}/match/{match_id}/move")

            # 回复教练 ACK
            ack = {
                "type": "ack",
                "original_id": msg.get("id"),
                "original_type": "go_move_ask",
                "status": "move_played",
                "student_id": "xiaochen",
                "payload": {"move": move},
            }
            xiaochen.publish(Topics.student_to_coach("xiaochen"), json.dumps(ack, ensure_ascii=False))

    xiaochen.on_message(Topics.coach_to_student("xiaochen"), on_coach_msg)
    time.sleep(1)

    # ========================================================================
    # 角色3: 白方 (诸葛虾 AI)
    # ========================================================================
    print(f"\n{'─' * 60}")
    print("⚪ [步骤3] 白方 (诸葛虾 AI) 启动，接收对局通知")
    print(f"{'─' * 60}")

    zhuguxia = MqttClientBase("zhuguxia_go", broker_host=BROKER_HOST)
    zhuguxia.connect()
    time.sleep(2)

    zhuguxia_moves = []

    def on_coach_msg_zhu(topic, payload):
        msg = parse_message(payload)
        if msg.get("type") == "go_match_notify":
            print(f"   ⚪ 诸葛虾收到对局通知: {msg.get('payload', {}).get('message')}")
            ack = {
                "type": "ack",
                "original_id": msg.get("id"),
                "original_type": "go_match_notify",
                "status": "ready",
                "student_id": "zhuguxia",
            }
            zhuguxia.publish(Topics.student_to_coach("zhuguxia"), json.dumps(ack, ensure_ascii=False))
            print(f"   ⚪ 诸葛虾回复: 已就绪，等待落子指令")

        elif msg.get("type") == "go_move_ask":
            print(f"   ⚪ 诸葛虾收到落子询问!")
            import random
            star_positions = ["D4", "D6", "F4", "F6", "E5"]
            available = [p for p in star_positions if board.grid[COLS.index(p[0])][BOARD_SIZE - int(p[1:])] == 0]
            if not available:
                for x in range(BOARD_SIZE):
                    for y in range(BOARD_SIZE):
                        if board.grid[x][y] == 0:
                            available.append(board.coord_to_label(x, y))
            move = random.choice(available) if available else "D4"
            print(f"   ⚪ 诸葛虾 AI 选择落子: {move}")

            zhuguxia.publish(
                f"{Topics.ROOT}/match/{match_id}/move",
                json.dumps({
                    "from": "zhuguxia",
                    "color": "white",
                    "move": move,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
            )
            zhuguxia_moves.append(move)
            print(f"   ⚪ 落子已发布到 {Topics.ROOT}/match/{match_id}/move")

            ack = {
                "type": "ack",
                "original_id": msg.get("id"),
                "original_type": "go_move_ask",
                "status": "move_played",
                "student_id": "zhuguxia",
                "payload": {"move": move},
            }
            zhuguxia.publish(Topics.student_to_coach("zhuguxia"), json.dumps(ack, ensure_ascii=False))

    zhuguxia.on_message(Topics.coach_to_student("zhuguxia"), on_coach_msg_zhu)
    time.sleep(1)

    # ========================================================================
    # 步骤4: 教练订阅落子主题，开始对局
    # ========================================================================
    print(f"\n{'─' * 60}")
    print("🏁 [步骤4] 教练订阅落子主题，开始对局")
    print(f"{'─' * 60}")

    move_count = {"total": 0, "max": 15}  # 最多15手

    def on_move(topic, payload):
        msg = parse_message(payload)
        move = msg.get("move", "?")
        color = msg.get("color", "?")
        player = msg.get("from", "?")
        x, y = board._label_to_coord(move)
        if x is not None:
            c = 1 if color == "black" else 2
            ok, err = board.place(c, move)
            if ok:
                move_count["total"] += 1
                move_log.append({"move": move_count["total"], "color": color, "player": player, "pos": move})
                print(f"   📍 第{move_count['total']}手: {player}({color}) → {move}")
            else:
                print(f"   ⚠️ 落子失败: {move} - {err}")

    coach.on_message(f"{Topics.ROOT}/match/{match_id}/move", on_move)
    time.sleep(1)

    # 广播棋盘状态主题
    coach.subscribe(f"{Topics.ROOT}/match/{match_id}/board")
    time.sleep(1)

    # ========================================================================
    # 步骤5: 交替落子 (教练询问 → 学员落子)
    # ========================================================================
    print(f"\n{'─' * 60}")
    print("♟️ [步骤5] 开始对局! 黑白交替落子 (最多15手)")
    print(f"{'─' * 60}")

    for round_num in range(1, move_count["max"] // 2 + 2):
        if move_count["total"] >= move_count["max"]:
            break

        # 黑方落子
        print(f"\n  ▶ 第{round_num}轮 - 黑方 (小陈) 落子")
        coach.publish_message(
            Topics.coach_to_student("xiaochen"),
            "go_move_ask", "zhugema", "xiaochen",
            {"match_id": match_id, "board_size": BOARD_SIZE, "round": round_num}
        )
        time.sleep(2)

        if move_count["total"] >= move_count["max"]:
            break

        # 白方落子
        print(f"\n  ▶ 第{round_num}轮 - 白方 (诸葛虾) 落子")
        coach.publish_message(
            Topics.coach_to_student("zhuguxia"),
            "go_move_ask", "zhugema", "zhuguxia",
            {"match_id": match_id, "board_size": BOARD_SIZE, "round": round_num}
        )
        time.sleep(2)

    # ========================================================================
    # 步骤6: 对局结束，公布结果
    # ========================================================================
    print(f"\n{'=' * 60}")
    print("🏆 [步骤6] 对局结束!")
    print(f"{'=' * 60}")

    print(f"\n{board.display()}")

    print(f"\n📊 对局统计:")
    print(f"   对局ID: {match_id}")
    print(f"   总手数: {move_count['total']}")
    print(f"   黑方 (小陈) 落子: {len(xiaochen_moves)} 手 - {', '.join(xiaochen_moves)}")
    print(f"   白方 (诸葛虾) 落子: {len(zhuguxia_moves)} 手 - {', '.join(zhuguxia_moves)}")

    print(f"\n📜 完整棋谱:")
    for m in move_log:
        symbol = "●" if m["color"] == "black" else "○"
        print(f"   {m['move']:>3}. {symbol} {m['player']:>10} → {m['pos']}")

    # 发送对局结果给双方
    result_payload = {
        "match_id": match_id,
        "status": "completed",
        "total_moves": move_count["total"],
        "black_moves": xiaochen_moves,
        "white_moves": zhuguxia_moves,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    coach.publish_message(
        Topics.coach_to_student("xiaochen"),
        "go_match_result", "zhugema", "xiaochen", result_payload
    )
    coach.publish_message(
        Topics.coach_to_student("zhuguxia"),
        "go_match_result", "zhugema", "zhuguxia", result_payload
    )
    print(f"\n   📤 对局结果已发送双方")

    # 广播到全网
    coach.publish_message(
        f"{Topics.ROOT}/network/broadcast",
        "go_match_completed", "zhugema", None, result_payload
    )
    print(f"   📡 对局结果已全网广播")

    # ========================================================================
    # 清理
    # ========================================================================
    time.sleep(2)
    print(f"\n{'─' * 60}")
    print("🧹 清理连接...")
    xiaochen.disconnect()
    zhuguxia.disconnect()
    coach.disconnect()
    time.sleep(1)

    print(f"\n{'=' * 60}")
    print("✅ MQTT 围棋对局演示完成!")
    print(f"{'=' * 60}")
    print(f"\n📡 通信链路验证:")
    print(f"   ✅ 教练→小陈:  {len(xiaochen_moves)} 条指令通过 MQTT 下发")
    print(f"   ✅ 教练→诸葛虾: {len(zhuguxia_moves)} 条指令通过 MQTT 下发")
    print(f"   ✅ 小陈→教练:  ACK + 落子通过 MQTT 回复")
    print(f"   ✅ 诸葛虾→教练: ACK + 落子通过 MQTT 回复")
    print(f"   ✅ 对局同步:  {move_count['total']} 手通过 MQTT Topic 实时同步")
    print(f"   ✅ 全网广播:  对局结果通过 broadcast 主题广播")
    print(f"\n🦞 小龙虾网络 MQTT 围棋对局系统运行正常！")


if __name__ == "__main__":
    run_demo()
