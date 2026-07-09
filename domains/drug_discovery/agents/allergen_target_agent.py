#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AllergenTargetAgent - 食物过敏原靶点发现与验证智能体

功能：
- 从过敏原数据库中发掘治疗靶点（IgE 表位、FcepsilonRI 受体、肥大细胞激活通路）
- 验证靶点可药性（结合位点分析、表达水平、通路参与度）
- 生成科学假说（靶点干预策略）

参考：
- WHO/IUIS 过敏原命名数据库
- UniProt 过敏原注释
- Allergome 数据库
"""

import json
import logging
import math
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


# ============================================================
# 日志配置
# ============================================================

logger = logging.getLogger("allergen_target_agent")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "allergen_target.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


# ============================================================
# 数据模型
# ============================================================

@dataclass
class AllergenEntry:
    """过敏原条目"""
    id: str
    name: str
    source: str
    protein_family: str
    epitopes: List[str] = field(default_factory=list)
    ige_binding_affinity: str = "moderate"
    prevalence: str = ""
    stability: str = ""


@dataclass
class TherapeuticTarget:
    """治疗靶点"""
    id: str
    name: str
    target_type: str
    pathway: str
    druggability_score: float = 0.5
    drug_modalities: List[str] = field(default_factory=list)
    known_inhibitors: List[str] = field(default_factory=list)


@dataclass
class Hypothesis:
    """科学假说"""
    hypothesis_id: str
    target_id: str
    description: str
    rationale: str
    predicted_efficacy: float
    confidence: float
    intervention_strategy: str
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# AllergenTargetAgent 主类
# ============================================================

class AllergenTargetAgent:
    """
    食物过敏原靶点发现与验证智能体

    核心能力：
    1. 从过敏原知识库中发现潜在治疗靶点
    2. 评估靶点可药性（结合位点、表达水平、通路角色）
    3. 基于知识图谱嵌入（RotatE 512 维概念）生成靶点关联预测
    4. 输出科学假说与干预策略建议

    知识库覆盖：
    - Ara h 1/2（花生）、Casein（牛奶）、Tropomyosin（甲壳类）
    - Ovalbumin（鸡蛋）、Parvalbumin（鱼类）、Gliadin（小麦）
    - Ses i 1（芝麻）、Pru p 3（桃子）
    """

    AGENT_NAME = "AllergenTargetAgent"
    AGENT_VERSION = "1.0.0"

    def __init__(self, knowledge_base_path: Optional[Path] = None):
        """
        初始化智能体。

        Args:
            knowledge_base_path: 过敏原知识库 JSON 路径，默认使用内置路径
        """
        if knowledge_base_path is None:
            knowledge_base_path = (
                Path(__file__).resolve().parent.parent / "knowledge_base" / "allergen_targets.json"
            )
        self.kb_path = knowledge_base_path
        self.allergens: List[AllergenEntry] = []
        self.targets: List[TherapeuticTarget] = []
        self.pathways: List[Dict[str, Any]] = []
        self._knowledge_embeddings: Dict[str, List[float]] = {}

        self._load_knowledge_base()
        self._init_knowledge_embeddings()
        logger.info(
            f"{self.AGENT_NAME} 初始化完成 | "
            f"过敏原: {len(self.allergens)} | "
            f"靶点: {len(self.targets)} | "
            f"通路: {len(self.pathways)}"
        )

    def _load_knowledge_base(self):
        """加载过敏原知识库"""
        if not self.kb_path.exists():
            logger.warning(f"知识库文件不存在: {self.kb_path}，使用内置默认数据")
            self._load_default_data()
            return

        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for a in data.get("allergens", []):
            self.allergens.append(AllergenEntry(
                id=a["id"], name=a["name"], source=a["source"],
                protein_family=a["protein_family"],
                epitopes=a.get("epitopes", []),
                ige_binding_affinity=a.get("ige_binding_affinity", "moderate"),
                prevalence=a.get("prevalence", ""),
                stability=a.get("stability", ""),
            ))

        for t in data.get("therapeutic_targets", []):
            self.targets.append(TherapeuticTarget(
                id=t["id"], name=t["name"], target_type=t["type"],
                pathway=t["pathway"],
                druggability_score=t.get("druggability_score", 0.5),
                drug_modalities=t.get("drug_modalities", []),
                known_inhibitors=t.get("known_inhibitors", []),
            ))

        self.pathways = data.get("pathways", [])

    def _load_default_data(self):
        """加载内置默认过敏原数据（知识库文件不可用时的回退）"""
        defaults = [
            ("ARA_H1", "Ara h 1", "Peanut", "Cupin (7S vicilin)"),
            ("ARA_H2", "Ara h 2", "Peanut", "Conglutin (2S albumin)"),
            ("CAS_S1", "Casein", "Cow's milk", "Casein"),
            ("TRO_P1", "Tropomyosin", "Shrimp", "Tropomyosin"),
            ("OVA_L1", "Ovalbumin", "Egg white", "Serpin"),
            ("PAR_V1", "Parvalbumin", "Fish", "Parvalbumin"),
        ]
        for aid, name, source, family in defaults:
            self.allergens.append(AllergenEntry(
                id=aid, name=name, source=source, protein_family=family
            ))
        self.targets.append(TherapeuticTarget(
            id="FCE_RI", name="FcepsilonRI", target_type="receptor",
            pathway="Mast cell degranulation", druggability_score=0.85,
        ))

    def _init_knowledge_embeddings(self):
        """
        初始化知识图谱嵌入（模拟 RotatE 512 维向量）

        实际生产中应使用预训练的 KG embedding（TransE / RotatE / ComplEx）。
        此处为演示目的生成确定性伪随机向量。
        """
        entities = [a.id for a in self.allergens] + [t.id for t in self.targets]
        random.seed(42)
        for entity_id in entities:
            # 确定性嵌入：基于 ID 哈希生成 512 维单位向量
            seed = sum(ord(c) for c in entity_id)
            rng = random.Random(seed)
            raw = [rng.gauss(0, 1) for _ in range(512)]
            norm = math.sqrt(sum(x * x for x in raw))
            self._knowledge_embeddings[entity_id] = [x / max(norm, 1e-8) for x in raw]
        logger.debug(f"知识嵌入初始化完成: {len(self._knowledge_embeddings)} 个实体")

    # ============================================================
    # 核心方法
    # ============================================================

    def discover_targets(self) -> Dict[str, Any]:
        """
        从过敏原数据库中发掘潜在治疗靶点。

        策略：
        1. 按 IgE 结合亲和力排序过敏原
        2. 按可药性分数排序治疗靶点
        3. 计算过敏原-靶点关联性（知识嵌入余弦相似度）

        Returns:
            包含优先级排序的靶点列表和关联分析的字典
        """
        logger.info("discover_targets: 开始靶点发现...")

        # 按 IgE 亲和力排序过敏原
        affinity_order = {"high": 3, "moderate": 2, "low": 1}
        ranked_allergens = sorted(
            self.allergens,
            key=lambda a: affinity_order.get(a.ige_binding_affinity, 0),
            reverse=True,
        )

        # 按可药性排序靶点
        ranked_targets = sorted(self.targets, key=lambda t: t.druggability_score, reverse=True)

        # 计算过敏原-靶点关联（知识嵌入余弦相似度）
        associations = []
        for allergen in self.allergens:
            for target in self.targets:
                sim = self._cosine_similarity(
                    self._knowledge_embeddings.get(allergen.id, []),
                    self._knowledge_embeddings.get(target.id, []),
                )
                if sim > 0.3:  # 阈值筛选
                    associations.append({
                        "allergen_id": allergen.id,
                        "target_id": target.id,
                        "similarity": round(sim, 4),
                        "interpretation": self._interpret_similarity(sim),
                    })

        associations.sort(key=lambda x: x["similarity"], reverse=True)

        result = {
            "agent": self.AGENT_NAME,
            "timestamp": datetime.now().isoformat(),
            "high_priority_allergens": [
                {"id": a.id, "name": a.name, "source": a.source,
                 "affinity": a.ige_binding_affinity}
                for a in ranked_allergens[:5]
            ],
            "druggable_targets": [
                {"id": t.id, "name": t.name, "type": t.target_type,
                 "druggability": t.druggability_score,
                 "modalities": t.drug_modalities}
                for t in ranked_targets[:5]
            ],
            "allergen_target_associations": associations[:10],
            "total_allergens": len(self.allergens),
            "total_targets": len(self.targets),
        }

        logger.info(
            f"discover_targets: 完成 | "
            f"高优先级过敏原: {len(result['high_priority_allergens'])} | "
            f"可药靶点: {len(result['druggable_targets'])} | "
            f"关联: {len(associations)}"
        )
        return result

    def validate_target(self, target_id: str) -> Dict[str, Any]:
        """
        验证靶点可药性。

        评估维度：
        - 结合位点可及性（模拟分析）
        - 组织表达水平
        - 通路参与深度
        - 已知配体/抑制剂可用性
        - 安全性信号

        Args:
            target_id: 靶点 ID（如 FCE_RI, SYK, BTK）

        Returns:
            靶点验证报告字典
        """
        logger.info(f"validate_target: 验证靶点 [{target_id}]")

        target = self._find_target(target_id)
        if not target:
            return {
                "agent": self.AGENT_NAME,
                "target_id": target_id,
                "status": "not_found",
                "message": f"靶点 {target_id} 不在知识库中",
            }

        # 模拟各维度评分
        seed = sum(ord(c) for c in target_id)
        rng = random.Random(seed)

        binding_site_score = round(0.5 + rng.random() * 0.45, 3)
        expression_score = round(0.4 + rng.random() * 0.5, 3)
        pathway_depth = round(0.3 + rng.random() * 0.6, 3)
        ligand_availability = 1.0 if target.known_inhibitors else 0.3
        safety_signal = round(0.6 + rng.random() * 0.35, 3)

        # 综合验证分数
        validation_score = (
            binding_site_score * 0.25 +
            expression_score * 0.15 +
            pathway_depth * 0.20 +
            ligand_availability * 0.25 +
            safety_signal * 0.15
        )
        validation_score = round(validation_score, 3)

        # 判断可药性等级
        if validation_score >= 0.75:
            druggability_grade = "HIGH"
        elif validation_score >= 0.55:
            druggability_grade = "MODERATE"
        else:
            druggability_grade = "LOW"

        # 关联过敏原
        related_allergens = [
            a.id for a in self.allergens
            if self._cosine_similarity(
                self._knowledge_embeddings.get(a.id, []),
                self._knowledge_embeddings.get(target_id, []),
            ) > 0.3
        ]

        result = {
            "agent": self.AGENT_NAME,
            "target_id": target_id,
            "target_name": target.name,
            "target_type": target.target_type,
            "pathway": target.pathway,
            "validation": {
                "binding_site_score": binding_site_score,
                "expression_score": expression_score,
                "pathway_depth": pathway_depth,
                "ligand_availability": ligand_availability,
                "safety_signal": safety_signal,
                "overall_score": validation_score,
                "druggability_grade": druggability_grade,
            },
            "known_inhibitors": target.known_inhibitors,
            "drug_modalities": target.drug_modalities,
            "related_allergens": related_allergens,
            "confidence": round(min(validation_score + 0.1, 1.0), 3),
        }

        logger.info(
            f"validate_target: [{target_id}] {druggability_grade} "
            f"(score={validation_score}, inhibitors={len(target.known_inhibitors)})"
        )
        return result

    def generate_hypothesis(self, target: Dict[str, Any]) -> Hypothesis:
        """
        基于靶点信息生成科学假说。

        假说模板：
        - 抑制 [靶点] 可阻断 [通路]，从而减轻 [过敏原] 诱导的过敏反应
        - [干预策略] 靶向 [靶点] 可能实现口服免疫耐受的增强

        Args:
            target: validate_target() 返回的靶点信息字典

        Returns:
            Hypothesis 数据类实例
        """
        target_id = target.get("target_id", "UNKNOWN")
        target_name = target.get("target_name", target_id)
        pathway = target.get("pathway", "allergic signaling")
        related = target.get("related_allergens", [])
        modalities = target.get("drug_modalities", ["small_molecule"])
        grade = target.get("validation", {}).get("druggability_grade", "MODERATE")

        allergen_names = []
        for aid in related[:3]:
            al = next((a for a in self.allergens if a.id == aid), None)
            if al:
                allergen_names.append(al.name)

        allergen_str = "、".join(allergen_names) if allergen_names else "多种食物过敏原"
        modality = modalities[0] if modalities else "small_molecule"

        # 根据可药性等级选择干预策略
        strategies = {
            "HIGH": f"高选择性 {modality} 抑制剂阻断 {target_name} 活性位点",
            "MODERATE": f"靶向 {target_name} 的 {modality} 或联合用药策略",
            "LOW": f"变构调节或间接靶向 {target_name} 的创新策略",
        }
        strategy = strategies.get(grade, strategies["MODERATE"])

        score = target.get("validation", {}).get("overall_score", 0.5)
        efficacy = round(min(score * 0.9 + random.uniform(0, 0.15), 1.0), 3)
        confidence = round(min(score * 0.85 + random.uniform(0.05, 0.2), 1.0), 3)

        hypothesis = Hypothesis(
            hypothesis_id=f"HYP_{target_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            target_id=target_id,
            description=(
                f"抑制 {target_name} 可有效阻断 {pathway}，"
                f"从而减轻 {allergen_str} 诱导的过敏反应症状。"
                f"基于当前可药性评估（{grade}），该靶点适合作为药物开发优先目标。"
            ),
            rationale=(
                f"{target_name} 在 {pathway} 中起关键调控作用，"
                f"已知 {len(target.get('known_inhibitors', []))} 个先导化合物可作为开发起点，"
                f"知识图谱分析显示与 {len(related)} 种过敏原存在显著关联。"
            ),
            predicted_efficacy=efficacy,
            confidence=confidence,
            intervention_strategy=strategy,
        )

        logger.info(
            f"generate_hypothesis: {hypothesis.hypothesis_id} | "
            f"efficacy={efficacy} confidence={confidence}"
        )
        return hypothesis

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            "target_discovery",
            "allergen_database_query",
            "ige_epitope_analysis",
            "druggability_assessment",
            "knowledge_graph_embedding",
            "hypothesis_generation",
            "pathway_analysis",
            "target_validation",
        ]

    # ============================================================
    # 内部工具方法
    # ============================================================

    def _find_target(self, target_id: str) -> Optional[TherapeuticTarget]:
        """根据 ID 查找靶点"""
        for t in self.targets:
            if t.id == target_id:
                return t
        return None

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a < 1e-8 or norm_b < 1e-8:
            return 0.0
        return dot / (norm_a * norm_b)

    @staticmethod
    def _interpret_similarity(sim: float) -> str:
        """解释相似度含义"""
        if sim > 0.7:
            return "Strong mechanistic link"
        elif sim > 0.5:
            return "Moderate association"
        elif sim > 0.3:
            return "Weak but notable connection"
        return "Minimal association"


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    agent = AllergenTargetAgent()
    print("=" * 60)
    print(f"  {agent.AGENT_NAME} v{agent.AGENT_VERSION}")
    print("=" * 60)

    # 靶点发现
    print("\n--- 靶点发现 ---")
    discovery = agent.discover_targets()
    print(json.dumps(discovery, indent=2, ensure_ascii=False)[:800])

    # 靶点验证
    print("\n--- 靶点验证 (FCE_RI) ---")
    validation = agent.validate_target("FCE_RI")
    print(json.dumps(validation, indent=2, ensure_ascii=False)[:600])

    # 生成假说
    print("\n--- 生成假说 ---")
    hyp = agent.generate_hypothesis(validation)
    print(f"  ID: {hyp.hypothesis_id}")
    print(f"  描述: {hyp.description[:100]}...")
    print(f"  预测效力: {hyp.predicted_efficacy}")
    print(f"  置信度: {hyp.confidence}")
