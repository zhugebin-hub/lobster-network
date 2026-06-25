#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级网络通信原理 - 增强版题库生成器
包含知识点讲解、选择题、判断题、填空题、配置题
"""

import json
import os
from datetime import datetime

# === 增强版课程大纲 ===
ENHANCED_COURSE = {
    "ch1": {
        "title": "第一章 绪论",
        "topics": {
            "网络演进4阶段": {
                "knowledge": "传统网络→SDN→云计算→AI云四阶段演进",
                "questions": [
                    {"type": "选择", "difficulty": "入门", "q": "网络技术演进的四个阶段按顺序是？", "a": "A. 传统网络→SDN→云计算→AI云", "options": ["A. 传统网络→SDN→云计算→AI云", "B. SDN→传统网络→AI云→云计算", "C. 云计算→AI云→SDN→传统网络", "D. AI云→云计算→传统网络→SDN"]},
                    {"type": "判断", "difficulty": "入门", "q": "AI云相比云计算具有更高的智能程度", "a": "对"},
                    {"type": "填空", "difficulty": "初级", "q": "SDN的核心思想是控制面与____面分离", "a": "数据"}
                ]
            },
            "架构对比": {
                "knowledge": "传统网络/SDN/云计算/AI云在架构模式、管理方式、可扩展性等方面的差异",
                "questions": [
                    {"type": "选择", "difficulty": "入门", "q": "以下哪个不是SDN的优势？", "a": "C. 控制器单点故障", "options": ["A. 可编程", "B. 创新快", "C. 控制器单点故障", "D. 灵活调度"]},
                    {"type": "判断", "difficulty": "入门", "q": "传统网络的控制面与数据面是分离的", "a": "错"},
                    {"type": "填空", "difficulty": "初级", "q": "云计算的核心思想是资源____化，按需分配", "a": "池化"}
                ]
            }
        }
    },
    "ch2_3": {
        "title": "第二、三章 交换机原理与STP算法",
        "topics": {
            "MAC地址学习": {
                "knowledge": "交换机通过查看数据帧源MAC地址学习，建立MAC地址表",
                "questions": [
                    {"type": "选择", "difficulty": "入门", "q": "交换机学习MAC地址的依据是？", "a": "A. 数据帧的源MAC地址", "options": ["A. 数据帧的源MAC地址", "B. 数据帧的目的MAC地址", "C. ARP请求", "D. ICMP报文"]},
                    {"type": "判断", "difficulty": "入门", "q": "交换机通过查看数据帧的源MAC地址来学习", "a": "对"},
                    {"type": "填空", "difficulty": "初级", "q": "交换机建立的表称为____地址表", "a": "MAC"}
                ]
            },
            "STP根桥选举": {
                "knowledge": "Bridge ID最小的成为根桥，Bridge ID=优先级+MAC地址",
                "questions": [
                    {"type": "选择", "difficulty": "初级", "q": "STP根桥选举的依据是？", "a": "A. Bridge ID最小", "options": ["A. Bridge ID最小", "B. Bridge ID最大", "C. MAC地址最小", "D. 优先级最大"]},
                    {"type": "判断", "difficulty": "初级", "q": "优先级值越大越可能成为根桥", "a": "错"},
                    {"type": "填空", "difficulty": "中级", "q": "STP中端口角色包括根端口、____端口和阻塞端口", "a": "指定"}
                ]
            }
        }
    }
}


def generate_enhanced_problems(output_dir):
    """生成增强版题库"""
    all_problems = []

    for ch_key, ch_info in ENHANCED_COURSE.items():
        for topic_key, topic_info in ch_info["topics"].items():
            for q_info in topic_info["questions"]:
                problem = {
                    "problem_id": f"net-{ch_key}-{topic_key}-{len(all_problems)+1:03d}",
                    "domain": "networking",
                    "chapter": ch_key,
                    "topic": topic_key,
                    "type": q_info["type"],
                    "difficulty": q_info["difficulty"],
                    "title": f"{ch_info['title']} - {topic_key}",
                    "description": q_info["q"],
                    "answer": q_info["a"],
                    "options": q_info.get("options", []),
                    "knowledge": topic_info["knowledge"],
                    "created_at": datetime.now().isoformat()
                }
                all_problems.append(problem)

    # 保存
    for ch_key in ENHANCED_COURSE:
        ch_problems = [p for p in all_problems if p["chapter"] == ch_key]
        ch_dir = os.path.join(output_dir, ch_key)
        os.makedirs(ch_dir, exist_ok=True)

        with open(os.path.join(ch_dir, "problems.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "domain": "networking",
                "chapter": ch_key,
                "total": len(ch_problems),
                "generated_at": datetime.now().isoformat(),
                "problems": ch_problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_enhanced_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道增强版题目")

    by_chapter = {}
    for p in problems:
        by_chapter[p["chapter"]] = by_chapter.get(p["chapter"], 0) + 1
    for ch, count in sorted(by_chapter.items()):
        print(f"  {ch}: {count}题")
