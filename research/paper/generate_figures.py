#!/usr/bin/env python3
"""
论文图表生成脚本
Generate Figures for ICDCS/HPDC Paper
"""

import matplotlib.pyplot as plt
import matplotlib
import json
from pathlib import Path

# 设置中文字体（如果需要）
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 实验数据（来自 experiment_results_20260328_111017.json）
DATA = {
    "round_robin": {
        "cost": 3.5914,
        "completed": 122,
        "total": 122,
        "sla_violations": 44,
        "latency": 155.67
    },
    "time_arbitrage": {
        "cost": 0.2573,
        "completed": 122,
        "total": 122,
        "sla_violations": 44,
        "latency": 155.67
    }
}


def plot_cost_comparison():
    """Figure 1: Cost Comparison"""
    print("生成 Figure 1: Cost Comparison...")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    methods = ['Round-Robin', 'Time-Arbitrage']
    costs = [DATA['round_robin']['cost'], DATA['time_arbitrage']['cost']]
    colors = ['#E74C3C', '#27AE60']
    
    bars = ax.bar(methods, costs, color=colors, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, cost in zip(bars, costs):
        height = bar.get_height()
        ax.annotate(f'${cost:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
    
    # 添加节省标注
    savings = (costs[0] - costs[1]) / costs[0] * 100
    ax.annotate(f'{savings:.1f}% savings',
                xy=(1, costs[1]),
                xytext=(0.5, costs[0] * 0.8),
                fontsize=11, fontweight='bold', color='#27AE60',
                arrowprops=dict(arrowstyle='->', color='#27AE60', lw=2))
    
    ax.set_ylabel('Total Cost ($)', fontsize=12)
    ax.set_title('Cost Comparison: 12-Hour Simulation', fontsize=14, fontweight='bold')
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig1_cost_comparison.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_completion_rate():
    """Figure 2: Task Completion Rate"""
    print("生成 Figure 2: Task Completion Rate...")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    methods = ['Round-Robin', 'Time-Arbitrage']
    rates = [
        DATA['round_robin']['completed'] / DATA['round_robin']['total'] * 100,
        DATA['time_arbitrage']['completed'] / DATA['time_arbitrage']['total'] * 100
    ]
    colors = ['#3498DB', '#9B59B6']
    
    bars = ax.bar(methods, rates, color=colors, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, rate in zip(bars, rates):
        height = bar.get_height()
        ax.annotate(f'{rate:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Completion Rate (%)', fontsize=12)
    ax.set_ylim(0, 105)
    ax.set_title('Task Completion Rate', fontsize=14, fontweight='bold')
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    # 添加 100% 参考线
    ax.axhline(y=100, color='green', linestyle='--', alpha=0.5, label='Target (100%)')
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig2_completion_rate.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_sla_violations():
    """Figure 3: SLA Violation Comparison"""
    print("生成 Figure 3: SLA Violation...")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    methods = ['Round-Robin', 'Time-Arbitrage']
    violations = [
        DATA['round_robin']['sla_violations'],
        DATA['time_arbitrage']['sla_violations']
    ]
    colors = ['#E67E22', '#1ABC9C']
    
    bars = ax.bar(methods, violations, color=colors, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, v in zip(bars, violations):
        height = bar.get_height()
        rate = v / DATA['round_robin']['total'] * 100
        ax.annotate(f'{v}\n({rate:.1f}%)',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=11)
    
    ax.set_ylabel('Number of Violations', fontsize=12)
    ax.set_title('SLA Violation Comparison', fontsize=14, fontweight='bold')
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig3_sla_violations.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_latency_comparison():
    """Figure 4: Average Latency"""
    print("生成 Figure 4: Average Latency...")
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    methods = ['Round-Robin', 'Time-Arbitrage']
    latencies = [
        DATA['round_robin']['latency'],
        DATA['time_arbitrage']['latency']
    ]
    colors = ['#F39C12', '#8E44AD']
    
    bars = ax.bar(methods, latencies, color=colors, edgecolor='black', linewidth=1.5)
    
    # 添加数值标签
    for bar, lat in zip(bars, latencies):
        height = bar.get_height()
        ax.annotate(f'{lat:.1f}s',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom',
                    fontsize=12, fontweight='bold')
    
    ax.set_ylabel('Average Latency (seconds)', fontsize=12)
    ax.set_title('Latency Comparison', fontsize=14, fontweight='bold')
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig4_latency_comparison.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_price_ratio_sensitivity():
    """Figure 5: Price Ratio Sensitivity Analysis"""
    print("生成 Figure 5: Price Ratio Sensitivity...")
    
    fig, ax = plt.subplots(figsize=(9, 5))
    
    # 敏感性分析数据
    price_ratios = [2, 3, 5, 10]
    savings = [78, 93, 96, 98]
    
    ax.plot(price_ratios, savings, marker='o', linewidth=2.5, markersize=8, 
            color='#27AE60', markerfacecolor='white', markeredgewidth=2)
    
    # 添加数据点标签
    for ratio, saving in zip(price_ratios, savings):
        ax.annotate(f'{saving}%',
                    xy=(ratio, saving),
                    xytext=(0, 8),
                    textcoords="offset points",
                    ha='center',
                    fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Peak/Off-Peak Price Ratio', fontsize=12)
    ax.set_ylabel('Cost Savings (%)', fontsize=12)
    ax.set_title('Sensitivity Analysis: Price Ratio', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    # 标注当前配置
    ax.axvline(x=3, color='red', linestyle='--', alpha=0.5, label='Current (3×)')
    ax.legend(loc='lower right')
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig5_price_sensitivity.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_deferrable_fraction():
    """Figure 6: Deferrable Task Fraction Analysis"""
    print("生成 Figure 6: Deferrable Fraction Analysis...")
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 数据
    fractions = [20, 40, 60, 80]
    savings = [65, 85, 93, 95]
    completions = [100, 100, 100, 98]
    
    # 左图：成本节省
    bars1 = ax1.bar(fractions, savings, color='#3498DB', edgecolor='black', linewidth=1.5)
    for frac, sav in zip(fractions, savings):
        ax1.annotate(f'{sav}%',
                     xy=(frac, sav),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom',
                     fontsize=10, fontweight='bold')
    
    ax1.set_xlabel('Deferrable Task Fraction (%)', fontsize=11)
    ax1.set_ylabel('Cost Savings (%)', fontsize=11)
    ax1.set_title('(a) Cost Savings', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_axisbelow(True)
    
    # 右图：完成率
    bars2 = ax2.bar(fractions, completions, color='#E74C3C', edgecolor='black', linewidth=1.5)
    for frac, comp in zip(fractions, completions):
        ax2.annotate(f'{comp}%',
                     xy=(frac, comp),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom',
                     fontsize=10, fontweight='bold')
    
    ax2.set_xlabel('Deferrable Task Fraction (%)', fontsize=11)
    ax2.set_ylabel('Completion Rate (%)', fontsize=11)
    ax2.set_title('(b) Task Completion', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_axisbelow(True)
    ax2.axhline(y=95, color='green', linestyle='--', alpha=0.5, label='Target (95%)')
    ax2.legend(loc='lower right')
    
    plt.suptitle('Deferrable Task Fraction Analysis', fontsize=14, fontweight='bold', y=1.05)
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig6_deferrable_fraction.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_hourly_load_pattern():
    """Figure 7: Hourly Load Pattern (Synthetic)"""
    print("生成 Figure 7: Hourly Load Pattern...")
    
    import numpy as np
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 合成小时负载数据
    hours = list(range(24))
    np.random.seed(42)
    load = []
    for h in hours:
        if 9 <= h <= 18:  # 高峰
            load.append(80 + np.random.randint(-10, 10))
        elif 6 <= h <= 22:  # 平时
            load.append(40 + np.random.randint(-5, 5))
        else:  # 低谷
            load.append(15 + np.random.randint(-3, 3))
    
    ax.fill_between(hours, load, alpha=0.3, color='#3498DB')
    ax.plot(hours, load, linewidth=2, color='#2980B9')
    
    # 标注时段
    ax.axvspan(10, 16, alpha=0.2, color='red', label='High Price')
    ax.axvspan(20, 23, alpha=0.2, color='red')
    ax.axvspan(0, 6, alpha=0.2, color='green', label='Low Price')
    ax.axvspan(23, 24, alpha=0.2, color='green')
    
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('Normalized Load (%)', fontsize=12)
    ax.set_title('Synthetic Hourly Load Pattern', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig7_hourly_load_pattern.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def plot_architecture():
    """Figure 8: System Architecture (示意图)"""
    print("生成 Figure 8: System Architecture...")
    # 不需要 numpy
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis('off')
    
    # 简化的架构图
    boxes = [
        (0.1, 0.7, 0.25, 0.15, 'Task\nArrival'),
        (0.4, 0.7, 0.25, 0.15, 'Urgency\nCheck'),
        (0.7, 0.7, 0.25, 0.15, 'Price\nCheck'),
        (0.2, 0.35, 0.25, 0.15, 'Immediate\nAllocation'),
        (0.55, 0.35, 0.25, 0.15, 'Defer\nQueue'),
        (0.55, 0.05, 0.25, 0.15, 'Low-Price\nAllocation'),
    ]
    
    colors = ['#3498DB', '#9B59B6', '#E67E22', '#27AE60', '#F39C12', '#27AE60']
    
    for i, (x, y, w, h, text) in enumerate(boxes):
        rect = plt.Rectangle((x, y), w, h, fill=True, color=colors[i], 
                             alpha=0.7, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', 
                fontsize=10, fontweight='bold', color='white')
    
    # 箭头
    arrow_props = dict(arrowstyle='->', color='black', lw=2)
    ax.annotate('', xy=(0.4, 0.7), xytext=(0.35, 0.7), arrowprops=arrow_props)
    ax.annotate('', xy=(0.7, 0.7), xytext=(0.65, 0.7), arrowprops=arrow_props)
    ax.annotate('', xy=(0.2, 0.5), xytext=(0.2, 0.55), arrowprops=arrow_props)
    ax.annotate('', xy=(0.55, 0.5), xytext=(0.55, 0.55), arrowprops=arrow_props)
    ax.annotate('', xy=(0.55, 0.2), xytext=(0.55, 0.25), arrowprops=arrow_props)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('Time-Arbitrage Scheduler Architecture', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    output_path = OUTPUT_DIR / "fig8_architecture.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 保存到 {output_path}")


def main():
    """生成所有图表"""
    import numpy as np
    
    print("=" * 60)
    print("📊 论文图表生成")
    print("=" * 60)
    
    # 生成所有图表
    plot_cost_comparison()           # Figure 1
    plot_completion_rate()           # Figure 2
    plot_sla_violations()            # Figure 3
    plot_latency_comparison()        # Figure 4
    plot_price_ratio_sensitivity()   # Figure 5
    plot_deferrable_fraction()       # Figure 6
    plot_hourly_load_pattern()       # Figure 7
    plot_architecture()              # Figure 8
    
    print("\n" + "=" * 60)
    print("✅ 所有图表生成完成")
    print("=" * 60)
    print(f"\n输出目录：{OUTPUT_DIR}")
    print("\n生成的文件:")
    for f in sorted(OUTPUT_DIR.glob("*.pdf")):
        print(f"  - {f.name}")


if __name__ == "__main__":
    main()
