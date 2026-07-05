#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v0.6.0 新模块综合测试

覆盖模块:
- dialogue.py (增强版对话引擎: Jaccard距离, bigram, 对话深度, 跨域洞察)
- learning/coordinator.py (学习协调器: 训练轮次, 自适应计划, 协作建议)
- network/http_transport.py (HTTP传输层: 消息收发, 心跳, 节点发现, 注册同步)
"""

import os
import socket
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from lobster_network.node import Node
from lobster_network.dialogue import (
    DialogueEngine,
    DialogueResult,
    _character_bigrams,
    _word_tokens,
    _jaccard_distance,
)
from lobster_network.learning.coordinator import (
    LearningCoordinator,
    TrainingPlan,
    ProgressReport,
    TrainingRoundResult,
    LearningState,
    CollaborationSuggestion,
)
from lobster_network.network.http_transport import HTTPTransport
from lobster_network.assessment.dimensions import (
    DimensionProfile,
    DIMENSION_REGISTRY,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_free_port() -> int:
    """Find an available TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _make_node(
    node_id: str,
    name: str = "",
    perspective: str = "",
    knowledge_base: str = "",
    capabilities: list = None,
) -> Node:
    """Create a Node with sensible defaults for testing."""
    return Node(
        node_id=node_id,
        name=name or node_id,
        perspective=perspective,
        knowledge_base=knowledge_base,
        capabilities=capabilities or [],
    )


# Standard training records that exercise many dimension scorers.
_STANDARD_RECORDS = [
    {
        "task_completion": 0.80,
        "output_quality": 0.75,
        "reasoning_accuracy": 0.60,
        "retrieval_accuracy": 0.70,
        "improvement_rate": 0.50,
        "tool_usage_accuracy": 0.65,
        "dialogue_quality": 0.55,
        "memory_retention": 0.45,
    },
]

_HIGH_RECORDS = [
    {
        "task_completion": 0.95,
        "output_quality": 0.92,
        "reasoning_accuracy": 0.90,
        "retrieval_accuracy": 0.88,
        "improvement_rate": 0.85,
        "tool_usage_accuracy": 0.93,
        "dialogue_quality": 0.91,
        "memory_retention": 0.87,
    },
]

_LOW_RECORDS = [
    {
        "task_completion": 0.20,
        "output_quality": 0.15,
        "reasoning_accuracy": 0.10,
        "retrieval_accuracy": 0.18,
        "improvement_rate": 0.12,
        "tool_usage_accuracy": 0.22,
        "dialogue_quality": 0.14,
        "memory_retention": 0.16,
    },
]


# ===========================================================================
# TestDialogueEnhanced
# ===========================================================================

class TestDialogueEnhanced:
    """增强对话引擎测试"""

    def test_jaccard_distance_identical(self):
        """相同文本 -> 距离 0"""
        text = "围棋死活题与策略分析"
        bigrams = _character_bigrams(text)
        dist = _jaccard_distance(bigrams, bigrams)
        assert dist == 0.0

    def test_jaccard_distance_different(self):
        """完全不同的文本 -> 高距离 (接近 1)"""
        set_a = {"ab", "bc", "cd"}
        set_b = {"xy", "yz", "zw"}
        dist = _jaccard_distance(set_a, set_b)
        assert dist == 1.0  # no overlap at all

    def test_jaccard_distance_empty_sets(self):
        """两个空集 -> 距离 0"""
        assert _jaccard_distance(set(), set()) == 0.0

    def test_character_bigrams(self):
        """验证字符 bigram 提取"""
        bigrams = _character_bigrams("hello")
        assert bigrams == {"he", "el", "ll", "lo"}

        # Single character
        assert _character_bigrams("x") == {"x"}

        # Empty string
        assert _character_bigrams("") == set()

    def test_word_tokens(self):
        """验证中英文分词"""
        tokens = _word_tokens("围棋, 人工智能; 策略")
        assert tokens == {"围棋", "人工智能", "策略"}

        # English with punctuation
        tokens_en = _word_tokens("hello world, foo bar")
        assert "hello" in tokens_en
        assert "world" in tokens_en
        assert "foo" in tokens_en
        assert "bar" in tokens_en

    def test_perspective_distance_continuous(self):
        """验证视角距离是连续的 (非二元), 相似但不相同的视角产生中间值"""
        node_a = _make_node(
            "a", perspective="逻辑推理与因果分析",
            knowledge_base="围棋, 数学",
            capabilities=["reasoning"],
        )
        # Very similar perspective - shares many bigrams
        node_b = _make_node(
            "b", perspective="逻辑推理与因果推断",
            knowledge_base="围棋, 数学",
            capabilities=["reasoning"],
        )
        engine = DialogueEngine()
        dist = engine._perspective_distance(node_a, node_b)
        # Should be between 0 and 1, not exactly 0 or 1
        assert 0.0 < dist < 1.0, f"Expected continuous distance, got {dist}"

        # Identical perspectives should give 0
        node_c = _make_node(
            "c", perspective="逻辑推理与因果分析",
            knowledge_base="围棋",
            capabilities=[],
        )
        dist_same = engine._perspective_distance(node_a, node_c)
        assert dist_same == 0.0

    def test_knowledge_complementarity_bonus(self):
        """验证知识互补性包含域覆盖奖励"""
        node_a = _make_node(
            "a",
            perspective="技术",
            knowledge_base="Python, 算法, 数据结构, 机器学习, 深度学习",
            capabilities=["coding"],
        )
        node_b = _make_node(
            "b",
            perspective="艺术",
            knowledge_base="绘画, 色彩, 构图, 设计, 排版",
            capabilities=["design"],
        )
        engine = DialogueEngine()
        comp = engine._knowledge_complementarity(node_a, node_b)

        # With completely different knowledge bases, complementarity should be high
        # Base Jaccard distance should be 1.0 (no overlap) + bonus
        assert comp > 0.8

        # Now test with overlapping knowledge: complementarity should be lower
        node_c = _make_node(
            "c",
            perspective="技术",
            knowledge_base="Python, 算法, 数据结构, 机器学习, 深度学习",
            capabilities=["coding"],
        )
        comp_overlap = engine._knowledge_complementarity(node_a, node_c)
        # Same knowledge base -> Jaccard distance = 0, only bonus remains
        assert comp_overlap < comp

    def test_dialogue_depth_grows(self):
        """验证对话深度随重复对话增加"""
        node_a = _make_node(
            "alice", name="Alice",
            perspective="逻辑",
            knowledge_base="数学, 围棋",
            capabilities=["reasoning"],
        )
        node_b = _make_node(
            "bob", name="Bob",
            perspective="直觉",
            knowledge_base="艺术, 设计",
            capabilities=["design"],
        )
        engine = DialogueEngine()

        # First dialogue: depth should be 1.0
        depth_0 = engine._dialogue_depth("alice", "bob")
        assert depth_0 == 1.0

        # Run a dialogue
        engine.dialogue(node_a, node_b, trigger="test1")
        depth_1 = engine._dialogue_depth("alice", "bob")
        assert depth_1 > depth_0

        # Run more dialogues
        engine.dialogue(node_a, node_b, trigger="test2")
        engine.dialogue(node_a, node_b, trigger="test3")
        depth_3 = engine._dialogue_depth("alice", "bob")
        assert depth_3 > depth_1

        # Depth should be capped at 1.3
        assert depth_3 <= 1.3

    def test_cross_domain_insights(self):
        """验证跨域洞察生成"""
        node_a = _make_node(
            "go_player", name="棋手",
            perspective="围棋策略",
            knowledge_base="围棋, 死活题, 定式, 布局",
            capabilities=["reasoning", "pattern_recognition"],
        )
        node_b = _make_node(
            "designer", name="设计师",
            perspective="视觉设计",
            knowledge_base="排版, 色彩, 构图, 交互",
            capabilities=["design", "pattern_recognition"],
        )
        engine = DialogueEngine()
        result = engine.dialogue(node_a, node_b, trigger="cross-domain test")

        assert isinstance(result, DialogueResult)
        # Should have cross-domain insights because nodes have unique domains
        assert len(result.cross_domain_insights) > 0
        # At least one insight should mention cross-domain
        insight_texts = " ".join(result.cross_domain_insights)
        assert "跨域" in insight_texts or "互补" in insight_texts or "协作" in insight_texts

    def test_emergence_score_range(self):
        """验证涌现值始终在 [0, 1] 范围内"""
        node_a = _make_node(
            "a", name="A",
            perspective="完全不同视角一",
            knowledge_base="领域甲, 知识甲",
            capabilities=["x"],
        )
        node_b = _make_node(
            "b", name="B",
            perspective="完全不同视角二",
            knowledge_base="领域乙, 知识乙",
            capabilities=["y"],
        )
        engine = DialogueEngine()
        result = engine.dialogue(node_a, node_b, trigger="range test")
        assert 0.0 <= result.emergence_score <= 1.0


# ===========================================================================
# TestLearningCoordinator
# ===========================================================================

class TestLearningCoordinator:
    """学习协调器测试"""

    def test_run_training_round(self, tmp_path):
        """基本训练轮次: 返回包含 assessment, plan, progress 的结果"""
        coord = LearningCoordinator(data_dir=str(tmp_path))
        result = coord.run_training_round(
            node_id="xiaochen",
            domain="go",
            training_records=_STANDARD_RECORDS,
        )

        assert isinstance(result, TrainingRoundResult)
        assert result.node_id == "xiaochen"
        assert result.domain == "go"
        assert result.round_number == 1
        assert result.assessment_result is not None
        assert result.next_plan is not None
        assert result.progress_report is not None

    def test_first_round_progress_stable(self, tmp_path):
        """第一轮: deltas 全为 0, trend 为 stable"""
        coord = LearningCoordinator(data_dir=str(tmp_path))
        result = coord.run_training_round(
            node_id="alice",
            domain="go",
            training_records=_STANDARD_RECORDS,
        )

        progress = result.progress_report
        assert isinstance(progress, ProgressReport)
        assert progress.trend == "stable"
        assert progress.overall_improvement == 0.0
        # All dimension deltas should be 0.0
        for dim in DIMENSION_REGISTRY:
            assert progress.dimension_deltas[dim] == 0.0

    def test_second_round_shows_progress(self, tmp_path):
        """第二轮训练后, deltas 非零"""
        coord = LearningCoordinator(data_dir=str(tmp_path))

        # Round 1 with standard records
        coord.run_training_round(
            node_id="bob",
            domain="go",
            training_records=_STANDARD_RECORDS,
        )

        # Round 2 with high records - should show improvement
        result2 = coord.run_training_round(
            node_id="bob",
            domain="go",
            training_records=_HIGH_RECORDS,
        )

        progress = result2.progress_report
        assert result2.round_number == 2
        # At least some deltas should be positive (improvement)
        positive_deltas = [v for v in progress.dimension_deltas.values() if v > 0]
        assert len(positive_deltas) > 0, "Expected some positive deltas after improvement"
        assert progress.overall_improvement > 0

    def test_adaptive_plan_focuses_weak(self, tmp_path):
        """自适应计划聚焦最弱的3个维度"""
        coord = LearningCoordinator(data_dir=str(tmp_path))

        # Use records that produce varied scores (some dims high, some low)
        records = [
            {
                "task_completion": 0.90,       # understanding -> high
                "output_quality": 0.85,         # execution -> high
                "reasoning_accuracy": 0.20,     # reasoning -> low
                "retrieval_accuracy": 0.15,     # retrieval -> low
                "improvement_rate": 0.25,       # reflection -> low
                "tool_usage_accuracy": 0.80,    # tooling -> high
                "dialogue_quality": 0.88,       # eq -> high
                "memory_retention": 0.10,       # memory -> very low
            },
        ]
        result = coord.run_training_round(
            node_id="charlie",
            domain="go",
            training_records=records,
        )

        plan = result.next_plan
        assert isinstance(plan, TrainingPlan)
        assert len(plan.focus_dimensions) == 3

        # The focused dimensions should be the weakest ones
        profile = result.assessment_result.profile
        sorted_dims = sorted(profile.scores.items(), key=lambda kv: kv[1])
        expected_bottom_3 = [d for d, _ in sorted_dims[:3]]
        assert plan.focus_dimensions == expected_bottom_3

    def test_adaptive_plan_difficulty(self, tmp_path):
        """计划难度匹配分数区间"""
        coord = LearningCoordinator(data_dir=str(tmp_path))

        # Low scores -> difficulty should be "easy"
        result_low = coord.run_training_round(
            node_id="low_node",
            domain="go",
            training_records=_LOW_RECORDS,
        )
        assert result_low.next_plan.difficulty == "easy"

        # High scores -> difficulty should be "hard"
        result_high = coord.run_training_round(
            node_id="high_node",
            domain="go",
            training_records=_HIGH_RECORDS,
        )
        assert result_high.next_plan.difficulty == "hard"

    def test_learning_state_updates(self, tmp_path):
        """学习状态正确更新: total_rounds, best_scores, growth_trajectory"""
        coord = LearningCoordinator(data_dir=str(tmp_path))

        # Run 3 rounds
        coord.run_training_round("dave", "go", _STANDARD_RECORDS)
        coord.run_training_round("dave", "go", _HIGH_RECORDS)
        coord.run_training_round("dave", "go", _STANDARD_RECORDS)

        state = coord.get_learning_state("dave")
        assert isinstance(state, LearningState)
        assert state.total_rounds == 3
        assert len(state.growth_trajectory) == 3
        assert state.current_plan is not None

        # best_scores should have entries for all 8 dimensions
        assert len(state.best_scores) == len(DIMENSION_REGISTRY)
        # Best scores should be at least as high as the high-records scores
        for dim in DIMENSION_REGISTRY:
            assert state.best_scores[dim] > 0.0

    def test_collaboration_suggestion(self, tmp_path):
        """互补能力画像产生协作建议"""
        coord = LearningCoordinator(data_dir=str(tmp_path))

        # Node A: strong in reasoning/execution, weak in eq/memory
        scores_a = {d: 0.8 for d in DIMENSION_REGISTRY}
        scores_a["eq"] = 0.2
        scores_a["memory"] = 0.15
        profile_a = DimensionProfile(node_id="node_a", domain="go", scores=scores_a)

        # Node B: strong in eq/memory, weak in reasoning/execution
        scores_b = {d: 0.2 for d in DIMENSION_REGISTRY}
        scores_b["eq"] = 0.85
        scores_b["memory"] = 0.90
        profile_b = DimensionProfile(node_id="node_b", domain="go", scores=scores_b)

        suggestions = coord.suggest_collaboration({
            "node_a": profile_a,
            "node_b": profile_b,
        })

        assert len(suggestions) > 0
        assert isinstance(suggestions[0], CollaborationSuggestion)
        assert suggestions[0].expected_benefit_score > 0.0
        # Both nodes should appear in the suggestion
        pair = {suggestions[0].node_a_id, suggestions[0].node_b_id}
        assert pair == {"node_a", "node_b"}

    def test_no_collaboration_when_similar(self, tmp_path):
        """相似能力画像不产生协作建议"""
        coord = LearningCoordinator(data_dir=str(tmp_path))

        # Two nodes with very similar profiles (all moderate scores)
        scores = {d: 0.55 for d in DIMENSION_REGISTRY}
        profile_a = DimensionProfile(node_id="twin_a", domain="go", scores=scores)
        profile_b = DimensionProfile(node_id="twin_b", domain="go", scores=dict(scores))

        suggestions = coord.suggest_collaboration({
            "twin_a": profile_a,
            "twin_b": profile_b,
        })

        # Neither node is strong (>0.6) where the other is weak (<0.4),
        # so no complementary dimensions exist.
        assert len(suggestions) == 0


# ===========================================================================
# TestHTTPTransport
# ===========================================================================

class TestHTTPTransport:
    """HTTP传输层测试"""

    @pytest.fixture()
    def transport(self):
        """Create an HTTPTransport with a free port, start it, yield, stop."""
        port = _find_free_port()
        t = HTTPTransport(base_url=f"http://127.0.0.1:{port}", port=port)
        t.start_server("127.0.0.1", port)
        # Give the server a moment to bind
        time.sleep(0.1)
        yield t
        t.stop_server()

    @pytest.fixture()
    def second_transport(self):
        """Create a second HTTPTransport on a different port."""
        port = _find_free_port()
        t = HTTPTransport(base_url=f"http://127.0.0.1:{port}", port=port)
        t.start_server("127.0.0.1", port)
        time.sleep(0.1)
        yield t
        t.stop_server()

    def test_start_stop_server(self):
        """服务器正常启停"""
        port = _find_free_port()
        t = HTTPTransport(port=port)
        assert not t.is_running

        t.start_server("127.0.0.1", port)
        time.sleep(0.1)
        assert t.is_running

        t.stop_server()
        assert not t.is_running

    def test_send_receive_message(self, transport):
        """发送消息并通过本地存储接收"""
        url = transport.base_url
        msg = {"from_node": "alice", "to_node": "bob", "payload": "hello"}

        ok = transport.send_message(url, msg)
        assert ok is True

        # Receive via local store
        messages = transport.receive_messages("bob")
        assert len(messages) == 1
        assert messages[0]["from_node"] == "alice"
        assert messages[0]["payload"] == "hello"

        # After draining, should be empty
        messages_again = transport.receive_messages("bob")
        assert len(messages_again) == 0

    def test_heartbeat(self, transport):
        """心跳端点返回 ok"""
        result = transport.heartbeat(transport.base_url)
        assert result["status"] == "ok"
        assert "timestamp" in result

    def test_discover_nodes(self, transport):
        """注册节点后可通过 /registry/nodes 发现"""
        transport.register_node({"node_id": "node_1", "name": "Alice"})
        transport.register_node({"node_id": "node_2", "name": "Bob"})

        nodes = transport.discover_nodes(transport.base_url)
        assert isinstance(nodes, list)
        assert len(nodes) == 2
        node_ids = {n["node_id"] for n in nodes}
        assert node_ids == {"node_1", "node_2"}

    def test_sync_registry(self, transport, second_transport):
        """同步节点注册表: 推送本地节点到远程并合并"""
        # Register a node on the first transport (acts as central registry)
        transport.register_node({"node_id": "central_node", "name": "Central"})

        # Sync from the second transport to the first
        local_nodes = [{"node_id": "remote_node", "name": "Remote"}]
        result = second_transport.sync_registry(local_nodes, transport.base_url)

        assert result.get("status") == "synced"
        assert result.get("total", 0) >= 2

        # The central registry should now have both nodes
        all_nodes = transport.discover_nodes(transport.base_url)
        node_ids = {n["node_id"] for n in all_nodes}
        assert "central_node" in node_ids
        assert "remote_node" in node_ids

    def test_pending_count(self, transport):
        """消息计数正确"""
        url = transport.base_url

        assert transport.pending_count() == 0
        assert transport.pending_count("bob") == 0

        transport.send_message(url, {"from_node": "a", "to_node": "bob", "payload": "msg1"})
        transport.send_message(url, {"from_node": "a", "to_node": "bob", "payload": "msg2"})
        transport.send_message(url, {"from_node": "a", "to_node": "carol", "payload": "msg3"})

        assert transport.pending_count("bob") == 2
        assert transport.pending_count("carol") == 1
        assert transport.pending_count() == 3

    def test_send_to_offline(self):
        """发送到不存在的服务器返回 False"""
        t = HTTPTransport()
        # Use a port that is almost certainly not listening
        offline_port = _find_free_port()
        offline_url = f"http://127.0.0.1:{offline_port}"
        ok = t.send_message(offline_url, {"from_node": "x", "to_node": "y", "payload": "test"})
        assert ok is False

    def test_is_running_property(self):
        """is_running 属性正确反映服务器状态"""
        port = _find_free_port()
        t = HTTPTransport(port=port)

        assert t.is_running is False

        t.start_server("127.0.0.1", port)
        time.sleep(0.1)
        assert t.is_running is True

        # Starting again should be a no-op
        t.start_server("127.0.0.1", port)
        assert t.is_running is True

        t.stop_server()
        assert t.is_running is False

        # Stopping again should be safe
        t.stop_server()
        assert t.is_running is False

    def test_receive_via_http_get(self, transport):
        """通过 HTTP GET 也可以读取消息 (不排空)"""
        url = transport.base_url
        msg = {"from_node": "alice", "to_node": "dave", "payload": "http-get-test"}
        transport.send_message(url, msg)

        # Use urlopen directly to test GET /messages/{node_id}
        from urllib.request import urlopen
        import json

        resp = urlopen(f"{url}/messages/dave", timeout=5)
        data = json.loads(resp.read().decode("utf-8"))
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["payload"] == "http-get-test"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
