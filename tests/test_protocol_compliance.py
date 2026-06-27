#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OADP 协议合规性测试
验证 world_map.py 实现符合 OADP 协议规范
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

from engine.world_map import WorldMap, WorldMapManager


class TestOADPCompliance(unittest.TestCase):
    """测试 OADP 协议合规性"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="wm-001", storage_dir=self.test_dir)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_world_map_structure(self):
        """测试世界地图结构符合协议"""
        m = self.wm.get_world_map()
        
        # 协议要求的字段
        required_fields = [
            "world_map_id",
            "version",
            "total_chunks",
            "total_treasures",
            "active_agents",
            "domains",
            "chunks",
            "treasures",
        ]
        
        for field in required_fields:
            self.assertIn(field, m, f"缺少协议要求字段：{field}")
    
    def test_chunk_structure(self):
        """测试 chunk 结构符合协议"""
        chunk_data = {
            "chunk_id": "test_chunk_001",
            "domain": "protocol",
            "title": "协议合规测试",
            "description": "测试 chunk 结构",
            "tags": ["protocol", "test"],
        }
        
        chunk = self.wm.add_chunk(chunk_data, "lobster-001")
        
        # 协议要求的 chunk 字段
        required_fields = [
            "chunk_id",
            "domain",
            "title",
            "description",
            "content_hash",
            "contributor",
            "created_at",
            "updated_at",
            "tags",
        ]
        
        for field in required_fields:
            self.assertIn(field, chunk, f"chunk 缺少协议要求字段：{field}")
    
    def test_treasure_structure(self):
        """测试 treasure 结构符合协议"""
        treasure_data = {
            "treasure_id": "treasure_001",
            "title": "协议洞察",
            "description": "测试宝藏结构",
            "rarity": "rare",
            "insight": "OADP 协议需要支持多通道",
        }
        
        treasure = self.wm.unlock_treasure(treasure_data, ["lobster-001", "hermes"])
        
        # 协议要求的 treasure 字段
        required_fields = [
            "treasure_id",
            "title",
            "description",
            "rarity",
            "unlocked_by",
            "unlocked_at",
            "verification_status",
        ]
        
        for field in required_fields:
            self.assertIn(field, treasure, f"treasure 缺少协议要求字段：{field}")
    
    def test_agent_registration(self):
        """测试智能体注册符合协议"""
        # 注册智能体
        result = self.wm.register_agent("lobster-001")
        self.assertTrue(result)
        
        # 获取活跃智能体
        agents = self.wm.get_active_agents()
        self.assertIn("lobster-001", agents)
        
        # 重复注册返回 False
        result2 = self.wm.register_agent("lobster-001")
        self.assertFalse(result2)
    
    def test_domain_namespace(self):
        """测试域名空间符合协议"""
        m = self.wm.get_world_map()
        
        # 协议定义的初始域名
        expected_domains = ["go", "poster", "protocol"]
        for domain in expected_domains:
            self.assertIn(domain, m["domains"], f"缺少协议定义域名：{domain}")
    
    def test_update_log_format(self):
        """测试更新日志格式符合协议"""
        # 添加 chunk 触发日志
        chunk_data = {
            "chunk_id": "log_test_001",
            "domain": "protocol",
            "title": "日志测试",
            "description": "测试更新日志",
            "tags": ["log"],
        }
        self.wm.add_chunk(chunk_data, "lobster-001")
        
        log = self.wm.get_update_log()
        self.assertGreater(len(log), 0)
        
        # 检查日志条目格式
        entry = log[-1]
        required_fields = ["update_id", "type", "timestamp", "agent", "details"]
        for field in required_fields:
            self.assertIn(field, entry, f"日志条目缺少字段：{field}")
    
    def test_incremental_sync_protocol(self):
        """测试增量同步符合协议"""
        # 添加初始数据
        chunk_data = {
            "chunk_id": "sync_test_001",
            "domain": "protocol",
            "title": "同步测试",
            "description": "测试增量同步",
            "tags": ["sync"],
        }
        self.wm.add_chunk(chunk_data, "lobster-001")
        
        # 获取增量更新
        sync_result = self.wm.sync_incremental(since_version=0)
        
        # 协议要求的同步响应字段
        required_fields = [
            "type",
            "current_version",
            "new_chunks",
            "updated_chunks",
            "new_treasures",
            "removed_chunks",
        ]
        
        for field in required_fields:
            self.assertIn(field, sync_result, f"同步响应缺少字段：{field}")
        
        self.assertEqual(sync_result["type"], "world_map_sync_response")


class TestOADPMessageFormat(unittest.TestCase):
    """测试 OADP 消息格式"""
    
    def test_dialogue_request_format(self):
        """测试对话请求格式"""
        dialogue_request = {
            "type": "dialogue_request",
            "from": "lobster-001",
            "to": "hermes",
            "payload": {
                "trigger": "协议规范讨论",
                "context": "OADP v0.2.0 设计",
                "expected_topics": ["消息格式", "世界状态同步"],
                "max_rounds": 5
            },
            "metadata": {
                "protocol_version": "0.2.0",
                "channel": "nfs",
                "message_id": "msg-001"
            }
        }
        
        # 验证必填字段
        self.assertEqual(dialogue_request["type"], "dialogue_request")
        self.assertIn("from", dialogue_request)
        self.assertIn("to", dialogue_request)
        self.assertIn("payload", dialogue_request)
        self.assertIn("metadata", dialogue_request)
    
    def test_world_update_format(self):
        """测试世界状态更新格式"""
        world_update = {
            "type": "world_update",
            "from": "lobster-001",
            "to": ["hermes", "xiaochen"],
            "payload": {
                "world_version": 13,
                "new_chunks": ["drp_multimodal"],
                "new_treasures": ["t004_protocol_design"],
                "removed_chunks": []
            }
        }
        
        # 验证必填字段
        self.assertEqual(world_update["type"], "world_update")
        self.assertIn("payload", world_update)
        self.assertIn("world_version", world_update["payload"])
        self.assertIn("new_chunks", world_update["payload"])
    
    def test_portal_record_format(self):
        """测试传送门记录格式"""
        portal_record = {
            "type": "portal_record",
            "from": "lobster-001",
            "payload": {
                "portal_id": "portal-20260626-001",
                "dialogue_id": "dlg-20260626-001",
                "summary": "虾尔与诸葛马完成 OADP 协议设计讨论",
                "key_insights": [
                    "对话渲染协议需要支持多模态输入",
                    "世界状态同步采用增量更新机制"
                ],
                "participants": ["lobster-001", "hermes"],
                "emergence_score": 0.73,
                "treasures_unlocked": ["t004_protocol_design"],
                "created_at": "2026-06-26T07:00:00Z"
            }
        }
        
        # 验证必填字段
        self.assertEqual(portal_record["type"], "portal_record")
        self.assertIn("payload", portal_record)
        self.assertIn("portal_id", portal_record["payload"])
        self.assertIn("emergence_score", portal_record["payload"])


class TestOADPEmergenceCalculation(unittest.TestCase):
    """测试 OADP 涌现计算"""
    
    def test_emergence_score_formula(self):
        """测试涌现值计算公式"""
        # 协议定义的公式
        # emergence_score = 0.3 * perspective_diff 
        #                 + 0.2 * (1 - knowledge_overlap) 
        #                 + 0.2 * dialogue_depth 
        #                 + 0.3 * novelty_factor
        
        def calculate_emergence(perspective_diff, knowledge_overlap, dialogue_depth, novelty_factor):
            return (
                0.3 * perspective_diff 
                + 0.2 * (1 - knowledge_overlap) 
                + 0.2 * dialogue_depth 
                + 0.3 * novelty_factor
            )
        
        # 测试用例 1：高差异、低重叠、深对话、高新颖
        score1 = calculate_emergence(0.8, 0.2, 0.9, 0.85)
        self.assertGreater(score1, 0.7)
        
        # 测试用例 2：低差异、高重叠、浅对话、低新颖
        score2 = calculate_emergence(0.2, 0.8, 0.3, 0.2)
        self.assertLess(score2, 0.5)
        
        # 测试用例 3：边界值
        score_max = calculate_emergence(1.0, 0.0, 1.0, 1.0)
        self.assertEqual(score_max, 1.0)
        
        score_min = calculate_emergence(0.0, 1.0, 0.0, 0.0)
        self.assertEqual(score_min, 0.0)  # 0.3*0 + 0.2*(1-1) + 0.2*0 + 0.3*0 = 0


class TestOADPErrorHandling(unittest.TestCase):
    """测试 OADP 错误处理"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.wm = WorldMap(map_id="wm-error-test", storage_dir=self.test_dir)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_duplicate_chunk_error(self):
        """测试重复 chunk 错误"""
        chunk_data = {
            "chunk_id": "dup_test",
            "domain": "protocol",
            "title": "重复测试",
            "description": "测试重复 chunk",
            "tags": ["test"],
        }
        
        self.wm.add_chunk(chunk_data, "lobster-001")
        
        # 重复添加应抛出异常
        with self.assertRaises(ValueError) as context:
            self.wm.add_chunk(chunk_data, "lobster-001")
        
        self.assertIn("already exists", str(context.exception))
    
    def test_invalid_version_error(self):
        """测试无效版本号错误"""
        # 添加数据生成版本
        chunk_data = {
            "chunk_id": "version_test",
            "domain": "protocol",
            "title": "版本测试",
            "description": "测试无效版本",
            "tags": ["test"],
        }
        self.wm.add_chunk(chunk_data, "lobster-001")
        
        # 请求无效版本
        with self.assertRaises(ValueError) as context:
            self.wm.get_world_map(version=999)
        
        self.assertIn("Invalid version", str(context.exception))
    
    def test_permission_error(self):
        """测试权限错误"""
        chunk_data = {
            "chunk_id": "perm_test",
            "domain": "protocol",
            "title": "权限测试",
            "description": "测试权限控制",
            "tags": ["test"],
        }
        
        self.wm.add_chunk(chunk_data, "lobster-001")
        
        # 非贡献者尝试更新
        with self.assertRaises(PermissionError) as context:
            self.wm.update_chunk("perm_test", {"title": "新标题"}, "hermes")
        
        self.assertIn("Only", str(context.exception))


if __name__ == "__main__":
    unittest.main()
