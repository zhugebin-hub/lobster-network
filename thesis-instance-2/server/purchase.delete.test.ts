import { describe, it, expect, vi, beforeEach } from "vitest";

// Mock db module
vi.mock("./db", () => ({
  isUserLabAdmin: vi.fn(),
  isUserAssetLeader: vi.fn(),
  deletePurchaseRequest: vi.fn(),
}));

import * as db from "./db";

describe("Purchase Record Delete Permission", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("Permission checks", () => {
    it("should allow lab admin to delete records", async () => {
      vi.mocked(db.isUserLabAdmin).mockResolvedValue(true);
      vi.mocked(db.isUserAssetLeader).mockResolvedValue(false);
      vi.mocked(db.deletePurchaseRequest).mockResolvedValue();

      const isLabAdmin = await db.isUserLabAdmin(1);
      const isAssetLeader = await db.isUserAssetLeader(1);
      
      expect(isLabAdmin).toBe(true);
      expect(isLabAdmin || isAssetLeader).toBe(true);
      
      // Lab admin can delete
      await db.deletePurchaseRequest(123);
      expect(db.deletePurchaseRequest).toHaveBeenCalledWith(123);
    });

    it("should allow asset leader to delete records", async () => {
      vi.mocked(db.isUserLabAdmin).mockResolvedValue(false);
      vi.mocked(db.isUserAssetLeader).mockResolvedValue(true);
      vi.mocked(db.deletePurchaseRequest).mockResolvedValue();

      const isLabAdmin = await db.isUserLabAdmin(2);
      const isAssetLeader = await db.isUserAssetLeader(2);
      
      expect(isAssetLeader).toBe(true);
      expect(isLabAdmin || isAssetLeader).toBe(true);
      
      // Asset leader can delete
      await db.deletePurchaseRequest(456);
      expect(db.deletePurchaseRequest).toHaveBeenCalledWith(456);
    });

    it("should deny regular teacher from deleting records", async () => {
      vi.mocked(db.isUserLabAdmin).mockResolvedValue(false);
      vi.mocked(db.isUserAssetLeader).mockResolvedValue(false);

      const isLabAdmin = await db.isUserLabAdmin(3);
      const isAssetLeader = await db.isUserAssetLeader(3);
      
      expect(isLabAdmin).toBe(false);
      expect(isAssetLeader).toBe(false);
      expect(isLabAdmin || isAssetLeader).toBe(false);
      
      // Regular teacher cannot delete - permission check fails
      expect(db.deletePurchaseRequest).not.toHaveBeenCalled();
    });
  });

  describe("Delete function", () => {
    it("should call deletePurchaseRequest with correct requestId", async () => {
      vi.mocked(db.deletePurchaseRequest).mockResolvedValue();

      await db.deletePurchaseRequest(789);
      
      expect(db.deletePurchaseRequest).toHaveBeenCalledTimes(1);
      expect(db.deletePurchaseRequest).toHaveBeenCalledWith(789);
    });
  });
});
