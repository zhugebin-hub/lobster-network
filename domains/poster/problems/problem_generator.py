#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海报设计题库生成器
"""

import json
import os
from datetime import datetime

POSTER_TRAINING_OUTLINE = {
    "phase1": {
        "name": "设计基础",
        "weeks": 4,
        "topics": {
            "week1": ["色彩理论", "排版原则", "字体选择", "视觉层次"],
            "week2": ["构图基础", "黄金比例", "对称与平衡", "留白艺术"],
            "week3": ["图片处理", "滤镜应用", "图层混合", "蒙版技巧"],
            "week4": ["品牌一致性", "Logo设计", "VI系统", "第一阶段考核"]
        },
        "problems_per_topic": 5,
        "total_problems": 80
    },
    "phase2": {
        "name": "进阶设计",
        "weeks": 6,
        "topics": {
            "week5": ["信息图表设计", "数据可视化", "图标设计", "插画基础"],
            "week6": ["动态海报", "GIF制作", "微交互动画", "视频封面"],
            "week7": ["社交媒体海报", "小红书配图", "朋友圈海报", "Banner设计"],
            "week8": ["活动海报", "学术海报", "商业海报", "公益海报"],
            "week9": ["响应式设计", "多尺寸适配", "暗色模式", "无障碍设计"],
            "week10": ["第二阶段综合考核"]
        },
        "problems_per_topic": 4,
        "total_problems": 90
    },
    "phase3": {
        "name": "实战创作",
        "weeks": 6,
        "topics": {
            "week11": ["AI辅助设计", "Midjourney提示词", "DALL-E应用", "Stable Diffusion"],
            "week12": ["设计思维", "用户调研", "A/B测试", "迭代优化"],
            "week13": ["跨平台设计", "Web+Mobile+Print", "品牌延展", "设计系统"],
            "week14": ["高效工作流", "模板化生产", "批量生成", "自动化脚本"],
            "week15": ["设计评审", "同行反馈", "客户沟通", "作品展示"],
            "week16": ["第三阶段综合考核"]
        },
        "problems_per_topic": 4,
        "total_problems": 90
    }
}

PROBLEM_TEMPLATES = {
    "色彩理论": [
        {"type": "选择", "difficulty": "入门", "template": "互补色搭配中，红色的互补色是{绿色}"},
        {"type": "判断", "difficulty": "入门", "template": "暖色调适合表现活力和热情（对/错）"},
    ],
    "排版原则": [
        {"type": "选择", "difficulty": "入门", "template": "海报标题字体大小通常是正文的{2-3}倍"},
        {"type": "填空", "difficulty": "入门", "template": "设计的四大原则是对比、重复、_、亲密性"},
    ],
    "AI辅助设计": [
        {"type": "选择", "difficulty": "初级", "template": "Midjourney中控制图片比例的参数是{--ar}"},
        {"type": "填空", "difficulty": "初级", "template": "DALL-E的提示词应该用_语言描述更准确"},
        {"type": "编程", "difficulty": "中级", "template": "编写Midjourney提示词生成一张赛博朋克风格海报"},
        {"type": "选择", "difficulty": "中级", "template": "Stable Diffusion中ControlNet的主要作用是{控制构图}"},
    ],
    "Midjourney提示词": [
        {"type": "填空", "difficulty": "初级", "template": "Midjourney中--v参数控制_版本"},
        {"type": "选择", "difficulty": "中级", "template": "--style raw参数的作用是{减少风格化}"},
        {"type": "编程", "difficulty": "中级", "template": "用Midjourney生成一张极简主义风格海报的完整提示词"},
    ],
    "DALL-E应用": [
        {"type": "选择", "difficulty": "初级", "template": "DALL-E 3支持的分辨率最高为_{1024x1024}"},
        {"type": "填空", "difficulty": "中级", "template": "DALL-E的inpainting功能用于_局部重绘"},
        {"type": "编程", "difficulty": "中级", "template": "编写DALL-E API调用代码生成一张海报"},
    ],
    "Stable Diffusion": [
        {"type": "选择", "difficulty": "中级", "template": "SD中LoRA的作用是{微调模型}"},
        {"type": "填空", "difficulty": "中级", "template": "SD的CFG Scale参数控制_提示词遵循度"},
        {"type": "编程", "difficulty": "高级", "template": "编写SD WebUI API调用生成系列海报"},
    ],
}


def generate_poster_problems(output_dir):
    """生成海报设计题目"""
    all_problems = []

    for phase, phase_info in POSTER_TRAINING_OUTLINE.items():
        for week_key, topics in phase_info["topics"].items():
            week_num = int(week_key.replace("week", ""))
            for topic in topics:
                templates = PROBLEM_TEMPLATES.get(topic, [
                    {"type": "选择", "difficulty": "入门", "template": f"{topic}基础题"},
                    {"type": "判断", "difficulty": "入门", "template": f"{topic}判断题"},
                    {"type": "填空", "difficulty": "入门", "template": f"{topic}填空题"},
                ])

                for i, template in enumerate(templates):
                    problem = {
                        "problem_id": f"poster-{phase}-w{week_num}-{topic}-{i+1:03d}",
                        "domain": "poster",
                        "phase": phase,
                        "week": week_num,
                        "topic": topic,
                        "type": template["type"],
                        "difficulty": template["difficulty"],
                        "title": f"{topic} #{i+1}",
                        "description": template["template"],
                        "answer": "标准答案",
                        "solution": "详细解析",
                        "knowledge_points": [topic],
                        "created_at": datetime.now().isoformat()
                    }
                    all_problems.append(problem)

    # 保存
    for phase in POSTER_TRAINING_OUTLINE:
        phase_problems = [p for p in all_problems if p["phase"] == phase]
        phase_dir = os.path.join(output_dir, phase)
        os.makedirs(phase_dir, exist_ok=True)

        with open(os.path.join(phase_dir, "problems.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "domain": "poster",
                "phase": phase,
                "total": len(phase_problems),
                "generated_at": datetime.now().isoformat(),
                "problems": phase_problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_poster_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道海报设计题目")

    by_phase = {}
    for p in problems:
        by_phase[p["phase"]] = by_phase.get(p["phase"], 0) + 1
    for phase, count in sorted(by_phase.items()):
        print(f"  {phase}: {count}题")
