#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小陈和诸葛虾 - 计算机网络联合学习计划
"""

import json
import os
from datetime import datetime

# === 学习计划 ===
LEARNING_PLAN = {
    "students": ["小陈", "诸葛虾"],
    "course": "高级网络通信原理",
    "start_date": "2026-06-25",
    "phases": [
        {
            "name": "基础篇",
            "chapters": ["ch1", "ch2_3", "ch4_5"],
            "schedule": {
                "day1": {"ch1": "绪论 - 网络技术演进", "task": "观看动画+完成5题"},
                "day2": {"ch2_3": "交换机原理与STP算法", "task": "观看动画+完成10题"},
                "day3": {"ch4_5": "路由器原理与路由协议", "task": "观看动画+完成10题"}
            }
        },
        {
            "name": "SDN篇",
            "chapters": ["ch13", "ch14", "ch15"],
            "schedule": {
                "day4": {"ch13": "OpenFlow流表实战", "task": "交互实验+完成15题"},
                "day5": {"ch14": "VXLAN网络虚拟化", "task": "交互实验+完成15题"},
                "day6": {"ch15": "OpenFlow计量表与组表", "task": "交互实验+完成15题"}
            }
        },
        {
            "name": "融合篇",
            "chapters": ["ch16"],
            "schedule": {
                "day7": {"ch16": "云网一体化", "task": "配置实验+完成20题"}
            }
        }
    ]
}

# === 学习进度 ===
PROGRESS = {
    "小陈": {
        "current_chapter": None,
        "completed_chapters": [],
        "problems_solved": 0,
        "wrong_book": [],
        "started_at": datetime.now().isoformat()
    },
    "诸葛虾": {
        "current_chapter": None,
        "completed_chapters": [],
        "problems_solved": 0,
        "wrong_book": [],
        "started_at": datetime.now().isoformat()
    }
}


def start_learning(student, chapter):
    """开始学习章节"""
    PROGRESS[student]["current_chapter"] = chapter
    print(f"📖 {student} 开始学习: {chapter}")
    return PROGRESS[student]


def complete_learning(student, chapter, correct_count, total_count):
    """完成章节学习"""
    if chapter not in PROGRESS[student]["completed_chapters"]:
        PROGRESS[student]["completed_chapters"].append(chapter)
    PROGRESS[student]["problems_solved"] += total_count
    PROGRESS[student]["current_chapter"] = None

    accuracy = correct_count / max(total_count, 1) * 100
    print(f"✅ {student} 完成: {chapter}")
    print(f"   做题: {total_count}题 | 正确: {correct_count}题 | 准确率: {accuracy:.1f}%")
    return PROGRESS[student]


def get_progress(student):
    """获取学习进度"""
    p = PROGRESS[student]
    return {
        "student": student,
        "completed": len(p["completed_chapters"]),
        "total": 7,
        "progress_percent": f"{len(p['completed_chapters'])/7*100:.1f}%",
        "problems_solved": p["problems_solved"],
        "current_chapter": p["current_chapter"]
    }


if __name__ == "__main__":
    print("🦞 小陈 & 诸葛虾 - 计算机网络联合学习")
    print("=" * 50)

    # 开始第一章学习
    for student in LEARNING_PLAN["students"]:
        start_learning(student, "ch1")

    # 模拟完成学习
    for student in LEARNING_PLAN["students"]:
        complete_learning(student, "ch1", 4, 5)

    # 查看进度
    for student in LEARNING_PLAN["students"]:
        print(f"\n📊 {student} 进度:")
        p = get_progress(student)
        print(f"   完成: {p['completed']}/{p['total']} ({p['progress_percent']})")
        print(f"   做题: {p['problems_solved']}题")
