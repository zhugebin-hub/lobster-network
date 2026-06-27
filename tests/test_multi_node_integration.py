#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多小龙虾协作生态联调测试
测试节点间消息传递、故障切换、心跳机制
"""

import json
import os
import tempfile
import shutil
import unittest
import time
import threading
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.world_map import WorldMap, WorldMapManager


class MockNode:
    """模拟小龙虾节点"""
    
    def __init__(self, node_id, name, storage_dir):
        self.node_id = node_id
        self.name = name
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.message_queue = []
        self.received_messages = []
        self.status = "active"
        self.last_heartbeat = time.time()
        
        # 创建世界地图实例
        self.world_map = WorldMap(
            map_id=f"wm-{node_id}",
            storage_dir=str(self.storage_dir / "world_map")
        )
    
    def send_message(self, to_node_id, message):
        """发送消息到目标节点"""
        msg = {
            "from": self.node_id,
            "to": to_node_id,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        self.message_queue.append(msg)
        return msg
    
    def receive_message(self, message):
        """接收消息"""
        message["status"] = "received"
        self.received_messages.append(message)
        return message
    
    def heartbeat(self):
        """发送心跳"""
        self.last_heartbeat = time.time()
        self.status = "active"
        return {
            "node_id": self.node_id,
            "status": self.status,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_status(self):
        """获取节点状态"""
        # 检查心跳超时（5 秒）
        if time.time() - self.last_heartbeat > 5:
            self.status = "suspected"
        return {
            "node_id": self.node_id,
            "name": self.name,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat,
            "messages_sent": len(self.message_queue),
            "messages_received": len(self.received_messages)
        }


class TestMultiNodeCommunication(unittest.TestCase):
    """测试多节点通信"""
    
    def setUp(self):
        """创建测试节点"""
        self.test_dir = tempfile.mkdtemp()
        
        # 创建 3 个测试节点
        self.nodes = {}
        for node_id, name in [("lobster-001", "虾尔"), ("hermes", "诸葛马"), ("xiaochen", "小陈")]:
            self.nodes[node_id] = MockNode(
                node_id=node_id,
                name=name,
                storage_dir=os.path.join(self.test_dir, node_id)
            )
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_node_creation(self):
        """测试节点创建"""
        self.assertEqual(len(self.nodes), 3)
        for node_id, node in self.nodes.items():
            self.assertEqual(node.status, "active")
            self.assertGreater(node.last_heartbeat, 0)
    
    def test_message_passing(self):
        """测试节点间消息传递"""
        # 虾尔发送消息给诸葛马
        msg = self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "dialogue_request", "content": "协议讨论"}
        )
        self.assertEqual(msg["status"], "sent")
        
        # 诸葛马接收消息
        received = self.nodes["hermes"].receive_message(msg)
        self.assertEqual(received["status"], "received")
        self.assertEqual(len(self.nodes["hermes"].received_messages), 1)
    
    def test_multi_round_dialogue(self):
        """测试多轮对话"""
        dialogue = [
            {"type": "dialogue_request", "content": "关于 OADP 协议"},
            {"type": "dialogue_response", "content": "协议设计合理"},
            {"type": "dialogue_response", "content": "建议增加心跳机制"},
        ]
        
        # 模拟多轮对话
        for i, content in enumerate(dialogue):
            if i % 2 == 0:
                msg = self.nodes["lobster-001"].send_message("hermes", content)
                self.nodes["hermes"].receive_message(msg)
            else:
                msg = self.nodes["hermes"].send_message("lobster-001", content)
                self.nodes["lobster-001"].receive_message(msg)
        
        # 检查消息统计
        self.assertGreater(len(self.nodes["lobster-001"].message_queue), 0)
        self.assertGreater(len(self.nodes["hermes"].message_queue), 0)


class TestFaultTolerance(unittest.TestCase):
    """测试故障切换"""
    
    def setUp(self):
        """创建测试节点"""
        self.test_dir = tempfile.mkdtemp()
        self.node = MockNode(
            node_id="test-node",
            name="测试节点",
            storage_dir=self.test_dir
        )
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_heartbeat_timeout(self):
        """测试心跳超时检测"""
        # 初始状态正常
        status = self.node.get_status()
        self.assertEqual(status["status"], "active")
        
        # 模拟心跳超时（手动设置 last_heartbeat 为过去时间）
        self.node.last_heartbeat = time.time() - 10
        status = self.node.get_status()
        self.assertEqual(status["status"], "suspected")
    
    def test_heartbeat_recovery(self):
        """测试心跳恢复"""
        # 模拟心跳超时
        self.node.last_heartbeat = time.time() - 10
        self.assertEqual(self.node.get_status()["status"], "suspected")
        
        # 发送心跳恢复
        self.node.heartbeat()
        self.assertEqual(self.node.get_status()["status"], "active")


class TestWorldMapSync(unittest.TestCase):
    """测试世界地图同步"""
    
    def setUp(self):
        """创建测试节点和世界地图"""
        self.test_dir = tempfile.mkdtemp()
        
        # 创建共享世界地图
        self.shared_map = WorldMap(
            map_id="shared-wm",
            storage_dir=os.path.join(self.test_dir, "shared")
        )
        
        # 创建节点
        self.nodes = {}
        for node_id in ["node-a", "node-b"]:
            self.nodes[node_id] = MockNode(
                node_id=node_id,
                name=f"节点 {node_id}",
                storage_dir=os.path.join(self.test_dir, node_id)
            )
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_chunk_sharing(self):
        """测试 chunk 共享"""
        # 节点 A 添加 chunk
        chunk_data = {
            "chunk_id": "shared_chunk_001",
            "domain": "protocol",
            "title": "共享知识碎片",
            "description": "测试节点间 chunk 共享",
            "tags": ["shared"],
        }
        self.shared_map.add_chunk(chunk_data, "node-a")
        
        # 节点 B 搜索 chunk
        results = self.shared_map.search_chunks(domain="protocol")
        self.assertGreaterEqual(len(results), 1)
        
        # 验证 chunk 内容
        chunk = self.shared_map.get_chunk("shared_chunk_001")
        self.assertIsNotNone(chunk)
        self.assertEqual(chunk["contributor"], "node-a")
    
    def test_treasure_unlock(self):
        """测试宝藏解锁"""
        # 模拟对话涌现解锁宝藏
        treasure_data = {
            "treasure_id": "treasure_001",
            "title": "协议设计洞察",
            "description": "通过对话产生的新知识",
            "rarity": "rare",
            "insight": "OADP 协议需要支持多通道故障切换",
        }
        
        treasure = self.shared_map.unlock_treasure(
            treasure_data,
            unlocked_by=["node-a", "node-b"]
        )
        
        self.assertEqual(treasure["verification_status"], "unlocked")
        self.assertIn("node-a", treasure["unlocked_by"])
        self.assertIn("node-b", treasure["unlocked_by"])


class TestConcurrentNodes(unittest.TestCase):
    """测试并发节点操作"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.shared_map = WorldMap(
            map_id="concurrent-wm",
            storage_dir=os.path.join(self.test_dir, "shared")
        )
        self.manager = WorldMapManager(self.shared_map)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_concurrent_chunk_add(self):
        """测试多节点并发添加 chunk"""
        results = []
        errors = []
        
        def add_chunk(node_id, chunk_id):
            try:
                chunk_data = {
                    "chunk_id": chunk_id,
                    "domain": "protocol",
                    "title": f"节点 {node_id} 的贡献",
                    "description": f"节点 {node_id} 添加的知识碎片",
                    "tags": [node_id],
                }
                result = self.manager.safe_add_chunk(chunk_data, node_id)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 创建 5 个并发节点
        threads = []
        for i in range(5):
            node_id = f"concurrent-node-{i}"
            t = threading.Thread(
                target=add_chunk,
                args=(node_id, f"concurrent_chunk_{i:03d}")
            )
            threads.append(t)
        
        # 启动所有线程
        for t in threads:
            t.start()
        
        # 等待完成
        for t in threads:
            t.join(timeout=10)
        
        # 验证结果
        self.assertGreaterEqual(len(results), 3)
        self.assertLessEqual(len(errors), 2)
        
        m = self.shared_map.get_world_map()
        self.assertGreaterEqual(m["total_chunks"], 3)


if __name__ == "__main__":
    unittest.main()
