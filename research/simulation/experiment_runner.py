#!/usr/bin/env python3
"""
仿真实验运行器
Experiment Runner for Scheduling Algorithms

运行对比实验：
- Round-Robin (基线)
- Priority (优先级)
- Time-Arbitrage (时间套利)
- RL (强化学习，待实现)
"""

import json
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# 导入仿真器
sys.path.insert(0, str(Path(__file__).parent))
from simulator import (
    Simulator, Task, Resource, ResourceType, TaskType, TaskPriority,
    LoadGenerator, RoundRobinScheduler, TimeArbitrageScheduler,
    SimulationMetrics
)


class ExperimentRunner:
    """实验运行器"""
    
    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent / "results"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
    
    def create_resource_pool(self) -> List[Resource]:
        """创建资源池（优化版 - 增加容量降低竞争）"""
        return [
            # CPU: 4→6 核，降低 CPU 任务竞争
            Resource("cpu_01", ResourceType.CPU, 32, 32, 0.05/3600),
            Resource("cpu_02", ResourceType.CPU, 32, 32, 0.05/3600),
            Resource("cpu_03", ResourceType.CPU, 32, 32, 0.05/3600),
            Resource("cpu_04", ResourceType.CPU, 32, 32, 0.05/3600),
            Resource("cpu_05", ResourceType.CPU, 32, 32, 0.05/3600),
            Resource("cpu_06", ResourceType.CPU, 32, 32, 0.05/3600),
            
            # GPU: 3→4 卡，降低 GPU 任务竞争
            Resource("gpu_01", ResourceType.GPU, 8, 8, 3.50/3600),
            Resource("gpu_02", ResourceType.GPU, 8, 8, 3.50/3600),
            Resource("gpu_03", ResourceType.GPU, 8, 8, 3.50/3600),
            Resource("gpu_04", ResourceType.GPU, 8, 8, 3.50/3600),
            
            # NPU: 2→3 卡
            Resource("npu_01", ResourceType.NPU, 16, 16, 2.00/3600),
            Resource("npu_02", ResourceType.NPU, 16, 16, 2.00/3600),
            Resource("npu_03", ResourceType.NPU, 16, 16, 2.00/3600),
            
            # Memory: 容量翻倍
            Resource("mem_01", ResourceType.MEMORY, 256, 256, 0.01/3600),
            Resource("mem_02", ResourceType.MEMORY, 256, 256, 0.01/3600),
        ]
    
    def run_single_experiment(
        self,
        scheduler_class,
        scheduler_name: str,
        duration_hours: int = 24,
        time_step: float = 60.0,
        seed: int = 42
    ) -> SimulationMetrics:
        """
        运行单次实验
        
        参数:
            scheduler_class: 调度器类
            scheduler_name: 调度器名称
            duration_hours: 仿真时长（小时）
            time_step: 时间步长（秒）
            seed: 随机种子
        """
        random.seed(seed)
        
        # 创建资源池
        resources = self.create_resource_pool()
        
        # 创建调度器
        scheduler = scheduler_class(resources)
        
        # 创建负载生成器
        load_generator = LoadGenerator()
        
        # 创建仿真器
        simulator = Simulator(scheduler, load_generator)
        simulator.simulation_duration = timedelta(hours=duration_hours)
        
        # 运行仿真
        print(f"运行实验：{scheduler_name} ({duration_hours}小时)...")
        metrics = simulator.run(time_step=time_step)
        
        return metrics
    
    def compare_schedulers(
        self,
        duration_hours: int = 24,
        repetitions: int = 3
    ) -> Dict:
        """
        对比不同调度器
        
        参数:
            duration_hours: 仿真时长
            repetitions: 重复次数
        """
        schedulers = [
            (RoundRobinScheduler, "Round-Robin"),
            (TimeArbitrageScheduler, "Time-Arbitrage"),
        ]
        
        results = {}
        
        for scheduler_class, name in schedulers:
            print(f"\n{'='*60}")
            print(f"调度器：{name}")
            print(f"{'='*60}")
            
            metrics_list = []
            
            for i in range(repetitions):
                metrics = self.run_single_experiment(
                    scheduler_class,
                    name,
                    duration_hours,
                    seed=42+i
                )
                metrics_list.append(metrics)
            
            # 计算平均指标
            avg_metrics = self._average_metrics(metrics_list)
            results[name] = avg_metrics
            
            # 打印结果
            self._print_metrics(name, avg_metrics)
        
        # 对比分析
        self._compare_results(results)
        
        # 保存结果
        self._save_results(results, duration_hours, repetitions)
        
        return results
    
    def _average_metrics(self, metrics_list: List[SimulationMetrics]) -> Dict:
        """计算平均指标"""
        n = len(metrics_list)
        
        return {
            "total_tasks": sum(m.total_tasks for m in metrics_list) / n,
            "completed_tasks": sum(m.completed_tasks for m in metrics_list) / n,
            "failed_tasks": sum(m.failed_tasks for m in metrics_list) / n,
            "total_cost": sum(m.total_cost for m in metrics_list) / n,
            "total_latency": sum(m.total_latency for m in metrics_list) / n,
            "sla_violations": sum(m.sla_violations for m in metrics_list) / n,
            "migrations": sum(m.migrations for m in metrics_list) / n,
        }
    
    def _print_metrics(self, name: str, metrics: Dict):
        """打印指标"""
        print(f"\n{name} 结果:")
        print(f"  总任务数：{metrics['total_tasks']:.0f}")
        print(f"  完成任务：{metrics['completed_tasks']:.0f}")
        print(f"  失败任务：{metrics['failed_tasks']:.0f}")
        print(f"  总成本：${metrics['total_cost']:.4f}")
        print(f"  平均延迟：{metrics['total_latency']/max(1, metrics['completed_tasks']):.2f}s")
        print(f"  SLA 违约：{metrics['sla_violations']:.0f}")
        print(f"  迁移次数：{metrics['migrations']:.0f}")
    
    def _compare_results(self, results: Dict):
        """对比结果"""
        print(f"\n{'='*60}")
        print("对比分析")
        print(f"{'='*60}")
        
        baseline_cost = results["Round-Robin"]["total_cost"]
        
        for name, metrics in results.items():
            if name == "Round-Robin":
                continue
            
            cost_saving = (baseline_cost - metrics["total_cost"]) / baseline_cost * 100
            print(f"\n{name} vs Round-Robin:")
            print(f"  成本节省：${baseline_cost - metrics['total_cost']:.4f} ({cost_saving:.1f}%)")
            
            if metrics["sla_violations"] < results["Round-Robin"]["sla_violations"]:
                improvement = results["Round-Robin"]["sla_violations"] - metrics["sla_violations"]
                print(f"  SLA 违约减少：{improvement:.0f} 次")
    
    def _save_results(self, results: Dict, duration: int, repetitions: int):
        """保存结果"""
        output_file = self.output_dir / f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "duration_hours": duration,
            "repetitions": repetitions,
            "results": results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n结果已保存到：{output_file}")
    
    def generate_chart_data(self, results: Dict):
        """生成图表数据（用于可视化）"""
        chart_data = {
            "cost_comparison": {
                "labels": list(results.keys()),
                "values": [r["total_cost"] for r in results.values()]
            },
            "completion_rate": {
                "labels": list(results.keys()),
                "values": [
                    r["completed_tasks"] / max(1, r["total_tasks"]) * 100
                    for r in results.values()
                ]
            },
            "sla_violations": {
                "labels": list(results.keys()),
                "values": [r["sla_violations"] for r in results.values()]
            }
        }
        
        output_file = self.output_dir / "chart_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, indent=2)
        
        print(f"图表数据已保存到：{output_file}")
        return chart_data


def main():
    """主函数"""
    print("=" * 60)
    print("🧪 算力调度仿真实验")
    print("=" * 60)
    
    # 创建实验运行器
    runner = ExperimentRunner()
    
    # 运行对比实验
    results = runner.compare_schedulers(
        duration_hours=12,  # 12 小时仿真
        repetitions=3       # 重复 3 次
    )
    
    # 生成图表数据
    runner.generate_chart_data(results)
    
    print(f"\n{'='*60}")
    print("✅ 实验完成")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
