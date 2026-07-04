import { int, mysqlEnum, mysqlTable, text, varchar, timestamp, json, longtext } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * 科研申报书项目表
 * 基于国家重点研发计划官方模板设计
 */
export const proposals = mysqlTable("proposals", {
  id: int("id").autoincrement().primaryKey(),
  userId: int("userId").notNull(),

  // 基本信息
  title: varchar("title", { length: 255 }).notNull(),
  abstract: text("abstract"),
  researchField: varchar("researchField", { length: 100 }),
  proposalType: mysqlEnum("proposalType", [
    "national_key_rd",
    "national_sci_tech",
    "nsfc",
  ]).notNull(),

  // 申报单位信息
  applicantUnit: varchar("applicantUnit", { length: 255 }),
  applicantUnitAddress: varchar("applicantUnitAddress", { length: 255 }),
  applicantUnitCode: varchar("applicantUnitCode", { length: 50 }),

  // 推荐单位信息
  recommendingUnit: varchar("recommendingUnit", { length: 255 }),
  recommendingUnitNature: varchar("recommendingUnitNature", { length: 100 }),

  // 项目负责人信息
  principalInvestigatorName: varchar("principalInvestigatorName", {
    length: 100,
  }),
  principalInvestigatorEmail: varchar("principalInvestigatorEmail", {
    length: 100,
  }),
  principalInvestigatorPhone: varchar("principalInvestigatorPhone", {
    length: 20,
  }),

  // 项目联系人信息
  contactPersonName: varchar("contactPersonName", { length: 100 }),
  contactPersonEmail: varchar("contactPersonEmail", { length: 100 }),
  contactPersonPhone: varchar("contactPersonPhone", { length: 20 }),

  // 经费信息
  totalBudget: int("totalBudget"),
  centralFunding: int("centralFunding"),
  localFunding: int("localFunding"),
  unitFunding: int("unitFunding"),

  // 工作流状态
  currentStep: varchar("currentStep", { length: 50 }).default("basic_info"),
  workflowState: json("workflowState"),

  // 时间戳
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Proposal = typeof proposals.$inferSelect;
export type InsertProposal = typeof proposals.$inferInsert;

/**
 * 申报书章节内容表
 * 支持官方模板的8个部分
 */
export const sections = mysqlTable("sections", {
  id: int("id").autoincrement().primaryKey(),
  proposalId: int("proposalId").notNull(),
  sectionKey: varchar("sectionKey", { length: 50 }).notNull(),
  title: varchar("title", { length: 255 }).notNull(),
  content: longtext("content"),
  userRequirements: longtext("userRequirements"),
  wordCount: int("wordCount"),
  maxWords: int("maxWords"),
  status: mysqlEnum("status", [
    "pending",
    "generating",
    "draft_ready",
    "confirmed",
    "revising",
  ])
    .default("pending")
    .notNull(),
  version: int("version").default(1),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  confirmedAt: timestamp("confirmedAt"),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
});

export type Section = typeof sections.$inferSelect;
export type InsertSection = typeof sections.$inferInsert;

/**
 * 参与单位表
 */
export const cooperatingUnits = mysqlTable("cooperatingUnits", {
  id: int("id").autoincrement().primaryKey(),
  proposalId: int("proposalId").notNull(),
  unitName: varchar("unitName", { length: 255 }).notNull(),
  unitNature: varchar("unitNature", { length: 100 }),
  organizationCode: varchar("organizationCode", { length: 50 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type CooperatingUnit = typeof cooperatingUnits.$inferSelect;
export type InsertCooperatingUnit = typeof cooperatingUnits.$inferInsert;

/**
 * 团队成员表
 */
export const teamMembers = mysqlTable("teamMembers", {
  id: int("id").autoincrement().primaryKey(),
  proposalId: int("proposalId").notNull(),
  name: varchar("name", { length: 100 }).notNull(),
  role: varchar("role", { length: 100 }),
  degree: varchar("degree", { length: 50 }),
  title: varchar("title", { length: 100 }),
  email: varchar("email", { length: 100 }),
  phone: varchar("phone", { length: 20 }),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type TeamMember = typeof teamMembers.$inferSelect;
export type InsertTeamMember = typeof teamMembers.$inferInsert;

/**
 * 经费预算表
 */
export const budgetDetails = mysqlTable("budgetDetails", {
  id: int("id").autoincrement().primaryKey(),
  proposalId: int("proposalId").notNull(),
  taskName: varchar("taskName", { length: 255 }).notNull(),
  responsibleUnit: varchar("responsibleUnit", { length: 255 }),
  totalBudget: int("totalBudget"),
  centralFunding: int("centralFunding"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type BudgetDetail = typeof budgetDetails.$inferSelect;
export type InsertBudgetDetail = typeof budgetDetails.$inferInsert;

/**
 * 操作历史日志表
 */
export const operationLogs = mysqlTable("operationLogs", {
  id: int("id").autoincrement().primaryKey(),
  proposalId: int("proposalId").notNull(),
  action: varchar("action", { length: 50 }).notNull(),
  sectionKey: varchar("sectionKey", { length: 50 }),
  detail: text("detail"),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
});

export type OperationLog = typeof operationLogs.$inferSelect;
export type InsertOperationLog = typeof operationLogs.$inferInsert;
