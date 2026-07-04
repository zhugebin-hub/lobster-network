#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 尝试注册中文字体
font_paths = [
    '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
    '/home/admin/.local/share/fonts/NotoSansSC-Regular.ttf',
]

font_registered = False
for fp in font_paths:
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('NotoSans', fp))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', fp))  # 用同一字体文件模拟粗体
            font_registered = True
            print(f"Using font: {fp}")
            break
        except Exception as e:
            print(f"Font error: {e}")
            continue

if not font_registered:
    print("Warning: No Chinese font found, using fallback")

def draw_gradient_bg(c, width, height):
    """Draw dark gradient background"""
    from reportlab.lib.colors import HexColor
    c.setFillColor(HexColor('#0a0a0a'))
    c.rect(0, 0, width, height, fill=True, stroke=False)

def draw_title_page(c, width, height):
    """封面页"""
    draw_gradient_bg(c, width, height)
    
    from reportlab.lib.colors import HexColor, white
    
    # 顶部小字
    c.setFont('NotoSans' if font_registered else 'Helvetica', 10)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width/2, height - 80, '浙江省宗教界"双通"人才研修班 · 毕业论文答辩')
    
    # 主标题
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 36)
    c.setFillColor(white)
    c.drawCentredString(width/2, height - 150, '利玛窦的译名实践')
    
    # 分隔线
    c.setStrokeColor(HexColor('#3b82f6'))
    c.setLineWidth(3)
    c.line(width/2 - 40, height - 175, width/2 + 40, height - 175)
    
    # 副标题
    c.setFont('NotoSans' if font_registered else 'Helvetica', 18)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawCentredString(width/2, height - 220, '从"太极""理"的诠释看耶儒思想的碰撞与调适')
    
    # 作者信息
    c.setFont('NotoSans' if font_registered else 'Helvetica', 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width/2, height - 280, '全方明  |  指导教师：王绪琴')
    c.drawCentredString(width/2, height - 305, '2026年6月')

def draw_content_page(c, width, height, title, bullets, subtitle=''):
    """内容页"""
    draw_gradient_bg(c, width, height)
    
    from reportlab.lib.colors import HexColor, white
    
    y = height - 80
    
    # 标题
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 28)
    c.setFillColor(white)
    c.drawCentredString(width/2, y, title)
    
    y -= 50
    
    # 副标题
    if subtitle:
        c.setFont('NotoSans' if font_registered else 'Helvetica', 14)
        c.setFillColor(HexColor('#9ca3af'))
        c.drawCentredString(width/2, y, subtitle)
        y -= 40
    
    # 要点
    c.setFont('NotoSans' if font_registered else 'Helvetica', 16)
    c.setFillColor(HexColor('#d1d5db'))
    
    for bullet in bullets:
        # 处理高亮标记
        parts = bullet.split('**')
        x = 80
        for i, part in enumerate(parts):
            if i % 2 == 1:  # 高亮部分
                c.setFillColor(HexColor('#60a5fa'))
                c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 16)
            else:
                c.setFillColor(HexColor('#d1d5db'))
                c.setFont('NotoSans' if font_registered else 'Helvetica', 16)
            c.drawString(x, y, part)
            x += c.stringWidth(part, 'NotoSans' if font_registered else 'Helvetica', 16)
        y -= 35

def main():
    pdf_path = '/home/admin/.openclaw/workspace/ppt-defenses/ricci-defense.pdf'
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # 页 1: 封面
    draw_title_page(c, width, height)
    c.showPage()
    
    # 页 2: 研究问题
    draw_content_page(c, width, height, '核心困境', [
        '如何用**儒家话语**表达**基督教神学**？',
        '利玛窦的选择：进入**"理"与"太极"**的语义场',
        '本质：一次有自觉的**"概念嫁接"**',
    ])
    c.showPage()
    
    # 页 3: 方法框架
    draw_content_page(c, width, height, '三重方法', [
        '**① 概念史** — 追踪语义位移',
        '**② 修辞分析** — 拆解论证逻辑',
        '**③ 接受史** — 揭示意义游移',
        '',
        '策略 → 接受 → **意义**',
    ])
    c.showPage()
    
    # 页 4: 釜底抽薪
    draw_content_page(c, width, height, '釜底抽薪', [
        '**① 降格：** "理" = **"依赖者"**（偶性），非本体',
        '**② 剥离：** 否定"理"的**生成能力**',
        '**③ 反转：** 以**"古儒"**压**"今儒"**',
    ])
    c.showPage()
    
    # 页 5: 借壳上市
    draw_content_page(c, width, height, '借壳上市', [
        '**壳：上帝** — 《诗》《书》中的至上神',
        '**核：Deus** — 位格性造物主',
        '',
        '借用中国文化之壳，装入基督教信仰之核',
    ])
    c.showPage()
    
    # 页 6: 三种接受
    draw_content_page(c, width, height, '三种回应', [
        '**合作性接受**（徐光启·李之藻）："补儒易佛"',
        '**选择性借鉴**（李贽）：借力反理学',
        '**批判性拒绝**（黄宗羲）：维护儒学正统',
    ])
    c.showPage()
    
    # 页 7: 创造性误解
    draw_content_page(c, width, height, '创造性误解', [
        '"误解不是意外，而是**常态**"',
        '前理解 → 意义游移 → **新思想诞生**',
        '双重误读 = 利玛窦误解理学 + 士人误解利玛窦',
    ])
    c.showPage()
    
    # 页 8: 结论
    draw_content_page(c, width, height, '跨文明的"化学反应"', [
        '不是"物理拼贴"，而是**不可逆的概念化合**',
        '当代启示：文化适应 ≠ 妥协，而是**本土化表达**',
        '创造性误解是文化创新的**源泉**',
    ])
    c.showPage()
    
    # 页 9: 致谢
    draw_gradient_bg(c, width, height)
    from reportlab.lib.colors import HexColor, white
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 42)
    c.setFillColor(white)
    c.drawCentredString(width/2, height - 180, '感谢聆听')
    c.setFont('NotoSans' if font_registered else 'Helvetica', 16)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawCentredString(width/2, height - 240, '恳请各位老师批评指正')
    c.drawCentredString(width/2, height - 280, '全方明 · 浙江省宗教界"双通"人才研修班')
    
    c.save()
    print(f'PDF generated: {pdf_path}')
    print(f'File size: {os.path.getsize(pdf_path) / 1024:.1f} KB')

if __name__ == '__main__':
    main()
