#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端提交验证器
验证训练任务从分发→学员解题→提交→教练评估的完整链路

功能：
1. 检查任务分发是否成功
2. 检查学员提交是否完整
3. 验证提交内容质量
4. 生成验证报告

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 路径配置
REPO_ROOT = Path(__file__).parent.parent
TRAINING_DIR = REPO_ROOT / ".shared" / "training" / "go"
QUEUE_DIR = REPO_ROOT / "lobster-data" / "messages" / "queue"


class E2ESubmissionValidator:
    """端到端提交验证器"""
    
    def __init__(self):
        self.training_dir = TRAINING_DIR
        self.queue_dir = QUEUE_DIR
        self.results = {}
        
    def check_task_distribution(self, student_id: str) -> Dict:
        """检查任务分发状态"""
        inbox_dir = self.queue_dir / student_id / "inbox"
        results = {
            "student_id": student_id,
            "inbox_exists": inbox_dir.exists(),
            "task_count": 0,
            "tasks": [],
        }
        
        if inbox_dir.exists():
            task_files = list(inbox_dir.glob("*.json"))
            results["task_count"] = len(task_files)
            
            for task_file in task_files:
                try:
                    with open(task_file, 'r') as f:
                        task = json.load(f)
                    results["tasks"].append({
                        "file": task_file.name,
                        "task_name": task.get("task_name", "N/A"),
                        "timestamp": task.get("timestamp", "N/A"),
                    })
                except Exception as e:
                    results["tasks"].append({
                        "file": task_file.name,
                        "error": str(e),
                    })
                    
        return results
        
    def check_student_submission(self, student_id: str) -> Dict:
        """检查学员提交状态"""
        from_dir = self.training_dir / f"from-{student_id}"
        results = {
            "student_id": student_id,
            "submission_dir_exists": from_dir.exists(),
            "submission_count": 0,
            "submissions": [],
        }
        
        if from_dir.exists():
            submission_files = list(from_dir.glob("*.json"))
            results["submission_count"] = len(submission_files)
            
            for sub_file in submission_files:
                try:
                    with open(sub_file, 'r') as f:
                        submission = json.load(f)
                    
                    # 分析提交内容
                    problems = submission.get("problems", [])
                    games = submission.get("games", [])
                    
                    correct = sum(1 for p in problems if p.get("is_correct", False))
                    total = len(problems)
                    accuracy = correct / total if total > 0 else 0
                    
                    results["submissions"].append({
                        "file": sub_file.name,
                        "day": submission.get("day", "N/A"),
                        "problem_count": total,
                        "correct_count": correct,
                        "accuracy": accuracy,
                        "game_count": len(games),
                    })
                except Exception as e:
                    results["submissions"].append({
                        "file": sub_file.name,
                        "error": str(e),
                    })
                    
        return results
        
    def validate_submission_quality(self, submission: Dict) -> Dict:
        """验证提交内容质量"""
        quality = {
            "problem_count_ok": False,
            "accuracy_ok": False,
            "analysis_provided": False,
            "overall_score": 0,
        }
        
        problems = submission.get("problems", [])
        
        # 检查题量
        if len(problems) >= 10:
            quality["problem_count_ok"] = True
            
        # 检查准确率
        correct = sum(1 for p in problems if p.get("is_correct", False))
        total = len(problems)
        accuracy = correct / total if total > 0 else 0
        
        if accuracy >= 0.70:
            quality["accuracy_ok"] = True
            
        # 检查分析内容
        has_analysis = any(p.get("analysis") or p.get("thinking_process") for p in problems)
        if has_analysis:
            quality["analysis_provided"] = True
            
        # 计算综合评分
        score = 0
        if quality["problem_count_ok"]:
            score += 30
        if quality["accuracy_ok"]:
            score += 40
        if quality["analysis_provided"]:
            score += 30
            
        quality["overall_score"] = score
        
        return quality
        
    def run_full_validation(self) -> Dict:
        """运行完整端到端验证"""
        print("=== 端到端提交验证 ===\n")
        
        students = ["xiaochen", "zhuguxia", "qoder"]
        validation_results = {}
        
        for student_id in students:
            print(f"👤 验证 {student_id}...")
            
            # 1. 检查任务分发
            distribution = self.check_task_distribution(student_id)
            print(f"  任务分发：{distribution['task_count']} 个任务")
            
            # 2. 检查学员提交
            submission = self.check_student_submission(student_id)
            print(f"  学员提交：{submission['submission_count']} 个提交")
            
            # 3. 验证提交质量
            quality_scores = []
            for sub in submission.get("submissions", []):
                if "error" not in sub:
                    # 加载完整提交内容
                    sub_file = self.training_dir / f"from-{student_id}" / sub["file"]
                    if sub_file.exists():
                        with open(sub_file, 'r') as f:
                            full_submission = json.load(f)
                        quality = self.validate_submission_quality(full_submission)
                        quality_scores.append(quality["overall_score"])
                        print(f"  提交质量：{quality['overall_score']}/100")
                        
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            validation_results[student_id] = {
                "distribution": distribution,
                "submission": submission,
                "avg_quality_score": avg_quality,
                "status": "pass" if avg_quality >= 60 else "fail",
            }
            
            print()
            
        # 生成验证报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "students": validation_results,
            "overall_status": "pass" if all(r["status"] == "pass" for r in validation_results.values()) else "fail",
        }
        
        # 保存报告
        report_file = self.training_dir / f"e2e_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📊 验证报告已保存：{report_file}")
        return report


def main():
    """主函数"""
    validator = E2ESubmissionValidator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "full":
            # 完整验证
            results = validator.run_full_validation()
            print(f"\n=== 验证结果 ===")
            print(f"整体状态：{results['overall_status']}")
            
        elif command == "check":
            # 检查单个学员
            student_id = sys.argv[2] if len(sys.argv) > 2 else "xiaochen"
            distribution = validator.check_task_distribution(student_id)
            submission = validator.check_student_submission(student_id)
            
            print(f"=== {student_id} 验证 ===")
            print(f"任务分发：{distribution['task_count']} 个")
            print(f"学员提交：{submission['submission_count']} 个")
            
        else:
            print(f"未知命令：{command}")
            print("可用命令：full, check [student_id]")
    else:
        print("=== 端到端提交验证器 ===")
        print("用法：")
        print("  python3 e2e_submission_validator.py full")
        print("  python3 e2e_submission_validator.py check [student_id]")


if __name__ == "__main__":
    main()
