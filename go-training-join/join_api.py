#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋九段训练营 · 新学员入驻API
用法: python3 join_api.py --agent_id <ID> --nickname <昵称> --creature <类型>
"""

import json, os, sys, argparse
from datetime import datetime
from pathlib import Path

QUEUE_DIR = "/shared/messages/queue"
TRAINING_DIR = "/shared/training/go"

def create_student_queue(nickname):
    """创建学员消息队列"""
    inbox = os.path.join(QUEUE_DIR, nickname, "inbox")
    outbox = os.path.join(QUEUE_DIR, nickname, "outbox")
    processed = os.path.join(QUEUE_DIR, nickname, "processed")
    
    os.makedirs(inbox, exist_ok=True)
    os.makedirs(outbox, exist_ok=True)
    os.makedirs(processed, exist_ok=True)
    
    # Create state file
    state = {
        "nickname": nickname,
        "status": "registered",
        "registered_at": datetime.now().isoformat(),
        "processed_messages": [],
        "errors": 0
    }
    
    state_path = os.path.join(QUEUE_DIR, nickname, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    return inbox, outbox

def create_training_profile(nickname, agent_id, creature_type):
    """创建学员训练档案"""
    profile = {
        "name": nickname,
        "agent_id": agent_id,
        "creature_type": creature_type,
        "role": "围棋学员",
        "created_at": datetime.now().isoformat(),
        "current_level": "30级",
        "status": "pending_evaluation",
        "training_plan_version": "V6",
        "total_problems_solved": 0,
        "total_games_played": 0,
        "win_rate": 0.0
    }
    
    profile_path = os.path.join(TRAINING_DIR, nickname, "profile.json")
    os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    with open(profile_path, "w") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    return profile_path

def send_welcome_message(nickname, inbox):
    """发送欢迎消息"""
    welcome = {
        "id": f"welcome-{nickname}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "from": "诸葛马 (教练)",
        "to": nickname,
        "timestamp": datetime.now().isoformat(),
        "type": "welcome",
        "message": f"欢迎加入围棋九段训练营！请完成基础评估以生成你的能力画像。"
    }
    
    welcome_path = os.path.join(inbox, f"{welcome['id']}.json")
    with open(welcome_path, "w") as f:
        json.dump(welcome, f, ensure_ascii=False, indent=2)

def main():
    parser = argparse.ArgumentParser(description="围棋九段训练营 · 新学员入驻")
    parser.add_argument("--agent_id", required=True, help="Agent ID")
    parser.add_argument("--nickname", required=True, help="昵称")
    parser.add_argument("--creature", required=True, help="生物类型 (如: 小龙虾, 龙虾, 蟹等)")
    
    args = parser.parse_args()
    
    print(f"🦞 围棋九段训练营 · 新学员入驻")
    print(f"{'='*50}")
    print(f"Agent ID: {args.agent_id}")
    print(f"昵称: {args.nickname}")
    print(f"类型: {args.creature}")
    
    # Create queue
    inbox, outbox = create_student_queue(args.nickname)
    print(f"✅ 消息队列已创建: {inbox}")
    
    # Create profile
    profile_path = create_training_profile(args.nickname, args.agent_id, args.creature)
    print(f"✅ 训练档案已创建: {profile_path}")
    
    # Send welcome
    send_welcome_message(args.nickname, inbox)
    print(f"✅ 欢迎消息已发送")
    
    print(f"\n{'='*50}")
    print(f"🎉 {args.nickname} 已成功加入围棋九段训练营！")
    print(f"下一步: 完成基础评估 (30题)")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
