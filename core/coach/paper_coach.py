#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文写作教练模块 (Paper Writing Coach)
========================================

龙虾网络论文写作训练系统的教练组件。
负责分析每位学员的论文写作进度，评估8个维度的能力水平，
生成个性化改进计划，并输出教练报告与 Hermes 风格指令。

模式：纯函数式 + 文件系统轮询，无 OOP。
数据源：/shared/training/paper/{player}/profile.json
输出：
  - /shared/training/paper/paper_coach_report.json
  - /shared/messages/from-hermes/hermes-paper-*.json
"""

import json
import os
import time
import glob
import datetime
import copy

# ─────────────────────────────────────────────
# 常量定义
# ─────────────────────────────────────────────

# 共享文件系统根路径
SHARED_ROOT = "/shared"

# 论文训练目录
PAPER_TRAINING_DIR = os.path.join(SHARED_ROOT, "training", "paper")

# Hermes 消息输出目录
HERMES_MESSAGES_DIR = os.path.join(SHARED_ROOT, "messages", "from-hermes")

# 教练报告输出路径
COACH_REPORT_PATH = os.path.join(PAPER_TRAINING_DIR, "paper_coach_report.json")

# 学员列表及其角色定义
PLAYERS = {
    "qoder": {
        "role": "analytical_specialist",
        "description": "分析型专家，擅长方法论与逻辑推理",
        "strengths": ["methodology", "structure"],
        "weaknesses": ["abstract", "argumentation"],
    },
    "xiaochen": {
        "role": "empirical_specialist",
        "description": "实证型专家，擅长数据分析与实验设计",
        "strengths": ["data_analysis", "methodology"],
        "weaknesses": ["literature_review", "formatting"],
    },
    "zhuguxia": {
        "role": "survey_specialist",
        "description": "综述型专家，擅长文献综述与知识梳理",
        "strengths": ["literature_review", "citations"],
        "weaknesses": ["data_analysis", "methodology"],
    },
    "professor_zhuge": {
        "role": "reviewer",
        "description": "审稿人角色，负责论文评审与质量把控",
        "strengths": ["argumentation", "formatting"],
        "weaknesses": ["structure", "abstract"],
    },
    "lobster-001": {
        "role": "protocol_architect",
        "description": "协议架构师，擅长系统架构设计与协议分析",
        "strengths": ["methodology", "structure"],
        "weaknesses": ["formatting", "abstract"],
    },
    "museum-001": {
        "role": "digital_archivist",
        "description": "数字档案员，擅长文献综述与知识管理",
        "strengths": ["literature_review", "citations"],
        "weaknesses": ["data_analysis", "methodology"],
    },
}

# 论文评估的8个维度
DIMENSIONS = [
    "structure",           # 论文结构
    "abstract",            # 摘要质量
    "literature_review",   # 文献综述
    "methodology",         # 方法论
    "data_analysis",       # 数据分析
    "argumentation",       # 论证逻辑
    "formatting",          # 格式规范
    "citations",           # 引用规范
]

# 维度中文名映射
DIMENSION_NAMES_ZH = {
    "structure": "论文结构",
    "abstract": "摘要质量",
    "literature_review": "文献综述",
    "methodology": "方法论",
    "data_analysis": "数据分析",
    "argumentation": "论证逻辑",
    "formatting": "格式规范",
    "citations": "引用规范",
}

# 各维度达标分数线
DIMENSION_THRESHOLDS = {
    "structure": 75,
    "abstract": 70,
    "literature_review": 70,
    "methodology": 80,
    "data_analysis": 75,
    "argumentation": 75,
    "formatting": 80,
    "citations": 70,
}

# 训练阶段定义
PHASES = {
    1: "基础规范训练",
    2: "专项能力强化",
    3: "综合论文写作",
    4: "高阶审稿互评",
    5: "发表级别打磨",
}

# 每个维度对应的练习库
EXERCISE_LIBRARY = {
    "structure": [
        {"name": "大纲重构练习", "desc": "给定一篇混乱结构的论文，重新组织大纲层级", "difficulty": 2},
        {"name": "段落逻辑链训练", "desc": "为每段写出承上启下的过渡句", "difficulty": 1},
        {"name": "IMRaD结构模仿", "desc": "按照IMRaD框架重写给定摘要", "difficulty": 3},
        {"name": "章节比例优化", "desc": "调整各章节篇幅占比至合理范围", "difficulty": 2},
    ],
    "abstract": [
        {"name": "摘要精炼训练", "desc": "将3000字论文压缩为200字摘要", "difficulty": 2},
        {"name": "关键词提取练习", "desc": "从论文中提取5-8个高质量关键词", "difficulty": 1},
        {"name": "结构化摘要写作", "desc": "按目的/方法/结果/结论四段式写摘要", "difficulty": 3},
        {"name": "英文摘要翻译", "desc": "将中文摘要翻译为学术英文", "difficulty": 3},
    ],
    "literature_review": [
        {"name": "文献分类整理", "desc": "将20篇文献按主题/方法/时间线分类", "difficulty": 1},
        {"name": "文献综述段落写作", "desc": "围绕一个子主题写300字综述段落", "difficulty": 2},
        {"name": "研究缺口识别", "desc": "从文献综述中推导出3个研究缺口", "difficulty": 3},
        {"name": "文献对比矩阵", "desc": "构建文献对比矩阵，横向比较方法与结论", "difficulty": 3},
    ],
    "methodology": [
        {"name": "变量操作化练习", "desc": "将抽象概念转化为可测量的变量", "difficulty": 2},
        {"name": "实验设计模拟", "desc": "设计一个2x2析因实验方案", "difficulty": 3},
        {"name": "方法论辩护写作", "desc": "为选定方法写出300字辩护段落", "difficulty": 3},
        {"name": "信效度分析练习", "desc": "评估问卷的信度与效度指标", "difficulty": 2},
    ],
    "data_analysis": [
        {"name": "描述统计报告", "desc": "对给定数据集写出完整描述统计", "difficulty": 1},
        {"name": "回归结果解读", "desc": "解读回归分析表格并写出500字分析", "difficulty": 2},
        {"name": "图表规范制作", "desc": "按学术规范制作数据可视化图表", "difficulty": 2},
        {"name": "稳健性检验设计", "desc": "设计至少两种稳健性检验方案", "difficulty": 3},
    ],
    "argumentation": [
        {"name": "论点-论据匹配", "desc": "为给定论点匹配最有力的论据", "difficulty": 1},
        {"name": "反驳与回应写作", "desc": "预设3个审稿人可能提出的质疑并写回应", "difficulty": 3},
        {"name": "因果推理链条", "desc": "构建从假设到结论的完整因果推理链", "difficulty": 2},
        {"name": "理论贡献提炼", "desc": "从研究发现中提炼理论贡献", "difficulty": 3},
    ],
    "formatting": [
        {"name": "APA格式校对", "desc": "校对并修正论文中的APA格式错误", "difficulty": 1},
        {"name": "图表标题规范化", "desc": "统一所有图表标题的命名规范", "difficulty": 1},
        {"name": "页眉页脚设置", "desc": "按期刊要求设置页眉页脚与页码", "difficulty": 2},
        {"name": "参考文献格式统一", "desc": "统一参考文献条目格式", "difficulty": 2},
    ],
    "citations": [
        {"name": "引用准确性检查", "desc": "核实正文引用与参考文献列表的一致性", "difficulty": 1},
        {"name": "引用密度优化", "desc": "调整各段落引用密度至合理水平", "difficulty": 2},
        {"name": "经典文献补充", "desc": "补充遗漏的经典与前沿文献引用", "difficulty": 2},
        {"name": "二次引用规范", "desc": "将二次引用改为原始文献引用", "difficulty": 3},
    ],
}

# 轮询间隔（秒）
POLL_INTERVAL = 60

# 最大轮询次数（0 表示无限）
MAX_POLL_ITERATIONS = 0


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────

def log(message):
    """打印带时间戳的日志信息"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[PaperCoach {timestamp}] {message}")


def load_json(filepath):
    """
    从指定路径加载 JSON 文件。

    参数:
        filepath (str): JSON 文件的绝对路径

    返回:
        dict/list/None: 解析后的数据，文件不存在或解析失败时返回 None
    """
    try:
        if not os.path.exists(filepath):
            log(f"[警告] 文件不存在: {filepath}")
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        log(f"[成功] 已加载: {filepath}")
        return data
    except json.JSONDecodeError as e:
        log(f"[错误] JSON 解析失败 {filepath}: {e}")
        return None
    except IOError as e:
        log(f"[错误] 文件读取失败 {filepath}: {e}")
        return None


def save_json(filepath, data):
    """
    将数据保存为 JSON 文件（自动创建目录）。

    参数:
        filepath (str): 输出文件的绝对路径
        data (dict/list): 要序列化的数据

    返回:
        bool: 保存成功返回 True，失败返回 False
    """
    try:
        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
            log(f"[创建] 目录: {dirpath}")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log(f"[成功] 已保存: {filepath}")
        return True
    except IOError as e:
        log(f"[错误] 文件保存失败 {filepath}: {e}")
        return False


def get_player_profile_path(player_key):
    """
    获取学员档案文件的完整路径。

    参数:
        player_key (str): 学员标识

    返回:
        str: profile.json 的绝对路径
    """
    return os.path.join(PAPER_TRAINING_DIR, player_key, "profile.json")


def ensure_default_profile(player_key):
    """
    确保学员档案存在。若不存在则创建默认档案。

    参数:
        player_key (str): 学员标识

    返回:
        dict: 学员档案数据
    """
    profile_path = get_player_profile_path(player_key)
    if os.path.exists(profile_path):
        profile = load_json(profile_path)
        if profile is not None:
            return profile

    # 构建默认档案
    player_info = PLAYERS.get(player_key, {})
    default_dimensions = {}
    for dim in DIMENSIONS:
        if dim in player_info.get("strengths", []):
            default_dimensions[dim] = 75  # 优势维度初始分较高
        elif dim in player_info.get("weaknesses", []):
            default_dimensions[dim] = 55  # 弱势维度初始分较低
        else:
            default_dimensions[dim] = 65  # 其他维度中等

    default_profile = {
        "player": player_key,
        "papers_written": 0,
        "avg_score": 0.0,
        "dimensions": default_dimensions,
        "papers": [],
        "exercises_completed": 0,
        "current_phase": 1,
    }

    save_json(profile_path, default_profile)
    log(f"[初始化] 已创建默认档案: {player_key}")
    return default_profile


# ─────────────────────────────────────────────
# 分析函数
# ─────────────────────────────────────────────

def analyze_player(player_key):
    """
    深度分析单个学员的论文写作能力。

    从档案中提取各维度分数、历史论文表现、训练进度，
    计算能力雷达图数据、薄弱维度排序、阶段适配度。

    参数:
        player_key (str): 学员标识

    返回:
        dict: 分析结果，包含以下字段:
            - player: 学员标识
            - role: 角色类型
            - dimension_scores: 各维度得分
            - weak_dimensions: 薄弱维度列表（低于阈值）
            - strong_dimensions: 优势维度列表（高于85分）
            - phase_readiness: 阶段就绪度评估
            - paper_trend: 论文分数趋势
            - recommended_exercises: 推荐练习列表
            - priority_dimension: 最需优先提升的维度
    """
    profile = ensure_default_profile(player_key)
    player_info = PLAYERS.get(player_key, {})
    dimensions = profile.get("dimensions", {})
    papers = profile.get("papers", [])
    current_phase = profile.get("current_phase", 1)

    # 识别薄弱维度与优势维度
    weak_dimensions = []
    strong_dimensions = []
    for dim in DIMENSIONS:
        score = dimensions.get(dim, 0)
        threshold = DIMENSION_THRESHOLDS.get(dim, 70)
        if score < threshold:
            weak_dimensions.append({
                "dimension": dim,
                "score": score,
                "threshold": threshold,
                "gap": threshold - score,
                "name_zh": DIMENSION_NAMES_ZH.get(dim, dim),
            })
        if score >= 85:
            strong_dimensions.append({
                "dimension": dim,
                "score": score,
                "name_zh": DIMENSION_NAMES_ZH.get(dim, dim),
            })

    # 按差距大小排序薄弱维度
    weak_dimensions.sort(key=lambda x: x["gap"], reverse=True)

    # 计算论文分数趋势
    paper_trend = "insufficient_data"
    if len(papers) >= 3:
        recent_scores = [p.get("score", 0) for p in papers[-5:]]
        if len(recent_scores) >= 2:
            diffs = [recent_scores[i+1] - recent_scores[i] for i in range(len(recent_scores)-1)]
            avg_diff = sum(diffs) / len(diffs)
            if avg_diff > 2:
                paper_trend = "improving"
            elif avg_diff < -2:
                paper_trend = "declining"
            else:
                paper_trend = "stable"

    # 阶段就绪度评估
    phase_readiness = _evaluate_phase_readiness(dimensions, current_phase)

    # 确定最优先提升的维度
    priority_dimension = None
    if weak_dimensions:
        priority_dimension = weak_dimensions[0]["dimension"]

    # 推荐练习
    recommended_exercises = _recommend_exercises(
        weak_dimensions, current_phase, profile.get("exercises_completed", 0)
    )

    analysis = {
        "player": player_key,
        "role": player_info.get("role", "unknown"),
        "role_description": player_info.get("description", ""),
        "dimension_scores": dimensions,
        "avg_score": profile.get("avg_score", 0.0),
        "papers_written": profile.get("papers_written", 0),
        "weak_dimensions": weak_dimensions,
        "strong_dimensions": strong_dimensions,
        "phase_readiness": phase_readiness,
        "current_phase": current_phase,
        "paper_trend": paper_trend,
        "priority_dimension": priority_dimension,
        "recommended_exercises": recommended_exercises,
        "exercises_completed": profile.get("exercises_completed", 0),
        "last_papers": papers[-3:] if papers else [],
    }

    log(f"[分析完成] {player_key}: 薄弱维度={len(weak_dimensions)}, "
        f"优势维度={len(strong_dimensions)}, 趋势={paper_trend}")
    return analysis


def _evaluate_phase_readiness(dimensions, current_phase):
    """
    评估学员是否准备好进入下一阶段。

    参数:
        dimensions (dict): 各维度分数
        current_phase (int): 当前阶段

    返回:
        dict: 包含 ready（是否就绪）、confidence（置信度）、notes（备注）
    """
    scores = list(dimensions.values())
    if not scores:
        return {"ready": False, "confidence": 0.0, "notes": "无维度分数数据"}

    avg = sum(scores) / len(scores)
    min_score = min(scores)

    # 阶段晋升条件：平均分 > 70 且最低分 > 60
    phase_thresholds = {
        1: {"avg_min": 65, "floor": 55},
        2: {"avg_min": 70, "floor": 60},
        3: {"avg_min": 75, "floor": 65},
        4: {"avg_min": 80, "floor": 70},
        5: {"avg_min": 85, "floor": 75},
    }

    threshold = phase_thresholds.get(current_phase, {"avg_min": 70, "floor": 60})
    avg_ok = avg >= threshold["avg_min"]
    floor_ok = min_score >= threshold["floor"]

    # 计算置信度
    if avg_ok and floor_ok:
        confidence = min(1.0, (avg - threshold["avg_min"] + 10) / 20.0)
        ready = True
        notes = f"平均分{avg:.1f}>=要求{threshold['avg_min']}，最低分{min_score}>=底线{threshold['floor']}，建议晋升"
    elif avg_ok:
        confidence = 0.4
        ready = False
        notes = f"平均分达标但存在短板维度(最低{min_score}<底线{threshold['floor']})，需专项补强"
    else:
        confidence = max(0.0, avg / threshold["avg_min"])
        ready = False
        notes = f"整体水平不足(均分{avg:.1f}<要求{threshold['avg_min']})，继续当前阶段训练"

    return {"ready": ready, "confidence": round(confidence, 2), "notes": notes}


def _recommend_exercises(weak_dimensions, current_phase, exercises_done):
    """
    为薄弱维度推荐具体练习。

    参数:
        weak_dimensions (list): 薄弱维度列表
        current_phase (int): 当前训练阶段
        exercises_done (int): 已完成练习数

    返回:
        list: 推荐的练习列表，每个包含 name/desc/dimension/difficulty
    """
    recommendations = []
    max_difficulty = min(current_phase + 1, 3)  # 难度不超过阶段+1

    for wd in weak_dimensions[:3]:  # 最多关注3个最薄弱维度
        dim = wd["dimension"]
        exercises = EXERCISE_LIBRARY.get(dim, [])
        suitable = [
            ex for ex in exercises
            if ex["difficulty"] <= max_difficulty
        ]
        # 按难度排序，优先推荐适中难度的练习
        suitable.sort(key=lambda x: abs(x["difficulty"] - current_phase))
        for ex in suitable[:2]:  # 每个维度最多推荐2个练习
            recommendations.append({
                "name": ex["name"],
                "desc": ex["desc"],
                "dimension": dim,
                "dimension_zh": DIMENSION_NAMES_ZH.get(dim, dim),
                "difficulty": ex["difficulty"],
                "priority": wd["gap"],
            })

    # 按优先级排序
    recommendations.sort(key=lambda x: x["priority"], reverse=True)
    return recommendations[:6]  # 最多推荐6个练习


# ─────────────────────────────────────────────
# 系统诊断与改进计划
# ─────────────────────────────────────────────

def diagnose_system():
    """
    诊断整个论文写作训练系统的状态。

    遍历所有学员，汇总系统级指标：
    - 总体进度分布
    - 共性问题
    - 阶段分布
    - 协同训练建议

    返回:
        dict: 系统诊断报告，包含:
            - total_players: 学员总数
            - active_players: 活跃学员数
            - phase_distribution: 各阶段学员分布
            - system_avg_score: 系统平均分数
            - common_weaknesses: 共性薄弱维度
            - collaboration_suggestions: 协同训练建议
            - alerts: 预警信息
    """
    all_analyses = []
    for player_key in PLAYERS:
        analysis = analyze_player(player_key)
        all_analyses.append(analysis)

    # 系统级统计
    total_players = len(all_analyses)
    active_players = sum(1 for a in all_analyses if a["papers_written"] > 0)
    total_papers = sum(a["papers_written"] for a in all_analyses)

    # 阶段分布
    phase_distribution = {}
    for a in all_analyses:
        phase = a["current_phase"]
        phase_name = PHASES.get(phase, f"阶段{phase}")
        phase_distribution[phase_name] = phase_distribution.get(phase_name, 0) + 1

    # 系统平均分
    scores = [a["avg_score"] for a in all_analyses if a["avg_score"] > 0]
    system_avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    # 共性薄弱维度统计
    weakness_counter = {}
    for a in all_analyses:
        for wd in a["weak_dimensions"]:
            dim = wd["dimension"]
            weakness_counter[dim] = weakness_counter.get(dim, 0) + 1
    common_weaknesses = [
        {"dimension": dim, "count": count, "name_zh": DIMENSION_NAMES_ZH.get(dim, dim)}
        for dim, count in sorted(weakness_counter.items(), key=lambda x: x[1], reverse=True)
    ]

    # 协同训练建议（优势互补的学员配对）
    collaboration_suggestions = _generate_collaboration_suggestions(all_analyses)

    # 预警
    alerts = []
    for a in all_analyses:
        if a["paper_trend"] == "declining":
            alerts.append({
                "level": "warning",
                "player": a["player"],
                "message": f"{a['player']} 论文分数呈下降趋势，需要关注",
            })
        if len(a["weak_dimensions"]) >= 5:
            alerts.append({
                "level": "critical",
                "player": a["player"],
                "message": f"{a['player']} 有{len(a['weak_dimensions'])}个维度未达标，需要密集训练",
            })
        if a["exercises_completed"] < 3 and a["papers_written"] > 2:
            alerts.append({
                "level": "info",
                "player": a["player"],
                "message": f"{a['player']} 练习完成数偏少，建议增加基础练习",
            })

    diagnosis = {
        "timestamp": datetime.datetime.now().isoformat(),
        "total_players": total_players,
        "active_players": active_players,
        "total_papers": total_papers,
        "phase_distribution": phase_distribution,
        "system_avg_score": system_avg_score,
        "common_weaknesses": common_weaknesses,
        "collaboration_suggestions": collaboration_suggestions,
        "alerts": alerts,
        "player_analyses": all_analyses,
    }

    log(f"[系统诊断] 学员={total_players}, 活跃={active_players}, "
        f"论文={total_papers}, 均分={system_avg_score}")
    return diagnosis


def _generate_collaboration_suggestions(analyses):
    """
    基于优势互补原则生成协同训练建议。

    参数:
        analyses (list): 所有学员的分析结果

    返回:
        list: 协同训练建议列表
    """
    suggestions = []
    players_list = list(analyses)

    for i in range(len(players_list)):
        for j in range(i + 1, len(players_list)):
            a = players_list[i]
            b = players_list[j]

            # 检查 A 的优势是否是 B 的弱势
            a_strong = set(s["dimension"] for s in a["strong_dimensions"])
            b_weak = set(w["dimension"] for w in b["weak_dimensions"])
            a_helps_b = a_strong & b_weak

            # 检查 B 的优势是否是 A 的弱势
            b_strong = set(s["dimension"] for s in b["strong_dimensions"])
            a_weak = set(w["dimension"] for w in a["weak_dimensions"])
            b_helps_a = b_strong & a_weak

            if a_helps_b or b_helps_a:
                suggestions.append({
                    "pair": [a["player"], b["player"]],
                    "a_helps_b": list(a_helps_b),
                    "b_helps_a": list(b_helps_a),
                    "mutual_benefit": bool(a_helps_b and b_helps_a),
                    "suggestion": _format_collaboration_text(
                        a["player"], b["player"], a_helps_b, b_helps_a
                    ),
                })

    # 优先推荐双向互补的配对
    suggestions.sort(key=lambda x: (x["mutual_benefit"], len(x["a_helps_b"]) + len(x["b_helps_a"])), reverse=True)
    return suggestions


def _format_collaboration_text(player_a, player_b, a_helps_b, b_helps_a):
    """
    格式化协同训练建议文本。

    参数:
        player_a (str): 学员A标识
        player_b (str): 学员B标识
        a_helps_b (set): A可帮助B的维度集合
        b_helps_a (set): B可帮助A的维度集合

    返回:
        str: 人类可读的协同训练建议
    """
    parts = []
    if a_helps_b:
        dims_zh = [DIMENSION_NAMES_ZH.get(d, d) for d in a_helps_b]
        parts.append(f"{player_a} 可在 {', '.join(dims_zh)} 方面指导 {player_b}")
    if b_helps_a:
        dims_zh = [DIMENSION_NAMES_ZH.get(d, d) for d in b_helps_a]
        parts.append(f"{player_b} 可在 {', '.join(dims_zh)} 方面指导 {player_a}")
    return "；".join(parts)


def generate_improved_plan(diagnosis):
    """
    基于系统诊断结果生成全局改进计划。

    参数:
        diagnosis (dict): diagnose_system() 的输出

    返回:
        dict: 改进计划，包含:
            - global_priorities: 全局优先事项
            - per_player_plans: 每位学员的个性化计划
            - phase_transitions: 阶段晋升建议
            - next_session_focus: 下次训练重点
    """
    per_player_plans = {}

    for analysis in diagnosis.get("player_analyses", []):
        player_key = analysis["player"]
        plan = _generate_player_plan(analysis)
        per_player_plans[player_key] = plan

    # 全局优先事项
    global_priorities = []
    common_weaknesses = diagnosis.get("common_weaknesses", [])
    for cw in common_weaknesses[:3]:
        if cw["count"] >= 2:
            global_priorities.append({
                "dimension": cw["dimension"],
                "dimension_zh": cw["name_zh"],
                "affected_count": cw["count"],
                "action": f"组织集体「{cw['name_zh']}」专项训练工作坊",
            })

    # 阶段晋升建议
    phase_transitions = []
    for analysis in diagnosis.get("player_analyses", []):
        readiness = analysis.get("phase_readiness", {})
        if readiness.get("ready"):
            phase_transitions.append({
                "player": analysis["player"],
                "from_phase": analysis["current_phase"],
                "to_phase": analysis["current_phase"] + 1,
                "confidence": readiness.get("confidence", 0),
                "notes": readiness.get("notes", ""),
            })

    # 下次训练重点
    next_session_focus = []
    for analysis in diagnosis.get("player_analyses", []):
        if analysis["priority_dimension"]:
            next_session_focus.append({
                "player": analysis["player"],
                "focus_dimension": analysis["priority_dimension"],
                "focus_zh": DIMENSION_NAMES_ZH.get(analysis["priority_dimension"], ""),
                "current_score": analysis["dimension_scores"].get(analysis["priority_dimension"], 0),
            })

    improved_plan = {
        "generated_at": datetime.datetime.now().isoformat(),
        "global_priorities": global_priorities,
        "per_player_plans": per_player_plans,
        "phase_transitions": phase_transitions,
        "next_session_focus": next_session_focus,
    }

    log(f"[改进计划] 全局优先={len(global_priorities)}, "
        f"阶段晋升={len(phase_transitions)}, 个人计划={len(per_player_plans)}")
    return improved_plan


def _generate_player_plan(analysis):
    """
    为单个学员生成个性化改进计划。

    参数:
        analysis (dict): analyze_player() 的输出

    返回:
        dict: 个人改进计划
    """
    player_key = analysis["player"]
    current_phase = analysis["current_phase"]
    weak_dims = analysis["weak_dimensions"]
    exercises = analysis["recommended_exercises"]
    trend = analysis["paper_trend"]

    # 本周训练目标
    weekly_goals = []
    if weak_dims:
        top_weak = weak_dims[0]
        weekly_goals.append({
            "goal": f"提升「{top_weak['name_zh']}」维度分数（当前{top_weak['score']}→目标{top_weak['threshold']+5}）",
            "dimension": top_weak["dimension"],
            "target_score": top_weak["threshold"] + 5,
        })

    if trend == "declining":
        weekly_goals.append({
            "goal": "完成2篇回顾性练习，巩固基础能力",
            "dimension": "general",
            "target_score": None,
        })

    # 每日任务分配
    daily_tasks = _build_daily_tasks(player_key, current_phase, weak_dims, exercises)

    # 里程碑
    milestones = []
    if analysis["papers_written"] < 3:
        milestones.append("完成第3篇完整论文写作")
    if current_phase < 5:
        next_phase = current_phase + 1
        milestones.append(f"达到阶段{next_phase}晋升条件")
    if not analysis["strong_dimensions"]:
        milestones.append("至少1个维度达到优势水平(>=85分)")

    plan = {
        "player": player_key,
        "current_phase": current_phase,
        "phase_name": PHASES.get(current_phase, f"阶段{current_phase}"),
        "paper_trend": trend,
        "weekly_goals": weekly_goals,
        "daily_tasks": daily_tasks,
        "milestones": milestones,
        "exercises_to_complete": exercises[:4],
        "estimated_completion_days": max(3, len(exercises) * 2),
    }

    return plan


def _build_daily_tasks(player_key, current_phase, weak_dims, exercises):
    """
    构建每日训练任务分配。

    参数:
        player_key (str): 学员标识
        current_phase (int): 当前阶段
        weak_dims (list): 薄弱维度列表
        exercises (list): 推荐练习列表

    返回:
        dict: 按天分配的任务（周一到周日）
    """
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    weekday_zh = {
        "monday": "周一", "tuesday": "周二", "wednesday": "周三",
        "thursday": "周四", "friday": "周五", "saturday": "周六", "sunday": "周日",
    }

    tasks = {}
    exercise_idx = 0

    for day in weekdays:
        day_tasks = {
            "day_zh": weekday_zh[day],
            "tasks": [],
        }

        if day == "sunday":
            day_tasks["tasks"].append({
                "type": "review",
                "desc": "回顾本周训练成果，更新个人档案",
                "duration_minutes": 30,
            })
        elif day == "saturday":
            day_tasks["tasks"].append({
                "type": "peer_review",
                "desc": "审阅其他学员的一篇论文并撰写评语",
                "duration_minutes": 60,
            })
        else:
            # 工作日：分配练习任务
            if exercise_idx < len(exercises):
                ex = exercises[exercise_idx]
                day_tasks["tasks"].append({
                    "type": "exercise",
                    "name": ex["name"],
                    "desc": ex["desc"],
                    "dimension": ex["dimension"],
                    "difficulty": ex["difficulty"],
                    "duration_minutes": 45 + ex["difficulty"] * 15,
                })
                exercise_idx += 1

            # 添加日常阅读任务
            day_tasks["tasks"].append({
                "type": "reading",
                "desc": "精读1篇相关领域论文，记录笔记",
                "duration_minutes": 40,
            })

        tasks[day] = day_tasks

    return tasks


# ─────────────────────────────────────────────
# 报告与消息生成
# ─────────────────────────────────────────────

def generate_coach_report(diagnosis, improved_plan):
    """
    生成教练综合报告并保存。

    报告内容包括：
    - 系统总览
    - 各学员详细分析与建议
    - 全局改进策略
    - 预警与关注事项

    参数:
        diagnosis (dict): 系统诊断结果
        improved_plan (dict): 改进计划

    返回:
        dict: 完整的教练报告
    """
    report = {
        "report_type": "paper_coach_report",
        "generated_at": datetime.datetime.now().isoformat(),
        "version": "1.0",
        "summary": {
            "total_players": diagnosis["total_players"],
            "active_players": diagnosis["active_players"],
            "total_papers": diagnosis["total_papers"],
            "system_avg_score": diagnosis["system_avg_score"],
            "top_concern": (
                diagnosis["common_weaknesses"][0]["name_zh"]
                if diagnosis["common_weaknesses"]
                else "无"
            ),
        },
        "system_health": {
            "phase_distribution": diagnosis["phase_distribution"],
            "common_weaknesses": diagnosis["common_weaknesses"],
            "alerts": diagnosis["alerts"],
        },
        "global_strategy": {
            "priorities": improved_plan["global_priorities"],
            "phase_transitions": improved_plan["phase_transitions"],
        },
        "player_reports": {},
    }

    # 为每位学员生成报告段落
    for analysis in diagnosis.get("player_analyses", []):
        player_key = analysis["player"]
        player_plan = improved_plan["per_player_plans"].get(player_key, {})

        report["player_reports"][player_key] = {
            "role": analysis["role"],
            "role_description": analysis["role_description"],
            "current_phase": analysis["current_phase"],
            "phase_name": PHASES.get(analysis["current_phase"], ""),
            "avg_score": analysis["avg_score"],
            "papers_written": analysis["papers_written"],
            "paper_trend": analysis["paper_trend"],
            "dimension_scores": analysis["dimension_scores"],
            "weak_dimensions": [
                {"dimension": wd["dimension"], "name_zh": wd["name_zh"], "score": wd["score"], "gap": wd["gap"]}
                for wd in analysis["weak_dimensions"]
            ],
            "strong_dimensions": [
                {"dimension": sd["dimension"], "name_zh": sd["name_zh"], "score": sd["score"]}
                for sd in analysis["strong_dimensions"]
            ],
            "phase_readiness": analysis["phase_readiness"],
            "weekly_goals": player_plan.get("weekly_goals", []),
            "milestones": player_plan.get("milestones", []),
            "priority_exercises": [
                {"name": ex["name"], "dimension_zh": ex["dimension_zh"], "difficulty": ex["difficulty"]}
                for ex in analysis["recommended_exercises"][:3]
            ],
        }

    # 协同训练建议
    report["collaboration"] = {
        "suggestions": diagnosis.get("collaboration_suggestions", []),
    }

    # 保存报告
    save_json(COACH_REPORT_PATH, report)
    log(f"[教练报告] 已生成并保存至 {COACH_REPORT_PATH}")

    return report


def generate_hermes_messages(report):
    """
    根据教练报告生成 Hermes 风格的消息文件。

    为每位学员生成一条 JSON 消息，写入 /shared/messages/from-hermes/ 目录。
    消息文件命名: hermes-paper-{player}.json

    参数:
        report (dict): generate_coach_report() 的输出

    返回:
        list: 已生成的消息文件路径列表
    """
    generated_paths = []
    timestamp = datetime.datetime.now().isoformat()

    for player_key, player_report in report.get("player_reports", {}).items():
        message = {
            "from": "hermes",
            "to": player_key,
            "type": "paper_coaching",
            "timestamp": timestamp,
            "subject": f"论文写作训练反馈 - {player_report.get('phase_name', '')}",
            "body": {
                "greeting": f"你好 {player_key}，以下是你的论文写作训练评估与下一步计划。",
                "current_status": {
                    "phase": player_report["current_phase"],
                    "phase_name": player_report.get("phase_name", ""),
                    "avg_score": player_report["avg_score"],
                    "papers_written": player_report["papers_written"],
                    "trend": player_report["paper_trend"],
                },
                "dimension_assessment": {
                    "scores": player_report["dimension_scores"],
                    "needs_attention": [
                        wd["name_zh"] for wd in player_report.get("weak_dimensions", [])
                    ],
                    "strengths": [
                        sd["name_zh"] for sd in player_report.get("strong_dimensions", [])
                    ],
                },
                "action_items": [
                    goal["goal"] for goal in player_report.get("weekly_goals", [])
                ],
                "recommended_exercises": [
                    f"{ex['name']}（{ex['dimension_zh']}，难度{ex['difficulty']}）"
                    for ex in player_report.get("priority_exercises", [])
                ],
                "milestones": player_report.get("milestones", []),
                "encouragement": _generate_encouragement(player_key, player_report),
            },
            "metadata": {
                "coach_version": "1.0",
                "report_path": COACH_REPORT_PATH,
                "next_review": (
                    datetime.datetime.now() + datetime.timedelta(days=7)
                ).isoformat(),
            },
        }

        msg_path = os.path.join(HERMES_MESSAGES_DIR, f"hermes-paper-{player_key}.json")
        if save_json(msg_path, message):
            generated_paths.append(msg_path)
            log(f"[Hermes消息] 已生成: {msg_path}")

    return generated_paths


def _generate_encouragement(player_key, player_report):
    """
    根据学员表现生成鼓励性文字。

    参数:
        player_key (str): 学员标识
        player_report (dict): 学员报告数据

    返回:
        str: 鼓励性文字
    """
    trend = player_report.get("paper_trend", "stable")
    avg_score = player_report.get("avg_score", 0)
    phase = player_report.get("current_phase", 1)
    weak_count = len(player_report.get("weak_dimensions", []))
    strong_count = len(player_report.get("strong_dimensions", []))

    if trend == "improving":
        base = "你的论文写作能力在稳步提升，继续保持这个势头！"
    elif trend == "declining":
        base = "最近的表现有所波动，不要气馁。回顾基础，从薄弱环节重新出发。"
    else:
        base = "你的表现保持稳定，是时候寻找突破点了。"

    if strong_count > 0:
        base += f"你在{strong_count}个维度上已经表现优异，这是很好的基础。"

    if weak_count > 3:
        base += "当前有多个维度需要关注，建议集中精力先攻克最薄弱的1-2个维度。"
    elif weak_count > 0:
        base += "关注几个薄弱维度，有针对性地进行专项练习。"

    if phase >= 4:
        base += "你已经进入高阶训练阶段，距离发表级别论文不远了！"
    elif phase >= 2:
        base += "稳步前进，每个阶段的积累都至关重要。"

    return base


# ─────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────

def main():
    """
    论文写作教练主入口。

    运行模式：
    1. 单次运行：执行一次完整的分析-诊断-报告流程
    2. 轮询模式：定期执行教练循环（通过 POLL_INTERVAL 控制）

    流程：
    1. 加载所有学员档案
    2. 逐一分析学员能力
    3. 执行系统级诊断
    4. 生成改进计划
    5. 输出教练报告
    6. 生成 Hermes 消息
    7. 等待下一轮（轮询模式）
    """
    log("=" * 60)
    log("论文写作教练系统启动")
    log(f"学员列表: {list(PLAYERS.keys())}")
    log(f"评估维度: {DIMENSIONS}")
    log(f"训练目录: {PAPER_TRAINING_DIR}")
    log(f"消息目录: {HERMES_MESSAGES_DIR}")
    log("=" * 60)

    # 确保输出目录存在
    os.makedirs(PAPER_TRAINING_DIR, exist_ok=True)
    os.makedirs(HERMES_MESSAGES_DIR, exist_ok=True)

    iteration = 0

    while True:
        iteration += 1
        log(f"--- 教练轮次 #{iteration} ---")

        try:
            # 步骤1: 确保所有学员档案存在
            for player_key in PLAYERS:
                ensure_default_profile(player_key)

            # 步骤2: 逐一分析学员
            log("[步骤2] 分析各学员能力...")
            player_analyses = {}
            for player_key in PLAYERS:
                player_analyses[player_key] = analyze_player(player_key)

            # 步骤3: 系统级诊断
            log("[步骤3] 执行系统级诊断...")
            diagnosis = diagnose_system()

            # 步骤4: 生成改进计划
            log("[步骤4] 生成改进计划...")
            improved_plan = generate_improved_plan(diagnosis)

            # 步骤5: 输出教练报告
            log("[步骤5] 生成教练报告...")
            report = generate_coach_report(diagnosis, improved_plan)

            # 步骤6: 生成 Hermes 消息
            log("[步骤6] 生成 Hermes 消息...")
            msg_paths = generate_hermes_messages(report)
            log(f"[完成] 已生成 {len(msg_paths)} 条 Hermes 消息")

            # 汇总
            log(f"[轮次完成] 分析了 {len(player_analyses)} 名学员, "
                f"报告路径: {COACH_REPORT_PATH}")

        except Exception as e:
            log(f"[错误] 教练轮次异常: {e}")
            import traceback
            traceback.print_exc()

        # 轮询控制
        if MAX_POLL_ITERATIONS > 0 and iteration >= MAX_POLL_ITERATIONS:
            log(f"已达到最大轮次数 ({MAX_POLL_ITERATIONS})，退出")
            break

        log(f"[等待] {POLL_INTERVAL}秒后开始下一轮...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
