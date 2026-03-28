---
name: token-monitor
description: 监控和报告 OpenClaw tokens 使用情况和成本
tags: [tokens, cost, monitoring, usage]
---

# 📊 Token Monitor - Tokens 监控技能

实时监控和报告 OpenClaw 的 tokens 使用情况和 API 成本。

## ✨ 功能

- **实时 tokens 统计** - 查看当前会话的 tokens 使用情况
- **成本估算** - 根据模型计算 API 成本
- **使用趋势** - 跟踪每日/每周 tokens 使用趋势
- **预算告警** - 设置预算上限，超出时发出警告
- **模型对比** - 比较不同模型的 tokens 使用效率

## 🔧 使用方法

### 查看当前会话状态

```bash
# 使用 session_status 工具
```

### 查询历史使用记录

查看 `memory/token-usage.json` 文件获取历史记录。

## 📈 数据记录

Tokens 使用数据自动记录到：
- `memory/token-usage.json` - 详细使用记录
- `memory/daily-cost.md` - 每日成本汇总

## 💰 成本计算

| 模型 | 输入价格 | 输出价格 |
|------|---------|---------|
| qwen3.5-plus | ¥0.004/1K | ¥0.012/1K |
| qwen3-max | ¥0.016/1K | ¥0.048/1K |
| gpt-4 | $0.03/1K | $0.06/1K |

## 📝 日志格式

```json
{
  "timestamp": "2026-03-23T06:00:00Z",
  "sessionKey": "agent:main:xxx",
  "model": "qwen3.5-plus",
  "inputTokens": 1000,
  "outputTokens": 500,
  "totalTokens": 1500,
  "estimatedCost": 0.01
}
```

---

**自动监控**: 每次会话结束后自动记录 tokens 使用情况
