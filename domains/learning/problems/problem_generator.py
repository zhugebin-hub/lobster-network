#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题库生成器 - 按训练大纲自动生成题目
支持：围棋、海报设计、通用逻辑
"""

import json
import os
from pathlib import Path
from datetime import datetime

# === 训练大纲定义 ===
TRAINING_OUTLINE = {
    "go": {
        "phase1": {
            "name": "基础入门",
            "weeks": 4,
            "topics": {
                "week1": ["气的概念", "吃子基础", "禁入点", "打吃"],
                "week2": ["连接与切断", "逃子", "双打吃", "征子"],
                "week3": ["扑与倒扑", "枷吃", "接不归", "倒脱靴"],
                "week4": ["两眼活棋", "基本死活", "劫的概念", "第一阶段考核"]
            },
            "problems_per_topic": 5,
            "total_problems": 80
        },
        "phase2": {
            "name": "定式基础",
            "weeks": 8,
            "topics": {
                "week5": ["小目定式·一间高挂", "小目定式·二间高挂", "星位定式", "三三定式"],
                "week6": ["定式选择原则", "定式后续变化", "定式与布局配合", "定式常见错误"],
                "week7": ["挂角方式", "夹击手法", "拆边原则", "根据地"],
                "week8": ["布局基础·三连星", "布局基础·中国流", "布局基础·小林流", "布局中盘过渡"],
                "week9": ["中盘战斗基础", "攻防要点", "厚薄判断", "形势判断基础"],
                "week10": ["手筋基础·吃子手筋", "手筋基础·连接手筋", "手筋基础·死活手筋", "手筋综合应用"],
                "week11": ["官子基础·大小计算", "官子基础·先手官子", "官子基础·后手官子", "官子综合练习"],
                "week12": ["第二阶段综合考核"]
            },
            "problems_per_topic": 4,
            "total_problems": 120
        },
        "phase3": {
            "name": "进阶实战",
            "weeks": 8,
            "topics": {
                "week13": ["复杂定式变化", "新型定式研究", "定式选择策略", "定式陷阱识别"],
                "week14": ["布局理论深化", "全局配合", "模样作战", "实地与外势"],
                "week15": ["中盘战术·攻击", "中盘战术·防守", "中盘战术·转换", "中盘战术·治孤"],
                "week16": ["死活进阶·大龙生死", "死活进阶·对杀", "死活进阶·双活", "死活综合难题"],
                "week17": ["官子进阶·微妙官子", "官子进阶·逆收", "官子进阶·劫争官子", "官子精确计算"],
                "week18": ["复盘分析方法", "AI复盘应用", "名局研究", "个人棋风分析"],
                "week19": ["比赛策略", "时间管理", "心理调适", "实战模拟"],
                "week20": ["第三阶段综合考核"]
            },
            "problems_per_topic": 4,
            "total_problems": 120
        }
    }
}

# === 题目模板 ===
PROBLEM_TEMPLATES = {
    "go": {
        "吃子基础": [
            {"type": "选择", "difficulty": "入门", "template": "黑棋有{N}口气，白棋有{M}口气，谁先吃谁？"},
            {"type": "判断", "difficulty": "入门", "template": "图中黑棋能否被吃？（能/不能）"},
            {"type": "填空", "difficulty": "入门", "template": "黑棋需要下在_位置才能吃白"},
        ],
        "连接与切断": [
            {"type": "选择", "difficulty": "入门", "template": "黑棋应该{连接/切断}白棋"},
            {"type": "判断", "difficulty": "入门", "template": "白棋的断点能否被利用？"},
        ],
        "扑与倒扑": [
            {"type": "选择", "difficulty": "入门", "template": "黑1应该{扑/倒扑/打吃}"},
            {"type": "填空", "difficulty": "入门", "template": "黑棋扑入后，白棋必须_"},
        ],
        "基本死活": [
            {"type": "判断", "difficulty": "入门", "template": "白棋是{死/活/劫}"},
            {"type": "填空", "difficulty": "入门", "template": "黑棋点入_位置可杀白"},
        ],
        "小目定式·一间高挂": [
            {"type": "选择", "difficulty": "初级", "template": "一间高挂后，黑棋常见应法有{托/扳/长/跳}"},
            {"type": "判断", "difficulty": "初级", "template": "这个定式结果是{两分/黑优/白优}"},
        ],
        "布局基础·三连星": [
            {"type": "选择", "difficulty": "初级", "template": "三连星布局侧重{模样/实地}"},
            {"type": "填空", "difficulty": "初级", "template": "三连星的第一手应下在_"},
        ],
    }
}


def generate_problem(problem_id, domain, phase, week, topic, template, index):
    """根据模板生成一道题"""
    import random
    problem = {
        "problem_id": f"{domain}-{phase}-w{week}-{topic}-{index:03d}",
        "domain": domain,
        "phase": phase,
        "week": week,
        "topic": topic,
        "type": template["type"],
        "difficulty": template["difficulty"],
        "title": f"{topic} #{index}",
        "description": template["template"].format(
            N=random.randint(2, 5),
            M=random.randint(1, 4),
            **{"连接/切断": random.choice(["连接", "切断"]),
               "扑/倒扑/打吃": random.choice(["扑", "倒扑", "打吃"]),
               "死/活/劫": random.choice(["死", "活", "劫"]),
               "模样/实地": random.choice(["模样", "实地"]),
               "两分/黑优/白优": random.choice(["两分", "黑优", "白优"]),
               "托/扳/长/跳": random.choice(["托", "扳", "长", "跳"])
            }
        ),
        "answer": "标准答案",
        "solution": "详细解析",
        "knowledge_points": [topic],
        "created_at": datetime.now().isoformat()
    }
    return problem


def generate_all_problems(output_dir):
    """生成全部题目"""
    all_problems = []
    problem_counter = {}

    for domain, phases in TRAINING_OUTLINE.items():
        for phase, phase_info in phases.items():
            for week_key, topics in phase_info["topics"].items():
                week_num = int(week_key.replace("week", ""))
                for topic in topics:
                    templates = PROBLEM_TEMPLATES.get(domain, {}).get(topic, [])
                    if not templates:
                        # 默认模板
                        templates = [
                            {"type": "选择", "difficulty": "入门", "template": f"{topic}基础题"},
                            {"type": "判断", "difficulty": "入门", "template": f"{topic}判断题"},
                        ]

                    for i, template in enumerate(templates):
                        problem = generate_problem(
                            len(all_problems), domain, phase, week_num, topic, template, i + 1
                        )
                        all_problems.append(problem)

    # 按领域+阶段分组保存
    by_domain_phase = {}
    for p in all_problems:
        key = f"{p['domain']}/{p['phase']}"
        if key not in by_domain_phase:
            by_domain_phase[key] = []
        by_domain_phase[key].append(p)

    for key, problems in by_domain_phase.items():
        dir_path = os.path.join(output_dir, key)
        os.makedirs(dir_path, exist_ok=True)
        file_path = os.path.join(dir_path, "problems.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump({
                "domain": key.split("/")[0],
                "phase": key.split("/")[1],
                "total": len(problems),
                "generated_at": datetime.now().isoformat(),
                "problems": problems
            }, f, ensure_ascii=False, indent=2)

    return all_problems


if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(__file__), "problems")
    problems = generate_all_problems(output_dir)
    print(f"✅ 生成 {len(problems)} 道题目")

    # 统计
    by_phase = {}
    for p in problems:
        by_phase[p["phase"]] = by_phase.get(p["phase"], 0) + 1
    for phase, count in sorted(by_phase.items()):
        print(f"  {phase}: {count}题")
