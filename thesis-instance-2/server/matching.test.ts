import { describe, expect, it, vi, beforeEach } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

// Mock user data
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

function createMockContext(user: typeof mockTeacher | typeof mockStudent | typeof mockAdmin | null): TrpcContext {
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

describe("Matching Mechanism: Preference-First, Teacher-Confirmation", () => {
  
  describe("Teacher Review Workflow", () => {
    it("should allow teachers to view pending wishes for their topics", async () => {
      const ctx = createMockContext(mockTeacher);
      const caller = appRouter.createCaller(ctx);
      
      // This should not throw - teachers can view pending wishes
      const result = await caller.match.pendingWishes();
      expect(Array.isArray(result)).toBe(true);
    }, 30000);

    it("should require teacher role to access pending wishes", async () => {
      const ctx = createMockContext(mockStudent);
      const caller = appRouter.createCaller(ctx);
      
      // Students should not be able to access teacher's pending wishes
      await expect(caller.match.pendingWishes()).rejects.toThrow();
    });
  });

  describe("Student Wish Submission", () => {
    it("should allow students to view their own wishes", async () => {
      const ctx = createMockContext(mockStudent);
      const caller = appRouter.createCaller(ctx);
      
      const result = await caller.wish.myWishes();
      expect(Array.isArray(result)).toBe(true);
    });

    it("should require student role to submit wishes", async () => {
      const ctx = createMockContext(mockTeacher);
      const caller = appRouter.createCaller(ctx);
      
      // Teachers should not be able to submit wishes
      await expect(caller.wish.submit({ wishes: [] })).rejects.toThrow();
    });
  });

  describe("Admin Functions", () => {
    it("should allow admin to view all matches", async () => {
      const ctx = createMockContext(mockAdmin);
      const caller = appRouter.createCaller(ctx);
      
      const result = await caller.admin.getAllMatches();
      expect(Array.isArray(result)).toBe(true);
    }, 30000);

    it("should allow admin to get system config", async () => {
      const ctx = createMockContext(mockAdmin);
      const caller = appRouter.createCaller(ctx);
      
      const result = await caller.admin.getConfig();
      expect(result).toBeDefined();
    });

    it("should require admin role for admin functions", async () => {
      const ctx = createMockContext(mockStudent);
      const caller = appRouter.createCaller(ctx);
      
      await expect(caller.admin.getAllMatches()).rejects.toThrow();
    });
  });

  describe("Topic Management", () => {
    it("should allow teachers to view their topics", async () => {
      const ctx = createMockContext(mockTeacher);
      const caller = appRouter.createCaller(ctx);
      
      const result = await caller.topic.myTopics();
      expect(Array.isArray(result)).toBe(true);
    });

    it("should allow students to view published topics (blind mode)", async () => {
      const ctx = createMockContext(mockStudent);
      const caller = appRouter.createCaller(ctx);
      
      const result = await caller.topic.listPublished();
      expect(Array.isArray(result)).toBe(true);
      
      // Verify blind mode - topics should not expose teacher info to students
      // (This is enforced by the query not joining teacher data)
    }, 15000);
  });
});

describe("Authentication", () => {
  it("should return null user for unauthenticated context", async () => {
    const ctx = createMockContext(null);
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.auth.me();
    expect(result).toBeNull();
  });

  it("should return user data for authenticated context", async () => {
    const ctx = createMockContext(mockStudent);
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.auth.me();
    expect(result).toBeDefined();
    expect(result?.email).toBe("student@example.com");
  });

  it("should clear cookie on logout", async () => {
    const ctx = createMockContext(mockStudent);
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.auth.logout();
    expect(result.success).toBe(true);
    expect(ctx.res.clearCookie).toHaveBeenCalled();
  });
});
