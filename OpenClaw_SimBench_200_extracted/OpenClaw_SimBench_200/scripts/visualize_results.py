#!/usr/bin/env python3
"""
OpenClaw-SimBench 实验结果可视化脚本
生成论文所需的柱状图和对比图
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 加载实验结果
outputs_dir = Path(__file__).parent.parent / 'outputs'

def load_metrics(filename):
    with open(outputs_dir / filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# 加载所有结果
results = {
    'openclaw_full': load_metrics('openclaw_full_metrics.json'),
    'openclaw_wo_retry': load_metrics('openclaw_wo_retry_metrics.json'),
    'openclaw_wo_validator': load_metrics('openclaw_wo_validator_metrics.json'),
    'react': load_metrics('react_metrics.json'),
    'zero_shot': load_metrics('zero_shot_metrics.json'),
    'recovery_openclaw_full': load_metrics('recovery_openclaw_full_metrics.json'),
    'recovery_zero_shot': load_metrics('recovery_zero_shot_metrics.json'),
}

# 方法名称映射
method_names = {
    'openclaw_full': 'OpenClaw Full',
    'openclaw_wo_retry': 'w/o Retry',
    'openclaw_wo_validator': 'w/o Validator',
    'react': 'ReAct',
    'zero_shot': 'Zero-shot',
}

# 颜色配置
colors = {
    'openclaw_full': '#2E86AB',
    'openclaw_wo_retry': '#A23B72',
    'openclaw_wo_validator': '#F18F01',
    'react': '#C73E1D',
    'zero_shot': '#6A994E',
}

# 图 1：主评测集 TSR 对比
fig, ax = plt.subplots(figsize=(10, 6))
methods = ['openclaw_full', 'openclaw_wo_retry', 'openclaw_wo_validator', 'react', 'zero_shot']
tsr_values = [results[m]['overall']['TSR'] for m in methods]
bars = ax.bar([method_names[m] for m in methods], tsr_values, color=[colors[m] for m in methods])

ax.set_ylabel('任务成功率 (TSR)', fontsize=12)
ax.set_title('主评测集任务成功率对比 (N=200)', fontsize=14)
ax.set_ylim(0, 1.1)

# 添加数值标签
for bar, val in zip(bars, tsr_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
            f'{val:.1%}', ha='center', va='bottom', fontsize=10)

plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig('figures/main_tsr_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 图 2：主评测集多指标雷达图
fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})

categories = ['TSR', '1-THR', '1-PFER', 'TCR', 'MCSR']
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

for method in methods:
    data = results[method]['overall']
    values = [
        data['TSR'],
        1 - data['THR'],
        1 - data['PFER'],
        data['TCR'],
        data.get('MCSR', 0) or 0
    ]
    values += values[:1]
    
    ax.plot(angles, values, 'o-', linewidth=2, label=method_names[method], color=colors[method])
    ax.fill(angles, values, alpha=0.15, color=colors[method])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11)
ax.set_ylim(0, 1.1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.set_title('主评测集多指标对比', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig('figures/main_radar_chart.png', dpi=300, bbox_inches='tight')
plt.close()

# 图 3：Recovery 实验 TSR 对比
fig, ax = plt.subplots(figsize=(10, 6))
recovery_methods = ['recovery_openclaw_full', 'openclaw_wo_retry', 'openclaw_wo_validator', 'react', 'recovery_zero_shot']
recovery_tsr = [
    results['recovery_openclaw_full']['overall']['TSR'],
    results['recovery_openclaw_wo_retry']['overall']['TSR'],
    results['recovery_openclaw_wo_validator']['overall']['TSR'],
    results['recovery_react_metrics']['overall']['TSR'] if (outputs_dir / 'recovery_react_metrics.json').exists() else 0,
    results['recovery_zero_shot']['overall']['TSR'],
]

# 重新加载 recovery_react
if (outputs_dir / 'recovery_react_metrics.json').exists():
    results['recovery_react_metrics'] = load_metrics('recovery_react_metrics.json')
    recovery_tsr[3] = results['recovery_react_metrics']['overall']['TSR']

recovery_method_names = ['OpenClaw Full', 'w/o Retry', 'w/o Validator', 'ReAct', 'Zero-shot']
recovery_colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']

bars = ax.bar(recovery_method_names, recovery_tsr, color=recovery_colors)
ax.set_ylabel('任务成功率 (TSR)', fontsize=12)
ax.set_title('Recovery 实验任务成功率对比 (N=120, 注入参数错误)', fontsize=14)
ax.set_ylim(0, 1.1)

for bar, val in zip(bars, recovery_tsr):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
            f'{val:.1%}', ha='center', va='bottom', fontsize=10)

plt.xticks(rotation=15)
plt.axhline(y=0, color='black', linewidth=0.5)
plt.tight_layout()
plt.savefig('figures/recovery_tsr_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 图 4：按任务类型分层统计
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

task_types = ['single', 'double', 'multi']
task_titles = ['单工具任务 (N=70)', '双工具任务 (N=60)', '多工具链任务 (N=70)']

for idx, (task_type, title) in enumerate(zip(task_types, task_titles)):
    ax = axes[idx]
    tsr_vals = []
    for method in methods:
        if task_type in results[method]:
            tsr_vals.append(results[method][task_type]['TSR'])
        else:
            tsr_vals.append(0)
    
    bars = ax.bar([method_names[m] for m in methods], tsr_vals, color=[colors[m] for m in methods])
    ax.set_ylabel('TSR')
    ax.set_title(title)
    ax.set_ylim(0, 1.1)
    ax.tick_params(axis='x', rotation=15)
    
    for bar, val in zip(bars, tsr_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{val:.1%}', ha='center', va='bottom', fontsize=8)

plt.suptitle('按任务类型分层统计', fontsize=14, y=1.05)
plt.tight_layout()
plt.savefig('figures/layered_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# 图 5：Recovery 实验按故障类型统计
fig, ax = plt.subplots(figsize=(12, 6))

fault_types = ['wrong_type', 'wrong_enum', 'missing_required']
fault_names = ['类型错误 (N=45)', '枚举错误 (N=45)', '缺少必填 (N=30)']
recovery_full = results['recovery_openclaw_full']

recovery_by_fault = [
    recovery_full['by_fault_type']['wrong_type']['RecoverySR'],
    recovery_full['by_fault_type']['wrong_enum']['RecoverySR'],
    recovery_full['by_fault_type']['missing_required']['RecoverySR'],
]

bars = ax.bar(fault_names, recovery_by_fault, color='#2E86AB')
ax.set_ylabel('恢复成功率 (RecoverySR)', fontsize=12)
ax.set_title('OpenClaw Full 按故障类型恢复成功率', fontsize=14)
ax.set_ylim(0, 1.1)

for bar, val in zip(bars, recovery_by_fault):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
            f'{val:.1%}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('figures/recovery_by_fault_type.png', dpi=300, bbox_inches='tight')
plt.close()

print('✅ 所有图表已生成至 figures/ 目录')
print('生成的文件:')
print('  - figures/main_tsr_comparison.png')
print('  - figures/main_radar_chart.png')
print('  - figures/recovery_tsr_comparison.png')
print('  - figures/layered_comparison.png')
print('  - figures/recovery_by_fault_type.png')
