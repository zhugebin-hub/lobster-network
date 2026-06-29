#!/usr/bin/env python3
"""
节点数字孪生 (Node Digital Twin)
部署在每个学员节点上，每5分钟更新一次状态
"""
import json
import os
import time
import subprocess
from datetime import datetime
from pathlib import Path

class NodeDigitalTwin:
    def __init__(self, node_id, hermes_host="47.93.6.57", hermes_user="admin"):
        self.node_id = node_id
        self.hermes_host = hermes_host
        self.hermes_user = hermes_user
        self.twin_file = f"/tmp/node_twin_{node_id}.json"
        self.state = self.load_or_init()
    
    def load_or_init(self):
        if os.path.exists(self.twin_file):
            try:
                with open(self.twin_file) as f:
                    return json.load(f)
            except:
                pass
        return {
            "node_id": self.node_id,
            "load": 0.0,
            "mood": "neutral",
            "skills": {},
            "health": "active",
            "last_heartbeat": datetime.now().isoformat(),
            "current_task": None,
            "stuck_at": None,
            "task_history": [],
            "retry_count": 0,
            "last_submission": None,
            "messages_read": 0
        }
    
    def save(self):
        self.state["last_heartbeat"] = datetime.now().isoformat()
        with open(self.twin_file, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def collect_metrics(self):
        """收集节点指标"""
        # CPU 负载
        try:
            load = os.getloadavg()[0]
            self.state["load"] = round(min(load / 4.0, 1.0), 2)
        except:
            self.state["load"] = 0.0
        
        # 磁盘使用
        try:
            stat = os.statvfs("/")
            used_pct = round(100 * (1 - stat.f_bavail / stat.f_blocks), 1)
            if used_pct > 90:
                self.state["health"] = "critical"
            elif used_pct > 80:
                self.state["health"] = "warning"
            else:
                self.state["health"] = "active"
            self.state["disk_usage_pct"] = used_pct
        except:
            pass
        
        # 情绪状态（基于重试次数）
        retry_count = self.state.get("retry_count", 0)
        if retry_count > 3:
            self.state["mood"] = "frustrated"
        elif retry_count > 1:
            self.state["mood"] = "struggling"
        else:
            self.state["mood"] = "neutral"
        
        # 运行时间
        try:
            with open("/proc/uptime") as f:
                uptime = int(float(f.read().split()[0]))
                self.state["uptime_days"] = uptime // 86400
                self.state["uptime_hours"] = (uptime % 86400) // 3600
        except:
            pass
    
    def is_stuck(self):
        """判断节点是否卡住"""
        return (
            self.state.get("load", 0) > 0.8 and
            self.state.get("mood") in ["frustrated", "struggling"]
        )
    
    def sync_to_hermes(self):
        """同步孪生状态到诸葛马"""
        try:
            dest_dir = f"/home/admin/go-training/shared/twins/"
            cmd = [
                "ssh", self.hermes_user + "@" + self.hermes_host,
                f"mkdir -p {dest_dir}"
            ]
            subprocess.run(cmd, timeout=10, capture_output=True)
            
            cmd = [
                "scp", self.twin_file,
                f"{self.hermes_user}@{self.hermes_host}:{dest_dir}"
            ]
            result = subprocess.run(cmd, timeout=30, capture_output=True)
            if result.returncode == 0:
                self.state["last_sync"] = datetime.now().isoformat()
                return True
            else:
                print(f"同步失败: {result.stderr.decode()}")
                return False
        except Exception as e:
            print(f"同步异常: {e}")
            return False
    
    def pull_messages(self):
        """从诸葛马拉取新消息"""
        try:
            cmd = [
                "ssh", self.hermes_user + "@" + self.hermes_host,
                f"ls /home/admin/go-training/shared/from-hermes/ 2>/dev/null"
            ]
            result = subprocess.run(cmd, timeout=15, capture_output=True, text=True)
            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                # 过滤出与本节点相关的消息
                my_messages = [f for f in files if self.node_id in f or f.startswith(f"day")]
                return my_messages
        except Exception as e:
            print(f"拉取消息失败: {e}")
        return []
    
    def run_once(self):
        """执行一次完整循环"""
        print(f"[{datetime.now().isoformat()}] 节点 {self.node_id} 数字孪生更新")
        
        # 1. 收集指标
        self.collect_metrics()
        
        # 2. 拉取消息
        messages = self.pull_messages()
        self.state["available_messages"] = len(messages)
        self.state["message_list"] = messages[:10]  # 只保留最近10个
        
        # 3. 保存状态
        self.save()
        
        # 4. 同步到诸葛马
        self.sync_to_hermes()
        
        print(f"  负载: {self.state['load']}, 情绪: {self.state['mood']}, "
              f"健康: {self.state['health']}, 消息: {len(messages)}")
    
    def run(self):
        """主循环 - 每5分钟执行一次"""
        print(f"节点数字孪生启动: {self.node_id}")
        while True:
            try:
                self.run_once()
            except Exception as e:
                print(f"循环异常: {e}")
            time.sleep(1200)  # 20分钟

if __name__ == "__main__":
    node_id = os.environ.get("STUDENT_ID", "zhuguxia")
    twin = NodeDigitalTwin(node_id)
    twin.run()
