#!/usr/bin/env python3
"""
CC Broadcast - 龙虾网络自动抄送与反馈机制
Protocol v1.0

用法:
    # 发送CC消息
    python cc_broadcast.py send --to zhugema,zhuguxia --subject "Day4训练完成" --body "..." --category training_report
    
    # 检查ACK状态
    python cc_broadcast.py check
    
    # 回复CC消息(作为目标节点)
    python cc_broadcast.py ack --tracking-id track-xxx --status received --response "已收到"
    
    # 列出待处理的CC消息
    python cc_broadcast.py inbox
"""

import json
import os
import sys
import uuid
import argparse
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
SHARED_DIR = REPO_ROOT / ".shared"
QUEUE_DIR = SHARED_DIR / "messages" / "queue"
TRACKING_FILE = SHARED_DIR / "messages" / "cc_tracking.json"

# 时区
CST = timezone(timedelta(hours=8))

# 活跃节点(有inbox的) — 动态加载策略
def _load_active_nodes() -> List[str]:
    """优先级: nodes.json > 环境变量 LOBSTER_NODES > 默认值"""
    # 1. 尝试从 registry/nodes.json 加载
    nodes_file = REPO_ROOT / "registry" / "nodes.json"
    if nodes_file.exists():
        try:
            with open(nodes_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            nodes = data.get("nodes", [])
            active = [
                n["node_id"] for n in nodes
                if n.get("status") == "active" and n.get("type") == "agent"
            ]
            if active:
                return active
        except (json.JSONDecodeError, IOError):
            pass

    # 2. 尝试从环境变量加载
    env_nodes = os.environ.get("LOBSTER_NODES", "")
    if env_nodes:
        return [n.strip() for n in env_nodes.split(",") if n.strip()]

    # 3. 默认值
    return ["qoder", "xiaochen", "xiaowei", "zhugema", "zhuguxia"]


ACTIVE_NODES = _load_active_nodes()

# ACK超时配置(小时)
ACK_TIMEOUTS = {
    "training_report": 4,
    "status_update": 8,
    "sync_request": 2,
    "feedback_request": 6,
    "general": 24,
}

# 觅游社区备份通道配置
MEYO_CONFIG_FILE = SHARED_DIR / "messages" / "cc_meyo_config.json"
MEYO_CREDS_FILE = Path.home() / ".meyo" / "credentials.json"

def load_meyo_config():
    """加载觅游备份通道配置"""
    if MEYO_CONFIG_FILE.exists():
        try:
            with open(MEYO_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"backup_enabled": False}

def load_meyo_creds():
    """加载觅游API凭证"""
    creds_path = MEYO_CREDS_FILE.expanduser()
    if creds_path.exists():
        try:
            with open(creds_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None

def meyo_backup_post(cc_log_entries, sender="qoder"):
    """
    将CC消息摘要备份到觅游社区帖子
    cc_log_entries: list of dict, 每条包含 from/to/track/subject/status
    """
    config = load_meyo_config()
    if not config.get("backup_enabled"):
        print("[MEYO] 备份未启用")
        return {"status": "disabled"}
    
    creds = load_meyo_creds()
    if not creds:
        print("[MEYO] 无API凭证")
        return {"status": "no_creds"}
    
    post_id = config.get("meyo_post_id")
    if not post_id:
        print("[MEYO] 无帖子ID")
        return {"status": "no_post_id"}
    
    # 构建评论内容
    lines = []
    for entry in cc_log_entries:
        lines.append(
            f"[CC-LOG] from:{entry['from']} to:{entry['to']} "
            f"track:{entry['tracking_id']} subject:{entry['subject']} "
            f"status:{entry['status']}"
        )
    lines.append(f"\n--- {sender} 备份于 {now_str()}")
    content = "\n".join(lines)
    
    # 发送评论
    url = f"https://www.meyo123.com/api/v1/feeds/{post_id}/comments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {creds['api_key']}",
        "X-Skill-Version": "1.6.0",
        "X-Trigger-Source": "self-explore",
        "X-Trigger-Reason": "cc-backup-log",
    }
    body = json.dumps({"content": content}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("code") == 200:
                print(f"[MEYO] 备份成功: {len(cc_log_entries)} 条CC日志")
                return {"status": "ok", "comment_id": result.get("data", {}).get("id")}
            else:
                print(f"[MEYO] 备份失败: {result.get('message')}")
                return {"status": "error", "message": result.get("message")}
    except urllib.error.HTTPError as e:
        print(f"[MEYO] HTTP错误: {e.code}")
        return {"status": "http_error", "code": e.code}
    except Exception as e:
        print(f"[MEYO] 错误: {e}")
        return {"status": "error", "message": str(e)}

def meyo_checkin(node_id="qoder", inbox_count=0, status="正常"):
    """节点签到到觅游帖子"""
    config = load_meyo_config()
    if not config.get("backup_enabled"):
        return {"status": "disabled"}
    
    creds = load_meyo_creds()
    if not creds:
        return {"status": "no_creds"}
    
    post_id = config.get("meyo_post_id")
    content = f"[CHECK-IN] node:{node_id} time:{now_str()} inbox:{inbox_count} status:{status}"
    
    url = f"https://www.meyo123.com/api/v1/feeds/{post_id}/comments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {creds['api_key']}",
        "X-Skill-Version": "1.6.0",
        "X-Trigger-Source": "self-explore",
        "X-Trigger-Reason": "node-checkin",
    }
    body = json.dumps({"content": content}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get("code") == 200:
                print(f"[MEYO] 签到成功: {node_id} status={status}")
                # 更新配置文件中的last_checkin
                config["last_checkin"] = now_str()
                with open(MEYO_CONFIG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                return {"status": "ok"}
            else:
                return {"status": "error", "message": result.get("message")}
    except Exception as e:
        print(f"[MEYO] 签到失败: {e}")
        return {"status": "error", "message": str(e)}

def now_str():
    return datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00")

def load_tracking():
    """加载追踪状态"""
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"pending": [], "completed": [], "escalated": []}

def save_tracking(data):
    """保存追踪状态"""
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_cc(to_nodes, subject, body, category="general", sender="qoder", requires_ack=True, git_push=True, no_meyo=False):
    """
    发送CC消息到目标节点
    
    Args:
        to_nodes: 目标节点列表
        subject: 消息主题
        body: 消息正文
        category: 消息类别
        sender: 发送者节点ID
        requires_ack: 是否需要ACK
        git_push: 是否自动git push
    
    Returns:
        dict: 发送结果摘要
    """
    tracking = load_tracking()
    timestamp = datetime.now(CST).strftime("%Y%m%d%H%M%S")
    tracking_id = f"track-{uuid.uuid4().hex[:8]}"
    
    timeout_hours = ACK_TIMEOUTS.get(category, 24)
    sent_at = now_str()
    deadline = (datetime.now(CST) + timedelta(hours=timeout_hours)).strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    # 过滤有效目标节点
    valid_targets = [n for n in to_nodes if n in ACTIVE_NODES and n != sender]
    if not valid_targets:
        print(f"[WARN] 无有效目标节点")
        return {"status": "no_targets"}
    
    # 写入每个目标节点的inbox
    msg_id = f"cc-{sender}-{timestamp}"
    for i, target in enumerate(valid_targets):
        full_msg_id = f"{msg_id}-{i}"
        inbox = QUEUE_DIR / target / "inbox"
        inbox.mkdir(parents=True, exist_ok=True)
        
        msg = {
            "msg_id": full_msg_id,
            "msg_type": "cc_broadcast",
            "protocol_version": "1.0",
            "from": sender,
            "to": valid_targets,
            "cc_to_human": True,
            "subject": subject,
            "body": body,
            "category": category,
            "requires_ack": requires_ack,
            "sent_at": sent_at,
            "ack_deadline": deadline,
            "tracking_id": tracking_id,
        }
        
        filename = f"cc-{sender}-{timestamp}-{i}.json"
        filepath = inbox / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(msg, f, ensure_ascii=False, indent=2)
        print(f"[OK] -> {target}: {filename}")
    
    # 记录追踪
    track_entry = {
        "tracking_id": tracking_id,
        "msg_id": msg_id,
        "from": sender,
        "targets": valid_targets,
        "subject": subject,
        "category": category,
        "sent_at": sent_at,
        "ack_deadline": deadline,
        "requires_ack": requires_ack,
        "acks_received": {},
        "acks_pending": list(valid_targets),
    }
    tracking["pending"].append(track_entry)
    save_tracking(tracking)
    
    # Git push
    if git_push:
        _git_commit_push(f"cc: {subject} -> {','.join(valid_targets)}")
    
    # 觅游备份
    meyo_result = {"status": "skipped"}
    if not no_meyo:
        meyo_result = meyo_backup_post([{
            "from": sender,
            "to": ",".join(valid_targets),
            "tracking_id": tracking_id,
            "subject": subject,
            "status": "sent",
        }], sender=sender)
    
    return {
        "status": "sent",
        "tracking_id": tracking_id,
        "targets": valid_targets,
        "deadline": deadline,
        "meyo_backup": meyo_result.get("status", "unknown"),
    }

def check_acks():
    """
    检查inbox中的ACK回复，更新追踪状态
    
    Returns:
        dict: 检查结果
    """
    tracking = load_tracking()
    if not tracking["pending"]:
        print("[INFO] 无待追踪的CC消息")
        return {"pending_count": 0}
    
    new_pending = []
    newly_completed = []
    need_escalation = []
    
    for entry in tracking["pending"]:
        tracking_id = entry["tracking_id"]
        sender = entry["from"]
        
        # 检查sender inbox中的ACK
        inbox = QUEUE_DIR / sender / "inbox"
        if inbox.exists():
            for f in inbox.iterdir():
                if f.name.startswith("ack-") and f.suffix == ".json":
                    try:
                        ack = json.loads(f.read_text(encoding='utf-8'))
                        if ack.get("tracking_id") == tracking_id:
                            ack_from = ack.get("from", "unknown")
                            if ack_from in entry["acks_pending"]:
                                entry["acks_received"][ack_from] = ack.get("status", "received")
                                entry["acks_pending"].remove(ack_from)
                                print(f"[ACK] {ack_from} -> {entry['subject']}: {ack.get('status')}")
                    except (json.JSONDecodeError, KeyError):
                        pass
        
        # 检查是否全部ACK
        if not entry["acks_pending"]:
            newly_completed.append(entry)
            print(f"[DONE] {entry['subject']}: 全部ACK已收到")
        elif entry["requires_ack"]:
            # 检查是否超时
            try:
                deadline = datetime.fromisoformat(entry["ack_deadline"])
                if datetime.now(CST) > deadline:
                    need_escalation.append(entry)
                    print(f"[TIMEOUT] {entry['subject']}: {entry['acks_pending']} 未响应 (截止: {entry['ack_deadline']})")
                else:
                    new_pending.append(entry)
            except ValueError:
                new_pending.append(entry)
        else:
            new_pending.append(entry)
    
    # 更新追踪
    tracking["pending"] = new_pending
    tracking["completed"].extend(newly_completed)
    tracking["escalated"].extend(need_escalation)
    save_tracking(tracking)
    
    return {
        "pending_count": len(new_pending),
        "completed": len(newly_completed),
        "escalated": len(need_escalation),
        "escalated_details": [
            {"subject": e["subject"], "unresponsive": e["acks_pending"], "deadline": e["ack_deadline"]}
            for e in need_escalation
        ],
    }

def send_ack(tracking_id, status="received", response="", sender="qoder"):
    """
    回复CC消息
    
    Args:
        tracking_id: 追踪ID
        status: 状态 (received/processing/completed/rejected)
        response: 回复内容
        sender: 回复者节点ID
    """
    # 找到原始消息获取发起者
    original_from = None
    original_msg_id = None
    
    # 扫描sender inbox找原始CC消息
    inbox = QUEUE_DIR / sender / "inbox"
    if inbox.exists():
        for f in inbox.iterdir():
            if f.name.startswith("cc-") and f.suffix == ".json":
                try:
                    msg = json.loads(f.read_text(encoding='utf-8'))
                    if msg.get("tracking_id") == tracking_id:
                        original_from = msg["from"]
                        original_msg_id = msg["msg_id"]
                        break
                except (json.JSONDecodeError, KeyError):
                    pass
    
    if not original_from:
        print(f"[ERROR] 找不到tracking_id={tracking_id}的原始消息")
        return {"status": "not_found"}
    
    # 写入ACK到发起者inbox
    target_inbox = QUEUE_DIR / original_from / "inbox"
    target_inbox.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now(CST).strftime("%Y%m%d%H%M%S")
    ack = {
        "msg_id": f"ack-{sender}-{tracking_id}",
        "msg_type": "cc_ack",
        "protocol_version": "1.0",
        "from": sender,
        "to": original_from,
        "tracking_id": tracking_id,
        "ref_msg_id": original_msg_id,
        "status": status,
        "response": response,
        "acked_at": now_str(),
    }
    
    filename = f"ack-{sender}-{tracking_id}.json"
    filepath = target_inbox / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(ack, f, ensure_ascii=False, indent=2)
    print(f"[OK] ACK -> {original_from}: {filename}")
    
    _git_commit_push(f"ack: {tracking_id} from {sender}")
    return {"status": "acked", "to": original_from}

def list_inbox(node_id="qoder"):
    """列出inbox中的CC消息"""
    inbox = QUEUE_DIR / node_id / "inbox"
    if not inbox.exists():
        print(f"[INFO] {node_id} inbox不存在")
        return []
    
    cc_messages = []
    for f in sorted(inbox.iterdir()):
        if f.name.startswith("cc-") and f.suffix == ".json":
            try:
                msg = json.loads(f.read_text(encoding='utf-8'))
                cc_messages.append({
                    "file": f.name,
                    "from": msg.get("from"),
                    "subject": msg.get("subject"),
                    "category": msg.get("category"),
                    "tracking_id": msg.get("tracking_id"),
                    "requires_ack": msg.get("requires_ack"),
                    "sent_at": msg.get("sent_at"),
                    "ack_deadline": msg.get("ack_deadline"),
                })
                print(f"  [{msg.get('category','?')}] {msg.get('subject','?')} from {msg.get('from','?')} (track: {msg.get('tracking_id','?')})")
            except (json.JSONDecodeError, KeyError):
                pass
    
    if not cc_messages:
        print(f"[INFO] {node_id} inbox中无CC消息")
    return cc_messages

def _git_commit_push(message):
    """Git commit + push"""
    try:
        subprocess.run(
            ["git", "add", ".shared/messages/"],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=10,
        )
        result = subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"[GIT] pushed: {message}")
        else:
            print(f"[GIT] push failed: {result.stderr.decode()[:200]}")
    except Exception as e:
        print(f"[GIT] error: {e}")

def generate_summary(result, human_readable=True):
    """生成人类可读的摘要"""
    if not human_readable:
        return json.dumps(result, ensure_ascii=False)
    
    lines = []
    if result.get("status") == "sent":
        lines.append(f"CC消息已发送")
        lines.append(f"  追踪ID: {result['tracking_id']}")
        lines.append(f"  目标: {', '.join(result['targets'])}")
        lines.append(f"  ACK截止: {result['deadline']}")
    elif "escalated_details" in result:
        if result["escalated"] > 0:
            lines.append(f"有 {result['escalated']} 条消息超时未响应:")
            for d in result["escalated_details"]:
                lines.append(f"  - {d['subject']}: {', '.join(d['unresponsive'])} 未回复 (截止: {d['deadline']})")
        else:
            lines.append("所有CC消息状态正常，无超时")
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CC Broadcast - 龙虾网络自动抄送机制")
    sub = parser.add_subparsers(dest="command")
    
    # send
    p_send = sub.add_parser("send", help="发送CC消息")
    p_send.add_argument("--to", required=True, help="目标节点(逗号分隔)")
    p_send.add_argument("--subject", required=True, help="消息主题")
    p_send.add_argument("--body", required=True, help="消息正文")
    p_send.add_argument("--category", default="general", help="类别")
    p_send.add_argument("--sender", default="qoder", help="发送者")
    p_send.add_argument("--no-ack", action="store_true", help="不需要ACK")
    p_send.add_argument("--no-push", action="store_true", help="不自动push")
    p_send.add_argument("--no-meyo", action="store_true", help="不备份到觅游")
    
    # check
    p_check = sub.add_parser("check", help="检查ACK状态")
    
    # ack
    p_ack = sub.add_parser("ack", help="回复CC消息")
    p_ack.add_argument("--tracking-id", required=True, help="追踪ID")
    p_ack.add_argument("--status", default="received", help="状态")
    p_ack.add_argument("--response", default="", help="回复内容")
    p_ack.add_argument("--sender", default="qoder", help="回复者")
    
    # inbox
    p_inbox = sub.add_parser("inbox", help="查看inbox")
    p_inbox.add_argument("--node", default="qoder", help="节点ID")
    
    # checkin (觅游签到)
    p_checkin = sub.add_parser("checkin", help="觅游社区签到")
    p_checkin.add_argument("--node", default="qoder", help="节点ID")
    
    args = parser.parse_args()
    
    if args.command == "send":
        targets = [t.strip() for t in args.to.split(",")]
        result = send_cc(
            targets, args.subject, args.body,
            category=args.category,
            sender=args.sender,
            requires_ack=not args.no_ack,
            git_push=not args.no_push,
            no_meyo=args.no_meyo,
        )
        print(generate_summary(result))
    
    elif args.command == "check":
        result = check_acks()
        print(generate_summary(result))
    
    elif args.command == "ack":
        result = send_ack(
            args.tracking_id,
            status=args.status,
            response=args.response,
            sender=args.sender,
        )
        print(json.dumps(result, ensure_ascii=False))
    
    elif args.command == "inbox":
        list_inbox(args.node)
    
    elif args.command == "checkin":
        # 统计inbox中的待处理CC消息
        inbox = QUEUE_DIR / args.node / "inbox"
        count = 0
        if inbox.exists():
            count = len([f for f in inbox.iterdir() if f.name.startswith("cc-")])
        result = meyo_checkin(node_id=args.node, inbox_count=count, status="正常")
        print(f"签到结果: {json.dumps(result, ensure_ascii=False)}")
    
    else:
        parser.print_help()


# ============================================================
# RetryManager — 指数退避重试
# ============================================================

import random as _random
import time as _time_module
import logging as _logging

_retry_logger = _logging.getLogger("cc_retry")
_retry_handler = _logging.FileHandler(
    SHARED_DIR / "messages" / "cc_retry.log", encoding="utf-8"
)
_retry_handler.setFormatter(_logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
_retry_logger.addHandler(_retry_handler)
_retry_logger.setLevel(_logging.INFO)


class RetryManager:
    """
    指数退避重试管理器。

    论文 6.3 节 CC Broadcast 可靠性增强：
    - 指数退避: 初始 1s, 最大 60s, 乘数 2.0
    - 最大重试 3 次
    - jitter: ±25% 随机抖动防止惊群
    - 重试日志记录到 cc_retry.log

    用法:
        rm = RetryManager()
        result = rm.execute(
            lambda: send_cc(...),
            operation_name="send_cc",
            target="zhugema"
        )
    """

    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        max_retries: int = 3,
        jitter_pct: float = 0.25,
    ):
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_retries = max_retries
        self.jitter_pct = jitter_pct

        self._total_retries = 0
        self._total_failures = 0

    def execute(self, func: Callable, operation_name: str = "", target: str = "") -> Any:
        """
        带重试的执行。

        参数:
          func: 要执行的函数（无参 callable）
          operation_name: 操作名称（用于日志）
          target: 目标标识（用于日志）

        返回:
          func 的返回值

        异常:
          重试耗尽后抛出最后一次异常
        """
        delay = self.initial_delay
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                result = func()
                if attempt > 0:
                    _retry_logger.info(
                        f"[RetryManager] {operation_name}(→{target}) 第 {attempt} 次重试成功"
                    )
                return result
            except Exception as e:
                last_exception = e
                self._total_retries += 1

                if attempt >= self.max_retries:
                    self._total_failures += 1
                    _retry_logger.error(
                        f"[RetryManager] {operation_name}(→{target}) "
                        f"已达最大重试 {self.max_retries} 次: {e}"
                    )
                    raise

                # 计算退避延迟（含 jitter）
                current_delay = min(delay, self.max_delay)
                if self.jitter_pct > 0:
                    jitter = _random.uniform(-self.jitter_pct, self.jitter_pct)
                    current_delay *= (1.0 + jitter)

                _retry_logger.warning(
                    f"[RetryManager] {operation_name}(→{target}) "
                    f"失败 (第 {attempt + 1}/{self.max_retries} 次), "
                    f"{current_delay:.1f}s 后重试: {e}"
                )
                _time_module.sleep(current_delay)
                delay *= self.backoff_multiplier

        if last_exception:
            raise last_exception

    def get_stats(self) -> dict:
        return {
            "total_retries": self._total_retries,
            "total_failures": self._total_failures,
            "max_retries": self.max_retries,
            "initial_delay": self.initial_delay,
            "max_delay": self.max_delay,
        }


# ============================================================
# BatchDispatcher — 批量 CC 消息分发器
# ============================================================

class BatchDispatcher:
    """
    批量 CC 消息分发器。

    减少 MQTT 连接开销：
    - 批量发送: 默认 20 条/批
    - 批量 ACK: 默认 10 条/批

    用法:
        bd = BatchDispatcher(batch_size=20, ack_batch_size=10)

        # 添加消息
        bd.add_message(targets=["qoder"], subject="训练完成", body="...", category="training_report")

        # 批量发送
        bd.flush_send()

        # 批量 ACK
        bd.add_ack(tracking_id="track-xxx", status="received", response="已收到")
        bd.flush_ack()
    """

    def __init__(
        self,
        batch_size: int = 20,
        ack_batch_size: int = 10,
        sender: str = "qoder",
    ):
        self.batch_size = batch_size
        self.ack_batch_size = ack_batch_size
        self.sender = sender

        self._send_batch: List[Dict[str, Any]] = []
        self._ack_batch: List[Dict[str, str]] = []

        # 统计
        self._total_sent = 0
        self._total_acked = 0
        self._total_batches = 0

    def add_message(
        self,
        targets: List[str],
        subject: str,
        body: str,
        category: str = "general",
    ):
        """添加一条 CC 消息到发送批次"""
        self._send_batch.append({
            "targets": targets,
            "subject": subject,
            "body": body,
            "category": category,
            "sender": self.sender,
        })

        if len(self._send_batch) >= self.batch_size:
            self.flush_send()

    def add_ack(self, tracking_id: str, status: str = "received", response: str = ""):
        """添加一条 ACK 到确认批次"""
        self._ack_batch.append({
            "tracking_id": tracking_id,
            "status": status,
            "response": response,
            "sender": self.sender,
        })

        if len(self._ack_batch) >= self.ack_batch_size:
            self.flush_ack()

    def flush_send(self) -> List[Dict[str, Any]]:
        """批量发送所有待发消息"""
        if not self._send_batch:
            return []

        results = []
        for msg in self._send_batch:
            try:
                result = send_cc(
                    targets=msg["targets"],
                    subject=msg["subject"],
                    body=msg["body"],
                    category=msg["category"],
                    sender=msg["sender"],
                )
                results.append({"status": "ok", "tracking_id": result.get("tracking_id", ""), "targets": msg["targets"]})
                self._total_sent += 1
            except Exception as e:
                results.append({"status": "error", "error": str(e), "targets": msg["targets"]})

        batch_size = len(self._send_batch)
        self._send_batch.clear()
        self._total_batches += 1

        _retry_logger.info(
            f"[BatchDispatcher] 批量发送 {batch_size} 条 CC 消息 "
            f"(批次 #{self._total_batches}, 累计: {self._total_sent})"
        )

        return results

    def flush_ack(self) -> List[Dict[str, Any]]:
        """批量发送所有待确认 ACK"""
        if not self._ack_batch:
            return []

        results = []
        for ack in self._ack_batch:
            try:
                result = send_ack(
                    tracking_id=ack["tracking_id"],
                    status=ack["status"],
                    response=ack["response"],
                    sender=ack["sender"],
                )
                results.append(result)
                self._total_acked += 1
            except Exception as e:
                results.append({"status": "error", "tracking_id": ack["tracking_id"], "error": str(e)})

        ack_batch_size = len(self._ack_batch)
        self._ack_batch.clear()

        _retry_logger.info(
            f"[BatchDispatcher] 批量确认 {ack_batch_size} 条 ACK (累计: {self._total_acked})"
        )

        return results

    def get_stats(self) -> dict:
        return {
            "pending_send": len(self._send_batch),
            "pending_ack": len(self._ack_batch),
            "total_sent": self._total_sent,
            "total_acked": self._total_acked,
            "total_batches": self._total_batches,
            "batch_size": self.batch_size,
            "ack_batch_size": self.ack_batch_size,
        }
