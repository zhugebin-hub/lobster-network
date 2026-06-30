# 🦞 会议室预约虾 - 多平台一键部署指南

**版本**: v1.0
**更新日期**: 2026-03-28
**支持平台**: 钉钉、飞书、企业微信、QQ 机器人

---

## 📊 平台对比

| 平台 | 适用场景 | 部署难度 | 审核时间 |
|------|---------|---------|---------|
| **钉钉** | 企业内部 | ⭐⭐ | 无需审核 |
| **飞书** | 企业/团队 | ⭐⭐ | 无需审核 |
| **企业微信** | 企业内部 | ⭐⭐⭐ | 无需审核 |
| **QQ 机器人** | 学生群体 | ⭐⭐⭐⭐ | 1-3 天 |

---

## 🚀 快速开始

### 方式一：交互式部署

```bash
# 钉钉（已配置）
node scripts/deploy-dingtalk.js

# 飞书
node scripts/deploy-feishu.js

# 企业微信
node scripts/deploy-wecom.js

# QQ 机器人
node scripts/deploy-qqbot.js
```

### 方式二：配置文件部署

```bash
# 1. 创建配置文件
mkdir -p config

# 2. 复制配置模板
cp config/dingtalk.env.example config/feishu.env
cp config/dingtalk.env.example config/wecom.env
cp config/dingtalk.env.example config/qqbot.env

# 3. 编辑配置文件
vim config/feishu.env
vim config/wecom.env
vim config/qqbot.env

# 4. 启动对应服务
node adapters/feishu-bot.js
node adapters/wecom-bot.js
node adapters/qqbot-bot.js
```

---

## 📋 平台部署详解

### 1. 钉钉（已就绪）✅

**配置文件**: `config/dingtalk.env`
**适配器**: `adapters/dingtalk-bot.js`
**端口**: 3000

**部署步骤**:
```bash
# 已在 OpenClaw 中集成
# 直接使用钉钉机器人即可
```

**使用示例**:
```
@会议室预约虾 给我预约周三下午的 10 人会议室
```

---

### 2. 飞书 🆕

**配置文件**: `config/feishu.env`
**适配器**: `adapters/feishu-bot.js`
**端口**: 3000

**部署步骤**:

1. **创建飞书应用**
   - 访问 https://open.feishu.cn/app
   - 创建企业自建应用
   - 获取 App ID 和 App Secret

2. **配置机器人**
   - 添加"机器人"能力
   - 获取 Webhook 地址
   - 配置事件订阅

3. **运行部署脚本**
   ```bash
   node scripts/deploy-feishu.js
   ```

4. **启动服务**
   ```bash
   node adapters/feishu-bot.js
   ```

5. **配置回调 URL**
   - http://your-domain.com:3000/feishu/webhook

---

### 3. 企业微信 🆕

**配置文件**: `config/wecom.env`
**适配器**: `adapters/wecom-bot.js`
**端口**: 3001

**部署步骤**:

1. **创建企业微信应用**
   - 访问 https://work.weixin.qq.com/wework_admin
   - 创建应用
   - 获取 Corp ID、Agent ID、Secret

2. **配置接收消息**
   - 配置"接收消息"服务器
   - 获取 Token 和 EncodingAESKey

3. **运行部署脚本**
   ```bash
   node scripts/deploy-wecom.js
   ```

4. **启动服务**
   ```bash
   node adapters/wecom-bot.js
   ```

5. **配置回调地址**
   - http://your-domain.com:3001/wecom/webhook

---

### 4. QQ 机器人 🆕

**配置文件**: `config/qqbot.env`
**适配器**: `adapters/qqbot-bot.js`
**端口**: 3002

**部署步骤**:

1. **创建 QQ 机器人**
   - 访问 https://bot.q.qq.com/open
   - 创建机器人
   - 获取 Bot ID、Bot Secret、Bot Token

2. **配置机器人功能**
   - 开启消息接收权限
   - 设置回调 URL

3. **运行部署脚本**
   ```bash
   node scripts/deploy-qqbot.js
   ```

4. **启动服务**
   ```bash
   node adapters/qqbot-bot.js
   ```

5. **配置回调地址**
   - http://your-domain.com:3002/qqbot/webhook

6. **提交审核**
   - 等待 1-3 天审核通过
   - 邀请到 QQ 群

---

## 🔧 统一启动脚本

创建 `start-all-bots.sh`:

```bash
#!/bin/bash

echo "🦞 启动所有平台机器人..."

# 钉钉
if [ -f config/dingtalk.env ]; then
  echo "✅ 启动钉钉机器人..."
  node adapters/dingtalk-bot.js &
fi

# 飞书
if [ -f config/feishu.env ]; then
  echo "✅ 启动飞书机器人..."
  node adapters/feishu-bot.js &
fi

# 企业微信
if [ -f config/wecom.env ]; then
  echo "✅ 启动企业微信机器人..."
  node adapters/wecom-bot.js &
fi

# QQ 机器人
if [ -f config/qqbot.env ]; then
  echo "✅ 启动 QQ 机器人..."
  node adapters/qqbot-bot.js &
fi

echo "✅ 所有机器人已启动！"
echo "📌 使用 'killall node' 停止所有服务"
```

---

## 📊 多平台消息格式

### 钉钉
```markdown
🦞 会议室预约虾

✅ 预约成功！
预约号：BK1774667886046
房间：信电小型会议室 412
时间：2026-04-01 14:00-18:00
```

### 飞书（卡片消息）
```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": "🦞 会议室预约虾"
    },
    "elements": [
      {
        "tag": "markdown",
        "content": "✅ 预约成功！..."
      }
    ]
  }
}
```

### 企业微信（文本卡片）
```json
{
  "msgtype": "textcard",
  "textcard": {
    "title": "🦞 会议室预约虾",
    "description": "✅ 预约成功！...",
    "url": "https://example.com"
  }
}
```

### QQ（文本消息）
```
🦞 会议室预约虾

✅ 预约成功！
预约号：BK1774667886046
房间：信电小型会议室 412
时间：2026-04-01 14:00-18:00
```

---

## 🎯 比赛加分项

### 多平台支持优势

| 评审维度 | 加分点 |
|----------|--------|
| **技术实现** | 4 个平台适配器，展示技术实力 |
| **完成度** | 一键部署脚本，降低使用门槛 |
| **商业价值** | 支持多平台，扩大市场覆盖 |
| **用户体验** | 用户可在熟悉平台使用 |

### 演示建议

```bash
# 演示多平台部署能力
echo "1. 钉钉部署（已就绪）"
echo "2. 飞书部署（演示交互式配置）"
echo "3. 企业微信部署（演示配置文件）"
echo "4. QQ 机器人部署（演示沙箱环境）"

# 展示统一代码库
echo "一套代码，四平台运行！"
```

---

## 📦 文件结构

```
skills/competition-package/
├── scripts/
│   ├── deploy-dingtalk.js      # 钉钉部署（已有）
│   ├── deploy-feishu.js        # 飞书部署 ⭐
│   ├── deploy-wecom.js         # 企业微信部署 ⭐
│   └── deploy-qqbot.js         # QQ 机器人部署 ⭐
├── adapters/
│   ├── dingtalk-bot.js         # 钉钉适配器
│   ├── feishu-bot.js           # 飞书适配器 ⭐
│   ├── wecom-bot.js            # 企业微信适配器 ⭐
│   └── qqbot-bot.js            # QQ 机器人适配器 ⭐
├── config/
│   ├── dingtalk.env            # 钉钉配置
│   ├── feishu.env              # 飞书配置 ⭐
│   ├── wecom.env               # 企业微信配置 ⭐
│   └── qqbot.env               # QQ 配置 ⭐
└── docs/
    └── multi-platform-deploy.md # 本文件
```

---

## ✅ 部署检查清单

### 钉钉
- [x] OpenClaw 集成
- [x] 配置文件就绪
- [x] 适配器已开发

### 飞书
- [ ] 创建飞书应用
- [ ] 获取 App ID/Secret
- [ ] 运行 deploy-feishu.js
- [ ] 启动服务
- [ ] 配置回调 URL

### 企业微信
- [ ] 创建企业微信应用
- [ ] 获取 Corp ID/Agent ID/Secret
- [ ] 运行 deploy-wecom.js
- [ ] 启动服务
- [ ] 配置回调地址

### QQ 机器人
- [ ] 创建 QQ 机器人
- [ ] 获取 Bot ID/Secret/Token
- [ ] 运行 deploy-qqbot.js
- [ ] 启动服务
- [ ] 配置回调 URL
- [ ] 提交审核

---

*多平台部署指南版本：v1.0*
*创建日期：2026-03-28*
*团队：陈俊烨 + AI 助手 信电大虾 🦞⚡️*

**🎯 一套代码，四平台运行！比赛加分！**
