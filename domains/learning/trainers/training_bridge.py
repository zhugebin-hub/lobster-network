#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实训练对接器 - 将调度器与小陈/诸葛虾的实际训练对接
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


class TrainingBridge:
    """训练对接桥接器"""

    def __init__(self, student_name, domain="go"):
        self.student_name = student_name
        self.domain = domain
        self.workspace = os.path.expanduser("~/.openclaw/workspace")
        self.network_dir = os.path.join(self.workspace, "docs/lobster-network")
        self.state_dir = os.path.join(self.network_dir, "domains/learning/trainers/state")

    def get_today_plan(self):
        """获取今日训练计划"""
        from domains.learning.trainers.scheduler import TrainingScheduler

        # 根据学员名确定类型
        type_map = {
            "小陈": "稳健型",
            "诸葛虾": "加速型",
            "qoder": "实战型"
        }
        student_type = type_map.get(self.student_name, "稳健型")

        scheduler = TrainingScheduler(self.student_name, student_type, self.domain)
        plan = scheduler.generate_daily_plan()
        return plan

    def sync_to_agent(self):
        """将训练计划同步到Agent"""
        plan = self.get_today_plan()

        # 保存到共享目录
        output_dir = os.path.join(self.state_dir, self.student_name)
        os.makedirs(output_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        plan_file = os.path.join(output_dir, f"plan_{today}.json")

        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)

        print(f"✅ 计划已保存到: {plan_file}")
        return plan

    def submit_results(self, results):
        """提交训练结果"""
        results_dir = os.path.join(self.state_dir, self.student_name, "results")
        os.makedirs(results_dir, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        results_file = os.path.join(results_dir, f"results_{today}.json")

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"✅ 结果已提交: {results_file}")

    def update_wrong_book(self, wrong_ids):
        """更新错题本"""
        from domains.learning.trainers.scheduler import TrainingScheduler

        type_map = {"小陈": "稳健型", "诸葛虾": "加速型", "qoder": "实战型"}
        student_type = type_map.get(self.student_name, "稳健型")

        scheduler = TrainingScheduler(self.student_name, student_type, self.domain)
        scheduler.update_wrong_book(wrong_ids)
        print(f"✅ 错题本已更新: {len(wrong_ids)}题")

    def generate_report(self):
        """生成训练报告"""
        results_dir = os.path.join(self.state_dir, self.student_name, "results")

        if not os.path.exists(results_dir):
            return {"error": "暂无训练结果"}

        reports = []
        for f in sorted(os.listdir(results_dir)):
            if f.endswith('.json'):
                with open(os.path.join(results_dir, f), 'r') as fp:
                    reports.append(json.load(fp))

        # 汇总统计
        total_problems = sum(r.get("total_problems", 0) for r in reports)
        total_correct = sum(r.get("correct", 0) for r in reports)
        avg_accuracy = total_correct / max(total_problems, 1) * 100

        return {
            "student": self.student_name,
            "domain": self.domain,
            "total_days": len(reports),
            "total_problems": total_problems,
            "total_correct": total_correct,
            "avg_accuracy": f"{avg_accuracy:.1f}%",
            "reports": reports[-7:]  # 最近7天
        }


def main():
    """演示"""
    for name in ["小陈", "诸葛虾"]:
        print(f"\n📋 {name} 训练对接:")
        bridge = TrainingBridge(name)
        plan = bridge.sync_to_agent()
        print(f"  Phase {plan.get('phase', '?')} · Week {plan.get('week', '?')}")
        for item in plan.get("schedule", []):
            print(f"  [{item['time']}] {item['module']}")


if __name__ == "__main__":
    main()
