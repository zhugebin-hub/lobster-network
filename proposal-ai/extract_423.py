#!/usr/bin/env python3
from docx import Document

doc = Document("/home/ubuntu/毕业论文_修订版2.docx")

# 找到4.2.3节
in_section = False
section_paras = []
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if "4.2.3" in text:
        in_section = True
        section_paras.append(f"[{i}] [{para.style.name}] {text}")
        continue
    if in_section:
        # 遇到下一个4.x.x节就停止
        if text and text[0].isdigit() and "4.2." not in text and ("4.3" in text or "4.4" in text or "4.2.4" in text):
            break
        section_paras.append(f"[{i}] [{para.style.name}] {text}")
        if len(section_paras) > 50:
            break

for p in section_paras:
    print(p)
