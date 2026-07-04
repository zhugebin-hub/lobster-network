---
name: docx-generator
description: 生成和编辑 Word 文档（.docx）。支持从 Markdown 转换、用 Python 脚本生成、模板填充、表格/图片/样式处理。触发场景：用户要求"生成 word"、"写文档"、"导出 docx"、"word 文档"、"生成报告"、"制作合同"、"生成简历 word"等。
---

# Word 文档生成器

支持两种方式生成 .docx 文件：

## 方式一：Markdown → DOCX（pandoc，推荐快速生成）

适合从已有 Markdown 内容快速生成排版良好的 Word 文档。

```bash
# 基本转换
pandoc input.md -o output.docx

# 带样式（需先提取默认参考文档）
pandoc input.md -o output.docx --reference-doc=reference.docx

# 设置元数据
pandoc input.md -o output.docx \
  --metadata title="文档标题" \
  --metadata author="作者" \
  --metadata date="2026-05-08"
```

**提取默认参考文档（首次使用）：**
```bash
pandoc --print-default-data-file reference.docx > reference.docx
```

**Markdown 元数据块示例：**
```markdown
---
title: 项目报告
author: 张三
date: 2026-05-08
subject: 项目汇报
lang: zh
---

# 正文内容...
```

## 方式二：Python 脚本生成（python-docx，推荐复杂文档）

适合需要精确控制格式、表格、样式的场景。

### 使用 helper 脚本

```bash
python scripts/generate_docx.py --input content.md --output report.docx
python scripts/generate_docx.py --input content.md --output report.docx --title "标题" --author "作者"
```

### 直接调用 python-docx

```python
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

doc = Document()

# === 中文字体设置 ===
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')

# === 标题 ===
doc.add_heading('一级标题', level=1)
doc.add_heading('二级标题', level=2)

# === 段落 ===
p = doc.add_paragraph('普通段落文本')
p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY  # 两端对齐

# === 加粗/斜体 ===
run = p.add_run('加粗文字')
run.bold = True
run.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)

# === 表格 ===
table = doc.add_table(rows=3, cols=3, style='Table Grid')
table.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = table.cell(0, 0)
cell.text = '表头'
# 合并单元格
cell_a = table.cell(0, 0)
cell_b = table.cell(0, 1)
cell_a.merge(cell_b)

# === 图片 ===
doc.add_picture('image.png', width=Cm(12))

# === 分页 ===
doc.add_page_break()

# === 页眉页脚 ===
section = doc.sections[0]
header = section.header
header.is_linked_to_previous = False
header_para = header.paragraphs[0]
header_para.text = '页眉文字'
footer_para = section.footer.paragraphs[0]
footer_para.text = '页脚文字'

# === 页面设置 ===
section.page_width = Cm(21)   # A4 宽
section.page_height = Cm(29.7)  # A4 高
section.top_margin = Cm(2.54)
section.bottom_margin = Cm(2.54)
section.left_margin = Cm(3.18)
section.right_margin = Cm(3.18)

doc.save('output.docx')
```

## 常用样式速查

| 需求 | 方法 |
|------|------|
| 设置字体 | `run.font.name = '宋体'` + `w:eastAsia` |
| 字号 | `Pt(12)` (小四), `Pt(14)` (四号), `Pt(16)` (三号) |
| 颜色 | `RGBColor(R, G, B)` |
| 居中对齐 | `WD_ALIGN_PARAGRAPH.CENTER` |
| 两端对齐 | `WD_ALIGN_PARAGRAPH.JUSTIFY` |
| 行距 | `pf.line_spacing = Pt(20)` 或 `pf.space_before = Pt(6)` |
| 首行缩进 | 用空格或设置 `paragraph_format.first_line_indent` |
| 表格边框 | `style='Table Grid'` |
| 插入图片 | `add_picture(path, width=Cm(12))` |
| 分页 | `add_page_break()` |

## 中文排版注意事项

1. **必须设置 eastAsia 字体**，否则中文显示异常
2. 常用中文字体：宋体、黑体、楷体、仿宋、微软雅黑
3. 公文标准：仿宋_GB2312 三号字，行距 28-30 磅
4. 学术报告：宋体小四，1.5 倍行距

## 脚本参考

- `scripts/generate_docx.py` — 通用 Markdown → DOCX 转换脚本
