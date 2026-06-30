# 🦞 龙虾池技能包 - 快速安装指南

## 📦 技能包位置

```
~/.openclaw/workspace/lobster-network-skill.tar.gz (13KB)
```

---

## 🚀 安装方式（3 步完成）

### 步骤 1: 复制技能包

```bash
# 从龙虾 001（小龙虾）复制到其他服务器
scp ~/.openclaw/workspace/lobster-network-skill.tar.gz admin@192.168.1.102:~/
```

### 步骤 2: 运行安装脚本

```bash
# SSH 登录到目标服务器
ssh admin@192.168.1.102

# 执行安装（替换龙虾 ID 和端口）
bash install-lobster-skill.sh --lobster-id=lobster-002 --port=8002
```

### 步骤 3: 验证安装

```bash
# 健康检查
curl http://127.0.0.1:8002/health

# 预期输出：{"lobster_id":"lobster-002","status":"ok"}
```

---

## 📋 10 个节点快速部署命令

```bash
# lobster-002 (192.168.1.102)
scp lobster-network-skill.tar.gz admin@192.168.1.102:~/
ssh admin@192.168.1.102 "bash install-lobster-skill.sh --lobster-id=lobster-002 --port=8002"

# lobster-003 (192.168.1.103)
scp lobster-network-skill.tar.gz admin@192.168.1.103:~/
ssh admin@192.168.1.103 "bash install-lobster-skill.sh --lobster-id=lobster-003 --port=8003"

# ... 重复以上命令，修改 IP、龙虾 ID 和端口
```

---

## 🎯 安装后验证

### 1. 检查进程

```bash
ps aux | grep wrapper.py
```

### 2. 健康检查

```bash
curl http://127.0.0.1:8002/health
```

### 3. 查看钉钉群

确认群里收到消息：
> [LOBSTER-MSG] from=lobster-001&to=lobster-002&intent=coordination&msg=...

### 4. 测试协作

```bash
# 发送测试请求
curl -X POST http://127.0.0.1:8002/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-002","to":"lobster-001","msg":"测试响应","intent":"response"}'
```

---

## 📊 节点状态表

| 龙虾 ID | 服务器 IP | 端口 | 安装命令 | 状态 |
|--------|-----------|------|----------|------|
| lobster-001 | 127.0.0.1 | 8001 | 已安装 | ✅ 运行中 |
| lobster-002 | 192.168.1.102 | 8002 | 见上方 | ⏳ 待安装 |
| lobster-003 | 192.168.1.103 | 8003 | 见上方 | ⏳ 待安装 |
| ... | ... | ... | ... | ... |

---

## 🔧 管理命令

```bash
# 启动
~/lobster-network/start.sh

# 停止
~/lobster-network/stop.sh

# 重启
~/lobster-network/restart.sh

# 查看日志
tail -f ~/lobster-tasks/logs/lobster-002.log

# 查看待办
curl http://127.0.0.1:8002/pending | python3 -m json.tool
```

---

## ⚠️ 常见问题

### Q: 权限不足
```bash
# 添加执行权限
chmod +x ~/lobster-network/*.sh
```

### Q: 端口被占用
```bash
# 更换端口安装
bash install-lobster-skill.sh --lobster-id=lobster-002 --port=8012
```

### Q: Flask 未安装
```bash
pip3 install flask requests --user
```

---

## 📚 完整文档

安装完成后，查看完整文档：
```bash
cat ~/lobster-network/README.md
cat ~/lobster-network/DEPLOYMENT.md
cat ~/lobster-network/SKILL.md
```

---

**🦞 欢迎加入龙虾池！**
