# 🧹 磁盘清理方案

**日期：** 2026-05-06
**当前状态：** 89%（33G/40G），剩余 4.4G

---

## 📊 磁盘空间分布

| 目录 | 大小 | 说明 |
|------|------|------|
| /home/admin | 14G | 用户数据（workspace 1.6G, media 1.4G, agents 179M） |
| /home/linuxbrew | 8.2G | Homebrew 包管理器（系统级依赖） |
| /opt/openclaw | 2.5G | OpenClaw 本体（node_modules 2.4G） |
| /usr | 5.5G | 系统文件 |
| /var | 605M | 日志+缓存 |
| /tmp | 385M | 临时文件 |
| /boot | 178M | 启动文件 |

---

## 🗑️ 可清理项目（按优先级）

### 🔴 高优先级（安全，立即执行）

#### 1. /var/cache/dnf — 204M
```bash
sudo dnf clean all
```
**风险：** 无。只是包管理器缓存，不影响已安装的包。

#### 2. /var/log/messages 旧日志 — ~25M
```bash
sudo journalctl --vacuum-size=50M   # 压缩journal日志到50M
sudo truncate -s 0 /var/log/messages # 清空messages日志
```
**风险：** 低。保留最近日志。

#### 3. /tmp 残留临时文件 — ~200M
```bash
rm -rf /tmp/node_modules /tmp/node-compile-cache /tmp/jiti
rm -rf /tmp/pip-build-env-* /tmp/pip-unpack-* /tmp/tmp*
rm -rf /tmp/pandoc_base /tmp/output_* /tmp/template_extracted
```
**风险：** 无。都是已完成的临时文件。

#### 4. /home/admin/.openclaw/media/inbound — 1.4G（820个文件）
- 已清理30天前的（144M）
- 建议定期清理超过7天的文件
```bash
find /home/admin/.openclaw/media/inbound/ -type f -mtime +7 -delete
```
**风险：** 低。这是钉钉消息附件缓存，OpenClaw 会自动重新下载需要的文件。

---

### 🟡 中优先级（需要确认）

#### 5. /home/admin/.openclaw/agents/main/sessions — 179M
- OpenClaw 会话历史缓存
- 定期清理超过30天的会话数据

#### 6. /home/admin/.openclaw/browser/openclaw — 84M
- 浏览器缓存数据
- 可安全清理

#### 7. 工作区旧项目目录
以下目录如果不再使用，可删除：
- `llm-enhanced-rumor-detection/`（70M）— 包含54M数据集
- `心理调研大赛复赛/`（91M）— 比赛相关
- `zhugebin-news/`（104M）— 新闻相关
- `teaching_cases/`（111M）— 教学案例（部分可能已归档）
- `video_frames/`（36M）+ `apriori_video_frames/`（30M）— 视频帧提取缓存

---

### 🟢 低优先级（谨慎操作）

#### 8. /home/linuxbrew — 8.2G
- Homebrew 包管理器，包含系统依赖
- **不建议删除**，但可以用 `brew cleanup` 清理旧版本
```bash
brew cleanup
```

#### 9. /opt/openclaw/node_modules — 2.4G
- OpenClaw 核心依赖，**不能删除**

---

## 🔄 持续清理策略

### 自动清理脚本（建议加入 cron）

```bash
#!/bin/bash
# /home/admin/.openclaw/workspace/scripts/daily-cleanup.sh

# 1. 清理7天前的media缓存
find /home/admin/.openclaw/media/inbound/ -type f -mtime +7 -delete

# 2. 清理/tmp下超过3天的临时文件
find /tmp -maxdepth 2 -type d -mtime +3 -name "pip-*" -exec rm -rf {} + 2>/dev/null
find /tmp -maxdepth 1 -type d -mtime +3 -name "output_*" -exec rm -rf {} + 2>/dev/null

# 3. 清理系统日志
journalctl --vacuum-size=50M 2>/dev/null

# 4. 清理dnf缓存（每周）
if [ "$(date +%u)" -eq 7 ]; then
  sudo dnf clean all 2>/dev/null
fi

echo "[$(date)] Daily cleanup done" >> /home/admin/.openclaw/workspace/memory/disk-cleanup.log
```

### 磁盘监控告警

建议设置告警：
- 使用率 > 85%：提醒
- 使用率 > 90%：警告
- 使用率 > 95%：紧急

---

## 📋 推荐执行顺序

### 立即可做（释放 ~500M）：
1. `sudo dnf clean all` → 204M
2. 清理 /tmp 残留 → ~200M
3. 清理 /var/log → ~25M

### 本周内做（释放 ~300M）：
4. 清理旧 video_frames → 66M
5. 清理不用的项目目录 → 按需

### 长期策略：
6. 设置每日自动清理 cron
7. 设置磁盘告警

---

**最后更新：** 2026-05-06
