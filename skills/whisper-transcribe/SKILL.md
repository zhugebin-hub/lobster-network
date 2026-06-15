---
name: whisper-transcribe
description: 语音识别与转录技能 - 使用 OpenAI Whisper 模型将音频文件转换为文字。支持多语言（中文/英文等），适用于会议记录、语音消息、采访等场景。
metadata:
  openclaw:
    emoji: "🎙️"
    os: [darwin, linux]
    requires:
      bins: [python3, ffmpeg]
      pip: [openai-whisper]
author: OpenClaw
version: 1.0.0
---

# 🎙️ Whisper 语音识别技能

**功能**: 使用 OpenAI Whisper 模型将音频文件转录为文字，支持多语言识别。

---

## 🎯 核心功能

### 1. 音频转录
- 支持 MP3, WAV, M4A, FLAC 等常见音频格式
- 自动检测语言（中文/英文/日文等）
- 高精度语音识别（Whisper Large 模型准确率>95%）

### 2. 多语言支持
- 中文（简体/繁体）
- 英文
- 日文
- 韩文
- 法语、德语、西班牙语等 99+ 语言

### 3. 智能分段
- 自动按句子分割
- 带时间戳
- 支持说话人区分（可选）

---

## 🔧 安装依赖

### 第一步：安装 Python 依赖

```bash
pip3 install openai-whisper --break-system-packages
```

或使用国内镜像：
```bash
pip3 install openai-whisper --break-system-packages --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 第二步：确认 ffmpeg 已安装

```bash
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt install ffmpeg

# Linux (CentOS/RHEL)
sudo yum install ffmpeg
```

---

## 📋 使用方法

### 方法 A：命令行调用

```bash
# 转录音频文件
python3 ~/.openclaw/workspace/skills/whisper-transcribe/scripts/transcribe.py /path/to/audio.mp3

# 指定语言
python3 ~/.openclaw/workspace/skills/whisper-transcribe/scripts/transcribe.py /path/to/audio.mp3 --language zh

# 输出带时间戳
python3 ~/.openclaw/workspace/skills/whisper-transcribe/scripts/transcribe.py /path/to/audio.mp3 --show-timestamps
```

### 方法 B：在 AI 对话中使用

当用户上传音频文件时，AI 会自动调用此技能：

**用户**: [上传音频文件] 帮我转录这个会议录音

**AI**: 
```
正在使用 Whisper 转录音频...
[执行转录脚本]
✅ 转录完成！

=== 会议记录 ===
[转录文本内容]
```

### 方法 C：批量处理

```bash
# 转录整个文件夹的音频
for file in ~/recordings/*.mp3; do
  python3 ~/.openclaw/workspace/skills/whisper-transcribe/scripts/transcribe.py "$file" --output-dir ~/transcripts
done
```

---

## 📊 模型选择

Whisper 提供多种模型，按准确度/速度权衡：

| 模型 | 参数量 | 中文准确率 | 速度 | 显存需求 |
|------|--------|-----------|------|---------|
| tiny | 39M | ~85% | 最快 | ~1GB |
| base | 74M | ~88% | 快 | ~1GB |
| small | 244M | ~92% | 中等 | ~2GB |
| medium | 769M | ~95% | 慢 | ~5GB |
| large | 1550M | ~97% | 最慢 | ~10GB |

**推荐**: 
- 日常使用：`small` 或 `medium`
- 重要会议：`large`
- 快速测试：`base`

---

## 🔧 配置选项

编辑 `config.json`（可选）:

```json
{
  "model": "medium",
  "language": "zh",
  "output_format": "text",
  "show_timestamps": true,
  "output_dir": "~/transcripts"
}
```

---

## 📁 输出格式

### 纯文本输出
```
这是转录的文本内容。
会议讨论了以下几个问题...
```

### JSON 输出（带时间戳）
```json
{
  "text": "完整转录文本",
  "segments": [
    {
      "start": 0.0,
      "end": 5.2,
      "text": "这是第一句话。"
    },
    {
      "start": 5.2,
      "end": 10.8,
      "text": "这是第二句话。"
    }
  ]
}
```

### SRT 字幕格式
```
1
00:00:00,000 --> 00:00:05,200
这是第一句话。

2
00:00:05,200 --> 00:00:10,800
这是第二句话。
```

---

## 🎯 使用场景

### 场景 1：会议记录
用户上传会议录音 → 自动转录 → 生成会议纪要

### 场景 2：采访整理
记者上传采访音频 → 转录为文字 → 编辑成文章

### 场景 3：学习笔记
学生上传课程录音 → 转录 → 整理为复习材料

### 场景 4：语音消息处理
接收长语音消息 → 转录为文字 → 快速浏览

---

## ⚠️ 注意事项

1. **处理时间**: 长音频（>30 分钟）可能需要较长时间
   - 60 分钟音频 ≈ 5-10 分钟处理时间（取决于模型）

2. **显存要求**: 
   - `large` 模型需要约 10GB 显存（GPU）或 16GB 内存（CPU）
   - 如无 GPU，建议使用 `small` 或 `medium` 模型

3. **音频质量**: 
   - 背景噪音会影响识别准确率
   - 建议使用清晰的录音

4. **隐私安全**: 
   - 所有处理在本地完成，不会上传到云端
   - 适合处理敏感内容

---

## 🛠️ 故障排查

### 问题 1：安装失败
```bash
# 清理缓存重试
pip3 cache purge
pip3 install openai-whisper --break-system-packages

# 或使用 conda
conda install -c conda-forge openai-whisper
```

### 问题 2：内存不足
```bash
# 使用更小的模型
python3 scripts/transcribe.py audio.mp3 --model base
```

### 问题 3：识别准确率低
```bash
# 指定语言
python3 scripts/transcribe.py audio.mp3 --language zh

# 使用更大的模型
python3 scripts/transcribe.py audio.mp3 --model large
```

### 问题 4：处理速度慢
```bash
# 使用 GPU 加速（如有 NVIDIA 显卡）
pip3 install openai-whisper[gpu]

# 或使用更小的模型
python3 scripts/transcribe.py audio.mp3 --model small
```

---

## 📚 示例脚本

### transcribe.py
```python
#!/usr/bin/env python3
import whisper
import sys
import json

def transcribe(audio_path, model_name="medium", language=None):
    # 加载模型
    print(f"加载 {model_name} 模型...")
    model = whisper.load_model(model_name)
    
    # 转录
    print("开始转录...")
    options = {}
    if language:
        options['language'] = language
    
    result = model.transcribe(audio_path, **options)
    
    # 输出结果
    print("\n=== 转录文本 ===")
    print(result['text'])
    
    # 保存 JSON
    with open(audio_path + '.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 结果已保存到 {audio_path}.json")
    
    return result['text']

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法：python3 transcribe.py <音频文件> [--model 模型名] [--language 语言代码]")
        sys.exit(1)
    
    audio_path = sys.argv[1]
    model_name = "medium"
    language = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--model' and i + 1 < len(sys.argv):
            model_name = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--language' and i + 1 < len(sys.argv):
            language = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    transcribe(audio_path, model_name, language)
```

---

## 📚 相关资源

- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [Whisper 模型说明](https://github.com/openai/whisper#available-models-and-languages)
- [Hugging Face Whisper](https://huggingface.co/openai/whisper-large-v3)

---

**技能版本**: 1.0.0  
**最后更新**: 2026-04-10  
**依赖**: Python 3.8+, openai-whisper, ffmpeg
