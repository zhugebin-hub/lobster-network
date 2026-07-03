#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 MQTT 基础客户端库 v1.0
基于 paho-mqtt 2.x，提供连接管理、发布/订阅、心跳、遗嘱消息等核心功能。

诸葛马 (教练端) 172.24.57.34 — Mosquitto Broker
"""

import json
import time
import uuid
import logging
import threading
import os
import socket
from datetime import datetime

try:
    import paho.mqtt.client as mqtt
    try:
        from paho.mqtt.enums import CallbackAPIVersion
    except ImportError:
        CallbackAPIVersion = None  # paho-mqtt 1.x
    HAS_PAHO = True
except ImportError:
    mqtt = None
    CallbackAPIVersion = None
    HAS_PAHO = False

# ============================================================================
# Topic 架构定义
# ============================================================================

class Topics:
    """小龙虾网络 MQTT Topic 命名空间"""

    ROOT = "lobster"

    # 教练 → 学员指令
    @staticmethod
    def coach_to_student(student_id):
        return "{}/coach/{}/cmd".format(Topics.ROOT, student_id)

    # 学员 → 教练 ACK/回复
    @staticmethod
    def student_to_coach(student_id):
        return "{}/{}/coach/ack".format(Topics.ROOT, student_id)

    # 对局落子同步
    @staticmethod
    def match_move(match_id):
        return "{}/match/{}/move".format(Topics.ROOT, match_id)

    # 对局棋盘状态
    @staticmethod
    def match_board(match_id):
        return "{}/match/{}/board".format(Topics.ROOT, match_id)

    # 对局结果
    @staticmethod
    def match_result(match_id):
        return "{}/match/{}/result".format(Topics.ROOT, match_id)

    # 训练任务下发
    @staticmethod
    def training_task(student_id):
        return "{}/training/{}/task".format(Topics.ROOT, student_id)

    # 训练结果上报
    @staticmethod
    def training_result(student_id):
        return "{}/training/{}/result".format(Topics.ROOT, student_id)

    # 节点心跳
    @staticmethod
    def heartbeat(node_id):
        return "{}/heartbeat/{}".format(Topics.ROOT, node_id)

    # 节点在线状态 (遗嘱)
    @staticmethod
    def online_status(node_id):
        return "{}/online/{}".format(Topics.ROOT, node_id)

    # 全网广播
    @staticmethod
    def broadcast():
        return "{}/network/broadcast".format(Topics.ROOT)

    # 学员订阅的所有主题 (通配符)
    @staticmethod
    def student_subscribe_all(student_id):
        """学员订阅: 教练指令 + 训练任务 + 对局通知 + 广播"""
        return [
            Topics.coach_to_student(student_id),
            Topics.training_task(student_id),
            "{}/match/{}/+".format(Topics.ROOT, "*"),  # 所有对局
            Topics.broadcast(),
        ]

    # 教练订阅的所有主题 (通配符)
    @staticmethod
    def coach_subscribe_all():
        """教练订阅: 所有学员ACK + 训练结果 + 对局结果 + 心跳"""
        return [
            "{}/{}/coach/ack".format(Topics.ROOT, "+"),
            "{}/training/{}/result".format(Topics.ROOT, "+"),
            "{}/match/{}/result".format(Topics.ROOT, "+"),
            "{}/heartbeat/+".format(Topics.ROOT),
            "{}/online/+".format(Topics.ROOT),
        ]


# ============================================================================
# 消息工具
# ============================================================================

def create_message(msg_type, from_node, to_node=None, payload=None, priority="normal"):
    """创建标准小龙虾网络 MQTT 消息"""
    return json.dumps({
        "id": str(uuid.uuid4())[:12],
        "type": msg_type,
        "from": from_node,
        "to": to_node,
        "payload": payload or {},
        "priority": priority,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proto": "mqtt-v1.0",
    }, ensure_ascii=False)


def parse_message(json_str):
    """解析 MQTT 消息"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return {"raw": json_str, "parse_error": True}


# ============================================================================
# MQTT 基础客户端
# ============================================================================

class MqttClientBase:
    """小龙虾网络 MQTT 基础客户端

    功能:
    - 自动连接/重连 (指数退避)
    - 遗嘱消息 (LWT) 离线检测
    - 心跳保活
    - 消息发布 (QoS 1)
    - 主题订阅
    - 回调分发

    使用:
        client = MqttClientBase(
            node_id="xiaochen",
            broker_host="172.24.57.34",
            broker_port=1883,
        )
        client.start()
        client.publish("lobster/coach/xiaochen/cmd", message)
    """

    def __init__(self, node_id, broker_host="127.0.0.1", broker_port=1883,
                 keepalive=60, clean_session=False, qos=1):
        if not HAS_PAHO:
            raise ImportError("paho-mqtt 未安装: pip install paho-mqtt")

        self.node_id = node_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.qos = qos
        self.clean_session = clean_session
        self.client_id = "lobster-{}".format(node_id)

        self._client = None
        self._running = False
        self._heartbeat_thread = None
        self._callbacks = {}  # topic -> [callback_fn]
        self._on_connect_callbacks = []
        self._on_disconnect_callbacks = []

        # 重连参数
        self._reconnect_delay = 1
        self._max_reconnect_delay = 60

        # 日志
        self.logger = logging.getLogger("mqtt.{}".format(node_id))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        self._setup_mqtt_client()

    def _setup_mqtt_client(self):
        """初始化 paho-mqtt 客户端 (兼容 1.x 和 2.x)"""
        try:
            # paho-mqtt 2.x
            self._client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=self.client_id,
                clean_session=self.clean_session,
                protocol=mqtt.MQTTv311,
            )
            self._mqtt_v2 = True
        except (AttributeError, TypeError):
            # paho-mqtt 1.x fallback
            self._client = mqtt.Client(
                client_id=self.client_id,
                clean_session=self.clean_session,
                protocol=mqtt.MQTTv311,
            )
            self._mqtt_v2 = False

        # 遗嘱消息: 节点离线时自动发布
        self._client.will_set(
            topic=Topics.online_status(self.node_id),
            payload=json.dumps({
                "node_id": self.node_id,
                "status": "offline",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }),
            qos=self.qos,
            retain=True,
        )

        # 回调绑定
        def on_connect(client, userdata, flags, rc, properties=None):
            self.logger.info("Connected to broker (rc={})".format(rc))
            self._reconnect_delay = 1  # 重置重连延迟
            for cb in self._on_connect_callbacks:
                try:
                    cb(client, userdata, flags, rc)
                except Exception as e:
                    self.logger.error("on_connect callback error: {}".format(e))

        def on_disconnect(client, userdata, rc, properties=None):
            self.logger.warning("Disconnected from broker (rc={})".format(rc))
            for cb in self._on_disconnect_callbacks:
                try:
                    cb(client, userdata, rc)
                except TypeError:
                    try:
                        cb(client, userdata, rc, properties)
                    except Exception as e2:
                        self.logger.error("on_disconnect callback error: {}".format(e2))
                except Exception as e:
                    self.logger.error("on_disconnect callback error: {}".format(e))

        def on_message(client, userdata, msg):
            try:
                payload = msg.payload.decode("utf-8")
                self.logger.debug("Received on [{}]: {}".format(msg.topic, payload[:200]))
                # 分发到注册的回调
                for topic_pattern, callbacks in self._callbacks.items():
                    if self._topic_match(topic_pattern, msg.topic):
                        for cb in callbacks:
                            try:
                                cb(msg.topic, payload)
                            except Exception as e:
                                self.logger.error("Message callback error: {}".format(e))
            except Exception as e:
                self.logger.error("on_message error: {}".format(e))

        def on_subscribe(client, userdata, mid, granted_qos, properties=None):
            self.logger.debug("Subscribed mid={} qos={}".format(mid, granted_qos))

        # 绑定回调 (兼容 paho-mqtt 2.x API)
        self._client.on_connect = on_connect
        self._client.on_disconnect = on_disconnect
        self._client.on_message = on_message
        self._client.on_subscribe = on_subscribe

    def _topic_match(self, pattern, topic):
        """简单的 MQTT 主题通配符匹配"""
        pat_parts = pattern.split("/")
        top_parts = topic.split("/")
        for i, p in enumerate(pat_parts):
            if p == "#":
                return True
            if i >= len(top_parts):
                return False
            if p != "+" and p != top_parts[i]:
                return False
        return len(pat_parts) == len(top_parts)

    def set_will(self, topic, payload, qos=1, retain=True):
        """设置遗嘱消息 (必须在 connect 前调用)"""
        self._client.will_set(topic, payload, qos=qos, retain=retain)

    def on_connect(self, callback):
        """注册连接成功回调"""
        self._on_connect_callbacks.append(callback)

    def on_disconnect(self, callback):
        """注册断开连接回调"""
        self._on_disconnect_callbacks.append(callback)

    def on_message(self, topic_pattern, callback):
        """注册主题消息回调 (支持 + 和 # 通配符)"""
        if topic_pattern not in self._callbacks:
            self._callbacks[topic_pattern] = []
        self._callbacks[topic_pattern].append(callback)
        # 自动订阅 (如果已连接)
        if self._running:
            self.subscribe(topic_pattern)
        else:
            # 延迟订阅，连接后执行
            def auto_sub(client, userdata, flags, rc):
                self.subscribe(topic_pattern)
            self._on_connect_callbacks.append(auto_sub)

    def connect(self):
        """连接到 Broker"""
        try:
            self._client.connect(self.broker_host, self.broker_port, self.keepalive)
            self._client.loop_start()
            self._running = True
            self.logger.info("Connected to {}:{} as {}".format(
                self.broker_host, self.broker_port, self.client_id))
            return True
        except Exception as e:
            self.logger.error("Connect failed: {}".format(e))
            return False

    def subscribe(self, topic_pattern, qos=None):
        """订阅主题 (支持通配符)"""
        if not self._running:
            self.logger.warning("Not connected, cannot subscribe")
            return False
        try:
            q = qos if qos is not None else self.qos
            self._client.subscribe(topic_pattern, q)
            self.logger.info("Subscribed to [{}]".format(topic_pattern))
            return True
        except Exception as e:
            self.logger.error("Subscribe failed [{}]: {}".format(topic_pattern, e))
            return False

    def publish(self, topic, payload, qos=None, retain=False):
        """发布消息

        Args:
            topic: MQTT 主题
            payload: 字符串或 dict (dict 自动 JSON 序列化)
            qos: QoS 级别 (默认使用实例默认值)
            retain: 是否保留消息
        """
        if not self._running:
            self.logger.warning("Not connected, cannot publish")
            return False
        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload, ensure_ascii=False)
            q = qos if qos is not None else self.qos
            info = self._client.publish(topic, payload, q, retain=retain)
            self.logger.debug("Published to [{}]: {} bytes".format(topic, len(payload)))
            return True
        except Exception as e:
            self.logger.error("Publish failed [{}]: {}".format(topic, e))
            return False

    def publish_message(self, topic, msg_type, from_node, to_node=None,
                        payload=None, priority="normal", qos=None):
        """发布标准小龙虾网络消息"""
        msg = create_message(msg_type, from_node, to_node, payload, priority)
        return self.publish(topic, msg, qos=qos)

    def start_heartbeat(self, interval=30):
        """启动心跳线程"""
        self._running = True

        def heartbeat_loop():
            while self._running:
                try:
                    hb = {
                        "node_id": self.node_id,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "host": socket.gethostname(),
                        "status": "alive",
                    }
                    self.publish(Topics.heartbeat(self.node_id), hb, retain=True)
                    # 同时发布在线状态
                    self.publish(Topics.online_status(self.node_id), {
                        "node_id": self.node_id,
                        "status": "online",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }, retain=True)
                except Exception as e:
                    self.logger.error("Heartbeat error: {}".format(e))
                time.sleep(interval)

        self._heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
        self.logger.info("Heartbeat started (interval={}s)".format(interval))

    def stop_heartbeat(self):
        """停止心跳"""
        self._running = False
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=5)

    def disconnect(self):
        """断开连接"""
        self._running = False
        self.stop_heartbeat()
        # 发布离线消息
        try:
            self.publish(Topics.online_status(self.node_id), {
                "node_id": self.node_id,
                "status": "offline",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, retain=True)
        except Exception:
            pass
        try:
            self._client.loop_stop()
            self._client.disconnect()
            self.logger.info("Disconnected")
        except Exception as e:
            self.logger.error("Disconnect error: {}".format(e))

    def is_connected(self):
        """检查连接状态"""
        return self._running and self._client.is_connected()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.disconnect()
