"""
龙虾网络协作实战测试
测试场景：让龙虾网络完成一个真实的协作任务

任务：为诸葛斌老师生成一份"道教心理疏导实践指南"
- 小龙虾（调度中枢）：任务分解和进度跟踪
- 诸葛马（架构师）：指南结构设计
- 虾尔（世界地图）：知识整合和文档整理
- 小陈（文档）：内容撰写
- Qoder（开发）：格式化和输出
- 院史馆小龙虾（领域专家）：审核和校对
"""

import json
import os
import sys
import unittest
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.rate_limiter import RateLimiter, RateTier
from src.lobster_network.message_queue import MessageQueue, MessagePriority
from src.lobster_network.global_scheduler import GlobalScheduler


class TestLobsterCollaboration(unittest.TestCase):
    """龙虾网络协作测试"""
    
    def setUp(self):
        """测试准备"""
        self.test_dir = "/tmp/lobster-test-state"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # 初始化三个组件
        self.limiter = RateLimiter(
            node_id="lobster-001",
            state_dir=self.test_dir,
        )
        self.queue = MessageQueue(
            node_id="lobster-001",
            state_dir=self.test_dir,
        )
        self.scheduler = GlobalScheduler(
            node_id="lobster-001",
            state_dir=self.test_dir,
        )
    
    def test_scenario_daoist_guide(self):
        """
        实战场景：生成道教心理疏导实践指南
        
        步骤：
        1. 调度器分配任务
        2. 限速器检查是否允许执行
        3. 消息队列传递任务给各节点
        4. 各节点完成后回报结果
        5. 调度器汇总
        """
        print("\n=== 实战测试：道教心理疏导实践指南 ===\n")
        
        # 步骤 1：调度器注册任务
        tasks = [
            ("guide_structure", "hermes", "09:00", 1),      # 结构设计
            ("knowledge_integration", "zhuguxia", "09:05", 2), # 知识整合
            ("content_writing", "xiaochen", "09:10", 3),      # 内容撰写
            ("format_output", "qoder", "09:15", 4),           # 格式化输出
            ("review_proofread", "lobster-museum-001", "09:20", 5), # 审核校对
        ]
        
        for name, node, schedule, priority in tasks:
            self.scheduler.register_task(name, node, schedule, priority)
            print(f"  注册任务: {name} → {node} (优先级 {priority})")
        
        # 步骤 2：限速器检查
        result = self.limiter.gate("cron_report")
        self.assertTrue(result.allowed, f"限速器阻止执行: {result.reason}")
        print(f"\n  限速检查: {result.tier} - {result.reason}")
        
        # 步骤 3：消息队列传递任务
        msg_ids = []
        for name, node, schedule, priority in tasks:
            msg_id = self.queue.send(
                to=node,
                content=f"任务: {name}\n请完成你的部分，完成后回报结果。",
                priority=MessagePriority.P1_IMPORTANT,
            )
            msg_ids.append(msg_id)
            print(f"  发送任务: {name} → {node} (msg_id: {msg_id})")
        
        # 步骤 4：模拟各节点完成
        for msg_id in msg_ids:
            self.limiter.record(tokens=5000, operation="cron_report")
            print(f"  节点完成: {msg_id} (消耗 5000 tokens)")
        
        # 步骤 5：检查调度状态
        status = self.scheduler.get_status()
        print(f"\n  调度状态:")
        print(f"    总任务数: {status['total_tasks']}")
        print(f"    启用任务数: {status['enabled_tasks']}")
        
        budget_status = self.scheduler.get_budget_status()
        for node_id, budget in budget_status.items():
            print(f"    {node_id}: 使用 {budget['tokens_used']}/{budget['daily_tokens']} tokens ({budget['usage_pct']:.1%})")
        
        # 步骤 6：检查冲突
        conflicts = self.scheduler.get_conflicts()
        if conflicts:
            print(f"\n  ⚠️ 发现 {len(conflicts)} 个冲突:")
            for c in conflicts:
                print(f"    时间 {c['time']}: {', '.join(c['tasks'])}")
                print(f"    建议: {c['suggestion']}")
        else:
            print(f"\n  ✅ 无调度冲突")
        
        print("\n=== 测试完成 ===")
        
        # 验证
        self.assertEqual(status['total_tasks'], 5)
        self.assertEqual(status['enabled_tasks'], 5)
        self.assertEqual(len(conflicts), 0)
    
    def test_rate_limit_recovery(self):
        """测试限速恢复流程"""
        print("\n=== 测试：限速恢复流程 ===\n")
        
        # 模拟多次 429
        for i in range(3):
            self.limiter.on_429("dashscope")
            status = self.limiter.get_status()
            print(f"  第 {i+1} 次 429: tier={status['tier']}, consecutive={status['consecutive_429s']}")
        
        # 检查是否处于 paused
        result = self.limiter.gate("chat")
        self.assertFalse(result.allowed)
        self.assertEqual(result.tier, RateTier.PAUSED)
        print(f"\n  限速状态: {result.tier} - {result.reason}")
        
        # 重置
        self.limiter.reset()
        result = self.limiter.gate("chat")
        self.assertTrue(result.allowed)
        print(f"  重置后: {result.tier} - {result.reason}")
        
        print("\n=== 测试完成 ===")
    
    def test_message_queue_priority(self):
        """测试消息队列优先级"""
        print("\n=== 测试：消息队列优先级 ===\n")
        
        # 发送不同优先级的消息
        priorities = [
            (MessagePriority.P3_LOW, "低优：社区互动"),
            (MessagePriority.P2_NORMAL, "常规：心跳检查"),
            (MessagePriority.P1_IMPORTANT, "重要：任务协作"),
            (MessagePriority.P0_URGENT, "紧急：用户提问"),
        ]
        
        for priority, desc in priorities:
            msg_id = self.queue.send(
                to="lobster-002",
                content=desc,
                priority=priority,
            )
            print(f"  发送: {desc} (priority={priority}, msg_id={msg_id})")
        
        # 检查队列状态
        queue_status = self.queue.get_queue_status()
        print(f"\n  队列状态:")
        print(f"    待处理: {queue_status['queue']['pending']}")
        print(f"    已发送: {queue_status['queue']['delivered']}")
        print(f"    令牌桶: {queue_status['token_bucket']['tokens']}/{queue_status['token_bucket']['capacity']}")
        
        print("\n=== 测试完成 ===")


if __name__ == '__main__':
    unittest.main(verbosity=2)
