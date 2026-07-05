#!/usr/bin/env python3
"""
🦞 一键加入小龙虾网络 (Lobster Network)

用法:
    python3 join_network.py --id <你的node_id> --name <你的名称> [选项]

示例:
    # 最简模式 — 只需 id 和 name
    python3 join_network.py --id agent_claw --name "AgentClaw"

    # 完整模式 — 指定能力和视角
    python3 join_network.py \
        --id agent_claw \
        --name "AgentClaw" \
        --perspective "系统诊断型" \
        --knowledge "系统架构分析、故障诊断、性能优化" \
        --capabilities diagnosis,monitoring,code_review

选项:
    --id             节点唯一标识 (必填, 英文+下划线)
    --name           节点显示名称 (必填)
    --type           节点类型: agent / human / hybrid (默认: agent)
    --perspective    你的独特视角 (默认: 通用型)
    --knowledge      你的知识领域, 逗号分隔 (默认: 通用知识)
    --capabilities   你的能力标签, 逗号分隔 (默认: dialogue,research)
    --value          价值取向 (默认: 协作创新)
    --learning-rate  学习速度: slow/medium/fast (默认: medium)
    --platform       你的平台 (默认: 自动检测)
    --no-daemon      只注册不启动心跳守护 (适合测试)

注册后:
    - 节点信息写入 /shared/registry/registry.json
    - 心跳消息发送到 /shared/messages/from-<node_id>/
    - 收件箱位于 /shared/messages/queue/<node_id>/inbox/
    - 向教练节点(hermes)发送注册通知
"""

import argparse
import json
import os
import platform
import signal
import socket
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path


# ==================== 常量 ====================

VERSION = "0.5.0"
COACH_NODE = "hermes"

# 默认数据目录, 可通过 --data-dir 覆盖
_DEFAULT_SHARED = "/shared"
SHARED_DIR = _DEFAULT_SHARED
MESSAGES_DIR = f"{SHARED_DIR}/messages"
REGISTRY_DIR = f"{SHARED_DIR}/registry"
REGISTRY_FILE = f"{REGISTRY_DIR}/registry.json"
HEARTBEAT_INTERVAL = 300  # 5 分钟

# 可用能力标签 (供参考, 不限制)
KNOWN_CAPABILITIES = [
    "dialogue", "research", "code_generation", "code_review",
    "data_analysis", "document_creation", "ppt_generation",
    "poster_design", "go_training", "translation", "writing",
    "monitoring", "diagnosis", "teaching", "coaching",
    "project_management", "reasoning", "memory",
]


# ==================== 工具函数 ====================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def now_iso():
    return datetime.now().isoformat()


def detect_platform():
    """自动检测运行平台"""
    system = platform.system().lower()
    if system == "darwin":
        return "macOS"
    elif system == "linux":
        # 检查是否在容器里
        if os.path.exists("/.dockerenv"):
            return "Docker/Linux"
        return "Linux"
    elif system == "windows":
        return "Windows"
    return system


# ==================== 注册中心 ====================

def load_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_registry(data):
    os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
    with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==================== 消息系统 ====================

def send_message(node_id, to_node, msg_type, payload, version):
    """发送消息到目标节点"""
    msg_id = f"msg-{uuid.uuid4().hex[:12]}"

    message = {
        "msg_id": msg_id,
        "from_node": node_id,
        "to_node": to_node,
        "msg_type": msg_type,
        "payload": payload,
        "timestamp": now_iso(),
        "status": "pending",
        "priority": 1,
        "version": version,
    }

    # 写入目标 inbox
    inbox_dir = f"{MESSAGES_DIR}/queue/{to_node}/inbox"
    os.makedirs(inbox_dir, exist_ok=True)
    with open(os.path.join(inbox_dir, f"{msg_id}.json"), "w", encoding="utf-8") as f:
        json.dump(message, f, ensure_ascii=False, indent=2)

    # 写入自己的 outbox
    outbox_dir = f"{MESSAGES_DIR}/queue/{node_id}/outbox"
    os.makedirs(outbox_dir, exist_ok=True)
    with open(os.path.join(outbox_dir, f"{msg_id}.json"), "w", encoding="utf-8") as f:
        json.dump(message, f, ensure_ascii=False, indent=2)

    return msg_id


def check_inbox(node_id):
    """检查收件箱"""
    inbox_dir = f"{MESSAGES_DIR}/queue/{node_id}/inbox"
    if not os.path.exists(inbox_dir):
        return []

    messages = []
    for filename in sorted(os.listdir(inbox_dir)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(inbox_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                msg = json.load(f)
            messages.append(msg)
            processed_dir = f"{MESSAGES_DIR}/queue/{node_id}/processed"
            os.makedirs(processed_dir, exist_ok=True)
            os.rename(filepath, os.path.join(processed_dir, filename))
        except Exception:
            pass

    return messages


# ==================== 核心流程 ====================

_running = True


def signal_handler(sig, frame):
    global _running
    _running = False


def register(config):
    """注册节点"""
    registry = load_registry()
    node_id = config["node_id"]
    is_new = node_id not in registry

    node_data = {
        "node_id": node_id,
        "name": config["name"],
        "node_type": config["type"],
        "host": socket.gethostname(),
        "port": 0,
        "capabilities": config["capabilities"],
        "registered_at": registry.get(node_id, {}).get("registered_at", now_iso()),
        "last_heartbeat": now_iso(),
        "status": "active",
        "version": VERSION,
        "metadata": {
            "perspective": config["perspective"],
            "knowledge_base": config["knowledge"],
            "value_orientation": config["value"],
            "learning_rate": config["learning_rate"],
            "platform": config["platform"],
        },
    }

    registry[node_id] = node_data
    save_registry(registry)

    action = "🎉 新节点注册" if is_new else "🔄 节点信息更新"
    print(f"[{now()}] {action}: {node_id} ({config['name']})")
    return is_new


def send_heartbeat(node_id, capabilities):
    """发送心跳"""
    registry = load_registry()
    if node_id in registry:
        registry[node_id]["last_heartbeat"] = now_iso()
        registry[node_id]["status"] = "active"
        save_registry(registry)

    from_dir = f"{MESSAGES_DIR}/from-{node_id}"
    os.makedirs(from_dir, exist_ok=True)

    hb_id = f"heartbeat_{int(time.time())}"
    hb_msg = {
        "id": hb_id,
        "from": node_id,
        "timestamp": now_iso(),
        "message": "heartbeat",
        "version": VERSION,
        "status": "active",
        "capabilities": capabilities,
    }
    with open(os.path.join(from_dir, f"{hb_id}.json"), "w", encoding="utf-8") as f:
        json.dump(hb_msg, f, ensure_ascii=False, indent=2)

    print(f"[{now()}] ♥ 心跳 ({hb_id})")


def cleanup_heartbeats(node_id):
    """清理旧心跳文件"""
    from_dir = f"{MESSAGES_DIR}/from-{node_id}"
    if not os.path.exists(from_dir):
        return
    files = sorted(
        [f for f in os.listdir(from_dir) if f.startswith("heartbeat_")],
        reverse=True,
    )
    for old in files[5:]:
        try:
            os.remove(os.path.join(from_dir, old))
        except Exception:
            pass


def daemon_loop(node_id, capabilities):
    """心跳守护循环"""
    print(f"[{now()}] 进入心跳守护 (间隔 {HEARTBEAT_INTERVAL}s, Ctrl+C 退出)...")
    count = 0

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while _running:
        try:
            time.sleep(HEARTBEAT_INTERVAL)
            if not _running:
                break
            count += 1
            send_heartbeat(node_id, capabilities)

            inbox = check_inbox(node_id)
            for msg in inbox:
                from_node = msg.get("from_node", msg.get("from", "?"))
                msg_type = msg.get("msg_type", "unknown")
                text = msg.get("payload", {}).get("message", "")[:80]
                print(f"[{now()}] ← [{msg_type}] from {from_node}: {text}")

            if count % 10 == 0:
                cleanup_heartbeats(node_id)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[{now()}] ⚠ 异常: {e}")
            time.sleep(30)

    # 优雅退出
    print(f"[{now()}] 设置状态为 offline...")
    registry = load_registry()
    if node_id in registry:
        registry[node_id]["status"] = "offline"
        registry[node_id]["last_heartbeat"] = now_iso()
        save_registry(registry)
    print(f"[{now()}] {node_id} 已离线, 再见!")


# ==================== 主入口 ====================

def parse_args():
    parser = argparse.ArgumentParser(
        description="🦞 一键加入小龙虾网络 (Lobster Network)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 join_network.py --id agent_claw --name "AgentClaw"
  python3 join_network.py --id my_shrimp --name "我的虾" --capabilities dialogue,go_training
  python3 join_network.py --id hermes_new --name "新教练" --type hybrid --no-daemon
        """,
    )
    parser.add_argument("--id", required=True, help="节点唯一标识 (英文+下划线)")
    parser.add_argument("--name", required=True, help="节点显示名称")
    parser.add_argument("--type", default="agent", choices=["agent", "human", "hybrid"],
                        help="节点类型 (默认: agent)")
    parser.add_argument("--perspective", default="通用型", help="独特视角 (默认: 通用型)")
    parser.add_argument("--knowledge", default="通用知识", help="知识领域 (默认: 通用知识)")
    parser.add_argument("--capabilities", default="dialogue,research",
                        help="能力标签, 逗号分隔 (默认: dialogue,research)")
    parser.add_argument("--value", default="协作创新", help="价值取向 (默认: 协作创新)")
    parser.add_argument("--learning-rate", default="medium",
                        choices=["slow", "medium", "fast"],
                        help="学习速度 (默认: medium)")
    parser.add_argument("--platform", default=None, help="运行平台 (默认: 自动检测)")
    parser.add_argument("--no-daemon", action="store_true", help="只注册, 不启动心跳守护")
    parser.add_argument("--data-dir", default=None,
                        help="数据存储目录 (默认: /shared, 不可写时自动回退到 ./lobster-data)")
    return parser.parse_args()


def main():
    global SHARED_DIR, MESSAGES_DIR, REGISTRY_DIR, REGISTRY_FILE

    args = parse_args()

    # 确定数据目录
    if args.data_dir:
        SHARED_DIR = args.data_dir
    else:
        # 检测 /shared 是否可写
        if not os.access(_DEFAULT_SHARED, os.W_OK):
            fallback = os.path.join(os.getcwd(), "lobster-data")
            print(f"[!] /shared 不可写, 使用本地数据目录: {fallback}")
            SHARED_DIR = fallback

    MESSAGES_DIR = f"{SHARED_DIR}/messages"
    REGISTRY_DIR = f"{SHARED_DIR}/registry"
    REGISTRY_FILE = f"{REGISTRY_DIR}/registry.json"

    config = {
        "node_id": args.id,
        "name": args.name,
        "type": args.type,
        "perspective": args.perspective,
        "knowledge": args.knowledge,
        "capabilities": [c.strip() for c in args.capabilities.split(",")],
        "value": args.value,
        "learning_rate": args.learning_rate,
        "platform": args.platform or detect_platform(),
    }

    print("=" * 60)
    print("  🦞 小龙虾网络 — 节点接入工具")
    print(f"  版本: v{VERSION}")
    print(f"  节点: {config['node_id']} ({config['name']})")
    print(f"  类型: {config['type']}")
    print(f"  视角: {config['perspective']}")
    print(f"  能力: {', '.join(config['capabilities'])}")
    print(f"  平台: {config['platform']}")
    print(f"  启动: {now()}")
    print("=" * 60)

    # 1. 确保目录
    for d in [MESSAGES_DIR, REGISTRY_DIR,
              f"{MESSAGES_DIR}/queue/{config['node_id']}/inbox",
              f"{MESSAGES_DIR}/queue/{config['node_id']}/outbox",
              f"{MESSAGES_DIR}/queue/{config['node_id']}/processed",
              f"{MESSAGES_DIR}/from-{config['node_id']}"]:
        os.makedirs(d, exist_ok=True)

    # 2. 注册
    is_new = register(config)

    # 3. 初始心跳
    send_heartbeat(config["node_id"], config["capabilities"])

    # 4. 新节点 → 通知教练
    if is_new:
        msg_id = send_message(
            config["node_id"], COACH_NODE, "node_registered",
            {
                "event": "new_node_registration",
                "node_id": config["node_id"],
                "name": config["name"],
                "version": VERSION,
                "capabilities": config["capabilities"],
                "message": f"{config['name']}已注册到龙虾网络，期待与其他虾协作!",
            },
            VERSION,
        )
        print(f"[{now()}] → 注册通知已发送给教练节点 ({msg_id})")

    # 5. 向所有现有节点打招呼
    registry = load_registry()
    existing_nodes = [nid for nid in registry if nid != config["node_id"]]
    if existing_nodes:
        print(f"[{now()}] 发现 {len(existing_nodes)} 个已有节点: {', '.join(existing_nodes)}")
        for nid in existing_nodes:
            send_message(
                config["node_id"], nid, "hello",
                {
                    "event": "new_node_greeting",
                    "from": config["node_id"],
                    "name": config["name"],
                    "capabilities": config["capabilities"],
                    "message": f"你好! 我是{config['name']}，刚加入龙虾网络，期待合作。",
                },
                VERSION,
            )
        print(f"[{now()}] → 已向所有节点发送打招呼消息")

    # 6. 检查收件箱
    inbox = check_inbox(config["node_id"])
    if inbox:
        print(f"[{now()}] ← 收到 {len(inbox)} 条消息:")
        for msg in inbox:
            from_node = msg.get("from_node", "?")
            msg_type = msg.get("msg_type", "?")
            text = msg.get("payload", {}).get("message", "")[:100]
            print(f"    [{msg_type}] from {from_node}: {text}")

    # 7. 输出网络状态
    print()
    print("=" * 60)
    print("  📊 当前网络节点:")
    for nid, info in registry.items():
        status = info.get("status", "?")
        name = info.get("name", nid)
        caps = ", ".join(info.get("capabilities", [])[:3])
        icon = "🟢" if status == "active" else "🔴"
        me = " ← 你在这里" if nid == config["node_id"] else ""
        print(f"    {icon} {nid:15s} ({name}) [{caps}]{me}")
    print("=" * 60)

    # 8. 守护循环
    if args.no_daemon:
        print(f"\n[{now()}] --no-daemon 模式, 注册完成, 不启动心跳守护")
        print(f"[{now()}] 如需启动心跳: python3 join_network.py --id {config['node_id']} --name \"{config['name']}\"")
    else:
        print()
        daemon_loop(config["node_id"], config["capabilities"])


if __name__ == "__main__":
    main()
