"""
Context Engineering — 上下文工程

核心原则: 上下文是稀缺资源，不是无限仓库。

四个工程化动作:
1. 结构化 — 上下文有 schema，不是自由文本
2. 分段化 — 按"系统约束/任务定义/当前状态/工具签名/历史摘要"分槽位
3. 可回放 — 每次上下文构造可重放、可 diff
4. 可审计 — 保留来源链，便于追责和调优

参考: 阿里云开发者 Harness Engineering 实践
"""

import json
import hashlib
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ContextSlot:
    """上下文槽位 — 按功能分段存储"""
    name: str                     # 槽位名称: system/task/state/tools/history
    content: str                  # 槽位内容
    priority: int = 5            # 1-10, 1最高优先
    source: str = ""             # 内容来源（可审计）
    version: str = ""            # 内容版本
    max_tokens: int = 0          # 最大 token 限制，0=无限制


@dataclass
class ContextSnapshot:
    """上下文快照 — 可回放、可 diff"""
    task_id: str
    slots: Dict[str, ContextSlot] = field(default_factory=dict)
    created_at: str = ""
    total_tokens_estimate: int = 0
    hash: str = ""  # sha256 for diff comparison

    def __post_init__(self):
        if not self.created_at:
            tz = timezone(timedelta(hours=8))
            self.created_at = datetime.now(tz).isoformat()
        if not self.hash:
            self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        data = json.dumps({k: v.content for k, v in self.slots.items()}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]


class ContextBuilder:
    """
    上下文构建器 — 工程化构建 Agent 上下文。

    铁律一: 上下文越少越好。
    不平铺所有信息，而是精挑细选，按优先级分段。

    用法:
        builder = ContextBuilder(task_id="task-001")
        builder.add_slot("system", system_prompt, priority=1)
        builder.add_slot("task", task_description, priority=2, source="orchestrator")
        builder.add_slot("state", current_state, priority=3, max_tokens=500)
        builder.add_slot("tools", tool_signatures, priority=4)
        builder.add_slot("history", summary, priority=10, max_tokens=300)
        context = builder.build()  # 返回排序、截断后的上下文
    """

    # 标准槽位定义
    STANDARD_SLOTS = {
        "system":    {"priority": 1,  "description": "系统约束与角色定义"},
        "task":      {"priority": 2,  "description": "任务定义与目标"},
        "state":     {"priority": 3,  "description": "当前状态（从Workspace读取）"},
        "tools":     {"priority": 4,  "description": "可用工具签名"},
        "history":   {"priority": 10, "description": "历史摘要（非全文）"},
        "constraint": {"priority": 5, "description": "架构约束与规则"},
    }

    def __init__(self, task_id: str, max_total_tokens: int = 4000):
        self.task_id = task_id
        self.max_total_tokens = max_total_tokens
        self.slots: Dict[str, ContextSlot] = {}
        self._build_log: List[Dict] = []  # 构建日志（可审计）

    def add_slot(self, name: str, content: str, *,
                 priority: Optional[int] = None,
                 source: str = "",
                 max_tokens: int = 0):
        """添加上下文槽位"""
        if name in self.STANDARD_SLOTS and priority is None:
            priority = self.STANDARD_SLOTS[name]["priority"]

        slot = ContextSlot(
            name=name,
            content=content,
            priority=priority or 5,
            source=source or "unknown",
            version=datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d_%H%M%S"),
            max_tokens=max_tokens,
        )
        self.slots[name] = slot
        self._build_log.append({
            "action": "add_slot",
            "slot": name,
            "source": source,
            "length": len(content),
            "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
        })

    def remove_slot(self, name: str):
        """移除上下文槽位"""
        if name in self.slots:
            self._build_log.append({
                "action": "remove_slot",
                "slot": name,
                "timestamp": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            })
            del self.slots[name]

    def build(self) -> str:
        """
        构建最终上下文字符串。

        规则:
        1. 按 priority 排序（低优先级的在前）
        2. 每个槽位如果设了 max_tokens，截断
        3. 总 token 数超过 max_total_tokens 时，从低优先级（priority数大）开始裁剪
        """
        sorted_slots = sorted(self.slots.values(), key=lambda s: s.priority)

        # 第一阶段: 构建每个槽位（应用截断）
        segments = []
        total_chars = 0

        for slot in sorted_slots:
            content = slot.content
            if slot.max_tokens > 0:
                # 粗略估算: 1 token ≈ 2 中文字符 ≈ 4 英文字符
                max_chars = slot.max_tokens * 4
                if len(content) > max_chars:
                    content = content[:max_chars] + "\n... [内容截断，剩余内容在Workspace]"
            segments.append((slot, content))

        # 第二阶段: 如果总字符数超标，从低优先级裁剪
        total_chars = sum(len(c) for _, c in segments)
        if total_chars > self.max_total_tokens * 4:
            # 从后往前裁剪（priority 高的在后面）
            target = self.max_total_tokens * 4
            for i in range(len(segments) - 1, -1, -1):
                if total_chars <= target:
                    break
                slot, content = segments[i]
                excess = total_chars - target
                new_len = max(100, len(content) - excess)
                segments[i] = (slot, content[:new_len] + "\n... [已裁剪]")
                total_chars = sum(len(c) for _, c in segments)

        # 第三阶段: 组装
        lines = []
        lines.append(f"## 任务: {self.task_id}")
        lines.append("")

        for slot, content in segments:
            lines.append(f"### {slot.name.upper()}: {slot.source}" if slot.source else f"### {slot.name.upper()}")
            lines.append(content)
            lines.append("")

        self._estimated_tokens = total_chars // 4

        return "\n".join(lines)

    def snapshot(self) -> ContextSnapshot:
        """生成上下文快照 — 用于回放和 diff"""
        return ContextSnapshot(
            task_id=self.task_id,
            slots={k: v for k, v in self.slots.items()},
            total_tokens_estimate=sum(len(v.content) for v in self.slots.values()) // 4,
        )

    def diff(self, other: 'ContextBuilder') -> Dict[str, str]:
        """Diff 两个上下文构建器 — 找出差异"""
        s1 = self.snapshot()
        s2 = other.snapshot()

        diffs = {}
        all_slots = set(s1.slots.keys()) | set(s2.slots.keys())
        for name in all_slots:
            c1 = s1.slots.get(name)
            c2 = s2.slots.get(name)
            if c1 is None:
                diffs[name] = f"+ 新增槽位 (来源: {c2.source})" if c2 else ""
            elif c2 is None:
                diffs[name] = f"- 移除槽位"
            elif c1.hash != c2.hash:  # 使用内容hash比较
                diffs[name] = f"已变更 (来源: {c2.source})"
        return diffs

    def get_audit_log(self) -> List[Dict]:
        """获取构建审计日志"""
        return self._build_log

    @property
    def estimated_tokens(self) -> int:
        return getattr(self, '_estimated_tokens', 0)


def context_for_task(task_id: str, **slots) -> str:
    """
    快捷函数: 为指定任务构建上下文。

    用法:
        ctx = context_for_task("task-001",
            system="你是小龙虾网络的AI助手",
            task="处理股票预测请求",
            state=open("workspace/state.json").read(),
        )
    """
    builder = ContextBuilder(task_id=task_id)
    for name, content in slots.items():
        builder.add_slot(name, content)
    return builder.build()
