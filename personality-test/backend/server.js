const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend/dist')));

// 数据文件路径
const DATA_DIR = path.join(__dirname, 'data');
const QUESTIONS_FILE = path.join(DATA_DIR, 'questions.json');
const TYPES_FILE = path.join(DATA_DIR, 'types.json');
const RESULTS_FILE = path.join(DATA_DIR, 'results.json');

// 确保数据目录存在
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// 加载数据
function loadJSON(file) {
  try {
    const data = fs.readFileSync(file, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return null;
  }
}

function saveJSON(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
}

// 获取所有题目
app.get('/api/questions', (req, res) => {
  try {
    const questions = loadJSON(QUESTIONS_FILE);
    if (!questions) {
      return res.status(500).json({ success: false, error: '题目数据不存在，请先运行 npm run init-db' });
    }
    res.json({ success: true, data: questions });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 提交测试结果
app.post('/api/submit', (req, res) => {
  try {
    const { sessionId, answers, scores, resultType } = req.body;
    
    // 保存测试结果
    const results = loadJSON(RESULTS_FILE) || [];
    results.push({
      sessionId,
      resultType,
      scores,
      answers,
      createdAt: new Date().toISOString()
    });
    saveJSON(RESULTS_FILE, results);
    
    // 获取详细结果
    const types = loadJSON(TYPES_FILE) || [];
    const typeInfo = types.find(t => t.type_code === resultType);
    
    res.json({ 
      success: true, 
      data: {
        type: resultType,
        ...typeInfo,
        scores
      } 
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 获取性格类型详情
app.get('/api/type/:code', (req, res) => {
  try {
    const types = loadJSON(TYPES_FILE) || [];
    const type = types.find(t => t.type_code === req.params.code);
    if (type) {
      res.json({ success: true, data: type });
    } else {
      res.status(404).json({ success: false, error: '类型不存在' });
    }
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});

// 前端路由（SPA 支持）
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/dist/index.html'));
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`🦞 性格测试服务器运行在 http://localhost:${PORT}`);
});
