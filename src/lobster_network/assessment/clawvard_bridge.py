"""
Clawvard School API 桥接模块

对接 Clawvard School 8维度评估API:
- 练习模式 (Practice): 即时反馈 + 参考答案
- 考试模式 (Exam): 正式评估，生成成绩单

API端点:
  POST /api/practice/start      — 开始练习
  POST /api/practice/answer     — 提交答案
  GET  /api/exam/status         — 考试状态
  POST /api/exam/start          — 开始考试
  POST /api/exam/batch-answer   — 批量提交答案
  POST /api/exam/start-auth     — 认证考试
  GET  /api/agent/goal          — Agent目标

用法:
    bridge = ClawvardBridge(agent_name="qoder小龙虾")
    session = bridge.start_practice()
    for q in session.questions:
        answer = session.answer(q["hash"], "我的答案")
        print(answer["feedback"])
    scores = session.get_scores()
"""

# from __future__ import annotations  # Python 3.6 不支持

import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError


CLAWVARD_BASE = "https://clawvard.school"
ALL_DIMENSIONS = [
    "understanding", "execution", "retrieval", "reasoning",
    "reflection", "tooling", "eq", "memory",
]


def _api_post(path: str, data: dict, timeout: int = 30) -> dict:
    """发送POST请求"""
    url = f"{CLAWVARD_BASE}{path}"
    body = json.dumps(data).encode("utf-8")
    req = Request(url, data=body, headers={
        "Content-Type": "application/json",
        "User-Agent": "LobsterNetwork/0.5.0",
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"Clawvard API error {e.code}: {error_body}") from e


def _api_get(path: str, timeout: int = 30) -> dict:
    """发送GET请求"""
    url = f"{CLAWVARD_BASE}{path}"
    req = Request(url, headers={
        "User-Agent": "LobsterNetwork/0.5.0",
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        raise RuntimeError(f"Clawvard API error {e.code}: {error_body}") from e


@dataclass
class PracticeQuestion:
    """单个练习题目"""
    dimension: str
    hash_id: str
    title: str
    question: str
    options: Optional[List[str]] = None  # 选择题选项
    question_type: str = "open"  # open / choice

    @classmethod
    def from_api(cls, raw: dict) -> "PracticeQuestion":
        return cls(
            dimension=raw.get("dimension", "unknown"),
            hash_id=raw.get("hash", ""),
            title=raw.get("title", ""),
            question=raw.get("question", ""),
            options=raw.get("options"),
            question_type="choice" if raw.get("options") else "open",
        )


@dataclass
class PracticeAnswer:
    """单个答案的反馈"""
    dimension: str
    hash_id: str
    score: float       # 0~1
    max_score: float
    feedback: str
    reference_answer: str
    grade: str = ""

    @classmethod
    def from_api(cls, raw: dict) -> "PracticeAnswer":
        return cls(
            dimension=raw.get("dimension", "unknown"),
            hash_id=raw.get("hash", ""),
            score=raw.get("score", 0),
            max_score=raw.get("maxScore", 1),
            feedback=raw.get("feedback", ""),
            reference_answer=raw.get("referenceAnswer", ""),
            grade=raw.get("grade", ""),
        )


@dataclass
class PracticeSession:
    """练习会话"""
    practice_id: str
    agent_name: str
    dimensions: List[str]
    questions: List[PracticeQuestion] = field(default_factory=list)
    answers: List[PracticeAnswer] = field(default_factory=list)
    scores: Dict[str, float] = field(default_factory=dict)
    started_at: str = ""

    def summary(self) -> str:
        """生成练习会话摘要"""
        lines = [
            f"═══ Clawvard 练习报告 ═══",
            f"Agent: {self.agent_name}",
            f"练习ID: {self.practice_id}",
            f"维度数: {len(self.dimensions)}",
            f"题目数: {len(self.questions)}",
            "",
        ]
        if self.answers:
            lines.append("── 答题结果 ──")
            for a in self.answers:
                lines.append(f"  [{a.dimension}] {a.score}/{a.max_score} {a.grade}")
                if a.feedback:
                    lines.append(f"    反馈: {a.feedback[:100]}...")
            lines.append("")
        if self.scores:
            lines.append("── 维度得分 ──")
            for dim, score in sorted(self.scores.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {dim}: {score:.0%}")
        return "\n".join(lines)


class ClawvardBridge:
    """
    Clawvard School API 桥接

    用法:
        bridge = ClawvardBridge("qoder小龙虾")

        # 练习模式
        session = bridge.start_practice()
        session = bridge.start_practice(dimensions=["reasoning", "execution"])

        # 答题
        answer = bridge.submit_answer(session, question_hash, "我的答案")

        # 考试模式
        exam_status = bridge.get_exam_status()
        exam = bridge.start_exam()
    """

    def __init__(self, agent_name: str = "qoder小龙虾"):
        self.agent_name = agent_name

    def start_practice(
        self, dimensions: Optional[List[str]] = None
    ) -> PracticeSession:
        """
        开始练习会话

        Args:
            dimensions: 要练习的维度列表，默认全部8维度

        Returns:
            PracticeSession 包含题目列表
        """
        dims = dimensions or ALL_DIMENSIONS
        data = {
            "agentName": self.agent_name,
            "dimensions": dims,
        }
        resp = _api_post("/api/practice/start", data)

        session = PracticeSession(
            practice_id=resp.get("practiceId", ""),
            agent_name=self.agent_name,
            dimensions=dims,
            started_at=resp.get("startedAt", ""),
        )

        # 解析题目
        raw_questions = resp.get("questions", [])
        for rq in raw_questions:
            session.questions.append(PracticeQuestion.from_api(rq))

        return session

    def submit_answer(
        self, session: PracticeSession, question_hash: str, answer: str
    ) -> PracticeAnswer:
        """提交单个答案并获取即时反馈"""
        data = {
            "practiceId": session.practice_id,
            "hash": question_hash,
            "answer": answer,
        }
        resp = _api_post("/api/practice/answer", data)
        pa = PracticeAnswer.from_api(resp)
        session.answers.append(pa)
        return pa

    def get_practice_scores(self, session: PracticeSession) -> Dict[str, float]:
        """从已完成的练习会话中提取维度分数"""
        dim_scores: Dict[str, List[float]] = {}
        for a in session.answers:
            dim_scores.setdefault(a.dimension, []).append(
                a.score / max(a.max_score, 1)
            )
        session.scores = {
            dim: sum(scores) / max(len(scores), 1)
            for dim, scores in dim_scores.items()
        }
        return session.scores

    def get_exam_status(self) -> dict:
        """查询考试状态"""
        return _api_get(f"/api/exam/status?agent={self.agent_name}")

    def start_exam(self) -> dict:
        """开始正式考试"""
        return _api_post("/api/exam/start", {"agentName": self.agent_name})

    def batch_answer_exam(self, exam_id: str, answers: List[dict]) -> dict:
        """批量提交考试答案"""
        data = {
            "examId": exam_id,
            "answers": answers,  # [{"hash": "...", "answer": "..."}, ...]
        }
        return _api_post("/api/exam/batch-answer", data)

    def get_agent_goal(self) -> dict:
        """获取Agent目标设定"""
        return _api_get(f"/api/agent/goal?agent={self.agent_name}")
