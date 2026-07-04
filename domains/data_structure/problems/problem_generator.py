#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据结构题库生成器
"""

import json
import os
from datetime import datetime

DATA_STRUCTURE_OUTLINE = {
    "phase1": {
        "name": "基础篇",
        "chapters": {
            "ch1": {
                "title": "数据结构概述",
                "topics": ["数据结构概念", "算法复杂度", "时间复杂度", "空间复杂度", "数据结构分类", "算法设计"]
            },
            "ch2": {
                "title": "线性结构",
                "topics": ["数组", "链表", "栈", "队列", "哈希表", "字符串"]
            },
            "ch3": {
                "title": "树结构",
                "topics": ["二叉树", "二叉搜索树", "平衡树", "堆", "哈弗曼树", "B树"]
            }
        },
        "total_problems": 90
    },
    "phase2": {
        "name": "进阶篇",
        "chapters": {
            "ch4": {
                "title": "图结构",
                "topics": ["图的概念", "图的存储", "DFS", "BFS", "最短路径", "最小生成树"]
            },
            "ch5": {
                "title": "排序算法",
                "topics": ["冒泡排序", "选择排序", "插入排序", "快速排序", "归并排序", "堆排序"]
            },
            "ch6": {
                "title": "搜索算法",
                "topics": ["线性搜索", "二分搜索", "深度优先搜索", "广度优先搜索", "A*搜索", "启发式搜索"]
            }
        },
        "total_problems": 90
    },
    "phase3": {
        "name": "高级篇",
        "chapters": {
            "ch7": {
                "title": "高级数据结构",
                "topics": ["跳表", "红黑树", "并查集", "字典树", "后缀数组", "布隆过滤器"]
            },
            "ch8": {
                "title": "算法设计",
                "topics": ["分治算法", "动态规划", "贪心算法", "回溯算法", "分支限界", "随机算法"]
            }
        },
        "total_problems": 60
    }
}


def generate_data_structure_problems(output_dir):
    """生成数据结构题库"""
    all_problems = []

    for phase, phase_info in DATA_STRUCTURE_OUTLINE.items():
        for ch_key, ch_info in phase_info["chapters"].items():
            for topic in ch_info["topics"]:
                templates = [
                    {"type": "选择", "difficulty": "入门", "template": f"{topic}基础选择题"},
                    {"type": "判断", "difficulty": "入门", "template": f"{topic}判断题"},
                    {"type": "填空", "difficulty": "初级", "template": f"{topic}填空题"},
                    {"type": "实战", "difficulty": "中级", "template": f"{topic}实战题"},
                ]

                for i, template in enumerate(templates):
                    problem = {
                        "problem_id": f"ds-{phase}-{ch_key}-{topic}-{i+1:03d}",
                        "domain": "data_structure",
                        "phase": phase,
                        "chapter": ch_key,
                        "topic": topic,
                        "type": template["type"],
                        "difficulty": template["difficulty"],
                        "title": f"{ch_info['title']} - {topic} #{i+1}",
                        "description": template["template"],
                        "answer": "标准答案",
                        "solution": "详细解析",
                        "knowledge_points": [topic],
                        "created_at": datetime.now().isoformat()
                    }
                    all_problems.append(problem)

    # 保存
    for phase in DATA_STRUCTURE_OUTLINE:
        phase_problems = [p for p in all_problems if p["phase"] == phase]
        phase_dir = os.path.join(output_dir, phase)
        os.makedirs(phase_dir, exist_ok=True)

        with open(os.path.join(phase_dir, "problems.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "domain": "data_structure",
                "phase": phase,
                "total": len(phase_problems),
                "generated_at": datetime.now().isoformat(),
                "problems": phase_problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_data_structure_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道数据结构题目")

    by_phase = {}
    for p in problems:
        by_phase[p["phase"]] = by_phase.get(p["phase"], 0) + 1
    for phase, count in sorted(by_phase.items()):
        print(f"  {phase}: {count}题")
