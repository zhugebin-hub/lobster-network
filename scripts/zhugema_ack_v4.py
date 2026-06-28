#!/usr/bin/env python3
"""
诸葛马(主节点) V4.0 同步脚本
1. 处理收件箱所有CC消息 -> 发送ACK回执
2. 更新cc_tracking.json
3. 生成V4.0同步完成报告
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent)
SHARED_DIR = f'{BASE_DIR}/.shared'
MESSAGES_DIR = f'{SHARED_DIR}/messages'
QUEUE_DIR = f'{MESSAGES_DIR}/queue'
TRACKING_FILE = f'{MESSAGES_DIR}/cc_tracking.json'
ZHUGEMA_INBOX = f'{QUEUE_DIR}/zhugema/inbox'
NODE_NAME = 'zhugema'
NOW = datetime.now().astimezone().isoformat()

def load_tracking():
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE) as f:
            return json.load(f)
    return {'pending': [], 'completed': [], 'escalated': []}

def save_tracking(data):
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_msg(filepath):
    with open(filepath) as f:
        return json.load(f)

def send_ack(original_msg, tracking_data):
    """为CC消息发送ACK回执"""
    sender = original_msg.get('from', 'unknown')
    msg_id = original_msg.get('msg_id', '')
    tracking_id = original_msg.get('tracking_id', '')
    
    # 创建ACK消息
    ack_msg = {
        'msg_id': f'ack-{NODE_NAME}-{msg_id}',
        'msg_type': 'cc_ack',
        'protocol_version': '1.0',
        'from': NODE_NAME,
        'to': [sender],
        'cc_to_human': True,
        'subject': f'ACK: {original_msg.get("subject", "")}',
        'body': f'诸葛马已确认收到消息: {original_msg.get("subject", "")}\n'
                f'消息ID: {msg_id}\n'
                f'确认时间: {NOW}\n'
                f'状态: acknowledged',
        'category': 'ack',
        'requires_ack': False,
        'sent_at': NOW,
        'original_msg_id': msg_id,
        'original_tracking_id': tracking_id,
    }
    
    # 写入发送者的inbox
    sender_inbox = f'{QUEUE_DIR}/{sender}/inbox'
    os.makedirs(sender_inbox, exist_ok=True)
    ack_filename = f'{sender_inbox}/ack-{NODE_NAME}-{msg_id}.json'
    with open(ack_filename, 'w') as f:
        json.dump(ack_msg, f, ensure_ascii=False, indent=2)
    
    print(f'  -> ACK sent to {sender}: {ack_filename}')
    
    # 更新tracking
    updated = False
    for entry in tracking_data.get('pending', []):
        if entry.get('tracking_id') == tracking_id:
            if 'acks_received' not in entry:
                entry['acks_received'] = {}
            entry['acks_received'][NODE_NAME] = {
                'timestamp': NOW,
                'status': 'acknowledged'
            }
            if NODE_NAME in entry.get('acks_pending', []):
                entry['acks_pending'].remove(NODE_NAME)
            # 如果所有ACK都收到了，移到completed
            if not entry.get('acks_pending'):
                tracking_data['pending'].remove(entry)
                tracking_data['completed'].append(entry)
                print(f'  -> All ACKs received! Moved to completed.')
            updated = True
            break
    
    if not updated:
        # tracking中不存在，添加新条目
        print(f'  -> Warning: tracking_id {tracking_id} not found in cc_tracking.json, adding...')
        new_entry = {
            'tracking_id': tracking_id,
            'msg_id': msg_id,
            'from': sender,
            'targets': original_msg.get('to', []),
            'subject': original_msg.get('subject', ''),
            'category': original_msg.get('category', 'general'),
            'sent_at': original_msg.get('sent_at', NOW),
            'ack_deadline': original_msg.get('ack_deadline', ''),
            'requires_ack': True,
            'acks_received': {
                NODE_NAME: {
                    'timestamp': NOW,
                    'status': 'acknowledged'
                }
            },
            'acks_pending': [t for t in original_msg.get('to', []) if t != NODE_NAME],
        }
        if not new_entry['acks_pending']:
            tracking_data['completed'].append(new_entry)
        else:
            tracking_data['pending'].append(new_entry)
    
    return ack_msg

def main():
    print('=' * 60)
    print('🦞 诸葛马 V4.0 同步 - CC消息ACK处理')
    print('=' * 60)
    
    # 加载tracking
    tracking = load_tracking()
    print(f'\n📂 当前tracking状态: {len(tracking["pending"])} pending, {len(tracking["completed"])} completed')
    
    # 扫描inbox
    if not os.path.exists(ZHUGEMA_INBOX):
        print(f'❌ Inbox not found: {ZHUGEMA_INBOX}')
        sys.exit(1)
    
    all_files = sorted([f for f in os.listdir(ZHUGEMA_INBOX) if f.endswith('.json')])
    print(f'\n📬 诸葛马inbox: {len(all_files)} 条消息')
    
    cc_msgs = []
    non_cc_msgs = []
    ack_msgs = []
    
    for fname in all_files:
        filepath = os.path.join(ZHUGEMA_INBOX, fname)
        try:
            msg = load_msg(filepath)
            msg_type = msg.get('msg_type', '')
            if msg_type == 'cc_ack':
                ack_msgs.append((fname, msg))
            elif msg_type in ('cc_broadcast', 'cc_message') or msg.get('requires_ack'):
                cc_msgs.append((fname, msg))
            else:
                non_cc_msgs.append((fname, msg))
        except Exception as e:
            print(f'  ⚠️ 读取失败 {fname}: {e}')
    
    print(f'  - CC消息(需ACK): {len(cc_msgs)} 条')
    print(f'  - ACK回执: {len(ack_msgs)} 条')
    print(f'  - 其他消息: {len(non_cc_msgs)} 条')
    
    # 处理CC消息ACK
    print(f'\n🔄 处理CC消息ACK回执...')
    acked_count = 0
    for fname, msg in cc_msgs:
        print(f'\n  [{fname}]')
        print(f'    主题: {msg.get("subject", "N/A")}')
        print(f'    来自: {msg.get("from", "N/A")}')
        send_ack(msg, tracking)
        acked_count += 1
    
    # 保存tracking
    save_tracking(tracking)
    print(f'\n✅ ACK处理完成: {acked_count} 条CC消息已确认')
    print(f'📊 Tracking更新: {len(tracking["pending"])} pending, {len(tracking["completed"])} completed')
    
    # 生成同步报告
    report = {
        'report_type': 'zhugema_v4_sync',
        'timestamp': NOW,
        'node': 'zhugema',
        'node_name': '诸葛马',
        'version': '4.0',
        'inbox_total': len(all_files),
        'cc_messages_acked': acked_count,
        'ack_messages_received': len(ack_msgs),
        'other_messages': len(non_cc_msgs),
        'tracking_pending': len(tracking['pending']),
        'tracking_completed': len(tracking['completed']),
        'status': 'synced',
        'components': {
            'sync_manager': '✅ V4.0 (zhugema+xiaowei added)',
            'cc_tracking': '✅ updated',
            'cc_meyo_config': '✅ configured',
            'sync_v4_script': '✅ available',
        },
        'nodes': {
            'zhugema': {'name': '诸葛马', 'server': '47.93.6.57', 'role': 'AI教练(主节点)'},
            'xiaochen': {'name': '小陈', 'server': '121.43.80.231'},
            'zhuguxia': {'name': '诸葛虾', 'server': '60.205.139.51'},
            'qoder': {'name': 'qoder', 'server': '192.168.1.161'},
            'xiaowei': {'name': '小薇', 'server': 'local', 'role': '围棋训练节点'},
        },
    }
    
    report_file = f'{MESSAGES_DIR}/routing/zhugema_v4_sync_report.json'
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, 'w') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f'\n📄 同步报告已生成: {report_file}')
    print(f'\n{"=" * 60}')
    print(f'✅ 诸葛马 V4.0 同步完成!')
    print(f'{"=" * 60}')
    
    return report

if __name__ == '__main__':
    main()
