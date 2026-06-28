#!/usr/bin/env python3
"""
Auto ACK Responder - 龙虾网络CC协议自动确认回复器
Protocol v1.1

自动扫描节点inbox中的CC消息，对requires_ack=true且尚未回复的消息
自动生成ACK响应并写入发送方inbox。

用法:
    python auto_ack.py --node qoder
    python auto_ack.py --node xiaochen --dry-run
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 路径配置(必须在import之前)
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
SHARED_DIR = REPO_ROOT / ".shared"
QUEUE_DIR = SHARED_DIR / "messages" / "queue"

from core.cc_broadcast import send_ack

# 时区
CST = timezone(timedelta(hours=8))


class AutoACKResponder:
    """自动ACK响应器，扫描节点inbox并回复未确认的CC消息"""

    def __init__(self, node_id):
        """
        Args:
            node_id: 本响应器所服务的节点ID
        """
        self.node_id = node_id
        self.inbox_dir = QUEUE_DIR / node_id / "inbox"

    def scan_pending_cc(self):
        """扫描inbox中需要ACK但尚未回复的CC消息

        Returns:
            list[dict]: 每条元素包含 file, msg, tracking_id, from 等字段
        """
        if not self.inbox_dir.exists():
            print(f"[AUTO-ACK] {self.node_id} inbox不存在: {self.inbox_dir}")
            return []

        pending = []
        for f in sorted(self.inbox_dir.iterdir()):
            if not (f.name.startswith("cc-") and f.suffix == ".json"):
                continue

            try:
                msg = json.loads(f.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                continue

            # 只处理 requires_ack=true 的消息
            if not msg.get("requires_ack", False):
                continue

            tracking_id = msg.get("tracking_id")
            original_sender = msg.get("from")
            if not tracking_id or not original_sender:
                continue

            # 检查是否已经对该 tracking_id 发送过 ACK
            # ACK 会被写入发送方的 inbox，因此去发送方 inbox 查找
            sender_inbox = QUEUE_DIR / original_sender / "inbox"
            already_acked = False
            if sender_inbox.exists():
                for ack_file in sender_inbox.iterdir():
                    if ack_file.name.startswith("ack-") and ack_file.suffix == ".json":
                        try:
                            ack_data = json.loads(ack_file.read_text(encoding="utf-8"))
                            if (
                                ack_data.get("tracking_id") == tracking_id
                                and ack_data.get("from") == self.node_id
                            ):
                                already_acked = True
                                break
                        except (json.JSONDecodeError, IOError):
                            continue

            if not already_acked:
                pending.append({
                    "file": f.name,
                    "msg": msg,
                    "tracking_id": tracking_id,
                    "from": original_sender,
                })

        return pending

    def auto_ack_all(self, dry_run=False):
        """对所有pending的CC消息发送ACK

        Args:
            dry_run: 若为True则只打印不实际写入

        Returns:
            int: 成功发送的ACK数量
        """
        pending = self.scan_pending_cc()

        if not pending:
            print(f"[AUTO-ACK] {self.node_id}: 无待ACK的CC消息")
            return 0

        count = 0
        for item in pending:
            tracking_id = item["tracking_id"]
            sender = item["from"]
            subject = item["msg"].get("subject", "")

            if dry_run:
                print(
                    f"[DRY-RUN] 将ACK: {item['file']} "
                    f"(tracking={tracking_id}, from={sender}, subject={subject})"
                )
                count += 1
                continue

            print(
                f"[AUTO-ACK] ACKing: {item['file']} "
                f"-> {sender} (tracking={tracking_id})"
            )
            # 调用 send_ack 完成 ACK 写入
            # send_ack 内部会扫描本节点 inbox 找到原始消息，
            # 将 ACK 写入发送方 inbox，并执行 git commit+push
            result = send_ack(
                tracking_id=tracking_id,
                status="received",
                response="已收到，正在处理",
                sender=self.node_id,
            )

            if result.get("status") == "acked":
                count += 1
            else:
                print(
                    f"[AUTO-ACK] 警告: ACK未成功 tracking={tracking_id} "
                    f"result={result}"
                )

        return count

    def run(self, dry_run=False):
        """主循环: pull最新 -> 扫描 -> ACK -> push

        Args:
            dry_run: 若为True则跳过写入和git操作

        Returns:
            dict: 包含 acked_count 的运行摘要
        """
        print(f"[AUTO-ACK] === 启动自动ACK响应器 (node={self.node_id}) ===")

        # 1. Pull latest changes
        if not dry_run:
            self._git_pull()

        # 2. Scan pending
        pending = self.scan_pending_cc()
        print(f"[AUTO-ACK] 发现 {len(pending)} 条待ACK消息")

        if not pending:
            return {"status": "ok", "acked_count": 0}

        # 3. ACK all
        count = self.auto_ack_all(dry_run=dry_run)

        # 4. Push changes (send_ack 内部已有 push，这里做最终确保)
        if count > 0 and not dry_run:
            self._git_push()

        print(f"[AUTO-ACK] === 完成: {count} 条ACK已发送 ===")
        return {"status": "ok", "acked_count": count}

    def _git_pull(self):
        """拉取远程最新变更"""
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            if result.returncode == 0:
                print("[GIT] pulled latest")
            else:
                print(f"[GIT] pull failed: {result.stderr.decode()[:200]}")
        except Exception as e:
            print(f"[GIT] pull error: {e}")

    def _git_push(self):
        """提交并推送变更"""
        try:
            subprocess.run(
                ["git", "add", ".shared/messages/"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
            subprocess.run(
                ["git", "commit", "-m", f"auto-ack: batch from {self.node_id}"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
            result = subprocess.run(
                ["git", "push", "origin", "main"],
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            if result.returncode == 0:
                print(f"[GIT] pushed: auto-ack from {self.node_id}")
            else:
                print(f"[GIT] push failed: {result.stderr.decode()[:200]}")
        except Exception as e:
            print(f"[GIT] push error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Auto ACK Responder - 龙虾网络CC协议自动确认"
    )
    parser.add_argument(
        "--node", default="qoder", help="节点ID (default: qoder)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="仅扫描，不实际发送ACK"
    )

    args = parser.parse_args()
    responder = AutoACKResponder(args.node)
    result = responder.run(dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False))
