import { COOKIE_NAME } from "@shared/const";
import { TRPCError } from "@trpc/server";
import { z } from "zod";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import * as db from "./db";
import { SignJWT } from "jose";
import { invokeLLM } from "./_core/llm";
import bcrypt from "bcryptjs";

function getJwtSecret() {
  return new TextEncoder().encode(process.env.JWT_SECRET || "thesis-secret-key");
}

async function createSessionToken(email: string, name: string): Promise<string> {
  const secretKey = getJwtSecret();
  const expiresInMs = 365 * 24 * 60 * 60 * 1000;
  const expirationSeconds = Math.floor((Date.now() + expiresInMs) / 1000);

  return new SignJWT({
    openId: email,
    appId: process.env.VITE_APP_ID || "thesis-app",
    name: name || email,
  })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setExpirationTime(expirationSeconds)
    .sign(secretKey);
}

const adminProcedure = protectedProcedure.use(({ ctx, next }) => {
  if (ctx.user.role !== "admin") {
    throw new TRPCError({ code: "FORBIDDEN", message: "需要管理员权限" });
  }
  return next({ ctx });
});

const teacherProcedure = protectedProcedure.use(({ ctx, next }) => {
  if (ctx.user.role !== "teacher" && ctx.user.role !== "admin") {
    throw new TRPCError({ code: "FORBIDDEN", message: "需要导师权限" });
  }
  return next({ ctx });
});

const studentProcedure = protectedProcedure.use(({ ctx, next }) => {
  if (ctx.user.role !== "student" && ctx.user.role !== "admin") {
    throw new TRPCError({ code: "FORBIDDEN", message: "需要学生权限" });
  }
  return next({ ctx });
});

// AI生成关键词
async function generateKeywords(title: string): Promise<string> {
  try {
    const response = await invokeLLM({
      messages: [
        { role: "system", content: "You are an academic assistant. Generate 3-5 keywords from the given thesis title. Return only the keywords separated by semicolons, no explanations. Keywords must be in English and must not duplicate the thesis title." },
        { role: "user", content: `Generate keywords for this thesis title: "${title}"` },
      ],
    });
    const content = response.choices[0]?.message?.content;
    return typeof content === 'string' ? content : "";
  } catch (error) {
    console.error("Failed to generate keywords:", error);
    return "";
  }
}

// AI生成研究方向
async function generateResearchFocus(title: string): Promise<string> {
  try {
    const response = await invokeLLM({
      messages: [
        { role: "system", content: "You are an academic assistant. Generate 1-2 research focus areas from the given thesis title. Return only the research areas separated by comma, no explanations. Must be in English and must differ from the major name (Electronic Information Engineering or Communication Engineering)." },
        { role: "user", content: `Generate research focus for this thesis title: "${title}"` },
      ],
    });
    const content = response.choices[0]?.message?.content;
    return typeof content === 'string' ? content : "";
  } catch (error) {
    console.error("Failed to generate research focus:", error);
    return "";
  }
}

export const appRouter = router({
  system: systemRouter,
  
  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return { success: true } as const;
    }),

    register: publicProcedure
      .input(z.object({
        email: z.string().min(1, "请输入邮箱或用户名"),
        password: z.string().min(6, "密码至少6位"),
        name: z.string().min(1, "请输入姓名"),
        role: z.enum(["teacher", "student"]),
        teacherType: z.enum(["chinese", "british"]).optional(),
        studentType: z.enum(["transfer", "non_transfer"]).optional(),
        studentMajor: z.enum(["electronic_info", "communication"]).optional(),
        studentId: z.string().optional(),
        candidateNo: z.string().optional(),
        studentClass: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const existing = await db.getUserByEmail(input.email);
        if (existing) {
          throw new TRPCError({ code: "CONFLICT", message: "该邮箱/用户名已被注册" });
        }

        const user = await db.createUser({
          email: input.email,
          password: input.password,
          name: input.name,
          role: input.role,
          teacherType: input.role === "teacher" ? input.teacherType : undefined,
          studentType: input.role === "student" ? input.studentType : undefined,
          studentMajor: input.role === "student" ? input.studentMajor : undefined,
          studentId: input.studentId,
          candidateNo: input.candidateNo,
          studentClass: input.studentClass,
        });

        if (!user) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "注册失败" });
        }

        const token = await createSessionToken(user.email, user.name || user.email);
        const cookieOptions = getSessionCookieOptions(ctx.req);
        ctx.res.cookie(COOKIE_NAME, token, cookieOptions);

        return { success: true, user };
      }),

    login: publicProcedure
      .input(z.object({
        email: z.string().min(1, "请输入邮箱或用户名"),
        password: z.string().min(1, "请输入密码"),
      }))
      .mutation(async ({ input, ctx }) => {
        const user = await db.verifyPassword(input.email, input.password);
        if (!user) {
          throw new TRPCError({ code: "UNAUTHORIZED", message: "邮箱或密码错误" });
        }

        const token = await createSessionToken(user.email, user.name || user.email);
        const cookieOptions = getSessionCookieOptions(ctx.req);
        ctx.res.cookie(COOKIE_NAME, token, cookieOptions);

        // 记录登录日志
        db.logUserActivity({
          userId: user.id,
          userName: user.name || user.email,
          userRole: user.role || 'student',
          action: 'login',
          module: 'auth',
          description: `用户 ${user.name || user.email} 登录系统`,
        });

        return { success: true, user };
      }),

    // 用户自主修改密码
    changePassword: protectedProcedure
      .input(z.object({
        currentPassword: z.string().min(1, "请输入当前密码"),
        newPassword: z.string().min(6, "新密码至少6位"),
      }))
      .mutation(async ({ input, ctx }) => {
        // 验证当前密码
        const verified = await db.verifyPassword(ctx.user.email, input.currentPassword);
        if (!verified) {
          throw new TRPCError({ code: "UNAUTHORIZED", message: "当前密码错误" });
        }
        
        // 更新密码
        const success = await db.updateUserPassword(ctx.user.id, input.newPassword);
        if (!success) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "密码修改失败" });
        }
        
        return { success: true };
      }),
  }),

  // 课题管理
  topic: router({
    // 获取导师的课题列表
    myTopics: teacherProcedure.query(async ({ ctx }) => {
      return db.getTopicsByTeacher(ctx.user.id);
    }),

    // 获取已发布的课题（学生浏览，显示热度和导师信息）
    listPublished: protectedProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const topicsWithHeat = await db.getPublishedTopicsWithHeat(academicYear);
      
      // 获取所有导师信息
      const teacherIdSet = new Set<number>();
      topicsWithHeat.forEach(t => teacherIdSet.add(t.teacherId));
      const teacherIds: number[] = [];
      teacherIdSet.forEach(id => teacherIds.push(id));
      const teacherInfoMap = new Map<number, { name: string; email: string; teacherType?: string; faculty?: string }>();
      for (const tid of teacherIds) {
        const teacher = await db.getUserById(tid);
        if (teacher) {
          teacherInfoMap.set(tid, {
            name: teacher.name || '',
            email: teacher.email,
            teacherType: teacher.teacherType || undefined,
            faculty: teacher.faculty || undefined,
          });
        }
      }
      
      return topicsWithHeat.map(t => {
        const teacherInfo = teacherInfoMap.get(t.teacherId);
        return {
          id: t.id,
          title: t.title,
          titleEn: t.titleEn,
          description: t.description,
          descriptionEn: t.descriptionEn,
          requiredSkills: t.requiredSkills,
          suitableMajor: t.suitableMajor,
          status: t.status,
          heat: t.heat, // 课题热度（被选人数）
          teacherType: t.teacherType, // 导师类型（用于分流学生过滤中方导师题目）
          keywords: t.keywords, // 论文关键词
          researchFocus: t.researchFocus, // 研究方向
          // 导师信息
          teacherName: teacherInfo?.name || '',
          teacherEmail: teacherInfo?.email || '',
          teacherFaculty: teacherInfo?.faculty || '',
          // 课题额外信息
          thesisType: (t as any).thesisType || '毕业论文', // 论文类型
          topicSource: (t as any).topicSource || '其他', // 选题来源
          topicLanguage: (t as any).topicLanguage || '英语', // 撰写语种
        };
      });
    }),

    // 创建课题
    create: teacherProcedure
      .input(z.object({
        title: z.string().optional().default(""),
        titleEn: z.string().min(1, "请输入英文标题"),
        description: z.string().optional().default(""),
        descriptionEn: z.string().min(1, "请输入英文描述"),
        requiredSkills: z.string().optional(),
        suitableMajor: z.enum(["electronic_info", "communication", "both"]).optional(),
        keywords: z.string().min(1, "请输入论文关键词"),
        researchFocus: z.string().min(1, "请输入研究方向"),
        thesisType: z.string().optional().default("毕业论文"),
        topicSource: z.string().min(1, "请选择选题来源"),
        topicLanguage: z.string().optional().default("英语"),
        researchProjectName: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查导师发布权限
        if ((ctx.user as any).canPublish === 0 || (ctx.user as any).canPublish === false) {
          throw new TRPCError({ code: "FORBIDDEN", message: "您的发布权限已被禁止，无法创建课题，请联系管理员" });
        }
        
        // 验证：如果选题来源不是"其他"且不是"科研项目（萨塞克斯老师适用）"，则researchProjectName必填
        if (input.topicSource !== "其他" && input.topicSource !== "科研项目（萨塞克斯老师适用）" && (!input.researchProjectName || !input.researchProjectName.trim())) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "请填写科研项目名称" });
        }
        // 验证：如果选题来源是"其他"或"科研项目（萨塞克斯老师适用）"，则researchProjectName必须为空
        if ((input.topicSource === "其他" || input.topicSource === "科研项目（萨塞克斯老师适用）") && input.researchProjectName && input.researchProjectName.trim()) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "选题来源为\"其他\"或\"科研项目（萨塞克斯老师适用）\"时，科研项目名称必须为空" });
        }
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        // 当title为空时，使用titleEn填充；当description为空时，使用descriptionEn填充
        const title = input.title && input.title.trim() ? input.title : input.titleEn;
        const description = input.description && input.description.trim() ? input.description : input.descriptionEn;
        
        // 检查题库中是否存在相同标题
        if (title) {
          const libraryCheck = await db.checkTopicTitleInLibrary(title);
          if (libraryCheck.exists) {
            throw new TRPCError({ 
              code: "CONFLICT", 
              message: `该课题标题已存在于题库中（${libraryCheck.existingTopic?.academicYear || '未知学年'}，导师: ${libraryCheck.existingTopic?.teacherName || '未知'}），请修改课题标题` 
            });
          }
        }
        
        return db.createTopic({
          ...input,
          title,
          description,
          teacherId: ctx.user.id,
          academicYear,
          status: "draft",
        });
      }),

    // 更新课题
    update: teacherProcedure
      .input(z.object({
        id: z.number(),
        title: z.string().optional(),
        titleEn: z.string().optional(),
        description: z.string().optional(),
        descriptionEn: z.string().optional(),
        requiredSkills: z.string().optional(),
        suitableMajor: z.enum(["electronic_info", "communication", "both"]).optional(),
        keywords: z.string().optional(),
        researchFocus: z.string().optional(),
        thesisType: z.string().optional(),
        topicSource: z.string().optional(),
        topicLanguage: z.string().optional(),
        researchProjectName: z.string().optional(),
        status: z.enum(["draft", "published"]).optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 验证：如果选题来源不是"其他"且不是"科研项目（萨塞克斯老师适用）"，则researchProjectName必填
        if (input.topicSource && input.topicSource !== "其他" && input.topicSource !== "科研项目（萨塞克斯老师适用）" && (!input.researchProjectName || !input.researchProjectName.trim())) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "请填写科研项目名称" });
        }
        // 验证：如果选题来源是"其他"或"科研项目（萨塞克斯老师适用）"，则researchProjectName必须为空
        if (input.topicSource && (input.topicSource === "其他" || input.topicSource === "科研项目（萨塞克斯老师适用）") && input.researchProjectName && input.researchProjectName.trim()) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "选题来源为\"其他\"或\"科研项目（萨塞克斯老师适用）\"时，科研项目名称必须为空" });
        }
        const topic = await db.getTopicById(input.id);
        if (!topic) {
          throw new TRPCError({ code: "NOT_FOUND", message: "课题不存在" });
        }
        if (topic.teacherId !== ctx.user.id && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权修改此课题" });
        }
        const { id, ...data } = input;
        // 当title为空时，使用titleEn填充；当description为空时，使用descriptionEn填充
        if (data.titleEn && (!data.title || !data.title.trim())) {
          data.title = data.titleEn;
        }
        if (data.descriptionEn && (!data.description || !data.description.trim())) {
          data.description = data.descriptionEn;
        }
        return db.updateTopic(id, data);
      }),

    // 删除课题
    delete: teacherProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input, ctx }) => {
        const topic = await db.getTopicById(input.id);
        if (!topic) {
          throw new TRPCError({ code: "NOT_FOUND", message: "课题不存在" });
        }
        if (topic.teacherId !== ctx.user.id && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权删除此课题" });
        }
        return db.deleteTopic(input.id);
      }),

    // 发布课题（中方导师受年度限额限制，英方导师不限）
    publish: teacherProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input, ctx }) => {
        const topic = await db.getTopicById(input.id);
        if (!topic) {
          throw new TRPCError({ code: "NOT_FOUND", message: "课题不存在" });
        }
        if (topic.teacherId !== ctx.user.id && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权发布此课题" });
        }
        
        // 检查导师发布权限
        // canPublish 字段是 tinyint 类型，0 表示禁止发布，1 表示允许发布
        if ((ctx.user as any).canPublish === 0 || (ctx.user as any).canPublish === false) {
          throw new TRPCError({ code: "FORBIDDEN", message: "您的发布权限已被禁止，请联系管理员" });
        }
        
        // 中方导师检查年度限额
        if (ctx.user.teacherType === "chinese") {
          const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
          const publishedCount = await db.getTeacherPublishedTopicCount(ctx.user.id, academicYear);
          const quota = ctx.user.annualQuota || 5;
          if (publishedCount >= quota) {
            throw new TRPCError({ 
              code: "FORBIDDEN", 
              message: `您已达到年度发布限额(${quota}个)，无法发布更多课题` 
            });
          }
        }
        // 英方导师不受限额限制
        
        // 检查时间阶段：如果配置了导师发布题目时间段，则必须在该时间段内才能发布
        const timePhase = await db.checkTimePhase();
        if (timePhase.topicPublishStart && timePhase.topicPublishEnd) {
          if (timePhase.phase !== "topic_publish") {
            throw new TRPCError({ 
              code: "FORBIDDEN", 
              message: "当前不在导师发布题目时间段，无法发布课题" 
            });
          }
        } else if (timePhase.phase === "student_selection" || timePhase.phase === "teacher_confirm") {
          // 如果没有配置专门的发布时间段，则在学生选题和导师确认期间不允许发布
          throw new TRPCError({ 
            code: "FORBIDDEN", 
            message: "当前处于学生选题或导师确认时间段，无法发布课题" 
          });
        }
        
        // 检查题库中是否存在相同标题
        const libraryCheck = await db.checkTopicTitleInLibrary(topic.title, topic.id);
        if (libraryCheck.exists) {
          throw new TRPCError({ 
            code: "CONFLICT", 
            message: `该课题标题已存在于题库中（${libraryCheck.existingTopic?.academicYear || '未知学年'}，导师: ${libraryCheck.existingTopic?.teacherName || '未知'}），请修改课题标题` 
          });
        }
        
        // 发布课题
        const result = await db.updateTopic(input.id, { status: "published", isCurrentYear: 1 });
        
        // 添加到题库
        await db.addToTopicLibrary(topic, ctx.user.name || '未知导师');
        
        return result;
      }),

    // 撤回发布（在学生选题和导师确认时间段外才允许）
    unpublish: teacherProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input, ctx }) => {
        const topic = await db.getTopicById(input.id);
        if (!topic) {
          throw new TRPCError({ code: "NOT_FOUND", message: "课题不存在" });
        }
        if (topic.teacherId !== ctx.user.id && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权撤回此课题" });
        }
        
        // 检查当前时间阶段
        const timePhase = await db.checkTimePhase();
        if (timePhase.topicPublishStart && timePhase.topicPublishEnd) {
          if (timePhase.phase !== "topic_publish") {
            throw new TRPCError({ 
              code: "FORBIDDEN", 
              message: "当前不在导师发布题目时间段，无法撤回发布" 
            });
          }
        } else if (timePhase.phase === "student_selection" || timePhase.phase === "teacher_confirm") {
          throw new TRPCError({ 
            code: "FORBIDDEN", 
            message: "当前处于学生选题或导师确认时间段，无法撤回发布" 
          });
        }
        
        // 检查是否有学生已选择该课题
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const wishCount = await db.getTopicWishCount(input.id, academicYear);
        if (wishCount > 0) {
          throw new TRPCError({ 
            code: "FORBIDDEN", 
            message: `已有${wishCount}名学生选择了该课题，无法撤回发布` 
          });
        }
        
        // 撤回课题
        const result = await db.updateTopic(input.id, { status: "draft" });
        
        // 从题库中移除
        await db.removeFromTopicLibrary(input.id);
        
        return result;
      }),

    // 课题查重
    checkDuplicate: teacherProcedure
      .input(z.object({ title: z.string(), excludeId: z.number().optional() }))
      .query(async ({ input }) => {
        return db.checkTopicDuplicate(input.title, input.excludeId);
      }),

    // 批量导入课题
    bulkImport: teacherProcedure
      .input(z.object({
        topics: z.array(z.object({
          titleEn: z.string().min(1, "英文标题不能为空"),
          title: z.string().optional().default(""),
          descriptionEn: z.string().min(1, "英文描述不能为空"),
          description: z.string().optional().default(""),
          keywords: z.string().min(1, "关键词不能为空"),
          researchFocus: z.string().min(1, "研究方向不能为空"),
          topicSource: z.string().optional().default("其他"),
          topicLanguage: z.string().optional().default("英语"),
          thesisType: z.string().optional().default("毕业论文"),
          suitableMajor: z.enum(["electronic_info", "communication", "both"]).optional().default("both"),
          requiredSkills: z.string().optional(),
          researchProjectName: z.string().optional(),
        })),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查导师发布权限
        if ((ctx.user as any).canPublish === 0 || (ctx.user as any).canPublish === false) {
          throw new TRPCError({ code: "FORBIDDEN", message: "您的发布权限已被禁止，无法导入课题，请联系管理员" });
        }
        
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        let success = 0;
        let failed = 0;
        const errors: string[] = [];
        
        for (let i = 0; i < input.topics.length; i++) {
          const topicData = input.topics[i];
          try {
            // 验证：如果选题来源不是"其他"且不是"科研项目（萨塞克斯老师适用）"，则researchProjectName必填
            if (topicData.topicSource !== "其他" && topicData.topicSource !== "科研项目（萨塞克斯老师适用）" && (!topicData.researchProjectName || !topicData.researchProjectName.trim())) {
              throw new Error("选题来源非'其他'或'科研项目（萨塞克斯老师适用）'时，科研项目名称必填");
            }
            // 验证：如果选题来源是"其他"或"科研项目（萨塞克斯老师适用）"，则researchProjectName必须为空
            if ((topicData.topicSource === "其他" || topicData.topicSource === "科研项目（萨塞克斯老师适用）") && topicData.researchProjectName && topicData.researchProjectName.trim()) {
              throw new Error("选题来源为'其他'或'科研项目（萨塞克斯老师适用）'时，科研项目名称必须为空");
            }
            
            // 当title为空时，使用titleEn填充
            const title = topicData.title && topicData.title.trim() ? topicData.title : topicData.titleEn;
            const description = topicData.description && topicData.description.trim() ? topicData.description : topicData.descriptionEn;
            
            // 检查题库中是否存在相同标题
            const libraryCheck = await db.checkTopicTitleInLibrary(title);
            if (libraryCheck.exists) {
              throw new Error(`课题标题已存在于题库中（${libraryCheck.existingTopic?.academicYear || '未知学年'}）`);
            }
            
            await db.createTopic({
              ...topicData,
              title,
              description,
              teacherId: ctx.user.id,
              academicYear,
              status: "draft",
            });
            success++;
          } catch (error: any) {
            failed++;
            errors.push(`第${i + 1}行: ${error.message}`);
          }
        }
        
        return { success, failed, errors, total: input.topics.length };
      }),
  }),

  // 志愿管理（志愿优先，教师确认制）
  wish: router({
    // 获取学生的志愿
    myWishes: studentProcedure.query(async ({ ctx }) => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      return db.getWishesByStudent(ctx.user.id, academicYear);
    }),

    // 提交志愿（选题声明非强制）
    submit: studentProcedure
      .input(z.object({
        wishes: z.array(z.object({
          topicId: z.number(),
          priority: z.number(),
          statement: z.string().optional(), // 非强制
        })),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查当前时间阶段
        const timePhase = await db.checkTimePhase();
        const isTransfer = ctx.user.studentType === "transfer";
        
        // 获取当前学年信息
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        
        // 检查当前时间阶段
        if (timePhase.phase !== "student_selection" && timePhase.phase !== "none") {
          throw new TRPCError({ 
            code: "FORBIDDEN", 
            message: "当前不在学生选题时间段，无法提交志愿" 
          });
        }

        // 检查学生是否属于当前学年
        if (ctx.user.academicYear && ctx.user.academicYear !== academicYear) {
          throw new TRPCError({ 
            code: "FORBIDDEN", 
            message: `您属于${ctx.user.academicYear}学年，当前学年为${academicYear}，无法进行选题操作` 
          });
        }
        
        // 检查志愿数量限制（所有学生统一为3个）
        const maxWishes = 3; // 所有学生都只能选3个志愿
        const minWishes = 3; // 必须填报3个志愿
        
        if (input.wishes.length < minWishes) {
          throw new TRPCError({ 
            code: "BAD_REQUEST", 
            message: `必须填报${minWishes}个志愿才能提交` 
          });
        }
        
        if (input.wishes.length > maxWishes) {
          throw new TRPCError({ 
            code: "BAD_REQUEST", 
            message: `最多可填报${maxWishes}个志愿` 
          });
        }
        
        // 分流学生只能选择中方导师的题目
        if (isTransfer) {
          for (const wish of input.wishes) {
            const topic = await db.getTopicById(wish.topicId);
            if (!topic) {
              throw new TRPCError({ code: "NOT_FOUND", message: `课题ID ${wish.topicId} 不存在` });
            }
            const teacher = await db.getUserById(topic.teacherId);
            if (!teacher || teacher.teacherType !== "chinese") {
              throw new TRPCError({ 
                code: "FORBIDDEN", 
                message: `分流学生只能选择中方导师的题目，课题「${topic.title}」不符合要求` 
              });
            }
          }
        }

        // 检查分流学生优先模式：如果激活且学生为非分流学生，且选择的是中方导师的课题，志愿将被自动拒绝
        const priorityMode = await db.checkTransferStudentPriorityMode();
        
        // 删除旧志愿
        await db.deleteWishesByStudent(ctx.user.id, academicYear);
        
        // 创建新志愿
        // 如果处于分流学生优先模式且为非分流学生，且选择的是中方导师的课题，志愿状态直接设为 rejected
        // 英文老师的课题不受分流优先模式影响
        const wishesData = await Promise.all(input.wishes.map(async w => {
          const topic = await db.getTopicById(w.topicId);
          const teacher = topic ? await db.getUserById(topic.teacherId) : null;
          const isChineseTeacherTopic = teacher?.teacherType === "chinese";
          
          // 只有非分流学生选择中方导师课题时才自动拒绝
          const autoReject = priorityMode.isActive && !isTransfer && isChineseTeacherTopic;
          
          return {
            studentId: ctx.user.id,
            topicId: w.topicId,
            priority: w.priority,
            statement: w.statement || null, // 非强制，可为空
            academicYear,
            status: autoReject ? "rejected" as const : "pending" as const,
            teacherDecision: autoReject ? "rejected" as const : "pending" as const,
          };
        }));
        
        await db.bulkCreateWishes(wishesData);

        // 记录志愿提交日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'student',
          action: 'submit_wish',
          module: 'wish',
          description: `提交了 ${input.wishes.length} 个志愿`,
        });
        
        // 检查是否有志愿被自动拒绝
        const hasAutoRejected = wishesData.some(w => w.status === "rejected");
        const allAutoRejected = wishesData.every(w => w.status === "rejected");
        
        if (allAutoRejected) {
          return { 
            success: true, 
            autoRejected: true,
            message: "当前处于分流学生优先模式，您选择的中方导师课题志愿已被自动拒绝。英文老师的课题不受影响。" 
          };
        } else if (hasAutoRejected) {
          return { 
            success: true, 
            autoRejected: true,
            message: "当前处于分流学生优先模式，您选择的部分中方导师课题志愿已被自动拒绝，英文老师的课题志愿正常提交。" 
          };
        }
        return { success: true };
      }),
  }),

  // 匹配管理（志愿优先，教师确认制）
  match: router({
    // 学生查看匹配结果
    myMatch: studentProcedure.query(async ({ ctx }) => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const match = await db.getMatchByStudent(ctx.user.id, academicYear);
      if (!match) return null;
      
      const topic = await db.getTopicById(match.topicId);
      const teacher = await db.getUserById(match.teacherId);
      
      return {
        ...match,
        topic,
        teacher: teacher ? {
          id: teacher.id,
          name: teacher.name,
          email: teacher.email,
          teacherType: teacher.teacherType,
        } : null,
      };
    }),

    // 学生查看志愿审核状态
    myWishStatus: studentProcedure.query(async ({ ctx }) => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const wishes = await db.getWishesByStudent(ctx.user.id, academicYear);
      
      const results = await Promise.all(wishes.map(async w => {
        const topic = await db.getTopicById(w.topicId);
        return {
          ...w,
          topic: topic ? { id: topic.id, title: topic.title, titleEn: topic.titleEn, keywords: topic.keywords, researchFocus: topic.researchFocus } : null,
        };
      }));
      
      return results;
    }),

    // 导师查看指导的学生
    myStudents: teacherProcedure.query(async ({ ctx }) => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const matches = await db.getMatchesByTeacher(ctx.user.id, academicYear);
      
      const results = await Promise.all(matches.map(async m => {
        const student = await db.getUserById(m.studentId);
        const topic = await db.getTopicById(m.topicId);
        // 获取学生的论文终稿信息
        const thesisDraft = await db.getThesisDraftByMatchId(m.id);
        return {
          ...m,
          student: student ? {
            id: student.id,
            name: student.name,
            email: student.email,
            studentType: student.studentType,
            studentMajor: student.studentMajor,
            studentId: student.studentId,
            sussexId: student.sussexId,
            studentClass: student.studentClass,
          } : null,
          topic,
          thesisDraft: thesisDraft ? {
            id: thesisDraft.id,
            fileName: thesisDraft.fileName,
            fileUrl: thesisDraft.fileUrl,
            fileSize: thesisDraft.fileSize,
            version: thesisDraft.version,
            status: thesisDraft.status,
            submittedAt: thesisDraft.submittedAt,
            score: thesisDraft.score,
            scoredAt: thesisDraft.scoredAt,
            scoredBy: thesisDraft.scoredBy,
          } : null,
        };
      }));
      
      return results;
    }),

    // 检查是否处于分流学生优先模式
    checkTransferPriorityMode: teacherProcedure.query(async () => {
      return db.checkTransferStudentPriorityMode();
    }),

    // 获取中方导师名额状态（供导师端显示）
    getQuotaStatus: teacherProcedure.query(async () => {
      return db.getChineseTeacherQuotaStats();
    }),

    // 导师查看待审核的志愿申请（志愿优先，教师确认制核心）
    // 根据当前审核轮次过滤，只显示对应轮次的待审核申请
    pendingWishes: teacherProcedure.query(async ({ ctx }) => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const pendingWishes = await db.getPendingWishesByTeacher(ctx.user.id, academicYear);
      
      // 获取当前审核轮次
      const currentReviewPriority = await db.getCurrentReviewPriority(academicYear);
      
      // 只返回当前审核轮次的志愿
      const filteredWishes = currentReviewPriority > 0 
        ? pendingWishes.filter(w => w.priority === currentReviewPriority)
        : pendingWishes;
      
      const results = await Promise.all(filteredWishes.map(async w => {
        const student = await db.getUserById(w.studentId);
        const topic = await db.getTopicById(w.topicId);
        return {
          ...w,
          student: student ? {
            id: student.id,
            name: student.name,
            namePinyin: student.namePinyin,
            email: student.email,
            studentType: student.studentType,
            studentMajor: student.studentMajor,
            studentId: student.studentId,
            candidateNo: student.candidateNo,
            studentClass: student.studentClass,
          } : null,
          topic: topic ? { id: topic.id, title: topic.title, titleEn: topic.titleEn, keywords: topic.keywords, researchFocus: topic.researchFocus } : null,
          currentReviewPriority, // 返回当前审核轮次信息
        };
      }));
      
      return results;
    }),

    // 导师审核志愿（同意/不同意）
    reviewWish: teacherProcedure
      .input(z.object({
        wishId: z.number(),
        decision: z.enum(["approved", "rejected"]),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查当前时间阶段
        const timePhase = await db.checkTimePhase();
        if (timePhase.phase !== "teacher_confirm" && timePhase.phase !== "none") {
          throw new TRPCError({ 
            code: "FORBIDDEN", 
            message: "当前不在导师确认时间段，无法审核志愿" 
          });
        }

        // 验证该志愿对应的课题属于当前导师
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const pendingWishes = await db.getPendingWishesByTeacher(ctx.user.id, academicYear);
        const wish = pendingWishes.find(w => w.id === input.wishId);
        
        if (!wish) {
          throw new TRPCError({ code: "NOT_FOUND", message: "该志愿不存在或不在您的审核范围内" });
        }

        // 检查名额限制和分流学生优先模式
        if (input.decision === "approved" && ctx.user.teacherType === "chinese") {
          // 检查名额是否已满
          const quotaStats = await db.getChineseTeacherQuotaStats();
          if (quotaStats.quotaEnabled && quotaStats.isQuotaFull) {
            throw new TRPCError({ 
              code: "FORBIDDEN", 
              message: `中方导师可确认学生总名额已满（${quotaStats.confirmedCount}/${quotaStats.totalQuota}），无法再确认新的学生志愿。` 
            });
          }
          
          // 检查分流学生优先模式
          const priorityMode = await db.checkTransferStudentPriorityMode();
          if (priorityMode.isActive) {
            const student = await db.getUserById(wish.studentId);
            if (student && student.studentType !== "transfer") {
              throw new TRPCError({ 
                code: "FORBIDDEN", 
                message: priorityMode.triggeredByQuota
                  ? `当前剩余确认名额（${quotaStats.remainingQuota}）需保留给分流学生，中方导师无法审批通过非分流学生的志愿申请。`
                  : "当前处于分流学生优先模式，中方导师无法审批通过非分流学生的志愿申请。请优先处理分流学生的申请。"
              });
            }
          }
        }
        
        const result = await db.reviewWish(input.wishId, input.decision);
        if (!result.success) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: result.message });
        }

        // 记录导师审核志愿日志
        const wishStudent = await db.getUserById(wish.studentId);
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'teacher',
          action: input.decision === 'approved' ? 'approve_wish' : 'reject_wish',
          module: 'wish',
          targetType: 'wish',
          targetId: input.wishId,
          targetName: wishStudent?.name || `学生ID:${wish.studentId}`,
          description: `${input.decision === 'approved' ? '同意' : '拒绝'}了学生 ${wishStudent?.name || wish.studentId} 的志愿申请`,
        });
        
        // 确认成功后，检查是否触发名额满额自动处理
        if (input.decision === "approved" && ctx.user.teacherType === "chinese") {
          const postQuotaStats = await db.getChineseTeacherQuotaStats();
          if (postQuotaStats.quotaEnabled && postQuotaStats.isQuotaFull) {
            // 名额已满，触发自动处理
            const autoResult = await db.handleChineseTeacherQuotaFull();
            console.log("[QuotaFull] 自动处理结果:", autoResult.message);
            return { 
              success: true, 
              message: result.message + "。" + autoResult.message 
            };
          }
          
          // 检查是否刚进入分流优先模式，如果是则自动触发批量拒绝非分流学生志愿
          const postPriorityMode = await db.checkTransferStudentPriorityMode();
          if (postPriorityMode.isActive) {
            const batchResult = await db.batchRejectNonTransferStudentWishes();
            if (batchResult.rejectedCount > 0) {
              console.log("[TransferPriority] 分流优先模式自动拒绝结果:", batchResult.message);
              return {
                success: true,
                message: result.message + "。" + batchResult.message
              };
            }
          }
        }
        
        return { success: true, message: result.message };
      }),

    // 保留旧的冲突处理接口（兼容）
    myConflicts: teacherProcedure.query(async ({ ctx }) => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const conflicts = await db.getPendingConflictsByTeacher(ctx.user.id, academicYear);
      
      const results = await Promise.all(conflicts.map(async c => {
        const topic = await db.getTopicById(c.topicId);
        const studentIds = c.studentIds as number[];
        const students = await Promise.all(studentIds.map(async id => {
          const student = await db.getUserById(id);
          const wishes = await db.getWishesByStudent(id, academicYear);
          const wish = wishes.find(w => w.topicId === c.topicId);
          return student ? {
            id: student.id,
            name: student.name,
            email: student.email,
            studentType: student.studentType,
            studentMajor: student.studentMajor,
            statement: wish?.statement,
          } : null;
        }));
        
        return {
          ...c,
          topic,
          students: students.filter(Boolean),
        };
      }));
      
      return results;
    }),

    // 保留旧的选择学生接口（兼容）
    selectStudent: teacherProcedure
      .input(z.object({
        conflictId: z.number(),
        studentId: z.number(),
      }))
      .mutation(async ({ input, ctx }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const conflicts = await db.getPendingConflictsByTeacher(ctx.user.id, academicYear);
        const conflict = conflicts.find(c => c.id === input.conflictId);
        
        if (!conflict) {
          throw new TRPCError({ code: "NOT_FOUND", message: "冲突记录不存在" });
        }
        
        await db.resolveConflict(input.conflictId, input.studentId);
        await db.createMatch({
          studentId: input.studentId,
          topicId: conflict.topicId,
          teacherId: ctx.user.id,
          matchRound: conflict.matchRound,
          academicYear,
        });
        await db.updateTopic(conflict.topicId, { status: "used" });
        
        return { success: true };
      }),

    resolveConflict: teacherProcedure
      .input(z.object({
        conflictId: z.number(),
        selectedStudentId: z.number(),
      }))
      .mutation(async ({ input, ctx }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const conflicts = await db.getPendingConflictsByTeacher(ctx.user.id, academicYear);
        const conflict = conflicts.find(c => c.id === input.conflictId);
        
        if (!conflict) {
          throw new TRPCError({ code: "NOT_FOUND", message: "冲突记录不存在" });
        }
        
        await db.resolveConflict(input.conflictId, input.selectedStudentId);
        await db.createMatch({
          studentId: input.selectedStudentId,
          topicId: conflict.topicId,
          teacherId: ctx.user.id,
          matchRound: conflict.matchRound,
          academicYear,
        });
        await db.updateTopic(conflict.topicId, { status: "used" });
        
        return { success: true };
      }),
  }),

  // 管理员功能
  admin: router({
    // 中方导师课题与生源监控
    getChineseTeacherTopicMonitoring: adminProcedure.query(async () => {
      return db.getChineseTeacherTopicMonitoring();
    }),

    getChineseTeacherTopicList: adminProcedure
      .input(z.object({
        status: z.enum(["used", "unused", "all"]).optional().default("all"),
      }))
      .query(async ({ input }) => {
        return db.getChineseTeacherTopicList({ status: input.status });
      }),

    getPendingTransferStudentsList: adminProcedure.query(async () => {
      return db.getPendingTransferStudentsList();
    }),

    // 批量拒绝所有中方导师待审核的非分流学生志愿（仅在分流优先模式下可用）
    batchRejectNonTransferStudentWishes: adminProcedure.mutation(async () => {
      return db.batchRejectNonTransferStudentWishes();
    }),

    // 获取中方导师确认名额统计
    getChineseTeacherQuotaStats: adminProcedure.query(async () => {
      return db.getChineseTeacherQuotaStats();
    }),

    // 手动触发名额满额处理（管理员操作）
    triggerQuotaFullHandling: adminProcedure.mutation(async () => {
      const quotaStats = await db.getChineseTeacherQuotaStats();
      if (!quotaStats.quotaEnabled) {
        throw new TRPCError({ code: "BAD_REQUEST", message: "名额限制功能未启用" });
      }
      if (!quotaStats.isQuotaFull) {
        throw new TRPCError({ code: "BAD_REQUEST", message: "名额尚未满，无法触发满额处理" });
      }
      return db.handleChineseTeacherQuotaFull();
    }),

    getUsers: adminProcedure.query(async () => {
      return db.getAllUsers();
    }),

    updateUser: adminProcedure
      .input(z.object({
        id: z.number(),
        name: z.string().optional(),
        role: z.enum(["admin", "teacher", "student"]).optional(),
        teacherType: z.enum(["chinese", "british"]).optional(),
        studentType: z.enum(["transfer", "non_transfer"]).optional(),
        studentMajor: z.enum(["electronic_info", "communication"]).optional(),
        annualQuota: z.number().optional(),
        studentId: z.string().optional(),
        candidateNo: z.string().optional(),
        studentClass: z.string().optional(),
        faculty: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const { id, ...data } = input;
        return db.updateUser(id, data);
      }),

    deleteUser: adminProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        return db.deleteUser(input.id);
      }),

    // 批量导入用户（支持新字段）
    bulkImportUsers: adminProcedure
      .input(z.object({
        users: z.array(z.object({
          email: z.string(),
          password: z.string(),
          name: z.string().optional(),
          role: z.enum(["teacher", "student"]),
          teacherType: z.enum(["chinese", "british"]).optional(),
          studentType: z.enum(["transfer", "non_transfer"]).optional(),
          studentMajor: z.enum(["electronic_info", "communication"]).optional(),
          studentId: z.string().optional(), // 中方学号
          sussexId: z.string().optional(), // 萨塞克斯学号
          candidateNo: z.string().optional(),
          studentClass: z.string().optional(),
          faculty: z.string().optional(),
          annualQuota: z.number().optional(),
          teacherNo: z.string().optional(), // 导师工号
          sussexEmail: z.string().optional(), // 萨塞克斯邮箱
          academicYear: z.string().optional(), // 学生所属学年
          namePinyin: z.string().optional(), // 姓名拼音
        })),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.bulkCreateUsers(input.users);

        // 记录批量导入日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'admin',
          action: 'bulk_import',
          module: 'user',
          description: `批量导入了 ${input.users.length} 个用户`,
        });

        return result;
      }),

    // 单项创建导师
    createTeacher: adminProcedure
      .input(z.object({
        email: z.string().min(1),
        name: z.string().min(1),
        teacherType: z.enum(["chinese", "british"]),
        teacherNo: z.string().optional(),
        sussexEmail: z.string().optional(),
        annualQuota: z.number().optional(),
        faculty: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const initialPassword = "zjsu@" + input.email.slice(0, 3).toLowerCase();
        const hashedPassword = await bcrypt.hash(initialPassword, 10);
        const result = await db.createSingleUser({
          email: input.email,
          password: hashedPassword,
          name: input.name,
          role: "teacher",
          teacherType: input.teacherType,
          teacherNo: input.teacherNo || "0000000",
          sussexEmail: input.sussexEmail,
          annualQuota: input.annualQuota || 5,
          faculty: input.faculty || "萨塞克斯人工智能学院",
          initialPassword,
        });

        // 记录创建导师日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'admin',
          action: 'create_user',
          module: 'user',
          targetType: 'teacher',
          targetName: input.name,
          description: `创建导师: ${input.name} (${input.email})`,
        });

        return result;
      }),

    // 单项创建学生
    createStudent: adminProcedure
      .input(z.object({
        email: z.string().min(1),
        name: z.string().min(1),
        studentType: z.enum(["transfer", "non_transfer"]),
        studentMajor: z.enum(["electronic_info", "communication"]),
        studentId: z.string().optional(),
        sussexId: z.string().optional(),
        sussexEmail: z.string().optional(),
        candidateNo: z.string().optional(),
        studentClass: z.string().optional(),
        faculty: z.string().optional(),
        academicYear: z.string().optional(),
        namePinyin: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const initialPassword = "zjsu@" + input.email.slice(0, 3).toLowerCase();
        const hashedPassword = await bcrypt.hash(initialPassword, 10);
        const result = await db.createSingleUser({
          email: input.email,
          password: hashedPassword,
          name: input.name,
          role: "student",
          studentType: input.studentType,
          studentMajor: input.studentMajor,
          studentId: input.studentId,
          sussexId: input.sussexId,
          sussexEmail: input.sussexEmail,
          candidateNo: input.candidateNo,
          studentClass: input.studentClass,
          faculty: input.faculty || "萨塞克斯人工智能学院",
          academicYear: input.academicYear,
          namePinyin: input.namePinyin,
          initialPassword,
        });

        // 记录创建学生日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'admin',
          action: 'create_user',
          module: 'user',
          targetType: 'student',
          targetName: input.name,
          description: `创建学生: ${input.name} (${input.email})`,
        });

        return result;
      }),

    // 单项创建管理员
    createAdmin: adminProcedure
      .input(z.object({
        email: z.string().min(1),
        name: z.string().min(1),
        password: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const initialPassword = input.password || ("zjsu@" + input.email.slice(0, 3).toLowerCase());
        const hashedPassword = await bcrypt.hash(initialPassword, 10);
        const result = await db.createSingleUser({
          email: input.email,
          password: hashedPassword,
          name: input.name,
          role: "admin",
          initialPassword,
        });
        if (result.success) {
        }
        return result;
      }),

    // 获取所有管理员列表
    getAdmins: adminProcedure.query(async () => {
      return db.getAdminUsers();
    }),

    // 删除管理员
    deleteAdmin: adminProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input, ctx }) => {
        // 不能删除自己
        if (input.id === ctx.user.id) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "不能删除自己的账号" });
        }
        // 获取被删除管理员信息
        const targetAdmin = await db.getUserById(input.id);
        await db.deleteUser(input.id);
        return { success: true };
      }),

    // 批量导入管理员
    bulkImportAdmins: adminProcedure
      .input(z.object({
        admins: z.array(z.object({
          email: z.string().min(1),
          name: z.string().optional(),
          password: z.string().optional(),
        })),
      }))
      .mutation(async ({ input, ctx }) => {
        let success = 0;
        let failed = 0;
        const errors: string[] = [];
        
        for (const admin of input.admins) {
          try {
            const initialPassword = admin.password || ("zjsu@" + admin.email.slice(0, 3).toLowerCase());
            const hashedPassword = await bcrypt.hash(initialPassword, 10);
            await db.createSingleUser({
              email: admin.email,
              password: hashedPassword,
              name: admin.name || admin.email,
              role: "admin",
              initialPassword,
            });
            success++;
          } catch (error: any) {
            failed++;
            errors.push(`${admin.email}: ${error.message || "创建失败"}`);
          }
        }
        

        
        return { success, failed, errors, total: input.admins.length };
      }),


    // 获取用户活动日志列表
    getUserActivityLogs: adminProcedure
      .input(z.object({
        userId: z.number().optional(),
        userRole: z.string().optional(),
        action: z.string().optional(),
        module: z.string().optional(),
        keyword: z.string().optional(),
        startDate: z.string().optional(),
        endDate: z.string().optional(),
        result: z.string().optional(),
        limit: z.number().optional(),
        offset: z.number().optional(),
      }).optional())
      .query(async ({ input }) => {
        return db.getUserActivityLogs(input);
      }),

    // 获取用户活动日志统计
    getUserActivityLogStats: adminProcedure.query(async () => {
      return db.getUserActivityLogStats();
    }),

    // 修改管理员初始密码
    updateAdminPassword: adminProcedure
      .input(z.object({
        adminId: z.number(),
        newPassword: z.string().min(1),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.updateAdminInitialPassword(input.adminId, input.newPassword);
        if (result.success) {
        }
        return result;
      }),

    updateTeacherQuota: adminProcedure
      .input(z.object({
        userId: z.number(),
        quota: z.number(),
      }))
      .mutation(async ({ input }) => {
        return db.updateUser(input.userId, { annualQuota: input.quota });
      }),

    // 切换导师发布权限
    toggleTeacherPublish: adminProcedure
      .input(z.object({
        teacherId: z.number(),
        canPublish: z.boolean(),
      }))
      .mutation(async ({ input }) => {
        return db.toggleTeacherPublishPermission(input.teacherId, input.canPublish);
      }),

    // 批量修改导师发布权限
    batchUpdatePublishPermission: adminProcedure
      .input(z.object({
        teacherIds: z.array(z.number()),
        canPublish: z.boolean(),
      }))
      .mutation(async ({ input }) => {
        let success = 0;
        let failed = 0;
        for (const teacherId of input.teacherIds) {
          try {
            await db.toggleTeacherPublishPermission(teacherId, input.canPublish);
            success++;
          } catch (error) {
            failed++;
          }
        }
        return { success, failed, total: input.teacherIds.length };
      }),

    // 批量修改导师年度课题限额
    batchUpdateQuota: adminProcedure
      .input(z.object({
        teacherIds: z.array(z.number()),
        quota: z.number().min(0),
      }))
      .mutation(async ({ input }) => {
        let success = 0;
        let failed = 0;
        for (const teacherId of input.teacherIds) {
          try {
            await db.updateUser(teacherId, { annualQuota: input.quota });
            success++;
          } catch (error) {
            failed++;
          }
        }
        return { success, failed, total: input.teacherIds.length };
      }),

    // 重置用户密码到初始密码
    resetUserPassword: adminProcedure
      .input(z.object({ userId: z.number() }))
      .mutation(async ({ input }) => {
        const user = await db.getUserById(input.userId);
        if (!user) {
          throw new TRPCError({ code: "NOT_FOUND", message: "用户不存在" });
        }
        const result = await db.resetUserPassword(input.userId);
        if (!result.success) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "重置密码失败" });
        }
        return { success: true, newPassword: result.initialPassword, userName: user.name || user.email };
      }),

    getConfig: adminProcedure.query(async () => {
      const configs = await db.getAllConfigs();
      const result: Record<string, string> = {};
      configs.forEach(c => { result[c.configKey] = c.configValue; });
      return {
        currentYear: result.currentAcademicYear || new Date().getFullYear().toString(),
        topicDeadline: result.topicDeadline || "",
        wishDeadline: result.wishDeadline || "",
        teacherSelectionDays: result.teacherSelectionDays || "2",
        maxWishesNormal: result.maxWishesNormal || "5",
        maxWishesTransfer: result.maxWishesTransfer || "8",
        statementRequired: result.statementRequired || "false",
      };
    }),

    saveConfig: adminProcedure
      .input(z.object({
        currentYear: z.string(),
        topicDeadline: z.string(),
        wishDeadline: z.string(),
        teacherSelectionDays: z.string(),
        maxWishesNormal: z.string(),
        maxWishesTransfer: z.string(),
        statementRequired: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        await db.setConfig("currentAcademicYear", input.currentYear);
        await db.setConfig("topicDeadline", input.topicDeadline);
        await db.setConfig("wishDeadline", input.wishDeadline);
        await db.setConfig("teacherSelectionDays", input.teacherSelectionDays);
        await db.setConfig("maxWishesNormal", input.maxWishesNormal);
        await db.setConfig("maxWishesTransfer", input.maxWishesTransfer);
        if (input.statementRequired !== undefined) {
          await db.setConfig("statementRequired", input.statementRequired);
        }
        return { success: true };
      }),

    getConfigs: adminProcedure.query(async () => {
      return db.getAllConfigs();
    }),

    setConfig: adminProcedure
      .input(z.object({
        key: z.string(),
        value: z.string(),
        description: z.string().optional(),
      }))
      .mutation(async ({ input }) => {
        const result = await db.setConfig(input.key, input.value, input.description);
        
        // 当修改名额配置时，自动检查并触发相应处理
        if (input.key === "chineseTeacherTotalQuota") {
          const quotaStats = await db.getChineseTeacherQuotaStats();
          
          if (quotaStats.quotaEnabled && quotaStats.isQuotaFull) {
            // 名额已满，触发满额自动处理
            const autoResult = await db.handleChineseTeacherQuotaFull();
            console.log("[QuotaConfig] 名额配置变更触发满额处理:", autoResult.message);
            return { success: true, autoHandled: true, message: autoResult.message };
          }
          
          // 检查是否进入分流优先模式
          const priorityMode = await db.checkTransferStudentPriorityMode();
          if (priorityMode.isActive) {
            const batchResult = await db.batchRejectNonTransferStudentWishes();
            if (batchResult.rejectedCount > 0) {
              console.log("[QuotaConfig] 名额配置变更触发分流优先模式自动拒绝:", batchResult.message);
              return { success: true, autoHandled: true, message: batchResult.message };
            }
          }
        }
        
        return result;
      }),

    // 获取所有匹配结果
    getAllMatches: adminProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const matches = await db.getAllMatches(academicYear);
      
      const results = await Promise.all(matches.map(async m => {
        const student = await db.getUserById(m.studentId);
        const teacher = await db.getUserById(m.teacherId);
        const topic = await db.getTopicById(m.topicId);
        return {
          ...m,
          student: student ? { 
            id: student.id, 
            name: student.name, 
            email: student.email,
            studentId: student.studentId,
            sussexId: student.sussexId,
            candidateNo: student.candidateNo,
            studentClass: student.studentClass,
            studentMajor: student.studentMajor,
            faculty: student.faculty,
          } : null,
          teacher: teacher ? { id: teacher.id, name: teacher.name, email: teacher.email } : null,
          topic: topic ? { 
            id: topic.id, 
            title: topic.title,
            titleEn: topic.titleEn,
            keywords: topic.keywords,
            researchFocus: topic.researchFocus,
            thesisType: topic.thesisType,
            topicSource: topic.topicSource,
            topicLanguage: topic.topicLanguage,
          } : null,
        };
      }));
      
      return results;
    }),

    // 导出匹配结果（Excel格式数据）- 完整导出所有信息
    exportMatches: adminProcedure
      .mutation(async () => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        
        // 获取完整的导出数据
        const exportData = await db.getExportData(academicYear);
        
        // 按照模板格式生成Excel
        // 列名参考: 序号, 学院 Faculty, 专业 Major, 学生班级 Class, 导师姓名 Supervisor, 
        // 学生中方学号 Student ID, 英方学号 Candidate No., 学生姓名 Name,
        // 论文类型 Thesis Type, 论文题目 Dissertation Title, 论文关键词 Keywords,
        // 论文选题来源, 论文研究方向 Research Focus, 论文撰写语种 Language, 成绩, 备注
        const headers = [
          "序号",
          "学院 Faculty",
          "专业 Major",
          "学生班级 Class",
          "导师姓名 Supervisor",
          "学生中方学号 Student ID",
          "英方学号 Candidate No.",
          "学生姓名 Name",
          "论文类型 Thesis Type",
          "论文题目 Dissertation Title",
          "论文关键词 Keywords",
          "论文选题来源",
          "论文研究方向 Research Focus",
          "论文撰写语种 Language",
          "成绩",
          "备注"
        ];
        
        const rows = exportData.map((item: any) => [
          item.序号 || "",
          item.学院 || "",
          item.专业 || "",
          item.学生班级 || "",
          item.导师姓名 || "",
          item.学生中方学号 || "",
          item.英方学号 || "",
          item.学生姓名 || "",
          item.论文类型 || "",
          item.论文题目 || "",
          item.论文关键词 || "",
          item.论文选题来源 || "",
          item.论文研究方向 || "",
          item.论文撰写语种 || "",
          item.成绩 || "",
          item.备注 || ""
        ]);
        
        // 使用Excel XML格式
        const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
<Worksheet ss:Name="匹配结果">
<Table>
<Row>${headers.map(h => `<Cell><Data ss:Type="String">${h}</Data></Cell>`).join("")}</Row>
${rows.map(row => `<Row>${row.map(cell => `<Cell><Data ss:Type="String">${String(cell).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</Data></Cell>`).join("")}</Row>`).join("\n")}
</Table>
</Worksheet>
</Workbook>`;
        
        const base64 = Buffer.from(xmlContent, "utf-8").toString("base64");
        return { base64, filename: `毕业论文选题匹配结果_${academicYear}.xls` };
      }),

    // AI填充缺失字段
    fillMissingFields: adminProcedure
      .input(z.object({
        matchId: z.number(),
        fields: z.array(z.enum(["keywords", "researchFocus"])),
      }))
      .mutation(async ({ input }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const matches = await db.getAllMatches(academicYear);
        const match = matches.find(m => m.id === input.matchId);
        
        if (!match) {
          throw new TRPCError({ code: "NOT_FOUND", message: "匹配记录不存在" });
        }
        
        const topic = await db.getTopicById(match.topicId);
        if (!topic) {
          throw new TRPCError({ code: "NOT_FOUND", message: "课题不存在" });
        }
        
        const updates: any = {};
        
        if (input.fields.includes("keywords") && !topic.keywords) {
          updates.keywords = await generateKeywords(topic.title);
        }
        
        if (input.fields.includes("researchFocus") && !topic.researchFocus) {
          updates.researchFocus = await generateResearchFocus(topic.title);
        }
        
        if (Object.keys(updates).length > 0) {
          await db.updateTopic(topic.id, updates);
        }
        
        return { success: true, updates };
      }),

    // 批量AI填充所有缺失字段
    fillAllMissingFields: adminProcedure.mutation(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const matches = await db.getAllMatches(academicYear);
      
      let filledCount = 0;
      
      for (const match of matches) {
        const topic = await db.getTopicById(match.topicId);
        if (!topic) continue;
        
        const updates: any = {};
        
        if (!topic.keywords) {
          updates.keywords = await generateKeywords(topic.title);
        }
        
        if (!topic.researchFocus) {
          updates.researchFocus = await generateResearchFocus(topic.title);
        }
        
        if (Object.keys(updates).length > 0) {
          await db.updateTopic(topic.id, updates);
          filledCount++;
        }
      }
      
      return { success: true, filledCount };
    }),

    // 撤回匹配结果
    revokeMatch: adminProcedure
      .input(z.object({ matchId: z.number() }))
      .mutation(async ({ input }) => {
        const result = await db.revokeMatch(input.matchId);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.message });
        }
        return result;
      }),

    // ==================== 匹配结果导入 ====================

    // 单个添加匹配结果
    importSingleMatch: adminProcedure
      .input(z.object({
        studentId: z.string().min(1, "学号不能为空"),
        studentName: z.string().min(1, "学生姓名不能为空"),
        sussexId: z.string().optional(),
        teacherName: z.string().min(1, "导师姓名不能为空"),
        topicTitle: z.string().min(1, "课题标题不能为空"),
        remarks: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const result = await db.importSingleMatch({
          ...input,
          academicYear,
        });
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.message });
        }
        // 记录用户活动日志
        await db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || "管理员",
          userRole: "admin",
          action: "导入匹配结果",
          module: "匹配管理",
          description: `单个导入：${input.studentName}(${input.studentId}) - ${input.teacherName} - ${input.topicTitle}`,
        });
        return result;
      }),

    // 批量导入匹配结果
    batchImportMatches: adminProcedure
      .input(z.object({
        items: z.array(z.object({
          studentId: z.string(),
          studentName: z.string(),
          sussexId: z.string().optional(),
          teacherName: z.string(),
          topicTitle: z.string(),
          remarks: z.string().optional(),
        })),
      }))
      .mutation(async ({ input, ctx }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const result = await db.batchImportMatches(input.items, academicYear);
        // 记录用户活动日志
        await db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || "管理员",
          userRole: "admin",
          action: "批量导入匹配结果",
          module: "匹配管理",
          description: `批量导入 ${input.items.length} 条，成功 ${result.successCount} 条，失败 ${result.failedCount} 条`,
        });
        return result;
      }),

    // 下载导入模板
    getImportTemplate: adminProcedure.query(async () => {
      return {
        headers: ["序号", "学生姓名", "中方学号", "英方学号", "论文题目", "导师", "备注"],
        sampleData: [
          ["1", "张三", "2037010101", "24001234", "基于深度学习的图像分类研究", "李教授", ""],
          ["2", "李四", "2037010102", "24001235", "自然语言处理在情感分析中的应用", "王教授", "分流学生"],
        ],
      };
    }),

    // ==================== 时间配置功能 ====================
    
    // 获取时间配置
    getTimeConfig: adminProcedure.query(async () => {
      const timePhase = await db.checkTimePhase();
      // 直接从数据库读取原始时间字符串，避免 Date 对象的时区转换问题
      const topicPublishStartConfig = await db.getConfig("topicPublishStart");
      const topicPublishEndConfig = await db.getConfig("topicPublishEnd");
      const studentSelectionStartConfig = await db.getConfig("studentSelectionStart");
      const studentSelectionEndConfig = await db.getConfig("studentSelectionEnd");
      const teacherConfirmStartConfig = await db.getConfig("teacherConfirmStart");
      const teacherConfirmEndConfig = await db.getConfig("teacherConfirmEnd");
      const thesisUploadStartConfig = await db.getConfig("thesisUploadStart");
      const thesisUploadEndConfig = await db.getConfig("thesisUploadEnd");
      const scoringStartConfig = await db.getConfig("scoringStart");
      const scoringEndConfig = await db.getConfig("scoringEnd");
      return {
        phase: timePhase.phase,
        topicPublishStart: topicPublishStartConfig || "",
        topicPublishEnd: topicPublishEndConfig || "",
        studentSelectionStart: studentSelectionStartConfig || "",
        studentSelectionEnd: studentSelectionEndConfig || "",
        teacherConfirmStart: teacherConfirmStartConfig || "",
        teacherConfirmEnd: teacherConfirmEndConfig || "",
        thesisUploadStart: thesisUploadStartConfig || "",
        thesisUploadEnd: thesisUploadEndConfig || "",
        scoringStart: scoringStartConfig || "",
        scoringEnd: scoringEndConfig || "",
      };
    }),

    // 保存时间配置
    saveTimeConfig: adminProcedure
      .input(z.object({
        topicPublishStart: z.string().optional(),
        topicPublishEnd: z.string().optional(),
        studentSelectionStart: z.string(),
        studentSelectionEnd: z.string(),
        teacherConfirmStart: z.string(),
        teacherConfirmEnd: z.string(),
        thesisUploadStart: z.string().optional(),
        thesisUploadEnd: z.string().optional(),
        scoringStart: z.string().optional(),
        scoringEnd: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 验证时间配置
        const validation = await db.validateTimeConfig(
          input.studentSelectionStart,
          input.studentSelectionEnd,
          input.teacherConfirmStart,
          input.teacherConfirmEnd,
          input.topicPublishStart,
          input.topicPublishEnd
        );
        
        if (!validation.valid) {
          throw new TRPCError({ code: "BAD_REQUEST", message: validation.message });
        }
        
        // 验证论文上传和评分时间段
        if (input.thesisUploadStart && input.thesisUploadEnd && input.scoringStart && input.scoringEnd) {
          const uploadStart = new Date(input.thesisUploadStart);
          const uploadEnd = new Date(input.thesisUploadEnd);
          const scoringStart = new Date(input.scoringStart);
          const scoringEnd = new Date(input.scoringEnd);
          const confirmEnd = new Date(input.teacherConfirmEnd);
          
          if (uploadStart < confirmEnd) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "学生上传论文开始时间必须在导师确认截止时间之后" });
          }
          if (uploadEnd <= uploadStart) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "学生上传论文截止时间必须在开始时间之后" });
          }
          if (scoringStart < uploadEnd) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "导师评分开始时间必须在学生上传论文截止时间之后" });
          }
          if (scoringEnd <= scoringStart) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "导师评分截止时间必须在开始时间之后" });
          }
        }
        
        // 保存配置
        if (input.topicPublishStart) await db.setConfig("topicPublishStart", input.topicPublishStart, "导师发布题目开始时间");
        if (input.topicPublishEnd) await db.setConfig("topicPublishEnd", input.topicPublishEnd, "导师发布题目截止时间");
        await db.setConfig("studentSelectionStart", input.studentSelectionStart, "学生选题开始时间");
        await db.setConfig("studentSelectionEnd", input.studentSelectionEnd, "学生选题截止时间");
        await db.setConfig("teacherConfirmStart", input.teacherConfirmStart, "导师确认开始时间");
        await db.setConfig("teacherConfirmEnd", input.teacherConfirmEnd, "导师确认截止时间");
        if (input.thesisUploadStart) await db.setConfig("thesisUploadStart", input.thesisUploadStart, "学生上传论文开始时间");
        if (input.thesisUploadEnd) await db.setConfig("thesisUploadEnd", input.thesisUploadEnd, "学生上传论文截止时间");
        if (input.scoringStart) await db.setConfig("scoringStart", input.scoringStart, "导师评分开始时间");
        if (input.scoringEnd) await db.setConfig("scoringEnd", input.scoringEnd, "导师评分截止时间");

        // 记录配置修改日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'admin',
          action: 'update_config',
          module: 'config',
          targetType: 'time_config',
          description: '修改了系统时间配置',
        });
        
        return { success: true };
      }),

    // ==================== 数据统计与监控 ====================
    
    // 获取学生选题统计
    getSelectionStats: adminProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      return db.getStudentSelectionStats(academicYear);
    }),

    // 获取未选择志愿的学生列表
    getUnselectedStudents: adminProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const students = await db.getUnselectedStudents(academicYear);
      return students.map(s => ({
        id: s.id,
        name: s.name || "",
        email: s.email,
        studentId: s.studentId || "", // 中方学号
        sussexId: s.sussexId || s.candidateNo || "", // 萨塞克斯学号
        sussexEmail: s.sussexEmail || "", // 萨塞克斯邮箱
        candidateNo: s.candidateNo || "",
        studentClass: s.studentClass || "",
        studentMajor: s.studentMajor,
        faculty: s.faculty || "萨塞克斯人工智能学院",
      }));
    }),

    // 导出未选择志愿的学生名单（Excel格式）
    exportUnselectedStudents: adminProcedure.mutation(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const students = await db.getUnselectedStudents(academicYear);
      
      const headers = [
        "序号",
        "中方学号",
        "萨塞克斯学号",
        "姓名",
        "萨塞克斯邮箱",
        "专业",
        "班级",
        "学院"
      ];
      
      const rows = students.map((s, index) => [
        index + 1,
        s.studentId || "",
        s.sussexId || s.candidateNo || "",
        s.name || "",
        s.sussexEmail || s.email,
        s.studentMajor === "electronic_info" ? "电子信息工程（中外合作办学）" : "通信工程（中外合作办学）",
        s.studentClass || "",
        s.faculty || "萨塞克斯人工智能学院"
      ]);
      
      const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
<Worksheet ss:Name="未选题学生名单">
<Table>
<Row>${headers.map(h => `<Cell><Data ss:Type="String">${h}</Data></Cell>`).join("")}</Row>
${rows.map(row => `<Row>${row.map(cell => `<Cell><Data ss:Type="String">${String(cell).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</Data></Cell>`).join("")}</Row>`).join("\n")}
</Table>
</Worksheet>
</Workbook>`;
      
      const base64 = Buffer.from(xmlContent, "utf-8").toString("base64");
      return { base64, filename: `未选题学生名单_${academicYear}.xls` };
    }),

    // 获取当前时间阶段（公开接口，用于前端显示）
    getCurrentPhase: protectedProcedure.query(async () => {
      const timePhase = await db.checkTimePhase();
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const currentReviewPriority = await db.getCurrentReviewPriority(academicYear);
      // 直接从数据库读取原始时间字符串，避免 Date 对象的时区转换问题
      const topicPublishStartConfig = await db.getConfig("topicPublishStart");
      const topicPublishEndConfig = await db.getConfig("topicPublishEnd");
      const studentSelectionStartConfig = await db.getConfig("studentSelectionStart");
      const studentSelectionEndConfig = await db.getConfig("studentSelectionEnd");
      const teacherConfirmStartConfig = await db.getConfig("teacherConfirmStart");
      const teacherConfirmEndConfig = await db.getConfig("teacherConfirmEnd");
      const thesisUploadStart = await db.getConfig("thesisUploadStart");
      const thesisUploadEnd = await db.getConfig("thesisUploadEnd");
      const scoringStart = await db.getConfig("scoringStart");
      const scoringEnd = await db.getConfig("scoringEnd");
      
      // 判断扩展阶段
      const now = new Date();
      let extendedPhase = timePhase.phase as string;
      if (timePhase.phase === "closed" || timePhase.phase === "none") {
        if (thesisUploadStart && thesisUploadEnd) {
          const uploadStart = new Date(thesisUploadStart);
          const uploadEnd = new Date(thesisUploadEnd);
          if (now >= uploadStart && now <= uploadEnd) {
            extendedPhase = "thesis_upload";
          }
        }
        if (scoringStart && scoringEnd) {
          const sStart = new Date(scoringStart);
          const sEnd = new Date(scoringEnd);
          if (now >= sStart && now <= sEnd) {
            extendedPhase = "scoring";
          }
        }
      }
      
      return {
        phase: timePhase.phase,
        extendedPhase,
        currentReviewPriority,
        topicPublishStart: topicPublishStartConfig || null,
        topicPublishEnd: topicPublishEndConfig || null,
        studentSelectionStart: studentSelectionStartConfig || null,
        studentSelectionEnd: studentSelectionEndConfig || null,
        teacherConfirmStart: teacherConfirmStartConfig || null,
        teacherConfirmEnd: teacherConfirmEndConfig || null,
        thesisUploadStart: thesisUploadStart || null,
        thesisUploadEnd: thesisUploadEnd || null,
        scoringStart: scoringStart || null,
        scoringEnd: scoringEnd || null,
      };
    }),

    // ==================== 题库管理功能 ====================
    
    // 获取题库列表
    getTopicLibrary: adminProcedure
      .input(z.object({
        status: z.enum(["published", "used", "withdrawn", "all"]).optional(),
        academicYear: z.string().optional(),
        teacherId: z.number().optional(),
        searchTerm: z.string().optional(),
        dateFrom: z.string().optional(),
        dateTo: z.string().optional(),
        page: z.number().optional(),
        pageSize: z.number().optional(),
      }))
      .query(async ({ input }) => {
        return db.getTopicLibraryList(input);
      }),
    
    // 获取题库统计信息
    getTopicLibraryStats: adminProcedure.query(async () => {
      return db.getTopicLibraryStats();
    }),
    
    // 删除题库记录
    deleteTopicLibraryItem: adminProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        const success = await db.deleteFromTopicLibrary(input.id);
        if (!success) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "删除失败" });
        }
        return { success: true };
      }),
    
    // 批量删除题库记录
    batchDeleteTopicLibrary: adminProcedure
      .input(z.object({ ids: z.array(z.number()) }))
      .mutation(async ({ input }) => {
        const success = await db.batchDeleteFromTopicLibrary(input.ids);
        if (!success) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "批量删除失败" });
        }
        return { success: true };
      }),
    
    // 清理三年前的题库记录
    cleanupOldTopicLibrary: adminProcedure.mutation(async () => {
      const deletedCount = await db.cleanupOldTopicLibrary();
      return { success: true, deletedCount };
    }),
    
    // 检查课题标题是否在题库中存在
    checkTopicTitleInLibrary: adminProcedure
      .input(z.object({ title: z.string(), excludeTopicId: z.number().optional() }))
      .query(async ({ input }) => {
        return db.checkTopicTitleInLibrary(input.title, input.excludeTopicId);
      }),

    // 管理员手动添加题库课题（单个）
    adminAddTopicLibraryItem: adminProcedure
      .input(z.object({
        title: z.string().min(1, "课题标题不能为空"),
        titleEn: z.string().optional().default(""),
        teacherName: z.string().optional().default(""),
        description: z.string().optional().default(""),
        academicYear: z.string().optional(),
        publishedAt: z.string().optional(), // 发布时间，不填则默认为当前时间
      }))
      .mutation(async ({ input }) => {
        return db.adminAddTopicLibraryItem(input);
      }),

    // 管理员批量导入题库课题
    adminBulkImportTopicLibrary: adminProcedure
      .input(z.object({
        items: z.array(z.object({
          title: z.string().min(1),
          titleEn: z.string().optional().default(""),
          teacherName: z.string().optional().default(""),
          description: z.string().optional().default(""),
          academicYear: z.string().optional(),
          publishedAt: z.string().optional(),
        })),
      }))
      .mutation(async ({ input }) => {
        return db.adminBulkImportTopicLibrary(input.items);
      }),

    // ==================== 年度管理功能 ====================
    
    // 获取所有学年
    getAllYears: adminProcedure.query(async () => {
      return db.getAllAcademicYears();
    }),

    // 获取当前活跃学年
    getCurrentYear: protectedProcedure.query(async () => {
      return db.getCurrentAcademicYear();
    }),

    // 创建新学年（简化版，移除志愿数配置）
    createYear: adminProcedure
      .input(z.object({
        yearName: z.string(),
        displayName: z.string().optional(),
        chineseTeacherQuota: z.number().optional(), // 中方导师年度发布限额
      }))
      .mutation(async ({ input }) => {
        const existing = await db.getAcademicYearByName(input.yearName);
        if (existing) {
          throw new TRPCError({ code: "CONFLICT", message: "该学年已存在" });
        }
        return db.createAcademicYear({
          yearName: input.yearName,
          displayName: input.displayName || input.yearName,
          chineseTeacherQuota: input.chineseTeacherQuota || 5,
          status: "draft",
        });
      }),

    // 更新学年配置（简化版，移除志愿数配置）
    updateYear: adminProcedure
      .input(z.object({
        id: z.number(),
        displayName: z.string().optional(),
        studentSelectionStart: z.string().optional(),
        studentSelectionEnd: z.string().optional(),
        teacherConfirmStart: z.string().optional(),
        teacherConfirmEnd: z.string().optional(),
        thesisUploadStart: z.string().optional(), // 学生上传论文开始时间
        thesisUploadEnd: z.string().optional(), // 学生上传论文截止时间
        scoringStart: z.string().optional(), // 导师评分开始时间
        scoringEnd: z.string().optional(), // 导师评分截止时间
        chineseTeacherQuota: z.number().optional(), // 中方导师年度发布限额
      }))
      .mutation(async ({ input }) => {
        const { id, ...data } = input;
        const year = await db.getAcademicYearById(id);
        if (!year) {
          throw new TRPCError({ code: "NOT_FOUND", message: "学年不存在" });
        }
        
        // 验证时间配置
        if (data.studentSelectionStart && data.studentSelectionEnd && 
            data.teacherConfirmStart && data.teacherConfirmEnd) {
          const validation = await db.validateTimeConfig(
            data.studentSelectionStart,
            data.studentSelectionEnd,
            data.teacherConfirmStart,
            data.teacherConfirmEnd
          );
          if (!validation.valid) {
            throw new TRPCError({ code: "BAD_REQUEST", message: validation.message });
          }
        }
        
        // 验证论文上传和评分时间段
        if (data.thesisUploadStart && data.thesisUploadEnd && data.scoringStart && data.scoringEnd) {
          const uploadStart = new Date(data.thesisUploadStart);
          const uploadEnd = new Date(data.thesisUploadEnd);
          const scoringStart = new Date(data.scoringStart);
          const scoringEnd = new Date(data.scoringEnd);
          const confirmEnd = data.teacherConfirmEnd ? new Date(data.teacherConfirmEnd) : (year.teacherConfirmEnd ? new Date(year.teacherConfirmEnd) : null);
          
          // 学生上传论文开始时间必须在导师确认截止时间之后
          if (confirmEnd && uploadStart < confirmEnd) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "学生上传论文开始时间必须在导师确认截止时间之后" });
          }
          // 学生上传论文截止时间必须在开始时间之后
          if (uploadEnd <= uploadStart) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "学生上传论文截止时间必须在开始时间之后" });
          }
          // 导师评分开始时间必须在学生上传论文截止时间之后
          if (scoringStart < uploadEnd) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "导师评分开始时间必须在学生上传论文截止时间之后" });
          }
          // 导师评分截止时间必须在开始时间之后
          if (scoringEnd <= scoringStart) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "导师评分截止时间必须在开始时间之后" });
          }
        }
        
        const updateData: any = {};
        if (data.displayName) updateData.displayName = data.displayName;
        if (data.studentSelectionStart) updateData.studentSelectionStart = new Date(data.studentSelectionStart);
        if (data.studentSelectionEnd) updateData.studentSelectionEnd = new Date(data.studentSelectionEnd);
        if (data.teacherConfirmStart) updateData.teacherConfirmStart = new Date(data.teacherConfirmStart);
        if (data.teacherConfirmEnd) updateData.teacherConfirmEnd = new Date(data.teacherConfirmEnd);
        if (data.thesisUploadStart) updateData.thesisUploadStart = new Date(data.thesisUploadStart);
        if (data.thesisUploadEnd) updateData.thesisUploadEnd = new Date(data.thesisUploadEnd);
        if (data.scoringStart) updateData.scoringStart = new Date(data.scoringStart);
        if (data.scoringEnd) updateData.scoringEnd = new Date(data.scoringEnd);
        if (data.chineseTeacherQuota !== undefined) updateData.chineseTeacherQuota = data.chineseTeacherQuota;
        
        return db.updateAcademicYear(id, updateData);
      }),

    // 设置当前活跃学年
    setCurrentYear: adminProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        const year = await db.getAcademicYearById(input.id);
        if (!year) {
          throw new TRPCError({ code: "NOT_FOUND", message: "学年不存在" });
        }
        await db.setCurrentAcademicYear(input.id);
        // 同步更新系统配置
        await db.setConfig("currentAcademicYear", year.yearName);
        return { success: true };
      }),

    // 删除学年（替代归档）
    deleteYear: adminProcedure
      .input(z.object({ id: z.number() }))
      .mutation(async ({ input }) => {
        const year = await db.getAcademicYearById(input.id);
        if (!year) {
          throw new TRPCError({ code: "NOT_FOUND", message: "学年不存在" });
        }
        if (year.isCurrentYear) {
          throw new TRPCError({ code: "FORBIDDEN", message: "当前活跃学年不可删除，请先设置其他学年为当前学年" });
        }
        return db.deleteAcademicYear(input.id);
      }),

    // 从历史年度复制课题模板
    copyTopicsFromYear: adminProcedure
      .input(z.object({
        sourceYearName: z.string(),
        targetYearName: z.string(),
        teacherId: z.number().optional(),
      }))
      .mutation(async ({ input }) => {
        const count = await db.copyTopicsFromYear(
          input.sourceYearName,
          input.targetYearName,
          input.teacherId
        );
        return { success: true, copiedCount: count };
      }),

    // ==================== 志愿轮次匹配功能 ====================
    
    // 获取当前审核轮次
    getCurrentReviewPriority: adminProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const priority = await db.getCurrentReviewPriority(academicYear);
      return { priority, academicYear };
    }),

    // 获取指定轮次的待审核志愿
    getPendingWishesByPriority: adminProcedure
      .input(z.object({ priority: z.number() }))
      .query(async ({ input }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const wishes = await db.getPendingWishesByPriority(input.priority, academicYear);
        
        const results = await Promise.all(wishes.map(async w => {
          const student = await db.getUserById(w.studentId);
          const topic = await db.getTopicById(w.topicId);
          const teacher = topic ? await db.getUserById(topic.teacherId) : null;
          return {
            ...w,
            student: student ? { id: student.id, name: student.name, studentId: student.studentId } : null,
            topic: topic ? { id: topic.id, title: topic.title, titleEn: topic.titleEn, keywords: topic.keywords, researchFocus: topic.researchFocus } : null,
            teacher: teacher ? { id: teacher.id, name: teacher.name } : null,
          };
        }));
        
        return results;
      }),

    // 逾期自动分配
    autoAssignOverdueWishes: adminProcedure
      .input(z.object({ overdueDays: z.number().optional() }))
      .mutation(async ({ input }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const overdueDays = input.overdueDays || 1;
        const result = await db.autoAssignOverdueWishes(academicYear, overdueDays);
        return result;
      }),

    // ==================== 导师审核状态分类 ====================
    
    // 获取所有导师审核状态
    getTeacherReviewStatuses: adminProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      return db.getTeacherReviewStatuses(academicYear);
    }),

    // 获取未完成审核的导师列表
    getIncompleteReviewTeachers: adminProcedure.query(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      return db.getIncompleteReviewTeachers(academicYear);
    }),

    // 导出未完成审核导师名单
    exportIncompleteReviewTeachers: adminProcedure.mutation(async () => {
      const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
      const teachers = await db.getIncompleteReviewTeachers(academicYear);
      
      const headers = [
        "序号",
        "导师姓名",
        "邮箱",
        "导师类型",
        "审核状态",
        "待审核数",
        "已同意数",
        "已拒绝数",
        "总申请数"
      ];
      
      const statusMap: Record<string, string> = {
        "partial": "部分完成",
        "not_started": "未开始审核",
        "completed": "已完成",
        "no_students": "无学生申请"
      };
      
      const rows = teachers.map((t, index) => [
        index + 1,
        t.teacherName,
        t.teacherEmail,
        t.teacherType === "chinese" ? "中方导师" : t.teacherType === "british" ? "英方导师" : "未设置",
        statusMap[t.status] || t.status,
        t.totalPending,
        t.totalApproved,
        t.totalRejected,
        t.totalStudents
      ]);
      
      const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
 xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
<Worksheet ss:Name="未完成审核导师">
<Table>
<Row>${headers.map(h => `<Cell><Data ss:Type="String">${h}</Data></Cell>`).join("")}</Row>
${rows.map(row => `<Row>${row.map(cell => `<Cell><Data ss:Type="String">${String(cell).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")}</Data></Cell>`).join("")}</Row>`).join("\n")}
</Table>
</Worksheet>
</Workbook>`;
      
      const base64 = Buffer.from(xmlContent, "utf-8").toString("base64");
      return { base64, filename: `未完成审核导师名单_${academicYear}.xls` };
    }),

    // ==================== 历史数据查询 ====================
    
    // 按年度获取匹配结果
    getMatchesByYear: adminProcedure
      .input(z.object({ academicYear: z.string() }))
      .query(async ({ input }) => {
        const matches = await db.getMatchesByYear(input.academicYear);
        const results = await Promise.all(matches.map(async m => {
          const student = await db.getUserById(m.studentId);
          const teacher = await db.getUserById(m.teacherId);
          const topic = await db.getTopicById(m.topicId);
          return {
            ...m,
            student: student ? { 
              id: student.id, 
              name: student.name, 
              email: student.email,
              studentId: student.studentId,
              candidateNo: student.candidateNo,
              studentClass: student.studentClass,
              studentMajor: student.studentMajor,
              faculty: student.faculty,
            } : null,
            teacher: teacher ? { id: teacher.id, name: teacher.name, email: teacher.email } : null,
            topic: topic ? { 
              id: topic.id, 
              title: topic.title,
              keywords: topic.keywords,
              researchFocus: topic.researchFocus,
            } : null,
          };
        }));
        return results;
      }),

    // 多维度筛选匹配结果
    getMatchesByFilters: adminProcedure
      .input(z.object({
        academicYear: z.string().optional(),
        faculty: z.string().optional(),
        studentMajor: z.string().optional(),
        teacherId: z.number().optional(),
      }))
      .query(async ({ input }) => {
        return db.getMatchesByFilters(input);
      }),

    // 导师查看历年指导记录
    getTeacherHistory: teacherProcedure
      .input(z.object({ teacherId: z.number().optional() }))
      .query(async ({ input, ctx }) => {
        const teacherId = input.teacherId || ctx.user.id;
        return db.getTeacherHistoryMatches(teacherId);
      }),

    // 管理员代理导入课题（为导师批量创建课题）
    proxyBulkImport: adminProcedure
      .input(z.object({
        topics: z.array(z.object({
          teacherEmail: z.string().min(1, "导师邮箱/登录名不能为空"),
          titleEn: z.string().min(1, "英文标题不能为空"),
          title: z.string().optional().default(""),
          descriptionEn: z.string().min(1, "英文描述不能为空"),
          description: z.string().optional().default(""),
          keywords: z.string().min(1, "关键词不能为空"),
          researchFocus: z.string().min(1, "研究方向不能为空"),
          topicSource: z.string().optional().default("其他"),
          topicLanguage: z.string().optional().default("英语"),
          thesisType: z.string().optional().default("毕业设计"),
          suitableMajor: z.enum(["electronic_info", "communication", "both"]).optional().default("both"),
          requiredSkills: z.string().optional(),
          researchProjectName: z.string().optional(),
        })),
        autoPublish: z.boolean().optional().default(false),
      }))
      .mutation(async ({ input }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        let success = 0;
        let failed = 0;
        const errors: string[] = [];
        
        // 预先缓存导师信息，避免重复查询
        const teacherCache: Record<string, any> = {};
        
        for (let i = 0; i < input.topics.length; i++) {
          const topicData = input.topics[i];
          try {
            // 查找导师
            let teacher = teacherCache[topicData.teacherEmail];
            if (!teacher) {
              teacher = await db.getUserByEmail(topicData.teacherEmail);
              if (teacher) {
                teacherCache[topicData.teacherEmail] = teacher;
              }
            }
            
            if (!teacher) {
              throw new Error(`未找到导师账号"${topicData.teacherEmail}"，请确认该导师已在系统中注册`);
            }
            if (teacher.role !== "teacher" && teacher.role !== "admin") {
              throw new Error(`账号"${topicData.teacherEmail}"不是导师角色，无法为其创建课题`);
            }
            
            // 检查导师发布权限
            if (teacher.canPublish === 0 || teacher.canPublish === false) {
              throw new Error(`导师"${teacher.name || topicData.teacherEmail}"的发布权限已被禁止`);
            }
            
            // 验证：如果选题来源不是"其他"且不是"科研项目（萨塞克斯老师适用）"，则researchProjectName必填
            if (topicData.topicSource !== "其他" && topicData.topicSource !== "科研项目（萨塞克斯老师适用）" && (!topicData.researchProjectName || !topicData.researchProjectName.trim())) {
              throw new Error("选题来源非'其他'时，科研项目名称必填");
            }
            // 验证：如果选题来源是"其他"或"科研项目（萨塞克斯老师适用）"，则researchProjectName必须为空
            if ((topicData.topicSource === "其他" || topicData.topicSource === "科研项目（萨塞克斯老师适用）") && topicData.researchProjectName && topicData.researchProjectName.trim()) {
              throw new Error("选题来源为'其他'或'科研项目（萨塞克斯老师适用）'时，科研项目名称必须为空");
            }
            
            // 当title为空时，使用titleEn填充
            const title = topicData.title && topicData.title.trim() ? topicData.title : topicData.titleEn;
            const description = topicData.description && topicData.description.trim() ? topicData.description : topicData.descriptionEn;
            
            // 检查题库中是否存在相同标题
            const libraryCheck = await db.checkTopicTitleInLibrary(title);
            if (libraryCheck.exists) {
              throw new Error(`课题标题已存在于题库中（${libraryCheck.existingTopic?.academicYear || '未知学年'}）`);
            }
            
            // 创建课题
            const newTopic = await db.createTopic({
              titleEn: topicData.titleEn,
              title,
              descriptionEn: topicData.descriptionEn,
              description,
              keywords: topicData.keywords,
              researchFocus: topicData.researchFocus,
              topicSource: topicData.topicSource,
              topicLanguage: topicData.topicLanguage,
              thesisType: topicData.thesisType,
              suitableMajor: topicData.suitableMajor,
              requiredSkills: topicData.requiredSkills,
              researchProjectName: topicData.researchProjectName,
              teacherId: teacher.id,
              academicYear,
              status: input.autoPublish ? "published" : "draft",
              isCurrentYear: input.autoPublish ? 1 : 0,
            });
            
            // 如果自动发布，还需要添加到题库
            if (input.autoPublish && newTopic) {
              // 检查中方导师限额
              if (teacher.teacherType === "chinese") {
                const publishedCount = await db.getTeacherPublishedTopicCount(teacher.id, academicYear);
                const quota = teacher.annualQuota || 5;
                if (publishedCount > quota) {
                  // 超出限额，回退为草稿
                  await db.updateTopic(newTopic.id, { status: "draft", isCurrentYear: 0 });
                  throw new Error(`导师"${teacher.name || topicData.teacherEmail}"已达到年度发布限额(${quota}个)`);
                }
              }
              await db.addToTopicLibrary(newTopic, teacher.name || '未知导师');
            }
            
            success++;
          } catch (error: any) {
            failed++;
            errors.push(`第${i + 1}行: ${error.message}`);
          }
        }
        
        return { success, failed, errors, total: input.topics.length };
      }),

    // 获取所有导师列表（用于代理导入时的导师匹配）
    getTeacherList: adminProcedure.query(async () => {
      const allUsers = await db.getAllUsers();
      return allUsers
        .filter(u => u.role === "teacher")
        .map(u => ({
          id: u.id,
          name: u.name,
          email: u.email,
          teacherType: u.teacherType,
          canPublish: u.canPublish,
          annualQuota: u.annualQuota,
        }));
    }),
  }),

  // 论文终稿管理
  thesis: router({
    // 学生获取自己的论文终稿信息
    getMyDraft: protectedProcedure.query(async ({ ctx }) => {
      if (ctx.user.role !== "student") {
        throw new TRPCError({ code: "FORBIDDEN", message: "只有学生可以访问此接口" });
      }
      const academicYear = ctx.user.academicYear || await db.getConfig("currentAcademicYear") || "2024-2025";
      const match = await db.getMatchByStudent(ctx.user.id, academicYear);
      if (!match) return null;
      
      const draft = await db.getThesisDraftByMatchId(match.id);
      const topic = await db.getTopicById(match.topicId);
      const teacher = await db.getUserById(match.teacherId);
      
      // 获取宽限期状态
      const gracePeriod = await db.checkThesisGracePeriod();
      
      // 设置上传状态
      let uploadPeriodStatus = "未配置";
      let canUpload = false;
      let uploadStartTime = null;
      let uploadEndTime = null;
      
      const thesisUploadStart = await db.getConfig("thesisUploadStart");
      const thesisUploadEnd = await db.getConfig("thesisUploadEnd");
      
      if (thesisUploadStart && thesisUploadEnd) {
        uploadStartTime = new Date(thesisUploadStart);
        uploadEndTime = new Date(thesisUploadEnd);
        
        switch (gracePeriod.status) {
          case "before_deadline":
            uploadPeriodStatus = "等待中";
            canUpload = false;
            break;
          case "normal":
            uploadPeriodStatus = "进行中";
            canUpload = true;
            break;
          case "grace_24h":
            uploadPeriodStatus = "宽限期-24小时内";
            canUpload = true;
            break;
          case "grace_7d":
            uploadPeriodStatus = "宽限期-7天内";
            canUpload = true;
            break;
          case "closed":
            uploadPeriodStatus = "已关闭";
            canUpload = false;
            break;
          default:
            uploadPeriodStatus = "未配置";
            canUpload = false;
        }
      }
      
      return {
        match,
        topic: topic ? {
          id: topic.id,
          title: topic.title,
          titleEn: topic.titleEn,
        } : null,
        teacher: teacher ? {
          id: teacher.id,
          name: teacher.name,
          email: teacher.email,
        } : null,
        draft,
        uploadPeriodStatus,
        canUpload,
        uploadStartTime,
        uploadEndTime,
        // 宽限期详细信息
        gracePeriod: {
          status: gracePeriod.status,
          penalty: gracePeriod.penalty,
          message: gracePeriod.message,
          graceEndTime: gracePeriod.graceEndTime,
          hoursOverdue: gracePeriod.hoursOverdue,
          daysOverdue: gracePeriod.daysOverdue,
        },
      };
    }),

    // 学生上传论文终稿
    uploadDraft: protectedProcedure
      .input(z.object({
        fileName: z.string(),
        fileKey: z.string(),
        fileUrl: z.string(),
        fileSize: z.number(),
        mimeType: z.string(),
      }))
      .mutation(async ({ input, ctx }) => {
        if (ctx.user.role !== "student") {
          throw new TRPCError({ code: "FORBIDDEN", message: "只有学生可以上传论文" });
        }
        if (ctx.user.studentType !== "transfer") {
          throw new TRPCError({ code: "FORBIDDEN", message: "只有分流学生可以上传论文终稿" });
        }
        
        // 检查宽限期状态
        const gracePeriod = await db.checkThesisGracePeriod();
        
        // 根据宽限期状态检查是否可以上传
        if (!gracePeriod.canUpload) {
          if (gracePeriod.status === "before_deadline") {
            throw new TRPCError({ code: "FORBIDDEN", message: gracePeriod.message });
          } else if (gracePeriod.status === "closed") {
            throw new TRPCError({ code: "FORBIDDEN", message: gracePeriod.message });
          } else if (gracePeriod.status === "not_configured") {
            throw new TRPCError({ code: "FORBIDDEN", message: "论文上传时间段尚未配置" });
          }
        }
        
        const academicYear = ctx.user.academicYear || await db.getConfig("currentAcademicYear") || "2024-2025";
        const match = await db.getMatchByStudent(ctx.user.id, academicYear);
        if (!match) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "您还未匹配课题，无法上传论文" });
        }
        
        // 确定是否为宽限期提交及扣分
        const isLateSubmission = gracePeriod.status === "grace_24h" || gracePeriod.status === "grace_7d";
        const latePenalty = gracePeriod.penalty;
        
        const draft = await db.createThesisDraft({
          studentId: ctx.user.id,
          matchId: match.id,
          fileName: input.fileName,
          fileKey: input.fileKey,
          fileUrl: input.fileUrl,
          fileSize: input.fileSize,
          mimeType: input.mimeType,
          academicYear,
          lateSubmission: isLateSubmission ? 1 : 0,
          latePenalty: latePenalty,
        });

        // 记录论文上传日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'student',
          action: 'upload_thesis',
          module: 'thesis',
          targetType: 'thesis_draft',
          targetName: input.fileName,
          description: `上传论文终稿: ${input.fileName}${isLateSubmission ? `（迟交，扣${latePenalty}分）` : ''}`,
        });
        
        // 返回结果包含宽限期信息
        return {
          ...draft,
          isLateSubmission,
          latePenalty,
          gracePeriodMessage: isLateSubmission 
            ? `论文已在宽限期内提交，将扣除${latePenalty}分` 
            : null,
        };
      }),

    // 获取论文历史版本
    getDraftHistory: protectedProcedure
      .input(z.object({ draftId: z.number() }))
      .query(async ({ input }) => {
        return db.getThesisDraftHistory(input.draftId);
      }),

    // 导师获取学生论文列表
    getStudentDrafts: teacherProcedure
      .input(z.object({ academicYear: z.string().optional() }))
      .query(async ({ input, ctx }) => {
        const academicYear = input.academicYear || await db.getConfig("currentAcademicYear") || "2024-2025";
        return db.getThesisDraftsByTeacherId(ctx.user.id, academicYear);
      }),

    // 管理员获取所有论文终稿
    getAllDrafts: adminProcedure
      .input(z.object({ academicYear: z.string().optional() }))
      .query(async ({ input }) => {
        return db.getAllThesisDrafts(input.academicYear);
      }),

    // 管理员获取分流学生论文提交状态
    getTransferStudentsDraftStatus: adminProcedure
      .input(z.object({ academicYear: z.string().optional() }))
      .query(async ({ input }) => {
        const academicYear = input.academicYear || await db.getConfig("currentAcademicYear") || "2024-2025";
        return db.getTransferStudentsWithDraftStatus(academicYear);
      }),

    // 更新论文状态
    updateDraftStatus: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        status: z.enum(["submitted", "reviewed", "approved"]),
      }))
      .mutation(async ({ input }) => {
        return db.updateThesisDraftStatus(input.draftId, input.status);
      }),

    // 导师为论文打分
    scoreDraft: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        score: z.number().min(0).max(100),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查导师评分时间段
        const scoringStart = await db.getConfig("scoringStart");
        const scoringEnd = await db.getConfig("scoringEnd");
        if (scoringStart && scoringEnd) {
          const now = new Date();
          const start = new Date(scoringStart);
          const end = new Date(scoringEnd);
          if (now < start) {
            throw new TRPCError({ code: "FORBIDDEN", message: `评分尚未开始，开始时间：${start.toLocaleString("zh-CN")}` });
          }
          if (now > end) {
            throw new TRPCError({ code: "FORBIDDEN", message: `评分已截止，截止时间：${end.toLocaleString("zh-CN")}` });
          }
        }
        
        // 验证该论文是否属于该导师的学生
        const draft = await db.getThesisDraftByMatchId(input.draftId);
        if (!draft) {
          // draftId可能是draft的id而不是matchId，先获取draft
          const draftById = await db.getDb().then(async (database) => {
            if (!database) return null;
            const { thesisDrafts } = await import("../drizzle/schema");
            const { eq } = await import("drizzle-orm");
            const result = await database.select().from(thesisDrafts).where(eq(thesisDrafts.id, input.draftId)).limit(1);
            return result.length > 0 ? result[0] : null;
          });
          
          if (!draftById) {
            throw new TRPCError({ code: "NOT_FOUND", message: "论文终稿不存在" });
          }
          
          // 检查该论文是否属于该导师的学生
          const match = await db.getMatchById(draftById.matchId);
          if (!match || match.teacherId !== ctx.user.id) {
            throw new TRPCError({ code: "FORBIDDEN", message: "您没有权限为该论文打分" });
          }
          
          // 检查是否已经打分
          if (draftById.score !== null) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "该论文已经打分，不可更改" });
          }
          
          const result = await db.scoreThesisDraft(input.draftId, input.score, ctx.user.id);
          if (!result.success) {
            throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "打分失败" });
          }
          return { success: true };
        }
        
        // 检查该论文是否属于该导师的学生
        const match = await db.getMatchById(draft.matchId);
        if (!match || match.teacherId !== ctx.user.id) {
          throw new TRPCError({ code: "FORBIDDEN", message: "您没有权限为该论文打分" });
        }
        
        // 检查是否已经打分
        if (draft.score !== null) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "该论文已经打分，不可更改" });
        }
        
        const result = await db.scoreThesisDraft(draft.id, input.score, ctx.user.id);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "打分失败" });
        }
        return { success: true };
      }),
  }),

  // ==================== 第二导师指派路由 ====================
  secondTeacher: router({
    // 获取待指派学生列表
    getStudents: adminProcedure
      .input(z.object({
        search: z.string().optional(),
        firstTeacherId: z.number().optional(),
        academicYear: z.string().optional(),
      }).optional())
      .query(async ({ input }) => {
        return db.getStudentsForSecondTeacherAssignment(input);
      }),

    // 获取导师列表（用于选择第二导师）
    getTeachers: adminProcedure
      .input(z.object({
        excludeTeacherId: z.number().optional(),
      }).optional())
      .query(async ({ input }) => {
        return db.getTeachersForSelection(input?.excludeTeacherId);
      }),

    // 指派第二导师
    assign: adminProcedure
      .input(z.object({
        matchId: z.number(),
        secondTeacherId: z.number(),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.assignSecondTeacher(input.matchId, input.secondTeacherId, ctx.user.id);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "指派失败" });
        }

        // 记录指派第二导师日志
        const secondTeacher = await db.getUserById(input.secondTeacherId);
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'admin',
          action: 'assign_second_teacher',
          module: 'second_teacher',
          targetType: 'match',
          targetId: input.matchId,
          targetName: secondTeacher?.name || `导师ID:${input.secondTeacherId}`,
          description: `为匹配(ID:${input.matchId})指派第二导师: ${secondTeacher?.name || input.secondTeacherId}`,
        });

        return { success: true };
      }),

    // 撤销指派
    revoke: adminProcedure
      .input(z.object({
        matchId: z.number(),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.revokeSecondTeacher(input.matchId, ctx.user.id);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "撤销失败" });
        }
        return { success: true };
      }),

    // 获取指派历史
    getHistory: adminProcedure
      .input(z.object({
        matchId: z.number(),
      }))
      .query(async ({ input }) => {
        return db.getSecondTeacherAssignmentHistory(input.matchId);
      }),

    // 批量指派
    batchAssign: adminProcedure
      .input(z.object({
        assignments: z.array(z.object({
          studentName: z.string(),
          secondTeacherName: z.string(),
        })),
        academicYear: z.string(),
      }))
      .mutation(async ({ input, ctx }) => {
        return db.batchAssignSecondTeacher(input.assignments, ctx.user.id, input.academicYear);
      }),

    // ==================== 论文评审路由 ====================
    
    // 获取第一导师的评审任务列表
    getFirstTeacherReviewTasks: teacherProcedure
      .input(z.object({
        academicYear: z.string().optional(),
      }).optional())
      .query(async ({ ctx, input }) => {
        const tasks = await db.getFirstTeacherReviewTasks(ctx.user.id, input?.academicYear);
        
        // 从systemConfig表获取评分时间段状态
        const scoringStartConfig = await db.getConfig("scoringStart");
        const scoringEndConfig = await db.getConfig("scoringEnd");
        
        let scoringPeriodStatus = {
          isInScoringPeriod: false,
          scoringStart: scoringStartConfig || null,
          scoringEnd: scoringEndConfig || null,
          message: "评分时间段未配置"
        };
        
        if (scoringStartConfig && scoringEndConfig) {
          const now = new Date();
          const scoringStart = new Date(scoringStartConfig);
          const scoringEnd = new Date(scoringEndConfig);
          
          if (now < scoringStart) {
            scoringPeriodStatus.message = `评分时间段尚未开始，开始时间：${scoringStart.toLocaleString('zh-CN')}`;
          } else if (now > scoringEnd) {
            scoringPeriodStatus.message = `评分时间段已结束，结束时间：${scoringEnd.toLocaleString('zh-CN')}`;
          } else {
            scoringPeriodStatus.isInScoringPeriod = true;
            scoringPeriodStatus.message = `当前在评分时间段内，截止时间：${scoringEnd.toLocaleString('zh-CN')}`;
          }
        }
        
        return {
          tasks,
          scoringPeriodStatus
        };
      }),

    // 获取第二导师的评审任务列表（带评分可见性控制）
    getReviewTasks: teacherProcedure
      .input(z.object({
        academicYear: z.string().optional(),
      }).optional())
      .query(async ({ ctx, input }) => {
        const tasks = await db.getSecondTeacherReviewTasksWithVisibility(ctx.user.id, input?.academicYear);
        
        // 从systemConfig表获取评分时间段状态
        const scoringStartConfig = await db.getConfig("scoringStart");
        const scoringEndConfig = await db.getConfig("scoringEnd");
        
        let scoringPeriodStatus = {
          isInScoringPeriod: false,
          scoringStart: scoringStartConfig || null,
          scoringEnd: scoringEndConfig || null,
          message: "评分时间段未配置"
        };
        
        if (scoringStartConfig && scoringEndConfig) {
          const now = new Date();
          const scoringStart = new Date(scoringStartConfig);
          const scoringEnd = new Date(scoringEndConfig);
          
          if (now < scoringStart) {
            scoringPeriodStatus.message = `评分时间段尚未开始，开始时间：${scoringStart.toLocaleString('zh-CN')}`;
          } else if (now > scoringEnd) {
            scoringPeriodStatus.message = `评分时间段已结束，结束时间：${scoringEnd.toLocaleString('zh-CN')}`;
          } else {
            scoringPeriodStatus.isInScoringPeriod = true;
            scoringPeriodStatus.message = `当前在评分时间段内，截止时间：${scoringEnd.toLocaleString('zh-CN')}`;
          }
        }
        
        return {
          tasks,
          scoringPeriodStatus
        };
      }),

    // 第一导师提交评分（支持评语）
    submitFirstTeacherScore: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        score: z.number().min(0).max(100),
        comment: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查评分时间段
        const scoringStartConfig = await db.getConfig("scoringStart");
        const scoringEndConfig = await db.getConfig("scoringEnd");
        if (scoringStartConfig && scoringEndConfig) {
          const now = new Date();
          const scoringStart = new Date(scoringStartConfig);
          const scoringEnd = new Date(scoringEndConfig);
          
          if (now < scoringStart) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "评分时间段尚未开始" });
          }
          if (now > scoringEnd) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "评分时间段已结束" });
          }
        }

        const result = await db.scoreThesisDraftWithComment(input.draftId, input.score, ctx.user.id, input.comment);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "评分失败" });
        }

        // 记录第一导师评分日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'teacher',
          action: 'score_thesis_first',
          module: 'thesis',
          targetType: 'thesis_draft',
          targetId: input.draftId,
          description: `第一导师对论文终稿(ID:${input.draftId})评分: ${input.score}分`,
        });

        return { success: true };
      }),

    // 第二导师提交评分（独立评分，支持评语）
    submitScore: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        score: z.number().min(0).max(100),
        comment: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查评分时间段
        const scoringStartConfig = await db.getConfig("scoringStart");
        const scoringEndConfig = await db.getConfig("scoringEnd");
        if (scoringStartConfig && scoringEndConfig) {
          const now = new Date();
          const scoringStart = new Date(scoringStartConfig);
          const scoringEnd = new Date(scoringEndConfig);
          
          if (now < scoringStart) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "评分时间段尚未开始" });
          }
          if (now > scoringEnd) {
            throw new TRPCError({ code: "BAD_REQUEST", message: "评分时间段已结束" });
          }
        }

        const result = await db.submitSecondTeacherScoreWithComment(input.draftId, input.score, ctx.user.id, input.comment);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "评分失败" });
        }

        // 记录第二导师评分日志
        db.logUserActivity({
          userId: ctx.user.id,
          userName: ctx.user.name || ctx.user.email,
          userRole: 'teacher',
          action: 'score_thesis_second',
          module: 'thesis',
          targetType: 'thesis_draft',
          targetId: input.draftId,
          description: `第二导师对论文终稿(ID:${input.draftId})评分: ${input.score}分`,
        });

        return { success: true, message: result.message };
      }),

    // 获取评分统计数据（管理员）
    getScoreStatistics: adminProcedure
      .input(z.object({
        academicYear: z.string().optional(),
      }).optional())
      .query(async ({ input }) => {
        const statistics = await db.getScoreStatistics(input?.academicYear);
        const overview = await db.getScoreStatisticsOverview(input?.academicYear);
         return { statistics, overview };
      }),

    // 删除评分记录（论文草稿）
    deleteScoreRecord: adminProcedure
      .input(z.object({
        draftId: z.number(),
        confirmDelete: z.boolean(),
      }))
      .mutation(async ({ input }) => {
        if (!input.confirmDelete) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "请确认删除操作" });
        }
        const result = await db.deleteScoreRecord(input.draftId);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "删除失败" });
        }
        return { success: true };
      }),

    // 第二导师申请取平均分
    requestAverage: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        reason: z.string().min(1, "请填写申请原因"),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.requestAverageScore(input.draftId, ctx.user.id, input.reason);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "申请失败" });
        }
        return { success: true };
      }),

    // 第二导师申请第一导师手动调整成绩
    requestManualAdjust: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        reason: z.string().min(1, "请填写申请原因"),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.requestManualAdjust(input.draftId, ctx.user.id, input.reason);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "申请失败" });
        }
        return { success: true };
      }),

    // 第一导师驳回第二导师的申请
    rejectRequest: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        reason: z.string().min(1, "请填写驳回原因"),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.rejectRequest(input.draftId, ctx.user.id, input.reason);
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "驳回失败" });
        }
        return { success: true };
      }),

    // 第一导师确认最终成绩（取平均分或手动调整）
    confirmFinalScore: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        action: z.enum(['confirm_average', 'manual_score']),
        manualScore: z.number().min(0).max(100).optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.confirmFinalScore(
          input.draftId,
          ctx.user.id,
          input.action,
          input.manualScore
        );
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "操作失败" });
        }
        return { success: true, finalScore: result.finalScore };
      }),

    // 获取第一导师待确认最终成绩的论文列表
    getPendingFinalScoreConfirmations: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getPendingFinalScoreConfirmations(ctx.user.id);
      }),

    // 获取第二导师可申请平均分的论文列表
    getPendingAverageRequests: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getPendingAverageRequests(ctx.user.id);
      }),

    // 获取已确定最终成绩的论文列表（教师视角）
    getCompletedFinalScores: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getCompletedFinalScores(ctx.user.id);
      }),

    // 获取需要协商的论文列表（分差>10分）
    getNegotiationPendingDrafts: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getNegotiationPendingDrafts(ctx.user.id);
      }),

    // 导师修改自己的评分（用于分差>10分时协商后修改）
    updateScore: teacherProcedure
      .input(z.object({
        draftId: z.number(),
        newScore: z.number().min(0).max(100),
        isFirstTeacher: z.boolean(),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.updateTeacherScore(
          input.draftId,
          input.newScore,
          ctx.user.id,
          input.isFirstTeacher
        );
        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "修改失败" });
        }
        return { success: true, message: result.message, finalScore: result.finalScore };
      }),
  }),

  // ==================== 题目修改申请路由 ====================
  titleChange: router({
    // 学生提交题目修改申请
    submit: studentProcedure
      .input(z.object({
        matchId: z.number(),
        newTitle: z.string().min(1, "新题目不能为空"),
        reason: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 获取匹配记录
        const match = await db.getMatchById(input.matchId);
        if (!match) {
          throw new TRPCError({ code: "NOT_FOUND", message: "匹配记录不存在" });
        }
        if (match.studentId !== ctx.user.id) {
          throw new TRPCError({ code: "FORBIDDEN", message: "您无权修改此论文题目" });
        }

        // 获取原始题目
        const topic = await db.getTopicById(match.topicId);
        if (!topic) {
          throw new TRPCError({ code: "NOT_FOUND", message: "课题不存在" });
        }

        const currentYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const result = await db.submitTitleChangeRequest(
          input.matchId,
          ctx.user.id,
          match.teacherId,
          topic.titleEn || topic.title,
          input.newTitle,
          input.reason,
          currentYear
        );

        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "提交失败" });
        }
        return { success: true, requestId: result.requestId };
      }),

    // 学生获取自己的题目修改申请历史
    getMyRequests: studentProcedure
      .query(async ({ ctx }) => {
        return db.getStudentTitleChangeRequests(ctx.user.id);
      }),

    // 导师获取待审核的题目修改申请
    getPendingRequests: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getTeacherPendingTitleChangeRequests(ctx.user.id);
      }),

    // 导师获取所有题目修改申请（包括已处理的）
    getAllRequests: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getTeacherAllTitleChangeRequests(ctx.user.id);
      }),

    // 导师获取待审核申请数量
    getPendingCount: teacherProcedure
      .query(async ({ ctx }) => {
        return db.getTeacherPendingTitleChangeCount(ctx.user.id);
      }),

    // 导师审核题目修改申请
    review: teacherProcedure
      .input(z.object({
        requestId: z.number(),
        approved: z.boolean(),
        reviewComment: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const result = await db.reviewTitleChangeRequest(
          input.requestId,
          ctx.user.id,
          input.approved,
          input.reviewComment
        );

        if (!result.success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: result.error || "审核失败" });
        }
        return { success: true };
      }),
  }),

  // ==================== 指导记录路由 ====================
  guidance: router({
    // 学生创建指导记录
    createLog: studentProcedure
      .input(z.object({
        guidanceDate: z.date(),
        topic: z.string().min(1, "请输入指导主题"),
        content: z.string().min(1, "请输入详细内容"),
        status: z.enum(["draft", "submitted"]).optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 获取学生的导师ID（通过已确认的志愿）
        const currentYear = await db.getCurrentAcademicYear();
        if (!currentYear) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "未找到当前学年" });
        }
        const confirmedWish = await db.getConfirmedWishByStudent(ctx.user.id, currentYear.yearName);
        if (!confirmedWish) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "未找到您的导师信息，请先完成选题" });
        }
        
        const logId = await db.createGuidanceLog({
          studentId: ctx.user.id,
          teacherId: confirmedWish.teacherId,
          guidanceDate: input.guidanceDate,
          topic: input.topic,
          content: input.content,
          status: input.status || "draft",
          academicYear: currentYear.yearName,
        });
        return { success: true, logId };
      }),

    // 学生更新指导记录
    updateLog: studentProcedure
      .input(z.object({
        logId: z.number(),
        guidanceDate: z.date().optional(),
        topic: z.string().optional(),
        content: z.string().optional(),
        status: z.enum(["draft", "submitted"]).optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        await db.updateGuidanceLog(input.logId, ctx.user.id, {
          guidanceDate: input.guidanceDate,
          topic: input.topic,
          content: input.content,
          status: input.status,
        });
        return { success: true };
      }),

    // 学生删除指导记录
    deleteLog: studentProcedure
      .input(z.object({ logId: z.number() }))
      .mutation(async ({ input, ctx }) => {
        await db.deleteGuidanceLog(input.logId, ctx.user.id);
        return { success: true };
      }),

    // 学生获取自己的指导记录列表
    getMyLogs: studentProcedure
      .input(z.object({ academicYear: z.string().optional() }).optional())
      .query(async ({ input, ctx }) => {
        return db.getStudentGuidanceLogs(ctx.user.id, input?.academicYear);
      }),

    // 获取单条指导记录详情
    getLogDetail: protectedProcedure
      .input(z.object({ logId: z.number() }))
      .query(async ({ input }) => {
        return db.getGuidanceLogDetail(input.logId);
      }),

    // 学生上传附件
    uploadAttachment: studentProcedure
      .input(z.object({
        logId: z.number().optional(),
        fileName: z.string(),
        fileUrl: z.string(),
        fileKey: z.string(),
        mimeType: z.string().optional(),
        fileSize: z.number().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查文件大小（20MB限制）
        if (input.fileSize && input.fileSize > 20 * 1024 * 1024) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "文件大小不能超过20MB" });
        }
        
        // 检查文件类型
        const allowedTypes = [
          "application/pdf",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "application/msword",
          "image/jpeg",
          "image/png",
        ];
        if (input.mimeType && !allowedTypes.includes(input.mimeType)) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "不支持的文件类型，仅支持PDF、DOCX、JPG、PNG" });
        }
        
        const attachmentId = await db.addGuidanceAttachment({
          logId: input.logId,
          studentId: ctx.user.id,
          fileName: input.fileName,
          fileUrl: input.fileUrl,
          fileKey: input.fileKey,
          mimeType: input.mimeType,
          fileSize: input.fileSize,
        });
        return { success: true, attachmentId };
      }),

    // 学生删除附件
    deleteAttachment: studentProcedure
      .input(z.object({ attachmentId: z.number() }))
      .mutation(async ({ input, ctx }) => {
        await db.deleteGuidanceAttachment(input.attachmentId, ctx.user.id);
        return { success: true };
      }),

    // 添加评论
    addComment: protectedProcedure
      .input(z.object({
        logId: z.number(),
        content: z.string().min(1, "请输入评论内容"),
      }))
      .mutation(async ({ input, ctx }) => {
        const userRole = ctx.user.role === "teacher" ? "teacher" : "student";
        const commentId = await db.addGuidanceComment({
          logId: input.logId,
          userId: ctx.user.id,
          userRole: userRole as "student" | "teacher",
          content: input.content,
        });
        return { success: true, commentId };
      }),

    // 导师确认指导记录
    confirmLog: teacherProcedure
      .input(z.object({ logId: z.number() }))
      .mutation(async ({ input, ctx }) => {
        await db.confirmGuidanceLog(input.logId, ctx.user.id);
        return { success: true };
      }),

    // 导师获取学生列表
    getStudents: teacherProcedure
      .input(z.object({ academicYear: z.string().optional() }).optional())
      .query(async ({ input, ctx }) => {
        return db.getTeacherGuidanceStudents(ctx.user.id, input?.academicYear);
      }),

    // 导师查看学生的指导记录
    getStudentLogs: teacherProcedure
      .input(z.object({
        studentId: z.number(),
        academicYear: z.string().optional(),
      }))
      .query(async ({ input, ctx }) => {
        return db.getTeacherViewStudentLogs(ctx.user.id, input.studentId, input.academicYear);
      }),

    // 导师获取学生所有附件（用于批量下载）
    getStudentAttachments: teacherProcedure
      .input(z.object({ studentId: z.number() }))
      .query(async ({ input, ctx }) => {
        return db.getStudentAllAttachments(input.studentId, ctx.user.id);
      }),

    // 导师导出学生指导记录PDF
    exportStudentLogsPdf: teacherProcedure
      .input(z.object({ studentId: z.number() }))
      .mutation(async ({ input, ctx }) => {
        const { generateGuidancePdf } = await import("./guidancePdf");
        // 获取学生信息
        const student = await db.getUserById(input.studentId);
        if (!student) {
          throw new TRPCError({ code: "NOT_FOUND", message: "学生不存在" });
        }
        // 获取指导记录
        const logs = await db.getStudentGuidanceLogs(input.studentId);
        // 获取每条记录的详情（含附件和评论）
        const logsWithDetails = await Promise.all(
          logs.map(async (log) => {
            const detail = await db.getGuidanceLogDetail(log.id);
            return detail || log;
          })
        );
        const teacher = await db.getUserById(ctx.user.id);
        const pdfBuffer = await generateGuidancePdf({
          studentName: student.name || "未知学生",
          studentId: student.studentId || undefined,
          teacherName: teacher?.name || undefined,
          logs: logsWithDetails as any,
          title: `${student.name || "学生"} - 指导记录`,
        });
        const base64 = pdfBuffer.toString("base64");
        return { base64, filename: `${student.name || "学生"}_指导记录.pdf` };
      }),

    // 学生导出自己的指导记录PDF
    exportMyLogsPdf: studentProcedure
      .mutation(async ({ ctx }) => {
        const { generateGuidancePdf } = await import("./guidancePdf");
        const student = await db.getUserById(ctx.user.id);
        if (!student) {
          throw new TRPCError({ code: "NOT_FOUND", message: "用户不存在" });
        }
        const logs = await db.getStudentGuidanceLogs(ctx.user.id);
        const logsWithDetails = await Promise.all(
          logs.map(async (log) => {
            const detail = await db.getGuidanceLogDetail(log.id);
            return detail || log;
          })
        );
        const pdfBuffer = await generateGuidancePdf({
          studentName: student.name || "未知学生",
          studentId: student.studentId || undefined,
          logs: logsWithDetails as any,
          title: `${student.name || "学生"} - 指导记录`,
        });
        const base64 = pdfBuffer.toString("base64");
        return { base64, filename: `${student.name || "学生"}_指导记录.pdf` };
      }),
  }),

  // ==================== 毕设采购审核模块 ====================
  purchase: router({
    // 获取当前用户的特殊角色
    getMySpecialRoles: protectedProcedure.query(async ({ ctx }) => {
      return db.getUserSpecialRoles(ctx.user.id);
    }),

    // 检查用户是否为实验室管理员
    isLabAdmin: protectedProcedure.query(async ({ ctx }) => {
      return db.isUserLabAdmin(ctx.user.id);
    }),

    // 检查用户是否为资产分管领导
    isAssetLeader: protectedProcedure.query(async ({ ctx }) => {
      return db.isUserAssetLeader(ctx.user.id);
    }),

    // 获取实验室管理员微信信息（学生查看）
    getLabAdminWechat: protectedProcedure.query(async () => {
      return db.getLabAdminWechatInfo();
    }),

    // 获取当前学年的在读班级列表
    getActiveClasses: protectedProcedure.query(async () => {
      return db.getActiveClasses();
    }),

    // 学生提交采购申请
    submitRequest: studentProcedure
      .input(z.object({
        studentName: z.string().min(1, "请输入学生姓名"),
        studentClass: z.string().min(1, "请输入班级"),
        studentNo: z.string().min(1, "请输入学号"),
        totalAmount: z.string().min(1, "请输入总费用"),
        reason: z.string().optional(),
        fileUrl: z.string().min(1, "请上传申请文件"),
        fileKey: z.string().min(1),
        fileName: z.string().min(1),
      }))
      .mutation(async ({ input, ctx }) => {
        const academicYear = await db.getConfig("currentAcademicYear") || "2024-2025";
        const request = await db.createPurchaseRequest({
          studentId: ctx.user.id,
          studentName: input.studentName,
          studentClass: input.studentClass,
          studentNo: input.studentNo,
          totalAmount: input.totalAmount,
          reason: input.reason,
          fileUrl: input.fileUrl,
          fileKey: input.fileKey,
          fileName: input.fileName,
          academicYear,
        });
        if (!request) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "提交申请失败" });
        }
        return request;
      }),

    // 学生查看自己的申请列表
    getMyRequests: studentProcedure.query(async ({ ctx }) => {
      return db.getStudentPurchaseRequests(ctx.user.id);
    }),

    // 获取申请详情
    getRequestDetail: protectedProcedure
      .input(z.object({ requestId: z.number() }))
      .query(async ({ input }) => {
        return db.getPurchaseRequestById(input.requestId);
      }),

    // 实验室管理员获取待审核列表
    getPendingLabReview: protectedProcedure.query(async ({ ctx }) => {
      const isLabAdmin = await db.isUserLabAdmin(ctx.user.id);
      if (!isLabAdmin && ctx.user.role !== "admin") {
        throw new TRPCError({ code: "FORBIDDEN", message: "无权限" });
      }
      return db.getPendingLabReviewRequests();
    }),

    // 导师获取待审核列表
    getPendingTeacherReview: teacherProcedure.query(async ({ ctx }) => {
      return db.getPendingTeacherReviewRequests(ctx.user.id);
    }),

    // 资产分管领导获取待审核列表
    getPendingAssetReview: protectedProcedure.query(async ({ ctx }) => {
      const isAssetLeader = await db.isUserAssetLeader(ctx.user.id);
      if (!isAssetLeader && ctx.user.role !== "admin") {
        throw new TRPCError({ code: "FORBIDDEN", message: "无权限" });
      }
      return db.getPendingAssetReviewRequests();
    }),

    // 实验室管理员审核
    labReview: protectedProcedure
      .input(z.object({
        requestId: z.number(),
        approved: z.boolean(),
        comment: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const isLabAdmin = await db.isUserLabAdmin(ctx.user.id);
        if (!isLabAdmin && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权限" });
        }
        const success = await db.labReviewPurchaseRequest(
          input.requestId,
          ctx.user.id,
          input.approved,
          input.comment
        );
        if (!success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "审核失败" });
        }
        return { success: true };
      }),

    // 导师审核
    teacherReview: teacherProcedure
      .input(z.object({
        requestId: z.number(),
        approved: z.boolean(),
        comment: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const success = await db.teacherReviewPurchaseRequest(
          input.requestId,
          ctx.user.id,
          input.approved,
          input.comment
        );
        if (!success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "审核失败" });
        }
        return { success: true };
      }),

    // 资产分管领导审核
    assetReview: protectedProcedure
      .input(z.object({
        requestId: z.number(),
        approved: z.boolean(),
        comment: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const isAssetLeader = await db.isUserAssetLeader(ctx.user.id);
        if (!isAssetLeader && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权限" });
        }
        const success = await db.assetReviewPurchaseRequest(
          input.requestId,
          ctx.user.id,
          input.approved,
          input.comment
        );
        if (!success) {
          throw new TRPCError({ code: "BAD_REQUEST", message: "审核失败" });
        }
        return { success: true };
      }),

    // 管理员：任命特殊角色
    appointRole: adminProcedure
      .input(z.object({
        userId: z.number(),
        roleType: z.enum(["lab_admin", "asset_leader"]),
        wechatId: z.string().optional(),
        wechatNote: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const role = await db.appointSpecialRole({
          userId: input.userId,
          roleType: input.roleType,
          appointedBy: ctx.user.id,
          wechatId: input.wechatId,
          wechatNote: input.wechatNote,
        });
        if (!role) {
          throw new TRPCError({ code: "INTERNAL_SERVER_ERROR", message: "任命失败" });
        }
        return role;
      }),

    // 管理员：撤销特殊角色
    revokeRole: adminProcedure
      .input(z.object({
        userId: z.number(),
        roleType: z.enum(["lab_admin", "asset_leader"]),
      }))
      .mutation(async ({ input }) => {
        await db.revokeSpecialRole(input.userId, input.roleType);
        return { success: true };
      }),

    // 管理员：获取特殊角色列表
    getSpecialRoles: adminProcedure
      .input(z.object({ roleType: z.enum(["lab_admin", "asset_leader"]) }))
      .query(async ({ input }) => {
        return db.getSpecialRolesByType(input.roleType);
      }),

    // 更新实验室管理员微信信息
    updateLabAdminWechat: protectedProcedure
      .input(z.object({
        wechatId: z.string().min(1, "请输入微信号"),
        wechatNote: z.string().optional(),
      }))
      .mutation(async ({ input, ctx }) => {
        const isLabAdmin = await db.isUserLabAdmin(ctx.user.id);
        if (!isLabAdmin && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权限" });
        }
        // 如果是管理员，更新第一个实验室管理员的微信信息
        if (ctx.user.role === "admin") {
          const labAdmins = await db.getSpecialRolesByType("lab_admin");
          if (labAdmins.length > 0) {
            await db.updateLabAdminWechat(labAdmins[0].userId, input.wechatId, input.wechatNote);
          }
        } else {
          await db.updateLabAdminWechat(ctx.user.id, input.wechatId, input.wechatNote);
        }
        return { success: true };
      }),

    // 管理员：获取所有申请列表
    getAllRequests: adminProcedure
      .input(z.object({
        status: z.string().optional(),
        academicYear: z.string().optional(),
      }).optional())
      .query(async ({ input }) => {
        return db.getAllPurchaseRequests(input);
      }),

    // 导师：获取审核记录（包括已审核和待审核的所有记录）
    // 实验室管理员和资产分管领导可以查看所有学生的记录
    getTeacherReviewHistory: protectedProcedure
      .input(z.object({
        studentClass: z.string().optional(),
        studentName: z.string().optional(),
        startDate: z.date().optional(),
        endDate: z.date().optional(),
        result: z.enum(["approved", "rejected", "all"]).optional(),
      }).optional())
      .query(async ({ input, ctx }) => {
        // 检查是否为实验室管理员或资产分管领导
        const isLabAdmin = await db.isUserLabAdmin(ctx.user.id);
        const isAssetLeader = await db.isUserAssetLeader(ctx.user.id);
        
        // 实验室管理员或资产分管领导可以查看所有记录
        if (isLabAdmin || isAssetLeader) {
          return db.getAllPurchaseReviewHistory(input);
        }
        
        // 普通导师只能查看自己指导学生的记录
        if (ctx.user.role !== "teacher" && ctx.user.role !== "admin") {
          throw new TRPCError({ code: "FORBIDDEN", message: "无权限" });
        }
        return db.getTeacherPurchaseReviewHistory(ctx.user.id, input);
      }),

    // 删除采购申请记录（仅限实验室管理员和资产分管领导）
    deleteReviewRecord: protectedProcedure
      .input(z.object({
        requestId: z.number(),
      }))
      .mutation(async ({ input, ctx }) => {
        // 检查是否为实验室管理员或资产分管领导
        const isLabAdmin = await db.isUserLabAdmin(ctx.user.id);
        const isAssetLeader = await db.isUserAssetLeader(ctx.user.id);
        
        if (!isLabAdmin && !isAssetLeader) {
          throw new TRPCError({ code: "FORBIDDEN", message: "仅实验室管理员和资产分管领导可以删除记录" });
        }
        
        await db.deletePurchaseRequest(input.requestId);
        return { success: true };
      }),
   }),

});
export type AppRouter = typeof appRouter;
