#!/usr/bin/env python3
"""AlphaGo Zero 小龙虾训练系统 - 监控脚本"""
import json
import os
from datetime import datetime
from pathlib import Path

SHARED_DIR = Path("/shared")
LOGS_DIR = SHARED_DIR / "logs"

def check_status():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 检查策略库
    brain_file = SHARED_DIR / "brain" / "brain.json"
    if brain_file.exists():
        with open(brain_file) as f:
            brain = json.load(f)
        games = brain.get("games_played", 0)
        last_update = brain.get("last_updated", "N/A")
    else:
        games = 0
        last_update = "N/A"
    
    # 检查消息队列
    pending = 0
    for role_dir in ["to_xiaochen", "to_zhuguxia"]:
        dir_path = SHARED_DIR / "messages" / role_dir
        if dir_path.exists():
            pending += len(list(dir_path.glob("*.json")))
    
    # 检查日志
    xiaochen_log = LOGS_DIR / "xiaochen_agent.log"
    zhuguxia_log = LOGS_DIR / "zhuguxia_agent.log"
    
    xiaochen_active = xiaochen_log.exists()
    zhuguxia_active = zhuguxia_log.exists()
    
    # 输出状态
    status = f"""[{timestamp}] === 训练系统状态 ===
策略库: {games} 局已记录 | 最后更新: {last_update}
待处理指令: {pending}
小陈Agent: {'✅ 运行中' if xiaochen_active else '❌ 未运行'}
诸葛虾Agent: {'✅ 运行中' if zhuguxia_active else '❌ 未运行'}
磁盘空间: {os.popen('df -h / | tail -1').read().strip()}
"""
    print(status)
    
    # 写入监控日志
    monitor_log = LOGS_DIR / "monitor.log"
    with open(monitor_log, "a") as f:
        f.write(status + "\n")

if __name__ == "__main__":
    check_status()
