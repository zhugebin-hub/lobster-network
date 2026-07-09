#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CompoundDesignAgent - 化合物设计智能体

功能：
- 针对食物过敏通路设计小分子和生物大分子化合物
- 多策略化合物设计（IgE 阻断肽、FcepsilonRI 拮抗剂、肥大细胞稳定剂等）
- 多目标先导化合物优化
- 结构类似物生成

设计策略：
1. IgE blocking peptides — 阻断 IgE-FcepsilonRI 结合的短肽
2. FcepsilonRI antagonist small molecules — 靶向受体结合界面的小分子
3. Mast cell stabilizers — 类色甘酸钠机制的肥大细胞稳定剂
4. Oral immunotherapy adjuvants — 增强口服免疫耐受的佐剂分子
5. Probiotic metabolite mimetics — 模拟益生菌代谢产物的分子
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

logger = logging.getLogger("compound_design_agent")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "compound_design.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


# ============================================================
# 数据模型
# ============================================================

@dataclass
class CompoundProperties:
    """化合物理化性质"""
    molecular_weight: float = 0.0
    logp: float = 0.0
    hbd: int = 0  # 氢键供体数
    hba: int = 0  # 氢键受体数
    tpsa: float = 0.0  # 拓扑极性表面积
    rotatable_bonds: int = 0
    aromatic_rings: int = 0


@dataclass
class Compound:
    """化合物设计"""
    compound_id: str
    name: str
    smiles: str
    strategy: str
    target_id: str
    properties: CompoundProperties = field(default_factory=CompoundProperties)
    predicted_activity_pic50: float = 5.0
    selectivity_score: float = 0.5
    synthesis_feasibility: float = 0.5
    status: str = "designed"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ============================================================
# 设计策略模板库
# ============================================================

DESIGN_STRATEGIES = {
    "ige_blocking_peptide": {
        "description": "IgE 阻断肽",
        "mw_range": (800, 2500),
        "logp_range": (-2.0, 1.0),
        "scaffold_smiles": "NCC(=O)NC(C)C(=O)NC(CC(=O)N)C(=O)O",
        "key_features": ["D-amino acid substitution", "cyclic constraint", "PEG linker"],
    },
    "fcepsilonri_antagonist": {
        "description": "FcepsilonRI 拮抗剂小分子",
        "mw_range": (250, 500),
        "logp_range": (1.0, 4.5),
        "scaffold_smiles": "C1=CC=C(C=C1)C2=NN=C3C=CC=CC3=C2",
        "key_features": ["hydrophobic pocket binding", "H-bond to Asp276", "pi-stacking"],
    },
    "mast_cell_stabilizer": {
        "description": "肥大细胞稳定剂",
        "mw_range": (200, 450),
        "logp_range": (0.5, 3.5),
        "scaffold_smiles": "O=C1CC(=O)C2=C(O1)C=CC=C2",
        "key_features": ["chromone core", "calcium channel modulation", "membrane stabilization"],
    },
    "oit_adjuvant": {
        "description": "口服免疫治疗佐剂",
        "mw_range": (150, 600),
        "logp_range": (-1.0, 3.0),
        "scaffold_smiles": "OC1C(O)C(O)C(O)C(O)C1O",
        "key_features": ["TLR agonist motif", "mucoadhesive", "sustained release"],
    },
    "probiotic_mimetic": {
        "description": "益生菌代谢物模拟分子",
        "mw_range": (100, 350),
        "logp_range": (-1.5, 2.5),
        "scaffold_smiles": "CCCC(=O)OCC(COP(=O)(O)O)OC(=O)CC",
        "key_features": ["SCFA mimetic", "butyrate-like", "gut epithelial targeting"],
    },
}


# ============================================================
# CompoundDesignAgent 主类
# ============================================================

class CompoundDesignAgent:
    """
    化合物设计智能体

    核心能力：
    1. 基于靶点和策略生成化合物设计（含 SMILES 表示）
    2. 多目标优化（活性、选择性、ADMET）
    3. 结构类似物库生成
    """

    AGENT_NAME = "CompoundDesignAgent"
    AGENT_VERSION = "1.0.0"

    def __init__(self):
        self._compounds: Dict[str, Compound] = {}
        self._next_id = 1
        logger.info(f"{self.AGENT_NAME} 初始化完成 | 策略库: {len(DESIGN_STRATEGIES)} 种")

    def design_compound(self, target: Dict[str, Any], strategy: str = "fcepsilonri_antagonist") -> Dict[str, Any]:
        """
        基于靶点和策略设计化合物。

        Args:
            target: 靶点信息字典（含 target_id, target_name 等）
            strategy: 设计策略名称

        Returns:
            化合物设计详情字典
        """
        target_id = target.get("target_id", "UNKNOWN")
        target_name = target.get("target_name", target_id)
        logger.info(f"design_compound: 靶点={target_id} 策略={strategy}")

        if strategy not in DESIGN_STRATEGIES:
            logger.warning(f"未知策略 {strategy}，使用默认 fcepsilonri_antagonist")
            strategy = "fcepsilonri_antagonist"

        strat = DESIGN_STRATEGIES[strategy]
        seed = hash(f"{target_id}_{strategy}_{self._next_id}") & 0xFFFFFFFF
        rng = random.Random(seed)

        # 生成化合物属性
        mw = round(rng.uniform(*strat["mw_range"]), 1)
        logp = round(rng.uniform(*strat["logp_range"]), 2)
        hbd = rng.randint(1, 5)
        hba = rng.randint(3, 10)
        tpsa = round(rng.uniform(40, 130), 1)
        rot_bonds = rng.randint(2, 8)
        aromatic = rng.randint(1, 4)

        # 预测活性
        base_activity = 5.5 + rng.gauss(0, 0.8)
        activity_pic50 = round(max(4.0, min(9.5, base_activity)), 2)

        # 选择性和合成可行性
        selectivity = round(0.4 + rng.random() * 0.55, 3)
        feasibility = round(0.3 + rng.random() * 0.6, 3)

        # 生成 SMILES 变体
        smiles_variant = self._generate_smiles_variant(strat["scaffold_smiles"], rng)

        compound_id = f"CPD_{target_id}_{self._next_id:04d}"
        self._next_id += 1

        compound = Compound(
            compound_id=compound_id,
            name=f"{strat['description']}-{target_name}-{compound_id.split('_')[-1]}",
            smiles=smiles_variant,
            strategy=strategy,
            target_id=target_id,
            properties=CompoundProperties(
                molecular_weight=mw, logp=logp, hbd=hbd, hba=hba,
                tpsa=tpsa, rotatable_bonds=rot_bonds, aromatic_rings=aromatic,
            ),
            predicted_activity_pic50=activity_pic50,
            selectivity_score=selectivity,
            synthesis_feasibility=feasibility,
        )
        self._compounds[compound_id] = compound

        result = {
            "agent": self.AGENT_NAME,
            "compound_id": compound_id,
            "name": compound.name,
            "smiles": compound.smiles,
            "strategy": strategy,
            "strategy_description": strat["description"],
            "target_id": target_id,
            "target_name": target_name,
            "properties": {
                "MW": mw, "LogP": logp, "HBD": hbd,
                "HBA": hba, "TPSA": tpsa,
                "rotatable_bonds": rot_bonds, "aromatic_rings": aromatic,
            },
            "predicted_activity": {
                "pIC50": activity_pic50,
                "IC50_nM": round(10 ** (9 - activity_pic50), 2),
            },
            "selectivity_score": selectivity,
            "synthesis_feasibility": feasibility,
            "key_features": strat["key_features"],
            "lipinski_compliant": self._check_lipinski(mw, logp, hbd, hba),
        }

        logger.info(
            f"design_compound: {compound_id} | "
            f"pIC50={activity_pic50} LogP={logp} MW={mw}"
        )
        return result

    def optimize_lead(
        self,
        compound_id: str,
        optimization_goals: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        多目标优化先导化合物。

        优化目标：
        - 提高活性（pIC50）
        - 提高选择性
        - 改善 ADMET 属性
        - 维持合成可行性

        Args:
            compound_id: 化合物 ID
            optimization_goals: 优化权重 {activity, selectivity, admet, feasibility}

        Returns:
            优化后的化合物信息
        """
        logger.info(f"optimize_lead: 优化 [{compound_id}]")

        compound = self._compounds.get(compound_id)
        if not compound:
            return {"error": f"化合物 {compound_id} 不存在", "agent": self.AGENT_NAME}

        if optimization_goals is None:
            optimization_goals = {
                "activity": 0.35,
                "selectivity": 0.25,
                "admet": 0.25,
                "feasibility": 0.15,
            }

        rng = random.Random(hash(compound_id + "_opt") & 0xFFFFFFFF)

        # 模拟优化过程
        iterations = 5
        history = []
        current_activity = compound.predicted_activity_pic50
        current_selectivity = compound.selectivity_score
        current_feasibility = compound.synthesis_feasibility

        for i in range(iterations):
            # 每轮小幅改进
            delta_act = rng.gauss(0.15, 0.1) * optimization_goals.get("activity", 0.25)
            delta_sel = rng.gauss(0.08, 0.05) * optimization_goals.get("selectivity", 0.25)
            delta_fea = rng.gauss(0.05, 0.03) * optimization_goals.get("feasibility", 0.15)

            current_activity = round(min(9.5, current_activity + delta_act), 3)
            current_selectivity = round(min(1.0, current_selectivity + delta_sel), 3)
            current_feasibility = round(min(1.0, current_feasibility + delta_fea), 3)

            # 综合得分
            composite = (
                current_activity / 10.0 * optimization_goals.get("activity", 0.25) +
                current_selectivity * optimization_goals.get("selectivity", 0.25) +
                (1.0 - abs(compound.properties.logp - 2.5) / 5.0) * optimization_goals.get("admet", 0.25) +
                current_feasibility * optimization_goals.get("feasibility", 0.15)
            )
            history.append({
                "iteration": i + 1,
                "activity_pic50": current_activity,
                "selectivity": current_selectivity,
                "feasibility": current_feasibility,
                "composite_score": round(composite, 4),
            })

        # 更新化合物
        compound.predicted_activity_pic50 = current_activity
        compound.selectivity_score = current_selectivity
        compound.synthesis_feasibility = current_feasibility
        compound.status = "optimized"

        result = {
            "agent": self.AGENT_NAME,
            "compound_id": compound_id,
            "optimization": {
                "iterations": iterations,
                "history": history,
                "final": {
                    "activity_pic50": current_activity,
                    "IC50_nM": round(10 ** (9 - current_activity), 2),
                    "selectivity": current_selectivity,
                    "feasibility": current_feasibility,
                },
                "improvement": {
                    "activity_delta": round(current_activity - history[0]["activity_pic50"] + history[0]["activity_pic50"] - compound.predicted_activity_pic50 + current_activity, 3) if len(history) > 1 else 0,
                },
            },
            "goals": optimization_goals,
        }

        logger.info(
            f"optimize_lead: [{compound_id}] 完成 | "
            f"final pIC50={current_activity} sel={current_selectivity}"
        )
        return result

    def generate_analogs(self, compound_id: str, n: int = 10) -> Dict[str, Any]:
        """
        生成结构类似物库。

        变换策略：
        - 生物电子等排替换（-F, -Cl, -CH3, -CF3, -OCH3）
        - 环系统修饰
        - 侧链长度调整
        - 官能团替换

        Args:
            compound_id: 母体化合物 ID
            n: 生成类似物数量

        Returns:
            类似物库详情
        """
        logger.info(f"generate_analogs: 为 [{compound_id}] 生成 {n} 个类似物")

        parent = self._compounds.get(compound_id)
        if not parent:
            return {"error": f"化合物 {compound_id} 不存在", "agent": self.AGENT_NAME}

        rng = random.Random(hash(compound_id + "_analog") & 0xFFFFFFFF)

        substituents = ["-F", "-Cl", "-Br", "-CH3", "-CF3", "-OCH3", "-OH", "-NH2",
                        "-CN", "-NO2", "-SO2CH3", "-N(CH3)2", "-C(=O)NH2"]
        ring_modifications = ["phenyl", "pyridine", "pyrimidine", "thiophene", "furan",
                              "cyclohexyl", "piperidine", "morpholine"]

        analogs = []
        for i in range(n):
            analog_id = f"{compound_id}_A{i+1:02d}"
            sub = rng.choice(substituents)
            ring = rng.choice(ring_modifications)

            # 属性微扰
            mw_delta = rng.gauss(0, 20)
            logp_delta = rng.gauss(0, 0.4)
            new_mw = round(max(100, parent.properties.molecular_weight + mw_delta), 1)
            new_logp = round(parent.properties.logp + logp_delta, 2)
            new_hbd = max(0, parent.properties.hbd + rng.choice([-1, 0, 0, 1]))
            new_hba = max(1, parent.properties.hba + rng.choice([-1, 0, 0, 1]))
            new_tpsa = round(max(20, parent.properties.tpsa + rng.gauss(0, 10)), 1)

            activity_delta = rng.gauss(0, 0.5)
            new_activity = round(max(4.0, min(9.5, parent.predicted_activity_pic50 + activity_delta)), 2)

            analogs.append({
                "analog_id": analog_id,
                "modification": f"{sub} at R{rng.randint(1,4)}, {ring} core",
                "properties": {
                    "MW": new_mw, "LogP": new_logp,
                    "HBD": new_hbd, "HBA": new_hba, "TPSA": new_tpsa,
                },
                "predicted_pIC50": new_activity,
                "similarity_to_parent": round(0.6 + rng.random() * 0.35, 3),
            })

        analogs.sort(key=lambda x: x["predicted_pIC50"], reverse=True)

        result = {
            "agent": self.AGENT_NAME,
            "parent_compound": compound_id,
            "n_analogs": len(analogs),
            "analogs": analogs,
            "top_3": analogs[:3],
            "activity_range": {
                "min": analogs[-1]["predicted_pIC50"],
                "max": analogs[0]["predicted_pIC50"],
            },
        }

        logger.info(f"generate_analogs: 完成 {n} 个类似物 | 活性范围 {analogs[-1]['predicted_pIC50']}-{analogs[0]['predicted_pIC50']}")
        return result

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            "compound_design",
            "smiles_generation",
            "lead_optimization",
            "analog_generation",
            "multi_objective_optimization",
            "lipinski_evaluation",
            "synthesis_feasibility",
        ]

    # ============================================================
    # 内部工具方法
    # ============================================================

    @staticmethod
    def _generate_smiles_variant(base_smiles: str, rng: random.Random) -> str:
        """基于骨架 SMILES 生成变体"""
        fragments = [
            "C(=O)", "N", "O", "S", "c1ccccc1", "C1CCCCC1",
            "C(F)(F)F", "OC", "NC", "C#N", "C(=O)O", "C(=O)N",
        ]
        additions = "".join(rng.choice(fragments) for _ in range(rng.randint(1, 3)))
        return base_smiles + additions

    @staticmethod
    def _check_lipinski(mw: float, logp: float, hbd: int, hba: int) -> bool:
        """检查 Lipinski 五规则"""
        return mw < 500 and logp < 5 and hbd <= 5 and hba <= 10


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    agent = CompoundDesignAgent()
    print("=" * 60)
    print(f"  {agent.AGENT_NAME} v{agent.AGENT_VERSION}")
    print("=" * 60)

    target = {"target_id": "FCE_RI", "target_name": "FcepsilonRI"}

    print("\n--- 化合物设计 ---")
    result = agent.design_compound(target, "fcepsilonri_antagonist")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:600])

    print("\n--- 先导优化 ---")
    opt = agent.optimize_lead(result["compound_id"])
    print(json.dumps(opt["optimization"]["final"], indent=2, ensure_ascii=False))

    print("\n--- 类似物生成 ---")
    analogs = agent.generate_analogs(result["compound_id"], n=5)
    print(f"生成 {analogs['n_analogs']} 个类似物")
    print(f"Top 3: {json.dumps(analogs['top_3'], indent=2, ensure_ascii=False)[:400]}")
