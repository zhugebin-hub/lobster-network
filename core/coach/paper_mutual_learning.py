#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文写作互相学习系统 (Paper Mutual Learning)
=============================================

在六学员之间建立持续知识传递机制，使智能体在论文协作写作中
互相学习、共同提升。核心机制包括：

1. **能力互补匹配**：根据八维能力短板，自动配对互学搭档
2. **知识提取-蒸馏-迁移**：从优秀产出中提取可复用方法论
3. **交叉审稿互评**：学员间轮转审稿，学习他人写作风格
4. **能力跃迁追踪**：记录每位学员通过学习获得的能力增量
5. **知识库共享**：建立共享方法论库（Shared Methodology Pool）

参考：小龙虾网络 V5.0 论文结论驱动的系统全面升级
"""

import json
import os
import time
import math
import copy
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger("paper_mutual_learning")
logger.setLevel(logging.INFO)

# ============================================================
# 常量与路径
# ============================================================

SHARED_ROOT = "/shared"
PAPER_TRAINING_DIR = os.path.join(SHARED_ROOT, "training", "paper")
SHARED_METHODOLOGY_POOL = os.path.join(PAPER_TRAINING_DIR, "shared_methodology_pool.json")
MUTUAL_LEARNING_LOG = os.path.join(PAPER_TRAINING_DIR, "mutual_learning_log.json")
CROSS_REVIEW_DIR = os.path.join(PAPER_TRAINING_DIR, "cross_reviews")
LEARNING_TRANSFER_RECORDS = os.path.join(PAPER_TRAINING_DIR, "learning_transfer_records.json")

# 确保目录存在
os.makedirs(CROSS_REVIEW_DIR, exist_ok=True)

# ============================================================
# 八维能力维度
# ============================================================

ABILITY_DIMENSIONS = [
    "abstract",        # 摘要撰写
    "literature_review",  # 文献综述
    "methodology",     # 研究方法
    "data_analysis",   # 数据分析
    "argumentation",   # 论证推理
    "structure",       # 结构组织
    "formatting",      # 格式规范
    "citations",       # 引用规范
]

# 能力维度中文名
DIMENSION_CN = {
    "abstract": "摘要撰写",
    "literature_review": "文献综述",
    "methodology": "研究方法",
    "data_analysis": "数据分析",
    "argumentation": "论证推理",
    "structure": "结构组织",
    "formatting": "格式规范",
    "citations": "引用规范",
}

# ============================================================
# 学员数据模型
# ============================================================

class Learner:
    """论文写作学员"""

    def __init__(self, player_id: str, profile: Dict[str, Any]):
        self.player_id = player_id
        self.role = profile.get("role", "unknown")
        self.description = profile.get("description", "")
        self.strengths: List[str] = profile.get("strengths", [])
        self.weaknesses: List[str] = profile.get("weaknesses", [])

        # 当前能力评分（从 profile 加载）
        self.scores: Dict[str, float] = profile.get("scores", {})
        for dim in ABILITY_DIMENSIONS:
            if dim not in self.scores:
                self.scores[dim] = 50.0

        # 学习记录
        self.learning_history: List[Dict] = []
        self.total_learning_gain: float = 0.0
        self.paired_count: int = 0
        self.cross_review_count: int = 0
        self.knowledge_shared: int = 0

    @property
    def overall_score(self) -> float:
        return sum(self.scores.values()) / len(ABILITY_DIMENSIONS)

    @property
    def weakest_dimensions(self) -> List[str]:
        """返回最弱的两项能力（用于配对学习）"""
        sorted_dims = sorted(self.scores.items(), key=lambda x: x[1])
        return [d[0] for d in sorted_dims[:2]]

    @property
    def strongest_dimensions(self) -> List[str]:
        """返回最强的两项能力（用于教学输出）"""
        sorted_dims = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        return [d[0] for d in sorted_dims[:2]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_id": self.player_id,
            "role": self.role,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "scores": self.scores,
            "overall_score": round(self.overall_score, 1),
            "total_learning_gain": round(self.total_learning_gain, 1),
            "paired_count": self.paired_count,
            "cross_review_count": self.cross_review_count,
            "knowledge_shared": self.knowledge_shared,
        }


# ============================================================
# 共享方法论池
# ============================================================

class MethodologyEntry:
    """方法论条目"""

    def __init__(
        self,
        entry_id: str,
        title: str,
        description: str,
        dimension: str,
        source_player: str,
        quality_score: float,
        tags: List[str] = None,
        created_at: str = None,
    ):
        self.entry_id = entry_id
        self.title = title
        self.description = description
        self.dimension = dimension
        self.source_player = source_player
        self.quality_score = quality_score
        self.tags = tags or []
        self.created_at = created_at or datetime.now().isoformat()
        self.usage_count = 0
        self.rated_by: Dict[str, float] = {}  # player_id -> rating
        self.last_accessed = None

    @property
    def avg_rating(self) -> float:
        if not self.rated_by:
            return quality_score
        return sum(self.rated_by.values()) / len(self.rated_by)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "description": self.description,
            "dimension": self.dimension,
            "source_player": self.source_player,
            "quality_score": self.quality_score,
            "tags": self.tags,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "avg_rating": round(self.avg_rating, 1),
            "rated_by_count": len(self.rated_by),
        }


class SharedMethodologyPool:
    """共享方法论池 — 所有学员共同维护和访问"""

    def __init__(self):
        self._entries: Dict[str, MethodologyEntry] = {}
        self._dimension_index: Dict[str, List[str]] = defaultdict(list)
        self._load()

    def _load(self):
        if os.path.exists(SHARED_METHODOLOGY_POOL):
            try:
                with open(SHARED_METHODOLOGY_POOL, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for entry_data in data.get("entries", []):
                    entry = MethodologyEntry(**entry_data)
                    self._entries[entry.entry_id] = entry
                    self._dimension_index[entry.dimension].append(entry.entry_id)
                logger.info(f"[MethodologyPool] 加载 {len(self._entries)} 条方法论")
            except Exception as e:
                logger.error(f"[MethodologyPool] 加载失败: {e}")

    def _save(self):
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "total_entries": len(self._entries),
            "entries": [e.to_dict() for e in self._entries.values()],
        }
        with open(SHARED_METHODOLOGY_POOL, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_entry(
        self,
        title: str,
        description: str,
        dimension: str,
        source_player: str,
        quality_score: float = 0.7,
        tags: List[str] = None,
    ) -> str:
        """添加新方法论条目，返回 entry_id"""
        entry_id = hashlib.md5(
            f"{source_player}:{title}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        entry = MethodologyEntry(
            entry_id=entry_id,
            title=title,
            description=description,
            dimension=dimension,
            source_player=source_player,
            quality_score=quality_score,
            tags=tags or [],
        )

        self._entries[entry_id] = entry
        self._dimension_index[dimension].append(entry_id)
        self._save()

        logger.info(f"[MethodologyPool] 新增: [{dimension}] {title} by {source_player}")
        return entry_id

    def query_by_dimension(self, dimension: str, top_k: int = 5) -> List[MethodologyEntry]:
        """按维度查询 top-k 高质量方法论"""
        ids = self._dimension_index.get(dimension, [])
        entries = [self._entries[eid] for eid in ids if eid in self._entries]

        # 按质量评分排序
        entries.sort(key=lambda e: e.quality_score * math.log(e.usage_count + 2), reverse=True)
        return entries[:top_k]

    def get_for_learner(self, player_id: str, top_k: int = 3) -> Dict[str, List[MethodologyEntry]]:
        """为指定学员获取其短板领域的高质量方法论"""
        result = {}
        # 这里需要外部传入 learners，所以此方法需要 learners 参数
        return result

    def rate_entry(self, entry_id: str, player_id: str, rating: float):
        """学员对方法论评分"""
        if entry_id in self._entries:
            self._entries[entry_id].rated_by[player_id] = max(0, min(5, rating))
            self._entries[entry_id].usage_count += 1
            self._entries[entry_id].last_accessed = datetime.now().isoformat()
            self._save()

    def stats(self) -> Dict[str, Any]:
        """方法论池统计"""
        dim_counts = {dim: len(ids) for dim, ids in self._dimension_index.items()}
        return {
            "total_entries": len(self._entries),
            "by_dimension": dim_counts,
            "total_usage": sum(e.usage_count for e in self._entries.values()),
            "avg_quality": round(
                sum(e.quality_score for e in self._entries.values()) / max(len(self._entries), 1), 2
            ),
        }


# ============================================================
# 互相学习引擎
# ============================================================

class MutualLearningEngine:
    """
    互相学习引擎 — 核心算法

    机制一：能力互补配对
    - 基于八维能力评分的余弦互补度计算最佳配对
    - 每周轮换搭档，确保知识充分传播

    机制二：知识蒸馏与迁移
    - 从高分论文中提取结构化方法论
    - 将方法论注入弱项学员的训练计划

    机制三：交叉审稿互评
    - 三位学员组成审稿圈，轮转审稿
    - 互评结果计入能力增量

    机制四：能力跃迁追踪
    - 记录每位学员的基线分数和当前分数
    - 计算学习增益，生成学习曲线
    """

    def __init__(self, learners: Dict[str, Learner], methodology_pool: SharedMethodologyPool = None):
        self.learners = learners
        self.pool = methodology_pool or SharedMethodologyPool()
        self.learning_log: List[Dict] = []
        self._load_log()

    def _load_log(self):
        if os.path.exists(MUTUAL_LEARNING_LOG):
            try:
                with open(MUTUAL_LEARNING_LOG, "r", encoding="utf-8") as f:
                    self.learning_log = json.load(f)
            except Exception:
                pass

    def _save_log(self):
        with open(MUTUAL_LEARNING_LOG, "w", encoding="utf-8") as f:
            json.dump(self.learning_log, f, ensure_ascii=False, indent=2)

    # ── 机制一：能力互补配对 ──────────────────────────

    def compute_complementarity(self, player_a: str, player_b: str) -> float:
        """
        计算两个学员的能力互补度。

        互补度 = 1 - cosine_similarity(scores_a, scores_b) × w
        其中 cosine_similarity 越高 = 能力越相似，互补度越低
        w: 维度权重（强弱项差异加权）
        """
        scores_a = self.learners[player_a].scores
        scores_b = self.learners[player_b].scores

        # 余弦相似度
        dot = sum(scores_a[d] * scores_b[d] for d in ABILITY_DIMENSIONS)
        norm_a = math.sqrt(sum(scores_a[d] ** 2 for d in ABILITY_DIMENSIONS))
        norm_b = math.sqrt(sum(scores_b[d] ** 2 for d in ABILITY_DIMENSIONS))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        cosine = dot / (norm_a * norm_b)

        # 加权：检查弱点互补程度
        weak_a = set(self.learners[player_a].weakest_dimensions)
        strong_b = set(self.learners[player_b].strongest_dimensions)
        weak_b = set(self.learners[player_b].weakest_dimensions)
        strong_a = set(self.learners[player_a].strongest_dimensions)

        # 互补匹配分数
        match_score = len(weak_a & strong_b) + len(weak_b & strong_a)
        weight = 1.0 + 0.3 * match_score

        # 互补度 = (1 - 相似度) × 权重
        complementarity = (1.0 - cosine) * weight

        return round(complementarity, 4)

    def generate_pairings(self) -> List[Tuple[str, str, float]]:
        """
        生成最优互学配对方案。

        使用贪心算法：每次选择互补度最高的未配对学员配对。
        """
        player_ids = list(self.learners.keys())
        if len(player_ids) < 2:
            return []

        # 计算所有配对的互补度
        all_pairs = []
        for i in range(len(player_ids)):
            for j in range(i + 1, len(player_ids)):
                comp = self.compute_complementarity(player_ids[i], player_ids[j])
                all_pairs.append((player_ids[i], player_ids[j], comp))

        # 按互补度降序
        all_pairs.sort(key=lambda x: x[2], reverse=True)

        # 贪心配对
        paired = set()
        result = []
        for a, b, comp in all_pairs:
            if a not in paired and b not in paired:
                result.append((a, b, comp))
                paired.add(a)
                paired.add(b)

        # 如果有单数学员，匹配互补度最高的已配学员作为辅助导师
        unpaired = [p for p in player_ids if p not in paired]
        for up in unpaired:
            best_match = None
            best_comp = -1
            for p in paired:
                comp = self.compute_complementarity(up, p)
                if comp > best_comp:
                    best_comp = comp
                    best_match = p
            if best_match:
                result.append((up, best_match, best_comp))

        return result

    # ── 机制二：知识蒸馏与迁移 ──────────────────────────

    def extract_methodology(
        self, source_player: str, min_quality: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        从指定学员的优秀产出中提取方法论。

        扫描该学员的 profile.json 中的 best_practices 和 recent_achievements，
        提取为结构化方法论条目，加入共享池。
        """
        profile_path = os.path.join(PAPER_TRAINING_DIR, source_player, "profile.json")
        if not os.path.exists(profile_path):
            return []

        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
        except Exception:
            return []

        extracted = []
        best_practices = profile.get("best_practices", [])
        achievements = profile.get("recent_achievements", [])

        for bp in best_practices:
            if bp.get("quality", 0) >= min_quality:
                for dim in bp.get("dimensions", []):
                    if dim in ABILITY_DIMENSIONS:
                        entry_id = self.pool.add_entry(
                            title=bp.get("title", "未命名方法论"),
                            description=bp.get("description", ""),
                            dimension=dim,
                            source_player=source_player,
                            quality_score=bp.get("quality", 0.7),
                            tags=bp.get("tags", []),
                        )
                        extracted.append({
                            "entry_id": entry_id,
                            "title": bp.get("title"),
                            "dimension": dim,
                            "source": source_player,
                        })

        self.learners[source_player].knowledge_shared += len(extracted)

        # 记录学习事件
        if extracted:
            self.learning_log.append({
                "type": "knowledge_extraction",
                "timestamp": datetime.now().isoformat(),
                "source_player": source_player,
                "entries_count": len(extracted),
                "entries": extracted,
            })
            self._save_log()

        return extracted

    def inject_methodology(
        self, target_player: str, dimension: str = None, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        为目标学员注入共享池中的方法论。

        优先选择目标学员弱项维度的方法论。
        """
        if dimension is None:
            # 选择目标学员最弱的维度
            dimensions = self.learners[target_player].weakest_dimensions
        else:
            dimensions = [dimension]

        entries = []
        for dim in dimensions[:2]:
            dim_entries = self.pool.query_by_dimension(dim, top_k)
            entries.extend(dim_entries)

        if not entries:
            return []

        # 去重并按质量排序
        seen = set()
        unique_entries = []
        for e in sorted(entries, key=lambda x: x.quality_score, reverse=True):
            if e.entry_id not in seen:
                unique_entries.append(e)
                seen.add(e.entry_id)
                if len(unique_entries) >= top_k:
                    break

        # 记录注入事件
        injected = []
        for e in unique_entries:
            e.usage_count += 1
            injected.append({
                "entry_id": e.entry_id,
                "title": e.title,
                "dimension": e.dimension,
                "quality_score": e.quality_score,
            })

        if injected:
            self.learning_log.append({
                "type": "methodology_injection",
                "timestamp": datetime.now().isoformat(),
                "target_player": target_player,
                "entries": injected,
            })
            self._save_log()

        return injected

    def transfer_knowledge(
        self, source_player: str, target_player: str
    ) -> Dict[str, Any]:
        """
        执行一次完整的知识迁移：从源学员提取方法论 → 注入目标学员。

        返回迁移报告。
        """
        # 先提取
        extracted = self.extract_methodology(source_player)

        # 再注入 — 针对目标学员的最弱维度
        injected = self.inject_methodology(target_player)

        # 模拟能力增益（基于方法论质量）
        gain_per_dim: Dict[str, float] = defaultdict(float)
        for inj in injected:
            gain = inj["quality_score"] * 2.0  # 每次注入可提升最多2分
            gain_per_dim[inj["dimension"]] += gain

        for dim, gain in gain_per_dim.items():
            old_score = self.learners[target_player].scores.get(dim, 50)
            self.learners[target_player].scores[dim] = min(100, old_score + gain * 0.3)

        total_gain = sum(gain_per_dim.values()) * 0.3
        self.learners[target_player].total_learning_gain += total_gain

        report = {
            "source": source_player,
            "target": target_player,
            "extracted_count": len(extracted),
            "injected_count": len(injected),
            "total_gain": round(total_gain, 1),
            "gains_by_dimension": {d: round(g, 1) for d, g in gain_per_dim.items()},
            "timestamp": datetime.now().isoformat(),
        }

        self.learning_log.append({"type": "knowledge_transfer", **report})
        self._save_log()

        return report

    # ── 机制三：交叉审稿互评 ──────────────────────────

    def generate_review_assignments(self) -> List[Dict[str, str]]:
        """
        生成交叉审稿分配方案。

        六学员分为两个审稿圈，每圈三人轮转审稿。
        A审B, B审C, C审D, D审E, E审F, F审A
        """
        player_ids = list(self.learners.keys())
        if len(player_ids) < 2:
            return []

        assignments = []
        for i in range(len(player_ids)):
            reviewer = player_ids[i]
            reviewee = player_ids[(i + 1) % len(player_ids)]
            assignments.append({
                "reviewer": reviewer,
                "reviewee": reviewee,
                "assigned_at": datetime.now().isoformat(),
                "status": "pending",
            })

        # 保存到文件
        review_batch = {
            "batch_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "created_at": datetime.now().isoformat(),
            "assignments": assignments,
        }
        review_path = os.path.join(
            CROSS_REVIEW_DIR, f"batch_{review_batch['batch_id']}.json"
        )
        with open(review_path, "w", encoding="utf-8") as f:
            json.dump(review_batch, f, ensure_ascii=False, indent=2)

        return assignments

    def submit_review(
        self, reviewer: str, reviewee: str, scores: Dict[str, float], comments: str = ""
    ) -> Dict[str, Any]:
        """
        提交审稿意见。

        scores: 八维度评分字典 {dimension: score}
        审稿人对被审稿人论文的评分会触发双方学习增益：
        - 被审稿人根据反馈调整得分
        - 审稿人通过审稿练习提升自己弱项
        """
        result = {
            "reviewer": reviewer,
            "reviewee": reviewee,
            "timestamp": datetime.now().isoformat(),
            "scores": scores,
            "comments": comments,
        }

        # 被审稿人能力增益（基于审稿人评分）
        if reviewee in self.learners:
            for dim, score in scores.items():
                if dim in ABILITY_DIMENSIONS:
                    current = self.learners[reviewee].scores.get(dim, 50)
                    gap = score - current
                    if gap > 0:
                        # 正反馈：小幅提升
                        self.learners[reviewee].scores[dim] = min(100, current + gap * 0.15)
                    elif gap < 0:
                        # 负反馈：如果审稿人该维度很强，则小量修正
                        reviewer_score = self.learners[reviewer].scores.get(dim, 50)
                        if reviewer_score > current + 10:
                            self.learners[reviewee].scores[dim] = max(0, current + gap * 0.05)

        # 审稿人能力增益（审稿本身是学习过程）
        if reviewer in self.learners:
            for dim in self.learners[reviewer].weakest_dimensions[:2]:
                # 审稿让审稿人在弱项上获得微量提升
                self.learners[reviewer].scores[dim] = min(
                    100, self.learners[reviewer].scores[dim] + 0.3
                )

        self.learners[reviewer].cross_review_count += 1
        self.learners[reviewee].paired_count += 1

        self.learning_log.append({"type": "cross_review", **result})
        self._save_log()

        return result

    # ── 机制四：能力跃迁追踪 ──────────────────────────

    def track_learning_progress(self) -> Dict[str, Any]:
        """生成全体学员学习进展报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "learners": {},
            "methodology_pool": self.pool.stats(),
            "recent_transfers": [
                log for log in self.learning_log[-20:]
                if log.get("type") == "knowledge_transfer"
            ],
            "review_stats": self._review_stats(),
        }

        for pid, learner in self.learners.items():
            report["learners"][pid] = {
                "overall_score": round(learner.overall_score, 1),
                "total_gain": round(learner.total_learning_gain, 1),
                "paired_count": learner.paired_count,
                "cross_reviews": learner.cross_review_count,
                "knowledge_shared": learner.knowledge_shared,
                "scores_by_dimension": {
                    d: round(s, 1) for d, s in learner.scores.items()
                },
                "weakest": learner.weakest_dimensions,
                "strongest": learner.strongest_dimensions,
            }

        return report

    def _review_stats(self) -> Dict[str, Any]:
        """审稿统计"""
        review_count = len([
            log for log in self.learning_log
            if log.get("type") == "cross_review"
        ])
        return {
            "total_reviews": review_count,
            "recent_30d": len([
                log for log in self.learning_log
                if log.get("type") == "cross_review"
                and (datetime.now() - datetime.fromisoformat(log["timestamp"])).days <= 30
            ]),
        }

    # ── 综合执行 ─────────────────────────────────────

    def run_weekly_cycle(self) -> Dict[str, Any]:
        """
        执行一周的完整互相学习周期：

        1. 知识提取：从所有学员提取方法论
        2. 配对生成：确定本周互学搭档
        3. 知识迁移：结对执行知识迁移
        4. 审稿分配：生成交叉审稿任务
        5. 学习报告：生成进展报告
        """
        cycle_report = {
            "cycle_id": datetime.now().strftime("WK%Y%m%d"),
            "started_at": datetime.now().isoformat(),
            "phases": {},
        }

        # Phase 1: 知识提取
        extraction_results = {}
        for pid in self.learners:
            extracted = self.extract_methodology(pid, min_quality=0.55)
            if extracted:
                extraction_results[pid] = len(extracted)
        cycle_report["phases"]["extraction"] = extraction_results

        # Phase 2: 配对生成
        pairings = self.generate_pairings()
        cycle_report["phases"]["pairings"] = [
            {"pair": [a, b], "complementarity": round(c, 4)} for a, b, c in pairings
        ]

        # Phase 3: 知识迁移
        transfer_results = []
        for a, b, _ in pairings:
            report = self.transfer_knowledge(a, b)
            transfer_results.append(report)
            report2 = self.transfer_knowledge(b, a)
            transfer_results.append(report2)
        cycle_report["phases"]["transfers"] = transfer_results

        # Phase 4: 审稿分配
        assignments = self.generate_review_assignments()
        cycle_report["phases"]["review_assignments"] = [
            {
                "reviewer": a["reviewer"],
                "reviewee": a["reviewee"],
                "status": "pending",
            }
            for a in assignments
        ]

        # Phase 5: 学习报告
        progress = self.track_learning_progress()
        cycle_report["phases"]["progress"] = progress
        cycle_report["completed_at"] = datetime.now().isoformat()

        # 保存周期报告
        report_path = os.path.join(
            PAPER_TRAINING_DIR, f"weekly_cycle_{cycle_report['cycle_id']}.json"
        )
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(cycle_report, f, ensure_ascii=False, indent=2)

        logger.info(
            f"[MutualLearning] 周循环完成: {len(pairings)}对配对, "
            f"{sum(extraction_results.values())}条方法论提取, "
            f"{len(transfer_results)}次知识迁移, {len(assignments)}次审稿分配"
        )

        return cycle_report


# ============================================================
# 命令行入口
# ============================================================

def load_learners_from_profiles() -> Dict[str, Learner]:
    """从 profile.json 文件加载所有学员"""
    learners = {}

    # 扫描训练目录
    if os.path.exists(PAPER_TRAINING_DIR):
        for item in os.listdir(PAPER_TRAINING_DIR):
            profile_path = os.path.join(PAPER_TRAINING_DIR, item, "profile.json")
            if os.path.exists(profile_path):
                try:
                    with open(profile_path, "r", encoding="utf-8") as f:
                        profile = json.load(f)
                    player_id = profile.get("player_id", item)
                    learners[player_id] = Learner(player_id, profile)
                except Exception:
                    pass

    return learners


def run_mutual_learning():
    """启动互相学习系统主循环"""
    logger.info("[MutualLearning] 初始化互相学习系统...")

    learners = load_learners_from_profiles()
    if not learners:
        # 使用默认六学员
        default_profiles = {
            "qoder": {
                "role": "analytical_specialist",
                "strengths": ["methodology", "structure"],
                "weaknesses": ["abstract", "argumentation"],
                "scores": {"abstract": 62, "literature_review": 75, "methodology": 84,
                          "data_analysis": 78, "argumentation": 68, "structure": 82,
                          "formatting": 60, "citations": 73},
            },
            "xiaochen": {
                "role": "empirical_specialist",
                "strengths": ["data_analysis", "methodology"],
                "weaknesses": ["literature_review", "formatting"],
                "scores": {"abstract": 68, "literature_review": 55, "methodology": 78,
                          "data_analysis": 85, "argumentation": 72, "structure": 65,
                          "formatting": 52, "citations": 60},
            },
            "zhuguxia": {
                "role": "survey_specialist",
                "strengths": ["literature_review", "citations"],
                "weaknesses": ["data_analysis", "methodology"],
                "scores": {"abstract": 75, "literature_review": 88, "methodology": 58,
                          "data_analysis": 55, "argumentation": 70, "structure": 68,
                          "formatting": 65, "citations": 85},
            },
            "professor_zhuge": {
                "role": "reviewer",
                "strengths": ["argumentation", "formatting"],
                "weaknesses": ["structure", "abstract"],
                "scores": {"abstract": 78, "literature_review": 95, "methodology": 88,
                          "data_analysis": 82, "argumentation": 92, "structure": 80,
                          "formatting": 90, "citations": 93},
            },
            "lobster-001": {
                "role": "protocol_architect",
                "strengths": ["methodology", "structure"],
                "weaknesses": ["formatting", "abstract"],
                "scores": {"abstract": 62, "literature_review": 70, "methodology": 84,
                          "data_analysis": 65, "argumentation": 72, "structure": 78,
                          "formatting": 60, "citations": 70},
            },
            "museum-001": {
                "role": "digital_archivist",
                "strengths": ["literature_review", "citations"],
                "weaknesses": ["data_analysis", "methodology"],
                "scores": {"abstract": 68, "literature_review": 82, "methodology": 62,
                          "data_analysis": 58, "argumentation": 70, "structure": 72,
                          "formatting": 75, "citations": 80},
            },
        }
        for pid, profile in default_profiles.items():
            learners[pid] = Learner(pid, profile)

    engine = MutualLearningEngine(learners)

    # 执行周循环
    report = engine.run_weekly_cycle()
    logger.info(f"[MutualLearning] 周循环完成: {report['cycle_id']}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="论文写作互相学习系统")
    parser.add_argument("--mode", choices=["cycle", "pair", "extract", "transfer", "review", "progress"],
                        default="cycle", help="运行模式")
    parser.add_argument("--source", type=str, help="源学员 ID")
    parser.add_argument("--target", type=str, help="目标学员 ID")

    args = parser.parse_args()

    learners = load_learners_from_profiles()
    if not learners:
        learner_profiles = {
            "qoder": {"role": "test", "strengths": [], "weaknesses": [], "scores": {d: 70 for d in ABILITY_DIMENSIONS}},
            "xiaochen": {"role": "test", "strengths": [], "weaknesses": [], "scores": {d: 65 for d in ABILITY_DIMENSIONS}},
            "zhuguxia": {"role": "test", "strengths": [], "weaknesses": [], "scores": {d: 75 for d in ABILITY_DIMENSIONS}},
        }
        learners = {pid: Learner(pid, p) for pid, p in learner_profiles.items()}

    engine = MutualLearningEngine(learners)

    if args.mode == "cycle":
        result = engine.run_weekly_cycle()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.mode == "pair":
        pairings = engine.generate_pairings()
        print("互学配对方案:")
        for a, b, comp in pairings:
            print(f"  {a} ↔ {b}  互补度: {comp:.4f}")
    elif args.mode == "extract" and args.source:
        entries = engine.extract_methodology(args.source)
        print(f"从 {args.source} 提取 {len(entries)} 条方法论")
    elif args.mode == "transfer" and args.source and args.target:
        report = engine.transfer_knowledge(args.source, args.target)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.mode == "review":
        assignments = engine.generate_review_assignments()
        for a in assignments:
            print(f"  {a['reviewer']} → 审稿 → {a['reviewee']}")
    elif args.mode == "progress":
        progress = engine.track_learning_progress()
        print(json.dumps(progress, ensure_ascii=False, indent=2))
