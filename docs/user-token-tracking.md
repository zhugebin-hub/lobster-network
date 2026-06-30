# 👥 用户 Token 追踪方案

## 📁 文件结构

```
memory/
├── user-profiles.json      # 用户档案
├── token-usage.jsonl       # Token 使用日志 (增强版)
└── daily-cost.md           # 每日成本报告

scripts/
├── update-token-usage.sh   # Token 记录更新脚本
├── export-user-token-report.sh  # 报告导出脚本
└── ...

skills/token-monitor/scripts/
└── monitor-enhanced.sh     # 增强版监控脚本
```

## 🔧 使用方法

### 1. 记录 Token 使用

```bash
# 手动调用
./scripts/update-token-usage.sh \
  "086209361535510921" \
  "诸葛斌" \
  "dingtalk" \
  "group" \
  "cidAKHxc5pjaXCdR1I7T2k1uQ==" \
  "msgvZrN02cD5OM6QvFN2HRi5g==" \
  1200 800 \
  "qwen3.5-plus"
```

### 2. 生成报告

```bash
# 生成用户 Token 使用报告
./scripts/export-user-token-report.sh
```

### 3. 自动集成

在 OpenClaw 会话结束时自动调用：

```javascript
// 从 inbound context 提取用户信息
const userId = inbound.sender_id;
const userName = inbound.sender;
const channel = inbound.channel;
const chatType = inbound.chat_type;
const conversationId = inbound.conversationId;
const messageId = inbound.message_id;

// 调用更新脚本
exec(`./scripts/update-token-usage.sh ${userId} "${userName}" ...`);
```

## 📊 数据格式

### user-profiles.json

```json
{
  "users": {
    "086209361535510921": {
      "userId": "086209361535510921",
      "displayName": "诸葛斌",
      "firstSeen": "2026-03-29T07:14:00+08:00",
      "lastSeen": "2026-03-29T07:17:00+08:00",
      "channel": "dingtalk",
      "chatType": "group",
      "conversationId": "cidAKHxc5pjaXCdR1I7T2k1uQ==",
      "messageCount": 3,
      "totalTokens": 2000,
      "totalCost": 0.0144,
      "tags": ["教材编写", "群成员"]
    }
  },
  "lastUpdated": "2026-03-29T07:17:00+08:00"
}
```

### token-usage.jsonl

```json
{
  "timestamp": "2026-03-29T07:14:00+08:00",
  "sessionKey": "agent:main:dingtalk:group:cidAKHxc5pjaXCdR1I7T2k1uQ==",
  "model": "dashscope-coding/qwen3.5-plus",
  "inputTokens": 1200,
  "outputTokens": 800,
  "totalTokens": 2000,
  "estimatedCost": 0.0144,
  "userId": "086209361535510921",
  "userName": "诸葛斌",
  "channel": "dingtalk",
  "chatType": "group",
  "conversationId": "cidAKHxc5pjaXCdR1I7T2k1uQ==",
  "messageId": "msgvZrN02cD5OM6QvFN2HRi5g=="
}
```

## 📈 报告内容

- 👥 用户统计表格
- 📈 渠道分布
- 🔥 活跃用户 Top 10
- 💰 高消耗用户 Top 10

## 🔒 隐私注意

- 用户 ID 属于敏感信息
- 导出报告时可选择匿名化
- 遵守平台隐私政策

---

*创建时间：2026-03-29*
