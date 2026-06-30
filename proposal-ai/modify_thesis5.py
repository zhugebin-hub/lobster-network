#!/usr/bin/env python3
"""最后处理P239"目录域"描述"""
from docx import Document

DST = "/home/ubuntu/毕业论文_修订版.docx"
doc = Document(DST)

def replace_para_text(para, new_text):
    if para.runs:
        para.runs[0].text = new_text
        for r in para.runs[1:]:
            r.text = ""
    else:
        para.text = new_text

for i, para in enumerate(doc.paragraphs):
    text = para.text
    if "目录域" in text and "docx 这个库" in text:
        new_text = text.replace(
            "样式、分页、页眉页脚和目录域都能程序化控制",
            "样式、分页、表格、封面页、单元格合并都能程序化控制"
        )
        if new_text != text:
            replace_para_text(para, new_text)
            print(f"[P{i}] 最后修正完成")

doc.save(DST)
