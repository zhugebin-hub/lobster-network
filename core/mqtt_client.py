#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 MQTT 通信客户端
基于 paho-mqtt 实现节点间实时消息通信、发布/订阅、路由与状态管理。
作者：诸葛马 (Hermes) | 版本：V1.0 | 日期：2026-07-10
"""

import paho.mqtt.client as mqtt
import json
import os
import time
import logging
from datetime import datetime
from typing import Dict, Any, Callable, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class LobsterMQTTClient:
    """小龙虾网络 MQTT 客户端核心类"""
    
    def __init__(self, node_id: str, broker_host: str = "localhost", broker_port: int = 1883, keepalive: int = 60):
        self.node_id = node_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.keepalive = keepalive
        self.connected = False
        self.callbacks: Dict[str, Callable] = {}
        
        # 初始化 MQTT 客户端
        self.client = mqtt.Client(client_id=f"lobster_{node_id}_{int(time.time())}", clean_session=True)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # 本地任务存储目录
        self.task_dir = f"/home/admin/lobster-network/tasks/{self.node_id}"
        os.makedirs(self.task_dir, exist_ok=True)
        
        logger.info(f"🦞 节点 {self.node_id} MQTT 客户端初始化完成")

    def _on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            self.connected = True
            logger.info(f"✅ 节点 {self.node_id} 成功连接 MQTT Broker ({self.broker_host}:{self.broker_port})")
            
            # 自动订阅节点专属主题与广播主题
            topics = [
                f"lobster/nodes/{self.node_id}/#",
                f"lobster/broadcast/#",
                f"lobster/system/commands"
            ]
            for topic in topics:
                client.subscribe(topic, qos=1)
                logger.info(f"📡 已订阅主题: {topic}")
                
            # 发布在线状态
            self.publish_status("online")
        else:
            logger.error(f"❌ 连接失败，错误码: {rc} (常见: 1=协议错误, 2=ID拒绝, 3=服务器不可用, 4=用户密码错误, 5=未授权)")

    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.connected = False
        if rc != 0:
            logger.warning(f"⚠️ 节点 {self.node_id} 意外断开连接，错误码: {rc}")
        else:
            logger.info(f"🔌 节点 {self.node_id} 主动断开连接")

    def _on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            topic = msg.topic
            
            logger.info(f"📩 收到消息 [{topic}] 类型: {payload.get('type', 'unknown')}")
            
            # 触发对应回调
            msg_type = payload.get('type', '')
            if msg_type in self.callbacks:
                self.callbacks[msg_type](topic, payload)
            else:
                self._default_handler(topic, payload)
                
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"⚠️ 消息处理异常: {e}")

    def _default_handler(self, topic: str, data: Dict[str, Any]):
        """默认消息处理器"""
        msg_type = data.get('type', '')
        if msg_type == 'task_assignment':
            self._save_task(data)
            logger.info(f"  📋 新任务已保存: {data.get('title', 'N/A')}")
        elif msg_type == 'ack_request':
            self.publish_ack(topic, data.get('request_id'))
        elif msg_type == 'system_broadcast':
            logger.info(f"  📢 系统广播: {data.get('content', 'N/A')}")

    def _save_task(self, data: Dict[str, Any]):
        """保存任务到本地文件系统"""
        task_file = os.path.join(self.task_dir, f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"  💾 任务已落盘: {task_file}")

    def publish(self, topic: str, data: Dict[str, Any], qos: int = 1):
        """发布消息"""
        if not self.connected:
            logger.warning("⚠️ 未连接，无法发布消息")
            return False
        try:
            payload = json.dumps(data, ensure_ascii=False)
            result = self.client.publish(topic, payload, qos=qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"📤 已发布 [{topic}] QoS:{qos}")
                return True
            else:
                logger.error(f"❌ 发布失败，错误码: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"❌ 发布异常: {e}")
            return False

    def publish_status(self, status: str):
        """发布节点状态"""
        self.publish(f"lobster/nodes/{self.node_id}/status", {
            "type": "status",
            "node_id": self.node_id,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0"
        })

    def publish_ack(self, original_topic: str, request_id: Optional[str] = None):
        """发送 ACK 回复"""
        ack_data = {
            "type": "ack",
            "node_id": self.node_id,
            "timestamp": datetime.now().isoformat(),
            "status": "received",
            "request_id": request_id or "unknown"
        }
        # 回复到对应的 outbox 或 reply 主题
        reply_topic = original_topic.replace("/inbox/", "/outbox/").replace("/request/", "/reply/")
        self.publish(reply_topic, ack_data)
        logger.info(f"✅ 已发送 ACK 到 {reply_topic}")

    def on(self, msg_type: str, callback: Callable):
        """注册消息类型回调"""
        self.callbacks[msg_type] = callback
        logger.info(f"🔗 已注册回调: {msg_type}")

    def connect(self, timeout: int = 5):
        """连接到 Broker"""
        try:
            self.client.connect(self.broker_host, self.broker_port, self.keepalive)
            self.client.loop_start()
            time.sleep(timeout)
            if not self.connected:
                logger.error("❌ 连接超时")
                return False
            return True
        except Exception as e:
            logger.error(f"❌ 连接异常: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        self.publish_status("offline")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info(f"🔌 节点 {self.node_id} 已安全断开")

# 示例用法
if __name__ == "__main__":
    import sys
    node_id = sys.argv[1] if len(sys.argv) > 1 else "test_node"
    
    client = LobsterMQTTClient(node_id)
    if client.connect():
        print(f"\n🚀 节点 {node_id} 已启动，等待消息... (按 Ctrl+C 退出)\n")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
            print("\n👋 退出")
