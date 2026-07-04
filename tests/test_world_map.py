#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
世界地图引擎单元测试
"""

import json
import os
import tempfile
import shutil
import unittest
from pathlib import Path

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.world_map import WorldMap, WorldMapManager


class TestWorldMap(unittest.TestCase):
    """世界地图核心功能测试"""

    def setUp(self):
        """创建临时存储目录"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="test-wm", storage_dir=self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_empty_map(self):
        """测试初始化空地图"""
        m = self.wm.get_world_map()
        self.assertEqual(m["world_map_id"], "test-wm")
        self.assertEqual(m["version"], 1)
        self.assertEqual(m["total_chunks"], 0)
        self.assertEqual(m["total_treasures"], 0)
        self.assertIn("go", m["domains"])
        self.assertIn("poster", m["domains"])

    def test_add_chunk(self):
        """测试添加知识碎片"""
        chunk_data = {
            "chunk_id": "test_chunk_001",
            "domain": "go",
            "title": "测试知识碎片",
            "description": "这是一个测试用的知识碎片",
            "tags": ["go", "test"],
            "data": {"key": "value"},
        }
        result = self.wm.add_chunk(chunk_data, "test_agent")

        self.assertEqual(result["chunk_id"], "test_chunk_001")
        self.assertEqual(result["domain"], "go")
        self.assertEqual(result["contributor"], "test_agent")
        self.assertIn("content_hash", result)
        self.assertIn("created_at", result)

        # 验证持久化
        m = self.wm.get_world_map()
        self.assertEqual(m["total_chunks"], 1)
        self.assertIn("test_chunk_001", m["chunks"])

    def test_add_duplicate_chunk(self):
        """测试添加重复知识碎片"""
        chunk_data = {
            "chunk_id": "dup_chunk",
            "domain": "go",
            "title": "重复测试",
        }
        self.wm.add_chunk(chunk_data, "agent1")

        with self.assertRaises(ValueError) as ctx:
            self.wm.add_chunk(chunk_data, "agent2")
        self.assertIn("already exists", str(ctx.exception))

    def test_update_chunk(self):
        """测试更新知识碎片"""
        chunk_data = {
            "chunk_id": "update_test",
            "domain": "go",
            "title": "原始标题",
            "description": "原始描述",
        }
        self.wm.add_chunk(chunk_data, "agent1")

        # 贡献者更新
        result = self.wm.update_chunk("update_test", {"title": "新标题"}, "agent1")
        self.assertEqual(result["title"], "新标题")

        # 非贡献者更新（应拒绝）
        with self.assertRaises(PermissionError):
            self.wm.update_chunk("update_test", {"title": "被黑"}, "agent2")

        # 管理员更新（应允许）
        result = self.wm.update_chunk("update_test", {"title": "管理员修改"}, "admin")
        self.assertEqual(result["title"], "管理员修改")

    def test_remove_chunk(self):
        """测试移除知识碎片"""
        chunk_data = {
            "chunk_id": "remove_test",
            "domain": "go",
            "title": "删除测试",
        }
        self.wm.add_chunk(chunk_data, "agent1")

        # 非管理员删除（应拒绝）
        with self.assertRaises(PermissionError):
            self.wm.remove_chunk("remove_test", "agent1")

        # 管理员删除
        result = self.wm.remove_chunk("remove_test", "admin")
        self.assertTrue(result)

        m = self.wm.get_world_map()
        self.assertEqual(m["total_chunks"], 0)

    def test_search_chunks(self):
        """测试搜索知识碎片"""
        # 添加多个碎片
        self.wm.add_chunk({"chunk_id": "c1", "domain": "go", "title": "围棋基础", "tags": ["go", "basics"]}, "agent1")
        self.wm.add_chunk({"chunk_id": "c2", "domain": "poster", "title": "海报设计", "tags": ["poster", "design"]}, "agent2")
        self.wm.add_chunk({"chunk_id": "c3", "domain": "go", "title": "围棋高级", "tags": ["go", "advanced"]}, "agent3")

        # 按域名搜索
        go_chunks = self.wm.search_chunks(domain="go")
        self.assertEqual(len(go_chunks), 2)

        # 按标签搜索
        basics = self.wm.search_chunks(tags=["basics"])
        self.assertEqual(len(basics), 1)
        self.assertEqual(basics[0]["chunk_id"], "c1")

        # 按关键词搜索
        results = self.wm.search_chunks(query="基础")
        self.assertEqual(len(results), 1)

        # 全搜索
        all_chunks = self.wm.search_chunks()
        self.assertEqual(len(all_chunks), 3)

    def test_unlock_treasure(self):
        """测试解锁宝藏"""
        treasure_data = {
            "treasure_id": "t001",
            "title": "首次跨域迁移",
            "description": "围棋思维 → 海报设计",
            "rarity": "rare",
            "insight": "大局观应用于布局",
        }
        result = self.wm.unlock_treasure(treasure_data, ["agent1", "agent2"])

        self.assertEqual(result["treasure_id"], "t001")
        self.assertEqual(result["rarity"], "rare")
        self.assertEqual(result["verification_status"], "unlocked")

        m = self.wm.get_world_map()
        self.assertEqual(m["total_treasures"], 1)

    def test_verify_treasure(self):
        """测试验证宝藏"""
        treasure_data = {
            "treasure_id": "t002",
            "title": "测试宝藏",
        }
        self.wm.unlock_treasure(treasure_data, ["agent1"])

        result = self.wm.verify_treasure("t002", "admin")
        self.assertEqual(result["verification_status"], "verified")
        self.assertIn("verified_at", result)

    def test_register_agent(self):
        """测试注册智能体"""
        self.wm.register_agent("agent1")
        self.wm.register_agent("agent2")
        self.wm.register_agent("agent1")  # 重复注册

        agents = self.wm.get_active_agents()
        self.assertEqual(len(agents), 2)
        self.assertIn("agent1", agents)
        self.assertIn("agent2", agents)

    def test_update_log(self):
        """测试更新日志"""
        self.wm.add_chunk({"chunk_id": "log_test", "domain": "go", "title": "日志测试"}, "agent1")
        self.wm.unlock_treasure({"treasure_id": "t_log", "title": "日志宝藏"}, ["agent1"])

        log = self.wm.get_update_log()
        self.assertGreaterEqual(len(log), 2)

        # 检查日志格式
        entry = log[0]
        self.assertIn("update_id", entry)
        self.assertIn("type", entry)
        self.assertIn("timestamp", entry)
        self.assertIn("agent", entry)

    def test_persistence(self):
        """测试持久化（重新加载）"""
        self.wm.add_chunk({"chunk_id": "persist_test", "domain": "go", "title": "持久化测试"}, "agent1")

        # 重新加载
        wm2 = WorldMap(map_id="test-wm", storage_dir=self.test_dir)
        m = wm2.get_world_map()
        self.assertEqual(m["total_chunks"], 1)
        self.assertIn("persist_test", m["chunks"])


class TestWorldMapManager(unittest.TestCase):
    """世界地图管理员测试"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="mgr-test", storage_dir=self.test_dir)
        self.manager = WorldMapManager(self.wm)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_safe_add_chunk(self):
        """测试安全添加"""
        chunk_data = {
            "chunk_id": "safe_test",
            "domain": "go",
            "title": "安全测试",
        }
        result = self.manager.safe_add_chunk(chunk_data, "agent1")
        self.assertEqual(result["chunk_id"], "safe_test")

    def test_safe_update_chunk(self):
        """测试安全更新"""
        self.wm.add_chunk({"chunk_id": "safe_update", "domain": "go", "title": "原始"}, "agent1")
        result = self.manager.safe_update_chunk("safe_update", {"title": "更新"}, "agent1")
        self.assertEqual(result["title"], "更新")


if __name__ == "__main__":
    unittest.main()
