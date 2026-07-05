"""
8维度评估引擎测试
"""

import sys
import os
import unittest

# 添加 src 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lobster_network.assessment.dimensions import (
    Dimension, DimensionProfile, DIMENSION_REGISTRY,
    DIMENSION_DESCRIPTIONS, DIMENSION_WEIGHTS, score_to_grade,
)
from lobster_network.assessment.eight_dim_engine import (
    EightDimEngine, AssessmentResult, DimensionScorer, ImprovementAdvisor,
)
from lobster_network.assessment.clawvard_bridge import (
    ClawvardBridge, PracticeSession, PracticeQuestion,
)


class TestDimensions(unittest.TestCase):
    """维度定义测试"""

    def test_registry_has_8_dims(self):
        self.assertEqual(len(DIMENSION_REGISTRY), 8)

    def test_all_dims_have_descriptions(self):
        for dim in DIMENSION_REGISTRY:
            self.assertIn(dim, DIMENSION_DESCRIPTIONS)
            desc = DIMENSION_DESCRIPTIONS[dim]
            self.assertIn("name_zh", desc)
            self.assertIn("name_en", desc)
            self.assertIn("desc", desc)

    def test_weights_sum_to_one(self):
        for domain, weights in DIMENSION_WEIGHTS.items():
            total = sum(weights.values())
            self.assertAlmostEqual(total, 1.0, places=2, msg=f"{domain} weights sum to {total}")

    def test_score_to_grade(self):
        self.assertEqual(score_to_grade(0.97), "S")
        self.assertEqual(score_to_grade(0.92), "A+")
        self.assertEqual(score_to_grade(0.87), "A")
        self.assertEqual(score_to_grade(0.75), "B")
        self.assertEqual(score_to_grade(0.55), "C")
        self.assertEqual(score_to_grade(0.20), "F")

    def test_dimension_from_registry(self):
        dim = Dimension.from_registry("reasoning")
        self.assertEqual(dim.key, "reasoning")
        self.assertEqual(dim.name_zh, "推理力")


class TestDimensionProfile(unittest.TestCase):
    """能力画像测试"""

    def setUp(self):
        self.scores = {
            "understanding": 0.85, "execution": 0.90, "retrieval": 0.70,
            "reasoning": 0.88, "reflection": 0.60, "tooling": 0.75,
            "eq": 0.65, "memory": 0.55,
        }
        self.profile = DimensionProfile(
            node_id="test_node", domain="go", scores=self.scores,
        )

    def test_grades_computed(self):
        self.assertEqual(self.profile.grades["execution"], "A+")
        self.assertEqual(self.profile.grades["understanding"], "A")
        self.assertEqual(self.profile.grades["memory"], "C")

    def test_weighted_total(self):
        # go 域 reasoning 权重最高(0.30)
        self.assertGreater(self.profile.weighted_total, 0)
        self.assertLessEqual(self.profile.weighted_total, 1.0)

    def test_strengths(self):
        top3 = self.profile.strengths(3)
        self.assertEqual(len(top3), 3)
        # execution (0.90) should be top
        self.assertIn("执行力", top3)

    def test_weaknesses(self):
        bottom3 = self.profile.weaknesses(3)
        self.assertEqual(len(bottom3), 3)
        # memory (0.55) should be bottom
        self.assertIn("记忆力", bottom3)

    def test_radar_data(self):
        data = self.profile.radar_data()
        self.assertEqual(len(data), 8)
        for item in data:
            self.assertIn("dimension", item)
            self.assertIn("score", item)

    def test_to_dict(self):
        d = self.profile.to_dict()
        self.assertEqual(d["node_id"], "test_node")
        self.assertIn("scores", d)
        self.assertIn("grades", d)
        self.assertIn("strengths", d)

    def test_summary(self):
        s = self.profile.summary()
        self.assertIn("test_node", s)
        self.assertIn("能力画像", s)

    def test_to_json(self):
        j = self.profile.to_json()
        import json
        parsed = json.loads(j)
        self.assertEqual(parsed["node_id"], "test_node")


class TestDimensionScorer(unittest.TestCase):
    """评分器测试"""

    def test_score_all_returns_8_dims(self):
        records = [{"task_completion": 0.8, "output_quality": 0.9}]
        scores = DimensionScorer.score_all(records)
        self.assertEqual(len(scores), 8)
        for dim in DIMENSION_REGISTRY:
            self.assertIn(dim, scores)

    def test_score_with_empty_records(self):
        scores = DimensionScorer.score_all([])
        for v in scores.values():
            self.assertEqual(v, 0.0)

    def test_score_go_domain_records(self):
        records = [
            {"domain": "go", "problems_solved": 80, "problems_attempted": 100, "win_rate": 0.6},
        ]
        scores = DimensionScorer.score_all(records)
        self.assertAlmostEqual(scores["execution"], 0.8)
        self.assertAlmostEqual(scores["reasoning"], 0.6)


class TestImprovementAdvisor(unittest.TestCase):
    """改进建议测试"""

    def test_generate_for_weak_dims(self):
        scores = {d: 0.9 for d in DIMENSION_REGISTRY}
        scores["memory"] = 0.3
        scores["eq"] = 0.4
        profile = DimensionProfile(node_id="test", domain="default", scores=scores)
        suggestions = ImprovementAdvisor.generate(profile, top_n=2)
        self.assertIn("memory", suggestions)
        self.assertIn("eq", suggestions)
        self.assertTrue(len(suggestions["memory"]) > 0)


class TestEightDimEngine(unittest.TestCase):
    """主引擎测试"""

    def test_assess_from_records(self):
        engine = EightDimEngine(data_dir="/tmp/lobster_test_8dim")
        records = [
            {"task_completion": 0.85, "output_quality": 0.90, "reasoning_accuracy": 0.75},
            {"domain": "go", "problems_solved": 50, "problems_attempted": 60, "win_rate": 0.55},
        ]
        result = engine.assess_from_records("xiaochen", "go", records)
        self.assertIsInstance(result, AssessmentResult)
        self.assertEqual(result.node_id, "xiaochen")
        self.assertEqual(result.domain, "go")
        self.assertEqual(result.source, "internal")
        self.assertIsInstance(result.profile, DimensionProfile)

    def test_assess_from_clawvard(self):
        engine = EightDimEngine(data_dir="/tmp/lobster_test_8dim")
        scores = {
            "understanding": 0.80, "execution": 0.75, "retrieval": 0.60,
            "reasoning": 0.85, "reflection": 0.70, "tooling": 0.65,
            "eq": 0.55, "memory": 0.50,
        }
        result = engine.assess_from_clawvard("qoder", scores)
        self.assertEqual(result.source, "clawvard")
        self.assertGreater(result.profile.weighted_total, 0)

    def test_assess_hybrid(self):
        engine = EightDimEngine(data_dir="/tmp/lobster_test_8dim")
        records = [{"task_completion": 0.9, "output_quality": 0.8}]
        clawvard = {"understanding": 0.85, "reasoning": 0.90, "execution": 0.80}
        result = engine.assess_hybrid("qoder", "go", records, clawvard)
        self.assertEqual(result.source, "hybrid")

    def test_compare_nodes(self):
        engine = EightDimEngine(data_dir="/tmp/lobster_test_8dim")
        p1 = DimensionProfile(node_id="a", domain="go", scores={d: 0.7 for d in DIMENSION_REGISTRY})
        p2 = DimensionProfile(node_id="b", domain="go", scores={d: 0.5 for d in DIMENSION_REGISTRY})
        comparison = engine.compare_nodes([p1, p2])
        self.assertEqual(len(comparison["dimensions"]), 8)
        for dim_data in comparison["dimensions"].values():
            self.assertEqual(dim_data["best"], "a")


class TestClawvardBridge(unittest.TestCase):
    """Clawvard 桥接测试 (离线)"""

    def test_bridge_init(self):
        bridge = ClawvardBridge("test_agent")
        self.assertEqual(bridge.agent_name, "test_agent")

    def test_practice_question_parse(self):
        raw = {
            "dimension": "reasoning",
            "hash": "reas-01",
            "title": "Logic Puzzle",
            "question": "If A then B. A is true. What about B?",
        }
        q = PracticeQuestion.from_api(raw)
        self.assertEqual(q.dimension, "reasoning")
        self.assertEqual(q.hash_id, "reas-01")
        self.assertEqual(q.question_type, "open")

    def test_practice_session_summary(self):
        session = PracticeSession(
            practice_id="test-123",
            agent_name="qoder小龙虾",
            dimensions=["reasoning", "execution"],
        )
        s = session.summary()
        self.assertIn("qoder小龙虾", s)
        self.assertIn("test-123", s)


if __name__ == "__main__":
    unittest.main()
