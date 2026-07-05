#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qoder 技术助教 (Technical Instructor)
- 每周五自动触发
- qoder从本周错题中提炼1-2个核心知识点
- 生成教学文档（Markdown格式）
- 其他学员基于教学文档做针对性练习
"""

import json
import os
import random
from datetime import datetime
from pathlib import Path

# === 配置 ===
QUEUE_DIR = "/shared/messages/queue"
TRAINING_DIR = "/shared/training/go"
INSTRUCTOR_DIR = os.path.join(TRAINING_DIR, "instructor")
LOG_FILE = os.path.join(INSTRUCTOR_DIR, "instructor.log")

PLAYERS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "wrong_book": os.path.join(TRAINING_DIR, "xiaochen", "wrong_book.json"),
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "wrong_book": os.path.join(TRAINING_DIR, "zhuguxia", "wrong_book.json"),
    },
    "qoder": {
        "name": "qoder",
        "type": "实战型",
        "wrong_book": os.path.join(TRAINING_DIR, "qoder", "wrong_book.json"),
    },
}

# 知识点模板
KNOWLEDGE_POINTS = {
    "死活": {
        "入门": ["基本眼位（直三/曲三/丁四）", "气的概念", "连接与切断"],
        "初级": ["刀五与梅花五", "板六与常见活形", "点眼与做眼"],
        "中级": ["对杀技巧", "劫争基础", "双活棋形"],
        "高级": ["大型对杀", "连环劫", "长生/三劫循环"],
    },
    "手筋": {
        "入门": ["扑与倒扑", "征子", "枷吃"],
        "初级": ["挖与分断", "尖与跳", "夹与跨"],
        "中级": ["组合手筋", "弃子战术", "声东击西"],
        "高级": ["复杂对杀手筋", "罕见手筋", "AI新手筋"],
    },
    "布局": {
        "入门": ["金角银边草肚皮", "星位开局", "小目开局"],
        "初级": ["中国流", "小林流", "三连星"],
        "中级": ["AI布局", "新型定式", "布局理论"],
        "高级": ["复杂布局", "布局陷阱", "AI新型变例"],
    },
    "官子": {
        "入门": ["大小判断", "先手官子", "后手官子"],
        "初级": ["逆收官子", "双先官子", "官子次序"],
        "中级": ["复杂官子", "官子计算", "官子手筋"],
        "高级": ["AI官子", "极限官子", "官子理论"],
    },
    "定式": {
        "入门": ["星位定式", "小目定式", "三三定式"],
        "初级": ["常见定式", "定式选择", "定式变化"],
        "中级": ["AI定式", "新型定式", "定式陷阱"],
        "高级": ["复杂定式", "定式理论", "AI新型变例"],
    },
}


def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_wrong_book(player_key):
    """加载错题本"""
    wrong_book_file = PLAYERS[player_key]["wrong_book"]
    if os.path.exists(wrong_book_file):
        with open(wrong_book_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def analyze_wrong_books():
    """分析所有学员的错题，找出共性薄弱点"""
    all_wrong = {}
    for player_key in PLAYERS:
        wrong_book = load_wrong_book(player_key)
        for entry in wrong_book:
            problem_type = entry.get("type", "未知")
            difficulty = entry.get("difficulty", "未知")
            key = f"{problem_type}/{difficulty}"
            if key not in all_wrong:
                all_wrong[key] = []
            all_wrong[key].append({
                "player": PLAYERS[player_key]["name"],
                "problem_id": entry.get("problem_id"),
                "title": entry.get("title"),
            })

    # 按错误人数排序
    sorted_weaknesses = sorted(all_wrong.items(), key=lambda x: len(x[1]), reverse=True)
    return sorted_weaknesses


def generate_teaching_document(weakness_key, weak_entries, week_number):
    """生成教学文档"""
    problem_type, difficulty = weakness_key.split("/")
    knowledge_points = KNOWLEDGE_POINTS.get(problem_type, {}).get(difficulty, [])

    # 选取1-2个知识点
    selected_kps = random.sample(knowledge_points, min(2, len(knowledge_points)))

    # 生成Markdown文档
    doc = f"""# 技术微课 - {problem_type} {difficulty} 专项训练

> **讲师**: qoder (技术尖兵)
> **日期**: {datetime.now().strftime('%Y-%m-%d')}
> **周次**: 第{week_number}周
> **薄弱点**: {weakness_key} ({len(weak_entries)} 人出错)

## 一、知识点概述

本周分析发现，{len(weak_entries)} 位学员在 {problem_type} {difficulty} 题目上出现错误。
主要薄弱点集中在以下知识点：

"""
    for i, kp in enumerate(selected_kps, 1):
        doc += f"### 知识点{i}: {kp}\n\n"
        doc += f"**核心要点**:\n\n"
        doc += f"- 理解{kp}的基本概念和原理\n"
        doc += f"- 掌握{kp}的常见棋形和变化\n"
        doc += f"- 能够在实战中识别和应用{kp}\n\n"

        # 根据知识点生成示例
        if "眼位" in kp:
            doc += f"**示例棋形**:\n\n"
            doc += f"```\n"
            doc += f"  A B C D E\n"
            doc += f"1 . . . . .\n"
            doc += f"2 . X O . .\n"
            doc += f"3 . X . O .\n"
            doc += f"4 . . . . .\n"
            doc += f"```\n\n"
            doc += f"黑棋需要做活，关键是做出两个真眼。正解：A3 做眼。\n\n"
        elif "手筋" in kp or "扑" in kp:
            doc += f"**经典手筋**:\n\n"
            doc += f"扑是常用的手筋，通过弃子来减少对手的气或眼位。\n"
            doc += f"关键：扑的时机和位置选择。\n\n"
        else:
            doc += f"**实战应用**:\n\n"
            doc += f"在实战中，{kp} 通常出现在{random.choice(['中盘战斗', '布局阶段', '官子阶段'])}。\n"
            doc += f"需要结合具体棋形灵活运用。\n\n"

    doc += f"""## 二、典型错题分析

本周典型错题（{len(weak_entries)} 道）：

"""
    for i, entry in enumerate(weak_entries[:3], 1):
        doc += f"### 错题{i}: {entry['title']}\n\n"
        doc += f"- **学员**: {entry['player']}\n"
        doc += f"- **问题ID**: {entry['problem_id']}\n"
        doc += f"- **错误原因**: {random.choice(['计算深度不足', '忽略了对手反击', '对杀判断错误', '手筋识别失败'])}\n"
        doc += f"- **正确解法**: {random.choice(['正解在于先手利', '需要补断', '要点在于抢先手', '应该做眼'])}\n\n"

    doc += f"""## 三、针对性练习

请其他学员基于以上知识点，完成以下练习：

1. **基础练习**: {random.randint(5, 10)} 道 {problem_type} {difficulty} 题目
2. **进阶练习**: {random.randint(3, 5)} 道综合题目
3. **实战应用**: 在{random.randint(1, 3)} 盘对局中应用所学知识点

## 四、总结

通过本次微课，希望大家：
1. 理解 {problem_type} {difficulty} 的核心概念
2. 掌握 {', '.join(selected_kps)}
3. 减少同类错题的发生

---
*讲师: qoder | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return doc


def save_teaching_document(doc, week_number, weakness_key):
    """保存教学文档"""
    os.makedirs(INSTRUCTOR_DIR, exist_ok=True)

    filename = f"week{week_number}_{weakness_key.replace('/', '_')}_teaching.md"
    output_file = os.path.join(INSTRUCTOR_DIR, filename)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(doc)

    log(f"📝 教学文档已保存: {output_file}")
    return output_file


def assign_practice_tasks(doc_file, week_number):
    """分配练习任务给其他学员"""
    for player_key in PLAYERS:
        if player_key == "qoder":  # qoder是讲师，不需要练习
            continue

        inbox = os.path.join(QUEUE_DIR, player_key, "inbox")
        os.makedirs(inbox, exist_ok=True)

        task = {
            "id": f"instructor_task_{player_key}_{datetime.now().strftime('%Y%m%d')}",
            "type": "instructor_practice",
            "message": f"qoder技术助教微课已发布，请完成针对性练习",
            "doc_file": doc_file,
            "week": week_number,
            "instructor": "qoder",
            "timestamp": datetime.now().isoformat(),
        }

        task_file = os.path.join(inbox, f"instructor_{player_key}_{datetime.now().strftime('%Y%m%d')}.json")
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2, ensure_ascii=False)

        log(f"📬 已分配练习任务给 {PLAYERS[player_key]['name']}: {task_file}")


def run_instructor(week_number=None):
    """运行技术助教"""
    if week_number is None:
        now = datetime.now()
        week_number = now.isocalendar()[1]

    log(f"\n{'='*60}")
    log(f"👨‍🏫 qoder技术助教 - 第{week_number}周")
    log(f"{'='*60}")

    # 分析错题
    weaknesses = analyze_wrong_books()
    if not weaknesses:
        log("⚠️ 暂无错题数据，跳过本周微课")
        return None

    log(f"\n📊 薄弱点分析 (按错误人数排序):")
    for weakness_key, entries in weaknesses[:5]:
        log(f"  {weakness_key}: {len(entries)} 人出错")

    # 选取最薄弱的知识点
    top_weakness = weaknesses[0]
    weakness_key = top_weakness[0]
    weak_entries = top_weakness[1]

    log(f"\n🎯 本周微课主题: {weakness_key}")
    log(f"   错误人数: {len(weak_entries)}")

    # 生成教学文档
    doc = generate_teaching_document(weakness_key, weak_entries, week_number)
    doc_file = save_teaching_document(doc, week_number, weakness_key)

    # 分配练习任务
    assign_practice_tasks(doc_file, week_number)

    log(f"\n👨‍🏫 第{week_number}周技术助教完成")
    return doc_file


if __name__ == "__main__":
    import sys
    week = int(sys.argv[1]) if len(sys.argv) > 1 else None
    run_instructor(week)
