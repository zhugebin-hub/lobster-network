import { describe, it, expect, beforeAll, afterAll } from "vitest";
import * as db from "./db";

describe("Transfer Student Priority Mode", () => {
  describe("checkTransferStudentPriorityMode", () => {
    it("should return priority mode status with correct fields", async () => {
      const result = await db.checkTransferStudentPriorityMode();
      
      expect(result).toHaveProperty("isActive");
      expect(result).toHaveProperty("unusedTopicsCount");
      expect(result).toHaveProperty("pendingTransferStudentsCount");
      expect(result).toHaveProperty("message");
      
      expect(typeof result.isActive).toBe("boolean");
      expect(typeof result.unusedTopicsCount).toBe("number");
      expect(typeof result.pendingTransferStudentsCount).toBe("number");
      expect(typeof result.message).toBe("string");
    });

    it("should return isActive true when unusedTopicsCount <= pendingTransferStudentsCount", async () => {
      const result = await db.checkTransferStudentPriorityMode();
      
      // 验证逻辑：isActive 应该在 unusedTopicsCount <= pendingTransferStudentsCount 时为 true
      const expectedActive = result.unusedTopicsCount <= result.pendingTransferStudentsCount;
      expect(result.isActive).toBe(expectedActive);
    });

    it("should return non-empty message when mode is active", async () => {
      const result = await db.checkTransferStudentPriorityMode();
      
      if (result.isActive) {
        expect(result.message.length).toBeGreaterThan(0);
        expect(result.message).toContain("分流学生");
      } else {
        expect(result.message).toBe("");
      }
    });
  });

  describe("getChineseTeacherTopicMonitoring", () => {
    it("should return monitoring data with correct structure", async () => {
      const result = await db.getChineseTeacherTopicMonitoring();
      
      expect(result).toHaveProperty("publishedTopicsCount");
      expect(result).toHaveProperty("usedTopicsCount");
      expect(result).toHaveProperty("unusedTopicsCount");
      expect(result).toHaveProperty("pendingTransferStudentsCount");
      expect(result).toHaveProperty("currentAcademicYear");
      
      expect(typeof result.publishedTopicsCount).toBe("number");
      expect(typeof result.usedTopicsCount).toBe("number");
      expect(typeof result.unusedTopicsCount).toBe("number");
      expect(typeof result.pendingTransferStudentsCount).toBe("number");
      expect(typeof result.currentAcademicYear).toBe("string");
    });

    it("should have unusedTopicsCount = publishedTopicsCount - usedTopicsCount", async () => {
      const result = await db.getChineseTeacherTopicMonitoring();
      
      expect(result.unusedTopicsCount).toBe(result.publishedTopicsCount - result.usedTopicsCount);
    });

    it("should return non-negative counts", async () => {
      const result = await db.getChineseTeacherTopicMonitoring();
      
      expect(result.publishedTopicsCount).toBeGreaterThanOrEqual(0);
      expect(result.usedTopicsCount).toBeGreaterThanOrEqual(0);
      expect(result.unusedTopicsCount).toBeGreaterThanOrEqual(0);
      expect(result.pendingTransferStudentsCount).toBeGreaterThanOrEqual(0);
    });
  });
});
