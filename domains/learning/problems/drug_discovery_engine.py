"""
新药创制科学智能体引擎 V1.0
聚焦：食物过敏防治药物研制

支持8大科学方法：
1. 靶点识别 (Target Identification) - 食物过敏通路靶点挖掘
2. 先导化合物筛选 (Lead Compound Screening) - 虚拟筛选+类药性评估
3. 分子对接评分 (Molecular Docking) - 结合自由能+关键残基分析
4. ADMET预测 - 吸收/分布/代谢/排泄/毒性五维评估
5. 药物安全评估 (Drug Safety) - 副作用/禁忌/相互作用
6. 临床试验设计 (Clinical Trial Design) - I/II/III期方案生成
7. 食物过敏通路分析 (Food Allergy Pathway) - IgE通路/Th2免疫/口服耐受
8. 免疫疗法设计 (Immunotherapy Design) - OIT/SLIT/EPIT方案
"""

import json
import os
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ========== 内置知识库 ==========

# 食物过敏主要靶点
FOOD_ALLERGY_TARGETS = {
    "IgE": {
        "name": "免疫球蛋白E",
        "pathway": "IgE介导型过敏反应",
        "mechanism": "过敏原与IgE交联→肥大细胞/嗜碱性粒细胞脱颗粒→组胺释放",
        "drug_class": "抗IgE单抗",
        "examples": ["奥马珠单抗(Omalizumab)", "利格珠单抗(Ligelizumab)"],
        "binding_site": "IgE Fc片段(Cε3 domain)",
        "clinical_stage": "已上市/III期",
        "efficacy": 0.72,
    },
    "IL-4Rα": {
        "name": "白细胞介素4受体α链",
        "pathway": "Th2型免疫反应",
        "mechanism": "阻断IL-4/IL-13信号→抑制Th2分化→减少IgE类别转换",
        "drug_class": "IL-4Rα单抗",
        "examples": ["度普利尤单抗(Dupilumab)"],
        "binding_site": "IL-4Rα胞外域",
        "clinical_stage": "III期(食物过敏适应症)",
        "efficacy": 0.68,
    },
    "FcεRI": {
        "name": "高亲和力IgE受体",
        "pathway": "肥大细胞激活",
        "mechanism": "阻断IgE-FcεRI结合→抑制脱颗粒",
        "drug_class": "抗FcεRI抗体",
        "examples": ["候选药物(临床前)"],
        "binding_site": "FcεRI α链",
        "clinical_stage": "临床前",
        "efficacy": 0.55,
    },
    "TSLP": {
        "name": "胸腺基质淋巴细胞生成素",
        "pathway": "上皮源性警报素通路",
        "mechanism": "阻断TSLP→抑制树突状细胞激活Th2→减少过敏原致敏",
        "drug_class": "抗TSLP单抗",
        "examples": ["特泽鲁单抗(Tezepelumab)"],
        "binding_site": "TSLP受体复合物",
        "clinical_stage": "II期(食物过敏探索)",
        "efficacy": 0.60,
    },
    "IL-33": {
        "name": "白细胞介素33",
        "pathway": "上皮警报素-ILC2通路",
        "mechanism": "中和IL-33→抑制ILC2激活→减少Th2细胞因子",
        "drug_class": "抗IL-33单抗/ST2受体融合蛋白",
        "examples": ["依妥珠单抗(Etokimab)", "ASTE-007"],
        "binding_site": "IL-33 / ST2受体",
        "clinical_stage": "II期",
        "efficacy": 0.58,
    },
    "FOXP3": {
        "name": "叉头框蛋白P3(调节性T细胞)",
        "pathway": "口服免疫耐受",
        "mechanism": "增强Treg功能→促进口服耐受→抑制过敏反应",
        "drug_class": "Treg增强剂/表观遗传调控",
        "examples": ["低剂量IL-2 / HDAC抑制剂(候选)"],
        "binding_site": "FOXP3启动子/增强子",
        "clinical_stage": "I期/临床前",
        "efficacy": 0.45,
    },
}

# 常见过敏原
ALLERGENS = {
    "花生": {
        "scientific": "Arachis hypogaea",
        "major_allergens": ["Ara h 1(7S球蛋白)", "Ara h 2(2S白蛋白)", "Ara h 3(11S球蛋白)", "Ara h 6(2S白蛋白)"],
        "prevalence": "0.6-1.0%",
        "severity": "高(致死性过敏风险)",
        "persistence": "约20%儿童可耐受",
        "cross_reactivity": ["大豆", "其他豆科"],
    },
    "牛奶": {
        "scientific": "Bos taurus",
        "major_allergens": ["αs1-酪蛋白", "β-乳球蛋白", "α-乳白蛋白"],
        "prevalence": "2-3%(儿童)",
        "severity": "中",
        "persistence": "约80%儿童5岁前耐受",
        "cross_reactivity": ["羊奶", "水牛奶"],
    },
    "鸡蛋": {
        "scientific": "Gallus gallus",
        "major_allergens": ["卵白蛋白(OVA)", "卵类黏蛋白(OVM)", "溶菌酶"],
        "prevalence": "1.6-3.2%(儿童)",
        "severity": "中",
        "persistence": "约70%儿童6岁前耐受",
        "cross_reactivity": ["其他禽类蛋"],
    },
    "小麦": {
        "scientific": "Triticum aestivum",
        "major_allergens": ["ω-5醇溶蛋白", "低分子量麦谷蛋白", "α-淀粉酶抑制剂"],
        "prevalence": "0.1-0.3%",
        "severity": "中(运动诱发加重)",
        "persistence": "约50%儿童可耐受",
        "cross_reactivity": ["大麦", "黑麦"],
    },
    "坚果": {
        "scientific": "多树种",
        "major_allergens": ["胡桃:Jug r 1(2S白蛋白)", "腰果:Ana o 3(2S白蛋白)", "榛子:Cor a 14"],
        "prevalence": "0.4-1.1%",
        "severity": "高(致死性过敏风险)",
        "persistence": "约10%可耐受",
        "cross_reactivity": ["同科属坚果"],
    },
    "海鲜": {
        "scientific": "甲壳类/软体类",
        "major_allergens": ["原肌球蛋白(Tropomyosin)", "精氨酸激酶"],
        "prevalence": "0.5-2.5%(成人更高)",
        "severity": "中-高",
        "persistence": "通常持续终生",
        "cross_reactivity": ["甲壳类间高度交叉", "尘螨"],
    },
}

# 先导化合物库(示例)
COMPOUND_LIBRARY = [
    {"id": "LN-001", "name": "龙虾素-A", "smiles": "CC1=CC(NC2=NC=NC(NC3=CC=C(F)C=C3)=N2)=CC=C1", "mw": 348.35, "logp": 3.2, "hbd": 2, "hba": 6, "rotatable": 4, "tpsa": 68.5, "class": "小分子激酶抑制剂"},
    {"id": "LN-002", "name": "龙虾素-B", "smiles": "OC1=CC=C(NC2=NC=NC(NC3=CC=C(Cl)C=C3)=N2)C=C1", "mw": 350.78, "logp": 2.8, "hbd": 3, "hba": 6, "rotatable": 4, "tpsa": 75.1, "class": "小分子激酶抑制剂"},
    {"id": "LN-003", "name": "耐虾肽-1", "smiles": "CC(C)CC1NC(=O)C(NC(=O)C(NC1=O)Cc1ccccc1)CCCN", "mw": 415.53, "logp": 0.5, "hbd": 5, "hba": 4, "rotatable": 8, "tpsa": 85.3, "class": "环肽"},
    {"id": "LN-004", "name": "耐虾肽-2", "smiles": "CC1CC(NC(=O)C2=CC=CC=C2)C(=O)NC(C(=O)NC(C(=O)N1)C(C)C)CC3=CC=CC=C3", "mw": 528.65, "logp": 1.2, "hbd": 4, "hba": 4, "rotatable": 7, "tpsa": 73.2, "class": "环肽"},
    {"id": "LN-005", "name": "虾青素衍生物-X", "smiles": "CC(C)=CCC(C)(C)C=CC1=C(C)C(O)=CC(C)=C1C=CC(C)(C)CCC=C(C)C", "mw": 596.86, "logp": 9.5, "hbd": 2, "hba": 3, "rotatable": 10, "tpsa": 58.2, "class": "类胡萝卜素衍生物"},
    {"id": "LN-006", "name": "免疫调节素-C", "smiles": "NC(=O)C1=CC=C(NC2=NC=NC(NC3=CC=C(OC)C=C3)=N2)C=C1", "mw": 349.37, "logp": 2.1, "hbd": 3, "hba": 7, "rotatable": 4, "tpsa": 82.1, "class": "小分子免疫调节剂"},
    {"id": "LN-007", "name": "脱敏素-D", "smiles": "O=C1CC2=CC=C(O)C=C2N1C3=CC=C(C(N)=O)C=C3", "mw": 294.30, "logp": 1.8, "hbd": 3, "hba": 4, "rotatable": 1, "tpsa": 79.5, "class": "小分子脱敏剂"},
    {"id": "LN-008", "name": "耐受因子-E", "smiles": "CCCCCCCC(=O)NCC1=CC=C(O)C=C1", "mw": 235.32, "logp": 4.1, "hbd": 2, "hba": 2, "rotatable": 5, "tpsa": 41.3, "class": "脂肪酸酰胺"},
    {"id": "LN-009", "name": "IgE阻断肽-F", "smiles": "CC1=CC=C(NC(=O)C2CCN(CC3=CC=CC=C3)C2)C=C1C", "mw": 308.42, "logp": 3.5, "hbd": 1, "hba": 3, "rotatable": 3, "tpsa": 43.8, "class": "小分子肽模拟物"},
    {"id": "LN-010", "name": "Th2调节素-G", "smiles": "O=C(NC1=CC=C(N2CCN(CC3=CC=C(F)C=C3)CC2)C=C1)C4=CC=CC=C4", "mw": 395.47, "logp": 4.2, "hbd": 1, "hba": 3, "rotatable": 4, "tpsa": 42.5, "class": "小分子免疫调节剂"},
]


class DrugDiscoveryEngine:
    """新药创制科学智能体引擎"""

    def __init__(self, problems_dir: str = None):
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__), 'problems', 'drug-discovery'
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self.targets = FOOD_ALLERGY_TARGETS
        self.allergens = ALLERGENS
        self.compound_library = COMPOUND_LIBRARY
        self._load_problems()

    def _load_problems(self):
        for phase in ['phase1', 'phase2', 'phase3']:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, 'problems.json')
            if os.path.exists(problems_file):
                with open(problems_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.phases[phase] = data

    # ========== 方法1: 靶点识别 ==========

    def identify_drug_target(self, allergen: str = "花生",
                             pathway: str = "IgE",
                             intervention_type: str = "阻断") -> Dict:
        """
        靶点识别 — 基于食物过敏通路分析推荐药物靶点

        Args:
            allergen: 过敏原(花生/牛奶/鸡蛋/小麦/坚果/海鲜)
            pathway: 通路偏好(IgE/Th2/TSLP/IL-33/口服耐受)
            intervention_type: 干预类型(阻断/增强/调节)

        Returns:
            靶点推荐报告
        """
        allergen_info = self.allergens.get(allergen, {})
        target_info = self.targets.get(pathway, {})

        # 多维度评分
        novelty = 0.5
        druggability = 0.5
        clinical_feasibility = 0.5
        market_potential = 0.5

        if pathway == "IgE":
            novelty = 0.3
            druggability = 0.85
            clinical_feasibility = 0.80
            market_potential = 0.90
        elif pathway == "IL-4Rα":
            novelty = 0.55
            druggability = 0.80
            clinical_feasibility = 0.75
            market_potential = 0.85
        elif pathway == "TSLP":
            novelty = 0.75
            druggability = 0.70
            clinical_feasibility = 0.60
            market_potential = 0.75
        elif pathway == "IL-33":
            novelty = 0.80
            druggability = 0.65
            clinical_feasibility = 0.55
            market_potential = 0.70
        elif pathway == "FOXP3":
            novelty = 0.90
            druggability = 0.35
            clinical_feasibility = 0.30
            market_potential = 0.65

        # 过敏原严重性加分
        severity = allergen_info.get("severity", "中")
        if "高" in severity or "致死" in severity:
            market_potential += 0.05
            clinical_feasibility += 0.03

        # 综合评分
        scores = {
            "靶点新颖性": round(novelty, 3),
            "可成药性": round(druggability, 3),
            "临床可行性": round(clinical_feasibility, 3),
            "市场潜力": round(market_potential, 3),
        }
        overall = sum(scores.values()) / len(scores)

        # 推荐策略
        if intervention_type == "阻断":
            strategy = f"开发{target_info.get('drug_class', '阻断剂')}，靶向{target_info.get('binding_site', '关键位点')}"
        elif intervention_type == "增强":
            strategy = f"增强{target_info.get('name', pathway)}功能，促进免疫耐受"
        else:
            strategy = f"调节{target_info.get('pathway', pathway)}通路，实现免疫平衡"

        return {
            "allergen": allergen,
            "allergen_info": allergen_info,
            "target": pathway,
            "target_info": {
                "name": target_info.get("name", pathway),
                "pathway": target_info.get("pathway", ""),
                "mechanism": target_info.get("mechanism", ""),
                "drug_class": target_info.get("drug_class", ""),
                "examples": target_info.get("examples", []),
                "binding_site": target_info.get("binding_site", ""),
                "clinical_stage": target_info.get("clinical_stage", ""),
                "known_efficacy": target_info.get("efficacy", 0),
            },
            "intervention": intervention_type,
            "strategy": strategy,
            "scores": scores,
            "overall_score": round(overall, 3),
            "recommendation": "推荐推进" if overall >= 0.6 else "需进一步验证" if overall >= 0.45 else "风险较高",
            "timestamp": datetime.now().isoformat(),
        }

    # ========== 方法2: 先导化合物筛选 ==========

    def screen_lead_compounds(self, target: str = "IgE",
                               max_results: int = 5,
                               mw_range: Tuple[float, float] = (200, 600),
                               logp_range: Tuple[float, float] = (-1, 5)) -> Dict:
        """
        先导化合物虚拟筛选 — Lipinski五规则+类药性评估

        Args:
            target: 药物靶点
            max_results: 最大返回数
            mw_range: 分子量范围
            logp_range: logP范围

        Returns:
            筛选结果
        """
        results = []

        for comp in self.compound_library:
            # Lipinski五规则
            lipinski_pass = (
                comp["mw"] <= 500 and
                comp["logp"] <= 5 and
                comp["hbd"] <= 5 and
                comp["hba"] <= 10
            )

            # 范围筛选
            in_range = (
                mw_range[0] <= comp["mw"] <= mw_range[1] and
                logp_range[0] <= comp["logp"] <= logp_range[1]
            )

            # 类药性评分 (Drug-likeness)
            dl_score = 0.5
            # 分子量最优区间 250-450
            if 250 <= comp["mw"] <= 450:
                dl_score += 0.15
            elif 200 <= comp["mw"] <= 500:
                dl_score += 0.05
            # logP最优区间 1-3
            if 1 <= comp["logp"] <= 3:
                dl_score += 0.15
            elif 0 <= comp["logp"] <= 4:
                dl_score += 0.05
            # TPSA最优 < 140 (口服生物利用度)
            if comp["tpsa"] <= 140:
                dl_score += 0.10
            # 可旋转键 < 10
            if comp["rotatable"] <= 10:
                dl_score += 0.05
            # HBD+HBA 适中
            if comp["hbd"] + comp["hba"] <= 12:
                dl_score += 0.05

            # 靶点适配加分
            target_bonus = 0
            if target == "IgE" and "肽" in comp["name"]:
                target_bonus = 0.10
            elif target == "IL-4Rα" and "免疫调节" in comp["class"]:
                target_bonus = 0.08
            elif target == "FOXP3" and "耐受" in comp["name"]:
                target_bonus = 0.12

            dl_score += target_bonus
            dl_score = min(dl_score, 1.0)

            if lipinski_pass and in_range:
                results.append({
                    "compound_id": comp["id"],
                    "name": comp["name"],
                    "smiles": comp["smiles"],
                    "mw": comp["mw"],
                    "logp": comp["logp"],
                    "hbd": comp["hbd"],
                    "hba": comp["hba"],
                    "rotatable_bonds": comp["rotatable"],
                    "tpsa": comp["tpsa"],
                    "class": comp["class"],
                    "lipinski_pass": lipinski_pass,
                    "drug_likeness_score": round(dl_score, 3),
                    "target_affinity_bonus": target_bonus,
                    "violations": self._count_lipinski_violations(comp),
                })

        # 按类药性评分排序
        results.sort(key=lambda x: x["drug_likeness_score"], reverse=True)
        top_results = results[:max_results]

        return {
            "target": target,
            "total_screened": len(self.compound_library),
            "total_passed": len(results),
            "pass_rate": round(len(results) / len(self.compound_library), 3) if self.compound_library else 0,
            "top_compounds": top_results,
            "screening_criteria": {
                "mw_range": f"{mw_range[0]}-{mw_range[1]} Da",
                "logp_range": f"{logp_range[0]}-{logp_range[1]}",
                "rules": "Lipinski五规则 + TPSA + 可旋转键",
            },
            "timestamp": datetime.now().isoformat(),
        }

    def _count_lipinski_violations(self, comp: Dict) -> int:
        violations = 0
        if comp["mw"] > 500: violations += 1
        if comp["logp"] > 5: violations += 1
        if comp["hbd"] > 5: violations += 1
        if comp["hba"] > 10: violations += 1
        return violations

    # ========== 方法3: 分子对接评分 ==========

    def molecular_docking_score(self, compound_name: str = None,
                                 target: str = "IgE",
                                 compound_id: str = None) -> Dict:
        """
        分子对接评分 — 结合自由能+关键残基分析

        Args:
            compound_name: 化合物名称
            target: 靶点
            compound_id: 化合物ID

        Returns:
            对接评分结果
        """
        # 查找化合物
        compound = None
        for c in self.compound_library:
            if compound_id and c["id"] == compound_id:
                compound = c
                break
            if compound_name and c["name"] == compound_name:
                compound = c
                break
        if not compound:
            return {"error": f"未找到化合物: {compound_name or compound_id}"}

        # 模拟对接评分
        # 结合自由能 (kcal/mol), 越负越好
        base_binding = -8.0

        # 分子量影响
        mw_factor = -abs(compound["mw"] - 350) * 0.005
        # logP影响
        logp_factor = -abs(compound["logp"] - 2.5) * 0.3
        # 氢键影响
        hbond_factor = -(compound["hbd"] + compound["hba"]) * 0.2
        # TPSA影响
        tpsa_factor = -abs(compound["tpsa"] - 70) * 0.01

        binding_energy = base_binding + mw_factor + logp_factor + hbond_factor + tpsa_factor

        # 靶点特异性
        target_info = self.targets.get(target, {})
        known_efficacy = target_info.get("efficacy", 0.5)
        target_factor = known_efficacy * 2
        binding_energy -= target_factor

        binding_energy = round(binding_energy, 2)

        # Ki估算 (Ki = exp(ΔG / RT), RT=0.593 at 298K)
        ki = math.exp(binding_energy / 0.593)
        ki_uM = ki * 1e6  # 转换为μM

        # 评分等级
        if binding_energy <= -10:
            grade = "A+ (极强结合)"
        elif binding_energy <= -8:
            grade = "A (强结合)"
        elif binding_energy <= -6:
            grade = "B (中等结合)"
        elif binding_energy <= -4:
            grade = "C (弱结合)"
        else:
            grade = "D (极弱)"

        # 关键残基(模拟)
        key_residues = {
            "IgE": ["R330", "K351", "D371", "E412"],
            "IL-4Rα": ["R53", "Y83", "Y127", "D105"],
            "FcεRI": ["K117", "E158", "R165", "H156"],
            "TSLP": ["R67", "E103", "K149", "Y152"],
            "IL-33": ["D125", "R146", "E159", "Y162"],
            "FOXP3": ["K31", "E63", "R95", "N106"],
        }
        residues = key_residues.get(target, ["未知"])

        # 氢键网络
        predicted_hbonds = min(compound["hbd"] + compound["hba"], 6)

        return {
            "compound": {
                "id": compound["id"],
                "name": compound["name"],
                "smiles": compound["smiles"],
                "class": compound["class"],
            },
            "target": {
                "name": target_info.get("name", target),
                "pathway": target_info.get("pathway", ""),
                "binding_site": target_info.get("binding_site", ""),
            },
            "binding_energy": binding_energy,
            "binding_energy_unit": "kcal/mol",
            "estimated_ki": round(ki_uM, 3),
            "ki_unit": "μM",
            "predicted_hbonds": predicted_hbonds,
            "key_residues": residues,
            "hydrophobic_contacts": max(1, int((compound["mw"] - 200) / 50)),
            "grade": grade,
            "confidence": round(min(0.95, 0.5 + known_efficacy * 0.4), 3),
            "timestamp": datetime.now().isoformat(),
        }

    # ========== 方法4: ADMET预测 ==========

    def predict_admet(self, compound_name: str = None,
                       compound_id: str = None,
                       mw: float = None, logp: float = None,
                       hbd: int = None, hba: int = None, tpsa: float = None) -> Dict:
        """
        ADMET预测 — 吸收/分布/代谢/排泄/毒性

        Returns:
            五维ADMET评估
        """
        # 获取化合物参数
        if compound_name or compound_id:
            compound = None
            for c in self.compound_library:
                if compound_id and c["id"] == compound_id:
                    compound = c
                    break
                if compound_name and c["name"] == compound_name:
                    compound = c
                    break
            if compound:
                mw = compound["mw"]
                logp = compound["logp"]
                hbd = compound["hbd"]
                hba = compound["hba"]
                tpsa = compound["tpsa"]

        if mw is None:
            return {"error": "需要提供化合物信息或分子参数"}

        # 1. 吸收 (Absorption)
        # 口服生物利用度估算
        bioavailability = 0.5
        if 200 <= mw <= 500:
            bioavailability += 0.15
        if 0 <= logp <= 3:
            bioavailability += 0.10
        if tpsa and tpsa <= 70:
            bioavailability += 0.10
        if hbd <= 2:
            bioavailability += 0.05
        bioavailability = min(bioavailability, 0.95)

        # Caco-2渗透性 (cm/s × 10^-6)
        caco2 = 5.0 + (logp * 2.0) - (tpsa * 0.03 if tpsa else 0)
        caco2 = max(0.5, min(caco2, 30.0))

        # 2. 分布 (Distribution)
        # 血浆蛋白结合率
        ppb = 0.5 + (logp * 0.08)
        ppb = max(0.1, min(ppb, 0.99))

        # 血脑屏障穿透
        bbb = 0.3
        if logp > 2 and (tpsa or 0) < 90 and mw < 450:
            bbb += 0.30
        bbb = min(bbb, 0.85)

        # 表观分布容积 (L/kg)
        vd = 0.5 + (logp * 0.3)
        vd = max(0.3, min(vd, 5.0))

        # 3. 代谢 (Metabolism)
        # CYP450 代谢稳定性
        cyp3a4_substr = 0.5 + (logp * 0.05)
        cyp3a4_substr = max(0.1, min(cyp3a4_substr, 0.95))

        cyp2d6_substr = 0.3 + (hba * 0.03) if hba else 0.3
        cyp2d6_substr = max(0.1, min(cyp2d6_substr, 0.80))

        # 代谢稳定性
        metabolic_stability = 0.5 - (logp * 0.03) + (mw * 0.001)
        metabolic_stability = max(0.1, min(metabolic_stability, 0.90))

        # 4. 排泄 (Excretion)
        # 清除率 (mL/min/kg)
        clearance = 5.0 + (mw * 0.02) - (logp * 0.5)
        clearance = max(1.0, min(clearance, 30.0))

        # 半衰期 (小时)
        half_life = (0.693 * vd * 1000) / clearance
        half_life = round(max(0.5, min(half_life, 48.0)), 2)

        # 5. 毒性 (Toxicity)
        # hERG抑制风险
        herg_risk = 0.3 + (logp * 0.06)
        if mw > 400:
            herg_risk += 0.10
        herg_risk = max(0.05, min(herg_risk, 0.90))

        # 肝毒性风险
        hepatotox = 0.2 + (logp * 0.05)
        if mw > 450:
            hepatotox += 0.08
        hepatotox = max(0.05, min(hepatotox, 0.85))

        # Ames致突变性
        ames_risk = 0.15 + (hba * 0.02) if hba else 0.15
        ames_risk = max(0.05, min(ames_risk, 0.60))

        # 综合安全性
        safety_score = (1 - herg_risk) * 0.3 + (1 - hepatotox) * 0.3 + (1 - ames_risk) * 0.2 + metabolic_stability * 0.2

        return {
            "compound": compound_name or compound_id or "自定义化合物",
            "parameters": {"mw": mw, "logp": logp, "hbd": hbd, "hba": hba, "tpsa": tpsa},
            "absorption": {
                "oral_bioavailability": round(bioavailability, 3),
                "caco2_permeability": round(caco2, 2),
                "caco2_unit": "×10⁻⁶ cm/s",
                "rating": "良好" if bioavailability >= 0.6 else "中等" if bioavailability >= 0.4 else "较差",
            },
            "distribution": {
                "plasma_protein_binding": round(ppb, 3),
                "bbb_penetration": round(bbb, 3),
                "vd": round(vd, 2),
                "vd_unit": "L/kg",
                "rating": "良好" if 0.3 <= vd <= 3.0 else "需关注",
            },
            "metabolism": {
                "cyp3a4_substr": round(cyp3a4_substr, 3),
                "cyp2d6_substr": round(cyp2d6_substr, 3),
                "metabolic_stability": round(metabolic_stability, 3),
                "rating": "稳定" if metabolic_stability >= 0.5 else "不稳定",
            },
            "excretion": {
                "clearance": round(clearance, 2),
                "clearance_unit": "mL/min/kg",
                "half_life": half_life,
                "half_life_unit": "h",
                "rating": "适中" if 2 <= half_life <= 24 else "需调整",
            },
            "toxicity": {
                "herg_inhibition_risk": round(herg_risk, 3),
                "hepatotoxicity_risk": round(hepatotox, 3),
                "ames_mutagenicity": round(ames_risk, 3),
                "safety_score": round(safety_score, 3),
                "rating": "安全" if safety_score >= 0.6 else "需优化" if safety_score >= 0.4 else "高风险",
            },
            "overall_admet_score": round(
                (bioavailability + (1 - abs(ppb - 0.9)) + metabolic_stability +
                 min(1, half_life / 12) + safety_score) / 5, 3
            ),
            "timestamp": datetime.now().isoformat(),
        }

    # ========== 方法5: 药物安全评估 ==========

    def evaluate_drug_safety(self, compound_name: str = None,
                              target: str = "IgE",
                              patient_group: str = "儿童") -> Dict:
        """
        药物安全评估 — 副作用/禁忌/相互作用

        Args:
            compound_name: 化合物名称
            target: 药物靶点
            patient_group: 患者群体(儿童/成人/孕妇/老年)

        Returns:
            安全评估报告
        """
        compound = None
        for c in self.compound_library:
            if c["name"] == compound_name:
                compound = c
                break

        # 靶点相关副作用
        target_aes = {
            "IgE": ["注射部位反应", "上呼吸道感染", "头痛", "过敏反应(罕见)"],
            "IL-4Rα": ["结膜炎", "注射部位反应", "上呼吸道感染", "头痛"],
            "TSLP": ["上呼吸道感染", "注射部位反应", "背痛"],
            "IL-33": ["注射部位反应", "上呼吸道感染", "关节痛"],
            "FOXP3": ["免疫抑制风险", "感染易感性增加", "自身免疫反应"],
            "FcεRI": ["过敏反应风险", "注射部位反应"],
        }

        aes = target_aes.get(target, ["未知"])
        target_info = self.targets.get(target, {})

        # 群体特异性风险
        group_risks = {
            "儿童": {"风险等级": "中", "特殊注意": "生长发育影响需长期监测", "年龄限制": "≥6岁(多数生物制剂)"},
            "成人": {"风险等级": "低", "特殊注意": "常规监测", "年龄限制": "无特殊限制"},
            "孕妇": {"风险等级": "高", "特殊注意": "胎儿安全性数据有限", "年龄限制": "妊娠C类(需权衡利弊)"},
            "老年": {"风险等级": "中", "特殊注意": "药物相互作用风险增加", "年龄限制": "无特殊限制"},
        }
        group_info = group_risks.get(patient_group, group_risks["成人"])

        # 药物相互作用
        interactions = []
        if target in ["IgE", "IL-4Rα"]:
            interactions.append({"drug": "免疫抑制剂", "risk": "协同免疫抑制", "severity": "中"})
        if target == "IgE":
            interactions.append({"drug": "活疫苗", "risk": "疫苗效力降低", "severity": "中"})
        interactions.append({"drug": "抗组胺药", "risk": "协同作用(通常安全)", "severity": "低"})

        # 禁忌症
        contraindications = []
        if target == "FOXP3":
            contraindications.append("活动性感染")
            contraindications.append("严重免疫缺陷")
        if patient_group == "孕妇":
            contraindications.append("妊娠期(除非获益大于风险)")
        contraindications.append("对药物成分过敏")

        # 黑框警告
        boxed_warning = None
        if target in ["FOXP3", "FcεRI"]:
            boxed_warning = "免疫抑制相关严重感染风险"

        # 安全性综合评分
        safety_base = 0.7
        if group_info["风险等级"] == "高":
            safety_base -= 0.2
        elif group_info["风险等级"] == "中":
            safety_base -= 0.1
        if boxed_warning:
            safety_base -= 0.1
        if len(contraindications) > 2:
            safety_base -= 0.05

        return {
            "compound": compound_name or "未指定",
            "compound_info": {"class": compound["class"], "mw": compound["mw"]} if compound else None,
            "target": target,
            "target_info": {"name": target_info.get("name", target), "drug_class": target_info.get("drug_class", "")},
            "patient_group": patient_group,
            "adverse_events": aes,
            "group_specific_risk": group_info,
            "drug_interactions": interactions,
            "contraindications": contraindications,
            "boxed_warning": boxed_warning,
            "safety_score": round(max(0.1, safety_base), 3),
            "recommendation": "可推进临床" if safety_base >= 0.6 else "需优化方案" if safety_base >= 0.45 else "风险较高需重新评估",
            "monitoring_plan": [
                "用药前基线检查(血常规/肝肾功能/IgE水平)",
                "首次用药后观察30分钟(过敏反应)",
                "定期随访(每4周)评估疗效和安全性",
                "长期安全性追踪(≥1年)",
            ],
            "timestamp": datetime.now().isoformat(),
        }

    # ========== 方法6: 临床试验设计 ==========

    def design_clinical_trial(self, target: str = "IgE",
                               phase: str = "II",
                               allergen: str = "花生",
                               patient_count: int = 100,
                               duration_weeks: int = 24) -> Dict:
        """
        临床试验设计 — I/II/III期方案生成

        Args:
            target: 药物靶点
            phase: 临床阶段(I/II/III)
            allergen: 目标过敏原
            patient_count: 患者数量
            duration_weeks: 试验周期(周)

        Returns:
            临床试验方案
        """
        # 阶段配置
        phase_config = {
            "I": {
                "name": "I期临床",
                "purpose": "安全性与耐受性",
                "sample_size_range": "20-80",
                "design": "开放标签剂量递增",
                "primary_endpoint": "最大耐受剂量(MTD) + 安全性",
                "duration": "8-12周",
            },
            "II": {
                "name": "II期临床",
                "purpose": "有效性与剂量探索",
                "sample_size_range": "100-300",
                "design": "随机双盲安慰剂对照",
                "primary_endpoint": "口服食物激发试验(OFC)耐受剂量提升",
                "duration": "16-28周",
            },
            "III": {
                "name": "III期临床",
                "purpose": "确证有效性+大规模安全性",
                "sample_size_range": "300-1000",
                "design": "随机双盲安慰剂对照多中心",
                "primary_endpoint": "OFC通过率(主要)+生活质量评分(次要)",
                "duration": "24-52周",
            },
        }
        config = phase_config.get(phase, phase_config["II"])

        # 入排标准
        inclusion = [
            f"确诊{allergen}过敏(皮肤点刺试验阳性+特异性IgE升高)",
            "年龄6-55岁" if phase != "I" else "年龄18-55岁",
            f"双盲安慰剂对照食物激发试验(DBPCFC)确认{allergen}过敏",
            "理解并签署知情同意书",
        ]
        exclusion = [
            "严重不受控的哮喘",
            "活动性自身免疫性疾病",
            "严重心血管疾病",
            "妊娠或哺乳期",
            "免疫抑制治疗中",
            f"对试验药物成分过敏",
        ]

        # 随机化方案
        if phase == "I":
            randomization = "3:1开放标签(低/中/高剂量:安慰剂)"
            arms = ["低剂量组", "中剂量组", "高剂量组", "安慰剂组"]
            arm_ratio = [3, 3, 3, 1]
        elif phase == "II":
            randomization = "1:1:1双盲(低剂量:高剂量:安慰剂)"
            arms = ["低剂量组", "高剂量组", "安慰剂组"]
            arm_ratio = [1, 1, 1]
        else:
            randomization = "2:1双盲(试验药:安慰剂)"
            arms = ["试验药组", "安慰剂组"]
            arm_ratio = [2, 1]

        # 分组
        total_ratio = sum(arm_ratio)
        arm_sizes = [int(patient_count * r / total_ratio) for r in arm_ratio]

        # 评估时间点
        timepoints = ["基线(第0周)"]
        if duration_weeks >= 12:
            timepoints.extend(["第4周", "第8周", "第12周"])
        if duration_weeks >= 24:
            timepoints.extend(["第16周", "第24周"])
        if duration_weeks >= 36:
            timepoints.append("第36周")
        timepoints.append(f"第{duration_weeks}周(终点)")

        # 终点指标
        primary_endpoints = [config["primary_endpoint"]]
        secondary_endpoints = [
            f"{allergen}特异性IgE/IgG4比值变化",
            "皮肤点刺试验风团直径变化",
            "生活质量问卷(FAQLQ)评分改善",
            "不良事件发生率",
            "应急肾上腺素使用次数",
        ]

        # 统计方法
        stat_methods = []
        if phase == "I":
            stat_methods = ["描述性统计", "剂量限制性毒性(DLT)评估", "MTD确定"]
        elif phase == "II":
            stat_methods = ["Fisher精确检验(主要终点)", "ANOVA(剂量-反应)", "Logistic回归(亚组分析)"]
        else:
            stat_methods = ["Cochran-Mantel-Haenszel检验", "Kaplan-Meier(脱敏维持)", "协方差分析(ANCOVA)"]

        # 样本量估算
        if phase == "II":
            # 基于有效率和检验效能
            expected_effect = self.targets.get(target, {}).get("efficacy", 0.6)
            alpha = 0.05
            power = 0.80
            # 简化的样本量估算
            z_alpha = 1.96
            z_beta = 0.84
            p1 = expected_effect
            p0 = 0.30  # 安慰剂有效率
            n_per_arm = int(((z_alpha + z_beta) ** 2 * (p1 * (1 - p1) + p0 * (1 - p0))) / (p1 - p0) ** 2)
            sample_justification = f"基于预期有效率{p1:.0%} vs 安慰剂{p0:.0%}，α={alpha}，功效={power:.0%}，每组需≈{n_per_arm}例"
        else:
            n_per_arm = patient_count // len(arms)
            sample_justification = f"基于{phase}期临床要求，每组≈{n_per_arm}例"

        return {
            "trial_id": f"FA-{target}-{phase}-{datetime.now().strftime('%Y%m%d')}",
            "phase": phase,
            "phase_info": config,
            "target": target,
            "allergen": allergen,
            "design": {
                "type": config["design"],
                "randomization": randomization,
                "arms": [{"name": a, "size": s} for a, s in zip(arms, arm_sizes)],
                "blinding": "双盲" if phase != "I" else "开放",
            },
            "patient_count": patient_count,
            "duration_weeks": duration_weeks,
            "inclusion_criteria": inclusion,
            "exclusion_criteria": exclusion,
            "timepoints": timepoints,
            "endpoints": {
                "primary": primary_endpoints,
                "secondary": secondary_endpoints,
            },
            "statistical_methods": stat_methods,
            "sample_size_justification": sample_justification,
            "estimated_n_per_arm": n_per_arm,
            "safety_monitoring": [
                "数据安全监察委员会(DSMB)独立审查",
                "预设停止规则(严重AE发生率>15%)",
                "中期分析(完成50%入组时)",
            ],
            "regulatory_pathway": "FDA突破性疗法(如适用) / NMPA优先审评",
            "timestamp": datetime.now().isoformat(),
        }

    # ========== 方法7: 食物过敏通路分析 ==========

    def food_allergy_pathway_analysis(self, allergen: str = "花生") -> Dict:
        """
        食物过敏通路分析 — IgE通路/Th2免疫/口服耐受全景

        Args:
            allergen: 过敏原

        Returns:
            通路分析报告
        """
        allergen_info = self.allergens.get(allergen, {})

        # 三大通路
        pathways = {
            "IgE介导通路": {
                "description": "速发型过敏反应(分钟级)",
                "steps": [
                    "1. 过敏原经肠道/皮肤进入→被DC摄取",
                    "2. DC将抗原提呈给Th2细胞→Th2活化",
                    "3. Th2分泌IL-4/IL-13→B细胞IgE类别转换",
                    "4. 特异性IgE结合肥大细胞/嗜碱性粒细胞FcεRI",
                    "5. 再次接触过敏原→IgE交联→脱颗粒",
                    "6. 组胺/白三烯/前列腺素释放→症状",
                ],
                "key_molecules": ["IgE", "FcεRI", "肥大细胞类胰蛋白酶", "组胺"],
                "intervention_points": ["阻断IgE产生", "阻断IgE-FcεRI结合", "抑制脱颗粒"],
                "timeline": "数分钟-2小时",
            },
            "Th2型免疫通路": {
                "description": "慢性过敏炎症(小时-天级)",
                "steps": [
                    "1. 上皮细胞释放TSLP/IL-33/IL-25",
                    "2. 激活ILC2→分泌IL-5/IL-13",
                    "3. 招募嗜酸性粒细胞→组织炎症",
                    "4. Th2细胞扩增→IL-4/IL-13→杯状细胞增生",
                    "5. 黏液过度分泌+组织重塑",
                    "6. 慢性炎症→过敏阈值降低",
                ],
                "key_molecules": ["TSLP", "IL-33", "ILC2", "IL-5", "IL-13", "嗜酸性粒细胞"],
                "intervention_points": ["阻断TSLP", "中和IL-33", "阻断IL-4Rα", "清除嗜酸性粒细胞"],
                "timeline": "数小时-数天",
            },
            "口服免疫耐受通路": {
                "description": "免疫调节与耐受诱导(天-周级)",
                "steps": [
                    "1. 肠道相关淋巴组织(GALT)识别无害抗原",
                    "2. CD103+ DC诱导Treg分化",
                    "3. Treg分泌IL-10/TGF-β→免疫抑制",
                    "4. FOXP3+ Treg维持外周耐受",
                    "5. 口服耐受破坏→过敏致敏",
                    "6. 恢复Treg功能→脱敏",
                ],
                "key_molecules": ["CD103+ DC", "FOXP3", "IL-10", "TGF-β", "Retinoic Acid"],
                "intervention_points": ["增强Treg功能", "促进CD103+ DC", "低剂量IL-2疗法", "微生物组调节"],
                "timeline": "数天-数周",
            },
        }

        # 过敏原特征
        allergen_proteins = allergen_info.get("major_allergens", [])

        # 推荐联合策略
        combination_strategies = [
            {
                "strategy": "抗IgE + 口服免疫疗法(OIT)",
                "rationale": "抗IgE降低过敏阈值→OIT安全递增剂量→诱导耐受",
                "evidence": "已有多项II期临床试验验证",
                "expected_synergy": 0.80,
            },
            {
                "strategy": "抗IL-4Rα + 益生菌",
                "rationale": "阻断Th2通路 + 调节肠道微生物组→增强口服耐受",
                "evidence": "概念验证阶段",
                "expected_synergy": 0.65,
            },
            {
                "strategy": "抗TSLP + 抗IgE",
                "rationale": "上游阻断上皮警报素 + 下游阻断IgE效应→双重阻断",
                "evidence": "临床前数据支持",
                "expected_synergy": 0.72,
            },
        ]

        return {
            "allergen": allergen,
            "allergen_info": allergen_info,
            "pathways": pathways,
            "allergen_proteins": allergen_proteins,
            "combination_strategies": combination_strategies,
            "recommended_approach": combination_strategies[0]["strategy"],
            "analysis_timestamp": datetime.now().isoformat(),
        }

    # ========== 方法8: 免疫疗法设计 ==========

    def design_immunotherapy(self, allergen: str = "花生",
                              method: str = "OIT",
                              patient_age: int = 8,
                              severity: str = "中度") -> Dict:
        """
        免疫疗法方案设计 — OIT/SLIT/EPIT

        Args:
            allergen: 过敏原
            method: 方法(OIT口服/SLIT舌下/EPIT经皮/生物制剂联合)
            patient_age: 患者年龄
            severity: 过敏严重程度

        Returns:
            免疫疗法方案
        """
        method_config = {
            "OIT": {
                "name": "口服免疫疗法",
                "full_name": "Oral Immunotherapy",
                "route": "口服",
                "mechanism": "逐步递增过敏原口服剂量→诱导免疫耐受",
                "advantages": ["疗效最确切", "可达到维持剂量", "FDA已批准(花生Palforzia)"],
                "disadvantages": ["副作用较多(口腔痒/腹痛)", "需要严格依从性", "回避期风险"],
                "approved": "FDA批准花生OIT(Palforzia)",
            },
            "SLIT": {
                "name": "舌下免疫疗法",
                "full_name": "Sublingual Immunotherapy",
                "route": "舌下含服",
                "mechanism": "舌下黏膜吸收→局部免疫调节→系统性耐受",
                "advantages": ["安全性较好", "给药方便", "儿童接受度高"],
                "disadvantages": ["疗效弱于OIT", "需要长期维持", "数据有限"],
                "approved": "研究阶段(食物过敏)",
            },
            "EPIT": {
                "name": "经皮免疫疗法",
                "full_name": "Epicutaneous Immunotherapy",
                "route": "皮肤贴片",
                "mechanism": "通过皮肤递送过敏原→LC提呈→免疫耐受",
                "advantages": ["无创无痛", "幼儿友好", "安全性最佳"],
                "disadvantages": ["疗效最弱", "局部皮肤反应", "需长时间贴敷"],
                "approved": "III期进行中(花生DBV712)",
            },
            "生物制剂联合": {
                "name": "生物制剂+OIT联合",
                "full_name": "Biologic + OIT Combination",
                "route": "注射+口服",
                "mechanism": "抗IgE/抗IL-4Rα降低阈值→OIT安全递增→协同耐受",
                "advantages": ["降低OIT副作用", "提高安全性", "可能缩短疗程"],
                "disadvantages": ["成本高", "需注射给药", "联合方案复杂"],
                "approved": "II/III期临床进行中",
            },
        }
        config = method_config.get(method, method_config["OIT"])

        allergen_info = self.allergens.get(allergen, {})

        # 剂量方案 (以花生蛋白为例, mg)
        if method == "OIT":
            protocol = {
                "初始日剂量": "0.5 mg 蛋白",
                "递增期": "每2周递增, 1mg→5mg→15mg→50mg→100mg→300mg",
                "维持剂量": "300 mg 蛋白/日",
                "维持期": "≥2年(建议3-5年)",
                "总疗程": "约3-5年",
            }
        elif method == "SLIT":
            protocol = {
                "初始日剂量": "0.05 mg 蛋白",
                "递增期": "每周递增, 0.05→0.1→0.5→1→2→5 mg",
                "维持剂量": "5-7 mg 蛋白/日",
                "维持期": "≥3年",
                "总疗程": "约3-5年",
            }
        elif method == "EPIT":
            protocol = {
                "初始剂量": "100 μg 蛋白贴片",
                "递增期": "24小时贴敷→48小时贴敷(逐渐延长)",
                "维持剂量": "250 μg 蛋白贴片/48h",
                "维持期": "≥2年",
                "总疗程": "约2-3年",
            }
        else:  # 生物制剂联合
            protocol = {
                "预处理": "抗IgE(奥马珠单抗) 150-375mg q2-4周 × 8周",
                "OIT启动": "预处理后启动标准OIT方案",
                "联合维持": "抗IgE + OIT 300mg/日 维持6-12月",
                "脱联合": "逐步停用抗IgE, 继续OIT维持",
                "总疗程": "约2-3年",
            }

        # 安全性考量
        safety = {
            "OIT": {"主要风险": "口腔过敏综合征(60%)", "严重AE": "过敏反应(约2-8%/年)", "禁忌": "不受控哮喘"},
            "SLIT": {"主要风险": "口腔痒(30%)", "严重AE": "罕见(<1%)", "禁忌": "严重口腔炎症"},
            "EPIT": {"主要风险": "局部红斑(80%)", "严重AE": "极罕见", "禁忌": "严重湿疹"},
            "生物制剂联合": {"主要风险": "注射反应", "严重AE": "过敏反应(罕见)", "禁忌": "活动性感染"},
        }

        # 年龄适配
        age_recommendation = "适合" if patient_age >= 4 else "需谨慎评估(幼儿)"
        if method == "OIT" and patient_age < 1:
            age_recommendation = "不建议(1岁以下)"
        if method == "EPIT":
            age_recommendation = "非常适合(婴幼儿首选)" if patient_age <= 5 else "适合"

        # 严重程度适配
        severity_match = True
        if severity == "重度" and method == "OIT":
            severity_match = False  # 重度过敏OIT风险高

        # 疗效预期
        efficacy_map = {"OIT": 0.70, "SLIT": 0.50, "EPIT": 0.40, "生物制剂联合": 0.82}
        expected_efficacy = efficacy_map.get(method, 0.6)
        if not severity_match:
            expected_efficacy -= 0.15

        return {
            "allergen": allergen,
            "allergen_info": allergen_info,
            "method": method,
            "method_info": config,
            "patient_age": patient_age,
            "severity": severity,
            "age_recommendation": age_recommendation,
            "severity_match": "匹配" if severity_match else "需调整(重度过敏建议先用生物制剂降阈值)",
            "protocol": protocol,
            "safety_profile": safety.get(method, {}),
            "expected_efficacy": round(expected_efficacy, 3),
            "monitoring": [
                "每次剂量递增后观察60分钟",
                "每日记录症状日记",
                "每月门诊随访+IgE/IgG4监测",
                "每3-6月评估OFC耐受剂量",
                "应急肾上腺素自动注射器随身携带",
            ],
            "success_criteria": [
                f"OFC耐受{allergen}蛋白≥300mg(脱敏成功)",
                "IgG4升高≥2倍基线(免疫耐受标志)",
                "无中重度过敏反应(安全性达标)",
            ],
            "timestamp": datetime.now().isoformat(),
        }

    # ========== 题库加载 ==========

    def get_problems(self, phase: str = None, problem_type: str = None,
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        """获取题目"""
        problems = []
        phases_to_check = [phase] if phase else list(self.phases.keys())
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]['problems']:
                if problem_type and prob.get('type') != problem_type:
                    continue
                if difficulty and prob.get('difficulty') != difficulty:
                    continue
                problems.append(prob)
        return problems[:limit]

    def get_all_targets(self) -> Dict:
        """获取所有靶点信息"""
        return self.targets

    def get_all_allergens(self) -> Dict:
        """获取所有过敏原信息"""
        return self.allergens

    def get_compound_library(self) -> List[Dict]:
        """获取化合物库"""
        return self.compound_library


# ========== 演示 ==========

if __name__ == '__main__':
    engine = DrugDiscoveryEngine()

    print("=" * 60)
    print("🦞 小龙虾网络 - 新药创制科学智能体引擎 V1.0")
    print("   聚焦：食物过敏防治药物研制")
    print("=" * 60)

    # 1. 靶点识别
    print("\n🎯 [1/8] 靶点识别:")
    target = engine.identify_drug_target(allergen="花生", pathway="IgE")
    print(f"   过敏原: {target['allergen']} (严重性: {target['allergen_info'].get('severity', '?')})")
    print(f"   靶点: {target['target_info']['name']} ({target['target_info']['drug_class']})")
    print(f"   机制: {target['target_info']['mechanism'][:50]}...")
    print(f"   综合评分: {target['overall_score']:.3f} → {target['recommendation']}")
    for k, v in target['scores'].items():
        print(f"     {k}: {v:.3f}")

    # 2. 先导化合物筛选
    print("\n🔍 [2/8] 先导化合物筛选:")
    screening = engine.screen_lead_compounds(target="IgE", max_results=3)
    print(f"   筛选: {screening['total_screened']}个化合物 → {screening['total_passed']}个通过 ({screening['pass_rate']:.0%})")
    for c in screening['top_compounds']:
        print(f"   {c['compound_id']} {c['name']}: 类药性={c['drug_likeness_score']:.3f}, MW={c['mw']}, logP={c['logp']}")

    # 3. 分子对接
    print("\n🧬 [3/8] 分子对接评分:")
    docking = engine.molecular_docking_score(compound_name="龙虾素-A", target="IgE")
    print(f"   化合物: {docking['compound']['name']} → 靶点: {docking['target']['name']}")
    print(f"   结合自由能: {docking['binding_energy']} {docking['binding_energy_unit']}")
    print(f"   估算Ki: {docking['estimated_ki']} {docking['ki_unit']}")
    print(f"   评级: {docking['grade']}")
    print(f"   关键残基: {', '.join(docking['key_residues'])}")

    # 4. ADMET预测
    print("\n💊 [4/8] ADMET预测:")
    admet = engine.predict_admet(compound_name="龙虾素-A")
    print(f"   口服生物利用度: {admet['absorption']['oral_bioavailability']:.1%} ({admet['absorption']['rating']})")
    print(f"   血浆蛋白结合: {admet['distribution']['plasma_protein_binding']:.1%}")
    print(f"   代谢稳定性: {admet['metabolism']['metabolic_stability']:.1%} ({admet['metabolism']['rating']})")
    print(f"   半衰期: {admet['excretion']['half_life']}h ({admet['excretion']['rating']})")
    print(f"   安全性评分: {admet['toxicity']['safety_score']:.1%} ({admet['toxicity']['rating']})")
    print(f"   ADMET综合: {admet['overall_admet_score']:.3f}")

    # 5. 药物安全评估
    print("\n🛡️ [5/8] 药物安全评估:")
    safety = engine.evaluate_drug_safety(compound_name="龙虾素-A", target="IgE", patient_group="儿童")
    print(f"   患者群体: {safety['patient_group']} (风险: {safety['group_specific_risk']['风险等级']})")
    print(f"   不良事件: {', '.join(safety['adverse_events'][:3])}...")
    print(f"   安全评分: {safety['safety_score']:.3f} → {safety['recommendation']}")

    # 6. 临床试验设计
    print("\n🏥 [6/8] 临床试验设计:")
    trial = engine.design_clinical_trial(target="IgE", phase="II", allergen="花生", patient_count=120, duration_weeks=24)
    print(f"   试验ID: {trial['trial_id']}")
    print(f"   阶段: {trial['phase_info']['name']} - {trial['phase_info']['purpose']}")
    print(f"   设计: {trial['design']['type']}")
    print(f"   分组: {trial['design']['randomization']}")
    print(f"   主要终点: {trial['endpoints']['primary'][0]}")
    print(f"   样本量: {trial['patient_count']}例 (每组≈{trial['estimated_n_per_arm']}例)")

    # 7. 食物过敏通路分析
    print("\n🧠 [7/8] 食物过敏通路分析:")
    pathway = engine.food_allergy_pathway_analysis(allergen="花生")
    for pname, pdata in pathway['pathways'].items():
        print(f"   [{pname}] {pdata['description']} (时间: {pdata['timeline']})")
    print(f"   推荐联合策略: {pathway['recommended_approach']}")

    # 8. 免疫疗法设计
    print("\n💉 [8/8] 免疫疗法设计:")
    immuno = engine.design_immunotherapy(allergen="花生", method="OIT", patient_age=8, severity="中度")
    print(f"   方法: {immuno['method_info']['name']} ({immuno['method_info']['full_name']})")
    print(f"   维持剂量: {immuno['protocol']['维持剂量']}")
    print(f"   预期疗效: {immuno['expected_efficacy']:.1%}")
    print(f"   年龄适配: {immuno['age_recommendation']}")

    # 题库统计
    print("\n📚 题库统计:")
    total = 0
    for phase, data in engine.phases.items():
        count = len(data['problems'])
        total += count
        print(f"   {phase}: {data['name']} - {count} 题")
    print(f"   合计: {total} 题")

    print("\n" + "=" * 60)
    print("✅ 新药创制科学智能体引擎测试完成！")
