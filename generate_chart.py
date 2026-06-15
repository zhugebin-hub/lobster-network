#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成成员 4 的双轴数据图：房价指数 vs 次级贷违约率"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 数据
years = [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008]
housing_price_index = [100, 107, 115, 125, 154, 178, 189, 157, 139]  # 2000=100
subprime_default_rate = [1.5, 1.8, 2.0, 2.2, 2.5, 3.8, 5.5, 10.2, 15.8]  # 百分比

# 创建双轴图
fig, ax1 = plt.subplots(figsize=(12, 7))

# 左轴 - 房价指数
color1 = '#2E86AB'
ax1.set_xlabel('年份', fontsize=14, fontweight='bold')
ax1.set_ylabel('房价指数 (2000=100)', color=color1, fontsize=13, fontweight='bold')
line1 = ax1.plot(years, housing_price_index, color=color1, marker='o', linewidth=3, markersize=8, label='房价指数')
ax1.tick_params(axis='y', labelcolor=color1, labelsize=11)
ax1.grid(True, alpha=0.3, linestyle='--')

# 设置 x 轴刻度
ax1.set_xticks(years)
ax1.set_xticklabels([str(y) for y in years])

# 右轴 - 违约率
ax2 = ax1.twinx()
color2 = '#A23B72'
ax2.set_ylabel('次级贷款违约率 (%)', color=color2, fontsize=13, fontweight='bold')
line2 = ax2.plot(years, subprime_default_rate, color=color2, marker='s', linewidth=3, markersize=8, label='违约率')
ax2.tick_params(axis='y', labelcolor=color2, labelsize=11)

# 添加数据标签
for i, (y1, y2) in enumerate(zip(housing_price_index, subprime_default_rate)):
    ax1.annotate(f'{y1}', (years[i], y1), textcoords="offset points", xytext=(0,10), 
                 ha='center', fontsize=9, color=color1, fontweight='bold')
    ax2.annotate(f'{y2}%', (years[i], y2), textcoords="offset points", xytext=(0,-15), 
                 ha='center', fontsize=9, color=color2, fontweight='bold')

# 添加标题
plt.title('2000-2008 年美国房价指数 vs 次级贷款违约率', fontsize=16, fontweight='bold', pad=20)

# 添加图例
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', fontsize=11)
ax2.legend(loc='upper right', fontsize=11)

# 添加注释
plt.annotate('房价峰值', xy=(2006, 189), xytext=(2003.5, 200),
             arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
             fontsize=10, fontweight='bold')

plt.annotate('危机爆发', xy=(2008, 139), xytext=(2007.5, 120),
             arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
             fontsize=10, fontweight='bold')

# 添加背景说明
fig.text(0.5, 0.02, '数据来源：美联储经济数据 (FRED) | 制作：成员 4', 
         ha='center', fontsize=9, style='italic')

plt.tight_layout()
plt.savefig('/home/admin/.openclaw/workspace/成员 4-房价与违约率双轴图.png', dpi=300, bbox_inches='tight')
print('图表已保存：成员 4-房价与违约率双轴图.png')
