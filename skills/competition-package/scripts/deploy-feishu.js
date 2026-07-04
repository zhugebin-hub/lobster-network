#!/usr/bin/env node

/**
 * 飞书机器人一键部署脚本
 * 用途：快速部署会议室预约虾到飞书平台
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
const FEISHU_CONFIG_TEMPLATE = `
# 飞书机器人配置
FEISHU_APP_ID=\${FEISHU_APP_ID}
FEISHU_APP_SECRET=\${FEISHU_APP_SECRET}
FEISHU_BOT_WEBHOOK=\${FEISHU_BOT_WEBHOOK}
FEISHU_ENCRYPT_KEY=\${FEISHU_ENCRYPT_KEY:-}

# 会议室预约虾配置
DATA_SOURCE=local
BOOKINGS_FILE=./data/bookings.json
MEETING_ROOMS_FILE=./data/meeting-rooms.json

# 通知配置
ENABLE_REMINDER=true
REMINDER_24H=true
REMINDER_1H=true
`;

// 飞书适配器代码
const FEISHU_ADAPTER_CODE = `#!/usr/bin/env node

/**
 * 飞书机器人适配器
 * 用途：将会议室预约虾接入飞书平台
 */

const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();
app.use(express.json());

const config = {
  appId: process.env.FEISHU_APP_ID,
  appSecret: process.env.FEISHU_APP_SECRET,
  botWebhook: process.env.FEISHU_BOT_WEBHOOK,
  encryptKey: process.env.FEISHU_ENCRYPT_KEY
};

// 验证飞书回调
function verifySignature(timestamp, nonce, signature) {
  const arr = [config.encryptKey, timestamp, nonce];
  arr.sort();
  const str = arr.join('');
  const hash = crypto.createHash('sha256');
  hash.update(str);
  return hash.digest('base64') === signature;
}

// 发送飞书消息
async function sendFeishuMessage(webhook, content) {
  try {
    await axios.post(webhook, {
      msg_type: 'interactive',
      card: {
        config: {
          wide_screen_mode: true
        },
        header: {
          template: 'blue',
          title: {
            tag: 'plain_text',
            content: '🦞 会议室预约虾'
          }
        },
        elements: content
      }
    });
    console.log('✅ 飞书消息发送成功');
  } catch (error) {
    console.error('❌ 飞书消息发送失败:', error.message);
  }
}

// 处理飞书消息
app.post('/feishu/webhook', async (req, res) => {
  const { challenge, header, event } = req.body;
  
  // 验证回调
  if (challenge) {
    res.send({ challenge });
    return;
  }
  
  // 处理消息
  if (event && event.message) {
    const message = event.message.content.text;
    const userId = event.sender.user_id;
    
    console.log('📝 收到飞书消息:', message);
    
    // 调用会议室预约脚本
    const { execSync } = require('child_process');
    try {
      const result = execSync(\`node scripts/book-meeting-room-v2.js "\${message}"\`, {
        encoding: 'utf-8',
        cwd: __dirname
      });
      
      // 发送结果到飞书
      await sendFeishuMessage(config.botWebhook, [
        {
          tag: 'markdown',
          content: result
        }
      ]);
    } catch (error) {
      await sendFeishuMessage(config.botWebhook, [
        {
          tag: 'markdown',
          content: '❌ 预约失败：' + error.message
        }
      ]);
    }
  }
  
  res.send({ success: true });
});

// 启动服务
const PORT = process.env.FEISHU_PORT || 3000;
app.listen(PORT, () => {
  console.log('🦞 飞书机器人已启动，端口:', PORT);
  console.log('📡 Webhook URL: http://localhost:' + PORT + '/feishu/webhook');
});
`;

// 安装依赖
function installDependencies() {
  console.log('📦 安装飞书依赖...\n');
  try {
    execSync('npm install express axios crypto --save', {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('✅ 依赖安装完成\n');
  } catch (error) {
    console.error('❌ 依赖安装失败:', error.message);
  }
}

// 创建配置文件
function createConfigFile(appId, appSecret, webhook, encryptKey) {
  const configPath = path.join(__dirname, '../config/feishu.env');
  const configDir = path.dirname(configPath);
  
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  const config = FEISHU_CONFIG_TEMPLATE
    .replace('${FEISHU_APP_ID}', appId)
    .replace('${FEISHU_APP_SECRET}', appSecret)
    .replace('${FEISHU_BOT_WEBHOOK}', webhook)
    .replace('${FEISHU_ENCRYPT_KEY}', encryptKey || '');
  
  fs.writeFileSync(configPath, config, 'utf-8');
  console.log(`✅ 配置文件已创建：${configPath}\n`);
}

// 创建适配器脚本
function createAdapter() {
  const adapterPath = path.join(__dirname, '../adapters/feishu-bot.js');
  const adapterDir = path.dirname(adapterPath);
  
  if (!fs.existsSync(adapterDir)) {
    fs.mkdirSync(adapterDir, { recursive: true });
  }
  
  fs.writeFileSync(adapterPath, FEISHU_ADAPTER_CODE, 'utf-8');
  console.log(`✅ 飞书适配器已创建：${adapterPath}\n`);
}

// 创建部署文档
function createDeployGuide() {
  const guidePath = path.join(__dirname, '../docs/deploy-feishu-guide.md');
  
  const guide = `# 🦞 会议室预约虾 - 飞书机器人部署指南

## 快速部署

### 1. 创建飞书应用
1. 访问 https://open.feishu.cn/app
2. 点击"创建企业自建应用"
3. 填写应用名称：会议室预约虾
4. 获取 App ID 和 App Secret

### 2. 配置机器人
1. 进入应用管理后台
2. 添加"机器人"能力
3. 获取 Webhook 地址
4. 配置事件订阅（消息）

### 3. 运行部署脚本
\`\`\`bash
node scripts/deploy-feishu.js
\`\`\`

### 4. 启动服务
\`\`\`bash
node adapters/feishu-bot.js
\`\`\`

### 5. 配置回调地址
- 在飞书开放平台配置事件订阅 URL
- 格式：http://your-domain.com:3000/feishu/webhook

## 使用示例

在飞书群聊中@机器人：
- "给我预约周三下午的 10 人会议室"
- "查看我的预约"
- "取消预约 BK123"

## 功能特性

- ✅ 自然语言预约
- ✅ 智能推荐
- ✅ 预约确认卡片
- ✅ 定时提醒
- ✅ 预约管理

---
*部署指南版本：v1.0*
`;

  fs.writeFileSync(guidePath, guide, 'utf-8');
  console.log(`✅ 部署指南已创建：${guidePath}\n`);
}

// 主函数
async function main() {
  console.log('🦞 飞书机器人一键部署\n');
  console.log('='.repeat(60));
  
  console.log('\n📝 请输入飞书应用配置:\n');
  
  const appId = await new Promise(resolve => {
    rl.question('App ID: ', resolve);
  });
  
  const appSecret = await new Promise(resolve => {
    rl.question('App Secret: ', resolve);
  });
  
  const webhook = await new Promise(resolve => {
    rl.question('Bot Webhook: ', resolve);
  });
  
  const encryptKey = await new Promise(resolve => {
    rl.question('Encrypt Key (可选): ', resolve);
  });
  
  rl.close();
  
  console.log('\n🔧 开始部署...\n');
  
  // 安装依赖
  installDependencies();
  
  // 创建配置文件
  createConfigFile(appId, appSecret, webhook, encryptKey);
  
  // 创建适配器
  createAdapter();
  
  // 创建部署指南
  createDeployGuide();
  
  console.log('='.repeat(60));
  console.log('✅ 飞书机器人部署完成！\n');
  console.log('📌 下一步:\n');
  console.log('   1. 启动服务：node adapters/feishu-bot.js');
  console.log('   2. 在飞书开放平台配置回调 URL');
  console.log('   3. 邀请机器人到群聊');
  console.log('   4. 测试：@机器人 "预约会议室"\n');
}

main();
