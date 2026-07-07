#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 MQTT 教练端发布器 v1.0
运行在诸葛马 (172.24.57.34)，负责向学员发布指令、训练任务、对局通知，
并收集学员 ACK 和训练结果。

替代 V4.0 的 message_sync_v4.py (SCP 轮询方案)。

使用:
    python3 core/mqtt_coach_publisher.py start    # 启动服务
    python3 core/mqtt_coach_publisher.py send <student> <type> <payload_json>
    python3 core/mqtt_coach_publisher.py status    # 查看学员状态
    python3 core/mqtt_coach_publisher.py test      # 端到端测试
"""

import sys
import os
import json
import time
import signal
import logging
from datetime import datetime

# 确保可以导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mqtt_client_base import (
    MqttClientBase, Topics, create_message, parse_message
)

# ============================================================================
# 配置
# ============================================================================

BROKER_HOST = "127.0.0.1"  # 本地 Broker
BROKER_PORT = 1883
NODE_ID = "zhugema"  # 教练节点 ID
STUDENTS = ["xiaochen", "zhuguxia"]  # 学员列表

# 学员状态追踪
STUDENT_STATUS_FILE = "/home/admin/go-training/shared/mqtt_student_status.json"


class CoachPublisher:
    """教练端 MQTT 发布器"""

    def __init__(self, broker_host=BROKER_HOST, broker_port=BROKER_PORT):
        self.client = MqttClientBase(
            node_id=NODE_ID,
            broker_host=broker_host,
            broker_port=broker_port,
            keepalive=60,
        )
        self.logger = logging.getLogger("coach.publisher")
        self.student_status = {}  # {student_id: {last_heartbeat, last_ack, status}}
        self._running = False

        # 注册回调
        self.client.on_connect(self._on_connect)
        self.client.on_message(Topics.broadcast(), self._on_broadcast)

        # 为每个学员注册 ACK 回调
        for student in STUDENTS:
            ack_topic = Topics.student_to_coach(student)
            self.client.on_message(ack_topic, self._make_ack_handler(student))

            result_topic = Topics.training_result(student)
            self.client.on_message(result_topic, self._make_result_handler(student))

            hb_topic = Topics.heartbeat(student)
            self.client.on_message(hb_topic, self._make_heartbeat_handler(student))

            online_topic = Topics.online_status(student)
            self.client.on_message(online_topic, self._make_online_handler(student))

        # 加载学员状态
        self._load_status()

    def _on_connect(self, client, userdata, flags, rc):
        """连接成功后订阅所有学员相关主题"""
        self.logger.info("教练端已连接，订阅学员主题...")
        for student in STUDENTS:
            self.client.subscribe(Topics.student_to_coach(student))
            self.client.subscribe(Topics.training_result(student))
            self.client.subscribe(Topics.heartbeat(student))
            self.client.subscribe(Topics.online_status(student))
        self.client.start_heartbeat(interval=30)
        self.logger.info("教练端订阅完成，心跳已启动")

    def _make_ack_handler(self, student_id):
        """创建 ACK 处理器闭包"""
        def handler(topic, payload):
            msg = parse_message(payload)
            self.logger.info("[{}] ACK: type={} id={}".format(
                student_id, msg.get("type", "?"), msg.get("id", "?")[:8]))
            self._update_student_status(student_id, {
                "last_ack": msg.get("timestamp"),
                "last_ack_type": msg.get("type"),
                "ack_count": self.student_status.get(student_id, {}).get("ack_count", 0) + 1,
            })
        return handler

    def _make_result_handler(self, student_id):
        """创建训练结果处理器闭包"""
        def handler(topic, payload):
            msg = parse_message(payload)
            self.logger.info("[{}] 训练结果: {}".format(student_id, payload[:100]))
            self._update_student_status(student_id, {
                "last_result": msg.get("timestamp"),
                "last_result_type": msg.get("type"),
            })
        return handler

    def _make_heartbeat_handler(self, student_id):
        """创建心跳处理器闭包"""
        def handler(topic, payload):
            msg = parse_message(payload)
            self._update_student_status(student_id, {
                "last_heartbeat": msg.get("timestamp"),
                "heartbeat_status": msg.get("status", "alive"),
            })
        return handler

    def _make_online_handler(self, student_id):
        """创建在线状态处理器闭包"""
        def handler(topic, payload):
            msg = parse_message(payload)
            status = msg.get("status", "unknown")
            self.logger.info("[{}] 在线状态: {}".format(student_id, status))
            self._update_student_status(student_id, {
                "online_status": status,
                "last_online_change": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        return handler

    def _on_broadcast(self, topic, payload):
        """处理全网广播"""
        self.logger.info("[广播] {}".format(payload[:200]))

    def _update_student_status(self, student_id, updates):
        """更新学员状态"""
        if student_id not in self.student_status:
            self.student_status[student_id] = {"node_id": student_id}
        self.student_status[student_id].update(updates)
        self._save_status()

    def _load_status(self):
        """加载学员状态"""
        try:
            if os.path.exists(STUDENT_STATUS_FILE):
                with open(STUDENT_STATUS_FILE) as f:
                    self.student_status = json.load(f)
        except Exception as e:
            self.logger.warning("加载状态失败: {}".format(e))
            self.student_status = {}

    def _save_status(self):
        """保存学员状态"""
        try:
            os.makedirs(os.path.dirname(STUDENT_STATUS_FILE), exist_ok=True)
            with open(STUDENT_STATUS_FILE, "w") as f:
                json.dump(self.student_status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.warning("保存状态失败: {}".format(e))

    # =========================================================================
    # 公开 API
    # =========================================================================

    def send_to_student(self, student_id, msg_type, payload=None, priority="normal"):
        """向学员发送消息"""
        topic = Topics.coach_to_student(student_id)
        return self.client.publish_message(
            topic, msg_type, NODE_ID, student_id, payload, priority
        )

    def send_training_task(self, student_id, task_data):
        """发送训练任务"""
        return self.send_to_student(student_id, "training_task", task_data)

    def send_go_match_notify(self, student_id, match_data):
        """发送对局通知"""
        return self.send_to_student(student_id, "go_match_notify", match_data)

    def send_go_move_ask(self, student_id, match_data):
        """询问学员落子 (学员AI引擎自动回复)"""
        return self.send_to_student(student_id, "go_move_ask", match_data)

    def send_go_move(self, student_id, match_data):
        """发送落子坐标给学员"""
        return self.send_to_student(student_id, "go_move", match_data)

    def send_reminder(self, student_id, message):
        """发送提醒"""
        return self.send_to_student(student_id, "reminder", {"message": message})

    def broadcast(self, msg_type, payload):
        """全网广播"""
        msg = create_message(msg_type, NODE_ID, payload=payload)
        return self.client.publish(Topics.broadcast(), msg)

    def get_student_status(self, student_id=None):
        """获取学员状态"""
        if student_id:
            return self.student_status.get(student_id, {})
        return self.student_status

    def get_status_summary(self):
        """获取状态摘要"""
        summary = []
        for sid, status in self.student_status.items():
            line = "{}: online={} heartbeat={} acks={}".format(
                sid,
                status.get("online_status", "unknown"),
                status.get("last_heartbeat", "never"),
                status.get("ack_count", 0),
            )
            summary.append(line)
        return "\n".join(summary) if summary else "无学员状态数据"

    def start(self):
        """启动教练端发布器"""
        self._running = True
        self.client.connect()
        self.logger.info("教练端发布器已启动")

        # 优雅退出
        def signal_handler(signum, frame):
            self.logger.info("收到退出信号，关闭教练端...")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # 主循环
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """停止教练端发布器"""
        self._running = False
        self.client.disconnect()
        self._save_status()
        self.logger.info("教练端发布器已停止")


# ============================================================================
# CLI 入口
# ============================================================================

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("用法: python3 mqtt_coach_publisher.py <command> [args]")
        print("命令: start | send <student> <type> [payload] | status | test")
        sys.exit(1)

    command = sys.argv[1]
    publisher = CoachPublisher()

    if command == "start":
        print("启动教练端 MQTT 发布器...")
        publisher.start()

    elif command == "send":
        if len(sys.argv) < 4:
            print("用法: send <student> <type> [payload_json]")
            sys.exit(1)
        student = sys.argv[2]
        msg_type = sys.argv[3]
        payload = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        publisher.client.connect()
        time.sleep(1)
        result = publisher.send_to_student(student, msg_type, payload)
        print("发送 {} 到 {}: {}".format(msg_type, student, "成功" if result else "失败"))
        time.sleep(1)
        publisher.client.disconnect()

    elif command == "status":
        publisher.client.connect()
        time.sleep(2)
        print("=== 学员状态 ===")
        print(publisher.get_status_summary())
        publisher.client.disconnect()

    elif command == "test":
        print("=== MQTT 端到端测试 ===")
        publisher.client.connect()
        time.sleep(2)

        for student in STUDENTS:
            print("发送测试消息到 {}...".format(student))
            publisher.send_to_student(student, "system", {
                "message": "MQTT 连接测试 - 诸葛马 {}".format(
                    datetime.now().strftime("%H:%M:%S"))
            })

        print("发送全网广播...")
        publisher.broadcast("system", {"message": "全网广播测试"})

        print("等待 ACK...")
        time.sleep(5)
        print("\n=== 学员状态 ===")
        print(publisher.get_status_summary())
        publisher.client.disconnect()
        print("=== 测试完成 ===")

    else:
        print("未知命令: {}".format(command))
        sys.exit(1)


if __name__ == "__main__":
    main()
