#!/usr/bin/env python3
from docx import Document

doc = Document("/home/ubuntu/毕业论文_修订版2.docx")

# 找到正文中4.2.3节（不是目录，是Heading样式或正文段落）
in_section = False
section_paras = []
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    style = para.style.name
    
    # 跳过目录行（toc样式）
    if 'toc' in style.lower():
        continue
    
    # 找到4.2.3标题
    if "4.2.3" in text and ('Heading' in style or 'heading' in style or style == 'Normal'):
        in_section = True
        section_paras.append(f"[{i}] [{style}] {text}")
        continue
    
    if in_section:
        # 遇到下一个同级或更高级标题就停止
        if text and ('4.2.4' in text or '4.3' in text or '4.4' in text or '第五章' in text):
            break
        section_paras.append(f"[{i}] [{style}] {text}")
        if len(section_paras) > 60:
            break

print(f"共找到 {len(section_paras)} 段：\n")
for p in section_paras:
    print(p)
