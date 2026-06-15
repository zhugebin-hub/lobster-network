#!/bin/bash
# DingTalk Voice Skill Installer
# 安装钉钉语音对话技能

set -e

SKILL_NAME="dingtalk-voice"
SKILL_DIR="$HOME/.openclaw/workspace/skills/$SKILL_NAME"
EXT_DIR="$HOME/.openclaw/extensions/dingtalk"

echo "🎙️  钉钉语音对话技能安装脚本"
echo "================================"

# 1. 检查钉钉插件是否已安装
echo ""
echo "📦 检查钉钉插件..."
if [ ! -d "$EXT_DIR" ]; then
    echo "❌ 钉钉插件未安装"
    echo "请先安装钉钉插件："
    echo "  openclaw plugins install @soimy/dingtalk"
    exit 1
fi
echo "✅ 钉钉插件已安装"

# 2. 检查 node-edge-tts 依赖
echo ""
echo "🔊 检查 TTS 依赖..."
cd "$EXT_DIR"
if npm list node-edge-tts &>/dev/null; then
    echo "✅ node-edge-tts 已安装"
else
    echo "⚠️  node-edge-tts 未安装，正在安装..."
    npm install node-edge-tts opusscript
    echo "✅ TTS 依赖安装完成"
fi

# 3. 复制技能文件
echo ""
echo "📋 安装技能文件..."
if [ -d "$SKILL_DIR" ]; then
    echo "✅ 技能目录已存在：$SKILL_DIR"
else
    echo "⚠️  技能目录不存在，请手动创建"
    echo "技能文件位于：$HOME/.openclaw/workspace/skills/dingtalk-voice/SKILL.md"
fi

# 4. 验证安装
echo ""
echo "🔍 验证安装..."
cd "$EXT_DIR"
if npx node-edge-tts --help &>/dev/null; then
    echo "✅ TTS 引擎工作正常"
else
    echo "❌ TTS 引擎测试失败"
    exit 1
fi

# 5. 提供配置说明
echo ""
echo "================================"
echo "✅ 安装完成！"
echo ""
echo "📝 下一步配置："
echo ""
echo "1. 编辑 ~/.openclaw/openclaw.json，添加语音配置："
echo ""
echo '   {'
echo '     "channels": {'
echo '       "dingtalk": {'
echo '         "voiceEnabled": true,'
echo '         "voiceAutoReply": false,'
echo '         "voiceLanguage": "zh-CN",'
echo '         "voiceVoice": "zh-CN-XiaoxiaoNeural"'
echo '       }'
echo '     }'
echo '   }'
echo ""
echo "2. 重启 OpenClaw 网关："
echo "   openclaw gateway restart"
echo ""
echo "3. 使用方法："
echo "   - 发送消息时添加 asVoice=true 参数"
echo "   - 或在聊天中说'用语音回复'"
echo ""
echo "🎉 享受语音对话功能！"
echo ""
