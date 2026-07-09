#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VirtualScreeningAgent - 虚拟筛选与分子对接智能体

功能：
- 化合物库虚拟筛选（基于简化打分函数）
- 分子对接模拟（结合亲和力估算）
- 筛选命中排序与富集分析

打分函数：
- 范德华相互作用（Lennard-Jones 简化）
- 静电相互作用（Coulomb 简化）
- 去溶剂化惩罚（GBSA 简化概念）
- 构象熵惩罚
"""

import json
import logging
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field


# ============================================================
# 日志配置
# ============================================================

logger = logging.getLogger("virtual_screening_agent")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "virtual_screening.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


# ============================================================
# 数据模型
# ============================================================

@dataclass
class DockingResult:
    """对接结果"""
    compound_id: str
    target_id: str
    binding_score: float       # 综合结合分数（kcal/mol 概念）
    vdw_score: float           # 范德华项
    electrostatic_score: float # 静电项
    desolvation_penalty: float # 去溶剂化惩罚
    entropy_penalty: float     # 构象熵惩罚
    pose_rmsd: float           # 构象 RMSD
    confidence: float          # 对接置信度


# ============================================================
# VirtualScreeningAgent 主类
# ============================================================

class VirtualScreeningAgent:
    """
    虚拟筛选与分子对接智能体

    核心能力：
    1. 对化合物库进行基于结构的虚拟筛选
    2. 分子对接模拟（简化打分函数估算结合亲和力）
    3. 命中排序与富集分析

    打分函数参考：
    - AutoDock Vina 简化评分体系
    - X-Score 概念
    """

    AGENT_NAME = "VirtualScreeningAgent"
    AGENT_VERSION = "1.0.0"

    def __init__(self):
        self._docking_results: Dict[str, List[DockingResult]] = {}
        logger.info(f"{self.AGENT_NAME} 初始化完成")

    def screen_library(
        self,
        target: Dict[str, Any],
        library_size: int = 10000,
    ) -> Dict[str, Any]:
        """
        对化合物库进行虚拟筛选。

        模拟流程：
        1. 生成虚拟化合物库（随机属性分布）
        2. 对每个化合物执行简化对接打分
        3. 按分数排序输出命中列表

        Args:
            target: 靶点信息字典
            library_size: 虚拟库大小

        Returns:
            筛选结果汇总
        """
        target_id = target.get("target_id", "UNKNOWN")
        logger.info(f"screen_library: 靶点={target_id} 库大小={library_size}")

        rng = random.Random(hash(f"screen_{target_id}") & 0xFFFFFFFF)

        results: List[DockingResult] = []
        for i in range(library_size):
            cpd_id = f"LIB_{target_id}_{i:06d}"
            docking = self._compute_docking_score(cpd_id, target_id, rng)
            results.append(docking)

        # 按结合分数排序（越低越好，类似 kcal/mol）
        results.sort(key=lambda r: r.binding_score)

        # 统计
        scores = [r.binding_score for r in results]
        mean_score = sum(scores) / len(scores)
        std_score = math.sqrt(sum((s - mean_score) ** 2 for s in scores) / len(scores))

        # 命中定义：低于均值 - 2 * 标准差
        hit_threshold = mean_score - 2 * std_score
        hits = [r for r in results if r.binding_score <= hit_threshold]

        self._docking_results[target_id] = results

        result = {
            "agent": self.AGENT_NAME,
            "target_id": target_id,
            "library_size": library_size,
            "screening_stats": {
                "mean_score": round(mean_score, 3),
                "std_score": round(std_score, 3),
                "min_score": round(min(scores), 3),
                "max_score": round(max(scores), 3),
                "hit_threshold": round(hit_threshold, 3),
                "n_hits": len(hits),
                "hit_rate": round(len(hits) / library_size * 100, 2),
            },
            "top_10": [
                {
                    "compound_id": r.compound_id,
                    "binding_score": round(r.binding_score, 3),
                    "confidence": round(r.confidence, 3),
                }
                for r in results[:10]
            ],
        }

        logger.info(
            f"screen_library: 完成 | 命中={len(hits)} ({result['screening_stats']['hit_rate']}%) | "
            f"top score={result['top_10'][0]['binding_score']}"
        )
        return result

    def dock(self, compound_id: str, target: Dict[str, Any]) -> Dict[str, Any]:
        """
        对单个化合物进行详细分子对接。

        Args:
            compound_id: 化合物 ID
            target: 靶点信息字典

        Returns:
            详细对接结果
        """
        target_id = target.get("target_id", "UNKNOWN")
        logger.info(f"dock: 化合物={compound_id} 靶点={target_id}")

        rng = random.Random(hash(f"dock_{compound_id}_{target_id}") & 0xFFFFFFFF)
        docking = self._compute_docking_score(compound_id, target_id, rng)

        # 多构象采样（取最优）
        n_poses = 10
        best_pose = docking
        for _ in range(n_poses - 1):
            pose = self._compute_docking_score(compound_id, target_id, rng)
            if pose.binding_score < best_pose.binding_score:
                best_pose = pose

        # 结合模式分析
        interactions = self._predict_interactions(compound_id, target_id, rng)

        result = {
            "agent": self.AGENT_NAME,
            "compound_id": compound_id,
            "target_id": target_id,
            "best_pose": {
                "binding_score_kcal_mol": round(best_pose.binding_score, 3),
                "vdw_score": round(best_pose.vdw_score, 3),
                "electrostatic_score": round(best_pose.electrostatic_score, 3),
                "desolvation_penalty": round(best_pose.desolvation_penalty, 3),
                "entropy_penalty": round(best_pose.entropy_penalty, 3),
                "pose_rmsd": round(best_pose.pose_rmsd, 3),
                "confidence": round(best_pose.confidence, 3),
            },
            "predicted_interactions": interactions,
            "n_poses_sampled": n_poses,
            "estimated_ki_nM": self._score_to_ki(best_pose.binding_score),
        }

        logger.info(
            f"dock: [{compound_id}] -> [{target_id}] "
            f"score={best_pose.binding_score:.3f} Ki={result['estimated_ki_nM']} nM"
        )
        return result

    def rank_hits(
        self,
        results: Optional[Dict[str, Any]] = None,
        top_n: int = 100,
    ) -> Dict[str, Any]:
        """
        对筛选结果进行排序和富集分析。

        Args:
            results: screen_library 返回的结果字典（None 则使用最近一次筛选结果）
            top_n: 返回前 N 个命中

        Returns:
            排序后的命中列表和富集分析
        """
        logger.info(f"rank_hits: 排序 top {top_n}")

        # 获取对接结果
        if results and "target_id" in results:
            target_id = results["target_id"]
        else:
            target_id = None

        all_results: List[DockingResult] = []
        if target_id and target_id in self._docking_results:
            all_results = self._docking_results[target_id]
        elif self._docking_results:
            # 使用最近一次
            target_id = list(self._docking_results.keys())[-1]
            all_results = self._docking_results[target_id]

        if not all_results:
            return {"error": "无可用筛选结果", "agent": self.AGENT_NAME}

        all_results.sort(key=lambda r: r.binding_score)
        top_hits = all_results[:top_n]

        # 富集分析（模拟）
        scores = [r.binding_score for r in all_results]
        top_scores = [r.binding_score for r in top_hits]
        enrichment = self._compute_enrichment_factor(scores, top_scores)

        ranked = []
        for rank, r in enumerate(top_hits, 1):
            ranked.append({
                "rank": rank,
                "compound_id": r.compound_id,
                "binding_score": round(r.binding_score, 3),
                "confidence": round(r.confidence, 3),
                "pose_rmsd": round(r.pose_rmsd, 3),
            })

        result = {
            "agent": self.AGENT_NAME,
            "target_id": target_id,
            "top_n": top_n,
            "total_screened": len(all_results),
            "ranked_hits": ranked,
            "enrichment": {
                "EF_1pct": enrichment.get("EF_1pct", 1.0),
                "EF_5pct": enrichment.get("EF_5pct", 1.0),
                "EF_10pct": enrichment.get("EF_10pct", 1.0),
            },
            "score_distribution": {
                "top_hit_score": round(top_scores[0], 3) if top_scores else 0,
                "top_n_cutoff": round(top_scores[-1], 3) if top_scores else 0,
                "mean_all": round(sum(scores) / len(scores), 3),
            },
        }

        logger.info(
            f"rank_hits: 完成 | top score={ranked[0]['binding_score']} | "
            f"EF_1%={enrichment.get('EF_1pct', 0):.1f}"
        )
        return result

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            "virtual_screening",
            "molecular_docking",
            "binding_affinity_prediction",
            "hit_ranking",
            "enrichment_analysis",
            "pose_sampling",
        ]

    # ============================================================
    # 内部方法
    # ============================================================

    def _compute_docking_score(
        self, compound_id: str, target_id: str, rng: random.Random,
    ) -> DockingResult:
        """计算简化对接打分"""
        # 各项打分模拟
        vdw = -rng.uniform(2.0, 8.0)
        elec = -rng.uniform(0.5, 5.0)
        desolv = rng.uniform(0.5, 3.0)
        entropy = rng.uniform(1.0, 4.0)
        binding = vdw + elec + desolv + entropy
        pose_rmsd = round(rng.uniform(0.5, 3.0), 3)
        confidence = round(0.5 + rng.random() * 0.45, 3)

        return DockingResult(
            compound_id=compound_id,
            target_id=target_id,
            binding_score=round(binding, 3),
            vdw_score=round(vdw, 3),
            electrostatic_score=round(elec, 3),
            desolvation_penalty=round(desolv, 3),
            entropy_penalty=round(entropy, 3),
            pose_rmsd=pose_rmsd,
            confidence=confidence,
        )

    def _predict_interactions(
        self, compound_id: str, target_id: str, rng: random.Random,
    ) -> List[Dict[str, Any]]:
        """预测分子间相互作用"""
        residue_names = ["Asp276", "Arg293", "Tyr320", "Glu305",
                         "Phe281", "Ser310", "Lys300", "Trp316"]
        interaction_types = ["H-bond", "pi-stacking", "salt bridge",
                             "hydrophobic", "van der Waals"]

        n_interactions = rng.randint(3, 7)
        interactions = []
        for _ in range(n_interactions):
            interactions.append({
                "residue": rng.choice(residue_names),
                "type": rng.choice(interaction_types),
                "distance_A": round(rng.uniform(2.5, 4.5), 2),
                "energy_kcal_mol": round(-rng.uniform(0.3, 2.5), 3),
            })
        return interactions

    @staticmethod
    def _score_to_ki(score: float) -> float:
        """
        将对接分数（kcal/mol 概念）转换为估计 Ki (nM)。
        Ki = exp(score / (RT)), RT ~= 0.592 kcal/mol at 298K
        """
        rt = 0.592
        ki_M = math.exp(score / rt)
        ki_nM = ki_M * 1e9
        return round(max(0.01, ki_nM), 2)

    @staticmethod
    def _compute_enrichment_factor(
        all_scores: List[float], top_scores: List[float],
    ) -> Dict[str, float]:
        """计算富集因子"""
        n_total = len(all_scores)
        threshold = sorted(all_scores)[int(n_total * 0.01)] if n_total > 0 else 0

        # 假设 "活性" 定义为 score <= threshold
        n_actives = sum(1 for s in all_scores if s <= threshold)
        active_fraction = n_actives / n_total if n_total > 0 else 0

        def ef(fraction: float) -> float:
            n_top = max(1, int(n_total * fraction))
            n_hit_in_top = sum(1 for s in top_scores[:n_top] if s <= threshold)
            expected = active_fraction * n_top
            return round(n_hit_in_top / max(expected, 0.01), 2)

        return {
            "EF_1pct": ef(0.01),
            "EF_5pct": ef(0.05),
            "EF_10pct": ef(0.10),
        }


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    agent = VirtualScreeningAgent()
    print("=" * 60)
    print(f"  {agent.AGENT_NAME} v{agent.AGENT_VERSION}")
    print("=" * 60)

    target = {"target_id": "FCE_RI", "target_name": "FcepsilonRI"}

    print("\n--- 虚拟筛选 (lib=1000) ---")
    screen = agent.screen_library(target, library_size=1000)
    print(json.dumps(screen["screening_stats"], indent=2, ensure_ascii=False))
    print(f"Top 3: {json.dumps(screen['top_10'][:3], indent=2, ensure_ascii=False)}")

    print("\n--- 单化合物对接 ---")
    dock = agent.dock("CPD_001", target)
    print(json.dumps(dock["best_pose"], indent=2, ensure_ascii=False))

    print("\n--- 命中排序 ---")
    ranked = agent.rank_hits(top_n=5)
    print(f"Total screened: {ranked['total_screened']}")
    print(f"Enrichment: {json.dumps(ranked['enrichment'], indent=2, ensure_ascii=False)}")
