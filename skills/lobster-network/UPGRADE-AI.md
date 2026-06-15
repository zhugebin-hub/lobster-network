# 🦞 虾尔 AI 升级指南

让虾尔从"笨笨的关键词机器人"变成"真正听懂人话的智能助手"！

---

## ✨ 升级后虾尔的新能力

| 之前 | 现在 |
|------|------|
| 只会关键词匹配 | 能理解自然语言 |
| 记不住你说的话 | 有对话上下文记忆 |
| 回复死板 | 说话可爱有趣 |
| 无法执行任务 | 能理解任务并执行 |

---

## 🚀 快速配置（3 步搞定）

### 步骤 1：配置钉钉 Webhook

获取你的钉钉机器人 Webhook：
1. 打开钉钉群 → 群设置 → 智能助手 → 添加机器人
2. 复制 Webhook 地址

```bash
# 添加到 ~/.bashrc
export LOBSTER_DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=你的 token"
export LOBSTER_BOT_ID="lobster-001"
```

### 步骤 2：测试 AI 回复

```bash
cd ~/.openclaw/workspace/skills/lobster-network

# 测试 AI 回复
LOBSTER_BOT_ID=lobster-001 \
LOBSTER_DINGTALK_WEBHOOK="你的 webhook" \
./lobster-ai-reply.sh "帮我记住明天要开会"
```

### 步骤 3：配置自动轮询

```bash
# 编辑 crontab
crontab -e

# 添加（每分钟轮询一次）：
*/1 * * * * cd ~/.openclaw/workspace/skills/lobster-network && \
  LOBSTER_BOT_ID=lobster-001 \
  LOBSTER_DINGTALK_WEBHOOK="你的 webhook" \
  ./lobster-dingtalk.sh poll >> ~/lobster-network.log 2>&1
```

---

## 📁 文件说明

```
lobster-network/
├── lobster-ai-reply.sh      # 🆕 AI 智能回复脚本
├── lobster-dingtalk.sh      # 钉钉集成脚本（已更新）
├── lobster-context.json     # 🆕 对话上下文（自动创建）
├── lobster-memory.md        # 🆕 长期记忆（自动创建）
└── UPGRADE-AI.md            # 本文件
```

---

## 🧠 记忆系统

### 对话上下文（lobster-context.json）
- 自动记录最近 20 条对话
- 让虾尔能理解"刚才说的"、"之前提到的"

### 长期记忆（lobster-memory.md）
- 记录主人说的重要事情
- 手动查看：`cat ~/lobster-memory.md`

---

## 🎯 虾尔能听懂的话

### 任务类
- "帮我记住..."
- "别忘了..."
- "明天要..."
- "提醒我..."

### 查询类
- "之前说过什么"
- "我刚才让你..."
- "你还记得吗"

### 日常对话
- "你好" / "早" / "嗨"
- "拜拜" / "再见"
- "你真棒" / "好聪明"

---

## 🔧 故障排查

### 虾尔还是不回复？
```bash
# 1. 检查 Webhook 配置
echo $LOBSTER_DINGTALK_WEBHOOK

# 2. 测试脚本
./lobster-ai-reply.sh "测试"

# 3. 查看日志
tail -f ~/lobster-network.log
```

### 虾尔回复很奇怪？
```bash
# 查看对话历史
cat ~/lobster-context.json | jq .

# 清空上下文重新开始
echo '{"conversations":[]}' > ~/lobster-context.json
```

---

## 🎨 自定义虾尔性格

编辑 `lobster-ai-reply.sh` 中的提示词部分：

```bash
# 修改这段来改变虾尔的性格
local prompt="你是虾尔，一只可爱的龙虾机器人🦞。
你的特点是：
- 说话简短有趣，带点虾虾的可爱
- 会记住主人说的话
- 认真完成任务
- 如果不懂就诚实说
```

---

## 📊 监控命令

```bash
# 查看虾尔状态
./lobster-dingtalk.sh status

# 查看记忆
cat ~/lobster-memory.md

# 查看对话历史
cat ~/lobster-context.json | jq .

# 清理旧消息
./lobster-dingtalk.sh cleanup
```

---

## 🎉 完成！

现在虾尔已经变聪明啦！试试对她说：
- "虾尔，帮我记住明天下午 3 点开会"
- "你还记得我刚才说什么吗"
- "帮我做 XXX 任务"

她会认真听你说的每句话哦！🦞💕
