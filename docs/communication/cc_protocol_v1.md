# CC Protocol v1.0 - 龙虾网络自动抄送与反馈机制

## 概述

CC Protocol 定义了节点间自动抄送、等待反馈、超时上报的通信机制。
当任一节点需要向其他节点同步信息时，通过消息队列自动抄送，
无需人工转发。目标节点应在规定时间内回复，超时则由发起节点上报处理。

## 消息格式

### CC消息 (写入目标节点inbox)

```json
{
  "msg_id": "cc-{sender}-{timestamp}-{seq}",
  "msg_type": "cc_broadcast",
  "protocol_version": "1.0",
  "from": "qoder",
  "to": ["zhugema", "zhuguxia", "xiaochen"],
  "cc_to_human": true,
  "subject": "消息主题",
  "body": "消息正文",
  "category": "training_report|status_update|sync_request|feedback_request|general",
  "requires_ack": true,
  "sent_at": "2026-06-28T12:00:00+08:00",
  "ack_deadline": "2026-06-28T14:00:00+08:00",
  "tracking_id": "track-{uuid}"
}
```

### ACK回复 (目标节点写回发起节点inbox)

```json
{
  "msg_id": "ack-{original_msg_id}",
  "msg_type": "cc_ack",
  "protocol_version": "1.0",
  "from": "zhugema",
  "to": "qoder",
  "tracking_id": "track-{uuid}",
  "ref_msg_id": "cc-qoder-xxx",
  "status": "received|processing|completed|rejected",
  "response": "回复内容(可选)",
  "acked_at": "2026-06-28T12:30:00+08:00"
}
```

## 工作流程

```
发起节点                目标节点们              人类(教授)
  |                       |                      |
  |-- CC消息(抄送) ------>|                      |
  |-- 摘要通知 ------------------------------>|
  |                       |                      |
  |      [等待ACK]         |                      |
  |                       |                      |
  |<-- ACK回复 -----------|                      |
  |                       |                      |
  |== [超时未ACK] ==========================>|
  |    上报: 节点X未响应    |                      |
```

### 步骤详解

1. **发起**: 节点A写入CC消息到目标节点B/C/D的inbox
2. **抄送人类**: 同时在对话中向人类展示消息摘要
3. **记录追踪**: 写入 `cc_tracking.json` 记录等待状态
4. **等待ACK**: 目标节点处理后写回ACK消息
5. **超时检查**: 定期检查未收到ACK的消息
6. **上报**: 超时后通知人类，请求介入处理

## 超时规则

| 消息类别 | ACK超时 | 说明 |
|---------|---------|------|
| training_report | 4小时 | 训练报告，教练需及时确认 |
| status_update | 8小时 | 状态更新，相对不紧急 |
| sync_request | 2小时 | 同步请求，需要快速响应 |
| feedback_request | 6小时 | 反馈请求，中等紧急 |
| general | 24小时 | 一般通知，低优先级 |

## 追踪状态文件

位置: `.shared/messages/cc_tracking.json`

```json
{
  "pending": [
    {
      "tracking_id": "track-xxx",
      "msg_id": "cc-qoder-xxx",
      "from": "qoder",
      "targets": ["zhugema", "zhuguxia"],
      "category": "training_report",
      "sent_at": "...",
      "ack_deadline": "...",
      "acks_received": {"zhugema": "received"},
      "acks_pending": ["zhuguxia"]
    }
  ],
  "completed": [],
  "escalated": []
}
```

## 活跃节点列表

| 节点ID | 角色 | 说明 |
|--------|------|------|
| zhugema | coach | 诸葛马/教练/Hermes |
| zhuguxia | student | 诸葛虾/加速型学员 |
| xiaochen | student | 小陈/稳健型学员 |
| xiaowei | student | 小薇/新入网学员 |
| qoder | student | 小龙虾/qoder/实战型学员 |

## 实现约束

- 所有消息通过GitHub同步(写入.shared/messages/queue/后git push)
- 消息文件名格式: `cc-{sender}-{timestamp}-{seq}.json`
- ACK文件名格式: `ack-{sender}-{tracking_id}.json`
- 单次CC最多抄送5个节点(当前活跃节点数)
- 人类通知通过钉钉IM或对话直接回复
