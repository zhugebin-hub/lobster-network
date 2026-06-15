#!/usr/bin/env python3
"""
纯 lxml + zipfile 构建 .docx，包含真正的 Word 脚注。
不依赖 python-docx 的脚注功能（它不支持）。
"""

from lxml import etree
import zipfile, os, tempfile, re, json, shutil
from collections import Counter

# 命名空间
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
W_ = lambda t: '{%s}%s' % (W, t)
R_ = lambda t: '{%s}%s' % (R, t)

# ============================================================
# 1. 读入原文
# ============================================================
with open('/home/admin/.openclaw/media/inbound/b6aef016-21bc-4db5-bd2a-82e52e349ada', 'r', encoding='utf-8') as f:
    raw = f.read()

SEP = '脚  注'
idx = raw.index(SEP)
body_text = raw[:idx]
fn_text = raw[idx:]

# ============================================================
# 2. 解析脚注
# ============================================================
sup_digits = '⁰¹²³⁴⁵⁶⁷⁸⁹'
sup_map = {c: str(i) for i, c in enumerate(sup_digits)}

def sup_to_num(s):
    return int(''.join(sup_map.get(c, c) for c in s if c in sup_map))

footnote_entries = {}
for line in fn_text.split('\n'):
    line = line.strip()
    if not line or line.startswith('===') or line.startswith('脚'):
        continue
    if line[0] in sup_digits:
        chars = []
        for c in line:
            if c in sup_digits: chars.append(c)
            else: break
        num = sup_to_num(''.join(chars))
        footnote_entries[num] = line[len(''.join(chars)):].strip()

print(f"解析到 {len(footnote_entries)} 条脚注")

# ============================================================
# 3. 去重
# ============================================================
seen, dedup_map, new_num = {}, {}, 0
for old_n in sorted(footnote_entries.keys()):
    key = re.sub(r'第\d+页', '', footnote_entries[old_n]).strip()
    if key in seen:
        dedup_map[old_n] = seen[key]
    else:
        new_num += 1
        seen[key] = new_num
        dedup_map[old_n] = new_num

dedup_footnotes = {n: footnote_entries[o] for o, n in dedup_map.items()}
counts = Counter(dedup_map.values())
merged = {n: c for n, c in counts.items() if c > 1}
print(f"去重后: {new_num} 条（合并 {len(merged)} 组）")

# ============================================================
# 4. 替换正文引用为占位符
# ============================================================
def replace_refs(text):
    def repl(m):
        old_n = sup_to_num(m.group(1))
        return f'__FN{dedup_map[old_n]}__' if old_n in dedup_map else m.group(0)
    return re.sub(r'([⁰-⁹]+)', repl, text)

body_text = replace_refs(body_text)

# ============================================================
# 5. 拆分章节
# ============================================================
parts = re.split(r'(第[一二三四五六七八九十]+节\s+[^\n]{1,80})', body_text)
abstract_raw = parts[0].strip() if parts else ''
sections = []
for i in range(1, len(parts), 2):
    title = parts[i].strip()
    content = parts[i + 1] if i + 1 < len(parts) else ''
    sections.append((title, content))

print(f"拆分为 {len(sections)} 节")

# ============================================================
# 6. 构建 XML 文档
# ============================================================

# --- document.xml ---
nsmap_doc = {
    'w': W, 'r': R,
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'
}
doc_root = etree.Element(W_('document'), nsmap=nsmap_doc)
doc_root.set('{http://schemas.openxmlformats.org/markup-compatibility/2006}IgnorableNamespaces', 'w14')
body = etree.SubElement(doc_root, W_('body'))

def add_rPr(r, font_size='24', bold=False, font_name='宋体', superscript=False):
    rPr = etree.SubElement(r, W_('rPr'))
    rFonts = etree.SubElement(rPr, W_('rFonts'))
    rFonts.set(W_('ascii'), font_name)
    rFonts.set(W_('hAnsi'), font_name)
    rFonts.set(W_('eastAsia'), font_name)
    rFonts.set(W_('cs'), font_name)
    sz = etree.SubElement(rPr, W_('sz'))
    sz.set(W_('val'), font_size)
    szCs = etree.SubElement(rPr, W_('szCs'))
    szCs.set(W_('val'), font_size)
    if bold:
        etree.SubElement(rPr, W_('b'))
        etree.SubElement(rPr, W_('bCs'))
    if superscript:
        va = etree.SubElement(rPr, W_('vertAlign'))
        va.set(W_('val'), 'superscript')

def add_text_run(parent, text, font_size='24', bold=False, font_name='宋体', superscript=False):
    r = etree.SubElement(parent, W_('r'))
    add_rPr(r, font_size, bold, font_name, superscript)
    t = etree.SubElement(r, W_('t'))
    t.text = text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

def add_footnote_ref(parent, fn_id):
    r = etree.SubElement(parent, W_('r'))
    rPr = etree.SubElement(r, W_('rPr'))
    sz = etree.SubElement(rPr, W_('sz'))
    sz.set(W_('val'), '16')
    szCs = etree.SubElement(rPr, W_('szCs'))
    szCs.set(W_('val'), '16')
    va = etree.SubElement(rPr, W_('vertAlign'))
    va.set(W_('val'), 'superscript')
    rFonts = etree.SubElement(rPr, W_('rFonts'))
    rFonts.set(W_('ascii'), 'Times New Roman')
    rFonts.set(W_('hAnsi'), 'Times New Roman')
    rFonts.set(W_('eastAsia'), '宋体')
    fn_ref = etree.SubElement(r, W_('footnoteReference'))
    fn_ref.set(W_('id'), str(fn_id))

def mk_para(p_style=None, indent=True, alignment=None, before='0', after='120', line='240'):
    p = etree.SubElement(body, W_('p'))
    pPr = etree.SubElement(p, W_('pPr'))
    if p_style:
        ps = etree.SubElement(pPr, W_('pStyle'))
        ps.set(W_('val'), p_style)
    if indent:
        ind = etree.SubElement(pPr, W_('ind'))
        ind.set(W_('left'), '480')
        ind.set(W_('firstLine'), '480')
    if alignment:
        jc = etree.SubElement(pPr, W_('jc'))
        jc.set(W_('val'), alignment)
    sp = etree.SubElement(pPr, W_('spacing'))
    sp.set(W_('before'), before)
    sp.set(W_('after'), after)
    sp.set(W_('line'), line)
    sp.set(W_('lineRule'), 'auto')
    return p

def add_text_para(text, p_style=None, indent=True, alignment=None, before='0', after='120', line='240'):
    p = mk_para(p_style, indent, alignment, before, after, line)
    parts = re.split(r'(__FN\d+__)', text)
    for part in parts:
        if not part:
            continue
        m = re.match(r'^__FN(\d+)__$', part)
        if m:
            add_footnote_ref(p, int(m.group(1)))
        else:
            add_text_run(p, part)

# === 标题页 ===
for _ in range(8):
    p = mk_para(indent=False, after='0', line='0')

# 主标题
p = mk_para(indent=False, alignment='center', after='120')
add_text_run(p, '利玛窦的译文实践', '52', True, '黑体')

# 副标题
p = mk_para(indent=False, alignment='center', after='300')
add_text_run(p, '\u2014\u2014"太极""理"的翻译与概念挪用', '36', False, '黑体')

# 作者
p = mk_para(indent=False, alignment='center', after='600')
add_text_run(p, '戴建华', '28')

# 日期
p = mk_para(indent=False, alignment='center', after='0')
add_text_run(p, '2026年6月', '24')

# 分页
p = mk_para(after='0', line='0')
r = etree.SubElement(p, W_('r'))
br = etree.SubElement(r, W_('br'))
br.set(W_('type'), 'page')

# === 摘要 ===
p = mk_para(p_style='Heading1', indent=False, before='240', after='120')
add_text_run(p, '摘  要', '32', True, '黑体')

if '关键词' in abstract_raw:
    abstract_only = abstract_raw[:abstract_raw.index('关键词')].strip()
    keywords_part = abstract_raw[abstract_raw.index('关键词'):].strip()
    add_text_para(abstract_only, indent=False)
    p = mk_para(indent=False, before='120', after='400')
    add_text_run(p, keywords_part, '24', True, '黑体')
else:
    add_text_para(abstract_raw.strip(), indent=False)

# === 正文 ===
for sec_title, sec_content in sections:
    p = mk_para(p_style='Heading2', indent=False, before='240', after='120')
    add_text_run(p, sec_title, '28', True, '黑体')
    
    for para in re.split(r'\n{2,}', sec_content):
        para = para.strip()
        if para:
            add_text_para(para)

# sectPr
sectPr = etree.SubElement(body, W_('sectPr'))
pgSz = etree.SubElement(sectPr, W_('pgSz'))
pgSz.set(W_('w'), '11906')
pgSz.set(W_('h'), '16838')
pgMar = etree.SubElement(sectPr, W_('pgMar'))
pgMar.set(W_('top'), '1440')
pgMar.set(W_('right'), '1800')
pgMar.set(W_('bottom'), '1440')
pgMar.set(W_('left'), '1800')

# ============================================================
# 7. 构建 footnotes.xml
# ============================================================
fn_ns = {'w': W, 'r': R}
fn_root = etree.Element(W_('footnotes'), nsmap=fn_ns)

# separator
sep_fn = etree.SubElement(fn_root, W_('footnote'))
sep_fn.set(W_('type'), 'separator')
sep_fn.set(W_('id'), '-1')
sep_p = etree.SubElement(sep_fn, W_('p'))
sep_pPr = etree.SubElement(sep_p, W_('pPr'))
sep_sp = etree.SubElement(sep_pPr, W_('spacing'))
sep_sp.set(W_('after'), '0')
sep_sp.set(W_('line'), '240')
sep_sp.set(W_('lineRule'), 'auto')
sep_r = etree.SubElement(sep_p, W_('r'))
etree.SubElement(sep_r, W_('separator'))

# continuationSeparator
cont_fn = etree.SubElement(fn_root, W_('footnote'))
cont_fn.set(W_('type'), 'continuationSeparator')
cont_fn.set(W_('id'), '0')
cont_p = etree.SubElement(cont_fn, W_('p'))
cont_pPr = etree.SubElement(cont_p, W_('pPr'))
cont_sp = etree.SubElement(cont_pPr, W_('spacing'))
cont_sp.set(W_('after'), '0')
cont_sp.set(W_('line'), '240')
cont_sp.set(W_('lineRule'), 'auto')
cont_r = etree.SubElement(cont_p, W_('r'))
etree.SubElement(cont_r, W_('continuationSeparator'))

# 脚注内容
for fn_id in sorted(dedup_footnotes.keys()):
    fn_text = dedup_footnotes[fn_id]
    fn = etree.SubElement(fn_root, W_('footnote'))
    fn.set(W_('id'), str(fn_id))
    p = etree.SubElement(fn, W_('p'))
    pPr = etree.SubElement(p, W_('pPr'))
    ind = etree.SubElement(pPr, W_('ind'))
    ind.set(W_('left'), '420')
    ind.set(W_('hanging'), '420')
    sp = etree.SubElement(pPr, W_('spacing'))
    sp.set(W_('line'), '240')
    sp.set(W_('lineRule'), 'auto')
    r = etree.SubElement(p, W_('r'))
    rPr = etree.SubElement(r, W_('rPr'))
    sz = etree.SubElement(rPr, W_('sz'))
    sz.set(W_('val'), '18')
    szCs = etree.SubElement(rPr, W_('szCs'))
    szCs.set(W_('val'), '18')
    rf = etree.SubElement(rPr, W_('rFonts'))
    rf.set(W_('ascii'), '宋体')
    rf.set(W_('hAnsi'), '宋体')
    rf.set(W_('eastAsia'), '宋体')
    t = etree.SubElement(r, W_('t'))
    t.text = fn_text
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

# ============================================================
# 8. 写入 .docx
# ============================================================
tmpdir = tempfile.mkdtemp()
os.makedirs(os.path.join(tmpdir, 'word', '_rels'))
os.makedirs(os.path.join(tmpdir, 'word', 'theme'))
os.makedirs(os.path.join(tmpdir, 'docProps'))
os.makedirs(os.path.join(tmpdir, '_rels'))

# document.xml
with open(os.path.join(tmpdir, 'word', 'document.xml'), 'wb') as f:
    f.write(etree.tostring(doc_root, xml_declaration=True, encoding='UTF-8', standalone='yes'))

# footnotes.xml
with open(os.path.join(tmpdir, 'word', 'footnotes.xml'), 'wb') as f:
    f.write(etree.tostring(fn_root, xml_declaration=True, encoding='UTF-8', standalone='yes'))

# document.xml.rels
with open(os.path.join(tmpdir, 'word', '_rels', 'document.xml.rels'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/webSettings" Target="webSettings.xml"/>
<Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
<Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
<Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes" Target="footnotes.xml"/>
</Relationships>''')

# settings.xml
with open(os.path.join(tmpdir, 'word', 'settings.xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:footnotePr>
<w:numRestart w:val="eachPage"/>
<w:numFmt w:val="decimal"/>
<w:start w:val="1"/>
</w:footnotePr>
<w:compat>
<w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>
</w:compat>
</w:settings>''')

# styles.xml
with open(os.path.join(tmpdir, 'word', 'styles.xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<w:docDefaults>
<w:rPrDefault>
<w:rPr>
<w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:eastAsia="宋体" w:cs="宋体"/>
<w:sz w:val="24"/><w:szCs w:val="24"/>
<w:lang w:val="zh-CN" w:eastAsia="zh-CN" w:bidi="ar-SA"/>
</w:rPr>
</w:rPrDefault>
<w:pPrDefault>
<w:pPr>
<w:spacing w:after="120" w:line="240" w:lineRule="auto"/>
</w:pPr>
</w:pPrDefault>
</w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal">
<w:name w:val="Normal"/><w:qFormat/>
<w:rPr><w:rFonts w:ascii="宋体" w:hAnsi="宋体" w:eastAsia="宋体"/><w:sz w:val="24"/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading1">
<w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
<w:rPr><w:rFonts w:ascii="黑体" w:hAnsi="黑体" w:eastAsia="黑体"/><w:sz w:val="32"/><w:b/><w:bCs/></w:rPr>
</w:style>
<w:style w:type="paragraph" w:styleId="Heading2">
<w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:before="240" w:after="120"/></w:pPr>
<w:rPr><w:rFonts w:ascii="黑体" w:hAnsi="黑体" w:eastAsia="黑体"/><w:sz w:val="28"/><w:b/><w:bCs/></w:rPr>
</w:style>
</w:styles>''')

# numbering.xml
with open(os.path.join(tmpdir, 'word', 'numbering.xml'), 'wb') as f:
    f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')

# webSettings.xml
with open(os.path.join(tmpdir, 'word', 'webSettings.xml'), 'wb') as f:
    f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:webSettings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')

# fontTable.xml
with open(os.path.join(tmpdir, 'word', 'fontTable.xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fontTable xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:font w:name="宋体"><w:altName w:val="SimSun"/><w:panose1 w:val="02010600030101010101"/><w:charset w:val="86"/><w:family w:val="auto"/><w:pitch w:val="variable"/></w:font>
<w:font w:name="黑体"><w:altName w:val="SimHei"/><w:panose1 w:val="02010600030101010101"/><w:charset w:val="86"/><w:family w:val="auto"/><w:pitch w:val="variable"/></w:font>
<w:font w:name="Times New Roman"><w:panose1 w:val="02020603050405020304"/><w:charset w:val="00"/><w:family w:val="auto"/><w:pitch w:val="variable"/></w:font>
</w:fontTable>''')

# theme
with open(os.path.join(tmpdir, 'word', 'theme', 'theme1.xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
<a:themeElements>
<a:clrScheme name="Office">
<a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
<a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
<a:dk2><a:srgbClr val="1F497D"/></a:dk2>
<a:lt2><a:srgbClr val="EEECE1"/></a:lt2>
<a:accent1><a:srgbClr val="4F81BD"/></a:accent1>
<a:accent2><a:srgbClr val="C0504D"/></a:accent2>
<a:accent3><a:srgbClr val="9BBB59"/></a:accent3>
<a:accent4><a:srgbClr val="8064A2"/></a:accent4>
<a:accent5><a:srgbClr val="4BACC6"/></a:accent5>
<a:accent6><a:srgbClr val="F79646"/></a:accent6>
<a:hlink><a:srgbClr val="0000FF"/></a:hlink>
<a:folHlink><a:srgbClr val="800080"/></a:folHlink>
</a:clrScheme>
<a:fontScheme name="Office">
<a:majorFont><a:latin typeface="黑体"/><a:ea typeface="黑体"/></a:majorFont>
<a:minorFont><a:latin typeface="宋体"/><a:ea typeface="宋体"/></a:minorFont>
</a:fontScheme>
<a:fmtScheme name="Office">
<a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst><a:ln w="9525" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>
</a:fmtScheme>
</a:themeElements>
</a:theme>''')

# _rels/.rels
with open(os.path.join(tmpdir, '_rels', '.rels'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>''')

# docProps
with open(os.path.join(tmpdir, 'docProps', 'core.xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>利玛窦的译文实践</dc:title>
<dc:creator>戴建华</dc:creator>
</cp:coreProperties>''')

with open(os.path.join(tmpdir, 'docProps', 'app.xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
<Application>python-lxml</Application>
</Properties>''')

# [Content_Types].xml
with open(os.path.join(tmpdir, '[Content_Types].xml'), 'wb') as f:
    f.write(b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/word/webSettings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml"/>
<Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
<Override PartName="/word/footnotes.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml"/>
<Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>''')

# 打包
output = '/home/admin/.openclaw/workspace/利玛窦译文实践_标准论文格式.docx'
if os.path.exists(output):
    os.remove(output)

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root_dir, dirs, files in os.walk(tmpdir):
        for file in files:
            full_path = os.path.join(root_dir, file)
            arc_name = os.path.relpath(full_path, tmpdir)
            zf.write(full_path, arc_name)

print(f"\n✅ 已保存: {output}")
print(f"文件大小: {os.path.getsize(output) / 1024:.1f} KB")

# 验证
with zipfile.ZipFile(output, 'r') as zf:
    fn_xml = zf.read('word/footnotes.xml')
    fn_tree = etree.fromstring(fn_xml)
    fns = fn_tree.findall(W_('footnote'))
    print(f"脚注数量: {len(fns) - 2} 条")
    
    doc_xml = zf.read('word/document.xml')
    doc_tree = etree.fromstring(doc_xml)
    fn_refs = doc_tree.findall('.//' + W_('footnoteReference'))
    print(f"正文脚注引用: {len(fn_refs)} 处")
    
    settings_xml = zf.read('word/settings.xml')
    settings_tree = etree.fromstring(settings_xml)
    fn_pr = settings_tree.find('.//w:footnotePr', {'w': W})
    if fn_pr is not None:
        nr = fn_pr.find(W_('numRestart'))
        if nr is not None:
            print(f"numRestart: {nr.get(W_('val'))}")
    
    print(f"文件结构: {sorted(zf.namelist())}")

shutil.rmtree(tmpdir)
