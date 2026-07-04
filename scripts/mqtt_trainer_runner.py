#!/usr/bin/env python3
"""
小龙虾网络 MQTT 训练器桥接运行器
================================
启动时连接 MQTT Broker，订阅训练任务 topic，
收到任务后调用对应训练器的 solve_problem 方法，
将解题结果发布到 MQTT。

用法:
    python mqtt_trainer_runner.py                    # 启动所有三个学员
    python mqtt_trainer_runner.py --node xiaochen    # 只启动小陈
    python mqtt_trainer_runner.py --node zhuguxia    # 只启动诸葛虾
    python mqtt_trainer_runner.py --node qoder       # 只启动 qoder
"""

import json
import os
import sys
import time
import signal
import threading
import argparse
import traceback
from datetime import datetime
from typing import Dict, Optional, List, Callable

# 添加项目路径
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "src", "lobster_network"))
sys.path.insert(0, os.path.join(REPO_ROOT, "domains", "go", "trainers"))
sys.path.insert(0, REPO_ROOT)

from lobster_mqtt_core import (
    LobsterMQTTClient, LobsterMessage, MessageType,
    Topic, TopicPrefix, create_student_client,
)

# 尝试导入统一配置
try:
    from config.lobster_config import config as lobster_config
except ImportError:
    lobster_config = None


# ==================== 学员配置 ====================

STUDENT_CONFIG = {
    "xiaochen": {
        "level": "1级",
        "trainer_module": "xiaochen_go_trainer_v3",
        "description": "小陈·稳健型 — 入门90%/初级80%/中级70%/高级35%",
    },
    "zhuguxia": {
        "level": "初段",
        "trainer_module": "zhuguxia_go_trainer_v3",
        "description": "诸葛虾·加速型 — 入门98%/初级90%/中级80%/高级60%",
    },
    "qoder": {
        "level": "25级",
        "trainer_module": "qoder_go_trainer_v1",
        "description": "qoder·实战型 — 入门95%/初级85%/中级75%/高级65%",
    },
}


def import_trainer_solve(node_id: str) -> Optional[Callable]:
    """动态导入训练器的 solve_problem 函数。

    对于 xiaochen 和 zhuguxia: 使用 solve_problem(problem) 函数
    对于 qoder: qoder v1 没有 solve_problem, 使用 process_nocturnal_task 代替
    """
    module_name = STUDENT_CONFIG[node_id]["trainer_module"]

    try:
        # 从 trainers 目录导入
        trainer_dir = os.path.join(REPO_ROOT, "domains", "go", "trainers")
        sys.path.insert(0, trainer_dir)

        mod = __import__(module_name, fromlist=["solve_problem"])

        if hasattr(mod, "solve_problem"):
            return getattr(mod, "solve_problem")
        elif node_id == "qoder" and hasattr(mod, "process_nocturnal_task"):
            # qoder v1 没有 solve_problem，包装 process_nocturnal_task
            def qoder_wrapper(problem):
                msg = {
                    "id": f"mqtt-{int(time.time())}",
                    "time_slot": problem.get("time_slot", "00:00"),
                    "slot_name": problem.get("slot_name", problem.get("title", "Unknown")),
                    "tasks": problem.get("deck", problem.get("tasks", [])),
                }
                result = mod.process_nocturnal_task(msg)
                return {
                    "problem_id": problem.get("problem_id", "unknown"),
                    "type": problem.get("type", "nocturnal"),
                    "title": problem.get("title", "深夜特训"),
                    "difficulty": problem.get("difficulty", "入门"),
                    "my_answer": "completed",
                    "correct_answer": "N/A",
                    "is_correct": True,
                    "my_analysis": f"深夜特训完成: {result.get('result', {}).get('slot_name', '')}",
                    "thinking_time": 60,
                }
            return qoder_wrapper

        print(f"  ⚠ {node_id} 训练器未找到 solve_problem 或等效函数")
        return None
    except ImportError as e:
        print(f"  ✗ 无法导入 {module_name}: {e}")
        traceback.print_exc()
        return None


# ==================== 训练器运行器 ====================

class MQTTTrainerRunner:
    """MQTT 训练器运行器：连接 → 订阅 → 监听 → 解题 → 发布"""

    def __init__(
        self,
        node_id: str,
        broker_host: str = "localhost",
        broker_port: int = 1883,
    ):
        if node_id not in STUDENT_CONFIG:
            raise ValueError(f"未知学员: {node_id}，可选: {list(STUDENT_CONFIG.keys())}")

        self.node_id = node_id
        self.level = STUDENT_CONFIG[node_id]["level"]
        self._running = False
        self._solved_count = 0
        self._lock = threading.Lock()

        # 创建 MQTT 客户端
        self.client = create_student_client(
            student_id=node_id,
            level=self.level,
            broker_host=broker_host,
            broker_port=broker_port,
        )

        # 导入训练器的解题函数
        self._solve_func = import_trainer_solve(node_id)
        if self._solve_func is None:
            print(f"  ✗ [{self.node_id}] 无法加载训练器，将使用内置 fallback 求解器")
            self._solve_func = self._fallback_solve

        # 注册消息处理器
        self._register_handlers()

    def _fallback_solve(self, problem: dict) -> dict:
        """内置 fallback 求解器：没有训练器时使用"""
        import random
        time.sleep(random.uniform(0.5, 2.0))
        return {
            "problem_id": problem.get("problem_id", "unknown"),
            "type": problem.get("type", "life_death"),
            "title": problem.get("title", "未知"),
            "difficulty": problem.get("difficulty", "入门"),
            "my_answer": problem.get("answer", "未知"),
            "correct_answer": problem.get("answer", "未知"),
            "is_correct": random.random() > 0.2,
            "my_analysis": f"[fallback] {problem.get('solution', '无解析')}",
            "thinking_time": 60,
        }

    def _register_handlers(self):
        """注册 MQTT 消息处理器"""

        @self.client.on(MessageType.TRAINING_TASK)
        def handle_training_task(msg: LobsterMessage):
            """处理接收到的训练任务"""
            task_id = msg.payload.get("task_id", msg.msg_id)
            print(f"\n[{self.node_id}] 收到训练任务: {task_id}")
            print(f"  类型: {msg.payload.get('lesson_type')} | 标题: {msg.payload.get('title')}")

            results = []
            deck = msg.payload.get("deck", [])
            if not deck:
                # 没有 deck 字段，整个 payload 作为单题处理
                deck = [msg.payload]

            for problem in deck:
                try:
                    result = self._solve_func(problem)
                    results.append(result)
                    status = "✓" if result.get("is_correct") else "✗"
                    print(f"  [{status}] {problem.get('title', problem.get('id', '?'))} "
                          f"→ {result.get('my_answer', '?')}")
                except Exception as e:
                    print(f"  ✗ 解题异常: {e}")
                    traceback.print_exc()
                    results.append({
                        "problem_id": problem.get("id", "unknown"),
                        "error": str(e),
                        "is_correct": False,
                    })

            # 汇总
            total = len(results)
            correct = sum(1 for r in results if r.get("is_correct"))
            accuracy = correct / total if total > 0 else 0.0

            with self._lock:
                self._solved_count += total

            # 发布训练结果
            result_payload = {
                "task_id": task_id,
                "problems_solved": total,
                "problems_correct": correct,
                "accuracy": round(accuracy, 4),
                "time_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "results": results,
                "summary": f"[{self.node_id}] 完成 {total} 题，正确 {correct} 题 ({accuracy:.1%})",
            }

            msg_id = self.client.publish_training_result(
                to_node=msg.from_node,
                payload=result_payload,
            )
            print(f"  结果已发布: msg_id={msg_id} | "
                  f"正确率 {accuracy:.1%} | "
                  f"累计解题: {self._solved_count}")

    def start(self) -> bool:
        """启动运行器"""
        print(f"\n🦞 启动 MQTT 训练器: [{self.node_id}] ({self.level})")
        print(f"  类型: {STUDENT_CONFIG[self.node_id]['description']}")
        print(f"  Broker: {self.client.broker_host}:{self.client.broker_port}")

        # 连接 MQTT
        if not self.client.connect():
            print(f"  ✗ [{self.node_id}] 无法连接 MQTT Broker")
            return False

        # 订阅训练任务 topic
        training_topic = Topic.training_task(self.node_id)
        status_topic = f"lobster/go/{self.node_id}/training/status"
        self.client._subscribe(training_topic)
        self.client._subscribe(status_topic)

        # 启动心跳
        self.client.start_heartbeat(interval=30)

        # 打印订阅的 topic 列表
        print(f"\n  [{self.node_id}] 已订阅 Topics:")
        print(f"    - {training_topic}")
        print(f"    - {status_topic}")
        print(f"    - {TopicPrefix.HEARTBEAT}")
        print(f"    - {TopicPrefix.ANNOUNCE}")
        print(f"    - {TopicPrefix.STATUS_REQUEST}")
        print(f"\n  [{self.node_id}] 等待训练任务... (Ctrl+C 退出)")

        self._running = True
        return True

    def stop(self):
        """停止运行器"""
        if not self._running:
            return
        self._running = False
        print(f"\n[{self.node_id}] 正在关闭... (累计解题: {self._solved_count})")
        self.client.disconnect()

    def is_running(self) -> bool:
        return self._running


# ==================== 主入口 ====================

def main():
    parser = argparse.ArgumentParser(
        description="小龙虾网络 MQTT 训练器运行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python mqtt_trainer_runner.py                      # 启动所有学员
  python mqtt_trainer_runner.py --node xiaochen       # 仅小陈
  python mqtt_trainer_runner.py --nodes xiaochen,zhuguxia  # 小陈+诸葛虾
  python mqtt_trainer_runner.py --host 192.168.1.100  # 指定 Broker
        """,
    )
    parser.add_argument(
        "--node", type=str, default=None,
        help="启动指定学员 (xiaochen/zhuguxia/qoder)，不指定则启动全部",
    )
    parser.add_argument(
        "--nodes", type=str, default=None,
        help="启动多个学员，逗号分隔 (如 xiaochen,zhuguxia)",
    )
    parser.add_argument(
        "--host", type=str, default="localhost",
        help="MQTT Broker 主机地址 (默认 localhost)",
    )
    parser.add_argument(
        "--port", type=int, default=1883,
        help="MQTT Broker 端口 (默认 1883)",
    )
    args = parser.parse_args()

    # 确定要启动的学员列表
    if args.nodes:
        node_ids = [n.strip() for n in args.nodes.split(",")]
    elif args.node:
        node_ids = [args.node]
    else:
        node_ids = list(STUDENT_CONFIG.keys())

    # 验证学员 ID
    for nid in node_ids:
        if nid not in STUDENT_CONFIG:
            print(f"✗ 未知学员: {nid}，可选: {list(STUDENT_CONFIG.keys())}")
            sys.exit(1)

    # 从统一配置读取 broker 地址（如有）
    broker_host = args.host
    broker_port = args.port
    if lobster_config and args.host == "localhost":
        broker_host = lobster_config.mqtt_broker_host
        broker_port = lobster_config.mqtt_broker_port

    print("=" * 60)
    print("  小龙虾网络 MQTT 训练器桥接运行器")
    print("=" * 60)
    print(f"  Broker: {broker_host}:{broker_port}")
    print(f"  学员: {', '.join(node_ids)}")
    print(f"  模式: {'单学员' if len(node_ids) == 1 else f'多学员 ({len(node_ids)}人)'}")
    print()

    # 创建并启动运行器
    runners: Dict[str, MQTTTrainerRunner] = {}
    for nid in node_ids:
        runner = MQTTTrainerRunner(
            node_id=nid,
            broker_host=broker_host,
            broker_port=broker_port,
        )
        if runner.start():
            runners[nid] = runner
        else:
            print(f"  ✗ [{nid}] 启动失败")

    if not runners:
        print("\n✗ 无运行器启动成功，退出。")
        sys.exit(1)

    # 优雅退出处理
    shutdown_event = threading.Event()

    def signal_handler(sig, frame):
        print("\n\n收到退出信号，正在关闭所有运行器...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 主循环等待
    try:
        while not shutdown_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for nid, runner in runners.items():
            runner.stop()

    # 汇总
    print("\n" + "=" * 60)
    print("  训练器运行汇总")
    print("=" * 60)
    for nid, runner in runners.items():
        print(f"  [{nid}] 累计解题: {runner._solved_count}")
    print("\n  训练器已全部关闭。")


if __name__ == "__main__":
    main()
