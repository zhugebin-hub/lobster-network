const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const path = require('path');

const db = new Database(path.join(__dirname, 'duty.db'));

// 创建用户表
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'teacher',
    name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

// 创建班级表
db.exec(`
  CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grade INTEGER NOT NULL,
    class_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    UNIQUE(grade, class_number)
  )
`);

// 创建值班记录表
db.exec(`
  CREATE TABLE IF NOT EXISTS duty_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    date DATE NOT NULL,
    time_period TEXT NOT NULL,
    hygiene_score INTEGER DEFAULT 5,
    discipline_score INTEGER DEFAULT 5,
    study_score INTEGER DEFAULT 5,
    notes TEXT,
    photo_path TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id)
  )
`);

// 创建时段配置表
db.exec(`
  CREATE TABLE IF NOT EXISTS time_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    order_num INTEGER NOT NULL,
    start_time TEXT,
    end_time TEXT
  )
`);

// 插入默认时段
const timePeriods = [
  { name: '晨间管理', order: 1, start: '07:00', end: '08:00' },
  { name: '上午', order: 2, start: '08:00', end: '09:40' },
  { name: '大课间', order: 3, start: '09:40', end: '10:10' },
  { name: '午餐', order: 4, start: '11:30', end: '12:30' },
  { name: '午间管理', order: 5, start: '12:30', end: '14:00' },
  { name: '下午', order: 6, start: '14:00', end: '17:00' },
  { name: '晚餐', order: 7, start: '17:00', end: '18:00' },
  { name: '晚间管理', order: 8, start: '18:00', end: '18:30' },
  { name: '晚自习', order: 9, start: '18:30', end: '21:00' }
];

const insertPeriod = db.prepare(`
  INSERT OR IGNORE INTO time_periods (name, order_num, start_time, end_time)
  VALUES (?, ?, ?, ?)
`);

timePeriods.forEach(period => {
  insertPeriod.run(period.name, period.order, period.start, period.end);
});

// 插入默认管理员账号 (密码：admin123)
const hashedPassword = bcrypt.hashSync('admin123', 10);
db.exec(`
  INSERT OR IGNORE INTO users (username, password_hash, role, name)
  VALUES ('admin', '${hashedPassword}', 'admin', '系统管理员')
`);

// 插入 24 个班级 (3 年级 × 8 班)
const insertClass = db.prepare(`
  INSERT OR IGNORE INTO classes (grade, class_number, name)
  VALUES (?, ?, ?)
`);

for (let grade = 1; grade <= 3; grade++) {
  for (let cls = 1; cls <= 8; cls++) {
    insertClass.run(grade, cls, `${grade}年级${cls}班`);
  }
}

console.log('✅ 数据库初始化完成！');
console.log('📊 已创建：');
console.log('   - 24 个班级 (3 年级 × 8 班)');
console.log('   - 9 个值班时段');
console.log('   - 默认管理员账号：admin / admin123');

db.close();
