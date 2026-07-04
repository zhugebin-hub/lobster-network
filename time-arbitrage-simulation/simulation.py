#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
时间套利调度用于异构云计算 - 仿真实验
Time Arbitrage Scheduling for Heterogeneous Cloud Computing - Simulation

作者：陈怡
AI 助手：小龙虾-OpenClaw
日期：2026 年 4 月 16 日
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
import random

# 设置随机种子以保证结果可复现
np.random.seed(42)
random.seed(42)

# ============== 配置参数 ==============
CONFIG = {
    'num_tasks': 100,          # 任务数量
    'num_cloud_providers': 5,  # 云服务商数量
    'time_slots': 24,          # 时间槽（小时）
    'simulation_days': 7,      # 仿真天数
}

# ============== 云服务商配置 ==============
CLOUD_PROVIDERS = {
    'AWS': {'base_price': 0.10, 'volatility': 0.3, 'performance': 1.0},
    'Azure': {'base_price': 0.09, 'volatility': 0.25, 'performance': 0.95},
    'GCP': {'base_price': 0.08, 'volatility': 0.35, 'performance': 0.9},
    'Aliyun': {'base_price': 0.07, 'volatility': 0.4, 'performance': 0.85},
    'Tencent': {'base_price': 0.06, 'volatility': 0.45, 'performance': 0.8},
}

# ============== 电价模型（受电网启发） ==============
# 高峰时段：10:00-16:00, 20:00-23:00 → 高价
# 平时段：6:00-9:00, 17:00-19:00 → 中价
# 低谷时段：其他时间（夜间） → 低价

# ============== 生成时间套利价格模型 ==============
def generate_spot_prices(days=7, hours_per_day=24):
    """
    生成现货价格序列，模拟云资源的时变价格
    考虑因素：基础价格、时段因子、随机波动
    """
    total_hours = days * hours_per_day
    prices = {}
    
    for provider, config in CLOUD_PROVIDERS.items():
        base = config['base_price']
        vol = config['volatility']
        
        # 生成基础价格序列
        price_series = np.zeros(total_hours)
        
        for t in range(total_hours):
            hour_of_day = t % 24
            
            # 时段因子：夜间便宜，白天贵
            if 0 <= hour_of_day < 8:
                time_factor = 0.7  # 夜间折扣
            elif 8 <= hour_of_day < 18:
                time_factor = 1.2  # 白天溢价
            else:
                time_factor = 1.0  # 晚间正常
            
            # 周末因子
            day_of_week = t // 24
            if day_of_week >= 5:  # 周末
                time_factor *= 0.8
            
            # 随机波动
            random_factor = np.random.normal(1.0, vol)
            random_factor = max(0.5, min(2.0, random_factor))  # 限制波动范围
            
            price_series[t] = base * time_factor * random_factor
        
        prices[provider] = price_series
    
    return prices

# ============== 任务生成模型 ==============
def generate_tasks(num_tasks=100):
    """
    生成任务队列，每个任务包含：
    - 计算需求（CPU 小时）
    - 内存需求（GB）
    - 截止时间（小时）
    - 优先级
    """
    tasks = []
    
    for i in range(num_tasks):
        task = {
            'id': i,
            'cpu_hours': np.random.exponential(10),  # CPU 小时，指数分布
            'memory_gb': np.random.uniform(1, 32),    # 内存 GB
            'deadline': np.random.randint(12, 168),   # 截止时间（12 小时 -7 天）
            'priority': np.random.choice(['high', 'medium', 'low'], p=[0.2, 0.5, 0.3]),
            'data_size_gb': np.random.exponential(5),  # 数据量
        }
        tasks.append(task)
    
    return tasks

# ============== 调度算法 ==============
class TimeArbitrageScheduler:
    """
    时间套利调度器
    核心思想：在价格低时执行更多任务，价格高时减少执行
    """
    
    def __init__(self, prices, tasks):
        self.prices = prices
        self.tasks = tasks
        self.schedule = []
        self.costs = []
        
    def schedule_greedy(self):
        """
        贪婪调度：总是选择当前最便宜的云服务商
        """
        total_cost = 0
        schedule = []
        
        for task in self.tasks:
            # 找到当前最便宜的提供商
            best_provider = None
            best_price = float('inf')
            
            for provider, price_series in self.prices.items():
                current_price = price_series[0] / CLOUD_PROVIDERS[provider]['performance']
                if current_price < best_price:
                    best_price = current_price
                    best_provider = provider
            
            # 计算任务成本
            task_cost = task['cpu_hours'] * best_price
            total_cost += task_cost
            
            schedule.append({
                'task_id': task['id'],
                'provider': best_provider,
                'cost': task_cost,
                'start_time': 0,
            })
        
        self.schedule = schedule
        self.costs.append(total_cost)
        return total_cost, schedule
    
    def schedule_time_arbitrage(self, look_ahead=24):
        """
        时间套利调度：考虑未来价格趋势，优化调度
        look_ahead: 向前看多少小时
        """
        total_cost = 0
        schedule = []
        current_time = 0
        
        # 按优先级排序任务
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_tasks = sorted(self.tasks, key=lambda x: priority_order[x['priority']])
        
        for task in sorted_tasks:
            # 寻找最优执行时间窗口
            best_provider = None
            best_time = None
            best_price = float('inf')
            
            for t in range(current_time, min(current_time + look_ahead, len(list(self.prices.values())[0]))):
                for provider, price_series in self.prices.items():
                    perf = CLOUD_PROVIDERS[provider]['performance']
                    effective_price = price_series[t] / perf
                    
                    if effective_price < best_price and t < task['deadline']:
                        best_price = effective_price
                        best_provider = provider
                        best_time = t
            
            if best_provider is None:
                # 如果没有找到合适时间，立即执行
                best_time = min(current_time, len(list(self.prices.values())[0]) - 1)
                best_provider = min(self.prices.keys(), 
                                   key=lambda p: self.prices[p][best_time] / CLOUD_PROVIDERS[p]['performance'])
                best_price = self.prices[best_provider][best_time] / CLOUD_PROVIDERS[best_provider]['performance']
            
            # 计算任务成本
            task_cost = task['cpu_hours'] * best_price
            total_cost += task_cost
            
            schedule.append({
                'task_id': task['id'],
                'provider': best_provider,
                'cost': task_cost,
                'start_time': best_time,
                'deadline': task['deadline'],
                'priority': task['priority'],
            })
            
            # 更新时间
            current_time = max(current_time, best_time) + 1
        
        self.schedule = schedule
        self.costs.append(total_cost)
        return total_cost, schedule
    
    def schedule_ml_predicted(self, look_ahead=24):
        """
        基于 ML 预测的调度（简化版：使用移动平均预测）
        """
        total_cost = 0
        schedule = []
        current_time = 0
        
        # 计算移动平均价格
        predicted_prices = {}
        for provider, price_series in self.prices.items():
            # 简单移动平均预测
            window = 6
            predicted = np.convolve(price_series, np.ones(window)/window, mode='same')
            predicted_prices[provider] = predicted
        
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_tasks = sorted(self.tasks, key=lambda x: priority_order[x['priority']])
        
        for task in sorted_tasks:
            best_provider = None
            best_time = None
            best_price = float('inf')
            
            for t in range(current_time, min(current_time + look_ahead, len(list(predicted_prices.values())[0]))):
                for provider, pred_series in predicted_prices.items():
                    perf = CLOUD_PROVIDERS[provider]['performance']
                    effective_price = pred_series[t] / perf
                    
                    if effective_price < best_price and t < task['deadline']:
                        best_price = effective_price
                        best_provider = provider
                        best_time = t
            
            if best_provider is None:
                best_time = min(current_time, len(list(predicted_prices.values())[0]) - 1)
                best_provider = min(predicted_prices.keys(), 
                                   key=lambda p: predicted_prices[p][best_time] / CLOUD_PROVIDERS[p]['performance'])
                best_price = predicted_prices[best_provider][best_time] / CLOUD_PROVIDERS[best_provider]['performance']
            
            task_cost = task['cpu_hours'] * best_price
            total_cost += task_cost
            
            schedule.append({
                'task_id': task['id'],
                'provider': best_provider,
                'cost': task_cost,
                'start_time': best_time,
                'deadline': task['deadline'],
                'priority': task['priority'],
            })
            
            current_time = max(current_time, best_time) + 1
        
        self.schedule = schedule
        self.costs.append(total_cost)
        return total_cost, schedule

# ============== 可视化函数 ==============
def plot_price_trends(prices, save_path='price_trends.png'):
    """绘制价格趋势图"""
    plt.figure(figsize=(14, 7))
    
    for provider, price_series in prices.items():
        plt.plot(price_series, label=provider, alpha=0.7)
    
    plt.xlabel('Time (hours)')
    plt.ylabel('Price ($/CPU-hour)')
    plt.title('Cloud Provider Spot Price Trends (7 days)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"价格趋势图已保存：{save_path}")

def plot_cost_comparison(costs, save_path='cost_comparison.png'):
    """绘制成本对比图"""
    plt.figure(figsize=(10, 6))
    
    algorithms = ['Greedy', 'Time Arbitrage', 'ML Predicted']
    plt.bar(algorithms, costs, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    
    plt.xlabel('Scheduling Algorithm')
    plt.ylabel('Total Cost ($)')
    plt.title('Cost Comparison of Different Scheduling Algorithms')
    
    for i, v in enumerate(costs):
        plt.text(i, v + 0.5, f'${v:.2f}', ha='center')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"成本对比图已保存：{save_path}")

def plot_task_distribution(schedule, save_path='task_distribution.png'):
    """绘制任务分布图"""
    provider_counts = {}
    for s in schedule:
        provider = s['provider']
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
    
    plt.figure(figsize=(10, 6))
    plt.bar(provider_counts.keys(), provider_counts.values(), color='#95E1D3')
    
    plt.xlabel('Cloud Provider')
    plt.ylabel('Number of Tasks')
    plt.title('Task Distribution Across Cloud Providers')
    
    for i, (k, v) in enumerate(provider_counts.items()):
        plt.text(i, v + 0.5, str(v), ha='center')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"任务分布图已保存：{save_path}")

def plot_savings_analysis(greedy_cost, arbitrage_cost, save_path='savings_analysis.png'):
    """绘制节省分析图"""
    savings = greedy_cost - arbitrage_cost
    savings_rate = savings / greedy_cost * 100
    
    plt.figure(figsize=(10, 6))
    
    categories = ['Greedy', 'Time Arbitrage', 'Savings']
    values = [greedy_cost, arbitrage_cost, savings]
    colors = ['#FF6B6B', '#4ECDC4', '#95E1D3']
    
    bars = plt.bar(categories, values, color=colors)
    
    plt.ylabel('Cost ($)')
    plt.title(f'Cost Savings Analysis (Saved: ${savings:.2f}, {savings_rate:.1f}%)')
    
    for i, v in enumerate(values):
        plt.text(i, v + 0.5, f'${v:.2f}' if i < 2 else f'{savings_rate:.1f}%', ha='center')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"节省分析图已保存：{save_path}")

# ============== 主实验函数 ==============
def run_simulation():
    """运行完整仿真"""
    print("=" * 60)
    print("时间套利调度用于异构云计算 - 仿真实验")
    print("=" * 60)
    
    # 1. 生成数据
    print("\n[1/5] 生成仿真数据...")
    prices = generate_spot_prices(days=CONFIG['simulation_days'], hours_per_day=CONFIG['time_slots'])
    tasks = generate_tasks(num_tasks=CONFIG['num_tasks'])
    
    print(f"  - 云服务商数量：{len(CLOUD_PROVIDERS)}")
    print(f"  - 任务数量：{len(tasks)}")
    print(f"  - 仿真时长：{CONFIG['simulation_days']} 天")
    
    # 2. 生成可视化
    print("\n[2/5] 生成价格趋势图...")
    plot_price_trends(prices, 'price_trends.png')
    
    # 3. 运行调度算法
    print("\n[3/5] 运行调度算法...")
    scheduler = TimeArbitrageScheduler(prices, tasks)
    
    greedy_cost, greedy_schedule = scheduler.schedule_greedy()
    print(f"  - 贪婪调度成本：${greedy_cost:.2f}")
    
    arbitrage_cost, arbitrage_schedule = scheduler.schedule_time_arbitrage()
    print(f"  - 时间套利调度成本：${arbitrage_cost:.2f}")
    
    ml_cost, ml_schedule = scheduler.schedule_ml_predicted()
    print(f"  - ML 预测调度成本：${ml_cost:.2f}")
    
    # 4. 生成对比图
    print("\n[4/5] 生成对比图表...")
    plot_cost_comparison([greedy_cost, arbitrage_cost, ml_cost], 'cost_comparison.png')
    plot_task_distribution(arbitrage_schedule, 'task_distribution.png')
    plot_savings_analysis(greedy_cost, arbitrage_cost, 'savings_analysis.png')
    
    # 5. 保存数据
    print("\n[5/5] 保存实验数据...")
    
    # 保存价格数据
    price_data = {provider: [float(p) for p in prices] for provider, prices in prices.items()}
    with open('spot_prices.json', 'w') as f:
        json.dump({'config': CONFIG, 'prices': price_data}, f, indent=2)
    
    # 保存任务数据
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f, indent=2)
    
    # 保存调度结果
    results = {
        'greedy': {'cost': greedy_cost, 'schedule': greedy_schedule},
        'time_arbitrage': {'cost': arbitrage_cost, 'schedule': arbitrage_schedule},
        'ml_predicted': {'cost': ml_cost, 'schedule': ml_schedule},
        'savings': {
            'absolute': greedy_cost - arbitrage_cost,
            'percentage': (greedy_cost - arbitrage_cost) / greedy_cost * 100
        }
    }
    with open('scheduling_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # 保存实验总结
    summary = f"""
实验总结：
- 贪婪调度总成本：${greedy_cost:.2f}
- 时间套利调度总成本：${arbitrage_cost:.2f}
- ML 预测调度总成本：${ml_cost:.2f}
- 节省金额：${greedy_cost - arbitrage_cost:.2f}
- 节省比例：{(greedy_cost - arbitrage_cost) / greedy_cost * 100:.1f}%
"""
    with open('experiment_summary.txt', 'w') as f:
        f.write(summary)
    
    print(summary)
    print("\n" + "=" * 60)
    print("实验完成！生成的文件：")
    print("  - price_trends.png (价格趋势图)")
    print("  - cost_comparison.png (成本对比图)")
    print("  - task_distribution.png (任务分布图)")
    print("  - savings_analysis.png (节省分析图)")
    print("  - spot_prices.json (现货价格数据)")
    print("  - tasks.json (任务数据)")
    print("  - scheduling_results.json (调度结果)")
    print("  - experiment_summary.txt (实验总结)")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    results = run_simulation()
