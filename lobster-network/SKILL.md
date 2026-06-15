# 🦞 Lobster Network Skill - 龙虾池协作技能

## 技能信息

- **名称**: lobster-network
- **版本**: 1.0.0
- **描述**: 龙虾池多智能体协作技能，实现 OpenClaw 实例间的消息中继与任务协调
- **作者**: 孙豪
- **触发词**: 龙虾池、lobster、协作请求、任务协调、多智能体

---

## 功能特性

- ✅ 接收其他龙虾的协作请求
- ✅ 通过钉钉群广播消息
- ✅ 请求队列管理（pending/done）
- ✅ HTTP API 接口（/invoke, /response, /pending, /status）
- ✅ systemd 服务支持（开机自启）
- ✅ 日志记录与监控

---

## 安装方式

### 方式一：本地安装（推荐）

```bash
cd ~/.openclaw/workspace/lobster-network
# 技能文件已存在，无需额外安装
```

### 方式二：从 ClawHub 安装

```bash
clawhub install lobster-network
```

### 方式三：手动安装

```bash
# 1. 下载技能包
wget https://github.com/your-repo/lobster-network-skill.tar.gz

# 2. 解压到技能目录
tar -xzf lobster-network-skill.tar.gz -C ~/.openclaw/workspace/skills/

# 3. 安装依赖
pip3 install flask requests --user
```

---

## 使用方法

### 1. 启动 Wrapper 服务

```bash
# 本地启动
python3 ~/.openclaw/workspace/lobster-network/wrapper.py \
  --lobster-id=lobster-002 \
  --port=8002

# 后台启动
nohup python3 ~/.openclaw/workspace/lobster-network/wrapper.py \
  --lobster-id=lobster-002 --port=8002 > ~/lobster-tasks/logs/lobster-002.log 2>&1 &
```

### 2. 使用 systemd 管理

```bash
# 复制服务文件
sudo cp ~/.openclaw/workspace/lobster-network/lobster-wrapper@.service /etc/systemd/system/

# 重载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start lobster-wrapper@lobster-002.service

# 开机自启
sudo systemctl enable lobster-wrapper@lobster-002.service

# 查看状态
sudo systemctl status lobster-wrapper@lobster-002.service
```

### 3. API 调用示例

```bash
# 健康检查
curl http://127.0.0.1:8002/health

# 接收协作请求
curl -X POST http://127.0.0.1:8002/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-001","to":"lobster-002","msg":"请处理任务","intent":"coordination"}'

# 提交响应
curl -X POST http://127.0.0.1:8002/response \
  -H "Content-Type: application/json" \
  -d '{"request_id":"req_xxx","from":"lobster-002","to":"lobster-001","result":"已完成","status":"completed"}'

# 查看待办
curl http://127.0.0.1:8002/pending

# 查看状态
curl http://127.0.0.1:8002/status
```

---

## 配置说明

### 钉钉配置（wrapper.py）

```python
DINGTALK_ACCESS_TOKEN = "你的 access_token"
DINGTALK_SECRET = "你的 SEC 开头的 secret"
```

### 龙虾 ID 配置

每个龙虾节点需要唯一的 ID：
- lobster-001: 调度中枢（小龙虾）
- lobster-002 ~ lobster-010: 工作节点

### 端口规划

| 龙虾 ID | 端口 |
|--------|------|
| lobster-001 | 8001 |
| lobster-002 | 8002 |
| ... | ... |
| lobster-010 | 8010 |

---

## 文件结构

```
~/.openclaw/workspace/lobster-network/
├── wrapper.py                    # HTTP Wrapper 主程序
├── lobster_scheduler.py          # 调度核心（小龙虾专用）
├── dingtalk_sender.py            # 钉钉发送工具
├── deploy.sh                     # 部署脚本
├── batch-deploy.sh               # 批量部署脚本
├── lobster-wrapper@.service      # systemd 服务模板
├── README.md                     # 使用指南
├── DEPLOYMENT.md                 # 部署文档
└── SKILL.md                      # 技能说明（本文档）
```

---

## 依赖要求

- Python 3.8+
- Flask
- requests
- systemd（可选，用于服务管理）

安装依赖：
```bash
pip3 install flask requests --user
```

---

## 日志与监控

### 日志位置

```bash
# Wrapper 日志
~/lobster-tasks/logs/lobster-002.log

# 请求队列
~/lobster-tasks/pending/requests.json

# 响应记录
~/lobster-tasks/done/responses.json
```

### 实时监控

```bash
# 查看实时日志
tail -f ~/lobster-tasks/logs/lobster-002.log

# 查看待办请求
watch -n 5 'cat ~/lobster-tasks/pending/requests.json | python3 -m json.tool'
```

---

## 常见问题

### Q1: 端口被占用
```bash
# 检查端口占用
netstat -tlnp | grep 8002

# 更换端口
python3 wrapper.py --lobster-id=lobster-002 --port=8012
```

### Q2: Flask 未安装
```bash
pip3 install flask requests --user
```

### Q3: systemd 服务启动失败
```bash
# 查看错误日志
sudo journalctl -u lobster-wrapper@lobster-002.service -n 50

# 手动测试
python3 ~/.openclaw/workspace/lobster-network/wrapper.py --lobster-id=lobster-002 --port=8002
```

### Q4: 钉钉消息发送失败
- 检查 access_token 和 secret 是否正确
- 检查机器人是否还在群里
- 检查是否触发频率限制（每分钟 20 条）

---

## 协作流程

```
1. lobster-001 发起请求
   ↓ (HTTP POST /invoke)
2. Wrapper 接收并写入队列
   ↓ (钉钉群广播)
3. 目标龙虾收到消息
   ↓ (处理任务)
4. 提交响应 (HTTP POST /response)
   ↓ (钉钉群广播)
5. lobster-001 收到响应
```

---

## 更新日志

### v1.0.0 (2026-04-19)
- ✅ 初始版本发布
- ✅ HTTP Wrapper 实现
- ✅ 钉钉消息发送
- ✅ 请求队列管理
- ✅ systemd 服务支持

---

## 联系与支持

- **作者**: 孙豪
- **钉钉群**: 智能体小龙虾测试
- **文档**: `~/.openclaw/workspace/lobster-network/README.md`

---

## 许可证

MIT License
