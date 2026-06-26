#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故障切换测试
测试 NFS 通道不可用时自动切换到 file 通道
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


class MultiChannelMessenger:
    """多通道消息传递器"""
    
    def __init__(self, node_id, channels_config):
        self.node_id = node_id
        self.channels = channels_config  # [{"type": "nfs", "endpoint": "...", "priority": 1, "enabled": True}, ...]
        self.pending_queue = []
        self.sent_messages = []
        self.received_messages = []
        self.channel_status = {}  # 记录通道状态
    
    def send_message(self, to_node, content, priority=1):
        """发送消息（自动故障切换）"""
        msg = {
            "from": self.node_id,
            "to": to_node,
            "content": content,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "attempts": [],
            "status": "pending"
        }
        
        # 按优先级尝试通道
        sorted_channels = sorted(self.channels, key=lambda x: x.get("priority", 99))
        
        for channel in sorted_channels:
            if not channel.get("enabled", True):
                continue
            
            channel_type = channel["type"]
            endpoint = channel["endpoint"]
            
            try:
                if channel_type == "nfs":
                    success = self._send_via_nfs(endpoint, msg)
                elif channel_type == "file":
                    success = self._send_via_file(endpoint, msg)
                elif channel_type == "http":
                    success = self._send_via_http(endpoint, msg)
                else:
                    success = False
                
                attempt = {
                    "channel": channel_type,
                    "endpoint": endpoint,
                    "success": success,
                    "timestamp": datetime.now().isoformat()
                }
                msg["attempts"].append(attempt)
                
                if success:
                    msg["status"] = "delivered"
                    self.sent_messages.append(msg)
                    return msg
                
            except Exception as e:
                attempt = {
                    "channel": channel_type,
                    "endpoint": endpoint,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                msg["attempts"].append(attempt)
        
        # 所有通道都失败，进入 pending 队列
        msg["status"] = "failed"
        self.pending_queue.append(msg)
        return msg
    
    def _send_via_nfs(self, endpoint, msg):
        """通过 NFS 发送消息"""
        try:
            target_dir = Path(endpoint) / msg["to"]
            target_dir.mkdir(parents=True, exist_ok=True)
            
            msg_file = target_dir / f"msg-{int(time.time() * 1000)}.json"
            with open(msg_file, "w", encoding="utf-8") as f:
                json.dump(msg, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def _send_via_file(self, endpoint, msg):
        """通过本地文件发送消息"""
        try:
            target_dir = Path(endpoint) / msg["to"]
            target_dir.mkdir(parents=True, exist_ok=True)
            
            msg_file = target_dir / f"msg-{int(time.time() * 1000)}.json"
            with open(msg_file, "w", encoding="utf-8") as f:
                json.dump(msg, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def _send_via_http(self, endpoint, msg):
        """通过 HTTP 发送消息（模拟）"""
        # 模拟 HTTP 发送失败
        return False
    
    def get_pending_messages(self):
        """获取待处理消息"""
        return self.pending_queue.copy()
    
    def retry_pending(self):
        """重试待处理消息"""
        retried = []
        still_pending = []
        
        for msg in self.pending_queue:
            # 重新尝试发送
            new_msg = self.send_message(msg["to"], msg["content"])
            if new_msg["status"] == "delivered":
                retried.append(new_msg)
            else:
                still_pending.append(msg)
        
        self.pending_queue = still_pending
        return retried


class TestFaultTolerance(unittest.TestCase):
    """测试故障切换"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        
        # 创建 NFS 通道目录（模拟不可用）
        self.nfs_dir = Path(self.test_dir) / "nfs" / "messages"
        self.nfs_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 file 通道目录
        self.file_dir = Path(self.test_dir) / "file" / "messages"
        self.file_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建节点
        self.nodes = {}
        for node_id in ["lobster-001", "hermes", "xiaochen"]:
            channels = [
                {
                    "type": "nfs",
                    "endpoint": str(self.nfs_dir),
                    "priority": 1,
                    "enabled": True
                },
                {
                    "type": "file",
                    "endpoint": str(self.file_dir),
                    "priority": 2,
                    "enabled": True
                }
            ]
            self.nodes[node_id] = MultiChannelMessenger(node_id, channels)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_normal_send(self):
        """测试正常发送（NFS 可用）"""
        msg = self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "dialogue_request", "content": "测试"}
        )
        
        self.assertEqual(msg["status"], "delivered")
        self.assertEqual(len(msg["attempts"]), 1)
        self.assertTrue(msg["attempts"][0]["success"])
    
    def test_nfs_failover_to_file(self):
        """测试 NFS 故障切换到 file 通道"""
        # 禁用 NFS 通道
        self.nodes["lobster-001"].channels[0]["enabled"] = False
        
        msg = self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "dialogue_request", "content": "故障切换测试"}
        )
        
        # 应该通过 file 通道发送成功
        self.assertEqual(msg["status"], "delivered")
        self.assertEqual(len(msg["attempts"]), 1)
        self.assertEqual(msg["attempts"][0]["channel"], "file")
    
    def test_all_channels_fail(self):
        """测试所有通道都失败"""
        # 禁用所有通道
        for channel in self.nodes["lobster-001"].channels:
            channel["enabled"] = False
        
        msg = self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "test", "content": "所有通道失败"}
        )
        
        # 消息应该进入 pending 队列
        self.assertEqual(msg["status"], "failed")
        self.assertEqual(len(self.nodes["lobster-001"].get_pending_messages()), 1)
    
    def test_retry_pending(self):
        """测试重试待处理消息"""
        # 先禁用所有通道
        for channel in self.nodes["lobster-001"].channels:
            channel["enabled"] = False
        
        # 发送消息（会失败）
        self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "test", "content": "待重试消息"}
        )
        
        # 启用 file 通道
        self.nodes["lobster-001"].channels[1]["enabled"] = True
        
        # 重试
        retried = self.nodes["lobster-001"].retry_pending()
        self.assertEqual(len(retried), 1)
        self.assertEqual(retried[0]["status"], "delivered")
    
    def test_multi_node_fault_tolerance(self):
        """测试多节点故障切换"""
        # 虾尔的 NFS 不可用
        self.nodes["lobster-001"].channels[0]["enabled"] = False
        
        # 诸葛马的 NFS 可用
        self.nodes["hermes"].channels[0]["enabled"] = True
        
        # 虾尔 -> 诸葛马（通过 file）
        msg1 = self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "message", "content": "通过 file 通道"}
        )
        self.assertEqual(msg1["status"], "delivered")
        
        # 诸葛马 -> 虾尔（通过 NFS）
        msg2 = self.nodes["hermes"].send_message(
            "lobster-001",
            {"type": "message", "content": "通过 NFS 通道"}
        )
        self.assertEqual(msg2["status"], "delivered")
        
        # 虾尔的所有通道不可用
        for channel in self.nodes["lobster-001"].channels:
            channel["enabled"] = False
        
        # 虾尔 -> 诸葛马（所有通道不可用，进入 pending）
        msg3 = self.nodes["lobster-001"].send_message(
            "hermes",
            {"type": "message", "content": "虾尔不可达"}
        )
        self.assertEqual(msg3["status"], "failed")
        self.assertEqual(len(self.nodes["lobster-001"].get_pending_messages()), 1)


class TestChannelHealthCheck(unittest.TestCase):
    """测试通道健康检查"""
    
    def setUp(self):
        """创建测试环境"""
        self.test_dir = tempfile.mkdtemp()
        
        self.nfs_dir = Path(self.test_dir) / "nfs"
        self.nfs_dir.mkdir(parents=True, exist_ok=True)
        
        self.file_dir = Path(self.test_dir) / "file"
        self.file_dir.mkdir(parents=True, exist_ok=True)
        
        channels = [
            {"type": "nfs", "endpoint": str(self.nfs_dir), "priority": 1, "enabled": True},
            {"type": "file", "endpoint": str(self.file_dir), "priority": 2, "enabled": True}
        ]
        self.messenger = MultiChannelMessenger("test-node", channels)
    
    def tearDown(self):
        """清理测试目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_channel_health_check(self):
        """测试通道健康检查"""
        # 初始状态所有通道启用
        for channel in self.messenger.channels:
            self.assertTrue(channel["enabled"])
        
        # 发送成功消息
        msg = self.messenger.send_message("target", {"type": "test"})
        self.assertEqual(msg["status"], "delivered")
    
    def test_channel_disable_on_failure(self):
        """测试通道失败后禁用"""
        # 模拟 NFS 通道连续失败
        self.messenger.channels[0]["enabled"] = True
        
        # 发送消息（NFS 失败）
        self.messenger.channels[0]["enabled"] = False
        msg = self.messenger.send_message("target", {"type": "test"})
        
        # 应该通过 file 通道成功
        self.assertEqual(msg["status"], "delivered")
        self.assertEqual(msg["attempts"][0]["channel"], "file")


if __name__ == "__main__":
    unittest.main()
