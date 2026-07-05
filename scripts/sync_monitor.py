#!/usr/bin/env python3
"""
同步监控器 - 小龙虾网络V3.1
监控各节点同步状态，自动告警

功能:
- 检查各节点 outbox/inbox 状态
- 检测同步延迟
- 自动生成告警
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 配置
SHARED_DIR = Path("/shared")
QUEUE_DIR = SHARED_DIR / "messages" / "queue"
TRAINING_DIR = SHARED_DIR / "training" / "go"
ALERT_THRESHOLD_HOURS = 24  # 告警阈值（小时）

# 节点列表
NODES = ["xiaochen", "zhuguxia", "qoder", "zhugema", "xiaowei"]


class SyncMonitor:
    """同步监控器"""

    def __init__(self):
        self._alerts: List[Dict] = []

    def check_node_sync(self, node: str) -> Dict:
        """检查节点同步状态"""
        result = {
            "node": node,
            "inbox_count": 0,
            "outbox_count": 0,
            "last_inbox_update": None,
            "last_outbox_update": None,
            "alerts": [],
        }

        # 检查 inbox
        inbox_dir = QUEUE_DIR / node / "inbox"
        if inbox_dir.exists():
            files = list(inbox_dir.glob("*"))
            result["inbox_count"] = len(files)
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                result["last_inbox_update"] = datetime.fromtimestamp(
                    latest.stat().st_mtime
                ).isoformat()

        # 检查 outbox
        outbox_dir = QUEUE_DIR / node / "outbox"
        if outbox_dir.exists():
            files = list(outbox_dir.glob("*"))
            result["outbox_count"] = len(files)
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                result["last_outbox_update"] = datetime.fromtimestamp(
                    latest.stat().st_mtime
                ).isoformat()

        # 检查告警
        now = datetime.now()
        if result["last_inbox_update"]:
            last_update = datetime.fromisoformat(result["last_inbox_update"])
            age_hours = (now - last_update).total_seconds() / 3600
            if age_hours > ALERT_THRESHOLD_HOURS:
                result["alerts"].append(
                    f"Inbox 更新延迟: {age_hours:.1f} 小时"
                )

        if result["inbox_count"] > 50:
            result["alerts"].append(
                f"Inbox 积压: {result['inbox_count']} 条消息"
            )

        return result

    def run_check(self) -> Dict:
        """运行全量检查"""
        results = {}
        total_alerts = 0
        for node in NODES:
            result = self.check_node_sync(node)
            results[node] = result
            total_alerts += len(result["alerts"])

        return {
            "checked_at": datetime.now().isoformat(),
            "total_nodes": len(NODES),
            "nodes_with_alerts": sum(
                1 for r in results.values() if r["alerts"]
            ),
            "total_alerts": total_alerts,
            "results": results,
        }

    def save_report(self, path: str):
        """保存报告"""
        report = self.run_check()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report


if __name__ == "__main__":
    monitor = SyncMonitor()
    report = monitor.run_check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
