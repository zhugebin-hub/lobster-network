#!/usr/bin/env python3
"""
小龙虾网络 MQTT 集成测试脚本
=============================
测试 LobsterMQTTClient 和 GoMQTTBridge 的完整功能链路。
"""

import json
import sys
import os
import time
import threading
import queue as queue_module

# 添加项目路径
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "lobster_network"))

from lobster_mqtt_core import (
    LobsterMQTTClient, LobsterMessage, MessageType,
    Topic, TopicPrefix, create_coach_client, create_student_client,
)
from lobster_mqtt_go_bridge import MQTTGoBridge


# ==================== 工具函数 ====================

def ensure_mosquitto_running():
    """确保 mosquitto 运行在 1883 端口，如果未运行则尝试启动。"""
    import subprocess
    result = subprocess.run(
        ["lsof", "-i", ":1883", "-t"],
        capture_output=True, text=True,
    )
    if result.stdout.strip():
        print("  ✓ mosquitto 已在运行 (PID: {})".format(result.stdout.strip()))
        return True

    # 尝试通过 brew services 启动
    print("  ! mosquitto 未运行，尝试启动...")
    r = subprocess.run(
        ["brew", "services", "start", "mosquitto"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        time.sleep(3)
        # 验证
        r2 = subprocess.run(["lsof", "-i", ":1883", "-t"], capture_output=True, text=True)
        if r2.stdout.strip():
            print("  ✓ mosquitto 启动成功")
            return True

    # 尝试直接启动
    mosquitto_bin = (
        "/opt/homebrew/sbin/mosquitto"
        if os.path.exists("/opt/homebrew/sbin/mosquitto")
        else "/usr/local/sbin/mosquitto"
    )
    config_file = os.path.join(REPO_ROOT, "config", "mosquitto.conf")
    if os.path.exists(mosquitto_bin):
        subprocess.Popen(
            [mosquitto_bin, "-c", config_file, "-d"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        r2 = subprocess.run(["lsof", "-i", ":1883", "-t"], capture_output=True, text=True)
        if r2.stdout.strip():
            print("  ✓ mosquitto 直接启动成功")
            return True

    print("  ✗ 无法启动 mosquitto")
    return False


def banner(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def pass_fail(condition, label):
    status = "✓ PASS" if condition else "✗ FAIL"
    print(f"  [{status}] {label}")
    return condition


# ==================== 测试 1: 连接 & 心跳 ====================

def test_1_connect_and_heartbeat():
    banner("测试1: 连接 Broker → 发布心跳 → 验证 retain 消息")

    coach = create_coach_client("zhugema-test", broker_host="localhost", broker_port=1883)
    xiaochen = create_student_client("xiaochen-test", "30级", broker_host="localhost", broker_port=1883)

    coach_ok = coach.connect()
    xc_ok = xiaochen.connect()

    results = []
    results.append(pass_fail(coach_ok, "教练连接 broker"))
    results.append(pass_fail(xc_ok, "小陈连接 broker"))

    if not (coach_ok and xc_ok):
        print("  ! 连接失败，跳过后续验证")
        return all(results)

    # 订阅心跳
    xiaochen.subscribe_system()
    hb_received = queue_module.Queue()

    @xiaochen.on(MessageType.HEARTBEAT)
    def on_hb(msg: LobsterMessage):
        hb_received.put(msg)

    # 发布在线心跳
    coach._publish_heartbeat("online", "test")
    xiaochen._publish_heartbeat("online", "test")

    time.sleep(2)

    hb_count = hb_received.qsize()
    results.append(pass_fail(hb_count >= 1, f"心跳消息接收 (收到 {hb_count} 条)"))

    # 检查 retain 消息（通过节点状态）
    online_nodes = xiaochen.get_online_nodes()
    print(f"  [{('✓' if len(online_nodes) >= 1 else '✗')}] 在线节点数: {len(online_nodes)}")
    for n in online_nodes:
        print(f"      - {n.node_id}: {n.status} ({n.role})")
    results.append(pass_fail(len(online_nodes) >= 1, "在线节点感知"))

    coach.disconnect()
    xiaochen.disconnect()
    time.sleep(1)
    return all(results)


# ==================== 测试 2: 训练任务发布/接收 ====================

def test_2_training_task_pub_sub():
    banner("测试2: 训练任务发布/接收")

    coach = create_coach_client("zhugema-test2", broker_host="localhost", broker_port=1883)
    xiaochen = create_student_client("xiaochen-test2", "30级", broker_host="localhost", broker_port=1883)

    coach.connect()
    xiaochen.connect()

    task_received = queue_module.Queue()

    # 小陈订阅训练任务
    xiaochen._subscribe(Topic.training_task("xiaochen-test2"))

    @xiaochen.on(MessageType.TRAINING_TASK)
    def on_task(msg: LobsterMessage):
        task_received.put(msg)

    # 确保订阅生效
    time.sleep(1)

    # 教练发布训练任务
    task_payload = {
        "task_id": "test-task-001",
        "lesson_type": "life_death",
        "title": "直三和曲三死活判断",
        "deck": [
            {"id": "ld-001", "type": "life_death", "diagram": "直三", "answer": "死棋"},
            {"id": "ld-002", "type": "life_death", "diagram": "曲三", "answer": "死棋"},
            {"id": "ld-003", "type": "life_death", "diagram": "直四", "answer": "活棋"},
        ],
    }
    msg_id = coach.publish_training_task("xiaochen-test2", task_payload)
    print(f"  教练发布任务: {msg_id}")

    time.sleep(3)

    results = []
    try:
        received = task_received.get(timeout=5)
        results.append(pass_fail(True, "训练任务被接收"))
        results.append(pass_fail(
            received.payload.get("task_id") == "test-task-001",
            f"任务 ID 匹配: {received.payload.get('task_id')}"
        ))
        results.append(pass_fail(
            received.payload.get("lesson_type") == "life_death",
            "任务类型匹配: life_death"
        ))
        results.append(pass_fail(
            len(received.payload.get("deck", [])) == 3,
            "题目数量: 3 题"
        ))
    except queue_module.Empty:
        results.append(pass_fail(False, "训练任务被接收 (超时)"))

    coach.disconnect()
    xiaochen.disconnect()
    time.sleep(1)
    return all(results)


# ==================== 测试 3: 对局走子 ====================

def test_3_match_moves():
    banner("测试3: 对局走子 — 模拟两步走子")

    black_player = create_student_client("zhuguxia-test", "初段", broker_host="localhost", broker_port=1883)
    white_player = create_student_client("xiaochen-test3", "30级", broker_host="localhost", broker_port=1883)

    black_player.connect()
    white_player.connect()

    match_id = "test-match-001"
    move_received = queue_module.Queue()

    # 双方订阅对局主题
    black_player._subscribe(f"lobster/go/matches/{match_id}/move")
    white_player._subscribe(f"lobster/go/matches/{match_id}/move")

    @white_player.on(MessageType.MATCH_MOVE)
    def on_white_move(msg: LobsterMessage):
        move_received.put(msg)

    @black_player.on(MessageType.MATCH_MOVE)
    def on_black_move(msg: LobsterMessage):
        move_received.put(msg)

    time.sleep(1)

    # 模拟两步走子
    move1_id = black_player.publish_match_move(
        match_id, "xiaochen-test3",
        {"match_id": match_id, "player": "zhuguxia-test", "color": "black",
         "coord": "Q16", "reason": "星位占角，稳健布局"},
    )
    print(f"  诸葛虾落子 Q16: {move1_id}")

    time.sleep(1)

    move2_id = white_player.publish_match_move(
        match_id, "zhuguxia-test",
        {"match_id": match_id, "player": "xiaochen-test3", "color": "white",
         "coord": "D4", "reason": "对角星，应对黑棋布局"},
    )
    print(f"  小陈落子 D4: {move2_id}")

    time.sleep(3)

    results = []
    move_count = move_received.qsize()
    results.append(pass_fail(move_count >= 2, f"对局消息接收 (收到 {move_count} 步, 期望 ≥2)"))

    moves = []
    while not move_received.empty():
        moves.append(move_received.get_nowait())

    coord_ok = False
    reason_ok = False
    for m in moves:
        if m.payload.get("coord") == "Q16" and m.payload.get("color") == "black":
            coord_ok = True
        if m.payload.get("reason"):
            reason_ok = True

    results.append(pass_fail(coord_ok, "走子坐标 Q16(黑) 验证"))
    results.append(pass_fail(reason_ok, "走子理由字段验证"))

    black_player.disconnect()
    white_player.disconnect()
    time.sleep(1)
    return all(results)


# ==================== 测试 4: 多学员消息隔离 ====================

def test_4_message_isolation():
    banner("测试4: 多学员消息隔离")

    coach = create_coach_client("zhugema-test4", broker_host="localhost", broker_port=1883)
    xiaochen = create_student_client("xiaochen-test4", "30级", broker_host="localhost", broker_port=1883)
    zhuguxia = create_student_client("zhuguxia-test4", "初段", broker_host="localhost", broker_port=1883)
    qoder = create_student_client("qoder-test4", "25级", broker_host="localhost", broker_port=1883)

    coach.connect()
    xiaochen.connect()
    zhuguxia.connect()
    qoder.connect()

    # 每个学员各自订阅自己的训练 topic
    xc_queue = queue_module.Queue()
    zgx_queue = queue_module.Queue()
    qd_queue = queue_module.Queue()

    xiaochen._subscribe(Topic.training_task("xiaochen-test4"))
    zhuguxia._subscribe(Topic.training_task("zhuguxia-test4"))
    qoder._subscribe(Topic.training_task("qoder-test4"))

    @xiaochen.on(MessageType.TRAINING_TASK)
    def on_xc(msg): xc_queue.put(msg)

    @zhuguxia.on(MessageType.TRAINING_TASK)
    def on_zgx(msg): zgx_queue.put(msg)

    @qoder.on(MessageType.TRAINING_TASK)
    def on_qd(msg): qd_queue.put(msg)

    time.sleep(1)

    # 教练向三个学员分别发布任务
    coach.publish_training_task("xiaochen-test4", {
        "task_id": "task-xc-001", "lesson_type": "life_death",
        "title": "小陈专属 - 直三死活",
    })
    coach.publish_training_task("zhuguxia-test4", {
        "task_id": "task-zgx-001", "lesson_type": "tesuji",
        "title": "诸葛虾专属 - 手筋练习",
    })
    coach.publish_training_task("qoder-test4", {
        "task_id": "task-qd-001", "lesson_type": "joseki",
        "title": "qoder 专属 - 定式学习",
    })

    print("  教练已发布 3 条专属任务")
    time.sleep(3)

    results = []

    # 验证小陈只收到自己的
    try:
        xc_msg = xc_queue.get(timeout=3)
        xc_ok = xc_msg.payload.get("task_id") == "task-xc-001"
        results.append(pass_fail(xc_ok, f"小陈收到专属任务: {xc_msg.payload.get('title')}"))
    except queue_module.Empty:
        results.append(pass_fail(False, "小陈收到专属任务 (超时)"))

    # 验证诸葛虾只收到自己的
    try:
        zgx_msg = zgx_queue.get(timeout=3)
        zgx_ok = zgx_msg.payload.get("task_id") == "task-zgx-001"
        results.append(pass_fail(zgx_ok, f"诸葛虾收到专属任务: {zgx_msg.payload.get('title')}"))
    except queue_module.Empty:
        results.append(pass_fail(False, "诸葛虾收到专属任务 (超时)"))

    # 验证 qoder 只收到自己的
    try:
        qd_msg = qd_queue.get(timeout=3)
        qd_ok = qd_msg.payload.get("task_id") == "task-qd-001"
        results.append(pass_fail(qd_ok, f"qoder 收到专属任务: {qd_msg.payload.get('title')}"))
    except queue_module.Empty:
        results.append(pass_fail(False, "qoder 收到专属任务 (超时)"))

    # 验证互不干扰：小陈不应收到诸葛虾或 qoder 的消息
    extra_xc = 0
    while not xc_queue.empty():
        xc_queue.get_nowait(); extra_xc += 1
    results.append(pass_fail(extra_xc == 0, f"小陈未收到他人消息 (额外消息: {extra_xc})"))

    extra_zgx = 0
    while not zgx_queue.empty():
        zgx_queue.get_nowait(); extra_zgx += 1
    results.append(pass_fail(extra_zgx == 0, f"诸葛虾未收到他人消息 (额外消息: {extra_zgx})"))

    extra_qd = 0
    while not qd_queue.empty():
        qd_queue.get_nowait(); extra_qd += 1
    results.append(pass_fail(extra_qd == 0, f"qoder 未收到他人消息 (额外消息: {extra_qd})"))

    coach.disconnect()
    xiaochen.disconnect()
    zhuguxia.disconnect()
    qoder.disconnect()
    time.sleep(1)
    return all(results)


# ==================== GoMQTTBridge 桥接测试 ====================

def test_5_bridge():
    banner("测试5: GoMQTTBridge 桥接器")

    student = MQTTGoBridge(
        node_id="xiaochen-bridge-test",
        role="agent",
        level="30级",
        broker_host="localhost",
        broker_port=1883,
    )
    student.start()
    time.sleep(2)

    results = []
    results.append(pass_fail(student.mqtt.is_connected(), "桥接器 MQTT 连接"))

    # 测试双写：发送训练结果
    msg_id = student.send_training_result(
        to_node="zhugema",
        task_id="bridge-test-001",
        result={
            "problems_solved": 3,
            "problems_correct": 2,
            "accuracy": 0.67,
        },
    )
    results.append(pass_fail(msg_id is not None, f"训练结果已发布 (msg_id={msg_id})"))

    student.stop()
    time.sleep(1)
    return all(results)


# ==================== 主入口 ====================

def main():
    print("=" * 60)
    print("  小龙虾网络 MQTT 集成测试")
    print("=" * 60)
    print(f"  Broker: localhost:1883")
    print(f"  仓库: {REPO_ROOT}")
    print()

    # 确保 mosquitto 运行
    if not ensure_mosquitto_running():
        print("\n" + "!" * 60)
        print("  mosquitto 无法启动，跳过所有测试。")
        print("  请手动执行: brew services start mosquitto")
        print("  或运行: bash scripts/deploy_mqtt.sh")
        print("!" * 60)
        sys.exit(1)

    time.sleep(1)

    results = {}
    results["测试1: 连接 & 心跳"] = test_1_connect_and_heartbeat()
    results["测试2: 训练任务发布/接收"] = test_2_training_task_pub_sub()
    results["测试3: 对局走子"] = test_3_match_moves()
    results["测试4: 多学员消息隔离"] = test_4_message_isolation()
    results["测试5: GoMQTTBridge 桥接"] = test_5_bridge()

    # 汇总
    banner("测试汇总")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    for name, ok in results.items():
        print(f"  [{('✓ PASS' if ok else '✗ FAIL')}] {name}")

    print(f"\n  结果: {passed}/{total} 通过")
    if passed == total:
        print("  🦞 所有 MQTT 集成测试通过!")
    else:
        print("  ! 部分测试失败，请检查 mosquitto 服务状态")
        sys.exit(1)


if __name__ == "__main__":
    main()
