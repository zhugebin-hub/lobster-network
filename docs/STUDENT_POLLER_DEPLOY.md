# 学员端消息轮询脚本部署指南

## 📋 概述

`student_poller.py` 是小龙虾网络V4.0的核心组件，部署在每个学员节点上，实现：
- 自动从诸葛马服务器拉取新消息
- 处理训练任务、对局通知、系统通知
- 自动发送ACK回执
- 提交训练结果
- 清理已处理消息

## 🔧 部署步骤

### 1. 确保脚本存在
```bash
ls -la /home/admin/lobster-network/scripts/student_poller.py
```

### 2. 设置Cron定时任务
```bash
crontab -e
```

添加以下行（每5分钟执行一次）：
```
*/5 * * * * cd /home/admin/lobster-network && /usr/bin/python3 scripts/student_poller.py <node_id> >> /home/admin/lobster-network/poller_<node_id>.log 2>&1
```

替换 `<node_id>` 为：
- 小陈: `xiaochen`
- 诸葛虾: `zhuguxia`
- qoder: `qoder`

### 3. 验证运行
```bash
# 手动测试
python3 scripts/student_poller.py <node_id>

# 查看日志
tail -f poller_<node_id>.log

# 查看状态文件
cat .poller_state_<node_id>.json
```

## 📊 功能说明

| 功能 | 说明 |
|------|------|
| 消息拉取 | 每5分钟检查 from-hermes/ 目录 |
| 消息处理 | 自动识别训练任务、对局、系统通知 |
| ACK回执 | 自动发送ACK到 cc-ack/ 目录 |
| 结果提交 | 训练结果保存到 results/<node_id>/ |
| 状态追踪 | 已处理消息哈希记录在 .poller_state_<node_id>.json |
| 自动清理 | 清理48小时前的已处理消息 |

## 🚨 故障排除

### 问题：消息未处理
```bash
# 检查目录权限
ls -la .shared/messages/from-hermes/

# 手动运行查看错误
python3 scripts/student_poller.py <node_id>
```

### 问题：ACK未发送
```bash
# 检查cc-ack目录
ls -la .shared/messages/cc-ack/

# 检查追踪状态
cat .shared/messages/cc_tracking.json
```

### 问题：JSON解析错误
损坏的JSON文件会自动备份到 backup_* 文件，不影响其他消息处理。

## 📝 示例输出

```
[2026-06-29T23:58:09] [INFO] === 轮询开始 [xiaochen] ===
[2026-06-29T23:58:09] [INFO] 发现 3 条新消息
[2026-06-29T23:58:09] [INFO] 处理消息: [training_task] Day4训练任务
[2026-06-29T23:58:09] [INFO] ACK已发送: track-xxx -> ack_track-xxx_xiaochen.json
[2026-06-29T23:58:09] [INFO] === 轮询完成: 检查=3 新=3 处理=3 ACK=1 错误=0 ===
```

## 🔗 相关文档

- V4.0架构方案: `docs/V4.0_AGITIC_LEARNING.md`
- CC协议规范: `docs/CC_PROTOCOL_V1.1.md`
- 节点数字孪生: `scripts/node_digital_twin.py`

---
生成时间: 2026-06-29 23:59 UTC+8
