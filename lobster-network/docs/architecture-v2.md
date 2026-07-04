# 🦞 小龙虾网络架构 v2.0 - 稳定性与可靠性优化方案

> 版本：v2.0.0  
> 作者：虾尔（lobster-001）  
> 日期：2026-06-27  
> 状态：设计草案 → 待实施

---

## 一、当前架构问题分析

### 1.1 问题清单

| 编号 | 问题 | 严重性 | 影响 |
|------|------|--------|------|
| P1 | 单点故障 | 🔴 高 | 调度节点（8001）宕机 = 全网瘫痪 |
| P2 | 无心跳机制 | 🔴 高 | 无法检测节点在线状态，离线节点无法自动恢复 |
| P3 | 无能力注册 | 🟡 中 | 不知道每个节点能做什么，无法智能调度 |
| P4 | 消息可能丢失 | 🔴 高 | 单文件 JSON，无备份，进程崩溃时消息丢失 |
| P5 | 无安全认证 | 🟡 中 | 任何人都可以调用 /join、/invoke |
| P6 | 无监控告警 | 🟡 中 | 故障发生后才知道，无法提前预警 |
| P7 | 无版本管理 | 🟢 低 | 节点版本不统一，可能导致协议不兼容 |
| P8 | 日志分散 | 🟢 低 | 每个节点独立日志，无法集中分析 |

### 1.2 根因分析

```
┌─────────────────────────────────────────────────────┐
│  核心问题：系统设计偏向"原型验证"，缺少"生产级"考虑  │
├─────────────────────────────────────────────────────┤
│  具体表现：                                           │
│  ① 单实例运行，无冗余                                │
│  ② 文件存储，无事务保证                              │
│  ③ 无健康检查，故障发现靠人工                        │
│  ④ 无认证授权，安全性不足                            │
│  ⑤ 无监控体系，运维靠猜                              │
└─────────────────────────────────────────────────────┘
```

---

## 二、v2.0 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        🦞 小龙虾网络 v2.0                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  调度节点     │  │  工作节点     │  │  路由节点     │            │
│  │  (scheduler) │  │  (worker)   │  │  (router)   │            │
│  │  主 + 备      │  │  按需扩展    │  │  可选部署    │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                 │                 │                     │
│  ┌──────┴─────────────────┴─────────────────┴───────┐            │
│  │              消息总线（Redis / 文件队列）            │            │
│  └────────────────────────┬──────────────────────────┘            │
│                           │                                       │
│  ┌────────────────────────┴──────────────────────────┐            │
│  │              注册中心（双轨制）                      │            │
│  │  ┌──────────────┐  ┌──────────────┐               │            │
│  │  │  GitHub 静态  │  │  HTTP 动态   │               │            │
│  │  │  注册 + 同步  │  │  注册 + 心跳 │               │            │
│  │  └──────────────┘  └──────────────┘               │            │
│  └───────────────────────────────────────────────────┘            │
│                           │                                       │
│  ┌────────────────────────┴──────────────────────────┐            │
│  │              监控告警层                             │            │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐          │            │
│  │  │ 健康检查  │ │ 日志聚合  │ │ 告警通知  │          │            │
│  │  └──────────┘ └──────────┘ └──────────┘          │            │
│  └───────────────────────────────────────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 节点角色定义

| 角色 | 职责 | 必需 | 数量 |
|------|------|------|------|
| scheduler | 任务调度、节点管理、消息路由 | ✅ | 1 主 + 1 备 |
| worker | 任务执行、结果上报 | ✅ | N（按需扩展） |
| router | 跨网段消息转发 | ❌ | 0-N |
| gateway | 外部通信（钉钉/微信） | ❌ | 0-N |

### 2.3 节点能力模型

```json
{
  "lobster_id": "lobster-001",
  "name": "调度龙虾",
  "type": "scheduler",
  "version": "2.0.0",
  "ip": "47.93.6.57",
  "port": 8001,
  "capabilities": {
    "task_scheduling": true,
    "node_management": true,
    "message_routing": true,
    "code_execution": false,
    "file_processing": true,
    "web_scraping": true,
    "pdf_generation": true,
    "ppt_generation": false
  },
  "resources": {
    "cpu_cores": 4,
    "memory_gb": 8,
    "disk_gb": 100
  },
  "dingtalk_id": "zhugebin",
  "owner": "诸葛斌",
  "created_at": "2026-06-27T00:00:00Z",
  "updated_at": "2026-06-27T00:00:00Z"
}
```

---

## 三、核心改进方案

### 3.1 心跳机制（解决 P2）

#### 3.1.1 心跳协议

```python
# 节点启动后定期发送心跳
# 默认间隔：30 秒
# 超时阈值：2 分钟（4 次心跳未收到 = 离线）

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """节点心跳上报"""
    data = request.json
    lobster_id = data.get('lobster_id')
    timestamp = data.get('timestamp', time.time())
    status = data.get('status', 'ok')  # ok | busy | error
    
    # 更新节点状态
    nodes_data = load_lobster_nodes()
    for node in nodes_data.get('nodes', []):
        if node['lobster_id'] == lobster_id:
            node['last_heartbeat'] = timestamp
            node['status'] = 'online' if status == 'ok' else 'busy'
            node['heartbeat_count'] = node.get('heartbeat_count', 0) + 1
            break
    save_lobster_nodes(nodes_data)
    
    return jsonify({"status": "ok", "next_heartbeat_in": 30})
```

#### 3.1.2 离线检测

```python
# 调度节点定期检查离线节点
def check_offline_nodes():
    """检查离线节点并标记"""
    nodes_data = load_lobster_nodes()
    now = time.time()
    offline_threshold = 120  # 2 分钟
    
    for node in nodes_data.get('nodes', []):
        last_hb = node.get('last_heartbeat', 0)
        if now - last_hb > offline_threshold:
            if node.get('status') != 'offline':
                node['status'] = 'offline'
                node['offline_at'] = datetime.now().isoformat()
                logger.warning(f"⚠️ 节点 {node['lobster_id']} 离线")
                # 发送告警通知
                send_alert(f"节点 {node['lobster_id']} 离线")
    
    save_lobster_nodes(nodes_data)
```

### 3.2 消息持久化（解决 P4）

#### 3.2.1 双写机制

```python
# 消息写入时同时写入主文件和备份文件
def save_message(msg: dict):
    """双写消息到主文件和备份文件"""
    # 主文件
    save_json_file(MESSAGES_FILE, msg)
    
    # 备份文件（带时间戳）
    backup_file = f"{MESSAGES_FILE}.{datetime.now().strftime('%Y%m%d')}.bak"
    save_json_file(backup_file, msg)
    
    # 定期归档（每天）
    if datetime.now().hour == 0 and datetime.now().minute < 5:
        archive_old_messages()
```

#### 3.2.2 消息队列

```python
# 使用文件作为简单消息队列
# 每条消息一个文件，避免并发写入冲突

QUEUE_DIR = os.path.expanduser("~/lobster-tasks/queue/")

def enqueue_message(msg: dict):
    """将消息加入队列"""
    os.makedirs(QUEUE_DIR, exist_ok=True)
    msg_id = f"{msg.get('lobster_id')}_{int(time.time()*1000)}_{random.randint(1000,9999)}"
    msg_file = os.path.join(QUEUE_DIR, f"{msg_id}.json")
    msg['id'] = msg_id
    msg['status'] = 'queued'
    msg['created_at'] = datetime.now().isoformat()
    with open(msg_file, 'w', encoding='utf-8') as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
    return msg_id

def dequeue_message():
    """从队列取出一条消息（FIFO）"""
    files = sorted(os.listdir(QUEUE_DIR))
    for f in files:
        if f.endswith('.json'):
            msg_file = os.path.join(QUEUE_DIR, f)
            try:
                with open(msg_file, 'r', encoding='utf-8') as fp:
                    msg = json.load(fp)
                # 标记为处理中
                msg['status'] = 'processing'
                with open(msg_file, 'w', encoding='utf-8') as fp:
                    json.dump(msg, fp, ensure_ascii=False, indent=2)
                return msg
            except:
                continue
    return None

def complete_message(msg_id: str, result: dict):
    """标记消息处理完成"""
    msg_file = os.path.join(QUEUE_DIR, f"{msg_id}.json")
    if os.path.exists(msg_file):
        with open(msg_file, 'r', encoding='utf-8') as f:
            msg = json.load(f)
        msg['status'] = 'completed'
        msg['result'] = result
        msg['completed_at'] = datetime.now().isoformat()
        with open(msg_file, 'w', encoding='utf-8') as f:
            json.dump(msg, f, ensure_ascii=False, indent=2)
```

### 3.3 安全认证（解决 P5）

#### 3.3.1 API Key 认证

```python
# 每个节点启动时生成唯一 API Key
# 存储在配置文件中，调用 API 时携带

@app.route('/join', methods=['POST'])
def lobster_join():
    # 验证 API Key
    api_key = request.headers.get('X-API-Key')
    if not validate_api_key(api_key):
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    # ... 原有逻辑

def validate_api_key(api_key: str) -> bool:
    """验证 API Key"""
    if not api_key:
        return False
    # 从配置文件加载合法 API Key 列表
    config = load_config()
    return api_key in config.get('allowed_api_keys', [])
```

#### 3.3.2 节点注册流程

```
1. 新节点启动 → 生成 API Key
2. 调用 /join → 携带 API Key
3. 调度节点验证 → 分配 lobster_id
4. 返回配置 → 包含节点信息
5. 新节点保存配置 → 定期发送心跳
```

### 3.4 监控告警（解决 P6）

#### 3.4.1 健康检查端点

```python
@app.route('/health', methods=['GET'])
def health_check():
    """增强版健康检查"""
    lobster_id = app.config['LOBSTER_ID']
    
    # 检查关键依赖
    checks = {
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage(),
        "queue_depth": get_queue_depth(),
        "last_heartbeat": get_last_heartbeat_time()
    }
    
    status = "ok" if all(c.get("ok") for c in checks.values()) else "degraded"
    
    return jsonify({
        "lobster_id": lobster_id,
        "status": status,
        "checks": checks,
        "uptime": get_uptime(),
        "version": "2.0.0"
    })
```

#### 3.4.2 告警通知

```python
def send_alert(level: str, message: str):
    """发送告警通知"""
    # P0: 紧急 → 钉钉 + 微信
    # P1: 重要 → 钉钉
    # P2: 一般 → 日志记录
    
    alert = {
        "level": level,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "source": app.config['LOBSTER_ID']
    }
    
    # 写入告警日志
    save_alert_log(alert)
    
    # P0/P1 发送到钉钉
    if level in ['P0', 'P1']:
        send_to_dingtalk(f"🚨 [{level}] {message}")
```

---

## 四、实施计划

### Phase 1: 基础改进（1-2 天）
- [ ] 实现心跳机制
- [ ] 实现离线检测
- [ ] 实现消息队列
- [ ] 实现双写备份

### Phase 2: 安全加固（1 天）
- [ ] 实现 API Key 认证
- [ ] 实现节点注册流程
- [ ] 实现权限控制

### Phase 3: 监控体系（1-2 天）
- [ ] 实现增强健康检查
- [ ] 实现告警通知
- [ ] 实现日志聚合

### Phase 4: 高可用（2-3 天）
- [ ] 实现主备切换
- [ ] 实现负载均衡
- [ ] 实现自动恢复

---

## 五、目录结构（v2.0）

```
lobster-network/
├── spec/
│   ├── protocol.md           # 核心协议
│   ├── rate-limit-mechanism.md  # 限速机制
│   ├── architecture-v2.md    # 本文件
│   └── ...
├── nodes/
│   ├── lobster-001.json      # 节点描述
│   └── ...
├── capabilities/
│   ├── lobster-001.json      # 能力清单
│   └── ...
├── registry/
│   └── network-map.json      # 网络拓扑
├── queue/                    # 消息队列
├── alerts/                   # 告警日志
├── backups/                  # 数据备份
└── scripts/
    ├── health-check.py       # 健康检查
    ├── monitor.py            # 监控脚本
    └── backup.py             # 备份脚本
```

---

## 六、技术选型

| 组件 | 当前 | v2.0 推荐 | 理由 |
|------|------|-----------|------|
| 消息队列 | 单文件 JSON | 文件队列（每消息一个文件） | 简单可靠，避免并发冲突 |
| 配置管理 | 硬编码 | YAML + JSON 分离 | 灵活可配置 |
| 日志管理 | 分散日志 | 集中日志 + 分级 | 便于分析 |
| 监控 | 无 | 文件 + 钉钉通知 | 轻量级，无需额外组件 |
| 认证 | 无 | API Key | 简单有效 |

---

## 七、总结

v2.0 架构在保持轻量级的同时，解决了生产环境的关键问题：

1. **可靠性**：心跳 + 离线检测 + 消息队列 + 双写备份
2. **安全性**：API Key 认证 + 权限控制
3. **可观测性**：健康检查 + 告警通知 + 集中日志
4. **可扩展性**：节点角色定义 + 能力模型 + 双轨注册

所有改进都基于现有代码演进，不需要重写，确保平滑升级。
