import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
// OAuth routes removed - using local JWT authentication
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";
import { initializeSystem } from "../init";
import multer from "multer";
import { storagePut, getStorageDir, ensureTemplatesDir } from "../storage";
import { COOKIE_NAME } from "@shared/const";
import { parse as parseCookieHeader } from "cookie";
import { jwtVerify } from "jose";
import * as db from "../db";
import { nanoid } from "nanoid";

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startServer() {
  const app = express();
  const server = createServer(app);

  // ============================================================
  // 安全中间件（漏洞修复）
  // ============================================================

  // 1. 安全响应头中间件
  //    修复：CSP缺失、X-Frame-Options缺失、X-Content-Type-Options缺失、
  //    X-XSS-Protection缺失、Referrer-Policy缺失、X-Download-Options缺失、
  //    X-Permitted-Cross-Domain-Policies缺失
  app.use((_req, res, next) => {
    // 防止点击劫持
    res.setHeader("X-Frame-Options", "SAMEORIGIN");
    // 防止 MIME 类型嗅探
    res.setHeader("X-Content-Type-Options", "nosniff");
    // 启用 XSS 过滤
    res.setHeader("X-XSS-Protection", "1; mode=block");
    // 内容安全策略
    res.setHeader(
      "Content-Security-Policy",
      "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'self'; base-uri 'self'; form-action 'self';"
    );
    // 控制 Referer 信息泄露
    res.setHeader("Referrer-Policy", "strict-origin-when-cross-origin");
    // 防止 IE 下载时直接打开文件
    res.setHeader("X-Download-Options", "noopen");
    // 限制跨域策略文件加载
    res.setHeader("X-Permitted-Cross-Domain-Policies", "none");
    // 隐藏 Express 框架标识
    res.removeHeader("X-Powered-By");
    next();
  });

  // 2. URL 重定向防护中间件
  //    修复：[中危] URL重定向漏洞 (CVE N/A)
  //    阻止包含反斜杠、双斜杠开头、编码字符等可疑路径的请求
  app.use((req, res, next) => {
    const rawUrl = req.url;
    // 检测反斜杠（常见的URL重定向绕过手段）
    if (rawUrl.includes("\\")) {
      res.status(400).send("Bad Request");
      return;
    }
    // 检测以 // 开头的路径（可能被解析为协议相对URL）
    if (/^\/\//.test(rawUrl)) {
      res.status(400).send("Bad Request");
      return;
    }
    // 检测路径中的 URL 编码的特殊字符序列（如 %2F..、%5C 等）
    const decodedPath = decodeURIComponent(rawUrl).toLowerCase();
    if (decodedPath.includes("\\") || /\/\//.test(decodedPath.split("?")[0])) {
      // 仅对路径部分（非查询参数）检查双斜杠
      const pathPart = decodedPath.split("?")[0];
      if (/\/\//.test(pathPart) || decodedPath.includes("\\")) {
        res.status(400).send("Bad Request");
        return;
      }
    }
    next();
  });

  // 3. 禁用 X-Powered-By（Express 默认会发送）
  app.disable("x-powered-by");

  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  // Local JWT authentication (no OAuth)

  // File upload endpoint
  const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 50 * 1024 * 1024 } });
  app.post("/api/upload", upload.single("file"), async (req, res) => {
    try {
      // Authenticate user via JWT cookie
      const cookieHeader = req.headers.cookie;
      if (!cookieHeader) {
        res.status(401).json({ error: "未登录" });
        return;
      }
      const cookies = parseCookieHeader(cookieHeader);
      const sessionCookie = cookies[COOKIE_NAME];
      if (!sessionCookie) {
        res.status(401).json({ error: "未登录" });
        return;
      }
      const secretKey = new TextEncoder().encode(process.env.JWT_SECRET || "thesis-secret-key");
      let user;
      try {
        const { payload } = await jwtVerify(sessionCookie, secretKey, { algorithms: ["HS256"] });
        user = await db.getUserByOpenId(payload.openId as string);
      } catch {
        res.status(401).json({ error: "登录已过期" });
        return;
      }
      if (!user) {
        res.status(401).json({ error: "用户不存在" });
        return;
      }

      const file = req.file;
      if (!file) {
        res.status(400).json({ error: "未选择文件" });
        return;
      }

      // Generate unique file key
      const ext = file.originalname.split(".").pop() || "bin";
      const fileKey = `uploads/${user.id}/${nanoid()}.${ext}`;

      // Upload to local storage
      const { key, url } = await storagePut(fileKey, file.buffer, file.mimetype);

      res.json({
        success: true,
        fileKey: key,
        url: url,
        fileName: file.originalname,
        fileSize: file.size,
        mimeType: file.mimetype,
      });
    } catch (error: any) {
      console.error("[Upload] File upload failed:", error);
      if (error.message?.includes("Forbidden") || error.message?.includes("session")) {
        res.status(401).json({ error: "未登录或登录已过期" });
      } else {
        res.status(500).json({ error: error.message || "文件上传失败" });
      }
    }
  });

  // Ensure templates directory exists for static template files
  ensureTemplatesDir();

  // Serve uploaded files from local storage directory
  app.use("/files", express.static(getStorageDir(), {
    maxAge: "7d",
    immutable: true,
    fallthrough: true,
  }));

  // tRPC API
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, async () => {
    console.log(`Server running on http://localhost:${port}/`);
    try {
      await initializeSystem();
    } catch (e) {
      console.error("[Init] Failed to initialize system:", e);
    }
  });
}

startServer().catch(console.error);
