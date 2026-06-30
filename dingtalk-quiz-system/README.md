# 📚 钉钉题库考试系统

## 功能特点

- ✅ **随机出题** - 支持按分类、难度随机组卷
- ✅ **即时评分** - 提交后立即出分，显示答题详情
- ✅ **题库管理** - 添加、删除题目，支持批量导入
- ✅ **考试记录** - 自动保存所有考试记录，支持查询
- ✅ **本地存储** - 使用 JSON 文件存储，无需额外数据库
- ✅ **响应式设计** - 支持电脑和手机访问

## 快速开始

### 1. 安装依赖

```bash
cd dingtalk-quiz-system
npm install
```

### 2. 初始化题库（添加示例题目）

```bash
npm run init
```

### 3. 启动系统

```bash
npm start
```

### 4. 访问系统

打开浏览器访问：http://localhost:3000

## 系统架构

```
dingtalk-quiz-system/
├── server.js          # 主服务器
├── package.json       # 项目配置
├── init-db.js         # 初始化脚本
├── public/
│   └── index.html     # 前端界面
├── data/
│   ├── questions.json # 题库数据
│   └── exams.json     # 考试记录
└── README.md          # 说明文档
```

## API 接口

### 题目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/questions | 获取题目列表 |
| POST | /api/questions | 添加题目 |
| POST | /api/questions/batch | 批量导入题目 |
| DELETE | /api/questions/:id | 删除题目 |
| GET | /api/categories | 获取题目分类 |

### 考试功能

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/exam/generate | 随机出题 |
| POST | /api/exam/submit | 提交考试 |
| GET | /api/exams | 获取考试记录 |

## 题目格式

### 单题添加

```json
{
  "category": "道教理论",
  "question": "《道德经》的作者是谁？",
  "options": ["A. 庄子", "B. 老子", "C. 列子", "D. 文子"],
  "answer": "B",
  "explanation": "《道德经》相传为老子（李耳）所著",
  "difficulty": 1  // 1-简单，2-中等，3-困难
}
```

### 批量导入

```json
[
  {
    "category": "道教理论",
    "question": "题目内容",
    "options": ["A. 选项 A", "B. 选项 B", "C. 选项 C", "D. 选项 D"],
    "answer": "A",
    "explanation": "解析内容",
    "difficulty": 2
  }
]
```

## 钉钉集成

### 方式一：网页嵌入

将系统部署到服务器后，在钉钉群中发送链接即可访问。

### 方式二：机器人推送

可以通过钉钉机器人推送考试通知：

```javascript
// 示例：推送考试通知
fetch('https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    msgtype: 'markdown',
    markdown: {
      title: '📚 考试通知',
      text: '## 考试通知\n\n请各位学员点击链接参加测试：\n[点击考试](http://your-server:3000)'
    }
  })
});
```

## 自定义配置

### 修改端口

```bash
PORT=8080 npm start
```

### 数据备份

数据文件位于 `data/` 目录，直接复制即可备份。

## 技术栈

- **后端**：Node.js + Express
- **数据库**：JSON 文件存储
- **前端**：原生 HTML/CSS/JavaScript
- **部署**：无需额外依赖，开箱即用

## 常见问题

### Q: 如何导入大量题目？

使用批量导入接口，或使用 Excel 转换后通过 API 导入。

### Q: 数据会丢失吗？

不会，数据保存在 JSON 文件中，除非删除 `data/` 目录。

### Q: 可以多人同时使用吗？

可以，JSON 文件读写支持并发。

### Q: 如何部署到服务器？

```bash
# 使用 PM2 守护进程
npm install -g pm2
pm2 start server.js --name quiz-system
pm2 save
pm2 startup
```

## 许可证

MIT License

## 更新日志

### v1.0.0 (2026-05-25)
- ✅ 初始版本发布
- ✅ 随机出题功能
- ✅ 题库管理功能
- ✅ 考试记录功能
- ✅ 响应式前端界面
