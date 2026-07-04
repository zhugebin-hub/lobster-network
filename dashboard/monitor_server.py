#!/usr/bin/env python3
"""
小龙虾网络可视化监控服务
实时扫描网络状态，生成JSON数据并服务HTML仪表盘
"""
import json
import os
import glob
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = Path(__file__).resolve().parent
SHARED_DIR = BASE_DIR / ".shared"
MESSAGES_DIR = SHARED_DIR / "messages"
QUEUE_DIR = MESSAGES_DIR / "queue"
REGISTRY_DIR = BASE_DIR / "registry"

# V4.0 节点配置（与 sync_manager.py 对齐）
NODES_CONFIG = {
    "zhugema":    {"name": "诸葛马",   "server": "47.93.6.57",    "role": "coach",  "label": "AI教练·主节点"},
    "xiaochen":   {"name": "小陈",     "server": "121.43.80.231", "role": "student", "label": "稳健型学员"},
    "zhuguxia":   {"name": "诸葛虾",   "server": "60.205.139.51", "role": "student", "label": "加速型学员"},
    "qoder":      {"name": "qoder",    "server": "192.168.1.161", "role": "student", "label": "实战型学员"},
    "xiaowei":    {"name": "小薇",     "server": "local",         "role": "student", "label": "进阶型学员"},
    "zhugebin-001": {"name": "诸葛斌", "server": "macOS-local",   "role": "observer", "label": "研究者·观察者"},
}


def scan_network():
    """扫描整个网络状态，返回结构化数据"""
    now = datetime.now(timezone.utc).astimezone()
    data = {
        "scan_time": now.isoformat(),
        "scan_timestamp": int(now.timestamp()),
        "version": "v4.0",
        "nodes": [],
        "cc_tracking": {},
        "message_stats": {},
        "recent_messages": [],
        "training_overview": {},
        "git_info": {},
    }

    # === 1. 节点信息 ===
    for nid, cfg in NODES_CONFIG.items():
        node_file = REGISTRY_DIR / "nodes" / f"{nid}.json"
        node_data = {"node_id": nid, **cfg}

        if node_file.exists():
            try:
                with open(node_file) as f:
                    raw = json.load(f)
                node_data["status"] = raw.get("status", "unknown")
                node_data["last_heartbeat"] = raw.get("last_heartbeat", "")
                node_data["heartbeat_count"] = raw.get("heartbeat_count", 0)
                node_data["version"] = raw.get("version", "")
                node_data["type"] = raw.get("type", "")
                node_data["capabilities"] = raw.get("capabilities", [])
                md = raw.get("metadata", {})
                node_data["tasks_completed"] = md.get("tasks_completed", 0)
                node_data["collaborations"] = md.get("collaborations", 0)
                node_data["token_balance"] = md.get("token_balance", 0)
                node_data["ssh_enabled"] = md.get("ssh_enabled", raw.get("ssh_enabled", False))

                # 训练信息
                training = raw.get("training", {})
                if training:
                    node_data["go_level"] = training.get("current_level", "")
                    node_data["win_rate"] = training.get("win_rate", 0)
                    node_data["training_style"] = training.get("style", "")
                    node_data["strengths"] = training.get("strengths", [])
                    node_data["weaknesses"] = training.get("weaknesses", [])
                    node_data["accuracy"] = training.get("accuracy_baseline", {})

                # 小薇特殊训练数据
                if nid == "xiaowei":
                    node_data["go_level"] = raw.get("level", "23k")
                    node_data["goal"] = raw.get("goal", "")
                    stats = raw.get("training_stats", {})
                    if stats:
                        node_data["skill_scores"] = stats.get("skill_scores", {})
                        node_data["total_problems"] = stats.get("total_problems", 0)
                        node_data["overall_accuracy"] = stats.get("overall_accuracy", 0)

                # 诸葛马学员列表
                if nid == "zhugema":
                    node_data["students"] = raw.get("students", [])
            except Exception as e:
                node_data["status"] = "error"
                node_data["error"] = str(e)
        else:
            node_data["status"] = "unregistered"

        # 队列统计
        inbox_dir = QUEUE_DIR / nid / "inbox"
        sent_dir = QUEUE_DIR / nid / "sent"
        outbox_dir = QUEUE_DIR / nid / "outbox"

        node_data["inbox_count"] = len(glob.glob(str(inbox_dir / "*.json"))) if inbox_dir.exists() else 0
        node_data["sent_count"] = len(glob.glob(str(sent_dir / "*.json"))) if sent_dir.exists() else 0
        node_data["outbox_count"] = len(glob.glob(str(outbox_dir / "*.json"))) if outbox_dir.exists() else 0

        data["nodes"].append(node_data)

    # === 2. CC 追踪 ===
    cc_file = MESSAGES_DIR / "cc_tracking.json"
    if cc_file.exists():
        try:
            with open(cc_file) as f:
                cc = json.load(f)
            data["cc_tracking"] = {
                "pending": len(cc.get("pending", [])),
                "completed": len(cc.get("completed", [])),
                "escalated": len(cc.get("escalated", [])),
                "total": len(cc.get("pending", [])) + len(cc.get("completed", [])) + len(cc.get("escalated", [])),
                "pending_details": cc.get("pending", []),
                "completed_details": [
                    {
                        "id": e.get("tracking_id", ""),
                        "from": e.get("from", ""),
                        "subject": e.get("subject", "")[:80],
                        "acks": list(e.get("acks_received", {}).keys()),
                        "ack_count": len(e.get("acks_received", {})),
                    }
                    for e in cc.get("completed", [])
                ],
                "escalated_details": cc.get("escalated", []),
            }
        except Exception as e:
            data["cc_tracking"] = {"error": str(e)}

    # === 3. 消息队列统计 ===
    total_inbox = sum(n["inbox_count"] for n in data["nodes"])
    total_sent = sum(n["sent_count"] for n in data["nodes"])
    data["message_stats"] = {
        "total_inbox": total_inbox,
        "total_sent": total_sent,
        "total": total_inbox + total_sent,
        "per_node": {n["node_id"]: {"inbox": n["inbox_count"], "sent": n["sent_count"]} for n in data["nodes"]},
    }

    # === 4. 最近消息 ===
    all_msgs = []
    for f in sorted(glob.glob(str(QUEUE_DIR / "*" / "inbox" / "*.json")), key=os.path.getmtime, reverse=True)[:20]:
        try:
            with open(f) as fh:
                d = json.load(fh)
            node = f.split("/queue/")[1].split("/")[0]
            fname = os.path.basename(f)
            is_ack = fname.startswith("ack-")
            is_cc = d.get("msg_id", "").startswith("cc-") if isinstance(d.get("msg_id"), str) else False

            subject = d.get("subject", "")
            if not subject and isinstance(d.get("body"), dict):
                subject = d["body"].get("subject", "")
            if not subject:
                subject = d.get("message", "")

            all_msgs.append({
                "file": fname,
                "to_node": node,
                "from": d.get("from", d.get("sender", "")),
                "subject": str(subject)[:60] if subject else ("ACK回执" if is_ack else "(无标题)"),
                "timestamp": d.get("sent_at", d.get("timestamp", "")),
                "type": "ack" if is_ack else ("cc" if is_cc else "normal"),
                "age_minutes": int((time.time() - os.path.getmtime(f)) / 60),
            })
        except:
            pass
    data["recent_messages"] = all_msgs

    # === 5. 训练概览 ===
    training = {}
    for n in data["nodes"]:
        if n.get("go_level") or n.get("training_style"):
            training[n["node_id"]] = {
                "name": n["name"],
                "level": n.get("go_level", ""),
                "win_rate": n.get("win_rate", 0),
                "style": n.get("training_style", ""),
                "strengths": n.get("strengths", []),
                "skill_scores": n.get("skill_scores", {}),
                "total_problems": n.get("total_problems", 0),
                "accuracy": n.get("accuracy", {}),
            }
    data["training_overview"] = training

    # === 6. Git 信息 ===
    import subprocess
    try:
        log = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            capture_output=True, text=True, cwd=str(BASE_DIR)
        )
        data["git_info"]["recent_commits"] = log.stdout.strip().split("\n")

        stat = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1"],
            capture_output=True, text=True, cwd=str(BASE_DIR)
        )
        data["git_info"]["last_change"] = stat.stdout.strip()[:200] if stat.stdout else ""
    except:
        data["git_info"]["error"] = "git not available"

    # === 7. 模块健康检查 ===
    modules = {}
    for mod_name, mod_path in [
        ("harness", BASE_DIR / "src" / "lobster_network" / "harness"),
        ("security", BASE_DIR / "src" / "lobster_network" / "security"),
        ("network", BASE_DIR / "src" / "lobster_network" / "network"),
        ("vector_memory", BASE_DIR / "vector_memory"),
        ("federated_learning", BASE_DIR / "federated_learning"),
        ("agent_economy", BASE_DIR / "agent_economy"),
        ("mcp_server", BASE_DIR / "mcp_server"),
        ("a2a_protocol", BASE_DIR / "a2a_protocol"),
        ("paper_writing", BASE_DIR / "domains" / "learning" / "problems" / "paper_writing_engine.py"),
        ("stock_predict", BASE_DIR / "domains" / "learning" / "problems" / "stock_predict_engine.py"),
        ("football_predict", BASE_DIR / "domains" / "learning" / "problems" / "football_predict_engine.py"),
        ("sync_manager", BASE_DIR / ".shared" / "messages" / "sync_manager.py"),
    ]:
        modules[mod_name] = "installed" if mod_path.exists() else "missing"
    data["modules"] = modules

    return data


class DashboardHandler(SimpleHTTPRequestHandler):
    """自定义HTTP处理器，提供API和静态文件"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/status":
            # 实时状态API
            data = scan_network()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
        elif parsed.path == "/" or parsed.path == "/index.html":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass  # 静默日志


def main():
    port = 8765
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    # 先生成一次数据
    print("🔍 扫描网络状态...")
    data = scan_network()
    print(f"   节点: {len(data['nodes'])} | 消息: {data['message_stats']['total']} | CC追踪: {data['cc_tracking'].get('total', 0)}")

    # 保存静态JSON快照
    snapshot_file = DASHBOARD_DIR / "status_snapshot.json"
    with open(snapshot_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"   快照已保存: {snapshot_file}")

    # 启动HTTP服务器
    server = HTTPServer(("0.0.0.0", port), DashboardHandler)
    print(f"\n🦞 小龙虾网络监控仪表盘已启动")
    print(f"   地址: http://localhost:{port}")
    print(f"   API:  http://localhost:{port}/api/status")
    print(f"   按 Ctrl+C 停止\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.server_close()


if __name__ == "__main__":
    main()
