// Local file system storage helpers
// Replaces the original S3 proxy with direct disk I/O

import fs from "fs";
import path from "path";

/**
 * Local storage root directory.
 * - In development: ./local-storage (relative to project root)
 * - In production: configurable via LOCAL_STORAGE_DIR env var (e.g. /data/thesis-files)
 */
const STORAGE_DIR = process.env.LOCAL_STORAGE_DIR || path.join(process.cwd(), "local-storage");

function normalizeKey(relKey: string): string {
  // 去除前导斜杠
  let key = relKey.replace(/^\/+/, "");
  // 路径穿越防护：规范化后检查是否仍在存储目录内
  const resolved = path.resolve(STORAGE_DIR, key);
  if (!resolved.startsWith(path.resolve(STORAGE_DIR) + path.sep) && resolved !== path.resolve(STORAGE_DIR)) {
    throw new Error("Invalid file path: path traversal detected");
  }
  return key;
}

/**
 * Upload (write) a file to local disk.
 * Returns { key, url } where url is the path served by the /files static route.
 */
export async function storagePut(
  relKey: string,
  data: Buffer | Uint8Array | string,
  contentType = "application/octet-stream"
): Promise<{ key: string; url: string }> {
  const key = normalizeKey(relKey);
  const filePath = path.join(STORAGE_DIR, key);

  // Ensure the parent directory exists
  await fs.promises.mkdir(path.dirname(filePath), { recursive: true });

  // Write file to disk
  const buffer = typeof data === "string" ? Buffer.from(data) : Buffer.from(data);
  await fs.promises.writeFile(filePath, buffer);

  // Return a URL that the /files static route can serve
  const url = `/files/${key}`;
  return { key, url };
}

/**
 * Get the accessible URL for a previously stored file.
 */
export async function storageGet(
  relKey: string
): Promise<{ key: string; url: string }> {
  const key = normalizeKey(relKey);
  return { key, url: `/files/${key}` };
}

/**
 * Check if a file exists in local storage.
 */
export async function storageExists(relKey: string): Promise<boolean> {
  const key = normalizeKey(relKey);
  const filePath = path.join(STORAGE_DIR, key);
  try {
    await fs.promises.access(filePath, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

/**
 * Delete a file from local storage.
 */
export async function storageDelete(relKey: string): Promise<void> {
  const key = normalizeKey(relKey);
  const filePath = path.join(STORAGE_DIR, key);
  try {
    await fs.promises.unlink(filePath);
  } catch (err: any) {
    if (err.code !== "ENOENT") throw err; // Ignore if file doesn't exist
  }
}

/**
 * Get the absolute path of the storage directory (for Express static serving).
 */
export function getStorageDir(): string {
  return STORAGE_DIR;
}

/**
 * Ensure the templates directory exists in the storage directory.
 * Called during server startup to create the templates folder structure.
 */
export function ensureTemplatesDir(): void {
  const templatesDir = path.join(STORAGE_DIR, "templates");
  fs.mkdirSync(templatesDir, { recursive: true });
}
