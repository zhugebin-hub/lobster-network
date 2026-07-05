#!/usr/bin/env python3
"""
算力优化器
增强功能：
- 任务优先级调度
- 资源利用率监控
- 动态负载均衡
- 成本效益分析
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

class TaskPriority(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

class ComputeOptimizer:
    """算力优化器"""
    
    def __init__(self, workspace_dir: str = "workspace"):
        self.workspace_dir = Path(workspace_dir) / "compute"
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.task_queue: List[Dict] = []
        self.resource_usage: Dict[str, float] = {
            "cpu": 0.0,
            "memory": 0.0,
            "gpu": 0.0
        }
        self.optimization_history: List[Dict] = []
        self._lock = threading.RLock()
        
        # 优化配置
        self.config = {
            "max_concurrent_tasks": 5,
            "resource_threshold": 0.8,
            "optimization_interval": 300,  # 5 分钟
            "cost_model": {
                "cpu_hour": 0.05,
                "memory_gb_hour": 0.01,
                "gpu_hour": 0.50
            }
        }
        
        # 加载配置
        self._load_config()
        
        # 启动优化循环
        self._optimization_thread = threading.Thread(
            target=self._optimization_loop,
            daemon=True
        )
        self._optimization_thread.start()
        
        print(f"[ComputeOptimizer] 初始化完成，最大并发任务：{self.config['max_concurrent_tasks']}")
    
    def submit_task(self, task_id: str, task_type: str, priority: TaskPriority,
                   estimated_duration: float, resource_requirements: Dict = None) -> bool:
        """提交任务"""
        with self._lock:
            task = {
                "task_id": task_id,
                "task_type": task_type,
                "priority": priority.value,
                "priority_name": priority.name,
                "estimated_duration": estimated_duration,
                "resource_requirements": resource_requirements or {},
                "status": "pending",
                "submitted_at": time.time(),
                "started_at": None,
                "completed_at": None
            }
            
            self.task_queue.append(task)
            self._sort_task_queue()
            
            print(f"[ComputeOptimizer] 提交任务：{task_id} (优先级：{priority.name})")
            return True
    
    def get_optimal_schedule(self) -> List[Dict]:
        """获取最优调度方案"""
        with self._lock:
            # 基于优先级和资源需求的调度算法
            scheduled = []
            available_resources = self.resource_usage.copy()
            
            for task in self.task_queue:
                if task["status"] != "pending":
                    continue
                
                # 检查资源是否足够
                if self._check_resources(task, available_resources):
                    scheduled.append(task)
                    self._allocate_resources(task, available_resources)
            
            return scheduled
    
    def optimize_resource_allocation(self) -> Dict:
        """优化资源分配"""
        with self._lock:
            optimization_result = {
                "timestamp": time.time(),
                "datetime": datetime.now().isoformat(),
                "current_usage": self.resource_usage.copy(),
                "optimizations": []
            }
            
            # 分析当前资源利用率
            total_usage = sum(self.resource_usage.values())
            avg_usage = total_usage / len(self.resource_usage) if self.resource_usage else 0
            
            # 如果资源利用率过高，降低低优先级任务
            if avg_usage > self.config["resource_threshold"]:
                low_priority_tasks = [
                    t for t in self.task_queue
                    if t["status"] == "pending" and t["priority"] <= TaskPriority.LOW.value
                ]
                
                for task in low_priority_tasks[:2]:  # 最多暂停 2 个低优先级任务
                    task["status"] = "paused"
                    optimization_result["optimizations"].append({
                        "action": "pause_low_priority",
                        "task_id": task["task_id"],
                        "reason": "资源利用率高"
                    })
            
            # 如果资源利用率过低，增加并发任务
            elif avg_usage < 0.3:
                pending_tasks = [
                    t for t in self.task_queue
                    if t["status"] == "pending"
                ]
                
                if pending_tasks:
                    optimization_result["optimizations"].append({
                        "action": "increase_concurrency",
                        "task_id": pending_tasks[0]["task_id"],
                        "reason": "资源利用率低"
                    })
            
            self.optimization_history.append(optimization_result)
            self._save_optimization_history()
            
            return optimization_result
    
    def get_cost_estimate(self, task_duration_hours: float, resource_usage: Dict = None) -> Dict:
        """成本估算"""
        resource_usage = resource_usage or self.resource_usage
        
        cpu_cost = resource_usage.get("cpu", 0) * self.config["cost_model"]["cpu_hour"] * task_duration_hours
        memory_cost = resource_usage.get("memory", 0) * self.config["cost_model"]["memory_gb_hour"] * task_duration_hours
        gpu_cost = resource_usage.get("gpu", 0) * self.config["cost_model"]["gpu_hour"] * task_duration_hours
        
        total_cost = cpu_cost + memory_cost + gpu_cost
        
        return {
            "task_duration_hours": task_duration_hours,
            "cpu_cost": round(cpu_cost, 4),
            "memory_cost": round(memory_cost, 4),
            "gpu_cost": round(gpu_cost, 4),
            "total_cost": round(total_cost, 4),
            "cost_breakdown": {
                "cpu": cpu_cost,
                "memory": memory_cost,
                "gpu": gpu_cost
            }
        }
    
    def get_optimization_stats(self) -> Dict:
        """获取优化统计"""
        with self._lock:
            total_tasks = len(self.task_queue)
            pending_tasks = len([t for t in self.task_queue if t["status"] == "pending"])
            running_tasks = len([t for t in self.task_queue if t["status"] == "running"])
            completed_tasks = len([t for t in self.task_queue if t["status"] == "completed"])
            
            return {
                "total_tasks": total_tasks,
                "pending_tasks": pending_tasks,
                "running_tasks": running_tasks,
                "completed_tasks": completed_tasks,
                "resource_usage": self.resource_usage.copy(),
                "optimization_count": len(self.optimization_history),
                "config": self.config.copy()
            }
    
    def _sort_task_queue(self):
        """排序任务队列（高优先级在前）"""
        self.task_queue.sort(key=lambda t: t["priority"], reverse=True)
    
    def _check_resources(self, task: Dict, available_resources: Dict) -> bool:
        """检查资源是否足够"""
        requirements = task.get("resource_requirements", {})
        
        for resource, required in requirements.items():
            if available_resources.get(resource, 0) < required:
                return False
        
        return True
    
    def _allocate_resources(self, task: Dict, available_resources: Dict):
        """分配资源"""
        requirements = task.get("resource_requirements", {})
        
        for resource, required in requirements.items():
            available_resources[resource] = available_resources.get(resource, 0) - required
    
    def _optimization_loop(self):
        """优化循环"""
        while True:
            try:
                self.optimize_resource_allocation()
            except Exception as e:
                print(f"[ComputeOptimizer] 优化循环错误：{e}")
            time.sleep(self.config["optimization_interval"])
    
    def _save_optimization_history(self):
        """保存优化历史"""
        try:
            history_file = self.workspace_dir / "optimization_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "history": self.optimization_history[-100:],  # 保留最近 100 条
                    "last_update": time.time()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ComputeOptimizer] 保存优化历史失败：{e}")
    
    def _load_config(self):
        """加载配置"""
        config_file = self.workspace_dir / "optimizer_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                print(f"[ComputeOptimizer] 加载配置失败：{e}")


# 测试代码
if __name__ == "__main__":
    print("=== 测试算力优化器 ===")
    
    optimizer = ComputeOptimizer()
    
    # 提交测试任务
    optimizer.submit_task("task_1", "training", TaskPriority.HIGH, 2.0, {"cpu": 0.5, "memory": 0.3})
    optimizer.submit_task("task_2", "analysis", TaskPriority.MEDIUM, 1.5, {"cpu": 0.3, "memory": 0.2})
    optimizer.submit_task("task_3", "generation", TaskPriority.LOW, 3.0, {"cpu": 0.4, "gpu": 0.6})
    
    # 获取最优调度
    schedule = optimizer.get_optimal_schedule()
    print(f"最优调度：{len(schedule)} 个任务")
    
    # 成本估算
    cost = optimizer.get_cost_estimate(2.0)
    print(f"成本估算：{cost['total_cost']} 元/2 小时")
    
    # 获取统计
    stats = optimizer.get_optimization_stats()
    print(f"优化统计：{stats}")
    
    print("✅ 测试完成")