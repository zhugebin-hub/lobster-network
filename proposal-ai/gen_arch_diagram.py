#!/usr/bin/env python3
"""生成系统三层架构图，使用Noto Sans CJK SC字体"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# 注册并使用Noto Sans CJK SC字体
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
font_bold_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'
prop = fm.FontProperties(fname=font_path)
prop_bold = fm.FontProperties(fname=font_bold_path)

fig, ax = plt.subplots(figsize=(5.5, 11))
ax.set_xlim(0, 10)
ax.set_ylim(0, 22)
ax.axis('off')
fig.patch.set_facecolor('white')

# 颜色配置
LAYER_COLORS = {
    '应用层': '#EBF5FB',
    '服务层': '#EAF7EF',
    '数据层': '#FEF9E7',
}
INNER_BG = 'white'
BORDER_COLOR = '#999999'
TEXT_COLOR = '#1A1A1A'
ARROW_COLOR = '#666666'
LAYER_BORDER = {
    '应用层': '#2980B9',
    '服务层': '#27AE60',
    '数据层': '#D4AC0D',
}

def draw_layer(ax, y_bottom, height, label, items):
    bg = LAYER_COLORS[label]
    border = LAYER_BORDER[label]
    # 外框
    rect = mpatches.FancyBboxPatch(
        (0.8, y_bottom), 8.4, height,
        boxstyle="round,pad=0.15",
        linewidth=1.8,
        edgecolor=border,
        facecolor=bg,
        zorder=1
    )
    ax.add_patch(rect)
    # 层标题（左上角）
    ax.text(1.3, y_bottom + height - 0.6, label,
            ha='left', va='center',
            fontsize=13, fontproperties=prop_bold,
            color=border, zorder=3)

    # 内部小框（均匀分布）
    n = len(items)
    box_h = 0.85
    total_inner = height - 1.2
    spacing = (total_inner - n * box_h) / (n + 1)
    box_w = 6.0
    x_start = 5 - box_w / 2

    for i, item in enumerate(items):
        y_box = y_bottom + spacing + i * (box_h + spacing)
        inner = mpatches.FancyBboxPatch(
            (x_start, y_box), box_w, box_h,
            boxstyle="round,pad=0.05",
            linewidth=1,
            edgecolor=border,
            facecolor=INNER_BG,
            zorder=2
        )
        ax.add_patch(inner)
        ax.text(5, y_box + box_h / 2, item,
                ha='center', va='center',
                fontsize=11.5, fontproperties=prop,
                color=TEXT_COLOR, zorder=3)

# 三层（从下到上）
layers = [
    (0.5,  5.8, '数据层',  ['关系数据库', '配置与模板库']),
    (7.3,  5.8, '服务层',  ['LLM 网关服务', '内容管理服务']),
    (14.1, 6.5, '应用层',  ['前端界面', '工作流引擎', '导出模块']),
]

for y_bottom, height, label, items in layers:
    draw_layer(ax, y_bottom, height, label, items)

# 虚线双向箭头（应用层 ↔ 服务层，服务层 ↔ 数据层）
arrow_kw = dict(
    arrowstyle='<|-|>',
    color=ARROW_COLOR,
    lw=1.5,
    mutation_scale=14,
    linestyle='dashed',
)

# 应用层底 → 服务层顶
ax.annotate('', xy=(5, 13.15), xytext=(5, 14.05),
            arrowprops=arrow_kw, zorder=4)

# 服务层底 → 数据层顶
ax.annotate('', xy=(5, 6.35), xytext=(5, 7.25),
            arrowprops=arrow_kw, zorder=4)

plt.tight_layout(pad=0.3)
out = '/home/ubuntu/thesis_pics/new_arch_diagram.png'
plt.savefig(out, dpi=180, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.close()
print(f"架构图已生成：{out}")
