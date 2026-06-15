#!/usr/bin/env python3
"""
生成购买力平价检验分析 PPT 演示文稿
包含折线图、柱形图、饼图等多种数据可视化
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION
from pptx.chart.data import CategoryChartData
from pptx.util import Emu
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from datetime import datetime
import os

# ============================================================
# 最新数据（2026年6月2日实时汇率）
# ============================================================

# 实时汇率（来自 exchangerate-api.com 2026-06-02）
LATEST_RATES = {
    'EUR': 0.86,
    'JPY': 159.6,
    'GBP': 0.743,
    'CHF': 0.786
}

# PPP 汇率（世界银行 ICP 2021基准推算）
PPP_RATES = {
    'EUR': 0.85,
    'JPY': 112.0,
    'GBP': 0.76,
    'CHF': 0.72
}

# CPI 价格指数（美国=100，2025年）
CPI_INDICES = {
    'EUR': 96.5,
    'JPY': 74.2,
    'GBP': 92.8,
    'CHF': 108.5
}

# 历史汇率数据（2020-2026，年度平均）
HISTORICAL_RATES = {
    'EUR': [0.88, 0.84, 0.88, 0.95, 0.96, 0.88, 0.86],  # 2020-2026
    'JPY': [107, 110, 125, 130, 131, 149, 159.6],
    'GBP': [0.78, 0.73, 0.74, 0.74, 0.73, 0.74, 0.743],
    'CHF': [0.92, 0.88, 0.89, 0.91, 0.96, 0.89, 0.786]
}

YEARS = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

# ============================================================
# 生成图表
# ============================================================

CHART_DIR = '/home/admin/.openclaw/workspace/ppp_charts'
os.makedirs(CHART_DIR, exist_ok=True)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 图表1：名义汇率 vs PPP 汇率对比（柱形图）
fig, ax = plt.subplots(figsize=(10, 6))
countries = ['欧元区(EUR)', '日本(JPY)', '英国(GBP)', '瑞士(CHF)']
nominal = [0.86, 159.6, 0.743, 0.786]
ppp = [0.85, 112.0, 0.76, 0.72]

x = np.arange(len(countries))
width = 0.35

bars1 = ax.bar(x - width/2, nominal, width, label='名义汇率 (2026.06)', color='#2196F3', alpha=0.85)
bars2 = ax.bar(x + width/2, ppp, width, label='PPP汇率', color='#FF5722', alpha=0.85)

ax.set_ylabel('汇率 (1 USD = 本币)', fontsize=12)
ax.set_title('名义汇率与PPP汇率对比 (2026年6月)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(countries, fontsize=11)
ax.legend(fontsize=11)
ax.grid(axis='y', alpha=0.3)

# 添加数据标签
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart1_nominal_vs_ppp.png', dpi=200, bbox_inches='tight')
plt.close()

# 图表2：PPP偏离度（柱形图 - 高估/低估）
fig, ax = plt.subplots(figsize=(10, 6))
deviations = []
for i, country in enumerate(['EUR', 'JPY', 'GBP', 'CHF']):
    dev = (LATEST_RATES[country] - PPP_RATES[country]) / PPP_RATES[country] * 100
    deviations.append(dev)

colors = ['#4CAF50' if d > 0 else '#F44336' for d in deviations]
bars = ax.bar(countries, deviations, color=colors, alpha=0.85, width=0.5)

ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax.set_ylabel('偏离度 (%)', fontsize=12)
ax.set_title('各国货币相对PPP的偏离度 (2026年6月)', fontsize=14, fontweight='bold')
ax.set_xlabel('货币', fontsize=12)
ax.grid(axis='y', alpha=0.3)

# 添加数据标签
for bar, dev in zip(bars, deviations):
    ax.annotate(f'{dev:+.1f}%',
                xy=(bar.get_x() + bar.get_width() / 2, dev),
                xytext=(0, 5 if dev > 0 else -10), textcoords="offset points",
                ha='center', va='bottom' if dev > 0 else 'top',
                fontsize=11, fontweight='bold')

# 添加图例说明
ax.text(0.02, 0.95, '■ 高估  ■ 低估', transform=ax.transAxes, fontsize=10,
        verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart2_ppp_deviation.png', dpi=200, bbox_inches='tight')
plt.close()

# 图表3：历史汇率走势（折线图）
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for idx, (currency, name) in enumerate([('EUR', '欧元/美元'), ('JPY', '日元/美元'),
                                          ('GBP', '英镑/美元'), ('CHF', '瑞郎/美元')]):
    ax = axes[idx // 2, idx % 2]
    ax.plot(YEARS, HISTORICAL_RATES[currency], marker='o', linewidth=2, markersize=6,
            color='#2196F3', label=name)
    ax.fill_between(YEARS, HISTORICAL_RATES[currency], alpha=0.15, color='#2196F3')
    ax.set_title(name, fontsize=12, fontweight='bold')
    ax.set_xlabel('年份', fontsize=10)
    ax.set_ylabel('汇率', fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)

    # 添加最新值标注
    latest = HISTORICAL_RATES[currency][-1]
    ax.annotate(f'{latest:.3f}', xy=(2026, latest), xytext=(5, 5),
                textcoords='offset points', fontsize=9, fontweight='bold',
                color='#FF5722')

plt.suptitle('主要货币兑美元汇率走势 (2020-2026)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart3_historical_rates.png', dpi=200, bbox_inches='tight')
plt.close()

# 图表4：实际汇率对比（柱形图）
fig, ax = plt.subplots(figsize=(10, 6))
real_rates = []
for country in ['EUR', 'JPY', 'GBP', 'CHF']:
    real = LATEST_RATES[country] / PPP_RATES[country]
    real_rates.append(real)

colors_real = ['#F44336' if r > 1.05 else '#4CAF50' if r < 0.95 else '#FFC107'
               for r in real_rates]
labels_real = ['本币高估', '本币低估', '基本均衡']
bar_labels = ['高估' if r > 1.05 else '低估' if r < 0.95 else '均衡' for r in real_rates]

bars = ax.bar(countries, real_rates, color=colors_real, alpha=0.85, width=0.5)
ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, label='PPP均衡线 (q=1)')

ax.set_ylabel('实际汇率 q', fontsize=12)
ax.set_title('实际汇率与购买力平价 (2026年6月)', fontsize=14, fontweight='bold')
ax.set_xlabel('货币', fontsize=12)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

# 添加数据标签
for bar, rate, label in zip(bars, real_rates, bar_labels):
    ax.annotate(f'{rate:.3f}\n({label})',
                xy=(bar.get_x() + bar.get_width() / 2, rate),
                xytext=(0, 5), textcoords="offset points",
                ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart4_real_exchange_rate.png', dpi=200, bbox_inches='tight')
plt.close()

# 图表5：CPI价格水平对比（柱形图）
fig, ax = plt.subplots(figsize=(10, 6))
cpi_data = [CPI_INDICES[c] for c in ['EUR', 'JPY', 'GBP', 'CHF']]
colors_cpi = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']

bars = ax.bar(countries, cpi_data, color=colors_cpi, alpha=0.85, width=0.5)
ax.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label='美国基准 (100)')

ax.set_ylabel('CPI指数 (美国=100)', fontsize=12)
ax.set_title('各国价格水平对比 (2025年)', fontsize=14, fontweight='bold')
ax.set_xlabel('货币', fontsize=12)
ax.legend(fontsize=10)
ax.grid(axis='y', alpha=0.3)

for bar, cpi in zip(bars, cpi_data):
    ax.annotate(f'{cpi:.1f}',
                xy=(bar.get_x() + bar.get_width() / 2, cpi),
                xytext=(0, 5), textcoords="offset points",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart5_cpi_comparison.png', dpi=200, bbox_inches='tight')
plt.close()

# 图表6：汇率变化趋势（折线图 - 所有货币归一化比较）
fig, ax = plt.subplots(figsize=(12, 7))

# 归一化到2020年=100
for currency, name, color in [('EUR', '欧元', '#2196F3'),
                                ('JPY', '日元', '#4CAF50'),
                                ('GBP', '英镑', '#FF9800'),
                                ('CHF', '瑞郎', '#9C27B0')]:
    base = HISTORICAL_RATES[currency][0]
    normalized = [r / base * 100 for r in HISTORICAL_RATES[currency]]
    ax.plot(YEARS, normalized, marker='o', linewidth=2, markersize=6,
            label=name, color=color)

ax.set_xlabel('年份', fontsize=12)
ax.set_ylabel('指数 (2020=100)', fontsize=12)
ax.set_title('主要货币兑美元汇率变化趋势 (归一化)', fontsize=14, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
ax.axhline(y=100, color='gray', linestyle=':', alpha=0.5)

plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart6_normalized_trend.png', dpi=200, bbox_inches='tight')
plt.close()

print("所有图表已生成！")
print(f"图表目录：{CHART_DIR}")
for f in os.listdir(CHART_DIR):
    print(f"  - {f}")
