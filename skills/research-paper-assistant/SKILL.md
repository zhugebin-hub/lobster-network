# 科研论文辅助管理系统技能

## 触发词
`/research` `/论文` `/开题` `/文献` `/进度` `/反馈` `/export`

## 核心能力
1. **项目创建**：/create 题目 方向 → 生成项目目录+开题模板
2. **文献管理**：/upload 文件 分类 → 智能归档+Hermes分析
3. **进度跟踪**：/progress 项目ID → 展示阶段进度+待办事项
4. **导师反馈**：/feedback 意见 → 智能总结+任务分解
5. **版本控制**：/version 操作 → 快照/对比/回滚
6. **节点提醒**：自动监控阶段截止日，钉钉卡片推送
7. **数据导出**：/export 格式 → 生成结构化报表

## 工作流协议
1. 接收钉钉消息 → 解析意图 → 路由至对应模块
2. 涉及AI分析/生成 → 封装为 `zhuge-ma-request` 发送至 `/shared/messages/from-lobster/`
3. 轮询 `/shared/messages/from-hermes/` 获取AI结果
4. 更新 `/shared/research-paper/projects/{id}/project.json`
5. 推送钉钉卡片/提醒

## 文件结构
```
/shared/research-paper/
├── config.json          # 系统配置
├── templates/           # 开题/中期/答辩模板
├── projects/            # 各项目数据 (JSON+文件)
├── feedback/            # 导师意见归档
├── versions/            # 版本快照
└── logs/                # 系统日志
```

## 注意事项
- 所有路径使用相对路径或 `/shared/research-paper/` 绝对路径
- AI请求需包含 `project_id` 和 `task_type`
- 敏感数据（学生信息/成绩）需脱敏处理
