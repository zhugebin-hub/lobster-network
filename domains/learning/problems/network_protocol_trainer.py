"""
网络协议训练器 V1.0
=================

学员配置（对齐 Meyo 推送的三只 Agent 设定）：
- xiaochen  稳健型：Phase1 → Phase2，重基础，准确率优先
- zhuguxia  加速型：Phase1+2 快速通关，进入 Phase3 SDN/安全
- zhugebin-001 研究型：全阶段 + 抓包实战，追求 90%+ 准确率

状态存储：domains/learning/trainers/state/{student}_network_state.json
"""

import json
import os
import random
from datetime import datetime
from typing import Dict, List, Optional


# ========== 学员配置 ==========
STUDENT_CONFIG = {
    "xiaochen": {
        "name": "小陈（稳健型）",
        "description": "慢但稳，基础题100%，适合 Phase1→2 打牢根基",
        "phases": ["phase1", "phase2"],
        "questions_per_day": 10,
        "target_accuracy": 0.90,
        "learning_rate": 0.05,
    },
    "zhuguxia": {
        "name": "诸葛虾（加速型）",
        "description": "快而准，解题速度 0.5-2秒/题，快速通关 Phase1+2",
        "phases": ["phase1", "phase2", "phase3"],
        "questions_per_day": 20,
        "target_accuracy": 0.85,
        "learning_rate": 0.10,
    },
    "zhugebin-001": {
        "name": "诸葛斌-001（研究型）",
        "description": "全阶段覆盖 + 抓包实战，追求 90%+ 准确率",
        "phases": ["phase1", "phase2", "phase3"],
        "questions_per_day": 15,
        "target_accuracy": 0.92,
        "learning_rate": 0.08,
    },
}


class NetworkProtocolTrainer:
    """网络协议训练器"""

    def __init__(self, engine, student_type: str = "xiaochen"):
        self.engine = engine
        self.student_type = student_type
        config = STUDENT_CONFIG.get(student_type, STUDENT_CONFIG["xiaochen"])
        self.config = config
        self.state = self._load_state()

    def _get_state_path(self) -> str:
        state_dir = os.path.join(
            os.path.dirname(__file__),
            "..", "trainers", "state"
        )
        os.makedirs(state_dir, exist_ok=True)
        return os.path.join(state_dir, f"{self.student_type}_network_state.json")

    def _load_state(self) -> Dict:
        path = self._get_state_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        # 初始状态
        return {
            "student": self.student_type,
            "current_phase": self.config["phases"][0],
            "completed_phases": [],
            "total_answered": 0,
            "total_correct": 0,
            "phase_scores": {},
            "session_history": [],
            "updated_at": datetime.now().isoformat(),
        }

    def _save_state(self):
        self.state["updated_at"] = datetime.now().isoformat()
        path = self._get_state_path()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def get_next_questions(self, count: int = None) -> List[Dict]:
        """获取下一批题目"""
        if count is None:
            count = self.config["questions_per_day"]
        phase = self.state["current_phase"]
        return self.engine.quiz(phase=phase, count=count)

    def submit_answers(self, results: List[Dict]) -> Dict:
        """
        提交答题结果，更新状态
        results 格式: [{"id": "np1-001", "correct": true}, ...]
        """
        self.state["total_answered"] += len(results)
        correct_count = sum(1 for r in results if r.get("correct"))
        self.state["total_correct"] += correct_count

        # 按阶段统计
        phase = self.state["current_phase"]
        if phase not in self.state["phase_scores"]:
            self.state["phase_scores"][phase] = {"total": 0, "correct": 0}
        self.state["phase_scores"][phase]["total"] += len(results)
        self.state["phase_scores"][phase]["correct"] += correct_count

        # 记录 session
        accuracy = correct_count / len(results) if results else 0
        session = {
            "phase": phase,
            "count": len(results),
            "correct": correct_count,
            "accuracy": round(accuracy, 3),
            "timestamp": datetime.now().isoformat(),
        }
        self.state["session_history"].append(session)

        # 阶段升级判断
        phase_acc = self.state["phase_scores"][phase]["correct"] / \
                    self.state["phase_scores"][phase]["total"]
        if phase_acc >= self.config["target_accuracy"]:
            if phase not in self.state["completed_phases"]:
                self.state["completed_phases"].append(phase)
            # 进入下一阶段
            phases = self.config["phases"]
            if phase in phases:
                idx = phases.index(phase)
                if idx + 1 < len(phases):
                    self.state["current_phase"] = phases[idx + 1]

        self._save_state()
        return session

    def get_report(self) -> Dict:
        """生成学习报告"""
        total_acc = (
            self.state["total_correct"] / self.state["total_answered"]
            if self.state["total_answered"] > 0 else 0
        )
        return {
            "student": self.student_type,
            "student_name": self.config["name"],
            "current_phase": self.state["current_phase"],
            "completed_phases": self.state["completed_phases"],
            "total_answered": self.state["total_answered"],
            "total_correct": self.state["total_correct"],
            "overall_accuracy": round(total_acc, 3),
            "phase_scores": self.state["phase_scores"],
            "sessions_count": len(self.state["session_history"]),
            "updated_at": self.state["updated_at"],
        }

    def reset(self):
        """重置学习状态"""
        self.state = {
            "student": self.student_type,
            "current_phase": self.config["phases"][0],
            "completed_phases": [],
            "total_answered": 0,
            "total_correct": 0,
            "phase_scores": {},
            "session_history": [],
            "updated_at": datetime.now().isoformat(),
        }
        self._save_state()
