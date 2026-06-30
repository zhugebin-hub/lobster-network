const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA_FILE = path.join(__dirname, 'lottery-data.json');

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// 初始化数据文件
if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify({
        participants: [],
        winners: [],
        status: 'registering',
        lastUpdated: new Date().toISOString()
    }, null, 2));
}

// 读取数据
function readData() {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('读取数据失败:', error);
        return {
            participants: [],
            winners: [],
            status: 'registering',
            lastUpdated: new Date().toISOString()
        };
    }
}

// 保存数据
function saveData(data) {
    data.lastUpdated = new Date().toISOString();
    fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
    return data;
}

// API 路由

// 获取所有数据
app.get('/api/data', (req, res) => {
    const data = readData();
    res.json(data);
});

// 添加报名
app.post('/api/register', (req, res) => {
    const { name, phone, address } = req.body;
    
    if (!name || !phone || !address) {
        return res.status(400).json({ error: '请填写完整信息' });
    }
    
    const data = readData();
    
    // 检查是否已报名
    if (data.participants.some(p => p.name === name && p.phone === phone)) {
        return res.status(400).json({ error: '该用户已报名' });
    }
    
    const participant = {
        id: Date.now(),
        name,
        phone,
        address,
        registeredAt: new Date().toISOString()
    };
    
    data.participants.push(participant);
    saveData(data);
    
    res.json({ success: true, participant });
});

// 添加中奖者
app.post('/api/winner', (req, res) => {
    const { participantId } = req.body;
    
    const data = readData();
    const participant = data.participants.find(p => p.id === participantId);
    
    if (!participant) {
        return res.status(400).json({ error: '参与者不存在' });
    }
    
    if (data.winners.some(w => w.id === participantId)) {
        return res.status(400).json({ error: '该用户已中奖' });
    }
    
    const winner = {
        ...participant,
        wonAt: new Date().toISOString()
    };
    
    data.winners.push(winner);
    saveData(data);
    
    res.json({ success: true, winner });
});

// 更新状态
app.put('/api/status', (req, res) => {
    const { status } = req.body;
    
    if (!['registering', 'drawing', 'completed'].includes(status)) {
        return res.status(400).json({ error: '无效的状态' });
    }
    
    const data = readData();
    data.status = status;
    saveData(data);
    
    res.json({ success: true, status });
});

// 清空数据
app.delete('/api/data', (req, res) => {
    const data = {
        participants: [],
        winners: [],
        status: 'registering',
        lastUpdated: new Date().toISOString()
    };
    saveData(data);
    res.json({ success: true });
});

// 导出 JSON
app.get('/api/export', (req, res) => {
    const data = readData();
    res.json(data);
});

// 启动服务器
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🦞 小龙虾网络抽奖服务运行在 http://0.0.0.0:${PORT}`);
    console.log(`📊 管理员后台: http://0.0.0.0:${PORT}/admin.html`);
});