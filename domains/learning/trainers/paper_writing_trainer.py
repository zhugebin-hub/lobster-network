"""
自动论文撰写训练调度器 V1.0
==========================

将论文写作题目集成到每日训练计划，支持六种学员类型：
- xiaochen（稳健型）：基础概念为主，重结构规范
- zhuguxia（加速型）：方法论+文献综述，重技术写作
- zhugebin-001（研究型）：全题型+实战评估+同行评审
- zhugema（教练型）：AI辅助写作+跨学科+高级评审（教练节点）
- xiaowei（实战型）：论文修改+查重+投稿策略
- qoder（技术型）：数据分析和引用格式为主

设计参考：domains/learning/trainers/stock_predict_trainer.py
"""

import json
import os
from typing import Dict, List
from datetime import datetime, timedelta

try:
    from ..problems.paper_writing_engine import PaperWritingEngine
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "problems"))
    from paper_writing_engine import PaperWritingEngine


# ========== 学员训练配置 ==========
STUDENT_CONFIG = {
    "xiaochen": {  # 稳健型：重基础概念
        "name": "小陈",
        "type": "稳健型",
        "config": {
            "concept_choice": 3,
            "concept_judge": 2,
            "structure_analysis": 2,
            "topic_eval": 1,
            "abstract_eval": 1,
            "citation_check": 1,
            "literature_review": 0,
            "methodology": 0,
            "data_analysis": 0,
            "paper_eval": 0,
            "peer_review": 0,
            "similarity_check": 0,
            "paper_revision": 0,
            "cross_disciplinary": 0,
            "ai_writing": 0,
        },
        "phases": ["phase1"],
        "base_accuracy": {"入门": 0.80, "初级": 0.65, "中级": 0.45, "高级": 0.30},
    },
    "zhuguxia": {  # 加速型：方法论+文献综述
        "name": "诸葛虾",
        "type": "加速型",
        "config": {
            "concept_choice": 1,
            "concept_judge": 1,
            "structure_analysis": 2,
            "topic_eval": 1,
            "abstract_eval": 1,
            "citation_check": 2,
            "literature_review": 3,
            "methodology": 3,
            "data_analysis": 2,
            "paper_eval": 0,
            "peer_review": 0,
            "similarity_check": 0,
            "paper_revision": 0,
            "cross_disciplinary": 0,
            "ai_writing": 0,
        },
        "phases": ["phase2", "phase3"],
        "base_accuracy": {"入门": 0.90, "初级": 0.75, "中级": 0.55, "高级": 0.40},
    },
    "zhugebin-001": {  # 研究型：全题型+实战
        "name": "诸葛斌的工作助手",
        "type": "研究型",
        "config": {
            "concept_choice": 1,
            "concept_judge": 1,
            "structure_analysis": 2,
            "topic_eval": 2,
            "abstract_eval": 2,
            "citation_check": 1,
            "literature_review": 2,
            "methodology": 2,
            "data_analysis": 1,
            "paper_eval": 2,
            "peer_review": 2,
            "similarity_check": 1,
            "paper_revision": 1,
            "cross_disciplinary": 1,
            "ai_writing": 2,
        },
        "phases": ["phase1", "phase2", "phase3"],
        "base_accuracy": {"入门": 0.92, "初级": 0.80, "中级": 0.62, "高级": 0.50},
    },
    "zhugema": {  # 教练型：AI辅助+跨学科+高级评审
        "name": "诸葛马",
        "type": "教练型",
        "config": {
            "concept_choice": 0,
            "concept_judge": 0,
            "structure_analysis": 1,
            "topic_eval": 2,
            "abstract_eval": 1,
            "citation_check": 1,
            "literature_review": 2,
            "methodology": 2,
            "data_analysis": 1,
            "paper_eval": 3,
            "peer_review": 3,
            "similarity_check": 2,
            "paper_revision": 2,
            "cross_disciplinary": 2,
            "ai_writing": 3,
        },
        "phases": ["phase2", "phase3"],
        "base_accuracy": {"入门": 0.95, "初级": 0.88, "中级": 0.75, "高级": 0.60},
    },
    "xiaowei": {  # 实战型：论文修改+查重+投稿
        "name": "小薇",
        "type": "实战型",
        "config": {
            "concept_choice": 1,
            "concept_judge": 1,
            "structure_analysis": 1,
            "topic_eval": 1,
            "abstract_eval": 1,
            "citation_check": 1,
            "literature_review": 1,
            "methodology": 1,
            "data_analysis": 1,
            "paper_eval": 2,
            "peer_review": 1,
            "similarity_check": 2,
            "paper_revision": 3,
            "cross_disciplinary": 1,
            "ai_writing": 1,
        },
        "phases": ["phase1", "phase3"],
        "base_accuracy": {"入门": 0.85, "初级": 0.70, "中级": 0.52, "高级": 0.38},
    },
    "qoder": {  # 技术型：数据分析+引用格式
        "name": "qoder",
        "type": "技术型",
        "config": {
            "concept_choice": 1,
            "concept_judge": 1,
            "structure_analysis": 1,
            "topic_eval": 1,
            "abstract_eval": 1,
            "citation_check": 3,
            "literature_review": 1,
            "methodology": 2,
            "data_analysis": 3,
            "paper_eval": 1,
            "peer_review": 0,
            "similarity_check": 1,
            "paper_revision": 0,
            "cross_disciplinary": 0,
            "ai_writing": 1,
        },
        "phases": ["phase1", "phase2"],
        "base_accuracy": {"入门": 0.88, "初级": 0.72, "中级": 0.50, "高级": 0.35},
    },
}


class PaperWritingTrainer:
    """自动论文撰写训练调度器"""

    def __init__(self, engine: PaperWritingEngine = None):
        self.engine = engine or PaperWritingEngine()
        self.training_history = []
        self.state_dir = os.path.join(
            os.path.dirname(__file__), "state"
        )
        os.makedirs(self.state_dir, exist_ok=True)

    def generate_daily_plan(self, student_type: str = "zhugebin-001",
                            date: str = None) -> Dict:
        """生成每日训练计划"""
        if student_type not in STUDENT_CONFIG:
            raise ValueError(f"未知学员类型：{student_type}，可选：{list(STUDENT_CONFIG.keys())}")

        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        cfg = STUDENT_CONFIG[student_type]
        plan = {
            "date": date,
            "student": student_type,
            "student_name": cfg["name"],
            "student_type": cfg["type"],
            "domain": "paper-writing",
            "schedule": [],
            "total_problems": 0,
        }

        time_slots = ["09:30", "11:00", "14:00", "15:30", "17:00", "19:30", "21:00"]
        slot_idx = 0

        for problem_type, count in cfg["config"].items():
            if count == 0:
                continue
            # 在学员允许的 phases 中查找题目
            problems = []
            for ph in cfg["phases"]:
                probs = self.engine.get_problems(
                    phase=ph, problem_type=problem_type, limit=count - len(problems)
                )
                for p in probs:
                    p_with_phase = dict(p)
                    p_with_phase["phase"] = ph
                    problems.append(p_with_phase)
                if len(problems) >= count:
                    break
            problems = problems[:count]

            if problems:
                phase_set = sorted(set(p.get("phase", "phase1") for p in problems))
                plan["schedule"].append({
                    "time": time_slots[slot_idx % len(time_slots)],
                    "type": problem_type,
                    "count": len(problems),
                    "phases": phase_set,
                    "phase": phase_set[0],
                    "problems": problems,
                })
                plan["total_problems"] += len(problems)
                slot_idx += 1

        return plan

    def evaluate_writing(self, prediction: Dict, actual_result: Dict) -> Dict:
        """评估写作练习"""
        correct = prediction.get("prediction") == actual_result.get("result")
        return {
            "topic": prediction.get("topic"),
            "prediction": prediction.get("prediction"),
            "actual": actual_result.get("result"),
            "correct": correct,
            "confidence": prediction.get("confidence", 0),
            "timestamp": datetime.now().isoformat(),
        }

    def get_student_state(self, student_type: str) -> Dict:
        """获取学员训练状态"""
        state_file = os.path.join(self.state_dir, f"{student_type}_paper_state.json")
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "student": student_type,
            "total_trainings": 0,
            "total_problems": 0,
            "total_correct": 0,
            "by_phase": {},
            "by_type": {},
            "by_difficulty": {},
            "streak": 0,
            "last_training": None,
            "history": [],
        }

    def save_student_state(self, student_type: str, state: Dict):
        """保存学员训练状态"""
        state_file = os.path.join(self.state_dir, f"{student_type}_paper_state.json")
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def update_student_state(self, student_type: str, training_result: Dict):
        """训练完成后更新学员状态"""
        state = self.get_student_state(student_type)

        state["total_trainings"] += 1
        state["total_problems"] += training_result["total"]
        state["total_correct"] += training_result["correct"]
        state["last_training"] = datetime.now().isoformat()

        # 连续训练天数
        last_date = state.get("last_training_date")
        today = datetime.now().strftime("%Y-%m-%d")
        if last_date:
            last_dt = datetime.fromisoformat(last_date).date()
            today_dt = datetime.fromisoformat(today)
            if (today_dt - last_dt).days == 1:
                state["streak"] += 1
            elif (today_dt - last_dt).days > 1:
                state["streak"] = 1
        else:
            state["streak"] = 1
        state["last_training_date"] = today

        # 按题型统计
        for detail in training_result.get("details", []):
            ptype = detail.get("type", "unknown")
            pdiff = detail.get("difficulty", "unknown")
            pphase = detail.get("phase", "unknown")
            correct = detail.get("correct", False)

            state["by_type"].setdefault(ptype, {"total": 0, "correct": 0})
            state["by_type"][ptype]["total"] += 1
            if correct:
                state["by_type"][ptype]["correct"] += 1

            state["by_difficulty"].setdefault(pdiff, {"total": 0, "correct": 0})
            state["by_difficulty"][pdiff]["total"] += 1
            if correct:
                state["by_difficulty"][pdiff]["correct"] += 1

            state["by_phase"].setdefault(pphase, {"total": 0, "correct": 0})
            state["by_phase"][pphase]["total"] += 1
            if correct:
                state["by_phase"][pphase]["correct"] += 1

        # 历史记录（仅保留最近20次）
        state["history"].append({
            "date": training_result["date"],
            "total": training_result["total"],
            "correct": training_result["correct"],
            "accuracy": training_result["accuracy"],
        })
        state["history"] = state["history"][-20:]

        self.save_student_state(student_type, state)
        return state

    def get_weekly_summary(self, student_type: str = "zhugebin-001") -> Dict:
        """获取周训练总结"""
        state = self.get_student_state(student_type)
        week_history = state.get("history", [])[-7:]

        total_problems = sum(h["total"] for h in week_history)
        total_correct = sum(h["correct"] for h in week_history)
        accuracy = total_correct / total_problems if total_problems > 0 else 0

        return {
            "week": datetime.now().isocalendar()[1],
            "student": student_type,
            "student_name": STUDENT_CONFIG.get(student_type, {}).get("name", student_type),
            "trainings": len(week_history),
            "total_problems": total_problems,
            "total_correct": total_correct,
            "accuracy": round(accuracy, 3),
            "streak": state.get("streak", 0),
            "by_type": state.get("by_type", {}),
            "by_difficulty": state.get("by_difficulty", {}),
            "timestamp": datetime.now().isoformat(),
        }

    def get_all_students_summary(self) -> List[Dict]:
        """获取所有学员训练摘要"""
        summaries = []
        for sid in STUDENT_CONFIG.keys():
            state = self.get_student_state(sid)
            total = state.get("total_problems", 0)
            correct = state.get("total_correct", 0)
            acc = correct / total if total > 0 else 0
            summaries.append({
                "student_id": sid,
                "name": STUDENT_CONFIG[sid]["name"],
                "type": STUDENT_CONFIG[sid]["type"],
                "total_trainings": state.get("total_trainings", 0),
                "total_problems": total,
                "total_correct": correct,
                "accuracy": round(acc, 3),
                "streak": state.get("streak", 0),
            })
        return summaries

    def cross_review(self, reviewer: str, reviewee: str) -> Dict:
        """
        学员间交叉评审（智能体互相学习机制）

        Args:
            reviewer: 评审者ID
            reviewee: 被评审者ID

        Returns:
            交叉评审结果
        """
        if reviewer not in STUDENT_CONFIG or reviewee not in STUDENT_CONFIG:
            raise ValueError(f"未知学员ID，可选：{list(STUDENT_CONFIG.keys())}")

        reviewee_state = self.get_student_state(reviewee)
        reviewer_state = self.get_student_state(reviewer)

        # 分析被评审者的薄弱项
        weak_types = []
        for ptype, stats in reviewee_state.get("by_type", {}).items():
            if stats["total"] > 0:
                acc = stats["correct"] / stats["total"]
                if acc < 0.5:
                    weak_types.append(ptype)

        # 评审者的强项
        strong_types = []
        for ptype, stats in reviewer_state.get("by_type", {}).items():
            if stats["total"] > 0:
                acc = stats["correct"] / stats["total"]
                if acc >= 0.7:
                    strong_types.append(ptype)

        # 生成评审建议
        suggestions = []
        for wt in weak_types:
            if wt in strong_types:
                suggestions.append(f"{STUDENT_CONFIG[reviewer]['name']}可在'{wt}'题型上指导{STUDENT_CONFIG[reviewee]['name']}")

        return {
            "reviewer": reviewer,
            "reviewer_name": STUDENT_CONFIG[reviewer]["name"],
            "reviewee": reviewee,
            "reviewee_name": STUDENT_CONFIG[reviewee]["name"],
            "reviewee_weak_types": weak_types,
            "reviewer_strong_types": strong_types,
            "suggestions": suggestions,
            "reviewee_accuracy": round(
                reviewee_state["total_correct"] / reviewee_state["total_problems"]
                if reviewee_state.get("total_problems", 0) > 0 else 0, 3
            ),
            "reviewer_accuracy": round(
                reviewer_state["total_correct"] / reviewer_state["total_problems"]
                if reviewer_state.get("total_problems", 0) > 0 else 0, 3
            ),
            "timestamp": datetime.now().isoformat(),
        }


# 演示
if __name__ == "__main__":
    trainer = PaperWritingTrainer()

    print("=" * 60)
    print("🦞 小龙虾网络 · 自动论文撰写训练调度器 V1.0")
    print("=" * 60)

    for sid, cfg in STUDENT_CONFIG.items():
        print(f"\n📋 {cfg['name']}（{cfg['type']}）每日训练计划:")
        plan = trainer.generate_daily_plan(sid)
        print(f"   日期：{plan['date']}")
        print(f"   总题数：{plan['total_problems']}")
        for slot in plan["schedule"]:
            print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题（{slot['phase']}）")

    print("\n" + "=" * 60)
    print("✅ 训练调度器测试完成！")
