#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 MQTT-文件桥接器 v1.0
运行在诸葛马 (172.24.57.34)，桥接 SSH 文件目录和 MQTT Broker。

功能:
1. 监控小陈的 SSH 文件目录 → 发布到 MQTT Topic
2. 订阅小陈的 MQTT Topic → 写入 SSH 文件目录
3. 实现 MQTT 和文件系统的双向同步

目录映射:
  SSH 文件                    →  MQTT Topic
  to-xiaochen/*.json          →  lobster/coach/xiaochen/cmd
  from-xiaochen/*.json        →  lobster/xiaochen/coach/ack
  training/xiaochen/inbox/    →  lobster/training/xiaochen/task
  training/xiaochen/result/   →  lobster/training/xiaochen/result

使用:
    python3 core/mqtt_file_bridge.py start    # 启动桥接
    python3 core/mqtt_file_bridge.py test     # 测试
"""

import sys
import os
import json
import time
import logging
import hashlib
import signal
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.mqtt_client_base import MqttClientBase, Topics, parse_message

# ============================================================================
# 配置
# ============================================================================

SHARED_DIR = "/home/admin/go-training/shared/"
STUDENTS = {
    "xiaochen": {
        "to_dir": os.path.join(SHARED_DIR, "to-xiaochen/"),       # 教练→小陈
        "from_dir": os.path.join(SHARED_DIR, "from-xiaochen/"),   # 小陈→教练
        "training_dir": os.path.join(SHARED_DIR, "training/xiaochen/inbox/"),
    },
}

BRIDGE_STATE_FILE = "/home/admin/go-training/shared/mqtt_bridge_state.json"


class MqttFileBridge:
    """MQTT-文件双向桥接器"""

    def __init__(self, broker_host="127.0.0.1", broker_port=1883):
        self.client = MqttClientBase(
            node_id="mqtt_bridge",
            broker_host=broker_host,
            broker_port=broker_port,
        )
        self.logger = logging.getLogger("mqtt_bridge")
        self._running = False
        self._file_hashes = {}  # {filepath: md5} 用于去重
        self._state = {"processed": 0, "errors": 0, "last_sync": None}

        # 确保目录存在
        for student_cfg in STUDENTS.values():
            for d in [student_cfg["to_dir"], student_cfg["from_dir"], student_cfg["training_dir"]]:
                os.makedirs(d, exist_ok=True)

        # 加载文件哈希状态
        self._load_state()

    def _load_state(self):
        try:
            if os.path.exists(BRIDGE_STATE_FILE):
                with open(BRIDGE_STATE_FILE) as f:
                    self._file_hashes = json.load(f).get("hashes", {})
        except Exception:
            self._file_hashes = {}

    def _save_state(self):
        try:
            with open(BRIDGE_STATE_FILE, "w") as f:
                json.dump({"hashes": self._file_hashes, "state": self._state}, f)
        except Exception:
            pass

    def _file_hash(self, filepath):
        """计算文件哈希"""
        try:
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return None

    def _is_new_file(self, filepath):
        """检查是否是新文件（去重）"""
        h = self._file_hash(filepath)
        if h and self._file_hashes.get(filepath) != h:
            return True
        return False

    def _mark_processed(self, filepath):
        """标记文件已处理"""
        h = self._file_hash(filepath)
        if h:
            self._file_hashes[filepath] = h

    # =========================================================================
    # 文件 → MQTT (监控 SSH 目录，发布到 MQTT)
    # =========================================================================

    def scan_and_publish(self):
        """扫描文件目录并发布到 MQTT"""
        published = 0
        for student_id, cfg in STUDENTS.items():
            # 教练→学员: to-xiaochen/ → coach/{student}/cmd
            for f in Path(cfg["to_dir"]).glob("*.json"):
                filepath = str(f)
                if self._is_new_file(filepath):
                    try:
                        with open(filepath) as fh:
                            data = json.load(fh)
                        topic = Topics.coach_to_student(student_id)
                        msg_type = data.get("type", "file_message")
                        self.client.publish_message(
                            topic, msg_type, "zhugema", student_id,
                            data.get("payload", data)
                        )
                        self._mark_processed(filepath)
                        published += 1
                        self.logger.info("[文件→MQTT] {} → {}".format(filepath, topic))
                    except Exception as e:
                        self.logger.error("发布文件失败 {}: {}".format(filepath, e))
                        self._state["errors"] += 1

            # 学员→教练: from-xiaochen/ → {student}/coach/ack
            for f in Path(cfg["from_dir"]).glob("*.json"):
                filepath = str(f)
                if self._is_new_file(filepath):
                    try:
                        with open(filepath) as fh:
                            data = json.load(fh)
                        topic = Topics.student_to_coach(student_id)
                        msg_type = data.get("type", "ack")
                        self.client.publish_message(
                            topic, msg_type, student_id, "zhugema",
                            data.get("payload", data)
                        )
                        self._mark_processed(filepath)
                        published += 1
                        self.logger.info("[文件→MQTT] {} → {}".format(filepath, topic))
                    except Exception as e:
                        self.logger.error("发布文件失败 {}: {}".format(filepath, e))
                        self._state["errors"] += 1

        if published > 0:
            self._state["processed"] += published
            self._state["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._save_state()
        return published

    # =========================================================================
    # MQTT → 文件 (订阅 MQTT，写入文件目录)
    # =========================================================================

    def _on_mqtt_to_file(self, student_id):
        """创建 MQTT→文件 处理器闭包"""
        def handler(topic, payload):
            msg = parse_message(payload)
            msg_type = msg.get("type", "unknown")

            # 确定写入目录
            if "coach" in topic and student_id in topic:
                # 教练→学员
                target_dir = STUDENTS[student_id]["to_dir"]
            elif "training" in topic:
                target_dir = STUDENTS[student_id]["training_dir"]
            else:
                target_dir = STUDENTS[student_id]["from_dir"]

            # 写入文件
            filename = "mqtt_{}_{}.json".format(
                msg.get("id", "unknown")[:8],
                datetime.now().strftime("%Y%m%d_%H%M%S")
            )
            filepath = os.path.join(target_dir, filename)
            try:
                with open(filepath, "w") as f:
                    json.dump(msg, f, ensure_ascii=False, indent=2)
                self.logger.info("[MQTT→文件] {} → {}".format(topic, filepath))
            except Exception as e:
                self.logger.error("写入文件失败: {}".format(e))

        return handler

    def setup_mqtt_subscriptions(self):
        """设置 MQTT 订阅 (MQTT→文件方向)"""
        for student_id in STUDENTS:
            handler = self._on_mqtt_to_file(student_id)
            self.client.on_message(Topics.coach_to_student(student_id), handler)
            self.client.on_message(Topics.training_task(student_id), handler)

    # =========================================================================
    # 生命周期
    # =========================================================================

    def start(self, scan_interval=5):
        """启动桥接器"""
        self._running = True
        self.client.connect()
        self.setup_mqtt_subscriptions()
        self.logger.info("MQTT-文件桥接器已启动 (扫描间隔={}s)".format(scan_interval))

        def signal_handler(signum, frame):
            self._running = False
            self._save_state()
            self.client.disconnect()
            self.logger.info("桥接器已停止")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            while self._running:
                self.scan_and_publish()
                time.sleep(scan_interval)
        except KeyboardInterrupt:
            signal_handler(None, None)

    def test(self):
        """测试桥接"""
        self.client.connect()
        time.sleep(1)

        # 创建测试文件
        test_file = os.path.join(STUDENTS["xiaochen"]["to_dir"], "bridge_test.json")
        with open(test_file, "w") as f:
            json.dump({
                "type": "system",
                "payload": {"message": "MQTT-文件桥接测试"},
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, f, ensure_ascii=False, indent=2)

        print("创建测试文件: {}".format(test_file))
        print("等待桥接扫描...")
        time.sleep(scan_interval + 2 if 'scan_interval' in dir() else 7)

        count = self.scan_and_publish()
        print("桥接发布: {} 条消息".format(count))
        print("状态: {}".format(json.dumps(self._state, ensure_ascii=False)))

        self.client.disconnect()
        print("=== 桥接测试完成 ===")


# ============================================================================
# CLI
# ============================================================================

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    if len(sys.argv) < 2:
        print("用法: python3 mqtt_file_bridge.py <start|test>")
        sys.exit(1)

    bridge = MqttFileBridge()

    if sys.argv[1] == "start":
        bridge.start()
    elif sys.argv[1] == "test":
        bridge.test()
    else:
        print("未知命令: {}".format(sys.argv[1]))
        sys.exit(1)


if __name__ == "__main__":
    main()
