# 附录 A：阿里云上小龙虾部署实战

---

## 附录说明

**编写者**：陈俊烨  
**单位**：浙江工商大学人工智能学院  
**日期**：2026 年 4 月  
**版本**：v1.0

本附录基于作者在阿里云平台的实际部署经验，补充第 8 章的云端部署方案，帮助读者在云服务器上部署和运行 OpenClaw（小龙虾）AI 助理。

---

## A.0 三层架构小龙虾：阿里云 + 百炼 + 钉钉

> 🦞 **小龙虾（OpenClaw）** 是一个开源 AI助手平台，它像一条灵活的"龙虾"，能钳住大模型的能力，通过多种渠道（钉钉、微信、Telegram 等）为用户提供 7×24 小时的智能服务。当小龙虾部署在阿里云上，并接入阿里云百炼大模型与钉钉通信平台时，就构成了一套完整的**企业级 AI助手解决方案**——我们称之为"三层架构小龙虾"。

### A.0.1 什么是三层架构小龙虾？

三层架构小龙虾将 AI助手的运行环境拆分为三个层次，每一层各司其职、独立演进，共同构成一个稳定、可扩展的 AI 服务系统：

```
┌─────────────────────────────────────────────────────────┐
│                    📱 用户层（交互层）                     │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │              钉钉（DingTalk）                      │   │
│   │   · 群聊机器人  · 私聊对话  · 工作通知  · 卡片消息  │   │
│   └──────────────────────┬──────────────────────────┘   │
│                          │ HTTPS 回调                    │
├──────────────────────────┼──────────────────────────────┤
│                    🧠 智能层（AI 层）                      │
│                                                         │
│   ┌──────────────────────┴──────────────────────────┐   │
│   │           OpenClaw 网关（小龙虾网关）              │   │
│   │   · 消息路由  · 技能调度  · 记忆管理  · 定时任务    │   │
│   └──────────────────────┬──────────────────────────┘   │
│                          │ DashScope API                 │
├──────────────────────────┼──────────────────────────────┤
│                    ☁️ 基础设施层（云资源层）                │
│                                                         │
│   ┌──────────────────────┴──────────────────────────┐   │
│   │        阿里云百炼（DashScope / 通义千问）           │   │
│   │   · qwen3.5-plus  · qwen3.5-max  · qwen-coder   │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │         阿里云 ECS（云服务器）                     │   │
│   │   · Ubuntu 22.04  · Node.js  · OpenClaw 运行时    │   │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### A.0.2 各层详解

#### 第一层：基础设施层 —— 阿里云 ECS + 百炼

**阿里云 ECS（Elastic Compute Service）** 是小龙虾的"家"。它提供了一台 7×24 小时不间断运行的云服务器，确保小龙虾随时在线。

| 配置项 | 推荐规格 | 说明 |
|--------|----------|------|
| CPU | 2-4 核 | 运行 Node.js 网关服务 |
| 内存 | 4-8 GB | 承载记忆文件与技能模块 |
| 存储 | 40-80 GB SSD | 存储日志、配置、记忆数据 |
| 带宽 | 3-5 Mbps | 保障消息实时收发 |
| 操作系统 | Ubuntu 22.04 LTS | 社区支持完善，文档丰富 |

**阿里云百炼（DashScope）** 是小龙虾的"大脑"。它是阿里云提供的大模型服务平台，内置通义千问（Qwen）系列模型，为小龙虾提供自然语言理解与生成能力。

| 模型 | 特点 | 适用场景 |
|------|------|----------|
| qwen3.5-plus | 性价比均衡，中文能力强 | 日常对话、通用任务 |
| qwen3.5-max | 推理能力最强 | 复杂分析、深度写作 |
| qwen-coder | 代码生成专精 | 编程辅助、代码审查 |
| qwen3.5-turbo | 响应速度最快，成本最低 | 简单问答、快速响应 |

> 💡 **为什么选择百炼？** 相比海外大模型 API，百炼具有三大优势：① **国内访问速度快**，无需翻墙，延迟低至 100ms 以内；② **中文理解能力强**，通义千问系列在中文 NLP  benchmarks 上表现优异；③ **价格亲民**，qwen3.5-plus 约 ¥0.01/千 tokens，学生用户还可享受专属优惠。

#### 第二层：智能层 —— OpenClaw 网关

**OpenClaw** 是小龙虾的"神经系统"，它运行在 ECS 服务器上，是整个架构的**核心调度中枢**。它不只是一个简单的 API 代理，而是一个功能完整的 AI助手平台：

**核心能力：**

- **🔄 多通道接入**：同时连接钉钉、微信、Telegram、Discord 等多个通信平台，一个大脑服务所有渠道
- **🧩 技能系统（Skills）**：通过插件化技能扩展能力，如天气查询、文件处理、语音识别、定时提醒等，按需安装
- **📝 记忆管理**：维护长期记忆（MEMORY.md）和每日笔记（memory/YYYY-MM-DD.md），让小龙虾"认识你"
- **⏰ 定时任务（Cron）**：支持定时汇报、周期性检查、自动提醒等自动化任务
- **🔀 模型路由**：支持多模型配置，可根据任务类型自动选择最合适的模型
- **🛡️ 安全沙箱**：敏感操作（如发送邮件、公网请求）需用户确认，防止误操作

**运行原理：**

```
用户消息 → 钉钉 → OpenClaw 网关 → 百炼大模型 → 生成回复 → 钉钉 → 用户
                │
                ├→ 加载记忆文件（了解用户背景）
                ├→ 加载技能模块（扩展能力）
                ├→ 执行工具调用（搜索、读文件等）
                └→ 更新记忆（记住重要信息）
```

#### 第三层：交互层 —— 钉钉

**钉钉（DingTalk）** 是小龙虾与用户之间的"桥梁"。作为国内领先的企业协同平台，钉钉为小龙虾提供了丰富的交互能力：

| 交互方式 | 说明 | 应用场景 |
|----------|------|----------|
| 群机器人 | 在群聊中以机器人身份参与讨论 | 团队知识问答、项目协作 |
| 单聊对话 | 用户与机器人一对一私聊 | 个人助手、隐私对话 |
| 工作通知 | 主动推送消息到用户钉钉 | 定时汇报、告警提醒 |
| 卡片消息 | 发送结构化卡片（含按钮、链接） | 审批流、数据展示 |

> 💡 **钉钉 + 小龙虾的化学反应**：钉钉提供了消息收发通道，OpenClaw 提供了 AI 大脑，两者结合后，用户只需在钉钉中发送一条消息，就能获得由大模型驱动的智能回复——无需安装额外 App，无需学习新界面。

### A.0.3 三层架构的优势

**1. 解耦设计，独立演进**

基础设施层、智能层、交互层相互独立，可以单独升级或替换：
- 想换模型？只需修改百炼模型配置，无需动服务器或钉钉
- 想加通道？只需在 OpenClaw 中启用新通道，无需改模型
- 想升级服务器？只需迁移 OpenClaw 配置，模型和通道不变

**2. 成本可控，按需付费**

| 层级 | 费用项 | 学生月成本（参考） |
|------|--------|---------------------|
| 基础设施层 | ECS 服务器 | ¥60-100（学生优惠后） |
| 智能层 | 百炼 API 调用 | ¥10-50（按实际用量） |
| 交互层 | 钉钉 | 免费 |
| **合计** | | **¥70-150/月** |

**3. 全中文生态，开箱即用**

- 百炼（通义千问）原生支持中文，无需额外翻译层
- 钉钉是国内最普及的办公平台，用户零学习成本
- OpenClaw 社区活跃，中文文档完善，问题响应快

**4. 适合教育与企业场景**

- **教育场景**：教师可部署班级助教小龙虾，自动答疑、作业提醒、知识讲解
- **企业场景**：IT 部门可部署运维助手，监控告警、工单处理、知识库检索
- **个人场景**：学生可部署个人 AI助手，日程管理、学习辅导、信息检索

### A.0.4 与教材的衔接关系

本教材以"从理论到实战、从本地到云端、从使用到开发"为主线，逐步引导读者掌握 AI助手的完整知识体系。附录 A 作为全书的收官之作，将前面各章的知识点融会贯通，呈现一个可投入生产环境的完整部署方案。

| 章节 | 内容概要 | 与附录 A 的衔接 |
|------|----------|----------------|
| **第 1 章** | 人工智能发展概述、大模型演化路径及 AI 助理的产业价值与应用场景，建立理论基础 | 附录 A 是第 1 章"AI 助理产业价值"的**最佳实践范本**——三层架构正是产业级 AI 助理的标准范式 |
| **第 2-3 章** | AI 助理基础能力篇，涵盖智能文档、数据处理、提示词定制等实用技能 | 附录 A 中的小龙虾已内置这些基础能力，读者可直接在钉钉对话中体验文档处理、数据分析等技能 |
| **第 4-5 章** | 面向典型办公生态与场景需求，如 PPT、脑图、视频、知识库、闪记等模块的自动化与协作化处理，展示 AI 在日常办公中的多维度赋能 | 附录 A 部署的小龙虾可通过技能系统扩展这些办公能力，实现钉钉内的**自动化办公流** |
| **第 6 章** | 全面讲解 AI 助理的定制开发路径，包括提示词设计、技能扩展、知识库构建与市场发布，并结合综合案例进行实战演练 | 附录 A 是第 6 章定制开发成果的**云端发布与运行环境**——定制好的助理部署到阿里云即可面向企业用户提供服务 |
| **第 7-8 章** | 应用开发与案例实战篇，提供连连看小游戏、调查问卷系统、DeepSeek 客服系统、旅客提交流程、AI 卡片生成与消息推送、工作流与宜搭表单集成等项目开发流程，覆盖从 0 代码到完整系统搭建的全过程 | 附录 A 是第 7-8 章所有实战项目的**统一运行平台**——这些项目均可作为小龙虾的技能或子应用，部署在三层架构上对外提供服务 |

**从"学"到"用"的最后一公里：** 教材前 8 章帮助读者掌握 AI 助理的理论基础、使用技能和开发方法，而附录 A 则回答了最后一个关键问题——**"我开发好的 AI 助理，如何部署到云端，让企业里的每个人都能用？"** 答案就是三层架构小龙虾：将定制好的 OpenClaw 实例部署到阿里云 ECS，接入百炼大模型作为 AI 引擎，通过钉钉通道触达企业用户，形成从开发到交付的完整闭环。

---

---

## A.1 为什么选择云端部署？

### A.1.1 云端部署 vs 本地部署

| 对比维度 | 本地部署 | 云端部署 |
|----------|----------|----------|
| 硬件成本 | 需自备高性能电脑 | 按需付费，弹性伸缩 |
| 运行时间 | 依赖本地设备开机 | 7×24 小时不间断 |
| 网络环境 | 依赖本地网络 | 数据中心高速网络 |
| 维护成本 | 自行维护 | 云平台托管 |
| 适用场景 | 学习测试、个人使用 | 生产环境、企业应用 |

### A.1.2 云端部署优势

- ✅ **7×24 小时在线**：无需担心设备关机
- ✅ **稳定网络环境**：数据中心级网络保障
- ✅ **弹性扩展**：根据需求随时升级配置
- ✅ **专业运维**：阿里云提供技术支持
- ✅ **成本可控**：按量付费，学生有优惠

---

## A.2 阿里云服务器选择指南

### A.2.1 推荐配置

| 配置项 | 入门版 | 推荐版 | 专业版 |
|--------|--------|--------|--------|
| CPU | 2 核 | 4 核 | 8 核 |
| 内存 | 4GB | 8GB | 16GB |
| 存储 | 40GB SSD | 80GB SSD | 160GB SSD |
| 带宽 | 3Mbps | 5Mbps | 10Mbps |
| 月费用（预估） | ¥60-100 | ¥150-200 | ¥300-500 |

### A.2.2 学生优惠

阿里云为在校大学生提供专属优惠：

- **云翼计划**：9.9 元/月起（2 核 2G）
- **高校计划**：免费试用 3 个月
- **开发者计划**：首购 1 折起

**申请方式**：
1. 访问 https://www.aliyun.com/campus
2. 完成学生认证（学信网验证）
3. 选择适合的云服务器套餐

### A.2.3 服务器地域选择

**推荐地域**：
- 华东 1（杭州）：距离近，延迟低
- 华东 2（上海）：网络稳定
- 华北 2（北京）：覆盖北方用户

**选择建议**：优先选择离你所在地区最近的数据中心。

---

## A.3 云服务器 ECS 购买与配置

### A.3.1 创建 ECS 实例

**步骤 1：登录阿里云控制台**

1. 访问 https://ecs.console.aliyun.com
2. 使用阿里云账号登录

**步骤 2：创建实例**

1. 点击"创建实例"
2. 选择计费方式（推荐"按量付费"，可随时释放）
3. 选择地域（建议：华东 1-杭州）

**步骤 3：选择实例规格**

1. 选择"共享型"或"计算型"
2. 推荐配置：2 核 4GB（入门学习）
3. 点击"下一步"

**步骤 4：选择镜像**

1. 选择"公共镜像"
2. 操作系统：Ubuntu 22.04 LTS（推荐）或 CentOS 7.9
3. 点击"下一步"

**步骤 5：配置存储**

1. 系统盘：40GB ESSD（默认）
2. 如需更多空间，可添加数据盘
3. 点击"下一步"

**步骤 6：网络配置**

1. 选择默认 VPC 和交换机
2. 分配公网 IPv4 地址（必需）
3. 带宽：3-5Mbps（根据需求）
4. 点击"下一步"

**步骤 7：安全组配置**

**开放以下端口**：
- ✅ 22（SSH 远程连接）
- ✅ 80（HTTP）
- ✅ 443（HTTPS）
- ✅ 8080（OpenClaw Web 界面）
- ✅ 3000（可选，其他服务）

**步骤 8：设置登录凭证**

1. 选择"自定义密码"
2. 设置 root 登录密码（请妥善保存）
3. 点击"确认订单"

**步骤 9：完成创建**

1. 确认配置和费用
2. 点击"创建实例"
3. 等待 1-3 分钟，实例创建完成

---

## A.4 连接云服务器

### A.4.1 使用 SSH 连接（Windows）

**方法 1：使用 PowerShell**

```powershell
# 替换为你的服务器公网 IP
ssh root@你的服务器 IP 地址

# 输入密码（输入时不显示）
# 成功登录后显示欢迎信息
```

**方法 2：使用 PuTTY**

1. 下载 PuTTY：https://www.putty.org
2. 打开 PuTTY
3. Host Name：输入服务器公网 IP
4. Port：22
5. Connection type：SSH
6. 点击"Open"
7. 输入用户名：root
8. 输入密码

### A.4.2 使用 SSH 连接（macOS/Linux）

```bash
# 打开终端
# 连接服务器
ssh root@你的服务器 IP 地址

# 首次连接会提示确认指纹，输入 yes
# 输入密码（输入时不显示）

# 成功登录后，命令行提示符变为 root@hostname:~#
```

### A.4.3 使用阿里云 Workbench（推荐新手）

1. 登录阿里云控制台
2. 进入 ECS 实例列表
3. 找到你的实例，点击"远程连接"
4. 选择"Workbench 远程连接"
5. 点击"发送验证码"
6. 输入手机验证码
7. 成功连接

---

## A.5 服务器环境配置

### A.5.1 更新系统软件

```bash
# 更新软件包列表
sudo apt update

# 升级已安装的软件
sudo apt upgrade -y

# 安装常用工具
sudo apt install -y curl git wget vim htop
```

### A.5.2 安装 Docker

```bash
# 下载 Docker 安装脚本
curl -fsSL https://get.docker.com -o get-docker.sh

# 执行安装脚本
sudo sh get-docker.sh

# 将当前用户添加到 docker 组（避免每次使用 sudo）
sudo usermod -aG docker $USER

# 退出并重新登录使组变更生效
exit
# 重新 SSH 连接

# 验证 Docker 安装
docker --version
docker run hello-world
```

### A.5.3 安装 Docker Compose

```bash
# 下载 Docker Compose（替换版本号）
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### A.5.4 安装 Node.js（可选）

```bash
# 使用 NodeSource 安装 Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version
npm --version
```

---

## A.6 部署 OpenClaw（小龙虾）

### A.6.1 创建 OpenClaw 工作目录

```bash
# 创建目录
mkdir -p ~/openclaw
cd ~/openclaw

# 创建配置文件目录
mkdir -p config skills memory
```

### A.6.2 获取 OpenClaw

**方法 1：使用 Git 克隆（推荐）**

```bash
# 克隆官方仓库
git clone https://github.com/openclaw/openclaw.git .

# 或者克隆国内镜像（速度更快）
git clone https://gitee.com/openclaw/openclaw.git .
```

**方法 2：下载安装包**

```bash
# 下载最新 release
wget https://github.com/openclaw/openclaw/releases/latest/download/openclaw-linux-amd64.tar.gz

# 解压
tar -xzf openclaw-linux-amd64.tar.gz
```

### A.6.3 配置 OpenClaw

```bash
# 编辑配置文件
vim config/openclaw.yaml

# 或使用 nano（更友好）
nano config/openclaw.yaml
```

**配置文件示例**：

```yaml
# OpenClaw 配置文件

# 阿里云百炼 API 配置
aliyun:
  api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxx"  # 替换为你的 API-KEY
  model: "qwen-max"  # 或 qwen-plus, qwen-turbo

# 钉钉机器人配置
dingtalk:
  client_id: "ding_xxxxxxxxxxxxx"
  client_secret: "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  webhook: "https://oapi.dingtalk.com/robot/send?access_token=xxxxx"

# 服务配置
server:
  host: "0.0.0.0"  # 监听所有网络接口
  port: 8080
  
# 记忆配置
memory:
  enabled: true
  path: "./memory"
  
# 日志配置
logging:
  level: "info"  # debug, info, warn, error
  file: "./logs/openclaw.log"
```

### A.6.4 启动 OpenClaw

**使用 Docker 启动（推荐）**

```bash
# 构建并启动
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

**直接启动**

```bash
# 如果使用二进制文件
./openclaw gateway start

# 查看状态
./openclaw status

# 查看日志
./openclaw logs
```

### A.6.5 验证部署

```bash
# 检查服务是否运行
curl http://localhost:8080/api/health

# 应该返回类似：
# {"status": "ok", "version": "1.0.0"}
```

**访问 Web 界面**：

在浏览器中访问：`http://你的服务器 IP 地址:8080`

---

## A.7 配置防火墙与安全组

### A.7.1 配置阿里云安全组

1. 登录阿里云控制台
2. 进入 ECS 实例详情页
3. 点击"安全组"标签
4. 点击"配置规则"
5. 添加入方向规则：

| 端口范围 | 授权对象 | 描述 |
|----------|----------|------|
| 8080/8080 | 0.0.0.0/0 | OpenClaw Web 界面 |
| 22/22 | 0.0.0.0/0 | SSH 连接 |

### A.7.2 配置 Ubuntu 防火墙（UFW）

```bash
# 启用 UFW
sudo ufw enable

# 允许 SSH
sudo ufw allow 22/tcp

# 允许 OpenClaw Web 界面
sudo ufw allow 8080/tcp

# 允许 HTTP/HTTPS（可选）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 查看状态
sudo ufw status
```

---

## A.8 域名与 HTTPS 配置（可选）

### A.8.1 绑定域名

1. 在域名服务商处添加 A 记录
2. 主机记录：`lobster` 或 `@`
3. 记录值：你的服务器公网 IP
4. TTL：默认

### A.8.2 使用 Nginx 反向代理

```bash
# 安装 Nginx
sudo apt install -y nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/openclaw
```

**Nginx 配置示例**：

```nginx
server {
    listen 80;
    server_name lobster.yourdomain.com;  # 替换为你的域名

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### A.8.3 配置 HTTPS（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d lobster.yourdomain.com

# 按提示输入邮箱，同意条款

# 自动续期测试
sudo certbot renew --dry-run
```

---

## A.9 日常运维与监控

### A.9.1 查看服务状态

```bash
# Docker 方式
docker-compose ps
docker-compose logs -f

# 系统服务方式
systemctl status openclaw

# 查看资源占用
htop
docker stats
```

### A.9.2 日志管理

```bash
# 查看实时日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 导出日志到文件
docker-compose logs > openclaw.log

# 清理旧日志
docker-compose logs --tail=50 > openclaw.log.new
mv openclaw.log.new openclaw.log
```

### A.9.3 备份与恢复

**备份配置文件**：

```bash
# 创建备份目录
mkdir -p ~/backups

# 备份配置
tar -czf ~/backups/openclaw-config-$(date +%Y%m%d).tar.gz ~/openclaw/config
```

**备份记忆文件**：

```bash
# 备份记忆
tar -czf ~/backups/openclaw-memory-$(date +%Y%m%d).tar.gz ~/openclaw/memory
```

**恢复配置**：

```bash
# 解压备份
tar -xzf ~/backups/openclaw-config-20260420.tar.gz -C ~/
```

### A.9.4 更新 OpenClaw

```bash
# 进入目录
cd ~/openclaw

# 拉取最新代码
git pull origin main

# 重新构建并重启
docker-compose down
docker-compose up -d --build

# 查看新版本
./openclaw version
```

---

## A.10 常见问题与解决方案

### A.10.1 无法 SSH 连接

**问题**：SSH 连接超时或拒绝

**解决方案**：
1. 检查安全组是否开放 22 端口
2. 检查服务器是否运行中
3. 确认公网 IP 地址正确
4. 检查本地防火墙设置

### A.10.2 Docker 容器无法启动

**问题**：`docker-compose up` 报错

**解决方案**：
```bash
# 查看详细错误
docker-compose logs

# 检查 Docker 状态
systemctl status docker

# 重启 Docker
sudo systemctl restart docker

# 重新构建
docker-compose down
docker-compose up -d --build
```

### A.10.3 内存不足

**问题**：服务器内存不足，服务崩溃

**解决方案**：
1. 升级服务器配置（推荐）
2. 添加 Swap 交换空间：

```bash
# 创建 4GB Swap 文件
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### A.10.4 钉钉机器人无法接收消息

**问题**：钉钉机器人不响应

**解决方案**：
1. 检查 Client ID 和 Client Secret 是否正确
2. 确认钉钉应用已发布
3. 检查安全组是否开放相应端口
4. 查看 OpenClaw 日志排查错误

### A.10.5 API 调用失败

**问题**：阿里云百炼 API 调用失败

**解决方案**：
1. 检查 API-KEY 是否正确
2. 确认账户余额充足
3. 检查网络连接
4. 查看阿里云控制台是否有服务告警

---

## A.11 成本优化建议

### A.11.1 选择合适的计费方式

- **按量付费**：适合测试、短期使用
- **包年包月**：适合长期运行，价格更优惠
- **抢占式实例**：价格最低，但可能被回收（适合无状态服务）

### A.11.2 使用学生优惠

- 完成学生认证，享受云翼计划优惠
- 关注阿里云校园活动，经常有免费额度
- 加入阿里云开发者社区，获取代金券

### A.11.3 资源优化

- 根据实际负载调整配置
- 非高峰期可降低配置
- 使用自动伸缩（进阶）

---

## A.12 安全最佳实践

### A.12.1 SSH 安全

```bash
# 禁用 root 密码登录，改用密钥
sudo nano /etc/ssh/sshd_config

# 修改以下配置：
# PermitRootLogin prohibit-password
# PasswordAuthentication no

# 重启 SSH 服务
sudo systemctl restart sshd
```

### A.12.2 定期更新

```bash
# 每周更新系统
sudo apt update && sudo apt upgrade -y

# 定期更新 Docker 镜像
docker-compose pull
docker-compose up -d
```

### A.12.3 备份策略

- 每日备份配置文件
- 每周备份记忆文件
- 每月完整备份到本地

---

## A.13 附录小结

通过本附录的学习，你应该能够：

- ✅ 选择合适的阿里云服务器配置
- ✅ 完成 ECS 实例的购买和配置
- ✅ 使用 SSH 连接云服务器
- ✅ 部署和配置 OpenClaw（小龙虾）
- ✅ 配置域名和 HTTPS（可选）
- ✅ 进行日常运维和故障排查
- ✅ 优化成本并确保安全

---

## A.14 延伸阅读

- [阿里云 ECS 官方文档](https://help.aliyun.com/product/25362.html)
- [Docker 官方文档](https://docs.docker.com/)
- [OpenClaw 部署指南](https://github.com/openclaw/openclaw)
- [Nginx 配置指南](https://nginx.org/en/docs/)
- [Let's Encrypt 证书配置](https://letsencrypt.org/)

---

## 关于作者

**陈俊烨**

浙江工商大学人工智能学院硕士研究生，软件工程专业背景。

**主要经历**：
- 信电学院"未来课堂"智能体开发者
- 多个校园服务小龙虾开发者（会议室预约、智慧就业、图书管理）
- 2026 年阿里小龙虾大会"黑客松勇士"
- 多项 AI 黑客松竞赛获奖者（GDPS Astron 一等奖、商汤龙虾节二等奖等）

**技术方向**：AI 应用开发、教育数字化、全栈开发

**联系方式**：
- 个人网站：https://cjy-websites.zeabur.app
- 邮箱：[待补充]

---

*附录 A 完*

*编写日期：2026 年 4 月*  
*版本：v1.0*
