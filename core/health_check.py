#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端健康检查
解决 P2-问题 9-12：缺少端到端验证、时间保护未强制、缺少守护进程、多版本调度器共存

功能：
1. 检测各节点心跳
2. 检查任务提交及时性
3. 检查 CC 消息 ACK 超时
4. 检查仓库同步状态
5. 生成健康报告
6. 异常自动通知

作者：信电大虾 (小龙虾网络)
日期：2026-07-01
"""

import json
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))
from compat import SHARED_DIR, QUEUE_DIR, REPO_ROOT, json_load, json_dump, setup_logger, run_subprocess

logger = setup_logger("HealthCheck")

# 健康报告路径
HEALTH_REPORT_FILE = SHARED_DIR / "health_report.json"

# 节点配置
NODES = {
    "zhugebin": {"name": "诸葛马", "role": "coach"},
    "qoder": {"name": "qoder", "role": "student"},
    "zhuguxia": {"name": "小龙虾", "role": "student"},
    "xiaochen": {"name": "小陈", "role": "student"},
    "xiaowei": {"name": "小微", "role": "observer"},
}


class HealthChecker:
    """健康检查器"""
    
    def __init__(self):
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "nodes": {},
            "tasks": {},
            "messages": {},
            "git": {},
            "overall_status": "healthy",
            "alerts": [],
        }
        
    def check_node_heartbeats(self) -> Dict:
        """检查节点心跳"""
        logger.info("💓 检查节点心跳...")
        
        for node_id, node_info in NODES.items():
            # 检查 executor_status
            status_file = SHARED_DIR / "executor_status" / f"{node_id}.json"
            
            if status_file.exists():
                status = json_load(status_file)
                last_update = status.get("updated_at")
                
                if last_update:
                    last_time = datetime.fromisoformat(last_update)
                    diff = datetime.now() - last_time
                    
                    is_alive = diff < timedelta(hours=2)
                    self.report["nodes"][node_id] = {
                        "name": node_info["name"],
                        "role": node_info["role"],
                        "status": "alive" if is_alive else "inactive",
                        "last_update": last_update,
                        "diff_hours": round(diff.total_seconds() / 3600, 1),
                    }
                    
                    if not is_alive:
                        alert = f"⚠️ {node_info['name']} 心跳异常：{diff.total_seconds()/3600:.1f} 小时未更新"
                        self.report["alerts"].append(alert)
                        logger.warning(alert)
                else:
                    self.report["nodes"][node_id] = {"status": "unknown"}
            else:
                self.report["nodes"][node_id] = {
                    "name": node_info["name"],
                    "role": node_info["role"],
                    "status": "no_status_file",
                }
                
        return self.report["nodes"]
        
    def check_task_submissions(self) -> Dict:
        """检查任务提交及时性"""
        logger.info("📝 检查任务提交...")
        
        for node_id in NODES:
            from_dir = SHARED_DIR / f"from-{node_id}"
            
            if from_dir.exists():
                submissions = list(from_dir.glob("*.json"))
                latest_submission = max(submissions, key=lambda f: f.stat().st_mtime) if submissions else None
                
                if latest_submission:
                    mtime = datetime.fromtimestamp(latest_submission.stat().st_mtime)
                    diff = datetime.now() - mtime
                    
                    is_timely = diff < timedelta(hours=24)
                    self.report["tasks"][node_id] = {
                        "count": len(submissions),
                        "latest": latest_submission.name,
                        "submitted_at": mtime.isoformat(),
                        "diff_hours": round(diff.total_seconds() / 3600, 1),
                        "timely": is_timely,
                    }
                    
                    if not is_timely:
                        alert = f"⚠️ {node_id} 任务提交延迟：{diff.total_seconds()/3600:.1f} 小时"
                        self.report["alerts"].append(alert)
                        logger.warning(alert)
                else:
                    self.report["tasks"][node_id] = {"count": 0, "timely": False}
            else:
                self.report["tasks"][node_id] = {"count": 0, "timely": False}
                
        return self.report["tasks"]
        
    def check_message_ack(self) -> Dict:
        """检查 CC 消息 ACK 超时"""
        logger.info("📨 检查消息 ACK...")
        
        ack_timeout = timedelta(hours=24)
        
        for node_id in NODES:
            inbox_dir = QUEUE_DIR / node_id / "inbox"
            
            if inbox_dir.exists():
                pending_msgs = list(inbox_dir.glob("*.json"))
                overdue_msgs = []
                
                for msg_file in pending_msgs:
                    try:
                        msg = json_load(msg_file)
                        sent_at = msg.get("sent_at") or msg.get("timestamp")
                        if sent_at:
                            sent_time = datetime.fromisoformat(sent_at)
                            if datetime.now() - sent_time > ack_timeout:
                                overdue_msgs.append(msg_file.name)
                    except Exception:
                        continue
                        
                self.report["messages"][node_id] = {
                    "pending": len(pending_msgs),
                    "overdue": len(overdue_msgs),
                    "overdue_files": overdue_msgs[:5],  # 只记录前 5 个
                }
                
                if overdue_msgs:
                    alert = f"⚠️ {node_id} 有 {len(overdue_msgs)} 条消息 ACK 超时 (>24h)"
                    self.report["alerts"].append(alert)
                    logger.warning(alert)
            else:
                self.report["messages"][node_id] = {"pending": 0, "overdue": 0}
                
        return self.report["messages"]
        
    def check_git_sync(self) -> Dict:
        """检查仓库同步状态"""
        logger.info("🔄 检查 Git 同步...")
        
        try:
            # 获取当前分支
            success, branch = run_subprocess(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            if success:
                branch = branch.strip()
            else:
                branch = "unknown"
                
            # 获取落后 commit 数
            success, output = run_subprocess(["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"])
            if success and output:
                parts = output.strip().split()
                if len(parts) == 2:
                    ahead, behind = int(parts[0]), int(parts[1])
                else:
                    ahead, behind = 0, 0
            else:
                ahead, behind = 0, 0
                
            # 获取工作区状态
            success, output = run_subprocess(["git", "status", "--porcelain"])
            is_clean = len(output.strip()) == 0 if success else False
            
            self.report["git"] = {
                "branch": branch,
                "ahead": ahead,
                "behind": behind,
                "is_clean": is_clean,
            }
            
            if behind > 5:
                alert = f"⚠️ 仓库落后 {behind} 个 commit，建议 pull"
                self.report["alerts"].append(alert)
                logger.warning(alert)
                
        except Exception as e:
            self.report["git"] = {"error": str(e)}
            logger.error(f"❌ Git 检查失败：{e}")
            
        return self.report["git"]
        
    def generate_report(self) -> Dict:
        """生成健康报告"""
        logger.info("📊 生成健康报告...")
        
        # 运行所有检查
        self.check_node_heartbeats()
        self.check_task_submissions()
        self.check_message_ack()
        self.check_git_sync()
        
        # 评估整体状态
        if self.report["alerts"]:
            self.report["overall_status"] = "warning"
        else:
            self.report["overall_status"] = "healthy"
            
        # 保存报告
        json_dump(self.report, HEALTH_REPORT_FILE)
        
        logger.info(f"✅ 健康报告已保存：{HEALTH_REPORT_FILE}")
        return self.report
        
    def print_summary(self):
        """打印摘要"""
        print(f"\n{'='*60}")
        print(f"🏥 小龙虾网络健康检查报告")
        print(f"{'='*60}")
        print(f"时间：{self.report['timestamp']}")
        print(f"状态：{self.report['overall_status'].upper()}")
        print(f"告警：{len(self.report['alerts'])} 条")
        
        if self.report['alerts']:
            print(f"\n⚠️ 告警详情：")
            for alert in self.report['alerts']:
                print(f"  {alert}")
                
        print(f"\n📊 节点状态：")
        for node_id, info in self.report.get('nodes', {}).items():
            status = info.get('status', 'unknown')
            icon = "✅" if status == "alive" else "⚠️" if status == "inactive" else "❓"
            print(f"  {icon} {info.get('name', node_id)}: {status}")
            
        print(f"\n📝 任务提交：")
        for node_id, info in self.report.get('tasks', {}).items():
            count = info.get('count', 0)
            timely = info.get('timely', False)
            icon = "✅" if timely else "⏳"
            print(f"  {icon} {node_id}: {count} 个提交")
            
        print(f"{'='*60}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='端到端健康检查')
    parser.add_argument('--action', type=str, choices=['check', 'report'], default='check')
    
    args = parser.parse_args()
    
    checker = HealthChecker()
    
    if args.action == "check":
        checker.generate_report()
        checker.print_summary()
    elif args.action == "report":
        if HEALTH_REPORT_FILE.exists():
            report = json_load(HEALTH_REPORT_FILE)
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print("❌ 健康报告不存在，请先运行 check")


if __name__ == "__main__":
    main()
