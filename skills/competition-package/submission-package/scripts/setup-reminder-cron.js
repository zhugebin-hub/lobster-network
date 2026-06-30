#!/usr/bin/env node

/**
 * 会议室预约提醒定时任务设置
 * 用途：设置每小时检查提醒的 cron 任务
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const SCRIPT_DIR = __dirname;
const REMINDER_SCRIPT = path.join(SCRIPT_DIR, 'send-booking-reminder.js');
const LOG_FILE = '/tmp/booking-reminder.log';
const CRON_FILE = '/tmp/booking-reminder-cron.txt';

// 生成 cron 表达式
function generateCronJob() {
  const nodePath = process.execPath;
  
  // 每小时检查一次
  const cronJob = `
# 会议室预约提醒定时任务
# 每小时检查一次，发送 24h 前和 1h 前提醒

0 * * * * ${nodePath} "${REMINDER_SCRIPT}" check >> "${LOG_FILE}" 2>&1
`.trim();

  return cronJob;
}

// 安装 cron 任务
function installCron() {
  console.log('🦞 会议室预约提醒定时任务设置\n');
  
  const cronJob = generateCronJob();
  
  // 写入 cron 文件
  fs.writeFileSync(CRON_FILE, cronJob, 'utf-8');
  console.log(`✅ Cron 配置已写入：${CRON_FILE}`);
  
  // 尝试安装到 crontab
  try {
    // 读取现有 crontab
    let existingCrontab = '';
    try {
      existingCrontab = execSync('crontab -l', { encoding: 'utf-8' });
    } catch (e) {
      // 没有现有 crontab，忽略
    }
    
    // 检查是否已存在
    if (existingCrontab.includes(REMINDER_SCRIPT)) {
      console.log('⚠️  提醒任务已存在，跳过安装');
      return;
    }
    
    // 合并并安装
    const newCrontab = existingCrontab + '\n' + cronJob + '\n';
    execSync(`echo "${newCrontab.replace(/\n/g, '\\n')}" | crontab -`, { encoding: 'utf-8' });
    
    console.log('✅ Cron 任务已安装');
    console.log('📅 执行频率：每小时检查一次');
    console.log(`📝 日志文件：${LOG_FILE}`);
    
  } catch (error) {
    console.log('⚠️  Cron 任务安装失败，请手动安装');
    console.log('\n手动安装方法:');
    console.log(`  crontab -e`);
    console.log('\n添加以下内容:');
    console.log(cronJob);
  }
  
  // 显示当前 crontab
  console.log('\n📋 当前 crontab:');
  try {
    const current = execSync('crontab -l', { encoding: 'utf-8' });
    console.log(current);
  } catch (e) {
    console.log('  (无 crontab 或无法读取)');
  }
}

// 查看 cron 状态
function checkCronStatus() {
  console.log('🦞 会议室预约提醒定时任务状态\n');
  
  try {
    const crontab = execSync('crontab -l', { encoding: 'utf-8' });
    
    if (crontab.includes(REMINDER_SCRIPT)) {
      console.log('✅ 提醒任务已安装');
      
      // 显示相关行
      const lines = crontab.split('\n');
      const reminderLines = lines.filter(line => line.includes(REMINDER_SCRIPT));
      console.log('\n📅 提醒任务配置:');
      reminderLines.forEach(line => console.log(`   ${line}`));
      
    } else {
      console.log('❌ 提醒任务未安装');
      console.log('\n运行以下命令安装:');
      console.log('  node scripts/setup-reminder-cron.js install');
    }
    
  } catch (error) {
    console.log('❌ 无法读取 crontab');
  }
  
  // 检查日志文件
  if (fs.existsSync(LOG_FILE)) {
    console.log(`\n📝 日志文件：${LOG_FILE}`);
    const stats = fs.statSync(LOG_FILE);
    console.log(`   大小：${(stats.size / 1024).toFixed(2)} KB`);
    console.log(`   最后修改：${stats.mtime.toLocaleString('zh-CN')}`);
    
    // 显示最后 5 行日志
    console.log('\n📋 最近日志:');
    const logContent = fs.readFileSync(LOG_FILE, 'utf-8');
    const lastLines = logContent.split('\n').slice(-5).filter(l => l.trim());
    lastLines.forEach(line => console.log(`   ${line}`));
  }
}

// 卸载 cron 任务
function uninstallCron() {
  console.log('🦞 卸载会议室预约提醒定时任务\n');
  
  try {
    const crontab = execSync('crontab -l', { encoding: 'utf-8' });
    const lines = crontab.split('\n');
    const newLines = lines.filter(line => !line.includes(REMINDER_SCRIPT));
    const newCrontab = newLines.join('\n');
    
    if (newCrontab.trim()) {
      execSync(`echo "${newCrontab.replace(/\n/g, '\\n')}" | crontab -`, { encoding: 'utf-8' });
    } else {
      execSync('crontab -r', { encoding: 'utf-8' });
    }
    
    console.log('✅ 提醒任务已卸载');
    
  } catch (error) {
    console.log('⚠️  卸载失败:', error.message);
  }
}

// 测试提醒
function testReminder() {
  console.log('🦞 测试会议室预约提醒\n');
  
  try {
    console.log('📱 发送测试消息...\n');
    execSync(`node "${REMINDER_SCRIPT}" send`, { 
      encoding: 'utf-8',
      stdio: 'inherit'
    });
    console.log('\n✅ 测试完成');
  } catch (error) {
    console.log('\n❌ 测试失败:', error.message);
  }
}

// 主函数
function main(action = 'status') {
  switch (action) {
    case 'install':
      installCron();
      break;
    case 'uninstall':
      uninstallCron();
      break;
    case 'status':
      checkCronStatus();
      break;
    case 'test':
      testReminder();
      break;
    default:
      console.log('🦞 会议室预约提醒定时任务管理\n');
      console.log('用法:');
      console.log('  node setup-reminder-cron.js [action]');
      console.log('\nActions:');
      console.log('  install    安装定时任务（每小时检查）');
      console.log('  uninstall  卸载定时任务');
      console.log('  status     查看任务状态');
      console.log('  test       测试提醒功能');
      console.log('\n示例:');
      console.log('  node setup-reminder-cron.js install');
      console.log('  node setup-reminder-cron.js status');
      console.log('  node setup-reminder-cron.js test');
  }
}

// 命令行执行
const args = process.argv.slice(2);
main(args[0] || 'status');
