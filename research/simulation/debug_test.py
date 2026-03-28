#!/usr/bin/env python3
"""调试测试 - 追踪任务去向"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from simulator import (
    Simulator, Resource, ResourceType, TaskType, TaskPriority,
    LoadGenerator, TimeArbitrageScheduler, SimulationMetrics
)
from datetime import timedelta

# 创建资源
resources = [
    Resource("cpu_01", ResourceType.CPU, 32, 32, 0.05/3600),
    Resource("cpu_02", ResourceType.CPU, 32, 32, 0.05/3600),
    Resource("gpu_01", ResourceType.GPU, 8, 8, 3.50/3600),
    Resource("gpu_02", ResourceType.GPU, 8, 8, 3.50/3600),
]

# 创建调度器
scheduler = TimeArbitrageScheduler(resources)

# 创建负载生成器
load_generator = LoadGenerator()

# 创建仿真器
simulator = Simulator(scheduler, load_generator)
simulator.simulation_duration = timedelta(hours=2)

# 运行仿真
print("开始仿真...")
metrics = simulator.run(time_step=60.0)

print(f"\n=== 结果 ===")
print(f"总任务数：{metrics.total_tasks}")
print(f"完成任务：{metrics.completed_tasks}")
print(f"失败任务：{metrics.failed_tasks}")
print(f"延迟队列剩余：{len(scheduler.deferred_queue)}")
print(f"任务队列剩余：{len(scheduler.task_queue)}")
print(f"活跃任务：{len(scheduler.active_tasks)}")
print(f"总成本：${metrics.total_cost:.4f}")
