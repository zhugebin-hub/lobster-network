import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createAdminContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "admin-user",
    email: "admin@example.com",
    name: "Admin User",
    loginMethod: "manus",
    role: "admin",
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
    openId: "teacher-user",
    email: "teacher@example.com",
    name: "Teacher User",
    loginMethod: "manus",
    role: "teacher",
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

describe("Chinese Teacher Monitoring", () => {
  describe("admin.getChineseTeacherTopicMonitoring", () => {
    it("should return monitoring statistics for admin", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.getChineseTeacherTopicMonitoring();

      // Verify the result structure
      expect(result).toHaveProperty("publishedTopicsCount");
      expect(result).toHaveProperty("usedTopicsCount");
      expect(result).toHaveProperty("unusedTopicsCount");
      expect(result).toHaveProperty("pendingTransferStudentsCount");
      
      // Verify types
      expect(typeof result.publishedTopicsCount).toBe("number");
      expect(typeof result.usedTopicsCount).toBe("number");
      expect(typeof result.unusedTopicsCount).toBe("number");
      expect(typeof result.pendingTransferStudentsCount).toBe("number");
      
      // Verify logical consistency
      expect(result.publishedTopicsCount).toBeGreaterThanOrEqual(0);
      expect(result.usedTopicsCount).toBeGreaterThanOrEqual(0);
      expect(result.unusedTopicsCount).toBeGreaterThanOrEqual(0);
      expect(result.pendingTransferStudentsCount).toBeGreaterThanOrEqual(0);
      
      // Used + Unused should equal Published
      expect(result.usedTopicsCount + result.unusedTopicsCount).toBe(result.publishedTopicsCount);
    });

    it("should reject non-admin users", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      await expect(caller.admin.getChineseTeacherTopicMonitoring()).rejects.toThrow();
    });
  });

  describe("admin.getChineseTeacherTopicList", () => {
    it("should return topic list for admin", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.getChineseTeacherTopicList({});

      // Verify the result is an array
      expect(Array.isArray(result)).toBe(true);
    }, 30000);

    it("should reject non-admin users", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      await expect(caller.admin.getChineseTeacherTopicList({})).rejects.toThrow();
    });
  });
});
