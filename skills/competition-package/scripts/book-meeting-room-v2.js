#!/usr/bin/env node

/**
 * 会议室预约脚本 v2 - 基于真实数据优化
 * 优化点：
 * 1. 用户偏好学习（基于历史预约）
 * 2. 热门房间推荐
 * 3. 智能容量匹配（避免浪费）
 * 4. 时间段推荐（基于使用频率）
 * 5. 冲突检测优化
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
  '上午': 'morning', '早上': 'morning', 'morning': 'morning', '8:00': 'morning',
  '下午': 'afternoon', 'afternoon': 'afternoon', '14:00': 'afternoon',
  '晚上': 'evening', '晚间': 'evening', 'evening': 'evening', '19:00': 'evening',
};

// 中文数字映射
const CHINESE_NUMS = {
  '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
  '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
  '1': 1, '2': 2, '3': 3, '4': 4, '5': 5,
  '6': 6, '7': 7, '8': 8, '9': 9, '0': 0,
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

// 解析自然语言请求
function parseRequest(query) {
  const result = {
    weekday: null,
    slot: null,
    capacity: null,
    roomType: null,
    raw: query,
    userName: null,
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

  // 解析用户（匹配"XXX 预约"或"给 XXX 预约"）
  const userMatch = query.match(/(?:给 | 替 | 帮)([\u4e00-\u9fa5]+)\s*预约/);
  if (userMatch) {
    result.userName = userMatch[1];
  }

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

// 分析用户偏好（基于历史数据）
function analyzeUserPreference(userName, bookings) {
  if (!userName) return null;

  const userBookings = bookings.filter(b => 
    b.userName === userName && b.status === 'confirmed'
  );

  if (userBookings.length === 0) return null;

  // 统计房间偏好
  const roomStats = {};
  userBookings.forEach(b => {
    roomStats[b.roomName] = (roomStats[b.roomName] || 0) + 1;
  });

  // 统计时间段偏好
  const slotStats = { morning: 0, afternoon: 0, evening: 0 };
  userBookings.forEach(b => {
    if (slotStats[b.slot] !== undefined) slotStats[b.slot]++;
  });

  // 统计容量偏好
  const capacities = userBookings.map(b => b.capacity || 10);
  const avgCapacity = capacities.reduce((a, b) => a + b, 0) / capacities.length;

  return {
    favoriteRooms: Object.entries(roomStats)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([name]) => name),
    favoriteSlot: Object.entries(slotStats)
      .sort((a, b) => b[1] - a[1])[0]?.[0] || 'afternoon',
    avgCapacity: Math.round(avgCapacity),
    bookingCount: userBookings.length
  };
}

// 分析热门房间（基于历史数据）
function analyzePopularRooms(bookingsData) {
  const bookings = Array.isArray(bookingsData) ? bookingsData : bookingsData.bookings || [];
  const roomStats = {};
  bookings.forEach(b => {
    if (b.status === 'confirmed') {
      roomStats[b.roomName] = (roomStats[b.roomName] || 0) + 1;
    }
  });

  return Object.entries(roomStats)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([name]) => name);
}

// 查找可用会议室（优化版）
function findAvailableRooms(parsed, rooms, bookings) {
  const targetDate = parsed.weekday !== null 
    ? getDateFromWeekday(parsed.weekday)
    : new Date().toISOString().split('T')[0];

  // 分析用户偏好
  const userPref = parsed.userName ? analyzeUserPreference(parsed.userName, bookings) : null;
  
  // 获取热门房间列表
  const popularRooms = analyzePopularRooms(bookings);

  const candidates = [];

  for (const room of rooms.rooms) {
    // 容量检查（智能匹配：避免过大浪费）
    if (parsed.capacity) {
      // 允许容量略小于需求（最多小 20%），但不超过需求 2 倍（避免浪费）
      if (room.capacity < parsed.capacity * 0.8 || room.capacity > parsed.capacity * 2) {
        continue;
      }
    }

    // 类型检查
    if (parsed.roomType && room.type !== parsed.roomType && parsed.roomType !== '自习室') {
      if (parsed.roomType !== '自习室') continue;
    }

    // 时间段检查
    for (const slot of room.availableSlots) {
      if (slot.date === targetDate && slot.slot === parsed.slot && slot.available) {
        // 检查是否已被预约
        const isBooked = bookings.bookings.some(b => 
          b.room === room.id && 
          b.date === slot.date && 
          b.slot === slot.slot &&
          b.status === 'confirmed'
        );

        if (!isBooked) {
          // 计算推荐分数
          let score = 0;
          
          // 热门房间加分
          if (popularRooms.includes(room.name)) {
            score += 30;
          }
          
          // 用户偏好房间加分
          if (userPref && userPref.favoriteRooms.includes(room.name)) {
            score += 50;
          }
          
          // 容量匹配度（越接近需求分数越高）
          if (parsed.capacity) {
            const capacityDiff = Math.abs(room.capacity - parsed.capacity);
            score += Math.max(0, 20 - capacityDiff * 2);
          }
          
          // 用户偏好时间段加分
          if (userPref && userPref.favoriteSlot === parsed.slot) {
            score += 20;
          }

          candidates.push({
            room,
            slot,
            date: targetDate,
            score
          });
        }
      }
    }
  }

  // 按推荐分数排序
  return candidates.sort((a, b) => b.score - a.score);
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
  fs.writeFileSync(BOOKINGS_FILE, JSON.stringify(bookings, null, 2), 'utf-8');

  return booking;
}

// 主函数
function main(query) {
  console.log('🦞 会议室预约虾 v2 - 智能推荐版\n');
  console.log(`📝 请求：${query}\n`);

  const parsed = parseRequest(query);
  
  console.log('🔍 解析结果:');
  console.log(`   星期：${parsed.wdayStr || '未指定'}`);
  console.log(`   时段：${parsed.slot || '未指定'}`);
  console.log(`   人数：${parsed.capacity || '未指定'}`);
  console.log(`   类型：${parsed.roomType || '未指定'}`);
  if (parsed.userName) {
    console.log(`   用户：${parsed.userName}`);
  }
  console.log();

  // 显示用户偏好分析
  if (parsed.userName) {
    const userPref = analyzeUserPreference(parsed.userName, loadBookings().bookings);
    if (userPref) {
      console.log('📊 用户偏好分析:');
      console.log(`   历史预约：${userPref.bookingCount} 次`);
      console.log(`   常用房间：${userPref.favoriteRooms.slice(0, 2).join(', ')}`);
      console.log(`   偏好时段：${userPref.favoriteSlot === 'morning' ? '上午' : userPref.favoriteSlot === 'afternoon' ? '下午' : '晚上'}`);
      console.log(`   平均容量：${userPref.avgCapacity}人`);
      console.log();
    }
  }

  if (!parsed.slot) {
    console.log('❌ 请指定时间段（上午/下午/晚上）');
    return;
  }

  const rooms = loadRooms();
  const bookings = loadBookings();
  const candidates = findAvailableRooms(parsed, rooms, bookings);

  if (candidates.length === 0) {
    console.log('❌ 没有找到符合条件的可用会议室');
    console.log('💡 尝试：调整时间、减少人数要求、或更换房间类型');
    return;
  }

  console.log(`✅ 找到 ${candidates.length} 个可用会议室:\n`);
  
  candidates.slice(0, 5).forEach((c, i) => {
    console.log(`${i + 1}. ${c.room.name} ${c.score >= 50 ? '⭐' : ''}`);
    console.log(`   📍 ${c.room.building} ${c.room.floor}楼`);
    console.log(`   👥 容量：${c.room.capacity}人`);
    console.log(`   🕐 时间：${c.slot.date} ${c.slot.time}`);
    console.log(`   🛠️ 设备：${c.room.equipment.join(', ')}`);
    console.log(`   📊 推荐分：${c.score}`);
    console.log();
  });

  // 选择最优方案
  const best = candidates[0];

  console.log('🎯 推荐方案:');
  console.log(`   ${best.room.name} (${best.room.building})`);
  console.log(`   ${best.slot.date} ${best.slot.time}`);
  console.log(`   推荐理由：${best.score >= 80 ? '完美匹配' : best.score >= 50 ? '高度匹配' : '可用选择'}`);
  console.log();

  // 模拟确认预约
  const userName = parsed.userName || '陈俊烨';
  const booking = bookRoom(best.room, best.slot, userName);
  console.log('✅ 预约成功!');
  console.log(`   预约号：${booking.id}`);
  console.log(`   房间：${booking.roomName}`);
  console.log(`   时间：${booking.date} ${booking.time}`);
  console.log(`   状态：${booking.status}`);
}

// 命令行执行
const query = process.argv.slice(2).join(' ') || '给我预约周三下午的五人会议室';
main(query);
