---
name: token-tracker
description: "记录和追踪 OpenClaw 会话的 token 消耗，提供每日、每周和累计统计，并提出节省 token 的建议。Use when: user asks about token consumption, needs to monitor token usage, or wants token saving suggestions."
homepage: https://github.com/openclaw/openclaw
metadata: { "openclaw": { "emoji": "📊", "install": [{ "id": "npm", "kind": "npm", "package": "tsx", "bins": ["tsx"], "label": "Install tsx (npm)" }] } }
---

# Token Tracker

记录和追踪 OpenClaw 会话的 token 消耗，提供每日、每周和累计统计，并提出节省 token 的建议。

## 当使用此技能时

当用户询问 token 消耗统计、需要监控 token 使用情况、或希望获得节省 token 的建议时使用此技能。

## 快速开始

```bash
# 使用全局命令
token-tracker today
token-tracker w
token-tracker a
token-tracker h
token-tracker s
token-tracker i

# 或使用 npm scripts
cd ~/.openclaw/skills/token-tracker
npm run token:today
npm run token:w
npm run token:a
npm run token:h
npm run token:s
npm run token:i
```

## 数据存储

Token 数据存储在 `~/.openclaw/skills/token-tracker/data/token-history.json`

## 节省 Token 的建议

- 使用 `memory_search` 而不是重复搜索
- 使用 `memory_get` 获取特定部分
- 避免重复读取 MEMORY.md
- 合并多个工具调用
- 减少日志输出
- 使用更精确的搜索词
- 定期清理不必要的历史

## 注意事项

1. Token 记录是近似值，可能略有偏差
2. 不同模型的 token 消耗不同
3. 建议定期备份 token 历史数据
