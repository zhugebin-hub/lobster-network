#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AdmetPredictionAgent - ADMET 属性预测智能体

功能：
- 吸收（Absorption）：口服生物利用度、Caco-2 渗透性
- 分布（Distribution）：血浆蛋白结合率、分布容积
- 代谢（Metabolism）：CYP450 相互作用（CYP3A4, CYP2D6, CYP2C9）
- 排泄（Excretion）：半衰期、清除途径
- 毒性（Toxicity）：hERG 风险、Ames 致突变性

类药性评估：
- Lipinski 五规则：MW<500, LogP<5, HBD<=5, HBA<=10
- Veber 规则：TPSA<140, RotBonds<=10
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

logger = logging.getLogger("admet_prediction_agent")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "admet_prediction.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


# ============================================================
# Lipinski / Veber 规则常量
# ============================================================

LIPINSKI_RULES = {
    "MW_max": 500.0,
    "LogP_max": 5.0,
    "HBD_max": 5,
    "HBA_max": 10,
}

VEBER_RULES = {
    "TPSA_max": 140.0,
    "rotatable_bonds_max": 10,
}


# ============================================================
# AdmetPredictionAgent 主类
# ============================================================

class AdmetPredictionAgent:
    """
    ADMET 属性预测智能体

    核心能力：
    1. 预测化合物完整 ADMET 属性档案
    2. 评估口服生物利用度和 Caco-2 渗透性
    3. 预测 CYP450 酶相互作用
    4. 预测 hERG 和 Ames 毒性风险
    5. Lipinski/Veber 类药性过滤
    """

    AGENT_NAME = "AdmetPredictionAgent"
    AGENT_VERSION = "1.0.0"

    def __init__(self):
        self._predictions: Dict[str, Dict[str, Any]] = {}
        logger.info(f"{self.AGENT_NAME} 初始化完成")

    def predict_admet(self, compound_id: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        预测化合物完整 ADMET 属性档案。

        Args:
            compound_id: 化合物 ID
            properties: 化合物理化属性（MW, LogP, HBD, HBA, TPSA），
                        None 则生成模拟属性

        Returns:
            完整 ADMET 预测档案
        """
        logger.info(f"predict_admet: 化合物 [{compound_id}]")

        if properties is None:
            rng = random.Random(hash(compound_id) & 0xFFFFFFFF)
            properties = {
                "MW": round(rng.uniform(200, 550), 1),
                "LogP": round(rng.uniform(0.5, 5.5), 2),
                "HBD": rng.randint(1, 7),
                "HBA": rng.randint(3, 12),
                "TPSA": round(rng.uniform(40, 160), 1),
            }

        absorption = self.predict_absorption(compound_id, properties)
        distribution = self._predict_distribution(compound_id, properties)
        metabolism = self.predict_metabolism(compound_id, properties)
        excretion = self._predict_excretion(compound_id, properties)
        toxicity = self.predict_toxicity_basic(compound_id, properties)

        result = {
            "agent": self.AGENT_NAME,
            "compound_id": compound_id,
            "input_properties": properties,
            "absorption": absorption,
            "distribution": distribution,
            "metabolism": metabolism,
            "excretion": excretion,
            "toxicity": toxicity,
            "drug_likeness": {
                "lipinski_pass": self._check_lipinski(properties),
                "veber_pass": self._check_veber(properties),
                "lipinski_violations": self._count_lipinski_violations(properties),
            },
            "timestamp": datetime.now().isoformat(),
        }

        self._predictions[compound_id] = result
        logger.info(
            f"predict_admet: [{compound_id}] 完成 | "
            f"Lipinski={result['drug_likeness']['lipinski_pass']} "
            f"hERG_risk={toxicity['herg_risk_level']}"
        )
        return result

    def predict_absorption(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        预测吸收特性。

        评估指标：
        - 口服生物利用度 (F20%/F30%)
        - Caco-2 渗透性 (log cm/s)
        - 水溶解度 (logS)
        - 肠道吸收率

        Args:
            compound_id: 化合物 ID
            properties: 理化属性

        Returns:
            吸收预测结果
        """
        mw = properties.get("MW", 350)
        logp = properties.get("LogP", 2.5)
        hbd = properties.get("HBD", 3)
        hba = properties.get("HBA", 6)
        tpsa = properties.get("TPSA", 80)

        # 口服生物利用度估算（基于属性规则）
        oral_bioavailability = 0.8
        if mw > 500:
            oral_bioavailability -= 0.2
        if logp > 5 or logp < 0:
            oral_bioavailability -= 0.15
        if hbd > 5:
            oral_bioavailability -= 0.15
        if hba > 10:
            oral_bioavailability -= 0.1
        if tpsa > 140:
            oral_bioavailability -= 0.2
        oral_bioavailability = round(max(0.05, min(0.95, oral_bioavailability)), 3)

        # Caco-2 渗透性（log cm/s，越高越好）
        caco2_permeability = round(-4.5 + logp * 0.3 - tpsa * 0.01, 3)
        caco2_permeability = max(-7.0, min(-3.5, caco2_permeability))

        # 水溶解度 logS
        log_solubility = round(0.5 - 0.01 * mw - 0.6 * logp + 0.005 * tpsa, 2)
        log_solubility = max(-8.0, min(1.0, log_solubility))

        # 肠道吸收率
        intestinal_absorption = round(
            95.0 - max(0, tpsa - 60) * 0.5 - max(0, mw - 400) * 0.05,
            1,
        )
        intestinal_absorption = max(10.0, min(98.0, intestinal_absorption))

        return {
            "oral_bioavailability_pct": round(oral_bioavailability * 100, 1),
            "caco2_permeability_log_cm_s": caco2_permeability,
            "aqueous_solubility_logS": log_solubility,
            "intestinal_absorption_pct": intestinal_absorption,
            "p_glycoprotein_substrate": logp > 3.5 and mw > 400,
        }

    def predict_metabolism(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        预测代谢特性（CYP450 相互作用）。

        CYP 酶：
        - CYP3A4：最丰富的肝药酶，代谢约 50% 的药物
        - CYP2D6：多态性显著，代谢约 25% 的药物
        - CYP2C9：代谢约 15% 的药物

        Args:
            compound_id: 化合物 ID
            properties: 理化属性

        Returns:
            CYP450 相互作用预测
        """
        logp = properties.get("LogP", 2.5)
        mw = properties.get("MW", 350)

        rng = random.Random(hash(f"met_{compound_id}") & 0xFFFFFFFF)

        # CYP 抑制/底物概率（基于属性的经验模型）
        cyp_interactions = {}
        cyps = {
            "CYP3A4": {"substrate_bias": 0.4, "inhibition_bias": 0.3},
            "CYP2D6": {"substrate_bias": 0.25, "inhibition_bias": 0.2},
            "CYP2C9": {"substrate_bias": 0.2, "inhibition_bias": 0.15},
            "CYP1A2": {"substrate_bias": 0.15, "inhibition_bias": 0.1},
            "CYP2C19": {"substrate_bias": 0.15, "inhibition_bias": 0.1},
        }

        for cyp, bias in cyps.items():
            # LogP 和 MW 增加抑制/底物概率
            sub_prob = bias["substrate_bias"] + (logp - 2.5) * 0.05 + (mw - 300) * 0.0005
            sub_prob = round(max(0.05, min(0.95, sub_prob + rng.gauss(0, 0.08))), 3)

            inh_prob = bias["inhibition_bias"] + (logp - 2.5) * 0.06 + (mw - 300) * 0.0006
            inh_prob = round(max(0.05, min(0.95, inh_prob + rng.gauss(0, 0.08))), 3)

            cyp_interactions[cyp] = {
                "substrate_probability": sub_prob,
                "inhibitor_probability": inh_prob,
                "risk_level": "high" if inh_prob > 0.6 else ("moderate" if inh_prob > 0.35 else "low"),
            }

        return {
            "cyp_interactions": cyp_interactions,
            "primary_metabolic_pathway": self._predict_primary_pathway(properties),
            "metabolic_stability": round(0.4 + rng.random() * 0.5, 3),
        }

    def predict_toxicity_basic(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        基础毒性预测。

        评估项目：
        - hERG 通道阻断风险
        - Ames 致突变性
        - 急性口服毒性分类

        Args:
            compound_id: 化合物 ID
            properties: 理化属性

        Returns:
            毒性预测结果
        """
        logp = properties.get("LogP", 2.5)
        mw = properties.get("MW", 350)
        hba = properties.get("HBA", 6)

        rng = random.Random(hash(f"tox_{compound_id}") & 0xFFFFFFFF)

        # hERG 风险（LogP 高、含氮碱性化合物风险高）
        herg_risk = 0.1 + (logp - 2.0) * 0.1 + max(0, (mw - 400) * 0.001)
        herg_risk = round(max(0.05, min(0.95, herg_risk + rng.gauss(0, 0.05))), 3)
        herg_level = "high" if herg_risk > 0.6 else ("moderate" if herg_risk > 0.3 else "low")

        # Ames 致突变性
        ames_prob = 0.05 + rng.gauss(0, 0.03)
        if hba > 8:
            ames_prob += 0.05
        ames_prob = round(max(0.01, min(0.5, ames_prob)), 3)
        ames_positive = ames_prob > 0.15

        # 急性口服毒性 LD50 估算（GHS 分类）
        ld50 = round(500 + (500 - mw) * 2 + (5 - logp) * 100 + rng.gauss(0, 50), 0)
        ld50 = max(5, ld50)
        ghs_class = self._ld50_to_ghs(ld50)

        return {
            "herg_risk_probability": herg_risk,
            "herg_risk_level": herg_level,
            "ames_mutagenicity_probability": ames_prob,
            "ames_positive": ames_positive,
            "acute_oral_ld50_mg_kg": round(ld50, 1),
            "ghs_toxicity_class": ghs_class,
        }

    def filter_drug_likeness(self, compounds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对化合物列表应用 Lipinski 五规则和 Veber 规则过滤。

        Args:
            compounds: 化合物列表，每项需含 MW, LogP, HBD, HBA 字段

        Returns:
            过滤结果汇总
        """
        logger.info(f"filter_drug_likeness: 过滤 {len(compounds)} 个化合物")

        passed = []
        failed = []

        for cpd in compounds:
            lipinski_pass = self._check_lipinski(cpd)
            veber_pass = self._check_veber(cpd)
            violations = self._count_lipinski_violations(cpd)

            entry = {
                "compound_id": cpd.get("compound_id", cpd.get("analog_id", "unknown")),
                "lipinski_pass": lipinski_pass,
                "veber_pass": veber_pass,
                "lipinski_violations": violations,
                "drug_like": lipinski_pass and veber_pass,
            }

            if lipinski_pass and veber_pass:
                passed.append(entry)
            else:
                entry["failure_reasons"] = []
                if not lipinski_pass:
                    entry["failure_reasons"].append("Lipinski violation")
                if not veber_pass:
                    entry["failure_reasons"].append("Veber rule failure")
                failed.append(entry)

        result = {
            "agent": self.AGENT_NAME,
            "total_input": len(compounds),
            "passed": len(passed),
            "failed": len(failed),
            "pass_rate": round(len(passed) / max(len(compounds), 1) * 100, 1),
            "passed_compounds": passed,
            "failed_compounds": failed[:10],  # 只返回前 10 个失败案例
        }

        logger.info(
            f"filter_drug_likeness: 完成 | "
            f"通过 {len(passed)}/{len(compounds)} ({result['pass_rate']}%)"
        )
        return result

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            "admet_prediction",
            "absorption_prediction",
            "cyp450_interaction",
            "hERG_risk_assessment",
            "ames_mutagenicity",
            "lipinski_evaluation",
            "veber_evaluation",
            "oral_bioavailability",
        ]

    # ============================================================
    # 内部方法
    # ============================================================

    def _predict_distribution(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """预测分布特性"""
        logp = properties.get("LogP", 2.5)
        rng = random.Random(hash(f"dist_{compound_id}") & 0xFFFFFFFF)

        ppb = round(min(99.5, 50 + logp * 8 + rng.gauss(0, 5)), 1)
        vd = round(0.3 + logp * 0.2 + rng.gauss(0, 0.1), 2)
        vd = max(0.1, min(5.0, vd))
        bbb = logp > 1.5 and logp < 4.0 and properties.get("TPSA", 80) < 90

        return {
            "plasma_protein_binding_pct": ppb,
            "volume_of_distribution_L_kg": vd,
            "blood_brain_barrier_permeable": bbb,
        }

    def _predict_excretion(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """预测排泄特性"""
        mw = properties.get("MW", 350)
        logp = properties.get("LogP", 2.5)
        rng = random.Random(hash(f"excr_{compound_id}") & 0xFFFFFFFF)

        half_life = round(2 + logp * 1.5 + rng.gauss(0, 1), 1)
        half_life = max(0.5, min(72, half_life))
        renal = mw < 300 and logp < 2
        biliary = mw > 400 or logp > 3

        return {
            "half_life_hours": half_life,
            "renal_clearance_dominant": renal,
            "biliary_clearance_likely": biliary,
        }

    @staticmethod
    def _predict_primary_pathway(properties: Dict[str, Any]) -> str:
        """预测主要代谢途径"""
        logp = properties.get("LogP", 2.5)
        if logp > 3.5:
            return "Oxidation (CYP3A4-mediated)"
        elif logp > 1.5:
            return "Mixed oxidation and conjugation"
        else:
            return "Phase II conjugation (glucuronidation)"

    @staticmethod
    def _check_lipinski(properties: Dict[str, Any]) -> bool:
        """Lipinski 五规则检查"""
        return (
            properties.get("MW", 0) < LIPINSKI_RULES["MW_max"] and
            properties.get("LogP", 0) < LIPINSKI_RULES["LogP_max"] and
            properties.get("HBD", 0) <= LIPINSKI_RULES["HBD_max"] and
            properties.get("HBA", 0) <= LIPINSKI_RULES["HBA_max"]
        )

    @staticmethod
    def _check_veber(properties: Dict[str, Any]) -> bool:
        """Veber 规则检查"""
        return (
            properties.get("TPSA", 0) < VEBER_RULES["TPSA_max"] and
            properties.get("rotatable_bonds", 0) <= VEBER_RULES["rotatable_bonds_max"]
        )

    @staticmethod
    def _count_lipinski_violations(properties: Dict[str, Any]) -> int:
        """计算 Lipinski 违规数"""
        violations = 0
        if properties.get("MW", 0) >= LIPINSKI_RULES["MW_max"]:
            violations += 1
        if properties.get("LogP", 0) >= LIPINSKI_RULES["LogP_max"]:
            violations += 1
        if properties.get("HBD", 0) > LIPINSKI_RULES["HBD_max"]:
            violations += 1
        if properties.get("HBA", 0) > LIPINSKI_RULES["HBA_max"]:
            violations += 1
        return violations

    @staticmethod
    def _ld50_to_ghs(ld50: float) -> str:
        """LD50 转 GHS 毒性分类"""
        if ld50 <= 5:
            return "Category 1 (Fatal if swallowed)"
        elif ld50 <= 50:
            return "Category 2 (Fatal if swallowed)"
        elif ld50 <= 300:
            return "Category 3 (Toxic if swallowed)"
        elif ld50 <= 2000:
            return "Category 4 (Harmful if swallowed)"
        else:
            return "Not classified"


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    agent = AdmetPredictionAgent()
    print("=" * 60)
    print(f"  {agent.AGENT_NAME} v{agent.AGENT_VERSION}")
    print("=" * 60)

    print("\n--- ADMET 完整预测 ---")
    props = {"MW": 380.4, "LogP": 2.8, "HBD": 2, "HBA": 6, "TPSA": 78.5}
    result = agent.predict_admet("CPD_TEST_001", props)
    print(json.dumps({
        "absorption": result["absorption"],
        "drug_likeness": result["drug_likeness"],
        "toxicity_summary": result["toxicity"],
    }, indent=2, ensure_ascii=False))

    print("\n--- 类药性过滤 ---")
    test_compounds = [
        {"compound_id": "A", "MW": 350, "LogP": 2.5, "HBD": 2, "HBA": 5, "TPSA": 70, "rotatable_bonds": 4},
        {"compound_id": "B", "MW": 550, "LogP": 5.5, "HBD": 6, "HBA": 12, "TPSA": 150, "rotatable_bonds": 12},
        {"compound_id": "C", "MW": 280, "LogP": 1.8, "HBD": 3, "HBA": 4, "TPSA": 55, "rotatable_bonds": 3},
    ]
    filter_result = agent.filter_drug_likeness(test_compounds)
    print(f"通过: {filter_result['passed']}/{filter_result['total_input']} ({filter_result['pass_rate']}%)")
