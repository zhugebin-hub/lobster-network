#!/usr/bin/env python3
"""
论文质量评估器 (Paper Quality Evaluator)
=========================================

龙虾网络论文写作模块的质量评估工具。对论文进行 8 维度量化评分（0-100），
生成 Markdown 格式的详细反馈报告，并提供个性化改进建议。

8 个评估维度：
  1. structure    （结构完整性）— IMRaD 格式遵循度、逻辑流畅性
  2. abstract     （摘要质量）  — 简洁性、完整性、关键词覆盖度
  3. literature_review（文献综述）— 广度、时效性、批判性分析
  4. methodology  （方法论）   — 严谨性、可复现性、适当性
  5. data_analysis（数据分析） — 统计有效性、可视化质量
  6. argumentation（论证逻辑） — 论点-证据-论据结构
  7. formatting   （格式规范） — LaTeX/Word 标准、图表质量
  8. citations    （引用质量） — 引用数量、格式一致性、自引比例

运行方式：
  python paper_evaluator.py                    # 对示例论文进行评估
  python paper_evaluator.py --compare a.json b.json  # 对比两篇论文

作者: 龙虾网络论文写作系统
"""

import json
import os
import sys
import random
import math
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# 常量：维度定义与权重
# ---------------------------------------------------------------------------

DIMENSIONS = {
    "structure": {
        "name": "结构完整性",
        "name_en": "Structure",
        "description": "IMRaD 格式遵循度、章节完整性、逻辑流畅性",
        "weight": 0.15,
        "criteria": [
            "是否遵循 IMRaD（引言-方法-结果-讨论）标准结构",
            "各章节篇幅比例是否合理",
            "章节之间的逻辑衔接是否自然",
            "是否包含所有必要组成部分（摘要、关键词、参考文献等）",
        ],
    },
    "abstract": {
        "name": "摘要质量",
        "name_en": "Abstract Quality",
        "description": "简洁性、完整性、关键词覆盖度",
        "weight": 0.10,
        "criteria": [
            "字数是否在 200-350 字之间",
            "是否涵盖背景、方法、结果、结论四要素",
            "关键词选取是否准确且有区分度",
            "是否避免使用缩写和引用",
        ],
    },
    "literature_review": {
        "name": "文献综述",
        "name_en": "Literature Review",
        "description": "广度、时效性、批判性分析",
        "weight": 0.15,
        "criteria": [
            "文献覆盖范围是否充分（领域、地域、时间）",
            "是否包含近 3 年的最新研究成果",
            "对已有工作是否有批判性分析而非简单罗列",
            "是否明确识别出研究空白（research gap）",
        ],
    },
    "methodology": {
        "name": "方法论",
        "name_en": "Methodology",
        "description": "严谨性、可复现性、适当性",
        "weight": 0.15,
        "criteria": [
            "方法描述是否足够详细以支持复现",
            "所选方法是否适合研究问题",
            "实验设计是否包含对照组或基线比较",
            "是否讨论了潜在的威胁效度（threats to validity）",
        ],
    },
    "data_analysis": {
        "name": "数据分析",
        "name_en": "Data Analysis",
        "description": "统计有效性、可视化质量",
        "weight": 0.10,
        "criteria": [
            "是否使用适当的统计检验方法",
            "是否报告了显著性水平（p-value）和效应量",
            "图表是否清晰、规范、信息密度适当",
            "数据可视化是否辅助而非替代文字论述",
        ],
    },
    "argumentation": {
        "name": "论证逻辑",
        "name_en": "Argumentation",
        "description": "论点-证据-论据（claim-evidence-warrant）结构",
        "weight": 0.15,
        "criteria": [
            "核心论点是否清晰、具体、可检验",
            "每个论点是否有充分的证据支撑",
            "从证据到结论的推理链条是否完整",
            "是否考虑并回应了可能的反对意见",
        ],
    },
    "formatting": {
        "name": "格式规范",
        "name_en": "Formatting",
        "description": "LaTeX/Word 标准、图表质量、排版一致性",
        "weight": 0.10,
        "criteria": [
            "是否遵循目标期刊/会议的格式模板",
            "标题层级是否一致且编号正确",
            "图表是否有编号、标题和必要的图注/表注",
            "数学公式、代码片段是否规范排版",
        ],
    },
    "citations": {
        "name": "引用质量",
        "name_en": "Citations",
        "description": "引用数量、格式一致性、自引比例",
        "weight": 0.10,
        "criteria": [
            "引用总数是否在合理范围（通常 20-60 篇）",
            "引用格式是否全文一致（如 APA / IEEE / GB/T 7714）",
            "自引比例是否过高（一般 < 20%）",
            "是否引用了领域内的经典文献和权威期刊",
        ],
    },
}

# 评分等级映射
GRADE_THRESHOLDS = [
    (90, "优秀 (Excellent)", "A"),
    (80, "良好 (Good)", "B"),
    (70, "中等 (Satisfactory)", "C"),
    (60, "及格 (Pass)", "D"),
    (0, "不及格 (Fail)", "F"),
]


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _ts() -> str:
    """返回当前时间戳字符串。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _grade_from_score(score: float) -> tuple:
    """
    根据分数返回 (等级描述, 等级字母)。

    参数:
        score: 0-100 的分数

    返回:
        (等级描述字符串, 等级字母) 元组
    """
    for threshold, desc, letter in GRADE_THRESHOLDS:
        if score >= threshold:
            return desc, letter
    return "不及格 (Fail)", "F"


def _score_bar(score: float, width: int = 20) -> str:
    """
    生成分数的文本进度条。

    参数:
        score: 0-100 的分数
        width: 进度条字符宽度

    返回:
        形如 "████████████░░░░░░░░ 60.0" 的字符串
    """
    filled = int(round(score / 100 * width))
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {score:.1f}"


# ---------------------------------------------------------------------------
# 核心评估函数
# ---------------------------------------------------------------------------


def evaluate_dimension(paper_data: dict, dimension: str) -> dict:
    """
    评估论文在单一维度上的质量，返回 0-100 的评分及详细依据。

    评估基于 paper_data 中的结构化字段进行启发式打分。若 paper_data
    包含该维度的显式得分（paper_data["scores"][dimension]），则直接使用；
    否则根据内容特征进行模拟评分。

    参数:
        paper_data: 论文数据字典，可包含 sections / word_count / citations 等字段
        dimension: 维度键名（如 "structure"、"abstract" 等）

    返回:
        评估结果字典：
        {
            "dimension": str,
            "name": str,
            "score": float,
            "grade": str,
            "grade_letter": str,
            "findings": [str, ...],
            "strengths": [str, ...],
            "weaknesses": [str, ...],
        }
    """
    if dimension not in DIMENSIONS:
        return {
            "dimension": dimension,
            "name": dimension,
            "score": 0,
            "grade": "未知维度",
            "grade_letter": "?",
            "findings": [f"维度 '{dimension}' 未在评估框架中定义"],
            "strengths": [],
            "weaknesses": [],
        }

    dim_meta = DIMENSIONS[dimension]

    # 尝试从论文数据中获取显式评分
    explicit_scores = paper_data.get("scores", {})
    if dimension in explicit_scores:
        raw = explicit_scores[dimension]
        # 可以是数字或含 score 键的字典
        if isinstance(raw, (int, float)):
            base_score = float(raw)
        elif isinstance(raw, dict):
            base_score = float(raw.get("score", 50))
        else:
            base_score = 50.0
    else:
        # 基于论文特征进行启发式评分
        base_score = _heuristic_score(paper_data, dimension)

    # 加入少量随机扰动（模拟评审者间差异）
    noise = random.gauss(0, 2.0)
    score = max(0, min(100, round(base_score + noise, 1)))

    grade_desc, grade_letter = _grade_from_score(score)

    # 生成评价依据
    findings, strengths, weaknesses = _generate_dimension_findings(
        paper_data, dimension, score, dim_meta
    )

    return {
        "dimension": dimension,
        "name": dim_meta["name"],
        "name_en": dim_meta["name_en"],
        "score": score,
        "grade": grade_desc,
        "grade_letter": grade_letter,
        "weight": dim_meta["weight"],
        "findings": findings,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }


def _heuristic_score(paper_data: dict, dimension: str) -> float:
    """
    基于论文数据特征进行启发式打分。

    参数:
        paper_data: 论文数据字典
        dimension: 维度键名

    返回:
        0-100 的基础分数
    """
    score = 50.0  # 基准分

    word_count = paper_data.get("word_count", 0)
    sections = paper_data.get("sections", [])
    citations = paper_data.get("citations", [])
    figures = paper_data.get("figures", [])
    tables = paper_data.get("tables", [])
    keywords = paper_data.get("keywords", [])
    has_abstract = paper_data.get("has_abstract", bool(paper_data.get("abstract")))
    has_methodology = paper_data.get("has_methodology", False)
    draft_version = paper_data.get("draft_version", 1)

    if dimension == "structure":
        score += min(20, len(sections) * 3)
        if len(sections) >= 6:
            score += 10
        if word_count > 5000:
            score += 5
        if has_abstract:
            score += 5

    elif dimension == "abstract":
        if has_abstract:
            score += 20
        abstract_text = paper_data.get("abstract", "")
        if isinstance(abstract_text, str):
            abstract_len = len(abstract_text)
        else:
            abstract_len = 0
        if 200 <= abstract_len <= 400:
            score += 15
        elif abstract_len > 100:
            score += 8
        score += min(10, len(keywords) * 2)

    elif dimension == "literature_review":
        n_citations = len(citations) if isinstance(citations, list) else int(citations) if citations else 0
        score += min(25, n_citations * 0.8)
        # 检查近年文献
        recent = 0
        if isinstance(citations, list):
            for c in citations:
                year = c.get("year", 0) if isinstance(c, dict) else 0
                if year >= 2022:
                    recent += 1
        score += min(10, recent * 3)

    elif dimension == "methodology":
        if has_methodology:
            score += 20
        if word_count > 1500:
            score += 10
        # 是否有实验设置描述
        for key in ["experiment_setup", "dataset", "baseline", "metrics"]:
            if key in paper_data:
                score += 5

    elif dimension == "data_analysis":
        n_figures = len(figures) if isinstance(figures, list) else int(figures) if figures else 0
        n_tables = len(tables) if isinstance(tables, list) else int(tables) if tables else 0
        score += min(15, n_figures * 5)
        score += min(10, n_tables * 5)
        if paper_data.get("statistical_tests"):
            score += 10
        if paper_data.get("p_value") is not None:
            score += 5

    elif dimension == "argumentation":
        # 章节数越多且字数越多，论证通常越充分
        score += min(15, len(sections) * 2)
        if word_count > 6000:
            score += 10
        elif word_count > 3000:
            score += 5
        # 草稿版本越高，论证越经过打磨
        score += min(10, (draft_version - 1) * 5)

    elif dimension == "formatting":
        # 检查结构化程度
        if paper_data.get("uses_latex") or paper_data.get("template"):
            score += 15
        score += min(10, len(sections) * 1.5)
        n_figures = len(figures) if isinstance(figures, list) else int(figures) if figures else 0
        n_tables = len(tables) if isinstance(tables, list) else int(tables) if tables else 0
        if n_figures > 0 and n_tables > 0:
            score += 10
        if paper_data.get("consistent_style", True):
            score += 5

    elif dimension == "citations":
        n_citations = len(citations) if isinstance(citations, list) else int(citations) if citations else 0
        if 20 <= n_citations <= 60:
            score += 25
        elif 10 <= n_citations < 20:
            score += 15
        elif n_citations > 60:
            score += 20
        else:
            score += 5
        if paper_data.get("citation_style"):
            score += 10
        self_cite_ratio = paper_data.get("self_citation_ratio", 0.1)
        if self_cite_ratio < 0.2:
            score += 5
        elif self_cite_ratio > 0.4:
            score -= 10

    return max(0, min(100, score))


def _generate_dimension_findings(
    paper_data: dict, dimension: str, score: float, dim_meta: dict
) -> tuple:
    """
    为指定维度生成评审发现、优点和缺点列表。

    参数:
        paper_data: 论文数据
        dimension: 维度键名
        score: 该维度的评分
        dim_meta: 维度元数据

    返回:
        (findings, strengths, weaknesses) 三元组
    """
    findings = []
    strengths = []
    weaknesses = []

    for criterion in dim_meta["criteria"]:
        # 模拟对每条准则的判定
        if score >= 80:
            findings.append(f"[通过] {criterion}")
            strengths.append(criterion)
        elif score >= 65:
            # 一半通过一半待改进
            if random.random() > 0.5:
                findings.append(f"[部分通过] {criterion} — 基本达标但有提升空间")
                strengths.append(criterion)
            else:
                findings.append(f"[待改进] {criterion} — 需要进一步加强")
                weaknesses.append(criterion)
        else:
            findings.append(f"[不通过] {criterion} — 需要重点修改")
            weaknesses.append(criterion)

    return findings, strengths, weaknesses


def evaluate_paper(paper_data: dict) -> dict:
    """
    对论文进行全维度评估，返回各维度评分和加权综合分。

    参数:
        paper_data: 论文数据字典

    返回:
        评估结果字典：
        {
            "dimension_scores": {dim_key: evaluate_dimension 的返回值, ...},
            "overall_score": float,
            "grade": str,
            "grade_letter": str,
            "evaluated_at": str,
            "paper_title": str,
        }
    """
    paper_title = paper_data.get("title", paper_data.get("paper_title", "未命名论文"))

    dimension_scores = {}
    for dim_key in DIMENSIONS:
        dimension_scores[dim_key] = evaluate_dimension(paper_data, dim_key)

    # 计算加权综合分
    weighted_sum = sum(
        dim_result["score"] * dim_result["weight"]
        for dim_result in dimension_scores.values()
    )
    total_weight = sum(d["weight"] for d in dimension_scores.values())
    overall_score = round(weighted_sum / total_weight, 1) if total_weight > 0 else 0

    grade_desc, grade_letter = _grade_from_score(overall_score)

    return {
        "paper_title": paper_title,
        "dimension_scores": dimension_scores,
        "overall_score": overall_score,
        "grade": grade_desc,
        "grade_letter": grade_letter,
        "evaluated_at": _ts(),
    }


# ---------------------------------------------------------------------------
# 反馈与改进建议生成
# ---------------------------------------------------------------------------


def generate_feedback(paper_data: dict, scores: dict) -> str:
    """
    生成 Markdown 格式的详细反馈报告。

    参数:
        paper_data: 论文数据字典
        scores: evaluate_paper() 返回的评估结果字典

    返回:
        Markdown 格式的反馈报告字符串
    """
    lines = []
    title = scores.get("paper_title", "未命名论文")
    overall = scores["overall_score"]
    grade = scores["grade"]
    grade_letter = scores["grade_letter"]

    # --- 标题 ---
    lines.append(f"# 论文质量评估报告")
    lines.append("")
    lines.append(f"**论文标题**: {title}")
    lines.append(f"**评估时间**: {scores.get('evaluated_at', _ts())}")
    lines.append(f"**综合评分**: {overall:.1f}/100 — {grade} ({grade_letter})")
    lines.append("")

    # --- 综合评分总览 ---
    lines.append("## 一、综合评分总览")
    lines.append("")
    lines.append(f"```")
    lines.append(f"综合得分: {_score_bar(overall, 30)}")
    lines.append(f"```")
    lines.append("")

    # 维度得分表格
    lines.append("| 维度 | 权重 | 得分 | 等级 | 进度 |")
    lines.append("|------|------|------|------|------|")
    for dim_key, dim_result in scores["dimension_scores"].items():
        name = dim_result["name"]
        weight = f"{dim_result['weight']:.0%}"
        sc = dim_result["score"]
        gl = dim_result["grade_letter"]
        bar = _score_bar(sc, 15)
        lines.append(f"| {name} | {weight} | {sc:.1f} | {gl} | `{bar}` |")
    lines.append("")

    # --- 各维度详细评价 ---
    lines.append("## 二、各维度详细评价")
    lines.append("")

    for dim_key, dim_result in scores["dimension_scores"].items():
        name = dim_result["name"]
        name_en = dim_result.get("name_en", "")
        sc = dim_result["score"]
        gl = dim_result["grade_letter"]

        lines.append(f"### {dim_result['grade_letter']}. {name} ({name_en}) — {sc:.1f}分")
        lines.append("")

        if dim_result.get("findings"):
            lines.append("**评审发现**:")
            lines.append("")
            for finding in dim_result["findings"]:
                lines.append(f"- {finding}")
            lines.append("")

        if dim_result.get("strengths"):
            lines.append("**优点**:")
            lines.append("")
            for s in dim_result["strengths"][:3]:
                lines.append(f"  - {s}")
            lines.append("")

        if dim_result.get("weaknesses"):
            lines.append("**不足**:")
            lines.append("")
            for w in dim_result["weaknesses"][:3]:
                lines.append(f"  - {w}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # --- 优先修订建议 ---
    lines.append("## 三、优先修订建议")
    lines.append("")

    sorted_dims = sorted(
        scores["dimension_scores"].values(),
        key=lambda x: x["score"],
    )
    for i, dim_result in enumerate(sorted_dims[:3], 1):
        name = dim_result["name"]
        sc = dim_result["score"]
        lines.append(f"{i}. **{name}** ({sc:.1f}分)")
        if dim_result.get("weaknesses"):
            for w in dim_result["weaknesses"][:2]:
                lines.append(f"   - 需要改进: {w}")
        lines.append("")

    # --- 总结 ---
    lines.append("## 四、总结")
    lines.append("")
    if overall >= 80:
        lines.append(
            "本文整体质量较高，在学术规范和论证深度方面表现良好。"
            "建议针对上述薄弱环节进行精修后即可投稿。"
        )
    elif overall >= 65:
        lines.append(
            "本文具备基本的学术框架，但在若干维度上仍有明显提升空间。"
            "建议进行一轮系统性修订，重点关注得分最低的 2-3 个维度。"
        )
    else:
        lines.append(
            "本文在多个维度上未达到预期标准，需要进行较大幅度的修改。"
            "建议先重新梳理论文结构和论证逻辑，再逐章进行修订。"
        )
    lines.append("")
    lines.append("---")
    lines.append(f"*本报告由龙虾网络论文质量评估器自动生成于 {_ts()}*")

    return "\n".join(lines)


def generate_improvement_plan(scores: dict, player_profile: dict) -> dict:
    """
    根据评估结果和玩家档案，生成个性化的改进计划与推荐练习。

    参数:
        scores: evaluate_paper() 返回的评估结果
        player_profile: 角色档案字典（包含 skill_scores / level / specialty 等）

    返回:
        改进计划字典：
        {
            "priority_areas": [...],
            "exercises": [...],
            "study_resources": [...],
            "estimated_effort_hours": float,
            "plan_text": str,
        }
    """
    dim_scores = scores.get("dimension_scores", {})
    player_skills = player_profile.get("skill_scores", {})
    player_level = player_profile.get("level", 1)

    # 按得分排序，找出最弱维度
    sorted_dims = sorted(dim_scores.items(), key=lambda x: x[1]["score"])
    priority_areas = []
    exercises = []
    study_resources = []

    # 练习模板
    exercise_templates = {
        "structure": [
            {
                "name": "IMRaD 结构拆解练习",
                "description": "选取 3 篇目标期刊的高引论文，逐一标注其 IMRaD 结构要素，"
                               "对比分析各部分的篇幅比例和过渡方式。",
                "duration_min": 60,
                "difficulty": "基础",
            },
            {
                "name": "大纲逆向工程",
                "description": "从一篇已发表论文逆向提取其大纲结构，"
                               "然后用自己的研究主题重新组织一份大纲。",
                "duration_min": 90,
                "difficulty": "进阶",
            },
        ],
        "abstract": [
            {
                "name": "摘要四要素速写",
                "description": "在 30 分钟内为自己的论文撰写包含"
                               "背景-方法-结果-结论四要素的摘要，控制在 250 字以内。",
                "duration_min": 30,
                "difficulty": "基础",
            },
            {
                "name": "摘要对比改写",
                "description": "找到同领域 5 篇论文的摘要，标注其优劣，"
                               "然后用最佳实践重写自己的摘要。",
                "duration_min": 60,
                "difficulty": "进阶",
            },
        ],
        "literature_review": [
            {
                "name": "文献矩阵构建",
                "description": "使用文献矩阵表格（作者-年份-方法-发现-局限），"
                               "系统整理 20 篇核心文献。",
                "duration_min": 120,
                "difficulty": "进阶",
            },
            {
                "name": "研究空白识别训练",
                "description": "阅读 5 篇综述论文的 Future Work 部分，"
                               "总结共性的研究空白，并与自己的选题对应。",
                "duration_min": 60,
                "difficulty": "基础",
            },
        ],
        "methodology": [
            {
                "name": "可复现性自检",
                "description": "将自己论文的方法论部分发给同行，"
                               "请其仅根据文字描述尝试复现实验，记录遇到的歧义和遗漏。",
                "duration_min": 90,
                "difficulty": "进阶",
            },
            {
                "name": "实验设计清单",
                "description": "使用标准实验设计清单（变量、控制、基线、指标、统计检验）"
                               "逐项核对自己的实验方案。",
                "duration_min": 45,
                "difficulty": "基础",
            },
        ],
        "data_analysis": [
            {
                "name": "统计检验选择练习",
                "description": "给定 5 种不同的实验场景，选择合适的统计检验方法并说明理由。",
                "duration_min": 45,
                "difficulty": "基础",
            },
            {
                "name": "图表重设计",
                "description": "将自己论文中的图表按照 Tufte 的数据墨水比原则重新设计。",
                "duration_min": 60,
                "difficulty": "进阶",
            },
        ],
        "argumentation": [
            {
                "name": "CEW 结构拆解",
                "description": "将自己论文中的每个核心论点按 Claim-Evidence-Warrant 结构"
                               "拆解，检查是否有缺失环节。",
                "duration_min": 60,
                "difficulty": "基础",
            },
            {
                "name": "魔鬼代言人练习",
                "description": "对自己的每个核心论点提出 3 个可能的反对意见，"
                               "然后撰写回应段落。",
                "duration_min": 90,
                "difficulty": "进阶",
            },
        ],
        "formatting": [
            {
                "name": "模板一致性检查",
                "description": "逐项对照目标期刊/会议的格式要求清单，"
                               "检查论文中的每个格式元素是否合规。",
                "duration_min": 45,
                "difficulty": "基础",
            },
            {
                "name": "LaTeX 排版优化",
                "description": "使用 LaTeX 的浮动体机制重新安排图表位置，"
                               "确保图文不跨页且引用在图表之前。",
                "duration_min": 60,
                "difficulty": "进阶",
            },
        ],
        "citations": [
            {
                "name": "引用审计",
                "description": "统计论文引用的年份分布、来源分布、自引比例，"
                               "识别缺失的关键引用。",
                "duration_min": 60,
                "difficulty": "基础",
            },
            {
                "name": "引用格式规范化",
                "description": "使用 Zotero/BibTeX 重新整理参考文献库，"
                               "确保格式 100% 一致。",
                "duration_min": 45,
                "difficulty": "基础",
            },
        ],
    }

    # 资源推荐模板
    resource_templates = {
        "structure": "《Academic Writing for Graduate Students》— Swales & Feak",
        "abstract": "《Writing an Abstract: A Guide》— Elsevier Author Guidelines",
        "literature_review": "《Systematic Approaches to a Successful Literature Review》— Booth et al.",
        "methodology": "《Research Design: Qualitative, Quantitative, and Mixed Methods》— Creswell",
        "data_analysis": "《The Visual Display of Quantitative Information》— Edward Tufte",
        "argumentation": "《They Say / I Say: The Moves That Matter in Academic Writing》— Graff & Birkenstein",
        "formatting": "《LaTeX: A Document Preparation System》— Leslie Lamport",
        "citations": "《Citation Styles Quick Guide》— Purdue OWL",
    }

    total_effort_min = 0

    for dim_key, dim_result in sorted_dims[:4]:  # 取最弱的 4 个维度
        name = dim_result["name"]
        sc = dim_result["score"]

        priority_areas.append({
            "dimension": dim_key,
            "name": name,
            "current_score": sc,
            "target_score": min(100, sc + 15),
        })

        # 为该维度推荐 1-2 个练习
        available_exercises = exercise_templates.get(dim_key, [])
        # 根据等级选择难度
        if player_level <= 2:
            selected = [e for e in available_exercises if e["difficulty"] == "基础"]
        else:
            selected = available_exercises

        if not selected:
            selected = available_exercises

        for ex in selected[:2]:
            exercise_entry = dict(ex)
            exercise_entry["target_dimension"] = dim_key
            exercises.append(exercise_entry)
            total_effort_min += ex["duration_min"]

        # 推荐学习资源
        resource = resource_templates.get(dim_key)
        if resource:
            study_resources.append({
                "dimension": dim_key,
                "resource": resource,
            })

    # 生成改进计划文本
    plan_lines = [
        f"# 个性化改进计划",
        f"",
        f"**角色**: {player_profile.get('display_name', 'unknown')}",
        f"**当前等级**: Lv.{player_level}",
        f"**评估综合分**: {scores.get('overall_score', 0):.1f}/100",
        f"",
        f"## 优先改进领域",
        f"",
    ]
    for i, area in enumerate(priority_areas, 1):
        plan_lines.append(
            f"{i}. **{area['name']}**: "
            f"{area['current_score']:.1f} → 目标 {area['target_score']:.1f}"
        )
    plan_lines.append("")
    plan_lines.append("## 推荐练习")
    plan_lines.append("")
    for i, ex in enumerate(exercises, 1):
        plan_lines.append(
            f"{i}. **{ex['name']}** ({ex['difficulty']}, {ex['duration_min']}分钟)"
        )
        plan_lines.append(f"   {ex['description']}")
        plan_lines.append("")

    plan_lines.append("## 学习资源")
    plan_lines.append("")
    for res in study_resources:
        plan_lines.append(f"- **{res['dimension']}**: {res['resource']}")
    plan_lines.append("")
    plan_lines.append(
        f"**预计总投入时间**: {total_effort_min / 60:.1f} 小时"
    )

    return {
        "priority_areas": priority_areas,
        "exercises": exercises,
        "study_resources": study_resources,
        "estimated_effort_hours": round(total_effort_min / 60, 1),
        "plan_text": "\n".join(plan_lines),
    }


def compare_papers(paper_a: dict, paper_b: dict) -> dict:
    """
    对比评估两篇论文的质量，生成逐维度对比报告。

    参数:
        paper_a: 论文 A 的数据字典
        paper_b: 论文 B 的数据字典

    返回:
        对比结果字典：
        {
            "paper_a_title": str,
            "paper_b_title": str,
            "scores_a": dict,
            "scores_b": dict,
            "overall_a": float,
            "overall_b": float,
            "dimension_deltas": {dim_key: delta, ...},
            "winner": str,
            "comparison_report": str,
        }
    """
    eval_a = evaluate_paper(paper_a)
    eval_b = evaluate_paper(paper_b)

    title_a = eval_a["paper_title"]
    title_b = eval_b["paper_title"]

    # 计算维度差值
    dimension_deltas = {}
    for dim_key in DIMENSIONS:
        score_a = eval_a["dimension_scores"][dim_key]["score"]
        score_b = eval_b["dimension_scores"][dim_key]["score"]
        dimension_deltas[dim_key] = round(score_a - score_b, 1)

    # 判定优胜者
    overall_a = eval_a["overall_score"]
    overall_b = eval_b["overall_score"]
    if overall_a > overall_b + 2:
        winner = f"论文 A ({title_a})"
    elif overall_b > overall_a + 2:
        winner = f"论文 B ({title_b})"
    else:
        winner = "旗鼓相当"

    # 生成对比报告文本
    lines = [
        f"# 论文对比评估报告",
        f"",
        f"**论文 A**: {title_a} (综合分: {overall_a:.1f})",
        f"**论文 B**: {title_b} (综合分: {overall_b:.1f})",
        f"**评估时间**: {_ts()}",
        f"",
        f"## 综合对比",
        f"",
        f"| 维度 | 论文 A | 论文 B | 差值 (A-B) |",
        f"|------|--------|--------|------------|",
    ]

    for dim_key in DIMENSIONS:
        name = DIMENSIONS[dim_key]["name"]
        sa = eval_a["dimension_scores"][dim_key]["score"]
        sb = eval_b["dimension_scores"][dim_key]["score"]
        delta = dimension_deltas[dim_key]
        delta_str = f"+{delta:.1f}" if delta > 0 else f"{delta:.1f}"
        # 高亮领先方
        if delta > 2:
            marker = " ← A 领先"
        elif delta < -2:
            marker = " ← B 领先"
        else:
            marker = ""
        lines.append(f"| {name} | {sa:.1f} | {sb:.1f} | {delta_str}{marker} |")

    lines.append(f"| **综合** | **{overall_a:.1f}** | **{overall_b:.1f}** | "
                 f"**{overall_a - overall_b:+.1f}** |")
    lines.append("")

    # 维度优势统计
    a_wins = sum(1 for d in dimension_deltas.values() if d > 2)
    b_wins = sum(1 for d in dimension_deltas.values() if d < -2)
    ties = len(DIMENSIONS) - a_wins - b_wins

    lines.append("## 维度胜负统计")
    lines.append("")
    lines.append(f"- 论文 A 领先: **{a_wins}** 个维度")
    lines.append(f"- 论文 B 领先: **{b_wins}** 个维度")
    lines.append(f"- 旗鼓相当: **{ties}** 个维度")
    lines.append("")
    lines.append(f"**综合判定**: {winner}")
    lines.append("")

    # A 的优势和劣势分析
    lines.append("## 详细分析")
    lines.append("")
    if a_wins > 0:
        a_strong = [
            DIMENSIONS[k]["name"]
            for k, v in dimension_deltas.items() if v > 2
        ]
        lines.append(f"**论文 A 的优势维度**: {', '.join(a_strong)}")
        lines.append("")
    if b_wins > 0:
        b_strong = [
            DIMENSIONS[k]["name"]
            for k, v in dimension_deltas.items() if v < -2
        ]
        lines.append(f"**论文 B 的优势维度**: {', '.join(b_strong)}")
        lines.append("")

    lines.append("---")
    lines.append(f"*本报告由龙虾网络论文质量评估器自动生成于 {_ts()}*")

    return {
        "paper_a_title": title_a,
        "paper_b_title": title_b,
        "scores_a": eval_a,
        "scores_b": eval_b,
        "overall_a": overall_a,
        "overall_b": overall_b,
        "dimension_deltas": dimension_deltas,
        "winner": winner,
        "comparison_report": "\n".join(lines),
    }


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------


def main() -> None:
    """
    评估器主入口。

    支持三种运行模式：
      1. 无参数：对内置示例论文进行评估并输出报告
      2. --evaluate <json_file>：评估指定的论文 JSON 文件
      3. --compare <file_a> <file_b>：对比两篇论文
    """
    args = sys.argv[1:]

    if len(args) >= 2 and args[0] == "--compare":
        # 对比模式
        file_a, file_b = args[1], args[2]
        print(f"正在对比两篇论文: {file_a} vs {file_b}")
        print()

        with open(file_a, "r", encoding="utf-8") as f:
            paper_a = json.load(f)
        with open(file_b, "r", encoding="utf-8") as f:
            paper_b = json.load(f)

        result = compare_papers(paper_a, paper_b)
        print(result["comparison_report"])
        return

    if len(args) >= 2 and args[0] == "--evaluate":
        # 文件评估模式
        filepath = args[1]
        print(f"正在评估论文: {filepath}")
        print()

        with open(filepath, "r", encoding="utf-8") as f:
            paper_data = json.load(f)
    else:
        # 演示模式：使用内置示例论文数据
        print("=" * 60)
        print("  龙虾网络论文质量评估器 — 演示模式")
        print("=" * 60)
        print()

        paper_data = {
            "title": "基于龙虾网络的多智能体协作论文写作系统",
            "word_count": 8500,
            "has_abstract": True,
            "abstract": (
                "学术写作是一项高度协作性的知识工作。本文提出了 LobsterWriter，"
                "一种基于龙虾网络拓扑的多智能体协作论文写作系统，通过四类异质智能体"
                "角色实现分布式的论文生产流水线。实验表明系统在 8 维质量评估中"
                "综合得分提升 23.7%。"
            ),
            "keywords": ["多智能体", "协作写作", "龙虾网络", "学术写作", "同行评审"],
            "sections": [
                {"title": "引言", "word_count": 1200},
                {"title": "相关工作", "word_count": 1500},
                {"title": "方法论", "word_count": 2000},
                {"title": "实验", "word_count": 1800},
                {"title": "结果与讨论", "word_count": 1500},
                {"title": "结论", "word_count": 500},
            ],
            "citations": [
                {"authors": "Zhang & Li", "year": 2023, "journal": "计算机学报"},
                {"authors": "Wang et al.", "year": 2024, "journal": "IEEE ToE"},
                {"authors": "Smith & Johnson", "year": 2022, "journal": "ACM CSUR"},
                {"authors": "Chen & Liu", "year": 2023, "journal": "软件学报"},
                {"authors": "Garcia et al.", "year": 2021, "journal": "Nature MI"},
                {"authors": "Tanaka & Sato", "year": 2022, "journal": "AAAI"},
                {"authors": "Brown & Davis", "year": 2024, "journal": "NeurIPS"},
                {"authors": "Park & Kim", "year": 2023, "journal": "ACL"},
                {"authors": "Zhuge et al.", "year": 2024, "journal": "计算机学报"},
                {"authors": "Anderson et al.", "year": 2020, "journal": "ICLR"},
                {"authors": "Lee & Choi", "year": 2023, "journal": "EMNLP"},
                {"authors": "Martinez et al.", "year": 2022, "journal": "JMLR"},
                {"authors": "Patel et al.", "year": 2024, "journal": "ICML"},
                {"authors": "Yamamoto et al.", "year": 2021, "journal": "IJCAI"},
                {"authors": "Mueller et al.", "year": 2023, "journal": "KDD"},
                {"authors": "Zhao & Qian", "year": 2022, "journal": "计算机学报"},
                {"authors": "Sun et al.", "year": 2023, "journal": "软件工程"},
                {"authors": "Liu & Wang", "year": 2024, "journal": "CHI"},
                {"authors": "Zhou et al.", "year": 2023, "journal": "CSCW"},
                {"authors": "Wu & Zheng", "year": 2022, "journal": "软件学报"},
                {"authors": "Kim & Lee", "year": 2021, "journal": "IEEE TSE"},
                {"authors": "Huang et al.", "year": 2024, "journal": "ACL"},
                {"authors": "Xu & Yang", "year": 2023, "journal": "NAACL"},
                {"authors": "Gao et al.", "year": 2022, "journal": "AAAI"},
                {"authors": "Feng & Ma", "year": 2024, "journal": "计算机学报"},
            ],
            "figures": [
                {"id": 1, "title": "系统架构图"},
                {"id": 2, "title": "智能体通信时序图"},
                {"id": 3, "title": "8 维评估雷达图"},
                {"id": 4, "title": "消融实验结果"},
                {"id": 5, "title": "案例对比截图"},
                {"id": 6, "title": "用户满意度调查结果"},
            ],
            "tables": [
                {"id": 1, "title": "基线对比实验结果"},
                {"id": 2, "title": "消融实验数据"},
                {"id": 3, "title": "各维度详细得分"},
                {"id": 4, "title": "智能体角色配置"},
            ],
            "has_methodology": True,
            "experiment_setup": True,
            "dataset": "30 篇模拟论文",
            "baseline": "单智能体写作模式",
            "metrics": "8 维质量评估框架",
            "statistical_tests": True,
            "p_value": 0.001,
            "uses_latex": True,
            "template": "IEEE Conference Template",
            "consistent_style": True,
            "citation_style": "IEEE",
            "self_citation_ratio": 0.12,
            "draft_version": 2,
        }

    # 执行评估
    scores = evaluate_paper(paper_data)

    # 输出评估结果
    print(f"论文: {scores['paper_title']}")
    print(f"综合评分: {scores['overall_score']:.1f}/100 — {scores['grade']} ({scores['grade_letter']})")
    print()

    # 快速概览
    print("各维度得分:")
    print("-" * 50)
    for dim_key, dim_result in scores["dimension_scores"].items():
        name = dim_result["name"]
        sc = dim_result["score"]
        gl = dim_result["grade_letter"]
        print(f"  {name: <8} [{gl}]  {_score_bar(sc, 20)}")
    print()

    # 生成并输出详细反馈报告
    feedback_report = generate_feedback(paper_data, scores)
    print(feedback_report)
    print()

    # 生成改进计划（使用默认档案）
    default_profile = {
        "display_name": "演示用户",
        "level": 2,
        "skill_scores": {
            "literature_mining": 60,
            "outline_writing": 55,
            "section_drafting": 50,
            "peer_review": 65,
            "revision_polish": 55,
        },
    }
    plan = generate_improvement_plan(scores, default_profile)
    print()
    print(plan["plan_text"])


if __name__ == "__main__":
    main()
