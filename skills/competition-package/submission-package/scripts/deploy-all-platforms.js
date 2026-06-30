#!/usr/bin/env node

/**
 * 多平台一键部署脚本
 * 用途：一次性部署所有平台（钉钉、飞书、企业微信、QQ）
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

// 平台配置
const PLATFORMS = {
  dingtalk: {
    name: '钉钉',
    config: 'config/dingtalk.env',
    adapter: 'adapters/dingtalk-bot.js',
    port: 3000,
    installed: true
  },
  feishu: {
    name: '飞书',
    config: 'config/feishu.env',
    adapter: 'adapters/feishu-bot.js',
    port: 3000,
    installed: false
  },
  wecom: {
    name: '企业微信',
    config: 'config/wecom.env',
    adapter: 'adapters/wecom-bot.js',
    port: 3001,
    installed: false
  },
  qqbot: {
    name: 'QQ 机器人',
    config: 'config/qqbot.env',
    adapter: 'adapters/qqbot-bot.js',
    port: 3002,
    installed: false
  }
};

// 安装依赖
function installDependencies() {
  console.log('\n📦 安装公共依赖...\n');
  try {
    execSync('npm install express axios crypto --save', {
      stdio: 'inherit',
      cwd: path.join(__dirname, '..')
    });
    console.log('\n✅ 依赖安装完成\n');
  } catch (error) {
    console.error('❌ 依赖安装失败:', error.message);
  }
}

// 创建配置目录
function createConfigDir() {
  const configDir = path.join(__dirname, '../config');
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
    console.log(`✅ 配置目录已创建：${configDir}\n`);
  }
}

// 创建启动脚本
function createStartAllScript() {
  const scriptPath = path.join(__dirname, '../start-all-bots.sh');
  
  const script = `#!/bin/bash

echo "🦞 启动所有平台机器人..."
echo ""

# 钉钉
if [ -f config/dingtalk.env ]; then
  echo "✅ 启动钉钉机器人 (端口 3000)..."
  source config/dingtalk.env
  node adapters/dingtalk-bot.js &
fi

# 飞书
if [ -f config/feishu.env ]; then
  echo "✅ 启动飞书机器人 (端口 3000)..."
  source config/feishu.env
  node adapters/feishu-bot.js &
fi

# 企业微信
if [ -f config/wecom.env ]; then
  echo "✅ 启动企业微信机器人 (端口 3001)..."
  source config/wecom.env
  node adapters/wecom-bot.js &
fi

# QQ 机器人
if [ -f config/qqbot.env ]; then
  echo "✅ 启动 QQ 机器人 (端口 3002)..."
  source config/qqbot.env
  node adapters/qqbot-bot.js &
fi

echo ""
echo "✅ 所有机器人已启动！"
echo ""
echo "📌 端口占用:"
echo "   钉钉：3000"
echo "   飞书：3000 (需单独配置)"
echo "   企业微信：3001"
echo "   QQ 机器人：3002"
echo ""
echo "🛑 停止所有服务：killall node"
`;

  fs.writeFileSync(scriptPath, script, 'utf-8');
  execSync(`chmod +x "${scriptPath}"`);
  console.log(`✅ 启动脚本已创建：${scriptPath}\n`);
}

// 创建系统服务文件
function createSystemdService() {
  const servicePath = path.join(__dirname, '../meeting-room-bot.service');
  
  const service = `[Unit]
Description=Meeting Room Bot - Multi-Platform
After=network.target

[Service]
Type=simple
User=${process.env.USER}
WorkingDirectory=${path.join(__dirname, '..')}
ExecStart=/usr/bin/bash ${path.join(__dirname, '../start-all-bots.sh')}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
`;

  fs.writeFileSync(servicePath, service, 'utf-8');
  console.log(`✅ Systemd 服务文件已创建：${servicePath}\n`);
  console.log('📌 安装系统服务:');
  console.log(`   sudo cp ${servicePath} /etc/systemd/system/`);
  console.log('   sudo systemctl daemon-reload');
  console.log('   sudo systemctl enable meeting-room-bot');
  console.log('   sudo systemctl start meeting-room-bot\n');
}

// 主函数
async function main() {
  console.log('🦞 会议室预约虾 - 多平台一键部署\n');
  console.log('='.repeat(60));
  
  console.log('\n📊 支持的平台:\n');
  Object.entries(PLATFORMS).forEach(([key, platform]) => {
    const status = platform.installed ? '✅ 已就绪' : '⏳ 待部署';
    console.log(`   ${platform.name}: ${status}`);
  });
  
  console.log('\n🔧 开始部署...\n');
  
  // 创建配置目录
  createConfigDir();
  
  // 安装依赖
  installDependencies();
  
  // 创建启动脚本
  createStartAllScript();
  
  // 创建系统服务文件
  createSystemdService();
  
  console.log('='.repeat(60));
  console.log('✅ 多平台部署框架已搭建完成！\n');
  
  console.log('📌 下一步:\n');
  console.log('   1. 配置各平台凭证:');
  console.log('      - 飞书：node scripts/deploy-feishu.js');
  console.log('      - 企业微信：node scripts/deploy-wecom.js');
  console.log('      - QQ 机器人：node scripts/deploy-qqbot.js\n');
  
  console.log('   2. 启动所有服务:');
  console.log('      bash start-all-bots.sh\n');
  
  console.log('   3. 或单独启动:');
  console.log('      node adapters/feishu-bot.js');
  console.log('      node adapters/wecom-bot.js');
  console.log('      node adapters/qqbot-bot.js\n');
  
  console.log('   4. 配置系统服务（可选）:');
  console.log('      sudo cp meeting-room-bot.service /etc/systemd/system/');
  console.log('      sudo systemctl enable meeting-room-bot\n');
  
  console.log('🎯 一套代码，四平台运行！\n');
}

main();
