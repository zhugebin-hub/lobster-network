# 🦞 AI 智能体跨服务器文件共享通信方案

> **设计时间**：2026-05-15  
> **设计者**：小龙虾 - 诸葛虾  
> **目标**：让不同服务器上的 AI 智能体（小龙虾 ↔ Hermes，小龙虾 ↔ 小龙虾）通过共享文件系统实现底层通信

---

## 📋 目录

1. [需求分析](#需求分析)
2. [方案对比](#方案对比)
3. [推荐方案](#推荐方案)
4. [共享目录结构设计](#共享目录结构设计)
5. [通信协议设计](#通信协议设计)
6. [部署步骤](#部署步骤)
7. [安全设计](#安全设计)
8. [运维监控](#运维监控)

---

## 需求分析

### 场景 1：小龙虾 ↔ Hermes 通信
```
服务器 A（阿里云）          服务器 B（阿里云）
┌─────────────┐           ┌─────────────┐
│  OpenClaw   │  ←共享→   │  Hermes     │
│  小龙虾     │  文件系统  │  智能体     │
│  Qwen 模型  │           │  任意模型   │
└─────────────┘           └─────────────┘
```

### 场景 2：小龙虾 ↔ 小龙虾 通信
```
服务器 A                   服务器 C
┌─────────────┐           ┌─────────────┐
│  OpenClaw   │  ←共享→   │  OpenClaw   │
│  小龙虾 #1  │  文件系统  │  小龙虾 #2  │
└─────────────┘           └─────────────┘
```

### 通信内容
| 类型 | 说明 | 频率 |
|------|------|------|
| **消息传递** | 智能体之间的对话/指令 | 实时 |
| **记忆共享** | MEMORY.md、USER.md 等 | 按需 |
| **任务委派** | 一个智能体把任务交给另一个 | 按需 |
| **文件交换** | 文档、图片、代码等 | 按需 |
| **状态同步** | 在线状态、负载情况 | 定时 |

---

## 方案对比

### 方案一：阿里云 NAS（推荐 ⭐⭐⭐⭐⭐）

```
┌─────────────────────────────────────────────┐
│           阿里云 NAS (NFS/SMB)              │
│         同一 VPC 内网共享存储               │
└──────────┬──────────────────────┬───────────┘
           │ NFS mount            │ NFS mount
     ┌─────▼─────┐         ┌─────▼─────┐
     │ 服务器 A   │         │ 服务器 B   │
     │ OpenClaw   │         │ Hermes    │
     └───────────┘         └───────────┘
```

**优点：**
- ✅ 阿里云托管，零运维
- ✅ 同一 VPC 内网访问，延迟 < 1ms
- ✅ 原生 NFS 协议，Linux 直接 mount
- ✅ 支持多服务器同时读写
- ✅ 自动备份、快照
- ✅ 按量付费，成本低（约 ¥0.002/GB/小时）

**缺点：**
- ❌ 需要同一 VPC（或跨 VPC 需配置）
- ❌ 费用略高于自建（但运维成本低）

**成本估算：**
- 存储：100GB × ¥0.002/GB/小时 × 720 小时 = ¥144/月
- 实际使用可能只有几 GB，实际费用更低

---

### 方案二：自建 NFS 服务器

```
┌─────────────────┐
│   服务器 A       │ ← NFS Server
│   OpenClaw      │
│   (也做 NFS 服务端)
└────────┬────────┘
         │ NFS mount
   ┌─────▼─────┐
   │ 服务器 B   │ ← NFS Client
   │ Hermes    │
   └───────────┘
```

**优点：**
- ✅ 零额外费用
- ✅ 完全自控
- ✅ 配置简单（Linux 原生支持）

**缺点：**
- ❌ 服务器 A 宕机则共享不可用
- ❌ 需要自己维护 NFS 服务
- ❌ 单向挂载（B 读 A），双向同步需要额外配置
- ❌ 跨服务器写入可能有延迟/冲突

---

### 方案三：Syncthing（双向同步）

```
┌─────────────┐         ┌─────────────┐
│  服务器 A    │ ←P2P→   │  服务器 B    │
│  Syncthing  │  加密同步 │  Syncthing  │
│  OpenClaw   │         │  Hermes     │
└─────────────┘         └─────────────┘
```

**优点：**
- ✅ 真正的双向同步
- ✅ P2P 加密传输
- ✅ 去中心化，无单点故障
- ✅ 版本历史（可回滚）
- ✅ 免费开源

**缺点：**
- ❌ 需要双方同时在线才能同步
- ❌ 冲突解决需要配置策略
- ❌ 不是真正的"共享文件系统"，是"同步文件系统"
- ❌ 有同步延迟（通常几秒到几十秒）

---

### 方案四：Rsync + Cron（定时同步）

```
┌─────────────┐         ┌─────────────┐
│  服务器 A    │ ←rsync→ │  服务器 B    │
│  OpenClaw   │  cron   │  Hermes     │
└─────────────┘         └─────────────┘
```

**优点：**
- ✅ 最简单
- ✅ Linux 原生支持
- ✅ 带宽占用低（只传差异）

**缺点：**
- ❌ 不是实时的（取决于 cron 间隔）
- ❌ 冲突处理困难
- ❌ 需要 SSH 密钥配置

---

### 方案五：阿里云 OSS + 挂载（对象存储）

```
┌─────────────────────────────────────────────┐
│           阿里云 OSS (S3 兼容)              │
└──────────┬──────────────────────┬───────────┘
           │ s3fs/rclone          │ s3fs/rclone
     ┌─────▼─────┐         ┌─────▼─────┐
     │ 服务器 A   │         │ 服务器 B   │
     │ OpenClaw   │         │ Hermes    │
     └───────────┘         └───────────┘
```

**优点：**
- ✅ 几乎无限存储
- ✅ 高持久性（99.999999999%）
- ✅ 跨地域访问

**缺点：**
- ❌ 不是真正的文件系统（延迟高）
- ❌ s3fs 挂载性能一般
- ❌ API 调用有费用
- ❌ 不适合频繁小文件读写

---

## 推荐方案

### 🏆 主方案：阿里云 NAS

**理由：**
1. 两台都是阿里云服务器，同一 VPC 内网访问延迟极低
2. 原生 NFS 支持，智能体进程直接读写文件，无需修改代码
3. 多服务器同时挂载，真正的共享文件系统
4. 阿里云托管，零运维
5. 成本低（实际使用量很小）

### 🥈 备选方案：Syncthing

**适用场景：**
- 服务器不在同一 VPC
- 需要跨云厂商部署
- 需要版本历史和回滚能力

---

## 共享目录结构设计

### 挂载点
```bash
# 两台服务器都将 NAS 挂载到相同路径
/mnt/ai-agents-share/
```

### 目录结构

```
/mnt/ai-agents-share/
│
├── 📁 agents/                    # 智能体注册表
│   ├── 📄 registry.json          # 所有智能体列表
│   ├── 📁 xiaolongxia/           # 小龙虾配置
│   │   ├── 📄 config.json        # 智能体元数据
│   │   └── 📄 status.json        # 在线状态
│   └── 📁 hermes/                # Hermes 配置
│       ├── 📄 config.json
│       └── 📄 status.json
│
├── 📁 messages/                  # 消息传递（核心！）
│   ├── 📁 inbox/                 # 收件箱（按智能体分）
│   │   ├── 📁 xiaolongxia/       # 小龙虾收到的消息
│   │   │   ├── 📄 2026-05-15-001.json
│   │   │   └── 📄 2026-05-15-002.json
│   │   └── 📁 hermes/            # Hermes 收到的消息
│   │       └── 📄 2026-05-15-001.json
│   └── 📁 outbox/                # 发件箱
│       ├── 📁 xiaolongxia/
│       └── 📁 hermes/
│
├── 📁 tasks/                     # 任务委派
│   ├── 📁 pending/               # 待处理任务
│   │   ├── 📄 task-001.json      # 任务描述
│   │   └── 📄 task-002.json
│   ├── 📁 in-progress/           # 进行中
│   └── 📁 completed/             # 已完成
│       └── 📄 task-000.json
│
├── 📁 shared-memory/             # 共享记忆
│   ├── 📄 SHARED_MEMORY.md       # 共同记忆（两个智能体都能读写）
│   ├── 📁 projects/              # 项目共享上下文
│   │   └── 📁 textbook-writing/  # 教材编写项目
│   │       ├── 📄 context.md     # 项目上下文
│   │       └── 📄 progress.md    # 进度跟踪
│   └── 📁 knowledge/             # 共享知识库
│       └── 📄 dingtalk-integration.md
│
├── 📁 files/                     # 文件交换
│   ├── 📁 incoming/              # 接收的文件
│   └── 📁 outgoing/              # 待发送的文件
│
├── 📁 sync/                      # 文件系统同步
│   ├── 📁 xiaolongxia-workspace/ # 小龙虾 workspace 同步
│   │   ├── 📄 .sync-config.json  # 同步配置
│   │   └── 📁 skills/            # 技能文件同步
│   └── 📁 hermes-home/           # Hermes 主目录同步
│
└── 📁 locks/                     # 分布式锁
    ├── 📄 messages.lock          # 消息目录锁
    └── 📄 tasks.lock             # 任务目录锁
```

---

## 通信协议设计

### 消息格式

每条消息是一个 JSON 文件，文件名 = 时间戳 + 序号：

```json
{
  "id": "msg-20260515-001",
  "from": "xiaolongxia",
  "to": "hermes",
  "timestamp": "2026-05-15T22:00:00+08:00",
  "type": "message|task|file|status",
  "priority": "low|normal|high|urgent",
  "subject": "教材编写进度同步",
  "body": "Hermes，我刚整理了第三章的草稿，请查阅 shared-memory/projects/textbook-writing/ 目录",
  "attachments": [
    "files/outgoing/textbook-ch3-draft.md"
  ],
  "reply_to": "msg-20260515-000",
  "status": "unread|read|replied|archived"
}
```

### 任务格式

```json
{
  "id": "task-001",
  "from": "xiaolongxia",
  "to": "hermes",
  "created": "2026-05-15T22:00:00+08:00",
  "due": "2026-05-16T12:00:00+08:00",
  "type": "summarize|translate|generate|analyze|custom",
  "title": "总结第三章教材内容",
  "description": "请对 shared-memory/projects/textbook-writing/ch3.md 进行总结...",
  "input_files": ["shared-memory/projects/textbook-writing/ch3.md"],
  "output_files": ["shared-memory/projects/textbook-writing/ch3-summary.md"],
  "status": "pending|in-progress|completed|failed",
  "result": ""
}
```

### 状态格式

```json
{
  "agent": "xiaolongxia",
  "server": "server-a",
  "updated": "2026-05-15T22:00:00+08:00",
  "status": "online|busy|offline|sleeping",
  "current_task": "教材编写 - 第三章",
  "load": {
    "cpu_percent": 45,
    "memory_percent": 60,
    "disk_percent": 80
  },
  "capabilities": ["chinese", "math", "coding", "dingtalk"],
  "message_count": 15
}
```

---

## 部署步骤

### 方案一：阿里云 NAS 部署

#### Step 1：创建 NAS 文件系统

1. 登录阿里云控制台 → NAS 控制台
2. 创建文件系统（选择与服务器相同的 VPC）
3. 创建挂载点（NFS 协议）
4. 记录挂载地址，如：`file-system-id.cn-shanghai.nas.aliyuncs.com`

#### Step 2：配置挂载权限

```bash
# 在 NAS 控制台添加挂载权限组
# 允许两台服务器的内网 IP 访问
# 读写权限
```

#### Step 3：两台服务器挂载 NAS

```bash
# 在两台服务器上执行（服务器 A 和服务器 B）

# 1. 安装 NFS 客户端
sudo yum install -y nfs-utils    # Alibaba Cloud Linux / CentOS
# 或
sudo apt install -y nfs-common   # Ubuntu/Debian

# 2. 创建挂载点
sudo mkdir -p /mnt/ai-agents-share

# 3. 挂载 NAS
sudo mount -t nfs -o vers=3,nolock,proto=tcp,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport \
  file-system-id.cn-shanghai.nas.aliyuncs.com:/ \
  /mnt/ai-agents-share

# 4. 设置权限
sudo chown -R admin:admin /mnt/ai-agents-share
chmod -R 775 /mnt/ai-agents-share

# 5. 设置开机自动挂载
echo "file-system-id.cn-shanghai.nas.aliyuncs.com:/ /mnt/ai-agents-share nfs vers=3,nolock,proto=tcp,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport 0 0" | sudo tee -a /etc/fstab

# 6. 验证
df -h /mnt/ai-agents-share
touch /mnt/ai-agents-share/test.txt && rm /mnt/ai-agents-share/test.txt
```

#### Step 4：初始化目录结构

```bash
# 在任意一台服务器上执行（因为共享，另一台自动可见）

cd /mnt/ai-agents-share

# 创建目录结构
mkdir -p agents/xiaolongxa agents/hermes
mkdir -p messages/inbox/xiaolongxia messages/inbox/hermes
mkdir -p messages/outbox/xiaolongxia messages/outbox/hermes
mkdir -p tasks/{pending,in-progress,completed}
mkdir -p shared-memory/projects/textbook-writing
mkdir -p shared-memory/knowledge
mkdir -p files/{incoming,outgoing}
mkdir -p sync/xiaolongxia-workspace sync/hermes-home
mkdir -p locks

# 创建智能体注册表
cat > agents/registry.json << 'EOF'
{
  "agents": {
    "xiaolongxia": {
      "name": "小龙虾 - 诸葛虾",
      "type": "openclaw",
      "server": "server-a",
      "capabilities": ["chinese", "math", "coding", "dingtalk", "teaching"],
      "model": "qwen3.5-plus",
      "dingtalk_group": "📖小龙虾教材编写"
    },
    "hermes": {
      "name": "Hermes Agent",
      "type": "hermes",
      "server": "server-b",
      "capabilities": ["coding", "analysis", "automation"],
      "model": "tbd"
    }
  }
}
EOF

# 创建共享记忆文件
cat > shared-memory/SHARED_MEMORY.md << 'EOF'
# 🤝 共享记忆 - 小龙虾 & Hermes

> 这是两个 AI 智能体的共享记忆空间
> 最后更新：2026-05-15

## 项目

### 📖 小龙虾教材编写
- 状态：进行中
- 参与者：陈俊烨、诸葛斌、小龙虾
- 进度：待更新

## 约定
- 消息文件格式：JSON，文件名 = 时间戳-序号
- 任务文件放在 tasks/ 目录
- 状态文件每 5 分钟更新一次
EOF

echo "✅ 共享目录初始化完成"
```

#### Step 5：智能体监控脚本

```bash
# 在两台服务器上创建消息监控脚本
cat > /home/admin/watch-messages.sh << 'SCRIPT'
#!/bin/bash
# AI 智能体消息监控
# 定期检查共享消息目录，有新消息时通知智能体

SHARE_DIR="/mnt/ai-agents-share"
AGENT_NAME="xiaolongxia"  # 每台服务器设置不同的值
INBOX="$SHARE_DIR/messages/inbox/$AGENT_NAME"
LOCK_FILE="$SHARE_DIR/locks/messages.lock"

# 使用文件锁防止重复处理
(
  flock -n 200 || exit 0
  
  # 检查是否有新消息
  NEW_MSGS=$(find "$INBOX" -name "*.json" -newer /tmp/last-check-$AGENT_NAME 2>/dev/null | wc -l)
  
  if [ "$NEW_MSGS" -gt 0 ]; then
    echo "[$(date)] 收到 $NEW_MSGS 条新消息"
    # 更新检查时间戳
    touch /tmp/last-check-$AGENT_NAME
    # 这里可以触发智能体处理（通过 API 或文件信号）
  fi
) 200>"$LOCK_FILE"
SCRIPT

chmod +x /home/admin/watch-messages.sh

# 添加到 crontab（每 30 秒检查一次）
# 注意：cron 最小间隔 1 分钟，更频繁需要用 while 循环
(crontab -l 2>/dev/null; echo "* * * * * /home/admin/watch-messages.sh") | crontab -

# 或者用 systemd timer 实现更频繁的轮询
```

---

### 方案二：Syncthing 部署（备选）

#### 安装 Syncthing

```bash
# 两台服务器都安装
# Alibaba Cloud Linux / CentOS
sudo rpm -Uvh https://github.com/syncthing/syncthing/releases/download/v1.27.0/syncthing-linux-amd64-v1.27.0.tar.gz

# 或者直接下载
curl -LO https://github.com/syncthing/syncthing/releases/download/v1.27.0/syncthing-linux-amd64-v1.27.0.tar.gz
tar xzf syncthing-linux-amd64-v1.27.0.tar.gz
sudo cp syncthing-linux-amd64-v1.27.0/syncthing /usr/local/bin/
```

#### 配置同步

```bash
# 1. 启动 Syncthing（两台服务器）
syncthing generate
syncthing daemon

# 2. 访问 Web UI（http://localhost:8384）
# 3. 添加对方设备（通过 Device ID）
# 4. 创建共享文件夹：
#    - 服务器 A: ~/.openclaw/workspace → 同步到服务器 B
#    - 服务器 B: ~/.hermes → 同步到服务器 A
```

---

## 安全设计

### 1. 文件系统权限

```bash
# NAS 挂载权限组：只允许两台服务器 IP
# 目录权限：
chmod 775 /mnt/ai-agents-share          # 主目录
chmod 770 /mnt/ai-agents-share/messages # 消息目录（敏感）
chmod 775 /mnt/ai-agents-share/shared-memory  # 共享记忆

# 创建专用用户组
sudo groupadd ai-agents
sudo usermod -aG ai-agents admin        # 两台服务器都加
sudo chgrp -R ai-agents /mnt/ai-agents-share
```

### 2. 消息加密（可选）

```bash
# 对敏感消息文件进行 GPG 加密
# 两台服务器共享同一个 GPG 密钥对

# 生成密钥
gpg --gen-key

# 加密消息
gpg -e -r ai-agents messages/inbox/xiaolongxia/secret.json

# 解密
gpg -d messages/inbox/xiaolongxia/secret.json.gpg
```

### 3. 网络隔离

```
# 安全组规则：
# - 只允许 VPC 内网访问 NAS 挂载点
# - 不暴露 NFS 端口到公网
# - 两台服务器之间通过内网互通
```

---

## 运维监控

### 健康检查

```bash
# 创建健康检查脚本
cat > /home/admin/check-share-health.sh << 'SCRIPT'
#!/bin/bash
SHARE_DIR="/mnt/ai-agents-share"

# 检查挂载状态
if ! mountpoint -q "$SHARE_DIR"; then
  echo "❌ NAS 未挂载！尝试重新挂载..."
  sudo mount -a
  if ! mountpoint -q "$SHARE_DIR"; then
    echo "🚨 NAS 挂载失败！" | tee -a /var/log/ai-share.log
    exit 1
  fi
fi

# 检查读写能力
TEST_FILE="$SHARE_DIR/.health-check"
if echo "$(date)" > "$TEST_FILE" 2>/dev/null; then
  rm -f "$TEST_FILE"
  echo "✅ NAS 健康检查通过"
else
  echo "🚨 NAS 读写失败！" | tee -a /var/log/ai-share.log
  exit 1
fi

# 检查磁盘使用
USAGE=$(df "$SHARE_DIR" | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USAGE" -gt 90 ]; then
  echo "⚠️ NAS 使用率 ${USAGE}%" | tee -a /var/log/ai-share.log
fi
SCRIPT

chmod +x /home/admin/check-share-health.sh

# 每 5 分钟检查一次
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/admin/check-share-health.sh >> /var/log/ai-share.log 2>&1") | crontab -
```

### 日志

```bash
# 消息日志
tail -f /var/log/ai-share.log

# 监控文件变化
inotifywait -m -r /mnt/ai-agents-share/messages/
```

---

## 实施计划

### 阶段一：基础设施（1-2 天）

- [ ] 创建阿里云 NAS 文件系统
- [ ] 配置 VPC 和网络
- [ ] 两台服务器挂载 NAS
- [ ] 初始化目录结构
- [ ] 测试读写性能

### 阶段二：通信机制（2-3 天）

- [ ] 实现消息收发脚本
- [ ] 实现任务委派机制
- [ ] 实现状态同步
- [ ] 测试小龙虾 ↔ Hermes 通信

### 阶段三：智能体集成（3-5 天）

- [ ] 小龙虾读取共享消息（作为 cron 任务）
- [ ] 小龙虾发送消息到 Hermes
- [ ] Hermes 读取共享消息
- [ ] Hermes 发送消息到小龙虾
- [ ] 实现共享记忆更新

### 阶段四：优化和扩展（持续）

- [ ] 性能优化
- [ ] 添加更多智能体
- [ ] 实现文件自动同步
- [ ] 添加监控告警

---

## 成本估算

| 项目 | 费用 | 说明 |
|------|------|------|
| **阿里云 NAS** | ~¥5-20/月 | 实际使用量很小（几 GB） |
| **内网流量** | ¥0 | 同 VPC 内网免费 |
| **运维时间** | ~1 小时/月 | 基本免维护 |
| **总计** | ~¥5-20/月 | |

---

## 总结

| 方案 | 推荐度 | 适合场景 |
|------|--------|----------|
| **阿里云 NAS** | ⭐⭐⭐⭐⭐ | 同 VPC 阿里云服务器，零运维 |
| **Syncthing** | ⭐⭐⭐⭐ | 跨云/跨地域，需要版本控制 |
| **自建 NFS** | ⭐⭐⭐ | 预算为零，能接受单点风险 |
| **Rsync** | ⭐⭐ | 简单场景，定时同步即可 |
| **OSS 挂载** | ⭐⭐ | 大文件为主，不频繁读写 |

**建议：先用阿里云 NAS 跑通，后续根据实际需求考虑是否需要 Syncthing 做双向同步备份。**

---

**设计完成时间**：2026-05-15  
**下一步**：确认方案后开始创建 NAS 文件系统 🦞
