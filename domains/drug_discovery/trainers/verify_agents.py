#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_agents.py - 食物过敏药物发现智能体验证脚本

功能：
- 测试每个智能体的核心功能
- 运行迷你药物发现流水线
- 生成验证报告（pass/fail）

用法：
    python verify_agents.py --all           # 验证所有智能体
    python verify_agents.py --agent target  # 只验证靶点智能体
    python verify_agents.py --pipeline      # 运行迷你流水线
"""

import argparse
import json
import logging
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


# ============================================================
# 路径设置 — 支持从 trainers/ 目录直接运行
# ============================================================

_DOMAIN_DIR = Path(__file__).resolve().parent.parent
if str(_DOMAIN_DIR) not in sys.path:
    sys.path.insert(0, str(_DOMAIN_DIR))

_AGENTS_DIR = _DOMAIN_DIR / "agents"
if str(_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_DIR))


# ============================================================
# 日志
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("verify_agents")


# ============================================================
# 验证结果模型
# ============================================================

class VerificationResult:
    """单项验证结果"""
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error = ""
        self.duration_s = 0.0
        self.details: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "error": self.error,
            "duration_s": round(self.duration_s, 3),
            "details": self.details,
        }


# ============================================================
# 各智能体验证函数
# ============================================================

def verify_allergen_target() -> VerificationResult:
    """验证 AllergenTargetAgent"""
    vr = VerificationResult("AllergenTargetAgent")
    start = time.time()
    try:
        from agents.allergen_target_agent import AllergenTargetAgent
        agent = AllergenTargetAgent()

        # 1. 靶点发现
        discovery = agent.discover_targets()
        assert "high_priority_allergens" in discovery, "缺少 high_priority_allergens"
        assert len(discovery["high_priority_allergens"]) > 0, "无高优先级过敏原"

        # 2. 靶点验证
        validation = agent.validate_target("FCE_RI")
        assert validation["target_id"] == "FCE_RI", "靶点 ID 不匹配"
        assert "validation" in validation, "缺少验证结果"
        assert validation["validation"]["overall_score"] > 0, "验证分数异常"

        # 3. 假说生成
        hyp = agent.generate_hypothesis(validation)
        assert hyp.hypothesis_id.startswith("HYP_"), "假说 ID 格式错误"
        assert hyp.confidence > 0, "置信度异常"

        # 4. 能力列表
        caps = agent.get_capabilities()
        assert len(caps) >= 5, "能力列表过短"

        vr.passed = True
        vr.details = {
            "allergens": discovery["total_allergens"],
            "targets": discovery["total_targets"],
            "hypothesis_id": hyp.hypothesis_id,
            "capabilities": len(caps),
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


def verify_compound_design() -> VerificationResult:
    """验证 CompoundDesignAgent"""
    vr = VerificationResult("CompoundDesignAgent")
    start = time.time()
    try:
        from agents.compound_design_agent import CompoundDesignAgent
        agent = CompoundDesignAgent()

        target = {"target_id": "FCE_RI", "target_name": "FcepsilonRI"}

        # 1. 化合物设计
        design = agent.design_compound(target, "fcepsilonri_antagonist")
        assert "compound_id" in design, "缺少 compound_id"
        assert design["properties"]["MW"] > 0, "MW 异常"

        # 2. 先导优化
        opt = agent.optimize_lead(design["compound_id"])
        assert "optimization" in opt, "缺少优化结果"

        # 3. 类似物生成
        analogs = agent.generate_analogs(design["compound_id"], n=5)
        assert analogs["n_analogs"] == 5, f"类似物数量错误: {analogs['n_analogs']}"

        # 4. 能力列表
        caps = agent.get_capabilities()
        assert len(caps) >= 4, "能力列表过短"

        vr.passed = True
        vr.details = {
            "compound_id": design["compound_id"],
            "MW": design["properties"]["MW"],
            "n_analogs": analogs["n_analogs"],
            "capabilities": len(caps),
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


def verify_virtual_screening() -> VerificationResult:
    """验证 VirtualScreeningAgent"""
    vr = VerificationResult("VirtualScreeningAgent")
    start = time.time()
    try:
        from agents.virtual_screening_agent import VirtualScreeningAgent
        agent = VirtualScreeningAgent()

        target = {"target_id": "FCE_RI", "target_name": "FcepsilonRI"}

        # 1. 虚拟筛选
        screen = agent.screen_library(target, library_size=500)
        assert screen["library_size"] == 500, "库大小不匹配"
        assert len(screen["top_10"]) > 0, "无 top 10 结果"

        # 2. 对接
        dock = agent.dock("CPD_TEST_001", target)
        assert "best_pose" in dock, "缺少对接结果"

        # 3. 排序
        ranked = agent.rank_hits(top_n=20)
        assert "ranked_hits" in ranked, "缺少排序结果"

        vr.passed = True
        vr.details = {
            "library_size": screen["library_size"],
            "hit_rate": screen["screening_stats"]["hit_rate"],
            "top_score": screen["top_10"][0]["binding_score"],
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


def verify_admet() -> VerificationResult:
    """验证 AdmetPredictionAgent"""
    vr = VerificationResult("AdmetPredictionAgent")
    start = time.time()
    try:
        from agents.admet_agent import AdmetPredictionAgent
        agent = AdmetPredictionAgent()

        props = {"MW": 380.4, "LogP": 2.8, "HBD": 2, "HBA": 6, "TPSA": 78.5}

        # 1. ADMET 预测
        result = agent.predict_admet("CPD_TEST_001", props)
        assert "absorption" in result, "缺少吸收预测"
        assert "metabolism" in result, "缺少代谢预测"
        assert "toxicity" in result, "缺少毒性预测"
        assert "drug_likeness" in result, "缺少类药性"

        # 2. Lipinski 检查
        assert result["drug_likeness"]["lipinski_pass"] is True, "Lipinski 应通过"

        # 3. 过滤功能
        compounds = [
            {"compound_id": "A", "MW": 350, "LogP": 2.5, "HBD": 2, "HBA": 5, "TPSA": 70},
            {"compound_id": "B", "MW": 600, "LogP": 6.0, "HBD": 8, "HBA": 15, "TPSA": 180},
        ]
        filter_result = agent.filter_drug_likeness(compounds)
        assert filter_result["passed"] == 1, f"应有 1 个通过，实际 {filter_result['passed']}"

        vr.passed = True
        vr.details = {
            "oral_bioavailability": result["absorption"]["oral_bioavailability_pct"],
            "lipinski_pass": result["drug_likeness"]["lipinski_pass"],
            "herg_risk": result["toxicity"]["herg_risk_level"],
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


def verify_toxicity() -> VerificationResult:
    """验证 ToxicityAssessmentAgent"""
    vr = VerificationResult("ToxicityAssessmentAgent")
    start = time.time()
    try:
        from agents.toxicity_agent import ToxicityAssessmentAgent
        agent = ToxicityAssessmentAgent()

        props = {"MW": 380.4, "LogP": 2.8, "HBD": 2, "HBA": 6, "TPSA": 78.5}

        # 1. 综合评估
        result = agent.assess_toxicity("CPD_TEST_001", props)
        assert "herg_assessment" in result, "缺少 hERG"
        assert "acute_toxicity" in result, "缺少急性毒性"
        assert "off_target_profile" in result, "缺少脱靶"
        assert result["overall_safety_score"] >= 0, "安全评分异常"

        # 2. 安全报告
        report = agent.safety_report("CPD_TEST_001")
        assert "key_findings" in report, "缺少关键发现"
        assert "recommendations" in report, "缺少建议"

        vr.passed = True
        vr.details = {
            "safety_grade": result["safety_grade"],
            "safety_score": result["overall_safety_score"],
            "herg_level": result["herg_assessment"]["herg_risk_level"],
            "off_target_high_risk": result["off_target_profile"]["n_high_risk"],
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


def verify_literature_mining() -> VerificationResult:
    """验证 LiteratureMiningAgent"""
    vr = VerificationResult("LiteratureMiningAgent")
    start = time.time()
    try:
        from agents.literature_mining_agent import LiteratureMiningAgent
        agent = LiteratureMiningAgent()

        # 1. 搜索
        search = agent.search_papers("food allergy IgE", max_results=5)
        assert search["returned"] > 0, "无搜索结果"

        # 2. 提取靶点
        targets = agent.extract_targets(search["papers"])
        assert targets["n_unique_targets"] > 0, "无提取靶点"

        # 3. 提取化合物
        compounds = agent.extract_compounds(search["papers"])
        assert compounds["n_unique_compounds"] > 0, "无提取化合物"

        # 4. 趋势分析
        trends = agent.trend_analysis("food allergy")
        assert "yearly_publications" in trends, "缺少年度发文量"

        # 5. 综述生成
        review = agent.generate_review("food allergy treatment")
        assert len(review["review_sections"]) >= 3, "综述段落过少"

        vr.passed = True
        vr.details = {
            "papers_found": search["returned"],
            "targets_extracted": targets["n_unique_targets"],
            "compounds_extracted": compounds["n_unique_compounds"],
            "review_sections": len(review["review_sections"]),
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


def verify_mini_pipeline() -> VerificationResult:
    """验证迷你流水线（全链路）"""
    vr = VerificationResult("MiniPipeline")
    start = time.time()
    try:
        from workflows.drug_discovery_pipeline import DrugDiscoveryPipeline
        pipeline = DrugDiscoveryPipeline()

        report = pipeline.run_pipeline("food allergy drug discovery")

        assert "key_findings" in report, "缺少关键发现"
        assert "candidate_compound" in report, "缺少候选化合物"
        assert "stage_summary" in report, "缺少阶段汇总"
        assert len(report["stage_summary"]) == 6, f"阶段数错误: {len(report['stage_summary'])}"
        assert all(s["status"] == "completed" for s in report["stage_summary"]), "存在未完成阶段"

        vr.passed = True
        vr.details = {
            "total_time_s": report["total_execution_time_s"],
            "key_findings_count": len(report["key_findings"]),
            "candidate": report["candidate_compound"].get("compound_id", "N/A"),
            "all_stages_completed": True,
        }
    except Exception as e:
        vr.error = str(e)
        logger.error(f"[{vr.name}] 验证失败: {e}\n{traceback.format_exc()}")
    finally:
        vr.duration_s = time.time() - start
    return vr


# ============================================================
# 验证调度
# ============================================================

AGENT_VERIFIERS = {
    "target": verify_allergen_target,
    "compound": verify_compound_design,
    "screening": verify_virtual_screening,
    "admet": verify_admet,
    "toxicity": verify_toxicity,
    "literature": verify_literature_mining,
}


def run_all_verifications() -> List[VerificationResult]:
    """运行所有智能体验证"""
    results = []
    for name, verifier in AGENT_VERIFIERS.items():
        logger.info(f"验证: {name}...")
        results.append(verifier())
    return results


def run_pipeline_verification() -> VerificationResult:
    """运行流水线验证"""
    return verify_mini_pipeline()


# ============================================================
# 报告生成
# ============================================================

def print_report(results: List[VerificationResult]):
    """打印验证报告"""
    print(f"\n{'='*60}")
    print(f"  食物过敏药物发现智能体 — 验证报告")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    print(f"\n  总计: {total} | 通过: {passed} | 失败: {failed}")
    print(f"  通过率: {passed/total*100:.1f}%")

    print(f"\n{'─'*60}")
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        icon = "[+]" if r.passed else "[-]"
        print(f"  {icon} {status:4s} | {r.name:30s} | {r.duration_s:.3f}s")
        if r.error:
            print(f"         Error: {r.error[:80]}")
        if r.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in r.details.items())
            print(f"         {detail_str[:80]}")

    print(f"{'─'*60}")

    if failed == 0:
        print(f"\n  ALL VERIFICATIONS PASSED")
    else:
        print(f"\n  {failed} VERIFICATION(S) FAILED — see errors above")

    print(f"\n{'='*60}\n")


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="食物过敏药物发现智能体验证工具"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="验证所有智能体",
    )
    parser.add_argument(
        "--agent", type=str,
        choices=list(AGENT_VERIFIERS.keys()),
        help="验证指定智能体",
    )
    parser.add_argument(
        "--pipeline", action="store_true",
        help="运行迷你流水线验证",
    )

    args = parser.parse_args()

    results: List[VerificationResult] = []

    if args.agent:
        verifier = AGENT_VERIFIERS[args.agent]
        results.append(verifier())
    elif args.pipeline:
        results.append(run_pipeline_verification())
    else:
        # 默认运行所有验证 + 流水线
        results = run_all_verifications()
        results.append(run_pipeline_verification())

    print_report(results)

    # 退出码
    all_passed = all(r.passed for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
