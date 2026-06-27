# 📡 小龙虾网络通信架构方案 v2.0

## 📊 通信现状诊断（2026-06-27）

### 网络拓扑
```
┌─────────────────────────────────────────────────────────────┐
│                     互联网 (公网)                            │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  诸葛马     │    │  诸葛虾     │    │  小陈       │     │
│  │ 172.24.57.34│    │ 172.24.56.3 │    │ 121.43.80.231│    │
│  │ (阿里云VPC) │    │ (阿里云VPC) │    │ (公网IP)    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                    │                    │         │
│         └────────────────────┴────────────────────┘         │
│                    VPC内网 (172.24.x.x)                      │
│                                                             │
│  ┌─────────────┐                                            │
│  │  qoder      │← 只能通过GitHub通信                         │
│  │ (Mac本地)   │  192.168.1.161                             │
│  └─────────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

### 通信现状
| 节点 | 内网IP | 公网IP | SSH状态 | GitHub |
|------|--------|--------|---------|--------|
| 诸葛马 | 172.24.57.34 | 47.93.6.57 | ✓ 服务器间互通 | ✓ |
| 诸葛虾 | 172.24.56.3 | 183.134.108.26 | ✗ 未配置key | ✓ |
| 小陈 | 172.27.52.212 | 121.43.80.231 | ✓ 已配置 | ✓ |
| qoder | 192.168.1.161 | - | ✗ 无法SSH | ✓ |

### 核心问题
1. **内网IP不可达**：172.24.x.x 是阿里云VPC内网地址，从外部无法访问
2. **SSH认证失败**：诸葛虾服务器未配置SSH key
3. **qoder隔离**：只能通过GitHub交换数据
4. **NFS共享目录**：只存在于服务器端，本机未挂载

---

## 🚀 三层通信架构方案

### 第一层：GitHub工作流（短期 - 已就绪）
**优先级**：★★★★★
**状态**：✅ 已部署

```bash
# 教练推送训练计划
git push origin main

# 学员拉取并执行
git pull origin main
python3 domains/go/trainers/xiaochen_go_trainer_v3.py

# 学员推送结果
git add docs/training_results/
git commit -m "Day1训练结果"
git push origin main
```

**优点**：
- 稳定可靠，无需额外配置
- 所有节点都能访问
- 版本控制天然支持

**缺点**：
- 非实时（需要轮询）
- 依赖网络连通性

---

### 第二层：SSH密钥配置（中期 - 需要配置）
**优先级**：★★★★☆
**状态**：🔧 需要配置

#### 配置步骤

**1. 诸葛虾服务器配置SSH密钥**
```bash
# 在诸葛虾服务器上执行
ssh -i ~/.ssh/id_rsa_hermes admin@183.134.108.26

# 添加诸葛马的公钥
cat ~/.ssh/id_rsa_hermes.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**2. 小陈服务器配置SSH密钥**
```bash
# 在小陈服务器上执行
ssh -i ~/.ssh/id_rsa_hermes admin@121.43.80.231

# 添加诸葛马的公钥
cat ~/.ssh/id_rsa_hermes.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

**3. 验证SSH连通性**
```bash
# 从诸葛马服务器测试
ssh -i ~/.ssh/id_rsa_hermes admin@183.134.108.26 "echo '诸葛虾在线'"
ssh -i ~/.ssh/id_rsa_hermes admin@121.43.80.231 "echo '小陈在线'"
```

---

### 第三层：v0.6.0 HTTP传输层（长期 - 推荐部署）
**优先级**：★★★☆☆
**状态**：📝 待部署

#### 部署架构
```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP Transport Layer                     │
│                                                             │
│  诸葛马: http://47.93.6.57:8199                            │
│  诸葛虾: http://183.134.108.26:8199                        │
│  小陈:   http://121.43.80.231:8199                         │
│                                                             │
│  功能：                                                     │
│  - 实时消息传递                                             │
│  - 心跳检测                                                 │
│  - 节点发现                                                 │
│  - 消息持久化                                               │
└─────────────────────────────────────────────────────────────┘
```

#### 部署脚本
见 `scripts/deploy_http_transport.sh`

---

## 📋 实施计划

| 阶段 | 时间 | 任务 | 负责人 |
|------|------|------|--------|
| 短期 | 立即 | GitHub工作流 | 诸葛马 |
| 中期 | 1周内 | SSH密钥配置 | 诸葛马+诸葛虾 |
| 长期 | 2周内 | HTTP传输层部署 | 诸葛马 |

---

## 🔗 通信协议

### GitHub工作流协议
```json
{
  "protocol": "github",
  "repo": "https://github.com/zhugebin-hub/lobster-network",
  "branches": {
    "main": "训练计划和结果",
    "dev": "开发分支"
  },
  "directories": {
    "plans": "docs/training_plans/",
    "results": "docs/training_results/",
    "assessments": "docs/assessments/"
  }
}
```

### SSH工作流协议
```json
{
  "protocol": "ssh",
  "key": "~/.ssh/id_rsa_hermes",
  "shared_dir": "/home/admin/go-training/shared/",
  "directories": {
    "from-hermes": "诸葛马→学员",
    "from-xiaochen": "小陈→诸葛马",
    "from-zhuguxia": "诸葛虾→诸葛马",
    "from-qoder": "qoder→诸葛马"
  }
}
```

### HTTP工作流协议
```json
{
  "protocol": "http",
  "port": 8199,
  "endpoints": {
    "send": "/api/v1/send",
    "receive": "/api/v1/receive",
    "heartbeat": "/api/v1/heartbeat",
    "discover": "/api/v1/discover"
  }
}
```

---

## 📊 通信矩阵（更新后）

| 通信路径 | 协议 | 状态 | 延迟 |
|----------|------|------|------|
| 诸葛马→诸葛虾 | GitHub | ✓ | 分钟级 |
| 诸葛马→小陈 | SSH | ✓ | 秒级 |
| 诸葛马→qoder | GitHub | ✓ | 分钟级 |
| 诸葛虾→诸葛马 | GitHub | ✓ | 分钟级 |
| 小陈→诸葛马 | SSH | ✓ | 秒级 |
| qoder→诸葛马 | GitHub | ✓ | 分钟级 |

---

*方案由诸葛马 (Hermes) v2.0 生成*
