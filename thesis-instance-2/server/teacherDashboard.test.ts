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

function createTeacherContext() {
  return createMockContext({
    id: 2,
    openId: null,
    name: "Teacher Test",
    email: "teacher@sussex.ac.uk",
    loginMethod: null,
    role: "teacher",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
    password: "",
    teacherType: "sussex",
    studentType: null,
    studentMajor: null,
    annualQuota: 5,
    language: "zh",
    studentId: null,
    candidateNo: null,
    studentClass: null,
    faculty: "萨塞克斯人工智能学院",
    initialPassword: "123456",
    teacherNo: "T001",
    sussexEmail: "teacher@sussex.ac.uk",
    sussexId: null,
    academicYear: null,
    canPublish: 1,
    namePinyin: null,
  } as any);
}

describe("Teacher Dashboard - getCurrentPhase API for teacher", () => {
  it("teacher can access getCurrentPhase and get all required fields", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    // 验证所有必需字段
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

  it("phase should be a valid value", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    const validPhases = ["none", "student_selection", "teacher_confirm", "closed"];
    expect(validPhases).toContain(result.phase);
  });

  it("extendedPhase should be a valid value", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();

    const validExtendedPhases = ["none", "student_selection", "teacher_confirm", "closed", "thesis_upload", "scoring"];
    expect(validExtendedPhases).toContain(result.extendedPhase);
  });

  it("currentReviewPriority should be a number", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getCurrentPhase();
    expect(typeof result.currentReviewPriority).toBe("number");
  });

  it("unauthenticated user cannot access getCurrentPhase", async () => {
    const { ctx } = createMockContext(null);
    const caller = appRouter.createCaller(ctx);

    await expect(caller.admin.getCurrentPhase()).rejects.toThrow();
  });
});
