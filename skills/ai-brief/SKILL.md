# AI Brief - 定时简报系统

信电大虾 AI 简报生成器，每天 9:00 自动推送全网热点资讯。

## 功能

- 🔍 **多源搜索**: 自动搜索 AI、科技、大模型等热点主题
- 📝 **智能摘要**: 生成结构化简报
- ⏰ **定时推送**: 每天 9:00 准时执行 (Asia/Shanghai)
- 📁 **历史存档**: 简报保存在 `memory/ai-briefs/` 目录

## 安装依赖

```bash
pip3 install --user apscheduler
```

## 使用方法

### 手动生成一次简报

```bash
cd /home/admin/.openclaw/workspace/skills/ai-brief/scripts
bash generate-brief.sh
```

### 启动定时调度器

```bash
cd /home/admin/.openclaw/workspace/skills/ai-brief/scripts
python3 brief-scheduler.py
```

### 后台运行（推荐）

```bash
# 使用 nohup 后台运行
nohup python3 brief-scheduler.py > /tmp/ai-brief.log 2>&1 &

# 查看日志
tail -f /tmp/ai-brief.log
```

## 配置

### 修改搜索主题

编辑 `scripts/brief-scheduler.py`，修改 `SEARCH_QUERIES` 列表：

```python
SEARCH_QUERIES = [
    "AI 人工智能 最新进展 2026",
    "科技新闻 热点 今日",
    # 添加你的主题...
]
```

### 修改推送时间

编辑 `brief-scheduler.py`，修改 Cron 表达式：

```python
# 每天 9:00
scheduler.add_job(job, CronTrigger(hour=9, minute=0), ...)

# 改为每天 8:30
scheduler.add_job(job, CronTrigger(hour=8, minute=30), ...)
```

## 推送配置

当前配置推送到：
- **群组**: 小龙虾测试群
- **频道**: DingTalk

需要在 OpenClaw 中配置目标群组的 channel ID。

## 文件结构

```
ai-brief/
├── SKILL.md              # 技能文档
├── scripts/
│   ├── generate-brief.sh # 简报生成脚本
│   └── brief-scheduler.py # 定时调度器
└── memory/ai-briefs/     # 简报存档目录
    ├── 2026-03-23.md
    └── ...
```

## 依赖

- Python 3.6+
- APScheduler
- Bash (用于 shell 脚本)

---

*信电学院数字守护者* 🦞⚡️
