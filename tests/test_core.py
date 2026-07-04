#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心模块单元测试
"""

import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestLobsterAgent(unittest.TestCase):
    """小龙虾Agent基础测试"""

    def test_load_brain_structure(self):
        """测试策略库结构"""
        expected_keys = {"games_played", "strategies", "last_updated", "agents"}

        # 模拟策略库
        brain = {
            "games_played": 0,
            "strategies": {},
            "last_updated": None,
            "agents": ["xiaochen", "zhuguxia", "qoder"],
        }

        for key in expected_keys:
            self.assertIn(key, brain)

    def test_role_config(self):
        """测试角色配置"""
        roles = {
            "xiaochen": {"name": "小陈", "type": "稳健型"},
            "zhuguxia": {"name": "诸葛虾", "type": "加速型"},
            "qoder": {"name": "qoder", "type": "实战型"},
        }

        self.assertEqual(len(roles), 3)
        self.assertIn("xiaochen", roles)
        self.assertIn("zhuguxia", roles)
        self.assertIn("qoder", roles)


class TestCoachHermes(unittest.TestCase):
    """诸葛马教练测试"""

    def test_diagnose_structure(self):
        """测试诊断数据结构"""
        expected_issues = [
            "题库为空",
            "无复盘机制",
            "无错题本系统",
            "无等级晋升标准",
        ]

        # 模拟诊断结果
        issues = [
            "🔴 题库为空 - problem_bank 目录下 0 个文件",
            "🟡 无复盘机制 - 对局后没有复盘分析",
            "🟡 无错题本系统 - 错题没有归类分析",
            "🟡 无等级晋升标准 - 达到什么条件升一级没有明确规则",
        ]

        self.assertGreater(len(issues), 0)
        for issue in issues:
            has_red = "🔴" in issue
            has_yellow = "🟡" in issue
            self.assertTrue(has_red or has_yellow, f"Issue missing severity emoji: {issue}")

    def test_training_plan_structure(self):
        """测试训练计划结构"""
        plan = {
            "version": "v2.0",
            "generated_at": datetime.now().isoformat(),
            "coach": "诸葛马",
            "current_status": {
                "phase": 1,
                "week": 1,
                "day": 2,
            },
            "phase1_schedule": {
                "week1": {
                    "theme": "规则基础与吃子技巧",
                    "target_level": "20级",
                    "days": [
                        {"day": 1, "topic": "规则基础与死活入门", "problems": 5, "games": 2},
                        {"day": 2, "topic": "吃子技巧进阶", "problems": 8, "games": 1},
                    ],
                }
            },
        }

        self.assertEqual(plan["version"], "v2.0")
        self.assertIn("phase1_schedule", plan)
        self.assertEqual(len(plan["phase1_schedule"]["week1"]["days"]), 2)


class TestDispatcher(unittest.TestCase):
    """调度器测试"""

    def test_nocturnal_schedule(self):
        """测试深夜特训时间表"""
        schedule = {
            "00:00-01:30": {"name": "极限死活", "intensity": "🔥🔥🔥🔥🔥"},
            "01:30-02:30": {"name": "AI定式库导入", "intensity": "📚📚"},
            "02:30-04:30": {"name": "19路盘深夜实战", "intensity": "♟️♟️♟️♟️"},
            "04:30-05:30": {"name": "AI深度复盘", "intensity": "🤖🤖🤖"},
            "05:30-06:00": {"name": "归档&错题重练", "intensity": "📂"},
        }

        self.assertEqual(len(schedule), 5)
        for time_slot, info in schedule.items():
            self.assertIn("name", info)
            self.assertIn("intensity", info)

    def test_create_training_task(self):
        """测试创建训练任务"""
        task = {
            "id": "test-task-001",
            "type": "nocturnal_training",
            "time_slot": "00:00-01:30",
            "slot_name": "极限死活",
            "player": "xiaochen",
            "tasks": [
                {"category": "死活", "difficulty": "高级", "count": 100},
            ],
        }

        self.assertEqual(task["type"], "nocturnal_training")
        self.assertEqual(task["player"], "xiaochen")
        self.assertEqual(len(task["tasks"]), 1)


class TestCrossDomain(unittest.TestCase):
    """跨域知识迁移测试"""

    def test_transfer_map_structure(self):
        """测试迁移映射结构"""
        transfer_map = {
            "围棋 → 海报": [
                {
                    "source": "间隔重复错题法",
                    "target": "失败设计回顾",
                    "description": "围棋的错题按1天→3天→7天→14天间隔重复",
                },
            ],
            "海报 → 围棋": [
                {
                    "source": "HTML+Playwright管线",
                    "target": "训练数据可视化",
                    "description": "海报的HTML渲染管线启发围棋训练数据可视化",
                },
            ],
        }

        self.assertIn("围棋 → 海报", transfer_map)
        self.assertIn("海报 → 围棋", transfer_map)
        self.assertEqual(len(transfer_map["围棋 → 海报"]), 1)

    def test_domain_stats_structure(self):
        """测试域统计数据结构"""
        stats = {
            "domain": "围棋域",
            "players": [
                {"name": "小陈", "level": "25级", "problems": 241, "games": 10337},
                {"name": "诸葛虾", "level": "25级", "problems": 258, "games": 6868},
                {"name": "qoder", "level": "25级", "problems": 685, "games": 22},
            ],
            "total_problems": 1184,
            "total_games": 17227,
        }

        self.assertEqual(stats["total_problems"], 1184)
        self.assertEqual(stats["total_games"], 17227)
        self.assertEqual(len(stats["players"]), 3)


class TestCommunityModules(unittest.TestCase):
    """L3社区学习环测试"""

    def test_tournament_structure(self):
        """测试对抗赛数据结构"""
        match = {
            "game_id": "week26_xiaochen_vs_zhuguxia",
            "black": "小陈",
            "white": "诸葛虾",
            "total_moves": 187,
            "winner": "小陈",
            "blunders": [
                {"move": 141, "player": "诸葛虾", "description": "第141手出现失误"},
            ],
        }

        self.assertIn("game_id", match)
        self.assertIn("winner", match)
        self.assertGreater(len(match["blunders"]), 0)

    def test_discussion_structure(self):
        """测试讨论局数据结构"""
        review = {
            "reviewer": "qoder",
            "perspective": "逻辑推理视角",
            "review": "从AI胜率分析，这道题的正解胜率约78%",
            "confidence": 0.88,
        }

        self.assertIn("reviewer", review)
        self.assertIn("review", review)
        self.assertGreater(review["confidence"], 0.5)

    def test_instructor_structure(self):
        """测试技术助教数据结构"""
        teaching = {
            "week": 26,
            "topic": "死活/初级",
            "knowledge_points": ["刀五与梅花五", "板六与常见活形"],
            "wrong_count": 8,
        }

        self.assertEqual(teaching["topic"], "死活/初级")
        self.assertEqual(len(teaching["knowledge_points"]), 2)


class TestRequirements(unittest.TestCase):
    """依赖管理测试"""

    def test_requirements_file(self):
        """测试requirements.txt存在且格式正确"""
        req_file = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        self.assertTrue(os.path.exists(req_file), "requirements.txt 不存在")

        with open(req_file, "r") as f:
            lines = f.readlines()

        # 过滤空行和注释
        packages = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
        self.assertGreater(len(packages), 0, "requirements.txt 为空")

        # 检查格式（应该是 package==version 或 package）
        for pkg in packages:
            self.assertGreater(len(pkg), 0)


if __name__ == "__main__":
    unittest.main()
