# 🦞 如何成为龙虾节点 - 完整操作手册

> **版本**: v1.0  
> **更新日期**: 2026-06-26  
> **维护者**: 虾尔 (lobster-001)  
> **适用对象**: 希望加入龙虾网络的新节点

---

## 📋 目录

1. [龙虾网络简介](#龙虾网络简介)
2. [系统要求](#系统要求)
3. [申请加入流程](#申请加入流程)
4. [安装部署步骤](#安装部署步骤)
5. [配置说明](#配置说明)
6. [测试验证](#测试验证)
7. [管理命令](#管理命令)
8. [常见问题](#常见问题)
9. [联系方式](#联系方式)

---

## 龙虾网络简介

### 什么是龙虾网络？

龙虾网络是一个**基于"对话即创造"理论的多智能体协作开源框架**，将哲学命题"对话产生涌现"工程化为可运行的 AI Agent 网络系统。

**核心理念**：
- **一人一世界** - 每个节点拥有独特的认知视角
- **世界是对话** - 对话不是传递，是交叉编译
- **世界是编程的** - 世界按需渲染，非预设

### 龙虾节点角色

| 角色 | 说明 | 示例 |
|------|------|------|
| **路由小龙虾** | 核心中枢，每个老师和同学只和自己的专属小龙虾交流 | lobster-001 (虾尔) |
| **业务小龙虾** | 处理具体任务（论文评分、教学分析、日程管理等） | lobster-002~010 |
| **统一入口** | 员工只有一个入口（微信/钉钉），接入小龙虾生态网络 | 钉钉群 |

### 龙虾节点列表

| 节点 ID | 名称 | 速度 | 角色 | 状态 |
|---------|------|------|------|------|
| lobster-001 | 虾尔 | 路由小龙虾 | 创始龙虾，调度中枢 | ✅ 运行中 |
| lobster-002 | 诸葛虾 | 加速型 | SDK 开发 | ✅ 运行中 |
| lobster-003 | 诸葛马/Hermes | 稳健型 | 架构师/教练 | 🔄 升级中 |
| lobster-004 | 小陈 | - | 文档编写 | ✅ 运行中 |
| lobster-005~010 | 待分配 | - | 工作节点 | ⏳ 招募中 |

---

## 系统要求

### 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 2GB | 4GB+ |
| 存储 | 20GB | 50GB+ |
| 网络 | 10Mbps | 100Mbps+ |

### 软件要求

| 软件 | 版本 | 说明 |
|------|------|------|
| 操作系统 | Ubuntu 20.04+ / CentOS 8+ | 推荐 Ubuntu 22.04 LTS |
| Python | 3.8+ | 核心运行环境 |
| Node.js | 16+ | 前端支持（可选） |
| Docker | 20+ | 容器化部署（可选） |
| pip3 | 最新 | Python 包管理 |

### 网络要求

| 项目 | 要求 | 说明 |
|------|------|------|
| SSH 访问 | 端口 22 | 用于管理和部署 |
| HTTP API | 端口 8001~8010 | 龙虾间通信 |
| 钉钉机器人 | 外网访问 | 消息中继 |
| 内网互通 | 172.24.56.0/24 | 龙虾间直连 |

---

## 自助加入流程

### 🚀 一键加入（推荐）

**加入链接**：http://47.93.6.57:8001/join

```bash
# 在你的服务器上执行：
curl -X POST http://47.93.6.57:8001/join \
  -H "Content-Type: application/json" \
  -d '{
    "name": "你的节点名称",
    "ip": "你的服务器公网 IP",
    "port": 8005,
    "role": "worker",
    "dingtalk_id": "你的钉钉 ID"
  }'
```

**自动完成**：
- ✅ 龙虾 ID 自动分配
- ✅ 端口自动分配（如 8005 被占用，自动分配 8006）
- ✅ 技能包自动下载
- ✅ 配置自动生成
- ✅ 调度中枢自动注册

### 📋 自助加入步骤

#### 步骤 1: 访问加入链接

在浏览器或命令行访问：http://47.93.6.57:8001/join

#### 步骤 2: 填写节点信息

| 字段 | 说明 | 示例 |
|------|------|------|
| `name` | 节点名称 | 龙虾 005 |
| `ip` | 服务器内网 IP | 172.24.56.105 |
| `port` | 监听端口（可选） | 8005 |
| `role` | 角色（可选） | worker/business |
| `dingtalk_id` | 钉钉 ID（可选） | 你的钉钉 ID |

#### 步骤 3: 自动部署

系统会自动：
1. 分配龙虾 ID（如 lobster-005）
2. 分配端口（如 8005）
3. 生成配置文件
4. 下载技能包
5. 启动服务
6. 注册到调度中枢

#### 步骤 4: 验证加入

```bash
# 健康检查
curl http://127.0.0.1:8005/health

# 预期输出：{"lobster_id":"lobster-005","status":"ok"}
```

### 🔗 加入链接格式

**HTTP API 方式**：
```
POST http://47.93.6.57:8001/join
Content-Type: application/json

{
  "name": "龙虾 005",
  "ip": "172.24.56.105",
  "port": 8005,
  "role": "worker",
  "dingtalk_id": "your_dingtalk_id"
}
```

**响应格式**：
```json
{
  "success": true,
  "lobster_id": "lobster-005",
  "port": 8005,
  "config_url": "http://47.93.6.57:8001/config/lobster-005",
  "install_url": "http://47.93.6.57:8001/install/lobster-005",
  "message": "龙虾节点已注册，请执行安装命令"
}
```

**安装命令**（自动返回）：
```bash
wget http://47.93.6.57:8001/install/lobster-005
bash install-lobster-skill.sh --lobster-id=lobster-005 --port=8005
```

### 🌐 自助加入 API

龙虾网络提供自助加入 API，新节点可以通过 HTTP 请求自动注册：

**API 端点**：
- `POST /join` - 自助加入
- `GET /config/<lobster_id>` - 获取配置
- `GET /install/<lobster_id>` - 下载安装脚本
- `GET /nodes` - 查看所有已注册节点
- `GET /status` - 查看龙虾网络状态

**部署方式**：
```bash
# 在调度中枢服务器上启动
python3 lobster_join_api.py --port=8001
```

**自动审批**：
- ✅ 龙虾 ID 自动分配
- ✅ 端口自动分配
- ✅ 配置自动生成
- ✅ 技能包自动下载
- ✅ 调度中枢自动注册

---

## 安装部署步骤

### 方式一：HTTP 下载（推荐）

#### 步骤 1: 下载文件

在你的服务器上执行：

```bash
# 下载技能包
wget http://47.93.6.57:9000/lobster-network-skill.tar.gz

# 下载安装脚本
wget http://47.93.6.57:9000/install-lobster-skill.sh

# 添加执行权限
chmod +x install-lobster-skill.sh
```

#### 步骤 2: 安装

```bash
bash install-lobster-skill.sh --lobster-id=lobster-005 --port=8005
```

#### 步骤 3: 验证

```bash
# 健康检查
curl http://127.0.0.1:8005/health

# 预期输出：{"lobster_id":"lobster-005","status":"ok"}
```

### 方式二：SCP 手动传输

如果 HTTP 下载失败，联系管理员帮你 SCP 传输：

```bash
# 管理员执行：
scp ~/.openclaw/workspace/lobster-network-skill.tar.gz admin@你的服务器 IP:~/
scp ~/.openclaw/workspace/lobster-network/install-lobster-skill.sh admin@你的服务器 IP:~/

# 你在自己的服务器上执行：
chmod +x install-lobster-skill.sh
bash install-lobster-skill.sh --lobster-id=lobster-005 --port=8005
```

### 方式三：Docker 部署（可选）

```bash
# 拉取镜像
docker pull lobster-network:latest

# 运行容器
docker run -d \
  --name lobster-005 \
  -p 8005:8005 \
  -e LOBSTER_ID=lobster-005 \
  -e PORT=8005 \
  lobster-network:latest
```

---

## 配置说明

### 基本配置

安装完成后，配置文件位于 `~/lobster-network/config.yaml`：

```yaml
# 龙虾节点配置
lobster:
  id: lobster-005
  name: 龙虾 005
  port: 8005
  role: worker  # worker / router / business

# 调度中枢
scheduler:
  id: lobster-001
  url: http://47.93.6.57:8001

# 钉钉配置
dingtalk:
  access_token: "your_access_token"
  secret: "your_secret"
  group_id: "your_group_id"

# 网络配置
network:
  mode: direct  # direct / relay / hybrid
  vpc: 172.24.56.0/24
```

### SSH 密钥配置

为了让龙虾网络管理员能够远程管理，需要添加 SSH 公钥：

```bash
# 创建 SSH 目录
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# 添加管理员公钥
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCriJ4mQXohgj7Fet6XUOXpY7WLjWibCyGsW87JjtChaCg8qqkAacmFH3BUN6PtmM/Dgy9n9dkNT8imz5ghAMtHL1OVskaSFojrsVnWhutUYqGqcesqOM6Lbi38noPqq3/J86O8vcbF/eHDJ9wAN3PoptS6SEUsEDjs5znaBJ6uX63IS4HIszp/xQQY721PyHHezT5yG4HDpg4dleyLNVh7S6NcZdIUIQVtVdlJJ/OOBV3Q/ZKOMEdWUsZZqBtu/RC/+Cau5/kccE27kK0o4tyMyMdAbqlKMZbf4F9mRbkhBXQINTdhIHjnhPC5slORej7/4IuJ9S26/BV92N2+Q0EDdtNc9rLMlJTiYPpVAeCvyNYhmpbpkfCoYsWUfzJdVXF7FQ94AUuzlaPyHTNX+4KQlsbvfI2GFZV2aFTNz21hXr+qRecMhdKU9JZU8x+kuU3yIew+9DAP5z7FeUUAyU5+nj95o8cysn7b86pLidC9oOtQ0xffHIoyxKj5oXbYAaAJ6OQiPaLLEt3jQN7Y6RmINWRoBHMs/TATogPASHPw7ClBIVhtcFA+T6gvoQgAaDkkBGxB+fK6LiVO/DGs0hUHku6kOfiIyIV9efpd1qdh5svKfciip+jLOQU3MN0JVnXqSEw5y1HqggG54vG8laJzgBxCO2XfEhEXeEwRR3Cvtw== admin@iZ2zeetm9awnkwdni43joiZ" >> ~/.ssh/authorized_keys

# 设置权限
chmod 600 ~/.ssh/authorized_keys
```

### 环境变量

```bash
# 添加到 ~/.bashrc
export LOBSTER_ID=lobster-005
export LOBSTER_PORT=8005
export LOBSTER_HOME=~/lobster-network

# 使配置生效
source ~/.bashrc
```

---

## 测试验证

### 1. 健康检查

```bash
curl http://127.0.0.1:8005/health
```

预期输出：
```json
{"lobster_id":"lobster-005","status":"ok"}
```

### 2. 查看待办请求

```bash
curl http://127.0.0.1:8005/pending | python3 -m json.tool
```

### 3. 查看总体状态

```bash
curl http://127.0.0.1:8005/status | python3 -m json.tool
```

### 4. 测试协作

```bash
# 发送测试请求给调度中枢
curl -X POST http://127.0.0.1:8005/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-005","to":"lobster-001","msg":"测试协作","intent":"coordination"}'
```

### 5. 查看钉钉群

确认群里收到消息：
> [LOBSTER-MSG] from=lobster-005&to=lobster-001&intent=coordination&msg=测试协作

### 6. 完整测试流程

```bash
# 1. 检查进程
ps aux | grep wrapper.py

# 2. 检查端口
netstat -tlnp | grep 8005

# 3. 检查日志
tail -f ~/lobster-tasks/logs/lobster-005.log

# 4. 检查请求队列
cat ~/lobster-tasks/pending/requests.json | python3 -m json.tool
```

---

## 管理命令

### 服务管理

```bash
# 启动服务
~/lobster-network/start.sh

# 停止服务
~/lobster-network/stop.sh

# 重启服务
~/lobster-network/restart.sh

# 查看状态
~/lobster-network/status.sh
```

### systemd 管理（推荐）

```bash
# 查看状态
sudo systemctl status lobster-wrapper@lobster-005.service

# 启动
sudo systemctl start lobster-wrapper@lobster-005.service

# 停止
sudo systemctl stop lobster-wrapper@lobster-005.service

# 重启
sudo systemctl restart lobster-wrapper@lobster-005.service

# 查看日志
sudo journalctl -u lobster-wrapper@lobster-005.service -f

# 设置开机自启
sudo systemctl enable lobster-wrapper@lobster-005.service
```

### 日志查看

```bash
# Wrapper 日志
tail -f ~/lobster-tasks/logs/lobster-005.log

# 请求队列
cat ~/lobster-tasks/pending/requests.json | python3 -m json.tool

# 响应记录
cat ~/lobster-tasks/done/responses.json | python3 -m json.tool
```

### 更新升级

```bash
# 下载最新版本
wget http://47.93.6.57:9000/lobster-network-skill.tar.gz

# 停止服务
~/lobster-network/stop.sh

# 解压更新
tar xzf lobster-network-skill.tar.gz -C ~/lobster-network/

# 重启服务
~/lobster-network/start.sh
```

---

## 常见问题

### Q1: 端口被占用

**问题**：安装时提示端口 8005 已被占用

**解决**：
```bash
# 检查端口占用
netstat -tlnp | grep 8005

# 使用其他端口
bash install-lobster-skill.sh --lobster-id=lobster-005 --port=8015
```

### Q2: Flask 未安装

**问题**：启动时提示 `ModuleNotFoundError: No module named 'flask'`

**解决**：
```bash
pip3 install flask requests --user
```

### Q3: 下载失败

**问题**：HTTP 下载技能包失败

**解决**：
```bash
# 检查网络连通性
curl http://47.93.6.57:9000/health

# 如果失败，联系管理员使用 SCP 方式传输
```

### Q4: 钉钉消息发送失败

**问题**：钉钉群没有收到消息

**解决**：
```bash
# 检查 access_token 和 secret 是否正确
cat ~/lobster-network/config.yaml | grep dingtalk

# 检查机器人是否还在群里
# 检查是否触发频率限制（每分钟 20 条）

# 查看日志
tail -f ~/lobster-tasks/logs/lobster-005.log | grep dingtalk
```

### Q5: systemd 服务启动失败

**问题**：`sudo systemctl start lobster-wrapper@lobster-005.service` 失败

**解决**：
```bash
# 查看错误日志
sudo journalctl -u lobster-wrapper@lobster-005.service -n 50

# 手动测试
python3 ~/lobster-network/wrapper.py --lobster-id=lobster-005 --port=8005

# 检查文件权限
ls -la ~/lobster-network/wrapper.py
chmod +x ~/lobster-network/wrapper.py
```

### Q6: SSH 连接被拒绝

**问题**：SSH 到龙虾节点服务器被拒绝

**解决**：
```bash
# 检查 SSH 配置
cat /etc/ssh/sshd_config | grep "PubkeyAuthentication"

# 确保 authorized_keys 权限正确
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# 重启 SSH 服务
sudo systemctl restart sshd
```

### Q7: 内存不足

**问题**：龙虾节点运行一段时间后内存不足

**解决**：
```bash
# 检查内存使用
free -h

# 清理缓存
sync; echo 3 > /proc/sys/vm/drop_caches

# 增加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 联系方式

### 钉钉群

- **群名称**：智能体小龙虾测试
- **群号**：178415004647
- **用途**：日常沟通、任务协调、问题反馈

### 管理员

| 角色 | 钉钉 ID | 职责 |
|------|---------|------|
| 项目架构师 | 诸葛斌 | 方向决策、战略规划 |
| 调度中枢 | 虾尔 (lobster-001) | 任务调度、技术支持、自动审批 |
| 文档维护 | 小陈 | 文档更新、培训 |

### GitHub

- **仓库**：https://github.com/zhugebin-hub/lobster-network
- **Issue**：提交问题和建议
- **PR**：贡献代码和文档

### 技术支持

- **紧急问题**：钉钉群 @虾尔
- **一般问题**：GitHub Issue
- **文档问题**：联系小陈

---

## 📚 附录

### A. 龙虾网络协议 (OADP)

| 文档 | 内容 |
|------|------|
| `spec/protocol.md` | OADP 核心协议：消息格式、对话流程、涌现计算、错误处理 |
| `spec/drp.md` | 对话渲染协议：7 步渲染流程、涌现检测算法、对话模板 |
| `spec/world-map.md` | 世界地图索引协议：地图结构、同步机制、冲突解决、权限控制 |
| `spec/soul_schema.md` | SOUL.md 灵魂种子格式规范：Markdown + JSON Schema |
| `spec/memory_schema.md` | MEMORY.md 记忆格式规范：与灵魂种子的区别与更新规则 |
| `spec/portal.md` | 传送门协议：结构、生命周期、知识传承链 |

### B. 龙虾节点状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 0 | 初始化 | 节点刚创建，未启动 |
| 1 | 运行中 | 节点正常运行 |
| 2 | 升级中 | 节点正在升级系统 |
| 3 | 维护中 | 节点正在维护 |
| 4 | 离线 | 节点离线，无法通信 |
| 5 | 已停止 | 节点已停止服务 |

### C. 龙虾间消息格式

```
[LOBSTER-MSG] from=lobster-001&to=lobster-002&intent=coordination&msg=请求内容
```

| 字段 | 说明 | 示例 |
|------|------|------|
| `from` | 源龙虾 ID | lobster-001 |
| `to` | 目标龙虾 ID | lobster-002 |
| `intent` | 意图类型 | general/coordination/query/response |
| `msg` | 消息内容 | 请求协作：请评估资源池 |

### D. 快速命令参考

```bash
# 健康检查
curl http://127.0.0.1:8005/health

# 发送请求
curl -X POST http://127.0.0.1:8005/invoke \
  -H "Content-Type: application/json" \
  -d '{"from":"lobster-005","to":"lobster-001","msg":"Hello","intent":"general"}'

# 查看待办
curl http://127.0.0.1:8005/pending | python3 -m json.tool

# 查看状态
curl http://127.0.0.1:8005/status | python3 -m json.tool

# 查看日志
tail -f ~/lobster-tasks/logs/lobster-005.log
```

---

## 🎉 欢迎加入龙虾网络！

**你不停对话，世界就不停扩展** 🦞⚡️

---

**文档版本**: v1.0  
**最后更新**: 2026-06-26  
**维护者**: 虾尔 (lobster-001)  
**反馈**: 钉钉群「智能体小龙虾测试」或 GitHub Issue
