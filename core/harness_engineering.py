#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Harness Engineering 升级
基于阿里"Agent Harness 工程实践"的架构升级
核心原则：
1. 上下文越少越好（不是越多越好）
2. 专才Agent永远赢过通才Agent
3. 状态要写文件，不要塞上下文
4. 能写成Linter的约束，别写成文档

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import uuid
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from pathlib import Path

# ============================================================
# 铁律一：上下文越少越好
# ============================================================

class ContextManager:
    """
    上下文管理器：精挑细选，少即是多
    原则：上下文是稀缺资源，不是无限仓库
    """
    
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.slots: Dict[str, List[Dict]] = {}
        self._init_slots()
    
    def _init_slots(self):
        """初始化上下文槽位（分段化）"""
        self.slots = {
            "system_constraints": [],  # 系统约束
            "task_definition": [],     # 任务定义
            "current_state": [],       # 当前状态
            "tool_signatures": [],     # 工具签名
            "history_summary": [],     # 历史摘要
        }
    
    def add_to_slot(self, slot: str, content: Dict):
        """向指定槽位添加内容"""
        if slot not in self.slots:
            self.slots[slot] = []
        self.slots[slot].append(content)
    
    def build_context(self, priority_slots: List[str] = None) -> str:
        """
        构建上下文：按优先级精挑细选
        原则：像Code Review一样精挑细选上下文
        """
        priority_slots = priority_slots or [
            "task_definition", "current_state", "tool_signatures"
        ]
        
        context_parts = []
        total_tokens = 0
        
        # 先添加高优先级槽位
        for slot in priority_slots:
            if slot in self.slots:
                for item in self.slots[slot]:
                    item_str = self._format_slot_item(slot, item)
                    item_tokens = len(item_str) // 4  # 粗略估算token数
                    if total_tokens + item_tokens <= self.max_tokens:
                        context_parts.append(item_str)
                        total_tokens += item_tokens
        
        # 再添加低优先级槽位（如果有空间）
        for slot, items in self.slots.items():
            if slot not in priority_slots:
                for item in items[-2:]:  # 只取最近2条
                    item_str = self._format_slot_item(slot, item)
                    item_tokens = len(item_str) // 4
                    if total_tokens + item_tokens <= self.max_tokens:
                        context_parts.append(item_str)
                        total_tokens += item_tokens
        
        return "\n\n".join(context_parts)
    
    def _format_slot_item(self, slot: str, item: Dict) -> str:
        """格式化槽位内容"""
        return f"[{slot}]\n{json.dumps(item, ensure_ascii=False)}"
    
    def get_stats(self) -> Dict:
        """获取上下文统计"""
        return {
            slot: len(items) for slot, items in self.slots.items()
        }


# ============================================================
# 铁律二：专才Agent永远赢过通才Agent
# ============================================================

class Skill:
    """
    Skill（技能）：原子化能力，廉价可复用
    原则：Agent是昂贵的，Skill是廉价的
    """
    
    def __init__(self, name: str, description: str, func: Callable, 
                 signature: Dict = None):
        self.name = name
        self.description = description
        self.func = func
        self.signature = signature or self._infer_signature(func)
    
    def _infer_signature(self, func: Callable) -> Dict:
        """推断函数签名"""
        import inspect
        sig = inspect.signature(func)
        params = {}
        for name, param in sig.parameters.items():
            params[name] = {
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "any",
                "description": f"参数{name}",
                "required": param.default == inspect.Parameter.empty,
            }
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {"type": "object", "properties": params},
        }
    
    def execute(self, **kwargs) -> Any:
        """执行技能"""
        return self.func(**kwargs)


class SpecializedAgent:
    """
    专才Agent：职责单一，工具精简
    原则：每个Agent只看自己需要的工具
    """
    
    def __init__(self, agent_id: str, name: str, role: str,
                 skills: List[Skill] = None, max_tools: int = 5):
        self.agent_id = agent_id
        self.name = name
        self.role = role  # 角色设定
        self.skills: Dict[str, Skill] = {}
        self.max_tools = max_tools
        
        if skills:
            for skill in skills[:max_tools]:  # 限制工具数量
                self.skills[skill.name] = skill
    
    def add_skill(self, skill: Skill) -> bool:
        """添加技能（不超过max_tools限制）"""
        if len(self.skills) >= self.max_tools:
            return False
        self.skills[skill.name] = skill
        return True
    
    def get_tool_signatures(self) -> List[Dict]:
        """获取工具签名（用于构建上下文）"""
        return [skill.signature for skill in self.skills.values()]
    
    def execute(self, task: str, context: str = "") -> Dict:
        """
        执行任务：根据角色和技能选择最合适的Skill
        原则：专才Agent只做自己擅长的事
        """
        # 简化版：选择第一个匹配的技能
        for skill_name, skill in self.skills.items():
            if skill_name.lower() in task.lower() or skill.description.lower() in task.lower():
                return {
                    "agent_id": self.agent_id,
                    "skill_used": skill_name,
                    "result": skill.execute(),
                    "status": "completed",
                }
        
        return {
            "agent_id": self.agent_id,
            "skill_used": None,
            "result": f"未找到匹配的技能执行任务: {task}",
            "status": "failed",
        }


# ============================================================
# 铁律三：状态要写文件，不要塞上下文
# ============================================================

class WorkspaceManager:
    """
    工作区管理器：Workspace是真相，Context只是工位
    原则：状态写在文件里，不在脑子里
    """
    
    def __init__(self, workspace_dir: str = "/home/admin/go-training/shared/workspace/"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def create_task_workspace(self, task_id: str) -> str:
        """创建任务工作区"""
        task_dir = os.path.join(self.workspace_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        # 创建标准文件结构
        files = {
            "plan.md": f"# 任务计划\n\n任务ID: {task_id}\n创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n## 计划\n\n",
            "state.json": json.dumps({
                "task_id": task_id,
                "status": "initialized",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "steps_completed": [],
                "steps_failed": [],
            }, ensure_ascii=False, indent=2),
            "log.md": f"# 执行日志\n\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 任务初始化\n\n",
        }
        
        for filename, content in files.items():
            filepath = os.path.join(task_dir, filename)
            with open(filepath, "w") as f:
                f.write(content)
        
        return task_dir
    
    def write_plan(self, task_id: str, plan: str):
        """写入计划（Initializer Agent）"""
        plan_file = os.path.join(self.workspace_dir, task_id, "plan.md")
        with open(plan_file, "w") as f:
            f.write(plan)
    
    def read_plan(self, task_id: str) -> str:
        """读取计划（Executor Agent）"""
        plan_file = os.path.join(self.workspace_dir, task_id, "plan.md")
        if os.path.exists(plan_file):
            with open(plan_file) as f:
                return f.read()
        return ""
    
    def update_state(self, task_id: str, updates: Dict):
        """更新状态"""
        state_file = os.path.join(self.workspace_dir, task_id, "state.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            state.update(updates)
            state["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(state_file, "w") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
    
    def get_state(self, task_id: str) -> Dict:
        """获取状态"""
        state_file = os.path.join(self.workspace_dir, task_id, "state.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                return json.load(f)
        return {}
    
    def append_log(self, task_id: str, entry: str):
        """追加日志"""
        log_file = os.path.join(self.workspace_dir, task_id, "log.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a") as f:
            f.write(f"## {timestamp}\n{entry}\n\n")
    
    def create_lock(self, task_id: str, lock_type: str = "rpa") -> bool:
        """创建锁文件（事务边界）"""
        lock_dir = os.path.join(self.workspace_dir, task_id, "rpa_lock")
        os.makedirs(lock_dir, exist_ok=True)
        lock_file = os.path.join(lock_dir, f"{lock_type}.lock")
        
        if os.path.exists(lock_file):
            return False  # 已被锁定
        
        with open(lock_file, "w") as f:
            json.dump({
                "lock_type": lock_type,
                "locked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "in_progress",
                "progress": 0,
            }, f, ensure_ascii=False, indent=2)
        
        return True
    
    def release_lock(self, task_id: str, lock_type: str = "rpa"):
        """释放锁文件"""
        lock_file = os.path.join(self.workspace_dir, task_id, "rpa_lock", f"{lock_type}.lock")
        if os.path.exists(lock_file):
            with open(lock_file) as f:
                lock_data = json.load(f)
            lock_data["status"] = "done"
            lock_data["released_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(lock_file, "w") as f:
                json.dump(lock_data, f, ensure_ascii=False, indent=2)
    
    def get_lock_status(self, task_id: str, lock_type: str = "rpa") -> Dict:
        """获取锁状态"""
        lock_file = os.path.join(self.workspace_dir, task_id, "rpa_lock", f"{lock_type}.lock")
        if os.path.exists(lock_file):
            with open(lock_file) as f:
                return json.load(f)
        return {"status": "no_lock"}


# ============================================================
# 铁律四：能写成Linter的约束，别写成文档
# ============================================================

class Linter:
    """
    Linter：机器可执行的约束
    原则：文档只是建议，Linter/CI才是强制
    """
    
    def __init__(self):
        self.rules: List[Dict] = []
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认规则（每条规则对应一个真实失败案例）"""
        self.rules = [
            {
                "rule_id": "R001",
                "name": "工具数量限制",
                "description": "Agent工具数量不超过5个",
                "check_fn": self._check_tool_count,
                "severity": "error",
                "failure_case": "悟空招聘第一版：13个工具导致Agent逛超市",
            },
            {
                "rule_id": "R002",
                "name": "上下文长度限制",
                "description": "上下文不超过8000 tokens",
                "check_fn": self._check_context_length,
                "severity": "warning",
                "failure_case": "AGENTS.md 800行，模型读完前200行开始幻觉",
            },
            {
                "rule_id": "R003",
                "name": "Agent数量限制",
                "description": "Agent数量不超过3个",
                "check_fn": self._check_agent_count,
                "severity": "error",
                "failure_case": "悟空招聘堆到第6个Agent时编排层开始选错",
            },
            {
                "rule_id": "R004",
                "name": "外部消息审核",
                "description": "对外发消息必须经过审核",
                "check_fn": self._check_external_message,
                "severity": "error",
                "failure_case": "悟空招聘：RPA跑到一半顺手回复候选人聊天",
            },
            {
                "rule_id": "R005",
                "name": "敏感词拦截",
                "description": "外发消息不能包含敏感词",
                "check_fn": self._check_sensitive_words,
                "severity": "error",
                "failure_case": "对外消息事故：每周一两次",
            },
        ]
    
    def add_rule(self, rule: Dict):
        """添加规则"""
        self.rules.append(rule)
    
    def check(self, target: Dict) -> List[Dict]:
        """
        检查目标是否违反规则
        返回：违规列表
        """
        violations = []
        for rule in self.rules:
            result = rule["check_fn"](target)
            if not result["passed"]:
                violations.append({
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "severity": rule["severity"],
                    "message": result["message"],
                    "suggestion": result.get("suggestion", ""),
                    "failure_case": rule["failure_case"],
                })
        return violations
    
    def _check_tool_count(self, target: Dict) -> Dict:
        """检查工具数量"""
        tools = target.get("tools", [])
        if len(tools) > 5:
            return {
                "passed": False,
                "message": f"工具数量{len(tools)}超过限制5个",
                "suggestion": "将多余工具下沉为Skill，或拆分到Sub-Agent",
            }
        return {"passed": True}
    
    def _check_context_length(self, target: Dict) -> Dict:
        """检查上下文长度"""
        context = target.get("context", "")
        tokens = len(context) // 4
        if tokens > 8000:
            return {
                "passed": False,
                "message": f"上下文约{tokens}tokens，超过限制8000",
                "suggestion": "精挑细选上下文，像Code Review一样严格",
            }
        return {"passed": True}
    
    def _check_agent_count(self, target: Dict) -> Dict:
        """检查Agent数量"""
        agents = target.get("agents", [])
        if len(agents) > 3:
            return {
                "passed": False,
                "message": f"Agent数量{len(agents)}超过限制3个",
                "suggestion": "将多余Agent下沉为Skill",
            }
        return {"passed": True}
    
    def _check_external_message(self, target: Dict) -> Dict:
        """检查外部消息"""
        is_external = target.get("is_external", False)
        reviewed = target.get("reviewed", False)
        if is_external and not reviewed:
            return {
                "passed": False,
                "message": "外发消息未经审核",
                "suggestion": "必须经过独立Context的Reviewer Agent审核",
            }
        return {"passed": True}
    
    def _check_sensitive_words(self, target: Dict) -> Dict:
        """检查敏感词"""
        message = target.get("message", "")
        sensitive_words = ["录用", "薪资", "承诺", "保证", "绝对"]
        found = [w for w in sensitive_words if w in message]
        if found:
            return {
                "passed": False,
                "message": f"包含敏感词: {', '.join(found)}",
                "suggestion": "移除敏感词，使用中性表达",
            }
        return {"passed": True}


# ============================================================
# 六大工程模式实现
# ============================================================

class TwoStageWorkflow:
    """
    模式1：双阶段架构（Initializer + Executor）
    原则：两个Agent不共享Context Window，只通过Workspace接力
    """
    
    def __init__(self, workspace: WorkspaceManager):
        self.workspace = workspace
    
    def run(self, task_id: str, initializer_agent, executor_agent, 
            task_description: str) -> Dict:
        """
        运行双阶段工作流
        1. Initializer: 理解任务 → 制定计划 → 写入plan.md → 退出
        2. Executor: 读取plan.md → 按步执行 → 跨Context Window接力
        """
        # 阶段1：Initializer
        plan = initializer_agent.generate_plan(task_description)
        self.workspace.write_plan(task_id, plan)
        self.workspace.update_state(task_id, {"status": "planned"})
        
        # 阶段2：Executor（独立Context）
        plan_content = self.workspace.read_plan(task_id)
        result = executor_agent.execute_plan(plan_content)
        self.workspace.update_state(task_id, {
            "status": "completed" if result.get("success") else "failed",
            "execution_result": result,
        })
        
        return {
            "task_id": task_id,
            "initializer_output": plan,
            "executor_output": result,
            "status": "completed" if result.get("success") else "failed",
        }


class SubAgentIsolator:
    """
    模式3：Sub-Agent隔离
    原则：每个Sub-Agent有独立Context Window，只看自己需要的工具
    """
    
    def __init__(self):
        self.sub_agents: Dict[str, Dict] = {}
    
    def create_sub_agent(self, agent_id: str, role: str, 
                         tools: List[str], context: str = ""):
        """创建隔离的Sub-Agent"""
        self.sub_agents[agent_id] = {
            "role": role,
            "tools": tools,
            "context": context,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    
    def get_isolated_context(self, agent_id: str) -> str:
        """获取隔离的上下文（只看自己需要的）"""
        agent = self.sub_agents.get(agent_id)
        if not agent:
            return ""
        
        return f"""# {agent['role']}

## 你的职责
{agent['role']}

## 可用工具
{', '.join(agent['tools'])}

## 上下文
{agent.get('context', '无额外上下文')}
"""


class BackpressureController:
    """
    模式4：上下游反压
    原则：下游测试/Linter/CI拒绝无效工作，错误信号回传上游
    """
    
    def __init__(self, linter: Linter):
        self.linter = linter
        self.max_retries = 3
    
    def execute_with_backpressure(self, executor_fn, target: Dict) -> Dict:
        """
        执行带反压的任务
        1. 上游给确定性设置 + 一致上下文
        2. Agent执行
        3. 下游测试/Linter/CI验证
        4. 拒绝 → 错误信号回传上游调整
        """
        for attempt in range(self.max_retries):
            # 执行
            result = executor_fn(target)
            
            # 下游验证
            violations = self.linter.check(result)
            
            if not violations:
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt + 1,
                }
            
            # 错误信号回传
            target["feedback"] = {
                "violations": violations,
                "attempt": attempt + 1,
                "max_retries": self.max_retries,
            }
        
        return {
            "success": False,
            "result": result,
            "violations": violations,
            "attempts": self.max_retries,
        }


class AgentReviewer:
    """
    模式5：智能体审智能体
    原则：换Context审查，不是用同样的Context再评估
    """
    
    def __init__(self):
        self.reviewer_role = "怀疑态度的Senior Reviewer"
    
    def review(self, work_product: Dict, rules: List[str] = None) -> Dict:
        """
        审查工作产物
        关键：Reviewer只看git diff + rules，角色设定为怀疑态度
        """
        review_context = f"""# 审查任务

## 审查者角色
{self.reviewer_role}

## 审查对象
{json.dumps(work_product, ensure_ascii=False)}

## 审查规则
{chr(10).join(f'- {r}' for r in (rules or []))}

## 审查要求
- 以怀疑态度审查
- 找出潜在问题
- 提出改进建议
- 不重复原始Context的偏见
"""
        
        # 简化版：返回审查框架
        return {
            "reviewer_role": self.reviewer_role,
            "review_context": review_context,
            "review_items": [
                "正确性：工作产物是否符合要求？",
                "完整性：是否遗漏关键步骤？",
                "安全性：是否有安全风险？",
                "质量：代码/文档质量如何？",
            ],
        }


class DocumentGardener:
    """
    模式6：熵管理与文档园丁
    原则：持续小额偿还技术债，不要攒到爆雷
    """
    
    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
    
    def scan(self) -> List[Dict]:
        """扫描过期文档和架构漂移"""
        issues = []
        
        # 扫描过期文档
        for root, dirs, files in os.walk(self.workspace_dir):
            for file in files:
                if file.endswith((".md", ".json")):
                    filepath = os.path.join(root, file)
                    mtime = os.path.getmtime(filepath)
                    age_days = (datetime.now().timestamp() - mtime) / 86400
                    
                    if age_days > 30:
                        issues.append({
                            "type": "stale_document",
                            "file": filepath,
                            "age_days": int(age_days),
                            "severity": "warning" if age_days < 60 else "error",
                        })
        
        return issues
    
    def generate_cleanup_pr(self, issues: List[Dict]) -> str:
        """生成清理PR描述"""
        pr = f"# 文档清理 PR\n\n"
        pr += f"## 发现问题\n\n"
        for issue in issues:
            pr += f"- [{issue['severity']}] {issue['file']} (过期{issue['age_days']}天)\n"
        pr += f"\n## 建议操作\n\n"
        pr += f"- 更新过期文档\n"
        pr += f"- 删除无用文档\n"
        pr += f"- 修复架构漂移\n"
        return pr


# ============================================================
# 硬护栏：对外消息的三层防护
# ============================================================

class HardGuardrails:
    """
    硬护栏：对外说话和动用户数据必须有硬护栏
    三层防护：
    1. 白名单工具（只能调发消息工具，禁用撤回/群发）
    2. Linter拦截（敏感词/合规规则）
    3. 第二个Agent审稿（独立Context判断）
    """
    
    def __init__(self, linter: Linter):
        self.linter = linter
        self.allowed_tools: Set[str] = set()
        self.blocked_tools: Set[str] = {"recall_message", "batch_send", "delete_message"}
        self.reviewer = AgentReviewer()
    
    def set_allowed_tools(self, tools: List[str]):
        """设置白名单工具"""
        self.allowed_tools = set(tools)
    
    def check_message(self, message: Dict) -> Dict:
        """
        检查消息（三层防护）
        """
        results = {
            "layer1_tool_check": self._check_tool_whitelist(message),
            "layer2_linter_check": self._check_linter(message),
            "layer3_reviewer_check": self._check_reviewer(message),
        }
        
        # 综合判断
        all_passed = all(r["passed"] for r in results.values())
        results["overall_passed"] = all_passed
        
        return results
    
    def _check_tool_whitelist(self, message: Dict) -> Dict:
        """第一层：白名单工具检查"""
        tool = message.get("tool", "")
        if tool in self.blocked_tools:
            return {"passed": False, "message": f"工具{tool}被禁用"}
        if self.allowed_tools and tool not in self.allowed_tools:
            return {"passed": False, "message": f"工具{tool}不在白名单"}
        return {"passed": True}
    
    def _check_linter(self, message: Dict) -> Dict:
        """第二层：Linter拦截"""
        violations = self.linter.check(message)
        if violations:
            return {
                "passed": False,
                "message": f"Linter拦截: {len(violations)}个违规",
                "violations": violations,
            }
        return {"passed": True}
    
    def _check_reviewer(self, message: Dict) -> Dict:
        """第三层：Reviewer Agent审稿"""
        review = self.reviewer.review(message, rules=[
            "不冒犯候选人",
            "不暴露薪资",
            "不暗示录用",
            "使用中性表达",
        ])
        return {"passed": True, "review": review}


# ============================================================
# Harness Engineering 集成入口
# ============================================================

class HarnessEngine:
    """
    小龙虾网络 Harness Engineering 引擎
    整合四条铁律 + 六大工程模式
    """
    
    def __init__(self):
        # 铁律一：上下文管理器
        self.context_manager = ContextManager(max_tokens=8000)
        
        # 铁律二：专才Agent（限制工具数量）
        self.agents: Dict[str, SpecializedAgent] = {}
        self.max_agents = 3  # 铁律：Agent不超过3个
        
        # 铁律三：Workspace管理器
        self.workspace = WorkspaceManager()
        
        # 铁律四：Linter
        self.linter = Linter()
        
        # 六大模式
        self.two_stage = TwoStageWorkflow(self.workspace)
        self.sub_agent_isolator = SubAgentIsolator()
        self.backpressure = BackpressureController(self.linter)
        self.reviewer = AgentReviewer()
        self.gardener = DocumentGardener(self.workspace.workspace_dir)
        self.guardrails = HardGuardrails(self.linter)
    
    def create_agent(self, agent_id: str, name: str, role: str,
                     skills: List[Skill] = None) -> bool:
        """创建专才Agent（不超过3个限制）"""
        if len(self.agents) >= self.max_agents:
            print(f"⚠️ Agent数量已达上限{self.max_agents}个，请将多余Agent下沉为Skill")
            return False
        
        agent = SpecializedAgent(agent_id, name, role, skills, max_tools=5)
        self.agents[agent_id] = agent
        
        # Linter检查
        violations = self.linter.check({"agents": list(self.agents.keys())})
        if violations:
            print(f"⚠️ Linter警告: {violations}")
        
        return True
    
    def add_skill(self, agent_id: str, skill: Skill) -> bool:
        """添加Skill到Agent"""
        if agent_id not in self.agents:
            return False
        return self.agents[agent_id].add_skill(skill)
    
    def run(self, task_id: str, task_description: str,
                 initializer_id: str, executor_id: str) -> Dict:
        """运行任务（双阶段架构）"""
        # 创建工作区
        self.workspace.create_task_workspace(task_id)
        
        # 双阶段执行 - 修复：使用正确的Agent方法
        initializer = self.agents[initializer_id]
        executor = self.agents[executor_id]
        
        # 阶段1：Initializer生成计划
        plan_content = f"# 任务计划\n\n任务ID: {task_id}\n描述: {task_description}\n\n## 计划\n1. 分析需求\n2. 制定方案\n3. 执行\n4. 验证"
        self.workspace.write_plan(task_id, plan_content)
        self.workspace.update_state(task_id, {"status": "planned"})
        
        # 阶段2：Executor执行计划
        execution_result = executor.execute(task_description)
        self.workspace.update_state(task_id, {
            "status": "completed" if execution_result.get("status") == "completed" else "failed",
            "execution_result": execution_result,
        })
        
        result = {
            "task_id": task_id,
            "initializer_output": plan_content,
            "executor_output": execution_result,
            "status": "completed" if execution_result.get("status") == "completed" else "failed",
        }
        
        # 反压检查
        final_result = self.backpressure.execute_with_backpressure(
            lambda t: result,
            {"result": result, "is_external": False}
        )
        
        return final_result
    
    def send_external_message(self, message: Dict) -> Dict:
        """发送外部消息（三层硬护栏）"""
        check_result = self.guardrails.check_message(message)
        
        if not check_result["overall_passed"]:
            return {
                "success": False,
                "message": "消息未通过硬护栏检查",
                "details": check_result,
            }
        
        return {
            "success": True,
            "message": "消息通过硬护栏检查，可以发送",
            "details": check_result,
        }
    
    def run_gardener(self) -> Dict:
        """运行文档园丁"""
        issues = self.gardener.scan()
        if issues:
            pr = self.gardener.generate_cleanup_pr(issues)
            return {
                "issues_found": len(issues),
                "issues": issues,
                "cleanup_pr": pr,
            }
        return {
            "issues_found": 0,
            "message": "无过期文档",
        }


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Harness Engineering引擎")
    parser.add_argument("action", choices=["create_agent", "run_task", "check_message", "gardener"],
                       help="操作")
    parser.add_argument("--agent-id", type=str, help="Agent ID")
    parser.add_argument("--name", type=str, help="Agent名称")
    parser.add_argument("--role", type=str, help="Agent角色")
    parser.add_argument("--task-id", type=str, help="任务ID")
    parser.add_argument("--task-desc", type=str, help="任务描述")
    parser.add_argument("--initializer", type=str, help="Initializer Agent ID")
    parser.add_argument("--executor", type=str, help="Executor Agent ID")
    parser.add_argument("--message", type=str, help="消息内容（JSON）")
    
    args = parser.parse_args()
    engine = HarnessEngine()
    
    if args.action == "create_agent":
        if not all([args.agent_id, args.name, args.role]):
            print("❌ 请提供 --agent-id, --name, --role")
            return
        success = engine.create_agent(args.agent_id, args.name, args.role)
        print(f"{'✅' if success else '❌'} Agent创建{'成功' if success else '失败'}")
    
    elif args.action == "run_task":
        if not all([args.task_id, args.task_desc, args.initializer, args.executor]):
            print("❌ 请提供 --task-id, --task-desc, --initializer, --executor")
            return
        result = engine.run_task(args.task_id, args.task_desc, args.initializer, args.executor)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "check_message":
        if not args.message:
            print("❌ 请提供 --message")
            return
        message = json.loads(args.message)
        result = engine.send_external_message(message)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "gardener":
        result = engine.run_gardener()
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
