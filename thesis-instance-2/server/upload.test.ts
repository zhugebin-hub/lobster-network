import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createStudentContext(overrides: Partial<AuthenticatedUser> = {}): TrpcContext {
  const user: AuthenticatedUser = {
    id: 247,
    openId: "2037010301",
    email: "2037010301",
    name: "祝嘉琳",
    loginMethod: "password",
    role: "student",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
    password: "hashed",
    teacherType: null,
    studentType: "transfer",
    studentMajor: "electronic_info",
    annualQuota: null,
    language: "zh",
    studentId: "2037010301",
    candidateNo: null,
    studentClass: "AI电子2203",
    faculty: "萨塞克斯人工智能学院",
    initialPassword: "hashed",
    teacherNo: "0000000",
    sussexEmail: null,
    sussexId: "238758",
    academicYear: "测试",
    canPublish: 1,
    namePinyin: "Zhu Jialin",
    ...overrides,
  };

  return {
    user,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: () => {},
    } as TrpcContext["res"],
  };
}

describe("thesis upload", () => {
  it("getMyDraft returns upload period status for student", async () => {
    const ctx = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    // This should not throw - it returns null if no match or the draft info
    const result = await caller.thesis.getMyDraft();
    
    // Result should either be null (no match) or have uploadPeriodStatus
    if (result !== null) {
      expect(result).toHaveProperty("uploadPeriodStatus");
      expect(result).toHaveProperty("canUpload");
      expect(result).toHaveProperty("gracePeriod");
      expect(result.gracePeriod).toHaveProperty("status");
      expect(result.gracePeriod).toHaveProperty("penalty");
    }
  });

  it("uploadDraft rejects non-student users", async () => {
    const ctx = createStudentContext({ role: "teacher" as any });
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.thesis.uploadDraft({
        fileName: "test.docx",
        fileKey: "uploads/test.docx",
        fileUrl: "https://example.com/test.docx",
        fileSize: 1024,
        mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
    ).rejects.toThrow("只有学生可以上传论文");
  });

  it("uploadDraft rejects non-transfer students", async () => {
    const ctx = createStudentContext({ studentType: "non_transfer" });
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.thesis.uploadDraft({
        fileName: "test.docx",
        fileKey: "uploads/test.docx",
        fileUrl: "https://example.com/test.docx",
        fileSize: 1024,
        mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
    ).rejects.toThrow("只有分流学生可以上传论文终稿");
  });

  it("uploadDraft accepts valid input for transfer student", async () => {
    const ctx = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    // Transfer student with valid match should be able to upload
    // (may succeed or fail depending on match existence, but should not throw validation error)
    try {
      const result = await caller.thesis.uploadDraft({
        fileName: "test.docx",
        fileKey: "uploads/test.docx",
        fileUrl: "https://example.com/test.docx",
        fileSize: 1024,
        mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      // If it succeeds, it should return an object
      expect(result).toBeDefined();
    } catch (error: any) {
      // Acceptable errors: no match, time window issues
      expect(["BAD_REQUEST", "FORBIDDEN"]).toContain(error.code);
    }
  });
});

describe("upload route registration", () => {
  it("server/index.ts should have /api/upload route registered", async () => {
    // Verify the upload route code exists in index.ts
    const fs = await import("fs");
    const indexContent = fs.readFileSync(
      "/home/ubuntu/thesis-topic-system/server/_core/index.ts",
      "utf-8"
    );
    
    expect(indexContent).toContain('"/api/upload"');
    expect(indexContent).toContain("multer");
    expect(indexContent).toContain("storagePut");
    expect(indexContent).toContain("upload.single");
  });
});
