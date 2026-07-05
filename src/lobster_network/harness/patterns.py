"""
Harness Engineering Patterns — 六大工程模式

基于阿里云开发者 Harness Engineering 实践的模式标准化实现。

六种模式:
1. 双阶段架构 (DualStagePattern)           — 跨会话接力
2. 工具签名即文档 (ToolSignaturePattern)    — 防止Agent选错工具
3. Sub-Agent 隔离 (SubAgentIsolationPattern) — 防止上下文污染
4. 上下游反压 (BackpressurePattern)          — 防止无限循环
5. 智能体审智能体 (AgentReviewPattern)       — 独立语境审查
6. 熵管理与文档园丁 (EntropyManagementPattern) — 防止代码腐化

每个模式都是可组合的、可复用的原语。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone, timedelta
from enum import Enum
import json
import os


class PatternStatus(Enum):
    APPLIED = "applied"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class PatternResult:
    """模式执行结果"""
    pattern_name: str
    status: PatternStatus
    message: str
    data: Dict = field(default_factory=dict)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            tz = timezone(timedelta(hours=8))
            self.timestamp = datetime.now(tz).isoformat()


class HarnessPattern(ABC):
    """Harness 模式基类"""

    def __init__(self, name: str):
        self.name = name
        self.status = PatternStatus.INACTIVE
        self._history: List[PatternResult] = []

    @abstractmethod
    def apply(self, context: Dict[str, Any]) -> PatternResult:
        """应用模式"""
        pass

    def deactivate(self):
        self.status = PatternStatus.INACTIVE

    def get_history(self) -> List[PatternResult]:
        return self._history

    def _record(self, result: PatternResult):
        self._history.append(result)
        self.status = result.status


class DualStagePattern(HarnessPattern):
    """
    模式一: 双阶段架构

    解决问题: 跨会话延续、不依赖单次 Context Window
    机制: Init Agent 写 plan.md → Exec Agent 读取执行 → 不共享 Context

    适用场景:
    - 复杂多步骤任务
    - 需要跨会话执行
    - 可能中断后恢复

    反例: 一个 Agent 在单次 Context Window 内完成复杂任务
    """

    def __init__(self):
        super().__init__("dual_stage")
        self.plans: Dict[str, Dict] = {}

    def apply(self, context: Dict[str, Any]) -> PatternResult:
        task_id = context.get("task_id", "unknown")
        task_desc = context.get("task_description", "")
        plan_dir = context.get("plan_dir", ".shared/workspace/plans")

        try:
            # Init: 生成计划
            plan = self._generate_plan(task_id, task_desc)
            os.makedirs(plan_dir, exist_ok=True)
            plan_path = os.path.join(plan_dir, f"{task_id}.json")
            with open(plan_path, 'w') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)

            self.plans[task_id] = plan
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ACTIVE,
                message=f"双阶段计划已生成: {len(plan.get('steps', []))} 步",
                data={"task_id": task_id, "plan_path": plan_path},
            )
        except Exception as e:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message=f"双阶段计划生成失败: {e}",
            )

    def _generate_plan(self, task_id: str, task_desc: str) -> Dict:
        return {
            "task_id": task_id,
            "description": task_desc,
            "stages": [
                {"name": "init", "description": "初始化: 分析任务"},
                {"name": "exec", "description": "执行: 按步执行"},
                {"name": "verify", "description": "验证: 检查结果"},
                {"name": "report", "description": "报告: 生成结果"},
            ],
            "steps": [
                {"id": "step-1", "stage": "init", "action": "分析"},
                {"id": "step-2", "stage": "exec", "action": "执行"},
                {"id": "step-3", "stage": "verify", "action": "验证"},
            ],
        }


class ToolSignaturePattern(HarnessPattern):
    """
    模式二: 工具签名即文档

    解决问题: Agent 选错工具
    机制: 工具名是动词短语、参数 schema 带 description、返回值结构稳定

    落地: 为每个工具定义清晰的签名，包含:
    - name: 动词短语 (如 "read_file", "run_tests")
    - description: 一句话说明用途
    - parameters: JSON Schema
    - returns: 返回值结构和含义
    """

    def __init__(self):
        super().__init__("tool_signature")

    def apply(self, context: Dict[str, Any]) -> PatternResult:
        tools = context.get("tools", [])
        if not tools:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message="未提供工具列表",
            )

        validated = []
        issues = []
        for tool in tools:
            check = self._validate_signature(tool)
            if check["valid"]:
                validated.append(tool)
            else:
                issues.append(check["issue"])

        if issues:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message=f"{len(issues)} 个工具签名不规范",
                data={"issues": issues, "validated": len(validated)},
            )

        return PatternResult(
            pattern_name=self.name,
            status=PatternStatus.ACTIVE,
            message=f"{len(validated)} 个工具签名验证通过",
            data={"count": len(validated)},
        )

    def _validate_signature(self, tool: Dict) -> Dict:
        issues = []
        name = tool.get("name", "")
        desc = tool.get("description", "")

        if not name:
            issues.append("缺少 name 字段")
        elif not any(v in name for v in ["_", "-"]):
            # 检查是否是动词短语
            pass

        if not desc:
            issues.append("缺少 description 字段")

        if "parameters" not in tool:
            issues.append("缺少 parameters schema")

        return {"valid": len(issues) == 0, "issue": "; ".join(issues) if issues else ""}


class SubAgentIsolationPattern(HarnessPattern):
    """
    模式三: Sub-Agent 隔离

    解决问题: 上下文污染 & 工具选择空间爆炸
    机制:
    - 独立 Context Window
    - 只看到需要的工具
    - 只接收结构化输出

    铁律二落地: 专才 > 通才

    落地规则:
    - 每个 Sub-Agent 最多可见 5 个工具
    - Prompt 控制在 100 行内
    - 输出必须是结构化的 JSON
    """

    MAX_TOOLS_PER_AGENT = 5
    MAX_PROMPT_LINES = 100

    def __init__(self):
        super().__init__("sub_agent_isolation")
        self.agents: Dict[str, Dict] = {}

    def apply(self, context: Dict[str, Any]) -> PatternResult:
        agent_name = context.get("agent_name", "unnamed")
        tools = context.get("tools", [])
        prompt = context.get("prompt", "")

        checks = []

        # 检查工具数量
        if len(tools) > self.MAX_TOOLS_PER_AGENT:
            checks.append(f"工具数 {len(tools)} 超过上限 {self.MAX_TOOLS_PER_AGENT}")

        # 检查 Prompt 行数
        prompt_lines = prompt.count("\n") + 1 if prompt else 0
        if prompt_lines > self.MAX_PROMPT_LINES:
            checks.append(f"Prompt {prompt_lines} 行超过上限 {self.MAX_PROMPT_LINES}")

        if checks:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message="Sub-Agent 隔离检查失败",
                data={"agent": agent_name, "issues": checks},
            )

        self.agents[agent_name] = {
            "tools": [t.get("name", "unnamed") for t in tools],
            "prompt_lines": prompt_lines,
            "created_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        }

        return PatternResult(
            pattern_name=self.name,
            status=PatternStatus.ACTIVE,
            message=f"Sub-Agent '{agent_name}' 隔离配置完成 ({len(tools)} 工具, {prompt_lines} 行 prompt)",
            data={"agent": agent_name, "tools": len(tools)},
        )


class BackpressurePattern(HarnessPattern):
    """
    模式四: 上下游反压

    解决问题: 无限循环、错误无法自我修复
    机制:
    - 上游给确定性设置
    - Agent 执行
    - 下游测试/Lint/CI 拒绝
    - 错误信号回传 → Agent 修正

    落地: 设置最大迭代次数、超时、失败后自动上报
    """

    def __init__(self, max_iterations: int = 3, timeout_minutes: int = 30):
        super().__init__("backpressure")
        self.max_iterations = max_iterations
        self.timeout_minutes = timeout_minutes

    def apply(self, context: Dict[str, Any]) -> PatternResult:
        iteration = context.get("iteration", 1)

        if iteration > self.max_iterations:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message=f"超过最大迭代次数 ({self.max_iterations})，触发反压",
                data={"reason": "max_iterations_exceeded"},
            )

        return PatternResult(
            pattern_name=self.name,
            status=PatternStatus.ACTIVE,
            message=f"反压模式激活 (迭代 {iteration}/{self.max_iterations})",
            data={"remaining": self.max_iterations - iteration},
        )

    def check_timeout(self, started_at: str) -> PatternResult:
        """检查是否超时"""
        tz = timezone(timedelta(hours=8))
        start = datetime.fromisoformat(started_at) if started_at else datetime.now(tz)
        elapsed = (datetime.now(tz) - start).total_seconds() / 60

        if elapsed > self.timeout_minutes:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message=f"超时 ({elapsed:.0f} 分钟 > {self.timeout_minutes} 分钟)，触发反压",
                data={"reason": "timeout"},
            )

        return PatternResult(
            pattern_name=self.name,
            status=PatternStatus.ACTIVE,
            message=f"执行中 ({elapsed:.0f} 分钟)",
        )


class AgentReviewPattern(HarnessPattern):
    """
    模式五: 智能体审智能体

    解决问题: 自我合理化、偏见无法被同一 Context 识别
    机制:
    - Reviewer 只看 diff + rules
    - 换 Context
    - 角色设定为"怀疑态度的 Senior Reviewer"

    落地: 每个 Agent 输出都经过独立 Reviewer 检查
    """

    def __init__(self, rules: List[str] = None):
        super().__init__("agent_review")
        self.rules = rules or [
            "输出必须是完整可执行的结果",
            "不能有未解决的外部依赖",
            "敏感信息(密钥/密码)不得出现在输出中",
            "所有文件操作必须使用绝对路径",
        ]

    def apply(self, context: Dict[str, Any]) -> PatternResult:
        content = context.get("content", "")
        agent_name = context.get("agent_name", "unknown")

        issues = []
        for rule in self.rules:
            # 简化检查: 关键词匹配
            if "敏感" in rule and any(kw in content.lower() for kw in ["password", "secret", "token"]):
                issues.append(rule)

        if issues:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ERROR,
                message=f"Agent '{agent_name}' 输出未通过审查",
                data={"issues": issues},
            )

        return PatternResult(
            pattern_name=self.name,
            status=PatternStatus.ACTIVE,
            message=f"Agent '{agent_name}' 输出审查通过",
            data={"rules_applied": len(self.rules)},
        )


class EntropyManagementPattern(HarnessPattern):
    """
    模式六: 熵管理与文档园丁

    解决问题: 代码库与文档随时间腐化
    机制:
    - 后台 Agent 定期扫描过期文档
    - 检测架构漂移
    - 提交清理 PR

    铁律: 持续小额偿还技术债，不要让熵积累
    """

    def __init__(self, scan_interval_days: int = 7):
        super().__init__("entropy_management")
        self.scan_interval_days = scan_interval_days

    def apply(self, context: Dict[str, Any]) -> PatternResult:
        root_dir = context.get("root_dir", ".")
        pattern = context.get("scan_pattern", "*.md")

        stale_files = self._find_stale_files(root_dir, pattern)

        if stale_files:
            return PatternResult(
                pattern_name=self.name,
                status=PatternStatus.ACTIVE,
                message=f"发现 {len(stale_files)} 个可能过期的文件",
                data={"stale_files": stale_files},
            )

        return PatternResult(
            pattern_name=self.name,
            status=PatternStatus.ACTIVE,
            message="未发现过期文件",
        )

    def _find_stale_files(self, root_dir: str, pattern: str) -> List[str]:
        import glob
        tz = timezone(timedelta(hours=8))
        threshold = datetime.now(tz).timestamp() - (self.scan_interval_days * 86400)

        stale = []
        for fpath in glob.glob(os.path.join(root_dir, "**", pattern), recursive=True):
            if os.path.getmtime(fpath) < threshold:
                name = os.path.relpath(fpath, root_dir)
                age_days = int((datetime.now(tz).timestamp() - os.path.getmtime(fpath)) / 86400)
                stale.append(f"{name} ({age_days}天)")

        return stale


# ============================================================
# 模式工厂: 一键应用所有模式
# ============================================================

ALL_PATTERNS = {
    "dual_stage": DualStagePattern,
    "tool_signature": ToolSignaturePattern,
    "sub_agent_isolation": SubAgentIsolationPattern,
    "backpressure": BackpressurePattern,
    "agent_review": AgentReviewPattern,
    "entropy_management": EntropyManagementPattern,
}


def apply_pattern(pattern_name: str, context: Dict[str, Any]) -> PatternResult:
    """
    快捷函数: 应用单个模式。

    用法:
        result = apply_pattern("agent_review", {
            "content": agent_output,
            "agent_name": "matcher",
        })
        if result.status == PatternStatus.ERROR:
            print(f"审查失败: {result.message}")
    """
    if pattern_name not in ALL_PATTERNS:
        return PatternResult(
            pattern_name=pattern_name,
            status=PatternStatus.ERROR,
            message=f"未知模式: {pattern_name}，可用: {list(ALL_PATTERNS.keys())}",
        )

    pattern = ALL_PATTERNS[pattern_name]()
    return pattern.apply(context)
