#!/usr/bin/env python3
"""生成docxGenerator.ts关键代码截图，使用Pillow+Pygments渲染高亮代码"""

import subprocess
import sys

# 安装pygments
subprocess.run([sys.executable, "-m", "pip", "install", "pygments", "-q"], check=True)

from pygments import highlight
from pygments.lexers import TypeScriptLexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name

# 要展示的代码片段（主函数 + 封面页构造）
CODE = '''\
import {
  Document, Packer, Paragraph, TextRun,
  AlignmentType, Table, TableRow, TableCell,
  WidthType, BorderStyle, ShadingType,
  VerticalMergeType, PageBreak,
} from "docx";

// ===== 主导出函数 =====
export async function generateDocxBuffer(
  proposal: ProposalInfo,
  sections: SectionData[]
): Promise<Buffer> {
  const doc = new Document({
    sections: [{
      properties: {
        page: { margin: { top: 1440, right: 1080,
                          bottom: 1440, left: 1440 } },
      },
      children: [
        // 第1页：封面
        ...buildCoverPage(proposal, piName),
        // 第2页：填报说明
        ...buildFillingInstructions(),
        // 第3页：项目基本信息表
        ...buildBasicInfoTable(proposal, piName, piEmail, piPhone),
        // 第4页：申报项目简介
        ...buildProjectSummary(proposal),
        // 正文各章节
        ...buildBodySections(sections),
      ],
    }],
  });
  const buffer = await Packer.toBuffer(doc);
  return buffer as Buffer;
}

// ===== 封面页 =====
function buildCoverPage(
  proposal: ProposalInfo, piName: string
): Paragraph[] {
  return [
    para([txt("申报编号：", { bold: true, size: 24 })]),
    // 大标题（居中，黑体44号）
    para([txt("国家重点研发计划",
              { size: 44, bold: true, font: "黑体" })],
         { align: AlignmentType.CENTER }),
    para([txt("项目申报书",
              { size: 44, bold: true, font: "黑体" })],
         { align: AlignmentType.CENTER, spaceAfter: 1200 }),
    // 信息行（带下划线）
    underline("项目名称：", proposal.title || ""),
    underline("所属专项：", proposal.researchField || ""),
    underline("推荐单位：", proposal.recommendingUnit || ""),
    underline("申报单位：", proposal.applicantUnit || ""),
    underline("项目负责人：", piName),
    // 底部落款
    para([txt("中华人民共和国科学技术部制",
              { bold: true, size: 28, font: "黑体" })],
         { align: AlignmentType.CENTER }),
  ];
}
'''

out_path = '/home/ubuntu/thesis_pics/new_docx_code.png'

formatter = ImageFormatter(
    style='vs',
    font_name='Liberation Mono',
    font_size=16,
    line_numbers=True,
    line_number_bg='#f0f0f0',
    line_number_fg='#888888',
    line_pad=4,
    image_pad=12,
    hl_lines=[],
)

result = highlight(CODE, TypeScriptLexer(), formatter)
with open(out_path, 'wb') as f:
    f.write(result)

print(f"代码截图已生成：{out_path}")
