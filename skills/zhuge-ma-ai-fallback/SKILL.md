# 🐎 诸葛马 AI 回退 Skill

> 当诸葛马（Hermes）无法处理请求时，自动用 AI 生成回复并转发

## 触发条件

当用户在钉钉消息中以 `诸葛马` 开头时激活此 skill。

## 处理流程

### 1. 识别诸葛马请求
```
用户: 诸葛马，讲个笑话
```

### 2. 转发给 Hermes
```bash
python3 /shared/zhuge-ma-proxy-v2.py send "讲个笑话"
```

### 3. 处理回复

#### 情况 A：Hermes 正常回复（规则匹配成功）
- 直接转发给用户
- 示例：`诸葛马，现在几点了？` → Hermes 回复时间 → 转发

#### 情况 B：Hermes 兜底回复（规则匹配失败）
- 检测到兜底特征：`收到你的消息: 'xxx' ✅ Hermes已处理`
- **用 AI 生成回复**
- 转发 AI 回复给用户
- 附加说明：`（🤖 此回复由小龙虾 AI 代答）`

### 4. 回复格式

```
🐎 诸葛马回复：

[AI 生成的回复内容]

---
🤖 此回复由小龙虾 AI 代答（诸葛马暂不支持此类问题）
```

## 实现方式

### 方式一：直接处理（推荐）
在收到 `诸葛马，xxx` 消息时：
1. 调用 `python3 /shared/zhuge-ma-proxy-v2.py send "xxx"`
2. 解析返回结果
3. 如果是 `ai_fallback` 状态，用 AI 生成回复
4. 发送回复给用户

### 方式二：异步处理
1. 调用 proxy 发送请求
2. 立即回复用户：`🐎 诸葛马正在处理，请稍候...`
3. 后台监控 AI 回退标记
4. 收到 AI 回复后主动发送给用户

## 兜底检测特征

```python
FALLBACK_PATTERNS = [
    r"收到你的消息:.*Hermes已处理",
    r"收到指令:.*已处理",
]
```

## 配置文件

- 代理脚本：`/shared/zhuge-ma-proxy-v2.py`
- AI 回退处理器：`/shared/ai-fallback-handler.py`
- 消息目录：`/shared/messages/`
- 日志文件：`/shared/messages/zhuge-ma-proxy-v2.log`

## 测试命令

```bash
# 发送测试消息
python3 /shared/zhuge-ma-proxy-v2.py send "讲个笑话"

# 查看状态
python3 /shared/zhuge-ma-proxy-v2.py status
```

## 注意事项

1. Hermes 处理超时时间：30 秒
2. 如果超时，回复：`⏳ 诸葛马处理超时，请稍后重试`
3. AI 代答时保持诸葛马的语气风格
4. 记录所有交互到日志文件

---

**版本：** v2.0  
**维护者：** 小龙虾 - 诸葛虾  
**最后更新：** 2026-05-16
