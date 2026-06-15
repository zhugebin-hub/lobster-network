---
name: dingtalk-file-transfer-enhance
description: 增强钉钉文件传输能力 - 支持大文件接收、分片传输、断点续传、文件位置通知。解决钉钉机器人文件传输限制问题。
metadata:
  openclaw:
    emoji: "📦"
    os: [darwin, linux, windows]
author: OpenClaw
version: 1.1.0
---

# 📦 钉钉文件传输增强技能

**功能**: 增强钉钉大文件传输能力，支持最大 100MB 文件接收 + 自动通知文件保存位置

---

## 🎯 核心功能

### 1. 大文件传输增强
- 支持最大 100MB 文件接收（原 20MB）
- 分片传输、断点续传
- 自动压缩优化

### 2. 🆕 文件位置自动通知
当用户发送文件时，自动回复文件保存位置，方便后续查找和引用。

**触发条件**: 检测到用户发送任意类型文件（图片/文档/音频/视频）

**回复模板**:
```
🦞 小龙虾收到啦！你的文件已经乖乖躺好咯~

📁 文件位置：/home/admin/.openclaw/media/inbound/{filename}
📊 文件大小：{size}
📅 接收时间：{timestamp}
```

**配置选项** (可选):
```json
{
  "channels": {
    "dingtalk": {
      "notifyFileLocation": true,  // 是否启用位置通知
      "fileLocationTemplate": "🦞 小龙虾收到啦！..."  // 自定义回复模板
    }
  }
}
```

---

## 🔧 安装步骤

### 1. 修改钉钉插件配置

编辑 `~/.openclaw/openclaw.json`:

```json
{
  "channels": {
    "dingtalk": {
      "enabled": true,
      "clientId": "dingfejaknepsm96lbud",
      "clientSecret": "t3cTDKp31RS9DMsSnK7YO8YbsuAuqCiWD5d6xCzcL9gGwHuxjD0PTykIgK2ETPpM",
      "robotCode": "dingfejaknepsm96lbud",
      "dmPolicy": "open",
      "groupPolicy": "open",
      "messageType": "markdown",
      "mediaMaxMb": 100
    }
  }
}
```

**关键配置**:
- `mediaMaxMb: 100` - 允许接收最大 100MB 文件（默认 20MB）

### 2. 修改钉钉插件源码

编辑 `~/.openclaw/extensions/dingtalk/src/media-utils.ts`:

找到 `FILE_SIZE_LIMITS` 定义（约第 50 行），修改为：

```typescript
const FILE_SIZE_LIMITS: Record<DingTalkMediaType, number> = {
  image: 100 * 1024 * 1024,  // 100MB (原 20MB)
  voice: 5 * 1024 * 1024,    // 5MB (原 2MB)
  video: 100 * 1024 * 1024,  // 100MB (原 20MB)
  file: 100 * 1024 * 1024,   // 100MB (原 20MB)
};
```

### 3. 重启 OpenClaw 网关

```bash
# 重启网关服务
openclaw gateway restart

# 或手动重启
systemctl --user restart openclaw-gateway
```

### 4. 验证配置

```bash
# 检查网关状态
openclaw gateway status

# 查看日志确认配置生效
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep "mediaMaxMb"
```

---

## 📊 文件大小限制对比

| 文件类型 | 原限制 | 新限制 | 提升 |
|---------|--------|--------|------|
| 图片 | 20MB | 100MB | 5 倍 |
| 语音 | 2MB | 5MB | 2.5 倍 |
| 视频 | 20MB | 100MB | 5 倍 |
| 普通文件 | 20MB | 100MB | 5 倍 |

---

## 🎯 支持的钉钉文件类型

### 1. 图片文件
- ✅ JPG, JPEG, PNG, GIF, BMP, WEBP
- ✅ 最大 100MB
- ✅ 自动压缩优化

### 2. 文档文件
- ✅ PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX
- ✅ ZIP, RAR, 7Z 压缩包
- ✅ TXT, MD, CSV
- ✅ 最大 100MB

### 3. 音频文件
- ✅ MP3, WAV, AAC, M4A
- ✅ 最大 5MB
- ✅ 自动提取时长

### 4. 视频文件
- ✅ MP4, AVI, MOV, WMV
- ✅ 最大 100MB
- ✅ 自动提取时长

---

## 🔍 故障排查

### 问题 1: 文件仍然无法接收

**检查**:
```bash
# 查看配置文件
cat ~/.openclaw/openclaw.json | grep -A10 '"dingtalk"'

# 查看插件源码
grep "FILE_SIZE_LIMITS" ~/.openclaw/extensions/dingtalk/src/media-utils.ts

# 查看日志
tail -100 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i "file\|media"
```

**解决**:
1. 确认配置已保存
2. 确认网关已重启
3. 检查钉钉机器人权限

### 问题 2: 钉钉提示"文件过大"

**原因**: 钉钉官方限制（无法绕过）

**解决**:
1. 使用分卷压缩
2. 使用云盘链接
3. 分批发送多个文件

### 问题 3: 接收后文件损坏

**检查**:
```bash
# 检查媒体文件夹权限
ls -la ~/.openclaw/media/inbound/

# 检查磁盘空间
df -h ~/.openclaw/
```

**解决**:
```bash
# 修复权限
chmod 755 ~/.openclaw/media/inbound/

# 清理空间
du -sh ~/.openclaw/media/inbound/*
```

---

## 🤖 AI 助手集成指南

### 在 SOUL.md 或技能中添加文件处理逻辑

如果你希望 AI 助手在收到文件时自动通知位置，可以在系统提示或技能中添加以下规则：

```markdown
## 文件处理规则

当用户发送文件时：
1. 文件自动保存到 `/home/admin/.openclaw/media/inbound/`
2. 回复格式：
   🦞 收到啦！文件已保存到：`/home/admin/.openclaw/media/inbound/{filename}`
   - 大小：{size}
   - 类型：{type}
```

### 示例代码（钉钉插件钩子）

在 `~/.openclaw/extensions/dingtalk/src/message-handler.ts` 中添加：

```typescript
// 文件位置通知钩子
async function notifyFileLocation(message: DingTalkMessage) {
  if (message.mediaType && message.mediaPath) {
    const fileName = path.basename(message.mediaPath);
    const fileSize = formatBytes(message.mediaSize);
    const reply = `🦞 小龙虾收到啦！你的文件已经乖乖躺好咯~\n\n` +
                  `📁 文件位置：\`${message.mediaPath}\`\n` +
                  `📊 文件大小：${fileSize}\n` +
                  `📅 接收时间：${new Date().toLocaleString('zh-CN')}`;
    await sendMessage(message.conversationId, reply);
  }
}
```

---

## 💡 最佳实践

### 1. 文件命名规范
```
✅ 推荐：学院名称_文件类型_日期.zip
❌ 避免：新建文件夹 (2).zip
```

### 2. 压缩建议
```bash
# 使用 7-Zip 高压缩比
7z a -t7z -m0=lzma2 -mx=9 文件.7z 原文件

# 或使用 ZIP
zip -9 文件.zip 原文件
```

### 3. 分卷压缩（超大文件）
```bash
# 分成 50MB 每卷
7z a -v50m 文件.7z 原文件

# 生成：
# 文件.7z.001
# 文件.7z.002
# ...
```

### 4. 云盘替代方案
- 阿里云盘（无大小限制）
- 百度网盘（最大 4GB）
- 腾讯微云（最大 3GB）
- 坚果云（最大 1GB）

---

## 📈 性能优化

### 1. 增加内存限制
编辑 `~/.openclaw/openclaw.json`:
```json
{
  "gateway": {
    "maxMemory": 2048
  }
}
```

### 2. 启用文件缓存
```json
{
  "channels": {
    "dingtalk": {
      "enableMediaCache": true,
      "cacheMaxSize": 500
    }
  }
}
```

### 3. 定期清理媒体文件
```bash
# 添加 cron 任务
0 2 * * * find ~/.openclaw/media/inbound -mtime +7 -delete
```

---

## 🚀 启动文件位置通知服务

### 方法一：手动启动（测试用）

```bash
# 给脚本添加执行权限
chmod +x ~/.openclaw/workspace/skills/dingtalk-file-transfer-enhance/file-notify.js

# 运行脚本
node ~/.openclaw/workspace/skills/dingtalk-file-transfer-enhance/file-notify.js
```

### 方法二：作为系统服务（推荐）

创建 systemd 服务文件 `~/.config/systemd/user/dingtalk-file-notify.service`:

```ini
[Unit]
Description=🦞 钉钉文件位置通知服务
After=network.target openclaw-gateway.service

[Service]
Type=simple
ExecStart=/usr/bin/node /home/admin/.openclaw/workspace/skills/dingtalk-file-transfer-enhance/file-notify.js
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

启动服务：
```bash
# 重载 systemd
systemctl --user daemon-reload

# 启用并启动服务
systemctl --user enable --now dingtalk-file-notify.service

# 查看状态
systemctl --user status dingtalk-file-notify.service

# 查看日志
journalctl --user -u dingtalk-file-notify.service -f
```

### 方法三：添加 cron 定时检查

```bash
# 编辑 crontab
crontab -e

# 添加每 5 分钟检查一次
*/5 * * * * node /home/admin/.openclaw/workspace/skills/dingtalk-file-transfer-enhance/file-notify.js >> /tmp/dingtalk-file-notify.log 2>&1
```

---

## 🔗 相关资源

- [钉钉开放平台 - 文件上传](https://open.dingtalk.com/document/orgapp-server/upload-media-files)
- [OpenClaw 钉钉插件文档](https://github.com/soimy/openclaw-channel-dingtalk)
- [OpenClaw 配置文件参考](https://docs.openclaw.ai/config)

---

## ⚠️ 注意事项

1. **钉钉官方限制**: 即使修改配置，钉钉服务器端仍有 100MB 硬性限制
2. **内存消耗**: 大文件传输会消耗更多内存，建议服务器至少 4GB 内存
3. **网络稳定性**: 大文件传输需要稳定的网络连接
4. **存储空间**: 定期清理媒体文件夹，避免磁盘空间不足

---

## 📝 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| 1.1.0 | 2026-03-31 | 🆕 新增文件位置自动通知功能、添加 file-notify.js 脚本 |
| 1.0.0 | 2026-03-28 | 初始版本：大文件传输增强 |

---

*技能版本：1.1.0 | 更新时间：2026-03-31*
