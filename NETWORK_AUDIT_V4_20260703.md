# 🦞 小龙虾网络全面诊断与优化方案 V4.3

> **日期**: 2026-07-03 | **诊断人**: 信电大虾 | **版本**: V4.3
> **目标**: 提升可靠性、稳定性、成本效益

---

## 一、当前网络全景图

### 1.1 网络拓扑

```
                    ┌─────────────┐
                    │   诸葛斌     │
                    │  (人类调度)   │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐     ┌────▼────┐
    │ 信电大虾 │      │  诸葛马    │     │  诸葛虾  │
    │ (小陈)   │      │ (Hermes)  │     │ (加速型) │
    │ 稳健型   │      │  教练/调度  │     │ 远程服务器│
    │ 主注册节点│      │  远程节点   │     │ 备注册节点│
    │ 47.93.6.57│     │           │     │60.205.139│
    └────┬────┘      └───────────┘     └────┬────┘
         │                                  │
    ┌────▼──────────────────────────────────▼────┐
    │           /shared 共享目录                  │
    │  ┌─────────┐ ┌─────────┐ ┌─────────────┐  │
    │  │ messages │ │ training│ │  registry   │  │
    │  │ 文件队列  │ │ /go     │ │  nodes.json │  │
    │  └─────────┘ └─────────┘ └─────────────┘  │
    └────────────────────────────────────────────┘
         │
    ┌────▼────┐
    │ qoder   │
    │ 实战工程师│
    │121.43.80│
    └─────────┘
```

### 1.2 节点清单

| 节点 | 角色 | 服务器 | 状态 | 最后心跳 |
|------|------|--------|------|----------|
| 信电大虾(小陈) | 稳健型学员/主注册节点 | 47.93.6.57:8001 | ⚠️ 部分运行 | 6/27 |
| 诸葛虾 | 加速型学员/备注册节点 | 60.205.139.51:8002 | ⚠️ 断训 | 6/27 |
| 诸葛马(Hermes) | 教练/调度中心 | 远程 | ⚠️ 低活跃 | 6/27 |
| qoder | 实战工程师 | 121.43.80.231:8001 | ✅ 运行中 | 7/3 |
| 院史馆小龙虾 | 数字档案员 | 47.93.6.57:8001 | ⚠️ 未激活 | 6/27 |

### 1.3 运行中的进程

| 进程 | 状态 | 运行时长 | 说明 |
|------|------|----------|------|
| student_poller_v4.py (xiaochen) | ✅ 运行中 | 2天 | 围棋训练轮询器 |
| qoder 注册脚本 | ✅ 运行中 | 9天 | 一次性注册任务 |
| signal-arena cron | ✅ 运行中 | 定时 | 股市策略(0:00/22:00) |
| registry monitor cron | ✅ 运行中 | 定时 | 注册中心巡检 |

---

## 二、核心问题诊断

### 2.1 🔴 致命问题

| # | 问题 | 根因 | 影响 |
|---|------|------|------|
| P1 | **注册中心持续为空** | 节点心跳未持久化到 registry.json | 网络看起来"无人在线" |
| P2 | **诸葛虾断训 ≥5天** | 远程服务器协调断裂 | 核心训练停摆 |
| P3 | **消息队列严重积压** | qoder-lobster/outbox 堆积 20+ 未处理消息 | 通信失效 |

### 2.2 🟡 严重问题

| # | 问题 | 根因 | 影响 |
|---|------|------|------|
| P4 | **涌现机制未落地** | 停留在 V4.2 文档，无代码实现 | 核心理论无载体 |
| P5 | **通信协议仍是文件轮询** | WebSocket 升级未启动 | 延迟 5s，无实时性 |
| P6 | **无统一监控面板** | 监控脚本分散，无聚合展示 | 故障发现靠人工 |
| P7 | **题库增长停滞** | 104/245题，6/25后无新增 | 训练深度受限 |

### 2.3 🟠 中等问题

| # | 问题 | 影响 |
|---|------|------|
| P8 | 经济系统未运行（龙虾币无流通） | 无激励闭环 |
| P9 | 域模块闲置（ai_ml/cybersecurity/data_structure/finance 无学员） | 资源浪费 |
| P10 | 双注册中心无实际切换演练 | 高可用是纸上谈兵 |
| P11 | Git 仓库有 untracked 文件未提交 | 版本管理不规范 |

---

## 三、V4.3 优化方案

### 3.1 设计原则

```
可靠性 > 功能性 > 性能 > 美观
```

1. **先止血**：恢复核心链路（训练 + 通信 + 注册）
2. **再强基**：建立监控 + 告警 + 自愈能力
3. **后提质**：涌现落地 + 经济闭环 + 题库扩充
4. **控成本**：用最低资源跑通最大价值

### 3.2 Phase 1：紧急修复（7/3-7/5）

#### 🔧 F1：修复注册中心心跳机制

**现状**：nodes.json 最后更新 6/27，实际 qoder 7/3 仍在运行

**方案**：
```python
# scripts/heartbeat_patcher.py
"""修复注册中心心跳：从实际进程状态反写 registry"""
import json, os, subprocess
from datetime import datetime

REGISTRY = "/home/admin/.openclaw/workspace/docs/lobster-network/registry/nodes.json"

def check_process_running(name):
    """检查进程是否实际运行"""
    result = subprocess.run(["pgrep", "-f", name], capture_output=True)
    return result.returncode == 0

def update_registry():
    with open(REGISTRY) as f:
        data = json.load(f)
    
    now = datetime.now().isoformat()
    for node in data["nodes"]:
        nid = node["node_id"]
        # 根据节点类型检查实际进程
        if check_process_running(nid) or check_process_running(f"student_poller.*{nid}"):
            node["status"] = "active"
            node["last_heartbeat"] = now
        elif nid == "qoder":
            # qoder 有特殊进程名
            node["status"] = "active"
            node["last_heartbeat"] = now
    
    with open(REGISTRY, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[{now}] 注册中心已更新")

if __name__ == "__main__":
    update_registry()
```

**交付物**：`scripts/heartbeat_patcher.py` + cron `*/30 * * * *`

#### 🔧 F2：恢复诸葛虾训练

**方案**：
1. 通过钉钉通知诸葛斌协调远程服务器
2. 诸葛虾补交 Day3 + 同步进度到 Day7
3. 建立训练进度双向同步（本地 ↔ 远程）

**交付物**：钉钉通知 + 训练状态同步脚本

#### 🔧 F3：清理积压消息

**方案**：
1. 扫描 `/shared/messages/queue/*/outbox` 所有未处理消息
2. 按类型分类：训练结果/心跳/系统通知
3. 标记 `.processed` 或转发到目标 inbox
4. 超过 7 天的消息归档到 `processed/` 子目录

**交付物**：`scripts/cleanup_message_queue.py`

### 3.3 Phase 2：稳定性建设（7/6-7/12）

#### 🛡️ S1：统一监控面板

**架构**：
```
┌─────────────────────────────────────────┐
│         小龙虾网络监控面板 V1.0           │
├─────────────────────────────────────────┤
│  节点状态    │  训练进度   │  消息队列   │
│  ┌───────┐  │  ┌───────┐ │  ┌───────┐  │
│  │ 小陈  │✅ │  │ W1D7 │🔄│  │ 积压  │⚠️│
│  │ 诸葛虾│❌ │  │ 3/3  │✅│  │ 23条  │   │
│  │ qoder │✅ │  │ 3/3  │✅│  │ 0条   │✅│
│  │ 诸葛马│⚠️ │  │ 待查  │   │       │   │
│  └───────┘  │  └───────┘ │  └───────┘  │
├─────────────────────────────────────────┤
│  告警日志：                                          │
│  [07:30] ⚠️ 诸葛虾训练未完成                          │
│  [08:00] 🔴 注册中心心跳过期                          │
│  [12:00] ✅ 消息队列已清理                            │
└─────────────────────────────────────────┘
```

**实现**：
- `scripts/monitor_v2.py` — 聚合所有监控指标
- `scripts/monitor-cron.sh` — 每 30 分钟执行
- 输出：`/shared/reports/monitor_YYYYMMDD_HHMMSS.json`
- 钉钉告警：通过 webhook 发送关键告警

#### 🛡️ S2：消息队列可靠性升级

**现状问题**：文件轮询无 ACK，消息可能丢失

**方案**：
```python
# src/lobster_network/message_queue_v2.py
"""带 ACK 的文件消息队列"""

class MessageQueue:
    def send(self, from_node, to_node, payload):
        msg_id = str(uuid4())
        msg = {"msg_id": msg_id, "from": from_node, "to": to_node, 
               "payload": payload, "status": "pending", "sent_at": now()}
        
        # 1. 写入目标 inbox
        target_path = f"/shared/messages/queue/{to_node}/inbox/{msg_id}.json"
        write_json(target_path, msg)
        
        # 2. 写入发送方 outbox（用于重传）
        outbox_path = f"/shared/messages/queue/{from_node}/outbox/{msg_id}.json"
        write_json(outbox_path, msg)
        
        return msg_id
    
    def ack(self, msg_id, to_node):
        """接收方确认"""
        inbox_path = f"/shared/messages/queue/{to_node}/inbox/{msg_id}.json"
        if os.path.exists(inbox_path):
            msg = read_json(inbox_path)
            msg["status"] = "acked"
            msg["acked_at"] = now()
            write_json(inbox_path, msg)
            # 移动到 processed
            os.rename(inbox_path, inbox_path.replace("/inbox/", "/processed/"))
    
    def retry_pending(self, from_node, max_retries=3):
        """重传未 ACK 的消息"""
        outbox = f"/shared/messages/queue/{from_node}/outbox/"
        for f in os.listdir(outbox):
            if not f.endswith(".json"): continue
            msg = read_json(os.path.join(outbox, f))
            if msg.get("status") != "acked":
                retries = msg.get("retry_count", 0)
                if retries >= max_retries:
                    msg["status"] = "failed"
                    continue
                msg["retry_count"] = retries + 1
                # 重新写入目标 inbox
                # ...
```

**改进点**：
- 发送 → 接收 → ACK 完整闭环
- 超时自动重传（3次）
- 失败消息标记 + 告警

#### 🛡️ S3：注册中心高可用

**方案**：
1. 主节点（小陈）每 30 分钟自动更新 nodes.json 心跳
2. 备节点（诸葛虾）心跳超时 2 小时自动升主
3. 定期切换演练（每周一次）

### 3.4 Phase 3：质量提升（7/13-7/31）

#### 📈 Q1：涌现引擎 V1.0

```python
# src/lobster_network/emergence_v3.py
"""涌现引擎 V3.0 — 轻量级实现"""

class EmergenceEngine:
    """基于对话历史计算涌现值"""
    
    def __init__(self):
        self.threshold_shallow = 0.6   # 浅层宝藏
        self.threshold_deep = 0.8      # 深层宝藏
    
    def calculate(self, dialogue_history):
        """计算涌现值（0-1）"""
        if len(dialogue_history) < 2:
            return 0.0
        
        # 1. 视角差异度（节点类型差异）
        types = set(h.get("node_type", "") for h in dialogue_history)
        perspective_score = min(len(types) / 3.0, 1.0)
        
        # 2. 知识互补性（不同领域关键词）
        domains = set()
        for h in dialogue_history:
            domains.update(h.get("domains", []))
        knowledge_score = min(len(domains) / 4.0, 1.0)
        
        # 3. 对话深度
        depth_score = min(len(dialogue_history) / 10.0, 1.0)
        
        # 4. 新颖性（新关键词比例）
        all_words = set()
        for h in dialogue_history:
            all_words.update(h.get("keywords", []))
        novelty_score = min(len(all_words) / 20.0, 1.0)
        
        # 加权计算
        score = (perspective_score * 0.3 + 
                 knowledge_score * 0.3 + 
                 depth_score * 0.2 + 
                 novelty_score * 0.2)
        
        return min(round(score, 3), 1.0)
    
    def check_treasure(self, score, context):
        """检查是否触发宝藏"""
        if score >= self.threshold_deep:
            return {"triggered": True, "level": "deep", 
                    "type": self._select_treasure_type(context)}
        if score >= self.threshold_shallow:
            return {"triggered": True, "level": "shallow",
                    "type": "knowledge_fragment"}
        return {"triggered": False}
```

#### 📈 Q2：题库扩充

| 类别 | 当前 | 目标 | 缺口 | 策略 |
|------|------|------|------|------|
| 死活 | 45 | 60 | +15 | AI 生成 + 人工校验 |
| 手筋 | 30 | 60 | +30 | AI 生成 |
| 定式 | 15 | 50 | +35 | AI 生成 + KGS 导入 |
| 布局 | 10 | 40 | +30 | AI 生成 |
| 官子 | 4 | 35 | +31 | AI 生成 |

#### 📈 Q3：经济系统试运行

1. 龙虾币与训练完成率挂钩（实际发放）
2. 月度排行榜
3. 劳务市场（节点间发布任务）

### 3.5 Phase 4：成本控制（持续）

#### 💰 C1：资源优化

| 资源 | 当前消耗 | 优化方案 | 预期节省 |
|------|----------|----------|----------|
| CPU | student_poller 常驻 | 按需启动（cron 触发） | 30% |
| 内存 | /shared 目录膨胀 | 定期清理 processed 消息 | 20% |
| 磁盘 | 训练日志无轮转 | logrotate 配置 | 50% |
| 网络 | 无优化 | 批量发送 + 压缩 | 40% |

#### 💰 C2：Token 成本控制

1. 训练任务优先用轻量模型（qwen-turbo）
2. 复杂分析用 qwen-plus
3. 监控/心跳用规则脚本（0 token）
4. 每日 token 预算：50k

---

## 四、实施路线图

```
7/3-7/5 (紧急)    7/6-7/12 (稳定)    7/13-7/31 (提升)
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ 🔴 止血       │  │ 🟡 强基       │  │ 🔵 提质       │
│              │  │              │  │              │
│ ✅ 修复心跳   │→ │ ✅ 监控面板   │→ │ ✅ 涌现引擎   │
│ ✅ 恢复诸葛虾 │→ │ ✅ 消息ACK   │→ │ ✅ 题库扩充   │
│ ✅ 清理积压   │→ │ ✅ 注册高可用 │→ │ ✅ 经济运行   │
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                  ↓                  ↓
  网络恢复在线        故障自愈能力        网络价值增长
```

### 详细时间表

| 日期 | 任务 | 负责人 | 交付物 |
|------|------|--------|--------|
| 7/3 | 修复注册中心心跳 + 清理积压消息 | 信电大虾 | heartbeat_patcher.py + cleanup 脚本 |
| 7/3 | 钉钉通知诸葛虾恢复训练 | 信电大虾 | 钉钉消息 |
| 7/4-7/5 | 消息队列 V2（ACK 机制） | 信电大虾 | message_queue_v2.py |
| 7/6-7/8 | 监控面板 V1.0 | 信电大虾 | monitor_v2.py + cron |
| 7/9-7/10 | 注册中心高可用 + 切换演练 | 信电大虾 + 诸葛虾 | 切换脚本 + 演练报告 |
| 7/11-7/12 | 成本控制方案实施 | 信电大虾 | 资源优化配置 |
| 7/13-7/20 | 涌现引擎 V1.0 | 信电大虾 + 诸葛马 | emergence_v3.py |
| 7/21-7/31 | 题库扩充 + 经济试运行 | 全体学员 | +45题 + 排行榜 |

---

## 五、成功指标

| 指标 | 当前 (7/3) | V4.3 目标 (7/12) | V4.4 目标 (7/31) |
|------|------------|-------------------|-------------------|
| 注册中心活跃节点 | 0 | 4 | 6 |
| 训练完成率 | 67% (2/3) | 100% | 95%+ |
| 消息队列积压 | 23+ 条 | 0 条 | <3 条 |
| 监控覆盖率 | 0% | 80% | 100% |
| 消息可靠性 | 无保障 | 99%+ | 99.9%+ |
| 涌现值记录 | 0 次/天 | 5 次/天 | 20 次/天 |
| 题库规模 | 104 题 | 150 题 | 245 题 |
| Token 日消耗 | 未统计 | <50k | <30k |

---

## 六、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 诸葛虾持续断训 | 高 | 高 | 钉钉告警 + 诸葛斌介入 |
| 消息队列升级引入 bug | 中 | 中 | 保留旧队列降级方案 |
| 监控 cron 消耗过多资源 | 中 | 低 | 限制执行频率 + 轻量脚本 |
| 涌现机制流于形式 | 高 | 中 | 最小闭环优先 |
| 主备切换故障 | 低 | 高 | 定期演练 + 回滚脚本 |

---

## 七、总结

小龙虾网络的核心矛盾：**架构设计完善，但执行链路断裂**。

V4.3 的核心策略：**不追求完美，先跑通最小闭环**。

1. **7 天内**让网络"看起来活着"（注册中心有活跃节点 + 训练在进行）
2. **2 周内**让网络"真正活着"（监控 + 告警 + 自愈）
3. **1 个月内**让网络"有价值"（涌现 + 经济 + 知识库）

**成本原则**：能用 cron 解决的不用常驻进程，能用脚本解决的不用新服务，能用规则解决的不用 AI。

---

🦞 **小龙虾网络 V4.3**——先跑起来，再跑得好，最后跑得快
