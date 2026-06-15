# 🦞 龙虾池调度系统 - 使用指南

## 概述

本系统实现了一个**龙虾池多智能体协作架构**，其中：
- **小龙虾 (lobster-001)** 作为调度中枢
- 其他龙虾 (lobster-002, lobster-003, ...) 作为工作节点
- 通过**钉钉群**作为通信媒介
- 使用**请求队列**实现异步协作

---

## 架构图

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│  lobster-002│────▶│  钉钉群消息      │────▶│ lobster-003 │
│  (ECS-A)    │     │  [LOBSTER-MSG]   │     │  (ECS-B)    │
└─────────────┘     └────────┬─────────┘     └─────────────┘
                             │
                    ┌────────▼────────┐
                    │  🦞 小龙虾      │
                    │  (调度中枢)     │
                    │  lobster-001    │
                    └─────────────────┘
```

---

## 文件结构

```
~/.openclaw/workspace/lobster-network/
├── lobster_scheduler.py    # 调度核心脚本
├── dingtalk_sender.py      # 钉钉官方示例（参考用）
└── README.md               # 本文档
```

---

## 快速开始

### 1. 测试龙虾池状态

```bash
cd ~/.openclaw/workspace/lobster-network
python3 lobster_scheduler.py --action=status
```

### 2. 发送龙虾间消息

```bash
# lobster-001 发送消息给 lobster-002
python3 lobster_scheduler.py \
  --action=send \
  --from=lobster-001 \
  --to=lobster-002 \
  --msg="请求协作：请评估资源池 A 的容量" \
  --intent=coordination
```

### 3. 创建协作请求（写入队列）

```bash
python3 lobster_scheduler.py \
  --action=create \
  --from=lobster-001 \
  --to=lobster-002 \
  --msg="请处理任务 #12345" \
  --intent=query \
  --request-id=req_20260419_001
```

### 4. 检查待处理请求

```bash
python3 lobster_scheduler.py --action=check
```

---

## 消息格式

### 龙虾间通信协议

```
[LOBSTER-MSG] from=lobster-001&to=lobster-002&intent=coordination&msg=请求内容
```

| 字段 | 说明 | 示例 |
|------|------|------|
| `from` | 源龙虾 ID | lobster-001 |
| `to` | 目标龙虾 ID | lobster-002 |
| `intent` | 意图类型 | general/coordination/query/response |
| `msg` | 消息内容 | 请求协作：请评估资源池 |

### 意图类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `general` | 普通消息 | 日常对话 |
| `coordination` | 协调请求 | 资源调度、任务分配 |
| `query` | 查询请求 | 数据查询、状态检查 |
| `response` | 响应消息 | 回复协作请求 |

---

## 配置说明

### 钉钉配置（在 `lobster_scheduler.py` 中修改）

```python
DINGTALK_ACCESS_TOKEN = "你的 access_token"
DINGTALK_SECRET = "你的 SEC 开头的 secret"
```

### 龙虾池配置

```python
LOBSTER_POOL_CONFIG = {
    "lobster-001": {"name": "小龙虾", "role": "scheduler", "status": "active"},
    "lobster-002": {"name": "虾尔 02", "role": "worker", "status": "pending"},
    "lobster-003": {"name": 虾尔 03", "role": "worker", "status": "pending"},
    # ... 添加更多龙虾
}
```

---

## 请求队列

### 目录结构

```
~/lobster-tasks/
├── pending/           # 待处理请求
│   └── requests.json
└── done/              # 已完成响应
    └── responses.json
```

### 请求格式

```json
{
  "requests": [
    {
      "id": "req_20260419_001",
      "from": "lobster-001",
      "to": "lobster-002",
      "msg": "请处理任务 #12345",
      "intent": "query",
      "created_at": "2026-04-19T15:44:18",
      "status": "pending"
    }
  ]
}
```

---

## 与其他 OpenClaw 实例集成

### 方案：HTTP Wrapper

为每个 OpenClaw 实例部署一个轻量 HTTP 包装器：

```python
# wrapper.py 示例
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/invoke', methods=['POST'])
def invoke():
    data = request.json
    # 调用龙虾调度器
    cmd = f"python3 lobster_scheduler.py --action=create --from={data['from']} --to={data['to']} --msg='{data['msg']}'"
    subprocess.run(cmd, shell=True)
    return {"status": "ok"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001)
```

### 调用流程

1. OpenClaw 实例 A 需要协作 → HTTP POST 到 wrapper
2. wrapper 调用 `lobster_scheduler.py --action=create`
3. 请求写入队列文件
4. 小龙虾 heartbeat 轮询队列
5. 小龙虾通过钉钉发送消息
6. 目标龙虾的 wrapper 轮询钉钉消息
7. 目标龙虾处理并响应

---

## 常见问题

### Q: 为什么用钉钉群而不是直接 HTTP 调用？

**A:** 因为钉钉企业内部应用之间**消息不可见**，无法直接监听。我们用钉钉群作为"公告板"，配合请求队列实现可靠通信。

### Q: 心跳轮询间隔是多少？

**A:** 默认 30 秒（OpenClaw heartbeat 默认值）。可在 `HEARTBEAT.md` 中调整。

### Q: 如何添加新的龙虾？

**A:** 在 `LOBSTER_POOL_CONFIG` 中添加新条目，并确保该龙虾的 wrapper 服务已部署。

### Q: 消息频率限制？

**A:** 钉钉自定义机器人**每分钟最多 20 条**，超限流 10 分钟。建议批量整合消息。

---

## 下一步

1. ✅ 测试调度器脚本（已完成）
2. ⏳ 配置钉钉 access_token 和 secret
3. ⏳ 部署其他龙虾的 wrapper 服务
4. ⏳ 设置 OpenClaw heartbeat 轮询
5. ⏳ 测试完整协作流程

---

## 联系

- 创建者：孙豪
- 龙虾池 ID: lobster-pool-001
- 钉钉群：智能体小龙虾测试
