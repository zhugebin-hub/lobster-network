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
    
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 28)
    c.setFillColor(white)
    c.drawCentredString(width/2, height - 120, '利玛窦的译名实践')
    
    c.setStrokeColor(HexColor('#3b82f6'))
    c.setLineWidth(3)
    c.line(width/2 - 50, height - 145, width/2 + 50, height - 145)
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 14)
    c.setFillColor(HexColor('#9ca3af'))
    c.drawCentredString(width/2, height - 175, '从"太极""理"的诠释看耶儒思想的碰撞与调适')
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 12)
    c.setFillColor(HexColor('#6b7280'))
    c.drawCentredString(width/2, height - 220, '答辩人：全方明  |  指导教师：王绪琴')
    c.drawCentredString(width/2, height - 245, '2026 年 6 月')

def draw_text_box(c, x, y, width, text, font_size=12, color='#d1d5db', bold=False):
    """绘制文本框"""
    from reportlab.lib.colors import HexColor
    c.setFont('NotoSans-Bold' if bold else 'NotoSans' if font_registered else 'Helvetica', font_size)
    c.setFillColor(HexColor(color))
    
    lines = text.split('\n')
    line_height = font_size * 1.4
    for i, line in enumerate(lines):
        c.drawString(x, y - i * line_height, line)
    return y - len(lines) * line_height

def draw_page(c, width, height, title, sections):
    """内容页"""
    draw_gradient_bg(c, width, height)
    from reportlab.lib.colors import HexColor, white
    
    y = height - 60
    
    # 标题
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 24)
    c.setFillColor(white)
    c.drawCentredString(width/2, y, title)
    
    y -= 45
    
    # 内容
    for section_title, content in sections:
        # 小标题
        c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 14)
        c.setFillColor(HexColor('#60a5fa'))
        c.drawString(50, y, section_title)
        y -= 22
        
        # 内容
        c.setFont('NotoSans' if font_registered else 'Helvetica', 12)
        c.setFillColor(HexColor('#d1d5db'))
        
        lines = content.split('\n')
        for line in lines:
            c.drawString(50, y, line)
            y -= 18
        y -= 10
    
    return y

def main():
    pdf_path = '/home/admin/.openclaw/workspace/ppt-defenses/ricci-defense-user.pdf'
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # 页 1: 封面
    draw_title_page(c, width, height)
    c.showPage()
    
    # 页 2: 研究背景与方法
    draw_gradient_bg(c, width, height)
    from reportlab.lib.colors import HexColor, white
    
    y = height - 60
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 24)
    c.setFillColor(white)
    c.drawCentredString(width/2, y, '研究背景与方法')
    
    y -= 45
    
    # 研究背景
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 13)
    c.setFillColor(HexColor('#60a5fa'))
    c.drawString(50, y, '研究背景')
    y -= 20
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '16 世纪末，利玛窦面临用儒家话语表达基督教神学而不被儒学消化的难题。')
    y -= 25
    
    # 核心议题
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 13)
    c.setFillColor(HexColor('#60a5fa'))
    c.drawString(50, y, '核心议题')
    y -= 20
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '以利玛窦对宋明理学核心范畴"理"与"太极"的处理为中心，')
    y -= 16
    c.drawString(50, y, '考察跨文化对话中"概念挪用与改造"的具体机制。')
    y -= 25
    
    # 研究主线
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 13)
    c.setFillColor(HexColor('#60a5fa'))
    c.drawString(50, y, '研究主线')
    y -= 20
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '沿着"策略—接受—意义"的脉络，揭示跨文化理解中"意义迁移"的内在规律。')
    y -= 35
    
    # 研究方法
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 13)
    c.setFillColor(HexColor('#a78bfa'))
    c.drawString(50, y, '研究方法')
    y -= 20
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '① 概念史方法：追踪"理"与"太极"的语义场位移，测量概念挪用的幅度')
    y -= 16
    c.drawString(50, y, '② 修辞与论证分析：剖析《天主实义》的论辩策略与论证类型')
    y -= 16
    c.drawString(50, y, '③ 接受史视角：考察明清士大夫的不同反应，揭示"创造性误解"的历史影响力')
    
    c.showPage()
    
    # 页 3: 核心观点
    draw_gradient_bg(c, width, height)
    
    y = height - 60
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 24)
    c.setFillColor(white)
    c.drawCentredString(width/2, y, '核心观点')
    
    y -= 45
    
    # 双重策略
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 14)
    c.setFillColor(HexColor('#60a5fa'))
    c.drawString(50, y, '"釜底抽薪"与"借壳上市"的双重策略')
    y -= 22
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '釜底抽薪：')
    y -= 16
    c.drawString(70, y, '依据西方经院哲学"自立者 - 依赖者"框架，将"理"与"太极"降格为属性，')
    y -= 16
    c.drawString(70, y, '否定其生成万物的本体论地位。')
    y -= 20
    
    c.drawString(50, y, '借壳上市：')
    y -= 16
    c.drawString(70, y, '利用先秦经典中"上帝"的文化符号，植入基督教神学内核，')
    y -= 16
    c.drawString(70, y, '建立信仰的本土合法性。')
    y -= 35
    
    # 概念嫁接术
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 14)
    c.setFillColor(HexColor('#a78bfa'))
    c.drawString(50, y, '"概念嫁接术"与"创造性误解"')
    y -= 22
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '利玛窦的策略是带有理论自觉的"以西格中"式概念重构。')
    y -= 18
    c.drawString(50, y, '明清士大夫的"前理解"促成了"创造性误解"，')
    y -= 16
    c.drawString(50, y, '这不仅是跨文化传播的常态，更是文化创新的核心动力。')
    
    c.showPage()
    
    # 页 4: 成果与启示
    draw_gradient_bg(c, width, height)
    
    y = height - 60
    c.setFont('NotoSans' if font_registered else 'Helvetica-Bold', 24)
    c.setFillColor(white)
    c.drawCentredString(width/2, y, '成果与当代基督教中国化的启示')
    
    y -= 45
    
    # 历史定性
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 14)
    c.setFillColor(HexColor('#60a5fa'))
    c.drawString(50, y, '历史定性成果')
    y -= 22
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '利玛窦的译名实践是触及本体论的跨文明"化学反应"，')
    y -= 16
    c.drawString(50, y, '是"基督教中国化"最早的策源地与关键事件。')
    y -= 35
    
    # 当代启示
    c.setFont('NotoSans-Bold' if font_registered else 'Helvetica-Bold', 14)
    c.setFillColor(HexColor('#a78bfa'))
    c.drawString(50, y, '对当代"基督教中国化"的正向意义')
    y -= 22
    
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#d1d5db'))
    c.drawString(50, y, '本土化表达：')
    y -= 16
    c.drawString(70, y, '"中国化"并非教义妥协，而是信仰在本土文化土壤中的')
    y -= 16
    c.drawString(70, y, '生根发芽与在地化表达。')
    y -= 20
    
    c.drawString(50, y, '深度概念对话：')
    y -= 16
    c.drawString(70, y, '不能停留在表层符号借用，需深入中国哲学核心概念体系')
    y -= 16
    c.drawString(70, y, '（如天人关系、心性论）展开实质性对话。')
    y -= 35
    
    # 结语
    c.setStrokeColor(HexColor('#8b5cf6'))
    c.setLineWidth(1)
    c.roundRect(50, y - 40, width - 100, 35, 8, stroke=True, fill=False)
    c.setFont('NotoSans' if font_registered else 'Helvetica', 11)
    c.setFillColor(HexColor('#a78bfa'))
    c.drawCentredString(width/2, y - 22, '各美其美，美人之美，美美与共，天下大同 — 费孝通')
    
    c.save()
    print(f'PDF generated: {pdf_path}')
    print(f'File size: {os.path.getsize(pdf_path) / 1024:.1f} KB')

if __name__ == '__main__':
    main()
