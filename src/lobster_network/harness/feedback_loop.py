"""
Feedback Loop — 反馈回路

模式五: 智能体审智能体

核心理念:
- Agent 无法在自己的 Context Window 内客观评判自己
- Reviewer 换 Context、换角色，只看到 diff + rules
- 角色设定为"怀疑态度的 Senior Reviewer"

模式四: 上下游反压
- 上游给确定性设置
- Agent 执行
- 下游测试/Lint/CI 拒绝
- 错误信号回传 → Agent 学习修正

参考: Cursor/Cline 内置反馈回路，悟空 AI 招聘的三层护栏
"""

import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class ReviewDecision(Enum):
    APPROVE = "approve"
    REVISE = "revise"
    REJECT = "reject"


@dataclass
class ReviewResult:
    """审查结果"""
    decision: ReviewDecision
    summary: str
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    reviewer: str = ""
    context_id: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            tz = timezone(timedelta(hours=8))
            self.timestamp = datetime.now(tz).isoformat()


@dataclass
class FailureRecord:
    """失败记录 — 每个失败都是一个学习机会"""
    id: str
    task_id: str
    error_type: str             # 错误类型: tool_selection / reasoning / compliance / ...
    error_message: str
    context_summary: str        # 失败时的上下文摘要
    root_cause: str = ""
    fix_applied: str = ""
    constraint_added: str = ""  # 新增了哪条约束
    resolved: bool = False
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            tz = timezone(timedelta(hours=8))
            self.timestamp = datetime.now(tz).isoformat()


class AgentReviewer:
    """
    Agent 审查器 — 独立 Context 对 Agent 输出进行审查。

    设计要点（铁律应用）:
    - 独立 Context Window: 不与被审查 Agent 共享上下文
    - 只看 diff: 不被原始推理过程影响
    - 怀疑态度: 角色设定为 Senior Reviewer
    - 只输出结构化: ReviewResult，不自由发挥
    """

    def __init__(self, name: str = "senior-reviewer", rules_file: str = ""):
        self.name = name
        self.rules: List[str] = []
        if rules_file and os.path.exists(rules_file):
            with open(rules_file) as f:
                self.rules = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    def add_rule(self, rule: str):
        """添加审查规则"""
        self.rules.append(rule)

    def review_diff(self, original: str, modified: str, context: Dict = None) -> ReviewResult:
        """
        审查变更 — 只看 diff，不看原始推理。

        这是 Agent Review Agent 的核心实现:
        1. 只接收 git diff 格式的变更
        2. 基于规则列表逐条检查
        3. 返回结构化的审查意见
        """
        context = context or {}
        issues = []
        suggestions = []

        # 规则检查
        for rule in self.rules:
            if self._check_rule(rule, original, modified):
                issues.append(f"违反规则: {rule}")

        # 基本情况检查
        if modified == original:
            issues.append("未检测到任何变更")

        # 安全关键词检查
        security_keywords = ["password", "secret", "token", "api_key", "private_key"]
        for kw in security_keywords:
            if kw in modified.lower() and kw not in original.lower():
                issues.append(f"可能暴露敏感信息: '{kw}' 出现在变更中")
                suggestions.append(f"确认 '{kw}' 不应该使用环境变量或 Secrets Manager")

        # 决策
        if issues:
            # 检查是否有阻断级别的问题
            fatal_keywords = ["secret", "password", "token", "api_key"]
            has_fatal = any(kw in " ".join(issues).lower() for kw in fatal_keywords)
            decision = ReviewDecision.REJECT if has_fatal else ReviewDecision.REVISE
        else:
            decision = ReviewDecision.APPROVE

        return ReviewResult(
            decision=decision,
            summary=f"审查完成: {len(issues)} 个问题, {len(suggestions)} 个建议",
            issues=issues,
            suggestions=suggestions,
            reviewer=self.name,
            context_id=context.get("task_id", ""),
        )

    def review_content(self, content: str, rules: List[str] = None) -> ReviewResult:
        """审查内容 — 基于规则列表检查"""
        rules = rules or self.rules
        issues = []

        for rule in rules:
            if self._pattern_check(rule, content):
                issues.append(f"违规: {rule}")

        decision = ReviewDecision.REVISE if issues else ReviewDecision.APPROVE
        return ReviewResult(
            decision=decision,
            summary=f"规则审查: {len(issues)} 个违规",
            issues=issues,
            reviewer=self.name,
        )

    def _check_rule(self, rule: str, original: str, modified: str) -> bool:
        """检查规则是否被触发"""
        # 简单关键词匹配
        keywords = rule.lower().split()
        return any(kw in modified.lower() for kw in keywords)

    def _pattern_check(self, rule: str, content: str) -> bool:
        """基于模式检查"""
        keywords = rule.lower().split()
        return any(kw in content.lower() for kw in keywords)


class FailureAnalyzer:
    """
    失败分析器 — 将失败转化为约束。

    Harness Engineering 核心循环:
    1. Agent 失败 → 记录失败
    2. 分析根因 → 找到可工程化的解
    3. 添加约束/Linter → 阻止同类失败再次发生
    4. 验证 → 确认问题已修复

    参考: Mitchell Hashimoto "每当你发现 Agent 犯错，就工程化一个解"
    """

    def __init__(self, workspace_dir: str = ""):
        self.workspace_dir = workspace_dir
        self.failures_file = os.path.join(workspace_dir, "failures.jsonl") if workspace_dir else ""
        self.failures: List[FailureRecord] = []

    def record_failure(self, task_id: str, error_type: str,
                       error_message: str, context_summary: str) -> FailureRecord:
        """记录一次失败"""
        record = FailureRecord(
            id=f"fail-{len(self.failures)+1:04d}",
            task_id=task_id,
            error_type=error_type,
            error_message=error_message,
            context_summary=context_summary,
        )
        self.failures.append(record)

        # 持久化
        if self.failures_file:
            os.makedirs(os.path.dirname(self.failures_file), exist_ok=True)
            with open(self.failures_file, "a") as f:
                from dataclasses import asdict
                f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

        return record

    def analyze_failure(self, failure: FailureRecord) -> Dict[str, str]:
        """
        分析失败根因 → 生成约束建议。

        返回: {"root_cause": ..., "suggested_fix": ..., "suggested_constraint": ...}
        """
        analysis = {
            "root_cause": "",
            "suggested_fix": "",
            "suggested_constraint": "",
        }

        # 基于错误类型给出建议
        if failure.error_type == "tool_selection":
            analysis["root_cause"] = "工具选择空间过大或签名不清晰"
            analysis["suggested_fix"] = "限制可见工具数量，优化工具签名"
            analysis["suggested_constraint"] = f"工具选择失败 → 限制 Sub-Agent 可见工具 ≤5"

        elif failure.error_type == "context_overflow":
            analysis["root_cause"] = "上下文超载，关键信息被挤压"
            analysis["suggested_fix"] = "只携带状态摘要，不携带历史全文"
            analysis["suggested_constraint"] = f"上下文超载 → 强制 max_total_tokens={4000}"

        elif failure.error_type == "reasoning_error":
            analysis["root_cause"] = "推理链路中存在逻辑断点"
            analysis["suggested_fix"] = "增加 Self-Verification 步骤"
            analysis["suggested_constraint"] = f"推理错误 → 引入 Reviewer Agent 审查输出"

        elif failure.error_type == "compliance":
            analysis["root_cause"] = "合规约束未机器化强制执行"
            analysis["suggested_fix"] = "将合规规则写成 Linter 自动拦截"
            analysis["suggested_constraint"] = f"合规违规 → 添加 LinterConstraint: {failure.error_message[:50]}"

        else:
            analysis["root_cause"] = "未知错误类型，需人工分析"
            analysis["suggested_fix"] = "记录完整上下文供人工排查"

        # 更新失败记录
        failure.root_cause = analysis["root_cause"]
        failure.fix_applied = analysis["suggested_fix"]
        failure.constraint_added = analysis["suggested_constraint"]

        return analysis

    def generate_constraint_from_failure(self, failure: FailureRecord) -> Optional[Dict]:
        """从失败记录生成一条架构约束"""
        if not failure.constraint_added:
            return None

        return {
            "id": f"auto-constraint-{failure.id}",
            "description": failure.constraint_added.split(" → ")[1] if " → " in failure.constraint_added else failure.constraint_added,
            "failure_case": failure.error_message[:200],
            "error_type": failure.error_type,
        }

    def get_unresolved_failures(self) -> List[FailureRecord]:
        """获取未解决的失败"""
        return [f for f in self.failures if not f.resolved]

    def resolve_failure(self, failure_id: str):
        """标记失败已解决"""
        for f in self.failures:
            if f.id == failure_id:
                f.resolved = True
                break


class FeedbackLoop:
    """
    反馈回路 — 端到端反馈循环。

    流程:
    1. 上游 (Orchestrator) → 下发任务 + 确定性设置
    2. Agent → 执行任务
    3. 下游 (Reviewer + Linter) → 检查输出
    4. 错误 → 回传信号 → Agent 修正
    5. 成功 → 记录最佳实践

    这是铁律四和模式四的综合落地。
    """

    def __init__(self, reviewer: AgentReviewer = None,
                 failure_analyzer: FailureAnalyzer = None):
        self.reviewer = reviewer or AgentReviewer()
        self.failure_analyzer = failure_analyzer or FailureAnalyzer()
        self.iteration_limit = 3  # 最多修正3轮
        self.results: List[Dict] = []

    def run(self, task_id: str, executor_fn: Callable,
            review_rules: List[str] = None) -> Dict:
        """
        运行反馈循环。

        参数:
            task_id: 任务ID
            executor_fn: 执行函数，每次调用返回 (output, context)
            review_rules: 审查规则

        返回:
            {"status": "success"|"failed", "iterations": n, "final_output": ...}
        """
        result = {
            "task_id": task_id,
            "status": "pending",
            "iterations": 0,
            "final_output": None,
            "failures": [],
            "reviews": [],
        }

        for i in range(self.iteration_limit):
            # 执行
            try:
                output, context = executor_fn(i + 1)
            except Exception as e:
                self.failure_analyzer.record_failure(
                    task_id, "execution_error", str(e),
                    f"第 {i+1} 次执行失败"
                )
                result["status"] = "failed"
                result["failures"].append(str(e))
                break

            # 审查
            review = self.reviewer.review_content(output, review_rules or [])
            result["reviews"].append({
                "iteration": i + 1,
                "decision": review.decision.value,
                "issues": review.issues,
            })

            if review.decision == ReviewDecision.APPROVE:
                result["status"] = "success"
                result["final_output"] = output
                result["iterations"] = i + 1
                break
            elif review.decision == ReviewDecision.REVISE:
                # 继续修正
                result["iterations"] = i + 1
                continue
            else:  # REJECT
                result["status"] = "failed"
                result["failures"].append("审查拒绝: " + "; ".join(review.issues))
                break

        if result["status"] == "pending":
            result["status"] = "failed"
            result["failures"].append(f"超过最大迭代次数 ({self.iteration_limit})")

        self.results.append(result)
        return result

    def get_statistics(self) -> Dict:
        """获取反馈循环统计"""
        total = len(self.results)
        success = sum(1 for r in self.results if r["status"] == "success")
        avg_iterations = sum(r["iterations"] for r in self.results) / total if total > 0 else 0
        return {
            "total_tasks": total,
            "success_rate": f"{success/total*100:.1f}%" if total > 0 else "N/A",
            "avg_iterations": round(avg_iterations, 1),
            "total_failures": sum(1 for r in self.results if r["status"] == "failed"),
        }
