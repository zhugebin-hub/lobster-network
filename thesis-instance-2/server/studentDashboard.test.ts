import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type CookieCall = {
  name: string;
  value?: string;
  options: Record<string, unknown>;
};

function createMockContext(user: TrpcContext["user"] = null): {
  ctx: TrpcContext;
  cookies: CookieCall[];
  clearedCookies: CookieCall[];
} {
  const cookies: CookieCall[] = [];
  const clearedCookies: CookieCall[] = [];

  const ctx: TrpcContext = {
    user,
    req: {
      protocol: "https",
      headers: {},
      ip: "127.0.0.1",
      get: () => "",
    } as unknown as TrpcContext["req"],
    res: {
      cookie: (name: string, value: string, options: Record<string, unknown>) => {
        cookies.push({ name, value, options });
      },
      clearCookie: (name: string, options: Record<string, unknown>) => {
        clearedCookies.push({ name, options });
      },
    } as TrpcContext["res"],
  };

  return { ctx, cookies, clearedCookies };
}

function createStudentContext(id: number = 3) {
  return createMockContext({
    id,
    openId: null,
    name: "Student Test",
    email: "student@test.com",
    loginMethod: null,
    role: "student",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
    password: "",
    teacherType: null,
    studentType: "non_transfer",
    studentMajor: "electronic_info",
    annualQuota: null,
    language: "zh",
    studentId: "S001",
    candidateNo: null,
    studentClass: "Class1",
    faculty: "萨塞克斯人工智能学院",
    initialPassword: "123456",
    teacherNo: "0000000",
    sussexEmail: null,
    sussexId: null,
    academicYear: "2024-2025",
    canPublish: 1,
    namePinyin: null,
  } as any);
}

function createAdminContext() {
  return createMockContext({
    id: 1,
    openId: null,
    name: "Admin",
    email: "root",
    loginMethod: null,
    role: "admin",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
    password: "",
    teacherType: null,
    studentType: null,
    studentMajor: null,
    annualQuota: null,
    language: "zh",
    studentId: null,
    candidateNo: null,
    studentClass: null,
    faculty: "萨塞克斯人工智能学院",
    initialPassword: "123456",
    teacherNo: "0000000",
    sussexEmail: null,
    sussexId: null,
    academicYear: null,
    canPublish: 1,
    namePinyin: null,
  } as any);
}

describe("Student Dashboard - getCurrentPhase API", () => {
  it("should return extended phase data with all required fields", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    // 验证基本字段存在
    expect(result).toHaveProperty("phase");
    expect(result).toHaveProperty("extendedPhase");
    expect(result).toHaveProperty("currentReviewPriority");
    expect(result).toHaveProperty("studentSelectionStart");
    expect(result).toHaveProperty("studentSelectionEnd");
    expect(result).toHaveProperty("teacherConfirmStart");
    expect(result).toHaveProperty("teacherConfirmEnd");
    expect(result).toHaveProperty("thesisUploadStart");
    expect(result).toHaveProperty("thesisUploadEnd");
    expect(result).toHaveProperty("scoringStart");
    expect(result).toHaveProperty("scoringEnd");
  });

  it("should return valid phase values", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    const validPhases = ["none", "student_selection", "teacher_confirm", "closed"];
    expect(validPhases).toContain(result.phase);

    const validExtendedPhases = [...validPhases, "thesis_upload", "scoring"];
    expect(validExtendedPhases).toContain(result.extendedPhase);
  });

  it("should return currentReviewPriority as a number", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    expect(typeof result.currentReviewPriority).toBe("number");
  });
});

describe("Student Dashboard - Wish Status API", () => {
  it("student can query wish status", async () => {
    const { ctx } = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.match.myWishStatus();
    expect(Array.isArray(result)).toBe(true);
  });

  it("student can query match status", async () => {
    const { ctx } = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.match.myMatch();
    // Should return null or match object
    expect(result === null || typeof result === "object").toBe(true);
  });

  it("student can query their wishes", async () => {
    const { ctx } = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.wish.myWishes();
    expect(Array.isArray(result)).toBe(true);
  });
});

describe("Student Dashboard - Unauthenticated access", () => {
  it("unauthenticated user cannot access getCurrentPhase", async () => {
    const { ctx } = createMockContext(null);
    const caller = appRouter.createCaller(ctx);

    await expect(caller.admin.getCurrentPhase()).rejects.toThrow();
  });

  it("unauthenticated user cannot access myWishStatus", async () => {
    const { ctx } = createMockContext(null);
    const caller = appRouter.createCaller(ctx);

    await expect(caller.match.myWishStatus()).rejects.toThrow();
  });
});
