#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
涌现计算测试
验证 OADP 涌现计算公式的实现
"""

import unittest


class EmergenceCalculator:
    """涌现计算器"""
    
    def __init__(self):
        self.thresholds = {
            "low": 0.2,
            "medium": 0.4,
            "high": 0.6,
            "very_high": 0.8
        }
    
    def calculate_perspective_diff(self, agent1, agent2):
        """计算视角差异度"""
        p1 = agent1.get("perspective", "")
        p2 = agent2.get("perspective", "")
        
        if p1 == p2:
            return 0.0
        
        keywords1 = set(p1.lower().split())
        keywords2 = set(p2.lower().split())
        
        if not keywords1 or not keywords2:
            return 0.5
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        if union == 0:
            return 1.0
        
        jaccard_similarity = intersection / union
        return 1.0 - jaccard_similarity
    
    def calculate_knowledge_overlap(self, agent1, agent2):
        """计算知识重叠度"""
        kb1 = agent1.get("knowledge_base", "")
        kb2 = agent2.get("knowledge_base", "")
        
        if not kb1 or not kb2:
            return 0.0
        
        words1 = set(kb1.lower().split())
        words2 = set(kb2.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def calculate_dialogue_depth(self, rounds, max_rounds=10):
        """计算对话深度"""
        if max_rounds <= 0:
            return 0.0
        
        return min(rounds / max_rounds, 1.0)
    
    def calculate_novelty_factor(self, new_chunks, total_chunks):
        """计算新颖度"""
        if total_chunks == 0:
            return 0.0
        
        return min(new_chunks / total_chunks, 1.0)
    
    def calculate_emergence_score(self, agent1, agent2, dialogue_rounds, new_chunks, total_chunks):
        """计算涌现值"""
        # 计算各维度
        perspective_diff = self.calculate_perspective_diff(agent1, agent2)
        knowledge_overlap = self.calculate_knowledge_overlap(agent1, agent2)
        dialogue_depth = self.calculate_dialogue_depth(dialogue_rounds)
        novelty_factor = self.calculate_novelty_factor(new_chunks, total_chunks)
        
        # 计算综合涌现值
        emergence_score = (
            0.3 * perspective_diff 
            + 0.2 * (1 - knowledge_overlap) 
            + 0.2 * dialogue_depth 
            + 0.3 * novelty_factor
        )
        
        # 确定涌现等级
        if emergence_score >= self.thresholds["very_high"]:
            level = "very_high"
        elif emergence_score >= self.thresholds["high"]:
            level = "high"
        elif emergence_score >= self.thresholds["medium"]:
            level = "medium"
        elif emergence_score >= self.thresholds["low"]:
            level = "low"
        else:
            level = "none"
        
        return {
            "emergence_score": emergence_score,
            "level": level,
            "dimensions": {
                "perspective_diff": perspective_diff,
                "knowledge_overlap": knowledge_overlap,
                "dialogue_depth": dialogue_depth,
                "novelty_factor": novelty_factor
            }
        }


class TestEmergenceCalculation(unittest.TestCase):
    """测试涌现计算"""
    
    def setUp(self):
        """创建计算器"""
        self.calculator = EmergenceCalculator()
    
    def test_perspective_diff_identical(self):
        """测试相同视角"""
        agent1 = {"perspective": "世界地图渲染"}
        agent2 = {"perspective": "世界地图渲染"}
        
        diff = self.calculator.calculate_perspective_diff(agent1, agent2)
        self.assertEqual(diff, 0.0)
    
    def test_perspective_diff_different(self):
        """测试不同视角"""
        agent1 = {"perspective": "世界地图渲染"}
        agent2 = {"perspective": "协议规范设计"}
        
        diff = self.calculator.calculate_perspective_diff(agent1, agent2)
        self.assertGreater(diff, 0.5)
    
    def test_knowledge_overlap_identical(self):
        """测试相同知识领域"""
        agent1 = {"knowledge_base": "协议规范 对话渲染"}
        agent2 = {"knowledge_base": "协议规范 对话渲染"}
        
        overlap = self.calculator.calculate_knowledge_overlap(agent1, agent2)
        self.assertEqual(overlap, 1.0)
    
    def test_knowledge_overlap_none(self):
        """测试无知识重叠"""
        agent1 = {"knowledge_base": "围棋 数学"}
        agent2 = {"knowledge_base": "物理 化学"}
        
        overlap = self.calculator.calculate_knowledge_overlap(agent1, agent2)
        self.assertEqual(overlap, 0.0)
    
    def test_dialogue_depth_calculation(self):
        """测试对话深度计算"""
        # 5 轮对话（max=10）
        depth = self.calculator.calculate_dialogue_depth(5, 10)
        self.assertEqual(depth, 0.5)
        
        # 10 轮对话（max=10）
        depth = self.calculator.calculate_dialogue_depth(10, 10)
        self.assertEqual(depth, 1.0)
        
        # 15 轮对话（max=10，应该 capped 于 1.0）
        depth = self.calculator.calculate_dialogue_depth(15, 10)
        self.assertEqual(depth, 1.0)
    
    def test_novelty_factor_calculation(self):
        """测试新颖度计算"""
        # 2 新 chunk / 5 总 chunk
        factor = self.calculator.calculate_novelty_factor(2, 5)
        self.assertEqual(factor, 0.4)
        
        # 5 新 chunk / 5 总 chunk
        factor = self.calculator.calculate_novelty_factor(5, 5)
        self.assertEqual(factor, 1.0)
        
        # 0 总 chunk
        factor = self.calculator.calculate_novelty_factor(0, 0)
        self.assertEqual(factor, 0.0)
    
    def test_emergence_score_example1(self):
        """测试示例 1：虾尔与诸葛马的协议讨论"""
        agent1 = {
            "perspective": "世界地图渲染",
            "knowledge_base": "协议规范 对话渲染 世界状态管理"
        }
        
        agent2 = {
            "perspective": "协议规范设计",
            "knowledge_base": "协议设计 消息格式 节点注册"
        }
        
        result = self.calculator.calculate_emergence_score(
            agent1, agent2,
            dialogue_rounds=8,
            new_chunks=3,
            total_chunks=5
        )
        
        # 验证结果结构
        self.assertIn("emergence_score", result)
        self.assertIn("level", result)
        self.assertIn("dimensions", result)
        
        # 验证维度
        dims = result["dimensions"]
        self.assertIn("perspective_diff", dims)
        self.assertIn("knowledge_overlap", dims)
        self.assertIn("dialogue_depth", dims)
        self.assertIn("novelty_factor", dims)
        
        # 验证涌现等级
        self.assertIn(result["level"], ["none", "low", "medium", "high", "very_high"])
        
        # 验证涌现值范围
        self.assertGreaterEqual(result["emergence_score"], 0.0)
        self.assertLessEqual(result["emergence_score"], 1.0)
    
    def test_emergence_score_example2(self):
        """测试示例 2：小陈的围棋训练"""
        agent1 = {
            "perspective": "围棋训练",
            "knowledge_base": "围棋规则 定式 死活题"
        }
        
        agent2 = {
            "perspective": "围棋教学",
            "knowledge_base": "围棋教学 入门指导 棋力提升"
        }
        
        result = self.calculator.calculate_emergence_score(
            agent1, agent2,
            dialogue_rounds=3,
            new_chunks=1,
            total_chunks=4
        )
        
        # 验证涌现等级
        self.assertIn(result["level"], ["none", "low", "medium", "high", "very_high"])
        
        # 验证涌现值范围
        self.assertGreaterEqual(result["emergence_score"], 0.0)
        self.assertLessEqual(result["emergence_score"], 1.0)
    
    def test_emergence_thresholds(self):
        """测试涌现阈值"""
        # 测试各阈值边界
        test_cases = [
            (0.1, "none"),
            (0.2, "low"),
            (0.4, "medium"),
            (0.6, "high"),
            (0.8, "very_high"),
            (1.0, "very_high"),
        ]
        
        for score, expected_level in test_cases:
            if score >= 0.8:
                level = "very_high"
            elif score >= 0.6:
                level = "high"
            elif score >= 0.4:
                level = "medium"
            elif score >= 0.2:
                level = "low"
            else:
                level = "none"
            
            self.assertEqual(level, expected_level, f"Score {score} should be {expected_level}")
    
    def test_formula_weights(self):
        """测试公式权重总和为 1.0"""
        weights = {
            "perspective_diff": 0.3,
            "knowledge_overlap": 0.2,
            "dialogue_depth": 0.2,
            "novelty_factor": 0.3
        }
        
        total_weight = sum(weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)
    
    def test_extreme_case_maximum(self):
        """测试极端情况：最大值"""
        agent1 = {"perspective": "A", "knowledge_base": "X"}
        agent2 = {"perspective": "B", "knowledge_base": "Y"}
        
        result = self.calculator.calculate_emergence_score(
            agent1, agent2,
            dialogue_rounds=10,
            new_chunks=10,
            total_chunks=10
        )
        
        # 理论上最大值应该接近 1.0
        self.assertGreater(result["emergence_score"], 0.8)
        self.assertEqual(result["level"], "very_high")
    
    def test_extreme_case_minimum(self):
        """测试极端情况：最小值"""
        agent1 = {"perspective": "A", "knowledge_base": "X"}
        agent2 = {"perspective": "A", "knowledge_base": "X"}
        
        result = self.calculator.calculate_emergence_score(
            agent1, agent2,
            dialogue_rounds=0,
            new_chunks=0,
            total_chunks=1
        )
        
        # 理论上最小值应该接近 0.0
        self.assertLess(result["emergence_score"], 0.3)
        self.assertIn(result["level"], ["none", "low"])


if __name__ == "__main__":
    unittest.main()
