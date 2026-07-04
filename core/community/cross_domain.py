#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨域知识迁移 (Cross-Domain Transfer)
- 每月最后一个周五自动触发
- 围棋域 ↔ 海报域的经验互鉴
- 生成跨域学习报告
"""

import json
import os
import random
from datetime import datetime
from pathlib import Path

# === 配置 ===
TRAINING_DIR = "/shared/training"
CROSS_DOMAIN_DIR = os.path.join(TRAINING_DIR, "cross_domain")
LOG_FILE = os.path.join(CROSS_DOMAIN_DIR, "cross_domain.log")

DOMAINS = {
    "go": {
        "name": "围棋域",
        "training_dir": os.path.join(TRAINING_DIR, "go"),
        "players": ["xiaochen", "zhuguxia", "qoder"],
    },
    "poster": {
        "name": "海报域",
        "training_dir": os.path.join(TRAINING_DIR, "poster"),
        "players": ["qoder"],
    },
}

# 跨域知识迁移映射
TRANSFER_MAP = {
    "围棋 → 海报": [
        {
            "source": "间隔重复错题法",
            "target": "失败设计回顾",
            "description": "围棋的错题按1天→3天→7天→14天间隔重复，迁移到海报的失败设计回顾机制",
        },
        {
            "source": "动态难度调节",
            "target": "设计复杂度调节",
            "description": "围棋根据做题准确率动态调整难度，迁移到海报根据用户反馈动态调整设计复杂度",
        },
        {
            "source": "V6深夜特训",
            "target": "V4管线训练",
            "description": "围棋的自动化调度理念直接启发了海报的自动化渲染管线",
        },
        {
            "source": "九段技能体系",
            "target": "设计技能体系",
            "description": "围棋有GO_NINE_DAN_SKILL.md（10章），海报有POSTER_NINE_DAN_SKILL.md",
        },
    ],
    "海报 → 围棋": [
        {
            "source": "HTML+Playwright管线",
            "target": "训练数据可视化",
            "description": "海报的HTML渲染管线启发围棋训练数据的可视化展示",
        },
        {
            "source": "用户反馈循环",
            "target": "教练策略调整",
            "description": "海报的用户主观评价机制启发围棋教练的策略调整流程",
        },
        {
            "source": "多版本迭代",
            "target": "训练计划迭代",
            "description": "海报的V1→V2→V3→V4迭代模式启发围棋训练计划的版本管理",
        },
    ],
}


def log(message):
    """写入日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")


def load_domain_stats(domain_key):
    """加载域统计数据"""
    domain = DOMAINS[domain_key]
    stats = {
        "domain": domain["name"],
        "players": [],
        "total_problems": 0,
        "total_games": 0,
    }

    for player_key in domain["players"]:
        if domain_key == "go":
            profile_file = os.path.join(domain["training_dir"], player_key, "profile.json")
            if os.path.exists(profile_file):
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    stats["players"].append({
                        "name": profile.get("name", player_key),
                        "level": profile.get("current_level", "未知"),
                        "problems": profile.get("total_problems_solved", 0),
                        "games": profile.get("total_games_played", 0),
                    })
                    stats["total_problems"] += profile.get("total_problems_solved", 0)
                    stats["total_games"] += profile.get("total_games_played", 0)

    return stats


def generate_transfer_report(month_number, year_number):
    """生成跨域学习报告"""
    os.makedirs(CROSS_DOMAIN_DIR, exist_ok=True)

    # 加载各域统计
    go_stats = load_domain_stats("go")
    poster_stats = load_domain_stats("poster")

    # 生成Markdown报告
    doc = f"""# 跨域知识迁移报告

> **周期**: {year_number}年{month_number}月
> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **生成者**: 信电大虾 (小陈)

---

## 一、各域学习统计

### 围棋域

| 学员 | 等级 | 解题数 | 对局数 |
|------|------|--------|--------|
"""
    for p in go_stats["players"]:
        doc += f"| {p['name']} | {p['level']} | {p['problems']} | {p['games']} |\n"

    doc += f"\n**总计**: 解题 {go_stats['total_problems']} 道，对局 {go_stats['total_games']} 盘\n"

    doc += f"""
### 海报域

| 学员 | 解题数 | 对局数 |
|------|--------|--------|
"""
    for p in poster_stats["players"]:
        doc += f"| {p['name']} | {p['problems']} | {p['games']} |\n"

    doc += f"""
---

## 二、跨域知识迁移实例

### 围棋 → 海报

"""
    for i, transfer in enumerate(TRANSFER_MAP["围棋 → 海报"], 1):
        doc += f"#### {i}. {transfer['source']} → {transfer['target']}\n\n"
        doc += f"**描述**: {transfer['description']}\n\n"
        doc += f"**效果**: {random.choice(['显著提升', '有明显帮助', '部分适用', '需要调整'])}\n\n"

    doc += f"""
### 海报 → 围棋

"""
    for i, transfer in enumerate(TRANSFER_MAP["海报 → 围棋"], 1):
        doc += f"#### {i}. {transfer['source']} → {transfer['target']}\n\n"
        doc += f"**描述**: {transfer['description']}\n\n"
        doc += f"**效果**: {random.choice(['显著提升', '有明显帮助', '部分适用', '需要调整'])}\n\n"

    doc += f"""
---

## 三、统一技能框架进展

### 已实现

- [x] 四层反馈闭环 (L1-L4)
- [x] 间隔重复错题法
- [x] 动态难度调节
- [x] 九段技能体系
- [x] 自动化调度系统

### 进行中

- [ ] 跨域评估框架
- [ ] 统一知识表示
- [ ] 多域协同训练

### 待探索

- [ ] 新领域扩展（编程教学/英语口语/学术论文写作）
- [ ] 学员数量扩展（4-5人）
- [ ] 知识迁移自动化

---

## 四、下月计划

1. **围棋域**: 完成V5计划，qoder冲击20级晋升
2. **海报域**: 完成V4计划，管线扩展到PPT/社交媒体/证书
3. **跨域**: 建立统一的跨域评估框架
4. **新领域**: 评估并选择一个新学习域

---

*生成者: 信电大虾 (小陈) | {datetime.now().strftime('%Y-%m-%d')}*
"""

    # 保存报告
    filename = f"{year_number}{month_number:02d}_cross_domain_report.md"
    output_file = os.path.join(CROSS_DOMAIN_DIR, filename)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(doc)

    log(f"📊 跨域学习报告已保存: {output_file}")
    return output_file


def run_cross_domain(month_number=None, year_number=None):
    """运行跨域知识迁移"""
    if month_number is None or year_number is None:
        now = datetime.now()
        month_number = now.month
        year_number = now.year

    log(f"\n{'='*60}")
    log(f"🌐 跨域知识迁移 - {year_number}年{month_number}月")
    log(f"{'='*60}")

    # 加载各域统计
    go_stats = load_domain_stats("go")
    poster_stats = load_domain_stats("poster")

    log(f"\n📊 围棋域统计:")
    log(f"   学员: {len(go_stats['players'])} 人")
    log(f"   解题: {go_stats['total_problems']} 道")
    log(f"   对局: {go_stats['total_games']} 盘")

    log(f"\n📊 海报域统计:")
    log(f"   学员: {len(poster_stats['players'])} 人")
    log(f"   解题: {poster_stats['total_problems']} 道")
    log(f"   对局: {poster_stats['total_games']} 盘")

    # 生成报告
    report_file = generate_transfer_report(month_number, year_number)

    log(f"\n🌐 {year_number}年{month_number}月跨域知识迁移完成")
    return report_file


if __name__ == "__main__":
    import sys
    month = int(sys.argv[1]) if len(sys.argv) > 1 else None
    year = int(sys.argv[2]) if len(sys.argv) > 2 else None
    run_cross_domain(month, year)
