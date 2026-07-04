#!/usr/bin/env python3
"""Convert HTML to PDF using reportlab"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import html

def convert_md_to_pdf(md_file, pdf_file):
    """Simple Markdown to PDF converter"""
    
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='ChineseTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER
    ))
    
    story = []
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple markdown parsing
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 12))
            continue
        
        # Headers
        if line.startswith('# '):
            text = line[2:]
            story.append(Paragraph(text, styles['Heading1']))
            story.append(Spacer(1, 12))
        elif line.startswith('## '):
            text = line[3:]
            story.append(Paragraph(text, styles['Heading2']))
            story.append(Spacer(1, 10))
        elif line.startswith('### '):
            text = line[4:]
            story.append(Paragraph(text, styles['Heading3']))
            story.append(Spacer(1, 8))
        elif line.startswith('#### '):
            text = line[5:]
            story.append(Paragraph(text, styles['Heading4']))
            story.append(Spacer(1, 6))
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:]
            story.append(Paragraph(f"• {text}", styles['Normal']))
        elif line.startswith('```'):
            continue
        elif line.startswith('|'):
            # Table row - simplify for now
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if cells and cells[0] not in ['---', '===']:
                text = ' | '.join(cells)
                story.append(Paragraph(text, styles['Normal']))
        elif len(line) > 100:
            # Long line - treat as paragraph
            story.append(Paragraph(line, styles['Normal']))
        else:
            # Regular text
            if len(line) > 2:
                story.append(Paragraph(line, styles['Normal']))
        
        if line.startswith('---') and len(line) > 10:
            story.append(PageBreak())
    
    doc.build(story)
    print(f"✅ PDF created: {pdf_file}")

if __name__ == '__main__':
    convert_md_to_pdf('experiment-report-xujie.md', 'experiment-report-xujie.pdf')
