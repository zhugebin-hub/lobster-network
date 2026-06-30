# 🎭 性格测试应用

基于 MBTI 模型的 Web 性格测试应用，帮助用户了解自己的性格特点。

## 🚀 快速开始

### 1. 安装后端依赖

```bash
cd backend
npm install
npm run init-db  # 初始化数据库
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 启动服务

**终端 1 - 启动后端：**
```bash
cd backend
npm start
# 服务运行在 http://localhost:3000
```

**终端 2 - 启动前端开发服务器：**
```bash
cd frontend
npm run dev
# 服务运行在 http://localhost:5173
```

### 4. 访问应用

打开浏览器访问：http://localhost:5173

## 📁 项目结构

```
personality-test/
├── backend/
│   ├── server.js          # Express 服务器
│   ├── scripts/
│   │   └── init-db.js     # 数据库初始化脚本
│   └── data/
│       └── personality.db # SQLite 数据库
├── frontend/
│   ├── src/
│   │   ├── views/         # 页面组件
│   │   ├── components/    # 可复用组件
│   │   ├── stores/        # Pinia 状态管理
│   │   └── router/        # 路由配置
│   └── dist/              # 构建输出
└── README.md
```

## 🎯 功能特点

- ✅ 40 道精选题目，覆盖 4 个性格维度
- ✅ 实时进度显示
- ✅ 16 种性格类型详细分析
- ✅ 性格优势、劣势和职业建议
- ✅ 响应式设计，支持移动端
- ✅ 结果分享功能

## 🧩 性格维度

| 维度 | 两极 | 说明 |
|------|------|------|
| 能量来源 | E (外向) ←→ I (内向) | 你从哪里获得能量 |
| 信息处理 | N (直觉) ←→ S (感觉) | 你如何处理信息 |
| 决策方式 | T (理性) ←→ F (感性) | 你如何做决定 |
| 生活态度 | J (计划) ←→ P (灵活) | 你如何组织生活 |

## 🛠️ 技术栈

- **前端**: Vue 3 + Vite + Tailwind CSS
- **后端**: Node.js + Express
- **数据库**: SQLite
- **状态管理**: Pinia

## 📦 生产部署

### 构建前端

```bash
cd frontend
npm run build
```

### 部署后端

```bash
cd backend
npm install --production
npm start
```

访问 http://localhost:3000 即可使用生产版本。

## 📝 自定义

### 修改题目

编辑 `backend/scripts/init-db.js` 中的 `questions` 数组。

### 修改性格类型描述

编辑 `backend/scripts/init-db.js` 中的 `personalityTypes` 数组。

### 修改样式

编辑 `frontend/src/style.css` 和 `frontend/tailwind.config.js`。

## 🦞 开发说明

本项目由 诸葛虾（小龙虾）创建，遵循简洁、实用的原则。

## 📄 License

MIT
