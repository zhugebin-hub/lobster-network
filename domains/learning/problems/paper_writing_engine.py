"""
自动论文撰写引擎 V1.0
=====================

支持：
1. 选题评估（新颖性/可行性/学术价值/影响力）—— 多因子加权模型
2. 大纲生成（基于论文结构模板）
3. 摘要质量评估（完整性/简洁性/关键词覆盖）
4. 文献综述评估（覆盖度/时效性/批判性）
5. 方法论评估（严谨性/可复现性/创新性）
6. 论文整体评分（多维度综合）
7. 引用格式检测（GB/T 7714 / APA / IEEE）
8. 查重预估（基于文本相似度启发式）

设计参考：domains/learning/problems/stock_predict_engine.py
"""

import json
import os
import math
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ========== 学科领域权重 ==========
DISCIPLINE_BIAS = {
    "计算机科学": 0.08, "人工智能": 0.12, "软件工程": 0.06,
    "通信工程": 0.05, "电子科学": 0.04, "机械工程": 0.02,
    "材料科学": 0.03, "生物医学": 0.04, "化学": 0.02,
    "物理学": 0.03, "数学": 0.01, "经济学": 0.05,
    "管理学": 0.03, "教育学": 0.02, "文学": 0.00,
    "哲学": -0.01, "历史学": 0.00, "法学": 0.02,
    "环境科学": 0.04, "能源科学": 0.06, "default": 0.00,
}

# ========== 论文结构模板 ==========
PAPER_STRUCTURES = {
    "empirical": {  # 实证研究
        "name": "实证研究型",
        "sections": ["引言", "文献综述", "研究假设", "研究方法", "数据分析", "研究结果", "讨论", "结论", "参考文献"],
        "weights": {"引言": 0.10, "文献综述": 0.15, "研究假设": 0.08, "研究方法": 0.15, "数据分析": 0.15, "研究结果": 0.15, "讨论": 0.12, "结论": 0.07, "参考文献": 0.03},
    },
    "theoretical": {  # 理论研究
        "name": "理论研究型",
        "sections": ["引言", "概念界定", "理论框架", "命题推演", "理论验证", "讨论", "结论", "参考文献"],
        "weights": {"引言": 0.12, "概念界定": 0.15, "理论框架": 0.20, "命题推演": 0.18, "理论验证": 0.15, "讨论": 0.10, "结论": 0.07, "参考文献": 0.03},
    },
    "review": {  # 综述论文
        "name": "综述研究型",
        "sections": ["引言", "检索策略", "主题分类", "研究趋势", "挑战与机遇", "未来方向", "结论", "参考文献"],
        "weights": {"引言": 0.10, "检索策略": 0.10, "主题分类": 0.20, "研究趋势": 0.15, "挑战与机遇": 0.15, "未来方向": 0.15, "结论": 0.10, "参考文献": 0.05},
    },
    "case_study": {  # 案例研究
        "name": "案例研究型",
        "sections": ["引言", "案例背景", "研究方法", "案例描述", "分析讨论", "启示与建议", "结论", "参考文献"],
        "weights": {"引言": 0.10, "案例背景": 0.12, "研究方法": 0.13, "案例描述": 0.20, "分析讨论": 0.20, "启示与建议": 0.12, "结论": 0.08, "参考文献": 0.05},
    },
}


class PaperWritingEngine:
    """自动论文撰写引擎"""

    def __init__(self, problems_dir: str = None):
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                "problems", "paper-writing"
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()

    def _load_problems(self):
        for phase in ["phase1", "phase2", "phase3"]:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, "problems.json")
            if os.path.exists(problems_file):
                with open(problems_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.phases[phase] = data

    def get_problems(self, phase: str = None, problem_type: str = None,
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        problems = []
        phases_to_check = [phase] if phase else list(self.phases.keys())
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]["problems"]:
                if problem_type and prob.get("type") != problem_type:
                    continue
                if difficulty and prob.get("difficulty") != difficulty:
                    continue
                problems.append(prob)
        return problems[:limit]

    # ========================================================
    # 选题评估：多因子加权模型
    # ========================================================
    def evaluate_topic(self, topic: str, discipline: str = "default",
                       novelty: float = 0.5, feasibility: float = 0.5,
                       academic_value: float = 0.5, impact: float = 0.5,
                       data_availability: float = 0.5,
                       existing_papers: int = 100) -> Dict:
        """
        选题质量评估（多因子加权模型）

        Args:
            topic: 论文题目
            discipline: 学科领域
            novelty: 新颖性 (0-1)
            feasibility: 可行性 (0-1)
            academic_value: 学术价值 (0-1)
            impact: 影响力 (0-1)
            data_availability: 数据可得性 (0-1)
            existing_papers: 已有相关论文数

        Returns:
            选题评估结果
        """
        # 基础分
        score = 0.5

        # 因子1：新颖性（权重 0.25）
        score += (novelty - 0.5) * 0.25

        # 因子2：可行性（权重 0.20）
        score += (feasibility - 0.5) * 0.20

        # 因子3：学术价值（权重 0.20）
        score += (academic_value - 0.5) * 0.20

        # 因子4：影响力（权重 0.15）
        score += (impact - 0.5) * 0.15

        # 因子5：数据可得性（权重 0.10）
        score += (data_availability - 0.5) * 0.10

        # 因子6：学科景气度
        disc_bias = DISCIPLINE_BIAS.get(discipline, DISCIPLINE_BIAS["default"])
        score += disc_bias

        # 因子7：竞争度（已有论文数）
        if existing_papers < 10:
            score += 0.05  # 蓝海领域
        elif existing_papers < 50:
            score += 0.02  # 适度竞争
        elif existing_papers > 500:
            score -= 0.05  # 红海领域
        elif existing_papers > 1000:
            score -= 0.08  # 过度饱和

        # 归一化
        score = max(0.0, min(1.0, score))

        # 评级
        if score >= 0.80:
            grade = "A（优秀选题）"
            recommendation = "强烈推荐，兼具创新性和可行性"
        elif score >= 0.65:
            grade = "B（良好选题）"
            recommendation = "推荐，建议进一步完善研究设计"
        elif score >= 0.50:
            grade = "C（一般选题）"
            recommendation = "可行但需提升创新性或缩小范围"
        elif score >= 0.35:
            grade = "D（较弱选题）"
            recommendation = "建议重新考虑选题方向"
        else:
            grade = "F（不推荐）"
            recommendation = "选题存在重大问题，建议更换"

        return {
            "topic": topic,
            "discipline": discipline,
            "score": round(score, 3),
            "grade": grade,
            "recommendation": recommendation,
            "factors": {
                "novelty": novelty,
                "feasibility": feasibility,
                "academic_value": academic_value,
                "impact": impact,
                "data_availability": data_availability,
                "existing_papers": existing_papers,
                "discipline_bias": disc_bias,
            },
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 大纲生成：基于论文结构模板
    # ========================================================
    def generate_outline(self, topic: str, paper_type: str = "empirical",
                         target_words: int = 8000) -> Dict:
        """
        生成论文大纲

        Args:
            topic: 论文题目
            paper_type: 论文类型 (empirical/theoretical/review/case_study)
            target_words: 目标字数

        Returns:
            论文大纲
        """
        if paper_type not in PAPER_STRUCTURES:
            paper_type = "empirical"

        structure = PAPER_STRUCTURES[paper_type]
        sections = []

        for i, section_name in enumerate(structure["sections"]):
            weight = structure["weights"].get(section_name, 0.10)
            word_count = int(target_words * weight)
            sections.append({
                "order": i + 1,
                "name": section_name,
                "target_words": word_count,
                "weight": weight,
                "key_points": self._get_section_key_points(section_name, paper_type),
            })

        return {
            "topic": topic,
            "paper_type": paper_type,
            "type_name": structure["name"],
            "target_words": target_words,
            "sections": sections,
            "section_count": len(sections),
            "timestamp": datetime.now().isoformat(),
        }

    def _get_section_key_points(self, section_name: str, paper_type: str) -> List[str]:
        """获取各章节关键要点"""
        key_points_map = {
            "引言": ["研究背景", "研究问题", "研究意义", "论文结构概述"],
            "文献综述": ["国内外研究现状", "研究脉络梳理", "研究空白识别", "本文定位"],
            "研究假设": ["假设提出", "理论依据", "假设表述"],
            "研究方法": ["研究设计", "数据来源", "变量定义", "分析方法"],
            "数据分析": ["描述性统计", "相关性分析", "回归分析/模型检验", "稳健性检验"],
            "研究结果": ["主要发现", "假设检验结果", "效应量", "结果可视化"],
            "讨论": ["结果解释", "与已有研究对比", "理论贡献", "实践启示"],
            "结论": ["研究总结", "研究局限", "未来展望"],
            "参考文献": ["格式规范", "引用完整性", "时效性"],
            "概念界定": ["核心概念", "概念关系", "操作化定义"],
            "理论框架": ["理论基础", "框架构建", "命题提出"],
            "命题推演": ["逻辑推演", "命题表述", "边界条件"],
            "理论验证": ["验证方法", "案例佐证", "逻辑一致性"],
            "检索策略": ["数据库选择", "检索词", "筛选标准", "PRISMA流程"],
            "主题分类": ["分类维度", "主题聚类", "研究图谱"],
            "研究趋势": ["时间趋势", "方法演进", "热点迁移"],
            "挑战与机遇": ["现存挑战", "技术瓶颈", "发展机遇"],
            "未来方向": ["研究空白", "新兴方向", "跨学科融合"],
            "案例背景": ["案例选择依据", "背景描述", "数据来源"],
            "案例描述": ["事件 timeline", "关键决策", "利益相关者"],
            "分析讨论": ["理论框架应用", "多角度分析", "比较分析"],
            "启示与建议": ["理论启示", "实践建议", "政策建议"],
        }
        return key_points_map.get(section_name, ["待补充关键要点"])

    # ========================================================
    # 摘要质量评估
    # ========================================================
    def evaluate_abstract(self, abstract: str, target_words: int = 300,
                          has_keywords: bool = True,
                          keyword_count: int = 5) -> Dict:
        """
        摘要质量评估

        Args:
            abstract: 摘要文本
            target_words: 目标字数
            has_keywords: 是否有关键词
            keyword_count: 关键词数量

        Returns:
            摘要评估结果
        """
        actual_words = len(abstract)
        sentences = re.split(r'[。！？.!?]', abstract)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 完整性：是否包含目的/方法/结果/结论
        completeness_keywords = {
            "目的": ["目的", "旨在", "为了", "研究目的", "本文"],
            "方法": ["方法", "采用", "基于", "利用", "通过"],
            "结果": ["结果", "发现", "表明", "显示", "得到"],
            "结论": ["结论", "综上", "总之", "启示", "建议"],
        }
        completeness = {}
        for dim, keywords in completeness_keywords.items():
            found = any(kw in abstract for kw in keywords)
            completeness[dim] = found

        completeness_score = sum(completeness.values()) / len(completeness) if completeness else 0

        # 简洁性：字数是否适中
        word_ratio = actual_words / target_words if target_words > 0 else 1
        if 0.8 <= word_ratio <= 1.2:
            conciseness = 1.0
        elif 0.6 <= word_ratio <= 1.5:
            conciseness = 0.7
        else:
            conciseness = 0.4

        # 关键词覆盖
        keyword_score = 1.0 if (has_keywords and 3 <= keyword_count <= 8) else 0.5

        # 综合评分
        overall = completeness_score * 0.5 + conciseness * 0.3 + keyword_score * 0.2

        return {
            "actual_words": actual_words,
            "target_words": target_words,
            "word_ratio": round(word_ratio, 2),
            "sentence_count": len(sentences),
            "completeness": completeness,
            "completeness_score": round(completeness_score, 3),
            "conciseness_score": round(conciseness, 3),
            "keyword_score": round(keyword_score, 3),
            "overall_score": round(overall, 3),
            "issues": self._identify_abstract_issues(completeness, word_ratio, has_keywords, keyword_count),
            "timestamp": datetime.now().isoformat(),
        }

    def _identify_abstract_issues(self, completeness: Dict, word_ratio: float,
                                   has_keywords: bool, keyword_count: int) -> List[str]:
        issues = []
        for dim, found in completeness.items():
            if not found:
                issues.append(f"缺少{dim}要素")
        if word_ratio > 1.5:
            issues.append("摘要过长，建议精简")
        elif word_ratio < 0.6:
            issues.append("摘要过短，建议补充内容")
        if not has_keywords:
            issues.append("缺少关键词")
        elif keyword_count < 3:
            issues.append("关键词数量不足")
        elif keyword_count > 8:
            issues.append("关键词过多")
        return issues

    # ========================================================
    # 文献综述评估
    # ========================================================
    def evaluate_literature_review(self, total_refs: int, recent_refs: int = 0,
                                    chinese_refs: int = 0, english_refs: int = 0,
                                    years_span: int = 10, has_critique: bool = True,
                                    has_gap_analysis: bool = True) -> Dict:
        """
        文献综述质量评估

        Args:
            total_refs: 参考文献总数
            recent_refs: 近3年文献数
            chinese_refs: 中文文献数
            english_refs: 英文文献数
            years_span: 文献时间跨度（年）
            has_critique: 是否有批判性分析
            has_gap_analysis: 是否有研究空白分析

        Returns:
            文献综述评估结果
        """
        # 覆盖度
        if total_refs >= 50:
            coverage = 1.0
        elif total_refs >= 30:
            coverage = 0.8
        elif total_refs >= 15:
            coverage = 0.6
        elif total_refs >= 5:
            coverage = 0.4
        else:
            coverage = 0.2

        # 时效性
        recency_ratio = recent_refs / total_refs if total_refs > 0 else 0
        if recency_ratio >= 0.4:
            recency = 1.0
        elif recency_ratio >= 0.25:
            recency = 0.7
        else:
            recency = 0.4

        # 中英文平衡
        total_lang = chinese_refs + english_refs
        if total_lang > 0:
            lang_balance = 1.0 - abs(chinese_refs - english_refs) / total_lang
        else:
            lang_balance = 0.3

        # 批判性
        critique_score = 1.0 if has_critique else 0.3

        # 研究空白
        gap_score = 1.0 if has_gap_analysis else 0.3

        # 综合
        overall = (coverage * 0.25 + recency * 0.20 + lang_balance * 0.15 +
                   critique_score * 0.20 + gap_score * 0.20)

        return {
            "total_refs": total_refs,
            "recent_refs": recent_refs,
            "recency_ratio": round(recency_ratio, 3),
            "chinese_refs": chinese_refs,
            "english_refs": english_refs,
            "years_span": years_span,
            "coverage_score": round(coverage, 3),
            "recency_score": round(recency, 3),
            "language_balance": round(lang_balance, 3),
            "critique_score": round(critique_score, 3),
            "gap_analysis_score": round(gap_score, 3),
            "overall_score": round(overall, 3),
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 方法论评估
    # ========================================================
    def evaluate_methodology(self, has_research_design: bool = True,
                             has_data_source: bool = True,
                             has_variables: bool = True,
                             has_analysis_method: bool = True,
                             has_reliability: bool = False,
                             has_validity: bool = False,
                             reproducible: bool = False,
                             innovative_method: bool = False) -> Dict:
        """
        方法论严谨性评估

        Args:
            has_research_design: 有研究设计
            has_data_source: 有数据来源说明
            has_variables: 有变量定义
            has_analysis_method: 有分析方法
            has_reliability: 有信度检验
            has_validity: 有效度检验
            reproducible: 可复现
            innovative_method: 方法创新

        Returns:
            方法论评估结果
        """
        checks = {
            "research_design": has_research_design,
            "data_source": has_data_source,
            "variables": has_variables,
            "analysis_method": has_analysis_method,
            "reliability": has_reliability,
            "validity": has_validity,
            "reproducibility": reproducible,
            "innovation": innovative_method,
        }

        # 基础项权重
        weights = {
            "research_design": 0.20,
            "data_source": 0.15,
            "variables": 0.10,
            "analysis_method": 0.15,
            "reliability": 0.10,
            "validity": 0.10,
            "reproducibility": 0.10,
            "innovation": 0.10,
        }

        score = sum(weights[k] for k, v in checks.items() if v)

        if score >= 0.80:
            grade = "A（方法论严谨）"
        elif score >= 0.60:
            grade = "B（方法论合格）"
        elif score >= 0.40:
            grade = "C（方法论有缺陷）"
        else:
            grade = "D（方法论不足）"

        return {
            "checks": checks,
            "score": round(score, 3),
            "grade": grade,
            "missing": [k for k, v in checks.items() if not v],
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 论文整体评分
    # ========================================================
    def evaluate_paper(self, topic_score: float = 0.7,
                       abstract_score: float = 0.7,
                       literature_score: float = 0.7,
                       methodology_score: float = 0.7,
                       results_score: float = 0.7,
                       discussion_score: float = 0.7,
                       writing_quality: float = 0.7,
                       formatting: float = 0.8) -> Dict:
        """
        论文整体质量评分（多维度综合）

        Args:
            topic_score: 选题质量 (0-1)
            abstract_score: 摘要质量 (0-1)
            literature_score: 文献综述质量 (0-1)
            methodology_score: 方法论质量 (0-1)
            results_score: 结果质量 (0-1)
            discussion_score: 讨论质量 (0-1)
            writing_quality: 写作质量 (0-1)
            formatting: 格式规范 (0-1)

        Returns:
            论文整体评分
        """
        dimensions = {
            "选题质量": {"score": topic_score, "weight": 0.10},
            "摘要质量": {"score": abstract_score, "weight": 0.08},
            "文献综述": {"score": literature_score, "weight": 0.15},
            "方法论": {"score": methodology_score, "weight": 0.20},
            "研究结果": {"score": results_score, "weight": 0.17},
            "讨论": {"score": discussion_score, "weight": 0.12},
            "写作质量": {"score": writing_quality, "weight": 0.10},
            "格式规范": {"score": formatting, "weight": 0.08},
        }

        overall = sum(d["score"] * d["weight"] for d in dimensions.values())

        if overall >= 0.85:
            grade = "A（优秀）"
            recommendation = "达到顶刊投稿水平"
        elif overall >= 0.75:
            grade = "B（良好）"
            recommendation = "达到核心期刊投稿水平"
        elif overall >= 0.60:
            grade = "C（合格）"
            recommendation = "达到普通期刊/会议投稿水平"
        elif overall >= 0.45:
            grade = "D（需修改）"
            recommendation = "需要大幅修改后重新评估"
        else:
            grade = "F（不合格）"
            recommendation = "需重新撰写"

        return {
            "dimensions": dimensions,
            "overall_score": round(overall, 3),
            "grade": grade,
            "recommendation": recommendation,
            "weakest": min(dimensions.items(), key=lambda x: x[1]["score"])[0],
            "strongest": max(dimensions.items(), key=lambda x: x[1]["score"])[0],
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 引用格式检测
    # ========================================================
    def check_citations(self, citations: List[str],
                        format_type: str = "gbt7714") -> Dict:
        """
        引用格式检测

        Args:
            citations: 引用文本列表
            format_type: 格式类型 (gbt7714/apa/ieee)

        Returns:
            格式检测结果
        """
        format_patterns = {
            "gbt7714": {
                "name": "GB/T 7714",
                "pattern": r"^\[?\d+\]?\s*.+?\.\s*.+?[,\.\[].+?\d{4}",
                "example": "[1] 作者. 题名[J]. 刊名, 年, 卷(期): 页码.",
            },
            "apa": {
                "name": "APA",
                "pattern": r"^.+?\s*\(\d{4}\)\.",
                "example": "Author, A. (2024). Title. Journal, vol(iss), pages.",
            },
            "ieee": {
                "name": "IEEE",
                "pattern": r"^\[?\d+\]?\s*A\..+?,\s*\".+?\"",
                "example": "[1] A. Author, \"Title,\" Journal, vol, 2024.",
            },
        }

        pattern_info = format_patterns.get(format_type, format_patterns["gbt7714"])
        pattern = re.compile(pattern_info["pattern"])

        correct = 0
        errors = []
        for i, cite in enumerate(citations):
            if pattern.match(cite.strip()):
                correct += 1
            else:
                errors.append({"index": i, "citation": cite, "issue": "格式不符合规范"})

        total = len(citations)
        compliance = correct / total if total > 0 else 0

        return {
            "format_type": format_type,
            "format_name": pattern_info["name"],
            "total_citations": total,
            "correct": correct,
            "errors": errors,
            "compliance_rate": round(compliance, 3),
            "example": pattern_info["example"],
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 查重预估（启发式）
    # ========================================================
    def estimate_similarity(self, paper_text: str,
                            reference_texts: List[str] = None) -> Dict:
        """
        查重预估（基于文本相似度启发式）

        Args:
            paper_text: 论文文本
            reference_texts: 参考文本列表

        Returns:
            查重预估结果
        """
        if not reference_texts:
            # 模拟参考文本
            reference_texts = [
                "随着人工智能技术的快速发展，深度学习在各个领域得到了广泛应用。",
                "本文提出了一种基于Transformer架构的新方法，通过实验验证了其有效性。",
                "研究结果表明，该方法在准确率和效率方面均优于现有方法。",
            ]

        # 计算 n-gram 重叠
        def get_ngrams(text, n=3):
            text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
            return set(text[i:i+n] for i in range(len(text) - n + 1))

        paper_ngrams = get_ngrams(paper_text)
        max_similarity = 0
        avg_similarity = 0

        for ref in reference_texts:
            ref_ngrams = get_ngrams(ref)
            if not ref_ngrams:
                continue
            overlap = len(paper_ngrams & ref_ngrams)
            sim = overlap / len(ref_ngrams) if ref_ngrams else 0
            max_similarity = max(max_similarity, sim)
            avg_similarity += sim

        avg_similarity = avg_similarity / len(reference_texts) if reference_texts else 0

        # 预估查重率
        estimated_rate = avg_similarity * 0.6 + max_similarity * 0.4

        if estimated_rate < 0.10:
            risk = "低风险"
        elif estimated_rate < 0.20:
            risk = "中风险"
        elif estimated_rate < 0.30:
            risk = "高风险"
        else:
            risk = "极高风险"

        return {
            "estimated_similarity": round(estimated_rate, 3),
            "max_similarity": round(max_similarity, 3),
            "avg_similarity": round(avg_similarity, 3),
            "risk_level": risk,
            "threshold": 0.15,
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 同行评审模拟
    # ========================================================
    def simulate_peer_review(self, paper_score: Dict) -> Dict:
        """
        模拟同行评审意见

        Args:
            paper_score: 论文整体评分结果

        Returns:
            评审意见
        """
        score = paper_score.get("overall_score", 0.5)
        weakest = paper_score.get("weakest", "未知")
        strongest = paper_score.get("strongest", "未知")

        if score >= 0.85:
            decision = "Accept（接收）"
            comments = [
                f"本文在{strongest}方面表现突出，具有较高的学术价值。",
                "研究方法严谨，数据分析充分，结论可信。",
                "建议在最终版本中检查排版细节。",
            ]
        elif score >= 0.70:
            decision = "Minor Revision（小修）"
            comments = [
                f"本文整体质量较好，{strongest}部分值得肯定。",
                f"建议加强{weakest}部分的论述。",
                "补充部分实验细节以提高可复现性。",
            ]
        elif score >= 0.55:
            decision = "Major Revision（大修）"
            comments = [
                f"本文{weakest}部分存在明显不足，需重点修改。",
                "建议重新梳理研究逻辑，加强文献支撑。",
                "方法论部分需要更详细的说明。",
            ]
        else:
            decision = "Reject（拒稿）"
            comments = [
                f"本文在多个维度存在不足，尤其是{weakest}。",
                "研究问题和贡献不清晰。",
                "建议重新设计研究方案后重新投稿。",
            ]

        return {
            "decision": decision,
            "score": score,
            "strengths": [strongest],
            "weaknesses": [weakest],
            "comments": comments,
            "timestamp": datetime.now().isoformat(),
        }


# 演示
if __name__ == "__main__":
    engine = PaperWritingEngine()

    print("=" * 60)
    print("🦞 小龙虾网络 · 自动论文撰写引擎 V1.0")
    print("=" * 60)

    # 1. 选题评估
    print("\n📊 选题评估:")
    topic_result = engine.evaluate_topic(
        topic="基于大语言模型的智能体自主任务分解方法研究",
        discipline="人工智能",
        novelty=0.85, feasibility=0.70, academic_value=0.90,
        impact=0.80, data_availability=0.65, existing_papers=120,
    )
    print(f"  题目：{topic_result['topic']}")
    print(f"  评分：{topic_result['score']:.3f}")
    print(f"  等级：{topic_result['grade']}")
    print(f"  建议：{topic_result['recommendation']}")

    # 2. 大纲生成
    print("\n📝 大纲生成:")
    outline = engine.generate_outline(
        topic="基于大语言模型的智能体自主任务分解方法研究",
        paper_type="empirical", target_words=8000,
    )
    print(f"  类型：{outline['type_name']}")
    print(f"  章节数：{outline['section_count']}")
    for s in outline["sections"]:
        print(f"  [{s['order']}] {s['name']}（{s['target_words']}字, {s['weight']:.0%}）")

    # 3. 摘要评估
    print("\n📋 摘要评估:")
    abstract = "本文旨在研究基于大语言模型的智能体自主任务分解方法。通过设计递归分解框架，利用GPT-4作为推理引擎，将复杂任务自动分解为可执行的子任务序列。实验结果表明，该方法在多个基准测试中的任务完成率达到87.3%，优于现有方法。结论表明，递归分解策略能有效提升智能体的自主性和可靠性。"
    abs_result = engine.evaluate_abstract(abstract, target_words=300, has_keywords=True, keyword_count=5)
    print(f"  完整性：{abs_result['completeness_score']:.1%}")
    print(f"  简洁性：{abs_result['conciseness_score']:.1%}")
    print(f"  综合：{abs_result['overall_score']:.1%}")
    if abs_result["issues"]:
        print(f"  问题：{', '.join(abs_result['issues'])}")

    # 4. 文献综述评估
    print("\n📚 文献综述评估:")
    lit_result = engine.evaluate_literature_review(
        total_refs=45, recent_refs=18, chinese_refs=15, english_refs=30,
        years_span=10, has_critique=True, has_gap_analysis=True,
    )
    print(f"  覆盖度：{lit_result['coverage_score']:.1%}")
    print(f"  时效性：{lit_result['recency_score']:.1%}")
    print(f"  综合：{lit_result['overall_score']:.1%}")

    # 5. 方法论评估
    print("\n🔬 方法论评估:")
    method_result = engine.evaluate_methodology(
        has_research_design=True, has_data_source=True, has_variables=True,
        has_analysis_method=True, has_reliability=True, has_validity=True,
        reproducible=True, innovative_method=True,
    )
    print(f"  评分：{method_result['score']:.1%}")
    print(f"  等级：{method_result['grade']}")
    if method_result["missing"]:
        print(f"  缺失：{', '.join(method_result['missing'])}")

    # 6. 论文整体评分
    print("\n🏆 论文整体评分:")
    paper_result = engine.evaluate_paper(
        topic_score=0.85, abstract_score=0.78, literature_score=0.72,
        methodology_score=0.80, results_score=0.75, discussion_score=0.70,
        writing_quality=0.78, formatting=0.85,
    )
    print(f"  总分：{paper_result['overall_score']:.1%}")
    print(f"  等级：{paper_result['grade']}")
    print(f"  建议：{paper_result['recommendation']}")
    print(f"  最强项：{paper_result['strongest']}")
    print(f"  最弱项：{paper_result['weakest']}")

    # 7. 同行评审模拟
    print("\n👨‍⚖️ 同行评审模拟:")
    review = engine.simulate_peer_review(paper_result)
    print(f"  决定：{review['decision']}")
    for c in review["comments"]:
        print(f"  - {c}")

    # 8. 题库统计
    print("\n📚 题库统计:")
    for phase, data in engine.phases.items():
        print(f"  {phase}: {data['name']} - {len(data['problems'])} 题")

    print("\n" + "=" * 60)
    print("✅ 自动论文撰写引擎测试完成！")
