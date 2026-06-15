import { eq, desc, and } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import {
  InsertUser,
  users,
  proposals,
  sections,
  cooperatingUnits,
  teamMembers,
  budgetDetails,
  operationLogs,
  type InsertProposal,
  type InsertSection,
  type InsertCooperatingUnit,
  type InsertTeamMember,
  type InsertBudgetDetail,
  type InsertOperationLog,
} from "../drizzle/schema";
import { ENV } from "./_core/env";

let _db: ReturnType<typeof drizzle> | null = null;

export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

// ==================== User helpers ====================

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) throw new Error("User openId is required for upsert");
  const db = await getDb();
  if (!db) { console.warn("[Database] Cannot upsert user: database not available"); return; }

  try {
    const values: InsertUser = { openId: user.openId };
    const updateSet: Record<string, unknown> = {};
    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];
    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };
    textFields.forEach(assignNullable);
    if (user.lastSignedIn !== undefined) { values.lastSignedIn = user.lastSignedIn; updateSet.lastSignedIn = user.lastSignedIn; }
    if (user.role !== undefined) { values.role = user.role; updateSet.role = user.role; }
    else if (user.openId === ENV.ownerOpenId) { values.role = "admin"; updateSet.role = "admin"; }
    if (!values.lastSignedIn) values.lastSignedIn = new Date();
    if (Object.keys(updateSet).length === 0) updateSet.lastSignedIn = new Date();
    await db.insert(users).values(values).onDuplicateKeyUpdate({ set: updateSet });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) { console.warn("[Database] Cannot get user: database not available"); return undefined; }
  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

// ==================== Proposal helpers ====================

export async function createProposal(userId: number, data: Omit<InsertProposal, "userId" | "id" | "createdAt" | "updatedAt">) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const result = await db.insert(proposals).values({ userId, ...data });
  // MySQL returns insertId in the result header
  const insertId = (result as any)[0]?.insertId;
  if (insertId) return { insertId };

  // fallback: query the latest proposal by this user
  const latest = await db
    .select()
    .from(proposals)
    .where(eq(proposals.userId, userId))
    .orderBy(desc(proposals.createdAt))
    .limit(1);
  return { insertId: latest[0]?.id };
}

export async function getProposalById(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db.select().from(proposals).where(eq(proposals.id, proposalId)).limit(1);
  return result[0] ?? null;
}

export async function getProposalsByUserId(userId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.select().from(proposals).where(eq(proposals.userId, userId)).orderBy(desc(proposals.createdAt));
}

export async function updateProposal(proposalId: number, data: Partial<InsertProposal>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.update(proposals).set(data).where(eq(proposals.id, proposalId));
}

export async function deleteProposal(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.delete(proposals).where(eq(proposals.id, proposalId));
}

// ==================== Section helpers ====================

export async function createSection(proposalId: number, data: Omit<InsertSection, "proposalId" | "id" | "createdAt" | "updatedAt">) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.insert(sections).values({ proposalId, ...data });
}

export async function getProposalSections(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.select().from(sections).where(eq(sections.proposalId, proposalId)).orderBy(sections.id);
}

export async function getSectionByKey(proposalId: number, sectionKey: string) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  const result = await db
    .select()
    .from(sections)
    .where(and(eq(sections.proposalId, proposalId), eq(sections.sectionKey, sectionKey)))
    .limit(1);
  return result[0] ?? null;
}

export async function updateSection(sectionId: number, data: Partial<InsertSection>) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.update(sections).set(data).where(eq(sections.id, sectionId));
}

// ==================== CooperatingUnit helpers ====================

export async function addCooperatingUnit(proposalId: number, data: Omit<InsertCooperatingUnit, "proposalId" | "id" | "createdAt">) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.insert(cooperatingUnits).values({ proposalId, ...data });
}

export async function getCooperatingUnits(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.select().from(cooperatingUnits).where(eq(cooperatingUnits.proposalId, proposalId));
}

// ==================== TeamMember helpers ====================

export async function addTeamMember(proposalId: number, data: Omit<InsertTeamMember, "proposalId" | "id" | "createdAt">) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.insert(teamMembers).values({ proposalId, ...data });
}

export async function getTeamMembers(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.select().from(teamMembers).where(eq(teamMembers.proposalId, proposalId));
}

// ==================== BudgetDetail helpers ====================

export async function addBudgetDetail(proposalId: number, data: Omit<InsertBudgetDetail, "proposalId" | "id" | "createdAt">) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.insert(budgetDetails).values({ proposalId, ...data });
}

export async function getBudgetDetails(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.select().from(budgetDetails).where(eq(budgetDetails.proposalId, proposalId));
}

// ==================== OperationLog helpers ====================

export async function addOperationLog(proposalId: number, data: Omit<InsertOperationLog, "proposalId" | "id" | "createdAt">) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  await db.insert(operationLogs).values({ proposalId, ...data });
}

export async function getOperationLogs(proposalId: number) {
  const db = await getDb();
  if (!db) throw new Error("Database not available");
  return db.select().from(operationLogs).where(eq(operationLogs.proposalId, proposalId)).orderBy(desc(operationLogs.createdAt));
}
