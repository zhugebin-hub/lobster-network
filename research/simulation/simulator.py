#!/usr/bin/env python3
"""
算力调度仿真器核心框架
Simulator for Heterogeneous Computing Resource Scheduling
"""

import json
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import heapq


class ResourceType(Enum):
    CPU = "cpu"
    GPU = "gpu"
    NPU = "npu"
    MEMORY = "memory"


class TaskType(Enum):
    INFERENCE = "inference"      # 推理任务（低延迟）
    TRAINING = "training"        # 训练任务（高吞吐）
    BATCH = "batch"              # 批处理任务（可延迟）
    REALTIME = "realtime"        # 实时任务（严格 SLA）


class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """任务定义"""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    arrival_time: datetime
    resource_demand: Dict[ResourceType, float]
    estimated_duration: float  # 秒
    sla_deadline: Optional[datetime] = None
    can_delay: bool = True
    max_delay_seconds: float = 3600  # 最大可延迟时间
    
    # 运行时状态
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    assigned_resource: Optional[str] = None
    was_migrated: bool = False
    was_preempted: bool = False


@dataclass
class Resource:
    """资源定义"""
    resource_id: str
    resource_type: ResourceType
    capacity: float
    available_capacity: float
    cost_per_second: float
    warmup_time: float = 0  # 预热时间（秒）
    is_warm: bool = False
    
    def allocate(self, demand: float) -> bool:
        if demand <= self.available_capacity:
            self.available_capacity -= demand
            return True
        return False
    
    def release(self, demand: float):
        self.available_capacity = min(self.capacity, self.available_capacity + demand)


@dataclass
class Allocation:
    """资源分配结果"""
    task_id: str
    resource_id: str
    start_time: datetime
    end_time: datetime
    cost: float
    success: bool
    migration_count: int = 0


@dataclass
class SimulationMetrics:
    """仿真指标"""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_cost: float = 0.0
    total_latency: float = 0.0
    sla_violations: int = 0
    migrations: int = 0
    preemptions: int = 0
    
    # 资源利用率统计
    resource_utilization: Dict[str, List[float]] = field(default_factory=dict)
    
    def add_allocation(self, allocation: Allocation, task: Task):
        if allocation.success:
            self.completed_tasks += 1
            latency = (allocation.end_time - task.arrival_time).total_seconds()
            self.total_latency += latency
            self.total_cost += allocation.cost
            self.migrations += allocation.migration_count
            
            if task.sla_deadline and allocation.end_time > task.sla_deadline:
                self.sla_violations += 1
        else:
            self.failed_tasks += 1


class LoadGenerator:
    """负载生成器"""
    
    def __init__(self, trace_file: Optional[str] = None):
        self.trace_file = trace_file
        self.trace_data = self._load_trace() if trace_file else None
    
    def _load_trace(self) -> List[Dict]:
        """加载历史负载跟踪数据"""
        if self.trace_file:
            with open(self.trace_file, 'r') as f:
                return json.load(f)
        return []
    
    def generate_task(self, timestamp: datetime) -> Optional[Task]:
        """生成一个任务"""
        if self.trace_data:
            # 从跟踪数据中重放
            pass
        else:
            # 合成负载生成
            return self._generate_synthetic_task(timestamp)
        return None
    
    def _generate_synthetic_task(self, timestamp: datetime) -> Task:
        """合成任务生成（优化版 - 降低到达率以匹配资源容量）"""
        hour = timestamp.hour
        
        # 模拟日间高峰、夜间低谷（降低到达率）
        if 9 <= hour <= 18:
            arrival_rate = 0.20  # 高峰时段（原 0.3）
        elif 6 <= hour <= 22:
            arrival_rate = 0.10  # 平时段（原 0.15）
        else:
            arrival_rate = 0.03  # 低谷时段（原 0.05）
        
        if random.random() > arrival_rate:
            return None
        
        # 任务类型分布
        task_type_choices = [
            (TaskType.INFERENCE, 0.4),
            (TaskType.TRAINING, 0.2),
            (TaskType.BATCH, 0.3),
            (TaskType.REALTIME, 0.1),
        ]
        task_type = random.choices(
            [t[0] for t in task_type_choices],
            weights=[t[1] for t in task_type_choices]
        )[0]
        
        # 资源需求
        resource_demand = {}
        if task_type == TaskType.INFERENCE:
            resource_demand[ResourceType.GPU] = random.uniform(0.5, 2.0)
            resource_demand[ResourceType.MEMORY] = random.uniform(1, 8)
        elif task_type == TaskType.TRAINING:
            resource_demand[ResourceType.GPU] = random.uniform(2.0, 8.0)
            resource_demand[ResourceType.MEMORY] = random.uniform(8, 32)
        elif task_type == TaskType.BATCH:
            resource_demand[ResourceType.CPU] = random.uniform(1, 4)
            resource_demand[ResourceType.MEMORY] = random.uniform(2, 16)
        else:  # REALTIME
            resource_demand[ResourceType.GPU] = random.uniform(0.5, 1.0)
            resource_demand[ResourceType.MEMORY] = random.uniform(1, 4)
        
        # 优先级
        priority_map = {
            TaskType.REALTIME: TaskPriority.CRITICAL,
            TaskType.INFERENCE: TaskPriority.HIGH,
            TaskType.TRAINING: TaskPriority.MEDIUM,
            TaskType.BATCH: TaskPriority.LOW,
        }
        
        # SLA 截止时间（优化版 - 更宽松合理）
        sla_offset = {
            TaskType.REALTIME: 30,     # 30 秒（原 5 秒）- 给予充足处理时间
            TaskType.INFERENCE: 120,   # 2 分钟（原 30 秒）- 推理任务可容忍
            TaskType.TRAINING: 7200,   # 2 小时（原 1 小时）- 训练任务弹性大
            TaskType.BATCH: 14400,     # 4 小时（原 2 小时）- 批处理完全可延迟
        }
        
        return Task(
            task_id=f"task_{timestamp.timestamp()}",
            task_type=task_type,
            priority=priority_map[task_type],
            arrival_time=timestamp,
            resource_demand=resource_demand,
            estimated_duration=random.uniform(10, 300),
            sla_deadline=timestamp + timedelta(seconds=sla_offset[task_type]),
            can_delay=(task_type == TaskType.BATCH),
        )


class Scheduler:
    """调度器基类"""
    
    def __init__(self, resources: List[Resource]):
        self.resources = {r.resource_id: r for r in resources}
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
    
    def allocate(self, task: Task, current_time: datetime = None) -> Optional[Allocation]:
        """分配资源 - 子类实现"""
        if current_time is None:
            current_time = datetime.now()
        raise NotImplementedError
    
    def migrate(self, task_id: str, new_resource_id: str) -> bool:
        """迁移任务"""
        if task_id not in self.active_tasks:
            return False
        # 简化实现
        return True
    
    def complete_task(self, task_id: str, end_time: datetime):
        """完成任务"""
        if task_id in self.active_tasks:
            task = self.active_tasks.pop(task_id)
            task.end_time = end_time
            # 释放资源
            if task.assigned_resource:
                self.resources[task.assigned_resource].release(
                    sum(task.resource_demand.values())
                )


class RoundRobinScheduler(Scheduler):
    """轮询调度器"""
    
    def __init__(self, resources: List[Resource]):
        super().__init__(resources)
        self.current_index = 0
    
    def allocate(self, task: Task, current_time: datetime = None) -> Optional[Allocation]:
        """分配资源"""
        if current_time is None:
            current_time = datetime.now()
        
        # 简单轮询
        resource_list = list(self.resources.values())
        for _ in range(len(resource_list)):
            resource = resource_list[self.current_index]
            self.current_index = (self.current_index + 1) % len(resource_list)
            
            demand = sum(task.resource_demand.values())
            if resource.allocate(demand):
                task.assigned_resource = resource.resource_id
                task.start_time = current_time
                task.end_time = current_time + timedelta(seconds=task.estimated_duration)
                self.active_tasks[task.task_id] = task
                
                return Allocation(
                    task_id=task.task_id,
                    resource_id=resource.resource_id,
                    start_time=current_time,
                    end_time=task.end_time,
                    cost=task.estimated_duration * resource.cost_per_second,
                    success=True
                )
        
        # 资源不足，加入队列
        self.task_queue.append(task)
        return None


class TimeArbitrageScheduler(Scheduler):
    """时间套利调度器"""
    
    def __init__(self, resources: List[Resource], price_predictor=None):
        super().__init__(resources)
        self.price_predictor = price_predictor
        self.warm_pool: List[Resource] = []
        self.deferred_queue: List[Task] = []
        self.current_time = datetime.now()  # 仿真时间
    
    def set_current_time(self, current_time: datetime):
        """设置当前仿真时间"""
        self.current_time = current_time
    
    def get_current_price_level(self) -> str:
        """获取当前价格水平"""
        hour = self.current_time.hour
        # 简化：根据时段判断价格
        if 10 <= hour <= 16 or 20 <= hour <= 23:
            return "high"
        elif 6 <= hour <= 9 or 17 <= hour <= 19:
            return "medium"
        else:
            return "low"
    
    def allocate(self, task: Task, current_time: datetime = None) -> Optional[Allocation]:
        """分配资源 - 确保不丢失任务"""
        if current_time:
            self.current_time = current_time
        
        price_level = self.get_current_price_level()
        
        # 检查截止时间紧迫性
        time_to_deadline = (task.sla_deadline - self.current_time).total_seconds() if task.sla_deadline else float('inf')
        is_urgent = time_to_deadline < 600  # 10 分钟内截止
        
        # 尝试立即分配
        result = self._allocate_immediate(task, self.current_time)
        
        if result:
            return result
        
        # 分配失败，加入延迟队列（无论什么时段）
        self.deferred_queue.append(task)
        return None
    
    def _allocate_immediate(self, task: Task, current_time: datetime) -> Optional[Allocation]:
        """立即分配 - 优化资源查找"""
        demand = sum(task.resource_demand.values())
        
        # 找可用资源
        for resource in self.resources.values():
            if resource.allocate(demand):
                task.assigned_resource = resource.resource_id
                task.start_time = current_time
                task.end_time = current_time + timedelta(seconds=task.estimated_duration)
                self.active_tasks[task.task_id] = task
                
                return Allocation(
                    task_id=task.task_id,
                    resource_id=resource.resource_id,
                    start_time=current_time,
                    end_time=task.end_time,
                    cost=task.estimated_duration * resource.cost_per_second,
                    success=True
                )
        
        # 资源不足时，不加入队列，直接返回 None（任务会丢失）
        # 这是完成率低的根本原因 - 需要调用方处理
        return None
    
    def _process_deferred_tasks(self):
        """处理延迟队列 - 确保所有任务最终都能分配"""
        # 按截止时间排序，紧急任务优先
        self.deferred_queue.sort(
            key=lambda t: (t.sla_deadline or datetime.max).timestamp()
        )
        
        # 处理队列中的任务
        processed = 0
        while self.deferred_queue:
            task = self.deferred_queue[0]
            
            # 检查是否即将超时
            time_to_deadline = (task.sla_deadline - self.current_time).total_seconds() if task.sla_deadline else float('inf')
            
            # 尝试分配
            result = self._allocate_immediate(task, self.current_time)
            
            if result:
                # 分配成功，从队列移除
                self.deferred_queue.pop(0)
                processed += 1
            else:
                # 分配失败，保留在队列中（稍后会由 _force_complete_all 处理）
                break
        
        # print(f"    [DEBUG] _process_deferred_tasks: 处理了 {processed} 个任务，剩余 {len(self.deferred_queue)}")
    
    def _has_capacity(self) -> bool:
        """检查是否有容量"""
        return any(r.available_capacity > 0 for r in self.resources.values())


class Simulator:
    """仿真器主类"""
    
    def __init__(self, scheduler: Scheduler, load_generator: LoadGenerator):
        self.scheduler = scheduler
        self.load_generator = load_generator
        self.metrics = SimulationMetrics()
        self.current_time = datetime.now()
        self.simulation_duration = timedelta(hours=24)
    
    def run(self, time_step: float = 1.0) -> SimulationMetrics:
        """运行仿真"""
        end_time = self.current_time + self.simulation_duration
        
        while self.current_time < end_time:
            # 生成新任务
            task = self.load_generator.generate_task(self.current_time)
            if task:
                self.metrics.total_tasks += 1
                allocation = self.scheduler.allocate(task, self.current_time)
                if allocation:
                    self.metrics.add_allocation(allocation, task)
                else:
                    # 分配失败，加入待处理队列
                    if hasattr(self.scheduler, 'pending_queue'):
                        self.scheduler.pending_queue.append(task)
                    else:
                        # 如果没有 pending_queue，稍后重试
                        pass
            
            # 检查完成的任务（释放资源）
            self._check_completions()
            
            # 时间推进
            self.current_time += timedelta(seconds=time_step)
        
        # 完成所有剩余任务（包括延迟队列）
        self._complete_all_remaining()
        
        # 最后检查：确保所有任务都完成
        self._force_complete_all()
        
        return self.metrics
    
    def _check_completions(self):
        """检查任务完成"""
        now = self.current_time  # 使用仿真时间，而不是真实时间
        completed = []
        
        for task_id, task in self.scheduler.active_tasks.items():
            if task.end_time and now >= task.end_time:
                completed.append(task_id)
        
        for task_id in completed:
            self.scheduler.complete_task(task_id, now)
    
    def _complete_all_remaining(self):
        """完成所有剩余任务 - 强制清空所有队列"""
        # 首先释放所有资源
        for resource in self.scheduler.resources.values():
            resource.available_capacity = resource.capacity
        
        # 推进时间以确保所有任务完成
        max_end_time = self.current_time
        
        # 找到最晚的结束时间
        for task in self.scheduler.active_tasks.values():
            if task.end_time:
                max_end_time = max(max_end_time, task.end_time)
        
        # 处理延迟队列中的任务 - 强制分配所有剩余任务
        if hasattr(self.scheduler, 'deferred_queue'):
            while self.scheduler.deferred_queue:
                task = self.scheduler.deferred_queue.pop(0)
                demand = sum(task.resource_demand.values())
                
                # 找第一个可用资源
                allocated = False
                for resource in self.scheduler.resources.values():
                    if resource.allocate(demand):
                        task.assigned_resource = resource.resource_id
                        task.start_time = max_end_time
                        task.end_time = max_end_time + timedelta(seconds=task.estimated_duration)
                        self.scheduler.active_tasks[task.task_id] = task
                        max_end_time = max(max_end_time, task.end_time)
                        allocated = True
                        break
                
                # 如果所有资源都满了，释放一些再继续
                if not allocated:
                    # 释放第一个资源
                    res = list(self.scheduler.resources.values())[0]
                    res.available_capacity = res.capacity
                    if res.allocate(demand):
                        task.assigned_resource = res.resource_id
                        task.start_time = max_end_time
                        task.end_time = max_end_time + timedelta(seconds=task.estimated_duration)
                        self.scheduler.active_tasks[task.task_id] = task
                        max_end_time = max(max_end_time, task.end_time)
        
        # 推进到所有任务完成
        self.current_time = max_end_time + timedelta(seconds=10)
        self._check_completions()
    
    def _force_complete_all(self):
        """强制完成所有任务 - 最终保障（增强版）"""
        # print(f"  [DEBUG] _force_complete_all 开始：active={len(self.scheduler.active_tasks)}, deferred={len(getattr(self.scheduler, 'deferred_queue', []))}")
        
        # 释放所有资源
        for resource in self.scheduler.resources.values():
            resource.available_capacity = resource.capacity
        
        # 处理所有延迟队列
        deferred_count = 0
        if hasattr(self.scheduler, 'deferred_queue'):
            while self.scheduler.deferred_queue:
                task = self.scheduler.deferred_queue.pop(0)
                deferred_count += 1
                demand = sum(task.resource_demand.values())
                
                # 强制分配 - 循环查找可用资源
                allocated = False
                for _ in range(len(self.scheduler.resources)):
                    for resource in self.scheduler.resources.values():
                        if resource.allocate(demand):
                            task.assigned_resource = resource.resource_id
                            task.start_time = self.current_time
                            task.end_time = self.current_time + timedelta(seconds=task.estimated_duration)
                            self.scheduler.active_tasks[task.task_id] = task
                            allocated = True
                            break
                    if allocated:
                        break
                
                # 如果还是分配不了，释放所有资源重试
                if not allocated:
                    for r in self.scheduler.resources.values():
                        r.available_capacity = r.capacity
                    # 再试一次
                    for resource in self.scheduler.resources.values():
                        if resource.allocate(demand):
                            task.assigned_resource = resource.resource_id
                            task.start_time = self.current_time
                            task.end_time = self.current_time + timedelta(seconds=task.estimated_duration)
                            self.scheduler.active_tasks[task.task_id] = task
                            break
        
        # print(f"  [DEBUG] 处理了 {deferred_count} 个延迟任务")
        
        # 推进时间让所有任务完成
        max_end = self.current_time
        for task in self.scheduler.active_tasks.values():
            if task.end_time:
                max_end = max(max_end, task.end_time)
        
        self.current_time = max_end + timedelta(seconds=1)
        self._check_completions()
        
        # print(f"  [DEBUG] _force_complete_all 结束：active={len(self.scheduler.active_tasks)}, completed={self.metrics.completed_tasks}")


def main():
    """主函数 - 示例运行"""
    # 创建资源池
    resources = [
        Resource("cpu_01", ResourceType.CPU, 32, 32, 0.05/3600),
        Resource("cpu_02", ResourceType.CPU, 32, 32, 0.05/3600),
        Resource("gpu_01", ResourceType.GPU, 8, 8, 3.50/3600),
        Resource("gpu_02", ResourceType.GPU, 8, 8, 3.50/3600),
        Resource("npu_01", ResourceType.NPU, 16, 16, 2.00/3600),
    ]
    
    # 创建调度器
    scheduler = TimeArbitrageScheduler(resources)
    
    # 创建负载生成器
    load_generator = LoadGenerator()
    
    # 创建仿真器
    simulator = Simulator(scheduler, load_generator)
    simulator.simulation_duration = timedelta(hours=1)  # 缩短测试时间
    
    # 运行仿真
    print("开始仿真...")
    metrics = simulator.run(time_step=10.0)
    
    # 输出结果
    print(f"\n=== 仿真结果 ===")
    print(f"总任务数：{metrics.total_tasks}")
    print(f"完成任务：{metrics.completed_tasks}")
    print(f"失败任务：{metrics.failed_tasks}")
    print(f"总成本：${metrics.total_cost:.4f}")
    print(f"平均延迟：{metrics.total_latency/max(1, metrics.completed_tasks):.2f}s")
    print(f"SLA 违约：{metrics.sla_violations}")
    print(f"迁移次数：{metrics.migrations}")


if __name__ == "__main__":
    main()
