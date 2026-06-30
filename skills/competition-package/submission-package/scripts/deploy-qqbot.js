#!/usr/bin/env node

/**
 * QQ 机器人一键部署脚本
 * 用途：快速部署会议室预约虾到 QQ 平台
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// 配置模板
const QQBOT_CONFIG_TEMPLATE = `
# QQ 机器人配置
QQBOT_BOT_ID=\${QQBOT_BOT_ID}
QQBOT_BOT_SECRET=\${QQBOT_BOT_SECRET}
QQBOT_BOT_TOKEN=\${QQBOT_BOT_TOKEN}
QQBOT_SANDBOX=\${QQBOT_SANDBOX:-false}

# 会议室预约虾配置
DATA_SOURCE=local
BOOKINGS_FILE=./data/bookings.json
MEETING_ROOMS_FILE=./data/meeting-rooms.json

# 通知配置
ENABLE_REMINDER=true
REMINDER_24H=true
REMINDER_1H=true
`;

// QQ 机器人适配器代码
const QQBOT_ADAPTER_CODE = `#!/usr/bin/env node

/**
 * QQ 机器人适配器
 * 用途：将会议室预约虾接入 QQ 平台
 */

const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const config = {
  botId: process.env.QQBOT_BOT_ID,
  botSecret: process.env.QQBOT_BOT_SECRET,
  botToken: process.env.QQBOT_BOT_TOKEN,
  sandbox: process.env.QQBOT_SANDBOX === 'true'
};

// QQ 机器人 API 基础 URL
const API_BASE = config.sandbox 
  ? 'https://sandbox.api.sgroup.qq.com'
  : 'https://api.sgroup.qq.com';

// 发送 QQ 消息
async function sendQQMessage(channelId, content) {
  try {
    await axios.post(
      \`\${API_BASE}/channels/\${channelId}/messages\`,
      {
        content: '🦞 会议室预约虾\\n\\n' + content,
        msg_type: 0
      },
      {
        headers: {
          'Authorization': 'Bot ' + config.botId + '.' + config.botToken,
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('✅ QQ 消息发送成功');
  } catch (error) {
    console.error('❌ QQ 消息发送失败:', error.message);
  }
}

// 处理 QQ 消息
app.post('/qqbot/webhook', async (req, res) => {
  const { id, channel_id, author, content } = req.body;
  
  // 忽略机器人自己的消息
  if (author.bot) {
    res.send({ success: true });
    return;
  }
  
  if (content) {
    const message = content;
    const userId = author.id;
    
    console.log('📝 收到 QQ 消息:', message);
    
    // 调用会议室预约脚本
    const { execSync } = require('child_process');
    try {
      const result = execSync(\`node scripts/book-meeting-room-v2.js "\${message}"\`, {
        encoding: 'utf-8',
        cwd: __dirname
      });
      
      // 发送结果到 QQ
      await sendQQMessage(channel_id, result);
    } catch (error) {
      await sendQQMessage(channel_id, '❌ 预约失败：' + error.message);
    }
  }
  
  res.send({ success: true });
});

// 启动服务
const PORT = process.env.QQBOT_PORT || 3002;
app.listen(PORT, () => {
  console.log('🦞 QQ 机器人已启动，端口:', PORT);
  console.log('📡 Webhook URL: http://localhost:' + PORT + '/qqbot/webhook');
});
`;

// 安装依赖
function installDependencies() {
  console.log('📦 安装 QQ 机器人依赖...\n');
  try {
    execSync('npm install express axios --save', {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('✅ 依赖安装完成\n');
  } catch (error) {
    console.error('❌ 依赖安装失败:', error.message);
  }
}

// 创建配置文件
function createConfigFile(botId, botSecret, botToken, sandbox) {
  const configPath = path.join(__dirname, '../config/qqbot.env');
  const configDir = path.dirname(configPath);
  
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  const config = QQBOT_CONFIG_TEMPLATE
    .replace('${QQBOT_BOT_ID}', botId)
    .replace('${QQBOT_BOT_SECRET}', botSecret)
    .replace('${QQBOT_BOT_TOKEN}', botToken)
    .replace('${QQBOT_SANDBOX}', sandbox || 'false');
  
  fs.writeFileSync(configPath, config, 'utf-8');
  console.log(`✅ 配置文件已创建：${configPath}\n`);
}

// 创建适配器脚本
function createAdapter() {
  const adapterPath = path.join(__dirname, '../adapters/qqbot-bot.js');
  const adapterDir = path.dirname(adapterPath);
  
  if (!fs.existsSync(adapterDir)) {
    fs.mkdirSync(adapterDir, { recursive: true });
  }
  
  fs.writeFileSync(adapterPath, QQBOT_ADAPTER_CODE, 'utf-8');
  console.log(`✅ QQ 机器人适配器已创建：${adapterPath}\n`);
}

// 创建部署文档
function createDeployGuide() {
  const guidePath = path.join(__dirname, '../docs/deploy-qqbot-guide.md');
  
  const guide = `# 🦞 会议室预约虾 - QQ 机器人部署指南

## 快速部署

### 1. 创建 QQ 机器人
1. 访问 https://bot.q.qq.com/open
2. 登录开发者账号
3. 点击"创建机器人"
4. 填写机器人信息：会议室预约虾
5. 获取 Bot ID、Bot Secret、Bot Token

### 2. 配置机器人
1. 进入机器人管理后台
2. 配置"机器人功能"
3. 开启消息接收权限
4. 设置回调 URL

### 3. 运行部署脚本
\`\`\`bash
node scripts/deploy-qqbot.js
\`\`\`

### 4. 启动服务
\`\`\`bash
node adapters/qqbot-bot.js
\`\`\`

### 5. 配置回调地址
- 在 QQ 机器人管理后台配置事件订阅 URL
- 格式：http://your-domain.com:3002/qqbot/webhook

### 6. 发布机器人
1. 提交机器人审核
2. 等待审核通过
3. 邀请机器人到 QQ 群

## 使用示例

在 QQ 群中@机器人：
- "给我预约周三下午的 10 人会议室"
- "查看我的预约"
- "取消预约 BK123"

## 功能特性

- ✅ 自然语言预约
- ✅ 智能推荐
- ✅ 群聊互动
- ✅ 定时提醒
- ✅ 预约管理

## 注意事项

- 沙箱环境：可用于测试
- 生产环境：需要审核通过
- 消息频率：避免频繁调用

---
*部署指南版本：v1.0*
`;

  fs.writeFileSync(guidePath, guide, 'utf-8');
  console.log(`✅ 部署指南已创建：${guidePath}\n`);
}

// 主函数
async function main() {
  console.log('🦞 QQ 机器人一键部署\n');
  console.log('='.repeat(60));
  
  console.log('\n📝 请输入 QQ 机器人配置:\n');
  
  const botId = await new Promise(resolve => {
    rl.question('Bot ID: ', resolve);
  });
  
  const botSecret = await new Promise(resolve => {
    rl.question('Bot Secret: ', resolve);
  });
  
  const botToken = await new Promise(resolve => {
    rl.question('Bot Token: ', resolve);
  });
  
  const sandbox = await new Promise(resolve => {
    rl.question('使用沙箱环境？(true/false): ', resolve);
  });
  
  rl.close();
  
  console.log('\n🔧 开始部署...\n');
  
  // 安装依赖
  installDependencies();
  
  // 创建配置文件
  createConfigFile(botId, botSecret, botToken, sandbox);
  
  // 创建适配器
  createAdapter();
  
  // 创建部署指南
  createDeployGuide();
  
  console.log('='.repeat(60));
  console.log('✅ QQ 机器人部署完成！\n');
  console.log('📌 下一步:\n');
  console.log('   1. 启动服务：node adapters/qqbot-bot.js');
  console.log('   2. 在 QQ 机器人管理后台配置回调 URL');
  console.log('   3. 提交机器人审核');
  console.log('   4. 审核通过后邀请到 QQ 群');
  console.log('   5. 测试：@机器人 "预约会议室"\n');
}

main();
