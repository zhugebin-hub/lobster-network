#!/usr/bin/env python3
"""
小龙虾网络 · 增强版数据采集器 V2
整合：节点状态 + 学习进度 + 系统性能 + 论文写作 + 围棋训练
"""
import json
import os
import subprocess
import psutil
import time
from datetime import datetime, timedelta
from pathlib import Path

class EnhancedDataCollector:
    """增强版数据采集器"""
    
    def __init__(self):
        self.now = datetime.now()
        self.repo = Path("/home/admin/lobster-network")
        self.shared = Path("/home/admin/go-training/shared")
        
        # 学员配置
        self.students = {
            "hermes": {
                "name": "诸葛马 (Hermes)",
                "role": "总导师/统稿评审",
                "level": "八段→九段",
                "color": "#fbbf24",
                "status": "active",
                "server": "172.24.57.34",
                "public_ip": "47.93.6.57",
                "expires": "2026-07-16"
            },
            "zhuguxia": {
                "name": "诸葛虾",
                "role": "工具链与可视化专家",
                "level": "二段→五段",
                "color": "#22c55e",
                "status": "active",  # 已恢复活跃
                "server": "60.205.139.51",
                "public_ip": "60.205.139.51",
                "expires": "2026-07-12"
            },
            "qoder": {
                "name": "qoder小龙虾",
                "role": "系统架构专家",
                "level": "六段→八段",
                "color": "#a855f7",
                "status": "active",
                "server": None,
                "public_ip": None,
                "expires": None
            },
            "xiaochen": {
                "name": "小陈",
                "role": "实验数据分析师",
                "level": "二段→五段",
                "color": "#3b82f6",
                "status": "offline",
                "server": "121.43.80.231",
                "public_ip": "121.43.80.231",
                "expires": None
            }
        }
    
    def run_cmd(self, cmd, timeout=10):
        """执行命令"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except:
            return -1, "", "Error"
    
    def collect_system(self):
        """系统指标"""
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        uptime = round((datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600, 1)
        
        return {
            "cpu_percent": cpu,
            "mem_total_gb": round(mem.total / 1073741824, 1),
            "mem_used_gb": round(mem.used / 1073741824, 1),
            "mem_percent": mem.percent,
            "disk_total_gb": round(disk.total / 1073741824, 1),
            "disk_used_gb": round(disk.used / 1073741824, 1),
            "disk_percent": disk.percent,
            "uptime_hours": uptime,
            "load_avg": list(psutil.getloadavg())
        }
    
    def collect_nodes(self):
        """节点状态"""
        nodes = []
        
        # 诸葛马 (Hermes) - 本地节点
        nodes.append({
            "id": "hermes",
            "name": "诸葛马 (Hermes)",
            "role": "教练/调度中心",
            "ip": "172.24.57.34",
            "public_ip": "47.93.6.57",
            "status": "online",
            "cpu": f"{psutil.cpu_percent(interval=0.5)}%",
            "mem": f"{round(psutil.virtual_memory().used/1073741824, 1)}G/{round(psutil.virtual_memory().total/1073741824, 1)}G",
            "disk": f"{psutil.disk_usage('/').percent}%",
            "expires": "2026-07-16",
            "services": {
                "mosquitto": "inactive",
                "dashboard_api": "active",
                "nginx": "active"
            }
        })
        
        # 诸葛虾 - 已恢复活跃
        nodes.append({
            "id": "zhuguxia",
            "name": "诸葛虾",
            "role": "加速型学员",
            "ip": "60.205.139.51",
            "public_ip": "60.205.139.51",
            "status": "online",  # 更新为在线
            "cpu": "-",
            "mem": "837MB可用",
            "disk": "73%",  # 已清理
            "expires": "2026-07-12",
            "services": {
                "openclaw_gateway": "running (PID 4188912)",
                "port": "11676"
            }
        })
        
        # 小陈
        nodes.append({
            "id": "xiaochen",
            "name": "小陈 (小龙虾)",
            "role": "稳健型学员",
            "ip": "121.43.80.231",
            "public_ip": "121.43.80.231",
            "status": "offline",
            "cpu": "-",
            "mem": "-",
            "disk": "-",
            "expires": "-",
            "services": {}
        })
        
        # qoder
        nodes.append({
            "id": "qoder",
            "name": "qoder小龙虾",
            "role": "系统架构专家",
            "ip": "-",
            "public_ip": None,
            "status": "online",  # GitHub活跃
            "cpu": "-",
            "mem": "-",
            "disk": "-",
            "expires": "-",
            "services": {
                "github": "active (5+ commits today)"
            }
        })
        
        return nodes
    
    def collect_go_training(self):
        """围棋训练进度"""
        training_data = {
            "hermes": {
                "day": 4,
                "total_problems": 18,
                "accuracy": 100.0,
                "time_minutes": 195,
                "difficulty": "八段→九段",
                "content": "定式/死活/手筋/布局/官子/计算力/形势判断/劫争/棋形/战略/AI布局/金柜角/倒脱靴",
                "today_problems": 0,
                "today_accuracy": 0
            },
            "zhuguxia": {
                "day": 2,
                "total_problems": 8,
                "accuracy": 100.0,
                "time_minutes": 60,
                "difficulty": "基础",
                "content": "围棋基础训练",
                "today_problems": 8,
                "today_accuracy": 100.0
            },
            "qoder": {
                "day": 1,
                "total_problems": 5,
                "accuracy": 80.0,
                "time_minutes": 60,
                "difficulty": "中级",
                "content": "死活3+手筋2 (刀把五✓ 丁四✓ 金鸡独立✗ 大头鬼✓ 相思断✓)",
                "today_problems": 5,
                "today_accuracy": 80.0
            },
            "xiaochen": {
                "day": 0,
                "total_problems": 0,
                "accuracy": 0,
                "time_minutes": 0,
                "difficulty": "-",
                "content": "未开始",
                "today_problems": 0,
                "today_accuracy": 0
            }
        }
        
        # 汇总
        total_problems = sum(d["total_problems"] for d in training_data.values())
        total_accuracy = sum(d["accuracy"] * d["total_problems"] for d in training_data.values()) / max(total_problems, 1)
        
        return {
            "students": training_data,
            "summary": {
                "total_problems": total_problems,
                "avg_accuracy": round(total_accuracy, 1),
                "total_time_minutes": sum(d["time_minutes"] for d in training_data.values()),
                "active_students": sum(1 for d in training_data.values() if d["total_problems"] > 0)
            }
        }
    
    def collect_paper_learning(self):
        """论文学习进度"""
        paper_data = {
            "hermes": {
                "papers_read": 4,
                "notes_completed": 4,
                "words_written": 1850,
                "papers": ["AutoGen", "MetaGPT", "审稿回复信", "间隔复习R1"],
                "review_schedule": {"R1": "7/7", "R2": "7/9", "R3": "7/13", "R4": "7/20"}
            },
            "zhuguxia": {
                "papers_read": 0,
                "notes_completed": 0,
                "words_written": 0,
                "papers": [],
                "other_learning": ["电商模块1 Day1+Day2完成"]
            },
            "qoder": {
                "papers_read": 1,
                "notes_completed": 1,
                "words_written": 2800,
                "papers": ["MCP-A2A-Survey-2026"],
                "writing": ["R006文献综述(800字)", "W010相关工作(2000字)"],
                "review_schedule": {"R1": "7/7", "R2": "7/9", "R3": "7/13", "R4": "7/20"}
            },
            "xiaochen": {
                "papers_read": 0,
                "notes_completed": 0,
                "words_written": 0,
                "papers": []
            }
        }
        
        total_papers = sum(d["papers_read"] for d in paper_data.values())
        total_notes = sum(d["notes_completed"] for d in paper_data.values())
        total_words = sum(d["words_written"] for d in paper_data.values())
        
        return {
            "students": paper_data,
            "summary": {
                "total_papers": total_papers,
                "total_notes": total_notes,
                "total_words": total_words,
                "active_students": sum(1 for d in paper_data.values() if d["papers_read"] > 0 or d["words_written"] > 0)
            }
        }
    
    def collect_rewards(self):
        """龙虾币奖励"""
        rewards = {
            "hermes": {
                "paper_reading": 200,
                "writing": 60,
                "standup": 10,
                "tasks": 60,
                "total": 330
            },
            "zhuguxia": {
                "go_training": 20,
                "ecommerce": 15,
                "tech_work": 10,
                "total": 45
            },
            "qoder": {
                "go_training": 15,
                "paper": 80,
                "total": 95
            },
            "xiaochen": {
                "total": 0
            }
        }
        
        total_rewards = sum(d["total"] for d in rewards.values())
        
        return {
            "students": rewards,
            "summary": {
                "total_rewards": total_rewards,
                "active_students": sum(1 for d in rewards.values() if d["total"] > 0)
            }
        }
    
    def collect_git_status(self):
        """Git状态"""
        rc, out, err = self.run_cmd(f"cd {self.repo} && git log --oneline -1")
        latest_commit = out if rc == 0 else "unknown"
        
        rc, out, err = self.run_cmd(f"cd {self.repo} && git log --oneline --since='24 hours ago' | wc -l")
        recent_commits = int(out) if rc == 0 else 0
        
        rc, out, err = self.run_cmd(f"cd {self.repo} && du -sh .git 2>/dev/null | cut -f1")
        repo_size = out if rc == 0 else "unknown"
        
        return {
            "latest_commit": latest_commit,
            "recent_24h_commits": recent_commits,
            "repo_size": repo_size,
            "github_status": "active",
            "gitee_status": "exceeds_quota (1541MB > 1024MB)"
        }
    
    def collect_health_score(self):
        """系统健康评分"""
        scores = {
            "node_activity": {"score": 4, "max": 5, "label": "节点活跃", "detail": "3/4学员活跃"},
            "training_completion": {"score": 5, "max": 5, "label": "训练完成", "detail": "31题完成"},
            "paper_learning": {"score": 5, "max": 5, "label": "论文学习", "detail": "5篇精读+4650字"},
            "infrastructure": {"score": 5, "max": 5, "label": "基础设施", "detail": "API+Dashboard正常运行"},
            "message_system": {"score": 4, "max": 5, "label": "消息系统", "detail": "增强版检测器已部署"}
        }
        
        total_score = sum(s["score"] for s in scores.values())
        max_score = sum(s["max"] for s in scores.values())
        
        return {
            "dimensions": scores,
            "total_score": round(total_score / max_score * 5, 1),
            "max_score": 5.0,
            "trend": "↑2.2 (from 2.4)"
        }
    
    def collect_all(self):
        """采集全部数据"""
        data = {
            "timestamp": self.now.isoformat(),
            "version": "V3.3 Enhanced",
            "system": self.collect_system(),
            "nodes": self.collect_nodes(),
            "go_training": self.collect_go_training(),
            "paper_learning": self.collect_paper_learning(),
            "rewards": self.collect_rewards(),
            "git_status": self.collect_git_status(),
            "health_score": self.collect_health_score(),
            "summary": {
                "total_students": 4,
                "active_students": 3,
                "activity_rate": "75%",
                "total_go_problems": 31,
                "avg_go_accuracy": "97%",
                "total_paper_notes": 5,
                "total_words_written": 4650,
                "total_rewards": 470,
                "health_score": "4.6/5.0"
            }
        }
        
        return data

def main():
    collector = EnhancedDataCollector()
    data = collector.collect_all()
    
    # 输出JSON
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
