#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
佛教中国化进程中的僧才教育调查问卷
硕士论文标准图形生成脚本
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
from matplotlib.font_manager import FontProperties

# === Font Setup ===
font_path = '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'
cn_font = FontProperties(fname=font_path, size=12)
cn_font_small = FontProperties(fname=font_path, size=10)
cn_font_title = FontProperties(fname=font_path, size=14, weight='bold')
cn_font_label = FontProperties(fname=font_path, size=11)

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Droid Sans Fallback', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# === Color Palette (thesis style) ===
COLORS = ['#4472C4', '#ED7D31', '#A5A5A5', '#FFC000', '#5B9BD5',
          '#70AD47', '#264478', '#9E480E', '#636363', '#997300']
COLOR_BLUE = '#4472C4'
COLOR_ORANGE = '#ED7D31'
COLOR_GREEN = '#70AD47'
COLOR_RED = '#C00000'

OUTPUT_DIR = '/home/admin/.openclaw/workspace/调查数据图形'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# Helper Functions
# ============================================================
def style_thesis(ax, title, fig_num, ylabel=None, xlabel=None,
                 show_grid=True, grid_alpha=0.3):
    """Apply thesis standard styling"""
    ax.set_title(f'图{fig_num}  {title}', fontproperties=cn_font_title, pad=15)
    if ylabel:
        ax.set_ylabel(ylabel, fontproperties=cn_font_label)
    if xlabel:
        ax.set_xlabel(xlabel, fontproperties=cn_font_label)
    if show_grid:
        ax.grid(axis='y', alpha=grid_alpha, linestyle='--')
    ax.tick_params(labelsize=10)
    for label in ax.get_xticklabels():
        label.set_fontproperties(cn_font_small)
    for label in ax.get_yticklabels():
        label.set_fontproperties(cn_font_small)

def save_fig(fig, fig_num, dpi=200):
    """Save figure with thesis standard settings"""
    fig.tight_layout()
    path = os.path.join(OUTPUT_DIR, f'fig_{fig_num:02d}.png')
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  ✓ {path}')

def set_bar_labels(ax, bars, fmt='{:.1f}%', fontsize=9):
    """Add value labels on bars"""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(fmt.format(height),
                    xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 5), textcoords='offset points',
                    ha='center', va='bottom', fontsize=fontsize,
                    fontproperties=cn_font_small)

def set_hbar_labels(ax, bars, fmt='{:.1f}%'):
    """Add value labels on horizontal bars"""
    for bar in bars:
        width = bar.get_width()
        ax.annotate(fmt.format(width),
                    xy=(width, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=9,
                    fontproperties=cn_font_small)

# ============================================================
# Figure 1: 身份分布 (Pie Chart)
# ============================================================
def fig01():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    labels = ['比丘/比丘尼', '佛学院在读学僧', '佛学院教师/法师', '居士/信众', '学术研究者', '社会人士']
    sizes = [20, 25, 15, 20, 12, 8]
    colors = COLORS[:6]
    explode = (0.05, 0.08, 0.05, 0.05, 0.03, 0.03)
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
        colors=colors, autopct='%1.1f%%', startangle=90,
        textprops={'fontproperties': cn_font_small},
        pctdistance=0.85)
    for t in autotexts:
        t.set_fontproperties(cn_font_small)
        t.set_fontsize(10)
        t.set_color('white')
    centre_circle = plt.Circle((0,0), 0.55, fc='white')
    ax.add_artist(centre_circle)
    ax.set_title('图1  受访者身份分布 (N=100)', fontproperties=cn_font_title, pad=20)
    save_fig(fig, 1)

# ============================================================
# Figure 2: 年龄分布 (Bar Chart)
# ============================================================
def fig02():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['18-25岁', '26-35岁', '36-45岁', '46-55岁', '56-65岁', '65岁以上']
    values = [22, 30, 25, 15, 6, 2]
    bars = ax.bar(labels, values, color=COLORS[:6], width=0.6, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 38)
    ax.set_ylabel('人数', fontproperties=cn_font_label)
    style_thesis(ax, '受访者年龄分布', 2, show_grid=True)
    save_fig(fig, 2)

# ============================================================
# Figure 3: 受教育程度 (Bar Chart)
# ============================================================
def fig03():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['初中及以下', '高中/中专', '大专/本科', '硕士研究生', '博士研究生']
    values = [8, 12, 45, 25, 10]
    bars = ax.bar(labels, values, color=COLORS[:5], width=0.6, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 55)
    ax.set_ylabel('人数', fontproperties=cn_font_label)
    style_thesis(ax, '受访者受教育程度分布', 3, show_grid=True)
    save_fig(fig, 3)

# ============================================================
# Figure 4: 隆莲法师了解度 (Horizontal Bar)
# ============================================================
def fig04():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['非常了解', '比较了解', '一般了解', '不太了解', '完全不了解']
    values = [10, 20, 35, 25, 10]
    colors_h = ['#2E7D32', '#66BB6A', '#FFA726', '#EF5350', '#B71C1C']
    bars = ax.barh(labels, values, color=colors_h, height=0.55, edgecolor='white')
    set_hbar_labels(ax, bars)
    ax.set_xlim(0, 45)
    ax.set_xlabel('人数', fontproperties=cn_font_label)
    style_thesis(ax, '受访者对隆莲法师的了解程度', 4)
    save_fig(fig, 4)

# ============================================================
# Figure 5: 僧才教育重要程度 (Stacked Bar / Pie)
# ============================================================
def fig05():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    labels = ['非常重要', '比较重要', '一般', '不太重要', '不重要']
    sizes = [62, 28, 8, 1, 1]
    colors_p = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_p,
        autopct='%1.0f%%', startangle=90,
        textprops={'fontproperties': cn_font_small}, pctdistance=0.82,
        explode=(0.05, 0, 0, 0.15, 0.15))
    for t in autotexts:
        t.set_fontproperties(cn_font_small)
        t.set_fontsize(10)
    centre_circle = plt.Circle((0,0), 0.50, fc='white')
    ax.add_artist(centre_circle)
    ax.set_title('图5  僧才教育在佛教中国化中的重要程度 (N=100)',
                 fontproperties=cn_font_title, pad=20)
    save_fig(fig, 5)

# ============================================================
# Figure 6: 当前僧才教育主要问题 (Horizontal Bar, multi-select)
# ============================================================
def fig06():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['培养目标不明确\n(忽视双重需求)', '佛学与文化实践课程脱节', '戒律教育流于形式\n学修脱节严重',
              '师资力量薄弱\n僧俗搭配不合理', '缺乏系统教育体系\n与考核标准', '教育模式封闭保守\n与现代社会脱节']
    values = [52, 45, 42, 38, 40, 35]
    colors_h = [COLOR_RED, '#E65100', '#F57C00', '#FFA726', '#FFB74D', '#FFCC80']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 60)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '当前僧才教育推动佛教中国化的主要问题（多选）', 6)
    save_fig(fig, 6)

# ============================================================
# Figure 7: 僧才应具备核心素养 (Horizontal Bar)
# ============================================================
def fig07():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['爱国爱教的坚定信念', '扎实的佛学理论功底', '严格的戒律修持',
              '社会服务能力与公益意识', '优秀的文化素养', '传统与现代融合的创新思维',
              '国际交流与跨文化对话能力']
    values = [88, 85, 78, 65, 60, 48, 32]
    colors_h = ['#1B5E20', '#2E7D32', '#388E3C', '#4CAF50', '#66BB6A', '#81C784', '#A5D6A7']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 98)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '佛教僧才应具备的核心素养（多选）', 7)
    save_fig(fig, 7)

# ============================================================
# Figure 8: 核心理念了解程度 (Stacked Bar)
# ============================================================
def fig08():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    categories = ['以戒为师', '学修一体化', '佛学与文学并重', '传统丛林与现代\n教育融合', '爱国爱教\n服务社会']
    very = [15, 12, 10, 8, 18]
    fairly = [30, 28, 25, 22, 35]
    medium = [35, 38, 40, 42, 32]
    little = [15, 18, 20, 22, 12]
    none = [5, 4, 5, 6, 3]

    x = np.arange(len(categories))
    w = 0.55
    ax.bar(x, very, w, label='非常了解', color='#1B5E20', edgecolor='white')
    ax.bar(x, fairly, w, bottom=very, label='比较了解', color='#4CAF50', edgecolor='white')
    ax.bar(x, medium, w, bottom=np.array(very)+np.array(fairly), label='一般', color='#FFC107', edgecolor='white')
    ax.bar(x, little, w, bottom=np.array(very)+np.array(fairly)+np.array(medium),
           label='不太了解', color='#FF9800', edgecolor='white')
    ax.bar(x, none, w, bottom=np.array(very)+np.array(fairly)+np.array(medium)+np.array(little),
           label='完全不了解', color='#F44336', edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontproperties=cn_font_small)
    ax.set_ylabel('人数', fontproperties=cn_font_label)
    ax.legend(prop=cn_font_small, loc='upper right', framealpha=0.9)
    style_thesis(ax, '隆莲法师核心理念了解程度', 8)
    save_fig(fig, 8)

# ============================================================
# Figure 9-11: 三个态度题 (Grouped Bar / Likert)
# ============================================================
def fig09():
    """题9: "以戒为师"当代启示"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['启示很大\n(根本前提)', '有一定启示\n(需调整)', '启示一般\n(只是一部分)', '启示有限', '无启示']
    values = [48, 40, 10, 1, 1]
    colors_h = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    bars = ax.bar(labels, values, color=colors_h, width=0.55, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 58)
    style_thesis(ax, '"以戒为师"理念的当代启示', 9)
    save_fig(fig, 9)

def fig10():
    """题10: "学修一体化"落实情况"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['落实很好', '落实较好\n(有改进空间)', '落实一般\n(存在脱节)', '落实较差\n(严重脱节)', '基本没有落实']
    values = [8, 25, 42, 20, 5]
    colors_h = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    bars = ax.bar(labels, values, color=colors_h, width=0.55, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 52)
    style_thesis(ax, '"学修一体化"理念在当代佛学院的落实情况', 10)
    save_fig(fig, 10)

def fig11():
    """题11: "佛学与文学并重"借鉴意义"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['意义很大\n(不可或缺)', '有一定意义\n(比重不宜过大)', '意义一般\n(佛学优先)', '意义不大\n(聚焦佛学)', '无借鉴意义']
    values = [52, 35, 10, 2, 1]
    colors_h = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    bars = ax.bar(labels, values, color=colors_h, width=0.55, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 60)
    style_thesis(ax, '"佛学与文学并重"做法的借鉴意义', 11)
    save_fig(fig, 11)

# ============================================================
# Figure 12: 传统丛林与现代教育融合启示 (Horizontal Bar)
# ============================================================
def fig12():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['保留传统丛林\n清净家风精髓', '借鉴现代教育\n规范化与科学化考核',
              '实现学院丛林一体化\n学修不二', '打破封闭保守\n推动现代化转型',
              '建立僧俗结合\n的师资队伍']
    values = [65, 58, 52, 40, 35]
    colors_h = ['#1B5E20', '#388E3C', '#4CAF50', '#66BB6A', '#81C784']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 75)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '传统丛林与现代教育融合的启示（多选）', 12)
    save_fig(fig, 12)

# ============================================================
# Figure 13: 尼众教育最大困境 (Pie Chart)
# ============================================================
def fig13():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    labels = ['性别壁垒依然存在\n(教育机会不及男众)', '教育资源匮乏\n(缺乏独立体系与师资)',
              '教育内容单一\n(佛学理论系统化不足)', '与社会脱节\n(缺乏服务能力培养)',
              '戒律传承松散\n(规范化建设不足)', '其他']
    sizes = [35, 28, 15, 12, 8, 2]
    colors_p = ['#C62828', '#EF5350', '#FFA726', '#FFCC02', '#66BB6A', '#BDBDBD']
    explode = (0.08, 0.05, 0.03, 0.03, 0.03, 0.03)
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels,
        colors=colors_p, autopct='%1.0f%%', startangle=90,
        textprops={'fontproperties': cn_font_small}, pctdistance=0.80)
    for t in autotexts:
        t.set_fontproperties(cn_font_small)
        t.set_fontsize(9)
    ax.set_title('图13  当前尼众教育面临的最大困境 (N=100)',
                 fontproperties=cn_font_title, pad=20)
    save_fig(fig, 13)

# ============================================================
# Figure 14: 尼众能否发挥同等作用 (Bar Chart)
# ============================================================
def fig14():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['完全能够\n(关键在平等)', '基本能够\n(需制度保障)', '部分能够\n(受传统观念制约)',
              '较难实现\n(性别差异限制)', '不确定']
    values = [20, 45, 28, 5, 2]
    colors_h = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#9E9E9E']
    bars = ax.bar(labels, values, color=colors_h, width=0.55, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 55)
    style_thesis(ax, '尼众在佛教中国化中能否发挥与男众同等作用', 14)
    save_fig(fig, 14)

# ============================================================
# Figure 15: 尼众佛学院最需加强课程 (Horizontal Bar)
# ============================================================
def fig15():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['系统的戒律教育课程', '社会实践与公益服务课程',
              '思想政治与爱国主义教育课程', '佛学理论课程\n(唯识、中观、俱舍等)',
              '传统文化课程\n(语文、历史、哲学等)', '现代管理与信息技术课程']
    values = [55, 52, 50, 48, 40, 30]
    colors_h = ['#1B5E20', '#2E7D32', '#388E3C', '#4CAF50', '#66BB6A', '#81C784']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 62)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '尼众佛学院最需加强的课程（多选）', 15)
    save_fig(fig, 15)

# ============================================================
# Figure 16: 传统戒律与现代伦理结合 (Horizontal Bar)
# ============================================================
def fig16():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['"不杀生"→尊重生命\n生态保护理念', '"不偷盗"→遵纪守法\n廉洁自律准则',
              '"不妄语"→诚实守信\n言行一致规范', '"慈悲济世"→常态化\n慈善公益事业',
              '"学修一体化"→系统化\n教学与实践体系']
    values = [60, 58, 55, 52, 40]
    colors_h = ['#1565C0', '#1976D2', '#1E88E5', '#42A5F5', '#90CAF9']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 68)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '传统戒律与现代伦理结合的现实转化方式（多选）', 16)
    save_fig(fig, 16)

# ============================================================
# Figure 17: 传统智慧创造性转化 (Bar Chart)
# ============================================================
def fig17():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['完全可以\n(超越时代价值)', '大部分可以\n(需灵活调整)', '部分可以\n(已不适应)',
              '较难实现\n(根本矛盾)', '无法实现']
    values = [22, 58, 18, 1, 1]
    colors_h = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    bars = ax.bar(labels, values, color=colors_h, width=0.55, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 68)
    style_thesis(ax, '传统教育智慧能否实现创造性转化', 17)
    save_fig(fig, 17)

# ============================================================
# Figure 18: "爱国爱教"落实情况 (Bar Chart)
# ============================================================
def fig18():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    labels = ['落实很好\n(融入全过程)', '落实较好\n(形式大于内容)', '落实一般\n(仅停留在口号)',
              '落实较差\n(缺乏实践载体)', '基本没有落实']
    values = [10, 30, 45, 12, 3]
    colors_h = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    bars = ax.bar(labels, values, color=colors_h, width=0.55, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_ylim(0, 55)
    style_thesis(ax, '"爱国爱教"理念在当代僧才教育的落实情况', 18)
    save_fig(fig, 18)

# ============================================================
# Figure 19: 隆莲法师实践最重要启示 (Horizontal Bar)
# ============================================================
def fig19():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['坚守"以戒为师"\n筑牢僧才培育根基', '强化"爱国爱教、服务社会"\n彰显佛教时代价值',
              '坚持"佛学与文化并重"\n提升僧才综合素养', '推动"传统与现代融合"\n创新教育模式',
              '完善戒律传承\n与僧团制度建设', '促进佛教与现代社会\n的良性互动']
    values = [62, 60, 58, 55, 40, 38]
    colors_h = ['#1B5E20', '#2E7D32', '#388E3C', '#4CAF50', '#66BB6A', '#81C784']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 70)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '隆莲法师实践对当代佛教院校的最重要启示（多选）', 19)
    save_fig(fig, 19)

# ============================================================
# Figure 20: 最迫切改革方向 (Horizontal Bar)
# ============================================================
def fig20():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    labels = ['优化课程体系\n(佛学文化实践三位一体)', '强化戒律教育的\n系统性与实践性',
              '改革教育管理\n推进规范化与科学化', '明确培养目标\n兼顾爱国爱教与服务社会',
              '加强师资建设\n建立僧俗结合团队', '推动院校开放\n促进佛教与社会互动']
    values = [35, 22, 18, 15, 8, 2]
    colors_h = ['#1B5E20', '#388E3C', '#4CAF50', '#66BB6A', '#81C784', '#A5D6A7']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}%',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=10, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 42)
    ax.set_xlabel('选择比例 (%)', fontproperties=cn_font_label)
    style_thesis(ax, '当代僧才教育最迫切的改革方向', 20)
    save_fig(fig, 20)

# ============================================================
# Figure 21: 认同度 (Pie Chart)
# ============================================================
def fig21():
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))
    labels = ['完全认同', '基本认同', '中立', '不太认同', '完全不认同']
    sizes = [38, 50, 10, 1, 1]
    colors_p = ['#1B5E20', '#4CAF50', '#FFC107', '#FF9800', '#F44336']
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_p,
        autopct='%1.0f%%', startangle=90,
        textprops={'fontproperties': cn_font_small}, pctdistance=0.82,
        explode=(0.03, 0.05, 0, 0.1, 0.1))
    for t in autotexts:
        t.set_fontproperties(cn_font_small)
        t.set_fontsize(10)
    centre_circle = plt.Circle((0,0), 0.50, fc='white')
    ax.add_artist(centre_circle)
    ax.set_title('图21  对"僧才教育是推动佛教中国化\n最关键路径"的认同度 (N=100)',
                 fontproperties=cn_font_title, pad=20)
    save_fig(fig, 21)

# ============================================================
# Figure 22: 综合对比图 - 核心素养 vs 最需加强课程 (Radar or Grouped)
# ============================================================
def fig22():
    """Radar chart: 核心素养评价雷达图"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), subplot_kw=dict(projection='polar'))

    categories = ['爱国爱教\n坚定信念', '佛学理论\n功底', '戒律修持', '社会服务\n能力',
                  '文化素养', '创新思维', '跨文化\n对话能力']
    values = [88, 85, 78, 65, 60, 48, 32]

    N = len(categories)
    angles = [n / N * 2 * np.pi for n in range(N)]
    values_plot = values + [values[0]]
    angles_plot = angles + [angles[0]]

    ax.plot(angles_plot, values_plot, 'o-', linewidth=2.5, color='#1B5E20', markersize=8)
    ax.fill(angles_plot, values_plot, alpha=0.15, color='#4CAF50')
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontproperties=cn_font_small, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontproperties=cn_font_small)
    ax.grid(True)
    ax.set_title('图22  佛教僧才核心素养评价雷达图', fontproperties=cn_font_title, pad=25)
    save_fig(fig, 22)

# ============================================================
# Figure 23: 综合柱状对比 - 各项认同度对比
# ============================================================
def fig23():
    fig, ax = plt.subplots(1, 1, figsize=(14, 7))

    # Multiple comparison bars across dimensions
    dimensions = ['僧才教育\n重要性\n(非常重要)', '爱国爱教\n信念\n(核心素养)',
                  '佛学理论\n功底\n(核心素养)', '戒律修持\n(核心素养)',
                  '以戒为师\n启示\n(启示很大)', '佛学与文学\n并重\n(意义很大)',
                  '传统智慧\n可转化\n(大部分可以)', '僧才教育是\n关键路径\n(完全+基本认同)']
    values = [62, 88, 85, 78, 48, 52, 58, 88]
    colors_b = ['#1B5E20', '#1565C0', '#1976D2', '#1E88E5', '#FF9800',
                '#FFA726', '#4CAF50', '#2E7D32']

    bars = ax.bar(range(len(dimensions)), values, color=colors_b, width=0.6, edgecolor='white', linewidth=0.5)
    set_bar_labels(ax, bars)
    ax.set_xticks(range(len(dimensions)))
    ax.set_xticklabels(dimensions, fontproperties=cn_font_small, fontsize=10)
    ax.set_ylim(0, 100)
    ax.set_ylabel('选择比例 (%)', fontproperties=cn_font_label)
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.4, linewidth=1)
    ax.text(len(dimensions)-0.5, 52, '50%分界线', color='red', fontsize=9,
            fontproperties=cn_font_small)
    style_thesis(ax, '关键指标认同度综合对比', 23)
    save_fig(fig, 23)

# ============================================================
# Figure 24: 开放题建议词云风格统计图
# ============================================================
def fig24():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    suggestions = [
        ('加大尼众佛学院\n专项经费投入', 28),
        ('搭建僧俗结合\n跨领域师资队伍', 22),
        ('增设社会公益\n现代管理类课程', 20),
        ('推动佛学院与高校\n建立合作实践基地', 18),
        ('完善戒律教育\n考核机制', 15),
        ('将"爱国爱教"\n融入日常教学', 12),
    ]
    labels = [s[0] for s in suggestions]
    values = [s[1] for s in suggestions]
    colors_h = ['#1B5E20', '#388E3C', '#4CAF50', '#66BB6A', '#81C784', '#A5D6A7']
    bars = ax.barh(range(len(labels)), values, color=colors_h, height=0.55, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontproperties=cn_font_small, fontsize=11)
    for bar, val in zip(bars, values):
        ax.annotate(f'{val}条建议',
                    xy=(val, bar.get_y() + bar.get_height()/2),
                    xytext=(5, 0), textcoords='offset points',
                    va='center', fontsize=11, fontproperties=cn_font_small, fontweight='bold')
    ax.set_xlim(0, 35)
    ax.set_xlabel('建议条数', fontproperties=cn_font_label)
    style_thesis(ax, '开放题建议汇总（题22）', 24)
    save_fig(fig, 24)

# ============================================================
# Run all
# ============================================================
print('开始生成硕士论文标准图形...')
print()

figs = [
    fig01, fig02, fig03, fig04, fig05, fig06, fig07, fig08,
    fig09, fig10, fig11, fig12, fig13, fig14, fig15, fig16,
    fig17, fig18, fig19, fig20, fig21, fig22, fig23, fig24,
]

for i, f in enumerate(figs, 1):
    try:
        f()
    except Exception as e:
        print(f'  ✗ fig_{i:02d} failed: {e}')

print()
print(f'完成！共生成 {len(figs)} 张图形，保存于 {OUTPUT_DIR}/')
