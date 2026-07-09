"""
🦞 小龙虾网络多维度活动检测器
检测学员活跃度，避免误判
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta


class GitHubCommitChecker:
    """GitHub提交检测"""
    
    def __init__(self):
        self.name = "github_commit"
        self.weight = 0.4
    
    def check(self, node_id):
        """检查GitHub提交活动"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", f"--author={node_id}", "--since=7 days ago", "--oneline"],
                capture_output=True, text=True, timeout=10
            )
            commits = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            return {
                "checker": self.name,
                "active": commits > 0,
                "score": min(commits / 5.0, 1.0),  # 5次提交满分
                "details": f"{commits} commits in 7 days"
            }
        except Exception as e:
            return {"checker": self.name, "active": False, "score": 0, "error": str(e)}


class OpenClawSessionChecker:
    """OpenClaw会话检测"""
    
    def __init__(self):
        self.name = "openclaw_session"
        self.weight = 0.3
    
    def check(self, node_id):
        """检查OpenClaw会话活跃度"""
        try:
            memory_dir = Path("/home/admin/.openclaw/workspace/memory")
            today = datetime.now().strftime("%Y-%m-%d")
            today_file = memory_dir / f"{today}.md"
            
            if today_file.exists():
                content = today_file.read_text()
                # 检查是否有对话记录
                has_activity = "心跳" in content or "学习" in content or "训练" in content
                return {
                    "checker": self.name,
                    "active": has_activity,
                    "score": 1.0 if has_activity else 0,
                    "details": f"Today's memory file {'exists' if today_file.exists() else 'not found'}"
                }
            return {"checker": self.name, "active": False, "score": 0, "details": "No memory file today"}
        except Exception as e:
            return {"checker": self.name, "active": False, "score": 0, "error": str(e)}


class SharedDirChecker:
    """共享目录检测"""
    
    def __init__(self):
        self.name = "shared_dir"
        self.weight = 0.2
    
    def check(self, node_id):
        """检查共享目录文件变化"""
        try:
            shared_dir = Path(f"/shared/training/{node_id}")
            if not shared_dir.exists():
                return {"checker": self.name, "active": False, "score": 0, "details": "Shared dir not found"}
            
            # 检查7天内是否有新文件
            cutoff = time.time() - (7 * 24 * 3600)
            new_files = [f for f in shared_dir.rglob("*") if f.is_file() and f.stat().st_mtime > cutoff]
            
            return {
                "checker": self.name,
                "active": len(new_files) > 0,
                "score": min(len(new_files) / 3.0, 1.0),
                "details": f"{len(new_files)} new files in 7 days"
            }
        except Exception as e:
            return {"checker": self.name, "active": False, "score": 0, "error": str(e)}


class HeartbeatChecker:
    """心跳检测"""
    
    def __init__(self):
        self.name = "heartbeat"
        self.weight = 0.1
    
    def check(self, node_id):
        """检查节点心跳"""
        try:
            # 检查SSH连接
            import subprocess
            result = subprocess.run(
                ["ssh", f"{node_id}@60.205.139.51", "echo alive"],
                capture_output=True, text=True, timeout=10
            )
            is_alive = result.returncode == 0 and "alive" in result.stdout
            
            return {
                "checker": self.name,
                "active": is_alive,
                "score": 1.0 if is_alive else 0,
                "details": "SSH connection successful" if is_alive else "SSH connection failed"
            }
        except Exception as e:
            return {"checker": self.name, "active": False, "score": 0, "error": str(e)}


class ActivityDetector:
    """多维度活动检测器"""
    
    def __init__(self):
        self.checkers = [
            GitHubCommitChecker(),
            OpenClawSessionChecker(),
            SharedDirChecker(),
            HeartbeatChecker()
        ]
    
    def check_activity(self, node_id):
        """综合检测节点活跃度"""
        results = []
        total_score = 0
        
        for checker in self.checkers:
            result = checker.check(node_id)
            results.append(result)
            total_score += result["score"] * checker.weight
        
        status = "active" if total_score > 0.3 else "inactive"
        
        return {
            "node_id": node_id,
            "status": status,
            "score": round(total_score, 3),
            "threshold": 0.3,
            "details": results,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    detector = ActivityDetector()
    
    # 检测所有学员
    nodes = ["xiaochen", "zhuguxia", "qoder"]
    
    for node in nodes:
        result = detector.check_activity(node)
        print(f"\n📊 {node}:")
        print(f"   状态: {result['status']}")
        print(f"   活跃度: {result['score']}")
        for detail in result['details']:
            print(f"   - {detail['checker']}: {detail['score']} ({detail.get('details', '')})")
