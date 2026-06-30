# 🦞 小龙虾网络 Harness Engineering 升级方案

> 生成时间：2026-06-30 15:30 UTC+8
> 设计人：诸葛马 (Hermes)
> 基于：阿里云《Agent Harness 工程实践》

---

## 一、核心洞察

### 1.1 一个公式

```
Agent = Model + Harness
```

- **模型**负责推理
- **Harness**负责"剩下的所有事情"：工具系统、上下文管理、权限控制、反馈回路、记忆与协作

**LangChain 实验验证：**
| 案例 | 模型是否更换 | 关键动作 | 效果 |
|------|-------------|----------|------|
| LangChain × Terminal Bench 2.0 | 未更换 | 优化Harness：自我验证+追踪+文档 | 排行榜30→5；得分52.8→66.5 |

### 1.2 范式三次跃迁

| 代际 | 范式 | 核心问题 | 形象对比 |
|------|------|----------|----------|
| 第一代 | Prompt Engineering | 怎么把话说清楚 | 对马喊话的技巧 |
| 第二代 | Context Engineering | 怎么给AI喂对信息 | 给马看的地图 |
| **第三代** | **Harness Engineering** | **怎么让Agent可控地工作** | **给马造高速公路，配护栏、限速牌、加油站** |

---

## 二、四条铁律

### 铁律一：上下文越少越好（不是越多越好）

**工程师本能**：信息越多决策越准
**Harness真相**：上下文是稀缺资源，会被污染、会相互干扰、会让模型"逛超市"

**小龙虾网络实现：**
```python
class ContextManager:
    """上下文管理器：精挑细选，少即是多"""
    def __init__(self, max_tokens=8000):
        self.max_tokens = 8000  # 限制上下文
        self.slots = {
            "system_constraints": [],  # 系统约束
            "task_definition": [],     # 任务定义
            "current_state": [],       # 当前状态
            "tool_signatures": [],     # 工具签名
            "history_summary": [],     # 历史摘要
        }
```

**改进前**：塞入所有历史、所有工具、所有规则
**改进后**：按槽位分段，只加载当前任务需要的上下文

---

### 铁律二：专才Agent永远赢过通才Agent

**工程师本能**：做一个超级Agent，什么都会
**Harness真相**：通才Agent在工具列表里"逛超市"，永远跑不过一组职责清晰的专才

**小龙虾网络实现：**
```python
class SpecializedAgent:
    """专才Agent：职责单一，工具精简"""
    def __init__(self, agent_id, name, role, skills=None, max_tools=5):
        self.max_tools = 5  # 限制工具数量
```

**改进前**：一个Agent承担规划/执行/审查/记忆多角色
**改进后**：
- Planner：只负责规划（工具≤5）
- Executor：只负责执行（工具≤5）
- Reviewer：只负责审查（工具≤5）
- Memory：只负责记忆（工具≤5）

**悟空招聘经验**：Agent数量不要超过3个，Skill可以无限加

---

### 铁律三：状态要写文件，不要塞上下文

**工程师本能**：让Agent"记住"任务进展
**Harness真相**：上下文是易失存储，文件系统才是持久内存

**小龙虾网络实现：**
```python
class WorkspaceManager:
    """Workspace是真相，Context只是工位"""
    def create_task_workspace(self, task_id):
        # 创建标准文件结构
        files = {
            "plan.md": "...",      # 计划
            "state.json": "...",   # 状态
            "log.md": "...",       # 日志
        }
    
    def create_lock(self, task_id, lock_type):
        """事务边界：RPA开始写lock文件"""
```

**改进前**：状态存在Session内存中，重启丢失
**改进后**：
- `plan.md`：Initializer写入，Executor读取
- `state.json`：持久化状态
- `log.md`：执行日志
- `rpa_lock/`：事务边界，断点续传

---

### 铁律四：能写成Linter的约束，别写成文档

**工程师本能**：把规则写进AGENTS.md让Agent自己读
**Harness真相**：文档只是"建议"，Linter/CI才是"强制"

**小龙虾网络实现：**
```python
class Linter:
    """机器可执行的约束"""
    rules = [
        {"rule_id": "R001", "name": "工具数量限制", "check_fn": ...},
        {"rule_id": "R002", "name": "上下文长度限制", "check_fn": ...},
        {"rule_id": "R003", "name": "Agent数量限制", "check_fn": ...},
        {"rule_id": "R004", "name": "外部消息审核", "check_fn": ...},
        {"rule_id": "R005", "name": "敏感词拦截", "check_fn": ...},
    ]
```

**每条规则对应一个真实失败案例**：
| 规则 | 失败案例 |
|------|----------|
| 工具数量限制 | 悟空招聘第一版：13个工具导致Agent逛超市 |
| 上下文长度限制 | AGENTS.md 800行，模型读完前200行开始幻觉 |
| Agent数量限制 | 悟空招聘堆到第6个Agent时编排层开始选错 |
| 外部消息审核 | RPA跑到一半顺手回复候选人聊天 |
| 敏感词拦截 | 对外消息事故：每周一两次 |

---

## 三、六大工程模式

### 模式1：双阶段架构（Initializer + Executor）

```
Initializer Agent → plan.md → Executor Agent
    (规划)              (执行)
```

**原则**：两个Agent不共享Context Window，只通过Workspace里的plan.md接力

**实现**：
```python
class TwoStageWorkflow:
    def run(self, task_id, initializer, executor, task_desc):
        # 阶段1：Initializer制定计划
        plan = initializer.generate_plan(task_desc)
        self.workspace.write_plan(task_id, plan)
        
        # 阶段2：Executor读取计划执行
        plan_content = self.workspace.read_plan(task_id)
        result = executor.execute_plan(plan_content)
```

---

### 模式2：工具签名即文档

**原则**：工具名是动词短语，参数schema每个字段都带description

**实现**：
```python
class Skill:
    def __init__(self, name, description, func, signature=None):
        self.signature = {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "count": {"type": "int", "description": "题目数量"},
                    ...
                }
            }
        }
```

---

### 模式3：Sub-Agent隔离

**原则**：每个Sub-Agent有独立Context Window，只看自己需要的工具

**实现**：
```python
class SubAgentIsolator:
    def get_isolated_context(self, agent_id):
        agent = self.sub_agents[agent_id]
        return f"""# {agent['role']}
## 你的职责
{agent['role']}
## 可用工具
{', '.join(agent['tools'])}
"""
```

---

### 模式4：上下游反压

```
上游设置 → Agent执行 → 下游Linter/CI验证 → 拒绝 → 回传上游调整
```

**原则**：Linter的错误信息本身就是上下文工程

**实现**：
```python
class BackpressureController:
    def execute_with_backpressure(self, executor_fn, target):
        for attempt in range(self.max_retries):
            result = executor_fn(target)
            violations = self.linter.check(result)
            if not violations:
                return {"success": True, "result": result}
            target["feedback"] = {"violations": violations}
```

---

### 模式5：智能体审智能体

**原则**：换Context审查，不是用同样的Context再评估

**实现**：
```python
class AgentReviewer:
    def __init__(self):
        self.reviewer_role = "怀疑态度的Senior Reviewer"
    
    def review(self, work_product, rules=None):
        review_context = f"""# 审查任务
## 审查者角色
{self.reviewer_role}
## 审查规则
{rules}
"""
```

---

### 模式6：熵管理与文档园丁

**原则**：持续小额偿还技术债，不要攒到爆雷

**实现**：
```python
class DocumentGardener:
    def scan(self):
        """扫描过期文档和架构漂移"""
        for file in files:
            age_days = (now - mtime) / 86400
            if age_days > 30:
                issues.append({"type": "stale_document", "age_days": age_days})
    
    def generate_cleanup_pr(self, issues):
        """生成清理PR"""
```

---

## 四、硬护栏：三层防护

**悟空招聘经验**：对外说话和动用户数据必须有硬护栏

```
第1层：白名单工具（只能调发消息工具，禁用撤回/群发）
第2层：Linter拦截（敏感词/合规规则）
第3层：第二个Agent审稿（独立Context判断）
```

**效果**：对外消息事故率从"每周一两次"降到"记不清上一次是什么时候"

**实现**：
```python
class HardGuardrails:
    def check_message(self, message):
        return {
            "layer1_tool_check": self._check_tool_whitelist(message),
            "layer2_linter_check": self._check_linter(message),
            "layer3_reviewer_check": self._check_reviewer(message),
        }
```

---

## 五、与OpenRath的融合

| 维度 | OpenRath | Harness Engineering | 融合方案 |
|------|----------|---------------------|----------|
| 数据载体 | Session | Workspace文件 | Session持久化到Workspace |
| Agent角色 | 变换层 | 专才Agent | 专才变换层 |
| 上下文 | Session chunks | ContextManager槽位 | 分段Session |
| 约束 | 无 | Linter强制 | Linter集成到Session验证 |
| 路由 | Selector | 反压控制器 | Selector+反压 |
| 记忆 | Memory Backend | Workspace状态文件 | 双写记忆 |

---

## 六、六句心法

| # | 心法 | 一句话注解 |
|---|------|------------|
| 1 | 你优化的不是Agent，是Agent的工作环境 | 把它当作员工，而不是工具 |
| 2 | 上下文是稀缺资源，不是无限仓库 | 少即是多，干净比丰富更重要 |
| 3 | 状态写在文件里，不在脑子里 | Context是工位，Workspace才是档案 |
| 4 | 能写成Linter的约束，别写成文档 | 机器能强制的，永远比人能记住的可靠 |
| 5 | Agent昂贵，Skill廉价，护栏最便宜 | 能用Skill解决别加Agent，能用Linter拦下别靠Prompt |
| 6 | 对外说话和动用户数据要有硬护栏 | Prompt可以漏，模型可以错，但合规底线不能破 |

---

## 七、实施清单

### 已完成
- [x] 上下文管理器（ContextManager）
- [x] 专才Agent（SpecializedAgent）
- [x] Workspace管理器（WorkspaceManager）
- [x] Linter（5条规则）
- [x] 双阶段工作流（TwoStageWorkflow）
- [x] Sub-Agent隔离（SubAgentIsolator）
- [x] 反压控制器（BackpressureController）
- [x] Agent Reviewer（AgentReviewer）
- [x] 文档园丁（DocumentGardener）
- [x] 硬护栏（HardGuardrails）

### 下一步
- [ ] 将现有Session持久化到Workspace
- [ ] 将sync_reminder集成到Executor
- [ ] 将e2e_validation集成到Linter
- [ ] 将time_protection集成到Backpressure
- [ ] 将dynamic_profile集成到Memory
- [ ] 部署文档园丁cron任务

---

*方案由诸葛马 (Hermes) 自动生成 | 基于阿里云《Agent Harness 工程实践》*
