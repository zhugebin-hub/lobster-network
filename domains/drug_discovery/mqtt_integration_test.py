#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
药物研制 MQTT 集成测试

测试内容:
1. MQTT 客户端初始化 (含仿真模式降级)
2. Topic 生成 (5种主题类型)
3. 消息格式校验 (JSON 序列化)
4. 仿真模式发布/订阅
5. 汇总测试结果
"""

import sys
import json
import traceback
from pathlib import Path

# 确保可以导入同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from domains.drug_discovery.mqtt_drug_discovery import (
    ScienceTopics,
    DrugDiscoveryMQTTClient,
    DrugDiscoveryCoordinator,
    _create_science_message,
    SCIENCE_AGENTS,
)

# ============================================================
# 测试框架
# ============================================================

_results = []  # (test_name, passed, detail)


def _run_test(name, fn):
    """运行单个测试并记录结果"""
    try:
        fn()
        _results.append((name, True, ""))
        print("  PASS  {}".format(name))
    except Exception as e:
        _results.append((name, False, str(e)))
        print("  FAIL  {} -- {}".format(name, e))
        traceback.print_exc()


# ============================================================
# 测试用例
# ============================================================

def test_client_init():
    """测试1: MQTT 客户端初始化"""
    client = DrugDiscoveryMQTTClient("test_node")
    assert client.node_id == "test_node", "node_id 不匹配"
    assert client.client_id == "lobster-science-test_node", "client_id 不匹配"
    # 不管有没有 paho-mqtt，初始化都不应报错
    print("       simulation={}".format(client.is_simulation))


def test_topic_task():
    """测试2a: task 主题生成"""
    assert ScienceTopics.task() == "lobster/science/drug_discovery/task/+"
    assert ScienceTopics.task("virtual_screening") == \
        "lobster/science/drug_discovery/task/virtual_screening"


def test_topic_result():
    """测试2b: result 主题生成"""
    assert ScienceTopics.result() == "lobster/science/drug_discovery/result/+"
    assert ScienceTopics.result("phase1_knowledge") == \
        "lobster/science/drug_discovery/result/phase1_knowledge"


def test_topic_status():
    """测试2c: status 主题生成"""
    assert ScienceTopics.status() == "lobster/science/drug_discovery/status/+"
    assert ScienceTopics.status("qoder") == \
        "lobster/science/drug_discovery/status/qoder"


def test_topic_progress():
    """测试2d: progress 主题生成"""
    assert ScienceTopics.progress() == "lobster/science/drug_discovery/progress"


def test_topic_review():
    """测试2e: review 主题生成"""
    assert ScienceTopics.review() == "lobster/science/drug_discovery/review"


def test_message_format():
    """测试3: 消息格式校验"""
    msg = _create_science_message("qoder", {"key": "value"}, msg_type="task")
    # 必须包含标准字段
    for field in ("msg_id", "from_node", "timestamp", "type", "payload", "priority"):
        assert field in msg, "缺少字段: {}".format(field)
    assert msg["from_node"] == "qoder"
    assert msg["type"] == "task"
    assert msg["payload"]["key"] == "value"
    # JSON 可序列化
    serialized = json.dumps(msg, ensure_ascii=False)
    assert len(serialized) > 0
    # 反序列化回来
    parsed = json.loads(serialized)
    assert parsed["msg_id"] == msg["msg_id"]


def test_publish_simulation():
    """测试4: 仿真模式发布"""
    client = DrugDiscoveryMQTTClient("test_pub")
    client.connect()
    assert client.is_simulation, "期望仿真模式"

    # 发布5种消息类型
    ok1 = client.publish_task("screening", {"target": "FceRI"}, "virtual_screening")
    ok2 = client.publish_result("phase2", {"hits": 10}, confidence=0.9)
    ok3 = client.publish_status({"cpu": 50.0})
    ok4 = client.publish_progress("Phase 2", 60, ["found 10 hits"])
    ok5 = client.publish_review("task_01", {"verdict": "ok"})

    assert all([ok1, ok2, ok3, ok4, ok5]), "部分发布失败"
    assert len(client.simulation_messages) == 5, \
        "期望5条消息, 实际{}条".format(len(client.simulation_messages))

    # 验证每条消息都是合法 JSON
    for rec in client.simulation_messages:
        json.dumps(rec["message"], ensure_ascii=False)

    client.disconnect()


def test_coordinator_init():
    """测试5: 协调器初始化"""
    coord = DrugDiscoveryCoordinator("qoder")
    assert coord.node_id == "qoder"
    assert coord.mqtt is not None
    assert len(SCIENCE_AGENTS) == 6, "应有6个科学智能体"


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("药物研制 MQTT 集成测试")
    print("=" * 60)

    tests = [
        ("客户端初始化", test_client_init),
        ("Topic: task", test_topic_task),
        ("Topic: result", test_topic_result),
        ("Topic: status", test_topic_status),
        ("Topic: progress", test_topic_progress),
        ("Topic: review", test_topic_review),
        ("消息格式校验", test_message_format),
        ("仿真模式发布", test_publish_simulation),
        ("协调器初始化", test_coordinator_init),
    ]

    for name, fn in tests:
        _run_test(name, fn)

    # 汇总
    passed = sum(1 for _, p, _ in _results if p)
    failed = sum(1 for _, p, _ in _results if not p)
    total = len(_results)

    print("\n" + "=" * 60)
    print("结果: {}/{} 通过, {} 失败".format(passed, total, failed))
    if failed:
        print("\n失败的测试:")
        for name, p, detail in _results:
            if not p:
                print("  - {}: {}".format(name, detail))
    print("=" * 60)

    sys.exit(0 if failed == 0 else 1)
