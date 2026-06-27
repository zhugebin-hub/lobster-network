"""
龙虾网络集成测试
测试限速器、消息队列、调度器的协同工作
"""

import json
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.lobster_network.rate_limiter import RateLimiter, RateTier
from src.lobster_network.global_scheduler import GlobalScheduler


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试准备"""
        import shutil
        self.test_dir = "/tmp/lobster-integration-test"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.limiter = RateLimiter(node_id="lobster-001", state_dir=self.test_dir)
        self.scheduler = GlobalScheduler(node_id="lobster-001", state_dir=self.test_dir)
    
    def test_limiter_scheduler_integration(self):
        """测试限速器和调度器集成"""
        print("\n=== 集成测试：限速器 + 调度器 ===\n")
        
        # 注册任务
        tasks = [
            ("task_a", "lobster-001", "09:00", 1),
            ("task_b", "lobster-001", "09:05", 2),
            ("task_c", "hermes", "09:10", 3),
        ]
        
        for name, node, schedule, priority in tasks:
            self.scheduler.register_task(name, node, schedule, priority)
            print(f"  注册任务: {name} → {node}")
        
        # 检查调度
        for name, _, _, _ in tasks:
            result = self.scheduler.can_execute(name)
            print(f"  调度检查 {name}: {'允许' if result.allowed else '拒绝'} - {result.reason}")
            self.assertTrue(result.allowed, f"任务 {name} 应该被允许")
        
        # 模拟执行
        for name, _, _, _ in tasks:
            self.limiter.record(tokens=5000, operation="cron_report")
            self.scheduler.record_execution(name, tokens=5000)
            print(f"  执行任务: {name} (5000 tokens)")
        
        # 检查状态
        limiter_status = self.limiter.get_status()
        scheduler_status = self.scheduler.get_status()
        
        print(f"\n  限速器状态: tier={limiter_status['tier']}")
        print(f"  调度器状态: tasks={scheduler_status['total_tasks']}")
        print(f"  冲突数: {len(scheduler_status['conflicts'])}")
        
        self.assertEqual(limiter_status['tier'], RateTier.OK)
        self.assertGreaterEqual(scheduler_status['total_tasks'], 3)  # 至少 3 个任务（默认 + 注册）
        self.assertEqual(len(scheduler_status['conflicts']), 0)
        
        print("\n=== 测试通过 ===")
    
    def test_budget_borrowing(self):
        """测试预算借用"""
        print("\n=== 测试：预算借用 ===\n")
        
        # 检查初始预算
        budgets = self.scheduler.get_budget_status()
        print(f"  初始预算:")
        for node_id, budget in budgets.items():
            print(f"    {node_id}: {budget['daily_tokens']} tokens")
        
        # 模拟高优先级节点预算用完
        high_node = "lobster-001"
        low_node = "qoder"
        
        # 借用预算（使用 lobster-001 的剩余预算，200000 - 15000 = 185000）
        success = self.scheduler.borrow_budget(high_node, low_node, 10000)
        self.assertTrue(success, "预算借用应该成功")
        
        # 检查借用后
        budgets = self.scheduler.get_budget_status()
        print(f"\n  借用后预算:")
        print(f"    {high_node}: {budgets[high_node]['daily_tokens']} tokens (借出 10000)")
        print(f"    {low_node}: {budgets[low_node]['daily_tokens']} tokens (借入 10000)")
        
        print("\n=== 测试通过 ===")
    
    def test_task_enable_disable(self):
        """测试任务启用/禁用"""
        print("\n=== 测试：任务启用/禁用 ===\n")
        
        # 先注册任务
        self.scheduler.register_task("task_a", "lobster-001", "10:00", 1)
        
        # 禁用一个任务
        self.scheduler.disable_task("task_a")
        result = self.scheduler.can_execute("task_a")
        self.assertFalse(result.allowed)
        print(f"  禁用 task_a: {'拒绝' if not result.allowed else '允许'} - {result.reason}")
        
        # 重新启用
        self.scheduler.enable_task("task_a")
        result = self.scheduler.can_execute("task_a")
        self.assertTrue(result.allowed)
        print(f"  启用 task_a: {'允许' if result.allowed else '拒绝'} - {result.reason}")
        
        print("\n=== 测试通过 ===")


if __name__ == '__main__':
    unittest.main(verbosity=2)
