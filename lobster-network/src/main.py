#!/usr/bin/env python3
"""
小龙虾网络 V4.1 集成入口
融合 Agent Harness工程实践 + 多智能体协作框架

核心模块：
1. 双阶段调度器（Initializer + Executor）
2. Sub-Agent 管理器
3. 事务管理器
4. 硬护栏系统
5. 文档园丁
"""

import json
import os
import sys
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from dual_phase_scheduler import DualPhaseScheduler
from sub_agent_manager import SubAgentManager
from transaction_manager import TransactionManager
from hard_guardrail import HardGuardrail
from doc_gardener import DocGardener


class LobsterNetworkV41:
    """
    小龙虾网络 V4.1
    集成所有优化模块
    """
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
        
        self.workspace_dir = Path(workspace_dir)
        
        # 初始化各模块
        self.scheduler = DualPhaseScheduler(str(self.workspace_dir))
        self.agent_manager = SubAgentManager(str(self.workspace_dir))
        self.transaction_manager = TransactionManager(str(self.workspace_dir))
        self.guardrail = HardGuardrail(str(self.workspace_dir))
        self.doc_gardener = DocGardener(str(self.workspace_dir))
        
        print("[LobsterNetwork V4.1] 初始化完成")
    
    def schedule_task(self, task: Dict) -> Dict:
        """
        调度任务（使用双阶段调度器）
        
        Args:
            task: 任务字典
            
        Returns:
            Dict: 执行结果
        """
        return self.scheduler.schedule(task)
    
    def dispatch_to_agent(self, agent_id: str, task: Dict) -> Dict:
        """
        分发任务到 Sub-Agent
        
        Args:
            agent_id: Sub-Agent ID
            task: 任务字典
            
        Returns:
            Dict: 执行结果
        """
        return self.agent_manager.dispatch(agent_id, task)
    
    def execute_with_transaction(self, transaction_id: str, steps: list) -> Dict:
        """
        带事务执行
        
        Args:
            transaction_id: 事务 ID
            steps: 步骤列表
            
        Returns:
            Dict: 执行结果
        """
        return self.transaction_manager.execute_with_transaction(transaction_id, steps)
    
    def validate_content(self, content: str) -> Dict:
        """
        验证内容（硬护栏）
        
        Args:
            content: 内容
            
        Returns:
            Dict: 验证结果
        """
        return self.guardrail.validate_content(content)
    
    def scan_documents(self) -> Dict:
        """
        扫描文档
        
        Returns:
            Dict: 扫描结果
        """
        return self.doc_gardener.scan()
    
    def cleanup_documents(self, dry_run: bool = True) -> Dict:
        """
        清理文档
        
        Args:
            dry_run: 是否仅模拟运行
            
        Returns:
            Dict: 清理结果
        """
        return self.doc_gardener.cleanup(dry_run=dry_run)
    
    def get_status(self) -> Dict:
        """
        获取系统状态
        
        Returns:
            Dict: 系统状态
        """
        return {
            "version": "V4.1",
            "workspace": str(self.workspace_dir),
            "agents": self.agent_manager.list_agents(),
            "doc_status": self.doc_gardener.get_status()
        }


def main():
    """主函数"""
    print("=" * 60)
    print("🦞 小龙虾网络 V4.1")
    print("=" * 60)
    
    # 初始化
    network = LobsterNetworkV41()
    
    # 测试 1: 双阶段调度
    print("\n=== 测试 1: 双阶段调度 ===")
    task = {
        "task_id": "test_training_001",
        "type": "training",
        "goal": "完成围棋 Day5 训练",
        "nodes": ["xiaochen", "zhuguxia", "qoder"],
        "params": {"day": 5, "subject": "go"}
    }
    result = network.schedule_task(task)
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试 2: Sub-Agent 分发
    print("\n=== 测试 2: Sub-Agent 分发 ===")
    result = network.dispatch_to_agent("training-coordinator", {
        "action": "distribute_training",
        "nodes": ["xiaochen", "zhuguxia", "qoder"],
        "day": 5
    })
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试 3: 硬护栏
    print("\n=== 测试 3: 硬护栏 ===")
    result = network.validate_content("您好，请问有什么可以帮助您的？")
    print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    # 测试 4: 文档园丁
    print("\n=== 测试 4: 文档园丁 ===")
    status = network.get_status()
    print(f"状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
EOF

echo "集成入口已创建"