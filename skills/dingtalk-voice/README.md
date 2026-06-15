# 🎙️ 钉钉语音对话技能 (DingTalk Voice Skill)

为 OpenClaw 钉钉机器人添加 TTS 语音输出能力。

## 快速开始

### 1. 安装

```bash
# 运行安装脚本
~/.openclaw/workspace/skills/dingtalk-voice/install.sh
```

或手动安装：

```bash
# 确保钉钉插件已安装
openclaw plugins install @soimy/dingtalk

# 安装 TTS 依赖
cd ~/.openclaw/extensions/dingtalk
npm install node-edge-tts opusscript

# 重启网关
openclaw gateway restart
```

### 2. 配置

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "your_client_id",
      "clientSecret": "your_client_secret",
      "robotCode": "your_robot_code",
      
      // 语音配置
      "voiceEnabled": true,
      "voiceAutoReply": false,
      "voiceLanguage": "zh-CN",
      "voiceVoice": "zh-CN-XiaoxiaoNeural",
      "voiceRate": 1.0,
      "voicePitch": 1.0
    }
  }
}
```

### 3. 使用

#### 方法 A：使用 message 工具

```
message action=send target="对话 ID" message="你好" asVoice=true
```

#### 方法 B：在聊天中请求

用户说："用语音回复" 或 "发语音"

AI 会自动使用语音消息回复。

## 功能特性

- ✅ **TTS 语音输出** - 使用 Microsoft Edge TTS
- ✅ **多语言支持** - 中文、英文、日文等 100+ 语言
- ✅ **多种音色** - 男声、女声、方言等
- ✅ **自动语音识别** - 钉钉自带 ASR
- ✅ **无需 API 密钥** - 免费使用

## 音色选择

### 中文音色

| 音色 | 说明 |
|------|------|
| zh-CN-XiaoxiaoNeural | 女声，温暖亲切 ⭐推荐 |
| zh-CN-YunxiNeural | 男声，沉稳专业 |
| zh-CN-YunjianNeural | 男声，运动激情 |
| zh-CN-XiaoyiNeural | 女声，可爱活泼 |

### 英文音色

| 音色 | 说明 |
|------|------|
| en-US-JennyNeural | 女声，友好 ⭐推荐 |
| en-US-GuyNeural | 男声，专业 |
| en-GB-SoniaNeural | 英式女声 |

完整列表：https://speech.microsoft.com/portal/voicegallery

## 技术细节

- **TTS 引擎**: node-edge-tts (Microsoft Edge TTS)
- **语音格式**: MP3, AMR, WAV
- **文件大小**: ≤ 5MB
- **语音时长**: ≤ 60 秒（推荐）

## 故障排查

### TTS 测试

```bash
cd ~/.openclaw/extensions/dingtalk
npx node-edge-tts --text "测试" --voice zh-CN-XiaoxiaoNeural --output /tmp/test.mp3
```

### 检查依赖

```bash
npm list node-edge-tts
```

## 相关资源

- [完整技能文档](SKILL.md)
- [钉钉插件](https://github.com/soimy/openclaw-channel-dingtalk)
- [Edge TTS](https://www.npmjs.com/package/node-edge-tts)

## 许可证

MIT
