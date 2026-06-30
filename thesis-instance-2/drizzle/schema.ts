import { int, mysqlEnum, mysqlTable, text, timestamp, varchar, json, tinyint, index, decimal } from "drizzle-orm/mysql-core";

// ==================== 用户表 ====================
export const users = mysqlTable("users", {
  id: int("id").autoincrement().primaryKey(),
  openId: varchar("openId", { length: 64 }),
  name: varchar("name", { length: 128 }),
  email: varchar("email", { length: 320 }).notNull(),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["admin", "teacher", "student"]).default("student").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn"),
  password: varchar("password", { length: 256 }).notNull(),
  teacherType: mysqlEnum("teacherType", ["chinese", "british"]),
  studentType: mysqlEnum("studentType", ["transfer", "non_transfer"]),
  studentMajor: mysqlEnum("studentMajor", ["electronic_info", "communication"]),
  annualQuota: int("annualQuota"),
  language: mysqlEnum("language", ["zh", "en"]).default("zh"),
  studentId: varchar("studentId", { length: 32 }),
  candidateNo: varchar("candidateNo", { length: 32 }),
  studentClass: varchar("studentClass", { length: 64 }),
  faculty: varchar("faculty", { length: 128 }).default("萨塞克斯人工智能学院"),
  initialPassword: varchar("initialPassword", { length: 256 }).default("123456"),
  teacherNo: varchar("teacherNo", { length: 32 }).default("0000000"),
  sussexEmail: varchar("sussexEmail", { length: 320 }),
  sussexId: varchar("sussexId", { length: 32 }),
  academicYear: varchar("academicYear", { length: 20 }),
  canPublish: tinyint("canPublish").default(1),
  namePinyin: varchar("namePinyin", { length: 128 }),
});

// ==================== 学年表 ====================
export const academicYears = mysqlTable("academicYears", {
  id: int("id").autoincrement().primaryKey(),
  yearName: varchar("yearName", { length: 32 }).notNull(),
  displayName: varchar("displayName", { length: 64 }),
  status: mysqlEnum("status", ["active", "draft"]).default("draft").notNull(),
  isCurrentYear: tinyint("isCurrentYear").default(0),
  studentSelectionStart: timestamp("studentSelectionStart", { mode: "string" }),
  studentSelectionEnd: timestamp("studentSelectionEnd", { mode: "string" }),
  teacherConfirmStart: timestamp("teacherConfirmStart", { mode: "string" }),
  teacherConfirmEnd: timestamp("teacherConfirmEnd", { mode: "string" }),
  maxWishesNormal: int("maxWishesNormal").default(5),
  maxWishesTransfer: int("maxWishesTransfer").default(8),
  effectiveWishes: int("effectiveWishes").default(5),
  statementRequired: tinyint("statementRequired").default(0),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  chineseTeacherQuota: int("chineseTeacherQuota").default(5),
  thesisUploadStart: timestamp("thesisUploadStart", { mode: "string" }),
  thesisUploadEnd: timestamp("thesisUploadEnd", { mode: "string" }),
  scoringStart: timestamp("scoringStart", { mode: "string" }),
  scoringEnd: timestamp("scoringEnd", { mode: "string" }),
  transferStudentSelectionStart: timestamp("transferStudentSelectionStart", { mode: "string" }),
  transferStudentSelectionEnd: timestamp("transferStudentSelectionEnd", { mode: "string" }),
});

// ==================== 课题表 ====================
export const topics = mysqlTable("topics", {
  id: int("id").autoincrement().primaryKey(),
  teacherId: int("teacherId").notNull(),
  title: varchar("title", { length: 512 }).notNull(),
  titleEn: varchar("titleEn", { length: 512 }),
  description: text("description").notNull(),
  descriptionEn: text("descriptionEn"),
  requiredSkills: text("requiredSkills"),
  suitableMajor: mysqlEnum("suitableMajor", ["electronic_info", "communication", "both"]).default("both"),
  status: mysqlEnum("status", ["draft", "published", "used"]).default("draft").notNull(),
  isCurrentYear: tinyint("isCurrentYear").default(0),
  academicYear: varchar("academicYear", { length: 32 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  keywords: varchar("keywords", { length: 512 }),
  researchFocus: varchar("researchFocus", { length: 256 }),
  thesisType: varchar("thesisType", { length: 64 }).default("毕业设计"),
  topicSource: varchar("topicSource", { length: 64 }).default("其他"),
  topicLanguage: varchar("topicLanguage", { length: 16 }).default("英语"),
  researchProjectName: varchar("researchProjectName", { length: 256 }),
  language: varchar("language", { length: 16 }).default("英语"),
});

// ==================== 志愿表 ====================
export const wishes = mysqlTable("wishes", {
  id: int("id").autoincrement().primaryKey(),
  studentId: int("studentId").notNull(),
  topicId: int("topicId").notNull(),
  priority: int("priority").notNull(),
  statement: text("statement"),
  status: mysqlEnum("status", ["pending", "selected", "rejected", "matched"]).default("pending").notNull(),
  academicYear: varchar("academicYear", { length: 32 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  teacherDecision: mysqlEnum("teacherDecision", ["pending", "approved", "rejected"]).default("pending"),
  decisionAt: timestamp("decisionAt", { mode: "string" }),
  currentPriority: int("currentPriority").default(1),
}, (table) => [
  index("idx_wishes_studentId").on(table.studentId),
  index("idx_wishes_topicId").on(table.topicId),
  index("idx_wishes_academicYear").on(table.academicYear),
  index("idx_wishes_teacherDecision").on(table.teacherDecision),
  index("idx_wishes_composite").on(table.academicYear, table.teacherDecision, table.topicId),
]);

// ==================== 匹配表 ====================
export const matches = mysqlTable("matches", {
  id: int("id").autoincrement().primaryKey(),
  studentId: int("studentId").notNull(),
  topicId: int("topicId").notNull(),
  teacherId: int("teacherId").notNull(),
  secondTeacherId: int("secondTeacherId"),
  matchRound: int("matchRound").default(1),
  isAdjustment: tinyint("isAdjustment").default(0),
  academicYear: varchar("academicYear", { length: 32 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),  score: int("score"),
  remarks: text("remarks"),
}, (table) => [
  index("idx_matches_studentId").on(table.studentId),
  index("idx_matches_topicId").on(table.topicId),
  index("idx_matches_teacherId").on(table.teacherId),
  index("idx_matches_academicYear").on(table.academicYear),
  index("idx_matches_student_year").on(table.studentId, table.academicYear),
]);
// ==================== 课题表突表 ====================
export const conflicts = mysqlTable("conflicts", {
  id: int("id").autoincrement().primaryKey(),
  topicId: int("topicId").notNull(),
  teacherId: int("teacherId").notNull(),
  studentIds: json("studentIds").notNull(),
  selectedStudentId: int("selectedStudentId"),
  matchRound: int("matchRound").default(1),
  deadline: timestamp("deadline", { mode: "string" }),
  resolved: tinyint("resolved").default(0),
  academicYear: varchar("academicYear", { length: 32 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

// ==================== 系统配置表 ====================
export const systemConfig = mysqlTable("systemConfig", {
  id: int("id").autoincrement().primaryKey(),
  configKey: varchar("configKey", { length: 64 }).notNull(),
  configValue: text("configValue").notNull(),
  description: text("description"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

// ==================== 论文草稿表 ====================
export const thesisDrafts = mysqlTable("thesisDrafts", {
  id: int("id").autoincrement().primaryKey(),
  studentId: int("studentId").notNull(),
  matchId: int("matchId").notNull(),
  fileName: varchar("fileName", { length: 256 }).notNull(),
  fileKey: varchar("fileKey", { length: 512 }).notNull(),
  fileUrl: varchar("fileUrl", { length: 1024 }).notNull(),
  fileSize: int("fileSize").notNull(),
  mimeType: varchar("mimeType", { length: 128 }).notNull(),
  version: int("version").default(1).notNull(),
  status: mysqlEnum("status", ["submitted", "reviewed", "approved"]).default("submitted").notNull(),
  submittedAt: timestamp("submittedAt", { mode: "string" }).defaultNow().notNull(),
  academicYear: varchar("academicYear", { length: 32 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  score: int("score"),
  scoredAt: timestamp("scoredAt", { mode: "string" }),
  scoredBy: int("scoredBy"),
  secondTeacherScore: int("secondTeacherScore"),
  secondTeacherScoredAt: timestamp("secondTeacherScoredAt", { mode: "string" }),
  secondTeacherScoredBy: int("secondTeacherScoredBy"),
  firstTeacherComment: text("firstTeacherComment"),
  secondTeacherComment: text("secondTeacherComment"),
  // 评分流程字段
  requestAverage: tinyint("requestAverage").default(0), // 第二导师是否申请取平均分
  requestManualAdjust: tinyint("requestManualAdjust").default(0), // 第二导师是否申请第一导师手动调整
  requestReason: text("requestReason"), // 第二导师申请原因
  rejectReason: text("rejectReason"), // 第一导师驳回原因
  averageConfirmed: tinyint("averageConfirmed"), // 第一导师是否确认取平均分 (null=未处理, 1=确认, 0=拒绝)
  finalScore: decimal("finalScore", { precision: 4, scale: 1 }), // 最终成绩（保留一位小数）
  finalScoreConfirmedAt: timestamp("finalScoreConfirmedAt", { mode: "string" }), // 最终成绩确认时间
  // 宽限期扣分字段
  lateSubmission: tinyint("lateSubmission").default(0), // 是否为宽限期提交 (0=否, 1=是)
  latePenalty: int("latePenalty").default(0), // 宽限期扣分 (5戆9戸10)
}, (table) => [
  index("idx_studentId").on(table.studentId),
  index("idx_matchId").on(table.matchId),
  index("idx_academicYear").on(table.academicYear),
]);

// ==================== 论文草稿历史表 ====================
export const thesisDraftHistory = mysqlTable("thesisDraftHistory", {
  id: int("id").autoincrement().primaryKey(),
  draftId: int("draftId").notNull(),
  studentId: int("studentId").notNull(),
  fileName: varchar("fileName", { length: 256 }).notNull(),
  fileKey: varchar("fileKey", { length: 512 }).notNull(),
  fileUrl: varchar("fileUrl", { length: 1024 }).notNull(),
  fileSize: int("fileSize").notNull(),
  mimeType: varchar("mimeType", { length: 128 }).notNull(),
  version: int("version").notNull(),
  archivedAt: timestamp("archivedAt").defaultNow().notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
}, (table) => [
  index("idx_draftId").on(table.draftId),
  index("idx_studentId").on(table.studentId),
]);

// ==================== 论文终稿表 ====================
export const thesisFinalDrafts = mysqlTable("thesisFinalDrafts", {
  id: int("id").autoincrement().primaryKey(),
  matchId: int("matchId").notNull(),
  studentId: int("studentId").notNull(),
  fileUrl: varchar("fileUrl", { length: 1024 }).notNull(),
  fileKey: varchar("fileKey", { length: 512 }).notNull(),
  fileName: varchar("fileName", { length: 256 }).notNull(),
  fileSize: int("fileSize"),
  version: int("version").default(1),
  uploadedAt: timestamp("uploadedAt").defaultNow().notNull(),
  academicYear: varchar("academicYear", { length: 16 }),
});

// ==================== 论文评分表 ====================
export const thesisScores = mysqlTable("thesisScores", {
  id: int("id").autoincrement().primaryKey(),
  matchId: int("matchId").notNull(),
  draftId: int("draftId").notNull(),
  teacherId: int("teacherId").notNull(),
  supervisorRole: mysqlEnum("supervisorRole", ["first", "second", "third"]).notNull(),
  score: int("score").notNull(),
  comments: text("comments"),
  scoredAt: timestamp("scoredAt").defaultNow().notNull(),
  academicYear: varchar("academicYear", { length: 16 }),
});

// ==================== 评分进度表 ====================
export const scoringProgress = mysqlTable("scoringProgress", {
  id: int("id").autoincrement().primaryKey(),
  matchId: int("matchId").notNull(),
  status: mysqlEnum("status", [
    "not_started", "draft_uploaded", "first_scored", "second_assigned",
    "second_scored", "score_diff_small", "score_diff_large",
    "third_assigned", "third_scored", "completed"
  ]).default("not_started").notNull(),
  scoreDifference: int("scoreDifference"),
  needsThirdSupervisor: tinyint("needsThirdSupervisor").default(0),
  adminNotified: tinyint("adminNotified").default(0),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  academicYear: varchar("academicYear", { length: 16 }),
}, (table) => [
  index("matchId").on(table.matchId),
]);

// ==================== 二导分配表 ====================
export const supervisorAssignments = mysqlTable("supervisorAssignments", {
  id: int("id").autoincrement().primaryKey(),
  matchId: int("matchId").notNull(),
  teacherId: int("teacherId").notNull(),
  supervisorRole: mysqlEnum("supervisorRole", ["second", "third"]).notNull(),
  assignedBy: int("assignedBy"),
  assignmentMethod: mysqlEnum("assignmentMethod", ["manual", "random"]).default("manual"),
  status: mysqlEnum("status", ["pending", "accepted", "completed"]).default("pending"),
  notifiedAt: timestamp("notifiedAt", { mode: "string" }),
  assignedAt: timestamp("assignedAt").defaultNow().notNull(),
  academicYear: varchar("academicYear", { length: 16 }),
});

// ==================== 联合评分表 ====================
export const jointScores = mysqlTable("jointScores", {
  id: int("id").autoincrement().primaryKey(),
  matchId: int("matchId").notNull(),
  finalScore: int("finalScore").notNull(),
  scoreMethod: mysqlEnum("scoreMethod", ["average", "negotiated", "majority"]).notNull(),
  firstSupervisorId: int("firstSupervisorId").notNull(),
  secondSupervisorId: int("secondSupervisorId").notNull(),
  thirdSupervisorId: int("thirdSupervisorId"),
  jointComments: text("jointComments"),
  confirmedBy: varchar("confirmedBy", { length: 256 }),
  confirmedAt: timestamp("confirmedAt").defaultNow().notNull(),
  academicYear: varchar("academicYear", { length: 16 }),
}, (table) => [
  index("matchId").on(table.matchId),
]);

// ==================== 题目变更申请表 ====================
export const titleChangeRequests = mysqlTable("titleChangeRequests", {
  id: int("id").autoincrement().primaryKey(),
  matchId: int("matchId").notNull(),
  studentId: int("studentId").notNull(),
  teacherId: int("teacherId").notNull(),
  originalTitle: varchar("originalTitle", { length: 512 }).notNull(),
  newTitle: varchar("newTitle", { length: 512 }).notNull(),
  reason: text("reason"),
  status: mysqlEnum("status", ["pending", "approved", "rejected"]).default("pending").notNull(),
  reviewedAt: timestamp("reviewedAt", { mode: "string" }),
  reviewComment: text("reviewComment"),
  academicYear: varchar("academicYear", { length: 32 }),
  createdAt: timestamp("createdAt", { mode: "string" }).defaultNow().notNull(),
  updatedAt: timestamp("updatedAt", { mode: "string" }).defaultNow().onUpdateNow().notNull(),
}, (table) => [
  index("matchId").on(table.matchId),
  index("studentId").on(table.studentId),
  index("teacherId").on(table.teacherId),
]);

// ==================== 类型导出 ====================
export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

export type AcademicYear = typeof academicYears.$inferSelect;
export type InsertAcademicYear = typeof academicYears.$inferInsert;

export type Topic = typeof topics.$inferSelect;
export type InsertTopic = typeof topics.$inferInsert;

export type Wish = typeof wishes.$inferSelect;
export type InsertWish = typeof wishes.$inferInsert;

export type Match = typeof matches.$inferSelect;
export type InsertMatch = typeof matches.$inferInsert;

export type Conflict = typeof conflicts.$inferSelect;
export type InsertConflict = typeof conflicts.$inferInsert;

export type SystemConfig = typeof systemConfig.$inferSelect;
export type InsertSystemConfig = typeof systemConfig.$inferInsert;

export type ThesisDraft = typeof thesisDrafts.$inferSelect;
export type InsertThesisDraft = typeof thesisDrafts.$inferInsert;

export type ThesisDraftHistory = typeof thesisDraftHistory.$inferSelect;
export type InsertThesisDraftHistory = typeof thesisDraftHistory.$inferInsert;

export type ThesisFinalDraft = typeof thesisFinalDrafts.$inferSelect;
export type InsertThesisFinalDraft = typeof thesisFinalDrafts.$inferInsert;

export type ThesisScore = typeof thesisScores.$inferSelect;
export type InsertThesisScore = typeof thesisScores.$inferInsert;

export type ScoringProgress = typeof scoringProgress.$inferSelect;
export type InsertScoringProgress = typeof scoringProgress.$inferInsert;

export type SupervisorAssignment = typeof supervisorAssignments.$inferSelect;
export type InsertSupervisorAssignment = typeof supervisorAssignments.$inferInsert;

export type JointScore = typeof jointScores.$inferSelect;
export type InsertJointScore = typeof jointScores.$inferInsert;

export type TitleChangeRequest = typeof titleChangeRequests.$inferSelect;
export type InsertTitleChangeRequest = typeof titleChangeRequests.$inferInsert;


// ==================== 题库表 ====================
export const topicLibrary = mysqlTable("topicLibrary", {
  id: int("id").autoincrement().primaryKey(),
  /** 跨库同步唯一标识（UUID，用于双实例部署时题库同步） */
  syncUuid: varchar("sync_uuid", { length: 36 }).notNull(),
  /** 来源实例编号（1或2，用于双实例部署时标记数据来源） */
  sourceInstance: int("source_instance").notNull().default(1),
  /** 原课题ID */
  originalTopicId: int("originalTopicId").notNull(),
  /** 课题标题 */
  title: varchar("title", { length: 512 }).notNull(),
  /** 课题标题（英文） */
  titleEn: varchar("titleEn", { length: 512 }),
  /** 导师ID */
  teacherId: int("teacherId").notNull(),
  /** 导师姓名 */
  teacherName: varchar("teacherName", { length: 128 }),
  /** 发布时间 */
  publishedAt: timestamp("publishedAt").defaultNow().notNull(),
  /** 状态：published-已发布, used-已使用(被选中), withdrawn-已撤回 */
  status: mysqlEnum("status", ["published", "used", "withdrawn"]).default("published").notNull(),
  /** 学年 */
  academicYear: varchar("academicYear", { length: 32 }),
  /** 课题描述 */
  description: text("description"),
  /** 适合学生类型 */
  suitableFor: varchar("suitableFor", { length: 64 }),
  /** 选题来源 */
  topicSource: varchar("topicSource", { length: 128 }),
  /** 科研项目名称 */
  researchProjectName: varchar("researchProjectName", { length: 256 }),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  /** 更新时间 */
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type TopicLibrary = typeof topicLibrary.$inferSelect;
export type InsertTopicLibrary = typeof topicLibrary.$inferInsert;


// ==================== 指导记录模块 ====================

/** 指导记录表 */
export const guidanceLogs = mysqlTable("guidanceLogs", {
  id: int("id").autoincrement().primaryKey(),
  /** 学生ID */
  studentId: int("studentId").notNull(),
  /** 导师ID（第一导师） */
  teacherId: int("teacherId").notNull(),
  /** 指导日期 */
  guidanceDate: timestamp("guidanceDate").notNull(),
  /** 指导主题/摘要 */
  topic: varchar("topic", { length: 256 }).notNull(),
  /** 详细内容与收获（富文本HTML） */
  content: text("content").notNull(),
  /** 状态：draft-草稿, submitted-已提交, confirmed-导师已确认 */
  status: mysqlEnum("status", ["draft", "submitted", "confirmed"]).default("draft").notNull(),
  /** 学年 */
  academicYear: varchar("academicYear", { length: 32 }),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  /** 更新时间 */
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

/** 指导记录附件表 */
export const guidanceAttachments = mysqlTable("guidanceAttachments", {
  id: int("id").autoincrement().primaryKey(),
  /** 关联的指导记录ID（可为空，表示独立上传） */
  logId: int("logId"),
  /** 学生ID */
  studentId: int("studentId").notNull(),
  /** 文件名 */
  fileName: varchar("fileName", { length: 256 }).notNull(),
  /** 文件URL（S3存储） */
  fileUrl: varchar("fileUrl", { length: 1024 }).notNull(),
  /** 文件Key（S3存储） */
  fileKey: varchar("fileKey", { length: 512 }).notNull(),
  /** 文件类型（MIME类型） */
  mimeType: varchar("mimeType", { length: 128 }),
  /** 文件大小（字节） */
  fileSize: int("fileSize"),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

/** 指导记录评论表 */
export const guidanceComments = mysqlTable("guidanceComments", {
  id: int("id").autoincrement().primaryKey(),
  /** 关联的指导记录ID */
  logId: int("logId").notNull(),
  /** 评论者ID */
  userId: int("userId").notNull(),
  /** 评论者角色 */
  userRole: mysqlEnum("userRole", ["student", "teacher"]).notNull(),
  /** 评论内容 */
  content: text("content").notNull(),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type GuidanceLog = typeof guidanceLogs.$inferSelect;
export type InsertGuidanceLog = typeof guidanceLogs.$inferInsert;

export type GuidanceAttachment = typeof guidanceAttachments.$inferSelect;
export type InsertGuidanceAttachment = typeof guidanceAttachments.$inferInsert;

export type GuidanceComment = typeof guidanceComments.$inferSelect;
export type InsertGuidanceComment = typeof guidanceComments.$inferInsert;


// ==================== 毕设采购审核模块 ====================

/** 特殊角色表 - 实验室管理员、资产分管领导 */
export const specialRoles = mysqlTable("specialRoles", {
  id: int("id").autoincrement().primaryKey(),
  /** 用户ID */
  userId: int("userId").notNull(),
  /** 角色类型：lab_admin-实验室管理员, asset_leader-资产分管领导 */
  roleType: mysqlEnum("roleType", ["lab_admin", "asset_leader"]).notNull(),
  /** 任命者ID（管理员） */
  appointedBy: int("appointedBy").notNull(),
  /** 任命时间 */
  appointedAt: timestamp("appointedAt").defaultNow().notNull(),
  /** 状态：active-生效中, revoked-已撤销 */
  status: mysqlEnum("status", ["active", "revoked"]).default("active").notNull(),
  /** 撤销时间 */
  revokedAt: timestamp("revokedAt", { mode: "string" }),
  /** 微信号（仅实验室管理员） */
  wechatId: varchar("wechatId", { length: 64 }),
  /** 微信备注说明 */
  wechatNote: text("wechatNote"),
});

/** 采购申请表 */
export const purchaseRequests = mysqlTable("purchaseRequests", {
  id: int("id").autoincrement().primaryKey(),
  /** 学生ID */
  studentId: int("studentId").notNull(),
  /** 学生姓名 */
  studentName: varchar("studentName", { length: 128 }).notNull(),
  /** 班级 */
  studentClass: varchar("studentClass", { length: 64 }).notNull(),
  /** 学号 */
  studentNo: varchar("studentNo", { length: 32 }).notNull(),
  /** 总费用（元） */
  totalAmount: decimal("totalAmount", { precision: 10, scale: 2 }).notNull(),
  /** 申请原因 */
  reason: text("reason"),
  /** 申请文件URL */
  fileUrl: varchar("fileUrl", { length: 1024 }).notNull(),
  /** 申请文件Key */
  fileKey: varchar("fileKey", { length: 512 }).notNull(),
  /** 申请文件名 */
  fileName: varchar("fileName", { length: 256 }).notNull(),
  /** 申请时间 */
  applyTime: timestamp("applyTime").defaultNow().notNull(),
  /** 
   * 审核状态：
   * pending_lab - 待实验室管理员审核
   * pending_teacher - 待导师审核
   * pending_asset - 待资产分管领导审核（超额时）
   * approved - 审核通过
   * rejected_lab - 实验室管理员拒绝
   * rejected_teacher - 导师拒绝
   * rejected_asset - 资产分管领导拒绝
   */
  status: mysqlEnum("status", [
    "pending_lab", "pending_teacher", "pending_asset", 
    "approved", "rejected_lab", "rejected_teacher", "rejected_asset"
  ]).default("pending_lab").notNull(),
  /** 是否超额（>1500元） */
  isOverBudget: tinyint("isOverBudget").default(0),
  /** 实验室管理员审核时间 */
  labReviewedAt: timestamp("labReviewedAt", { mode: "string" }),
  /** 实验室管理员审核人ID */
  labReviewedBy: int("labReviewedBy"),
  /** 实验室管理员审核意见 */
  labComment: text("labComment"),
  /** 导师审核时间 */
  teacherReviewedAt: timestamp("teacherReviewedAt", { mode: "string" }),
  /** 导师审核人ID */
  teacherReviewedBy: int("teacherReviewedBy"),
  /** 导师审核意见 */
  teacherComment: text("teacherComment"),
  /** 资产分管领导审核时间 */
  assetReviewedAt: timestamp("assetReviewedAt", { mode: "string" }),
  /** 资产分管领导审核人ID */
  assetReviewedBy: int("assetReviewedBy"),
  /** 资产分管领导审核意见 */
  assetComment: text("assetComment"),
  /** 学年 */
  academicYear: varchar("academicYear", { length: 32 }),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  /** 更新时间 */
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
}, (table) => [
  index("idx_studentId").on(table.studentId),
  index("idx_status").on(table.status),
]);

export type SpecialRole = typeof specialRoles.$inferSelect;
export type InsertSpecialRole = typeof specialRoles.$inferInsert;

export type PurchaseRequest = typeof purchaseRequests.$inferSelect;
export type InsertPurchaseRequest = typeof purchaseRequests.$inferInsert;


// ==================== 管理员操作日志表 ====================
export const adminLogs = mysqlTable("adminLogs", {
  id: int("id").autoincrement().primaryKey(),
  /** 操作管理员ID */
  adminId: int("adminId").notNull(),
  /** 操作管理员姓名 */
  adminName: varchar("adminName", { length: 128 }),
  /** 操作类型 */
  action: varchar("action", { length: 64 }).notNull(),
  /** 操作模块 */
  module: varchar("module", { length: 64 }).notNull(),
  /** 操作目标类型（如：user, topic, config等） */
  targetType: varchar("targetType", { length: 64 }),
  /** 操作目标ID */
  targetId: int("targetId"),
  /** 操作目标名称 */
  targetName: varchar("targetName", { length: 256 }),
  /** 操作详情描述 */
  description: text("description"),
  /** 操作前数据（JSON格式） */
  beforeData: text("beforeData"),
  /** 操作后数据（JSON格式） */
  afterData: text("afterData"),
  /** IP地址 */
  ipAddress: varchar("ipAddress", { length: 64 }),
  /** 用户代理 */
  userAgent: text("userAgent"),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
}, (table) => [
  index("idx_adminId").on(table.adminId),
  index("idx_action").on(table.action),
  index("idx_module").on(table.module),
  index("idx_createdAt").on(table.createdAt),
]);

export type AdminLog = typeof adminLogs.$inferSelect;
export type InsertAdminLog = typeof adminLogs.$inferInsert;


// ==================== 用户活动日志表 ====================
export const userActivityLogs = mysqlTable("userActivityLogs", {
  id: int("id").autoincrement().primaryKey(),
  /** 操作用户ID */
  userId: int("userId").notNull(),
  /** 操作用户姓名 */
  userName: varchar("userName", { length: 128 }),
  /** 用户角色: admin, teacher, student */
  userRole: varchar("userRole", { length: 32 }).notNull(),
  /** 操作类型: login, logout, submit_wish, approve_wish, reject_wish, score_thesis, upload_thesis, update_config, create_topic, update_topic, delete_topic, assign_second_teacher, title_change_request, title_change_review, purchase_request, purchase_review, bulk_import, proxy_import, guidance_log, etc. */
  action: varchar("action", { length: 64 }).notNull(),
  /** 操作模块: auth, wish, topic, thesis, config, user, second_teacher, title_change, purchase, guidance, matching */
  module: varchar("module", { length: 64 }).notNull(),
  /** 操作目标类型（如：user, topic, thesis, wish, config等） */
  targetType: varchar("targetType", { length: 64 }),
  /** 操作目标ID */
  targetId: int("targetId"),
  /** 操作目标名称 */
  targetName: varchar("targetName", { length: 256 }),
  /** 操作详情描述 */
  description: text("description"),
  /** 操作结果: success, failure */
  result: varchar("result", { length: 16 }).default("success"),
  /** IP地址 */
  ipAddress: varchar("ipAddress", { length: 64 }),
  /** 用户代理 */
  userAgent: text("userAgent"),
  /** 创建时间 */
  createdAt: timestamp("createdAt").defaultNow().notNull(),
}, (table) => [
  index("idx_ual_userId").on(table.userId),
  index("idx_ual_userRole").on(table.userRole),
  index("idx_ual_action").on(table.action),
  index("idx_ual_module").on(table.module),
  index("idx_ual_createdAt").on(table.createdAt),
]);

export type UserActivityLog = typeof userActivityLogs.$inferSelect;
export type InsertUserActivityLog = typeof userActivityLogs.$inferInsert;
