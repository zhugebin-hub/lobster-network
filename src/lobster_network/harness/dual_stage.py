"""
Dual-Stage Architecture — 双阶段架构

模式一: Init + Exec

核心理念:
1. Init Stage (Initializer Agent): 理解任务 → 制定计划 → 写入 plan.md → 退出
2. Exec Stage (Executor Agent): 读取 plan.md → 按步执行 → 不共享 Context Window

为什么这样做：
- 跨 Context Window 接力：Init 和 Exec 使用不同的 Context
- plan.md 是持久化的"交接棒"
- Exec 只看计划，不被初始推理过程干扰
- 支持断点续传：Exec 失败后可从上次 checkpoint 继续

参考:
- Anthropic Claude Code: Initializer + Executor 双阶段
- LangChain Deep Agents: 自我验证 + 追踪
- Mitchell Hashimoto: "状态写文件，不塞上下文"
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .workspace import Workspace, TaskStatus


class StageStatus(Enum):
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class InitStage:
    """
    Init Stage — 初始化阶段。

    职责:
    1. 理解任务
    2. 分解为子任务
    3. 写入 plan.md
    4. 退出 (不执行)

    铁律三落地: plan.md 是文件，不是上下文
    """
    task_id: str
    workspace: Workspace
    plan_content: str = ""
    subtasks: List[Dict] = field(default_factory=list)
    status: StageStatus = StageStatus.READY

    def analyze_task(self, task_description: str,
                     context: Dict[str, Any] = None) -> List[Dict]:
        """
        分析任务并生成子任务计划。

        子任务结构:
        {
            "id": "sub-1",
            "description": "验证SSH连接",
            "depends_on": [],
            "expected_output": "连接成功或失败信息",
            "timeout_minutes": 5,
        }
        """
        context = context or {}

        # 基于任务描述生成子任务
        # 这是一个模板化的分解，实际生产环境应由 LLM 完成
        subtasks = []

        # 模式识别: 根据常见任务类型分解
        task_lower = task_description.lower()

        if any(kw in task_lower for kw in ["部署", "deploy", "推送", "push"]):
            subtasks = [
                {"id": "sub-1", "description": "验证代码变更", "depends_on": [],
                 "expected_output": "变更列表和风险评估", "timeout_minutes": 5},
                {"id": "sub-2", "description": "运行测试套件", "depends_on": ["sub-1"],
                 "expected_output": "测试通过/失败", "timeout_minutes": 10},
                {"id": "sub-3", "description": "推送到远程仓库", "depends_on": ["sub-2"],
                 "expected_output": "推送成功确认", "timeout_minutes": 5},
                {"id": "sub-4", "description": "验证服务健康检查", "depends_on": ["sub-3"],
                 "expected_output": "服务状态报告", "timeout_minutes": 5},
            ]
        elif any(kw in task_lower for kw in ["同步", "sync", "训练", "train"]):
            subtasks = [
                {"id": "sub-1", "description": "拉取最新代码/数据", "depends_on": [],
                 "expected_output": "同步状态", "timeout_minutes": 5},
                {"id": "sub-2", "description": "验证数据完整性", "depends_on": ["sub-1"],
                 "expected_output": "数据校验报告", "timeout_minutes": 5},
                {"id": "sub-3", "description": "执行训练/同步", "depends_on": ["sub-2"],
                 "expected_output": "训练/同步结果", "timeout_minutes": 30},
                {"id": "sub-4", "description": "生成报告并通知", "depends_on": ["sub-3"],
                 "expected_output": "报告文件", "timeout_minutes": 5},
            ]
        else:
            # 通用分解
            subtasks = [
                {"id": "sub-1", "description": "任务分析", "depends_on": [],
                 "expected_output": "分析报告", "timeout_minutes": 5},
                {"id": "sub-2", "description": "执行任务", "depends_on": ["sub-1"],
                 "expected_output": "执行结果", "timeout_minutes": 30},
                {"id": "sub-3", "description": "验证结果", "depends_on": ["sub-2"],
                 "expected_output": "验证报告", "timeout_minutes": 5},
            ]

        self.subtasks = subtasks
        return subtasks

    def write_plan(self) -> str:
        """将计划写入 plan.md"""
        lines = [
            f"# 任务计划: {self.task_id}",
            f"# 节点: {self.workspace.node_id}",
            f"# 创建时间: {datetime.now(timezone(timedelta(hours=8))).isoformat()}",
            "",
            "## 子任务",
            "",
        ]

        for sub in self.subtasks:
            deps = ", ".join(sub.get("depends_on", [])) or "无"
            lines.append(f"- **{sub['id']}**: {sub['description']}")
            lines.append(f"  - 依赖: {deps}")
            lines.append(f"  - 期望输出: {sub.get('expected_output', 'N/A')}")
            lines.append(f"  - 超时: {sub.get('timeout_minutes', 30)} 分钟")
            lines.append("")

        self.plan_content = "\n".join(lines)
        self.workspace.save_plan(self.task_id, self.plan_content)
        self.workspace.save_task_status(self.task_id, TaskStatus.PLANNING)

        return self.plan_content

    def wait_for_confirmation(self) -> bool:
        """
        等待计划确认（由 Orchestrator 调用的阻塞点）。

        在实际系统中，这里会通过 CC Protocol 请求用户确认。
        """
        self.status = StageStatus.RUNNING
        return True  # 简化: 自动确认


@dataclass
class ExecStage:
    """
    Exec Stage — 执行阶段。

    职责:
    1. 读取 plan.md
    2. 按步执行
    3. 不共享 Init 的 Context Window
    4. 支持断点续传

    铁律三落地: 读取文件，不读上下文
    """
    task_id: str
    workspace: Workspace
    status: StageStatus = StageStatus.READY
    current_step: int = 0
    results: List[Dict] = field(default_factory=list)
    executor_fn: Optional[Callable] = None

    def load_plan(self) -> Optional[str]:
        """从 workspace 加载 plan.md"""
        return self.workspace.get_plan(self.task_id)

    def set_executor(self, fn: Callable):
        """设置执行函数"""
        self.executor_fn = fn

    def execute(self, step_id: str = None) -> Dict:
        """
        执行一个步骤。

        参数:
            step_id: 指定执行哪个子任务，None = 执行下一个

        返回: {"step": step_id, "status": "completed"/"failed", "output": ...}
        """
        if not self.executor_fn:
            return {"step": "", "status": "failed", "output": "executor_fn not set"}

        self.status = StageStatus.RUNNING
        self.workspace.save_task_status(self.task_id, TaskStatus.EXECUTING,
                                         {"step": step_id or f"auto-{self.current_step+1}"})

        try:
            output = self.executor_fn(self.task_id, step_id or f"auto-{self.current_step+1}",
                                      self.workspace)

            result = {
                "step": step_id or f"step-{len(self.results)+1}",
                "status": "completed",
                "output": output,
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            }
        except Exception as e:
            result = {
                "step": step_id or f"step-{len(self.results)+1}",
                "status": "failed",
                "output": str(e),
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            }
            self.workspace.record_failure(str(e), self.task_id)

        self.results.append(result)
        self.current_step = len(self.results)
        return result

    def execute_all(self) -> List[Dict]:
        """按顺序执行所有步骤"""
        self.status = StageStatus.RUNNING
        self.workspace.save_task_status(self.task_id, TaskStatus.EXECUTING)

        subtasks = self._parse_subtasks()
        all_results = []

        for sub in subtasks:
            result = self.execute(sub["id"])
            all_results.append(result)
            if result["status"] == "failed":
                self.status = StageStatus.FAILED
                self.workspace.save_task_status(self.task_id, TaskStatus.FAILED,
                                                 {"failed_at": sub["id"]})
                break

        if self.status != StageStatus.FAILED:
            self.status = StageStatus.COMPLETED
            self.workspace.save_task_status(self.task_id, TaskStatus.COMPLETED,
                                             {"steps_completed": len(all_results)})

        return all_results

    def _parse_subtasks(self) -> List[Dict]:
        """从 plan.md 解析子任务"""
        plan = self.load_plan()
        if not plan:
            return []

        subtasks = []
        for line in plan.split("\n"):
            if line.startswith("- **"):
                task_id = line.split("**")[1]
                desc = line.split("**: ")[1] if "**: " in line else ""
                subtasks.append({"id": task_id, "description": desc})

        return subtasks

    def resume_from(self, step_index: int) -> List[Dict]:
        """从指定步骤恢复执行（断点续传）"""
        self.current_step = step_index
        plan = self._parse_subtasks()
        remaining = plan[step_index:]
        results = []

        for sub in remaining:
            result = self.execute(sub["id"])
            results.append(result)
            if result["status"] == "failed":
                break

        return results


class DualStageExecutor:
    """
    双阶段执行器 — Init + Exec 模式。

    用法:
        workspace = Workspace("zhugebin-001")

        def my_executor(task_id, step_id, ws):
            return f"执行 {step_id} 完成"

        executor = DualStageExecutor("deploy-v4", workspace)
        executor.init("推送到服务器47.93.6.57")
        executor.set_executor(my_executor)
        results = executor.run()
    """

    def __init__(self, task_id: str, workspace: Workspace):
        self.task_id = task_id
        self.workspace = workspace
        self.init_stage = InitStage(task_id, workspace)
        self.exec_stage = ExecStage(task_id, workspace)
        self.status = StageStatus.READY

    def init(self, task_description: str, context: Dict = None) -> InitStage:
        """
        Init Stage: 分析任务，生成计划。
        """
        self.init_stage.analyze_task(task_description, context)
        self.init_stage.write_plan()
        self.init_stage.wait_for_confirmation()
        return self.init_stage

    def set_executor(self, fn: Callable):
        """设置 Exec Stage 的执行函数"""
        self.exec_stage.set_executor(fn)

    def run(self) -> List[Dict]:
        """
        Exec Stage: 执行所有步骤。

        Exec 从 workspace 读取 plan.md，不共享 Init 的 Context。
        """
        plan = self.exec_stage.load_plan()
        if not plan:
            self.status = StageStatus.FAILED
            return [{"step": "init", "status": "failed", "output": "plan.md 不存在"}]

        self.workspace.save_task_status(self.task_id, TaskStatus.EXECUTING)
        results = self.exec_stage.execute_all()

        self.status = self.exec_stage.status
        return results

    def resume(self, from_step: int) -> List[Dict]:
        """断点续传"""
        return self.exec_stage.resume_from(from_step)

    def get_progress(self) -> Dict:
        """获取当前进度"""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "init_status": self.init_stage.status.value,
            "exec_status": self.exec_stage.status.value,
            "current_step": self.exec_stage.current_step,
            "total_steps": len(self.exec_stage.results),
            "results": self.exec_stage.results,
        }
