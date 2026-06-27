#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI/机器学习题库生成器
"""

import json
import os
from datetime import datetime

AI_ML_OUTLINE = {
    "phase1": {
        "name": "基础篇",
        "chapters": {
            "ch1": {
                "title": "AI概述",
                "topics": ["AI概念", "AI历史", "AI分支", "AI应用", "AI伦理", "AI未来"]
            },
            "ch2": {
                "title": "机器学习基础",
                "topics": ["监督学习", "无监督学习", "强化学习", "特征工程", "模型评估", "模型优化"]
            },
            "ch3": {
                "title": "深度学习基础",
                "topics": ["神经网络", "CNN", "RNN", "Transformer", "生成模型", "训练技巧"]
            }
        },
        "total_problems": 90
    },
    "phase2": {
        "name": "进阶篇",
        "chapters": {
            "ch4": {
                "title": "自然语言处理",
                "topics": ["文本预处理", "词向量", "语言模型", "文本分类", "机器翻译", "问答系统"]
            },
            "ch5": {
                "title": "计算机视觉",
                "topics": ["图像分类", "目标检测", "图像分割", "图像生成", "视频分析", "3D视觉"]
            },
            "ch6": {
                "title": "强化学习",
                "topics": ["MDP", "Q学习", "策略梯度", "Actor-Critic", "多智能体", "应用实战"]
            }
        },
        "total_problems": 90
    },
    "phase3": {
        "name": "高级篇",
        "chapters": {
            "ch7": {
                "title": "AI伦理",
                "topics": ["AI偏见", "AI隐私", "AI安全", "AI治理", "AI法规", "AI责任"]
            },
            "ch8": {
                "title": "AI应用",
                "topics": ["AI医疗", "AI金融", "AI教育", "AI制造", "AI交通", "AI创意"]
            }
        },
        "total_problems": 60
    }
}


def generate_ai_ml_problems(output_dir):
    """生成AI/机器学习题库"""
    all_problems = []

    for phase, phase_info in AI_ML_OUTLINE.items():
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
                        "problem_id": f"ai-{phase}-{ch_key}-{topic}-{i+1:03d}",
                        "domain": "ai_ml",
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
    for phase in AI_ML_OUTLINE:
        phase_problems = [p for p in all_problems if p["phase"] == phase]
        phase_dir = os.path.join(output_dir, phase)
        os.makedirs(phase_dir, exist_ok=True)

        with open(os.path.join(phase_dir, "problems.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "domain": "ai_ml",
                "phase": phase,
                "total": len(phase_problems),
                "generated_at": datetime.now().isoformat(),
                "problems": phase_problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_ai_ml_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道AI/机器学习题目")

    by_phase = {}
    for p in problems:
        by_phase[p["phase"]] = by_phase.get(p["phase"], 0) + 1
    for phase, count in sorted(by_phase.items()):
        print(f"  {phase}: {count}题")
