import { describe, expect, it, beforeAll } from "vitest";
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

function createTeacherContext(id: number = 2) {
  return createMockContext({
    id,
    openId: null,
    name: "Teacher Test",
    email: "teacher@test.com",
    loginMethod: null,
    role: "teacher",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
    password: "",
    teacherType: "chinese",
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

// ==================== Role-based Access Control Tests ====================
describe("Role-based access control", () => {
  it("admin can access admin procedures", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    // Admin should be able to get all users
    const users = await caller.admin.getUsers();
    expect(Array.isArray(users)).toBe(true);
  });

  it("teacher cannot access admin procedures", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    await expect(caller.admin.getUsers()).rejects.toThrow();
  });

  it("student cannot access admin procedures", async () => {
    const { ctx } = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    await expect(caller.admin.getUsers()).rejects.toThrow();
  });

  it("unauthenticated user cannot access protected procedures", async () => {
    const { ctx } = createMockContext(null);
    const caller = appRouter.createCaller(ctx);

    await expect(caller.admin.getUsers()).rejects.toThrow();
  });
});

// ==================== System Config Tests ====================
describe("System config", () => {
  it("admin can get system configs", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const configs = await caller.admin.getConfigs();
    expect(configs).toBeDefined();
  });
});

// ==================== Topic Management Tests ====================
describe("Topic management", () => {
  it("teacher can get their topics", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    const topics = await caller.topic.myTopics();
    expect(Array.isArray(topics)).toBe(true);
  });

  it("student cannot create topics", async () => {
    const { ctx } = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.topic.create({
        title: "Test Topic",
        description: "Test Description",
      })
    ).rejects.toThrow();
  });
});

// ==================== Academic Year Tests ====================
describe("Academic year management", () => {
  it("admin can get academic years", async () => {
    const { ctx } = createAdminContext();
    const caller = appRouter.createCaller(ctx);

    const years = await caller.admin.getAllYears();
    expect(Array.isArray(years)).toBe(true);
  });
});

// ==================== Wish (Selection) Tests ====================
describe("Wish submission", () => {
  it("student can get their wishes", async () => {
    const { ctx } = createStudentContext();
    const caller = appRouter.createCaller(ctx);

    const wishes = await caller.wish.myWishes();
    expect(Array.isArray(wishes)).toBe(true);
  });

  it("teacher can get pending wishes for review", async () => {
    const { ctx } = createTeacherContext();
    const caller = appRouter.createCaller(ctx);

    const wishes = await caller.match.pendingWishes();
    expect(Array.isArray(wishes)).toBe(true);
  });
});
