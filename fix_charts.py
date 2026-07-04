import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

# Use available Chinese font
zh_font_path = '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'
fm.fontManager.addfont(zh_font_path)
prop = fm.FontProperties(fname=zh_font_path)

CHART_DIR = '/home/admin/.openclaw/workspace/ppp_charts'

countries = ['欧元区', '日本', '英国', '瑞士']
years = [2020, 2021, 2022, 2023, 2024, 2025, 2026]

hist = {
    'EUR': [0.88, 0.84, 0.88, 0.95, 0.96, 0.88, 0.86],
    'JPY': [107, 110, 125, 130, 131, 149, 159.6],
    'GBP': [0.78, 0.73, 0.74, 0.74, 0.73, 0.74, 0.743],
    'CHF': [0.92, 0.88, 0.89, 0.91, 0.96, 0.89, 0.786]
}

# Chart 1: Nominal vs PPP
fig, ax = plt.subplots(figsize=(10, 6))
nominal = [0.86, 159.6, 0.743, 0.786]
ppp = [0.85, 112.0, 0.76, 0.72]
x = np.arange(len(countries))
width = 0.35
bars1 = ax.bar(x - width/2, nominal, width, label='名义汇率 (2026.06)', color='#2196F3', alpha=0.85)
bars2 = ax.bar(x + width/2, ppp, width, label='PPP汇率', color='#FF5722', alpha=0.85)
ax.set_ylabel('汇率 (1 USD = 本币)', fontsize=12, fontproperties=prop)
ax.set_title('名义汇率与PPP汇率对比 (2026年6月)', fontsize=14, fontweight='bold', fontproperties=prop)
ax.set_xticks(x)
ax.set_xticklabels(countries, fontsize=11, fontproperties=prop)
ax.legend(prop=prop, fontsize=11)
ax.grid(axis='y', alpha=0.3)
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.3f}', xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart1_nominal_vs_ppp.png', dpi=200, bbox_inches='tight')
plt.close()
print("Chart 1 done")

# Chart 2: PPP Deviation
fig, ax = plt.subplots(figsize=(10, 6))
deviations = [(0.86-0.85)/0.85*100, (159.6-112.0)/112.0*100, (0.743-0.76)/0.76*100, (0.786-0.72)/0.72*100]
colors = ['#4CAF50' if d > 0 else '#F44336' for d in deviations]
bars = ax.bar(countries, deviations, color=colors, alpha=0.85, width=0.5)
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
ax.set_ylabel('偏离度 (%)', fontsize=12, fontproperties=prop)
ax.set_title('各国货币相对PPP的偏离度 (2026年6月)', fontsize=14, fontweight='bold', fontproperties=prop)
ax.set_xlabel('货币', fontsize=12, fontproperties=prop)
ax.grid(axis='y', alpha=0.3)
for bar, dev in zip(bars, deviations):
    ax.annotate(f'{dev:+.1f}%', xy=(bar.get_x() + bar.get_width() / 2, dev),
                xytext=(0, 5 if dev > 0 else -10), textcoords="offset points",
                ha='center', va='bottom' if dev > 0 else 'top', fontsize=11, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart2_ppp_deviation.png', dpi=200, bbox_inches='tight')
plt.close()
print("Chart 2 done")

# Chart 3: Historical rates
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
names = [('EUR', '欧元/美元'), ('JPY', '日元/美元'), ('GBP', '英镑/美元'), ('CHF', '瑞郎/美元')]
for idx, (currency, name) in enumerate(names):
    ax = axes[idx // 2, idx % 2]
    ax.plot(years, hist[currency], marker='o', linewidth=2, markersize=6, color='#2196F3', label=name)
    ax.fill_between(years, hist[currency], alpha=0.15, color='#2196F3')
    ax.set_title(name, fontsize=12, fontweight='bold', fontproperties=prop)
    ax.set_xlabel('年份', fontsize=10, fontproperties=prop)
    ax.set_ylabel('汇率', fontsize=10, fontproperties=prop)
    ax.grid(alpha=0.3)
    ax.legend(prop=prop, fontsize=9)
    latest = hist[currency][-1]
    ax.annotate(f'{latest:.3f}', xy=(2026, latest), xytext=(5, 5), textcoords='offset points',
                fontsize=9, fontweight='bold', color='#FF5722')
plt.suptitle('主要货币兑美元汇率走势 (2020-2026)', fontsize=14, fontweight='bold', fontproperties=prop)
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart3_historical_rates.png', dpi=200, bbox_inches='tight')
plt.close()
print("Chart 3 done")

# Chart 4: Real exchange rate
fig, ax = plt.subplots(figsize=(10, 6))
real_rates = [0.86/0.85, 159.6/112.0, 0.743/0.76, 0.786/0.72]
labels = ['高估' if r > 1.05 else '低估' if r < 0.95 else '均衡' for r in real_rates]
colors_real = ['#F44336' if r > 1.05 else '#4CAF50' if r < 0.95 else '#FFC107' for r in real_rates]
bars = ax.bar(countries, real_rates, color=colors_real, alpha=0.85, width=0.5)
ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, label='PPP均衡线 (q=1)')
ax.set_ylabel('实际汇率 q', fontsize=12, fontproperties=prop)
ax.set_title('实际汇率与购买力平价 (2026年6月)', fontsize=14, fontweight='bold', fontproperties=prop)
ax.set_xlabel('货币', fontsize=12, fontproperties=prop)
ax.legend(prop=prop, fontsize=10)
ax.grid(axis='y', alpha=0.3)
for bar, rate, label in zip(bars, real_rates, labels):
    ax.annotate(f'{rate:.3f}\n({label})', xy=(bar.get_x() + bar.get_width() / 2, rate),
                xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart4_real_exchange_rate.png', dpi=200, bbox_inches='tight')
plt.close()
print("Chart 4 done")

# Chart 5: CPI comparison
fig, ax = plt.subplots(figsize=(10, 6))
cpi_data = [96.5, 74.2, 92.8, 108.5]
colors_cpi = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']
bars = ax.bar(countries, cpi_data, color=colors_cpi, alpha=0.85, width=0.5)
ax.axhline(y=100, color='red', linestyle='--', linewidth=1.5, label='美国基准 (100)')
ax.set_ylabel('CPI指数 (美国=100)', fontsize=12, fontproperties=prop)
ax.set_title('各国价格水平对比 (2025年)', fontsize=14, fontweight='bold', fontproperties=prop)
ax.set_xlabel('货币', fontsize=12, fontproperties=prop)
ax.legend(prop=prop, fontsize=10)
ax.grid(axis='y', alpha=0.3)
for bar, cpi in zip(bars, cpi_data):
    ax.annotate(f'{cpi:.1f}', xy=(bar.get_x() + bar.get_width() / 2, cpi),
                xytext=(0, 5), textcoords="offset points", ha='center', va='bottom', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart5_cpi_comparison.png', dpi=200, bbox_inches='tight')
plt.close()
print("Chart 5 done")

# Chart 6: Normalized trend
fig, ax = plt.subplots(figsize=(12, 7))
for currency, name, color in [('EUR', '欧元', '#2196F3'), ('JPY', '日元', '#4CAF50'),
                                ('GBP', '英镑', '#FF9800'), ('CHF', '瑞郎', '#9C27B0')]:
    base = hist[currency][0]
    normalized = [r / base * 100 for r in hist[currency]]
    ax.plot(years, normalized, marker='o', linewidth=2, markersize=6, label=name, color=color)
ax.set_xlabel('年份', fontsize=12, fontproperties=prop)
ax.set_ylabel('指数 (2020=100)', fontsize=12, fontproperties=prop)
ax.set_title('主要货币兑美元汇率变化趋势 (归一化)', fontsize=14, fontweight='bold', fontproperties=prop)
ax.legend(prop=prop, fontsize=11)
ax.grid(alpha=0.3)
ax.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
plt.tight_layout()
plt.savefig(f'{CHART_DIR}/chart6_normalized_trend.png', dpi=200, bbox_inches='tight')
plt.close()
print("Chart 6 done")

print("\nAll charts regenerated with Chinese font support!")
