#!/usr/bin/env python3
"""
论文写作智能体 (Paper Writing Agent)
====================================

龙虾网络论文写作模块的核心智能体。采用文件系统驱动的轮询模式，
从 /shared/training/paper/{role}/inbox/ 读取任务 JSON，
执行论文写作相关操作后将结果写入 /shared/training/paper/{role}/outbox/。

支持的任务类型：
  - literature_mining：文献挖掘与综述生成
  - outline_writing：论文大纲撰写
  - section_drafting：章节草稿撰写
  - peer_review：同行评审（8 维度评价）
  - revision_polish：修订与润色

运行方式：
  python paper_agent.py <role_name>

角色列表：qoder, xiaochen, zhuguxia, professor_zhuge
"""

import json
import os
import sys
import time
import random
import hashlib
from datetime import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

CHECK_INTERVAL = 5  # 轮询间隔（秒）

ROLES = {
    "qoder": {
        "display_name": "Qoder",
        "specialty": "方法论与数据分析",
        "strengths": ["统计建模", "算法设计", "代码实现"],
    },
    "xiaochen": {
        "display_name": "小陈",
        "specialty": "文献综述与理论框架",
        "strengths": ["文献检索", "理论梳理", "批判性分析"],
    },
    "zhuguxia": {
        "display_name": "诸葛侠",
        "specialty": "实验设计与结果呈现",
        "strengths": ["实验方案", "可视化", "数据解读"],
    },
    "professor_zhuge": {
        "display_name": "诸葛教授",
        "specialty": "学术指导与论文架构",
        "strengths": ["选题把关", "论证逻辑", "学术规范"],
    },
    "lobster-001": {
        "display_name": "小龙虾",
        "specialty": "系统架构与协议设计",
        "strengths": ["协议设计", "系统架构", "涌现分析"],
    },
    "museum-001": {
        "display_name": "院史馆小龙虾",
        "specialty": "文献综述与知识管理",
        "strengths": ["文献检索", "知识图谱", "档案管理"],
    },
}

# 共享根路径（容器内挂载点或本地模拟路径）
SHARED_ROOT = os.environ.get(
    "LOBSTER_SHARED_ROOT",
    "/shared/training/paper",
)

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _ts() -> str:
    """返回当前时间戳字符串。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _ensure_dir(path: str) -> None:
    """确保目录存在，若不存在则递归创建。"""
    os.makedirs(path, exist_ok=True)


def _role_dir(role: str) -> str:
    """返回角色在共享目录中的根路径。"""
    return os.path.join(SHARED_ROOT, role)


def _inbox_dir(role: str) -> str:
    """返回角色收件箱路径。"""
    return os.path.join(_role_dir(role), "inbox")


def _outbox_dir(role: str) -> str:
    """返回角色发件箱路径。"""
    return os.path.join(_role_dir(role), "outbox")


def _profile_path(role: str) -> str:
    """返回角色档案文件路径。"""
    return os.path.join(_role_dir(role), "profile.json")


def _history_dir(role: str) -> str:
    """返回角色练习历史目录。"""
    return os.path.join(_role_dir(role), "exercise_history")


# ---------------------------------------------------------------------------
# 核心函数
# ---------------------------------------------------------------------------


def log(role: str, message: str) -> None:
    """
    打印带时间戳和角色标识的日志信息。

    参数:
        role: 角色名称
        message: 日志消息内容
    """
    print(f"[{_ts()}] [{role}] {message}", flush=True)


def load_profile(role: str) -> dict:
    """
    加载角色档案。若档案不存在，则创建默认档案并保存。

    参数:
        role: 角色名称

    返回:
        角色档案字典，包含 level / xp / tasks_completed / skill_scores 等字段。
    """
    path = _profile_path(role)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # 创建默认档案
    role_meta = ROLES.get(role, {})
    profile = {
        "role": role,
        "display_name": role_meta.get("display_name", role),
        "specialty": role_meta.get("specialty", "通用学术写作"),
        "level": 1,
        "xp": 0,
        "tasks_completed": 0,
        "skill_scores": {
            "literature_mining": 50,
            "outline_writing": 50,
            "section_drafting": 50,
            "peer_review": 50,
            "revision_polish": 50,
        },
        "papers_authored": [],
        "papers_reviewed": [],
        "created_at": _ts(),
        "updated_at": _ts(),
    }
    save_profile(role, profile)
    return profile


def save_profile(role: str, profile: dict) -> None:
    """
    保存角色档案到 profile.json。

    参数:
        role: 角色名称
        profile: 要保存的档案字典
    """
    _ensure_dir(_role_dir(role))
    profile["updated_at"] = _ts()
    path = _profile_path(role)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def check_task(role: str) -> Optional[dict]:
    """
    轮询检查角色收件箱中是否存在待处理的任务 JSON 文件。

    扫描 inbox 目录下所有 .json 文件，取最早创建的一个作为当前任务。
    读取后会将该文件从 inbox 中移除（防止重复处理）。

    参数:
        role: 角色名称

    返回:
        任务字典，或 None（无待处理任务时）。
    """
    inbox = _inbox_dir(role)
    _ensure_dir(inbox)

    json_files = sorted(
        [f for f in os.listdir(inbox) if f.endswith(".json")]
    )
    if not json_files:
        return None

    task_file = json_files[0]
    task_path = os.path.join(inbox, task_file)

    try:
        with open(task_path, "r", encoding="utf-8") as f:
            task = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        log(role, f"读取任务文件失败，跳过: {task_file} ({e})")
        # 将损坏的文件移到回收目录
        trash_dir = os.path.join(_role_dir(role), "trash")
        _ensure_dir(trash_dir)
        os.rename(task_path, os.path.join(trash_dir, task_file))
        return None

    # 从收件箱移除已读取的任务
    os.remove(task_path)
    log(role, f"收到任务: {task.get('type', 'unknown')} (id={task.get('id', 'N/A')})")
    return task


# ---------------------------------------------------------------------------
# 任务执行：各类型的具体实现
# ---------------------------------------------------------------------------


def _do_literature_mining(role: str, task: dict) -> dict:
    """
    执行文献挖掘任务：生成文献综述摘要，包含关键论文、主题和研究空白。

    参数:
        role: 执行者角色
        task: 任务字典，可含 topic / max_papers 等参数

    返回:
        结果字典，包含 literature_summary。
    """
    topic = task.get("topic", "龙虾网络协作学习")
    max_papers = task.get("max_papers", random.randint(8, 15))

    log(role, f"开始文献挖掘: 主题='{topic}', 最大论文数={max_papers}")

    # 模拟检索过程
    time.sleep(random.uniform(0.5, 1.5))

    # 生成模拟论文列表
    sample_authors = [
        "Zhang & Li", "Wang et al.", "Chen & Liu", "Smith & Johnson",
        "Garcia et al.", "Tanaka & Sato", "Mueller et al.", "Park & Kim",
        "Zhuge et al.", "Brown & Davis", "Patel et al.", "Anderson et al.",
        "Lee & Choi", "Martinez et al.", "Yamamoto et al.",
    ]
    sample_years = list(range(2018, 2025))

    papers = []
    for i in range(max_papers):
        papers.append({
            "id": i + 1,
            "title": f"{topic}相关研究论文 #{i + 1}",
            "authors": random.choice(sample_authors),
            "year": random.choice(sample_years),
            "journal": random.choice([
                "计算机学报", "软件学报", "Journal of AI Research",
                "IEEE Trans. on Education", "Computers & Education",
                "ACM Computing Surveys", "Nature Machine Intelligence",
            ]),
            "relevance_score": round(random.uniform(0.6, 0.98), 2),
        })

    # 生成主题聚类
    themes = [
        {"theme": "协作学习理论框架", "paper_count": random.randint(2, 5)},
        {"theme": "AI 辅助教学系统设计", "paper_count": random.randint(2, 4)},
        {"theme": "多智能体协同机制", "paper_count": random.randint(1, 3)},
        {"theme": "学习效果评估方法", "paper_count": random.randint(2, 4)},
        {"theme": "知识图谱与推荐系统", "paper_count": random.randint(1, 3)},
    ]

    # 识别研究空白
    gaps = [
        "现有研究多集中于单一智能体，缺乏多角色协作的实证分析",
        "对于 AI 智能体在学术写作中的协同模式缺乏系统性框架",
        "纵向研究不足，多数实验周期短于一个学期",
        "跨文化、跨学科的泛化能力验证较为薄弱",
        "人机协作中的信任建立与认知负荷管理尚待深入探讨",
    ]

    summary = {
        "topic": topic,
        "total_papers_found": max_papers,
        "papers": papers,
        "themes": themes,
        "research_gaps": random.sample(gaps, k=min(3, len(gaps))),
        "summary_text": (
            f"本次文献挖掘围绕「{topic}」主题，从 {max_papers} 篇核心文献中"
            f"提炼出 {len(themes)} 个主要研究主题，并识别出 "
            f"{min(3, len(gaps))} 个关键研究空白。"
            f"文献时间跨度覆盖 2018-2024 年，涵盖中英文顶级期刊与会议。"
        ),
    }

    log(role, f"文献挖掘完成: 找到 {max_papers} 篇论文, {len(themes)} 个主题")
    return {"literature_summary": summary}


def _do_outline_writing(role: str, task: dict) -> dict:
    """
    执行大纲撰写任务：生成包含章节与子章节的论文大纲。

    参数:
        role: 执行者角色
        task: 任务字典，可含 paper_title / research_topic 等参数

    返回:
        结果字典，包含 outline。
    """
    paper_title = task.get("paper_title", "基于龙虾网络的多智能体协作论文写作系统")
    research_topic = task.get("research_topic", "AI 多智能体协作学术写作")

    log(role, f"开始撰写论文大纲: '{paper_title}'")
    time.sleep(random.uniform(0.5, 1.5))

    outline = {
        "title": paper_title,
        "research_topic": research_topic,
        "sections": [
            {
                "id": 1,
                "title": "摘要 (Abstract)",
                "word_count_target": 300,
                "subsections": [],
                "key_points": [
                    "研究背景与动机",
                    "提出的方法/系统",
                    "核心实验结果",
                    "主要贡献",
                ],
            },
            {
                "id": 2,
                "title": "引言 (Introduction)",
                "word_count_target": 1200,
                "subsections": [
                    {"id": "2.1", "title": "研究背景", "word_count_target": 400},
                    {"id": "2.2", "title": "问题陈述", "word_count_target": 300},
                    {"id": "2.3", "title": "研究贡献", "word_count_target": 300},
                    {"id": "2.4", "title": "论文结构", "word_count_target": 200},
                ],
                "key_points": [
                    "阐述学术写作协作的痛点",
                    "引出多智能体系统的必要性",
                    "明确列出 3-4 项核心贡献",
                ],
            },
            {
                "id": 3,
                "title": "相关工作 (Related Work)",
                "word_count_target": 1500,
                "subsections": [
                    {"id": "3.1", "title": "协作写作工具", "word_count_target": 500},
                    {"id": "3.2", "title": "AI 辅助写作系统", "word_count_target": 500},
                    {"id": "3.3", "title": "多智能体协作框架", "word_count_target": 500},
                ],
                "key_points": [
                    "综述现有协作写作工具的局限性",
                    "分析 AI 写作助手的技术路线",
                    "对比多智能体系统的异同",
                ],
            },
            {
                "id": 4,
                "title": "方法论 (Methodology)",
                "word_count_target": 2000,
                "subsections": [
                    {"id": "4.1", "title": "系统架构设计", "word_count_target": 600},
                    {"id": "4.2", "title": "智能体角色定义", "word_count_target": 500},
                    {"id": "4.3", "title": "协作协议与通信机制", "word_count_target": 500},
                    {"id": "4.4", "title": "质量评估框架", "word_count_target": 400},
                ],
                "key_points": [
                    "描述龙虾网络拓扑结构",
                    "定义各智能体职责与能力",
                    "说明任务分发与结果汇聚流程",
                ],
            },
            {
                "id": 5,
                "title": "实验 (Experiments)",
                "word_count_target": 1800,
                "subsections": [
                    {"id": "5.1", "title": "实验设置", "word_count_target": 400},
                    {"id": "5.2", "title": "评估指标", "word_count_target": 400},
                    {"id": "5.3", "title": "主实验结果", "word_count_target": 600},
                    {"id": "5.4", "title": "消融实验", "word_count_target": 400},
                ],
                "key_points": [
                    "描述数据集与基准方法",
                    "列出 8 维评估指标体系",
                    "展示对比实验与统计显著性",
                ],
            },
            {
                "id": 6,
                "title": "结果与讨论 (Results & Discussion)",
                "word_count_target": 1500,
                "subsections": [
                    {"id": "6.1", "title": "定量结果分析", "word_count_target": 500},
                    {"id": "6.2", "title": "定性案例分析", "word_count_target": 500},
                    {"id": "6.3", "title": "局限性与未来工作", "word_count_target": 500},
                ],
                "key_points": [
                    "解读关键实验数据",
                    "提供具体的写作案例对比",
                    "坦诚讨论系统的不足",
                ],
            },
            {
                "id": 7,
                "title": "结论 (Conclusion)",
                "word_count_target": 500,
                "subsections": [],
                "key_points": [
                    "总结核心发现",
                    "强调实践意义",
                    "展望后续研究方向",
                ],
            },
            {
                "id": 8,
                "title": "参考文献 (References)",
                "word_count_target": 0,
                "subsections": [],
                "key_points": ["预计引用 30-50 篇文献"],
            },
        ],
        "total_word_count_target": 8800,
        "estimated_figures": 6,
        "estimated_tables": 4,
    }

    log(role, f"大纲撰写完成: {len(outline['sections'])} 个章节, "
              f"目标字数 {outline['total_word_count_target']}")
    return {"outline": outline}


def _do_section_drafting(role: str, task: dict) -> dict:
    """
    执行章节草稿撰写任务：针对指定章节生成学术文本草稿。

    参数:
        role: 执行者角色
        task: 任务字典，必须含 section 字段，可选 paper_title / outline 等

    返回:
        结果字典，包含 draft。
    """
    section = task.get("section", "abstract")
    paper_title = task.get("paper_title", "基于龙虾网络的多智能体协作论文写作系统")

    log(role, f"开始撰写章节草稿: {section}")
    time.sleep(random.uniform(1.0, 2.5))

    # 各章节模拟草稿内容
    draft_templates = {
        "abstract": {
            "section": "摘要",
            "word_count": random.randint(250, 320),
            "content": (
                "学术写作是一项高度协作性的知识工作，传统的人工写作模式面临效率低、"
                "质量参差不齐等问题。本文提出了一种基于龙虾网络拓扑结构的多智能体协作"
                "论文写作系统（LobsterWriter），通过定义四类异质智能体角色（编码者、"
                "文献分析师、实验设计师、学术导师），构建了一个分布式的论文生产流水线。"
                "系统采用文件系统驱动的异步通信协议，支持文献挖掘、大纲生成、章节撰写、"
                "同行评审和修订润色的全流程自动化。在 30 篇模拟论文的实验中，LobsterWriter "
                "在 8 维质量评估框架下的综合得分较单智能体基线提升了 23.7%，"
                "其中论证逻辑（+31.2%）和文献综述（+28.5%）的改进最为显著。"
                "本研究为 AI 驱动的学术写作协作提供了新的范式参考。"
            ),
            "keywords": [
                "多智能体系统", "协作写作", "龙虾网络",
                "学术写作自动化", "同行评审",
            ],
        },
        "introduction": {
            "section": "引言",
            "word_count": random.randint(1000, 1400),
            "content": (
                "1. 研究背景\n\n"
                "学术写作是科研工作的核心产出形式。随着人工智能技术的飞速发展，"
                "大型语言模型（LLM）已展现出在文本生成方面的强大能力，然而，"
                "单一模型在长篇学术写作中仍存在一致性和深度不足的问题。\n\n"
                "2. 问题陈述\n\n"
                "当前 AI 辅助写作系统主要采用单智能体模式，缺乏角色分工与相互审查"
                "机制，导致产出论文在论证逻辑、文献覆盖和格式规范等方面存在系统性缺陷。\n\n"
                "3. 研究贡献\n\n"
                "本文做出以下四项核心贡献：\n"
                "(1) 提出了面向学术写作的龙虾网络多智能体拓扑结构；\n"
                "(2) 设计了四类互补型智能体角色及其协作协议；\n"
                "(3) 构建了涵盖 8 个维度的论文质量评估框架；\n"
                "(4) 通过系统实验验证了多智能体协作的有效性。"
            ),
        },
        "methodology": {
            "section": "方法论",
            "word_count": random.randint(1800, 2200),
            "content": (
                "4.1 系统架构设计\n\n"
                "LobsterWriter 采用去中心化的文件系统驱动架构。各智能体通过共享目录"
                "（/shared/training/paper/）中的 inbox/outbox 机制进行异步通信，"
                "以 JSON 文件作为任务与结果的序列化载体。\n\n"
                "4.2 智能体角色定义\n\n"
                "系统定义四类智能体角色：\n"
                "- Qoder（编码者）：负责方法论描述与数据分析部分的撰写\n"
                "- 小陈（文献分析师）：负责文献挖掘与综述生成\n"
                "- 诸葛侠（实验设计师）：负责实验设计与结果呈现\n"
                "- 诸葛教授（学术导师）：负责整体架构指导与质量把关\n\n"
                "4.3 协作协议\n\n"
                "任务流转遵循以下阶段：\n"
                "阶段 1: 文献挖掘 → 阶段 2: 大纲撰写 → 阶段 3: 章节草稿 → "
                "阶段 4: 同行评审 → 阶段 5: 修订润色\n\n"
                "4.4 质量评估框架\n\n"
                "设计了 8 维评估指标体系，涵盖结构完整性、摘要质量、文献综述、"
                "方法论、数据分析、论证逻辑、格式规范和引用质量。"
            ),
        },
        "results": {
            "section": "结果",
            "word_count": random.randint(1500, 1900),
            "content": (
                "5.1 实验设置\n\n"
                "实验在包含 4 个智能体的龙虾网络上进行，共生成 30 篇模拟论文。"
                "基线系统为单智能体（仅使用教授角色）的写作模式。\n\n"
                "5.2 评估指标\n\n"
                "采用 8 维质量评估框架，每个维度评分范围 0-100。\n\n"
                "5.3 主实验结果\n\n"
                "表 1 展示了 LobsterWriter 与基线系统在各维度上的平均得分对比。\n"
                "- 结构完整性: 基线 62.3 → 系统 78.5 (+26.0%)\n"
                "- 摘要质量: 基线 58.7 → 系统 75.2 (+28.1%)\n"
                "- 文献综述: 基线 55.1 → 系统 70.8 (+28.5%)\n"
                "- 方法论: 基线 64.8 → 系统 79.3 (+22.4%)\n"
                "- 数据分析: 基线 60.2 → 系统 74.6 (+23.9%)\n"
                "- 论证逻辑: 基线 52.4 → 系统 68.7 (+31.2%)\n"
                "- 格式规范: 基线 70.5 → 系统 82.1 (+16.5%)\n"
                "- 引用质量: 基线 57.9 → 系统 73.4 (+26.8%)\n\n"
                "综合得分: 基线 60.2 → 系统 74.4 (+23.7%)，"
                "t 检验 p < 0.001，差异具有统计学显著性。\n\n"
                "5.4 消融实验\n\n"
                "移除同行评审环节后综合得分下降 12.3%，"
                "移除多角色分工后下降 18.6%，验证了各组件的有效性。"
            ),
        },
        "discussion": {
            "section": "讨论",
            "word_count": random.randint(1200, 1600),
            "content": (
                "6.1 定量结果分析\n\n"
                "实验结果表明，多智能体协作模式在论文质量上具有显著优势。"
                "论证逻辑维度改进最大（+31.2%），这主要归功于同行评审环节引入的"
                "批判性反馈机制。\n\n"
                "6.2 定性案例分析\n\n"
                "以第 12 号论文为例，经过两轮评审-修订循环后，"
                "论证逻辑得分从 54 提升至 82，文献引用数量从 15 增至 38。\n\n"
                "6.3 局限性与未来工作\n\n"
                "本研究存在以下局限：\n"
                "(1) 实验基于模拟数据，尚需在真实学术写作场景中验证\n"
                "(2) 智能体数量固定为 4，未探索更大规模的协作模式\n"
                "(3) 评估框架依赖自动化指标，缺乏人类专家评审\n"
                "未来工作将聚焦于：引入人类反馈的强化学习、"
                "跨语言和跨学科的泛化实验、以及动态角色分配策略。"
            ),
        },
    }

    draft = draft_templates.get(section, {
        "section": section,
        "word_count": random.randint(500, 1000),
        "content": f"[{section} 章节草稿内容 — 由 {role} 撰写]",
    })

    # 添加元数据
    draft["author"] = role
    draft["paper_title"] = paper_title
    draft["draft_version"] = task.get("draft_version", 1)
    draft["timestamp"] = _ts()
    draft["char_count"] = len(draft.get("content", ""))

    log(role, f"章节草稿完成: {draft['section']}, "
              f"{draft['word_count']} 字, "
              f"v{draft['draft_version']}")
    return {"draft": draft}


def _do_peer_review(role: str, task: dict) -> dict:
    """
    执行同行评审任务：对论文草稿进行 8 维度评价并生成反馈报告。

    参数:
        role: 评审者角色
        task: 任务字典，可含 paper_data / author / draft 等参数

    返回:
        结果字典，包含 review_report。
    """
    paper_data = task.get("paper_data", task.get("draft", {}))
    author = task.get("author", "unknown")
    section = paper_data.get("section", "全文")

    log(role, f"开始同行评审: 作者={author}, 章节={section}")
    time.sleep(random.uniform(1.0, 2.0))

    # 8 个评审维度
    dimensions = {
        "structure": {
            "name": "结构完整性",
            "description": "IMRaD 格式遵循度、逻辑流畅性",
        },
        "abstract": {
            "name": "摘要质量",
            "description": "简洁性、完整性、关键词覆盖度",
        },
        "literature_review": {
            "name": "文献综述",
            "description": "广度、时效性、批判性分析",
        },
        "methodology": {
            "name": "方法论",
            "description": "严谨性、可复现性、适当性",
        },
        "data_analysis": {
            "name": "数据分析",
            "description": "统计有效性、可视化质量",
        },
        "argumentation": {
            "name": "论证逻辑",
            "description": "论点-证据-论据结构",
        },
        "formatting": {
            "name": "格式规范",
            "description": "LaTeX/Word 标准、图表质量",
        },
        "citations": {
            "name": "引用质量",
            "description": "引用数量、格式一致性、自引比例",
        },
    }

    scores = {}
    feedback_items = []

    for dim_key, dim_info in dimensions.items():
        # 模拟评分（基于角色专长有所浮动）
        base_score = random.randint(55, 85)
        # 评审者自身的专长维度打分偏高（更宽容）
        role_meta = ROLES.get(role, {})
        specialty = role_meta.get("specialty", "")
        if dim_info["name"] in specialty or any(
            s in dim_info["name"] for s in role_meta.get("strengths", [])
        ):
            base_score = min(100, base_score + random.randint(3, 10))

        scores[dim_key] = {
            "score": base_score,
            "name": dim_info["name"],
            "description": dim_info["description"],
        }

        # 生成分维度反馈
        if base_score >= 80:
            verdict = "优秀"
            suggestion = "可进一步打磨细节表述"
        elif base_score >= 65:
            verdict = "良好"
            suggestion = f"建议加强{dim_info['name']}方面的深度"
        else:
            verdict = "待改进"
            suggestion = f"{dim_info['name']}需要重点修改，参考相关范例进行重构"

        feedback_items.append({
            "dimension": dim_key,
            "dimension_name": dim_info["name"],
            "score": base_score,
            "verdict": verdict,
            "suggestion": suggestion,
        })

    overall = sum(s["score"] for s in scores.values()) / len(scores)

    review_report = {
        "reviewer": role,
        "author": author,
        "section_reviewed": section,
        "timestamp": _ts(),
        "scores": scores,
        "overall_score": round(overall, 1),
        "feedback": feedback_items,
        "general_comments": (
            f"本文由 {author} 撰写，{role} 进行同行评审。"
            f"综合得分 {round(overall, 1)}/100。"
            f"整体而言，文章具备基本的学术规范，但在论证深度和文献覆盖面上仍有提升空间。"
            f"建议重点关注得分低于 70 的维度，进行针对性修订。"
        ),
        "revision_priority": [
            item["dimension"]
            for item in sorted(feedback_items, key=lambda x: x["score"])[:3]
        ],
    }

    log(role, f"同行评审完成: 综合评分 {round(overall, 1)}/100, "
              f"优先修订: {review_report['revision_priority']}")
    return {"review_report": review_report}


def _do_revision_polish(role: str, task: dict) -> dict:
    """
    执行修订润色任务：根据评审反馈对章节草稿进行修改。

    参数:
        role: 执行者角色
        task: 任务字典，可含 draft / feedback / review_report 等参数

    返回:
        结果字典，包含 revised_draft 和 revision_log。
    """
    draft = task.get("draft", {})
    feedback = task.get("feedback", task.get("review_report", {}).get("feedback", []))

    section = draft.get("section", "unknown")
    original_version = draft.get("draft_version", 1)

    log(role, f"开始修订润色: 章节={section}, 原版本=v{original_version}")
    time.sleep(random.uniform(0.8, 2.0))

    # 模拟修订过程
    revision_actions = []
    for item in feedback:
        dim = item.get("dimension", item.get("dimension_name", "unknown"))
        score = item.get("score", 70)
        if score < 75:
            revision_actions.append({
                "dimension": dim,
                "action": f"针对「{dim}」进行了重点修订，补充了相关内容",
                "score_before": score,
                "score_after": min(100, score + random.randint(8, 20)),
            })
        else:
            revision_actions.append({
                "dimension": dim,
                "action": f"对「{dim}」进行了微调润色",
                "score_before": score,
                "score_after": min(100, score + random.randint(2, 8)),
            })

    # 构造修订后的草稿
    revised_draft = dict(draft)
    revised_draft["draft_version"] = original_version + 1
    revised_draft["revised_by"] = role
    revised_draft["revision_timestamp"] = _ts()
    revised_draft["word_count"] = draft.get("word_count", 500) + random.randint(50, 200)
    revised_draft["content"] = (
        draft.get("content", "")
        + f"\n\n[修订 v{original_version + 1}：根据评审反馈进行了 {len(revision_actions)} 项修改]"
    )

    # 修订日志
    revision_log = {
        "original_version": original_version,
        "new_version": original_version + 1,
        "revisor": role,
        "timestamp": _ts(),
        "actions": revision_actions,
        "total_improvements": len(revision_actions),
        "avg_score_before": round(
            sum(a["score_before"] for a in revision_actions) / max(len(revision_actions), 1), 1
        ),
        "avg_score_after": round(
            sum(a["score_after"] for a in revision_actions) / max(len(revision_actions), 1), 1
        ),
    }

    log(role, f"修订润色完成: v{original_version} → v{original_version + 1}, "
              f"{len(revision_actions)} 项修改, "
              f"均分 {revision_log['avg_score_before']} → {revision_log['avg_score_after']}")
    return {"revised_draft": revised_draft, "revision_log": revision_log}


# ---------------------------------------------------------------------------
# 任务调度与提交
# ---------------------------------------------------------------------------

# 任务类型 → 执行函数的映射
TASK_EXECUTORS = {
    "literature_mining": _do_literature_mining,
    "outline_writing": _do_outline_writing,
    "section_drafting": _do_section_drafting,
    "peer_review": _do_peer_review,
    "revision_polish": _do_revision_polish,
}

# 任务类型 → 经验值奖励
XP_REWARDS = {
    "literature_mining": 120,
    "outline_writing": 150,
    "section_drafting": 200,
    "peer_review": 180,
    "revision_polish": 160,
}


def execute_task(role: str, task: dict) -> dict:
    """
    根据任务类型分发并执行对应的处理逻辑。

    参数:
        role: 执行者角色
        task: 任务字典，必须包含 type 字段

    返回:
        执行结果字典；若类型未知则返回 error 字段。
    """
    task_type = task.get("type", "")
    task_id = task.get("id", f"auto_{int(time.time())}")

    log(role, f"执行任务: type={task_type}, id={task_id}")

    executor = TASK_EXECUTORS.get(task_type)
    if executor is None:
        error_msg = f"未知的任务类型: {task_type}"
        log(role, error_msg)
        return {"error": error_msg, "task_id": task_id}

    try:
        result = executor(role, task)
    except Exception as e:
        error_msg = f"任务执行异常: {type(e).__name__}: {e}"
        log(role, error_msg)
        return {"error": error_msg, "task_id": task_id}

    # 附加元数据
    result["task_id"] = task_id
    result["task_type"] = task_type
    result["executor"] = role
    result["completed_at"] = _ts()

    return result


def submit_result(role: str, result: dict) -> None:
    """
    将任务执行结果写入 outbox，更新角色档案和练习历史。

    参数:
        role: 执行者角色
        result: 执行结果字典
    """
    outbox = _outbox_dir(role)
    _ensure_dir(outbox)

    task_type = result.get("task_type", "unknown")
    task_id = result.get("task_id", f"result_{int(time.time())}")

    # --- 写入发件箱 ---
    result_file = os.path.join(outbox, f"{task_type}_{task_id}.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    log(role, f"结果已写入: {result_file}")

    # --- 更新角色档案 ---
    profile = load_profile(role)
    profile["tasks_completed"] += 1

    # 增加经验值
    xp_gain = XP_REWARDS.get(task_type, 100)
    profile["xp"] += xp_gain

    # 升级判定（每 500 XP 升一级）
    new_level = (profile["xp"] // 500) + 1
    if new_level > profile["level"]:
        log(role, f"升级! Lv.{profile['level']} → Lv.{new_level}")
        profile["level"] = new_level

    # 更新技能分数（小幅提升）
    if task_type in profile["skill_scores"]:
        old_score = profile["skill_scores"][task_type]
        improvement = random.randint(2, 8)
        profile["skill_scores"][task_type] = min(100, old_score + improvement)

    save_profile(role, profile)

    # --- 记录练习历史 ---
    history_dir = _history_dir(role)
    _ensure_dir(history_dir)
    history_entry = {
        "task_id": task_id,
        "task_type": task_type,
        "timestamp": _ts(),
        "xp_gained": xp_gain,
        "level": profile["level"],
        "skill_scores": profile["skill_scores"],
        "result_file": result_file,
    }
    history_file = os.path.join(
        history_dir,
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_type}.json",
    )
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history_entry, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 主循环
# ---------------------------------------------------------------------------


def main() -> None:
    """
    智能体主入口：验证角色参数后进入轮询循环，持续监听并处理收件箱中的任务。

    退出方式:
        - 收到 SIGTERM / SIGINT 信号
        - 在 inbox 中放入 {"type": "shutdown"} 的任务
    """
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <role_name>")
        print(f"可用角色: {', '.join(ROLES.keys())}")
        sys.exit(1)

    role = sys.argv[1]
    if role not in ROLES:
        print(f"未知角色: {role}")
        print(f"可用角色: {', '.join(ROLES.keys())}")
        sys.exit(1)

    # 初始化目录和档案
    for d in [_inbox_dir(role), _outbox_dir(role), _history_dir(role)]:
        _ensure_dir(d)
    profile = load_profile(role)

    role_meta = ROLES[role]
    log(role, f"论文写作智能体启动 — {role_meta['display_name']} "
              f"(专长: {role_meta['specialty']})")
    log(role, f"档案加载: Lv.{profile['level']}, "
              f"XP={profile['xp']}, "
              f"已完成任务={profile['tasks_completed']}")
    log(role, f"监听收件箱: {_inbox_dir(role)} (每 {CHECK_INTERVAL}s 轮询)")

    idle_count = 0
    while True:
        task = check_task(role)

        if task is not None:
            # 检查是否为停机指令
            if task.get("type") == "shutdown":
                log(role, "收到停机指令，正在退出...")
                break

            idle_count = 0
            result = execute_task(role, task)
            submit_result(role, result)
            log(role, "任务处理完毕，继续监听...")
        else:
            idle_count += 1
            if idle_count % 12 == 0:  # 每 60 秒输出一次心跳
                log(role, f"等待任务中... (空闲 {idle_count * CHECK_INTERVAL}s)")

        time.sleep(CHECK_INTERVAL)

    log(role, "智能体已停止。")


if __name__ == "__main__":
    main()
