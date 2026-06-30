# Token 监控技能配置说明

## 已安装技能

| 技能 | 版本 | 用途 |
|------|------|------|
| **token-budget-monitor** | 1.0.0 | Token 预算控制与告警 |
| **token-tracker-v2** | 2.0.0 | Token 消耗统计与追踪 |

---

## 配置概览

### 每日限额
- **总限额**: 200,000 tokens/天
- **告警阈值**: 80% (160,000 tokens)

### 任务限额
| 任务 | 限额 (tokens) |
|------|--------------|
| AI 每日简报 (9:00) | 30,000 |
| OpenClaw 信息速递 (12h) | 40,000 |
| 日常推文 | 5,000 |
| RSS 简报 | 15,000 |
| OpenClaw 搜索 | 20,000 |
| 安全审计 | 10,000 |
| 问题研究 | 25,000 |

---

## 使用方法

### 查看今日消耗
```bash
cd /home/admin/.openclaw/workspace/skills/token-tracker-v2
npm run token:today
```

### 查看本周消耗
```bash
npm run token:w
```

### 查看累计消耗
```bash
npm run token:a
```

### 查看帮助
```bash
npm run token:h
```

---

## 定时报告

### 每日 Token 日报（21:00）
```bash
/home/admin/.openclaw/workspace/skills/token-budget-monitor/scripts/daily-token-report.sh
```

推送目标：
- 小龙虾测试群
- 🦀功能测试群

---

## 集成到定时任务

### AI 简报系统
在 `brief-scheduler.py` 中添加：
```python
# 任务完成后记录 token 消耗
def record_token_usage(input_tokens, output_tokens):
    subprocess.run([
        "node", "/home/admin/.openclaw/workspace/skills/token-budget-monitor/track-usage.js",
        "track", "ai-brief-daily",
        str(input_tokens), str(output_tokens), "dashscope-coding/qwen3.5-plus"
    ])
```

### OpenClaw 信息速递
在 `monitor-scheduler.py` 中添加：
```python
# 任务完成后记录 token 消耗
def record_token_usage(input_tokens, output_tokens):
    subprocess.run([
        "node", "/home/admin/.openclaw/workspace/skills/token-budget-monitor/track-usage.js",
        "track", "openclaw-monitor",
        str(input_tokens), str(output_tokens), "dashscope-coding/qwen3.5-plus"
    ])
```

---

## 节省 Token 建议

1. **使用 memory_search** - 避免重复搜索记忆文件
2. **使用 memory_get** - 精准获取特定部分
3. **避免重复读取** - 不要多次读取 MEMORY.md
4. **合并工具调用** - 减少 API 调用次数
5. **减少日志输出** - 精简不必要的日志
6. **精确搜索词** - 使用更具体的搜索关键词
7. **定期清理** - 删除不必要的历史记录

---

## 免费模型推荐

以下模型提供免费额度或低成本：

- `nvidia/moonshotai/kimi-k2.5`
- `google/gemini-2.0-flash-exp`
- `nvidia/deepseek-ai/deepseek-r1`
- `dashscope-coding/qwen3.5-plus` (当前使用)

---

## 告警配置

当 token 消耗达到 80% 时，系统会自动告警并推送到：
- 小龙虾测试群 (`cidrMRsnzVf/TnyxtvMp9MnrQ==`)
- 🦀功能测试群 (`cid2Qfigiuz0ILMHMkqbw7D0A==`)

---

*信电学院数字守护者* 🦞⚡️
