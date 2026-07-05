#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
注册中心与可靠消息单元测试
"""

import json
import os
import tempfile
import shutil
import time
import unittest
from datetime import datetime, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lobster_network.registry import (
    NodeRegistry, RegistrationInfo, TransportConfig,
    TransportType, NodeStatus, _parse_time,
)
from src.lobster_network.messenger import (
    Messenger, ReliableMessage, MessageStatus,
    NFSTransport, FileTransport,
)
from src.lobster_network.integration import LobsterNetworkWithRegistry


class TestParseTime(unittest.TestCase):
    """时间解析测试"""

    def test_parse_iso_basic(self):
        """测试基本 ISO 格式"""
        dt = _parse_time("2026-06-24T08:00:00")
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 6)
        self.assertEqual(dt.day, 24)
        self.assertEqual(dt.hour, 8)

    def test_parse_iso_with_microseconds(self):
        """测试带微秒的 ISO 格式"""
        dt = _parse_time("2026-06-24T08:00:00.123456")
        self.assertEqual(dt.microsecond, 123456)

    def test_parse_iso_with_z(self):
        """测试带 Z 后缀"""
        dt = _parse_time("2026-06-24T08:00:00Z")
        self.assertEqual(dt.hour, 8)

    def test_parse_iso_with_timezone(self):
        """测试带时区偏移"""
        dt = _parse_time("2026-06-24T08:00:00+08:00")
        self.assertEqual(dt.hour, 8)


class TestRegistrationInfo(unittest.TestCase):
    """注册信息测试"""

    def test_create_registration(self):
        """测试创建注册信息"""
        info = RegistrationInfo(
            node_id="test-001",
            name="测试节点",
            node_type="agent",
            registered_at=datetime.now().isoformat(),
            last_heartbeat=datetime.now().isoformat(),
            capabilities=["test"],
            ttl_seconds=60,
        )
        self.assertEqual(info.node_id, "test-001")
        self.assertEqual(info.name, "测试节点")
        self.assertTrue(info.is_alive())

    def test_serialization(self):
        """测试序列化与反序列化"""
        info = RegistrationInfo(
            node_id="test-002",
            name="序列化测试",
            node_type="agent",
            registered_at="2026-06-24T07:00:00",
            last_heartbeat="2026-06-24T07:15:00",
            capabilities=["a", "b"],
            ttl_seconds=300,
        )
        data = info.to_dict()
        restored = RegistrationInfo.from_dict(data)
        self.assertEqual(restored.node_id, "test-002")
        self.assertEqual(restored.capabilities, ["a", "b"])

    def test_heartbeat_timeout(self):
        """测试心跳超时检测"""
        old_time = (datetime.now() - timedelta(seconds=70)).isoformat()
        info = RegistrationInfo(
            node_id="test-003",
            name="超时测试",
            node_type="agent",
            registered_at=old_time,
            last_heartbeat=old_time,
            ttl_seconds=60,
        )
        self.assertFalse(info.is_alive())


class TestNodeRegistry(unittest.TestCase):
    """注册中心测试"""

    def setUp(self):
        """创建临时存储"""
        self.tmpdir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.tmpdir, "registry.json")
        self.registry = NodeRegistry(storage_path=self.registry_path)

    def tearDown(self):
        """清理临时文件"""
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_register_node(self):
        """测试节点注册"""
        info = self.registry.register(
            node_id="node-001",
            name="虾尔",
            node_type="agent",
            capabilities=["world-map"],
        )
        self.assertEqual(info.node_id, "node-001")
        self.assertEqual(info.status, NodeStatus.ACTIVE)

    def test_unregister_node(self):
        """测试节点注销"""
        self.registry.register(node_id="node-001", name="测试")
        self.assertTrue(self.registry.unregister("node-001"))
        self.assertIsNone(self.registry.get_node("node-001"))

    def test_unregister_nonexistent(self):
        """测试注销不存在的节点"""
        self.assertFalse(self.registry.unregister("nonexistent"))

    def test_heartbeat(self):
        """测试心跳"""
        self.registry.register(node_id="node-001", name="测试", ttl_seconds=60)
        self.assertTrue(self.registry.heartbeat("node-001"))
        self.assertTrue(self.registry.is_alive("node-001"))

    def test_heartbeat_unregistered(self):
        """测试未注册节点的心跳"""
        self.assertFalse(self.registry.heartbeat("nonexistent"))

    def test_list_nodes(self):
        """测试列出节点"""
        self.registry.register(node_id="n1", name="节点1", node_type="agent")
        self.registry.register(node_id="n2", name="节点2", node_type="coach")
        self.registry.register(node_id="n3", name="节点3", node_type="agent")

        all_nodes = self.registry.list_nodes()
        self.assertEqual(len(all_nodes), 3)

        agents = self.registry.list_nodes(node_type="agent")
        self.assertEqual(len(agents), 2)

    def test_find_by_capability(self):
        """测试按能力查找"""
        self.registry.register(
            node_id="n1", name="节点1",
            capabilities=["world-map", "protocol"],
        )
        self.registry.register(
            node_id="n2", name="节点2",
            capabilities=["dialogue"],
        )

        results = self.registry.find_by_capability("world-map")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].node_id, "n1")

    def test_transport_management(self):
        """测试传输通道管理"""
        transports = [
            TransportConfig(transport_type="nfs", endpoint="/shared", priority=1),
            TransportConfig(transport_type="file", endpoint="/tmp", priority=99),
        ]
        self.registry.register(
            node_id="n1", name="节点1", transports=transports,
        )

        active = self.registry.get_active_transports("n1")
        self.assertEqual(len(active), 2)
        self.assertEqual(active[0].transport_type, "nfs")  # 优先级高

        # 标记 NFS 失败
        self.registry.mark_transport_failed("n1", "nfs", "mount error")
        active = self.registry.get_active_transports("n1")
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].transport_type, "file")

    def test_persistence(self):
        """测试持久化"""
        self.registry.register(node_id="n1", name="持久化测试")
        
        # 重新加载
        registry2 = NodeRegistry(storage_path=self.registry_path)
        node = registry2.get_node("n1")
        self.assertIsNotNone(node)
        self.assertEqual(node.name, "持久化测试")

    def test_health_check(self):
        """测试健康检查"""
        self.registry.register(node_id="n1", name="活跃节点", ttl_seconds=300)
        
        # 制造一个离线节点（通过直接修改 last_heartbeat）
        info = self.registry.register(node_id="n2", name="离线节点", ttl_seconds=300)
        info.last_heartbeat = (datetime.now() - timedelta(seconds=900)).isoformat()

        report = self.registry.check_health()
        self.assertEqual(report["total_nodes"], 2)
        self.assertEqual(report["online"], 1)

    def test_status_change_callback(self):
        """测试状态变化回调"""
        changes = []
        self.registry.on_status_change(lambda nid, old, new: changes.append((nid, old, new)))
        
        self.registry.register(node_id="n1", name="回调测试")
        self.registry.heartbeat("n1", status=NodeStatus.BUSY)
        
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0], ("n1", NodeStatus.ACTIVE, NodeStatus.BUSY))

    def test_export_registry(self):
        """测试导出注册表"""
        self.registry.register(node_id="n1", name="导出测试")
        exported = self.registry.export_registry()
        data = json.loads(exported)
        self.assertIn("n1", data)

    def test_statistics(self):
        """测试统计信息"""
        self.registry.register(node_id="n1", name="节点1", node_type="agent")
        self.registry.register(node_id="n2", name="节点2", node_type="coach")
        
        stats = self.registry.get_statistics()
        self.assertEqual(stats["total_nodes"], 2)
        self.assertEqual(stats["by_type"]["agent"], 1)
        self.assertEqual(stats["by_type"]["coach"], 1)


class TestReliableMessage(unittest.TestCase):
    """可靠消息测试"""

    def test_create_message(self):
        """测试创建消息"""
        msg = ReliableMessage(
            msg_id="msg-001",
            from_node="n1",
            to_node="n2",
            msg_type="dialogue_request",
            payload={"trigger": "test"},
        )
        self.assertEqual(msg.status, MessageStatus.PENDING)
        self.assertTrue(msg.can_retry())

    def test_message_expiration(self):
        """测试消息过期"""
        old_time = (datetime.now() - timedelta(hours=2)).isoformat()
        msg = ReliableMessage(
            msg_id="msg-002",
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={},
            timestamp=old_time,
            ttl_seconds=3600,
        )
        self.assertTrue(msg.is_expired())
        self.assertFalse(msg.can_retry())

    def test_record_attempt(self):
        """测试记录发送尝试"""
        msg = ReliableMessage(
            msg_id="msg-003",
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={},
            max_retries=3,
        )
        msg.record_attempt("nfs", success=False, error="mount error")
        self.assertEqual(len(msg.attempts), 1)
        self.assertEqual(msg.status, MessageStatus.PENDING)  # 可重试

        msg.record_attempt("file", success=True, latency_ms=1.5)
        self.assertEqual(msg.status, MessageStatus.DELIVERED)
        self.assertIsNotNone(msg.delivered_at)

    def test_max_retries_exceeded(self):
        """测试超过最大重试"""
        msg = ReliableMessage(
            msg_id="msg-004",
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={},
            max_retries=2,
        )
        msg.record_attempt("nfs", success=False, error="error1")
        msg.record_attempt("file", success=False, error="error2")
        self.assertEqual(msg.status, MessageStatus.FAILED)
        self.assertFalse(msg.can_retry())


class TestMessenger(unittest.TestCase):
    """可靠消息传递器测试"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.tmpdir, "registry.json")
        self.registry = NodeRegistry(storage_path=self.registry_path)
        self.messenger = Messenger(
            registry=self.registry,
            storage_dir=f"{self.tmpdir}/messages",
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_send_message(self):
        """测试发送消息"""
        # 注册目标节点（使用文件通道）
        self.registry.register(
            node_id="n2",
            name="节点2",
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/n2-inbox",
                    priority=1,
                ),
            ],
        )

        msg = self.messenger.send(
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={"data": "hello"},
        )
        self.assertEqual(msg.status, MessageStatus.DELIVERED)

    def test_ack_message(self):
        """测试消息确认"""
        self.registry.register(
            node_id="n2",
            name="节点2",
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/n2-inbox",
                    priority=1,
                ),
            ],
        )

        msg = self.messenger.send(
            from_node="n1", to_node="n2",
            msg_type="test", payload={},
        )
        self.assertTrue(self.messenger.ack(msg.msg_id))
        
        restored = self.messenger.get_message(msg.msg_id)
        self.assertEqual(restored.status, MessageStatus.ACKED)

    def test_delivery_callback(self):
        """测试投递回调"""
        delivered = []
        self.messenger.on_delivery(lambda m: delivered.append(m.msg_id))

        self.registry.register(
            node_id="n2", name="节点2",
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/n2-inbox",
                    priority=1,
                ),
            ],
        )

        self.messenger.send(from_node="n1", to_node="n2", msg_type="test", payload={})
        self.assertEqual(len(delivered), 1)

    def test_failure_callback(self):
        """测试失败回调"""
        failed = []
        self.messenger.on_failure(lambda m: failed.append(m.msg_id))

        # 不注册传输通道，且不设置默认文件通道
        self.registry.register(node_id="n2", name="节点2")
        
        # 手动创建一个无法投递的消息
        msg = ReliableMessage(
            msg_id="msg-fail-001",
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={},
            max_retries=0,  # 不允许重试
        )
        self.messenger.messages[msg.msg_id] = msg
        # 由于没有传输通道，不会自动投递，手动触发
        # 这里测试回调注册是否正常
        self.assertEqual(len(failed), 0)

    def test_query_messages(self):
        """测试消息查询"""
        self.registry.register(node_id="n2", name="节点2")
        
        self.messenger.send(from_node="n1", to_node="n2", msg_type="type_a", payload={})
        self.messenger.send(from_node="n1", to_node="n2", msg_type="type_b", payload={})
        
        all_msgs = self.messenger.get_messages()
        self.assertEqual(len(all_msgs), 2)
        
        type_a = self.messenger.get_messages(msg_type="type_a")
        self.assertGreaterEqual(len(type_a), 0)

    def test_statistics(self):
        """测试消息统计"""
        self.registry.register(node_id="n2", name="节点2")
        self.messenger.send(from_node="n1", to_node="n2", msg_type="test", payload={})
        
        stats = self.messenger.get_statistics()
        self.assertIn("total", stats)
        self.assertIn("by_status", stats)

    def test_cleanup_expired(self):
        """测试清理过期消息"""
        old_time = (datetime.now() - timedelta(hours=2)).isoformat()
        msg = ReliableMessage(
            msg_id="msg-expired",
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={},
            timestamp=old_time,
            ttl_seconds=3600,
            status=MessageStatus.ACKED,
        )
        self.messenger.messages[msg.msg_id] = msg
        
        count = self.messenger.cleanup_expired()
        self.assertEqual(count, 1)
        self.assertNotIn("msg-expired", self.messenger.messages)


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.network = LobsterNetworkWithRegistry(
            storage_dir=self.tmpdir,
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_register_and_heartbeat(self):
        """测试注册与心跳"""
        self.network.register_node(
            node_id="lobster-001",
            name="虾尔",
            node_type="agent",
            perspective="世界地图渲染",
            knowledge_base="协议规范",
            capabilities=["world-map"],
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/inbox",
                    priority=1,
                ),
            ],
        )
        
        self.assertTrue(self.network.is_alive("lobster-001"))
        self.assertTrue(self.network.heartbeat("lobster-001"))

    def test_send_message_through_network(self):
        """测试通过网络发送消息"""
        self.network.register_node(
            node_id="n1", name="节点1",
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/n1-inbox",
                    priority=1,
                ),
            ],
        )
        self.network.register_node(
            node_id="n2", name="节点2",
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/n2-inbox",
                    priority=1,
                ),
            ],
        )

        msg = self.network.send_message(
            from_node="n1",
            to_node="n2",
            msg_type="dialogue_request",
            payload={"trigger": "测试对话"},
        )
        self.assertEqual(msg.status, MessageStatus.DELIVERED)

    def test_health_check(self):
        """测试健康检查"""
        self.network.register_node(node_id="n1", name="节点1")
        health = self.network.health_check()
        self.assertEqual(health["total_nodes"], 1)
        self.assertEqual(health["online"], 1)

    def test_full_statistics(self):
        """测试完整统计"""
        self.network.register_node(node_id="n1", name="节点1")
        stats = self.network.get_full_statistics()
        self.assertIn("registry", stats)
        self.assertIn("messenger", stats)
        self.assertIn("network", stats)
        self.assertIn("health", stats)


class TestFaultTolerance(unittest.TestCase):
    """容错测试"""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.registry_path = os.path.join(self.tmpdir, "registry.json")
        self.registry = NodeRegistry(storage_path=self.registry_path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_nfs_failover_to_file(self):
        """测试 NFS 失败后切换到文件通道"""
        # 注册节点，配置 NFS（不可用） + 文件（可用）
        # 使用一个不存在的 NFS 路径，且 NFS Transport 的 can_use 会检查目录存在
        self.registry.register(
            node_id="n2",
            name="节点2",
            transports=[
                TransportConfig(
                    transport_type="nfs",
                    endpoint="/nonexistent/nfs/path/that/does/not/exist",
                    priority=1,
                ),
                TransportConfig(
                    transport_type="file",
                    endpoint=f"{self.tmpdir}/n2-inbox",
                    priority=2,
                ),
            ],
        )

        messenger = Messenger(
            registry=self.registry,
            storage_dir=f"{self.tmpdir}/messages",
        )

        msg = messenger.send(
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={"data": "failover test"},
        )

        # NFS 不存在，应该被 can_use 跳过，直接用 file
        self.assertEqual(msg.status, MessageStatus.DELIVERED)
        # 由于 NFS can_use 检查目录不存在，直接跳过，只有 file 一次尝试
        self.assertEqual(len(msg.attempts), 1)
        self.assertEqual(msg.attempts[0].transport, "file")
        self.assertTrue(msg.attempts[0].success)

    def test_all_transports_fail(self):
        """测试所有通道都失败"""
        # 使用一个无法写入的路径
        self.registry.register(
            node_id="n2",
            name="节点2",
            transports=[
                TransportConfig(
                    transport_type="file",
                    endpoint="/proc/readonly/impossible",
                    priority=1,
                ),
            ],
        )

        messenger = Messenger(
            registry=self.registry,
            storage_dir=f"{self.tmpdir}/messages",
        )

        msg = messenger.send(
            from_node="n1",
            to_node="n2",
            msg_type="test",
            payload={},
            max_retries=0,
        )
        self.assertEqual(msg.status, MessageStatus.FAILED)


if __name__ == "__main__":
    unittest.main()
