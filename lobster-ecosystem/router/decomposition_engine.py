#!/usr/bin/env python3
"""
 递归自主式分解引擎 v1.0
============================
核心功能：
  - 将宏观任务递归分解为元业务（原子任务）
  - 构建任务DAG（依赖关系图）
  - 约束剪枝（时间/预算/安全/质量/依赖）
  - 执行者匹配（基于能力画像三维量化）
  - 协作模式选择（A/B/C/D四种模式）

设计来源：案例002「递归自主式分解与人机协作新范式」
"""

import json
import uuid
import re
import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger("decomposition-engine")

# ============ 数据模型 ============

class CollaborationMode(Enum):
    A = "pure_ai"        # 纯AI执行
    B = "ai_with_review" # AI执行+人工审核
    C = "human_led"      # 人工主导+AI辅助
    D = "parallel"       # 人机并行

class TaskStatus(Enum):
    PENDING = "pending"
    DECOMPOSING = "decomposing"
    MATCHING = "matching"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Constraint:
    """约束条件"""
    time_deadline: Optional[str] = None       # 截止时间 ISO格式
    time_urgency: str = "normal"              # urgent/high/normal/low
    budget_max: float = 999999                # 最大成本（token数）
    budget_currency: str = "tokens"
    safety_level: str = "low"                 # low/medium/high/critical
    quality_min: float = 0.0                  # 最低质量要求（0-1）
    review_required: bool = False             # 是否需要人工审核
    dependencies: list = field(default_factory=list)  # 依赖的元业务ID

@dataclass
class ExecutorCandidate:
    """执行者候选"""
    service_id: str
    name: str
    role: str
    cost: float = 5.0          # 成本评分（越低越好）
    speed: float = 0.7         # 速度评分（0-1，越高越快）
    quality: float = 0.8       # 质量评分（0-1，越高越好）
    capability_match: float = 0.5  # 能力匹配度（0-1）
    online: bool = True
    load: float = 0.0          # 当前负载（0-1）
    max_concurrent: int = 3
    score: float = 0.0         # 综合评分

@dataclass
class MetaBusiness:
    """元业务（原子任务）"""
    id: str
    title: str
    description: str
    task_type: str
    constraints: Constraint
    executor_candidates: list = field(default_factory=list)
    selected_executor: Optional[str] = None
    collaboration_mode: str = "A"
    dependency_ids: list = field(default_factory=list)
    estimated_cost: float = 0.0
    estimated_time: float = 0.0  # 分钟
    status: str = "pending"
    result: Optional[dict] = None

@dataclass
class DecompositionPlan:
    """分解计划"""
    task_id: str
    original_task: str
    constraints: dict
    meta_businesses: list = field(default_factory=list)
    dag: dict = field(default_factory=dict)
    estimated_total_cost: float = 0.0
    estimated_total_time: float = 0.0
    status: str = "pending"
    created_at: str = ""

# ============ 任务类型识别 ============

TASK_TYPE_KEYWORDS = {
    "go_training_task": ["围棋", "死活", "手筋", "定式", "布局", "对局", "训练", "做题"],
    "go_match": ["对局", "下棋", "比赛", "match", "落子"],
    "go_review": ["复盘", "点评", "分析", "review"],
    "review_request": ["评审", "审核", "评价", "review", "评价报告"],
    "content_generation": ["生成", "撰写", "写", "创作", "文档", "报告", "论文"],
    "document_analysis": ["分析", "解析", "解读", "提取", "文档", "文件"],
    "strategic_planning": ["规划", "方案", "设计", "战略", "生态"],
    "teaching_analysis": ["教学", "课程", "分析", "评分", "评价"],
    "schedule_management": ["日程", "提醒", "安排", "计划"],
}

# ============ 协作模式规则 ============

COLLABORATION_RULES = {
    "go_training_task": "A",    # 围棋训练：纯AI
    "go_match": "D",            # 对局：人机并行
    "go_review": "C",           # 复盘：人工主导
    "review_request": "B",      # 评审：AI+人审
    "content_generation": "C",  # 内容生成：人工主导+AI辅助
    "document_analysis": "A",   # 文档分析：纯AI
    "strategic_planning": "C",  # 战略规划：人工主导
    "teaching_analysis": "B",   # 教学分析：AI+人审
    "schedule_management": "A", # 日程管理：纯AI
}

# ============ 递归分解引擎 ============

class DecompositionEngine:
    """递归自主式分解引擎"""

    def __init__(self, capability_db=None, service_registry=None):
        """
        Args:
            capability_db: 能力画像数据库（dict: service_id -> profile）
            service_registry: 服务注册表（dict: service_id -> service_info）
        """
        self.capability_db = capability_db or {}
        self.service_registry = service_registry or {}
        self.decomposition_depth = 0
        self.max_depth = 5  # 最大递归深度

    def decompose_task(self, task_description: str, constraints: dict = None) -> DecompositionPlan:
        """
        将宏观任务递归分解为元业务

        Args:
            task_description: 用户自然语言描述的任务
            constraints: 约束条件字典

        Returns:
            DecompositionPlan: 分解计划
        """
        self.decomposition_depth = 0
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        constraint_obj = self._parse_constraints(constraints or {})

        logger.info(f"开始分解任务: {task_id}")
        logger.info(f"任务描述: {task_description[:100]}...")

        # 步骤1：语义理解 - 提取任务组件
        components = self._extract_components(task_description)
        logger.info(f"提取到 {len(components)} 个任务组件")

        # 步骤2：递归分解
        meta_businesses = []
        for i, component in enumerate(components):
            mbs = self._recursive_decompose(
                component, constraint_obj, parent_id=None, depth=0
            )
            meta_businesses.extend(mbs)

        # 步骤3：构建DAG
        dag = self._build_dag(meta_businesses)

        # 步骤4：计算预估成本和时间
        total_cost = sum(mb.estimated_cost for mb in meta_businesses)
        total_time = self._calculate_critical_path(meta_businesses, dag)

        plan = DecompositionPlan(
            task_id=task_id,
            original_task=task_description,
            constraints=constraints or {},
            meta_businesses=meta_businesses,
            dag=dag,
            estimated_total_cost=total_cost,
            estimated_total_time=total_time,
            status="decomposed",
            created_at=datetime.now().isoformat()
        )

        logger.info(f"分解完成: {len(meta_businesses)} 个元业务, "
                   f"预估成本: {total_cost}, 预估时间: {total_time}分钟")
        return plan

    def _parse_constraints(self, constraints: dict) -> Constraint:
        """解析约束条件"""
        c = Constraint()

        if "time" in constraints:
            time_c = constraints["time"]
            if isinstance(time_c, dict):
                c.time_deadline = time_c.get("deadline")
                c.time_urgency = time_c.get("urgency", "normal")
            elif isinstance(time_c, str):
                c.time_deadline = time_c

        if "budget" in constraints:
            budget_c = constraints["budget"]
            if isinstance(budget_c, dict):
                c.budget_max = budget_c.get("max_cost", 999999)
                c.budget_currency = budget_c.get("currency", "tokens")
            elif isinstance(budget_c, (int, float)):
                c.budget_max = budget_c

        if "safety" in constraints:
            safety_c = constraints["safety"]
            if isinstance(safety_c, dict):
                c.safety_level = safety_c.get("level", "low")

        if "quality" in constraints:
            quality_c = constraints["quality"]
            if isinstance(quality_c, dict):
                c.quality_min = quality_c.get("min_accuracy", 0.0)
                c.review_required = quality_c.get("review_required", False)

        return c

    def _extract_components(self, task_description: str) -> list:
        """
        从自然语言中提取任务组件

        策略：
        1. 识别参与者（人名/角色）
        2. 识别任务类型关键词
        3. 按参与者×任务类型交叉生成组件
        4. 识别额外组件（汇总、评审等）
        """
        components = []

        # 识别参与者
        participants = self._extract_participants(task_description)

        # 识别任务组件
        task_components = self._extract_task_components(task_description)

        # 交叉生成：每个参与者 × 每个任务组件
        if participants and task_components:
            for participant in participants:
                for tc in task_components:
                    components.append({
                        "title": f"{participant['name']}_{tc['type']}",
                        "description": f"为{participant['name']}执行{tc['description']}",
                        "task_type": tc['type'],
                        "participant": participant['id'],
                        "is_atomic": tc.get('is_atomic', True)
                    })
        elif task_components:
            for tc in task_components:
                components.append({
                    "title": tc['type'],
                    "description": tc['description'],
                    "task_type": tc['type'],
                    "is_atomic": tc.get('is_atomic', True)
                })

        # 识别汇总/评审类额外组件
        if "汇总" in task_description or "报告" in task_description or "点评" in task_description:
            components.append({
                "title": "训练结果汇总与点评",
                "description": "汇总所有训练结果并生成点评",
                "task_type": "go_review",
                "is_atomic": True,
                "is_summary": True
            })

        return components

    def _extract_participants(self, text: str) -> list:
        """提取参与者"""
        participants = []

        # 预定义的参与者映射
        participant_map = {
            "诸葛虾": {"id": "lobster-002", "name": "诸葛虾", "role": "worker"},
            "小陈": {"id": "xiaochen", "name": "小陈", "role": "student"},
            "虾尔": {"id": "lobster-001", "name": "虾尔", "role": "gateway"},
            "诸葛马": {"id": "hermes-001", "name": "诸葛马", "role": "coach"},
        }

        for name, info in participant_map.items():
            if name in text:
                participants.append(info)

        return participants

    def _extract_task_components(self, text: str) -> list:
        """提取任务类型组件"""
        components = []

        # 围棋相关任务
        if any(kw in text for kw in ["死活", "做题"]):
            components.append({
                "type": "go_training_task",
                "description": "死活题训练",
                "is_atomic": True
            })
        if any(kw in text for kw in ["手筋"]):
            components.append({
                "type": "go_training_task",
                "description": "手筋题训练",
                "is_atomic": True
            })
        if any(kw in text for kw in ["定式", "布局"]):
            components.append({
                "type": "go_training_task",
                "description": "定式/布局学习",
                "is_atomic": True
            })
        if any(kw in text for kw in ["对局", "下棋", "比赛"]):
            components.append({
                "type": "go_match",
                "description": "围棋对局",
                "is_atomic": False
            })

        # 评审相关
        if any(kw in text for kw in ["评审", "审核", "评价"]):
            components.append({
                "type": "review_request",
                "description": "评审任务",
                "is_atomic": False
            })

        # 内容生成
        if any(kw in text for kw in ["撰写", "生成", "写", "论文", "报告"]):
            components.append({
                "type": "content_generation",
                "description": "内容生成任务",
                "is_atomic": False
            })

        # 默认组件
        if not components:
            # 尝试匹配预定义的任务类型
            for task_type, keywords in TASK_TYPE_KEYWORDS.items():
                if any(kw in text for kw in keywords):
                    components.append({
                        "type": task_type,
                        "description": text[:50],
                        "is_atomic": True
                    })
                    break

            if not components:
                components.append({
                    "type": "general_task",
                    "description": text[:50],
                    "is_atomic": True
                })

        return components

    def _recursive_decompose(self, component: dict, constraints: Constraint,
                             parent_id: str = None, depth: int = 0) -> list:
        """递归分解单个组件"""
        if depth >= self.max_depth:
            logger.warning(f"达到最大递归深度 {self.max_depth}")
            return []

        mb_id = f"mb-{uuid.uuid4().hex[:8]}"
        task_type = component['task_type']

        # 创建元业务
        mb = MetaBusiness(
            id=mb_id,
            title=component['title'],
            description=component['description'],
            task_type=task_type,
            constraints=constraints,
            dependency_ids=constraints.dependencies if parent_id else [],
            estimated_cost=self._estimate_cost(task_type),
            estimated_time=self._estimate_time(task_type)
        )

        if parent_id:
            mb.dependency_ids.append(parent_id)

        # 如果不是原子任务，继续递归分解
        if not component.get('is_atomic', True):
            sub_components = self._extract_sub_components(component)
            sub_mbs = []
            for sub in sub_components:
                subs = self._recursive_decompose(sub, constraints, mb_id, depth + 1)
                sub_mbs.extend(subs)
            # 子元业务替代父元业务
            return sub_mbs if sub_mbs else [mb]

        return [mb]

    def _extract_sub_components(self, component: dict) -> list:
        """提取子任务组件"""
        task_type = component['task_type']

        if task_type == "go_match":
            return [
                {"title": "创建对局", "description": "初始化围棋对局",
                 "task_type": "go_match_setup", "is_atomic": True},
                {"title": "对局进行中", "description": "双方交替落子",
                 "task_type": "go_match_play", "is_atomic": True},
                {"title": "对局结束", "description": "计算胜负并记录",
                 "task_type": "go_match_end", "is_atomic": True},
            ]
        elif task_type == "review_request":
            return [
                {"title": "评审标准对齐", "description": "确认评审维度",
                 "task_type": "review_setup", "is_atomic": True},
                {"title": "逐项评审", "description": "按标准逐项评价",
                 "task_type": "review_execute", "is_atomic": True},
                {"title": "评审汇总", "description": "生成评审报告",
                 "task_type": "review_summary", "is_atomic": True},
            ]
        else:
            return [component]

    def _build_dag(self, meta_businesses: list) -> dict:
        """构建任务依赖DAG"""
        dag = {"nodes": [], "edges": []}

        for mb in meta_businesses:
            dag["nodes"].append({
                "id": mb.id,
                "title": mb.title,
                "task_type": mb.task_type,
                "estimated_cost": mb.estimated_cost,
                "estimated_time": mb.estimated_time
            })
            for dep_id in mb.dependency_ids:
                dag["edges"].append({"from": dep_id, "to": mb.id})

        return dag

    def _estimate_cost(self, task_type: str) -> float:
        """预估任务成本（token数）"""
        cost_map = {
            "go_training_task": 3.0,
            "go_match": 8.0,
            "go_match_setup": 2.0,
            "go_match_play": 5.0,
            "go_match_end": 2.0,
            "go_review": 5.0,
            "review_request": 10.0,
            "review_setup": 2.0,
            "review_execute": 6.0,
            "review_summary": 3.0,
            "content_generation": 15.0,
            "document_analysis": 8.0,
            "strategic_planning": 12.0,
            "teaching_analysis": 8.0,
            "schedule_management": 2.0,
        }
        return cost_map.get(task_type, 5.0)

    def _estimate_time(self, task_type: str) -> float:
        """预估任务时间（分钟）"""
        time_map = {
            "go_training_task": 15.0,
            "go_match": 30.0,
            "go_match_setup": 2.0,
            "go_match_play": 25.0,
            "go_match_end": 3.0,
            "go_review": 20.0,
            "review_request": 30.0,
            "review_setup": 5.0,
            "review_execute": 20.0,
            "review_summary": 10.0,
            "content_generation": 45.0,
            "document_analysis": 20.0,
            "strategic_planning": 30.0,
            "teaching_analysis": 25.0,
            "schedule_management": 5.0,
        }
        return time_map.get(task_type, 15.0)

    def _calculate_critical_path(self, meta_businesses: list, dag: dict) -> float:
        """计算关键路径（最长执行时间）"""
        if not meta_businesses:
            return 0.0

        # 简化计算：找到最长路径
        time_map = {mb.id: mb.estimated_time for mb in meta_businesses}

        # 找到没有依赖的节点（起点）
        all_ids = {mb.id for mb in meta_businesses}
        dep_targets = {e["to"] for e in dag.get("edges", [])}
        start_nodes = all_ids - dep_targets

        # BFS计算最长路径
        max_time = 0.0
        for start in start_nodes:
            path_time = self._dfs_longest_path(start, dag, time_map, set())
            max_time = max(max_time, path_time)

        return max_time

    def _dfs_longest_path(self, node_id: str, dag: dict, time_map: dict,
                          visited: set) -> float:
        if node_id in visited:
            return 0.0
        visited.add(node_id)

        node_time = time_map.get(node_id, 0)
        # 找到所有后继节点
        successors = [e["to"] for e in dag.get("edges", []) if e["from"] == node_id]

        if not successors:
            return node_time

        max_successor_time = 0
        for succ in successors:
            t = self._dfs_longest_path(succ, dag, time_map, visited)
            max_successor_time = max(max_successor_time, t)

        return node_time + max_successor_time

# ============ 能力匹配器 ============

class CapabilityMatcher:
    """执行者能力匹配器"""

    def __init__(self, capability_db: dict = None, service_registry: dict = None):
        self.capability_db = capability_db or {}
        self.service_registry = service_registry or {}

    def match_executors(self, meta_business: MetaBusiness) -> list:
        """
        为元业务匹配最优执行者

        Returns:
            按综合评分排序的候选执行者列表
        """
        candidates = []

        for service_id, profile in self.capability_db.items():
            if not profile.get("online", True):
                continue

            # 检查负载
            if profile.get("load", 0) >= 1.0:
                continue

            # 计算能力匹配度
            match_score = self._calculate_match_score(
                meta_business.task_type, profile
            )

            if match_score < 0.3:  # 低于阈值不候选
                continue

            # 计算综合评分
            cost_score = 1.0 / (1.0 + profile.get("cost", 5))
            speed_score = profile.get("speed", 0.7)
            quality_score = profile.get("quality", 0.8)

            # 权重：质量40% + 速度30% + 成本20% + 匹配度10%
            composite_score = (
                quality_score * 0.4 +
                speed_score * 0.3 +
                cost_score * 0.2 +
                match_score * 0.1
            )

            candidate = ExecutorCandidate(
                service_id=service_id,
                name=profile.get("name", service_id),
                role=profile.get("role", "worker"),
                cost=profile.get("cost", 5),
                speed=speed_score,
                quality=quality_score,
                capability_match=match_score,
                online=True,
                load=profile.get("load", 0),
                max_concurrent=profile.get("max_concurrent", 3),
                score=round(composite_score, 3)
            )
            candidates.append(candidate)

        # 按综合评分排序
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def _calculate_match_score(self, task_type: str, profile: dict) -> float:
        """计算能力匹配度"""
        capabilities = profile.get("capabilities", [])
        preferred = profile.get("preferred_task_types", [])

        score = 0.0

        # 直接能力匹配（精确）
        if task_type in capabilities:
            score += 0.5

        # 模糊匹配（关键词包含）
        best_fuzzy = 0.0
        for cap in capabilities:
            if task_type == cap:
                best_fuzzy = max(best_fuzzy, 0.5)
            elif task_type in cap:
                best_fuzzy = max(best_fuzzy, 0.4)
            elif cap in task_type:
                best_fuzzy = max(best_fuzzy, 0.4)
            else:
                # 部分词匹配
                cap_parts = set(cap.replace("_", " ").split())
                task_parts = set(task_type.replace("_", " ").split())
                overlap = cap_parts & task_parts
                if overlap:
                    best_fuzzy = max(best_fuzzy, 0.3 * len(overlap) / max(len(cap_parts), len(task_parts)))
        score += best_fuzzy

        # 偏好匹配
        for pref in preferred:
            if pref in task_type or task_type in pref:
                score += 0.2
                break

        # 角色匹配
        role = profile.get("role", "")
        if task_type.startswith("go_") and role in ["worker", "coach", "student"]:
            score += 0.1

        return min(score, 1.0)

    def constraint_prune(self, candidates: list, constraints: Constraint) -> list:
        """约束剪枝"""
        pruned = list(candidates)

        # 预算剪枝
        if constraints.budget_max < 999999:
            pruned = [c for c in pruned if c.cost <= constraints.budget_max]

        # 质量剪枝
        if constraints.quality_min > 0:
            pruned = [c for c in pruned if c.quality >= constraints.quality_min]

        # 安全剪枝（简化：高安全级别排除低成本执行者）
        if constraints.safety_level in ["high", "critical"]:
            pruned = [c for c in pruned if c.cost >= 3]  # 低成本=低安全

        return pruned

    def select_optimal(self, candidates: list) -> Optional[ExecutorCandidate]:
        """选择最优执行者"""
        if not candidates:
            return None
        return candidates[0]

    def select_collaboration_mode(self, meta_business: MetaBusiness,
                                  executor: ExecutorCandidate) -> str:
        """选择协作模式"""
        # 优先使用预定义规则
        default_mode = COLLABORATION_RULES.get(meta_business.task_type, "A")

        # 如果需要人工审核，强制模式B
        if meta_business.constraints.review_required:
            return "B"

        # 如果质量要求极高，模式C（人工主导）
        if meta_business.constraints.quality_min >= 0.9:
            return "C"

        # 如果任务复杂（预估时间>30分钟），模式D
        if meta_business.estimated_time > 30:
            return "D"

        return default_mode

# ============ 主接口 ============

class RecursiveTaskEngine:
    """递归任务引擎（对外统一接口）"""

    def __init__(self, capability_db: dict = None, service_registry: dict = None):
        self.decomposer = DecompositionEngine(capability_db, service_registry)
        self.matcher = CapabilityMatcher(capability_db, service_registry)

    def process_task(self, task_description: str, constraints: dict = None) -> dict:
        """
        完整处理流程：分解 → 匹配 → 生成执行计划

        Returns:
            完整的执行计划（JSON可序列化）
        """
        # 步骤1：递归分解
        plan = self.decomposer.decompose_task(task_description, constraints)

        # 步骤2：为每个元业务匹配执行者
        for mb in plan.meta_businesses:
            candidates = self.matcher.match_executors(mb)
            pruned = self.matcher.constraint_prune(candidates, mb.constraints)
            best = self.matcher.select_optimal(pruned)

            mb.executor_candidates = [
                {
                    "service_id": c.service_id,
                    "name": c.name,
                    "score": c.score,
                    "cost": c.cost,
                    "speed": c.speed,
                    "quality": c.quality
                }
                for c in candidates[:3]  # 只保留前3个候选
            ]

            if best:
                mb.selected_executor = best.service_id
                mb.collaboration_mode = self.matcher.select_collaboration_mode(mb, best)

        # 步骤3：生成可序列化的执行计划
        result = {
            "task_id": plan.task_id,
            "original_task": plan.original_task,
            "constraints": plan.constraints,
            "meta_businesses": [self._serialize_mb(mb) for mb in plan.meta_businesses],
            "dag": plan.dag,
            "estimated_total_cost": plan.estimated_total_cost,
            "estimated_total_time": plan.estimated_total_time,
            "status": plan.status,
            "created_at": plan.created_at,
            "summary": self._generate_summary(plan)
        }

        return result

    def _serialize_mb(self, mb: MetaBusiness) -> dict:
        return {
            "id": mb.id,
            "title": mb.title,
            "description": mb.description,
            "task_type": mb.task_type,
            "executor_candidates": mb.executor_candidates,
            "selected_executor": mb.selected_executor,
            "collaboration_mode": mb.collaboration_mode,
            "dependency_ids": mb.dependency_ids,
            "estimated_cost": mb.estimated_cost,
            "estimated_time": mb.estimated_time,
            "status": mb.status
        }

    def _generate_summary(self, plan: DecompositionPlan) -> str:
        """生成执行计划摘要"""
        lines = [
            f"📋 任务ID: {plan.task_id}",
            f" 原始任务: {plan.original_task[:50]}...",
            f"📊 元业务数量: {len(plan.meta_businesses)}",
            f"💰 预估总成本: {plan.estimated_total_cost} tokens",
            f"⏱️ 预估总时间: {plan.estimated_total_time} 分钟",
            "",
            "执行序列:"
        ]

        # 按依赖关系排序
        sorted_mbs = self._topological_sort(plan.meta_businesses, plan.dag)
        for i, mb in enumerate(sorted_mbs, 1):
            mode_icon = {"A": "🤖", "B": "🤖👤", "C": "👤🤖", "D": "👥🤖"}
            icon = mode_icon.get(mb.collaboration_mode, "❓")
            lines.append(
                f"  {i}. [{icon} 模式{mb.collaboration_mode}] "
                f"{mb.title} → {mb.selected_executor or '未分配'}"
            )

        return "\n".join(lines)

    def _topological_sort(self, meta_businesses: list, dag: dict) -> list:
        """拓扑排序"""
        in_degree = {mb.id: 0 for mb in meta_businesses}
        for edge in dag.get("edges", []):
            if edge["to"] in in_degree:
                in_degree[edge["to"]] += 1

        queue = [mb.id for mb in meta_businesses if in_degree[mb.id] == 0]
        result = []
        mb_map = {mb.id: mb for mb in meta_businesses}

        while queue:
            node_id = queue.pop(0)
            result.append(mb_map[node_id])
            for edge in dag.get("edges", []):
                if edge["from"] == node_id and edge["to"] in in_degree:
                    in_degree[edge["to"]] -= 1
                    if in_degree[edge["to"]] == 0:
                        queue.append(edge["to"])

        # 添加未排序的节点（无依赖的）
        for mb in meta_businesses:
            if mb not in result:
                result.append(mb)

        return result

# ============ 测试 ============

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # 模拟能力数据库
    capability_db = {
        "lobster-001": {
            "name": "虾尔", "role": "gateway",
            "capabilities": ["dingtalk_gateway", "wechat_gateway", "task_dispatch", "routing"],
            "cost": 2, "speed": 0.95, "quality": 0.80,
            "preferred_task_types": ["task_dispatch", "routing"],
            "online": True, "load": 0.2, "max_concurrent": 10
        },
        "lobster-002": {
            "name": "诸葛虾", "role": "worker",
            "capabilities": ["go_training", "go_match", "review", "content_generation"],
            "cost": 3, "speed": 0.9, "quality": 0.85,
            "preferred_task_types": ["go_training", "go_match", "content_generation"],
            "online": True, "load": 0.3, "max_concurrent": 5
        },
        "hermes-001": {
            "name": "诸葛马", "role": "coach",
            "capabilities": ["go_coaching", "go_training", "thesis_review", "teaching_analysis",
                           "strategic_planning", "match_referee"],
            "cost": 5, "speed": 0.7, "quality": 0.95,
            "preferred_task_types": ["go_coaching", "thesis_review", "strategic_planning"],
            "online": True, "load": 0.4, "max_concurrent": 3
        },
        "xiaochen": {
            "name": "小陈", "role": "student",
            "capabilities": ["go_training", "go_match"],
            "cost": 1, "speed": 0.6, "quality": 0.70,
            "preferred_task_types": ["go_training"],
            "online": True, "load": 0.1, "max_concurrent": 2
        },
    }

    service_registry = {
        "lobster-001": {"name": "虾尔", "role": "gateway"},
        "lobster-002": {"name": "诸葛虾", "role": "worker"},
        "hermes-001": {"name": "诸葛马", "role": "coach"},
        "xiaochen": {"name": "小陈", "role": "student"},
    }

    engine = RecursiveTaskEngine(capability_db, service_registry)

    # 测试1：围棋学习计划
    print("=" * 60)
    print(" 测试1：围棋学习计划分解")
    print("=" * 60)

    task1 = "安排本周围棋学习计划，诸葛虾和小陈都要参加，包括死活题训练、定式学习和一场对局，预算控制在50元以内，下周三前完成。"
    constraints1 = {
        "time": {"deadline": "2026-06-18", "urgency": "normal"},
        "budget": {"max_cost": 50, "currency": "tokens"},
        "participants": ["xiaochen", "zhuguxia"]
    }

    result1 = engine.process_task(task1, constraints1)
    print(result1["summary"])
    print()

    # 测试2：AI黑客松评审
    print("=" * 60)
    print(" 测试2：AI黑客松评审分解")
    print("=" * 60)

    task2 = "帮我评审AI黑客松作品展页面，从文字表述、技术规范、内容完整性、学术规范性四个维度评价，最后给我一个汇总报告。"
    constraints2 = {
        "quality": {"min_accuracy": 0.85, "review_required": True}
    }

    result2 = engine.process_task(task2, constraints2)
    print(result2["summary"])
