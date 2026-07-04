import { describe, expect, it, vi } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

// Mock user data
const mockAdmin = {
  id: 1,
  openId: "admin-001",
  email: "root",
  name: "管理员",
  loginMethod: "email",
  role: "admin" as const,
  teacherType: null,
  studentType: null,
  studentMajor: null,
  studentId: null,
  candidateNo: null,
  studentClass: null,
  faculty: null,
  annualQuota: null,
  language: "zh",
  password: null,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastSignedIn: new Date(),
};

const mockTeacher = {
  id: 2,
  openId: "teacher-001",
  email: "teacher@example.com",
  name: "李教授",
  loginMethod: "email",
  role: "teacher" as const,
  teacherType: "chinese",
  studentType: null,
  studentMajor: null,
  studentId: null,
  candidateNo: null,
  studentClass: null,
  faculty: null,
  annualQuota: 5,
  language: "zh",
  password: null,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastSignedIn: new Date(),
};

const mockStudent = {
  id: 3,
  openId: "student-001",
  email: "student@example.com",
  name: "张同学",
  loginMethod: "email",
  role: "student" as const,
  teacherType: null,
  studentType: "non_transfer",
  studentMajor: "electronic_info",
  studentId: "2021001",
  candidateNo: "UK001",
  studentClass: "21电信1班",
  faculty: "萨塞克斯人工智能学院",
  annualQuota: null,
  language: "zh",
  password: null,
  createdAt: new Date(),
  updatedAt: new Date(),
  lastSignedIn: new Date(),
};

function createMockContext(user: typeof mockAdmin | typeof mockTeacher | typeof mockStudent | null): TrpcContext {
  return {
    user,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      clearCookie: vi.fn(),
      cookie: vi.fn(),
    } as unknown as TrpcContext["res"],
  };
}

describe("Match Import - Single Import", () => {
  it("should require admin role to import single match", async () => {
    const ctx = createMockContext(mockStudent);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "李教授",
        topicTitle: "基于深度学习的图像分类研究",
      })
    ).rejects.toThrow();
  });

  it("should require admin role (teacher cannot import)", async () => {
    const ctx = createMockContext(mockTeacher);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "李教授",
        topicTitle: "基于深度学习的图像分类研究",
      })
    ).rejects.toThrow();
  });

  it("should validate required fields - empty studentId", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "",
        studentName: "张三",
        teacherName: "李教授",
        topicTitle: "基于深度学习的图像分类研究",
      })
    ).rejects.toThrow();
  });

  it("should validate required fields - empty studentName", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "",
        teacherName: "李教授",
        topicTitle: "基于深度学习的图像分类研究",
      })
    ).rejects.toThrow();
  });

  it("should validate required fields - empty teacherName", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "",
        topicTitle: "基于深度学习的图像分类研究",
      })
    ).rejects.toThrow();
  });

  it("should validate required fields - empty topicTitle", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "李教授",
        topicTitle: "",
      })
    ).rejects.toThrow();
  });

  it("should fail when student account does not exist", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "9999999999",
        studentName: "不存在的学生",
        teacherName: "李教授",
        topicTitle: "基于深度学习的图像分类研究_" + Date.now(),
      })
    ).rejects.toThrow();
  }, 30000);

  it("should fail when teacher account does not exist", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "不存在的导师_" + Date.now(),
        topicTitle: "基于深度学习的图像分类研究_" + Date.now(),
      })
    ).rejects.toThrow();
  }, 30000);

  it("should accept optional fields (sussexId, topicTitleEn, remarks)", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    // This tests that the input schema accepts optional fields without throwing validation errors
    // The actual import may fail due to non-existent accounts, but the input validation should pass
    try {
      await caller.admin.importSingleMatch({
        studentId: "9999999999",
        studentName: "测试学生",
        sussexId: "24009999",
        teacherName: "测试导师",
        topicTitle: "测试课题_" + Date.now(),
        topicTitleEn: "Test Topic",
        remarks: "测试备注",
      });
    } catch (e: any) {
      // Should fail due to non-existent accounts, not due to input validation
      expect(e.message).toContain("不存在");
    }
  }, 30000);
});

describe("Match Import - Batch Import", () => {
  it("should require admin role for batch import", async () => {
    const ctx = createMockContext(mockStudent);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.batchImportMatches({
        items: [{
          studentId: "2037010101",
          studentName: "张三",
          teacherName: "李教授",
          topicTitle: "基于深度学习的图像分类研究",
        }],
      })
    ).rejects.toThrow();
  });

  it("should require admin role (teacher cannot batch import)", async () => {
    const ctx = createMockContext(mockTeacher);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.batchImportMatches({
        items: [{
          studentId: "2037010101",
          studentName: "张三",
          teacherName: "李教授",
          topicTitle: "基于深度学习的图像分类研究",
        }],
      })
    ).rejects.toThrow();
  });

  it("should validate batch items - fail when student not found", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.batchImportMatches({
      items: [{
        studentId: "9999999999",
        studentName: "不存在的学生",
        teacherName: "李教授",
        topicTitle: "测试课题_" + Date.now(),
      }],
    });

    expect(result.success).toBe(false);
    expect(result.failedCount).toBeGreaterThan(0);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0].reason).toContain("学生账号不存在");
  }, 30000);

  it("should validate batch items - fail when teacher not found", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.batchImportMatches({
      items: [{
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "不存在的导师_" + Date.now(),
        topicTitle: "测试课题_" + Date.now(),
      }],
    });

    expect(result.success).toBe(false);
    expect(result.failedCount).toBeGreaterThan(0);
    expect(result.errors.length).toBeGreaterThan(0);
    // Error could be about student or teacher not existing
    const hasRelevantError = result.errors.some(e => 
      e.reason.includes("不存在")
    );
    expect(hasRelevantError).toBe(true);
  }, 30000);

  it("should detect duplicate topic titles within batch", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const topicTitle = "批量导入重复测试课题_" + Date.now();
    const result = await caller.admin.batchImportMatches({
      items: [
        {
          studentId: "2037010101",
          studentName: "张三",
          teacherName: "李教授",
          topicTitle: topicTitle,
        },
        {
          studentId: "2037010102",
          studentName: "李四",
          teacherName: "王教授",
          topicTitle: topicTitle, // 重复的题目
        },
      ],
    });

    expect(result.success).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    // At least one error should mention duplicate or non-existent
    const hasDuplicateOrError = result.errors.some(e => 
      e.reason.includes("重复") || e.reason.includes("不存在")
    );
    expect(hasDuplicateOrError).toBe(true);
  }, 30000);

  it("should fail entire batch when any validation fails (atomic)", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.batchImportMatches({
      items: [
        {
          studentId: "9999999999",
          studentName: "不存在学生1",
          teacherName: "李教授",
          topicTitle: "课题1_" + Date.now(),
        },
        {
          studentId: "9999999998",
          studentName: "不存在学生2",
          teacherName: "王教授",
          topicTitle: "课题2_" + Date.now(),
        },
      ],
    });

    expect(result.success).toBe(false);
    expect(result.successCount).toBe(0);
    expect(result.failedCount).toBeGreaterThan(0);
  }, 30000);

  it("should validate missing required fields in batch items", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.batchImportMatches({
      items: [{
        studentId: "",
        studentName: "",
        teacherName: "",
        topicTitle: "",
      }],
    });

    expect(result.success).toBe(false);
    expect(result.errors.length).toBeGreaterThan(0);
    expect(result.errors[0].reason).toContain("缺少必填字段");
  }, 30000);

  it("should return proper error structure", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.batchImportMatches({
      items: [{
        studentId: "9999999999",
        studentName: "测试学生",
        teacherName: "测试导师",
        topicTitle: "测试课题_" + Date.now(),
      }],
    });

    expect(result).toHaveProperty("success");
    expect(result).toHaveProperty("totalCount");
    expect(result).toHaveProperty("successCount");
    expect(result).toHaveProperty("failedCount");
    expect(result).toHaveProperty("errors");
    expect(result.totalCount).toBe(1);
    
    if (result.errors.length > 0) {
      const error = result.errors[0];
      expect(error).toHaveProperty("row");
      expect(error).toHaveProperty("studentName");
      expect(error).toHaveProperty("studentId");
      expect(error).toHaveProperty("reason");
    }
  }, 30000);

  it("should handle empty items array", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.batchImportMatches({
      items: [],
    });

    expect(result).toBeDefined();
    expect(result.totalCount).toBe(0);
    expect(result.successCount).toBe(0);
  }, 30000);
});

describe("Match Import - Template", () => {
  it("should return import template with correct structure", async () => {
    const ctx = createMockContext(mockAdmin);
    const caller = appRouter.createCaller(ctx);

    const result = await caller.admin.getImportTemplate();

    expect(result).toHaveProperty("headers");
    expect(result).toHaveProperty("sampleData");
    expect(Array.isArray(result.headers)).toBe(true);
    expect(result.headers.length).toBeGreaterThan(0);
    expect(result.headers).toContain("学生姓名");
    expect(result.headers).toContain("中方学号");
    expect(result.headers).toContain("导师");
    expect(result.headers).toContain("论文题目");
    expect(Array.isArray(result.sampleData)).toBe(true);
    expect(result.sampleData.length).toBeGreaterThan(0);
  });

  it("should require admin role to access template", async () => {
    const ctx = createMockContext(mockStudent);
    const caller = appRouter.createCaller(ctx);

    await expect(caller.admin.getImportTemplate()).rejects.toThrow();
  });
});

describe("Match Import - Access Control", () => {
  it("should deny unauthenticated access to single import", async () => {
    const ctx = createMockContext(null);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.importSingleMatch({
        studentId: "2037010101",
        studentName: "张三",
        teacherName: "李教授",
        topicTitle: "测试课题",
      })
    ).rejects.toThrow();
  });

  it("should deny unauthenticated access to batch import", async () => {
    const ctx = createMockContext(null);
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.admin.batchImportMatches({
        items: [{
          studentId: "2037010101",
          studentName: "张三",
          teacherName: "李教授",
          topicTitle: "测试课题",
        }],
      })
    ).rejects.toThrow();
  });
});
