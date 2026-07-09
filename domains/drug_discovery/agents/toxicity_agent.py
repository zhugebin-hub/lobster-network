#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ToxicityAssessmentAgent - 毒性评估智能体

功能：
- 综合毒性档案评估
- hERG 通道阻断风险预测
- 急性毒性 LD50 估算
- 脱靶效应筛选
- 安全评估报告生成

参考：
- ICH S7A/B 安全药理学指导原则
- ICH M7 致突变杂质评估
- FDA hERG 安全性评估指南
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

logger = logging.getLogger("toxicity_assessment_agent")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "toxicity_assessment.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


# ============================================================
# 脱靶靶点库
# ============================================================

OFF_TARGET_PANEL = [
    {"target": "hERG (KCNH2)", "type": "ion_channel", "risk_impact": "cardiac_arrhythmia"},
    {"target": "Nav1.5 (SCN5A)", "type": "ion_channel", "risk_impact": "cardiac_conduction"},
    {"target": "Cav1.2 (CACNA1C)", "type": "ion_channel", "risk_impact": "cardiovascular"},
    {"target": "5-HT2B", "type": "gpcr", "risk_impact": "valvular_heart_disease"},
    {"target": "D2 (Dopamine)", "type": "gpcr", "risk_impact": "CNS_side_effects"},
    {"target": "H1 (Histamine)", "type": "gpcr", "risk_impact": "sedation"},
    {"target": "MAO-A", "type": "enzyme", "risk_impact": "drug_interaction"},
    {"target": "COX-1", "type": "enzyme", "risk_impact": "GI_toxicity"},
    {"target": "COX-2", "type": "enzyme", "risk_impact": "cardiovascular_risk"},
    {"target": "PXR (NR1I2)", "type": "nuclear_receptor", "risk_impact": "drug_interaction"},
]


# ============================================================
# ToxicityAssessmentAgent 主类
# ============================================================

class ToxicityAssessmentAgent:
    """
    毒性评估智能体

    核心能力：
    1. 综合毒性档案评估（心脏毒性、肝毒性、基因毒性）
    2. hERG 通道阻断风险定量预测
    3. 急性口服毒性 LD50 估算与 GHS 分类
    4. 脱靶效应多靶点筛选
    5. 结构化安全评估报告生成
    """

    AGENT_NAME = "ToxicityAssessmentAgent"
    AGENT_VERSION = "1.0.0"

    def __init__(self):
        self._assessments: Dict[str, Dict[str, Any]] = {}
        logger.info(f"{self.AGENT_NAME} 初始化完成 | 脱靶面板: {len(OFF_TARGET_PANEL)} 靶点")

    def assess_toxicity(self, compound_id: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        综合毒性评估。

        Args:
            compound_id: 化合物 ID
            properties: 化合物理化属性

        Returns:
            综合毒性档案
        """
        logger.info(f"assess_toxicity: 综合评估 [{compound_id}]")

        if properties is None:
            rng = random.Random(hash(compound_id) & 0xFFFFFFFF)
            properties = {
                "MW": round(rng.uniform(200, 550), 1),
                "LogP": round(rng.uniform(0.5, 5.5), 2),
                "HBD": rng.randint(1, 7),
                "HBA": rng.randint(3, 12),
                "TPSA": round(rng.uniform(40, 160), 1),
            }

        herg = self.predict_herg(compound_id, properties)
        ld50 = self.predict_ld50(compound_id, properties)
        off_target = self.check_off_target(compound_id, properties)

        # 肝毒性风险
        rng = random.Random(hash(f"hep_{compound_id}") & 0xFFFFFFFF)
        hepatotoxicity_risk = round(0.1 + (properties.get("LogP", 2.5) - 2) * 0.05 + rng.gauss(0, 0.04), 3)
        hepatotoxicity_risk = round(max(0.02, min(0.8, hepatotoxicity_risk)), 3)

        # 综合安全评分
        safety_score = 1.0
        safety_score -= herg["herg_risk_probability"] * 0.3
        safety_score -= max(0, (0.3 - ld50["ld50_category_score"])) * 0.2
        safety_score -= max(0, off_target["n_high_risk"]) * 0.05
        safety_score -= hepatotoxicity_risk * 0.15
        safety_score = round(max(0.0, min(1.0, safety_score)), 3)

        result = {
            "agent": self.AGENT_NAME,
            "compound_id": compound_id,
            "herg_assessment": herg,
            "acute_toxicity": ld50,
            "off_target_profile": off_target,
            "hepatotoxicity": {
                "risk_probability": hepatotoxicity_risk,
                "risk_level": "high" if hepatotoxicity_risk > 0.4 else ("moderate" if hepatotoxicity_risk > 0.2 else "low"),
            },
            "overall_safety_score": safety_score,
            "safety_grade": self._score_to_grade(safety_score),
            "timestamp": datetime.now().isoformat(),
        }

        self._assessments[compound_id] = result
        logger.info(
            f"assess_toxicity: [{compound_id}] {result['safety_grade']} "
            f"(score={safety_score})"
        )
        return result

    def predict_herg(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        hERG 通道阻断风险预测。

        风险因素：
        - LogP > 3.5（脂溶性越高，风险越大）
        - 碱性含氮基团（与 hERG 孔道芳香残基作用）
        - MW > 400
        - 低极性表面积

        Args:
            compound_id: 化合物 ID
            properties: 理化属性

        Returns:
            hERG 风险评估
        """
        logp = properties.get("LogP", 2.5)
        mw = properties.get("MW", 350)
        tpsa = properties.get("TPSA", 80)
        hba = properties.get("HBA", 6)

        rng = random.Random(hash(f"herg_{compound_id}") & 0xFFFFFFFF)

        # hERG 阻断概率模型
        risk = 0.05
        risk += max(0, (logp - 2.0)) * 0.12
        risk += max(0, (mw - 350)) * 0.0008
        risk -= max(0, (tpsa - 60)) * 0.002
        risk += rng.gauss(0, 0.03)
        risk = round(max(0.02, min(0.95, risk)), 3)

        # IC50 估算 (uM)
        herg_ic50 = round(10 ** (2.5 - logp * 0.4 + tpsa * 0.01 + rng.gauss(0, 0.3)), 2)
        herg_ic50 = max(0.01, herg_ic50)

        if risk > 0.6:
            risk_level = "high"
            recommendation = "Structural optimization required to reduce hERG liability"
        elif risk > 0.3:
            risk_level = "moderate"
            recommendation = "Consider LogP reduction or TPSA increase"
        else:
            risk_level = "low"
            recommendation = "Acceptable hERG risk profile"

        return {
            "herg_risk_probability": risk,
            "herg_risk_level": risk_level,
            "estimated_ic50_uM": herg_ic50,
            "safety_margin": round(herg_ic50 / max(0.01, 0.1), 1),  # vs. estimated therapeutic conc.
            "recommendation": recommendation,
        }

    def predict_ld50(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        急性口服毒性 LD50 估算。

        基于 QSAR 概念的简化模型：
        - 分子量、脂溶性、极性表面积与毒性的经验关系
        - GHS 全球协调系统分类

        Args:
            compound_id: 化合物 ID
            properties: 理化属性

        Returns:
            LD50 估算和 GHS 分类
        """
        mw = properties.get("MW", 350)
        logp = properties.get("LogP", 2.5)
        hbd = properties.get("HBD", 3)

        rng = random.Random(hash(f"ld50_{compound_id}") & 0xFFFFFFFF)

        # 简化 LD50 模型
        ld50 = 800 + (500 - mw) * 1.5 + (3 - logp) * 80 + hbd * 15 + rng.gauss(0, 80)
        ld50 = round(max(5, ld50), 1)

        # GHS 分类
        if ld50 <= 5:
            ghs_class = "Category 1"
            category_score = 0.95
        elif ld50 <= 50:
            ghs_class = "Category 2"
            category_score = 0.8
        elif ld50 <= 300:
            ghs_class = "Category 3"
            category_score = 0.5
        elif ld50 <= 2000:
            ghs_class = "Category 4"
            category_score = 0.2
        else:
            ghs_class = "Not classified"
            category_score = 0.05

        return {
            "estimated_ld50_mg_kg": ld50,
            "ghs_classification": ghs_class,
            "ld50_category_score": category_score,
            "confidence": round(0.5 + rng.random() * 0.35, 3),
        }

    def check_off_target(self, compound_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        脱靶效应筛选。

        对预定义的脱靶靶点面板进行虚拟筛选，
        评估每个靶点的结合概率和风险等级。

        Args:
            compound_id: 化合物 ID
            properties: 理化属性

        Returns:
            脱靶筛选结果
        """
        logp = properties.get("LogP", 2.5)
        mw = properties.get("MW", 350)
        rng = random.Random(hash(f"offt_{compound_id}") & 0xFFFFFFFF)

        off_targets = []
        n_high = 0
        n_moderate = 0

        for panel_item in OFF_TARGET_PANEL:
            # 结合概率模拟
            base_prob = 0.1
            if panel_item["type"] == "ion_channel":
                base_prob += max(0, (logp - 2.5)) * 0.08
            elif panel_item["type"] == "gpcr":
                base_prob += max(0, (logp - 2.0)) * 0.06
            elif panel_item["type"] == "enzyme":
                base_prob += max(0, (mw - 350)) * 0.0005

            prob = base_prob + rng.gauss(0, 0.04)
            prob = round(max(0.01, min(0.95, prob)), 3)

            if prob > 0.5:
                level = "high"
                n_high += 1
            elif prob > 0.25:
                level = "moderate"
                n_moderate += 1
            else:
                level = "low"

            off_targets.append({
                "target": panel_item["target"],
                "type": panel_item["type"],
                "binding_probability": prob,
                "risk_level": level,
                "risk_impact": panel_item["risk_impact"],
            })

        off_targets.sort(key=lambda x: x["binding_probability"], reverse=True)

        return {
            "n_targets_screened": len(OFF_TARGET_PANEL),
            "n_high_risk": n_high,
            "n_moderate_risk": n_moderate,
            "off_targets": off_targets,
            "selectivity_index": round(1.0 - (n_high + n_moderate * 0.5) / len(OFF_TARGET_PANEL), 3),
        }

    def safety_report(self, compound_id: str) -> Dict[str, Any]:
        """
        生成结构化安全评估报告。

        Args:
            compound_id: 化合物 ID

        Returns:
            完整安全评估报告
        """
        logger.info(f"safety_report: 生成报告 [{compound_id}]")

        assessment = self._assessments.get(compound_id)
        if not assessment:
            logger.warning(f"safety_report: [{compound_id}] 无已有评估，执行自动评估")
            assessment = self.assess_toxicity(compound_id)

        # 风险汇总
        risks = []
        if assessment["herg_assessment"]["herg_risk_level"] == "high":
            risks.append("HIGH hERG risk - cardiac arrhythmia concern")
        if assessment["acute_toxicity"]["ghs_classification"] in ("Category 1", "Category 2"):
            risks.append("HIGH acute oral toxicity")
        if assessment["off_target_profile"]["n_high_risk"] > 2:
            risks.append("Multiple off-target interactions")
        if assessment["hepatotoxicity"]["risk_level"] == "high":
            risks.append("Hepatotoxicity concern")

        if not risks:
            risks.append("No major safety concerns identified")

        # 建议
        recommendations = []
        if assessment["herg_assessment"]["herg_risk_level"] in ("high", "moderate"):
            recommendations.append("Optimize LogP and reduce basic nitrogen centers")
        if assessment["off_target_profile"]["n_high_risk"] > 0:
            recommendations.append("Increase selectivity through structural modification")
        if assessment["overall_safety_score"] < 0.5:
            recommendations.append("Consider alternative compound series")
        if not recommendations:
            recommendations.append("Proceed to further preclinical evaluation")

        report = {
            "agent": self.AGENT_NAME,
            "report_type": "Safety Assessment Report",
            "compound_id": compound_id,
            "safety_grade": assessment["safety_grade"],
            "overall_safety_score": assessment["overall_safety_score"],
            "key_findings": risks,
            "recommendations": recommendations,
            "detailed_assessment": assessment,
            "report_generated_at": datetime.now().isoformat(),
        }

        logger.info(
            f"safety_report: [{compound_id}] {assessment['safety_grade']} | "
            f"risks={len(risks)} recommendations={len(recommendations)}"
        )
        return report

    def get_capabilities(self) -> List[str]:
        """返回智能体能力列表"""
        return [
            "toxicity_assessment",
            "hERG_prediction",
            "acute_toxicity_ld50",
            "off_target_screening",
            "hepatotoxicity_prediction",
            "safety_report_generation",
            "ghs_classification",
        ]

    # ============================================================
    # 内部方法
    # ============================================================

    @staticmethod
    def _score_to_grade(score: float) -> str:
        """安全评分转等级"""
        if score >= 0.8:
            return "A (Excellent)"
        elif score >= 0.6:
            return "B (Good)"
        elif score >= 0.4:
            return "C (Moderate)"
        elif score >= 0.2:
            return "D (Poor)"
        else:
            return "F (Unacceptable)"


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    agent = ToxicityAssessmentAgent()
    print("=" * 60)
    print(f"  {agent.AGENT_NAME} v{agent.AGENT_VERSION}")
    print("=" * 60)

    props = {"MW": 380.4, "LogP": 2.8, "HBD": 2, "HBA": 6, "TPSA": 78.5}

    print("\n--- 综合毒性评估 ---")
    result = agent.assess_toxicity("CPD_TEST_001", props)
    print(f"安全等级: {result['safety_grade']}")
    print(f"安全评分: {result['overall_safety_score']}")
    print(f"hERG 风险: {result['herg_assessment']['herg_risk_level']}")
    print(f"LD50: {result['acute_toxicity']['estimated_ld50_mg_kg']} mg/kg")
    print(f"脱靶高风险数: {result['off_target_profile']['n_high_risk']}")

    print("\n--- 安全报告 ---")
    report = agent.safety_report("CPD_TEST_001")
    print(f"关键发现: {report['key_findings']}")
    print(f"建议: {report['recommendations']}")
