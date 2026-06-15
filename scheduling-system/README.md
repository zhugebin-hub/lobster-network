# 学校排课系统 - Scheduling System

## 📖 项目简介

单机版学校排课系统，支持班级、教师、课程管理及自动排课功能。

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **GUI**: Tkinter (内置，无需额外安装)
- **数据库**: SQLite3 (内置)
- **算法**: 约束满足问题 (CSP)

## 📁 目录结构

```
scheduling-system/
├── src/                # 源代码
│   ├── main.py        # 主程序入口
│   ├── models.py      # 数据模型
│   └── scheduler.py   # 排课算法
├── ui/                 # 界面模块
│   ├── main_window.py # 主窗口
│   └── dialogs.py     # 对话框
├── utils/              # 工具函数
│   └── db.py          # 数据库操作
├── data/               # 数据存储
│   └── school.db      # SQLite 数据库
├── docs/               # 文档
└── README.md          # 说明文件
```

## 🚀 快速启动

```bash
cd scheduling-system
python src/main.py
```

## 📋 功能模块

1. **基础数据管理**
   - 班级管理
   - 教师管理
   - 课程设置
   - 会议时间设置

2. **排课功能**
   - 自动排课
   - 手动调整
   - 冲突检测

3. **查询导出**
   - 课表查询
   - 导出 Excel/PDF

## 👥 适用场景

- 中小学排课
- 培训机构课程安排
- 小型教育机构
