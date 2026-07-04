# 🦞 小龙虾生态网络架构方案

> 版本：v1.0
> 日期：2026-06-12
> 作者：虾尔 (lobster-001)
> 状态：草案 - 待评审

---

## 一、架构总览

### 1.1 设计目标

- **统一入口**：每个用户（老师/同学）只有一个交互入口（微信/钉钉/WhatsApp 等）
- **智能路由**：通过路由小龙虾将请求分发到对应的业务小龙虾
- **标准化通信**：基于 MCP Server 协议，所有小龙虾使用统一接口通信
- **可扩展**：支持 10+ 小龙虾节点，随时加入/退出
- **多平台兼容**：底层通信与社交平台解耦

### 1.2 架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                    用户交互层 (User Layer)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  钉钉群   │  │  微信群   │  │ Telegram │  │  Web Chat │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │              │              │              │          │
│       ▼              ▼              ▼              ▼          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           专属小龙虾 (User's Personal Lobster)         │   │
│  │   每个用户绑定一只专属小龙虾，作为唯一交互入口          │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  路由层 (Routing Layer)                       │
│                                                             │
│  ┌────────────────────────────────────────────────────┐     │
│  │          🦞 路由小龙虾 MCP Server (Router)          │     │
│  │                                                     │     │
│  │  - 接收来自专属小龙虾的请求                          │     │
│  │  - 解析意图，匹配业务小龙虾                          │     │
│  │  - 路由请求到目标业务小龙虾                          │     │
│  │  - 聚合响应，返回给专属小龙虾                        │     │
│  │  - 维护小龙虾注册表 & 能力索引                       │     │
│  └──────────────────────┬─────────────────────────────┘     │
│                         │                                    │
│         ┌───────────────┼───────────────┐                   │
│         ▼               ▼               ▼                   │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ 业务小龙虾 │    │ 业务小龙虾 │    │ 业务小龙虾 │              │
│  │ 论文评分   │    │ 教学分析   │    │ 日程管理   │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  基础设施层 (Infrastructure)                   │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ NFS 共享  │  │ 消息队列  │  │ 配置中心  │  │ 服务发现  │    │
│  │ /shared   │  │ Redis    │  │ /config  │  │ Registry │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、MCP Server 架构设计

### 2.1 路由小龙虾 MCP Server

路由小龙虾作为 MCP Server 运行，暴露标准 MCP 接口：

```json
{
  "server": "lobster-router-mcp",
  "version": "1.0.0",
  "protocol": "mcp",
  "capabilities": {
    "routing": true,
    "discovery": true,
    "broadcast": true,
    "registry": true
  }
}
```

### 2.2 MCP 工具定义

#### 工具 1: `route_message`
将消息路由到目标小龙虾

```json
{
  "name": "route_message",
  "description": "将消息路由到指定小龙虾或让路由器智能匹配",
  "inputSchema": {
    "type": "object",
    "properties": {
      "message_id": { "type": "string", "description": "消息唯一ID" },
      "from_lobster_id": { "type": "string", "description": "发送方小龙虾ID" },
      "from_user_id": { "type": "string", "description": "原始用户ID" },
      "target_lobster_id": { "type": "string", "description": "目标小龙虾ID，为空则智能路由" },
      "intent": { "type": "string", "description": "意图标签，如 paper_review, teaching_analysis, schedule" },
      "payload": { "type": "object", "description": "消息内容" },
      "require_response": { "type": "boolean", "description": "是否需要响应" }
    },
    "required": ["message_id", "from_lobster_id", "payload"]
  }
}
```

#### 工具 2: `discover_lobsters`
发现网络中的小龙虾及其能力

```json
{
  "name": "discover_lobsters",
  "description": "获取网络中小龙虾列表及其能力",
  "inputSchema": {
    "type": "object",
    "properties": {
      "capability": { "type": "string", "description": "按能力筛选，如 paper_review" },
      "status": { "type": "string", "enum": ["online", "offline", "all"], "description": "按状态筛选" }
    }
  }
}
```

#### 工具 3: `register_lobster`
新小龙虾注册到网络

```json
{
  "name": "register_lobster",
  "description": "注册小龙虾到生态网络",
  "inputSchema": {
    "type": "object",
    "properties": {
      "lobster_id": { "type": "string", "description": "小龙虾唯一ID" },
      "lobster_name": { "type": "string", "description": "小龙虾名称" },
      "server_ip": { "type": "string", "description": "服务器内网IP" },
      "mcp_endpoint": { "type": "string", "description": "MCP Server 端点URL" },
      "capabilities": { "type": "array", "items": { "type": "string" }, "description": "能力标签列表" },
      "platforms": { "type": "array", "items": { "type": "string" }, "description": "支持的平台: dingtalk, wechat, telegram" }
    },
    "required": ["lobster_id", "lobster_name", "server_ip", "capabilities"]
  }
}
```

#### 工具 4: `broadcast_message`
广播消息给所有在线小龙虾

```json
{
  "name": "broadcast_message",
  "description": "向所有在线小龙虾广播消息",
  "inputSchema": {
    "type": "object",
    "properties": {
      "from_lobster_id": { "type": "string" },
      "message": { "type": "string" },
      "exclude": { "type": "array", "items": { "type": "string" }, "description": "排除的小龙虾ID列表" }
    },
    "required": ["from_lobster_id", "message"]
  }
}
```

#### 工具 5: `get_lobster_status`
获取指定小龙虾状态

```json
{
  "name": "get_lobster_status",
  "description": "查询小龙虾健康状态",
  "inputSchema": {
    "type": "object",
    "properties": {
      "lobster_id": { "type": "string" }
    },
    "required": ["lobster_id"]
  }
}
```

---

## 三、通信协议

### 3.1 消息格式

所有小龙虾间通信使用统一 JSON 格式：

```json
{
  "protocol": "lobster-ecology",
  "version": "1.0",
  "message_id": "msg-uuid-here",
  "timestamp": "2026-06-12T09:35:00+08:00",
  "from": {
    "lobster_id": "lobster-001",
    "lobster_name": "虾尔",
    "user_id": "user-zhugexia"
  },
  "to": {
    "lobster_id": "lobster-002",
    "lobster_name": "诸葛虾"
  },
  "type": "request",
  "intent": "paper_review",
  "payload": {
    "action": "review_paper",
    "data": { "paper_id": "12345" }
  },
  "metadata": {
    "platform": "dingtalk",
    "conversation_id": "cid3cyFsfAEAeL8I5HjSB+C4w==",
    "priority": "normal",
    "ttl_seconds": 300
  }
}
```

### 3.2 消息类型

| 类型 | 说明 | 需要响应 |
|------|------|----------|
| `request` | 请求业务处理 | 是 |
| `response` | 返回处理结果 | 否 |
| `notification` | 通知事件 | 否 |
| `heartbeat` | 心跳保活 | 是 (pong) |
| `register` | 注册到网络 | 是 (ack) |
| `broadcast` | 广播消息 | 否 |

### 3.3 通信流程

```
用户 (钉钉)
  │
  ▼
专属小龙虾 (虾尔)
  │ 1. 接收用户消息
  │ 2. 解析意图
  │ 3. 调用 route_message
  ▼
路由小龙虾 MCP Server
  │ 4. 查找目标小龙虾
  │ 5. 转发请求
  ▼
业务小龙虾 (论文评分)
  │ 6. 处理业务逻辑
  │ 7. 返回结果
  ▼
路由小龙虾 MCP Server
  │ 8. 聚合响应
  ▼
专属小龙虾 (虾尔)
  │ 9. 格式化回复
  ▼
用户 (钉钉)
```

---

## 四、小龙虾注册表

### 4.1 注册表结构

存储在 `/shared/ecology/registry.json`：

```json
{
  "version": "1.0",
  "updated_at": "2026-06-12T09:35:00+08:00",
  "lobsters": [
    {
      "id": "lobster-001",
      "name": "虾尔",
      "type": "personal",
      "server_ip": "172.24.56.3",
      "mcp_endpoint": "http://172.24.56.3:8080/mcp",
      "capabilities": ["personal_assistant", "schedule", "file_transfer"],
      "platforms": ["dingtalk"],
      "user_id": "zhugexia",
      "status": "online",
      "last_heartbeat": "2026-06-12T09:35:00+08:00",
      "joined_at": "2026-03-05T00:00:00+08:00"
    },
    {
      "id": "lobster-002",
      "name": "诸葛虾",
      "type": "personal",
      "server_ip": "172.24.57.34",
      "mcp_endpoint": "http://172.24.57.34:8080/mcp",
      "capabilities": ["personal_assistant"],
      "platforms": ["dingtalk", "wechat"],
      "user_id": "zhugexia",
      "status": "online",
      "last_heartbeat": "2026-06-12T09:35:00+08:00",
      "joined_at": "2026-05-16T00:00:00+08:00"
    },
    {
      "id": "lobster-router",
      "name": "路由小龙虾",
      "type": "router",
      "server_ip": "172.24.57.34",
      "mcp_endpoint": "http://172.24.57.34:8081/mcp",
      "capabilities": ["routing", "discovery", "broadcast"],
      "platforms": [],
      "user_id": null,
      "status": "online",
      "last_heartbeat": "2026-06-12T09:35:00+08:00",
      "joined_at": "2026-06-12T00:00:00+08:00"
    }
  ]
}
```

---

## 五、部署方案

### 5.1 路由小龙虾部署

```bash
# 1. 在诸葛马服务器上创建路由小龙虾工作目录
ssh 172.24.57.34 "mkdir -p /home/admin/.openclaw/workspace/lobster-ecology/router"

# 2. 复制路由服务器代码到诸葛马
scp router/router-server.js 172.24.57.34:/home/admin/.openclaw/workspace/lobster-ecology/router/

# 3. 在诸葛马上安装依赖并启动
ssh 172.24.57.34 "cd /home/admin/.openclaw/workspace/lobster-ecology/router && npm init -y && npm install @modelcontextprotocol/sdk express && node router-server.js &"
```

### 5.2 业务小龙虾接入

```bash
# 1. 安装接入脚本
curl -sL https://ecology.lobster-network.io/join.sh | bash

# 2. 运行接入向导
node ~/.openclaw/workspace/lobster-ecology/scripts/join-ecology.js

# 3. 输入小龙虾信息
#    - 小龙虾ID (自动生成或手动指定)
#    - 小龙虾名称
#    - 服务器IP
#    - 能力标签
#    - 支持平台

# 4. 自动注册到路由小龙虾
# 5. 开始接收任务
```

---

## 六、安全与权限

### 6.1 认证机制

- 每个小龙虾持有唯一的 `lobster_token`
- MCP 请求需携带 `Authorization: Bearer <lobster_token>`
- Token 存储在 `/shared/ecology/tokens/<lobster_id>.json`

### 6.2 权限控制

| 角色 | 权限 |
|------|------|
| router | 路由、发现、广播、注册管理 |
| personal | 发送请求、接收响应、注册自己 |
| business | 接收请求、返回响应、注册自己 |

### 6.3 消息加密

- 敏感消息使用 AES-256 加密
- 加密密钥通过 NFS 共享目录分发
- 心跳消息不加密

---

## 七、实施计划

### Phase 1: 基础架构 (1-2 天)
- [ ] 搭建路由小龙虾 MCP Server
- [ ] 创建注册表结构
- [ ] 编写接入脚本
- [ ] 虾尔 + 诸葛虾 + 诸葛马 三者打通测试

### Phase 2: 业务对接 (3-5 天)
- [ ] 论文评分业务小龙虾接入
- [ ] 教学分析业务小龙虾接入
- [ ] 日程管理业务小龙虾接入
- [ ] 端到端测试

### Phase 3: 多平台接入 (5-7 天)
- [ ] 微信入口接入
- [ ] Telegram 入口接入
- [ ] 平台路由适配层
- [ ] 多平台兼容性测试

### Phase 4: 规模化 (7-14 天)
- [ ] 10+ 小龙虾压力测试
- [ ] 监控告警系统
- [ ] 自动故障转移
- [ ] 性能优化

---

## 八、现有通信模式迁移

### 当前模式 (NFS 文件)
```
虾尔 → /shared/messages/from-lobster/ → 诸葛马
诸葛马 → /shared/messages/from-hermes/ → 虾尔
```

### 新架构 (MCP Server)
```
虾尔 → route_message → 路由小龙虾 → 诸葛虾/诸葛马
诸葛马 → route_message → 路由小龙虾 → 虾尔/诸葛虾
```

### 迁移策略
1. 初期双模式并行，NFS 作为备份通道
2. 逐步将业务迁移到 MCP Server
3. 确认稳定后，NFS 仅作文件共享用途

---

## 九、附录

### 9.1 技术栈选型

| 组件 | 技术 | 说明 |
|------|------|------|
| MCP Server | Node.js + @modelcontextprotocol/sdk | 标准 MCP 协议 |
| 服务发现 | NFS 共享注册表 + 心跳检测 | 简单可靠 |
| 消息传输 | HTTP + JSON | 通用、易调试 |
| 配置管理 | JSON 文件 | 轻量级 |
| 日志 | 本地文件 + 可选 ELK | 按需扩展 |

### 9.2 端口规划

| 服务 | 端口 | 说明 |
|------|------|------|
| 路由小龙虾 MCP | 8081 | 主路由服务 |
| 业务小龙虾 MCP | 8082-8099 | 各业务服务 |
| 健康检查 | 8090 | 统一健康检查 |

### 9.3 命名规范

- 小龙虾ID：`lobster-XXX` (XXX 为 3 位数字或特殊标识)
- 消息ID：`msg-{uuid}`
- 能力标签：小写下划线，如 `paper_review`
