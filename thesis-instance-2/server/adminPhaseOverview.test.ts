import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

function createMockContext(user: TrpcContext["user"] = null): {
  ctx: TrpcContext;
} {
  const ctx: TrpcContext = {
    user,
    req: {
      protocol: "https",
      headers: {},
      ip: "127.0.0.1",
      get: () => "",
    } as unknown as TrpcContext["req"],
    res: {
      cookie: () => {},
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
  return { ctx };
}

function createAdminContext() {
  return createMockContext({
    id: 1,
    openId: null,
    name: "Admin Test",
    email: "admin@test.com",
    loginMethod: null,
    role: "admin",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
    password: "",
    teacherType: null,
    studentType: null,
    studentMajor: null,
    annualQuota: 0,
    language: "zh",
    studentId: null,
    candidateNo: null,
    studentClass: null,
    faculty: null,
    initialPassword: null,
    teacherNo: null,
    sussexEmail: null,
    sussexId: null,
    academicYear: null,
    canPublish: 0,
    namePinyin: null,
  } as any);
}

describe("Admin Dashboard - Phase Overview Panel", () => {
  it("admin can access getCurrentPhase with all phase time fields", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    // 验证基础字段
    expect(result).toHaveProperty("phase");
    expect(result).toHaveProperty("extendedPhase");
    expect(result).toHaveProperty("currentReviewPriority");

    // 验证所有时间段字段
    expect(result).toHaveProperty("studentSelectionStart");
    expect(result).toHaveProperty("studentSelectionEnd");
    expect(result).toHaveProperty("teacherConfirmStart");
    expect(result).toHaveProperty("teacherConfirmEnd");
    expect(result).toHaveProperty("thesisUploadStart");
    expect(result).toHaveProperty("thesisUploadEnd");
    expect(result).toHaveProperty("scoringStart");
    expect(result).toHaveProperty("scoringEnd");
  });

  it("phase and extendedPhase should be valid values", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    const validPhases = ["none", "student_selection", "teacher_confirm", "closed"];
    const validExtendedPhases = ["none", "student_selection", "teacher_confirm", "closed", "thesis_upload", "scoring"];

    expect(validPhases).toContain(result.phase);
    expect(validExtendedPhases).toContain(result.extendedPhase);
  });

  it("currentReviewPriority should be a non-negative number", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();
    expect(typeof result.currentReviewPriority).toBe("number");
    expect(result.currentReviewPriority).toBeGreaterThanOrEqual(-1);
  });

  it("time fields should be string or null", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    const timeFields = [
      "studentSelectionStart", "studentSelectionEnd",
      "teacherConfirmStart", "teacherConfirmEnd",
      "thesisUploadStart", "thesisUploadEnd",
      "scoringStart", "scoringEnd",
    ] as const;

    for (const field of timeFields) {
      const val = result[field];
      expect(val === null || val === undefined || typeof val === "string").toBe(true);
    }
  });
});
