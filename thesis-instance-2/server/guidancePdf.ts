import PDFDocument from "pdfkit";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";

// ES module 兼容的 __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 中文字体路径 - 使用从 TTC 提取的 TTF 格式字体（pdfkit 不支持 TTC 集合字体）
const FONT_CANDIDATES = [
  path.join(__dirname, "fonts", "wqy-zenhei.ttf"),  // 项目内嵌字体（从 wqy-zenhei.ttc 提取）
  "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
];

function findChineseFont(): string | null {
  for (const fontPath of FONT_CANDIDATES) {
    if (fs.existsSync(fontPath)) return fontPath;
  }
  return null;
}

interface GuidanceLogForPdf {
  id: number;
  guidanceDate: Date | string;
  topic: string;
  content: string;
  status: string;
  createdAt: Date | string;
  updatedAt?: Date | string | null;
  attachments?: Array<{
    id: number;
    fileName: string;
    fileSize?: number | null;
    createdAt: Date | string;
  }>;
  comments?: Array<{
    id: number;
    userName: string;
    userRole: string;
    content: string;
    createdAt: Date | string;
  }>;
}

interface PdfOptions {
  studentName: string;
  studentId?: string;
  teacherName?: string;
  logs: GuidanceLogForPdf[];
  title?: string;
}

function formatDate(date: Date | string): string {
  const d = new Date(date);
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

function formatDateTime(date: Date | string): string {
  const d = new Date(date);
  return d.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusText(status: string): string {
  switch (status) {
    case "draft": return "草稿";
    case "submitted": return "待确认";
    case "confirmed": return "已确认";
    default: return status;
  }
}

function formatFileSize(bytes: number | null | undefined): string {
  if (!bytes) return "未知大小";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export async function generateGuidancePdf(options: PdfOptions): Promise<Buffer> {
  const { studentName, studentId, teacherName, logs, title } = options;
  
  const chineseFontPath = findChineseFont();
  
  const doc = new PDFDocument({
    size: "A4",
    margins: { top: 60, bottom: 60, left: 50, right: 50 },
    bufferPages: true,
    info: {
      Title: title || `${studentName} - 指导记录`,
      Author: teacherName || "毕业设计管理系统",
      Subject: "学生指导记录导出",
    },
  });

  const chunks: Buffer[] = [];
  doc.on("data", (chunk: Buffer) => chunks.push(chunk));

  const pageWidth = doc.page.width - doc.page.margins.left - doc.page.margins.right;

  // Register Chinese font (TTF only, TTC not supported by pdfkit)
  if (chineseFontPath) {
    doc.registerFont("Chinese", chineseFontPath);
  }

  // Use same font for both normal and bold (DroidSansFallback has no separate bold variant)
  const fontName = chineseFontPath ? "Chinese" : "Helvetica";
  const fontBold = chineseFontPath ? "Chinese" : "Helvetica-Bold";

  // Helper: check page break
  function checkPageBreak(requiredHeight: number) {
    const bottomLimit = doc.page.height - doc.page.margins.bottom;
    if (doc.y + requiredHeight > bottomLimit) {
      doc.addPage();
    }
  }

  // Helper: draw horizontal line
  function drawLine(y?: number) {
    const lineY = y || doc.y;
    doc.strokeColor("#d1d5db")
      .lineWidth(0.5)
      .moveTo(doc.page.margins.left, lineY)
      .lineTo(doc.page.width - doc.page.margins.right, lineY)
      .stroke();
    doc.y = lineY + 8;
  }

  // ==================== Title Page ====================
  doc.font(fontBold).fontSize(22).fillColor("#1e3a5f");
  doc.text(title || "学生指导记录", { align: "center" });
  doc.moveDown(0.5);

  // Subtitle line
  doc.strokeColor("#2563eb").lineWidth(2)
    .moveTo(doc.page.margins.left + pageWidth * 0.3, doc.y)
    .lineTo(doc.page.margins.left + pageWidth * 0.7, doc.y)
    .stroke();
  doc.moveDown(1);

  // Student info
  doc.font(fontName).fontSize(12).fillColor("#374151");
  
  const infoItems: string[] = [];
  infoItems.push(`学生姓名：${studentName}`);
  if (studentId) infoItems.push(`学号：${studentId}`);
  if (teacherName) infoItems.push(`指导教师：${teacherName}`);
  infoItems.push(`记录总数：${logs.length} 条`);
  
  const confirmedCount = logs.filter(l => l.status === "confirmed").length;
  const submittedCount = logs.filter(l => l.status === "submitted").length;
  const draftCount = logs.filter(l => l.status === "draft").length;
  
  infoItems.push(`已确认：${confirmedCount} 条 | 待确认：${submittedCount} 条 | 草稿：${draftCount} 条`);
  infoItems.push(`导出时间：${formatDateTime(new Date())}`);

  for (const item of infoItems) {
    doc.text(item, { align: "center" });
    doc.moveDown(0.3);
  }
  
  doc.moveDown(1);
  drawLine();
  doc.moveDown(0.5);

  // ==================== Records ====================
  // Sort logs by date descending
  const sortedLogs = [...logs].sort((a, b) => 
    new Date(b.guidanceDate).getTime() - new Date(a.guidanceDate).getTime()
  );

  for (let i = 0; i < sortedLogs.length; i++) {
    const log = sortedLogs[i];
    
    checkPageBreak(120);

    // Record header with number and date
    doc.font(fontBold).fontSize(14).fillColor("#1e40af");
    doc.text(`第 ${sortedLogs.length - i} 次指导记录`, { continued: false });
    doc.moveDown(0.3);

    // Info row
    doc.font(fontName).fontSize(10).fillColor("#6b7280");
    const statusText = getStatusText(log.status);
    const dateText = `指导日期：${formatDate(log.guidanceDate)}`;
    const publishText = `发布时间：${formatDateTime(log.createdAt)}`;
    doc.text(`${dateText}    |    ${publishText}    |    状态：${statusText}`);
    doc.moveDown(0.3);

    // Topic
    doc.font(fontBold).fontSize(11).fillColor("#111827");
    doc.text(`主题：${log.topic || "无主题"}`);
    doc.moveDown(0.3);

    // Content
    doc.font(fontName).fontSize(10).fillColor("#374151");
    const content = log.content || "无内容";
    // Wrap long content
    doc.text(content, {
      width: pageWidth,
      lineGap: 3,
    });
    doc.moveDown(0.4);

    // Attachments
    if (log.attachments && log.attachments.length > 0) {
      checkPageBreak(40);
      doc.font(fontBold).fontSize(10).fillColor("#6b7280");
      doc.text(`附件 (${log.attachments.length})：`);
      doc.font(fontName).fontSize(9).fillColor("#9ca3af");
      for (const att of log.attachments) {
        doc.text(`  - ${att.fileName}  (${formatFileSize(att.fileSize)})`, {
          width: pageWidth,
        });
      }
      doc.moveDown(0.3);
    }

    // Comments
    if (log.comments && log.comments.length > 0) {
      checkPageBreak(40);
      doc.font(fontBold).fontSize(10).fillColor("#6b7280");
      doc.text(`评论 (${log.comments.length})：`);
      doc.moveDown(0.2);
      for (const comment of log.comments) {
        doc.font(fontName).fontSize(9).fillColor("#4b5563");
        const roleLabel = comment.userRole === "teacher" ? "导师" : "学生";
        doc.text(`  [${roleLabel}] ${comment.userName}  (${formatDateTime(comment.createdAt)})`, {
          width: pageWidth,
        });
        doc.font(fontName).fontSize(9).fillColor("#6b7280");
        doc.text(`    ${comment.content}`, {
          width: pageWidth - 20,
          lineGap: 2,
        });
        doc.moveDown(0.2);
      }
      doc.moveDown(0.2);
    }

    // Separator between records
    if (i < sortedLogs.length - 1) {
      checkPageBreak(20);
      drawLine();
      doc.moveDown(0.3);
    }
  }

  // ==================== Footer on each page ====================
  const totalPages = doc.bufferedPageRange().count;
  for (let i = 0; i < totalPages; i++) {
    doc.switchToPage(i);
    doc.font(fontName).fontSize(8).fillColor("#9ca3af");
    doc.text(
      `第 ${i + 1} / ${totalPages} 页  |  ${studentName} - 指导记录  |  导出于 ${formatDateTime(new Date())}`,
      doc.page.margins.left,
      doc.page.height - 40,
      { align: "center", width: pageWidth }
    );
  }

  doc.end();

  return new Promise<Buffer>((resolve, reject) => {
    doc.on("end", () => {
      resolve(Buffer.concat(chunks));
    });
    doc.on("error", reject);
  });
}
