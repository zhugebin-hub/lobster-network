#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 MQTT 学员端订阅器 v1.0
运行在学员服务器 (小陈 121.43.80.231 / 诸葛虾 172.24.56.3)，
自动接收教练指令、处理训练任务、回复 ACK、上报训练结果。

替代 V4.0 的 student_poller_v4.py (SCP 轮询方案)。

使用:
    python3 core/mqtt_student_subscriber.py xiaochen    # 启动小陈订阅器
    python3 core/mqtt_student_subscriber.py zhuguxia     # 启动诸葛虾订阅器
    python3 core/mqtt_student_subscriber.py --test       # 本地测试
"""

import sys
import os
import json
import time
import signal
import logging
import subprocess
from datetime import datetime

# 确保可以导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mqtt_client_base import (
    MqttClientBase, Topics, create_message, parse_message
)

# ============================================================================
# 配置
# ============================================================================

BROKER_HOST = "172.24.57.34"  # 诸葛马 Broker 地址
BROKER_PORT = 1883
NODE_ID = "xiaochen"  # 默认学员 ID (通过命令行参数覆盖)
HEARTBEAT_INTERVAL = 30  # 心跳间隔 (秒)

# 消息处理分发器
MESSAGE_HANDLERS = {}


def register_handler(msg_type):
    """消息类型处理器装饰器"""
    def decorator(func):
        MESSAGE_HANDLERS[msg_type] = func
        return func
    return decorator


# ============================================================================
# 消息处理器
# ============================================================================

@register_handler("system")
def handle_system(topic, msg, subscriber):
    """处理系统消息"""
    subscriber.logger.info("[系统] {}".format(msg.get("payload", {})))
    subscriber.send_ack(msg, "received")


@register_handler("training_task")
def handle_training_task(topic, msg, subscriber):
    """处理训练任务"""
    payload = msg.get("payload", {})
    task_type = payload.get("task_type", "unknown")
    subscriber.logger.info("[训练任务] type={} id={}".format(task_type, msg.get("id", "?")))

    # 发送 ACK
    subscriber.send_ack(msg, "received")

    # 保存任务到本地文件 (供学员 AI Agent 执行)
    task_dir = "/home/admin/go-training/shared/training/{}/inbox/".format(subscriber.node_id)
    os.makedirs(task_dir, exist_ok=True)
    task_file = os.path.join(task_dir, "task_{}_{}.json".format(
        msg.get("id", "unknown"),
        datetime.now().strftime("%Y%m%d_%H%M%S")
    ))
    with open(task_file, "w") as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
    subscriber.logger.info("训练任务已保存: {}".format(task_file))


@register_handler("go_match_notify")
def handle_go_match_notify(topic, msg, subscriber):
    """处理对局通知"""
    payload = msg.get("payload", {})
    match_id = payload.get("match_id", "unknown")
    subscriber.logger.info("[对局通知] match_id={}".format(match_id))
    subscriber.send_ack(msg, "received")

    # 保存对局信息
    match_dir = "/home/admin/go-training/shared/training/go/matches/"
    os.makedirs(match_dir, exist_ok=True)
    match_file = os.path.join(match_dir, "match_{}.json".format(match_id))
    with open(match_file, "w") as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)


@register_handler("go_move")
def handle_go_move(topic, msg, subscriber):
    """处理落子通知"""
    payload = msg.get("payload", {})
    match_id = payload.get("match_id", "unknown")
    move = payload.get("move", "unknown")
    subscriber.logger.info("[落子] match={} move={}".format(match_id, move))
    subscriber.send_ack(msg, "received")

    # 更新本地棋谱
    match_dir = "/home/admin/go-training/shared/training/go/matches/"
    os.makedirs(match_dir, exist_ok=True)
    move_file = os.path.join(match_dir, "last_move_{}.json".format(subscriber.node_id))
    with open(move_file, "w") as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)


@register_handler("go_move_ask")
def handle_go_move_ask(topic, msg, subscriber):
    """处理落子询问 — 调用 AI 引擎回复"""
    payload = msg.get("payload", {})
    match_id = payload.get("match_id", "unknown")
    board_size = payload.get("board_size", 9)
    subscriber.logger.info("[落子询问] match={} board={}x{}".format(match_id, board_size, board_size))

    subscriber.send_ack(msg, "processing")

    # 调用围棋 AI 引擎
    go_engine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "go_ai_engine_v2.py")
    if not os.path.exists(go_engine):
        go_engine = os.path.join(os.path.dirname(os.path.abspath(__file__)), "go_ai_engine_v1.py")

    if os.path.exists(go_engine):
        try:
            result = subprocess.run(
                [sys.executable, go_engine, str(board_size)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                timeout=30,
            )
            # 解析最后一手棋坐标
            output = result.stdout.strip()
            move = "unknown"
            for line in output.split("\n"):
                if "黑" in line or "white" in line.lower() or "move" in line.lower():
                    parts = line.split()
                    for p in parts:
                        if len(p) >= 2 and p[0].isalpha() and p[1:].isdigit():
                            move = p
                            break
            if move == "unknown":
                # 默认落子
                move = "D4" if board_size == 9 else "D4"

            subscriber.logger.info("AI 落子: {}".format(move))

            # 回复落子坐标
            reply_payload = {
                "match_id": match_id,
                "move": move,
                "board_size": board_size,
                "student_id": subscriber.node_id,
                "method": "ai_engine",
            }
            subscriber.send_ack(msg, "completed", extra_payload=reply_payload)

            # 发布落子到对局主题
            reply_topic = Topics.match_move(match_id)
            subscriber.client.publish(reply_topic, json.dumps({
                "from": subscriber.node_id,
                "move": move,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }))

        except subprocess.TimeoutExpired:
            subscriber.logger.error("AI 引擎超时")
            subscriber.send_ack(msg, "error", {"error": "AI engine timeout"})
        except Exception as e:
            subscriber.logger.error("AI 引擎错误: {}".format(e))
            subscriber.send_ack(msg, "error", {"error": str(e)})
    else:
        subscriber.logger.warning("AI 引擎不存在，跳过落子")
        subscriber.send_ack(msg, "completed", {"note": "no engine"})


@register_handler("reminder")
def handle_reminder(topic, msg, subscriber):
    """处理提醒"""
    payload = msg.get("payload", {})
    subscriber.logger.info("[提醒] {}".format(payload.get("message", "?")))
    subscriber.send_ack(msg, "received")


@register_handler("ack")
def handle_ack(topic, msg, subscriber):
    """处理 ACK (忽略，这是教练端发的)"""
    pass


# ============================================================================
# 学员端 MQTT 订阅器
# ============================================================================

class StudentSubscriber:
    """学员端 MQTT 订阅器"""

    def __init__(self, node_id, broker_host=BROKER_HOST, broker_port=BROKER_PORT):
        self.node_id = node_id
        self.client = MqttClientBase(
            node_id=node_id,
            broker_host=broker_host,
            broker_port=broker_port,
            keepalive=60,
            clean_session=False,  # 持久会话，断线重连后恢复
        )
        self.logger = logging.getLogger("student.{}".format(node_id))
        self._running = False

        # 注册主题回调
        self._register_callbacks()

    def _register_callbacks(self):
        """注册所有消息类型回调"""
        # 教练指令主题
        coach_topic = Topics.coach_to_student(self.node_id)
        self.client.on_message(coach_topic, self._on_coach_message)

        # 训练任务主题
        training_topic = Topics.training_task(self.node_id)
        self.client.on_message(training_topic, self._on_coach_message)

        # 对局主题 (通配符)
        self.client.on_message(
            "{}/match/{}/+".format(Topics.ROOT, "+"),
            self._on_match_message,
        )

        # 广播主题
        self.client.on_message(Topics.broadcast(), self._on_broadcast)

    def _on_coach_message(self, topic, payload):
        """处理教练消息 (统一分发)"""
        msg = parse_message(payload)
        if msg.get("parse_error"):
            self.logger.warning("消息解析失败: {}".format(payload[:100]))
            return

        msg_type = msg.get("type", "unknown")
        self.logger.info("[{}] 收到: type={} id={}".format(
            self.node_id, msg_type, msg.get("id", "?")[:8]))

        # 分发到具体处理器
        handler = MESSAGE_HANDLERS.get(msg_type)
        if handler:
            try:
                handler(topic, msg, self)
            except Exception as e:
                self.logger.error("处理 {} 消息出错: {}".format(msg_type, e))
                self.send_ack(msg, "error", {"error": str(e)})
        else:
            self.logger.warning("未知消息类型: {}".format(msg_type))
            self.send_ack(msg, "unknown_type")

    def _on_match_message(self, topic, payload):
        """处理对局消息"""
        msg = parse_message(payload)
        self.logger.info("[对局] topic={} from={}".format(
            topic, msg.get("from", "?")))

    def _on_broadcast(self, topic, payload):
        """处理广播消息"""
        msg = parse_message(payload)
        self.logger.info("[广播] type={} from={}".format(
            msg.get("type", "?"), msg.get("from", "?")))

    def send_ack(self, original_msg, status, extra_payload=None):
        """发送 ACK 到教练端"""
        ack_payload = {
            "original_id": original_msg.get("id"),
            "original_type": original_msg.get("type"),
            "status": status,
            "student_id": self.node_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "subscriber_version": "1.0",
        }
        if extra_payload:
            ack_payload.update(extra_payload)

        ack_topic = Topics.student_to_coach(self.node_id)
        ack_msg = create_message("ack", self.node_id, "zhugema", ack_payload)
        return self.client.publish(ack_topic, ack_msg)

    def send_training_result(self, result_data):
        """上报训练结果"""
        result_topic = Topics.training_result(self.node_id)
        result_msg = create_message("training_result", self.node_id, "zhugema", result_data)
        return self.client.publish(result_topic, result_msg)

    def start(self):
        """启动学员端订阅器"""
        self._running = True
        self.client.connect()
        self.client.start_heartbeat(interval=HEARTBEAT_INTERVAL)
        self.logger.info("学员端订阅器已启动 (node={}, broker={}:{})".format(
            self.node_id, self.client.broker_host, self.client.broker_port))

        # 优雅退出
        def signal_handler(signum, frame):
            self.logger.info("收到退出信号，关闭学员端...")
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
        """停止学员端订阅器"""
        self._running = False
        self.client.disconnect()
        self.logger.info("学员端订阅器已停止")


# ============================================================================
# CLI 入口
# ============================================================================

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("用法: python3 mqtt_student_subscriber.py <node_id> [--broker HOST:PORT]")
        print("示例: python3 mqtt_student_subscriber.py xiaochen")
        print("      python3 mqtt_student_subscriber.py zhuguxia --broker 172.24.57.34:1883")
        sys.exit(1)

    node_id = sys.argv[1]
    broker_host = BROKER_HOST
    broker_port = BROKER_PORT

    # 解析 --broker 参数
    if "--broker" in sys.argv:
        idx = sys.argv.index("--broker")
        if idx + 1 < len(sys.argv):
            parts = sys.argv[idx + 1].split(":")
            broker_host = parts[0]
            if len(parts) > 1:
                broker_port = int(parts[1])

    subscriber = StudentSubscriber(node_id, broker_host, broker_port)
    subscriber.start()


if __name__ == "__main__":
    main()
