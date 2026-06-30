---
name: dingtalk-voice
description: 钉钉语音对话技能 - 支持 TTS 语音输出和语音消息处理。让 AI 助手用语音回复钉钉消息。
metadata:
  openclaw:
    emoji: "🎙️"
    os: [darwin, linux, windows]
author: OpenClaw
version: 1.0.0
---

# 🎙️ 钉钉语音对话技能

**功能**: 为钉钉机器人添加 TTS 语音输出能力，支持将 AI 回复转换为语音消息发送

---

## 🎯 核心功能

### 1. TTS 语音输出
- 使用 **Microsoft Edge TTS** 引擎（已内置在钉钉插件依赖中）
- 支持多种语言和音色
- 自动生成语音消息并发送到钉钉

### 2. 语音消息发送
- 通过 `asVoice=true` 参数发送语音消息
- 支持 MP3、AMR、WAV 格式
- 最大 5MB 语音文件

### 3. 语音输入处理
- 钉钉自带语音识别（ASR）
- 自动接收并处理用户发送的语音消息
- 识别结果以文本形式传递给 AI

---

## 🔧 使用方法

### 方法 A：使用 `asVoice` 参数（推荐）

在发送消息时添加 `asVoice=true` 参数，系统会自动将文本转换为语音：

```json
{
  "action": "send",
  "to": "对话 ID",
  "message": "你好，这是语音回复",
  "asVoice": true
}
```

### 方法 B：使用 message 工具

在钉钉聊天中，AI 可以通过 message 工具发送语音：

```
message action=send target=对话 ID message="你好" asVoice=true
```

### 方法 C：自动生成语音回复

配置自动语音回复模式（见下方配置章节）

---

## 📋 配置选项

### 1. 启用自动语音回复

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "your_client_id",
      "clientSecret": "your_client_secret",
      "robotCode": "your_robot_code",
      "dmPolicy": "open",
      "groupPolicy": "open",
      "messageType": "markdown",
      
      // 🎙️ 语音相关配置
      "voiceEnabled": true,           // 启用语音回复
      "voiceAutoReply": false,        // 自动将所有回复转为语音
      "voiceLanguage": "zh-CN",       // TTS 语言：zh-CN, en-US, ja-JP 等
      "voiceVoice": "zh-CN-XiaoxiaoNeural", // TTS 音色
      "voiceRate": 1.0,               // 语速：0.5-2.0
      "voicePitch": 1.0               // 音调：0.5-2.0
    }
  }
}
```

### 2. TTS 音色选择

Microsoft Edge TTS 支持的常用中文音色：

| 音色代码 | 说明 |
|---------|------|
| `zh-CN-XiaoxiaoNeural` | 女声，温暖亲切（推荐） |
| `zh-CN-YunxiNeural` | 男声，沉稳专业 |
| `zh-CN-YunjianNeural` | 男声，运动激情 |
| `zh-CN-XiaoyiNeural` | 女声，可爱活泼 |
| `zh-CN-liaoning-XiaobeiNeural` | 东北口音 |
| `zh-CN-shaanxi-XiaoniNeural` | 陕西口音 |

英文音色：
| 音色代码 | 说明 |
|---------|------|
| `en-US-JennyNeural` | 女声，友好（推荐） |
| `en-US-GuyNeural` | 男声，专业 |
| `en-GB-SoniaNeural` | 英式女声 |

完整音色列表参考：https://speech.microsoft.com/portal/voicegallery

---

## 🎯 使用场景

### 场景 1：手动发送语音消息

当用户要求"用语音回复"或"发语音"时：

```
好的，我用语音回复你：

[系统自动将以下消息转为语音发送]
"这是语音回复内容"
```

实际操作：
```
message action=send target="用户 ID" message="这是语音回复内容" asVoice=true
```

### 场景 2：自动语音回复模式

启用 `voiceAutoReply: true` 后，所有 AI 回复都会自动转为语音消息。

适合场景：
- 驾驶/运动场景
- 视障用户
- 语音交互优先的场景

### 场景 3：多语言语音

配置不同语言的音色：

```json
{
  "voiceLanguage": "en-US",
  "voiceVoice": "en-US-JennyNeural"
}
```

---

## 🔍 技术实现

### TTS 引擎

本技能使用 **node-edge-tts**（Microsoft Edge TTS 的 Node.js 封装）：

- **无需 API 密钥** - 免费使用
- **高质量语音** - 神经网络 TTS
- **多语言支持** - 100+ 语言
- **本地生成** - 隐私安全

### 语音消息流程

```
用户发送文本消息
    ↓
AI 生成回复文本
    ↓
TTS 引擎转换为音频 (MP3)
    ↓
上传到钉钉媒体服务器
    ↓
发送语音消息给用户
```

### 语音消息格式

钉钉语音消息要求：
- 格式：MP3, AMR, WAV
- 大小：≤ 5MB
- 时长：≤ 60 秒（推荐）

---

## ⚠️ 注意事项

1. **语音文件大小**：超过 5MB 会自动拒绝，建议控制回复长度
2. **网络依赖**：TTS 需要访问 Microsoft Edge 服务
3. **语音时长**：建议单条语音不超过 60 秒
4. **自动模式慎用**：`voiceAutoReply: true` 会增加响应时间和流量

---

## 🛠️ 故障排查

### 问题 1：语音消息发送失败

**检查**：
- 钉钉插件版本 ≥ 3.2.0
- node-edge-tts 已安装：`npm list node-edge-tts`
- 网络连接正常

**解决**：
```bash
cd ~/.openclaw/extensions/dingtalk
npm install node-edge-tts
openclaw gateway restart
```

### 问题 2：TTS 生成失败

**检查**：
- 能否访问 `speech.platform.bing.com`
- 防火墙/代理设置

**解决**：
```bash
# 测试 Edge TTS 连接
npx node-edge-tts --text "测试" --voice zh-CN-XiaoxiaoNeural --output /tmp/test.mp3
```

### 问题 3：语音识别不工作

钉钉自带 ASR，如果语音识别不工作：

**检查**：
- 钉钉机器人权限（需要语音消息权限）
- 语音消息格式是否正确

---

## 📚 相关资源

- [钉钉插件文档](https://github.com/soimy/openclaw-channel-dingtalk)
- [Edge TTS 音色列表](https://speech.microsoft.com/portal/voicegallery)
- [node-edge-tts](https://www.npmjs.com/package/node-edge-tts)
- [钉钉语音消息 API](https://open.dingtalk.com/document/robots/send-voice-messages)

---

## 🎉 示例对话

**用户**: 用语音告诉我今天的天气

**AI**: 好的，我用语音回复你：
```
[发送语音消息]
"今天北京晴朗，气温 15 到 25 度，适合外出活动。"
```

**用户**: 发语音

**AI**: 
```
[发送语音消息]
"这是你要的语音消息，有什么其他需要帮助的吗？"
```

---

**技能版本**: 1.0.0  
**最后更新**: 2026-04-01  
**依赖**: @soimy/dingtalk ≥ 3.2.0, node-edge-tts ≥ 1.2.10
