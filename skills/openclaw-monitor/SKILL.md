# OpenClaw Monitor - 信息速递监控

每 12 小时自动搜索 OpenClaw 最新动态，为教材编写提供"信息速递"板块素材。

## 功能

- 🔍 **多源搜索**: 自动搜索 OpenClaw 相关新闻、更新、社区动态
- 📝 **智能整理**: 生成结构化简报，标注教材编写建议
- ⏰ **定时更新**: 每 12 小时自动执行
- 📁 **历史存档**: 简报保存在 `memory/openclaw-monitor/` 目录

## 安装依赖

```bash
pip3 install --user apscheduler
```

## 使用方法

### 启动监控器

```bash
cd /home/admin/.openclaw/workspace/skills/openclaw-monitor/scripts
python3 monitor-scheduler.py
```

### 后台运行（推荐）

```bash
# 使用 nohup 后台运行
nohup python3 monitor-scheduler.py > /tmp/openclaw-monitor.log 2>&1 &

# 查看日志
tail -f /tmp/openclaw-monitor.log

# 停止服务
kill $(cat /tmp/openclaw-monitor.pid)
```

### 手动生成一次简报

```bash
cd /home/admin/.openclaw/workspace/skills/openclaw-monitor/scripts
python3 -c "from monitor_scheduler import job; job()"
```

## 配置

### 修改搜索主题

编辑 `scripts/monitor-scheduler.py`，修改 `SEARCH_QUERIES` 列表：

```python
SEARCH_QUERIES = [
    "OpenClaw AI agent framework latest news",
    "OpenClaw clawhub skills update",
    # 添加你的主题...
]
```

### 修改更新频率

编辑 `monitor-scheduler.py`，修改 IntervalTrigger 参数：

```python
# 每 12 小时
scheduler.add_job(job, IntervalTrigger(hours=12), ...)

# 改为每 6 小时
scheduler.add_job(job, IntervalTrigger(hours=6), ...)
```

## 推送配置

当前配置推送到：
- **群组**: 小龙虾测试群
- **频道**: DingTalk
- **Channel ID**: `cidrMRsnzVf/TnyxtvMp9MnrQ==`

## 文件结构

```
openclaw-monitor/
├── SKILL.md                      # 技能文档
├── scripts/
│   └── monitor-scheduler.py      # 定时调度器
└── memory/openclaw-monitor/      # 简报存档目录
    ├── 2026-03-23.md
    └── ...
```

## 搜索主题

1. OpenClaw AI agent framework latest news
2. OpenClaw clawhub skills update
3. OpenClaw new features 2026
4. OpenClaw GitHub repository update
5. AI agent automation framework news
6. OpenClaw documentation tutorial
7. OpenClaw community discord update
8. OpenClaw dingtalk telegram integration

## 依赖

- Python 3.6+
- APScheduler
- OpenClaw message 工具（推送用）

---

*信电学院数字守护者* 🦞⚡️
