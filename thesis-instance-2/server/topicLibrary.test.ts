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
    loginMethod: "password",
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
    loginMethod: "password",
    role: "teacher",
    teacherType: "chinese",
    annualQuota: 5,
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

describe("Topic Library Management", () => {
  describe("admin.getTopicLibrary", () => {
    it("should return topic library list for admin", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.getTopicLibrary({
        status: "all",
        page: 1,
        pageSize: 20,
      });

      expect(result).toHaveProperty("items");
      expect(result).toHaveProperty("total");
      expect(Array.isArray(result.items)).toBe(true);
      expect(typeof result.total).toBe("number");
    });

    it("should filter by status", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.getTopicLibrary({
        status: "published",
        page: 1,
        pageSize: 20,
      });

      expect(result).toHaveProperty("items");
      // All items should have status "published"
      result.items.forEach(item => {
        expect(item.status).toBe("published");
      });
    });
  });

  describe("admin.getTopicLibraryStats", () => {
    it("should return statistics for admin", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.getTopicLibraryStats();

      expect(result).toHaveProperty("total");
      expect(result).toHaveProperty("published");
      expect(result).toHaveProperty("used");
      expect(result).toHaveProperty("withdrawn");
      expect(result).toHaveProperty("byYear");
      expect(typeof result.total).toBe("number");
      expect(typeof result.published).toBe("number");
      expect(typeof result.used).toBe("number");
      expect(typeof result.withdrawn).toBe("number");
      expect(Array.isArray(result.byYear)).toBe(true);
    });
  });

  describe("admin.checkTopicTitleInLibrary", () => {
    it("should check if title exists in library", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.checkTopicTitleInLibrary({
        title: "Test Topic Title That Does Not Exist",
      });

      expect(result).toHaveProperty("exists");
      expect(typeof result.exists).toBe("boolean");
    });
  });

  describe("admin.cleanupOldTopicLibrary", () => {
    it("should cleanup old records and return count", async () => {
      const ctx = createAdminContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.admin.cleanupOldTopicLibrary();

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("deletedCount");
      expect(result.success).toBe(true);
      expect(typeof result.deletedCount).toBe("number");
    });
  });
});

describe("Topic Title Duplicate Check", () => {
  describe("topic.checkDuplicate", () => {
    it("should check for duplicate titles", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      const result = await caller.topic.checkDuplicate({
        title: "Test Topic Title",
      });

      // checkDuplicate returns an array of similar topics
      expect(Array.isArray(result)).toBe(true);
    });
  });
});
