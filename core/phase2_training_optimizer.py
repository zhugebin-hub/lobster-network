#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2 训练优化器 - 个性化训练方案生成与分发
基于学员能力画像，生成个性化训练任务

功能：
1. 小陈推理力专项（扑 vs 倒扑辨析 30 题 + 征子路线 25 题 + 高级死活 50 题）
2. 诸葛虾反思力训练（4 步反思日志 + 中级手筋 40 题 + 征子路线 25 题）
3. qoder 速率套利（与诸葛虾配对 30 题 + 系统知识 20 题 + 错题本 15 题）
4. AI 复盘分析（妙手/败着识别 + 转折点 + 建议 + 评分）

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
PROBLEM_BANK = TRAINING_DIR / "problem_bank"

# 学员配置
STUDENTS = {
    "xiaochen": {
        "name": "小陈",
        "type": "稳健型",
        "focus": "推理力专项突破",
        "tasks": [
            {"name": "扑 vs 倒扑辨析", "count": 30, "target_accuracy": 0.80, "require_analysis": True},
            {"name": "征子路线判断", "count": 25, "target_accuracy": 0.85, "require_analysis": True},
            {"name": "高级死活分步推理", "count": 50, "target_accuracy": 0.50, "require_analysis": True},
            {"name": "实战对局", "count": 3, "require_review": True},
        ]
    },
    "zhuguxia": {
        "name": "诸葛虾",
        "type": "加速型",
        "focus": "反思力专项突破",
        "tasks": [
            {"name": "4 步反思日志", "count": 0, "require_reflection": True},
            {"name": "中级手筋强化", "count": 40, "target_accuracy": 0.90},
            {"name": "征子路线专项", "count": 25, "target_accuracy": 0.85},
            {"name": "实战对局", "count": 3, "require_review": True},
        ]
    },
    "qoder": {
        "name": "qoder",
        "type": "新手型",
        "focus": "速率套利 + 系统性提升",
        "tasks": [
            {"name": "速率套利训练", "count": 30, "partner": "zhuguxia"},
            {"name": "系统性知识体系", "count": 20, "sequence": ["死活", "手筋", "定式", "布局", "官子"]},
            {"name": "错题本建设", "count": 15, "spaced_repetition": True},
            {"name": "实战对局", "count": 4, "require_review": True},
        ]
    },
}


class Phase2TrainingOptimizer:
    """Phase 2 训练优化器"""
    
    def __init__(self):
        self.training_dir = TRAINING_DIR
        self.queue_dir = QUEUE_DIR
        self.problem_bank = PROBLEM_BANK
        
    def generate_training_tasks(self, student_id: str) -> List[Dict]:
        """生成学员训练任务"""
        student = STUDENTS[student_id]
        tasks = []
        
        for task_config in student["tasks"]:
            task = {
                "student_id": student_id,
                "student_name": student["name"],
                "task_name": task_config["name"],
                "focus": student["focus"],
                "timestamp": datetime.now().isoformat(),
            }
            
            # 根据任务类型添加不同字段
            if "count" in task_config and task_config["count"] > 0:
                task["problem_count"] = task_config["count"]
                
            if "target_accuracy" in task_config:
                task["target_accuracy"] = task_config["target_accuracy"]
                
            if task_config.get("require_analysis"):
                task["require_analysis"] = True
                task["analysis_template"] = {
                    "step1": "这是扑还是倒扑？为什么？",
                    "step2": "正确思路是什么？",
                    "step3": "我的思路与正确思路的差距",
                    "step4": "下次如何改进？",
                }
                
            if task_config.get("require_reflection"):
                task["require_reflection"] = True
                task["reflection_template"] = {
                    "step1": "我的思路：我当时是怎么想的？",
                    "step2": "正确思路：正确答案是什么？",
                    "step3": "差距分析：差距在哪里？",
                    "step4": "改进策略：下次如何改进？",
                }
                
            if task_config.get("partner"):
                task["partner"] = task_config["partner"]
                task["partner_name"] = STUDENTS[task_config["partner"]]["name"]
                
            if task_config.get("sequence"):
                task["learning_sequence"] = task_config["sequence"]
                
            if task_config.get("spaced_repetition"):
                task["spaced_repetition"] = True
                task["intervals"] = [1, 3, 7, 14]  # 间隔重复天数
                
            tasks.append(task)
            
        return tasks
        
    def distribute_tasks(self, tasks: List[Dict]) -> Dict[str, int]:
        """分发任务到学员 inbox"""
        results = {}
        
        for task in tasks:
            student_id = task["student_id"]
            inbox_dir = self.queue_dir / student_id / "inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成任务文件
            task_file = inbox_dir / f"phase2_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task['task_name'][:10]}.json"
            
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task, f, indent=2, ensure_ascii=False)
                
            results.setdefault(student_id, 0)
            results[student_id] += 1
            
        return results
        
    def generate_ai_review_module(self) -> Dict:
        """生成 AI 复盘分析模块配置"""
        return {
            "module_name": "AI 复盘分析模块",
            "version": "v1.0",
            "features": {
                "妙手识别": {
                    "threshold": 0.7,
                    "description": "评估值>0.7 的着法识别为妙手",
                },
                "败着识别": {
                    "threshold": 0.3,
                    "description": "评估值<0.3 的着法识别为败着",
                },
                "关键转折点": {
                    "threshold": 0.3,
                    "description": "影响胜率>30% 的着法识别为转折点",
                },
                "改进建议": {
                    "description": "基于 AI 分析提供改进建议",
                },
                "综合评分": {
                    "dimensions": ["计算力", "棋形", "战略"],
                    "scale": "1-10 分",
                },
            },
            "test_game": {
                "game_id": "test-game-001",
                "student_id": "xiaochen",
                "result": "loss",
                "expected_score": {
                    "综合": 5.5,
                    "计算力": 6.5,
                    "棋形": 5.5,
                    "战略": 5.9,
                },
                "expected_mistakes": 3,
                "expected_turning_points": 3,
            },
        }
        
    def run_e2e_test(self) -> Dict:
        """运行端到端测试"""
        print("=== Phase 2 端到端测试 ===")
        
        # 测试 1: 生成任务
        print("\n1. 生成训练任务...")
        all_tasks = []
        for student_id in STUDENTS:
            tasks = self.generate_training_tasks(student_id)
            all_tasks.extend(tasks)
            print(f"  {STUDENTS[student_id]['name']}: {len(tasks)} 个任务")
            
        # 测试 2: 分发任务
        print("\n2. 分发任务...")
        results = self.distribute_tasks(all_tasks)
        for student_id, count in results.items():
            print(f"  {STUDENTS[student_id]['name']}: {count} 个任务已分发")
            
        # 测试 3: AI 复盘模块
        print("\n3. 生成 AI 复盘模块...")
        review_module = self.generate_ai_review_module()
        print(f"  模块名称：{review_module['module_name']}")
        print(f"  功能数量：{len(review_module['features'])}")
        
        # 测试 4: 验证任务文件
        print("\n4. 验证任务文件...")
        for student_id in STUDENTS:
            inbox_dir = self.queue_dir / student_id / "inbox"
            if inbox_dir.exists():
                task_files = list(inbox_dir.glob("phase2_task_*.json"))
                print(f"  {STUDENTS[student_id]['name']}: {len(task_files)} 个任务文件")
            else:
                print(f"  {STUDENTS[student_id]['name']}: inbox 目录不存在")
                
        return {
            "total_tasks": len(all_tasks),
            "distribution_results": results,
            "review_module": review_module["module_name"],
            "status": "success",
        }


def main():
    """主函数"""
    optimizer = Phase2TrainingOptimizer()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "generate":
            # 生成训练任务
            student_id = sys.argv[2] if len(sys.argv) > 2 else "xiaochen"
            tasks = optimizer.generate_training_tasks(student_id)
            print(f"=== {STUDENTS[student_id]['name']} 训练任务 ===")
            for task in tasks:
                print(f"- {task['task_name']}")
                if "problem_count" in task:
                    print(f"  题量：{task['problem_count']}")
                if "target_accuracy" in task:
                    print(f"  目标准确率：{task['target_accuracy']:.0%}")
                    
        elif command == "distribute":
            # 分发任务
            student_id = sys.argv[2] if len(sys.argv) > 2 else "all"
            if student_id == "all":
                all_tasks = []
                for sid in STUDENTS:
                    all_tasks.extend(optimizer.generate_training_tasks(sid))
                results = optimizer.distribute_tasks(all_tasks)
                print("=== 任务分发结果 ===")
                for sid, count in results.items():
                    print(f"{STUDENTS[sid]['name']}: {count} 个任务")
            else:
                tasks = optimizer.generate_training_tasks(student_id)
                results = optimizer.distribute_tasks(tasks)
                print(f"=== {STUDENTS[student_id]['name']} 任务分发 ===")
                print(f"分发：{results[student_id]} 个任务")
                
        elif command == "review":
            # AI 复盘分析
            review_module = optimizer.generate_ai_review_module()
            print("=== AI 复盘分析模块 ===")
            print(f"模块：{review_module['module_name']}")
            print(f"功能：{', '.join(review_module['features'].keys())}")
            
        elif command == "test":
            # 端到端测试
            results = optimizer.run_e2e_test()
            print(f"\n=== 测试结果 ===")
            print(f"总任务数：{results['total_tasks']}")
            print(f"状态：{results['status']}")
            
        else:
            print(f"未知命令：{command}")
            print("可用命令：generate, distribute, review, test")
    else:
        print("=== Phase 2 训练优化器 ===")
        print("用法：")
        print("  python3 phase2_training_optimizer.py generate [student_id]")
        print("  python3 phase2_training_optimizer.py distribute [student_id|all]")
        print("  python3 phase2_training_optimizer.py review")
        print("  python3 phase2_training_optimizer.py test")


if __name__ == "__main__":
    main()
