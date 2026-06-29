#!/usr/bin/env python3
"""
围棋对局监控器 - 小龙虾网络V3.1
监控对局结果提交，定时检查并汇报

功能:
- 检查对局结果目录
- 监控学员 outbox
- 超时告警
- 生成监控报告
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 配置
MATCHES_DIR = Path("/shared/training/go/matches")
QUEUE_DIR = Path("/shared/messages/queue")
ALERT_THRESHOLD_MINUTES = 30  # 告警阈值（分钟）

# 当前对局
CURRENT_MATCH = {
    "id": "go-match-20260629_144249",
    "player1": "xiaochen",
    "player2": "zhuguxia",
    "board_size": 9,
    "time_per_side": "10min",
    "deadline": datetime(2026, 6, 29, 18, 42, 0),
}


class GoMatchMonitor:
    """围棋对局监控器"""

    def __init__(self):
        self.match = CURRENT_MATCH
        self._alerts: List[Dict] = []

    def check_match_dir(self) -> Dict:
        """检查对局目录"""
        result = {
            "match_id": self.match["id"],
            "player1": self.match["player1"],
            "player2": self.match["player2"],
            "board_size": self.match["board_size"],
            "deadline": self.match["deadline"].isoformat(),
            "status": "pending",  # pending/playing/completed/timeout
            "files": [],
            "last_update": None,
        }

        # 检查对局子目录
        for player in [self.match["player1"], self.match["player2"]]:
            subdir = MATCHES_DIR / f"{player}_vs_{self.match['player1' if player == self.match['player2'] else 'player2']}"
            if subdir.exists():
                files = list(subdir.glob("*.json"))
                result["files"].extend([f.name for f in files])
                if files:
                    latest = max(files, key=lambda f: f.stat().st_mtime)
                    result["last_update"] = datetime.fromtimestamp(
                        latest.stat().st_mtime
                    ).isoformat()

        # 检查对局状态
        if result["files"]:
            result["status"] = "completed"
        else:
            now = datetime.now()
            if now > self.match["deadline"]:
                result["status"] = "timeout"
            else:
                result["status"] = "pending"

        return result

    def check_outbox(self, player: str) -> Dict:
        """检查学员 outbox"""
        outbox_dir = QUEUE_DIR / player / "outbox"
        result = {
            "player": player,
            "outbox_count": 0,
            "match_files": [],
            "last_update": None,
        }

        if outbox_dir.exists():
            files = list(outbox_dir.glob("*"))
            result["outbox_count"] = len(files)
            # 过滤对局相关文件
            match_files = [f for f in files if "match" in f.name.lower() or "game" in f.name.lower()]
            result["match_files"] = [f.name for f in match_files]
            if files:
                latest = max(files, key=lambda f: f.stat().st_mtime)
                result["last_update"] = datetime.fromtimestamp(
                    latest.stat().st_mtime
                ).isoformat()

        return result

    def run_check(self) -> Dict:
        """运行全量检查"""
        match_result = self.check_match_dir()
        player1_outbox = self.check_outbox(self.match["player1"])
        player2_outbox = self.check_outbox(self.match["player2"])

        # 检查告警
        now = datetime.now()
        time_left = (self.match["deadline"] - now).total_seconds() / 60

        alerts = []
        if match_result["status"] == "timeout":
            alerts.append("⚠️ 对局已超时，学员未提交结果")
        elif time_left < ALERT_THRESHOLD_MINUTES and not match_result["files"]:
            alerts.append(f"⏰ 距离截止仅剩 {time_left:.0f} 分钟，学员尚未提交")

        return {
            "checked_at": now.isoformat(),
            "match": match_result,
            "player1_outbox": player1_outbox,
            "player2_outbox": player2_outbox,
            "time_left_minutes": round(time_left, 1),
            "alerts": alerts,
            "status": "ok" if not alerts else "alert",
        }

    def save_report(self, path: str):
        """保存报告"""
        report = self.run_check()
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return report


if __name__ == "__main__":
    monitor = GoMatchMonitor()
    report = monitor.run_check()
    print(json.dumps(report, ensure_ascii=False, indent=2))
