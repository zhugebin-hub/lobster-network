#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 · 全链路验证脚本
目标链路: 老师 → 车虾 → 诸葛马 → 专项虾 → 原路返回
"""

import paho.mqtt.client as mqtt
import json
import time
import sys
import os
from datetime import datetime

BROKER = "localhost"
PORT = 1883
TIMEOUT = 15

# 模拟角色
class LobsterNode:
    def __init__(self, name, broker=BROKER, port=PORT):
        self.name = name
        self.client = mqtt.Client(client_id=name)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.received_messages = []
        self.client.connect(broker, port, 60)
        self.client.loop_start()
        time.sleep(1)

    def on_connect(self, client, userdata, flags, rc):
        print(f"[{self.name}] 已连接至 Broker (RC: {rc})")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.received_messages.append(payload)
            print(f"[{self.name}] 收到消息: {payload.get('type')} -> {msg.topic}")
        except Exception as e:
            print(f"[{self.name}] 解析消息失败: {e}")

    def publish(self, topic, payload):
        msg_json = json.dumps(payload)
        self.client.publish(topic, msg_json)
        print(f"[{self.name}] 发送消息: {topic} -> {payload.get('type')}")

    def wait_for(self, expected_type, timeout=TIMEOUT):
        start = time.time()
        while time.time() - start < timeout:
            for msg in self.received_messages:
                if msg.get('type') == expected_type:
                    return msg
            time.sleep(0.5)
        return None

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

def run_verification():
    print("="*70)
    print("🦞 小龙虾网络 · 全链路验证开始")
    print("="*70)
    print()

    # 1. 初始化节点
    che_xia = LobsterNode("che_xia")
    zhuge_ma = LobsterNode("zhuge_ma")
    zhuanxiang = LobsterNode("zhuanxiang")

    # 2. 订阅 Topic
    che_xia.client.subscribe("lobster/che_xia/result")
    zhuge_ma.client.subscribe("lobster/che_xia/relay")
    zhuge_ma.client.subscribe("lobster/zhuanxiang/result")
    zhuanxiang.client.subscribe("lobster/zhuanxiang/inbox")

    time.sleep(1)

    # 3. 定义路由逻辑 (诸葛马)
    def zhuge_ma_route(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic == "lobster/che_xia/relay":
                target = payload.get("target", "zhuanxiang")
                print(f"[zhuge_ma] 路由转发: che_xia -> {target}")
                client.publish(f"lobster/{target}/inbox", json.dumps(payload))
            elif msg.topic == "lobster/zhuanxiang/result":
                print(f"[zhuge_ma] 结果回传: zhuanxiang -> che_xia")
                client.publish("lobster/che_xia/result", json.dumps(payload))
        except Exception as e:
            print(f"[zhuge_ma] 路由失败: {e}")

    zhuge_ma.client.on_message = zhuge_ma_route
    # 重新订阅以应用新的 on_message
    zhuge_ma.client.subscribe("lobster/che_xia/relay")
    zhuge_ma.client.subscribe("lobster/zhuanxiang/result")

    # 4. 定义专项虾处理逻辑
    def zhuanxiang_process(client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            if msg.topic == "lobster/zhuanxiang/inbox":
                print(f"[zhuanxiang] 处理任务: {payload.get('task')}")
                time.sleep(1) # 模拟处理
                response = {
                    "type": "result",
                    "task": payload.get("task"),
                    "result": "处理完成",
                    "timestamp": datetime.now().isoformat()
                }
                client.publish("lobster/zhuanxiang/result", json.dumps(response))
        except Exception as e:
            print(f"[zhuanxiang] 处理失败: {e}")

    zhuanxiang.client.on_message = zhuanxiang_process
    zhuanxiang.client.subscribe("lobster/zhuanxiang/inbox")

    time.sleep(1)

    # 5. 执行全链路验证
    print("\n--- 开始验证 ---")
    
    # 老师 → 车虾 → 诸葛马 → 专项虾
    task_msg = {
        "type": "task_request",
        "from": "teacher",
        "to": "zhuanxiang",
        "target": "zhuanxiang",
        "task": "分析过敏原数据",
        "timestamp": datetime.now().isoformat()
    }
    che_xia.publish("lobster/che_xia/relay", task_msg)

    # 专项虾 → 诸葛马 → 车虾
    ack_msg = che_xia.wait_for("result")
    
    if ack_msg:
        print("\n✅ 验证成功: 消息已成功往返!")
        print(f"   返回内容: {ack_msg}")
    else:
        print("\n❌ 验证失败: 超时未收到返回消息")

    # 6. 清理
    che_xia.disconnect()
    zhuge_ma.disconnect()
    zhuanxiang.disconnect()
    print("\n✅ 验证结束")

if __name__ == "__main__":
    run_verification()
