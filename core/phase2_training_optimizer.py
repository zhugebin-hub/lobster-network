#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络 Phase 2 - 个性化训练优化引擎
功能：
1. 小陈推理力专项（扑vs倒扑辨析+征子路线+高级死活）
2. 诸葛虾反思力训练（4步反思日志+中级手筋强化）
3. qoder速率套利（与诸葛虾配对）
4. AI复盘分析（每局对局后自动生成）
5. Day5训练任务生成与分发

作者：诸葛马 (Hermes)
日期：2026-06-30
版本：v1.0
"""

import json
import os
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# ============================================================
# 配置
# ============================================================

class Config:
    """Phase 2训练优化配置"""
    
    # 共享目录
    SHARED_DIR = "/home/admin/go-training/shared/"
    FROM_HERMES_DIR = f"{SHARED_DIR}from-hermes/"
    RESULTS_DIR = f"{SHARED_DIR}results/"
    PROBLEM_BANK = "/home/admin/lobster-network/domains/go/problem_bank/"
    ACK_DIR = f"{SHARED_DIR}acks/"
    
    # 学员配置
    STUDENTS = {
        "xiaochen": {
            "name": "小陈",
            "type": "稳健型",
            "current_level": "30级",
            "target_level": "25级",
            "strengths": ["基础扎实", "稳定性好", "累计对局量大"],
            "weaknesses": ["推理力35分(Critical)", "高级题准确率35%", "倒扑/扑区分不清"],
            "focus_areas": ["推理力", "理解力", "高级死活"],
            "daily_problems": 50,
            "daily_games": 3,
        },
        "zhuguxia": {
            "name": "诸葛虾",
            "type": "加速型",
            "current_level": "25级",
            "target_level": "20级",
            "strengths": ["入门题98%准确率", "解题速度快", "工具力强"],
            "weaknesses": ["反思力58分", "中级手筋84%", "征子路线判断不足"],
            "focus_areas": ["反思力", "中级手筋", "征子路线"],
            "daily_problems": 60,
            "daily_games": 3,
        },
        "qoder": {
            "name": "qoder",
            "type": "实战型",
            "current_level": "25级",
            "target_level": "20级",
            "strengths": ["高级题准确率65%", "实战对局能力强", "质量高"],
            "weaknesses": ["训练量偏少(685题)", "缺乏系统性", "执行力20分"],
            "focus_areas": ["训练量", "系统性", "速率套利"],
            "daily_problems": 40,
            "daily_games": 4,
        },
    }
    
    # 训练模块定义
    TRAINING_MODULES = {
        "xiaochen": [
            {
                "module_id": "xiaochen_reasoning_1",
                "name": "扑与倒扑辨析专项",
                "focus": "理解力+推理力",
                "problem_count": 30,
                "difficulty": "中级",
                "categories": ["手筋"],
                "target_accuracy": 0.80,
                "method": "对比训练：扑vs倒扑典型棋形对比，建立模式识别",
                "steps": [
                    "识别棋形特征（扑：送吃1子；倒扑：送吃后被提可反提）",
                    "判断后续变化（扑后对方能否逃脱；倒扑后能否反提）",
                    "实战应用（在対局中识别使用机会）",
                ],
            },
            {
                "module_id": "xiaochen_reasoning_2",
                "name": "征子路线判断专项",
                "focus": "推理力",
                "problem_count": 25,
                "difficulty": "中级",
                "categories": ["手筋"],
                "target_accuracy": 0.85,
                "method": "征子路线判断：判断引征→计算路线→验证",
                "steps": [
                    "判断有无引征（对方是否有接应子）",
                    "计算路线长度（能否逃到棋盘边缘）",
                    "验证结论（模拟完整征子过程）",
                ],
            },
            {
                "module_id": "xiaochen_reasoning_3",
                "name": "高级死活分步推理",
                "focus": "推理力",
                "problem_count": 50,
                "difficulty": "高级",
                "categories": ["死活"],
                "target_accuracy": 0.50,
                "method": "分步推理训练：识别棋形→计算变化→验证结论",
                "steps": [
                    "识别基本棋形（直三/曲三/刀五/花六等）",
                    "计算变化分支（对方最强抵抗）",
                    "验证结论（正解/劫活/净死）",
                ],
            },
            {
                "module_id": "xiaochen_game_1",
                "name": "实战对局+推理应用",
                "focus": "执行力",
                "game_count": 3,
                "opponents": ["zhuguxia", "qoder", "zhuguxia"],
                "method": "每局强制应用推理训练：每10手写一次形势判断",
            },
        ],
        "zhuguxia": [
            {
                "module_id": "zhuguxia_reflection_1",
                "name": "4步反思日志训练",
                "focus": "反思力",
                "problem_count": 0,
                "difficulty": "N/A",
                "categories": [],
                "method": "每道错题写4步反思：1.我的思路 2.正确思路 3.差距分析 4.改进策略",
                "reflection_template": {
                    "step1_mindset": "我当时是怎么想的？为什么这么想？",
                    "step2_correct": "正确答案是什么？为什么正确？",
                    "step3_gap": "我的思路和正确答案之间的差距在哪里？",
                    "step4_improve": "下次遇到类似题目，我应该如何改进？",
                },
            },
            {
                "module_id": "zhuguxia_tesuji_1",
                "name": "中级手筋强化",
                "focus": "理解力",
                "problem_count": 40,
                "difficulty": "中级",
                "categories": ["手筋"],
                "target_accuracy": 0.90,
                "method": "针对性训练：当前准确率84%，目标90%",
                "sub_categories": ["双打吃", "倒扑", "接不归", "跨断挖靠"],
            },
            {
                "module_id": "zhuguxia_reasoning_1",
                "name": "征子路线专项突破",
                "focus": "推理力",
                "problem_count": 25,
                "difficulty": "中级",
                "categories": ["手筋"],
                "target_accuracy": 0.85,
                "method": "征子路线判断：判断引征→计算路线→验证",
            },
            {
                "module_id": "zhuguxia_game_1",
                "name": "实战对局+反思应用",
                "focus": "执行力",
                "game_count": 3,
                "opponents": ["xiaochen", "qoder", "xiaochen"],
                "method": "每局后强制写4步反思日志",
            },
        ],
        "qoder": [
            {
                "module_id": "qoder_rate_1",
                "name": "速率套利训练（与诸葛虾配对）",
                "focus": "执行力",
                "problem_count": 30,
                "difficulty": "混合",
                "categories": ["死活", "手筋", "官子", "布局"],
                "target_accuracy": 0.80,
                "method": "与zhuguxia配对：zhuguxia生成题，qoder解题，利用速率差异增加训练密度",
                "pairing": {
                    "generator": "zhuguxia",
                    "solver": "qoder",
                    "mechanism": "zhuguxia从题库选题→推送到qoder inbox→qoder解题→提交结果",
                },
            },
            {
                "module_id": "qoder_systematic_1",
                "name": "系统性知识体系构建",
                "focus": "理解力",
                "problem_count": 20,
                "difficulty": "中级",
                "categories": ["死活", "手筋", "定式", "布局", "官子"],
                "target_accuracy": 0.85,
                "method": "按围棋知识体系系统训练：死活→手筋→定式→布局→官子",
                "sequence": ["死活", "手筋", "定式", "布局", "官子"],
            },
            {
                "module_id": "qoder_wrongbook_1",
                "name": "错题本建设",
                "focus": "反思力",
                "problem_count": 15,
                "difficulty": "高级",
                "categories": ["死活", "手筋"],
                "target_accuracy": 0.70,
                "method": "建立个人错题本，定期复习，间隔重复（1天→3天→7天→14天）",
            },
            {
                "module_id": "qoder_game_1",
                "name": "实战对局+速率套利",
                "focus": "执行力",
                "game_count": 4,
                "opponents": ["zhuguxia", "xiaochen", "zhuguxia", "xiaochen"],
                "method": "增加对局密度，每局后写简短复盘",
            },
        ],
    }


# ============================================================
# 训练任务生成器
# ============================================================

class TrainingTaskGenerator:
    """训练任务生成器"""
    
    def __init__(self):
        self.config = Config()
    
    def generate_day5_tasks(self) -> Dict[str, List[Dict]]:
        """生成Day5训练任务（个性化）"""
        all_tasks = {}
        
        for student_id, student_info in self.config.STUDENTS.items():
            modules = self.config.TRAINING_MODULES[student_id]
            tasks = []
            
            for module in modules:
                task = self._create_task(student_id, module)
                tasks.append(task)
            
            all_tasks[student_id] = tasks
        
        return all_tasks
    
    def _create_task(self, student_id: str, module: Dict) -> Dict:
        """创建单个训练任务"""
        task_id = f"day5-{student_id}-{module['module_id']}-{int(datetime.now().timestamp())}"
        
        task = {
            "id": task_id,
            "type": "training_task",
            "from": "hermes",
            "to": student_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "day": 5,
            "student_id": student_id,
            "module": module,
            "task": {
                "title": module["name"],
                "phase": "Phase 2 - 个性化训练优化",
                "week": 1,
                "day": 1,
                "category": module.get("categories", ["综合"])[0] if module.get("categories") else "综合",
                "difficulty": module.get("difficulty", "混合"),
                "problem_count": module.get("problem_count", 0),
                "game_count": module.get("game_count", 0),
                "target_accuracy": module.get("target_accuracy", 0.80),
                "method": module["method"],
                "focus": module["focus"],
            },
            "special_instructions": self._get_special_instructions(student_id, module),
            "submission_requirements": {
                "require_ack": True,
                "require_reflection": student_id == "zhuguxia",
                "require_wrongbook": student_id == "qoder",
                "require_step_by_step": student_id == "xiaochen",
            },
        }
        
        return task
    
    def _get_special_instructions(self, student_id: str, module: Dict) -> str:
        """获取特殊指令"""
        if student_id == "xiaochen":
            if "扑与倒扑" in module.get("name", ""):
                return ("⚠️ 小陈注意：本题训练重点是区分扑和倒扑。\n"
                       "扑 = 送吃1子，对方提后你不能再提\n"
                       "倒扑 = 送吃1子，对方提后你可以立即反提\n"
                       "请对每道题写出：这是扑还是倒扑？为什么？")
            elif "征子" in module.get("name", ""):
                return ("⚠️ 小陈注意：征子路线判断三步法：\n"
                       "1. 看对方有没有引征子（接应子）\n"
                       "2. 计算征子路线能走多远\n"
                       "3. 模拟完整征子过程验证\n"
                       "请对每道题写出三步分析过程。")
            elif "高级死活" in module.get("name", ""):
                return ("⚠️ 小陈注意：高级死活分步推理法：\n"
                       "1. 先识别基本棋形（直三/曲三/刀五/花六等）\n"
                       "2. 再计算变化分支（考虑对方最强抵抗）\n"
                       "3. 最后验证结论（正解/劫活/净死）\n"
                       "请对每道题写出分步推理过程。")
        
        elif student_id == "zhuguxia":
            if "反思" in module.get("name", ""):
                template = module.get("reflection_template", {})
                return (f"⚠️ 诸葛虾注意：每道错题必须写4步反思日志：\n"
                       f"1️⃣ 我的思路：{template.get('step1_mindset', '')}\n"
                       f"2️⃣ 正确思路：{template.get('step2_correct', '')}\n"
                       f"3️⃣ 差距分析：{template.get('step3_gap', '')}\n"
                       f"4️⃣ 改进策略：{template.get('step4_improve', '')}")
        
        elif student_id == "qoder":
            if "速率套利" in module.get("name", ""):
                return ("⚠️ qoder注意：速率套利模式：\n"
                       "诸葛虾将生成题目推送到你的inbox\n"
                       "你需要快速解题并提交结果\n"
                       "目标：利用速率差异增加训练密度\n"
                       "请保持高准确率（目标80%+）")
        
        return ""


# ============================================================
# AI复盘分析模块
# ============================================================

class AIReviewAnalyzer:
    """AI复盘分析器"""
    
    def __init__(self):
        self.config = Config()
    
    def analyze_game(self, game_data: Dict) -> Dict:
        """分析对局数据，生成复盘报告"""
        game_id = game_data.get("game_id", "unknown")
        student_id = game_data.get("student_id", "unknown")
        moves = game_data.get("moves", [])
        result = game_data.get("result", "unknown")
        
        # 生成复盘报告
        review = {
            "review_id": f"review-{game_id}-{int(datetime.now().timestamp())}",
            "game_id": game_id,
            "student_id": student_id,
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "game_result": result,
            "total_moves": len(moves),
            "analysis": {
                "good_moves": self._identify_good_moves(moves),
                "bad_moves": self._identify_bad_moves(moves),
                "critical_moments": self._identify_critical_moments(moves),
                "suggestions": self._generate_suggestions(moves, result),
            },
            "learning_points": self._extract_learning_points(moves, result),
            "rating": self._calculate_rating(moves, result),
        }
        
        return review
    
    def _identify_good_moves(self, moves: List[Dict]) -> List[Dict]:
        """识别妙手"""
        good_moves = []
        for move in moves:
            if move.get("evaluation", 0) > 0.7:
                good_moves.append({
                    "move_number": move.get("move_number"),
                    "reason": move.get("reason", "好棋"),
                    "evaluation": move.get("evaluation"),
                })
        return good_moves[:5]  # 最多5个妙手
    
    def _identify_bad_moves(self, moves: List[Dict]) -> List[Dict]:
        """识别败着"""
        bad_moves = []
        for move in moves:
            if move.get("evaluation", 0.5) < 0.3:
                bad_moves.append({
                    "move_number": move.get("move_number"),
                    "reason": move.get("reason", "败着"),
                    "evaluation": move.get("evaluation"),
                    "better_alternative": move.get("better_alternative", "建议重新计算"),
                })
        return bad_moves[:5]  # 最多5个败着
    
    def _identify_critical_moments(self, moves: List[Dict]) -> List[Dict]:
        """识别关键转折点"""
        critical = []
        for i, move in enumerate(moves):
            if abs(move.get("evaluation", 0.5) - 0.5) > 0.3:
                critical.append({
                    "move_number": move.get("move_number"),
                    "impact": "正面" if move.get("evaluation", 0) > 0.5 else "负面",
                    "description": move.get("description", "关键一手"),
                })
        return critical[:3]  # 最多3个转折点
    
    def _generate_suggestions(self, moves: List[Dict], result: str) -> List[str]:
        """生成改进建议"""
        suggestions = []
        
        # 基于败着生成建议
        bad_moves = self._identify_bad_moves(moves)
        if bad_moves:
            suggestions.append(f"注意避免{len(bad_moves)}个败着，加强计算深度")
        
        # 基于胜率生成建议
        if result in ["loss", "负"]:
            suggestions.append("本局失利，建议重点复盘关键转折点")
        else:
            suggestions.append("本局获胜，继续保持优势")
        
        # 基于着数生成建议
        total_moves = len(moves)
        if total_moves < 50:
            suggestions.append("对局较短，建议增加中盘战斗训练")
        elif total_moves > 200:
            suggestions.append("对局较长，建议加强官子精度训练")
        
        return suggestions
    
    def _extract_learning_points(self, moves: List[Dict], result: str) -> List[str]:
        """提取学习要点"""
        points = []
        
        # 根据对局结果提取
        if result in ["loss", "负"]:
            points.extend([
                "失败是成功之母，重点分析败因",
                "记录本次失利的情境和决策过程",
                "找出可以改进的关键点",
            ])
        else:
            points.extend([
                "总结本次获胜的关键因素",
                "巩固成功的经验和策略",
                "思考如何在更高水平对局中应用",
            ])
        
        return points
    
    def _calculate_rating(self, moves: List[Dict], result: str) -> Dict:
        """计算对局评分"""
        if not moves:
            return {"overall": 0, "reading": 0, "shape": 0, "strategy": 0}
        
        avg_evaluation = sum(m.get("evaluation", 0.5) for m in moves) / len(moves)
        
        return {
            "overall": round(avg_evaluation * 10, 1),
            "reading": round(min(10, avg_evaluation * 10 + 1), 1),
            "shape": round(min(10, avg_evaluation * 9 + 0.5), 1),
            "strategy": round(min(10, avg_evaluation * 8 + 1.5), 1),
        }


# ============================================================
# 任务分发器
# ============================================================

class TaskDispatcher:
    """训练任务分发器"""
    
    def __init__(self):
        self.config = Config()
        self.generator = TrainingTaskGenerator()
        self.analyzer = AIReviewAnalyzer()
        os.makedirs(self.config.FROM_HERMES_DIR, exist_ok=True)
    
    def distribute_day5_tasks(self) -> Dict:
        """分发Day5训练任务"""
        all_tasks = self.generator.generate_day5_tasks()
        results = {"distributed": 0, "failed": 0, "tasks": {}}
        
        for student_id, tasks in all_tasks.items():
            student_tasks = []
            
            for task in tasks:
                try:
                    # 写入from-hermes目录
                    task_file = os.path.join(
                        self.config.FROM_HERMES_DIR,
                        f"day5-task-{student_id}-{task['id']}.json"
                    )
                    
                    with open(task_file, "w") as f:
                        json.dump(task, f, ensure_ascii=False, indent=2)
                    
                    student_tasks.append(task["id"])
                    results["distributed"] += 1
                    
                    print(f"📤 分发任务: student={student_id}, task={task['module']['name']}")
                    
                except Exception as e:
                    results["failed"] += 1
                    print(f"❌ 分发失败: student={student_id}, task={task.get('id')}: {e}")
            
            results["tasks"][student_id] = student_tasks
        
        return results
    
    def create_training_plan_summary(self) -> str:
        """创建训练计划总结（Markdown）"""
        md = []
        md.append("# 🏯 Day 5 个性化训练计划")
        md.append(f"\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("> Phase 2 - 个性化训练优化")
        md.append("")
        
        for student_id, student_info in self.config.STUDENTS.items():
            modules = self.config.TRAINING_MODULES[student_id]
            
            md.append(f"## 📚 {student_info['name']} ({student_id})")
            md.append("")
            md.append(f"**当前等级**：{student_info['current_level']} → **目标等级**：{student_info['target_level']}")
            md.append("")
            md.append(f"**优势**：{', '.join(student_info['strengths'])}")
            md.append("")
            md.append(f"**待改进**：{', '.join(student_info['weaknesses'])}")
            md.append("")
            md.append(f"**每日目标**：{student_info['daily_problems']}题 + {student_info['daily_games']}局")
            md.append("")
            
            md.append("### 训练模块")
            md.append("")
            md.append("| 模块 | 重点 | 题量 | 目标准确率 |")
            md.append("|------|------|------|------------|")
            
            for module in modules:
                ta = module.get('target_accuracy', 'N/A')
                if isinstance(ta, str):
                    ta_str = ta
                else:
                    ta_str = f"{ta:.0%}"
                md.append(f"| {module['name']} | {module['focus']} | "
                         f"{module.get('problem_count', module.get('game_count', 0))} | "
                         f"{ta_str} |")
            
            md.append("")
            
            # 特殊指令
            for module in modules:
                if module.get("method"):
                    md.append(f"**{module['name']}**：{module['method']}")
                    if "steps" in module:
                        for i, step in enumerate(module["steps"], 1):
                            md.append(f"  {i}. {step}")
                    md.append("")
        
        md.append("---")
        md.append(f"*训练计划由诸葛马 (Hermes) Phase 2 v1.0 自动生成*")
        
        return "\n".join(md)


# ============================================================
# 命令行接口
# ============================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Phase 2 个性化训练优化")
    parser.add_argument("action", choices=["generate", "distribute", "review", "summary"],
                       help="操作: generate(生成任务) | distribute(分发任务) | review(AI复盘) | summary(训练总结)")
    parser.add_argument("--student", type=str, help="学员ID")
    parser.add_argument("--game-file", type=str, help="对局文件路径（用于review）")
    
    args = parser.parse_args()
    dispatcher = TaskDispatcher()
    
    if args.action == "generate":
        tasks = dispatcher.generator.generate_day5_tasks()
        print(json.dumps(tasks, ensure_ascii=False, indent=2))
    
    elif args.action == "distribute":
        results = dispatcher.distribute_day5_tasks()
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif args.action == "review":
        if args.game_file and os.path.exists(args.game_file):
            with open(args.game_file) as f:
                game_data = json.load(f)
            review = dispatcher.analyzer.analyze_game(game_data)
            print(json.dumps(review, ensure_ascii=False, indent=2))
        else:
            print("❌ 请提供有效的对局文件路径")
    
    elif args.action == "summary":
        summary = dispatcher.create_training_plan_summary()
        print(summary)
        
        # 保存总结文件
        summary_file = os.path.join(
            dispatcher.config.FROM_HERMES_DIR,
            f"day5-training-summary-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        with open(summary_file, "w") as f:
            f.write(summary)
        print(f"\n📝 训练总结已保存: {summary_file}")


if __name__ == "__main__":
    main()
