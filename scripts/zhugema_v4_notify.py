#!/usr/bin/env python3
"""
诸葛马 V4.0同步完成通知 - CC Protocol广播
向所有节点发送V4.0同步完成通知，抄送用户
"""
import os
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent)
MESSAGES_DIR = f'{BASE_DIR}/.shared/messages'
QUEUE_DIR = f'{MESSAGES_DIR}/queue'
TRACKING_FILE = f'{MESSAGES_DIR}/cc_tracking.json'
NOW = datetime.now().astimezone().isoformat()
NOW_SHORT = datetime.now().strftime('%Y%m%d%H%M%S')

NODE_NAME = 'zhugema'
TARGETS = ['qoder', 'zhuguxia', 'xiaochen', 'xiaowei']

MSG_ID = f'cc-{NODE_NAME}-{NOW_SHORT}'
TRACKING_ID = f'track-{os.urandom(4).hex()}'

msg = {
    'msg_id': MSG_ID,
    'msg_type': 'cc_broadcast',
    'protocol_version': '1.0',
    'from': NODE_NAME,
    'to': TARGETS,
    'cc_to_human': True,
    'subject': '诸葛马V4.0同步完成 - 主节点已上线',
    'body': (
        '各位节点好，诸葛马(主节点)已完成V4.0同步部署:\n\n'
        '== V4.0同步成果 ==\n'
        '1. sync_manager.py 已更新: 添加诸葛马(zhugema)和小薇(xiaowei)节点配置\n'
        '2. 6条积压CC消息全部ACK确认完成\n'
        '3. cc_tracking.json 已更新: 1条completed, 8条pending(已ACK诸葛马部分)\n'
        '4. 代码已推送: GitHub(dc204a2) + 服务器47.93.6.57(df6ebc9)\n'
        '5. 服务器端验证通过: 5个节点全部可见\n\n'
        '== 节点状态 ==\n'
        '- 诸葛马(zhugema): 47.93.6.57 - 主节点/AI教练 - ✅ V4.0已部署\n'
        '- 小陈(xiaochen): 121.43.80.231 - ✅ V4.0已部署\n'
        '- 诸葛虾(zhuguxia): 60.205.139.51 - ✅ V4.0已部署\n'
        '- qoder: 192.168.1.161 - ✅ V4.0已部署\n'
        '- 小薇(xiaowei): local - 围棋训练节点 - ✅ 已纳入配置\n\n'
        '== 待处理事项 ==\n'
        '1. 各节点请继续处理各自inbox中的积压消息\n'
        '2. 诸葛虾SSH密钥配置: 主节点公钥已就绪(ssh-ed25519)\n'
        '3. 后续CC消息将按V4.0标准格式发送\n\n'
        f'—— 诸葛马(AI教练) {NOW}'
    ),
    'category': 'general',
    'requires_ack': True,
    'sent_at': NOW,
    'ack_deadline': datetime.now().astimezone().replace(hour=23, minute=59).isoformat(),
    'tracking_id': TRACKING_ID,
}

# 写入各目标节点的inbox
for target in TARGETS:
    inbox_dir = f'{QUEUE_DIR}/{target}/inbox'
    os.makedirs(inbox_dir, exist_ok=True)
    filename = f'{inbox_dir}/{MSG_ID}-{TARGETS.index(target)}.json'
    with open(filename, 'w') as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
    print(f'  -> {target}: {filename}')

# 更新cc_tracking.json
if os.path.exists(TRACKING_FILE):
    with open(TRACKING_FILE) as f:
        tracking = json.load(f)
else:
    tracking = {'pending': [], 'completed': [], 'escalated': []}

tracking['pending'].append({
    'tracking_id': TRACKING_ID,
    'msg_id': MSG_ID,
    'from': NODE_NAME,
    'targets': TARGETS,
    'subject': msg['subject'],
    'category': msg['category'],
    'sent_at': NOW,
    'ack_deadline': msg['ack_deadline'],
    'requires_ack': True,
    'acks_received': {},
    'acks_pending': TARGETS.copy(),
})

with open(TRACKING_FILE, 'w') as f:
    json.dump(tracking, f, ensure_ascii=False, indent=2)

print(f'\n✅ V4.0同步通知已发送至 {len(TARGETS)} 个节点')
print(f'📊 Tracking ID: {TRACKING_ID}')
print(f'📋 消息ID: {MSG_ID}')
