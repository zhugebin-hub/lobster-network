#!/usr/bin/env python3
"""Apply template formatting to pandoc-generated docx."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from lxml.etree import SubElement

def set_rfonts(run, font_name='宋体'):
    rpr = run._element.get_or_add_rPr()
    rFonts = rpr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = SubElement(rpr, qn('w:rFonts'))
    rFonts.set(qn('w:eastAsia'), font_name)
    # Also set ascii for English
    rFonts.set(qn('w:ascii'), font_name)

def fix_run(run, font_name='宋体', font_size=Pt(12), bold=False, align=None):
    run.font.name = font_name
    run.font.size = font_size
    run.bold = bold
    set_rfonts(run, font_name)
    # Color
    color_elem = run._element.find(qn('w:color'))
    if color_elem is not None:
        run._element.remove(color_elem)

def process_paragraph(p, level=0):
    """Process a paragraph and apply appropriate formatting."""
    text = p.text.strip()
    if not text:
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        return
    
    p.paragraph_format.line_spacing = 1.5
    
    # Determine level based on content
    is_chapter = False
    is_section = False
    is_subsection = False
    
    # Chapter: ## 第X章
    if text.startswith('第一章') or text.startswith('第二章') or text.startswith('第三章') or text.startswith('第四章') or text.startswith('第五章'):
        is_chapter = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(18)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('第一节') or text.startswith('第二节') or text.startswith('第三节') or text.startswith('第四节') or text.startswith('第五节'):
        is_section = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('一、') or text.startswith('二、') or text.startswith('三、') or text.startswith('四、') or text.startswith('五、'):
        is_subsection = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('结语') or text == '结  语':
        is_chapter = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(18)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('参考文献'):
        is_chapter = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(18)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('附  录') or text.startswith('附录'):
        is_chapter = True
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(18)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('致  谢') or text.startswith('致谢'):
        is_section = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.first_line_indent = 0
    elif text.startswith('论文原创性声明'):
        is_section = True
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        p.paragraph_format.first_line_indent = 0
    else:
        # Regular body text
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.first_line_indent = Cm(0.74)
    
    # Apply font to all runs
    for run in p.runs:
        if is_chapter:
            fix_run(run, '黑体', Pt(16), True)
        elif is_section:
            fix_run(run, '黑体', Pt(14), True)
        elif is_subsection:
            fix_run(run, '黑体', Pt(12), True)
        else:
            # Check if run text is English
            run_text = run.text.strip()
            if run_text and all(c.isascii() for c in run_text):
                fix_run(run, 'Times New Roman', Pt(12), run.bold)
            else:
                fix_run(run, '宋体', Pt(12), run.bold)

def main():
    doc = Document('/home/admin/.openclaw/workspace/论文_新时代道教神仙信仰的传承与中国化路径.docx')
    
    # Page setup
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(3.18)
    
    # Process all paragraphs
    for p in doc.paragraphs:
        process_paragraph(p)
    
    output_path = '/home/admin/.openclaw/workspace/新时代道教神仙信仰的传承与中国化路径_完整版.docx'
    doc.save(output_path)
    print(f'✅ 论文已生成: {output_path}')

if __name__ == '__main__':
    main()
