#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrugDiscoveryPipeline - 食物过敏药物发现全流程编排引擎

流水线阶段：
1. 靶点识别 (AllergenTargetAgent)
2. 文献综述 (LiteratureMiningAgent)
3. 化合物设计 (CompoundDesignAgent)
4. 虚拟筛选 (VirtualScreeningAgent)
5. ADMET 预测 (AdmetPredictionAgent)
6. 毒性评估 (ToxicityAssessmentAgent)

输出：
- 结构化研究报告（JSON）
- 各阶段结果汇总
- 候选化合物优先级排序
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


# ============================================================
# 日志配置
# ============================================================

logger = logging.getLogger("drug_discovery_pipeline")
logger.setLevel(logging.INFO)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

if not logger.handlers:
    _handler = logging.FileHandler(_LOG_DIR / "pipeline.log", encoding="utf-8")
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


# ============================================================
# 流水线状态
# ============================================================

class PipelineStage(str, Enum):
    TARGET_ID = "target_identification"
    LITERATURE = "literature_review"
    COMPOUND_DESIGN = "compound_design"
    VIRTUAL_SCREENING = "virtual_screening"
    ADMET = "admet_prediction"
    TOXICITY = "toxicity_assessment"


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ============================================================
# DrugDiscoveryPipeline 主类
# ============================================================

class DrugDiscoveryPipeline:
    """
    食物过敏药物发现全流程编排引擎

    编排 6 个专业智能体，依次执行：
    靶点识别 → 文献综述 → 化合物设计 → 虚拟筛选 → ADMET 预测 → 毒性评估

    用法:
        pipeline = DrugDiscoveryPipeline()
        report = pipeline.run_pipeline("food allergy drug discovery")
    """

    PIPELINE_NAME = "DrugDiscoveryPipeline"
    PIPELINE_VERSION = "1.0.0"

    STAGE_ORDER = [
        PipelineStage.TARGET_ID,
        PipelineStage.LITERATURE,
        PipelineStage.COMPOUND_DESIGN,
        PipelineStage.VIRTUAL_SCREENING,
        PipelineStage.ADMET,
        PipelineStage.TOXICITY,
    ]

    STAGE_LABELS = {
        PipelineStage.TARGET_ID: "靶点识别",
        PipelineStage.LITERATURE: "文献综述",
        PipelineStage.COMPOUND_DESIGN: "化合物设计",
        PipelineStage.VIRTUAL_SCREENING: "虚拟筛选",
        PipelineStage.ADMET: "ADMET 预测",
        PipelineStage.TOXICITY: "毒性评估",
    }

    def __init__(self):
        # 延迟导入避免循环依赖，支持包模式和直接运行模式
        try:
            from ..agents import (
                AllergenTargetAgent,
                CompoundDesignAgent,
                VirtualScreeningAgent,
                AdmetPredictionAgent,
                ToxicityAssessmentAgent,
                LiteratureMiningAgent,
            )
        except ImportError:
            from agents.allergen_target_agent import AllergenTargetAgent
            from agents.compound_design_agent import CompoundDesignAgent
            from agents.virtual_screening_agent import VirtualScreeningAgent
            from agents.admet_agent import AdmetPredictionAgent
            from agents.toxicity_agent import ToxicityAssessmentAgent
            from agents.literature_mining_agent import LiteratureMiningAgent

        self.allergen_agent = AllergenTargetAgent()
        self.literature_agent = LiteratureMiningAgent()
        self.compound_agent = CompoundDesignAgent()
        self.screening_agent = VirtualScreeningAgent()
        self.admet_agent = AdmetPredictionAgent()
        self.toxicity_agent = ToxicityAssessmentAgent()

        self._stage_results: Dict[str, Dict[str, Any]] = {}
        self._stage_status: Dict[str, StageStatus] = {
            s.value: StageStatus.PENDING for s in self.STAGE_ORDER
        }
        self._stage_times: Dict[str, float] = {}
        self._pipeline_start: Optional[float] = None
        self._pipeline_end: Optional[float] = None

        logger.info(
            f"{self.PIPELINE_NAME} v{self.PIPELINE_VERSION} 初始化完成 | "
            f"6 个智能体已加载"
        )

    def run_pipeline(self, query: str = "food allergy drug discovery") -> Dict[str, Any]:
        """
        执行完整药物发现流水线。

        Args:
            query: 研究查询（如 "food allergy drug discovery"）

        Returns:
            完整研究报告
        """
        logger.info(f"{'='*60}")
        logger.info(f"Pipeline 启动: query='{query}'")
        logger.info(f"{'='*60}")

        self._pipeline_start = time.time()
        self._stage_results.clear()
        self._stage_times.clear()

        # ============================================
        # Stage 1: 靶点识别
        # ============================================
        stage1_result = self.run_stage(PipelineStage.TARGET_ID, {"query": query})

        # 选择最佳靶点用于后续阶段
        best_target = self._select_best_target(stage1_result)

        # ============================================
        # Stage 2: 文献综述
        # ============================================
        stage2_result = self.run_stage(
            PipelineStage.LITERATURE,
            {"query": query, "target": best_target},
        )

        # ============================================
        # Stage 3: 化合物设计
        # ============================================
        stage3_result = self.run_stage(
            PipelineStage.COMPOUND_DESIGN,
            {"target": best_target},
        )

        # 提取设计的化合物 ID
        designed_compound_id = stage3_result.get("compound_id", "CPD_UNKNOWN")

        # ============================================
        # Stage 4: 虚拟筛选
        # ============================================
        stage4_result = self.run_stage(
            PipelineStage.VIRTUAL_SCREENING,
            {"target": best_target, "library_size": 5000},
        )

        # ============================================
        # Stage 5: ADMET 预测
        # ============================================
        compound_props = stage3_result.get("properties", {})
        stage5_result = self.run_stage(
            PipelineStage.ADMET,
            {"compound_id": designed_compound_id, "properties": compound_props},
        )

        # ============================================
        # Stage 6: 毒性评估
        # ============================================
        stage6_result = self.run_stage(
            PipelineStage.TOXICITY,
            {"compound_id": designed_compound_id, "properties": compound_props},
        )

        self._pipeline_end = time.time()
        total_time = self._pipeline_end - self._pipeline_start

        # 生成最终报告
        report = self.generate_report({
            "query": query,
            "best_target": best_target,
            "stages": self._stage_results,
            "stage_times": self._stage_times,
            "total_time_s": round(total_time, 2),
        })

        logger.info(f"Pipeline 完成 | 总耗时: {total_time:.1f}s")
        return report

    def run_stage(self, stage: PipelineStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个流水线阶段。

        Args:
            stage: 阶段枚举
            input_data: 阶段输入数据

        Returns:
            阶段执行结果
        """
        stage_name = stage.value
        label = self.STAGE_LABELS.get(stage, stage_name)
        logger.info(f"[{label}] 开始执行...")

        self._stage_status[stage_name] = StageStatus.RUNNING
        start_time = time.time()

        try:
            result = self._execute_stage(stage, input_data)
            self._stage_status[stage_name] = StageStatus.COMPLETED
            elapsed = time.time() - start_time
            self._stage_times[stage_name] = round(elapsed, 3)
            self._stage_results[stage_name] = result

            logger.info(f"[{label}] 完成 ({elapsed:.2f}s)")
            return result

        except Exception as e:
            self._stage_status[stage_name] = StageStatus.FAILED
            elapsed = time.time() - start_time
            self._stage_times[stage_name] = round(elapsed, 3)
            error_result = {
                "agent": stage_name,
                "status": "error",
                "error": str(e),
            }
            self._stage_results[stage_name] = error_result
            logger.error(f"[{label}] 失败: {e}")
            return error_result

    def generate_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合研究报告。

        Args:
            results: 各阶段结果汇总

        Returns:
            结构化研究报告
        """
        logger.info("generate_report: 生成综合研究报告...")

        query = results.get("query", "")
        best_target = results.get("best_target", {})
        stages = results.get("stages", {})
        total_time = results.get("total_time_s", 0)

        # 提取关键发现
        target_id_result = stages.get(PipelineStage.TARGET_ID.value, {})
        compound_result = stages.get(PipelineStage.COMPOUND_DESIGN.value, {})
        admet_result = stages.get(PipelineStage.ADMET.value, {})
        toxicity_result = stages.get(PipelineStage.TOXICITY.value, {})

        key_findings = []

        # 靶点发现
        if "druggable_targets" in target_id_result:
            top_targets = target_id_result["druggable_targets"][:3]
            key_findings.append(
                f"识别 {len(target_id_result.get('druggable_targets', []))} 个可药靶点，"
                f"Top 3: {', '.join(t['name'] for t in top_targets)}"
            )

        # 化合物设计
        if "compound_id" in compound_result:
            key_findings.append(
                f"设计先导化合物 {compound_result['compound_id']}，"
                f"预测 pIC50={compound_result.get('predicted_activity', {}).get('pIC50', 'N/A')}"
            )

        # ADMET
        drug_like = admet_result.get("drug_likeness", {})
        if drug_like:
            key_findings.append(
                f"类药性评估: Lipinski={drug_like.get('lipinski_pass', 'N/A')}, "
                f"Veber={drug_like.get('veber_pass', 'N/A')}"
            )

        # 毒性
        safety_grade = toxicity_result.get("safety_grade", "N/A")
        safety_score = toxicity_result.get("overall_safety_score", "N/A")
        key_findings.append(f"安全评估等级: {safety_grade} (score={safety_score})")

        # 候选化合物摘要
        candidate_summary = {
            "compound_id": compound_result.get("compound_id", "N/A"),
            "compound_name": compound_result.get("name", "N/A"),
            "target": best_target.get("target_id", "N/A"),
            "predicted_activity_pic50": compound_result.get("predicted_activity", {}).get("pIC50", "N/A"),
            "lipinski_compliant": drug_like.get("lipinski_pass", "N/A"),
            "safety_grade": safety_grade,
            "safety_score": safety_score,
        }

        # 阶段状态
        stage_summary = []
        for stage in self.STAGE_ORDER:
            stage_name = stage.value
            status = self._stage_status.get(stage_name, StageStatus.PENDING)
            elapsed = self._stage_times.get(stage_name, 0)
            stage_summary.append({
                "stage": self.STAGE_LABELS.get(stage, stage_name),
                "stage_id": stage_name,
                "status": status.value,
                "time_s": elapsed,
            })

        report = {
            "report_type": "Food Allergy Drug Discovery Pipeline Report",
            "pipeline_version": self.PIPELINE_VERSION,
            "query": query,
            "generated_at": datetime.now().isoformat(),
            "total_execution_time_s": total_time,
            "key_findings": key_findings,
            "candidate_compound": candidate_summary,
            "stage_summary": stage_summary,
            "detailed_results": stages,
            "conclusion": self._generate_conclusion(candidate_summary, key_findings),
        }

        logger.info(f"generate_report: 完成 | 发现数={len(key_findings)}")
        return report

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        返回当前流水线状态。

        Returns:
            状态概览字典
        """
        completed = sum(
            1 for s in self._stage_status.values() if s == StageStatus.COMPLETED
        )
        total = len(self._stage_status)

        elapsed = 0.0
        if self._pipeline_start:
            end = self._pipeline_end or time.time()
            elapsed = end - self._pipeline_start

        return {
            "pipeline": self.PIPELINE_NAME,
            "version": self.PIPELINE_VERSION,
            "progress": f"{completed}/{total}",
            "progress_pct": round(completed / total * 100, 1) if total else 0,
            "elapsed_s": round(elapsed, 2),
            "stages": {
                self.STAGE_LABELS.get(s, s.value): self._stage_status.get(s.value, StageStatus.PENDING).value
                for s in self.STAGE_ORDER
            },
        }

    # ============================================================
    # 内部方法
    # ============================================================

    def _execute_stage(self, stage: PipelineStage, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行阶段逻辑分发"""
        if stage == PipelineStage.TARGET_ID:
            return self._run_target_identification(input_data)
        elif stage == PipelineStage.LITERATURE:
            return self._run_literature_review(input_data)
        elif stage == PipelineStage.COMPOUND_DESIGN:
            return self._run_compound_design(input_data)
        elif stage == PipelineStage.VIRTUAL_SCREENING:
            return self._run_virtual_screening(input_data)
        elif stage == PipelineStage.ADMET:
            return self._run_admet_prediction(input_data)
        elif stage == PipelineStage.TOXICITY:
            return self._run_toxicity_assessment(input_data)
        else:
            return {"error": f"Unknown stage: {stage}"}

    def _run_target_identification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 1：靶点识别"""
        discovery = self.allergen_agent.discover_targets()
        # 验证 Top 1 靶点
        if discovery.get("druggable_targets"):
            top_target_id = discovery["druggable_targets"][0]["id"]
            validation = self.allergen_agent.validate_target(top_target_id)
            hypothesis = self.allergen_agent.generate_hypothesis(validation)
            discovery["top_validation"] = validation
            discovery["hypothesis"] = {
                "id": hypothesis.hypothesis_id,
                "description": hypothesis.description,
                "predicted_efficacy": hypothesis.predicted_efficacy,
                "confidence": hypothesis.confidence,
            }
        return discovery

    def _run_literature_review(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 2：文献综述"""
        query = data.get("query", "food allergy drug discovery")
        search = self.literature_agent.search_papers(query, max_results=10)
        targets = self.literature_agent.extract_targets(search.get("papers", []))
        compounds = self.literature_agent.extract_compounds(search.get("papers", []))
        trends = self.literature_agent.trend_analysis(query)

        return {
            "agent": "LiteratureMiningAgent",
            "search_results": search,
            "extracted_targets": targets,
            "extracted_compounds": compounds,
            "trends": trends,
        }

    def _run_compound_design(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 3：化合物设计"""
        target = data.get("target", {"target_id": "FCE_RI", "target_name": "FcepsilonRI"})
        design = self.compound_agent.design_compound(target, "fcepsilonri_antagonist")
        # 优化
        if design.get("compound_id"):
            self.compound_agent.optimize_lead(design["compound_id"])
            # 生成类似物
            self.compound_agent.generate_analogs(design["compound_id"], n=5)
        return design

    def _run_virtual_screening(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 4：虚拟筛选"""
        target = data.get("target", {"target_id": "FCE_RI", "target_name": "FcepsilonRI"})
        lib_size = data.get("library_size", 5000)
        screen = self.screening_agent.screen_library(target, library_size=lib_size)
        ranked = self.screening_agent.rank_hits(top_n=50)
        return {
            "agent": "VirtualScreeningAgent",
            "screening": screen,
            "ranked": ranked,
        }

    def _run_admet_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 5：ADMET 预测"""
        compound_id = data.get("compound_id", "CPD_DEFAULT")
        properties = data.get("properties", None)
        return self.admet_agent.predict_admet(compound_id, properties)

    def _run_toxicity_assessment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """阶段 6：毒性评估"""
        compound_id = data.get("compound_id", "CPD_DEFAULT")
        properties = data.get("properties", None)
        assessment = self.toxicity_agent.assess_toxicity(compound_id, properties)
        report = self.toxicity_agent.safety_report(compound_id)
        return {
            **assessment,
            "safety_report": report,
        }

    def _select_best_target(self, stage1_result: Dict[str, Any]) -> Dict[str, Any]:
        """从靶点识别结果中选择最佳靶点"""
        druggable = stage1_result.get("druggable_targets", [])
        if druggable:
            best = druggable[0]
            return {
                "target_id": best["id"],
                "target_name": best["name"],
                "type": best["type"],
                "druggability": best["druggability"],
            }
        # 回退默认
        return {
            "target_id": "FCE_RI",
            "target_name": "FcepsilonRI",
            "type": "receptor",
            "druggability": 0.85,
        }

    @staticmethod
    def _generate_conclusion(candidate: Dict[str, Any], findings: List[str]) -> str:
        """生成结论段落"""
        compound = candidate.get("compound_id", "N/A")
        safety = candidate.get("safety_grade", "N/A")
        lipinski = candidate.get("lipinski_compliant", "N/A")

        parts = [
            f"本药物发现流水线已完成全流程分析。",
            f"基于 6 个专业智能体的协同工作，识别了先导化合物 {compound}。",
        ]

        if lipinski:
            parts.append("该化合物符合 Lipinski 类药性规则。")
        parts.append(f"安全评估等级为 {safety}。")
        parts.append(
            "建议后续进行体外活性验证、体内药效学研究和制剂开发。"
        )

        return " ".join(parts)


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    pipeline = DrugDiscoveryPipeline()
    print("=" * 60)
    print(f"  {pipeline.PIPELINE_NAME} v{pipeline.PIPELINE_VERSION}")
    print("=" * 60)

    report = pipeline.run_pipeline("food allergy drug discovery")

    print(f"\n{'='*60}")
    print("  流水线执行报告")
    print(f"{'='*60}")
    print(f"查询: {report['query']}")
    print(f"总耗时: {report['total_execution_time_s']}s")

    print("\n--- 关键发现 ---")
    for i, finding in enumerate(report["key_findings"], 1):
        print(f"  {i}. {finding}")

    print("\n--- 候选化合物 ---")
    for k, v in report["candidate_compound"].items():
        print(f"  {k}: {v}")

    print("\n--- 阶段状态 ---")
    for s in report["stage_summary"]:
        print(f"  [{s['status']}] {s['stage']} ({s['time_s']}s)")

    print(f"\n--- 结论 ---")
    print(f"  {report['conclusion'][:200]}...")
