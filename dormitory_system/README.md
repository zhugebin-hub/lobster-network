# 新生选寝系统 - 业务小龙虾版

## 快速启动

```bash
cd /home/admin/.openclaw/workspace/dormitory-system
python3 server.py
```

默认监听 `0.0.0.0:8765`

## 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| HOST | 0.0.0.0 | 监听地址 |
| PORT | 8765 | 监听端口 |

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/health | 健康检查 |
| GET | /api/demo | 示例数据 |
| POST | /api/match | 导入并匹配 |
| POST | /api/export | 导出 Excel |
| POST | /api/save_version | 保存版本 |
| POST | /api/list_versions | 列出版本 |
| POST | /api/restore_version | 恢复版本 |
| POST | /api/move_student | 移动学生 |
| POST | /api/swap_students | 互换学生 |
| POST | /api/move_to_suspended | 移入挂起池 |
| POST | /api/recompute_room | 重算房间风险 |

## 依赖

- Python 3.12+
- openpyxl

```bash
pip install openpyxl
```

## 目录结构

```
dormitory-system/
├── server.py           # 核心服务（HTTP + 匹配算法）
├── tools/
│   └── agent_tools.py  # 智能体工具层
├── data/
│   └── school_city_map.csv  # 院校-城市映射
├── static/             # 静态资源（HTML/CSS/JS）
├── versions/           # 版本存储
├── SYSTEM_PROMPT.md    # 小龙虾系统提示词
└── README.md           # 本文件
```
