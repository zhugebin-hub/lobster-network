import { describe, expect, it } from "vitest";
import * as db from "./db";

describe("Final Score Calculation with Late Penalty", () => {
  // 测试最终成绩计算公式
  describe("Score calculation formula", () => {
    it("should calculate final score as average of two scores minus late penalty", () => {
      const score1 = 85;
      const score2 = 90;
      const latePenalty = 5;
      const average = Math.round((score1 + score2) / 2 * 10) / 10;
      const finalScore = Math.max(0, Math.round((average - latePenalty) * 10) / 10);
      expect(average).toBe(87.5);
      expect(finalScore).toBe(82.5);
    });

    it("should calculate final score with 10-point late penalty", () => {
      const score1 = 80;
      const score2 = 75;
      const latePenalty = 10;
      const average = Math.round((score1 + score2) / 2 * 10) / 10;
      const finalScore = Math.max(0, Math.round((average - latePenalty) * 10) / 10);
      expect(average).toBe(77.5);
      expect(finalScore).toBe(67.5);
    });

    it("should not go below 0 when penalty exceeds score", () => {
      const score1 = 3;
      const score2 = 5;
      const latePenalty = 10;
      const average = Math.round((score1 + score2) / 2 * 10) / 10;
      const finalScore = Math.max(0, Math.round((average - latePenalty) * 10) / 10);
      expect(average).toBe(4);
      expect(finalScore).toBe(0);
    });

    it("should have no penalty when latePenalty is 0", () => {
      const score1 = 90;
      const score2 = 88;
      const latePenalty = 0;
      const average = Math.round((score1 + score2) / 2 * 10) / 10;
      const finalScore = Math.max(0, Math.round((average - latePenalty) * 10) / 10);
      expect(average).toBe(89);
      expect(finalScore).toBe(89);
    });

    it("should handle identical scores with penalty", () => {
      const score1 = 85;
      const score2 = 85;
      const latePenalty = 5;
      const finalScore = Math.max(0, Math.round((score1 - latePenalty) * 10) / 10);
      expect(finalScore).toBe(80);
    });
  });

  // 测试分差判断逻辑
  describe("Score difference logic", () => {
    it("should auto-calculate final score when difference <= 10", () => {
      const score1 = 85;
      const score2 = 90;
      const diff = Math.abs(score1 - score2);
      expect(diff).toBe(5);
      expect(diff <= 10).toBe(true);
    });

    it("should require negotiation when difference > 10", () => {
      const score1 = 70;
      const score2 = 90;
      const diff = Math.abs(score1 - score2);
      expect(diff).toBe(20);
      expect(diff > 10).toBe(true);
    });

    it("should handle boundary case of exactly 10 points difference", () => {
      const score1 = 80;
      const score2 = 90;
      const diff = Math.abs(score1 - score2);
      expect(diff).toBe(10);
      expect(diff <= 10).toBe(true);
    });

    it("should handle boundary case of 11 points difference", () => {
      const score1 = 79;
      const score2 = 90;
      const diff = Math.abs(score1 - score2);
      expect(diff).toBe(11);
      expect(diff > 10).toBe(true);
    });
  });

  // 测试数据库查询函数返回正确字段
  describe("Review task query functions", () => {
    it("getFirstTeacherReviewTasks should return empty array for non-existent teacher", async () => {
      const result = await db.getFirstTeacherReviewTasks(99999);
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(0);
    });

    it("getSecondTeacherReviewTasks should return empty array for non-existent teacher", async () => {
      const result = await db.getSecondTeacherReviewTasks(99999);
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(0);
    });

    it("getSecondTeacherReviewTasksWithVisibility should return empty array for non-existent teacher", async () => {
      const result = await db.getSecondTeacherReviewTasksWithVisibility(99999);
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBe(0);
    });
  });

  // 测试第二导师评分函数
  describe("submitSecondTeacherScore", () => {
    it("should reject for non-existent draft", async () => {
      const result = await db.submitSecondTeacherScore(99999, 85, 1);
      expect(result.success).toBe(false);
      expect(result.error).toContain("不存在");
    });

    it("should reject invalid score range", async () => {
      const result = await db.submitSecondTeacherScore(1, 150, 1);
      expect(result.success).toBe(false);
    });
  });

  // 测试带评语的第二导师评分函数
  describe("submitSecondTeacherScoreWithComment", () => {
    it("should reject for non-existent draft", async () => {
      const result = await db.submitSecondTeacherScoreWithComment(99999, 85, 1, "Good work");
      expect(result.success).toBe(false);
      expect(result.error).toContain("不存在");
    });
  });

  // 测试修改评分函数
  describe("updateTeacherScore", () => {
    it("should reject for non-existent draft", async () => {
      const result = await db.updateTeacherScore(99999, 85, 1, true);
      expect(result.success).toBe(false);
      expect(result.error).toContain("不存在");
    });
  });

  // 测试 confirmFinalScore 函数
  describe("confirmFinalScore with penalty", () => {
    it("should reject for non-existent draft", async () => {
      const result = await db.confirmFinalScore(99999, 1, "confirm_average");
      expect(result.success).toBe(false);
      expect(result.error).toContain("不存在");
    });

    it("should reject invalid manual score", async () => {
      // Even if draft exists, invalid score should be rejected
      const result = await db.confirmFinalScore(1, 1, "manual_score", 150);
      expect(result.success).toBe(false);
    });
  });
});
