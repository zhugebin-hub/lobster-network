#!/usr/bin/env node

/**
 * 会议室预约简报生成器
 * 用途：生成预约确认简报（Markdown 格式），支持转换为 Word 文档
 */

const fs = require('fs');
const path = require('path');

const BOOKINGS_FILE = path.join(__dirname, '../data/bookings.json');
const BRIEFS_DIR = path.join(__dirname, '../briefs');

// 确保简报目录存在
if (!fs.existsSync(BRIEFS_DIR)) {
  fs.mkdirSync(BRIEFS_DIR, { recursive: true });
}

// 加载预约记录
function loadBookings() {
  if (!fs.existsSync(BOOKINGS_FILE)) {
    return { bookings: [] };
  }
  const data = fs.readFileSync(BOOKINGS_FILE, 'utf-8');
  return JSON.parse(data);
}

// 获取最新预约
function getLatestBooking() {
  const bookings = loadBookings();
  if (bookings.bookings.length === 0) {
    return null;
  }
  // 返回最后一条预约
  return bookings.bookings[bookings.bookings.length - 1];
}

// 生成 Markdown 简报
function generateBrief(booking) {
  const date = new Date().toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });

  const brief = `# 🦞 会议室预约确认简报

**生成时间**: ${date}
**预约号**: ${booking.id}

---

## 📋 预约信息

| 项目 | 内容 |
|------|------|
| **预约人** | ${booking.userName} |
| **会议室** | ${booking.roomName} |
| **楼栋位置** | ${booking.building} |
| **预约日期** | ${booking.date} |
| **时间段** | ${booking.time} |
| **预约状态** | ✅ ${booking.status === 'confirmed' ? '已确认' : booking.status} |
| **预约时间** | ${booking.bookedAt} |

---

## 📍 位置指引

### 建筑信息
- **楼栋**: ${booking.building}
- **房间**: ${booking.roomName}
- **容量**: [待补充] 人
- **设备**: [待补充]

### 交通指引
- **校区**: 浙江工商大学下沙校区
- **导航**: [待补充具体位置]

---

## ⏰ 时间提醒

| 提醒类型 | 时间 | 状态 |
|----------|------|------|
| 预约成功 | 即时 | ✅ 已发送 |
| 使用前 24h | ${getReminderDate(booking.date, -1)} | 🟡 待发送 |
| 使用前 1h | ${getReminderDate(booking.date, 0)} | 🟡 待发送 |
| 使用结束 | ${booking.time} | 🟡 待发送 |

---

## 📝 注意事项

### 使用规范
1. 请按时到达，如需取消请提前 2 小时
2. 保持室内整洁，使用后恢复原状
3. 爱护设备，损坏需照价赔偿
4. 禁止在室内吸烟、饮食
5. 离开时关闭电源、门窗

### 设备使用
- 投影仪、空调等设备请规范操作
- 遇到问题请联系管理员
- 使用后请关闭所有设备

### 联系方式
- **管理员**: [待补充]
- **联系电话**: [待补充]
- **技术支持**: [待补充]

---

## 🔄 预约管理

### 修改预约
如需修改预约时间或房间，请提前联系管理员。

### 取消预约
- 提前 2 小时以上取消：免费
- 提前不足 2 小时：可能影响信用记录
- 未使用且未取消：记为爽约

### 查看预约
```bash
# 查看我的预约
node scripts/book-meeting-room.js "查看我的预约"
```

---

## 📊 使用统计

| 统计项 | 数值 |
|--------|------|
| 本月预约次数 | [待统计] 次 |
| 累计使用时长 | [待统计] 小时 |
| 常用会议室 | ${booking.roomName} |

---

## 💡 智能推荐

基于您的预约历史，推荐以下会议室：
- [待推荐]

---

## 📞 帮助与支持

### 常见问题
- **Q: 如何取消预约？**
  A: 联系管理员或发送"取消预约 [预约号]"

- **Q: 可以提前多久预约？**
  A: 最多可提前 7 天预约

- **Q: 会议室可以续订吗？**
  A: 如无后续预约，可现场续订

### 技术支持
- **GitHub**: [待补充]
- **文档**: [待补充]
- **反馈**: [待补充]

---

*本简报由会议室预约虾系统自动生成*
*系统版本：v1.0 | 生成时间：${date}*
*浙江工商大学下沙校区 | 信电学院*
`;

  return brief;
}

// 计算提醒日期
function getReminderDate(bookingDate, daysOffset) {
  const booking = new Date(bookingDate);
  booking.setDate(booking.getDate() + daysOffset);
  return booking.toLocaleDateString('zh-CN');
}

// 保存简报
function saveBrief(brief, bookingId) {
  const filename = `booking-${bookingId}.md`;
  const filepath = path.join(BRIEFS_DIR, filename);
  fs.writeFileSync(filepath, brief, 'utf-8');
  return filepath;
}

// 转换为 Word 文档
async function convertToWord(mdPath) {
  const { execSync } = require('child_process');
  const wordPath = mdPath.replace('.md', '.docx');
  
  try {
    // 使用 md2word-cn 技能转换
    execSync(`node /home/admin/.openclaw/workspace/md2pdf.js "${mdPath}"`, {
      cwd: path.dirname(mdPath)
    });
    return wordPath;
  } catch (error) {
    console.log('⚠️  Word 转换失败，请手动转换');
    return null;
  }
}

// 主函数
function main(bookingId = null) {
  console.log('🦞 会议室预约简报生成器\n');

  let booking;

  if (bookingId) {
    // 查找指定预约
    const bookings = loadBookings();
    booking = bookings.bookings.find(b => b.id === bookingId);
    if (!booking) {
      console.log(`❌ 未找到预约号：${bookingId}`);
      return;
    }
  } else {
    // 获取最新预约
    booking = getLatestBooking();
    if (!booking) {
      console.log('❌ 没有找到预约记录');
      return;
    }
  }

  console.log(`📝 生成预约号 ${booking.id} 的简报...\n`);

  // 生成简报
  const brief = generateBrief(booking);
  
  // 保存简报
  const mdPath = saveBrief(brief, booking.id);
  console.log(`✅ Markdown 简报已生成：${mdPath}`);

  // 显示简报预览
  console.log('\n' + '='.repeat(60));
  console.log('📋 简报预览（前 20 行）:');
  console.log('='.repeat(60));
  const lines = brief.split('\n').slice(0, 20);
  lines.forEach(line => console.log(line));
  console.log('...');
  console.log('='.repeat(60));

  // 提示转换
  console.log('\n💡 转换为 Word 文档:');
  console.log(`   使用 md2word-cn 技能转换：${mdPath}`);
  console.log(`   或使用命令：node md2pdf.js "${mdPath}"`);

  return {
    bookingId: booking.id,
    mdPath,
    brief
  };
}

// 命令行执行
const bookingId = process.argv[2];
main(bookingId);
