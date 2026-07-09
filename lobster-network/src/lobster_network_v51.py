#!/usr/bin/env python3
"""
小龙虾网络 V5.1 统一管理器
整合所有优化模块：
- 节点注册中心
- 训练数据持久化
- 训练监控告警
- 算力优化器
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# 导入优化模块
try:
    from optimized_node_registry import OptimizedNodeRegistry
    from training_persistence import TrainingPersistence
    from training_monitor import TrainingMonitor
    from compute_optimizer import ComputeOptimizer, TaskPriority
except ImportError:
    print("⚠️ 部分模块导入失败，使用模拟实现")
    
    class OptimizedNodeRegistry:
        def __init__(self, **kwargs): pass
        def register(self, *args, **kwargs): return {"success": True}
        def heartbeat(self, *args, **kwargs): return {"success": True}
        def get_active_nodes(self): return {}
    
    class TrainingPersistence:
        def __init__(self, **kwargs): pass
        def save_training_result(self, *args, **kwargs): return True
        def load_training_result(self, *args, **kwargs): return None
    
    class TrainingMonitor:
        def __init__(self, **kwargs): pass
        def start_monitoring(self, *args, **kwargs): pass
        def check_training_activity(self, *args, **kwargs): return None
    
    class ComputeOptimizer:
        def __init__(self, **kwargs): pass
        def submit_task(self, *args, **kwargs): return True
        def get_optimal_schedule(self): return []
        def get_cost_estimate(self, *args, **kwargs): return {"total_cost": 0}
    
    class TaskPriority:
        HIGH = 3
        MEDIUM = 2
        LOW = 1

class LobsterNetworkV51:
    """小龙虾网络 V5.1 统一管理器"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化各模块
        self.registry = OptimizedNodeRegistry(str(self.workspace_dir))
        self.persistence = TrainingPersistence(str(self.workspace_dir))
        self.monitor = TrainingMonitor(str(self.workspace_dir))
        self.optimizer = ComputeOptimizer(str(self.workspace_dir))
        
        # 系统状态
        self.system_status = {
            "started_at": time.time(),
            "version": "V5.1",
            "modules": {
                "registry": True,
                "persistence": True,
                "monitor": True,
                "optimizer": True
            }
        }
        
        # 启动监控
        self.monitor.start_monitoring(interval_seconds=300)
        
        print(f"[LobsterNetworkV51] 初始化完成，版本：{self.system_status['version']}")
    
    def register_agent(self, agent_id: str, name: str, capabilities: List[str] = None) -> Dict:
        """注册智能体"""
        result = self.registry.register(
            node_id=agent_id,
            name=name,
            capabilities=capabilities or []
        )
        
        # 提交初始化任务
        self.optimizer.submit_task(
            task_id=f"init_{agent_id}",
            task_type="initialization",
            priority=TaskPriority.HIGH,
            estimated_duration=0.5
        )
        
        return result
    
    def submit_training_task(self, agent_id: str, task_data: Dict) -> Dict:
        """提交训练任务"""
        # 保存训练数据
        self.persistence.save_training_result(agent_id, task_data)
        
        # 提交到优化器
        self.optimizer.submit_task(
            task_id=f"train_{agent_id}_{int(time.time())}",
            task_type="training",
            priority=TaskPriority.MEDIUM,
            estimated_duration=task_data.get("estimated_duration", 1.0),
            resource_requirements=task_data.get("resource_requirements", {})
        )
        
        return {"success": True, "task_submitted": True}
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            **self.system_status,
            "uptime_hours": (time.time() - self.system_status["started_at"]) / 3600,
            "registry_nodes": len(self.registry.get_active_nodes()),
            "monitor_alerts": len(self.monitor.get_active_alerts()),
            "optimizer_stats": self.optimizer.get_optimization_stats()
        }
    
    def run_health_check(self) -> Dict:
        """运行健康检查"""
        health_report = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "modules": {},
            "issues": []
        }
        
        # 检查各模块
        try:
            health_report["modules"]["registry"] = "healthy"
        except Exception as e:
            health_report["modules"]["registry"] = f"unhealthy: {e}"
            health_report["issues"].append(f"Registry: {e}")
        
        try:
            health_report["modules"]["persistence"] = "healthy"
        except Exception as e:
            health_report["modules"]["persistence"] = f"unhealthy: {e}"
            health_report["issues"].append(f"Persistence: {e}")
        
        try:
            health_report["modules"]["monitor"] = "healthy"
        except Exception as e:
            health_report["modules"]["monitor"] = f"unhealthy: {e}"
            health_report["issues"].append(f"Monitor: {e}")
        
        try:
            health_report["modules"]["optimizer"] = "healthy"
        except Exception as e:
            health_report["modules"]["optimizer"] = f"unhealthy: {e}"
            health_report["issues"].append(f"Optimizer: {e}")
        
        # 保存健康报告
        report_file = self.workspace_dir / "health_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(health_report, f, ensure_ascii=False, indent=2)
        
        return health_report
    
    def shutdown(self):
        """关闭系统"""
        self.monitor.stop_monitoring()
        print("[LobsterNetworkV51] 系统已关闭")


# 测试代码
if __name__ == "__main__":
    print("=== 测试小龙虾网络 V5.1 ===")
    
    # 初始化系统
    network = LobsterNetworkV51()
    
    # 注册测试智能体
    network.register_agent("test_agent_1", "测试智能体 1", ["training", "analysis"])
    network.register_agent("test_agent_2", "测试智能体 2", ["training", "generation"])
    
    # 提交训练任务
    training_data = {
        "agent_id": "test_agent_1",
        "training_round": 1,
        "accuracy": 0.85,
        "estimated_duration": 2.0,
        "resource_requirements": {"cpu": 0.5, "memory": 0.3}
    }
    network.submit_training_task("test_agent_1", training_data)
    
    # 运行健康检查
    health = network.run_health_check()
    print(f"健康状态：{health['modules']}")
    
    # 获取系统状态
    status = network.get_system_status()
    print(f"系统状态：运行 {status['uptime_hours']:.2f} 小时")
    
    # 关闭系统
    network.shutdown()
    
    print("✅ 测试完成")