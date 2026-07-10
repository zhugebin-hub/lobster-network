#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药物研制科学智能体 MQTT 集成模块

将食物过敏药物研制的6个科学智能体接入小龙虾网络MQTT通信层，
实现实时任务分发、进度上报和节点间协作。

Broker: 47.93.6.57:1883 (Mosquitto)
Topic命名空间:
  lobster/science/drug_discovery/task     — 科学任务分发
  lobster/science/drug_discovery/result   — 研究结果上报
  lobster/science/drug_discovery/status   — 节点状态心跳
  lobster/science/drug_discovery/progress — 研究进度广播
  lobster/science/drug_discovery/review   — 同行评审
"""

import json
import time
import uuid
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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

# ============================================================
# 日志配置
# ============================================================

logger = logging.getLogger("mqtt_drug_discovery")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "mqtt_drug_discovery.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)
    _console = logging.StreamHandler()
    _console.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(_console)


# ============================================================
# 药物研制6个科学智能体定义
# ============================================================

SCIENCE_AGENTS = {
    "literature_mining": "文献挖掘智能体",
    "allergen_target": "过敏原靶点智能体",
    "compound_design": "化合物设计智能体",
    "virtual_screening": "虚拟筛选智能体",
    "admet_prediction": "ADMET预测智能体",
    "toxicity_assessment": "毒性评估智能体",
}


# ============================================================
# Topic 命名空间
# ============================================================

class ScienceTopics:
    """药物研制 MQTT Topic 命名空间"""

    ROOT = "lobster/science/drug_discovery"

    @staticmethod
    def task(agent_id=None):
        """科学任务分发主题"""
        if agent_id:
            return "{}/task/{}".format(ScienceTopics.ROOT, agent_id)
        return "{}/task/+".format(ScienceTopics.ROOT)

    @staticmethod
    def result(stage=None):
        """研究结果上报主题"""
        if stage:
            return "{}/result/{}".format(ScienceTopics.ROOT, stage)
        return "{}/result/+".format(ScienceTopics.ROOT)

    @staticmethod
    def status(node_id=None):
        """节点状态心跳主题"""
        if node_id:
            return "{}/status/{}".format(ScienceTopics.ROOT, node_id)
        return "{}/status/+".format(ScienceTopics.ROOT)

    @staticmethod
    def progress():
        """研究进度广播主题"""
        return "{}/progress".format(ScienceTopics.ROOT)

    @staticmethod
    def review():
        """同行评审主题"""
        return "{}/review".format(ScienceTopics.ROOT)


# ============================================================
# 消息工具
# ============================================================

def _create_science_message(from_node, payload, msg_type="science",
                            priority="normal"):
    """创建药物研制标准 MQTT 消息

    Returns:
        dict: 包含 msg_id, from_node, timestamp, type, payload, priority 的消息字典
    """
    return {
        "msg_id": str(uuid.uuid4())[:12],
        "from_node": from_node,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": msg_type,
        "payload": payload or {},
        "priority": priority,
    }


def _topic_match(pattern, topic):
    """简单的 MQTT 主题通配符匹配 (+ 和 #)"""
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


# ============================================================
# DrugDiscoveryMQTTClient
# ============================================================

class DrugDiscoveryMQTTClient:
    """药物研制 MQTT 客户端

    将科学智能体接入小龙虾网络，支持任务分发、结果上报、
    状态心跳和进度广播。当 paho-mqtt 不可用时自动降级为
    仿真模式 (simulation mode)，所有发布操作记录到内存。

    使用:
        client = DrugDiscoveryMQTTClient("qoder")
        client.connect()
        client.publish_task("virtual_screening", {"action": "screen", "target": "FceRI"})
    """

    def __init__(self, node_id, broker_host="47.93.6.57", broker_port=1883):
        self.node_id = node_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = "lobster-science-{}".format(node_id)

        self._client = None
        self._running = False
        self._simulation = not HAS_PAHO
        self._callbacks = {}       # topic_pattern -> [callback_fn]
        self._sim_messages = []    # 仿真模式消息记录

        # 日志
        self.logger = logging.getLogger("mqtt.science.{}".format(node_id))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        if self._simulation:
            self.logger.warning(
                "paho-mqtt 未安装，进入仿真模式 (simulation mode)")
        else:
            self._setup_mqtt_client()

    def _setup_mqtt_client(self):
        """初始化 paho-mqtt 客户端 (兼容 1.x 和 2.x)"""
        try:
            self._client = mqtt.Client(
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                client_id=self.client_id,
                clean_session=True,
                protocol=mqtt.MQTTv311,
            )
        except (AttributeError, TypeError):
            self._client = mqtt.Client(
                client_id=self.client_id,
                clean_session=True,
                protocol=mqtt.MQTTv311,
            )

        # 遗嘱消息
        self._client.will_set(
            topic=ScienceTopics.status(self.node_id),
            payload=json.dumps({
                "node_id": self.node_id,
                "status": "offline",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, ensure_ascii=False),
            qos=0,
            retain=True,
        )

        # 回调
        def on_connect(client, userdata, flags, rc, properties=None):
            self.logger.info("Connected to broker (rc={})".format(rc))
            # 重新订阅已注册的 topic
            for pattern in self._callbacks:
                client.subscribe(pattern, 1)

        def on_message(client, userdata, msg):
            try:
                payload_str = msg.payload.decode("utf-8")
                data = json.loads(payload_str)
                for pattern, cbs in self._callbacks.items():
                    if _topic_match(pattern, msg.topic):
                        for cb in cbs:
                            try:
                                cb(msg.topic, data)
                            except Exception as e:
                                self.logger.error("Callback error: {}".format(e))
            except Exception as e:
                self.logger.error("on_message error: {}".format(e))

        self._client.on_connect = on_connect
        self._client.on_message = on_message

    # ----------------------------------------------------------
    # 连接 / 断开
    # ----------------------------------------------------------

    def connect(self):
        """连接到 MQTT Broker

        Returns:
            bool: 连接是否成功 (仿真模式始终返回 True)
        """
        if self._simulation:
            self._running = True
            self.logger.info("[SIM] 仿真连接成功: {}".format(self.client_id))
            return True

        try:
            self._client.connect(self.broker_host, self.broker_port, keepalive=60)
            self._client.loop_start()
            self._running = True
            self.logger.info("Connected to {}:{} as {}".format(
                self.broker_host, self.broker_port, self.client_id))
            return True
        except Exception as e:
            self.logger.error("Connect failed: {}".format(e))
            self._simulation = True
            self._running = True
            self.logger.warning("降级为仿真模式")
            return True

    def disconnect(self):
        """断开连接"""
        self._running = False
        if self._simulation:
            self.logger.info("[SIM] 仿真断开连接")
            return

        try:
            # 发布离线状态
            self._client.publish(
                ScienceTopics.status(self.node_id),
                json.dumps({
                    "node_id": self.node_id,
                    "status": "offline",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }, ensure_ascii=False),
                qos=0, retain=True,
            )
            self._client.loop_stop()
            self._client.disconnect()
            self.logger.info("Disconnected")
        except Exception as e:
            self.logger.error("Disconnect error: {}".format(e))

    # ----------------------------------------------------------
    # 发布方法
    # ----------------------------------------------------------

    def _publish(self, topic, message, qos=1):
        """内部发布方法

        Args:
            topic: MQTT 主题
            message: dict 消息 (自动 JSON 序列化)
            qos: QoS 级别

        Returns:
            bool: 发布是否成功
        """
        payload_str = json.dumps(message, ensure_ascii=False)

        if self._simulation:
            record = {"topic": topic, "message": message, "qos": qos}
            self._sim_messages.append(record)
            self.logger.info("[SIM] Publish [{}] ({} bytes)".format(
                topic, len(payload_str)))
            return True

        try:
            self._client.publish(topic, payload_str, qos=qos)
            self.logger.debug("Published [{}] ({} bytes)".format(
                topic, len(payload_str)))
            return True
        except Exception as e:
            self.logger.error("Publish failed [{}]: {}".format(topic, e))
            return False

    def publish_task(self, task_type, payload, target_agent=None):
        """发布科学任务

        Args:
            task_type: 任务类型 (如 "screening", "literature_search")
            payload: 任务详情 dict
            target_agent: 目标智能体ID (None 则广播给所有智能体)

        Returns:
            bool: 发布是否成功
        """
        topic = ScienceTopics.task(target_agent) if target_agent \
            else ScienceTopics.task("broadcast")
        msg = _create_science_message(
            self.node_id,
            payload={"task_type": task_type, "details": payload},
            msg_type="task",
            priority="high",
        )
        return self._publish(topic, msg, qos=1)

    def publish_result(self, stage, result_data, confidence=0.0):
        """发布研究结果

        Args:
            stage: 研究阶段 (如 "phase1_knowledge", "phase2_screening")
            result_data: 结果数据 dict
            confidence: 结果置信度 (0.0-1.0)

        Returns:
            bool: 发布是否成功
        """
        topic = ScienceTopics.result(stage)
        msg = _create_science_message(
            self.node_id,
            payload={
                "stage": stage,
                "result": result_data,
                "confidence": confidence,
            },
            msg_type="result",
        )
        return self._publish(topic, msg, qos=1)

    def publish_status(self, status_data):
        """发布节点状态心跳

        Args:
            status_data: 状态数据 dict (如 cpu, memory, active_agents 等)

        Returns:
            bool: 发布是否成功
        """
        topic = ScienceTopics.status(self.node_id)
        msg = _create_science_message(
            self.node_id,
            payload={
                "node_id": self.node_id,
                "status": "alive",
                **status_data,
            },
            msg_type="status",
        )
        return self._publish(topic, msg, qos=0)

    def publish_progress(self, phase, progress_pct, findings):
        """广播研究进度

        Args:
            phase: 当前阶段名称 (如 "Phase 1: 知识构建")
            progress_pct: 进度百分比 (0-100)
            findings: 当前发现列表

        Returns:
            bool: 发布是否成功
        """
        topic = ScienceTopics.progress()
        msg = _create_science_message(
            self.node_id,
            payload={
                "phase": phase,
                "progress_pct": progress_pct,
                "findings": findings,
            },
            msg_type="progress",
        )
        return self._publish(topic, msg, qos=0)

    def publish_review(self, task_id, review_data):
        """发布同行评审

        Args:
            task_id: 被评审的任务ID
            review_data: 评审数据 dict

        Returns:
            bool: 发布是否成功
        """
        topic = ScienceTopics.review()
        msg = _create_science_message(
            self.node_id,
            payload={
                "task_id": task_id,
                "review": review_data,
            },
            msg_type="review",
        )
        return self._publish(topic, msg, qos=1)

    # ----------------------------------------------------------
    # 订阅方法
    # ----------------------------------------------------------

    def subscribe_tasks(self, callback):
        """订阅任务消息

        Args:
            callback: 回调函数 callback(topic, data)
        """
        pattern = ScienceTopics.task()  # task/+
        self._subscribe(pattern, callback)

    def subscribe_results(self, callback):
        """订阅研究结果消息

        Args:
            callback: 回调函数 callback(topic, data)
        """
        pattern = ScienceTopics.result()  # result/+
        self._subscribe(pattern, callback)

    def _subscribe(self, pattern, callback):
        """内部订阅方法"""
        if pattern not in self._callbacks:
            self._callbacks[pattern] = []
        self._callbacks[pattern].append(callback)

        if self._simulation:
            self.logger.info("[SIM] Subscribe to [{}]".format(pattern))
            return

        if self._running:
            self._client.subscribe(pattern, 1)
            self.logger.info("Subscribed to [{}]".format(pattern))

    def start_listening(self):
        """启动消息监听 (非阻塞)

        仿真模式下仅标记为运行状态。
        """
        if self._simulation:
            self._running = True
            self.logger.info("[SIM] 开始监听")
            return

        if not self._running:
            self.logger.warning("未连接，请先调用 connect()")
            return

        # paho loop_start 已在 connect() 中调用
        self.logger.info("Listening on {} topic(s)".format(len(self._callbacks)))

    @property
    def is_simulation(self):
        """是否在仿真模式"""
        return self._simulation

    @property
    def simulation_messages(self):
        """仿真模式消息记录 (只读)"""
        return list(self._sim_messages)


# ============================================================
# DrugDiscoveryCoordinator
# ============================================================

class DrugDiscoveryCoordinator:
    """药物研制 MQTT 协调器

    负责通过 MQTT 编排多智能体协作流程，包括阶段启动、
    任务分配、结果收集和进度广播。

    使用:
        coord = DrugDiscoveryCoordinator("qoder")
        coord.start_phase(1, "知识构建")
        coord.assign_task("literature_mining", "literature_search", {...})
        results = coord.collect_results(timeout=120)
    """

    def __init__(self, node_id):
        self.node_id = node_id
        self.mqtt = DrugDiscoveryMQTTClient(node_id)
        self._collected_results = []  # type: List[Dict]
        self._node_statuses = {}      # type: Dict[str, Dict]
        self._phase_info = {}         # type: Dict[str, Any]

        self.logger = logging.getLogger("coordinator.{}".format(node_id))
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                "%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def start_phase(self, phase_num, phase_name):
        """宣告研究阶段启动

        Args:
            phase_num: 阶段编号 (1, 2, 3)
            phase_name: 阶段名称 (如 "知识构建")
        """
        self._phase_info = {
            "phase_num": phase_num,
            "phase_name": phase_name,
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.mqtt.publish_progress(
            phase="Phase {}: {}".format(phase_num, phase_name),
            progress_pct=0,
            findings=["阶段启动"],
        )
        self.logger.info("Phase {} 启动: {}".format(phase_num, phase_name))

    def assign_task(self, agent_id, task_type, task_data):
        """向智能体分配任务

        Args:
            agent_id: 目标智能体ID (如 "literature_mining")
            task_type: 任务类型
            task_data: 任务数据 dict

        Returns:
            bool: 发布是否成功
        """
        if agent_id not in SCIENCE_AGENTS:
            self.logger.warning("未知智能体: {}".format(agent_id))

        result = self.mqtt.publish_task(task_type, task_data, target_agent=agent_id)
        self.logger.info("任务已分配: {} -> {} ({})".format(
            agent_id, task_type, "ok" if result else "fail"))
        return result

    def collect_results(self, timeout=300):
        """收集各智能体上报的结果 (带超时)

        Args:
            timeout: 超时时间 (秒)

        Returns:
            list: 收集到的结果列表
        """
        collected = []
        lock = threading.Lock()

        def on_result(topic, data):
            with lock:
                collected.append(data)
                self.logger.info("收到结果: {} (共{}条)".format(
                    topic, len(collected)))

        self.mqtt.subscribe_results(on_result)

        self.logger.info("开始收集结果 (超时 {}s)...".format(timeout))
        deadline = time.time() + timeout

        while time.time() < deadline:
            time.sleep(1)
            with lock:
                if len(collected) >= len(SCIENCE_AGENTS):
                    break

        self.logger.info("结果收集完成: 收到 {}/{} 条".format(
            len(collected), len(SCIENCE_AGENTS)))
        self._collected_results = collected
        return collected

    def broadcast_progress(self, phase, findings_count):
        """向网络广播研究进度

        Args:
            phase: 当前阶段名称
            findings_count: 发现数量
        """
        progress_pct = min(100, findings_count * 5)
        self.mqtt.publish_progress(
            phase=phase,
            progress_pct=progress_pct,
            findings=["已发现 {} 项结果".format(findings_count)],
        )
        self.logger.info("进度广播: {} ({}%)".format(phase, progress_pct))

    def run_phase1_knowledge_building(self):
        """运行 Phase 1: 知识构建 (通过 MQTT 协调)

        分配文献挖掘和靶点分析任务，收集知识构建阶段的结果。
        """
        self.start_phase(1, "知识构建")

        # 分配文献挖掘任务
        self.assign_task("literature_mining", "literature_search", {
            "scope": "2020-2026年食物过敏药物研发文献",
            "sources": ["PubMed", "Web of Science", "ClinicalTrials.gov"],
            "target_count": 200,
        })

        # 分配靶点分析任务
        self.assign_task("allergen_target", "target_analysis", {
            "pathways": ["Th2免疫通路", "IgE-FceRI通路", "肥大细胞激活通路"],
            "priority_targets": ["FceRI", "IgE", "Syk", "BTK", "KIT"],
        })

        self.broadcast_progress("Phase 1: 知识构建", 5)
        self.logger.info("Phase 1 任务已全部下发")

    def run_phase2_screening(self):
        """运行 Phase 2: 计算筛选 (通过 MQTT 协调)

        分配虚拟筛选和化合物设计任务。
        """
        self.start_phase(2, "计算筛选")

        # 分配虚拟筛选任务
        self.assign_task("virtual_screening", "virtual_screening", {
            "compound_lib": "PubChem + ZINC",
            "targets": ["FceRI", "IgE", "Syk"],
            "top_n": 100,
        })

        # 分配化合物设计任务
        self.assign_task("compound_design", "compound_design", {
            "strategy": "IgE阻断肽 + FceRI拮抗剂",
            "optimization": "RDKit + MM-PBSA",
            "target_count": 20,
        })

        # 分配 ADMET 预测任务
        self.assign_task("admet_prediction", "admet_screening", {
            "filters": ["Lipinski", "CYP450", "hERG"],
            "compound_set": "phase2_hits",
        })

        self.broadcast_progress("Phase 2: 计算筛选", 3)
        self.logger.info("Phase 2 任务已全部下发")

    def get_network_status(self):
        """获取所有参与节点的状态

        Returns:
            dict: {node_id: status_data} 映射
        """
        return dict(self._node_statuses)


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("药物研制科学智能体 MQTT 集成 — 演示")
    print("=" * 60)

    # 1. 创建协调器 (qoder 节点)
    coord = DrugDiscoveryCoordinator("qoder")
    connected = coord.mqtt.connect()
    print("\n[1] 连接状态: {} ({})".format(
        "成功" if connected else "失败",
        "仿真模式" if coord.mqtt.is_simulation else "实时模式"))

    # 2. 发布科学任务
    coord.mqtt.publish_task("virtual_screening", {
        "target": "FceRI",
        "compound_library": "PubChem",
        "docking_tool": "AutoDock Vina",
    }, target_agent="virtual_screening")
    print("[2] 已发布虚拟筛选任务 -> virtual_screening")

    # 3. 发布研究结果
    coord.mqtt.publish_result("phase2_screening", {
        "hits_count": 42,
        "top_compound": "CID_12345",
        "binding_affinity": -9.2,
    }, confidence=0.85)
    print("[3] 已发布筛选结果 (置信度 0.85)")

    # 4. 发布节点状态心跳
    coord.mqtt.publish_status({
        "active_agents": ["virtual_screening", "compound_design"],
        "cpu_usage": 45.2,
        "memory_mb": 2048,
    })
    print("[4] 已发布节点状态心跳")

    # 5. 广播研究进度
    coord.mqtt.publish_progress(
        phase="Phase 2: 计算筛选",
        progress_pct=65,
        findings=["已筛选 50000 化合物", "Top 42 hits 待验证"],
    )
    print("[5] 已广播研究进度 (65%)")

    # 6. 发布同行评审
    coord.mqtt.publish_review("task_001", {
        "verdict": "approve",
        "comments": "方法学合理，建议补充交叉反应分析",
        "reviewer": "qoder",
    })
    print("[6] 已发布同行评审")

    # 打印仿真消息摘要
    if coord.mqtt.is_simulation:
        msgs = coord.mqtt.simulation_messages
        print("\n--- 仿真消息记录 ({} 条) ---".format(len(msgs)))
        for i, m in enumerate(msgs, 1):
            print("  {}. [{}] type={} qos={}".format(
                i, m["topic"],
                m["message"].get("type", "?"),
                m["qos"]))

    # 7. 断开连接
    coord.mqtt.disconnect()
    print("\n[完成] 演示结束")
