#!/usr/bin/env python3
"""Convert Markdown to PDF with Chinese font support"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import re

# Register Chinese font
try:
    pdfmetrics.registerFont(TTFont('Chinese', '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc'))
    print("✅ Chinese font registered: WenQuanYi Micro Hei")
except Exception as e:
    print(f"⚠️ Font registration issue: {e}")

def convert_md_to_pdf(md_file, pdf_file):
    """Markdown to PDF converter with Chinese support"""
    
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2*cm
    )
    
    # Create styles with Chinese font
    styles = getSampleStyleSheet()
    
    # Register Chinese font for all styles
    chinese_font = 'Chinese'
    
    styles.add(ParagraphStyle(
        name='ChineseTitle',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=22,
        spaceAfter=30,
        alignment=TA_CENTER,
        leading=30
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseH1',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=16,
        spaceAfter=12,
        spaceBefore=20,
        leading=22
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseH2',
        parent=styles['Heading2'],
        fontName=chinese_font,
        fontSize=14,
        spaceAfter=10,
        spaceBefore=16,
        leading=18
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseH3',
        parent=styles['Heading3'],
        fontName=chinese_font,
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        leading=16
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseNormal',
        parent=styles['Normal'],
        fontName=chinese_font,
        fontSize=11,
        spaceAfter=6,
        leading=16,
        alignment=TA_JUSTIFY
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=9,
        spaceAfter=6,
        leading=12,
        textColor=colors.darkblue
    ))
    
    story = []
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Process content
    lines = content.split('\n')
    in_code_block = False
    code_text = []
    table_rows = []
    in_table = False
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        # Code blocks
        if line.startswith('```'):
            if in_code_block:
                # End code block
                code_content = '\n'.join(code_text)
                story.append(Paragraph(f"<b>代码:</b>", styles['ChineseNormal']))
                story.append(Paragraph(code_content.replace('<', '&lt;').replace('>', '&gt;'), styles['ChineseCode']))
                story.append(Spacer(1, 12))
                code_text = []
                in_code_block = False
            else:
                in_code_block = True
            continue
        
        if in_code_block:
            code_text.append(line)
            continue
        
        # Empty line
        if not line:
            if in_table:
                # End table
                if table_rows:
                    table = Table(table_rows, colWidths=[5*cm, 5*cm, 5*cm])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                        ('FONTSIZE', (0, 0), (-1, 0), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                        ('FONTSIZE', (0, 1), (-1, -1), 10),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 12))
                    table_rows = []
                    in_table = False
            story.append(Spacer(1, 6))
            continue
        
        # Headers
        if line.startswith('# ') and not line.startswith('##'):
            text = line[2:]
            story.append(Paragraph(text, styles['ChineseH1']))
            story.append(Spacer(1, 12))
        elif line.startswith('## '):
            text = line[3:]
            story.append(Paragraph(text, styles['ChineseH2']))
            story.append(Spacer(1, 10))
        elif line.startswith('### '):
            text = line[4:]
            story.append(Paragraph(text, styles['ChineseH3']))
            story.append(Spacer(1, 8))
        elif line.startswith('#### '):
            text = line[5:]
            story.append(Paragraph(text, styles['ChineseH3']))
            story.append(Spacer(1, 6))
        
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:]
            story.append(Paragraph(f"• {text}", styles['ChineseNormal']))
        
        # Table detection
        elif line.startswith('|') and '|' in line[1:]:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and not all(c.startswith('---') or c.startswith('===') for c in cells):
                in_table = True
                table_rows.append(cells)
        
        # Bold text
        elif line.startswith('**') and line.endswith('**'):
            text = line[2:-2]
            story.append(Paragraph(f"<b>{text}</b>", styles['ChineseNormal']))
        
        # Regular paragraph
        elif len(line) > 1:
            # Handle inline formatting
            formatted = line
            formatted = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', formatted)
            formatted = re.sub(r'`(.+?)`', r'<font color="blue">\1</font>', formatted)
            
            if len(formatted) > 80:
                story.append(Paragraph(formatted, styles['ChineseNormal']))
            else:
                story.append(Paragraph(formatted, styles['ChineseNormal']))
        
        # Page break
        if line.startswith('---') and len(line) > 10:
            story.append(PageBreak())
    
    # Handle any remaining table
    if table_rows:
        table = Table(table_rows, colWidths=[5*cm, 5*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), chinese_font),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), chinese_font),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
    
    doc.build(story, onFirstPage=lambda c, p: None, onLaterPages=lambda c, p: None)
    print(f"✅ PDF 已生成：{pdf_file}")

if __name__ == '__main__':
    convert_md_to_pdf('experiment-report-xujie.md', 'experiment-report-xujie-v2.pdf')
