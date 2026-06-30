# 🦞 小龙虾网络优化方案 v2026-06-29

> 日期: 2026-06-29  
> 作者: 虾尔 (诸葛虾)  
> 基于: 2026-06-29 全天运行数据  
> 状态: 待实施

---

## 一、今日运行诊断

### 1.1 核心问题清单

| # | 问题 | 严重性 | 影响 | 状态 |
|---|------|--------|------|------|
| P1 | 学员提交目录全空 | 🔴 致命 | 训练系统形同虚设 | 未解决 |
| P2 | SSH 密钥失效 | 🔴 致命 | 小陈/诸葛虾均无法 SSH 连接 | 未解决 |
| P3 | CC 消息单向通道 | 🔴 致命 | 学员收不到消息，ACK 永远超时 | 未解决 |
| P4 | sync_reminder.py Python 3.6 兼容 Bug | 🟡 已修复 | 脚本报错但继续运行 | ✅ 已修复 |
| P5 | from-hermes/ 垃圾文件泛滥 | 🟡 已缓解 | 217→29 文件，但仍有 46 个 | 部分解决 |
| P6 | 诸葛马负载 19+ | 🟠 警告 | Hermes gateway 占用大量资源 | 未解决 |
| P7 | 磁盘 72% | 🟡 警告 | 40G 用了 27G，含大量日志 | 未解决 |
| P8 | Gitee SSH 未配置 | 🟢 已修复 | 双平台推送只走 GitHub | ✅ 已修复 |

### 1.2 训练进度总览

| 学员 | Day1 | Day2 | Day3 | Day4 | 评级 | 状态 |
|------|------|------|------|------|------|------|
| qoder | ✅ 100% | ✅ 81.7% | ✅ 89.3% | ✅ 87.3% | A | 最佳，473题 |
| 诸葛虾 | ✅ 90% | ❌ | ✅ 89.3% | ❌ | B+ | Day2/4 缺失 |
| 小陈 | ✅ 90% | ❌ | ❌ | ❌ | B | 仅 Day1，严重滞后 |
| 小薇 | ❌ | ❌ | ❌ | ❌ | 未评级 | 无服务器，未接入 |

---

## 二、优化方案（按优先级排序）

### 优先级 1：打通学员端消息消费（P1 + P3）

**问题：** 消息只写 `from-hermes/`，学员不读。

**方案：学员端消息轮询脚本**

```python
#!/usr/bin/env python3
"""
学员端消息轮询脚本
每个学员节点部署一个，定期从诸葛马拉取消息
"""
import os, json, subprocess, time

HERMES_HOST = "47.93.6.57"
HERMES_USER = "admin"
STUDENT_ID = os.environ.get("STUDENT_ID", "zhuguxia")

def pull_messages():
    """从诸葛马拉取新消息"""
    cmd = f"ssh {HERMES_USER}@{HERMES_HOST} 'cat /home/admin/go-training/shared/from-hermes/day3_redistribute_{STUDENT_ID}.json'"
    try:
        result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"拉取失败: {e}")
    return None

def submit_result(result_data):
    """提交训练结果"""
    filename = f"{STUDENT_ID}_day3_{time.strftime('%Y%m%d_%H%M%S')}.json"
    cmd = f"scp {filename} {HERMES_USER}@{HERMES_HOST}:/home/admin/go-training/shared/results/"
    subprocess.run(cmd.split(), timeout=30)

if __name__ == "__main__":
    while True:
        msg = pull_messages()
        if msg:
            print(f"收到任务: {msg.get('task', {}).get('title', 'unknown')}")
            # 执行训练...
            # submit_result(...)
        time.sleep(300)  # 每5分钟轮询
```

**实施步骤：**
1. 在诸葛虾、小陈服务器上部署轮询脚本
2. 设置环境变量 `STUDENT_ID`
3. 配置 cron 每 5 分钟执行一次
4. qoder 通过 GitHub Issue 通知替代

**预期效果：** 学员端自动拉取消息 → 执行训练 → 提交结果 → 回复 ACK

---

### 优先级 2：修复 SSH 密钥（P2）

**问题：** 诸葛马无法 SSH 到小陈和诸葛虾（密钥被拒绝）

**方案：**
1. 诸葛虾：确认 SSH 密钥是否被替换（`~/.ssh/authorized_keys` 检查）
2. 小陈：同上
3. 统一密钥管理：所有节点共享同一个 SSH 密钥对

**快速修复：**
```bash
# 在诸葛马上将 Hermes 密钥重新分发
ssh-copy-id -i ~/.ssh/id_rsa_hermes.pub admin@121.43.80.231  # 小陈
ssh-copy-id -i ~/.ssh/id_rsa_hermes.pub admin@60.205.139.51  # 诸葛虾
```

---

### 优先级 3：降低诸葛马负载（P6）

**问题：** 负载 19+，主要是 Hermes gateway

**方案：**
1. 检查 Hermes gateway 进程，确认是否可降频
2. 关闭不必要的 cron 广播（象棋/围棋/五子棋每 1 分钟广播 × 3 = 资源浪费）
3. 考虑将 Hermes gateway 迁移到更高配置服务器

**临时措施：**
```bash
# 关闭不必要的广播（每天 22:00-08:00）
# 在 crontab 中添加：
0 22 * * * pkill -f cron_broadcast  # 晚上停止
0 8 * * * /shared/go/cron_broadcast.sh &  # 早上恢复
```

---

### 优先级 4：磁盘清理（P7）

**问题：** 72% 使用率，含大量日志和垃圾文件

**方案：**
1. 清理 sync_reminder.log 历史备份
2. 清理 from-hermes/ 过期文件（保留最近 7 天）
3. 设置自动清理 cron

```bash
# 自动清理 cron（每天凌晨 3 点）
0 3 * * * find /home/admin/go-training/shared/ -name "*.log.old" -mtime +7 -delete
0 3 * * * find /home/admin/go-training/shared/from-hermes/ -name "reminder_*" -mtime +7 -delete
0 3 * * * find /home/admin/go-training/shared/from-hermes/ -name "github_reminder_*" -mtime +7 -delete
```

---

### 优先级 5：双平台同步机制（P8）

**问题：** GitHub/Gitee 推送不一致

**方案：双平台同步脚本**

```bash
#!/bin/bash
# dual_push.sh - 双平台同步提交
cd /home/admin/lobster-network

# 自动提交（如果有变更）
if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -m "auto-sync: $(date +%Y-%m-%d_%H:%M)"
fi

# 双平台推送
git push origin main 2>&1 | tail -3
git push gitee main 2>&1 | tail -3

echo "✅ 双平台同步完成: $(date)"
```

**配置：**
```bash
# 添加到 crontab（每 2 小时同步一次）
0 */2 * * * /home/admin/lobster-network/scripts/dual_push.sh >> /home/admin/lobster-network/logs/dual_push.log 2>&1
```

---

### 优先级 6：小薇节点接入

**问题：** 无服务器，无法通过 SSH/GitHub 正常接入

**方案：**
1. 为小薇分配一个轻量云服务器（最低配置即可）
2. 或通过诸葛马代理（诸葛马代为执行训练任务）
3. 短期方案：诸葛马代理执行，小薇只负责学习

---

## 三、实施时间表

| 阶段 | 时间 | 任务 | 负责人 |
|------|------|------|--------|
| **Phase 1** | 今天 | SSH 密钥修复 + 磁盘清理 | 虾尔 |
| **Phase 2** | 明天 | 学员端消息轮询脚本部署 | 虾尔 + 诸葛马 |
| **Phase 3** | 本周 | 双平台同步 + 负载优化 | 虾尔 |
| **Phase 4** | 本月 | 小薇节点接入 + 自动化监控 | 诸葛斌 |

---

## 四、预期效果

| 指标 | 当前 | 目标 |
|------|------|------|
| 学员提交率 | 0% | ≥80% |
| ACK 回复率 | 0% | ≥70% |
| 训练完成率 | 33% (1/3 学员有 Day2+) | 100% |
| 双平台同步 | 仅 GitHub | GitHub + Gitee 双写 |
| 磁盘使用 | 72% | ≤60% |
| 诸葛马负载 | 19+ | ≤10 |

---

## 五、风险与应对

| 风险 | 概率 | 应对 |
|------|------|------|
| 学员仍不提交 | 高 | 诸葛斌直接钉钉通知 |
| SSH 密钥再次失效 | 中 | 定期自动检查 + 告警 |
| 轮询脚本被学员关闭 | 低 | 进程监控 + 自动重启 |
| 双平台冲突 | 低 | 以 GitHub 为主，Gitee 为镜像 |

---

**文档路径：** `docs/OPTIMIZATION_PLAN_20260629.md`  
**下次评审：** 2026-06-30 09:00
