#!/usr/bin/env python3
"""
叶畏兵毕业论文 - 添加脚注上标
在引用位置插入上标参考文献编号
"""
import docx
import re
from copy import deepcopy
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INPUT = "/home/admin/.openclaw/workspace/叶畏兵_论文_完善版.docx"
OUTPUT = "/home/admin/.openclaw/workspace/叶畏兵_论文_终稿.docx"

doc = docx.Document(INPUT)

# ==========================================
# 脚注映射表：段落索引 → 该段内每个引用位置对应的参考文献编号
# ==========================================
# 根据正文内容逐一匹配参考文献
footnote_map = {
    # 第一章 引言
    124: [59],       # "五个认同"引用 → 习近平2021讲话[59]
    126: [56, 62],   # 王伟光[56]、游斌[62]
    127: [63, 54, 51], # 张志刚[63]、牟钟鉴[54]、何虎生[51]
    138: [16, 4],    # Nygren[16]、Aquinas[4]
    140: [70, 52],   # 朱全红[70]、黄勇[52]
    142: [10, 6],    # Casanova[10]、Bellah[6]
    143: [23, 25, 15], # Troeltsch[23]、Weber[25]、Niebuhr[15]
    144: [8, 19],    # Bevans[8]、Schreiter[19]
    146: [63, 36, 40], # 张志刚[63]、牟钟鉴[36]、王作安[40]
    147: [30, 37, 41, 42], # 段琦[30]、唐晓峰[37]、徐以骅[41]、游斌[42]
    148: [29, 33, 45], # 陈宗皋[29]、李平晔[33]、赵敦华[45]
    150: [47, 66, 50], # 曹正勇[47]、赵卫红[66]、韩雪莉[50]
    151: [55, 53, 48], # 王思琪[55]、吕臻雨[53]、陈金羽[48]
    # 第二章
    184: [16],       # Nygren
    185: [4, 17],    # Aquinas[4]、Pope Benedict[17]
    189: [2],        # 刘耘华[2]
    190: [70],       # 朱全红[70]
    191: [65],       # 赵天恩[65]
    192: [30, 53],   # 段琦[30]、吕臻雨[53]
    196: [60],       # 杨宝安[60]
    215: [2],        # 刘耘华[2]
    216: [9],        # Bhabha[9]
    220: [8],        # Bevans[8]
    221: [19],       # Schreiter[19]
    223: [7],        # Berger[7]
    # 第三章
    229: [55],       # 王思琪[55]
    230: [52],       # 黄勇[52]
    245: [53],       # 吕臻雨[53]
    246: [11],       # Hauerwas[11]
    254: [10],       # Casanova[10]
    265: [27],       # 陈来[27]
    269: [52],       # 黄勇[52]
    270: [9],        # Bhabha[9]
    275: [61],       # 杨凤岗[61]
    283: [48],       # 陈金羽[48]
    293: [48],       # 陈金羽
    # 第五章
    311: [2],        # 刘耘华
    320: [67],       # 浙江神学院[67]
    321: [67],       # 研讨会[67]
    322: [64],       # 张忠成[64]
    324: [46, 35],   # 莫幸福[46][35]
    340: [79],       # 光盐基金会[79]
    343: [53],       # 吕臻雨
    351: [59],       # 习近平讲话
}

# ==========================================
# 添加上标函数
# ==========================================
def insert_superscript(para, char_pos, number):
    """在段落指定字符位置后插入上标数字"""
    current_pos = 0
    for run in para.runs:
        if not run.text:
            continue
        run_len = len(run.text)
        if current_pos <= char_pos < current_pos + run_len:
            # 找到目标run
            insert_idx = char_pos - current_pos + 1  # 标点后插入
            
            text_before = run.text[:insert_idx]
            text_after = run.text[insert_idx:]
            
            # 修改当前run
            run.text = text_before
            
            # 创建上标run
            from lxml import etree
            sup_run = etree.SubElement(run._element.getparent(), 
                                        run._element.tag, 
                                        run._element.attrib)
            
            # 复制样式
            rPr = run._element.find(qn('w:rPr'))
            if rPr is not None:
                from copy import deepcopy
                sup_rPr = deepcopy(rPr)
                sup_run.append(sup_rPr)
            
            # 确保有rPr
            rPr_elem = sup_run.find(qn('w:rPr'))
            if rPr_elem is None:
                rPr_elem = OxmlElement(qn('w:rPr'))
                sup_run.append(rPr_elem)
            
            # 设置上标
            vert_align = OxmlElement(qn('w:vertAlign'))
            vert_align.set(qn('w:val'), 'superscript')
            rPr_elem.append(vert_align)
            
            # 设置较小字号
            sz = OxmlElement(qn('w:sz'))
            sz.set(qn('w:val'), '16')
            rPr_elem.append(sz)
            
            szCs = OxmlElement(qn('w:szCs'))
            szCs.set(qn('w:val'), '16')
            rPr_elem.append(szCs)
            
            # 添加文本
            t_elem = OxmlElement(qn('w:t'))
            t_elem.text = f'[{number}]'
            t_elem.set(qn('xml:space'), 'preserve')
            sup_run.append(t_elem)
            
            # 插入剩余文本
            if text_after:
                after_run = etree.SubElement(sup_run.getparent(),
                                            run._element.tag,
                                            run._element.attrib)
                if rPr is not None:
                    after_run.append(deepcopy(rPr))
                t2 = OxmlElement(qn('w:t'))
                t2.text = text_after
                t2.set(qn('xml:space'), 'preserve')
                after_run.append(t2)
            
            return True
        current_pos += run_len
    return False

# ==========================================
# 处理所有引用位置
# ==========================================
print("=== 添加脚注上标 ===")
total_added = 0

for p_idx, para in enumerate(doc.paragraphs):
    if p_idx not in footnote_map:
        continue
    
    t = para.text
    ref_nums = footnote_map[p_idx]
    
    # 找到所有引用位置
    positions = []
    for m in re.finditer(r'([。》"）]) (?=[\u4e00-\u9fffA-Z])', t):
        positions.append(m.start())
    
    # 为每个位置添加上标
    for seq, pos in enumerate(positions):
        if seq < len(ref_nums) and ref_nums[seq] is not None:
            if insert_superscript(para, pos, ref_nums[seq]):
                total_added += 1
                ref = ref_nums[seq]
                # 找到对应参考文献
                print(f"  [{ref}] ...{t[max(0,pos-30):pos]}...")

print(f"\n✅ 共添加 {total_added} 个脚注上标")

# ==========================================
# 保存
# ==========================================
doc.save(OUTPUT)
print(f"\n保存至: {OUTPUT}")
