#!/usr/bin/env python3
"""
小龙虾网络 MQTT 围棋训练桥接层 v1.0
===================================
连接 MQTT 协议与现有围棋训练系统（文件系统消息队列）。

职责：
  1. 接收 MQTT 训练任务 → 写入文件系统 inbox
  2. 监听文件系统 outbox → 通过 MQTT 发送结果
  3. 接收 MQTT 对局落子 → 同步到 match 文件
  4. 双通道兼容：MQTT 优先，NFS/本地降级

依赖：pip install paho-mqtt
"""

import json
import os
import time
import uuid
import threading
import logging
from typing import Optional, Dict, Callable, List, Any
from pathlib import Path
from datetime import datetime

from lobster_mqtt_core import (
    LobsterMQTTClient, LobsterMessage, MessageType,
    Topic, create_coach_client, create_student_client,
)

logger = logging.getLogger("lobster.mqtt.bridge")

# 文件系统路径（与现有训练系统保持一致）
FS_BASE = "/shared/messages/queue"
FS_TRAINING = "/shared/training/go"


# ==================== 桥接器 ====================

class MQTTGoBridge:
    """
    MQTT ⇄ 文件系统 围棋训练桥接器

    工作模式：
      - MQTT 可用：通过 MQTT 收发，同时同步写入文件系统（双写）
      - MQTT 不可用：回退到纯文件系统模式（兼容旧版）
    """

    def __init__(
        self,
        node_id: str,
        role: str = "agent",
        level: Optional[str] = None,
        broker_host: str = "localhost",
        broker_port: int = 1883,
        fs_base: str = FS_BASE,
        training_dir: str = FS_TRAINING,
    ):
        self.node_id = node_id
        self.role = role
        self.level = level
        self.fs_base = Path(fs_base)
        self.training_dir = Path(training_dir)

        # 文件系统路径
        self.inbox_dir = self.fs_base / node_id / "inbox"
        self.outbox_dir = self.fs_base / node_id / "outbox"
        self.processed_dir = self.fs_base / node_id / "processed"

        # MQTT 客户端
        self.mqtt = create_student_client(
            student_id=node_id,
            level=level or "30级",
            broker_host=broker_host,
            broker_port=broker_port,
        ) if role == "agent" else create_coach_client(
            coach_id=node_id,
            broker_host=broker_host,
            broker_port=broker_port,
        )

        # 状态
        self._running = False
        self._mqtt_available = False
        self._threads: List[threading.Thread] = []

        # 注册 MQTT 消息处理
        self._register_handlers()

    def _register_handlers(self):
        """注册 MQTT → 文件系统的消息转发"""

        @self.mqtt.on(MessageType.TRAINING_TASK)
        def handle_training_task(msg: LobsterMessage):
            """MQTT 训练任务 → 写入 inbox"""
            task_file = self.inbox_dir / f"{msg.msg_id}.json"
            self.inbox_dir.mkdir(parents=True, exist_ok=True)
            task_data = {
                "task_id": msg.payload.get("task_id", msg.msg_id),
                "type": "training_task",
                "task": msg.payload,
                "from": msg.from_node,
                "timestamp": msg.timestamp,
                "source": "mqtt",
            }
            with open(task_file, "w") as f:
                json.dump(task_data, f, ensure_ascii=False, indent=2)
            logger.info(f"🦞 [{self.node_id}] MQTT→inbox: {task_file.name}")

        @self.mqtt.on(MessageType.ANNOUNCE)
        def handle_announce(msg: LobsterMessage):
            """系统公告 → 写入公告文件"""
            announce_dir = self.training_dir / "announcements"
            announce_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            announce_file = announce_dir / f"mqtt_announce_{ts}.json"
            with open(announce_file, "w") as f:
                json.dump({
                    "from": msg.from_node,
                    "message": msg.payload.get("message", ""),
                    "timestamp": msg.timestamp,
                    "source": "mqtt",
                }, f, ensure_ascii=False, indent=2)

        @self.mqtt.on(MessageType.MATCH_MOVE)
        def handle_match_move(msg: LobsterMessage):
            """对局落子 → 同步到 match 文件"""
            match_id = msg.payload.get("match_id", "unknown")
            match_dir = Path(FS_TRAINING) / "matches"
            match_dir.mkdir(parents=True, exist_ok=True)
            match_file = match_dir / f"{match_id}.json"

            # 读取或创建对局文件
            if match_file.exists():
                with open(match_file) as f:
                    match_data = json.load(f)
            else:
                match_data = {
                    "game_id": match_id,
                    "status": "in_progress",
                    "moves": [],
                    "created_at": msg.timestamp,
                }

            move_num = len(match_data.get("moves", [])) + 1
            match_data.setdefault("moves", []).append({
                "move": move_num,
                "player": msg.payload.get("player"),
                "color": msg.payload.get("color", "black"),
                "coord": msg.payload.get("coord"),
                "reason": msg.payload.get("reason", ""),
                "timestamp": msg.timestamp,
                "source": "mqtt",
            })
            match_data["last_move"] = msg.timestamp

            with open(match_file, "w") as f:
                json.dump(match_data, f, ensure_ascii=False, indent=2)

    # ==================== 公开 API ====================

    def start(self) -> bool:
        """启动桥接（连接 MQTT + 启动文件监听）"""
        self._running = True

        # 尝试连接 MQTT
        try:
            self._mqtt_available = self.mqtt.connect()
        except Exception as e:
            logger.warning(f"🦞 [{self.node_id}] MQTT 不可用: {e}，将使用纯文件系统模式")
            self._mqtt_available = False

        if self._mqtt_available:
            self.mqtt.subscribe_all()
            self.mqtt.start_heartbeat(interval=30)

        # 启动 outbox 监听线程
        t = threading.Thread(
            target=self._watch_outbox,
            daemon=True,
            name=f"outbox-watcher-{self.node_id}",
        )
        t.start()
        self._threads.append(t)

        logger.info(f"🦞 [{self.node_id}] 桥接器已启动 (MQTT={'✓' if self._mqtt_available else '✗'})")
        return True

    def stop(self):
        """停止桥接"""
        self._running = False
        if self._mqtt_available:
            self.mqtt.disconnect()
        logger.info(f"🦞 [{self.node_id}] 桥接器已停止")

    def send_training_result(
        self,
        to_node: str,
        task_id: str,
        result: dict,
    ) -> Optional[str]:
        """
        发送训练结果（双写：MQTT + 文件系统）

        Args:
            to_node: 教练节点 ID
            task_id: 任务 ID
            result: 结果数据（solved, correct, accuracy, summary 等）

        Returns:
            msg_id，仅 MQTT 模式
        """
        payload = {
            "task_id": task_id,
            **result,
        }

        msg_id = None
        if self._mqtt_available:
            msg_id = self.mqtt.publish_training_result(to_node, payload)

        # 同时写入 outbox（兼容文件系统）
        outbox_file = self.outbox_dir / f"result_{task_id}.json"
        self.outbox_dir.mkdir(parents=True, exist_ok=True)
        outbox_data = {
            "task_id": task_id,
            "type": "training_result",
            "result": payload,
            "to": to_node,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "mqtt_msg_id": msg_id,
        }
        with open(outbox_file, "w") as f:
            json.dump(outbox_data, f, ensure_ascii=False, indent=2)

        return msg_id

    def send_match_move(
        self,
        match_id: str,
        to_node: str,
        coord: str,
        color: str,
        reason: str = "",
    ) -> Optional[str]:
        """
        发送落子（双写：MQTT + 文件系统）

        Args:
            match_id: 对局 ID
            to_node: 对手节点 ID
            coord: 坐标（如 Q16）
            color: 颜色 (black/white)
            reason: 落子理由

        Returns:
            msg_id
        """
        payload = {
            "match_id": match_id,
            "player": self.node_id,
            "color": color,
            "coord": coord,
            "reason": reason,
        }

        msg_id = None
        if self._mqtt_available:
            msg_id = self.mqtt.publish_match_move(match_id, to_node, payload)

        return msg_id

    def get_pending_tasks(self) -> List[dict]:
        """获取待处理的训练任务（从 inbox 目录）"""
        tasks = []
        if self.inbox_dir.exists():
            for f in sorted(self.inbox_dir.glob("*.json")):
                try:
                    with open(f) as fp:
                        tasks.append(json.load(fp))
                except Exception:
                    pass
        return tasks

    def mark_task_processed(self, task_id: str):
        """标记任务已处理（移动到 processed 目录）"""
        for f in self.inbox_dir.glob(f"*{task_id}*.json"):
            self.processed_dir.mkdir(parents=True, exist_ok=True)
            f.rename(self.processed_dir / f.name)

    def request_coach_task(self, coach_id: str, request_type: str = "training"):
        """向教练请求训练任务"""
        if self._mqtt_available:
            self.mqtt._publish_msg(
                MessageType.STATUS_REQUEST, coach_id,
                {"request_type": request_type, "node_id": self.node_id, "level": self.level},
                topic=f"lobster/go/{coach_id}/training/status",
            )

    # ==================== 内部方法 ====================

    def _watch_outbox(self):
        """监听 outbox 目录，将文件系统中的结果通过 MQTT 发送"""
        known_files = set()
        while self._running:
            if self.outbox_dir.exists():
                current = set(str(p) for p in self.outbox_dir.glob("*.json"))
                new_files = current - known_files

                for filepath in new_files:
                    if self._mqtt_available:
                        try:
                            with open(filepath) as f:
                                data = json.load(f)
                            to_node = data.get("to", "*")
                            if data.get("type") == "training_result":
                                self.mqtt.publish_training_result(
                                    to_node, data.get("result", {})
                                )
                            logger.debug(f"🦞 outbox→MQTT: {Path(filepath).name}")
                        except Exception as e:
                            logger.warning(f"outbox 转发失败: {e}")

                known_files = current

            time.sleep(2)  # outbox 轮询间隔


# ==================== 便捷函数 ====================

def bridge_coach(
    coach_id: str = "zhugema",
    broker_host: str = "localhost",
    broker_port: int = 1883,
) -> MQTTGoBridge:
    """创建教练桥接器"""
    bridge = MQTTGoBridge(
        node_id=coach_id,
        role="coach",
        broker_host=broker_host,
        broker_port=broker_port,
    )
    bridge.start()
    return bridge


def bridge_student(
    student_id: str,
    level: str,
    broker_host: str = "localhost",
    broker_port: int = 1883,
) -> MQTTGoBridge:
    """创建学员桥接器"""
    bridge = MQTTGoBridge(
        node_id=student_id,
        role="agent",
        level=level,
        broker_host=broker_host,
        broker_port=broker_port,
    )
    bridge.start()
    return bridge


# ==================== 集成演示脚本 ====================

def demo_coach_send_task():
    """演示：教练通过 MQTT 发送训练任务"""
    coach = bridge_coach("zhugema")

    # 教练发布训练任务到小陈
    task_payload = {
        "task_id": f"task-{int(time.time())}",
        "lesson_type": "life_death",
        "title": "直三和曲三死活判断",
        "deck": [
            {"id": "ld-001", "type": "life_death", "diagram": "直三", "answer": "死棋"},
            {"id": "ld-002", "type": "life_death", "diagram": "曲三", "answer": "死棋"},
            {"id": "ld-003", "type": "life_death", "diagram": "直四", "answer": "活棋"},
        ],
        "deadline": "2026-07-04T18:00:00",
        "reward_lc": 50,
    }
    msg_id = coach.mqtt.publish_training_task("xiaochen", task_payload)
    print(f"教练已发布训练任务: {msg_id}")

    coach.mqtt.publish_announce("今日围棋训练任务已发布，请各位学员查收！")

    time.sleep(2)
    coach.stop()


def demo_student_receive_and_submit():
    """演示：学员接收 MQTT 任务并提交结果"""
    student = bridge_student("xiaochen", "30级")

    # 等待接收任务
    print("小陈正在等待训练任务...")
    for _ in range(10):
        tasks = student.get_pending_tasks()
        if tasks:
            for task in tasks:
                print(f"收到任务: {task.get('task_id')}")
                # 模拟做题
                time.sleep(2)
                student.send_training_result(
                    to_node="zhugema",
                    task_id=task.get("task_id", "unknown"),
                    result={
                        "problems_solved": 3,
                        "problems_correct": 2,
                        "accuracy": 0.67,
                        "time_minutes": 8,
                        "summary": "直三和曲三判断正确，直四判断为死棋(错误)，需要加强学习。",
                        "next_focus": "直四和方四的死活判断",
                    },
                )
                print("训练结果已提交")
        time.sleep(1)

    student.stop()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(sys.argv) < 2:
        print("用法:")
        print("  python lobster_mqtt_go_bridge.py coach    # 教练模式")
        print("  python lobster_mqtt_go_bridge.py student  # 学员模式")
        print("  python lobster_mqtt_go_bridge.py demo     # 完整演示(需先启动 Mosquitto)")
        sys.exit(0)

    mode = sys.argv[1]
    if mode == "coach":
        demo_coach_send_task()
    elif mode == "student":
        demo_student_receive_and_submit()
    elif mode == "demo":
        print("=== 小龙虾网络 MQTT 围棋训练演示 ===\n")
        # 启动教练
        coach_thread = threading.Thread(target=demo_coach_send_task, daemon=True)
        coach_thread.start()
        time.sleep(1)
        # 启动学员
        demo_student_receive_and_submit()
        print("\n=== 演示完成 ===")
