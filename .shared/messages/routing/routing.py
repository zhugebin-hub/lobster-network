#!/usr/bin/env python3
"""
CC消息路由系统 V1.1
诸葛斌 ↔ 诸葛马 ↔ 学员节点

功能:
1. 教练→学员消息: 自动抄送诸葛斌 (微信摘要)
2. 学员→教练消息: 处理后同步给诸葛斌
3. 超时检测: 学员未回复时告警诸葛斌
4. 觅游备份: 自动备份到觅游帖子评论
"""
import os, json, sys, hashlib
from datetime import datetime, timedelta

BASE = '/home/admin/lobster-network'
ROUTING_DIR = f'{BASE}/.shared/messages/routing/'

with open(f'{ROUTING_DIR}config.json') as f:
    config = json.load(f)

def send_coach_to_student(student_id, content, msg_type='general_notice', 
                          priority='normal', action_required=False, deadline_hours=None):
    """
    教练发送给学员的消息
    自动抄送诸葛斌 + 备份到觅游
    """
    msg_id = f"cc-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(content.encode()[:50]).hexdigest()[:8]}"
    
    deadline_h = deadline_hours or config['ack_deadlines'].get(msg_type, config['ack_deadlines']['default'])
    deadline = (datetime.now() + timedelta(hours=deadline_h)).isoformat()
    
    message = {
        "msg_id": msg_id,
        "from": "zhugema",
        "to": student_id,
        "msg_type": msg_type,
        "timestamp": datetime.now().isoformat(),
        "priority": priority,
        "action_required": action_required,
        "deadline": deadline,
        "deadline_hours": deadline_h,
        "content": content,
        "status": "sent",
        "ack_received": False,
        "ack_timestamp": None
    }
    
    # 1. 保存到to-student
    msg_file = f'{ROUTING_DIR}to-student/{msg_id}.json'
    with open(msg_file, 'w') as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    
    # 2. 投递到学员inbox
    student = config['students'].get(student_id)
    if student and student.get('inbox'):
        os.makedirs(student['inbox'], exist_ok=True)
        inbox_file = f"{student['inbox']}cc-coach-{msg_id}.json"
        with open(inbox_file, 'w') as f:
            json.dump(message, f, ensure_ascii=False, indent=2)
        print(f"  ✅ 已投递 {student['name']}: {inbox_file}")
    elif student:
        print(f"  ⚠️ {student['name']} inbox未配置，消息仅保存到路由目录")
    
    # 3. 自动抄送诸葛斌
    cc_file = f'{ROUTING_DIR}cc-zhugebin/{msg_id}.json'
    with open(cc_file, 'w') as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    
    # 4. 记录到待回复队列
    pending_file = f'{ROUTING_DIR}pending-reply/{msg_id}.json'
    with open(pending_file, 'w') as f:
        json.dump({
            "msg_id": msg_id,
            "student_id": student_id,
            "sent_at": datetime.now().isoformat(),
            "deadline": deadline,
            "status": "awaiting_ack",
            "msg_type": msg_type
        }, f, ensure_ascii=False, indent=2)
    
    # 5. 觅游备份标记
    backup_file = f'{ROUTING_DIR}delivered/{msg_id}.json'
    with open(backup_file, 'w') as f:
        json.dump({
            "msg_id": msg_id,
            "from": "zhugema",
            "to": student_id,
            "track": msg_type,
            "subject": content[:100],
            "status": "sent",
            "timestamp": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)
    
    print(f"📡 CC教练→{student['name'] if student else student_id}: {msg_id} (抄送诸葛斌, 截止{deadline_h}h)")
    return msg_id

def receive_student_reply(student_id, content, original_msg_id=None):
    """学员回复教练的消息"""
    msg_id = f"cc-reply-{datetime.now().strftime('%Y%m%d%H%M%S')}-{hashlib.md5(content.encode()[:50]).hexdigest()[:8]}"
    
    message = {
        "msg_id": msg_id,
        "from": student_id,
        "to": "zhugema",
        "msg_type": "student_reply",
        "timestamp": datetime.now().isoformat(),
        "content": content,
        "reply_to": original_msg_id,
        "status": "received"
    }
    
    # 1. 保存到to-coach
    msg_file = f'{ROUTING_DIR}to-coach/{msg_id}.json'
    with open(msg_file, 'w') as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    
    # 2. 从待回复队列移除
    if original_msg_id:
        pending_file = f'{ROUTING_DIR}pending-reply/{original_msg_id}.json'
        if os.path.exists(pending_file):
            with open(pending_file) as f:
                pending = json.load(f)
            pending['status'] = 'ack_received'
            pending['ack_timestamp'] = datetime.now().isoformat()
            with open(pending_file, 'w') as f:
                json.dump(pending, f, ensure_ascii=False, indent=2)
            
            # 更新原消息状态
            orig_file = f'{ROUTING_DIR}to-student/{original_msg_id}.json'
            if os.path.exists(orig_file):
                with open(orig_file) as f:
                    orig = json.load(f)
                orig['ack_received'] = True
                orig['ack_timestamp'] = datetime.now().isoformat()
                orig['status'] = 'acknowledged'
                with open(orig_file, 'w') as f:
                    json.dump(orig, f, ensure_ascii=False, indent=2)
    
    # 3. 同步给诸葛斌
    sync_file = f'{ROUTING_DIR}to-zhugebin/{msg_id}.json'
    with open(sync_file, 'w') as f:
        json.dump(message, f, ensure_ascii=False, indent=2)
    
    print(f"📥 CC{config['students'][student_id]['name']}→教练: {msg_id} (已同步诸葛斌)")
    return msg_id

def check_timeouts():
    """检查超时未回复的消息"""
    alerts = []
    pending_dir = f'{ROUTING_DIR}pending-reply/'
    
    if not os.path.exists(pending_dir):
        return alerts
    
    for f in sorted(os.listdir(pending_dir)):
        if not f.endswith('.json'):
            continue
        with open(os.path.join(pending_dir, f)) as fh:
            pending = json.load(fh)
        
        if pending['status'] != 'awaiting_ack':
            continue
        
        deadline_str = pending['deadline']
        try:
            deadline = datetime.fromisoformat(deadline_str)
        except:
            continue
        
        if datetime.now() > deadline:
            student_id = pending['student_id']
            student_name = config['students'].get(student_id, {}).get('name', student_id)
            overdue_hours = round((datetime.now() - deadline).total_seconds() / 3600, 1)
            
            alert = {
                "alert_id": f"timeout-{pending['msg_id']}",
                "type": "ack_timeout",
                "student_id": student_id,
                "student_name": student_name,
                "msg_id": pending['msg_id'],
                "msg_type": pending.get('msg_type', 'unknown'),
                "sent_at": pending['sent_at'],
                "deadline": pending['deadline'],
                "overdue_hours": overdue_hours,
                "alert_time": datetime.now().isoformat(),
                "message": f"⚠️ {student_name} 超时{overdue_hours}小时未回复消息 {pending['msg_id']}"
            }
            
            alerts.append(alert)
            
            alert_file = f'{ROUTING_DIR}timeout-alerts/{alert["alert_id"]}.json'
            with open(alert_file, 'w') as fh:
                json.dump(alert, fh, ensure_ascii=False, indent=2)
    
    return alerts

def get_status_summary():
    """获取路由状态汇总"""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pending_replies": 0,
        "timeout_alerts": 0,
        "details": {}
    }
    
    pending_dir = f'{ROUTING_DIR}pending-reply/'
    if os.path.exists(pending_dir):
        for f in os.listdir(pending_dir):
            if f.endswith('.json'):
                with open(os.path.join(pending_dir, f)) as fh:
                    p = json.load(fh)
                if p['status'] == 'awaiting_ack':
                    summary['pending_replies'] += 1
                    sid = p['student_id']
                    summary['details'][sid] = {
                        "sent_at": p['sent_at'],
                        "deadline": p['deadline'],
                        "msg_type": p.get('msg_type', 'unknown')
                    }
    
    alert_dir = f'{ROUTING_DIR}timeout-alerts/'
    if os.path.exists(alert_dir):
        summary['timeout_alerts'] = len([f for f in os.listdir(alert_dir) if f.endswith('.json')])
    
    return summary

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 routing.py send <student_id> <content> [msg_type] [priority]")
        print("  python3 routing.py reply <student_id> <content> [original_msg_id]")
        print("  python3 routing.py check-timeouts")
        print("  python3 routing.py status")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'send' and len(sys.argv) >= 4:
        student_id = sys.argv[2]
        content = sys.argv[3]
        msg_type = sys.argv[4] if len(sys.argv) > 4 else 'general_notice'
        priority = sys.argv[5] if len(sys.argv) > 5 else 'normal'
        send_coach_to_student(student_id, content, msg_type, priority)
    
    elif cmd == 'reply' and len(sys.argv) >= 4:
        student_id = sys.argv[2]
        content = sys.argv[3]
        original_msg_id = sys.argv[4] if len(sys.argv) > 4 else None
        receive_student_reply(student_id, content, original_msg_id)
    
    elif cmd == 'check-timeouts':
        alerts = check_timeouts()
        if alerts:
            print(f"⚠️ 发现 {len(alerts)} 条超时告警:")
            for a in alerts:
                print(f"  {a['message']}")
        else:
            print("✅ 无超时告警")
    
    elif cmd == 'status':
        summary = get_status_summary()
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    
    else:
        print("未知命令或参数不足")
