import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, router, protectedProcedure } from "./_core/trpc";
import { z } from "zod";
import {
  createProposal,
  getProposalById,
  getProposalsByUserId,
  updateProposal,
  createSection,
  getProposalSections,
  updateSection,
  addOperationLog,
  getOperationLogs,
} from "./db";
import {
  OfficialProposalWorkflow,
  OFFICIAL_WORKFLOW_ORDER,
  SECTION_TITLES,
  SECTION_DEPENDENCIES,
  type SectionKey,
} from "./workflow_official";
import { OfficialLLMPrompts } from "./llmPrompts";
import { LLMService } from "./llmService";
import { ContextManager } from "./contextManager";
import { eq } from "drizzle-orm";
import { generateDocxBuffer } from "./docxGeneratorReal";

const llmService = new LLMService();
const contextManager = new ContextManager();

export const appRouter = router({
  system: systemRouter,
  auth: router({
    me: publicProcedure.query((opts) => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  proposal: router({
    /**
     * 创建新的申报书项目
     */
    create: protectedProcedure
      .input(
        z.object({
          title: z.string().min(1, "项目名称不能为空"),
          abstract: z.string().min(1, "项目摘要不能为空"),
          researchField: z.string().min(1, "研究领域不能为空"),
          proposalType: z.enum(["national_key_rd", "national_sci_tech", "nsfc"]),
          applicantUnit: z.string().min(1, "申报单位不能为空"),
          principalInvestigatorName: z.string().optional(),
          principalInvestigatorEmail: z.string().optional(),
          principalInvestigatorPhone: z.string().optional(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const proposalResult = await createProposal(ctx.user.id, {
          title: input.title,
          abstract: input.abstract,
          researchField: input.researchField,
          proposalType: input.proposalType as "national_key_rd" | "national_sci_tech" | "nsfc",
          applicantUnit: input.applicantUnit,
          principalInvestigatorName: input.principalInvestigatorName,
          principalInvestigatorEmail: input.principalInvestigatorEmail,
          principalInvestigatorPhone: input.principalInvestigatorPhone,
          workflowState: JSON.stringify(new OfficialProposalWorkflow().getAllStatus()),
        });

        // 获取插入后的proposal id
        const proposalId = (proposalResult as any).insertId;
        if (!proposalId) {
          throw new Error("Failed to create proposal: no insertId returned");
        }

        // 为proposal创建所有8个章节
        for (const sectionKey of OFFICIAL_WORKFLOW_ORDER) {
          await createSection(proposalId, {
            sectionKey,
            title: SECTION_TITLES[sectionKey],
            status: "pending",
          });
        }

        // 记录操作日志
        await addOperationLog(proposalId, {
          action: "create",
          sectionKey: undefined,
          detail: `创建新项目: ${input.title}`,
        });

        return { id: proposalId, ...input };
      }),

    /**
     * 获取申报书项目详情
     */
    getById: protectedProcedure
      .input(z.object({ proposalId: z.number() }))
      .query(async ({ ctx, input }) => {
        const proposal = await getProposalById(input.proposalId);

        if (!proposal || proposal.userId !== ctx.user.id) {
          throw new Error("Proposal not found or access denied");
        }

        const sections = await getProposalSections(input.proposalId);
        return { proposal, sections };
      }),

    /**
     * 获取用户的所有申报书项目
     */
    list: protectedProcedure.query(async ({ ctx }) => {
      return await getProposalsByUserId(ctx.user.id);
    }),

    /**
     * 触发章节生成（流式输出）
     */
    generateSection: protectedProcedure
      .input(
        z.object({
          proposalId: z.number(),
          sectionKey: z.string(),
          userRequirements: z.string().optional(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const proposal = await getProposalById(input.proposalId);

        if (!proposal || proposal.userId !== ctx.user.id) {
          throw new Error("Proposal not found or access denied");
        }

        const sections = await getProposalSections(input.proposalId);
        const section = sections.find((s) => s.sectionKey === input.sectionKey);

        if (!section) {
          throw new Error("Section not found");
        }

        // 检查依赖关系
        // 从数据库中读取实际的章节状态来检查依赖
        const dependencies = SECTION_DEPENDENCIES[input.sectionKey as SectionKey] || [];
        const canGenerate = dependencies.every((dep) => {
          const depSection = sections.find((s) => s.sectionKey === dep);
          return depSection?.status === "confirmed";
        });
        
        if (!canGenerate) {
          throw new Error("前置章节未完成，无法生成此章节");
        }

        // 更新章节状态为生成中
        await updateSection(section.id, { status: "generating" });

        // 获取前置章节的摘要作为上下文
        const previousSections = sections.filter(
          (s) =>
            OFFICIAL_WORKFLOW_ORDER.indexOf(s.sectionKey as SectionKey) <
            OFFICIAL_WORKFLOW_ORDER.indexOf(input.sectionKey as SectionKey)
        );

        const previousContext = contextManager.compressPreviousContext(
          previousSections.map((s) => s.content || "")
        );

        // 生成LLM提示词
        const userPrompt = OfficialLLMPrompts.getUserPrompt(
          input.sectionKey as SectionKey,
          proposal.title,
          proposal.abstract || "",
          proposal.researchField || "",
          previousContext,
          input.userRequirements
        );

        // 调用LLM生成内容
        const content = await llmService.generateContent(
          OfficialLLMPrompts.getSystemPrompt(),
          userPrompt
        );

        // 计算字数
        const wordCount = content.split(/\s+/).length;

        // 更新章节内容和状态
        await updateSection(section.id, {
          content,
          wordCount,
          status: "draft_ready",
          userRequirements: input.userRequirements,
        });

        // 记录操作日志
        await addOperationLog(input.proposalId, {
          action: "generate",
          sectionKey: input.sectionKey,
          detail: `生成章节: ${SECTION_TITLES[input.sectionKey as SectionKey]}`,
        } as any);

        return { content, wordCount };
      }),

    /**
     * 确认章节内容
     */
    confirmSection: protectedProcedure
      .input(
        z.object({
          proposalId: z.number(),
          sectionKey: z.string(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const proposal = await getProposalById(input.proposalId);

        if (!proposal || proposal.userId !== ctx.user.id) {
          throw new Error("Proposal not found or access denied");
        }

        const sections = await getProposalSections(input.proposalId);
        const section = sections.find((s) => s.sectionKey === input.sectionKey);

        if (!section) {
          throw new Error("Section not found");
        }

        // 更新章节状态为已确认
        await updateSection(section.id, {
          status: "confirmed",
          confirmedAt: new Date(),
        });

        // 记录操作日志
        await addOperationLog(input.proposalId, {
          action: "confirm",
          sectionKey: input.sectionKey,
          detail: `确认章节: ${SECTION_TITLES[input.sectionKey as SectionKey]}`,
        } as any);

        return { success: true };
      }),

    /**
     * 请求章节修改
     */
    requestRevision: protectedProcedure
      .input(
        z.object({
          proposalId: z.number(),
          sectionKey: z.string(),
          feedback: z.string(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const proposal = await getProposalById(input.proposalId);

        if (!proposal || proposal.userId !== ctx.user.id) {
          throw new Error("Proposal not found or access denied");
        }

        const sections = await getProposalSections(input.proposalId);
        const section = sections.find((s) => s.sectionKey === input.sectionKey);

        if (!section) {
          throw new Error("Section not found");
        }

        // 更新章节状态为修改中
        await updateSection(section.id, {
          status: "revising",
          userRequirements: input.feedback,
        });

        // 记录操作日志
        await addOperationLog(input.proposalId, {
          action: "revision",
          sectionKey: input.sectionKey,
          detail: `请求修改: ${input.feedback}`,
        } as any);

        return { success: true };
      }),

    /**
     * 获取操作历史日志
     */
    getHistory: protectedProcedure
      .input(z.object({ proposalId: z.number() }))
      .query(async ({ ctx, input }) => {
        const proposal = await getProposalById(input.proposalId);

        if (!proposal || proposal.userId !== ctx.user.id) {
          throw new Error("Proposal not found or access denied");
        }

        return await getOperationLogs(input.proposalId);
      }),

    /**
     * 导出Word文档
     */
    exportWord: protectedProcedure
      .input(z.object({ proposalId: z.number() }))
      .mutation(async ({ ctx, input }) => {
        const proposal = await getProposalById(input.proposalId);

        if (!proposal || proposal.userId !== ctx.user.id) {
          throw new Error("Proposal not found or access denied");
        }

        const sections = await getProposalSections(input.proposalId);
        const confirmedSections = sections
          .filter((s) => s.status === "confirmed")
          .map((s) => ({
            sectionKey: s.sectionKey,
            title: s.title,
            content: s.content || "",
          }));

        if (confirmedSections.length === 0) {
          throw new Error("没有已确认的章节，无法导出");
        }

        const docxBuffer = await generateDocxBuffer(
          {
            title: proposal.title,
            abstract: proposal.abstract || "",
            researchField: proposal.researchField || "",
            proposalType: proposal.proposalType,
          },
          confirmedSections
        );

        return {
          filename: `${proposal.title}_申报书.docx`,
          buffer: docxBuffer.toString("base64"),
          mimeType:
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        };
      }),
  }),
});

export type AppRouter = typeof appRouter;
