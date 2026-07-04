"""
炒股预测训练调度器 V1.0
=====================

将炒股预测题目集成到每日训练计划，支持三种学员类型：
- xiaochen（稳健型）：基础题量，重基础概念
- zhuguxia（加速型）：更多题，重技术分析
- zhugebin-001（研究型）：全部题型 + 实战预测 + 仓位管理

设计参考：domains/learning/trainers/football_predict_trainer.py
"""

import json
import os
from typing import Dict, List
from datetime import datetime, timedelta

try:
    from ..problems.stock_predict_engine import StockPredictEngine
except ImportError:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "problems"))
    from stock_predict_engine import StockPredictEngine


# ========== 学员训练配置 ==========
STUDENT_CONFIG = {
    "xiaochen": {  # 稳健型：重基础
        "name": "小陈",
        "type": "稳健型",
        "config": {
            "concept_choice": 3,
            "concept_judge": 2,
            "basic_calc": 2,
            "kline_pattern": 1,
            "indicator_analysis": 1,
            "trend": 1,
            "price_range": 0,
            "amplitude": 0,
            "position_sizing": 0,
            "portfolio": 0,
        },
        "phases": ["phase1"],
        "base_accuracy": {"入门": 0.80, "初级": 0.65, "中级": 0.45, "高级": 0.30},
    },
    "zhuguxia": {  # 加速型：技术分析为主
        "name": "诸葛虾",
        "type": "加速型",
        "config": {
            "concept_choice": 1,
            "concept_judge": 1,
            "basic_calc": 1,
            "kline_pattern": 3,
            "indicator_analysis": 3,
            "trend": 2,
            "price_range": 1,
            "amplitude": 1,
            "position_sizing": 0,
            "portfolio": 0,
        },
        "phases": ["phase2", "phase3"],
        "base_accuracy": {"入门": 0.90, "初级": 0.75, "中级": 0.55, "高级": 0.40},
    },
    "zhugebin-001": {  # 研究型：全题型 + 仓位管理
        "name": "诸葛斌的工作助手",
        "type": "研究型",
        "config": {
            "concept_choice": 1,
            "concept_judge": 1,
            "basic_calc": 1,
            "kline_pattern": 2,
            "indicator_analysis": 2,
            "trend": 3,
            "price_range": 2,
            "amplitude": 1,
            "position_sizing": 2,
            "portfolio": 2,
        },
        "phases": ["phase1", "phase2", "phase3"],
        "base_accuracy": {"入门": 0.92, "初级": 0.80, "中级": 0.62, "高级": 0.50},
    },
}


class StockPredictTrainer:
    """炒股预测训练调度器"""

    def __init__(self, engine: StockPredictEngine = None):
        self.engine = engine or StockPredictEngine()
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
            "domain": "stock-predict",
            "schedule": [],
            "total_problems": 0,
        }

        time_slots = ["09:30", "11:00", "14:00", "15:30"]
        slot_idx = 0

        for problem_type, count in cfg["config"].items():
            if count == 0:
                continue
            # 在学员允许的 phases 中查找题目，每个题目带 phase 标签
            problems = []
            for ph in cfg["phases"]:
                probs = self.engine.get_problems(
                    phase=ph, problem_type=problem_type, limit=count - len(problems)
                )
                # 给每题注入 phase 来源标签
                for p in probs:
                    p_with_phase = dict(p)
                    p_with_phase["phase"] = ph
                    problems.append(p_with_phase)
                if len(problems) >= count:
                    break
            problems = problems[:count]

            if problems:
                # 统计本次 schedule 的 phase 来源
                phase_set = sorted(set(p.get("phase", "phase1") for p in problems))
                plan["schedule"].append({
                    "time": time_slots[slot_idx % len(time_slots)],
                    "type": problem_type,
                    "count": len(problems),
                    "phases": phase_set,
                    "phase": phase_set[0],  # 兼容字段
                    "problems": problems,
                })
                plan["total_problems"] += len(problems)
                slot_idx += 1

        return plan

    def evaluate_prediction(self, prediction: Dict, actual_result: Dict) -> Dict:
        """评估预测准确率"""
        correct = prediction.get("prediction") == actual_result.get("result")
        return {
            "stock": prediction.get("stock"),
            "prediction": prediction.get("prediction"),
            "actual": actual_result.get("result"),
            "correct": correct,
            "confidence": prediction.get("confidence", 0),
            "timestamp": datetime.now().isoformat(),
        }

    def get_student_state(self, student_type: str) -> Dict:
        """获取学员训练状态"""
        state_file = os.path.join(self.state_dir, f"{student_type}_stock_state.json")
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
        state_file = os.path.join(self.state_dir, f"{student_type}_stock_state.json")
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


# 演示
if __name__ == "__main__":
    trainer = StockPredictTrainer()

    print("=" * 60)
    print("🦞 小龙虾网络 · 炒股预测训练调度器 V1.0")
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
