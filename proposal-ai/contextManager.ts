/**
 * 上下文管理器 - 负责压缩前置章节内容，避免超出LLM上下文窗口
 */
export class ContextManager {
  private readonly maxContextLength: number;
  private readonly summaryRatio: number;

  constructor(maxContextLength = 3000, summaryRatio = 0.3) {
    this.maxContextLength = maxContextLength;
    this.summaryRatio = summaryRatio;
  }

  /**
   * 压缩前置章节内容作为上下文
   */
  compressPreviousContext(previousContents: string[]): string {
    if (!previousContents || previousContents.length === 0) return "";

    const nonEmpty = previousContents.filter(c => c && c.trim().length > 0);
    if (nonEmpty.length === 0) return "";

    const combined = nonEmpty.join("\n\n---\n\n");

    if (combined.length <= this.maxContextLength) {
      return combined;
    }

    // 超出限制时，截取每个章节的摘要部分
    const summaries = nonEmpty.map(content => {
      const maxLen = Math.floor(this.maxContextLength * this.summaryRatio / nonEmpty.length);
      if (content.length <= maxLen) return content;
      return content.substring(0, maxLen) + "...（已截断）";
    });

    return summaries.join("\n\n---\n\n");
  }

  /**
   * 估算token数量（中文约1.5字/token，英文约4字/token）
   */
  estimateTokens(text: string): number {
    const chineseChars = (text.match(/[\u4e00-\u9fa5]/g) || []).length;
    const otherChars = text.length - chineseChars;
    return Math.ceil(chineseChars / 1.5 + otherChars / 4);
  }

  /**
   * 检查内容是否超出字数限制
   */
  checkWordLimit(content: string, limit: number): { valid: boolean; count: number } {
    // 统计中文字符数（不含标点和空格）
    const chineseChars = (content.match(/[\u4e00-\u9fa5]/g) || []).length;
    return { valid: chineseChars <= limit, count: chineseChars };
  }

  /**
   * 构建上下文（用于LLM生成）
   */
  buildContext(proposal: any, sections: any[]): string {
    const context: string[] = [];
    
    // 添加项目基本信息
    context.push(`项目名称：${proposal.title}`);
    context.push(`研究领域：${proposal.researchField || ""}`);
    context.push(`申报单位：${proposal.applicantUnit || ""}`);
    
    // 添加已确认的前置章节内容
    const confirmedSections = sections
      .filter((s: any) => s.status === "confirmed" && s.content)
      .sort((a: any, b: any) => (a.order || 0) - (b.order || 0));
    
    for (const section of confirmedSections) {
      context.push(`\n【${section.title}】\n${section.content}`);
    }
    
    return context.join("\n");
  }
}
