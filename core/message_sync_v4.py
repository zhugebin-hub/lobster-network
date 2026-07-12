#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 V4.0 - 消息同步系统
教练端统一消息同步：推送→轮询→拉取→ACK验证

作者：诸葛马 (Hermes)
日期：2026-07-01
版本：v4.0
"""

import json
import os
import sys
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# ============================================================
# 配置
# ============================================================

STUDENTS = {
    "xiaochen": {
        "name": "小陈",
        "host": "121.43.80.231",
        "user": "admin",
        "ssh_key": os.path.expanduser("~/.ssh/id_rsa_hermes"),
        "remote_base": "/home/admin/go-training/shared",
        "poller_path": "/home/admin/lobster-network/core/student_poller_v4.py",
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "host": "60.205.139.51",
        "user": "admin",
        "ssh_key": os.path.expanduser("~/.ssh/id_rsa_hermes"),
        "remote_base": "/home/admin/go-training/shared",
        "poller_path": "/home/admin/lobster-network/core/student_poller_v4.py",
    },
}

LOCAL_BASE = "/home/admin/go-training/shared"

# ============================================================
# SSH 工具
# ============================================================

def ssh_cmd(student_id, command, timeout=10):
    """执行SSH命令"""
    cfg = STUDENTS[student_id]
    cmd = [
        "ssh", "-i", cfg["ssh_key"],
        "-o", "StrictHostKeyChecking=no",
        "-o", f"ConnectTimeout={timeout}",
        f"{cfg['user']}@{cfg['host']}",
        command
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout+5)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def scp_to_student(student_id, local_file, remote_path):
    """SCP文件到学员"""
    cfg = STUDENTS[student_id]
    cmd = [
        "scp", "-i", cfg["ssh_key"],
        "-o", "StrictHostKeyChecking=no",
        local_file,
        f"{cfg['user']}@{cfg['host']}:{remote_path}"
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    return result.returncode == 0

def scp_from_student(student_id, remote_path, local_file):
    """SCP文件从学员"""
    cfg = STUDENTS[student_id]
    cmd = [
        "scp", "-i", cfg["ssh_key"],
        "-o", "StrictHostKeyChecking=no",
        f"{cfg['user']}@{cfg['host']}:{remote_path}",
        local_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
    return result.returncode == 0

# ============================================================
# 消息同步
# ============================================================

class MessageSync:
    """消息同步器"""
    
    def __init__(self):
        self.local_base = LOCAL_BASE
    
    def send_message(self, student_id, msg_dict):
        """发送消息到学员（通过SCP）"""
        # 1. 本地保存
        local_inbox = os.path.join(self.local_base, f"to-{student_id}")
        os.makedirs(local_inbox, exist_ok=True)
        
        msg_id = msg_dict.get("id", f"msg_{int(time.time())}")
        filename = f"{msg_id}.json"
        local_file = os.path.join(local_inbox, filename)
        
        with open(local_file, 'w') as f:
            json.dump(msg_dict, f, indent=2, ensure_ascii=False)
        
        # 2. SCP到学员服务器
        remote_path = os.path.join(
            STUDENTS[student_id]["remote_base"],
            f"to-{student_id}",
            filename
        )
        success = scp_to_student(student_id, local_file, remote_path)
        
        if success:
            print(f"  ✅ 消息已发送到 {STUDENTS[student_id]['name']}: {msg_id}")
        else:
            print(f"  ❌ 消息发送失败: {msg_id}")
        
        return success
    
    def collect_replies(self, student_id):
        """收集学员回复（通过SCP）"""
        replies = []
        
        # 1. 从学员端拉取 from-{student}/ 目录
        remote_from = os.path.join(
            STUDENTS[student_id]["remote_base"],
            f"from-{student_id}"
        )
        
        # 列出远程文件
        stdout, stderr, rc = ssh_cmd(student_id, f"ls {remote_from}/*.json 2>/dev/null")
        if rc != 0 or not stdout:
            return replies
        
        remote_files = stdout.strip().split('\n')
        
        # 2. 拉取每个文件
        local_from = os.path.join(self.local_base, f"from-{student_id}")
        os.makedirs(local_from, exist_ok=True)
        
        for remote_file in remote_files:
            filename = os.path.basename(remote_file)
            local_file = os.path.join(local_from, filename)
            
            if scp_from_student(student_id, remote_file, local_file):
                try:
                    with open(local_file, 'r') as f:
                        reply = json.load(f)
                    replies.append(reply)
                    print(f"  ✅ 收到 {STUDENTS[student_id]['name']} 回复: {reply.get('id', filename)}")
                except:
                    pass
        
        return replies
    
    def sync_all(self):
        """同步所有学员"""
        print(f"\n🔄 消息同步开始 ({datetime.now().strftime('%H:%M:%S')})")
        
        all_replies = {}
        for student_id in STUDENTS:
            replies = self.collect_replies(student_id)
            if replies:
                all_replies[student_id] = replies
        
        print(f"\n📊 同步完成: 收到 {sum(len(v) for v in all_replies.values())} 条回复")
        return all_replies
    
    def start_poller(self, student_id):
        """启动学员端轮询器"""
        cfg = STUDENTS[student_id]
        
        # 确保轮询器已部署
        remote_poller = cfg["poller_path"]
        stdout, stderr, rc = ssh_cmd(student_id, f"test -f {remote_poller} && echo OK")
        if rc != 0 or stdout != "OK":
            print(f"  ⚠️ 轮询器未部署到 {cfg['name']}，先部署...")
            local_poller = "/home/admin/lobster-network/core/student_poller_v4.py"
            scp_to_student(student_id, local_poller, remote_poller)
        
        # 启动轮询器（后台运行）
        cmd = f"nohup python3 {remote_poller} {student_id} --daemon > /dev/null 2>&1 &"
        stdout, stderr, rc = ssh_cmd(student_id, cmd)
        
        if rc == 0:
            print(f"  ✅ {cfg['name']} 轮询器已启动")
            return True
        else:
            print(f"  ❌ {cfg['name']} 轮询器启动失败: {stderr}")
            return False
    
    def stop_poller(self, student_id):
        """停止学员端轮询器"""
        cfg = STUDENTS[student_id]
        stdout, stderr, rc = ssh_cmd(student_id, 
            "pkill -f 'student_poller_v4.py' 2>/dev/null; echo 'stopped'")
        print(f"  ⏹ {cfg['name']} 轮询器已停止")
        return True
    
    def check_poller_status(self, student_id):
        """检查轮询器状态"""
        cfg = STUDENTS[student_id]
        
        # 检查进程
        stdout, stderr, rc = ssh_cmd(student_id, 
            "ps aux | grep student_poller_v4 | grep -v grep")
        running = "student_poller_v4" in stdout
        
        # 读取状态文件
        state_file = os.path.join(cfg["remote_base"], "poller_state", f"{student_id}_state.json")
        stdout2, stderr2, rc2 = ssh_cmd(student_id, f"cat {state_file} 2>/dev/null")
        
        status = {
            "student": cfg["name"],
            "running": running,
            "state": None
        }
        
        if rc2 == 0 and stdout2:
            try:
                status["state"] = json.loads(stdout2)
            except:
                pass
        
        return status

# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    sync = MessageSync()
    
    if len(sys.argv) < 2:
        print("用法: python3 message_sync_v4.py <command> [args]")
        print("命令:")
        print("  start <student>     - 启动学员端轮询器")
        print("  stop <student>      - 停止学员端轮询器")
        print("  status [student]    - 检查轮询器状态")
        print("  send <student> <file> - 发送消息文件到学员")
        print("  collect [student]   - 收集学员回复")
        print("  sync                - 同步所有学员")
        print("  test                - 端到端通信测试")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        student = sys.argv[2] if len(sys.argv) > 2 else None
        if student:
            sync.start_poller(student)
        else:
            for s in STUDENTS:
                sync.start_poller(s)
    
    elif command == "stop":
        student = sys.argv[2] if len(sys.argv) > 2 else None
        if student:
            sync.stop_poller(student)
        else:
            for s in STUDENTS:
                sync.stop_poller(s)
    
    elif command == "status":
        student = sys.argv[2] if len(sys.argv) > 2 else None
        if student:
            status = sync.check_poller_status(student)
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            for s in STUDENTS:
                status = sync.check_poller_status(s)
                print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif command == "send":
        if len(sys.argv) < 4:
            print("用法: python3 message_sync_v4.py send <student> <json_file>")
            sys.exit(1)
        student = sys.argv[2]
        filepath = sys.argv[3]
        with open(filepath, 'r') as f:
            msg = json.load(f)
        sync.send_message(student, msg)
    
    elif command == "collect":
        student = sys.argv[2] if len(sys.argv) > 2 else None
        if student:
            sync.collect_replies(student)
        else:
            sync.sync_all()
    
    elif command == "sync":
        sync.sync_all()
    
    elif command == "test":
        print("🧪 端到端通信测试")
        print("=" * 50)
        
        # 1. 启动轮询器
        print("\n1️⃣ 启动轮询器...")
        for s in STUDENTS:
            sync.start_poller(s)
        
        time.sleep(2)
        
        # 2. 发送测试消息
        print("\n2️⃣ 发送测试消息...")
        for s in STUDENTS:
            test_msg = {
                "id": f"test_{s}_{int(time.time())}",
                "type": "system",
                "action": "ping",
                "message": "这是来自诸葛马的测试消息，请回复pong",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            sync.send_message(s, test_msg)
        
        time.sleep(3)
        
        # 3. 收集回复
        print("\n3️⃣ 收集回复...")
        all_replies = sync.sync_all()
        
        # 4. 检查ACK
        print("\n4️⃣ 检查结果...")
        for s in STUDENTS:
            if s in all_replies:
                for reply in all_replies[s]:
                    print(f"  📨 {STUDENTS[s]['name']}: {reply.get('type')} - {reply.get('status', '?')}")
            else:
                print(f"  ❌ {STUDENTS[s]['name']}: 无回复")
        
        print("\n✅ 测试完成")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
