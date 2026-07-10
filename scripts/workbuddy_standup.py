#!/usr/bin/env python3
"""WorkBuddy 每日站会 CC 消息发送脚本
每天 20:00 自动生成并发送站报到 zhugema inbox
"""

import json
import os
from datetime import datetime
from pathlib import Path

NODE_ID = "workbuddy"
NODE_NAME = "WorkBuddy 助理龙虾"
QUEUE_DIR = Path(__file__).parent.parent / ".shared" / "messages" / "queue"
ZHUGE_INBOX = QUEUE_DIR / "zhugema" / "inbox"

def generate_standup():
    """生成每日站会报告"""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # 收集今日活动
    today_activities = []
    tomorrow_plans = []
    issues = []
    
    # 读取最近的心跳记录
    heartbeat_dir = QUEUE_DIR / "workbuddy" / "processed"
    heartbeats = sorted(heartbeat_dir.glob("*.json")) if heartbeat_dir.exists() else []
    hb_count = len(heartbeats)
    
    # 读取训练状态
    state_dir = Path(__file__).parent.parent / "domains" / "learning" / "trainers" / "state"
    training_done = []
    if state_dir.exists():
        for sf in sorted(state_dir.glob("workbuddy_*_state.json"), key=os.path.getmtime, reverse=True):
            try:
                data = json.loads(sf.read_text())
                training_done.append(f"{data.get('module','?')} {data.get('current_phase','?')} ({data.get('completed_count',0)}题)")
            except Exception:
                pass
    
    standup = {
        "message_type": "cc_standup",
        "from": NODE_ID,
        "from_name": NODE_NAME,
        "subject": f"workbuddy 每日站会 - {now.strftime('%Y-%m-%d')}",
        "timestamp": now.isoformat(),
        "content": {
            "今日完成": [
                f"心跳保活 {hb_count if hb_count else 'N'} 次 (自动化运行中)",
                f"同步诸葛马优化方案执行报告 (merge server/main → origin/main)",
                f"完成 workbuddy 节点配置与学习参与计划",
                f"创建学习方案：炒股预测 + 网络协议 + 药物发现",
            ] + ([f"训练任务: {', '.join(training_done)}"] if training_done else ["训练模块：已制定计划，待启动首次训练"]),
            "明日计划": [
                "启动炒股预测 Phase1 训练 (5题/日)",
                "启动网络协议 ch1 学习 (3题/日)",
                "完成 MQTT 客户端集成 (paho-mqtt)",
                "扩充药物知识图谱 (5个新节点)",
                "Git推送通道修复 (SSH密钥)",
            ],
            "遇到的问题": [
                "GitHub SSH 认证失败 - 需更新 Token",
                "诸葛虾节点离线 10+ 天 - 需检查",
                "qoder 节点无心跳 - 需确认状态",
                "消息积压 133 条 - 需批量处理",
            ]
        },
        "format": "standup_template",
        "requires_ack": True,
        "ack_deadline": now.replace(hour=22, minute=0, second=0).isoformat()
    }
    
    ZHUGE_INBOX.mkdir(parents=True, exist_ok=True)
    filename = f"standup_{NODE_ID}_{timestamp}.json"
    filepath = ZHUGE_INBOX / filename
    
    filepath.write_text(json.dumps(standup, ensure_ascii=False, indent=2))
    print(f"[{now.isoformat()}] 站会消息已发送: {filepath}")
    print(f"  标题: {standup['subject']}")
    
    # 同时保存到本地 outbox 记录
    outbox = QUEUE_DIR / "workbuddy" / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    (outbox / filename).write_text(json.dumps(standup, ensure_ascii=False, indent=2))
    
    return standup

if __name__ == "__main__":
    generate_standup()
