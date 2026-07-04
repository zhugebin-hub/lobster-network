#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文写作任务调度器 (Paper Writing Task Dispatcher)
==================================================

龙虾网络论文写作训练系统的任务调度组件。
根据每日时间表自动为各学员生成、分发训练任务。
采用文件系统轮询模式，通过 JSON 文件在 inbox/outbox 间传递任务。

时间表：
  08:00-10:00  文献挖掘 (literature_mining)
  10:00-12:00  大纲撰写 (outline_writing)
  14:00-16:00  章节起草 (section_drafting)
  16:00-18:00  同伴互评 (peer_review)
  20:00-22:00  修改润色 (revision_polish)

模式：纯函数式 + 文件系统轮询，无 OOP。
数据目录：/shared/training/paper/
"""

import json
import os
import time
import random
import datetime
import uuid

# ─────────────────────────────────────────────
# 常量定义
# ─────────────────────────────────────────────

# 共享文件系统根路径
SHARED_ROOT = "/shared"

# 论文训练基础目录
PAPER_TRAINING_DIR = os.path.join(SHARED_ROOT, "training", "paper")

# 学员注册表：定义每位学员的路径与属性
PLAYERS = {
    "qoder": {
        "name_zh": "Qoder（分析型专家）",
        "role": "analytical_specialist",
        "description": "擅长方法论与逻辑推理，负责论文的理论框架与假设推导",
        "profile_path": os.path.join(PAPER_TRAINING_DIR, "qoder", "profile.json"),
        "inbox_path": os.path.join(PAPER_TRAINING_DIR, "qoder", "inbox"),
        "outbox_path": os.path.join(PAPER_TRAINING_DIR, "qoder", "outbox"),
        "primary_dimensions": ["methodology", "structure"],
        "secondary_dimensions": ["argumentation", "data_analysis"],
        "weak_dimensions": ["abstract", "formatting"],
        "task_preferences": {
            "literature_mining": "theory_frameworks",
            "outline_writing": "logical_structure",
            "section_drafting": "methodology_section",
            "peer_review": "methodology_review",
            "revision_polish": "argument_refinement",
        },
    },
    "xiaochen": {
        "name_zh": "小陈（实证型专家）",
        "role": "empirical_specialist",
        "description": "擅长数据分析与实验设计，负责论文的实证部分与数据呈现",
        "profile_path": os.path.join(PAPER_TRAINING_DIR, "xiaochen", "profile.json"),
        "inbox_path": os.path.join(PAPER_TRAINING_DIR, "xiaochen", "inbox"),
        "outbox_path": os.path.join(PAPER_TRAINING_DIR, "xiaochen", "outbox"),
        "primary_dimensions": ["data_analysis", "methodology"],
        "secondary_dimensions": ["structure", "argumentation"],
        "weak_dimensions": ["literature_review", "formatting"],
        "task_preferences": {
            "literature_mining": "empirical_studies",
            "outline_writing": "experiment_design",
            "section_drafting": "results_section",
            "peer_review": "data_quality_review",
            "revision_polish": "statistical_rigor",
        },
    },
    "zhuguxia": {
        "name_zh": "竹古侠（综述型专家）",
        "role": "survey_specialist",
        "description": "擅长文献综述与知识梳理，负责论文的文献综述与引言部分",
        "profile_path": os.path.join(PAPER_TRAINING_DIR, "zhuguxia", "profile.json"),
        "inbox_path": os.path.join(PAPER_TRAINING_DIR, "zhuguxia", "inbox"),
        "outbox_path": os.path.join(PAPER_TRAINING_DIR, "zhuguxia", "outbox"),
        "primary_dimensions": ["literature_review", "citations"],
        "secondary_dimensions": ["abstract", "structure"],
        "weak_dimensions": ["data_analysis", "methodology"],
        "task_preferences": {
            "literature_mining": "systematic_review",
            "outline_writing": "thematic_mapping",
            "section_drafting": "literature_section",
            "peer_review": "citation_accuracy_review",
            "revision_polish": "coherence_polish",
        },
    },
    "professor_zhuge": {
        "name_zh": "诸葛教授（审稿人）",
        "role": "reviewer",
        "description": "审稿人角色，负责论文整体质量把控与学术规范审查",
        "profile_path": os.path.join(PAPER_TRAINING_DIR, "professor_zhuge", "profile.json"),
        "inbox_path": os.path.join(PAPER_TRAINING_DIR, "professor_zhuge", "inbox"),
        "outbox_path": os.path.join(PAPER_TRAINING_DIR, "professor_zhuge", "outbox"),
        "primary_dimensions": ["argumentation", "formatting"],
        "secondary_dimensions": ["citations", "abstract"],
        "weak_dimensions": ["structure", "data_analysis"],
        "task_preferences": {
            "literature_mining": "review_methodology",
            "outline_writing": "review_checklist",
            "section_drafting": "review_report",
            "peer_review": "comprehensive_review",
            "revision_polish": "editorial_feedback",
        },
    },
}

# 每日训练时间表
PAPER_SCHEDULE = {
    "08:00-10:00": {
        "slot_id": "literature_mining",
        "name_zh": "文献挖掘",
        "description": "搜索、筛选、总结相关领域论文，构建文献知识库",
        "duration_minutes": 120,
        "per_player_tasks": {
            "qoder": {
                "focus_dimension": "methodology",
                "task_desc": "搜索方法论相关文献，总结3种常用研究方法及其适用场景",
                "difficulty": 3,
                "references": [
                    "Creswell, J.W. (2014). Research Design",
                    "Yin, R.K. (2018). Case Study Research and Applications",
                ],
                "deliverable": "方法论文献摘要卡片（不少于5篇）",
            },
            "xiaochen": {
                "focus_dimension": "data_analysis",
                "task_desc": "搜索实证分析相关文献，整理数据分析方法的演进脉络",
                "difficulty": 3,
                "references": [
                    "Field, A. (2018). Discovering Statistics Using IBM SPSS",
                    "Hair, J.F. et al. (2019). Multivariate Data Analysis",
                ],
                "deliverable": "数据分析方法对比表",
            },
            "zhuguxia": {
                "focus_dimension": "literature_review",
                "task_desc": "进行系统性文献检索，构建主题-方法-结论三维文献矩阵",
                "difficulty": 2,
                "references": [
                    "Kitchenham, B. (2007). Guidelines for Systematic Literature Reviews",
                    "Tranfield, D. et al. (2003). Towards a Methodology for Developing Evidence-Informed Management Knowledge",
                ],
                "deliverable": "系统文献综述框架 + 文献矩阵",
            },
            "professor_zhuge": {
                "focus_dimension": "argumentation",
                "task_desc": "从审稿视角审查文献引用质量，评估文献的代表性与时效性",
                "difficulty": 2,
                "references": [
                    "APA Publication Manual (7th ed.)",
                    "Belcher, W.L. (2019). Writing Your Journal Article in Twelve Weeks",
                ],
                "deliverable": "文献引用质量评估报告",
            },
        },
    },
    "10:00-12:00": {
        "slot_id": "outline_writing",
        "name_zh": "大纲撰写",
        "description": "根据文献挖掘成果，创建或优化论文结构大纲",
        "duration_minutes": 120,
        "per_player_tasks": {
            "qoder": {
                "focus_dimension": "structure",
                "task_desc": "设计论文的逻辑框架大纲，明确各章节的核心论点与论证路径",
                "difficulty": 3,
                "references": [
                    "Swales, J.M. (2004). Research Genres",
                    "Dunleavy, P. (2003). Authoring a PhD",
                ],
                "deliverable": "三级大纲（章-节-要点）+ 逻辑流程图",
            },
            "xiaochen": {
                "focus_dimension": "methodology",
                "task_desc": "设计实证研究方案大纲，包括变量定义、数据来源、分析策略",
                "difficulty": 3,
                "references": [
                    "Shadish, W.R. et al. (2002). Experimental and Quasi-Experimental Designs",
                    "Babbie, E.R. (2020). The Practice of Social Research",
                ],
                "deliverable": "实证研究方案大纲 + 变量操作化表",
            },
            "zhuguxia": {
                "focus_dimension": "structure",
                "task_desc": "撰写文献综述部分的层级大纲，按主题/时间线/方法论三种方式组织",
                "difficulty": 2,
                "references": [
                    "Machi, L.A. & McEvoy, B.T. (2016). The Literature Review: Six Steps",
                    "Ridley, D. (2012). The Literature Review: A Step-by-Step Guide",
                ],
                "deliverable": "文献综述三级大纲（含各节字数规划）",
            },
            "professor_zhuge": {
                "focus_dimension": "formatting",
                "task_desc": "制定大纲评审清单，从审稿人角度审视大纲的完整性与规范性",
                "difficulty": 2,
                "references": [
                    "APA Publication Manual (7th ed.) - Section Organization",
                    "Target journal's author guidelines",
                ],
                "deliverable": "大纲评审清单（含20个审查要点）",
            },
        },
    },
    "14:00-16:00": {
        "slot_id": "section_drafting",
        "name_zh": "章节起草",
        "description": "根据大纲起草论文的特定章节",
        "duration_minutes": 120,
        "per_player_tasks": {
            "qoder": {
                "focus_dimension": "methodology",
                "task_desc": "起草方法论章节：描述研究设计、数据收集方法、分析策略",
                "difficulty": 3,
                "references": [
                    "Creswell & Plano Clark (2018). Designing and Conducting Mixed Methods Research",
                    "Johnson & Christensen (2019). Educational Research",
                ],
                "deliverable": "方法论章节初稿（1500-2000字）",
            },
            "xiaochen": {
                "focus_dimension": "data_analysis",
                "task_desc": "起草结果与分析章节：呈现数据发现，配合图表说明",
                "difficulty": 3,
                "references": [
                    "Nicol, A.A.M. & Pexman, P.M. (2010). Displaying Your Findings",
                    "Tufte, E.R. (2001). The Visual Display of Quantitative Information",
                ],
                "deliverable": "结果与分析章节初稿（含图表，1500-2000字）",
            },
            "zhuguxia": {
                "focus_dimension": "literature_review",
                "task_desc": "起草文献综述章节：综合已有研究，识别研究缺口",
                "difficulty": 2,
                "references": [
                    "Webster, J. & Watson, R.T. (2002). Analyzing the Past to Prepare for the Future",
                    "Paré, G. et al. (2015). Types of Literature Reviews",
                ],
                "deliverable": "文献综述章节初稿（2000-2500字）",
            },
            "professor_zhuge": {
                "focus_dimension": "argumentation",
                "task_desc": "起草讨论章节：将研究发现与文献对话，提炼理论贡献",
                "difficulty": 3,
                "references": [
                    "Corley, K.G. & Gioia, D.A. (2011). Building Theory about Theory Building",
                    "Suddaby, R. (2006). From the Editors: What Grounded Theory is Not",
                ],
                "deliverable": "讨论章节初稿（1500-2000字）",
            },
        },
    },
    "16:00-18:00": {
        "slot_id": "peer_review",
        "name_zh": "同伴互评",
        "description": "审阅其他学员的论文章节，提供建设性反馈",
        "duration_minutes": 120,
        "per_player_tasks": {
            "qoder": {
                "focus_dimension": "argumentation",
                "task_desc": "审阅竹古侠的文献综述章节，评估论证逻辑与文献覆盖度",
                "difficulty": 2,
                "review_target": "zhuguxia",
                "review_focus": "文献综述的完整性与逻辑性",
                "references": [
                    "Peer Review Guidelines: Constructive Feedback Framework",
                    "Belcher (2019). Writing Your Journal Article - Peer Review Chapter",
                ],
                "deliverable": "评审意见书（含优点3条+改进建议5条）",
            },
            "xiaochen": {
                "focus_dimension": "methodology",
                "task_desc": "审阅Qoder的方法论章节，检查实验设计的科学性与可复现性",
                "difficulty": 3,
                "review_target": "qoder",
                "review_focus": "方法论的严谨性与可复现性",
                "references": [
                    "Shadish et al. (2002). Threats to Validity",
                    "Open Science Collaboration (2015). Estimating the Reproducibility",
                ],
                "deliverable": "方法论评审报告（含可复现性评分）",
            },
            "zhuguxia": {
                "focus_dimension": "citations",
                "task_desc": "审阅小陈的结果章节，检查引用规范与数据呈现的清晰度",
                "difficulty": 2,
                "review_target": "xiaochen",
                "review_focus": "数据呈现的准确性与引用规范",
                "references": [
                    "APA Publication Manual (7th ed.) - Citing Data Sets",
                    "Tufte (2001). Graphical Integrity Principles",
                ],
                "deliverable": "引用与数据呈现审查报告",
            },
            "professor_zhuge": {
                "focus_dimension": "formatting",
                "task_desc": "对所有学员提交的章节进行综合评审，从审稿人视角给出整体评价",
                "difficulty": 3,
                "review_target": "all",
                "review_focus": "整体学术质量与发表潜力",
                "references": [
                    "Reviewer Guidelines: Journal Review Process",
                    "COPE (Committee on Publication Ethics) Guidelines",
                ],
                "deliverable": "综合审稿意见（含各章节评分与总体建议）",
            },
        },
    },
    "20:00-22:00": {
        "slot_id": "revision_polish",
        "name_zh": "修改润色",
        "description": "根据同伴互评反馈修改润色论文章节",
        "duration_minutes": 120,
        "per_player_tasks": {
            "qoder": {
                "focus_dimension": "argumentation",
                "task_desc": "根据审稿反馈强化方法论章节的论证逻辑，补充方法论辩护段落",
                "difficulty": 3,
                "references": [
                    "Antaki, C. (2003). Writing: Tips for the Perplexed",
                    "Becker, H.S. (2007). Writing for Social Scientists",
                ],
                "deliverable": "方法论章节修改稿 + 修改说明",
            },
            "xiaochen": {
                "focus_dimension": "data_analysis",
                "task_desc": "根据审稿反馈优化数据分析呈现，增加稳健性检验讨论",
                "difficulty": 3,
                "references": [
                    "Luft, J. & Zimmerman, J.L. (2016). Editors' Comments on Statistical Methods",
                    "Aguinis, H. et al. (2016). Conducting Management and Organizational Research",
                ],
                "deliverable": "结果章节修改稿 + 稳健性分析补充",
            },
            "zhuguxia": {
                "focus_dimension": "citations",
                "task_desc": "根据审稿反馈补充文献引用，优化综述的连贯性与批判性分析",
                "difficulty": 2,
                "references": [
                    "Booth, W.C. et al. (2016). The Craft of Research",
                    "Graff, G. & Birkenstein, C. (2018). They Say / I Say",
                ],
                "deliverable": "文献综述修改稿 + 引用完整性检查表",
            },
            "professor_zhuge": {
                "focus_dimension": "formatting",
                "task_desc": "汇总所有修改稿，进行格式统一与整体润色，撰写编辑反馈信",
                "difficulty": 2,
                "references": [
                    "APA Publication Manual (7th ed.) - Final Checklist",
                    "Strunk, W. & White, E.B. (2000). The Elements of Style",
                ],
                "deliverable": "格式统一报告 + 编辑反馈信 + 修改追踪清单",
            },
        },
    },
}

# 难度等级描述
DIFFICULTY_LEVELS = {
    1: "入门级 - 基础练习，适合新手",
    2: "中级 - 需要一定基础，有挑战性",
    3: "高级 - 综合性任务，适合进阶学员",
}

# 轮询间隔（秒）
POLL_INTERVAL = 30

# 最大轮询次数（0 表示无限）
MAX_POLL_ITERATIONS = 0

# 任务过期时间（小时）
TASK_EXPIRY_HOURS = 24


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────

def log(message):
    """打印带时间戳的日志信息"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[PaperDispatcher {timestamp}] {message}")


def generate_task_id():
    """
    生成唯一的任务标识。

    返回:
        str: 格式为 task-{日期}-{短UUID} 的唯一标识
    """
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    short_uuid = str(uuid.uuid4())[:8]
    return f"task-{date_str}-{short_uuid}"


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
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError) as e:
        log(f"[警告] 无法读取 {filepath}: {e}")
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
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        log(f"[错误] 保存失败 {filepath}: {e}")
        return False


def load_profile(player_key):
    """
    加载指定学员的训练档案。

    若档案不存在，则创建默认档案（与 paper_coach.py 保持一致的默认值）。

    参数:
        player_key (str): 学员标识

    返回:
        dict: 学员档案数据，结构如下:
            - player: 学员标识
            - papers_written: 已完成论文数
            - avg_score: 平均分数
            - dimensions: 各维度得分
            - papers: 论文列表
            - exercises_completed: 已完成练习数
            - current_phase: 当前训练阶段
    """
    player_info = PLAYERS.get(player_key)
    if not player_info:
        log(f"[错误] 未知学员: {player_key}")
        return None

    profile_path = player_info["profile_path"]
    profile = load_json(profile_path)

    if profile is not None:
        return profile

    # 创建默认档案
    default_dimensions = {}
    for dim_key in ["structure", "abstract", "literature_review", "methodology",
                     "data_analysis", "argumentation", "formatting", "citations"]:
        if dim_key in player_info.get("primary_dimensions", []):
            default_dimensions[dim_key] = 75
        elif dim_key in player_info.get("secondary_dimensions", []):
            default_dimensions[dim_key] = 65
        elif dim_key in player_info.get("weak_dimensions", []):
            default_dimensions[dim_key] = 55
        else:
            default_dimensions[dim_key] = 60

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


def ensure_directories():
    """
    确保所有学员的 inbox / outbox 目录存在。
    """
    for player_key, player_info in PLAYERS.items():
        for dirpath in [player_info["inbox_path"], player_info["outbox_path"]]:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)
                log(f"[创建目录] {dirpath}")


# ─────────────────────────────────────────────
# 时间判断函数
# ─────────────────────────────────────────────

def get_current_time_slot():
    """
    判断当前时间属于哪个训练时间段。

    返回:
        tuple: (time_slot_key, slot_config) 或 (None, None)（不在训练时间内）
    """
    now = datetime.datetime.now()
    current_minutes = now.hour * 60 + now.minute

    for time_range, slot_config in PAPER_SCHEDULE.items():
        start_str, end_str = time_range.split("-")
        start_h, start_m = map(int, start_str.split(":"))
        end_h, end_m = map(int, end_str.split(":"))
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m

        if start_minutes <= current_minutes < end_minutes:
            return time_range, slot_config

    return None, None


def get_today_task_log_path():
    """
    获取今日任务日志文件路径。

    返回:
        str: 今日任务日志路径
    """
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    return os.path.join(PAPER_TRAINING_DIR, f"dispatch_log_{date_str}.json")


def load_today_task_log():
    """
    加载今日已分发任务的记录。

    返回:
        dict: 今日任务记录，格式为 {slot_id: [task_id, ...]}
    """
    log_path = get_today_task_log_path()
    data = load_json(log_path)
    if data is None:
        data = {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "dispatched": {}}
    return data


def save_today_task_log(task_log):
    """
    保存今日任务分发记录。

    参数:
        task_log (dict): 任务日志数据
    """
    log_path = get_today_task_log_path()
    save_json(log_path, task_log)


def is_slot_already_dispatched(task_log, slot_id):
    """
    检查某个时间段的任务是否已经分发过。

    参数:
        task_log (dict): 今日任务记录
        slot_id (str): 时间段标识

    返回:
        bool: 已分发返回 True
    """
    dispatched = task_log.get("dispatched", {})
    slot_tasks = dispatched.get(slot_id, [])
    return len(slot_tasks) > 0


# ─────────────────────────────────────────────
# 任务创建与分发
# ─────────────────────────────────────────────

def create_training_task(time_slot_key, player_key):
    """
    为指定学员在指定时间段创建训练任务。

    根据学员角色、当前能力水平、时间段特性，生成个性化的训练任务。

    参数:
        time_slot_key (str): 时间表中的时间段键（如 "08:00-10:00"）
        player_key (str): 学员标识

    返回:
        dict: 完整的任务对象，结构如下:
            - task_id: 唯一任务标识
            - type: 任务类型（slot_id）
            - player: 学员标识
            - player_name_zh: 学员中文名
            - focus_dimension: 重点训练维度
            - focus_dimension_zh: 维度中文名
            - difficulty: 难度等级 (1-3)
            - description: 任务描述
            - deliverable: 交付物说明
            - references: 参考文献列表
            - due_time: 截止时间 (ISO-8601)
            - created_at: 创建时间 (ISO-8601)
            - status: 任务状态 ("pending")
            - review_target: 互评对象（仅 peer_review 类型）
            - personalization: 个性化调整说明
    """
    slot_config = PAPER_SCHEDULE.get(time_slot_key)
    if not slot_config:
        log(f"[错误] 无效的时间段: {time_slot_key}")
        return None

    player_info = PLAYERS.get(player_key)
    if not player_info:
        log(f"[错误] 无效学员: {player_key}")
        return None

    player_tasks = slot_config.get("per_player_tasks", {})
    player_task = player_tasks.get(player_key)
    if not player_task:
        log(f"[警告] 学员 {player_key} 在时间段 {time_slot_key} 无预设任务")
        return None

    # 加载档案以获取能力水平
    profile = load_profile(player_key)
    current_phase = profile.get("current_phase", 1) if profile else 1
    dimensions = profile.get("dimensions", {}) if profile else {}

    # 基础难度来自任务配置
    base_difficulty = player_task.get("difficulty", 2)

    # 根据能力水平调整难度
    focus_dim = player_task.get("focus_dimension", "")
    dim_score = dimensions.get(focus_dim, 60)
    adjusted_difficulty = base_difficulty
    if dim_score >= 80:
        # 能力强则提高难度
        adjusted_difficulty = min(3, base_difficulty + 1)
    elif dim_score < 60:
        # 能力弱则降低难度
        adjusted_difficulty = max(1, base_difficulty - 1)

    # 计算截止时间
    end_time_str = time_slot_key.split("-")[1]
    end_h, end_m = map(int, end_time_str.split(":"))
    today = datetime.datetime.now().replace(hour=end_h, minute=end_m, second=0, microsecond=0)
    due_time = today.isoformat()

    # 构建任务对象
    task = {
        "task_id": generate_task_id(),
        "type": slot_config["slot_id"],
        "type_zh": slot_config["name_zh"],
        "time_slot": time_slot_key,
        "player": player_key,
        "player_name_zh": player_info["name_zh"],
        "role": player_info["role"],
        "focus_dimension": focus_dim,
        "focus_dimension_zh": _dim_zh(focus_dim),
        "focus_score": dim_score,
        "difficulty": adjusted_difficulty,
        "difficulty_label": DIFFICULTY_LEVELS.get(adjusted_difficulty, ""),
        "description": player_task.get("task_desc", ""),
        "deliverable": player_task.get("deliverable", ""),
        "references": player_task.get("references", []),
        "due_time": due_time,
        "created_at": datetime.datetime.now().isoformat(),
        "expires_at": (today + datetime.timedelta(hours=TASK_EXPIRY_HOURS)).isoformat(),
        "status": "pending",
        "current_phase": current_phase,
        "personalization": _build_personalization(player_key, profile, player_task, slot_config),
    }

    # 互评任务额外字段
    if "review_target" in player_task:
        task["review_target"] = player_task["review_target"]
        task["review_focus"] = player_task.get("review_focus", "")

    log(f"[任务创建] {player_key} | {slot_config['name_zh']} | "
        f"维度={focus_dim}(分数={dim_score}) | 难度={adjusted_difficulty}")
    return task


def _dim_zh(dim_key):
    """
    获取维度的中文名。

    参数:
        dim_key (str): 维度英文键

    返回:
        str: 中文名
    """
    mapping = {
        "structure": "论文结构",
        "abstract": "摘要质量",
        "literature_review": "文献综述",
        "methodology": "方法论",
        "data_analysis": "数据分析",
        "argumentation": "论证逻辑",
        "formatting": "格式规范",
        "citations": "引用规范",
    }
    return mapping.get(dim_key, dim_key)


def _build_personalization(player_key, profile, player_task, slot_config):
    """
    构建任务的个性化调整说明。

    根据学员当前能力水平、训练历史，给出个性化的注意事项与建议。

    参数:
        player_key (str): 学员标识
        profile (dict): 学员档案
        player_task (dict): 学员的任务配置
        slot_config (dict): 时间段配置

    返回:
        dict: 个性化说明，包含 tips / warnings / bonus_challenge
    """
    tips = []
    warnings = []
    bonus_challenge = None

    if profile:
        dimensions = profile.get("dimensions", {})
        current_phase = profile.get("current_phase", 1)
        exercises_done = profile.get("exercises_completed", 0)

        focus_dim = player_task.get("focus_dimension", "")
        focus_score = dimensions.get(focus_dim, 60)

        # 根据分数给出提示
        if focus_score < 55:
            tips.append(f"「{_dim_zh(focus_dim)}」是当前的重点薄弱环节，建议从基础概念入手，循序渐进")
            tips.append("遇到困难时可以查阅参考文献中的入门章节")
        elif focus_score < 70:
            tips.append(f"「{_dim_zh(focus_dim)}」已有一定基础，本次练习侧重巩固与提升")
        elif focus_score >= 80:
            tips.append(f"「{_dim_zh(focus_dim)}」能力较强，本次练习可尝试更高阶的挑战")
            bonus_challenge = f"尝试在 {_dim_zh(focus_dim)} 方面提出创新性的方法或观点"

        # 阶段相关提示
        if current_phase >= 3:
            tips.append("当前处于高级阶段，注意与整体论文的逻辑衔接")
        if exercises_done < 5:
            warnings.append("基础练习完成较少，建议在任务前先完成1-2个基础练习热身")

    slot_id = slot_config.get("slot_id", "")
    player_info = PLAYERS.get(player_key, {})
    preference = player_info.get("task_preferences", {}).get(slot_id, "")
    if preference:
        tips.append(f"根据你的角色定位，本次任务的侧重方向: {preference}")

    return {
        "tips": tips,
        "warnings": warnings,
        "bonus_challenge": bonus_challenge,
    }


def send_to_inbox(player_key, task):
    """
    将任务发送到学员的收件箱。

    将任务 JSON 文件写入学员的 inbox 目录，文件名为 {task_id}.json。
    同时更新今日任务日志。

    参数:
        player_key (str): 学员标识
        task (dict): 任务对象（由 create_training_task 生成）

    返回:
        bool: 发送成功返回 True
    """
    player_info = PLAYERS.get(player_key)
    if not player_info:
        log(f"[错误] 无法发送任务: 未知学员 {player_key}")
        return False

    inbox_path = player_info["inbox_path"]
    if not os.path.exists(inbox_path):
        os.makedirs(inbox_path, exist_ok=True)

    task_id = task.get("task_id", generate_task_id())
    task_file = os.path.join(inbox_path, f"{task_id}.json")

    success = save_json(task_file, task)
    if success:
        log(f"[任务分发] -> {player_key}/inbox/{task_id}.json")
    else:
        log(f"[错误] 任务分发失败: {player_key}/{task_id}")

    return success


def process_outbox(player_key):
    """
    检查学员的发件箱，处理已完成的任务。

    读取 outbox 中的任务结果文件，更新学员档案。

    参数:
        player_key (str): 学员标识

    返回:
        list: 已处理的任务结果列表
    """
    player_info = PLAYERS.get(player_key)
    if not player_info:
        return []

    outbox_path = player_info["outbox_path"]
    if not os.path.exists(outbox_path):
        return []

    processed = []
    for filename in os.listdir(outbox_path):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(outbox_path, filename)
        result = load_json(filepath)
        if result is None:
            continue

        task_id = result.get("task_id", filename.replace(".json", ""))
        status = result.get("status", "unknown")

        if status == "completed":
            processed.append(result)
            log(f"[任务完成] {player_key}: {task_id} "
                f"(得分={result.get('score', 'N/A')})")

            # 更新档案中的练习完成数
            _update_profile_exercise(player_key, result)

            # 归档已处理的任务（移入 archive 子目录）
            archive_dir = os.path.join(outbox_path, "archive")
            if not os.path.exists(archive_dir):
                os.makedirs(archive_dir, exist_ok=True)
            archive_path = os.path.join(archive_dir, filename)
            try:
                os.rename(filepath, archive_path)
            except OSError:
                pass

        elif status == "failed":
            log(f"[任务失败] {player_key}: {task_id} - {result.get('error', '未知错误')}")
            processed.append(result)

    return processed


def _update_profile_exercise(player_key, task_result):
    """
    根据完成的任务结果更新学员档案中的练习计数。

    参数:
        player_key (str): 学员标识
        task_result (dict): 任务完成结果
    """
    player_info = PLAYERS.get(player_key)
    if not player_info:
        return

    profile_path = player_info["profile_path"]
    profile = load_json(profile_path)
    if profile is None:
        return

    exercises = profile.get("exercises_completed", 0)
    profile["exercises_completed"] = exercises + 1

    # 更新维度分数（如果任务结果包含评分）
    score = task_result.get("score")
    focus_dim = task_result.get("focus_dimension")
    if score is not None and focus_dim:
        dimensions = profile.get("dimensions", {})
        old_score = dimensions.get(focus_dim, 60)
        # 新分数占 30% 权重，旧分数占 70%
        new_score = round(old_score * 0.7 + score * 0.3, 1)
        dimensions[focus_dim] = new_score
        profile["dimensions"] = dimensions

    save_json(profile_path, profile)
    log(f"[档案更新] {player_key}: 练习数={profile['exercises_completed']}")


# ─────────────────────────────────────────────
# 调度循环
# ─────────────────────────────────────────────

def dispatch_slot_tasks(time_slot_key, slot_config):
    """
    为指定时间段分发所有学员的训练任务。

    参数:
        time_slot_key (str): 时间段键（如 "08:00-10:00"）
        slot_config (dict): 时间段配置

    返回:
        dict: 分发结果，格式为 {player_key: task_id}
    """
    slot_id = slot_config["slot_id"]
    log(f"[分发开始] 时间段: {time_slot_key} ({slot_config['name_zh']})")

    # 检查是否已经分发
    task_log = load_today_task_log()
    if is_slot_already_dispatched(task_log, slot_id):
        log(f"[跳过] 时间段 {slot_id} 今日已分发")
        return {}

    dispatched = {}

    for player_key in PLAYERS:
        task = create_training_task(time_slot_key, player_key)
        if task is None:
            log(f"[跳过] {player_key} 无可用任务")
            continue

        success = send_to_inbox(player_key, task)
        if success:
            dispatched[player_key] = task["task_id"]

    # 记录分发日志
    if dispatched:
        dispatched_slots = task_log.get("dispatched", {})
        dispatched_slots[slot_id] = list(dispatched.values())
        task_log["dispatched"] = dispatched_slots
        task_log["last_updated"] = datetime.datetime.now().isoformat()
        save_today_task_log(task_log)
        log(f"[分发完成] {slot_id}: 已分发 {len(dispatched)} 个任务")

    return dispatched


def run_dispatch_cycle():
    """
    执行一次完整的调度周期。

    流程：
    1. 检查当前时间是否属于某个训练时间段
    2. 若是，且尚未分发，则为所有学员创建并分发任务
    3. 检查所有学员的发件箱，处理已完成的任务
    4. 输出本周期状态摘要
    """
    # 步骤1: 检查当前时间段
    time_slot_key, slot_config = get_current_time_slot()

    if time_slot_key and slot_config:
        log(f"[当前时段] {time_slot_key} - {slot_config['name_zh']}")
        dispatch_slot_tasks(time_slot_key, slot_config)
    else:
        log("[非训练时段] 当前不在训练时间表范围内")

    # 步骤2: 处理所有学员的 outbox
    total_completed = 0
    for player_key in PLAYERS:
        results = process_outbox(player_key)
        total_completed += len(results)

    if total_completed > 0:
        log(f"[收件箱处理] 本轮处理了 {total_completed} 个已完成任务")

    # 步骤3: 状态摘要
    _print_status_summary()


def _print_status_summary():
    """打印当前状态摘要。"""
    summary_lines = ["--- 状态摘要 ---"]

    for player_key, player_info in PLAYERS.items():
        inbox_path = player_info["inbox_path"]
        outbox_path = player_info["outbox_path"]

        # 计算 inbox 中的待处理任务数
        inbox_count = 0
        if os.path.exists(inbox_path):
            inbox_count = len([f for f in os.listdir(inbox_path) if f.endswith(".json")])

        # 计算 outbox 中的待处理结果数
        outbox_count = 0
        if os.path.exists(outbox_path):
            outbox_count = len([
                f for f in os.listdir(outbox_path)
                if f.endswith(".json") and not os.path.isdir(os.path.join(outbox_path, f))
            ])

        summary_lines.append(
            f"  {player_key}: 收件箱={inbox_count} 待处理, 发件箱={outbox_count} 待处理"
        )

    for line in summary_lines:
        log(line)


# ─────────────────────────────────────────────
# 主函数
# ─────────────────────────────────────────────

def main():
    """
    论文写作任务调度器主入口。

    运行模式：文件系统轮询
    - 每 POLL_INTERVAL 秒检查一次当前时间
    - 在训练时间段内自动创建并分发任务
    - 持续处理学员发件箱中的已完成任务
    - 非训练时段仍处理 outbox，但不创建新任务

    启动流程：
    1. 初始化目录结构
    2. 加载/创建所有学员档案
    3. 进入轮询循环
    """
    log("=" * 60)
    log("论文写作任务调度器启动")
    log(f"训练目录: {PAPER_TRAINING_DIR}")
    log(f"学员列表: {list(PLAYERS.keys())}")
    log(f"轮询间隔: {POLL_INTERVAL}秒")
    log("=" * 60)

    # 打印时间表
    log("每日训练时间表:")
    for time_range, slot in PAPER_SCHEDULE.items():
        log(f"  {time_range}  {slot['name_zh']} - {slot['description']}")

    # 步骤1: 初始化目录
    log("[初始化] 确保目录结构...")
    ensure_directories()

    # 步骤2: 加载/创建所有学员档案
    log("[初始化] 加载学员档案...")
    for player_key in PLAYERS:
        profile = load_profile(player_key)
        if profile:
            log(f"  {player_key}: 阶段={profile.get('current_phase', 1)}, "
                f"论文数={profile.get('papers_written', 0)}, "
                f"均分={profile.get('avg_score', 0.0)}")

    # 步骤3: 轮询循环
    iteration = 0
    log("[启动] 进入轮询循环...")

    while True:
        iteration += 1
        try:
            run_dispatch_cycle()
        except Exception as e:
            log(f"[错误] 调度周期异常: {e}")
            import traceback
            traceback.print_exc()

        # 轮询控制
        if MAX_POLL_ITERATIONS > 0 and iteration >= MAX_POLL_ITERATIONS:
            log(f"已达到最大轮次数 ({MAX_POLL_ITERATIONS})，退出")
            break

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
