import { describe, expect, it } from "vitest";
import { deleteScoreRecord } from "./db";

describe("Delete Score Record", () => {
  describe("deleteScoreRecord", () => {
    it("should return error when draft does not exist", async () => {
      const result = await deleteScoreRecord(999999);
      expect(result.success).toBe(false);
      expect(result.error).toBe("记录不存在");
    });

    it("should return error message on database failure", async () => {
      // Test with invalid ID to trigger error handling
      const result = await deleteScoreRecord(-1);
      expect(result.success).toBe(false);
    });
  });
});
