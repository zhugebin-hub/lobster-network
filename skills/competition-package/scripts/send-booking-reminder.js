#!/usr/bin/env node

/**
 * 会议室预约提醒发送器
 * 用途：在预约时间点前发送钉钉提醒消息
 * 支持：预约成功通知、使用前 24h 提醒、使用前 1h 提醒
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BOOKINGS_FILE = path.join(__dirname, '../data/bookings.json');
const REMINDERS_FILE = path.join(__dirname, '../data/reminders.json');

// 加载预约记录
function loadBookings() {
  if (!fs.existsSync(BOOKINGS_FILE)) {
    return { bookings: [] };
  }
  const data = fs.readFileSync(BOOKINGS_FILE, 'utf-8');
  return JSON.parse(data);
}

// 加载提醒记录
function loadReminders() {
  if (!fs.existsSync(REMINDERS_FILE)) {
    return { reminders: [] };
  }
  const data = fs.readFileSync(REMINDERS_FILE, 'utf-8');
  return JSON.parse(data);
}

// 保存提醒记录
function saveReminders(reminders) {
  fs.writeFileSync(REMINDERS_FILE, JSON.stringify(reminders, null, 2), 'utf-8');
}

// 获取最新预约
function getLatestBooking() {
  const bookings = loadBookings();
  if (bookings.bookings.length === 0) {
    return null;
  }
  return bookings.bookings[bookings.bookings.length - 1];
}

// 计算提醒时间
function calculateReminderTimes(booking) {
  const bookingDate = booking.date; // YYYY-MM-DD
  const bookingTime = booking.time; // HH:MM-HH:MM
  
  // 解析开始时间
  const [startTime] = bookingTime.split('-');
  const [hours, minutes] = startTime.split(':').map(Number);
  
  // 创建预约开始时间对象
  const bookingStart = new Date(`${bookingDate}T${startTime}:00+08:00`);
  
  // 计算提醒时间点
  const reminder24h = new Date(bookingStart);
  reminder24h.setDate(reminder24h.getDate() - 1);
  
  const reminder1h = new Date(bookingStart);
  reminder1h.setHours(reminder1h.getHours() - 1);
  
  return {
    booking: bookingStart,
    reminder24h,
    reminder1h,
    bookingTimeStr: `${bookingDate} ${bookingTime}`
  };
}

// 发送钉钉消息
function sendDingTalkMessage(message, userId = null) {
  console.log('📱 发送钉钉消息...\n');
  
  try {
    // 使用 OpenClaw message 工具发送
    const command = `openclaw message send --target "${userId || '03373037366737633702'}" --message "${message.replace(/"/g, '\\"')}"`;
    
    const output = execSync(command, { encoding: 'utf-8' });
    console.log('✅ 钉钉消息发送成功！');
    return true;
  } catch (error) {
    console.log('⚠️  钉钉消息发送失败，记录到日志');
    console.log('   错误信息:', error.message);
    return false;
  }
}

// 生成提醒消息
function generateReminderMessage(booking, reminderType) {
  const times = calculateReminderTimes(booking);
  
  let title, content, emoji;
  
  switch (reminderType) {
    case 'booking_success':
      emoji = '✅';
      title = '会议室预约成功';
      content = `
🦞 会议室预约确认

📋 预约信息
• 预约号：${booking.id}
• 会议室：${booking.roomName}
• 位置：${booking.building}
• 时间：${times.bookingTimeStr}
• 预约人：${booking.userName}

📍 位置指引
• 校区：浙江工商大学下沙校区
• 楼栋：${booking.building}

⏰ 时间提醒
• 使用前 24h 将发送提醒
• 使用前 1h 将再次提醒

📝 注意事项
• 请按时到达，如需取消请提前 2 小时
• 保持室内整洁，使用后恢复原状
• 离开时关闭电源、门窗

---
*本消息由会议室预约虾自动发送*
      `.trim();
      break;
      
    case '24h_before':
      emoji = '⏰';
      title = '会议室使用提醒（24 小时后）';
      content = `
🦞 会议室使用提醒

📋 预约信息
• 预约号：${booking.id}
• 会议室：${booking.roomName}
• 位置：${booking.building}
• 时间：${times.bookingTimeStr}

⏱️ 距离使用还有 24 小时

📍 位置指引
• 校区：浙江工商大学下沙校区
• 楼栋：${booking.building}
• 导航：请提前规划路线

💡 温馨提示
• 请确认参会人员时间
• 准备好会议材料
• 如需取消请尽早通知

---
*本消息由会议室预约虾自动发送*
      `.trim();
      break;
      
    case '1h_before':
      emoji = '🚨';
      title = '会议室使用提醒（1 小时后）';
      content = `
🦞 会议室使用提醒

📋 预约信息
• 预约号：${booking.id}
• 会议室：${booking.roomName}
• 位置：${booking.building}
• 时间：${times.bookingTimeStr}

⏱️ 距离使用还有 1 小时！

📍 位置指引
• 校区：浙江工商大学下沙校区
• 楼栋：${booking.building}
• 请现在出发前往会议室

💡 温馨提示
• 请带好会议材料
• 提前 5-10 分钟到达
• 检查设备是否正常

🚀 即将开会，请准时到达！

---
*本消息由会议室预约虾自动发送*
      `.trim();
      break;
      
    default:
      return null;
  }
  
  return `${emoji} **${title}**\n\n${content}`;
}

// 记录提醒
function recordReminder(bookingId, reminderType, sent) {
  const reminders = loadReminders();
  
  const reminder = {
    id: `REM${Date.now()}`,
    bookingId,
    type: reminderType,
    sentAt: new Date().toISOString(),
    sent
  };
  
  reminders.reminders.push(reminder);
  saveReminders(reminders);
}

// 发送预约成功提醒
function sendBookingSuccessReminder(booking) {
  console.log('📱 发送预约成功提醒...\n');
  
  const message = generateReminderMessage(booking, 'booking_success');
  const success = sendDingTalkMessage(message, booking.userId);
  
  recordReminder(booking.id, 'booking_success', success);
  
  if (success) {
    console.log('✅ 预约成功提醒已发送');
  }
  
  return success;
}

// 发送 24 小时前提醒
function send24hReminder(booking) {
  console.log('📱 发送 24 小时前提醒...\n');
  
  const message = generateReminderMessage(booking, '24h_before');
  const success = sendDingTalkMessage(message, booking.userId);
  
  recordReminder(booking.id, '24h_before', success);
  
  if (success) {
    console.log('✅ 24 小时前提醒已发送');
  }
  
  return success;
}

// 发送 1 小时前提醒
function send1hReminder(booking) {
  console.log('📱 发送 1 小时前提醒（紧急）...\n');
  
  const message = generateReminderMessage(booking, '1h_before');
  const success = sendDingTalkMessage(message, booking.userId);
  
  recordReminder(booking.id, '1h_before', success);
  
  if (success) {
    console.log('✅ 1 小时前提醒已发送');
  }
  
  return success;
}

// 检查并发送待发送的提醒
function checkAndSendReminders() {
  console.log('🦞 会议室预约提醒检查器\n');
  console.log(`⏰ 检查时间：${new Date().toLocaleString('zh-CN')}\n`);
  
  const bookings = loadBookings();
  const now = new Date();
  let sentCount = 0;
  
  for (const booking of bookings.bookings) {
    // 跳过已取消的预约
    if (booking.status === 'cancelled') continue;
    
    const times = calculateReminderTimes(booking);
    const reminders = loadReminders();
    
    // 检查 24 小时前提醒
    if (
      times.reminder24h <= now &&
      !reminders.reminders.find(r => r.bookingId === booking.id && r.type === '24h_before')
    ) {
      console.log(`⏰ 发送 24 小时前提醒：${booking.id}`);
      send24hReminder(booking);
      sentCount++;
    }
    
    // 检查 1 小时前提醒
    if (
      times.reminder1h <= now &&
      !reminders.reminders.find(r => r.bookingId === booking.id && r.type === '1h_before')
    ) {
      console.log(`⏰ 发送 1 小时前提醒：${booking.id}`);
      send1hReminder(booking);
      sentCount++;
    }
  }
  
  console.log(`\n✅ 检查完成，发送了 ${sentCount} 条提醒`);
  return sentCount;
}

// 主函数
function main(action = 'check', bookingId = null) {
  console.log('🦞 会议室预约提醒发送器\n');
  
  if (action === 'check') {
    // 定时检查模式（用于 cron）
    return checkAndSendReminders();
  }
  
  if (action === 'send') {
    // 手动发送模式
    const bookings = loadBookings();
    let booking;
    
    if (bookingId) {
      booking = bookings.bookings.find(b => b.id === bookingId);
    } else {
      booking = getLatestBooking();
    }
    
    if (!booking) {
      console.log('❌ 未找到预约记录');
      return;
    }
    
    console.log(`📝 发送预约号 ${booking.id} 的提醒...\n`);
    
    // 发送预约成功提醒
    sendBookingSuccessReminder(booking);
    
    // 显示下次提醒时间
    const times = calculateReminderTimes(booking);
    console.log('\n⏰ 下次提醒时间:');
    console.log(`   24 小时前：${times.reminder24h.toLocaleString('zh-CN')}`);
    console.log(`   1 小时前：${times.reminder1h.toLocaleString('zh-CN')}`);
    
    return booking;
  }
  
  // 默认显示帮助
  console.log('用法:');
  console.log('  node send-booking-reminder.js [action] [bookingId]');
  console.log('\nActions:');
  console.log('  check              检查并发送待发送的提醒（用于 cron）');
  console.log('  send [bookingId]   手动发送预约成功提醒');
  console.log('\n示例:');
  console.log('  node send-booking-reminder.js check');
  console.log('  node send-booking-reminder.js send BK1774658600852');
  console.log('  node send-booking-reminder.js send  # 发送最新预约');
}

// 命令行执行
const args = process.argv.slice(2);
main(args[0] || 'check', args[1]);
