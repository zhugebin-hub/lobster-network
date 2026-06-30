# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🦞 Lobster Network

- **机器人 ID**: lobster-001 (创始龙虾)
- **消息文件**: ~/.openclaw/workspace/lobster-messages.json
- **轮询间隔**: 30 秒
- **技能路径**: ~/.openclaw/workspace/skills/lobster-network/

## 📌 钉钉群配置

### 🦞一败涂地 群
- **群号**: 178415004647
- **群名**: 🦞一败涂地
- **规则**: 生成 PPT 时自动打包成 ZIP 发送
- **群文件**: 支持读取群聊中发送的文件

---

## 📅 中方课表转换工具

- **技能路径**: `~/.openclaw/workspace/skills/cn-to-uk-timetable/`
- **转换脚本**: `scripts/convert_cn_to_uk_timetable.py`
- **课程映射**: `assets/course_mapping.json`
- **使用方式**: 下次转换中方课表时，使用此脚本而非内联 Python 代码
- **命令示例**:
  ```bash
  python3 scripts/convert_cn_to_uk_timetable.py \
    --source-file "AII040-数字信号处理.xls" \
    --output "AII040_数字信号处理_英方课表.xlsx" \
    --log "AII040_数字信号处理_转换日志.json"
  ```

---

Add whatever helps you do your job. This is your cheat sheet.
