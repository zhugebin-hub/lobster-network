#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络安全题库生成器
"""

import json
import os
from datetime import datetime

CYBERSECURITY_OUTLINE = {
    "phase1": {
        "name": "基础篇",
        "chapters": {
            "ch1": {
                "title": "网络安全概述",
                "topics": ["安全概念", "CIA三元组", "安全模型", "安全策略", "安全标准", "安全法规"]
            },
            "ch2": {
                "title": "常见攻击手法",
                "topics": ["SQL注入", "XSS攻击", "CSRF攻击", "DDoS攻击", "中间人攻击", "社会工程"]
            },
            "ch3": {
                "title": "防御技术基础",
                "topics": ["防火墙", "IDS/IPS", "加密技术", "认证授权", "安全审计", "漏洞扫描"]
            }
        },
        "total_problems": 90
    },
    "phase2": {
        "name": "进阶篇",
        "chapters": {
            "ch4": {
                "title": "渗透测试",
                "topics": ["信息收集", "漏洞扫描", "漏洞利用", "权限提升", "后渗透", "报告编写"]
            },
            "ch5": {
                "title": "安全审计",
                "topics": ["审计基础", "系统审计", "网络审计", "应用审计", "数据库审计", "合规审计"]
            },
            "ch6": {
                "title": "应急响应",
                "topics": ["应急计划", "事件分类", "证据收集", "事件处理", "恢复重建", "总结改进"]
            }
        },
        "total_problems": 90
    },
    "phase3": {
        "name": "高级篇",
        "chapters": {
            "ch7": {
                "title": "高级威胁",
                "topics": ["APT攻击", "零日漏洞", "恶意软件", "高级持久化", "隐蔽通道", "威胁情报"]
            },
            "ch8": {
                "title": "安全架构",
                "topics": ["零信任", "微隔离", "安全设计", "安全开发", "安全运维", "安全治理"]
            }
        },
        "total_problems": 60
    }
}


def generate_cybersecurity_problems(output_dir):
    """生成网络安全题库"""
    all_problems = []

    for phase, phase_info in CYBERSECURITY_OUTLINE.items():
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
                        "problem_id": f"cyber-{phase}-{ch_key}-{topic}-{i+1:03d}",
                        "domain": "cybersecurity",
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
    for phase in CYBERSECURITY_OUTLINE:
        phase_problems = [p for p in all_problems if p["phase"] == phase]
        phase_dir = os.path.join(output_dir, phase)
        os.makedirs(phase_dir, exist_ok=True)

        with open(os.path.join(phase_dir, "problems.json"), 'w', encoding='utf-8') as f:
            json.dump({
                "domain": "cybersecurity",
                "phase": phase,
                "total": len(phase_problems),
                "generated_at": datetime.now().isoformat(),
                "problems": phase_problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_cybersecurity_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道网络安全题目")

    by_phase = {}
    for p in problems:
        by_phase[p["phase"]] = by_phase.get(p["phase"], 0) + 1
    for phase, count in sorted(by_phase.items()):
        print(f"  {phase}: {count}题")
