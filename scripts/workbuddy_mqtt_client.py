#!/usr/bin/env python3
"""WorkBuddy MQTT 集成客户端
连接到小龙虾网络 Mosquitto Broker (121.43.80.231:1883)
订阅 workbuddy 相关主题，发布节点状态
"""

import json
import time
from datetime import datetime

BROKER_HOST = "121.43.80.231"
BROKER_PORT = 1883
NODE_ID = "workbuddy"
NODE_NAME = "WorkBuddy 助理龙虾"

class WorkbuddyMQTTClient:
    """封装的 MQTT 客户端"""
    
    def __init__(self, host=BROKER_HOST, port=BROKER_PORT):
        self.host = host
        self.port = port
        self.client = None
        self.connected = False
        
    def connect(self):
        """连接 MQTT Broker"""
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            print("❌ paho-mqtt 未安装。执行: pip install paho-mqtt")
            return False
        
        self.client = mqtt.Client(client_id=f"lobster-workbuddy-{int(time.time())}")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        
        try:
            self.client.connect(self.host, self.port, keepalive=60)
            self.client.loop_start()
            time.sleep(1)
            return True
        except Exception as e:
            print(f"❌ MQTT 连接失败: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"✅ MQTT 已连接 {self.host}:{self.port}")
            # 订阅主题
            topics = [
                f"lobster/nodes/workbuddy/#",
                "lobster/broadcast",
                "lobster/drug-discovery/#",
                "lobster/system/#",
            ]
            for topic in topics:
                client.subscribe(topic)
                print(f"  📡 订阅: {topic}")
        else:
            print(f"❌ MQTT 连接失败 rc={rc}")
    
    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            print(f"\n📨 [{msg.topic}] {payload.get('from', 'unknown')}: {payload.get('subject', '无标题')}")
        except Exception:
            print(f"\n📨 [{msg.topic}] {msg.payload.decode()[:100]}")
    
    def publish_status(self):
        """发布节点状态"""
        if not self.connected:
            return
        
        status = {
            "node_id": NODE_ID,
            "name": NODE_NAME,
            "status": "active",
            "type": "student (综合学习型)",
            "version": "0.6.0",
            "timestamp": datetime.now().isoformat(),
            "learning_modules": ["炒股预测", "网络协议", "药物发现"],
            "capabilities": ["代码开发", "文档处理", "数据分析", "自动化运维"],
        }
        
        topic = f"lobster/nodes/workbuddy/status"
        self.client.publish(topic, json.dumps(status, ensure_ascii=False))
        print(f"📤 状态已发布: {topic}")
    
    def publish_training_result(self, module, phase, score, details=None):
        """发布训练结果"""
        if not self.connected:
            return
        
        result = {
            "node_id": NODE_ID,
            "module": module,
            "phase": phase,
            "score": score,
            "details": details or {},
            "timestamp": datetime.now().isoformat(),
        }
        
        topic = f"lobster/nodes/workbuddy/training"
        self.client.publish(topic, json.dumps(result, ensure_ascii=False))
        print(f"📤 训练结果已发布: {topic} - {module}/{phase} score={score}")
    
    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("👋 MQTT 已断开")


if __name__ == "__main__":
    client = WorkbuddyMQTTClient()
    if client.connect():
        client.publish_status()
        try:
            while True:
                time.sleep(3600)  # 每小时发一次状态
                client.publish_status()
        except KeyboardInterrupt:
            pass
        finally:
            client.disconnect()
