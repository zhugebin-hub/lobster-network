#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
训练调度器 - 自动生成每日训练计划
根据学员等级、错题本、掌握度动态调整
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path


class TrainingScheduler:
    """训练调度器"""

    def __init__(self, student_name, student_type, domain="go"):
        self.student_name = student_name
        self.student_type = student_type  # 稳健型/加速型/实战型
        self.domain = domain
        self.state_file = os.path.join(
            os.path.dirname(__file__), "state", f"{student_name}_scheduler.json"
        )
        self.state = self._load_state()

    def _load_state(self):
        """加载调度状态"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "student": self.student_name,
            "current_phase": 1,
            "current_week": 1,
            "current_day": 1,
            "total_training_days": 0,
            "last_schedule_date": None,
            "wrong_book": [],
            "mastery": {}  # {problem_id: mastery_level 0-1}
        }

    def _save_state(self):
        """保存状态"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def load_problem_bank(self):
        """加载题库"""
        problems = []
        learning_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        problems_dir = os.path.join(learning_dir, "problems", "problems", self.domain)

        if not os.path.exists(problems_dir):
            return problems

        for phase_dir in os.listdir(problems_dir):
            phase_path = os.path.join(problems_dir, phase_dir)
            if os.path.isdir(phase_path):
                for f in os.listdir(phase_path):
                    if f.endswith('.json'):
                        with open(os.path.join(phase_path, f), 'r') as fp:
                            data = json.load(fp)
                            problems.extend(data.get("problems", []))

        return problems

    def generate_daily_plan(self, date=None):
        """生成每日训练计划"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        problems = self.load_problem_bank()
        if not problems:
            return {"error": "题库为空", "date": date}

        # 筛选当前阶段的题目
        phase_key = f"phase{self.state['current_phase']}"
        phase_problems = [p for p in problems if p.get("phase") == phase_key]

        # 当前周的题目
        week = self.state["current_week"]
        week_problems = [p for p in phase_problems if p.get("week") == week]

        # 错题本优先（占30%）
        wrong_ids = self.state.get("wrong_book", [])
        wrong_problems = [p for p in problems if p.get("problem_id") in wrong_ids]

        # 新题（占70%）
        new_problems = week_problems[:5] if week_problems else phase_problems[:5]

        # 按学员类型调整
        if self.student_type == "稳健型":
            # 稳健型：复习比例高，难度递增慢
            review_ratio = 0.4
            difficulty_bias = "入门"
        elif self.student_type == "加速型":
            # 加速型：新题多，难度递增快
            review_ratio = 0.2
            difficulty_bias = "初级"
        else:  # 实战型
            review_ratio = 0.3
            difficulty_bias = "中级"

        # 组合题目
        plan = {
            "date": date,
            "student": self.student_name,
            "type": self.student_type,
            "phase": self.state["current_phase"],
            "week": week,
            "day": self.state["current_day"],
            "schedule": [
                {
                    "time": "09:00",
                    "module": "死活题",
                    "count": 10,
                    "problems": wrong_problems[:3] + new_problems[:3],
                    "target_accuracy": 0.8 if self.student_type == "稳健型" else 0.7
                },
                {
                    "time": "14:00",
                    "module": "定式/手筋",
                    "count": 15,
                    "problems": new_problems[3:8],
                    "target_accuracy": 0.75
                },
                {
                    "time": "19:00",
                    "module": "实战对局",
                    "count": 1,
                    "opponent": "诸葛虾" if self.student_name != "诸葛虾" else "小陈",
                    "target": "应用今日所学"
                }
            ],
            "review_ratio": review_ratio,
            "generated_at": datetime.now().isoformat()
        }

        # 更新状态
        self.state["last_schedule_date"] = date
        self.state["total_training_days"] += 1
        self.state["current_day"] = (self.state["current_day"] % 7) + 1
        if self.state["current_day"] == 1:
            self.state["current_week"] += 1
            if self.state["current_week"] > 20:
                self.state["current_phase"] += 1
                self.state["current_week"] = 1

        self._save_state()
        return plan

    def update_wrong_book(self, wrong_problem_ids):
        """更新错题本"""
        for pid in wrong_problem_ids:
            if pid not in self.state["wrong_book"]:
                self.state["wrong_book"].append(pid)
        self._save_state()

    def update_mastery(self, problem_id, correct):
        """更新掌握度"""
        current = self.state["mastery"].get(problem_id, 0.5)
        if correct:
            self.state["mastery"][problem_id] = min(1.0, current + 0.1)
        else:
            self.state["mastery"][problem_id] = max(0.0, current - 0.15)
        self._save_state()


def main():
    """演示"""
    for name, type_ in [("小陈", "稳健型"), ("诸葛虾", "加速型"), ("qoder", "实战型")]:
        scheduler = TrainingScheduler(name, type_)
        plan = scheduler.generate_daily_plan()
        print(f"\n📋 {name} ({type_}) 今日计划:")
        print(f"  Phase {plan['phase']} · Week {plan['week']} · Day {plan['day']}")
        for item in plan.get("schedule", []):
            print(f"  [{item['time']}] {item['module']} ({item['count']}题)")
        print(f"  复习比例: {item.get('review_ratio', 0.3)*100:.0f}%")


if __name__ == "__main__":
    main()
