#!/usr/bin/env python3
"""
将论文中的旧图替换为新图：
- image4.jpeg（三层架构图）→ new_arch_diagram.png
- image7.png（三层架构图，与image4相同内容）→ new_arch_diagram.png
- image14.png（旧版docx代码截图）→ new_docx_code.png
"""
import zipfile
import shutil
import os
from pathlib import Path

SRC = "/home/ubuntu/毕业论文_修订版.docx"
DST = "/home/ubuntu/毕业论文_修订版2.docx"
ARCH_IMG = "/home/ubuntu/thesis_pics/new_arch_diagram.png"
CODE_IMG = "/home/ubuntu/thesis_pics/new_docx_code.png"

# 复制原文件
shutil.copy2(SRC, DST)

# 确定替换映射：docx内部路径 → 新图片路径
# image4.jpeg 和 image7.png 替换为架构图（png）
# image14.png 替换为代码截图
REPLACEMENTS = {
    "word/media/image4.jpeg": ARCH_IMG,
    "word/media/image7.png": ARCH_IMG,
    "word/media/image14.png": CODE_IMG,
}

# 读取原始zip内容
with zipfile.ZipFile(SRC, 'r') as zin:
    names = zin.namelist()
    file_contents = {}
    for name in names:
        file_contents[name] = zin.read(name)

# 处理image4.jpeg → image4.png（格式变化需要更新关系文件）
# 先检查image4是否真的是jpeg
print("原始图片列表：")
for n in names:
    if 'media' in n:
        print(f"  {n}")

# 写入新zip，替换图片
with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as zout:
    for name in names:
        if name in REPLACEMENTS:
            # 读取新图片
            new_img_path = REPLACEMENTS[name]
            with open(new_img_path, 'rb') as f:
                new_data = f.read()
            # 如果原来是jpeg但新图是png，需要保留原扩展名或更新关系
            # 这里直接用原文件名写入新内容（Word只看文件名，不看扩展名内容）
            zout.writestr(name, new_data)
            print(f"已替换：{name} → {new_img_path}")
        else:
            zout.writestr(name, file_contents[name])

print(f"\n修订版2已保存：{DST}")
print(f"文件大小：{os.path.getsize(DST):,} bytes")
