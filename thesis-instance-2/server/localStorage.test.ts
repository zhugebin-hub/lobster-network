import { describe, it, expect, beforeAll, afterAll } from "vitest";
import fs from "fs";
import path from "path";

// Set a temp storage dir for tests before importing storage module
const TEST_STORAGE_DIR = path.join(process.cwd(), "test-local-storage-" + Date.now());
process.env.LOCAL_STORAGE_DIR = TEST_STORAGE_DIR;

// Dynamic import after env is set
const { storagePut, storageGet, storageExists, storageDelete, getStorageDir } = await import("./storage");

describe("Local Storage Module", () => {
  beforeAll(() => {
    // Ensure test directory is clean
    if (fs.existsSync(TEST_STORAGE_DIR)) {
      fs.rmSync(TEST_STORAGE_DIR, { recursive: true });
    }
  });

  afterAll(() => {
    // Clean up test directory
    if (fs.existsSync(TEST_STORAGE_DIR)) {
      fs.rmSync(TEST_STORAGE_DIR, { recursive: true });
    }
  });

  describe("getStorageDir", () => {
    it("should return the configured storage directory", () => {
      expect(getStorageDir()).toBe(TEST_STORAGE_DIR);
    });
  });

  describe("storagePut", () => {
    it("should write a file and return key and url", async () => {
      const result = await storagePut("test/hello.txt", "Hello World", "text/plain");
      expect(result.key).toBe("test/hello.txt");
      expect(result.url).toBe("/files/test/hello.txt");

      // Verify file exists on disk
      const filePath = path.join(TEST_STORAGE_DIR, "test/hello.txt");
      expect(fs.existsSync(filePath)).toBe(true);
      expect(fs.readFileSync(filePath, "utf-8")).toBe("Hello World");
    });

    it("should write a Buffer and return correct url", async () => {
      const buffer = Buffer.from("Binary content");
      const result = await storagePut("uploads/1/doc.pdf", buffer, "application/pdf");
      expect(result.key).toBe("uploads/1/doc.pdf");
      expect(result.url).toBe("/files/uploads/1/doc.pdf");

      const filePath = path.join(TEST_STORAGE_DIR, "uploads/1/doc.pdf");
      expect(fs.existsSync(filePath)).toBe(true);
      expect(fs.readFileSync(filePath).toString()).toBe("Binary content");
    });

    it("should strip leading slashes from key", async () => {
      const result = await storagePut("///leading/slashes.txt", "content");
      expect(result.key).toBe("leading/slashes.txt");
      expect(result.url).toBe("/files/leading/slashes.txt");
    });

    it("should create nested directories automatically", async () => {
      const result = await storagePut("a/b/c/d/deep.txt", "deep content");
      expect(result.key).toBe("a/b/c/d/deep.txt");

      const filePath = path.join(TEST_STORAGE_DIR, "a/b/c/d/deep.txt");
      expect(fs.existsSync(filePath)).toBe(true);
    });

    it("should overwrite existing files", async () => {
      await storagePut("overwrite.txt", "original");
      await storagePut("overwrite.txt", "updated");

      const filePath = path.join(TEST_STORAGE_DIR, "overwrite.txt");
      expect(fs.readFileSync(filePath, "utf-8")).toBe("updated");
    });

    it("should handle Uint8Array input", async () => {
      const data = new Uint8Array([72, 101, 108, 108, 111]); // "Hello"
      const result = await storagePut("uint8.txt", data);
      expect(result.key).toBe("uint8.txt");

      const filePath = path.join(TEST_STORAGE_DIR, "uint8.txt");
      expect(fs.readFileSync(filePath, "utf-8")).toBe("Hello");
    });
  });

  describe("storageGet", () => {
    it("should return key and url for an existing file", async () => {
      await storagePut("get-test.txt", "content");
      const result = await storageGet("get-test.txt");
      expect(result.key).toBe("get-test.txt");
      expect(result.url).toBe("/files/get-test.txt");
    });

    it("should return url even for non-existing files (no existence check)", async () => {
      const result = await storageGet("nonexistent.txt");
      expect(result.key).toBe("nonexistent.txt");
      expect(result.url).toBe("/files/nonexistent.txt");
    });

    it("should strip leading slashes from key", async () => {
      const result = await storageGet("///path/to/file.txt");
      expect(result.key).toBe("path/to/file.txt");
      expect(result.url).toBe("/files/path/to/file.txt");
    });
  });

  describe("storageExists", () => {
    it("should return true for existing files", async () => {
      await storagePut("exists-test.txt", "content");
      expect(await storageExists("exists-test.txt")).toBe(true);
    });

    it("should return false for non-existing files", async () => {
      expect(await storageExists("does-not-exist.txt")).toBe(false);
    });
  });

  describe("storageDelete", () => {
    it("should delete an existing file", async () => {
      await storagePut("delete-test.txt", "to be deleted");
      expect(await storageExists("delete-test.txt")).toBe(true);

      await storageDelete("delete-test.txt");
      expect(await storageExists("delete-test.txt")).toBe(false);
    });

    it("should not throw when deleting a non-existing file", async () => {
      await expect(storageDelete("nonexistent-delete.txt")).resolves.not.toThrow();
    });
  });

  describe("URL format consistency", () => {
    it("should always produce URLs starting with /files/", async () => {
      const putResult = await storagePut("url-test/file.txt", "content");
      const getResult = await storageGet("url-test/file.txt");

      expect(putResult.url).toMatch(/^\/files\//);
      expect(getResult.url).toMatch(/^\/files\//);
      expect(putResult.url).toBe(getResult.url);
    });
  });
});
