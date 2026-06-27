"""
Clawvard School 学习集成模块

实现与目标:
1. 连接 Clawvard School API
2. 自动获取练习题和考试
3. 提交答案并获取反馈
4. 更新8维度评估得分
5. 实现持续学习循环
"""

from __future__ import annotations

import json
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .assessment.eight_dim_engine import EightDimEngine, AssessmentResult
from .assessment.clawvard_bridge import ClawvardBridge, PracticeSession


class ClawvardLearner:
    """
    Clawvard School 学习器
    
    用法:
        learner = ClawvardLearner(node_id="zhugebin-001")
        learner.start_learning_loop()
    """
    
    def __init__(
        self,
        node_id: str,
        agent_name: str = "",
        data_dir: str = "",
        clawvard_api_url: str = "https://clawvard.school",
    ):
        """
        初始化学习器
        
        Args:
            node_id: 节点ID
            agent_name: Agent名称（默认与node_id相同）
            data_dir: 学习数据存储目录
            clawvard_api_url: Clawvard API地址
        """
        self.node_id = node_id
        self.agent_name = agent_name or node_id
        self.clawvard_api_url = clawvard_api_url
        
        # 数据存储
        default_dir = Path.home() / ".lobster-network" / "learning"
        self.data_dir = Path(data_dir) if data_dir else default_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 8维度评估引擎
        self.engine = EightDimEngine(data_dir=str(self.data_dir / "8dim_results"))
        
        # Clawvard API 桥接
        self.bridge = ClawvardBridge(agent_name=self.agent_name)
        
        # 学习记录
        self.learning_history: List[Dict] = []
        
        print(f"✅ ClawvardLearner 初始化完成")
        print(f"   Node ID: {self.node_id}")
        print(f"   Agent Name: {self.agent_name}")
        print(f"   Data Dir: {self.data_dir}")
    
    def start_practice(self, dimensions: Optional[List[str]] = None) -> PracticeSession:
        """
        开始练习会话
        
        Args:
            dimensions: 要练习的维度列表，默认全部8维度
        
        Returns:
            PracticeSession: 练习会话对象
        """
        print(f"\n═══ 开始 Clawvard 练习 ═══")
        print(f"   Agent: {self.agent_name}")
        print(f"   维度: {dimensions or '全部8维度'}")
        
        try:
            session = self.bridge.start_practice(dimensions=dimensions)
            print(f"✅ 练习会话已创建: {session.practice_id}")
            print(f"   题目数: {len(session.questions)}")
            
            # 保存会话
            self._save_practice_session(session)
            
            return session
        
        except Exception as e:
            print(f"❌ 无法连接 Clawvard API: {e}")
            print(f"   使用模拟练习模式")
            return self._create_mock_practice_session(dimensions)
    
    def answer_practice_question(
        self, session: PracticeSession, question_index: int, answer: str
    ) -> Dict[str, Any]:
        """
        回答练习题目
        
        Args:
            session: 练习会话
            question_index: 题目索引
            answer: 答案
        
        Returns:
            dict: 反馈信息
        """
        if question_index >= len(session.questions):
            raise ValueError(f"题目索引超出范围: {question_index}")
        
        question = session.questions[question_index]
        
        try:
            # 提交答案
            feedback = self.bridge.submit_answer(session, question.hash_id, answer)
            
            print(f"\n── 题目 {question_index + 1} 反馈 ──")
            print(f"   维度: {feedback.dimension}")
            print(f"   得分: {feedback.score}/{feedback.max_score}")
            print(f"   等级: {feedback.grade}")
            print(f"   反馈: {feedback.feedback[:200]}...")
            
            # 保存反馈
            self._save_practice_feedback(session, question_index, feedback)
            
            return {
                "dimension": feedback.dimension,
                "score": feedback.score,
                "max_score": feedback.max_score,
                "grade": feedback.grade,
                "feedback": feedback.feedback,
                "reference_answer": feedback.reference_answer,
            }
        
        except Exception as e:
            print(f"❌ 提交答案失败: {e}")
            return {"error": str(e)}
    
    def finish_practice(self, session: PracticeSession) -> Dict[str, float]:
        """
        完成练习并获取8维度得分
        
        Args:
            session: 练习会话
        
        Returns:
            Dict[str, float]: 8维度得分
        """
        print(f"\n═══ 完成练习 ═══")
        
        # 提取得分
        scores = self.bridge.get_practice_scores(session)
        
        print(f"   8维度得分:")
        for dim, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            print(f"     {dim}: {score:.0%}")
        
        # 更新评估引擎
        result = self.engine.assess_from_clawvard(
            node_id=self.node_id,
            clawvard_scores=scores,
            domain="clawvard_practice",
        )
        
        print(f"\n✅ 评估结果已保存")
        print(f"   来源: {result.source}")
        print(f"   时间: {result.timestamp}")
        
        # 保存结果
        self._save_learning_record(session, result)
        
        return scores
    
    def start_exam(self) -> Dict[str, Any]:
        """
        开始正式考试
        
        Returns:
            dict: 考试信息
        """
        print(f"\n═══ 开始 Clawvard 考试 ═══")
        print(f"   Agent: {self.agent_name}")
        
        try:
            exam_info = self.bridge.start_exam()
            print(f"✅ 考试已创建: {exam_info.get('examId', 'N/A')}")
            return exam_info
        
        except Exception as e:
            print(f"❌ 无法连接 Clawvard API: {e}")
            return {"error": str(e)}
    
    def start_learning_loop(self, max_iterations: int = 10) -> None:
        """
        启动持续学习循环
        
        Args:
            max_iterations: 最大迭代次数
        """
        print(f"\n═══ 启动持续学习循环 ═══")
        print(f"   Node: {self.node_id}")
        print(f"   最大迭代: {max_iterations}")
        
        for i in range(max_iterations):
            print(f"\n── 迭代 {i + 1}/{max_iterations} ──")
            
            # 1. 开始练习
            session = self.start_practice()
            
            # 2. 回答所有题目（模拟：自动生成答案）
            for idx, question in enumerate(session.questions):
                # 模拟答案生成（实际应该调用AI生成答案）
                mock_answer = f"这是关于 {question.dimension} 的练习答案（题目: {question.title}）"
                self.answer_practice_question(session, idx, mock_answer)
            
            # 3. 完成练习并获取得分
            scores = self.finish_practice(session)
            
            # 4. 检查是否达到目标（所有维度 > 80%）
            all_good = all(score >= 0.8 for score in scores.values())
            if all_good:
                print(f"\n🎉 所有维度已达到 80% 以上！学习完成！")
                break
            
            # 5. 找出最弱的维度，针对性练习
            weakest_dim = min(scores, key=scores.get)
            print(f"\n   最弱维度: {weakest_dim} ({scores[weakest_dim]:.0%})")
            print(f"   下一轮将针对性练习该维度")
            
            # 等待一段时间（避免API限流）
            time.sleep(2)
        
        print(f"\n✅ 学习循环完成")
    
    def get_learning_report(self) -> Dict[str, Any]:
        """
        生成学习报告
        
        Returns:
            dict: 学习报告
        """
        # 加载历史评估记录
        history = self.engine.load_history(self.node_id)
        
        if not history:
            return {"error": "没有学习记录"}
        
        # 计算进步幅度
        first = history[0]
        latest = history[-1]
        
        improvement = {}
        for dim in first.profile.scores:
            old_score = first.profile.scores.get(dim, 0)
            new_score = latest.profile.scores.get(dim, 0)
            improvement[dim] = new_score - old_score
        
        report = {
            "node_id": self.node_id,
            "agent_name": self.agent_name,
            "total_sessions": len(history),
            "first_assessment": first.timestamp,
            "latest_assessment": latest.timestamp,
            "latest_scores": latest.profile.scores,
            "improvement": improvement,
            "overall_improvement": sum(improvement.values()) / max(len(improvement), 1),
        }
        
        print(f"\n═══ 学习报告 ═══")
        print(f"   Node: {report['node_id']}")
        print(f"   总评估次数: {report['total_sessions']}")
        print(f"   首次评估: {report['first_assessment']}")
        print(f"   最新评估: {report['latest_assessment']}")
        print(f"\n── 最新8维度得分 ──")
        for dim, score in sorted(report['latest_scores'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {dim}: {score:.0%}")
        print(f"\n── 进步幅度 ──")
        for dim, imp in sorted(report['improvement'].items(), key=lambda x: x[1], reverse=True):
            sign = "+" if imp >= 0 else ""
            print(f"   {dim}: {sign}{imp:.0%}")
        print(f"\n   总进步: {report['overall_improvement']:+.0%}")
        
        return report
    
    # ── 内部方法 ────────────────────────────────────────────────
    
    def _save_practice_session(self, session: PracticeSession) -> None:
        """保存练习会话"""
        file_path = self.data_dir / f"practice_{session.practice_id}.json"
        data = {
            "practice_id": session.practice_id,
            "agent_name": session.agent_name,
            "dimensions": session.dimensions,
            "started_at": session.started_at,
            "questions": [q.__dict__ for q in session.questions],
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_practice_feedback(self, session: PracticeSession, question_index: int, feedback) -> None:
        """保存练习反馈"""
        file_path = self.data_dir / f"practice_{session.practice_id}_feedback.json"
        
        # 加载现有反馈
        feedback_list = []
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                feedback_list = json.load(f)
        
        # 添加新反馈
        feedback_list.append({
            "question_index": question_index,
            "dimension": feedback.dimension,
            "score": feedback.score,
            "max_score": feedback.max_score,
            "grade": feedback.grade,
            "feedback": feedback.feedback,
            "timestamp": datetime.now().isoformat(),
        })
        
        # 保存
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, ensure_ascii=False, indent=2)
    
    def _save_learning_record(self, session: PracticeSession, result: AssessmentResult) -> None:
        """保存学习记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "practice_id": session.practice_id,
            "assessment_result": result.to_dict(),
        }
        self.learning_history.append(record)
        
        # 保存到文件
        history_file = self.data_dir / f"{self.node_id}_learning_history.json"
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(self.learning_history, f, ensure_ascii=False, indent=2)
    
    def _create_mock_practice_session(self, dimensions: Optional[List[str]] = None) -> PracticeSession:
        """创建模拟练习会话（当API不可用时）"""
        from .assessment.clawvard_bridge import PracticeQuestion
        
        dims = dimensions or ["understanding", "execution", "reasoning", "reflection", "tooling", "eq", "memory", "retrieval"]
        
        session = PracticeSession(
            practice_id=f"mock_{int(time.time())}",
            agent_name=self.agent_name,
            dimensions=dims,
            started_at=datetime.now().isoformat(),
        )
        
        # 创建模拟题目
        for dim in dims:
            q = PracticeQuestion(
                dimension=dim,
                hash_id=f"mock_{dim}_{int(time.time())}",
                title=f"{dim} 练习题目",
                question=f"请展示你在 {dim} 维度上的能力（模拟题目）",
                question_type="open",
            )
            session.questions.append(q)
        
        print(f"✅ 模拟练习会话已创建: {session.practice_id}")
        print(f"   （Clawvard API 不可用，使用模拟模式）")
        
        return session


def test_learner():
    """测试学习器"""
    print("═══ 测试 ClawvardLearner ═══")
    
    learner = ClawvardLearner(node_id="zhugebin-001", agent_name="诸葛斌的工作助手")
    
    # 测试1: 开始练习
    print("\n1. 测试开始练习:")
    session = learner.start_practice(dimensions=["reasoning", "execution"])
    
    # 测试2: 回答问题
    print("\n2. 测试回答问题:")
    if session.questions:
        answer = "这是我的答案（测试）"
        feedback = learner.answer_practice_question(session, 0, answer)
        print(f"   反馈: {feedback}")
    
    # 测试3: 完成练习
    print("\n3. 测试完成练习:")
    scores = learner.finish_practice(session)
    print(f"   得分: {scores}")
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    test_learner()
