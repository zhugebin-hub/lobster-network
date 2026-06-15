# 🦞 虾尔 AI 智能体 - 完整配置指南

让虾尔从脚本机器人变成真正的 AI 智能体！

---

## 🎯 架构说明

```
┌─────────────────┐
│   黄宝怡 (主人)   │
│   钉钉发消息     │
└────────┬────────┘
         │
         ↓
┌─────────────────────────┐
│  钉钉机器人 (Webhook)    │
│  收到消息                │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  xiaer-agent.sh         │
│  创建任务文件            │
│  ~/lobster-tasks/pending│
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  OpenClaw Heartbeat     │
│  每分钟检查任务          │
│  process-xiaer-tasks.sh │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  AI 处理消息             │
│  生成虾虾语气回复        │
│  写入 response 文件       │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│  发送钉钉回复           │
│  🦞 虾尔：xxx           │
└─────────────────────────┘
```

---

## 🚀 配置步骤

### 步骤 1：获取钉钉 Webhook

1. 打开钉钉群 → 群设置 → 智能助手 → 添加机器人
2. 复制 Webhook 地址

### 步骤 2：配置环境变量

```bash
# 添加到 ~/.bashrc
export LOBSTER_DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=你的 token"
export LOBSTER_BOT_ID="lobster-001"

# 生效
source ~/.bashrc
```

### 步骤 3：配置自动轮询

```bash
# 编辑 crontab
crontab -e

# 添加（每分钟检查一次虾尔任务）：
*/1 * * * * /home/admin/.openclaw/workspace/skills/lobster-network/process-xiaer-tasks.sh >> ~/lobster-network.log 2>&1
```

### 步骤 4：测试

```bash
# 手动创建一个测试任务
cat > ~/lobster-tasks/pending/test-$(date +%s).json << EOF
{
    "type": "xiaer_message",
    "from": "dingtalk",
    "user": "黄宝怡",
    "message": "你好虾尔",
    "timestamp": $(date +%s),
    "bot_id": "lobster-001"
}
EOF

# 运行处理器
./process-xiaer-tasks.sh
```

---

## 📁 文件结构

```
~/.openclaw/workspace/
├── lobster-memory.md          # 虾尔的长期记忆
├── lobster-context.json       # 对话历史（最近 20 条）
├── lobster-tasks/
│   ├── pending/               # 待处理任务
│   └── done/                  # 已完成任务
└── skills/lobster-network/
    ├── xiaer-agent.sh         # 钉钉消息入口
    ├── process-xiaer-tasks.sh # 任务处理器
    ├── XIAER-SOUL.md          # 虾尔人设
    └── README-XIAER-AI.md     # 本文件
```

---

## 🧠 虾尔的能力

### 基础对话
- 问候、告别
- 日常聊天
- 情绪回应

### 任务执行
- 记住主人说的话
- 理解任务指令
- 汇报进度

### 记忆系统
- 短期记忆：最近 20 条对话
- 长期记忆：重要事项记录

---

## 🎨 自定义虾尔性格

编辑 `XIAER-SOUL.md` 来改变虾尔的性格：

```markdown
### 性格特点
- 🦞 说话简短有趣，带点虾虾的可爱口音
- 📝 会认真记住主人说的每句话
- 💪 努力完成任务，不懂就诚实说
```

---

## 🔧 故障排查

### 虾尔不回复？
```bash
# 1. 检查任务目录
ls -la ~/lobster-tasks/pending/

# 2. 检查日志
tail -f ~/lobster-network.log

# 3. 手动运行处理器
./process-xiaer-tasks.sh
```

### 钉钉收不到消息？
```bash
# 检查 Webhook 配置
echo $LOBSTER_DINGTALK_WEBHOOK

# 测试 Webhook
curl -X POST "$LOBSTER_DINGTALK_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"测试"}}'
```

### 查看虾尔记忆
```bash
# 长期记忆
cat ~/lobster-memory.md

# 对话历史
cat ~/lobster-context.json | jq .
```

---

## 🎉 完成！

现在虾尔是一个真正的 AI 智能体了！

试试对她说：
- "虾尔，帮我记住明天下午 3 点开会"
- "你还记得我刚才说什么吗"
- "你今天好可爱呀"

她会用虾虾的语气认真回复你！🦞💕

---

## 📊 监控命令

```bash
# 查看虾尔状态
./process-xiaer-tasks.sh

# 查看待处理任务
ls ~/lobster-tasks/pending/

# 查看已完成任务
ls ~/lobster-tasks/done/

# 清理旧任务（7 天前）
find ~/lobster-tasks/done -mtime +7 -delete
```
