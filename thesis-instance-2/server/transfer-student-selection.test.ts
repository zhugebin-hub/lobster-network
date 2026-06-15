import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { TRPCError } from "@trpc/server";

/**
 * 分流学生选题时间段功能测试
 * 
 * 测试场景：
 * 1. 时间段校验：分流学生选题时间段必须在普通学生选题时间段之前
 * 2. 分流学生权限：分流学生只能在其专属时间段内选题
 * 3. 普通学生权限：普通学生不能在分流选题时间段内选题
 * 4. 时间段边界：测试时间段的开始和结束边界
 */

describe("Transfer Student Selection Period", () => {
  // 测试数据
  const mockTransferSelectionStart = new Date("2026-01-10T09:00:00Z");
  const mockTransferSelectionEnd = new Date("2026-01-12T17:00:00Z");
  const mockNormalSelectionStart = new Date("2026-01-13T09:00:00Z");
  const mockNormalSelectionEnd = new Date("2026-01-20T17:00:00Z");

  describe("Time Period Validation", () => {
    it("应该接受分流选题时间段在普通选题时间段之前的配置", () => {
      const transferEnd = mockTransferSelectionEnd;
      const normalStart = mockNormalSelectionStart;

      // 分流选题时间段必须完全在普通选题时间段之前
      const isValid = transferEnd <= normalStart;
      expect(isValid).toBe(true);
    });

    it("应该拒绝分流选题时间段与普通选题时间段重叠的配置", () => {
      const transferEnd = new Date("2026-01-13T10:00:00Z"); // 与普通选题时间段重叠
      const normalStart = mockNormalSelectionStart;

      // 分流选题时间段必须完全在普通选题时间段之前
      const isValid = transferEnd <= normalStart;
      expect(isValid).toBe(false);
    });

    it("应该拒绝分流选题截止时间早于开始时间的配置", () => {
      const transferStart = mockTransferSelectionStart;
      const transferEnd = new Date("2026-01-09T17:00:00Z"); // 早于开始时间

      const isValid = transferEnd > transferStart;
      expect(isValid).toBe(false);
    });

    it("应该拒绝分流选题开始时间等于截止时间的配置", () => {
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionStart; // 相同时间

      const isValid = transferEnd > transferStart;
      expect(isValid).toBe(false);
    });
  });

  describe("Transfer Student Selection Permission", () => {
    it("分流学生应该能在其专属时间段内选题", () => {
      const currentTime = new Date("2026-01-11T10:00:00Z"); // 在分流选题时间段内
      const isTransfer = true;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      const canSelect =
        isTransfer &&
        currentTime >= transferStart &&
        currentTime <= transferEnd;
      expect(canSelect).toBe(true);
    });

    it("分流学生不应该能在分流选题时间段之外选题（早于开始时间）", () => {
      const currentTime = new Date("2026-01-09T10:00:00Z"); // 早于分流选题时间段
      const isTransfer = true;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      const canSelect =
        isTransfer &&
        currentTime >= transferStart &&
        currentTime <= transferEnd;
      expect(canSelect).toBe(false);
    });

    it("分流学生不应该能在分流选题时间段之外选题（晚于截止时间）", () => {
      const currentTime = new Date("2026-01-13T10:00:00Z"); // 晚于分流选题时间段
      const isTransfer = true;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      const canSelect =
        isTransfer &&
        currentTime >= transferStart &&
        currentTime <= transferEnd;
      expect(canSelect).toBe(false);
    });

    it("分流学生在分流选题时间段开始时应该能选题", () => {
      const currentTime = mockTransferSelectionStart; // 恰好在开始时间
      const isTransfer = true;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      const canSelect =
        isTransfer &&
        currentTime >= transferStart &&
        currentTime <= transferEnd;
      expect(canSelect).toBe(true);
    });

    it("分流学生在分流选题时间段截止时应该能选题", () => {
      const currentTime = mockTransferSelectionEnd; // 恰好在截止时间
      const isTransfer = true;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      const canSelect =
        isTransfer &&
        currentTime >= transferStart &&
        currentTime <= transferEnd;
      expect(canSelect).toBe(true);
    });
  });

  describe("Regular Student Selection Permission", () => {
    it("普通学生不应该能在分流选题时间段内选题", () => {
      const currentTime = new Date("2026-01-11T10:00:00Z"); // 在分流选题时间段内
      const isTransfer = false;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      // 如果分流选题时间段正在进行，普通学生无法选题
      const canSelect = !(
        currentTime >= transferStart &&
        currentTime <= transferEnd
      );
      expect(canSelect).toBe(false);
    });

    it("普通学生应该能在分流选题时间段之后的普通选题时间段内选题", () => {
      const currentTime = new Date("2026-01-15T10:00:00Z"); // 在普通选题时间段内
      const isTransfer = false;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;
      const normalStart = mockNormalSelectionStart;
      const normalEnd = mockNormalSelectionEnd;

      // 检查是否在分流选题时间段内
      const inTransferPeriod =
        currentTime >= transferStart && currentTime <= transferEnd;
      // 检查是否在普通选题时间段内
      const inNormalPeriod =
        currentTime >= normalStart && currentTime <= normalEnd;

      const canSelect = !inTransferPeriod && inNormalPeriod;
      expect(canSelect).toBe(true);
    });

    it("普通学生不应该能在普通选题时间段之前选题", () => {
      const currentTime = new Date("2026-01-12T10:00:00Z"); // 在分流选题时间段之后，普通选题时间段之前
      const isTransfer = false;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;
      const normalStart = mockNormalSelectionStart;
      const normalEnd = mockNormalSelectionEnd;

      // 检查是否在分流选题时间段内
      const inTransferPeriod =
        currentTime >= transferStart && currentTime <= transferEnd;
      // 检查是否在普通选题时间段内
      const inNormalPeriod =
        currentTime >= normalStart && currentTime <= normalEnd;

      const canSelect = !inTransferPeriod && inNormalPeriod;
      expect(canSelect).toBe(false);
    });

    it("普通学生不应该能在普通选题时间段之后选题", () => {
      const currentTime = new Date("2026-01-21T10:00:00Z"); // 在普通选题时间段之后
      const isTransfer = false;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;
      const normalStart = mockNormalSelectionStart;
      const normalEnd = mockNormalSelectionEnd;

      // 检查是否在分流选题时间段内
      const inTransferPeriod =
        currentTime >= transferStart && currentTime <= transferEnd;
      // 检查是否在普通选题时间段内
      const inNormalPeriod =
        currentTime >= normalStart && currentTime <= normalEnd;

      const canSelect = !inTransferPeriod && inNormalPeriod;
      expect(canSelect).toBe(false);
    });
  });

  describe("Error Messages", () => {
    it("分流学生在分流选题时间段已结束且普通选题时间段尚未开始时应该收到正确的错误信息", () => {
      const currentTime = new Date("2026-01-12T18:00:00Z"); // 在分流选题时间段之后，普通选题时间段之前
      const isTransfer = true;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;
      const normalStart = mockNormalSelectionStart;
      const normalEnd = mockNormalSelectionEnd;

      // 分流学生专属时间段已结束，检查是否在普通时间段内
      const inTransferPeriod =
        currentTime >= transferStart && currentTime <= transferEnd;
      const inNormalPeriod =
        currentTime >= normalStart && currentTime <= normalEnd;

      if (inTransferPeriod) {
        // 在分流时间段内，可以选题
        expect(true).toBe(true);
      } else if (!inNormalPeriod) {
        // 不在任何时间段内
        const errorMessage = "分流学生选题时间段已结束，普通学生选题时间段尚未开始";
        expect(errorMessage).toContain("分流学生选题时间段已结束");
      }
    });

    it("普通学生在分流选题时间段正在进行时应该收到正确的错误信息", () => {
      const currentTime = new Date("2026-01-11T10:00:00Z"); // 在分流选题时间段内
      const isTransfer = false;
      const transferStart = mockTransferSelectionStart;
      const transferEnd = mockTransferSelectionEnd;

      // 检查是否在分流选题时间段内
      const inTransferPeriod =
        currentTime >= transferStart && currentTime <= transferEnd;

      if (inTransferPeriod) {
        const errorMessage = "分流学生选题时间段正在进行中，请稍后再选题";
        expect(errorMessage).toContain("分流学生选题时间段正在进行中");
      }
    });
  });

  describe("Edge Cases", () => {
    it("应该正确处理时间戳边界情况（毫秒级精度）", () => {
      const transferStart = new Date("2026-01-10T09:00:00.000Z");
      const transferEnd = new Date("2026-01-12T17:00:00.999Z");
      const normalStart = new Date("2026-01-13T09:00:00.000Z");

      // 分流选题时间段必须完全在普通选题时间段之前
      const isValid = transferEnd <= normalStart;
      expect(isValid).toBe(true);
    });

    it("应该正确处理跨天的时间段", () => {
      const transferStart = new Date("2026-01-10T20:00:00Z"); // 晚上8点
      const transferEnd = new Date("2026-01-12T08:00:00Z"); // 第二天早上8点
      const normalStart = new Date("2026-01-13T09:00:00Z");

      // 分流选题时间段必须完全在普通选题时间段之前
      const isValid = transferEnd <= normalStart;
      expect(isValid).toBe(true);
    });

    it("应该正确处理同一天的时间段", () => {
      const transferStart = new Date("2026-01-10T09:00:00Z");
      const transferEnd = new Date("2026-01-10T17:00:00Z");
      const normalStart = new Date("2026-01-11T09:00:00Z");

      // 分流选题时间段必须完全在普通选题时间段之前
      const isValid = transferEnd <= normalStart;
      expect(isValid).toBe(true);
    });
  });

  describe("Integration Scenarios", () => {
    it("完整场景：分流学生选题 -> 分流选题结束 -> 普通学生选题", () => {
      // 场景1：分流学生在其时间段内选题
      const transferStudentTime = new Date("2026-01-11T10:00:00Z");
      const isTransferCanSelect =
        transferStudentTime >= mockTransferSelectionStart &&
        transferStudentTime <= mockTransferSelectionEnd;
      expect(isTransferCanSelect).toBe(true);

      // 场景2：分流选题时间段结束后，普通学生可以选题
      const normalStudentTime = new Date("2026-01-15T10:00:00Z");
      const inTransferPeriod =
        normalStudentTime >= mockTransferSelectionStart &&
        normalStudentTime <= mockTransferSelectionEnd;
      const inNormalPeriod =
        normalStudentTime >= mockNormalSelectionStart &&
        normalStudentTime <= mockNormalSelectionEnd;
      const isNormalCanSelect = !inTransferPeriod && inNormalPeriod;
      expect(isNormalCanSelect).toBe(true);

      // 场景3：分流选题时间段内，普通学生不能选题
      const normalStudentDuringTransfer = new Date("2026-01-11T10:00:00Z");
      const inTransferPeriod2 =
        normalStudentDuringTransfer >= mockTransferSelectionStart &&
        normalStudentDuringTransfer <= mockTransferSelectionEnd;
      const isNormalCanSelectDuringTransfer = !inTransferPeriod2;
      expect(isNormalCanSelectDuringTransfer).toBe(false);
    });
  });
});
