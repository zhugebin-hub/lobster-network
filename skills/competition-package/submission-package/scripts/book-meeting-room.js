#!/usr/bin/env node

/**
 * 会议室预约脚本 - 下沙校区
 * 支持自然语言预约：「给我预约周三下午的五人会议室」
 */

const fs = require('fs');
const path = require('path');

const DATA_FILE = path.join(__dirname, '../data/meeting-rooms-xiasha.json');
const BOOKINGS_FILE = path.join(__dirname, '../data/bookings.json');

// 星期映射
const WEEKDAY_MAP = {
  '周日': 0, '星期天': 0, 'Sunday': 0,
  '周一': 1, '星期一': 1, 'Monday': 1,
  '周二': 2, '星期二': 2, 'Tuesday': 2,
  '周三': 3, '星期三': 3, 'Wednesday': 3,
  '周四': 4, '星期四': 4, 'Thursday': 4,
  '周五': 5, '星期五': 5, 'Friday': 5,
  '周六': 6, '星期六': 6, 'Saturday': 6,
};

// 时间段映射
const SLOT_MAP = {
  '上午': 'morning', '早上': 'morning', 'morning': 'morning',
  '下午': 'afternoon', 'afternoon': 'afternoon',
  '晚上': 'evening', '晚间': 'evening', 'evening': 'evening',
};

// 加载数据
function loadRooms() {
  const data = fs.readFileSync(DATA_FILE, 'utf-8');
  return JSON.parse(data);
}

// 加载预约记录
function loadBookings() {
  if (!fs.existsSync(BOOKINGS_FILE)) {
    return { bookings: [] };
  }
  const data = fs.readFileSync(BOOKINGS_FILE, 'utf-8');
  return JSON.parse(data);
}

// 保存预约记录
function saveBookings(bookings) {
  fs.writeFileSync(BOOKINGS_FILE, JSON.stringify(bookings, null, 2), 'utf-8');
}

// 中文数字映射
const CHINESE_NUMS = {
  '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
  '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
  '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
  '6': 6, '7': 7, '8': 8, '9': 9, '0': 0,
};

// 解析自然语言请求
function parseRequest(query) {
  const result = {
    weekday: null,
    slot: null,
    capacity: null,
    roomType: null,
    raw: query,
  };

  // 解析星期
  for (const [cn, num] of Object.entries(WEEKDAY_MAP)) {
    if (query.includes(cn)) {
      result.weekday = num;
      result.wdayStr = cn;
      break;
    }
  }

  // 解析时间段
  for (const [cn, slot] of Object.entries(SLOT_MAP)) {
    if (query.includes(cn)) {
      result.slot = slot;
      break;
    }
  }

  // 解析人数（匹配中文或阿拉伯数字 + 人）
  const capacityMatch = query.match(/([一二三四五六七八九十\d]+)\s*人/);
  if (capacityMatch) {
    const numStr = capacityMatch[1];
    // 中文数字转阿拉伯数字
    if (CHINESE_NUMS[numStr]) {
      result.capacity = CHINESE_NUMS[numStr];
    } else if (/^\d+$/.test(numStr)) {
      result.capacity = parseInt(numStr, 10);
    }
  }

  // 解析房间类型
  if (query.includes('会议室')) result.roomType = '会议室';
  else if (query.includes('报告厅')) result.roomType = '报告厅';
  else if (query.includes('实验室')) result.roomType = '实验室';
  else if (query.includes('多功能厅')) result.roomType = '多功能厅';
  else if (query.includes('研讨室')) result.roomType = '会议室';
  else if (query.includes('自习室')) result.roomType = '自习室';

  return result;
}

// 根据星期几计算日期（从今天起）
function getDateFromWeekday(weekday) {
  const today = new Date();
  const currentDay = today.getDay();
  const diff = weekday - currentDay;
  const targetDate = new Date(today);
  targetDate.setDate(today.getDate() + (diff >= 0 ? diff : diff + 7));
  return targetDate.toISOString().split('T')[0];
}

// 查找可用会议室
function findAvailableRooms(parsed) {
  const data = loadRooms();
  const targetDate = parsed.weekday !== null 
    ? getDateFromWeekday(parsed.weekday)
    : new Date().toISOString().split('T')[0];

  const candidates = [];

  for (const room of data.rooms) {
    // 容量检查
    if (parsed.capacity && room.capacity < parsed.capacity) {
      continue;
    }

    // 类型检查
    if (parsed.roomType && room.type !== parsed.roomType && parsed.roomType !== '自习室') {
      // 自习室可以匹配任何类型
      if (parsed.roomType !== '自习室') continue;
    }

    // 时间段检查
    for (const slot of room.availableSlots) {
      if (slot.date === targetDate && slot.slot === parsed.slot && slot.available) {
        candidates.push({
          room,
          slot,
          date: targetDate,
        });
      }
    }
  }

  return candidates;
}

// 执行预约
function bookRoom(room, slot, userName = '用户') {
  const bookings = loadBookings();
  
  const booking = {
    id: `BK${Date.now()}`,
    room: room.id,
    roomName: room.name,
    building: room.building,
    date: slot.date,
    slot: slot.slot,
    time: slot.time,
    userName,
    bookedAt: new Date().toISOString(),
    status: 'confirmed',
  };

  bookings.bookings.push(booking);
  saveBookings(bookings);

  return booking;
}

// 主函数
function main(query) {
  console.log('🦞 会议室预约虾 - 下沙校区\n');
  console.log(`📝 请求：${query}\n`);

  const parsed = parseRequest(query);
  console.log('🔍 解析结果:');
  console.log(`   星期：${parsed.wdayStr || '未指定'}`);
  console.log(`   时段：${parsed.slot || '未指定'}`);
  console.log(`   人数：${parsed.capacity || '未指定'}`);
  console.log(`   类型：${parsed.roomType || '未指定'}\n`);

  if (!parsed.slot) {
    console.log('❌ 请指定时间段（上午/下午/晚上）');
    return;
  }

  const candidates = findAvailableRooms(parsed);

  if (candidates.length === 0) {
    console.log('❌ 没有找到符合条件的可用会议室');
    console.log('💡 尝试：调整时间、减少人数要求、或更换房间类型');
    return;
  }

  console.log(`✅ 找到 ${candidates.length} 个可用会议室:\n`);
  
  candidates.forEach((c, i) => {
    console.log(`${i + 1}. ${c.room.name}`);
    console.log(`   📍 ${c.room.building} ${c.room.floor}楼`);
    console.log(`   👥 容量：${c.room.capacity}人`);
    console.log(`   🕐 时间：${c.slot.date} ${c.slot.time}`);
    console.log(`   🛠️ 设备：${c.room.equipment.join(', ')}`);
    console.log();
  });

  // 自动选择第一个（容量最接近的）
  const best = candidates.reduce((best, c) => {
    if (!best) return c;
    const bestDiff = Math.abs(best.room.capacity - (parsed.capacity || 0));
    const currDiff = Math.abs(c.room.capacity - (parsed.capacity || 0));
    return currDiff < bestDiff ? c : best;
  }, null);

  console.log('🎯 推荐方案:');
  console.log(`   ${best.room.name} (${best.room.building})`);
  console.log(`   ${best.slot.date} ${best.slot.time}`);
  console.log();

  // 模拟确认预约
  const booking = bookRoom(best.room, best.slot, '陈俊烨');
  console.log('✅ 预约成功!');
  console.log(`   预约号：${booking.id}`);
  console.log(`   房间：${booking.roomName}`);
  console.log(`   时间：${booking.date} ${booking.time}`);
  console.log(`   状态：${booking.status}`);
}

// 命令行执行
const query = process.argv.slice(2).join(' ') || '给我预约周三下午的五人会议室';
main(query);
