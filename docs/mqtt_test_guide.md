# 🦞 小龙虾网络 MQTT 测试操作手册

> **版本**: v1.2 | **日期**: 2026-07-03
> **MQTT Broker**: `47.93.6.57:1883`（诸葛马 公网IP）
> **防火墙**: ✅ 已开放 TCP 1883，来源 0.0.0.0/0

---

## 一、前置检查

### 1. 确认文件已到位

```bash
cd /home/admin/lobster-network/core
ls -la mqtt_client_base.py mqtt_student_subscriber.py
```

缺少文件请联系诸葛马重新 SCP。

### 2. 确认 paho-mqtt 已安装

```bash
python3 -c "import paho.mqtt.client; print('paho-mqtt OK')"
```

报错则安装：`pip3 install paho-mqtt`

### 3. 确认 1883 端口可达

```bash
timeout 5 bash -c 'echo > /dev/tcp/47.93.6.57/1883' && echo '端口可达 ✅' || echo '端口不通 ❌'
```

---

## 二、诸葛虾测试（直连模式）

诸葛虾 (172.24.56.3) 与诸葛马同 VPC，**直连公网 IP**。

### 测试 1：基础连接

```bash
cd /home/admin/lobster-network
python3 -c "
import sys, time
sys.path.insert(0, '.')
from core.mqtt_client_base import MqttClientBase, Topics

client = MqttClientBase('zhuguxia', broker_host='47.93.6.57')
ok = client.connect()
print('连接:', '成功 ✅' if ok else '失败 ❌')
time.sleep(2)
if ok:
    client.publish(Topics.heartbeat('zhuguxia'), {'test': '诸葛虾 MQTT 在线'})
    print('心跳已发送 ✅')
    client.publish(Topics.online_status('zhuguxia'), {'status': 'online'})
    print('在线状态已发布 ✅')
time.sleep(1)
client.disconnect()
print('测试完成！')
"
```

**预期**：连接成功 ✅ 心跳已发送 ✅ 在线状态已发布 ✅ 测试完成！

### 测试 2：接收教练消息 + 自动 ACK

```bash
cd /home/admin/lobster-network
python3 -c "
import sys, time, json
sys.path.insert(0, '.')
from core.mqtt_client_base import MqttClientBase, Topics, parse_message

client = MqttClientBase('zhuguxia-sub', broker_host='47.93.6.57')
client.connect()
time.sleep(2)

msgs = []
def on_message(topic, payload):
    msg = parse_message(payload)
    msgs.append(msg)
    print('收到消息:')
    print('  主题:', topic)
    print('  类型:', msg.get('type'))
    print('  内容:', json.dumps(msg.get('payload', {}), ensure_ascii=False))
    # 自动回复 ACK
    ack = {
        'id': 'ack_' + msg.get('id', ''),
        'type': 'ack',
        'original_id': msg.get('id'),
        'original_type': msg.get('type'),
        'status': 'received',
        'student_id': 'zhuguxia',
    }
    client.publish(Topics.student_to_coach('zhuguxia'), json.dumps(ack, ensure_ascii=False))
    print('  ACK 已发送 ✅')

client.on_message(Topics.coach_to_student('zhuguxia'), on_message)
print('等待教练消息（30秒）...')
print('请通知诸葛马向 zhuguxia 发送测试消息')
time.sleep(30)
print('共收到 {} 条消息'.format(len(msgs)))
client.disconnect()
"
```

**操作**：运行后保持终端开启 30 秒，同时通知诸葛马发送测试消息。

### 测试 3：启动长期订阅器

```bash
cd /home/admin/lobster-network
nohup python3 core/mqtt_student_subscriber.py zhuguxia --broker 47.93.6.57:1883 \
  > /home/admin/go-training/shared/logs/zhuguxia_mqtt.log 2>&1 &
echo "订阅器 PID: $!"
```

**验证运行**：
```bash
ps aux | grep mqtt_student_subscriber | grep -v grep
tail -20 /home/admin/go-training/shared/logs/zhuguxia_mqtt.log
```

**停止**：`pkill -f mqtt_student_subscriber`

---

## 三、小陈测试（文件桥接模式）

小陈 (121.43.80.231) 跨 VPC，通过**文件目录桥接**与 MQTT 通信。

### 测试 1：发送消息给教练

```bash
cd /home/admin/lobster-network
python3 -c "
import json, os
from datetime import datetime

d = '/home/admin/go-training/shared/from-xiaochen/'
os.makedirs(d, exist_ok=True)

f = d + 'mqtt_test_{}.json'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
with open(f, 'w') as fh:
    json.dump({
        'type': 'ack',
        'payload': {'message': '小陈 MQTT 桥接测试'},
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }, fh, ensure_ascii=False, indent=2)

print('文件已写入: {}'.format(f))
print('诸葛马桥接器会自动读取并发布到 MQTT ✅')
"
```

### 测试 2：查看教练发来的消息

```bash
# 查看最新 5 条消息
ls -lt /home/admin/go-training/shared/to-xiaochen/ | head -5

# 查看最新一条内容
cat $(ls -t /home/admin/go-training/shared/to-xiaochen/*.json 2>/dev/null | head -1)
```

### 测试 3：启动文件轮询器

```bash
cd /home/admin/lobster-network
nohup python3 -c "
import os, json, time
from datetime import datetime

INBOX = '/home/admin/go-training/shared/to-xiaochen/'
PROCESSED = '/home/admin/go-training/shared/processed/xiaochen/'
os.makedirs(PROCESSED, exist_ok=True)

print('小陈文件轮询器启动（每10秒扫描）...')
while True:
    for f in sorted(os.listdir(INBOX)):
        if f.endswith('.json'):
            fp = os.path.join(INBOX, f)
            try:
                with open(fp) as fh:
                    data = json.load(fh)
                print('收到: type={} file={}'.format(data.get('type', '?'), f[:30]))
                os.rename(fp, os.path.join(PROCESSED, f))
            except Exception as e:
                print('处理失败: {}'.format(e))
    time.sleep(10)
" > /home/admin/go-training/shared/logs/xiaochen_file_poller.log 2>&1 &
echo "轮询器 PID: $!"
```

---

## 四、对局同步测试（诸葛虾）

```bash
cd /home/admin/lobster-network
python3 core/mqtt_go_match_sync.py test 2>&1
```

**预期输出**：
```
=== 围棋对局同步测试 ===
对局ID: match_xxxxxx
黑方 (小陈) 落子 D5...
白方 (诸葛虾) 落子 D4...

=== 对局状态 ===
棋盘大小: 9x9
棋子数: 2
提子: 黑=0 白=0
当前轮次: black
=== 测试完成 ===
```

---

## 五、常见问题

### Q1: 连接超时

```bash
# 检查端口
timeout 5 bash -c 'echo > /dev/tcp/47.93.6.57/1883' && echo 'OK' || echo 'FAIL'
```

FAIL → 检查阿里云安全组是否已添加 TCP 1883 规则。

### Q2: paho-mqtt 版本

```bash
python3 -c "import paho.mqtt.client as m; print(m.__version__ if hasattr(m,'__version__') else '1.x')"
```

诸葛虾推荐 2.x，小陈 1.6.1 已兼容。

### Q3: 订阅器无输出

```bash
tail -50 /home/admin/go-training/shared/logs/zhuguxia_mqtt.log
ps aux | grep mqtt_student
```

### Q4: 停止订阅器

```bash
pkill -f mqtt_student_subscriber
pkill -f file_poller
```

---

## 六、测试完成检查清单

- [ ] 端口可达测试通过
- [ ] 基础连接测试通过
- [ ] 收到诸葛马测试消息
- [ ] ACK 自动回复成功
- [ ] 订阅器在后台运行
- [ ] 日志文件正常写入

全部通过后，通知诸葛马 ✅
