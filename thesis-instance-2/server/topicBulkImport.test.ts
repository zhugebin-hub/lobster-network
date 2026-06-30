import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type AuthenticatedUser = NonNullable<TrpcContext["user"]>;

function createTeacherContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "teacher-test-bulk",
    email: "teacher-bulk@example.com",
    name: "Test Teacher Bulk",
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

describe("Topic Bulk Import API", () => {
  describe("bulkImport procedure", () => {
    it("should import multiple topics and return correct counts", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      const topics = [
        {
          titleEn: `Test Topic Bulk ${Date.now()}-1`,
          title: "测试课题1",
          descriptionEn: "This is a test topic for bulk import functionality",
          description: "这是批量导入功能的测试课题",
          keywords: "AI, Machine Learning, Deep Learning",
          researchFocus: "Computer Vision",
          topicSource: "其他",
          suitableMajor: "both" as const,
        },
        {
          titleEn: `Test Topic Bulk ${Date.now()}-2`,
          title: "测试课题2",
          descriptionEn: "Another test topic for bulk import",
          description: "另一个批量导入测试课题",
          keywords: "IoT, Sensors, Networks",
          researchFocus: "Embedded Systems",
          topicSource: "其他",
          suitableMajor: "electronic_info" as const,
        },
      ];

      const result = await caller.topic.bulkImport({ topics });

      expect(result).toHaveProperty("success");
      expect(result).toHaveProperty("failed");
      expect(result).toHaveProperty("total");
      expect(result).toHaveProperty("errors");
      expect(result.total).toBe(2);
      expect(result.success + result.failed).toBe(2);
    });

    it("should reject topics with missing required fields via validation", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      try {
        await caller.topic.bulkImport({
          topics: [
            {
              titleEn: "",
              descriptionEn: "Test description",
              keywords: "test",
              researchFocus: "test",
            },
          ],
        });
        expect(true).toBe(false); // Should not reach here
      } catch (error: any) {
        expect(error.message).toContain("英文标题不能为空");
      }
    });

    it("should fail topics with non-other source but missing project name", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      const topics = [
        {
          titleEn: `Test Topic Source ${Date.now()}`,
          descriptionEn: "Test description for project source topic",
          keywords: "AI, ML, DL",
          researchFocus: "AI Research",
          topicSource: "国家重点研发计划项目",
          researchProjectName: "",
        },
      ];

      const result = await caller.topic.bulkImport({ topics });

      expect(result.failed).toBe(1);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors[0]).toContain("科研项目名称必填");
    });

    it("should handle mixed success and failure correctly", async () => {
      const ctx = createTeacherContext();
      const caller = appRouter.createCaller(ctx);

      const timestamp = Date.now();
      const topics = [
        {
          titleEn: `Valid Topic Mixed ${timestamp}`,
          descriptionEn: "Valid description",
          keywords: "key1, key2, key3",
          researchFocus: "Valid Focus",
          topicSource: "其他",
        },
        {
          titleEn: `Topic Invalid Source ${timestamp}`,
          descriptionEn: "Description",
          keywords: "key1, key2, key3",
          researchFocus: "Focus",
          topicSource: "国家自然科学基金项目",
          researchProjectName: "",
        },
      ];

      const result = await caller.topic.bulkImport({ topics });

      expect(result.total).toBe(2);
      expect(result.success).toBe(1);
      expect(result.failed).toBe(1);
    });
  });
});
