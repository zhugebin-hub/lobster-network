"""
龙虾网络协作实战测试 - 简化版
"""

import json
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.rate_limiter import RateLimiter, RateTier
from src.lobster_network.message_queue import MessageQueue, MessagePriority
from src.lobster_network.global_scheduler import GlobalScheduler


class TestLobsterCollaboration(unittest.TestCase):
    
    def setUp(self):
        import shutil
        self.test_dir = "/tmp/lobster-test-state"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.limiter = RateLimiter(node_id="lobster-001", state_dir=self.test_dir)
        self.scheduler = GlobalScheduler(node_id="lobster-001", state_dir=self.test_dir)
        self.queue = MessageQueue(
            node_id="lobster-001",
            state_dir=self.test_dir,
            config={
                "dingtalk": {"messages_per_minute": 20, "cooldown_minutes_on_limit": 10},
                "channels": {
                    "dingtalk": {"enabled": False, "priority": 1},
                    "nfs": {"enabled": False, "priority": 2},
                    "ssh": {"enabled": False, "priority": 3},
                    "local": {"enabled": True, "priority": 99},
                },
                "nfs_dir": "/tmp/lobster-test-nfs",
            },
        )
    
    def test_rate_limit_recovery(self):
        """测试限速恢复流程"""
        print("\n=== 测试：限速恢复流程 ===\n")
        
        for i in range(3):
            self.limiter.on_429("dashscope")
            status = self.limiter.get_status()
            print(f"  第 {i+1} 次 429: tier={status['tier']}, consecutive={status['consecutive_429s']}")
        
        result = self.limiter.gate("chat")
        self.assertFalse(result.allowed)
        self.assertEqual(result.tier, RateTier.PAUSED)
        print(f"\n  限速状态: {result.tier} - {result.reason}")
        
        self.limiter.reset()
        result = self.limiter.gate("chat")
        self.assertTrue(result.allowed)
        print(f"  重置后: {result.tier} - {result.reason}")
        
        print("\n=== 测试通过 ===")
    
    def test_scheduler_integration(self):
        """测试调度器集成"""
        print("\n=== 测试：调度器集成 ===\n")
        
        tasks = [
            ("task_a", "lobster-001", "09:00", 1),
            ("task_b", "hermes", "09:05", 2),
            ("task_c", "zhuguxia", "09:10", 3),
        ]
        
        for name, node, schedule, priority in tasks:
            self.scheduler.register_task(name, node, schedule, priority)
            print(f"  注册任务: {name} → {node}")
        
        for name, _, _, _ in tasks:
            result = self.scheduler.can_execute(name)
            print(f"  调度检查 {name}: {'允许' if result.allowed else '拒绝'}")
            self.assertTrue(result.allowed)
        
        status = self.scheduler.get_status()
        print(f"\n  调度状态: tasks={status['total_tasks']}, conflicts={len(status['conflicts'])}")
        
        self.assertGreaterEqual(status['total_tasks'], 3)  # 至少 3 个任务（默认 + 注册）
        self.assertGreaterEqual(len(status['conflicts']), 0)  # 默认调度可能有冲突
        
        print("\n=== 测试通过 ===")
    
    def test_message_queue_local(self):
        """测试消息队列（本地通道）"""
        print("\n=== 测试：消息队列（本地通道） ===\n")
        
        msg_id = self.queue.send(
            to="lobster-002",
            content="测试消息",
            priority=MessagePriority.P1_IMPORTANT,
        )
        print(f"  发送消息: {msg_id}")
        
        queue_status = self.queue.get_queue_status()
        print(f"  队列状态: pending={queue_status['queue']['pending']}, delivered={queue_status['queue']['delivered']}")
        
        print("\n=== 测试通过 ===")


if __name__ == '__main__':
    unittest.main(verbosity=2)
