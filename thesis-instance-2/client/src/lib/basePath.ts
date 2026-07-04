/**
 * 子路径部署工具函数
 *
 * 通过 Vite 的 import.meta.env.BASE_URL 获取构建时配置的 base path。
 * - 实例1 构建时 base = "/"，import.meta.env.BASE_URL = "/"
 * - 实例2 构建时 base = "/instance2/"，import.meta.env.BASE_URL = "/instance2/"
 *
 * 这些函数用于在前端代码中动态拼接正确的 URL 前缀。
 */

/** 获取 base path，去掉尾部斜杠（如 "/instance2"），根路径返回空字符串 */
export function getBasePath(): string {
  const base = import.meta.env.BASE_URL || "/";
  // 去掉尾部斜杠，根路径 "/" 返回 ""
  return base === "/" ? "" : base.replace(/\/$/, "");
}

/**
 * 为 API 路径添加 base path 前缀
 * 例如: prefixPath("/api/trpc") → "/instance2/api/trpc"（实例2）
 *       prefixPath("/api/trpc") → "/api/trpc"（实例1）
 */
export function prefixPath(path: string): string {
  return getBasePath() + path;
}

/**
 * 为数据库中存储的文件 URL 添加 base path 前缀
 * 数据库中存储的格式为 "/files/uploads/xxx"
 * 例如: prefixFileUrl("/files/uploads/1/abc.pdf") → "/instance2/files/uploads/1/abc.pdf"（实例2）
 */
export function prefixFileUrl(url: string | null | undefined): string {
  if (!url) return "";
  // 如果已经包含 base path 前缀，不重复添加
  const base = getBasePath();
  if (base && url.startsWith(base)) return url;
  return base + url;
}
