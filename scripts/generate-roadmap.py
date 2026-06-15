#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术发展路径图生成脚本
使用 matplotlib 生成类似 Visio 的流程图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 颜色定义
BLUE_DARK = '#1E5FBF'
BLUE_LIGHT = '#E8F1FF'
GREEN_DARK = '#00A862'
GREEN_LIGHT = '#E8F5E9'
WHITE = '#FFFFFF'
GRAY_LIGHT = '#F5F5F5'

# 创建画布 (横向 A3 比例)
fig, ax = plt.subplots(figsize=(20, 8), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis('off')

# 五个阶段的位置和宽度
stages = [
    {'x': 2, 'width': 16, 'title': '1 博士阶段', 'color': BLUE_DARK, 'bg': BLUE_LIGHT},
    {'x': 20, 'width': 16, 'title': '2 博士后阶段', 'color': BLUE_DARK, 'bg': BLUE_LIGHT},
    {'x': 38, 'width': 24, 'title': '3 MSCA-PF 阶段：SafeGuide', 'color': GREEN_DARK, 'bg': GREEN_LIGHT},
    {'x': 64, 'width': 16, 'title': '4 3-5 年目标', 'color': BLUE_DARK, 'bg': BLUE_LIGHT},
    {'x': 82, 'width': 16, 'title': '5 未来 10 年目标', 'color': BLUE_DARK, 'bg': BLUE_LIGHT},
]

# 绘制五个阶段
for i, stage in enumerate(stages):
    # 主矩形框
    rect = patches.Rectangle(
        (stage['x'], 12), stage['width'], 35,
        linewidth=2, edgecolor=stage['color'], facecolor=stage['bg'],
        alpha=0.8
    )
    ax.add_patch(rect)
    
    # 标题栏
    title_rect = patches.Rectangle(
        (stage['x'], 43), stage['width'], 4,
        linewidth=0, facecolor=stage['color']
    )
    ax.add_patch(title_rect)
    
    # 标题文字
    ax.text(stage['x'] + stage['width']/2, 45, stage['title'],
            ha='center', va='center', fontsize=11, weight='bold', color=WHITE)
    
    # 阶段间箭头
    if i < len(stages) - 1:
        arrow_x = stage['x'] + stage['width']
        ax.annotate('', xy=(arrow_x + 1.5, 30), xytext=(arrow_x + 0.5, 30),
                   arrowprops=dict(arrowstyle='->', color=BLUE_DARK, lw=2))

# 添加各阶段内容 (简化版)
content_y = 38

# 阶段 1 内容
ax.text(stages[0]['x'] + 2, content_y, '研究基础:', fontsize=9, weight='bold', color=BLUE_DARK)
ax.text(stages[0]['x'] + 2, content_y - 2, '传感器测试、多模态信号处理', fontsize=8)
ax.text(stages[0]['x'] + 2, content_y - 4, '时间序列建模、人工智能', fontsize=8)
ax.text(stages[0]['x'] + 2, content_y - 7, '能力积累:', fontsize=9, weight='bold', color=BLUE_DARK)
ax.text(stages[0]['x'] + 2, content_y - 9, '系统科研训练 + 国际联合培养', fontsize=8)
ax.text(stages[0]['x'] + 2, content_y - 11, '形成初步国际科研经验', fontsize=8)

# 阶段 2 内容
ax.text(stages[1]['x'] + 2, content_y, '研究聚焦:', fontsize=9, weight='bold', color=BLUE_DARK)
ax.text(stages[1]['x'] + 2, content_y - 2, '小样本条件下的异构传感器', fontsize=8)
ax.text(stages[1]['x'] + 2, content_y - 4, '通用补偿、可解释建模', fontsize=8)
ax.text(stages[1]['x'] + 2, content_y - 7, '能力提升:', fontsize=9, weight='bold', color=BLUE_DARK)
ax.text(stages[1]['x'] + 2, content_y - 9, '主持项目、指导学生、产学研合作', fontsize=8)
ax.text(stages[1]['x'] + 2, content_y - 11, '形成独立科研与团队组织能力', fontsize=8)

# 阶段 3 内容 (MSCA-PF)
ax.text(stages[2]['x'] + 2, content_y, 'A) 平台与资源', fontsize=9, weight='bold', color=GREEN_DARK)
ax.text(stages[2]['x'] + 2, content_y - 2, '机器人研究基础', fontsize=8)
ax.text(stages[2]['x'] + 2, content_y - 4, '人工智能学术环境', fontsize=8)
ax.text(stages[2]['x'] + 2, content_y - 6, '研究者发展支持', fontsize=8)
ax.text(stages[2]['x'] + 2, content_y - 8, '开放科学体系', fontsize=8)

ax.text(stages[2]['x'] + 13, content_y, 'B) 关键跨学科能力提升', fontsize=9, weight='bold', color=GREEN_DARK)
ax.text(stages[2]['x'] + 13, content_y - 2, '工程问题转化能力', fontsize=8)
ax.text(stages[2]['x'] + 13, content_y - 4, '跨领域实验组织与验证能力', fontsize=8)
ax.text(stages[2]['x'] + 13, content_y - 6, '智能系统研发能力', fontsize=8)
ax.text(stages[2]['x'] + 13, content_y - 8, '合作协调与成果转化能力', fontsize=8)

# 阶段 4 内容
ax.text(stages[3]['x'] + 2, content_y, '发表高水平成果', fontsize=8)
ax.text(stages[3]['x'] + 2, content_y - 3, '建设开放数据与算法资源', fontsize=8)
ax.text(stages[3]['x'] + 2, content_y - 6, '申请国家级和国际合作项目', fontsize=8)
ax.text(stages[3]['x'] + 2, content_y - 9, '推动与埃克塞特大学长期合作', fontsize=8)
# 底部蓝色框
bottom_rect = patches.Rectangle((stages[3]['x'] + 1, 14), 14, 3, 
                                linewidth=0, facecolor=BLUE_DARK, alpha=0.7)
ax.add_patch(bottom_rect)
ax.text(stages[3]['x'] + 8, 15.5, '研究方向升级 +', fontsize=8, color=WHITE, ha='center')
ax.text(stages[3]['x'] + 8, 13.5, '国际网络拓展', fontsize=8, color=WHITE, ha='center')

# 阶段 5 内容
ax.text(stages[4]['x'] + 2, content_y, '组织跨学科团队', fontsize=8)
ax.text(stages[4]['x'] + 2, content_y - 3, '牵头大型科研项目国际影响力计划', fontsize=8)
ax.text(stages[4]['x'] + 2, content_y - 6, '推动安全、可信、包容的辅助机器人', fontsize=8)
ax.text(stages[4]['x'] + 2, content_y - 9, '培养青年研究人员，拓展产学研', fontsize=8)
# 底部深蓝色框
bottom_rect = patches.Rectangle((stages[4]['x'] + 1, 14), 14, 3, 
                                linewidth=0, facecolor=BLUE_DARK, alpha=0.9)
ax.add_patch(bottom_rect)
ax.text(stages[4]['x'] + 8, 15.5, '成为该领域具有', fontsize=8, color=WHITE, ha='center')
ax.text(stages[4]['x'] + 8, 13.5, '国际影响力的学术带头人', fontsize=8, color=WHITE, ha='center')

# 底部流程条
flow_y = 7
flow_items = [
    ('技术基础', 10),
    ('独立研究', 26),
    ('MSCA-PF 跨学科拓展', 42),
    ('国际合作网络', 62),
    ('学术领导力', 82),
]

# 流程条背景
flow_bg = patches.Rectangle((2, flow_y - 2), 96, 6, 
                            linewidth=2, edgecolor='#CCCCCC', facecolor=WHITE, alpha=0.5)
ax.add_patch(flow_bg)

# 流程节点
for i, (text, x_pos) in enumerate(flow_items):
    # 圆形节点
    circle = patches.Circle((x_pos, flow_y), 2.5, linewidth=2, 
                           edgecolor=BLUE_DARK, facecolor=WHITE, alpha=0.8)
    ax.add_patch(circle)
    ax.text(x_pos, flow_y, text, ha='center', va='center', fontsize=8, weight='bold', color=BLUE_DARK)
    
    # 箭头
    if i < len(flow_items) - 1:
        ax.text(x_pos + 4, flow_y, '»', ha='center', va='center', 
               fontsize=16, color=BLUE_DARK, weight='bold')

# 添加标题
ax.text(50, 49, '学术发展路径图', ha='center', va='center', 
       fontsize=16, weight='bold', color='#333333')

# 保存图片
plt.tight_layout()
plt.savefig('/home/admin/.openclaw/workspace/academic-roadmap.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
plt.savefig('/home/admin/.openclaw/workspace/academic-roadmap.pdf', 
           bbox_inches='tight', facecolor='white')

print("✅ 图表已生成:")
print("   - /home/admin/.openclaw/workspace/academic-roadmap.png")
print("   - /home/admin/.openclaw/workspace/academic-roadmap.pdf")
print("\n💡 提示：")
print("   1. 可以使用此 PNG/PDF 作为 Visio 绘制的参考")
print("   2. 详细的 Visio 绘制步骤请查看：visio-redraw-guide.md")
print("   3. 在 Visio 中按照指南重新绘制可获得更专业的效果")
