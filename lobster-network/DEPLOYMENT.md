# 🦞 龙虾池部署包 - 完整清单

## 📦 文件列表

```
~/.openclaw/workspace/lobster-network/
├── wrapper.py                    # HTTP Wrapper（每个龙虾节点一份）
├── lobster_scheduler.py          # 调度核心（小龙虾专用）
├── dingtalk_sender.py            # 钉钉官方示例（参考用）
├── deploy.sh                     # 单节点部署脚本
├── batch-deploy.sh               # 批量部署脚本
├── lobster-wrapper@.service      # systemd 服务模板
├── README.md                     # 使用指南
└── DEPLOYMENT.md                 # 本文档
```

---

## ✅ 本地部署验证（已完成）

| 组件 | 状态 | 验证结果 |
|------|------|----------|
| wrapper.py | ✅ 运行中 | `http://127.0.0.1:8001/health` → `{"status":"ok"}` |
| 钉钉发送 | ✅ 测试通过 | 消息已发送到「智能体小龙虾测试」群 |
| 请求队列 | ✅ 正常工作 | 请求已写入 `~/lobster-tasks/pending/requests.json` |

---

## 🚀 部署到其他 9 台服务器

### 方案 A：手动部署（推荐，可控性强）

对每台服务器执行：

```bash
# 1. 上传文件
scp ~/.openclaw/workspace/lobster-network/wrapper.py \
    ~/.openclaw/workspace/lobster-network/deploy.sh \
    admin@192.168.1.102:~/lobster-network/

# 2. SSH 登录并部署
ssh admin@192.168.1.102
cd ~/lobster-network
bash deploy.sh --lobster-id=lobster-002 --port=8002
```

### 方案 B：批量部署（快速，但需要信任配置）

```bash
# 编辑 batch-deploy.sh 中的 IP 列表
vim ~/.openclaw/workspace/lobster-network/batch-deploy.sh

# 执行批量部署
bash ~/.openclaw/workspace/lobster-network/batch-deploy.sh
```

---

## 📋 10 个龙虾节点规划

| 节点 ID | 服务器 IP | 端口 | 角色 | 状态 |
|--------|-----------|------|------|------|
| lobster-001 | 127.0.0.1 (本地) | 8001 | 调度中枢 | ✅ 已部署 |
| lobster-002 | 192.168.1.102 | 8002 | 工作节点 | ⏳ 待部署 |
| lobster-003 | 192.168.1.103 | 8003 | 工作节点 | ⏳ 待部署 |
| lobster-004 | 192.168.1.104 | 8004 | 工作节点 | ⏳ 待部署 |
| lobster-005 | 192.168.1.105 | 8005 | 工作节点 | ⏳ 待部署 |
| lobster-006 | 192.168.1.106 | 8006 | 工作节点 | ⏳ 待部署 |
| lobster-007 | 192.168.1.107 | 8007 | 工作节点 | ⏳ 待部署 |
| lobster-008 | 192.168.1.108 | 8008 | 工作节点 | ⏳ 待部署 |
| lobster-009 | 192.168.1.109 | 8009 | 工作节点 | ⏳ 待部署 |
| lobster-010 | 192.168.1.110 | 8010 | 工作节点 | ⏳ 待部署 |

---

## 🔧 管理命令

### 本地节点 (lobster-001)

```bash
# 查看状态
curl http://127.0.0.1:8001/health

# 查看待办请求
curl http://127.0.0.1:8001/pending

# 查看总体状态
curl http://127.0.0.1:8001/status

# 停止服务
pkill -f "wrapper.py.*lobster-001"

# 重启服务
pkill -f "wrapper.py.*lobster-001"
sleep 1
cd ~/.openclaw/workspace/lobster-network
nohup python3 wrapper.py --lobster-id=lobster-001 --port=8001 > ~/lobster-tasks/logs/lobster-001.log 2>&1 &
```

### 远程节点 (通过 systemd)

```bash
# 查看状态
sudo systemctl status lobster-wrapper@lobster-002.service

# 启动
sudo systemctl start lobster-wrapper@lobster-002.service

# 停止
sudo systemctl stop lobster-wrapper@lobster-002.service

# 查看日志
sudo journalctl -u lobster-wrapper@lobster-002.service -f
```

---

## 🧪 测试流程

### 1. 测试本地协作

```bash
# 发送请求
curl -X POST http://127.0.0.1:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-001","to":"lobster-002","msg":"测试协作","intent":"coordination"}'

# 查看钉钉群，应该收到：
# [LOBSTER-MSG] from=lobster-001&to=lobster-002&intent=coordination&msg=测试协作
```

### 2. 测试完整流程

```bash
# 1. lobster-001 发起请求
curl -X POST http://127.0.0.1:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-001","to":"lobster-002","msg":"请评估资源池 A","intent":"query"}'

# 2. lobster-002 处理并响应（模拟）
curl -X POST http://127.0.0.1:8002/response \
  -H "Content-Type: application/json" \
  -d '{"request_id":"req_xxx","from":"lobster-002","to":"lobster-001","result":"资源池 A 剩余 80%","status":"completed"}'

# 3. 查看钉钉群，应该收到响应消息
```

---

## 📊 监控与日志

### 日志位置

```bash
# Wrapper 日志
~/lobster-tasks/logs/lobster-001.log

# 请求队列
~/lobster-tasks/pending/requests.json

# 响应记录
~/lobster-tasks/done/responses.json
```

### 实时监控

```bash
# 查看实时日志
tail -f ~/lobster-tasks/logs/lobster-001.log

# 查看待办请求
watch -n 5 'cat ~/lobster-tasks/pending/requests.json | python3 -m json.tool'

# 查看钉钉消息（手动）
# 打开钉钉群「智能体小龙虾测试」
```

---

## ⚠️ 常见问题

### Q1: 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep 8001

# 更换端口
python3 wrapper.py --lobster-id=lobster-001 --port=8011
```

### Q2: Flask 未安装
```bash
pip3 install flask requests --user
```

### Q3: systemd 服务启动失败
```bash
# 查看错误日志
sudo journalctl -u lobster-wrapper@lobster-001.service -n 50

# 手动测试
python3 ~/lobster-network/wrapper.py --lobster-id=lobster-001 --port=8001
```

### Q4: 钉钉消息发送失败
```bash
# 检查 access_token 和 secret 是否正确
# 检查机器人是否还在群里
# 检查是否触发频率限制（每分钟 20 条）
```

---

## 📈 下一步

1. ✅ 本地节点部署完成（lobster-001）
2. ⏳ 部署其他 9 个节点（lobster-002 ~ lobster-010）
3. ⏳ 配置 OpenClaw heartbeat 轮询
4. ⏳ 测试完整协作流程
5. ⏳ 监控与优化

---

## 🎯 快速命令参考

```bash
# 健康检查
curl http://127.0.0.1:8001/health

# 发送请求
curl -X POST http://127.0.0.1:8001/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-001","to":"lobster-002","msg":"Hello","intent":"general"}'

# 查看待办
curl http://127.0.0.1:8001/pending | python3 -m json.tool

# 查看状态
curl http://127.0.0.1:8001/status | python3 -m json.tool
```

---

**🦞 龙虾池，启动！**
