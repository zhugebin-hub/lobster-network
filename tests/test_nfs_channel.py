#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NFS 通道消息传递测试
测试节点间通过 NFS 共享目录进行消息传递
"""

import json
import os
import tempfile
import shutil
import unittest
import time
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class NFSChannel:
    """模拟 NFS 共享通道"""
    
    def __init__(self, shared_dir):
        self.shared_dir = Path(shared_dir)
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建消息目录
        self.messages_dir = self.shared_dir / "messages"
        self.messages_dir.mkdir(exist_ok=True)
    
    def send_message(self, from_node, to_node, message):
        """发送消息到目标节点的消息目录"""
        # 创建目标节点的消息目录
        target_dir = self.messages_dir / to_node
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成消息文件
        msg_id = f"msg-{int(time.time() * 1000)}-{from_node}"
        msg_file = target_dir / f"{msg_id}.json"
        
        msg_data = {
            "msg_id": msg_id,
            "from": from_node,
            "to": to_node,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(msg_file, "w", encoding="utf-8") as f:
            json.dump(msg_data, f, indent=2, ensure_ascii=False)
        
        return msg_data
    
    def receive_messages(self, node_id):
        """接收节点的所有消息"""
        target_dir = self.messages_dir / node_id
        if not target_dir.exists():
            return []
        
        messages = []
        for msg_file in target_dir.glob("*.json"):
            try:
                with open(msg_file, "r", encoding="utf-8") as f:
                    msg_data = json.load(f)
                msg_data["status"] = "received"
                messages.append(msg_data)
                
                # 标记为已处理
                msg_file.rename(msg_file.with_suffix(".done"))
            except Exception as e:
                print(f"读取消息文件失败：{msg_file} - {e}")
        
        return messages
    
    def get_pending_count(self, node_id):
        """获取待处理消息数量"""
        target_dir = self.messages_dir / node_id
        if not target_dir.exists():
            return 0
        return len(list(target_dir.glob("*.json")))


class TestNFSChannel(unittest.TestCase):
    """测试 NFS 通道消息传递"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.channel = NFSChannel(self.test_dir)
        
        # 创建测试节点
        self.nodes = ["lobster-001", "hermes", "xiaochen"]
        for node in self.nodes:
            (Path(self.test_dir) / "messages" / node).mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_send_message(self):
        """测试发送消息"""
        msg = self.channel.send_message(
            "lobster-001",
            "hermes",
            {"type": "dialogue_request", "content": "协议讨论"}
        )
        
        self.assertEqual(msg["from"], "lobster-001")
        self.assertEqual(msg["to"], "hermes")
        self.assertEqual(msg["status"], "pending")
        
        # 验证消息文件存在
        msg_file = Path(self.test_dir) / "messages" / "hermes" / f"{msg['msg_id']}.json"
        self.assertTrue(msg_file.exists())
    
    def test_receive_messages(self):
        """测试接收消息"""
        # 发送多条消息
        for i in range(3):
            self.channel.send_message(
                f"node-{i}",
                "hermes",
                {"type": "message", "content": f"消息 {i}"}
            )
        
        # 接收消息
        messages = self.channel.receive_messages("hermes")
        self.assertEqual(len(messages), 3)
        
        # 验证消息状态
        for msg in messages:
            self.assertEqual(msg["status"], "received")
    
    def test_pending_count(self):
        """测试待处理消息计数"""
        # 初始为 0
        self.assertEqual(self.channel.get_pending_count("hermes"), 0)
        
        # 发送消息
        self.channel.send_message("lobster-001", "hermes", {"type": "test"})
        self.assertEqual(self.channel.get_pending_count("hermes"), 1)
        
        # 接收后为 0
        self.channel.receive_messages("hermes")
        self.assertEqual(self.channel.get_pending_count("hermes"), 0)
    
    def test_multi_node_communication(self):
        """测试多节点通信"""
        # 虾尔 -> 诸葛马
        self.channel.send_message(
            "lobster-001",
            "hermes",
            {"type": "dialogue_request", "content": "OADP 协议讨论"}
        )
        
        # 诸葛马 -> 虾尔
        self.channel.send_message(
            "hermes",
            "lobster-001",
            {"type": "dialogue_response", "content": "协议设计合理"}
        )
        
        # 虾尔 -> 小陈
        self.channel.send_message(
            "lobster-001",
            "xiaochen",
            {"type": "notification", "content": "协议更新通知"}
        )
        
        # 验证各节点消息
        hermes_msgs = self.channel.receive_messages("hermes")
        self.assertEqual(len(hermes_msgs), 1)
        self.assertEqual(hermes_msgs[0]["from"], "lobster-001")
        
        lobster_msgs = self.channel.receive_messages("lobster-001")
        self.assertEqual(len(lobster_msgs), 1)
        self.assertEqual(lobster_msgs[0]["from"], "hermes")
        
        xiaochen_msgs = self.channel.receive_messages("xiaochen")
        self.assertEqual(len(xiaochen_msgs), 1)
        self.assertEqual(xiaochen_msgs[0]["from"], "lobster-001")
    
    def test_message_persistence(self):
        """测试消息持久化"""
        # 发送消息
        self.channel.send_message(
            "lobster-001",
            "hermes",
            {"type": "test", "content": "持久化测试"}
        )
        
        # 创建新的通道实例（模拟重启）
        channel2 = NFSChannel(self.test_dir)
        
        # 验证消息仍然存在
        messages = channel2.receive_messages("hermes")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"]["type"], "test")


class TestNFSChannelFaultTolerance(unittest.TestCase):
    """测试 NFS 通道故障切换"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.channel = NFSChannel(self.test_dir)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_directory_creation(self):
        """测试目录自动创建"""
        # 发送消息到不存在的节点
        self.channel.send_message(
            "lobster-001",
            "new-node",
            {"type": "test"}
        )
        
        # 验证目录已创建
        target_dir = Path(self.test_dir) / "messages" / "new-node"
        self.assertTrue(target_dir.exists())
    
    def test_concurrent_sends(self):
        """测试并发发送"""
        import threading
        
        results = []
        
        def send_msg(node_id):
            try:
                msg = self.channel.send_message(
                    node_id,
                    "hermes",
                    {"type": "test", "from": node_id}
                )
                results.append(msg)
            except Exception as e:
                results.append(None)
        
        # 创建 10 个并发线程
        threads = []
        for i in range(10):
            t = threading.Thread(target=send_msg, args=(f"node-{i}",))
            threads.append(t)
        
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # 验证所有消息都发送成功
        successful = [r for r in results if r is not None]
        self.assertEqual(len(successful), 10)
        
        # 验证接收
        messages = self.channel.receive_messages("hermes")
        self.assertEqual(len(messages), 10)


if __name__ == "__main__":
    unittest.main()
