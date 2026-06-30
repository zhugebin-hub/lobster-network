import { describe, it, expect, vi } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createAdminContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "admin-proxy-test",
    email: "root",
    name: "Admin",
    loginMethod: "password",
    role: "admin",
    teacherType: null,
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
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

function createTeacherContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 2,
    openId: "teacher-proxy-test",
    email: "teacher@example.com",
    name: "Teacher",
    loginMethod: "password",
    role: "teacher",
    teacherType: "english",
    createdAt: new Date(),
    updatedAt: new Date(),
    lastSignedIn: new Date(),
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

describe("Admin Proxy Bulk Import", () => {
  describe("proxyBulkImport procedure", () => {
    it("should reject non-admin users", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      try {
        await caller.admin.proxyBulkImport({
          topics: [{
            teacherEmail: "root",
            titleEn: "Test Topic",
            descriptionEn: "Test description",
            keywords: "AI, ML, DL",
            researchFocus: "Computer Vision",
          }],
          autoPublish: false,
        });
        expect.fail("Should have thrown FORBIDDEN error");
      } catch (error: any) {
        expect(error.code).toBe("FORBIDDEN");
      }
    });

    it("should handle non-existent teacher email gracefully", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.proxyBulkImport({
        topics: [{
          teacherEmail: "nonexistent@example.com",
          titleEn: `Proxy Test ${Date.now()}-1`,
          descriptionEn: "Test description for proxy import",
          keywords: "AI, ML, DL",
          researchFocus: "Computer Vision",
        }],
        autoPublish: false,
      });

      expect(result.failed).toBe(1);
      expect(result.success).toBe(0);
      expect(result.errors.length).toBe(1);
      expect(result.errors[0]).toContain("未找到导师账号");
    });

    it("should validate required fields via zod schema", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      try {
        await caller.admin.proxyBulkImport({
          topics: [{
            teacherEmail: "",
            titleEn: "",
            descriptionEn: "",
            keywords: "",
            researchFocus: "",
          }],
          autoPublish: false,
        });
        expect.fail("Should have thrown validation error");
      } catch (error: any) {
        // Zod validation should reject empty required fields
        expect(error).toBeDefined();
      }
    });

    it("should validate topic source and research project name rules", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      // Test: when topicSource is "其他", researchProjectName must be empty
      const result = await caller.admin.proxyBulkImport({
        topics: [{
          teacherEmail: "root",
          titleEn: `Proxy Validation Test ${Date.now()}`,
          descriptionEn: "Test description",
          keywords: "AI, ML, DL",
          researchFocus: "Computer Vision",
          topicSource: "其他",
          researchProjectName: "Some Project",
        }],
        autoPublish: false,
      });

      // Should fail because topicSource is "其他" but researchProjectName is provided
      expect(result.failed).toBe(1);
      expect(result.errors[0]).toContain("科研项目名称必须为空");
    });

    it("should return correct result structure", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.proxyBulkImport({
        topics: [{
          teacherEmail: "root",
          titleEn: `Proxy Structure Test ${Date.now()}`,
          descriptionEn: "Test description for structure check",
          keywords: "AI, ML, DL",
          researchFocus: "Computer Vision",
          topicSource: "其他",
        }],
        autoPublish: false,
      });

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("failed");
      expect(result).toHaveProperty("errors");
      expect(result).toHaveProperty("total");
      expect(typeof result.success).toBe("number");
      expect(typeof result.failed).toBe("number");
      expect(Array.isArray(result.errors)).toBe(true);
      expect(result.total).toBe(1);
    });
  });

  describe("getTeacherList procedure", () => {
    it("should return teacher list for admin users", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const teachers = await caller.admin.getTeacherList();

      expect(Array.isArray(teachers)).toBe(true);
      // Each teacher should have expected fields
      if (teachers.length > 0) {
        const teacher = teachers[0];
        expect(teacher).toHaveProperty("id");
        expect(teacher).toHaveProperty("name");
        expect(teacher).toHaveProperty("email");
        expect(teacher).toHaveProperty("teacherType");
        expect(teacher).toHaveProperty("canPublish");
        expect(teacher).toHaveProperty("annualQuota");
      }
    });

    it("should reject non-admin users", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      try {
        await caller.admin.getTeacherList();
        expect.fail("Should have thrown FORBIDDEN error");
      } catch (error: any) {
        expect(error.code).toBe("FORBIDDEN");
      }
    });
  });
});
