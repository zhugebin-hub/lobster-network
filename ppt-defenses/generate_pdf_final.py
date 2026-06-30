#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# 注册中文字体
font_paths = ['/usr/share/fonts/wqy-microhei/wqy-microhei.ttc']
font_registered = False
for fp in font_paths:
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('NotoSans', fp))
            pdfmetrics.registerFont(TTFont('NotoSans-Bold', fp))
            font_registered = True
            print(f"Using font: {fp}")
            break
        except:
            continue

def draw_gradient_bg(c, width, height):
    from reportlab.lib.colors import HexColor
    c.setFillColor(HexColor('#0a0a0a'))
    c.rect(0, 0, width, height, fill=True, stroke=False)

def draw_title_page(c, width, height):
    """封面页"""
    draw_gradient_bg(c, width, height)
    from reportlab.lib.colors import HexColor, white
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 10)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width/2, height - 60, '浙江省宗教界"双通"人才研修班 · 毕业论文答辩')
    
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 32)
    c.setFillColor(white)
    c.drawCentredString(width/2, height - 130, '利玛窦的译名实践')
    
    c.setStrokeColor(HexColor('#3b82f6'))
    c.setLineWidth(3)
    c.line(width/2 - 40, height - 155, width/2 + 40, height - 155)
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 14)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawCentredString(width/2, height - 190, '从"太极""理"的诠释看耶儒思想的碰撞与调适')
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width/2, height - 240, '全方明  |  指导教师：王绪琴')
    c.drawCentredString(width/2, height - 260, '2026 年 6 月')

def draw_page(c, width, height, title, subtitle, points, conclusion=None):
    """内容页"""
    draw_gradient_bg(c, width, height)
    from reportlab.lib.colors import HexColor, white
    
    y = height - 70
    
    # 标题
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 26)
    c.setFillColor(white)
    c.drawCentredString(width/2, y, title)
    
    y -= 35
    
    # 副标题
    if subtitle:
        c.setFont('NotoSans' if font_registered else 'Helvetica', 13)
        c.setFillColor(HexColor('#3b82f6'))
        c.drawCentredString(width/2, y, subtitle)
        y -= 35
    
    # 要点
    c.setFont('NotoSans' if font_registered else 'Helvetica', 15)
    c.setFillColor(HexColor('#d1d5db'))
    
    for bullet in points:
        x = 60
        parts = bullet.split('**')
        for i, part in enumerate(parts):
            if i % 2 == 1:
                c.setFillColor(HexColor('#60a5fa'))
                c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 15)
            else:
                c.setFillColor(HexColor('#d1d5db'))
                c.setFont('NotoSans' if font_registered else 'Helvetica', 15)
            c.drawString(x, y, part)
            x += c.stringWidth(part, 'NotoSans' if font_registered else 'Helvetica', 15)
        y -= 30
    
    # 结论框
    if conclusion:
        y -= 15
        c.setStrokeColor(HexColor('#8b5cf6'))
        c.setLineWidth(1)
        c.roundRect(60, y - 55, width - 120, 50, 8, stroke=True, fill=False)
        c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 13)
        c.setFillColor(HexColor('#a78bfa'))
        c.drawString(75, y - 20, conclusion)

def main():
    pdf_path = '/home/admin/.openclaw/workspace/ppt-defenses/ricci-defense-final.pdf'
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # 页 1: 封面
    draw_title_page(c, width, height)
    c.showPage()
    
    # 页 2: 研究问题与方法
    draw_page(c, width, height, 
        '研究问题与方法',
        '核心困境：如何用儒家话语表达基督教神学？',
        [
            '**研究对象：** 利玛窦《天主实义》对"理"与"太极"的诠释策略',
            '**三重方法：** 概念史（追踪语义位移）+ 修辞分析（拆解论证）+ 接受史（揭示意义游移）',
            '**分析框架：** 策略 → 接受 → 意义',
        ])
    c.showPage()
    
    # 页 3: 核心观点
    draw_page(c, width, height,
        '核心观点',
        '两种策略：釜底抽薪 + 借壳上市',
        [
            '**釜底抽薪（破）：** 将"理"降格为"依赖者"，否定其本体地位与生成能力',
            '**借壳上市（立）：** 借用中国经典"上帝"之壳，装入基督教 Deus 之核',
            '**本质：** 一次有理论自觉的"概念嫁接术"，而非简单的文化适应',
        ])
    c.showPage()
    
    # 页 4: 研究结论与当代启示
    draw_page(c, width, height,
        '研究结论与当代启示',
        '对"基督教中国化"的正向思维借鉴',
        [
            '**历史正当性：** 利玛窦实践证明"中国化"是基督教在华发展的内在逻辑',
            '**方法论范本：** 保持信仰内核，用中国文化语言重新表述教义',
            '**双向建构：** 不是单向"同化"，而是"你中有我、我中有你"的创造性融合',
        ],
        '费孝通："各美其美，美人之美，美美与共，天下大同"')
    
    c.save()
    print(f'PDF generated: {pdf_path}')
    print(f'File size: {os.path.getsize(pdf_path) / 1024:.1f} KB')

if __name__ == '__main__':
    main()
