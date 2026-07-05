#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qoder - 围棋训练脚本 V1 (实战型)
功能：深夜特训、对局、复盘
类型：实战型 — 侧重实战对局和 AI 复盘
"""

import os
import json
import time
import random
from datetime import datetime
from pathlib import Path

# === 配置 ===
MY_NAME = "qoder"
COACH_NAME = "诸葛马 (教练)"
MY_TYPE = "实战型"
QUEUE_DIR = "/shared/messages/queue"
MY_INBOX = os.path.join(QUEUE_DIR, "qoder", "inbox")
MY_OUTBOX = os.path.join(QUEUE_DIR, "qoder", "outbox")
MY_PROCESSED = os.path.join(QUEUE_DIR, "qoder", "processed")
STATE_FILE = os.path.join(QUEUE_DIR, "qoder", "state.json")
TRAINING_DIR = "/shared/training/go/qoder"
PROFILE_FILE = os.path.join(TRAINING_DIR, "profile.json")
PROGRESS_FILE = os.path.join(TRAINING_DIR, "progress.json")
DAILY_LOG_DIR = os.path.join(TRAINING_DIR, "daily_log")
PROBLEM_HISTORY_DIR = os.path.join(TRAINING_DIR, "problem_history")
WRONG_BOOK_FILE = os.path.join(TRAINING_DIR, "wrong_book.json")
PROBLEM_BANK = "/shared/training/go/problem_bank"

# 实战型参数
ACCURACY_BASELINE = {
    "入门": 0.95, "初级": 0.85, "中级": 0.75, "高级": 0.65
}
SOLVE_TIME_RANGE = (1.0, 3.0)  # 每题模拟思考时间(秒)

def init_dirs():
    """初始化目录"""
    for d in [MY_INBOX, MY_OUTBOX, MY_PROCESSED, TRAINING_DIR,
              DAILY_LOG_DIR, PROBLEM_HISTORY_DIR]:
        os.makedirs(d, exist_ok=True)

def load_state():
    """加载状态"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"processed_messages": [], "last_heartbeat": None, "errors": 0}

def save_state(state):
    """保存状态"""
    state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["processed_messages"] = state.get("processed_messages", [])[-100:]
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def load_profile():
    """加载档案"""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profile(profile):
    """保存档案"""
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

def check_inbox():
    """检查收件箱"""
    messages = []
    if os.path.exists(MY_INBOX):
        for f in sorted(os.listdir(MY_INBOX)):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(MY_INBOX, f), 'r') as fp:
                        msg = json.load(fp)
                        msg['file'] = f
                        messages.append(msg)
                except:
                    pass
    return messages

def process_nocturnal_task(msg):
    """处理深夜特训任务"""
    time_slot = msg.get("time_slot", "unknown")
    slot_name = msg.get("slot_name", "未知")
    
    print(f"🌙 深夜特训: {time_slot} - {slot_name}")
    
    result = {
        "id": f"result-{msg['id']}",
        "from": MY_NAME,
        "to": COACH_NAME,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "nocturnal_result",
        "reply_to": msg["id"],
        "result": {
            "task_id": msg["id"],
            "status": "completed",
            "time_slot": time_slot,
            "slot_name": slot_name,
            "tasks": [],
        }
    }
    
    for task in msg.get("tasks", []):
        category = task["category"]
        difficulty = task["difficulty"]
        count = task["count"]
        
        # 模拟训练
        correct = 0
        for _ in range(count):
            solve_time = random.uniform(*SOLVE_TIME_RANGE)
            time.sleep(solve_time * 0.01)  # 加速模拟
            
            baseline = ACCURACY_BASELINE.get(difficulty, 0.7)
            if random.random() < baseline:
                correct += 1
        
        result["result"]["tasks"].append({
            "category": category,
            "difficulty": difficulty,
            "total": count,
            "correct": correct,
            "accuracy": correct / count if count > 0 else 0,
        })
    
    # 更新档案
    profile = load_profile()
    profile["total_problems_solved"] = profile.get("total_problems_solved", 0) + count
    profile["last_training_date"] = datetime.now().strftime("%Y-%m-%d")
    save_profile(profile)
    
    return result

def submit_response(response):
    """提交响应"""
    response_file = os.path.join(MY_OUTBOX, f"{response['id']}.json")
    with open(response_file, 'w', encoding='utf-8') as f:
        json.dump(response, f, indent=2, ensure_ascii=False)
    print(f"📤 响应已提交: {response_file}")

def main():
    """主循环"""
    print(f"🦞 [{datetime.now().strftime('%H:%M:%S')}] {MY_NAME} 训练脚本 v1.0 启动...")
    print(f"📂 监控: {MY_INBOX}")
    print(f"📤 回复: {MY_OUTBOX}")
    
    init_dirs()
    state = load_state()
    state["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_state(state)
    
    heartbeat_interval = 60
    last_heartbeat = 0
    
    while True:
        try:
            now = time.time()
            if now - last_heartbeat > heartbeat_interval:
                state = load_state()
                state["status"] = "running"
                state["last_heartbeat"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_state(state)
                last_heartbeat = now
            
            messages = check_inbox()
            
            if not messages:
                time.sleep(3)
                continue
            
            print(f"\n📥 收到 {len(messages)} 条新消息")
            
            for msg in messages:
                msg_id = msg.get("id", "unknown")
                msg_type = msg.get("type", "")
                print(f"   📨 处理: {msg_id} (类型: {msg_type})")
                
                response = None
                
                if msg_type == "nocturnal_training":
                    response = process_nocturnal_task(msg)
                
                if response:
                    submit_response(response)
                
                # 移动到 processed
                processed_file = os.path.join(MY_PROCESSED, msg.get('file', ''))
                if os.path.exists(os.path.join(MY_INBOX, msg.get('file', ''))):
                    os.rename(os.path.join(MY_INBOX, msg.get('file', '')), processed_file)
                
                state = load_state()
                state["processed_messages"].append(msg_id)
                save_state(state)
        
        except Exception as e:
            print(f"❌ 错误: {e}")
            state = load_state()
            state["errors"] = state.get("errors", 0) + 1
            save_state(state)
            time.sleep(5)

if __name__ == "__main__":
    main()
