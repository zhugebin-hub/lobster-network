import { describe, it, expect } from "vitest";
import * as db from "./db";

describe("Thesis Grace Period", () => {
  describe("checkThesisGracePeriod", () => {
    it("should return grace period status with correct fields", async () => {
      const result = await db.checkThesisGracePeriod();
      
      expect(result).toHaveProperty("status");
      expect(result).toHaveProperty("canUpload");
      expect(result).toHaveProperty("penalty");
      expect(result).toHaveProperty("message");
      expect(result).toHaveProperty("deadlineTime");
      expect(result).toHaveProperty("graceEndTime");
      expect(result).toHaveProperty("hoursOverdue");
      expect(result).toHaveProperty("daysOverdue");
      
      expect(typeof result.canUpload).toBe("boolean");
      expect(typeof result.penalty).toBe("number");
      expect(typeof result.message).toBe("string");
      expect(typeof result.hoursOverdue).toBe("number");
      expect(typeof result.daysOverdue).toBe("number");
    });

    it("should return valid status values", async () => {
      const result = await db.checkThesisGracePeriod();
      
      const validStatuses = [
        "before_deadline",
        "normal", 
        "grace_24h",
        "grace_7d",
        "closed",
        "not_configured"
      ];
      
      expect(validStatuses).toContain(result.status);
    });

    it("should return correct penalty values based on status", async () => {
      const result = await db.checkThesisGracePeriod();
      
      // 根据状态验证扣分值
      switch (result.status) {
        case "grace_24h":
          expect(result.penalty).toBe(5);
          expect(result.canUpload).toBe(true);
          break;
        case "grace_7d":
          expect(result.penalty).toBe(10);
          expect(result.canUpload).toBe(true);
          break;
        case "normal":
          expect(result.penalty).toBe(0);
          expect(result.canUpload).toBe(true);
          break;
        case "before_deadline":
        case "closed":
        case "not_configured":
          expect(result.penalty).toBe(0);
          expect(result.canUpload).toBe(false);
          break;
      }
    });

    it("should have non-negative overdue values", async () => {
      const result = await db.checkThesisGracePeriod();
      
      expect(result.hoursOverdue).toBeGreaterThanOrEqual(0);
      expect(result.daysOverdue).toBeGreaterThanOrEqual(0);
    });

    it("should have consistent deadline and grace end times", async () => {
      const result = await db.checkThesisGracePeriod();
      
      // 如果配置了时间，graceEndTime 应该是 deadlineTime + 7天
      if (result.deadlineTime && result.graceEndTime) {
        const deadline = new Date(result.deadlineTime);
        const graceEnd = new Date(result.graceEndTime);
        const expectedGraceEnd = new Date(deadline.getTime() + 7 * 24 * 60 * 60 * 1000);
        
        expect(graceEnd.getTime()).toBe(expectedGraceEnd.getTime());
      }
    });
  });

  describe("Grace Period Business Rules", () => {
    it("should follow the penalty rules: 24h=5pts, 7d=10pts", async () => {
      const result = await db.checkThesisGracePeriod();
      
      // 验证业务规则
      if (result.status === "grace_24h") {
        expect(result.penalty).toBe(5);
        expect(result.message).toContain("5");
      }
      
      if (result.status === "grace_7d") {
        expect(result.penalty).toBe(10);
        expect(result.message).toContain("10");
      }
    });

    it("should close system after 7 days", async () => {
      const result = await db.checkThesisGracePeriod();
      
      if (result.status === "closed") {
        expect(result.canUpload).toBe(false);
        expect(result.message).toContain("关闭");
      }
    });
  });
});
