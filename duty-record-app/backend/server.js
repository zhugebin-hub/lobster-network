const express = require('express');
const initSqlJs = require('sql.js');
const multer = require('multer');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'duty-record-secret-key-2026';

let db;
const DB_PATH = path.join(__dirname, 'duty.sqlite');

// 中间件
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, '../web')));

// 文件上传配置
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, 'uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });

// JWT 认证中间件
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: '未登录' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: '登录已过期' });
    req.user = user;
    next();
  });
};

// 保存数据库
function saveDb() {
  if (db) {
    const data = db.export();
    const buffer = Buffer.from(data);
    fs.writeFileSync(DB_PATH, buffer);
  }
}

// 初始化数据库
async function initDatabase() {
  const SQL = await initSqlJs();
  
  if (fs.existsSync(DB_PATH)) {
    const fileBuffer = fs.readFileSync(DB_PATH);
    db = new SQL.Database(fileBuffer);
    console.log('✅ 数据库已加载');
  } else {
    db = new SQL.Database();
    console.log('🆕 创建新数据库');
    
    // 创建用户表
    db.run(`
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
    db.run(`
      CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grade INTEGER NOT NULL,
        class_number INTEGER NOT NULL,
        name TEXT NOT NULL,
        UNIQUE(grade, class_number)
      )
    `);

    // 创建值班记录表
    db.run(`
      CREATE TABLE IF NOT EXISTS duty_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        date TEXT NOT NULL,
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
    db.run(`
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

    timePeriods.forEach(period => {
      db.run(`INSERT INTO time_periods (name, order_num, start_time, end_time) VALUES (?, ?, ?, ?)`,
        [period.name, period.order, period.start, period.end]);
    });

    // 插入默认管理员账号
    const hashedPassword = bcrypt.hashSync('admin123', 10);
    db.run(`INSERT INTO users (username, password_hash, role, name) VALUES (?, ?, ?, ?)`,
      ['admin', hashedPassword, 'admin', '系统管理员']);

    // 插入 24 个班级
    for (let grade = 1; grade <= 3; grade++) {
      for (let cls = 1; cls <= 8; cls++) {
        db.run(`INSERT INTO classes (grade, class_number, name) VALUES (?, ?, ?)`,
          [grade, cls, `${grade}年级${cls}班`]);
      }
    }

    saveDb();
    console.log('✅ 数据库初始化完成');
  }

  console.log('📊 已创建：24 个班级，9 个时段，默认管理员账号 admin/admin123');
}

// ============ 认证接口 ============

app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  const result = db.exec(`SELECT * FROM users WHERE username = '${username}'`);
  
  if (result.length === 0 || result[0].values.length === 0) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }

  const row = result[0].values[0];
  const columns = result[0].columns;
  const user = {};
  columns.forEach((col, i) => user[col] = row[i]);

  if (!bcrypt.compareSync(password, user.password_hash)) {
    return res.status(401).json({ error: '用户名或密码错误' });
  }

  const token = jwt.sign(
    { id: user.id, username: user.username, role: user.role, name: user.name },
    JWT_SECRET,
    { expiresIn: '7d' }
  );

  res.json({ token, user: { id: user.id, username: user.username, role: user.role, name: user.name } });
});

// ============ 班级接口 ============

app.get('/api/classes', (req, res) => {
  const result = db.exec('SELECT * FROM classes ORDER BY grade, class_number');
  const classes = result.length > 0 ? result[0].values.map(row => {
    const obj = {};
    result[0].columns.forEach((col, i) => obj[col] = row[i]);
    return obj;
  }) : [];
  res.json(classes);
});

// ============ 时段接口 ============

app.get('/api/time-periods', (req, res) => {
  const result = db.exec('SELECT * FROM time_periods ORDER BY order_num');
  const periods = result.length > 0 ? result[0].values.map(row => {
    const obj = {};
    result[0].columns.forEach((col, i) => obj[col] = row[i]);
    return obj;
  }) : [];
  res.json(periods);
});

// ============ 记录接口 ============

app.post('/api/records', authenticateToken, upload.single('photo'), (req, res) => {
  const { class_id, date, time_period, hygiene_score, discipline_score, study_score, notes } = req.body;
  const photo_path = req.file ? `/uploads/${req.file.filename}` : null;

  try {
    db.run(`INSERT INTO duty_records (user_id, class_id, date, time_period, hygiene_score, discipline_score, study_score, notes, photo_path)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [req.user.id, class_id, date, time_period, parseInt(hygiene_score) || 5, parseInt(discipline_score) || 5, parseInt(study_score) || 5, notes || '', photo_path]);
    saveDb();
    
    const result = db.exec('SELECT last_insert_rowid()');
    const id = result[0].values[0][0];
    res.json({ id, message: '记录成功' });
  } catch (error) {
    res.status(500).json({ error: '保存失败', details: error.message });
  }
});

app.get('/api/records', authenticateToken, (req, res) => {
  const { date, class_id, time_period, week_start } = req.query;
  
  let query = `
    SELECT r.*, c.name as class_name, u.name as recorder_name
    FROM duty_records r
    JOIN classes c ON r.class_id = c.id
    JOIN users u ON r.user_id = u.id
    WHERE 1=1
  `;
  const params = [];

  if (date) { query += ' AND r.date = ?'; params.push(date); }
  if (class_id) { query += ' AND r.class_id = ?'; params.push(class_id); }
  if (time_period) { query += ' AND r.time_period = ?'; params.push(time_period); }
  if (week_start) { query += ' AND r.date >= ?'; params.push(week_start); }

  query += ' ORDER BY r.date DESC, r.created_at DESC';
  
  const result = db.exec(query.replace(/\?/g, () => `'${params.shift()}'`));
  const records = result.length > 0 ? result[0].values.map(row => {
    const obj = {};
    result[0].columns.forEach((col, i) => obj[col] = row[i]);
    return obj;
  }) : [];
  res.json(records);
});

// ============ 统计接口 ============

app.get('/api/stats/weekly', authenticateToken, (req, res) => {
  const { week_start } = req.query;
  
  const query = `
    SELECT 
      c.id as class_id,
      c.name as class_name,
      c.grade,
      c.class_number,
      COUNT(r.id) as record_count,
      AVG(r.hygiene_score) as avg_hygiene,
      AVG(r.discipline_score) as avg_discipline,
      AVG(r.study_score) as avg_study,
      (AVG(r.hygiene_score) + AVG(r.discipline_score) + AVG(r.study_score)) / 3 as total_avg
    FROM classes c
    LEFT JOIN duty_records r ON c.id = r.class_id AND r.date >= '${week_start}'
    GROUP BY c.id
    ORDER BY total_avg DESC
  `;

  const result = db.exec(query);
  const stats = result.length > 0 ? result[0].values.map(row => {
    const obj = {};
    result[0].columns.forEach((col, i) => obj[col] = row[i]);
    return obj;
  }) : [];
  res.json(stats);
});

// ============ AI 总结接口 ============

app.post('/api/ai/weekly-summary', authenticateToken, async (req, res) => {
  const { week_start, week_end } = req.body;

  const result = db.exec(`
    SELECT r.*, c.name as class_name, c.grade, c.class_number
    FROM duty_records r
    JOIN classes c ON r.class_id = c.id
    WHERE r.date BETWEEN '${week_start}' AND '${week_end}'
    ORDER BY r.date, r.time_period
  `);

  const records = result.length > 0 ? result[0].values.map(row => {
    const obj = {};
    result[0].columns.forEach((col, i) => obj[col] = row[i]);
    return obj;
  }) : [];

  if (records.length === 0) {
    return res.json({ summary: '本周暂无值班记录。' });
  }

  const classStats = {};
  records.forEach(r => {
    if (!classStats[r.class_name]) {
      classStats[r.class_name] = { count: 0, hygiene: 0, discipline: 0, study: 0, issues: [] };
    }
    classStats[r.class_name].count++;
    classStats[r.class_name].hygiene += r.hygiene_score;
    classStats[r.class_name].discipline += r.discipline_score;
    classStats[r.class_name].study += r.study_score;
    
    if (r.hygiene_score < 4 || r.discipline_score < 4 || r.study_score < 4) {
      classStats[r.class_name].issues.push({ time: r.time_period, date: r.date, notes: r.notes });
    }
  });

  Object.keys(classStats).forEach(name => {
    const s = classStats[name];
    s.avg_hygiene = (s.hygiene / s.count).toFixed(2);
    s.avg_discipline = (s.discipline / s.count).toFixed(2);
    s.avg_study = (s.study / s.count).toFixed(2);
    s.total_avg = ((parseFloat(s.avg_hygiene) + parseFloat(s.avg_discipline) + parseFloat(s.avg_study)) / 3).toFixed(2);
  });

  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (apiKey) {
    const prompt = `你是学校值班记录 AI 分析助手。请根据以下数据生成周报总结：

【数据概览】记录总数：${records.length}条，涉及班级：${Object.keys(classStats).length}个

【班级表现】
${Object.entries(classStats).map(([name, s]) => 
  `${name}: 记录${s.count}次，卫生${s.avg_hygiene}分，纪律${s.avg_discipline}分，学习${s.avg_study}分，综合${s.total_avg}分`
).join('\n')}

请生成 300 字左右的周报，包括：1.整体情况 2.优秀班级（前 3 名）3.需关注班级 4.改进建议`;

    try {
      const response = await axios.post(
        'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation',
        { model: 'qwen-turbo', input: { messages: [{ role: 'user', content: prompt }] } },
        { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } }
      );
      res.json({ summary: response.data.output.text, data: classStats });
    } catch (error) {
      res.status(500).json({ error: 'AI 总结失败', details: error.message });
    }
  } else {
    const topClasses = Object.entries(classStats).sort((a, b) => b[1].total_avg - a[1].total_avg).slice(0, 3);
    const summary = `## 本周值班总结\n\n### 整体情况\n本周共记录 ${records.length} 次，覆盖 ${Object.keys(classStats).length} 个班级。\n\n### 优秀班级\n${topClasses.map(([name, s], i) => `${i + 1}. ${name} - 综合${s.total_avg}分`).join('\n')}\n\n### 建议\n1. 继续保持良好班风\n2. 关注卫生细节\n3. 加强自习纪律管理`;
    res.json({ summary, data: classStats, note: '配置 DASHSCOPE_API_KEY 可获得更智能 AI 总结' });
  }
});

// 启动
app.listen(PORT, async () => {
  await initDatabase();
  console.log(`🚀 服务已启动：http://localhost:${PORT}`);
  console.log(`📁 上传目录：${path.join(__dirname, 'uploads')}`);
});
