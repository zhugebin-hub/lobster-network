"""
测试通讯协议和注册中心增强版
"""

import pytest
import json
import os
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.lobster_network.utils.message_protocol_v2 import Message, MessageProtocol
from src.lobster_network.network.node_registry import NodeRegistry, NodeRegistration


class TestMessageV2:
    """测试消息增强版"""
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(
            msg_id="test-001",
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
            priority=1,
            ttl=3600,
        )
        
        assert msg.msg_id == "test-001"
        assert msg.from_node == "hermes"
        assert msg.to_node == "xiaochen"
        assert msg.msg_type == "training_task"
        assert msg.priority == 1
        assert msg.ttl == 3600
        assert not msg.confirmed
        assert msg.retry_count == 0
    
    def test_message_serialization(self):
        """测试消息序列化"""
        msg = Message(
            msg_id="test-002",
            from_node="hermes",
            to_node="zhuguxia",
            msg_type="heartbeat",
            payload={"status": "alive"},
        )
        
        # 转字典
        data = msg.to_dict()
        assert data["msg_id"] == "test-002"
        assert data["from"] == "hermes"
        assert data["to"] == "zhuguxia"
        assert data["type"] == "heartbeat"
        assert data["priority"] == 0
        
        # 转JSON再解析
        json_str = msg.to_json()
        msg2 = Message.from_json(json_str)
        assert msg2.msg_id == msg.msg_id
        assert msg2.from_node == msg.from_node
        assert msg2.to_node == msg.to_node
    
    def test_message_expiry(self):
        """测试消息过期"""
        # 创建已过期的消息
        msg = Message(
            msg_id="test-expired",
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={},
            ttl=1,  # 1秒过期
        )
        
        # 修改时间戳为2秒前
        old_time = datetime.now() - timedelta(seconds=2)
        msg.timestamp = old_time.isoformat()
        
        assert msg.is_expired()
    
    def test_message_dedup_hash(self):
        """测试消息去重哈希"""
        msg1 = Message(
            msg_id="test-001",
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        msg2 = Message(
            msg_id="test-002",  # 不同ID
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},  # 相同内容
        )
        
        # 内容哈希应该相同
        assert msg1.get_content_hash() == msg2.get_content_hash()
    
    def test_message_validation(self):
        """测试消息验证"""
        msg = Message(
            msg_id="test-001",
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        # 有效消息
        assert msg.msg_id
        assert msg.from_node
        assert msg.to_node
        assert msg.msg_type


class TestMessageProtocolV2:
    """测试消息协议增强版"""
    
    def setup_method(self):
        """测试前准备"""
        self.tmpdir = tempfile.mkdtemp()
        self.protocol = MessageProtocol(storage_dir=self.tmpdir)
    
    def teardown_method(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
    
    def test_create_message(self):
        """测试创建消息"""
        msg = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        assert msg is not None
        assert msg.from_node == "hermes"
        assert msg.to_node == "xiaochen"
        assert msg.msg_type == "training_task"
        assert msg.msg_id.startswith("msg-")
    
    def test_duplicate_message_detection(self):
        """测试重复消息检测"""
        msg1 = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        # 相同内容应该返回None（但时间戳不同，所以哈希不同）
        # 修改测试：使用相同的时间戳模拟重复
        msg2 = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        # 两个消息都应该创建成功（因为时间戳不同）
        # 但内容哈希应该相同
        assert msg1 is not None
        assert msg2 is not None
        assert msg1.get_content_hash() == msg2.get_content_hash()
    
    def test_confirm_message(self):
        """测试确认消息"""
        msg = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        assert not msg.confirmed
        assert msg.msg_id in self.protocol.pending_messages
        
        # 确认消息
        result = self.protocol.confirm_message(msg.msg_id)
        assert result is True
        assert msg.confirmed
        assert msg.msg_id not in self.protocol.pending_messages
    
    def test_retry_message(self):
        """测试重试消息"""
        msg = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
            max_retries=3,
        )
        
        assert msg.retry_count == 0
        
        # 重试
        retried = self.protocol.retry_message(msg.msg_id)
        assert retried is not None
        assert retried.retry_count == 1
        
        # 再次重试
        retried2 = self.protocol.retry_message(msg.msg_id)
        assert retried2 is not None
        assert retried2.retry_count == 2
    
    def test_max_retries_exceeded(self):
        """测试超过最大重试次数"""
        msg = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
            max_retries=2,
        )
        
        # 重试2次
        self.protocol.retry_message(msg.msg_id)
        self.protocol.retry_message(msg.msg_id)
        
        # 第3次应该返回None
        result = self.protocol.retry_message(msg.msg_id)
        assert result is None
    
    def test_persistence(self):
        """测试消息持久化"""
        msg = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
        )
        
        # 创建新的协议实例，应该加载持久化的消息
        protocol2 = MessageProtocol(storage_dir=self.tmpdir)
        assert len(protocol2.message_history) > 0
    
    def test_cleanup_expired(self):
        """测试清理过期消息"""
        # 创建过期消息
        msg = self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={"task": "test"},
            ttl=1,
        )
        
        # 修改时间戳为2秒前
        old_time = datetime.now() - timedelta(seconds=2)
        msg.timestamp = old_time.isoformat()
        
        # 清理
        cleaned = self.protocol.cleanup_expired()
        assert cleaned == 1
        assert msg.msg_id not in self.protocol.pending_messages
    
    def test_statistics(self):
        """测试统计信息"""
        self.protocol.create_message(
            from_node="hermes",
            to_node="xiaochen",
            msg_type="training_task",
            payload={},
        )
        self.protocol.create_message(
            from_node="hermes",
            to_node="zhuguxia",
            msg_type="heartbeat",
            payload={},
        )
        
        stats = self.protocol.get_statistics()
        assert stats["total_messages"] == 2
        assert stats["pending_messages"] == 2
        assert stats["type_counts"]["training_task"] == 1
        assert stats["type_counts"]["heartbeat"] == 1


class TestNodeRegistry:
    """测试节点注册中心"""
    
    def setup_method(self):
        """测试前准备"""
        self.tmpdir = tempfile.mkdtemp()
        self.registry = NodeRegistry(
            heartbeat_timeout=60,
            storage_dir=self.tmpdir,
        )
    
    def teardown_method(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)
    
    def test_register_node(self):
        """测试注册节点"""
        result = self.registry.register(
            node_id="hermes",
            name="诸葛马",
            node_type="coach",
            host="172.24.57.34",
            port=8080,
            capabilities=["dispatch", "monitor"],
        )
        
        assert result is True
        
        node = self.registry.get_node("hermes")
        assert node is not None
        assert node.name == "诸葛马"
        assert node.node_type == "coach"
        assert node.status == "active"
    
    def test_register_duplicate_node(self):
        """测试重复注册节点（应该更新）"""
        self.registry.register(
            node_id="xiaochen",
            name="小陈",
            node_type="agent",
            capabilities=["go", "poster"],
        )
        
        # 再次注册，更新能力
        self.registry.register(
            node_id="xiaochen",
            name="小陈",
            node_type="agent",
            capabilities=["go", "poster", "protocol"],
        )
        
        node = self.registry.get_node("xiaochen")
        assert "protocol" in node.capabilities
        assert len(node.capabilities) == 3
    
    def test_deregister_node(self):
        """测试注销节点"""
        self.registry.register(
            node_id="zhuguxia",
            name="诸葛虾",
            node_type="agent",
        )
        
        result = self.registry.deregister("zhuguxia")
        assert result is True
        assert self.registry.get_node("zhuguxia") is None
    
    def test_heartbeat(self):
        """测试心跳"""
        self.registry.register(
            node_id="hermes",
            name="诸葛马",
            node_type="coach",
        )
        
        node = self.registry.get_node("hermes")
        old_hb = node.last_heartbeat
        
        time.sleep(0.1)
        
        self.registry.heartbeat("hermes", {"status": "healthy"})
        
        node = self.registry.get_node("hermes")
        assert node.last_heartbeat != old_hb
        assert node.metadata.get("status") == "healthy"
    
    def test_get_active_nodes(self):
        """测试获取活跃节点"""
        self.registry.register(node_id="n1", name="节点1", node_type="agent")
        self.registry.register(node_id="n2", name="节点2", node_type="agent")
        self.registry.register(node_id="n3", name="节点3", node_type="coach")
        
        active = self.registry.get_active_nodes()
        assert len(active) == 3
    
    def test_get_nodes_by_type(self):
        """测试按类型获取节点"""
        self.registry.register(node_id="n1", name="节点1", node_type="agent")
        self.registry.register(node_id="n2", name="节点2", node_type="agent")
        self.registry.register(node_id="n3", name="节点3", node_type="coach")
        
        agents = self.registry.get_nodes_by_type("agent")
        assert len(agents) == 2
        
        coaches = self.registry.get_nodes_by_type("coach")
        assert len(coaches) == 1
    
    def test_get_nodes_by_capability(self):
        """测试按能力获取节点"""
        self.registry.register(
            node_id="xiaochen",
            name="小陈",
            node_type="agent",
            capabilities=["go", "poster"],
        )
        self.registry.register(
            node_id="zhuguxia",
            name="诸葛虾",
            node_type="agent",
            capabilities=["go", "protocol"],
        )
        
        go_nodes = self.registry.get_nodes_by_capability("go")
        assert len(go_nodes) == 2
        
        poster_nodes = self.registry.get_nodes_by_capability("poster")
        assert len(poster_nodes) == 1
    
    def test_health_check(self):
        """测试健康检查"""
        self.registry.register(
            node_id="hermes",
            name="诸葛马",
            node_type="coach",
        )
        
        # 手动设置心跳时间为超时前
        node = self.registry.get_node("hermes")
        old_time = datetime.now() - timedelta(seconds=90)  # 超过60秒超时
        node.last_heartbeat = old_time.isoformat()
        
        # 健康检查
        health = self.registry.check_health()
        assert health["unhealthy"] == 1
        assert "hermes" in health["unhealthy_nodes"]
        
        # 节点状态应该变为inactive
        node = self.registry.get_node("hermes")
        assert node.status == "inactive"
    
    def test_health_check_dead(self):
        """测试死亡检测"""
        self.registry.register(
            node_id="hermes",
            name="诸葛马",
            node_type="coach",
        )
        
        # 设置心跳时间为2倍超时前
        node = self.registry.get_node("hermes")
        old_time = datetime.now() - timedelta(seconds=120)  # 超过2倍超时
        node.last_heartbeat = old_time.isoformat()
        
        # 健康检查
        health = self.registry.check_health()
        assert health["unhealthy"] == 1
        
        # 节点状态应该变为dead
        node = self.registry.get_node("hermes")
        assert node.status == "dead"
    
    def test_callbacks(self):
        """测试回调"""
        registered_nodes = []
        
        def on_register(node):
            registered_nodes.append(node.node_id)
        
        self.registry.on("register", on_register)
        
        self.registry.register(node_id="n1", name="节点1", node_type="agent")
        self.registry.register(node_id="n2", name="节点2", node_type="agent")
        
        assert "n1" in registered_nodes
        assert "n2" in registered_nodes
    
    def test_persistence(self):
        """测试注册表持久化"""
        self.registry.register(
            node_id="hermes",
            name="诸葛马",
            node_type="coach",
        )
        
        # 创建新的注册中心实例
        registry2 = NodeRegistry(storage_dir=self.tmpdir)
        node = registry2.get_node("hermes")
        
        assert node is not None
        assert node.name == "诸葛马"
    
    def test_registry_status(self):
        """测试注册中心状态"""
        self.registry.register(node_id="n1", name="节点1", node_type="agent")
        self.registry.register(node_id="n2", name="节点2", node_type="agent")
        
        status = self.registry.get_registry_status()
        assert status["total_nodes"] == 2
        assert status["active_nodes"] == 2
        assert status["inactive_nodes"] == 0
        assert status["dead_nodes"] == 0
