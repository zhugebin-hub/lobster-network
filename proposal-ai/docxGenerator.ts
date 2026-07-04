import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  AlignmentType,
  Table,
  TableRow,
  TableCell,
  WidthType,
  BorderStyle,
  ShadingType,
  VerticalMergeType,
  PageBreak,
} from "docx";

// ===== 类型定义 =====
interface ProposalInfo {
  id: number;
  title: string;
  researchField?: string | null;
  proposalType: string;
  applicantUnit?: string | null;
  applicantUnitAddress?: string | null;
  applicantUnitCode?: string | null;
  recommendingUnit?: string | null;
  recommendingUnitNature?: string | null;
  principalInvestigatorName?: string | null;
  principalInvestigatorEmail?: string | null;
  principalInvestigatorPhone?: string | null;
  contactPersonName?: string | null;
  contactPersonEmail?: string | null;
  contactPersonPhone?: string | null;
  totalBudget?: number | null;
  centralFunding?: number | null;
  localFunding?: number | null;
  unitFunding?: number | null;
  abstract?: string | null;
  // legacy aliases
  principalInvestigator?: string | null;
  piEmail?: string | null;
  piPhone?: string | null;
  [key: string]: unknown;
}

interface SectionData {
  sectionKey: string;
  title: string;
  content?: string | null;
  status: string;
  wordCount?: number | null;
  [key: string]: unknown;
}

// ===== 常量 =====
const BORDER_SINGLE = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
const BORDER_NONE = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const LABEL_SHADING = { type: ShadingType.CLEAR, fill: "F2F2F2", color: "auto" };
const FONT_HEITI = "黑体";
const FONT_SONGTI = "宋体";

// ===== 辅助函数 =====
function txt(text: string, opts?: {
  bold?: boolean;
  size?: number;
  font?: string;
  color?: string;
  underline?: boolean;
}): TextRun {
  return new TextRun({
    text,
    bold: opts?.bold,
    size: opts?.size ?? 24,
    font: opts?.font ?? FONT_SONGTI,
    color: opts?.color,
    underline: opts?.underline ? {} : undefined,
  });
}

function para(children: TextRun[], opts?: {
  align?: typeof AlignmentType[keyof typeof AlignmentType];
  spaceBefore?: number;
  spaceAfter?: number;
  line?: number;
  indent?: number;
  firstLine?: number;
  pageBreak?: boolean;
}): Paragraph {
  return new Paragraph({
    children,
    alignment: opts?.align,
    spacing: {
      before: opts?.spaceBefore,
      after: opts?.spaceAfter ?? 0,
      line: opts?.line,
    },
    indent: {
      left: opts?.indent,
      firstLine: opts?.firstLine,
    },
    pageBreakBefore: opts?.pageBreak,
  });
}

function emptyPara(spaceAfter = 0): Paragraph {
  return para([txt("")], { spaceAfter });
}

// 创建单元格（支持合并）
function cell(
  content: string | Paragraph[],
  opts?: {
    columnSpan?: number;
    verticalMerge?: "restart" | "continue";
    shading?: boolean;
    bold?: boolean;
    fontSize?: number;
    align?: typeof AlignmentType[keyof typeof AlignmentType];
    verticalAlign?: "top" | "center" | "bottom";
    width?: number;
    borders?: {
      top?: typeof BORDER_SINGLE | typeof BORDER_NONE;
      bottom?: typeof BORDER_SINGLE | typeof BORDER_NONE;
      left?: typeof BORDER_SINGLE | typeof BORDER_NONE;
      right?: typeof BORDER_SINGLE | typeof BORDER_NONE;
    };
  }
): TableCell {
  const paragraphs: Paragraph[] =
    typeof content === "string"
      ? [
          new Paragraph({
            children: [
              new TextRun({
                text: content,
                bold: opts?.bold,
                size: opts?.fontSize ?? 20,
                font: FONT_SONGTI,
              }),
            ],
            alignment: opts?.align ?? AlignmentType.CENTER,
            spacing: { before: 60, after: 60 },
          }),
        ]
      : content;

  return new TableCell({
    children: paragraphs,
    columnSpan: opts?.columnSpan,
    verticalMerge: opts?.verticalMerge === "restart"
      ? VerticalMergeType.RESTART
      : opts?.verticalMerge === "continue"
      ? VerticalMergeType.CONTINUE
      : undefined,
    shading: opts?.shading ? LABEL_SHADING : undefined,
    verticalAlign: opts?.verticalAlign as "top" | "center" | "bottom" | undefined,
    width: opts?.width ? { size: opts.width, type: WidthType.DXA } : undefined,
    borders: opts?.borders
      ? {
          top: opts.borders.top ?? BORDER_SINGLE,
          bottom: opts.borders.bottom ?? BORDER_SINGLE,
          left: opts.borders.left ?? BORDER_SINGLE,
          right: opts.borders.right ?? BORDER_SINGLE,
        }
      : {
          top: BORDER_SINGLE,
          bottom: BORDER_SINGLE,
          left: BORDER_SINGLE,
          right: BORDER_SINGLE,
        },
  });
}

// ===== 主导出函数 =====
export async function generateDocxBuffer(
  proposal: ProposalInfo,
  sections: SectionData[]
): Promise<Buffer> {
  console.log("[docxGenerator] Generating document with docx library (template format)");

  // 字段兼容处理
  const piName = proposal.principalInvestigatorName || proposal.principalInvestigator || "";
  const piEmail = proposal.principalInvestigatorEmail || proposal.piEmail || "";
  const piPhone = proposal.principalInvestigatorPhone || proposal.piPhone || "";

  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: FONT_SONGTI, size: 24 },
        },
      },
    },
    sections: [
      {
        properties: {
          page: {
            margin: { top: 1440, right: 1080, bottom: 1440, left: 1440 },
          },
        },
        children: [
          // ===== 第1页：封面 =====
          ...buildCoverPage(proposal, piName),
          // ===== 第2页：填报说明 =====
          ...buildFillingInstructions(),
          // ===== 第3页：项目基本信息表 =====
          ...buildBasicInfoTable(proposal, piName, piEmail, piPhone),
          // ===== 第4页：申报项目简介 =====
          ...buildProjectSummary(proposal),
          // ===== 正文各章节 =====
          ...buildBodySections(sections, proposal),
          // ===== 诚信承诺书 =====
          ...buildIntegrityPledge(proposal, piName),
        ],
      },
    ],
  });

  console.log("[docxGenerator] Document generated successfully");
  const buffer = await Packer.toBuffer(doc);
  return buffer as Buffer;
}

// ===== 封面页 =====
function buildCoverPage(proposal: ProposalInfo, piName: string): Paragraph[] {
  const underline = (label: string, value: string) =>
    para(
      [
        txt(label, { size: 24, font: FONT_SONGTI }),
        txt("  " + (value || ""), { size: 24, font: FONT_SONGTI, underline: true }),
      ],
      { spaceAfter: 120 }
    );

  return [
    // 申报编号
    para([txt("申报编号：", { bold: true, size: 24, font: FONT_HEITI })], { spaceAfter: 0 }),
    emptyPara(1200),
    // 大标题
    para([txt("国家重点研发计划", { size: 44, bold: true, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 200,
    }),
    para([txt("项目申报书", { size: 44, bold: true, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 1200,
    }),
    emptyPara(400),
    // 信息行
    underline("项目名称：", proposal.title || ""),
    underline("所属专项：", proposal.researchField || ""),
    underline("指南方向（榜单任务）：", ""),
    underline("创新分类：", ""),
    underline("项目管理专业机构：", ""),
    underline("推荐单位：", proposal.recommendingUnit || ""),
    para(
      [
        txt("申报单位：  ", { size: 24, font: FONT_SONGTI }),
        txt((proposal.applicantUnit || "") + "  ", { size: 24, font: FONT_SONGTI, underline: true }),
        txt("（公章）", { size: 24, font: FONT_SONGTI }),
      ],
      { spaceAfter: 120 }
    ),
    underline("项目负责人：", piName),
    emptyPara(1200),
    // 底部
    para([txt("中华人民共和国科学技术部制", { bold: true, size: 28, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 200,
    }),
    para([txt("年    月    日", { bold: true, size: 28, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 0,
    }),
  ];
}

// ===== 填报说明 =====
function buildFillingInstructions(): Paragraph[] {
  const items = [
    "1、申报书填写应以预申报书内容为基础，不得降低考核指标，不得自行调整主要研究内容，但可进一步具体细化。",
    "2. \u9879\u76ee\u7533\u62a5\u4e66\u5206\u4e3a\u300c\u56fd\u5185\u5916\u73b0\u72b6\u53ca\u8d8b\u52bf\u5206\u6790\u300d\u3001\u300c\u7814\u7a76\u76ee\u6807\u53ca\u5185\u5bb9\u300d\u3001\u300c\u7533\u62a5\u5355\u4f4d\u53ca\u53c2\u4e0e\u5355\u4f4d\u7814\u7a76\u57fa\u7840\u300d\u3001\u300c\u8fdb\u5ea6\u5b89\u6392\u300d\u3001\u300c\u9879\u76ee\u7ec4\u7ec7\u5b9e\u65bd\u3001\u4fdd\u969c\u63aa\u65bd\u53ca\u98ce\u9669\u5206\u6790\u300d\u3001\u300c\u7814\u7a76\u56e2\u961f\u300d\u3001\u300c\u7ecf\u8d39\u9884\u7b97\u300d\u548c\u300c\u6307\u5357\u6240\u8981\u6c42\u7684\u9644\u4ef6\u300d\u516b\u4e2a\u90e8\u5206\u3002\u7533\u62a5\u4e66\u7684\u5185\u5bb9\u5c06\u4f5c\u4e3a\u9879\u76ee\u8bc4\u5ba1\u3001\u4ee5\u53ca\u7b7e\u8ba2\u4efb\u52a1\u4e66\u7684\u91cd\u8981\u4f9d\u636e\uff0c\u7533\u62a5\u4e66\u7684\u5404\u9879\u586b\u62a5\u5185\u5bb9\u987b\u5b9e\u4e8b\u6c42\u662f\u3001\u51c6\u786e\u5b8c\u6574\u3001\u5c42\u6b21\u6e05\u6670\u3002",
    "3、请申报单位认真阅读指南，所申报的项目研究内容须对应指南、符合指南的要求。",
    "4、项目名称应清晰、准确反映研究内容，项目名称不宜宽泛。",
    "5\u3001\u7533\u62a5\u5355\u4f4d\u901a\u8fc7\u56fd\u5bb6\u79d1\u6280\u7ba1\u7406\u4fe1\u606f\u7cfb\u7edf\u6309\u7167\u7cfb\u7edf\u63d0\u793a\u5728\u7ebf\u586b\u5199\u7533\u62a5\u4e66\u3002\u7533\u62a5\u4e66\u6807\u9898\u7edf\u4e00\u7528\u9ed1\u4f53\u56db\u53f7\u5b57\uff0c\u7533\u62a5\u4e66\u6b63\u6587\u90e8\u5206\u7edf\u4e00\u7528\u5b8b\u4f53\u5c0f\u56db\u53f7\u5b57\u586b\u5199\u3002\u6b63\u6587\uff08\u5305\u62ec\u6807\u9898\uff09\u884c\u8ddd\u4e3a1.5\u500d\u3002\u51e1\u4e0d\u586b\u5199\u7684\u5185\u5bb9\uff0c\u8bf7\u7528\u300c\u65e0\u300d\u8868\u793a\u3002",
    "6、外来语要同时用原文和中文表达，第一次出现的缩略词，须注明全称。",
    "7、申报书中的单位名称，请填写全称，并与单位公章一致。",
  ];

  const result: Paragraph[] = [
    para([new PageBreak(), txt("")]),
    para([txt("填报说明", { bold: true, size: 32, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 400,
    }),
    para([txt("一、填写说明", { bold: true, size: 24, font: FONT_HEITI })], {
      indent: 480,
      spaceAfter: 200,
    }),
  ];

  for (const item of items) {
    result.push(
      para([txt(item, { size: 24 })], {
        firstLine: 480,
        spaceAfter: 160,
        line: 360,
      })
    );
  }

  result.push(
    para([txt("二、申报说明", { bold: true, size: 24, font: FONT_HEITI })], {
      indent: 480,
      spaceBefore: 200,
      spaceAfter: 200,
    }),
    para([txt("申报单位对申报材料的真实性、完整性负责。", { size: 24 })], {
      firstLine: 480,
      spaceAfter: 160,
      line: 360,
    }),
    para([txt("请申报单位审核、确认申报材料后，网上提交。", { size: 24 })], {
      firstLine: 480,
      spaceAfter: 160,
      line: 360,
    })
  );

  return result;
}

// ===== 项目基本信息表 =====
function buildBasicInfoTable(
  proposal: ProposalInfo,
  piName: string,
  piEmail: string,
  piPhone: string
): (Paragraph | Table)[] {
  const budget = proposal.totalBudget
    ? `总预算${proposal.totalBudget}万元，其中中央财政专项资金${proposal.centralFunding ?? "_"}万元，地方财政资金${proposal.localFunding ?? "_"}万元，单位自筹资金${proposal.unitFunding ?? "_"}万元，其他渠道获得资金_万元`
    : "总预算_万元，其中中央财政专项资金_万元，地方财政资金_万元，单位自筹资金_万元，其他渠道获得资金_万元";

  // 表格总宽度 9072 DXA (约16cm)，分为18列，每列504 DXA
  const COL = 504;
  const TOTAL = COL * 18;

  const tableBorders = {
    top: BORDER_SINGLE,
    bottom: BORDER_SINGLE,
    left: BORDER_SINGLE,
    right: BORDER_SINGLE,
    insideHorizontal: BORDER_SINGLE,
    insideVertical: BORDER_SINGLE,
  };

  const labelCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, shading: true, verticalMerge: vMerge, verticalAlign: "center" });

  const valueCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, verticalMerge: vMerge, align: AlignmentType.LEFT, verticalAlign: "center" });

  const rows: TableRow[] = [
    // 项目名称
    new TableRow({
      children: [
        labelCell("项目名称", 4),
        valueCell(proposal.title || "", 14),
      ],
    }),
    // 所属专项
    new TableRow({
      children: [
        labelCell("所属专项", 4),
        valueCell(proposal.researchField || "", 14),
      ],
    }),
    // 指南方向
    new TableRow({
      children: [
        labelCell("指南方向\n（榜单任务）", 4),
        valueCell("", 14),
      ],
    }),
    // 创新分类
    new TableRow({
      children: [
        labelCell("创新分类", 4),
        valueCell("□基础研究  □技术开发  □应用示范  □其他类型", 14),
      ],
    }),
    // 项目遴选方式
    new TableRow({
      children: [
        labelCell("项目遴选方式", 4),
        valueCell("□公开竞争  □定向委托  □定向择优", 14),
      ],
    }),
    // 项目实施模式
    new TableRow({
      children: [
        labelCell("项目实施模式", 4),
        valueCell("□青年科学家  □揭榜挂帅  □首席科学家\n□滚动支持  □应急攻关  □常规模式  □其他模式", 14),
      ],
    }),
    // 单位总数 / 课题数
    new TableRow({
      children: [
        labelCell("单位总数", 4),
        valueCell("", 5),
        labelCell("课题数", 4),
        valueCell("", 5),
      ],
    }),
    // 经费预算
    new TableRow({
      children: [
        labelCell("经费预算", 4),
        valueCell(budget, 14),
      ],
    }),
    // 项目周期节点 - 起始/结束
    new TableRow({
      children: [
        labelCell("项目周期节点", 4, "restart"),
        labelCell("起始时间", 3),
        valueCell("年    月", 4),
        labelCell("结束时间", 3),
        valueCell("年    月", 4),
      ],
    }),
    // 项目周期节点 - 实施周期
    new TableRow({
      children: [
        labelCell("", 4, "continue"),
        labelCell("实施周期", 3),
        valueCell("共    个月", 4),
        labelCell("预计中期时间点", 3),
        valueCell("年    月", 4),
      ],
    }),
    // 申报单位 - 单位名称
    new TableRow({
      children: [
        labelCell("申\n报\n单\n位", 2, "restart"),
        labelCell("单位名称", 3),
        valueCell(proposal.applicantUnit || "", 7),
        labelCell("单位性质", 2),
        valueCell("", 4),
      ],
    }),
    // 申报单位 - 单位所在地
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("单位所在地", 3),
        valueCell("", 7),
        labelCell("组织机构代码", 2),
        valueCell(proposal.applicantUnitCode || "", 4),
      ],
    }),
    // 申报单位 - 通信地址
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("通信地址", 3),
        valueCell(proposal.applicantUnitAddress || "", 7),
        labelCell("邮政编码", 2),
        valueCell("", 4),
      ],
    }),
    // 推荐单位
    new TableRow({
      children: [
        labelCell("推\n荐\n单\n位", 2),
        labelCell("单位名称", 3),
        valueCell(proposal.recommendingUnit || "", 5),
        labelCell("推荐单位\n性质", 2),
        valueCell(
          proposal.recommendingUnitNature
            ? proposal.recommendingUnitNature
            : "□部门  □地方  □行业协会\n□产业技术创新战略联盟  □其他",
          6
        ),
      ],
    }),
    // 项目负责人 - 姓名/性别/出生日期
    new TableRow({
      children: [
        labelCell("项\n目\n负\n责\n人", 2, "restart"),
        labelCell("姓 名", 2),
        valueCell(piName, 3),
        labelCell("性 别", 2),
        valueCell("□男□女", 4),
        labelCell("出生日期", 2),
        valueCell("", 3),
      ],
    }),
    // 项目负责人 - 证件类型/号码
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("证件类型", 2),
        valueCell("", 3),
        labelCell("证件号码", 2),
        valueCell("", 9),
      ],
    }),
    // 项目负责人 - 所在单位
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("所在单位", 2),
        valueCell("", 14),
      ],
    }),
    // 项目负责人 - 最高学位
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("最高学位", 2),
        valueCell("□博士  □硕士  □学士  □其他", 14),
      ],
    }),
    // 项目负责人 - 职称/职务
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("职 称", 2),
        valueCell("□正高级  □副高级  □中级  □初级  □其他", 11),
        labelCell("职务", 2),
        valueCell("", 1),
      ],
    }),
    // 项目负责人 - 电子邮箱/移动电话
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("电子邮箱", 2),
        valueCell(piEmail, 7),
        labelCell("移动电话", 2),
        valueCell(piPhone, 5),
      ],
    }),
    // 项目联系人 - 姓名/电子邮箱
    new TableRow({
      children: [
        labelCell("项\n目\n联\n系\n人", 2, "restart"),
        labelCell("姓 名", 2),
        valueCell(proposal.contactPersonName || "", 4),
        labelCell("电子邮箱", 2),
        valueCell(proposal.contactPersonEmail || "", 8),
      ],
    }),
    // 项目联系人 - 固定电话/移动电话
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("固定电话", 2),
        valueCell("", 4),
        labelCell("移动电话", 2),
        valueCell(proposal.contactPersonPhone || "", 8),
      ],
    }),
    // 项目联系人 - 证件类型/号码
    new TableRow({
      children: [
        labelCell("", 2, "continue"),
        labelCell("证件类型", 2),
        valueCell("", 4),
        labelCell("证件号码", 2),
        valueCell("", 8),
      ],
    }),
    // 课题分解标题行
    new TableRow({
      children: [
        labelCell("课\n题\n分\n解", 2, "restart"),
        labelCell("序号", 1),
        labelCell("课题名称", 4),
        labelCell("承担单位", 4),
        labelCell("负责人", 2),
        labelCell("总经费\n（万元）", 2),
        labelCell("其中中央\n财政专项资金\n（万元）", 3),
      ],
    }),
    // 课题分解 - 空行1
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        labelCell("", 2, "continue"),
        valueCell("", 1),
        valueCell("", 4),
        valueCell("", 4),
        valueCell("", 2),
        valueCell("", 2),
        valueCell("", 3),
      ],
    }),
    // 课题分解 - 空行2
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        labelCell("", 2, "continue"),
        valueCell("", 1),
        valueCell("", 4),
        valueCell("", 4),
        valueCell("", 2),
        valueCell("", 2),
        valueCell("", 3),
      ],
    }),
    // 课题分解 - 空行3
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        labelCell("", 2, "continue"),
        valueCell("", 1),
        valueCell("", 4),
        valueCell("", 4),
        valueCell("", 2),
        valueCell("", 2),
        valueCell("", 3),
      ],
    }),
    // 其他参与单位标题行
    new TableRow({
      children: [
        labelCell("其\n他\n参\n与\n单\n位", 2, "restart"),
        labelCell("序号", 1),
        labelCell("单位名称", 7),
        labelCell("单位性质", 4),
        labelCell("组织机构代码", 4),
      ],
    }),
    // 其他参与单位 - 空行1
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        labelCell("", 2, "continue"),
        valueCell("", 1),
        valueCell("", 7),
        valueCell("", 4),
        valueCell("", 4),
      ],
    }),
    // 其他参与单位 - 空行2
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        labelCell("", 2, "continue"),
        valueCell("", 1),
        valueCell("", 7),
        valueCell("", 4),
        valueCell("", 4),
      ],
    }),
    // 其他参与单位 - 空行3
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        labelCell("", 2, "continue"),
        valueCell("", 1),
        valueCell("", 7),
        valueCell("", 4),
        valueCell("", 4),
      ],
    }),
    // 项目参加人数 行1
    new TableRow({
      children: [
        labelCell("项目参加人数", 4),
        valueCell("_人。其中：", 3),
        valueCell("高级职称_人，中级职称_人，初级职称_人，其他_人；", 11),
      ],
    }),
    // 项目参加人数 行2
    new TableRow({
      children: [
        labelCell("", 4),
        valueCell("", 3),
        valueCell("博士学位_人，硕士学位_人，学士学位_人，其他_人。", 11),
      ],
    }),
  ];

  return [
    para([new PageBreak(), txt("")]),
    para([txt("项目基本信息表", { bold: true, size: 32, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 200,
    }),
    new Table({
      width: { size: TOTAL, type: WidthType.DXA },
      columnWidths: Array(18).fill(COL),
      borders: tableBorders,
      rows,
    }),
    emptyPara(200),
    para(
      [
        txt("填表说明：", { bold: true, size: 20, font: FONT_HEITI }),
        txt("1.组织机构代码指企事业单位国家标准代码，单位若已三证合一请填写单位统一社会信用代码，无组织机构代码的单位填写\"000000000\"；", { size: 20 }),
      ],
      { spaceAfter: 80, line: 320 }
    ),
    para(
      [txt("2.单位公章名称必须与单位名称一致；", { size: 20 })],
      { indent: 480, spaceAfter: 80, line: 320 }
    ),
  ];
}

// ===== 申报项目简介 =====
function buildProjectSummary(proposal: ProposalInfo): (Paragraph | Table)[] {
  return [
    para([new PageBreak(), txt("")]),
    para([txt("申报项目简介", { bold: true, size: 32, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 400,
    }),
    para(
      [
        txt(
          proposal.abstract ||
            "从研究背景、研究目标、研究内容（包括拟解决的重大科学问题或关键技术问题）、技术路线、研究基础和团队、预期成果和效益等方面简要描述。限1500字以内。",
          { size: 24 }
        ),
      ],
      { firstLine: 480, spaceAfter: 200, line: 360 }
    ),
  ];
}

// ===== 项目目标考核指标表（Table 2，11行×10列）=====
function buildObjectivesTable(): (Paragraph | Table)[] {
  // 10列，总宽9072 DXA
  const COL = 907;
  const TOTAL = COL * 10;
  const tableBorders = {
    top: BORDER_SINGLE,
    bottom: BORDER_SINGLE,
    left: BORDER_SINGLE,
    right: BORDER_SINGLE,
    insideHorizontal: BORDER_SINGLE,
    insideVertical: BORDER_SINGLE,
  };

  const hCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, shading: true, verticalMerge: vMerge, verticalAlign: "center", bold: false });

  const vCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, verticalMerge: vMerge, align: AlignmentType.LEFT, verticalAlign: "center" });

  const rows: TableRow[] = [
    // 表头行1
    new TableRow({
      children: [
        hCell("项目目标", 1, "restart"),
        hCell("预期成果名称", 1, "restart"),
        hCell("预期成果\n类型", 1, "restart"),
        hCell("对应的\n课题", 1, "restart"),
        hCell("考核指标", 5),
        hCell("考核方式（方法）及评价手段", 1, "restart"),
      ],
    }),
    // 表头行2
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("", 1, "continue"),
        hCell("", 1, "continue"),
        hCell("", 1, "continue"),
        hCell("指标\n名称", 1),
        hCell("立项时已有\n指标值/状态", 1),
        hCell("中期指标\n值/状态", 1),
        hCell("完成时指标\n值/状态", 2),
        hCell("", 1, "continue"),
      ],
    }),
    // 数据行1：成果1 - 指标1.1
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "restart"),
        vCell("1：", 1, "restart"),
        vCell("□新理论  □新原理\n□新产品  □新材料\n□新工艺  □新方法\n□其他", 1, "restart"),
        vCell("", 1, "restart"),
        vCell("指标1.1", 1),
        vCell("", 1),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
      ],
    }),
    // 数据行2：成果1 - 指标...
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("……", 1),
        vCell("", 1),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
      ],
    }),
    // 数据行3：成果2 - 指标2.1
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "continue"),
        vCell("2：", 1, "restart"),
        vCell("同上", 1, "restart"),
        vCell("", 1, "restart"),
        vCell("指标2.1", 1),
        vCell("", 1),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
      ],
    }),
    // 数据行4：成果2 - 指标...
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("……", 1),
        vCell("", 1),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
      ],
    }),
    // 数据行5：成果... - 指标
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "continue"),
        vCell("…", 1, "restart"),
        vCell("同上", 1, "restart"),
        vCell("", 1, "restart"),
        vCell("指标", 1),
        vCell("", 1),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
      ],
    }),
    // 数据行6：成果... - 指标...
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("", 1, "continue"),
        vCell("……", 1),
        vCell("", 1),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
      ],
    }),
    // 科技报告考核指标 - 表头
    new TableRow({
      children: [
        hCell("科技报告\n考核指标", 1, "restart"),
        hCell("序号", 1),
        hCell("报告类型", 2),
        hCell("数量", 1),
        hCell("提交时间", 3),
        hCell("公开类别及时限", 2),
      ],
    }),
    // 科技报告考核指标 - 数据行
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        vCell("", 1, "continue"),
        vCell("", 1),
        vCell("", 2),
        vCell("", 1),
        vCell("", 3),
        vCell("", 2),
      ],
    }),
    // 其他目标与考核指标完成情况
    new TableRow({
      height: { value: 800, rule: "atLeast" as const },
      children: [
        hCell("其他目标与考核指标完成情况", 10),
      ],
    }),
  ];

  return [
    new Table({
      width: { size: TOTAL, type: WidthType.DXA },
      columnWidths: Array(10).fill(COL),
      borders: tableBorders,
      rows,
    }),
    emptyPara(200),
  ];
}

// ===== 企业概况表（Table 3，12行×13列）=====
function buildEnterpriseTable(): (Paragraph | Table)[] {
  // 13列，总宽9072 DXA
  const COL = 698;
  const TOTAL = COL * 13;
  const tableBorders = {
    top: BORDER_SINGLE,
    bottom: BORDER_SINGLE,
    left: BORDER_SINGLE,
    right: BORDER_SINGLE,
    insideHorizontal: BORDER_SINGLE,
    insideVertical: BORDER_SINGLE,
  };

  const hCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, shading: true, verticalMerge: vMerge, verticalAlign: "center" });

  const vCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, verticalMerge: vMerge, align: AlignmentType.LEFT, verticalAlign: "center" });

  const rows: TableRow[] = [
    // Row0: 项目牵头企业概况 - 企业名称
    new TableRow({
      children: [
        hCell("项\n目\n牵\n头\n企\n业\n概\n况", 1, "restart"),
        hCell("企业名称", 1),
        vCell("", 11),
      ],
    }),
    // Row1: 行业/领域
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("行业/领域", 1),
        vCell("", 11),
      ],
    }),
    // Row2: 经济性质 / 企业特性
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("经济性质", 1),
        vCell("□国有企业  □集体企业   □私营企业  □有限责任公司", 5),
        hCell("企业特性", 1),
        vCell("□经认定的高新技术企业 □国家创新型企业 □其他：", 5),
      ],
    }),
    // Row3: 上市情况 / 上级主管单位
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("上市情况", 1),
        vCell("□深交所 □上交所 □新加坡  □香港 □创业板  □新三板", 5),
        hCell("上级主管单位", 1),
        vCell("□大专院校  □中科院科研院所 □其他部委科研院所  □地方", 5),
      ],
    }),
    // Row4: 公司注册地址 / 注册资本
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("公司注册地址", 1),
        vCell("", 5),
        hCell("注册资本\n（万元）", 1),
        vCell("", 5),
      ],
    }),
    // Row5: 成立时间 / 人员规模
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("成立时间\n（年、月）", 4),
        vCell("", 1),
        hCell("人员规模", 3),
        vCell("", 4),
      ],
    }),
    // Row6: 主营方向
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("主营方向", 1),
        vCell("", 11),
      ],
    }),
    // Row7: 经营概况（标题行）
    new TableRow({
      height: { value: 400, rule: "atLeast" as const },
      children: [
        hCell("经\n营\n概\n况", 1, "restart"),
        vCell("", 12),
      ],
    }),
    // Row8: 研发概况 - 研发人员数量 / 上年度研究开发经费投入
    new TableRow({
      children: [
        hCell("研\n发\n概\n况", 1, "restart"),
        hCell("研发人员\n数量", 2),
        vCell("", 2),
        hCell("上年度研究开发经费投入（万元）", 5),
        vCell("", 3),
      ],
    }),
    // Row9: 上年度研究开发经费投入与主营业务收入的比
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("上年度研究开发经费投入与主营业务收入的比（投入强度，%）", 11),
        vCell("", 1),
      ],
    }),
    // Row10: 专利情况（空行）
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: [
        hCell("", 1, "continue"),
        vCell("", 12),
      ],
    }),
    // Row11: 制定标准
    new TableRow({
      children: [
        hCell("", 1, "continue"),
        hCell("制定国内标准（项）", 4),
        vCell("", 1),
        hCell("制定国际标准（项）", 4),
        vCell("", 1),
        vCell("", 2),
      ],
    }),
  ];

  return [
    new Table({
      width: { size: TOTAL, type: WidthType.DXA },
      columnWidths: Array(13).fill(COL),
      borders: tableBorders,
      rows,
    }),
    emptyPara(200),
  ];
}

// ===== 研究团队人员表（Table 4，6行×15列）=====
function buildTeamTable(): (Paragraph | Table)[] {
  // 15列，总宽9072 DXA
  const COL = 605;
  const TOTAL = COL * 15;
  const tableBorders = {
    top: BORDER_SINGLE,
    bottom: BORDER_SINGLE,
    left: BORDER_SINGLE,
    right: BORDER_SINGLE,
    insideHorizontal: BORDER_SINGLE,
    insideVertical: BORDER_SINGLE,
  };

  const hCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, shading: true, verticalMerge: vMerge, verticalAlign: "center" });

  const vCell = (text: string, span = 1, vMerge?: "restart" | "continue") =>
    cell(text, { columnSpan: span, verticalMerge: vMerge, align: AlignmentType.LEFT, verticalAlign: "center" });

  const rows: TableRow[] = [
    // 填表说明行
    new TableRow({
      children: [
        cell(
          [new Paragraph({
            children: [new TextRun({
              text: "填表说明： 1、专业技术职称：A、正高级  B、副高级  C、中级  D、初级  E、其他；2、人员分类代码：A、项目负责人  B、课题负责人  C、骨干成员  D、一般成员；3、是否有工资性收入：Y、是  N、否",
              size: 18,
              font: FONT_SONGTI,
            })],
            spacing: { before: 40, after: 40 },
          })],
          { columnSpan: 15, shading: true }
        ),
      ],
    }),
    // 表头行
    new TableRow({
      children: [
        hCell("序\n号", 1),
        hCell("姓名", 1),
        hCell("性别", 1),
        hCell("出生日期", 1),
        hCell("证件类型", 1),
        hCell("证件号码", 1),
        hCell("专业技术\n职称", 1),
        hCell("职务", 1),
        hCell("最高\n学位", 1),
        hCell("专业", 1),
        hCell("投入本项目的\n全时工作时间\n（人月）", 1),
        hCell("人员分\n类代码", 1),
        hCell("所属\n课题", 1),
        hCell("是否有\n工资性\n收入", 1),
        hCell("工作单位", 1),
      ],
    }),
    // 数据行（3行空白）
    new TableRow({
      height: { value: 600, rule: "atLeast" as const },
      children: Array(15).fill(null).map(() => vCell("")),
    }),
    // 固定研究人员合计
    new TableRow({
      children: [
        hCell("固定研究人员合计", 10),
        vCell("", 1),
        hCell("／", 1),
        hCell("／", 1),
        hCell("／", 1),
        hCell("／", 1),
      ],
    }),
    // 流动人员或临时聘用人员合计
    new TableRow({
      children: [
        hCell("流动人员或临时聘用人员合计", 10),
        vCell("", 1),
        hCell("／", 1),
        hCell("／", 1),
        hCell("／", 1),
        hCell("／", 1),
      ],
    }),
    // 累计
    new TableRow({
      children: [
        hCell("累计", 10),
        vCell("", 1),
        hCell("／", 1),
        hCell("／", 1),
        hCell("／", 1),
        hCell("／", 1),
      ],
    }),
  ];

  return [
    new Table({
      width: { size: TOTAL, type: WidthType.DXA },
      columnWidths: Array(15).fill(COL),
      borders: tableBorders,
      rows,
    }),
    emptyPara(200),
  ];
}

// ===== 经费预算表（Table 11，16行×5列）=====
function buildBudgetTable(proposal: ProposalInfo): (Paragraph | Table)[] {
  // 5列，总宽9072 DXA
  const TOTAL = 9072;
  const colWidths = [500, 3000, 1857, 1857, 1858];
  const tableBorders = {
    top: BORDER_SINGLE,
    bottom: BORDER_SINGLE,
    left: BORDER_SINGLE,
    right: BORDER_SINGLE,
    insideHorizontal: BORDER_SINGLE,
    insideVertical: BORDER_SINGLE,
  };

  const hCell = (text: string, span = 1) =>
    cell(text, { columnSpan: span, shading: true, verticalAlign: "center" });

  const vCell = (text: string, span = 1, align?: typeof AlignmentType[keyof typeof AlignmentType]) =>
    cell(text, { columnSpan: span, align: align ?? AlignmentType.LEFT, verticalAlign: "center" });

  const slashCell = () => cell("／", { align: AlignmentType.CENTER });

  const rows: TableRow[] = [
    // 表头
    new TableRow({
      children: [
        hCell("序号"),
        hCell("预算科目名称"),
        hCell("合计"),
        hCell("中央财政专项资金"),
        hCell("其他来源资金"),
      ],
    }),
    // 序号标注行
    new TableRow({
      children: [
        hCell("序号"),
        hCell("（1）"),
        hCell("（2）"),
        hCell("（3）"),
        hCell("（4）"),
      ],
    }),
    // 1. 一、资金支出
    new TableRow({ children: [vCell("1"), vCell("一、资金支出"), vCell(""), vCell(""), vCell("")] }),
    // 2. （一）直接费用
    new TableRow({ children: [vCell("2"), vCell("（一）直接费用"), vCell(""), vCell(""), vCell("")] }),
    // 3. 1.设备费
    new TableRow({ children: [vCell("3"), vCell("1.设备费"), vCell(""), vCell(""), vCell("")] }),
    // 4. （1）购置设备费
    new TableRow({ children: [vCell("4"), vCell("（1）购置设备费"), vCell(""), vCell(""), vCell("")] }),
    // 5. （2）设备试制/改造/租赁费
    new TableRow({ children: [vCell("5"), vCell("（2）设备试制/改造/租赁费"), vCell(""), vCell(""), vCell("")] }),
    // 6. 2.材料费、测试化验加工费...
    new TableRow({ children: [vCell("6"), vCell("2.材料费、测试化验加工费、燃料动力费、出版/文献/信息传播/知识产权事务费"), vCell(""), vCell(""), vCell("")] }),
    // 7. 3.会议/差旅/国际合作交流费...
    new TableRow({ children: [vCell("7"), vCell("3.会议/差旅/国际合作交流费、劳务/专家咨询费、其他直接费用"), vCell(""), vCell(""), vCell("")] }),
    // 8. （二）间接费用
    new TableRow({ children: [vCell("8"), vCell("（二）间接费用（自动计算）"), vCell(""), vCell(""), vCell("")] }),
    // 9. 二、资金来源
    new TableRow({ children: [vCell("9"), vCell("二、资金来源"), vCell(""), vCell(""), vCell("")] }),
    // 10. （一）中央财政专项资金
    new TableRow({ children: [vCell("10"), vCell("（一）中央财政专项资金"), vCell(""), vCell(proposal.centralFunding ? String(proposal.centralFunding) : ""), slashCell()] }),
    // 11. （二）其他来源资金
    new TableRow({ children: [vCell("11"), vCell("（二）其他来源资金"), vCell(""), slashCell(), vCell("")] }),
    // 12. 1.地方财政资金
    new TableRow({ children: [vCell("12"), vCell("1.地方财政资金"), vCell(""), slashCell(), vCell(proposal.localFunding ? String(proposal.localFunding) : "")] }),
    // 13. 2.单位自筹资金
    new TableRow({ children: [vCell("13"), vCell("2.单位自筹资金"), vCell(""), slashCell(), vCell(proposal.unitFunding ? String(proposal.unitFunding) : "")] }),
    // 14. 3.其他渠道获得资金
    new TableRow({ children: [vCell("14"), vCell("3.其他渠道获得资金"), vCell(""), slashCell(), vCell("")] }),
  ];

  return [
    new Table({
      width: { size: TOTAL, type: WidthType.DXA },
      columnWidths: colWidths,
      borders: tableBorders,
      rows,
    }),
    emptyPara(200),
    para(
      [
        txt("预算说明：", { bold: true, size: 20, font: FONT_HEITI }),
        txt("根据《国家重点研发计划重点专项项目预算编报指南》，对各预算科目的经费安排进行说明。", { size: 20 }),
      ],
      { spaceAfter: 80, line: 320 }
    ),
  ];
}

// ===== 正文各章节 =====
function buildBodySections(sections: SectionData[], proposal?: ProposalInfo): (Paragraph | Table)[] {
  // 章节key到模板部分的映射（部分编号 + 子标题）
  const sectionPartMap: Record<string, { part: number; partTitle: string; subTitle?: string }> = {
    project_objectives: { part: 2, partTitle: "第二部分  研究目标及内容" },
    subtask_research_content: { part: 2, partTitle: "第二部分  研究目标及内容", subTitle: "各课题研究内容" },
    innovation_points: { part: 2, partTitle: "第二部分  研究目标及内容", subTitle: "创新点" },
    expected_benefits: { part: 2, partTitle: "第二部分  研究目标及内容", subTitle: "预期效益" },
    prior_achievements: { part: 3, partTitle: "第三部分  申报单位及参与单位研究基础" },
    pi_qualifications: { part: 3, partTitle: "第三部分  申报单位及参与单位研究基础", subTitle: "项目负责人资质" },
    research_conditions: { part: 3, partTitle: "第三部分  申报单位及参与单位研究基础", subTitle: "科研条件支撑" },
    enterprise_status: { part: 3, partTitle: "第三部分  申报单位及参与单位研究基础", subTitle: "企业运行状况" },
    risk_analysis: { part: 5, partTitle: "第五部分  项目组织实施、保障措施及风险分析" },
    schedule_plan: { part: 4, partTitle: "第四部分  进度安排" },
    quality_assurance: { part: 5, partTitle: "第五部分  项目组织实施、保障措施及风险分析", subTitle: "质量保证" },
    open_sharing: { part: 8, partTitle: "第八部分  指南所要求的附件", subTitle: "开放共享承诺" },
    supporting_documents: { part: 8, partTitle: "第八部分  指南所要求的附件" },
    additional_notes: { part: 0, partTitle: "其他说明" },
  };

  // 模板中的8个部分（按顺序）
  const templateParts = [
    { part: 1, title: "第一部分  国内外现状及趋势分析" },
    { part: 2, title: "第二部分  研究目标及内容" },
    { part: 3, title: "第三部分  申报单位及参与单位研究基础" },
    { part: 4, title: "第四部分  进度安排" },
    { part: 5, title: "第五部分  项目组织实施、保障措施及风险分析" },
    { part: 6, title: "第六部分  研究团队" },
    { part: 7, title: "第七部分  经费预算" },
    { part: 8, title: "第八部分  指南所要求的附件" },
  ];

  const confirmedSections = sections.filter((s) => s.status === "confirmed" && s.content);

  if (confirmedSections.length === 0) {
    // 没有已确认章节，输出所有部分的空白框架
    const result: (Paragraph | Table)[] = [];
    for (const part of templateParts) {
      result.push(
        para([new PageBreak(), txt("")]),
        para([txt(part.title, { bold: true, size: 32, font: FONT_HEITI })], {
          align: AlignmentType.CENTER,
          spaceAfter: 400,
        }),
        para([txt("（待填写）", { size: 24, color: "999999" })], {
          firstLine: 480,
          spaceAfter: 200,
          line: 360,
        })
      );
      // 第二部分后插入项目目标考核指标表
      if (part.part === 2) {
        result.push(...buildObjectivesTable());
      }
      // 第三部分后插入企业概况表
      if (part.part === 3) {
        result.push(...buildEnterpriseTable());
      }
      // 第六部分后插入研究团队人员表
      if (part.part === 6) {
        result.push(...buildTeamTable());
      }
      // 第七部分后插入经费预算表
      if (part.part === 7) {
        result.push(...buildBudgetTable(proposal || {} as ProposalInfo));
      }
    }
    return result;
  }

  const result: (Paragraph | Table)[] = [];
  const renderedParts = new Set<number>();

  // 按模板部分顺序输出
  for (const part of templateParts) {
    // 找出属于这个部分的已确认章节
    const partSections = confirmedSections.filter((s) => {
      const mapping = sectionPartMap[s.sectionKey];
      return mapping && mapping.part === part.part;
    });

    // 如果没有这个部分的章节，输出空白框架
    if (partSections.length === 0) {
      result.push(
        para([new PageBreak(), txt("")]),
        para([txt(part.title, { bold: true, size: 32, font: FONT_HEITI })], {
          align: AlignmentType.CENTER,
          spaceAfter: 400,
        }),
        para([txt("（待填写）", { size: 24, color: "999999" })], {
          firstLine: 480,
          spaceAfter: 200,
          line: 360,
        })
      );
    } else {
      // 输出部分标题（只输出一次）
      result.push(
        para([new PageBreak(), txt("")]),
        para([txt(part.title, { bold: true, size: 32, font: FONT_HEITI })], {
          align: AlignmentType.CENTER,
          spaceAfter: 400,
        })
      );
      renderedParts.add(part.part);

      // 输出该部分的所有章节
      for (const section of partSections) {
        const mapping = sectionPartMap[section.sectionKey];
        if (mapping?.subTitle) {
          result.push(
            para([txt(mapping.subTitle, { bold: true, size: 28, font: FONT_HEITI })], {
              spaceBefore: 200,
              spaceAfter: 200,
            })
          );
        }
        // 输出章节内容
        result.push(...renderSectionContent(section));
      }
    }

    // 在特定部分后插入对应的表格
    if (part.part === 2) {
      result.push(...buildObjectivesTable());
    }
    if (part.part === 3) {
      result.push(...buildEnterpriseTable());
    }
    if (part.part === 6) {
      result.push(...buildTeamTable());
    }
    if (part.part === 7) {
      result.push(...buildBudgetTable(proposal || {} as ProposalInfo));
    }
  }

  // 输出未映射到任何部分的章节（如additional_notes）
  const unmappedSections = confirmedSections.filter((s) => {
    const mapping = sectionPartMap[s.sectionKey];
    return !mapping || mapping.part === 0;
  });

  for (const section of unmappedSections) {
    result.push(
      para([new PageBreak(), txt("")]),
      para([txt(section.title, { bold: true, size: 32, font: FONT_HEITI })], {
        align: AlignmentType.CENTER,
        spaceAfter: 400,
      }),
      ...renderSectionContent(section)
    );
  }

  return result;
}

// 渲染章节内容（解析Markdown格式）
function renderSectionContent(section: SectionData): Paragraph[] {
  const result: Paragraph[] = [];
  const contentLines = (section.content || "").split("\n");

  for (const line of contentLines) {
    const trimmed = line.trim();
    if (!trimmed) {
      result.push(emptyPara(80));
      continue;
    }

    // 判断是否为子标题
    const isSubHeading =
      trimmed.match(/^[一二三四五六七八九十\d]+[、.．。）)]\s*\*?\*?/) ||
      trimmed.match(/^#+\s+/) ||
      (trimmed.startsWith("**") && trimmed.endsWith("**") && trimmed.length < 60);

    const cleanText = trimmed
      .replace(/^#+\s*/, "")
      .replace(/\*\*/g, "")
      .replace(/\*/g, "")
      .replace(/^-\s+/, "");

    if (isSubHeading) {
      result.push(
        para([txt(cleanText, { bold: true, size: 24, font: FONT_HEITI })], {
          spaceBefore: 240,
          spaceAfter: 120,
          line: 360,
        })
      );
    } else if (trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
      result.push(
        para([txt("• " + cleanText, { size: 24 })], {
          indent: 480,
          spaceAfter: 120,
          line: 360,
        })
      );
    } else {
      result.push(
        para([txt(cleanText, { size: 24 })], {
          firstLine: 480,
          spaceAfter: 160,
          line: 360,
        })
      );
    }
  }

  return result;
}

// ===== 诚信承诺书 =====
function buildIntegrityPledge(proposal: ProposalInfo, piName: string): Paragraph[] {
  return [
    para([new PageBreak(), txt("")]),
    para([txt("诚信承诺书", { bold: true, size: 32, font: FONT_HEITI })], {
      align: AlignmentType.CENTER,
      spaceAfter: 600,
    }),
    para(
      [txt("本人（项目负责人）及申报单位郑重承诺：", { size: 24 })],
      { firstLine: 480, spaceAfter: 200, line: 360 }
    ),
    para(
      [txt("一、本申报书中所填写的全部内容均真实、准确，不存在任何弄虚作假行为。", { size: 24 })],
      { firstLine: 480, spaceAfter: 200, line: 360 }
    ),
    para(
      [txt("二、本项目不存在重复申报、重复立项情况，未在其他渠道申请相同研究内容的资助。", { size: 24 })],
      { firstLine: 480, spaceAfter: 200, line: 360 }
    ),
    para(
      [txt("三、项目研究内容不涉及国家秘密，或已按规定进行保密审查。", { size: 24 })],
      { firstLine: 480, spaceAfter: 200, line: 360 }
    ),
    para(
      [txt("四、本人及申报单位遵守科研诚信相关规定，接受有关部门的监督检查。", { size: 24 })],
      { firstLine: 480, spaceAfter: 200, line: 360 }
    ),
    para(
      [txt("五、如有违反上述承诺，愿意承担相应的法律责任和后果。", { size: 24 })],
      { firstLine: 480, spaceAfter: 600, line: 360 }
    ),
    para(
      [txt("项目负责人（签字）：", { size: 24 })],
      { indent: 480, spaceAfter: 200 }
    ),
    para(
      [txt("申报单位（公章）：", { size: 24 })],
      { indent: 480, spaceAfter: 200 }
    ),
    para(
      [txt("日期：      年      月      日", { size: 24 })],
      { indent: 480, spaceAfter: 0 }
    ),
  ];
}
