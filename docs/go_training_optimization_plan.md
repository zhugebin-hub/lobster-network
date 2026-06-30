# 🦞 围棋训练系统优化方案

> 版本：v1.0  
> 作者：信电大虾  
> 日期：2026-06-30  
> 状态：诊断与优化方案

---

## 一、当前系统状态诊断

### 1.1 调度器状态

| 检查项 | 状态 | 问题 |
|--------|------|------|
| 调度器版本 | V4 | 运行中调度器未更新 |
| 当前 Day | 4 | 日志显示"Day 3/4 不在计划中" |
| 训练计划 | Day 3-35 | 仓库已添加，但运行中未加载 |
| 状态更新 | 2026-06-30T16:19 | 手动更新，非自动 |

**关键问题：**
- 运行中的调度器（/shared/scripts/go_coach_dispatcher_v4.py）未同步仓库最新版本
- 调度器日志显示"Day 3 不在计划中"，说明仍在使用旧版计划（Day 17+）
- 状态文件手动更新，但调度器未识别

### 1.2 学员提交状态

| 学员 | 本地提交 | 共享目录提交 | 最新提交 | 问题 |
|------|----------|--------------|----------|------|
| 小陈 | Day 3-4 | Day 2-3 | Day 4 (6/29) | 本地与共享目录不同步 |
| 诸葛虾 | 无 | Day 2 | Day 2 (6/28) | 节点可能离线 |
| qoder | Day 2-4 | Day 2-3 | Day 4 (6/29) | 本地与共享目录不同步 |

**关键问题：**
- 本地提交（.shared/training/go/from-*）与共享目录（/shared/training/go/from-*）不同步
- 诸葛虾节点可能离线（无本地提交，共享目录只有 Day 2）
- 同步服务（sync_reminder.py）未运行

### 1.3 待处理任务

| 学员 | 待处理任务 | 任务内容 | 问题 |
|------|------------|----------|------|
| 小陈 | 4 个 | Day 5 任务 | 任务已分发，但未执行 |
| 诸葛虾 | 4 个 | Day 5 任务 | 任务已分发，但未执行 |
| qoder | 4 个 | Day 5 任务 | 任务已分发，但未执行 |

**关键问题：**
- 12 个任务已分发到 inbox，但无学员执行
- 消息轮询持久化模块未集成到实际运行
- 学员端无自动轮询机制

### 1.4 核心模块状态

| 模块 | 状态 | 集成情况 |
|------|------|----------|
| phase2_training_optimizer.py | ✅ 存在 | ❌ 未集成到调度器 |
| e2e_submission_validator.py | ✅ 存在 | ❌ 未集成到调度器 |
| time_protection_v2.py | ✅ 存在 | ❌ 未集成到调度器 |
| dynamic_ability_profile.py | ✅ 存在 | ❌ 未集成到调度器 |
| rank_promotion.py | ✅ 存在 | ❌ 未集成到调度器 |
| nine_dan_plan_v2.py | ✅ 存在 | ❌ 未集成到调度器 |
| message_polling_persistence.py | ✅ 存在 | ❌ 未集成到调度器 |
| context_manager.py | ✅ 存在 | ❌ 未集成到调度器 |
| linter_system.py | ✅ 存在 | ❌ 未集成到调度器 |
| workspace_manager.py | ✅ 存在 | ❌ 未集成到调度器 |

**关键问题：**
- 所有 Phase 2-3 模块已创建并测试通过
- 但**未集成到实际运行的调度器中**
- 调度器仍在使用旧版逻辑，未调用新模块

---

## 二、根因分析

### 2.1 核心问题：模块未集成

**现象：**
- 仓库中有 10 个核心模块（Phase 1-3）
- 但运行中的调度器未调用任何新模块
- 调度器日志显示"Day X 不在计划中"

**根因：**
- 调度器脚本（/shared/scripts/go_coach_dispatcher_v4.py）未更新
- 新模块（phase2_training_optimizer.py 等）未集成到调度器
- 缺少集成测试和部署流程

### 2.2 同步问题：本地与共享目录不同步

**现象：**
- 本地提交（.shared/training/go/from-*）有 Day 3-4
- 共享目录（/shared/training/go/from-*）只有 Day 2-3
- sync_reminder.py 未运行

**根因：**
- 同步服务未启动
- 本地与共享目录使用不同路径
- 缺少自动同步机制

### 2.3 执行问题：学员未执行任务

**现象：**
- 12 个任务已分发到 inbox
- 但无学员执行记录
- 消息轮询持久化未运行

**根因：**
- 学员端无自动轮询机制
- 消息队列未与训练系统集成
- 缺少任务执行触发器

---

## 三、优化方案

### 3.1 短期优化（1-2 天）

#### 3.1.1 同步调度器到最新版本

**目标：** 让运行中的调度器加载 Day 3-35 完整计划

**步骤：**
1. 将仓库最新版本复制到运行目录
   ```bash
   cp /home/admin/lobster-network/core/dispatcher/go_coach_dispatcher_v4.py /shared/scripts/go_coach_dispatcher_v4.py
   ```

2. 重启调度器
   ```bash
   # 停止旧调度器
   pkill -f go_coach_dispatcher_v4.py
   
   # 启动新调度器
   nohup python3 /shared/scripts/go_coach_dispatcher_v4.py >> /shared/training/go/dispatcher.log 2>&1 &
   ```

3. 验证调度器加载新计划
   ```bash
   python3 -c "
   import sys
   sys.path.insert(0, '/shared/scripts')
   from go_coach_dispatcher_v4 import DAILY_PLAN_V4
   print(f'计划范围：Day {min(DAILY_PLAN_V4.keys())} - Day {max(DAILY_PLAN_V4.keys())}')
   print(f'总天数：{len(DAILY_PLAN_V4)}')
   "
   ```

#### 3.1.2 启动同步服务

**目标：** 同步本地与共享目录的训练数据

**步骤：**
1. 检查 sync_reminder.py 路径
   ```bash
   ls -la /home/admin/lobster-network/core/sync_reminder.py
   ```

2. 启动同步服务
   ```bash
   nohup python3 /home/admin/lobster-network/core/sync_reminder.py >> /shared/training/go/sync_reminder.log 2>&1 &
   ```

3. 验证同步状态
   ```bash
   tail -20 /shared/training/go/sync_reminder.log
   ```

#### 3.1.3 集成 Phase 2 模块到调度器

**目标：** 让调度器调用新模块

**步骤：**
1. 创建集成脚本
   ```python
   # /shared/scripts/go_training_integration.py
   import sys
   sys.path.insert(0, '/home/admin/lobster-network/core')
   
   from phase2_training_optimizer import Phase2TrainingOptimizer
   from e2e_submission_validator import E2ESubmissionValidator
   from time_protection_v2 import TimeProtectionV2
   
   # 初始化模块
   optimizer = Phase2TrainingOptimizer()
   validator = E2ESubmissionValidator()
   protector = TimeProtectionV2()
   
   # 集成到调度器
   def run_training_day(day):
       # 1. 时间保护检查
       window = protector.check_training_window()
       if not window['in_training_window']:
           print(f"⚠️ 不在训练窗口内，跳过 Day {day}")
           return
       
       # 2. 生成训练任务
       for student_id in ['xiaochen', 'zhuguxia', 'qoder']:
           tasks = optimizer.generate_training_tasks(student_id)
           results = optimizer.distribute_tasks(tasks)
           print(f"✅ {student_id}: {results[student_id]} 个任务已分发")
       
       # 3. 端到端验证
       validation = validator.run_full_validation()
       print(f"✅ 验证结果：{validation['overall_status']}")
   ```

2. 修改调度器调用集成脚本
   ```python
   # 在 go_coach_dispatcher_v4.py 中添加
   import importlib.util
   spec = importlib.util.spec_from_file_location("integration", "/shared/scripts/go_training_integration.py")
   integration = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(integration)
   
   # 在调度循环中调用
   integration.run_training_day(status['day'])
   ```

### 3.2 中期优化（3-7 天）

#### 3.2.1 实现学员端自动轮询

**目标：** 学员端自动轮询 inbox，执行任务

**步骤：**
1. 创建学员端轮询脚本
   ```python
   # /shared/scripts/student_polling.py
   import sys
   import time
   from pathlib import Path
   
   def poll_student_inbox(student_id, interval=300):
       """轮询学员 inbox"""
       inbox_dir = Path(f"/home/admin/lobster-network/lobster-data/messages/queue/{student_id}/inbox")
       
       while True:
           # 扫描 inbox
           tasks = list(inbox_dir.glob("phase2_task_*.json"))
           
           if tasks:
               print(f"📥 {student_id}: 发现 {len(tasks)} 个任务")
               
               for task_file in tasks:
                   # 执行任务
                   execute_task(student_id, task_file)
                   
                   # 移动到 processed
                   task_file.rename(inbox_dir.parent / "processed" / task_file.name)
           
           time.sleep(interval)
   
   def execute_task(student_id, task_file):
       """执行训练任务"""
       import json
       with open(task_file) as f:
           task = json.load(f)
       
       print(f"🎯 执行任务：{task['task_name']}")
       
       # 调用训练模块
       # ... (实际执行逻辑)
       
       print(f"✅ 任务完成：{task['task_name']}")
   
   # 启动轮询
   if __name__ == "__main__":
       for student_id in ['xiaochen', 'zhuguxia', 'qoder']:
           poll_student_inbox(student_id)
   ```

2. 启动轮询服务
   ```bash
   nohup python3 /shared/scripts/student_polling.py >> /shared/training/go/polling.log 2>&1 &
   ```

#### 3.2.2 集成动态能力画像

**目标：** 每日更新学员能力画像，动态调整训练计划

**步骤：**
1. 创建每日画像更新脚本
   ```python
   # /shared/scripts/daily_profile_update.py
   import sys
   sys.path.insert(0, '/home/admin/lobster-network/core')
   
   from dynamic_ability_profile import DynamicAbilityProfile
   
   def update_all_profiles():
       """更新所有学员能力画像"""
       for student_id in ['xiaochen', 'zhuguxia', 'qoder']:
           profile = DynamicAbilityProfile(student_id)
           profile.update_profile()
           print(f"✅ {student_id} 画像已更新")
   
   if __name__ == "__main__":
       update_all_profiles()
   ```

2. 添加到 cron 任务
   ```bash
   # 每天 07:00 更新画像
   0 7 * * * python3 /shared/scripts/daily_profile_update.py >> /shared/training/go/profile_update.log 2>&1
   ```

#### 3.2.3 实现段位晋升检查

**目标：** 每日检查学员晋升条件，达标自动晋升

**步骤：**
1. 创建晋升检查脚本
   ```python
   # /shared/scripts/daily_promotion_check.py
   import sys
   sys.path.insert(0, '/home/admin/lobster-network/core')
   
   from rank_promotion import RankPromotionSystem
   
   def check_all_promotions():
       """检查所有学员晋升条件"""
       for student_id in ['xiaochen', 'zhuguxia', 'qoder']:
           system = RankPromotionSystem(student_id)
           result = system.check_promotion()
           
           if result.get('can_promote'):
               # 执行晋升
               system.promote()
               print(f"🎉 {student_id} 晋升到 {result['next_rank']}")
           else:
               print(f"⏳ {student_id} 暂未满足晋升条件")
   
   if __name__ == "__main__":
       check_all_promotions()
   ```

2. 添加到 cron 任务
   ```bash
   # 每天 07:30 检查晋升
   30 7 * * * python3 /shared/scripts/daily_promotion_check.py >> /shared/training/go/promotion_check.log 2>&1
   ```

### 3.3 长期优化（1-2 周）

#### 3.3.1 实现 Session Graph 集成

**目标：** 将 OpenRath 的 Session Graph 集成到训练系统

**步骤：**
1. 创建 Session 数据结构
   ```python
   # /home/admin/lobster-network/core/session_graph.py
   class TrainingSession:
       """训练 Session"""
       
       def __init__(self, session_id, student_id, day):
           self.session_id = session_id
           self.student_id = student_id
           self.day = day
           self.status = "active"
           self.chunks = []
           self.graph = {"forks": [], "merges": [], "branches": []}
           self.metadata = {}
       
       def add_chunk(self, chunk_type, content):
           """添加数据块"""
           chunk = {
               "chunk_id": f"chunk_{len(self.chunks)+1:03d}",
               "type": chunk_type,
               "content": content,
               "timestamp": datetime.now().isoformat(),
           }
           self.chunks.append(chunk)
           return chunk
       
       def fork(self, new_session_id):
           """分叉 Session"""
           self.graph["forks"].append({
               "from": self.session_id,
               "to": new_session_id,
               "timestamp": datetime.now().isoformat(),
           })
           return new_session_id
   ```

2. 集成到调度器
   ```python
   # 在调度器中使用 Session
   session = TrainingSession(f"session_{day}_{student_id}", student_id, day)
   session.add_chunk("task", task_data)
   session.add_chunk("result", result_data)
   
   # 保存 Session
   with open(f"/shared/training/go/sessions/{session.session_id}.json", 'w') as f:
       json.dump(session.__dict__, f, indent=2)
   ```

#### 3.3.2 实现 Linter 约束系统

**目标：** 用 Linter 替代文档约束，确保规则执行

**步骤：**
1. 创建训练任务 Linter
   ```python
   # /shared/scripts/training_linter.py
   import sys
   sys.path.insert(0, '/home/admin/lobster-network/core')
   
   from linter_system import TrainingLinter, CommunicationLinter, ToolLinter
   
   def lint_training_task(task):
       """检查训练任务合法性"""
       linter = TrainingLinter()
       result = linter.validate_task(task)
       
       if not result['valid']:
           print(f"❌ 任务不合法：{result['errors']}")
           return False
       
       print(f"✅ 任务合法：{result['task_id']}")
       return True
   
   def lint_communication(message):
       """检查通信合法性"""
       linter = CommunicationLinter()
       result = linter.validate_message(message)
       
       if not result['valid']:
           print(f"❌ 消息不合法：{result['errors']}")
           return False
       
       print(f"✅ 消息合法：{result['msg_id']}")
       return True
   ```

2. 集成到消息处理流程
   ```python
   # 在处理消息前进行 Linter 检查
   if not lint_communication(message):
       print("⚠️ 消息未通过 Linter 检查，拒绝处理")
       continue
   ```

#### 3.3.3 实现 Workspace 状态管理

**目标：** 用 Workspace 替代分散的状态管理

**步骤：**
1. 创建统一 Workspace 结构
   ```
   /shared/training/go/workspace/
   ├── agents/
   │   ├── orchestrator/
   │   │   ├── state.json
   │   │   ├── tasks/
   │   │   └── history/
   │   ├── training/
   │   │   ├── state.json
   │   │   ├── schedule.json
   │   │   └── evaluations/
   │   └── communication/
   │       ├── state.json
   │       ├── routes.json
   │       └── ack_log.json
   ├── tasks/
   │   └── {task_id}/
   │       ├── plan.md
   │       ├── state.json
   │       ├── progress.json
   │       └── result.json
   ├── context/
   │   ├── schema.json
   │   ├── filters/
   │   └── cache/
   └── locks/
       ├── training/
       └── communication/
   ```

2. 集成到调度器
   ```python
   # 使用 Workspace 管理状态
   from workspace_manager import WorkspaceManager
   
   workspace = WorkspaceManager()
   
   # 创建任务
   task = workspace.create_task(task_id, task_data)
   
   # 更新进度
   workspace.update_task_progress(task_id, step, status)
   
   # 完成任务
   workspace.complete_task(task_id, result)
   ```

---

## 四、实施计划

### Phase 1：紧急修复（1-2 天）

| 任务 | 负责人 | 预计时间 | 状态 |
|------|--------|----------|------|
| 同步调度器到最新版本 | 信电大虾 | 2 小时 | 待执行 |
| 启动同步服务 | 信电大虾 | 1 小时 | 待执行 |
| 集成 Phase 2 模块到调度器 | 信电大虾 | 4 小时 | 待执行 |
| 验证调度器加载新计划 | 信电大虾 | 1 小时 | 待执行 |

### Phase 2：中期优化（3-7 天）

| 任务 | 负责人 | 预计时间 | 状态 |
|------|--------|----------|------|
| 实现学员端自动轮询 | 信电大虾 | 1 天 | 待执行 |
| 集成动态能力画像 | 信电大虾 | 1 天 | 待执行 |
| 实现段位晋升检查 | 信电大虾 | 1 天 | 待执行 |
| 配置 cron 定时任务 | 信电大虾 | 2 小时 | 待执行 |

### Phase 3：长期优化（1-2 周）

| 任务 | 负责人 | 预计时间 | 状态 |
|------|--------|----------|------|
| 实现 Session Graph 集成 | 信电大虾 | 3 天 | 待执行 |
| 实现 Linter 约束系统 | 信电大虾 | 2 天 | 待执行 |
| 实现 Workspace 状态管理 | 信电大虾 | 3 天 | 待执行 |
| 完整集成测试 | 信电大虾 | 2 天 | 待执行 |

---

## 五、预期收益

| 指标 | 当前 | 优化后 | 提升 |
|------|------|--------|------|
| 调度器计划完整度 | 50% | 100% | +50% |
| 任务执行率 | 0% | 80% | +80% |
| 数据同步及时性 | 低 | 高 | +100% |
| 模块集成度 | 0% | 100% | +100% |
| 系统可靠性 | 低 | 高 | +100% |

---

## 六、风险控制

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 调度器更新失败 | 训练中断 | 保留旧版调度器，快速回滚 |
| 同步服务冲突 | 数据不一致 | 使用文件锁，避免并发写入 |
| 模块集成错误 | 功能异常 | 分阶段集成，每阶段测试验证 |
| 学员端轮询失败 | 任务未执行 | 添加重试机制，超时告警 |

---

## 七、总结

**核心问题：**
- 调度器未更新到最新版本
- 新模块未集成到实际运行
- 同步服务未启动
- 学员端无自动轮询机制

**优化方向：**
- 短期：同步调度器、启动同步服务、集成 Phase 2 模块
- 中期：实现自动轮询、动态画像、段位晋升
- 长期：集成 Session Graph、Linter 约束、Workspace 管理

**预期效果：**
- 调度器计划完整度 100%
- 任务执行率 80%+
- 数据同步及时性 100%
- 模块集成度 100%
- 系统可靠性显著提升

**Agent 是工人，Session 才是工作本身。Harness Engineering 让 Agent 可控地工作。** 🦞
