#!/usr/bin/env python3
"""Build the TOP100 book from individual case files according to the directory."""

import os
import subprocess
import glob

SRC_DIR = "/home/admin/.openclaw/media/inbound/TOP100_extracted/TOP100校内案例"
OUT_DIR = "/home/admin/.openclaw/workspace/TOP100_book/chapters"
BOOK_DIR = "/home/admin/.openclaw/workspace/TOP100_book"

os.makedirs(OUT_DIR, exist_ok=True)

# Get all source files
all_files = os.listdir(SRC_DIR)
print(f"Found {len(all_files)} files in source directory")
for f in sorted(all_files):
    print(f"  {f}")

# Map directory entries to filename patterns (partial match)
# Format: (output_file, chapter_label, filename_pattern)
entries = [
    # Preface
    ("00_preface.md", "序", "沈剑军）与"),
    
    # Chapter 1: 智启课堂 · AI赋能教学新范式
    ("01_01.md", "第一章 第1节", "陈亚澜）问题引领"),
    ("01_02.md", "第一章 第2节", "金怡雯）AI融教启思"),
    ("01_03.md", "第一章 第3节", "姚储）情境"),
    ("01_04.md", "第一章 第4节", "江明欢）AI赋能历史"),
    ("01_05.md", "第一章 第5节", "张勤）AI"),
    ("01_06.md", "第一章 第6节", "诸晓惠）基于AI的情境"),
    ("01_07.md", "第一章 第7节", "高宇轩）AI赋能"),
    ("01_08.md", "第一章 第8节", "岑杭）基于AI实时图像"),
    ("01_09.md", "第一章 第9节", "沈剑军）与"),
    
    # Chapter 2: 智创作业 · AI赋能设计新路径
    ("02_01.md", "第二章 第1节", "夏长斌）基于数智作业"),
    ("02_02.md", "第二章 第2节", "肖玲燕）AI应用"),
    ("02_03.md", "第二章 第3节", "朱颖秋）AI智能批阅"),
    ("02_04.md", "第二章 第4节", "陈煜瑶）一核三阶"),
    ("02_05.md", "第二章 第5节", "刘悦）基于大语言模型"),
    ("02_06.md", "第二章 第6节", "彭玲琪）基于智慧作业"),
    ("02_07.md", "第二章 第7节", "陆佳怡）数智赋能"),
    ("02_08.md", "第二章 第8节", "马玲怡）基于AI的初中历史"),
    
    # Chapter 3: 智驭技术 · AI赋能应用新探索
    ("03_01.md", "第三章 第1节", "许嘉诚）AI听说课堂赋能初中英语"),
    ("03_02.md", "第三章 第2节", "郑嘉琳）英语AI听说课堂"),
    ("03_03.md", "第三章 第3节", "杨雨欣）AI赋能教学案例"),
    ("03_04.md", "第三章 第4节", "武莹凡）AI赋能初中数学相似"),
    ("03_05.md", "第三章 第5节", "占丽菲）等式的基本性质"),
    ("03_06.md", "第三章 第6节", "张佳妮）AI赋能地理"),
    ("03_07.md", "第三章 第7节", "姜越）利用gemini3"),
    ("03_08.md", "第三章 第8节", "孙康怡）AI赋能的科学实验"),
    ("03_09.md", "第三章 第9节", "储佳敏）AI赋能微观可视化"),
    ("03_10.md", "第三章 第10节", "裴伊梦）AI赋能初中科学凸透镜"),
    ("03_11.md", "第三章 第11节", "冯建芳）AI赋能初中科学精准"),
    ("03_12.md", "第三章 第12节", "沈正华）数据跑起来"),
    ("03_13.md", "第三章 第13节", "程欣）AI赋能初中社会"),
    ("03_14.md", "第三章 第14节", "方淳）AI赋能心理健康"),
    ("03_15.md", "第三章 第15节", "郭士豪）AI赋能教育教学"),
    ("03_16.md", "第三章 第16节", "申屠楚翘）双轨并行"),
    
    # Chapter 4: 智育良师 · AI赋能成长新生态
    ("04_01.md", "第四章 第1节", "李承城）巧用AI绘图"),
    ("04_02.md", "第四章 第2节", "李雪雯）基于人工智能通识"),
    ("04_03.md", "第四章 第3节", "陈乐凡）AI赋能下"),
    ("04_04.md", "第四章 第4节", "沈艺莹）AI赋能：让"),
]

def find_file(pattern):
    """Find a file matching the pattern."""
    for f in all_files:
        if pattern in f:
            return os.path.join(SRC_DIR, f)
    return None

# Convert each file
converted = 0
failed = 0
skipped_doc = 0
for out_file, label, pattern in entries:
    src_file = find_file(pattern)
    if not src_file:
        print(f"❌ NOT FOUND: pattern='{pattern}'")
        failed += 1
        continue
    
    # Check if it's a .doc file (not .docx) - pandoc can't handle .doc
    if src_file.endswith('.doc') and not src_file.endswith('.docx'):
        print(f"⚠️  SKIP .doc format: {os.path.basename(src_file)}")
        skipped_doc += 1
        failed += 1
        continue
    
    out_path = os.path.join(OUT_DIR, out_file)
    try:
        result = subprocess.run(
            ["pandoc", src_file, "-t", "markdown", "-o", out_path],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and os.path.getsize(out_path) > 50:
            converted += 1
            print(f"✅ {out_file}: {os.path.getsize(out_path)} bytes")
        else:
            print(f"⚠️  {out_file}: pandoc error - {result.stderr[:100]}")
            failed += 1
    except Exception as e:
        print(f"❌ {out_file}: {e}")
        failed += 1

print(f"\nDone: {converted} converted, {failed} failed ({skipped_doc} .doc skipped) out of {len(entries)} entries")

# Now build the combined markdown book
print("\n--- Building combined book ---")

chapters = []
for out_file, label, pattern in entries:
    out_path = os.path.join(OUT_DIR, out_file)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 50:
        with open(out_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chapters.append(content)
    else:
        print(f"⚠️  Skipping missing/small: {out_file}")

combined = "\n\n---\n\n".join(chapters)

book_md = os.path.join(BOOK_DIR, "book.md")
with open(book_md, 'w', encoding='utf-8') as f:
    f.write(combined)

print(f"Combined book: {os.path.getsize(book_md)} bytes")
print(f"Total chapters: {len(chapters)}")
