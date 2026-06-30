#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
围棋教练调度器 V4 - Day 3-16 训练计划补充
填补 Day 3-16 空白，与 Day 17+ 计划衔接

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

# === Day 3-16 训练计划 ===
# 基于 V3 训练任务 + 学员能力画像设计
# 小陈 (稳健型): 侧重死活补强、推理力训练
# 诸葛虾 (加速型): 侧重中级进阶、反思力训练
# qoder (新手): 侧重基础积累、速率套利

DAILY_PLAN_DAY3_16 = {
    # Day 3: 扑与倒扑辨析（小陈推理力专项）
    3: {"topic": "扑与倒扑辨析", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "手筋", "difficulty": "初级", "count": 5}},
    
    # Day 4: 对抗赛准备 + 专项突破
    4: {"topic": "对抗赛准备 + 专项突破", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "match_day": True},
    
    # Day 5: 征子路线判断（推理力强化）
    5: {"topic": "征子路线判断", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "手筋", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "手筋", "difficulty": "中级", "count": 5}},
    
    # Day 6: 错题复习日（V4 新增）
    6: {"topic": "错题复习 + 手筋巩固", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 7: 第 1 周考核（综合）
    7: {"topic": "第 1 周考核", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "手筋", "difficulty": "中级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 8: 休息 + 阶段总结
    8: {"topic": "休息 + 阶段总结", "tasks": [], "review_wrong_book": False},
    
    # Day 9: 第 2 周开始 - 死活专项
    9: {"topic": "初级死活强化", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 8},
        {"category": "死活", "difficulty": "中级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False, "xiaochen_extra": {"category": "死活", "difficulty": "初级", "count": 5}},
    
    # Day 10: 中级死活进阶
    10: {"topic": "中级死活进阶", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "死活", "difficulty": "中级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "zhuguxia_extra": {"category": "死活", "difficulty": "中级", "count": 5}},
    
    # Day 11: 错题复习日
    11: {"topic": "错题复习 + 死活实战", "tasks": [
        {"category": "死活", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": True, "review_count_steady": 5, "review_count_fast": 4},
    
    # Day 12: 手筋与死活综合
    12: {"topic": "手筋与死活综合", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "死活", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
        {"category": "手筋", "difficulty": "中级", "count_steady": 2, "count_fast": 3},
    ], "review_wrong_book": False},
    
 # Day 13: 定式入门
    13: {"topic": "定式入门", "tasks": [
        {"category": "定式", "difficulty": "入门", "count_steady": 5, "count_fast": 8},
        {"category": "定式", "difficulty": "初级", "count_steady": 3, "count_fast": 5},
    ], "review_wrong_book": False},
    
    # Day 14: 定式进阶
    14: {"topic": "定式进阶", "tasks": [
        {"category": "定式", "difficulty": "入门", "count_steady": 4, "count_fast": 6},
        {"category": "定式", "difficulty": "初级", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False},
    
    # Day 15: 第 2 周考核（综合）
    15: {"topic": "第 2 周考核", "tasks": [
        {"category": "手筋", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "死活", "difficulty": "初级", "count_steady": 5, "count_fast": 7},
        {"category": "定式", "difficulty": "入门", "count_steady": 4, "count_fast": 6},
    ], "review_wrong_book": False, "exam_day": True},
    
    # Day 16: 休息 + 阶段总结
    16: {"topic": "休息 + 阶段总结", "tasks": [], "review_wrong_book": False},
}

# === 训练量配置 ===
TRAINING_CONFIG = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "base_problems": 100,  # 基础题量
        "base_games": 10,      # 基础对局数
        "focus": "死活补强 + 推理力训练",
        "extra_days": [3, 5, 9, 11],  # 额外训练日
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "base_problems": 120,
        "base_games": 12,
        "focus": "中级进阶 + 反思力训练",
        "extra_days": [10, 12, 14],
    },
    "qoder": {
        "name": "qoder",
        "type": "新手型",
        "base_problems": 80,
        "base_games": 8,
        "focus": "基础积累 + 速率套利",
        "extra_days": [],
    },
}

# === 评估标准 ===
EVALUATION_CRITERIA = {
    "rating_A": {"accuracy_min": 0.80, "description": "优秀"},
    "rating_B": {"accuracy_min": 0.70, "description": "良好"},
    "rating_C": {"accuracy_min": 0.60, "description": "合格"},
    "rating_D": {"accuracy_min": 0.00, "description": "不合格"},
}

# === 动态难度调整规则 ===
DYNAMIC_DIFFICULTY = {
    "upgrade_threshold": 0.90,  # 连续 2 天准确率>90% 升档
    "downgrade_threshold": 0.70,  # 连续 2 天准确率<70% 降档
    "review_wrong_book_interval": 3,  # 每 3 天错题复习
    "exam_interval": 7,  # 每 7 天考核
}

if __name__ == "__main__":
    print("=== Day 3-16 训练计划 ===")
    for day in sorted(DAILY_PLAN_DAY3_16.keys()):
        plan = DAILY_PLAN_DAY3_16[day]
        print(f"Day {day}: {plan['topic']}")
        if plan['tasks']:
            for task in plan['tasks']:
                print(f"  - {task['category']} ({task['difficulty']}): {task['count_steady']}题 (小陈) / {task['count_fast']}题 (诸葛虾)")
        if plan.get('review_wrong_book'):
            print(f"  - 错题复习: {plan.get('review_count_steady', 5)}题 (小陈) / {plan.get('review_count_fast', 4)}题 (诸葛虾)")
        if plan.get('xiaochen_extra'):
            extra = plan['xiaochen_extra']
            print(f"  - 小陈额外: {extra['category']} ({extra['difficulty']}): {extra['count']}题")
        if plan.get('zhuguxia_extra'):
            extra = plan['zhuguxia_extra']
            print(f"  - 诸葛虾额外: {extra['category']} ({extra['difficulty']}): {extra['count']}题")
        if plan.get('exam_day'):
            print(f"  - ⭐ 考核日")
        if plan.get('match_day'):
            print(f"  - ⚔️ 对抗赛")
        print()
