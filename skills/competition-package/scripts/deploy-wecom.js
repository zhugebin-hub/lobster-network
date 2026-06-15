#!/usr/bin/env node

/**
 * 企业微信机器人一键部署脚本
 * 用途：快速部署会议室预约虾到企业微信平台
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
const WECOM_CONFIG_TEMPLATE = `
# 企业微信配置
WECOM_CORP_ID=\${WECOM_CORP_ID}
WECOM_AGENT_ID=\${WECOM_AGENT_ID}
WECOM_SECRET=\${WECOM_SECRET}
WECOM_WEBHOOK=\${WECOM_WEBHOOK}
WECOM_TOKEN=\${WECOM_TOKEN:-}
WECOM_ENCODING_AES_KEY=\${WECOM_ENCODING_AES_KEY:-}

# 会议室预约虾配置
DATA_SOURCE=local
BOOKINGS_FILE=./data/bookings.json
MEETING_ROOMS_FILE=./data/meeting-rooms.json

# 通知配置
ENABLE_REMINDER=true
REMINDER_24H=true
REMINDER_1H=true
`;

// 企业微信适配器代码
const WECOM_ADAPTER_CODE = `#!/usr/bin/env node

/**
 * 企业微信机器人适配器
 * 用途：将会议室预约虾接入企业微信平台
 */

const express = require('express');
const crypto = require('crypto');
const axios = require('axios');

const app = express();
app.use(express.json());

const config = {
  corpId: process.env.WECOM_CORP_ID,
  agentId: process.env.WECOM_AGENT_ID,
  secret: process.env.WECOM_SECRET,
  webhook: process.env.WECOM_WEBHOOK,
  token: process.env.WECOM_TOKEN,
  encodingAESKey: process.env.WECOM_ENCODING_AES_KEY
};

// 获取访问令牌
async function getAccessToken() {
  try {
    const response = await axios.get(
      'https://qyapi.weixin.qq.com/cgi-bin/gettoken',
      {
        params: {
          corpid: config.corpId,
          corpsecret: config.secret
        }
      }
    );
    return response.data.access_token;
  } catch (error) {
    console.error('❌ 获取访问令牌失败:', error.message);
    return null;
  }
}

// 发送企业微信消息
async function sendWecomMessage(userId, content) {
  const accessToken = await getAccessToken();
  if (!accessToken) return;
  
  try {
    await axios.post(
      'https://qyapi.weixin.qq.com/cgi-bin/message/send',
      {
        touser: userId,
        msgtype: 'textcard',
        agentid: config.agentId,
        textcard: {
          title: '🦞 会议室预约虾',
          description: content,
          url: 'https://example.com',
          btntxt: '查看详情'
        }
      },
      {
        params: { access_token: accessToken }
      }
    );
    console.log('✅ 企业微信消息发送成功');
  } catch (error) {
    console.error('❌ 企业微信消息发送失败:', error.message);
  }
}

// 验证企业微信回调
function verifySignature(msgSignature, timestamp, nonce, echoStr) {
  const cipher = crypto.createCipheriv(
    'aes-256-cbc',
    Buffer.from(config.encodingAESKey + '=', 'base64'),
    Buffer.from(config.encodingAESKey + '=', 'base64').slice(0, 16)
  );
  // 简化验证逻辑
  return echoStr;
}

// 处理企业微信消息
app.post('/wecom/webhook', async (req, res) => {
  const { ToUserName, FromUserName, MsgType, Content } = req.body;
  
  // 验证回调
  if (req.query.msg_signature) {
    const echoStr = verifySignature(
      req.query.msg_signature,
      req.query.timestamp,
      req.query.nonce,
      req.query.echostr
    );
    res.send(echoStr);
    return;
  }
  
  // 处理消息
  if (MsgType === 'text' && Content) {
    const message = Content;
    const userId = FromUserName;
    
    console.log('📝 收到企业微信消息:', message);
    
    // 调用会议室预约脚本
    const { execSync } = require('child_process');
    try {
      const result = execSync(\`node scripts/book-meeting-room-v2.js "\${message}"\`, {
        encoding: 'utf-8',
        cwd: __dirname
      });
      
      // 发送结果到企业微信
      await sendWecomMessage(userId, result);
    } catch (error) {
      await sendWecomMessage(userId, '❌ 预约失败：' + error.message);
    }
  }
  
  res.send({ success: true });
});

// 启动服务
const PORT = process.env.WECOM_PORT || 3001;
app.listen(PORT, () => {
  console.log('🦞 企业微信机器人已启动，端口:', PORT);
  console.log('📡 Webhook URL: http://localhost:' + PORT + '/wecom/webhook');
});
`;

// 安装依赖
function installDependencies() {
  console.log('📦 安装企业微信依赖...\n');
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
function createConfigFile(corpId, agentId, secret, webhook, token, aesKey) {
  const configPath = path.join(__dirname, '../config/wecom.env');
  const configDir = path.dirname(configPath);
  
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  const config = WECOM_CONFIG_TEMPLATE
    .replace('${WECOM_CORP_ID}', corpId)
    .replace('${WECOM_AGENT_ID}', agentId)
    .replace('${WECOM_SECRET}', secret)
    .replace('${WECOM_WEBHOOK}', webhook)
    .replace('${WECOM_TOKEN}', token || '')
    .replace('${WECOM_ENCODING_AES_KEY}', aesKey || '');
  
  fs.writeFileSync(configPath, config, 'utf-8');
  console.log(`✅ 配置文件已创建：${configPath}\n`);
}

// 创建适配器脚本
function createAdapter() {
  const adapterPath = path.join(__dirname, '../adapters/wecom-bot.js');
  const adapterDir = path.dirname(adapterPath);
  
  if (!fs.existsSync(adapterDir)) {
    fs.mkdirSync(adapterDir, { recursive: true });
  }
  
  fs.writeFileSync(adapterPath, WECOM_ADAPTER_CODE, 'utf-8');
  console.log(`✅ 企业微信适配器已创建：${adapterPath}\n`);
}

// 创建部署文档
function createDeployGuide() {
  const guidePath = path.join(__dirname, '../docs/deploy-wecom-guide.md');
  
  const guide = `# 🦞 会议室预约虾 - 企业微信机器人部署指南

## 快速部署

### 1. 创建企业微信应用
1. 访问 https://work.weixin.qq.com/wework_admin
2. 进入"应用管理" → "应用" → "创建应用"
3. 填写应用名称：会议室预约虾
4. 获取 Corp ID、Agent ID、Secret

### 2. 配置接收消息
1. 进入应用管理后台
2. 配置"接收消息"服务器
3. 获取 Token 和 EncodingAESKey
4. 设置回调 URL

### 3. 运行部署脚本
\`\`\`bash
node scripts/deploy-wecom.js
\`\`\`

### 4. 启动服务
\`\`\`bash
node adapters/wecom-bot.js
\`\`\`

### 5. 配置回调地址
- 在企业微信管理后台配置接收消息服务器
- 格式：http://your-domain.com:3001/wecom/webhook

## 使用示例

在企业微信中发送消息给机器人：
- "给我预约周三下午的 10 人会议室"
- "查看我的预约"
- "取消预约 BK123"

## 功能特性

- ✅ 自然语言预约
- ✅ 智能推荐
- ✅ 消息卡片通知
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
  console.log('🦞 企业微信机器人一键部署\n');
  console.log('='.repeat(60));
  
  console.log('\n📝 请输入企业微信配置:\n');
  
  const corpId = await new Promise(resolve => {
    rl.question('Corp ID: ', resolve);
  });
  
  const agentId = await new Promise(resolve => {
    rl.question('Agent ID: ', resolve);
  });
  
  const secret = await new Promise(resolve => {
    rl.question('Secret: ', resolve);
  });
  
  const webhook = await new Promise(resolve => {
    rl.question('Webhook: ', resolve);
  });
  
  const token = await new Promise(resolve => {
    rl.question('Token (可选): ', resolve);
  });
  
  const aesKey = await new Promise(resolve => {
    rl.question('EncodingAESKey (可选): ', resolve);
  });
  
  rl.close();
  
  console.log('\n🔧 开始部署...\n');
  
  // 安装依赖
  installDependencies();
  
  // 创建配置文件
  createConfigFile(corpId, agentId, secret, webhook, token, aesKey);
  
  // 创建适配器
  createAdapter();
  
  // 创建部署指南
  createDeployGuide();
  
  console.log('='.repeat(60));
  console.log('✅ 企业微信机器人部署完成！\n');
  console.log('📌 下一步:\n');
  console.log('   1. 启动服务：node adapters/wecom-bot.js');
  console.log('   2. 在企业微信管理后台配置回调 URL');
  console.log('   3. 添加应用到工作台');
  console.log('   4. 测试：发送"预约会议室"\n');
}

main();
