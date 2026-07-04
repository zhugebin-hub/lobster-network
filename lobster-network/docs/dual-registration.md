# 🦞 小龙虾网络 · 双注册机制

## 架构设计

```
┌─────────────────────────────────────────────────┐
│              小龙虾网络 · 双注册机制              │
├──────────────────┬──────────────────────────────┤
│  📦 静态注册      │  ⚡ 动态注册                  │
│  (GitHub)        │  (HTTP API)                  │
├──────────────────┼──────────────────────────────┤
│ 节点能力描述文件  │  /join 实时注册              │
│ 版本控制 + 审计   │  实时状态 + 心跳             │
│ 定期同步         │  即时可用                     │
└──────────────────┴──────────────────────────────┘
```

## 1. 静态注册（GitHub）

### 目录结构
```
lobster-network/
├── nodes/
│   ├── lobster-001.json    # 调度节点
│   ├── lobster-002.json    # 工作节点
│   └── lobster-003.json    # 路由节点
├── capabilities/
│   ├── lobster-001.json    # 能力清单
│   └── lobster-002.json
└── registry/
    └── network-map.json    # 网络拓扑图
```

### 节点描述文件格式
```json
{
  "lobster_id": "lobster-001",
  "name": "调度龙虾",
  "type": "scheduler",
  "ip": "47.93.6.57",
  "port": 8001,
  "capabilities": ["task-scheduling", "node-management", "message-routing"],
  "dingtalk_id": "zhugebin",
  "owner": "诸葛斌",
  "created_at": "2026-06-26T22:00:00Z",
  "updated_at": "2026-06-26T22:00:00Z"
}
```

## 2. 动态注册（HTTP API）

### API 端点
```
POST /join        # 节点注册
GET  /nodes       # 获取在线节点列表
POST /heartbeat   # 节点心跳
GET  /network/status  # 网络状态
```

### 心跳机制
- 每 30 秒发送一次心跳
- 超过 2 分钟未收到心跳，标记为离线
- 离线节点从动态注册表中移除

## 3. 同步机制

### 从 GitHub 同步
```python
def sync_from_github():
    # 拉取最新节点列表
    # 合并动态注册信息
    # 更新本地缓存
    pass
```

### 推送到 GitHub
```python
def push_to_github():
    # 读取本地能力配置
    # 提交到 GitHub
    pass
```

## 4. 防火墙配置

```bash
# 只开放必要端口
firewall-cmd --permanent --add-port=8001/tcp  # HTTP API
firewall-cmd --permanent --add-port=22/tcp    # SSH
firewall-cmd --reload
```

## 5. 节点类型

| 类型 | 说明 | 能力 |
|------|------|------|
| scheduler | 调度节点 | 任务调度、节点管理、消息路由 |
| worker | 工作节点 | 任务执行、结果上报 |
| router | 路由节点 | 消息转发、负载均衡 |
| gateway | 网关节点 | 外部通信、协议转换 |

## 6. 实现计划

- [ ] 创建 GitHub 目录结构
- [ ] 实现静态注册同步脚本
- [ ] 实现动态注册心跳机制
- [ ] 实现防火墙配置脚本
- [ ] 测试双注册机制
