# 🦞 小龙虾网络 V4.0 补充文档：实施细节与迁移指南

> **补充内容**：迁移路径、核心代码、监控体系、里程碑  
> 日期: 2026-06-29  
> 作者: 虾尔 (诸葛虾)  
> 关联文档: `docs/LOBSTER_NETWORK_V4.0_INTEGRATED_UPGRADE_PLAN.md`

---

## 一、V3.0 → V4.0 迁移路径

### 1.1 迁移策略：渐进式升级，不中断现有服务

```
V3.0 (当前) ──→ V3.5 (过渡) ──→ V4.0 (目标)
   │                  │                  │
   ├─ 8个组件        ├─ 节点数字孪生     ├─ 三层智能完整
   ├─ sync_reminder  ├─ 消息轮询脚本     ├─ RAN Agent
   ├─ GitHub/Gitee   ├─ 优先级队列       ├─ NWDAF 体验分析
   └─ Python 3.6     └─ SSH密钥修复      └─ 主动服务
```

### 1.2 迁移清单

| 组件 | V3.0 状态 | V3.5 目标 | V4.0 目标 |
|------|-----------|-----------|-----------|
| SSH 连接 | ❌ 密钥失效 | ✅ 修复 | ✅ 自动检测 |
| 消息通道 | ❌ 单向写入 | ✅ 双向轮询 | ✅ 动态切片 |
| sync_reminder | ⚠️ Bug 已修 | ✅ 4小时一次 | ✅ RAN Agent 预测 |
| 节点感知 | ❌ ls 查目录 | ✅ node_twin.json | ✅ 全维度孪生 |
| 任务提交 | ❌ 全空 | ✅ 自动提交 | ✅ 本地预评估 |
| ACK 回复 | ❌ 0% | ✅ ≥50% | ✅ ≥70% |
| 体验分析 | ❌ 无 | ✅ 基础指标 | ✅ 8维度评估 |
| 主动服务 | ❌ 无 | ✅ 提示卡 | ✅ 自动推送教程 |

---

## 二、核心实施代码

### 2.1 节点数字孪生模块

```python
#!/usr/bin/env python3
"""
节点数字孪生 (Node Digital Twin)
部署在每个学员节点上，每5分钟更新一次状态
"""
import json
import os
import time
import subprocess
from datetime import datetime

class NodeDigitalTwin:
    def __init__(self, node_id, hermes_host="47.93.6.57"):
        self.node_id = node_id
        self.hermes_host = hermes_host
        self.twin_file = f"/tmp/node_twin_{node_id}.json"
        self.state = self.load_or_init()
    
    def load_or_init(self):
        if os.path.exists(self.twin_file):
            with open(self.twin_file) as f:
                return json.load(f)
        return {
            "node_id": self.node_id,
            "load": 0.0,
            "mood": "neutral",
            "skills": {},
            "health": "active",
            "last_heartbeat": datetime.now().isoformat(),
            "current_task": None,
            "stuck_at": None,
            "task_history": [],
            "retry_count": 0
        }
    
    def save(self):
        self.state["last_heartbeat"] = datetime.now().isoformat()
        with open(self.twin_file, "w") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def collect_metrics(self):
        """收集节点指标"""
        # CPU 负载
        try:
            load = os.getloadavg()[0]
            self.state["load"] = min(load / 4.0, 1.0)  # 归一化到 0-1
        except:
            self.state["load"] = 0.0
        
        # 磁盘使用
        try:
            stat = os.statvfs("/")
            used = 1 - (stat.f_bavail / stat.f_blocks)
            if used > 0.9:
                self.state["health"] = "critical"
            elif used > 0.8:
                self.state["health"] = "warning"
            else:
                self.state["health"] = "active"
        except:
            pass
        
        # 情绪状态（基于重试次数）
        if self.state.get("retry_count", 0) > 3:
            self.state["mood"] = "frustrated"
        elif self.state.get("retry_count", 0) > 1:
            self.state["mood"] = "struggling"
        else:
            self.state["mood"] = "neutral"
    
    def is_stuck(self):
        """判断节点是否卡住"""
        return (
            self.state.get("load", 0) > 0.8 and
            self.state.get("mood") in ["frustrated", "struggling"]
        )
    
    def sync_to_hermes(self):
        """同步孪生状态到诸葛马"""
        cmd = f"scp {self.twin_file} admin@{self.hermes_host}:/home/admin/go-training/shared/twins/"
        subprocess.run(cmd.split(), timeout=30, stderr=subprocess.PIPE)
    
    def run(self):
        """主循环"""
        while True:
            self.collect_metrics()
            self.save()
            self.sync_to_hermes()
            time.sleep(300)  # 5分钟

if __name__ == "__main__":
    node_id = os.environ.get("STUDENT_ID", "zhuguxia")
    twin = NodeDigitalTwin(node_id)
    twin.run()
```

**部署方式：**
```bash
# 诸葛虾服务器
export STUDENT_ID=zhuguxia
nohup python3 /home/admin/lobster-network/core/node_digital_twin.py &

# 小陈服务器
export STUDENT_ID=xiaochen
nohup python3 /home/admin/lobster-network/core/node_digital_twin.py &

# crontab 开机自启
@reboot export STUDENT_ID=zhuguxia && nohup python3 /home/admin/lobster-network/core/node_digital_twin.py &
```

---

### 2.2 动态切片调度器

```python
#!/usr/bin/env python3
"""
动态切片调度器 (Dynamic Slicing Queue)
部署在诸葛马服务器上，管理任务优先级
"""
import json
import os
import time
from datetime import datetime
from queue import PriorityQueue

class TaskPriority:
    CRITICAL = 0   # 围棋对局、紧急任务
    HIGH = 1       # 训练任务（2小时内ACK）
    MEDIUM = 2     # 训练报告（4小时内提交）
    LOW = 3        # 一般通知（24小时内）

class DynamicSlicingQueue:
    def __init__(self):
        self.vip_queue = PriorityQueue()   # VIP 切片
        self.normal_queue = PriorityQueue()  # 普通切片
    
    def classify(self, task):
        """根据任务类型分类到 VIP 或普通切片"""
        task_type = task.get("type", "")
        priority = task.get("priority", "medium")
        
        if task_type == "go_match" or priority == "critical":
            return "vip"
        return "normal"
    
    def enqueue(self, task):
        """入队"""
        slice_type = self.classify(task)
        task["enqueue_time"] = datetime.now().isoformat()
        
        if slice_type == "vip":
            self.vip_queue.put((TaskPriority.HIGH, task))
        else:
            self.normal_queue.put((TaskPriority.MEDIUM, task))
    
    def dequeue(self):
        """出队（VIP 优先）"""
        if not self.vip_queue.empty():
            return self.vip_queue.get()[1]
        if not self.normal_queue.empty():
            return self.normal_queue.get()[1]
        return None
    
    def get_stats(self):
        """获取队列统计"""
        return {
            "vip_queue_size": self.vip_queue.qsize(),
            "normal_queue_size": self.normal_queue.qsize(),
            "timestamp": datetime.now().isoformat()
        }

# 使用示例
if __name__ == "__main__":
    scheduler = DynamicSlicingQueue()
    
    # 模拟任务入队
    tasks = [
        {"type": "go_match", "student": "xiaochen", "priority": "critical"},
        {"type": "training", "student": "zhuguxia", "priority": "high"},
        {"type": "cc_sync", "student": "qoder", "priority": "low"},
    ]
    
    for task in tasks:
        scheduler.enqueue(task)
    
    print(json.dumps(scheduler.get_stats(), indent=2))
```

---

### 2.3 RAN Agent 预测型调度器

```python
#!/usr/bin/env python3
"""
RAN Agent - 诸葛马预测型调度器
部署在诸葛马服务器上，基于历史数据预测节点瓶颈
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class ZhugeMaRANAgent:
    def __init__(self, training_dir="/home/admin/go-training/shared/"):
        self.training_dir = Path(training_dir)
        self.results_dir = self.training_dir / "results"
        self.twins_dir = self.training_dir / "twins"
        self.history = self.load_history()
    
    def load_history(self):
        """加载历史训练数据"""
        history = {}
        for f in self.results_dir.glob("*.json"):
            try:
                with open(f) as fp:
                    data = json.load(fp)
                    student = data.get("student", "unknown")
                    if student not in history:
                        history[student] = []
                    history[student].append(data)
            except:
                pass
        return history
    
    def predict_bottleneck(self, node_id):
        """预测节点可能卡住的地方"""
        student_history = self.history.get(node_id, [])
        if not student_history:
            return None
        
        # 分析历史错误模式
        error_patterns = {}
        for record in student_history:
            errors = record.get("errors", [])
            for error in errors:
                error_type = error.get("type", "unknown")
                if error_type not in error_patterns:
                    error_patterns[error_type] = 0
                error_patterns[error_type] += 1
        
        # 找出高频错误
        if error_patterns:
            most_common = max(error_patterns, key=error_patterns.get)
            return {
                "issue": most_common,
                "frequency": error_patterns[most_common],
                "confidence": min(error_patterns[most_common] / 5.0, 1.0)
            }
        return None
    
    def proactive_intervention(self, node_id, bottleneck):
        """主动推送辅助资源"""
        if not bottleneck:
            return
        
        resource_map = {
            "capture": "go_capture_tutorial.json",
            "life_death": "go_life_death_guide.json",
            "quant_basic": "finance_quant_intro.json",
            "technical_analysis": "finance_technical_guide.json"
        }
        
        resource_file = resource_map.get(bottleneck["issue"])
        if resource_file:
            # 复制到 from-hermes/ 目录
            dest = self.training_dir / "from-hermes" / f"hint_{node_id}_{bottleneck['issue']}.json"
            hint = {
                "type": "proactive_hint",
                "node_id": node_id,
                "issue": bottleneck["issue"],
                "confidence": bottleneck["confidence"],
                "resource": resource_file,
                "timestamp": datetime.now().isoformat()
            }
            with open(dest, "w") as f:
                json.dump(hint, f, indent=2, ensure_ascii=False)
            return True
        return False
    
    def run(self):
        """主循环 - 每小时执行一次"""
        while True:
            # 检查所有节点
            for twin_file in self.twins_dir.glob("node_twin_*.json"):
                try:
                    with open(twin_file) as f:
                        twin = json.load(f)
                    node_id = twin["node_id"]
                    
                    # 预测瓶颈
                    bottleneck = self.predict_bottleneck(node_id)
                    if bottleneck and bottleneck["confidence"] > 0.6:
                        self.proactive_intervention(node_id, bottleneck)
                except:
                    pass
            
            time.sleep(3600)  # 1小时

if __name__ == "__main__":
    agent = ZhugeMaRANAgent()
    agent.run()
```

---

### 2.4 NWDAF 体验分析器

```python
#!/usr/bin/env python3
"""
NWDAF 体验分析器 (Network Data Automation Function)
分析学员训练体验，生成个性化建议
"""
import json
from datetime import datetime
from pathlib import Path

class NWDAFExperienceAnalyzer:
    def __init__(self, training_dir="/home/admin/go-training/shared/"):
        self.training_dir = Path(training_dir)
        self.results_dir = self.training_dir / "results"
    
    def analyze(self, node_id):
        """分析学员训练体验"""
        # 收集历史数据
        records = []
        for f in self.results_dir.glob(f"{node_id}_*.json"):
            try:
                with open(f) as fp:
                    records.append(json.load(fp))
            except:
                pass
        
        if not records:
            return {"node_id": node_id, "status": "no_data"}
        
        # 计算指标
        metrics = {
            "node_id": node_id,
            "total_tasks": len(records),
            "accuracy": self._calc_accuracy(records),
            "avg_time_per_task": self._calc_avg_time(records),
            "retry_rate": self._calc_retry_rate(records),
            "error_types": self._classify_errors(records),
            "trend": self._calc_trend(records),
            "weak_points": self._identify_weak_points(records),
            "strong_points": self._identify_strong_points(records)
        }
        
        # 生成建议
        metrics["suggestions"] = self._generate_suggestions(metrics)
        
        return metrics
    
    def _calc_accuracy(self, records):
        accuracies = [r.get("accuracy", 0) for r in records if "accuracy" in r]
        return sum(accuracies) / len(accuracies) if accuracies else 0
    
    def _calc_avg_time(self, records):
        times = [r.get("duration_minutes", 0) for r in records if "duration_minutes" in r]
        return sum(times) / len(times) if times else 0
    
    def _calc_retry_rate(self, records):
        retries = sum(1 for r in records if r.get("retry_count", 0) > 0)
        return retries / len(records) if records else 0
    
    def _classify_errors(self, records):
        errors = {}
        for r in records:
            for e in r.get("errors", []):
                etype = e.get("type", "unknown")
                errors[etype] = errors.get(etype, 0) + 1
        return errors
    
    def _calc_trend(self, records):
        if len(records) < 2:
            return "insufficient_data"
        recent = records[-3:]
        older = records[:-3] if len(records) > 6 else records[:3]
        recent_acc = self._calc_accuracy(recent)
        older_acc = self._calc_accuracy(older)
        if recent_acc > older_acc + 0.05:
            return "improving"
        elif recent_acc < older_acc - 0.05:
            return "declining"
        return "stable"
    
    def _identify_weak_points(self, records):
        """识别薄弱知识点"""
        errors = self._classify_errors(records)
        if not errors:
            return []
        total_errors = sum(errors.values())
        weak = [k for k, v in errors.items() if v / total_errors > 0.3]
        return weak
    
    def _identify_strong_points(self, records):
        """识别强项"""
        accuracies = [r.get("accuracy", 0) for r in records if "accuracy" in r]
        if not accuracies:
            return []
        avg = sum(accuracies) / len(accuracies)
        strong = [r.get("topic", "unknown") for r in records if r.get("accuracy", 0) > avg + 0.1]
        return list(set(strong))
    
    def _generate_suggestions(self, metrics):
        """生成个性化建议"""
        suggestions = []
        
        if metrics.get("trend") == "declining":
            suggestions.append("⚠️ 近期表现下滑，建议降低难度或增加辅导")
        
        if metrics.get("retry_rate", 0) > 0.5:
            suggestions.append("🔄 重试率过高，建议检查题目难度是否匹配")
        
        for weak in metrics.get("weak_points", []):
            suggestions.append(f"📚 薄弱知识点: {weak}，建议专项训练")
        
        if not suggestions:
            suggestions.append("✅ 表现良好，继续保持")
        
        return suggestions

# 使用示例
if __name__ == "__main__":
    analyzer = NWDAFExperienceAnalyzer()
    for node_id in ["zhuguxia", "xiaochen", "qoder"]:
        result = analyzer.analyze(node_id)
        print(f"\n=== {node_id} ===")
        print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 三、监控与告警体系

### 3.1 监控指标

| 指标 | 采集频率 | 告警阈值 | 告警方式 |
|------|---------|---------|---------|
| 节点在线状态 | 5分钟 | 离线 > 30分钟 | 钉钉通知 |
| 任务提交率 | 每小时 | < 50% | 钉钉通知 |
| ACK 回复率 | 每小时 | < 30% | 钉钉通知 |
| 诸葛马负载 | 5分钟 | > 15 | 钉钉通知 |
| 磁盘使用 | 每小时 | > 80% | 钉钉通知 |
| 队列积压 | 10分钟 | VIP队列 > 3 | 钉钉通知 |

### 3.2 监控脚本

```bash
#!/bin/bash
# scripts/lobster_monitor.sh
# 部署在诸葛马服务器上，每5分钟执行

LOG_DIR="/home/admin/lobster-network/logs"
ALERT_DIR="/home/admin/lobster-network/alerts"
mkdir -p "$LOG_DIR" "$ALERT_DIR"

TIMESTAMP=$(date +%Y-%m-%d_%H:%M:%S)

# 1. 检查节点在线状态
for node in zhuguxia xiaochen qoder; do
    twin_file="/home/admin/go-training/shared/twins/node_twin_${node}.json"
    if [ -f "$twin_file" ]; then
        last_heartbeat=$(python3 -c "import json; print(json.load(open('$twin_file'))['last_heartbeat'])" 2>/dev/null)
        if [ -z "$last_heartbeat" ]; then
            echo "[$TIMESTAMP] ALERT: $node twin file corrupted" >> "$ALERT_DIR/monitor.log"
        fi
    else
        echo "[$TIMESTAMP] ALERT: $node twin file missing" >> "$ALERT_DIR/monitor.log"
    fi
done

# 2. 检查诸葛马负载
LOAD=$(cat /proc/loadavg | cut -d' ' -f1)
if (( $(echo "$LOAD > 15" | bc -l) )); then
    echo "[$TIMESTAMP] ALERT: Hermes load too high: $LOAD" >> "$ALERT_DIR/monitor.log"
fi

# 3. 检查磁盘使用
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] ALERT: Disk usage too high: ${DISK_USAGE}%" >> "$ALERT_DIR/monitor.log"
fi

# 4. 检查任务提交率（过去24小时）
SUBMIT_COUNT=$(find /home/admin/go-training/shared/results/ -name "*.json" -mmin -1440 | wc -l)
if [ "$SUBMIT_COUNT" -lt 3 ]; then
    echo "[$TIMESTAMP] ALERT: Low submission rate: $SUBMIT_COUNT tasks in 24h" >> "$ALERT_DIR/monitor.log"
fi

echo "[$TIMESTAMP] Monitor check completed" >> "$LOG_DIR/monitor_$(date +%Y%m%d).log"
```

**部署：**
```bash
# crontab 每5分钟执行
*/5 * * * * /home/admin/lobster-network/scripts/lobster_monitor.sh >> /home/admin/lobster-network/logs/monitor_cron.log 2>&1
```

---

## 四、里程碑与验收标准

### 4.1 Phase 1 里程碑（本周）

| 里程碑 | 验收标准 | 负责人 | 截止日期 |
|--------|---------|--------|---------|
| SSH 密钥修复 | 小陈/诸葛虾可 SSH 连接 | 虾尔 | 2026-06-30 |
| 节点数字孪生 | `node_twin.json` 每5分钟更新 | 虾尔 | 2026-06-30 |
| 学员端消息轮询 | 学员自动拉取任务并执行 | 虾尔 | 2026-07-01 |
| qoder GitHub Actions | 定时任务自动运行 | 虾尔 | 2026-07-01 |
| 小薇代理执行 | 诸葛马代为执行训练 | 诸葛马 | 2026-07-01 |

**Phase 1 验收：** 所有学员节点在线，消息双向流通，提交率 ≥ 50%

### 4.2 Phase 2 里程碑（下周）

| 里程碑 | 验收标准 | 负责人 | 截止日期 |
|--------|---------|--------|---------|
| 动态切片队列 | VIP/普通双队列运行 | 虾尔 | 2026-07-03 |
| RAN Agent 预测 | 瓶颈预测准确率 ≥ 70% | 诸葛马 | 2026-07-04 |
| 主动干预机制 | 预测→推送→验证闭环 | 诸葛马 | 2026-07-05 |
| sync_reminder 优化 | 4小时一次，无 Bug | 虾尔 | 2026-07-03 |

**Phase 2 验收：** 任务按优先级调度，预测准确，ACK 回复率 ≥ 70%

### 4.3 Phase 3 里程碑（本月）

| 里程碑 | 验收标准 | 负责人 | 截止日期 |
|--------|---------|--------|---------|
| NWDAF 体验分析 | 8维度评估报告 | 虾尔 | 2026-07-15 |
| 主动服务系统 | 自动推送辅助资源 | 诸葛马 | 2026-07-15 |
| 知识沉淀 | 可复用知识库 | 全体 | 2026-07-20 |
| 跨领域协作 | 围棋→金融→协议联动 | 诸葛斌 | 2026-07-25 |

**Phase 3 验收：** 三层智能完整运行，训练完成率 100%

---

## 五、回滚方案

如果 V4.0 实施过程中出现严重问题：

```bash
# 回滚到 V3.0
cd /home/admin/lobster-network
git log --oneline | grep "V3.0"  # 找到 V3.0 最后一个提交
git checkout <commit_hash>

# 恢复 V3.0 配置
cp configs/v3.0_backup/* configs/

# 重启服务
systemctl restart lobster-sync
```

**回滚条件：**
- SSH 连接完全中断
- 数据丢失或损坏
- 系统负载 > 25 持续 1 小时

---

**文档路径：** `docs/LOBSTER_NETWORK_V4.0_ENHANCED_SUPPLEMENT.md`  
**下次评审：** 2026-06-30 09:00
