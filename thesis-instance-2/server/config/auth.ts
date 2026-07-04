/**
 * JWT认证服务
 * 独立于Manus平台的标准JWT认证实现
 * 支持账号密码登录和会话管理
 */

import { SignJWT, jwtVerify } from "jose";
import { parse as parseCookieHeader } from "cookie";
import type { Request, Response } from "express";
import * as bcrypt from "bcryptjs";
import { AUTH_CONFIG } from "./env";
import * as db from "../db";

// 会话载荷类型
export interface SessionPayload {
  userId: number;
  email: string;
  role: "admin" | "teacher" | "student";
  name?: string;
}

// 获取JWT密钥
function getJwtSecret(): Uint8Array {
  return new TextEncoder().encode(AUTH_CONFIG.jwtSecret);
}

/**
 * 创建JWT会话令牌
 */
export async function createSessionToken(payload: SessionPayload): Promise<string> {
  const secret = getJwtSecret();
  const expiresIn = AUTH_CONFIG.jwtExpiresIn;
  
  // 解析过期时间
  let expirationTime: string | number;
  if (expiresIn.endsWith("d")) {
    expirationTime = `${expiresIn}`;
  } else if (expiresIn.endsWith("h")) {
    expirationTime = `${expiresIn}`;
  } else {
    expirationTime = parseInt(expiresIn) || "7d";
  }
  
  return new SignJWT({
    userId: payload.userId,
    email: payload.email,
    role: payload.role,
    name: payload.name,
  })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setIssuedAt()
    .setExpirationTime(expirationTime)
    .sign(secret);
}

/**
 * 验证JWT会话令牌
 */
export async function verifySessionToken(token: string): Promise<SessionPayload | null> {
  try {
    const secret = getJwtSecret();
    const { payload } = await jwtVerify(token, secret, {
      algorithms: ["HS256"],
    });
    
    const { userId, email, role, name } = payload as Record<string, unknown>;
    
    if (
      typeof userId !== "number" ||
      typeof email !== "string" ||
      !["admin", "teacher", "student"].includes(role as string)
    ) {
      return null;
    }
    
    return {
      userId,
      email,
      role: role as "admin" | "teacher" | "student",
      name: name as string | undefined,
    };
  } catch (error) {
    console.warn("[Auth] Token verification failed:", error);
    return null;
  }
}

/**
 * 从请求中获取会话
 */
export async function getSessionFromRequest(req: Request): Promise<SessionPayload | null> {
  // 尝试从Cookie获取
  const cookieHeader = req.headers.cookie;
  if (cookieHeader) {
    const cookies = parseCookieHeader(cookieHeader);
    const token = cookies[AUTH_CONFIG.cookieName];
    if (token) {
      return verifySessionToken(token);
    }
  }
  
  // 尝试从Authorization头获取
  const authHeader = req.headers.authorization;
  if (authHeader?.startsWith("Bearer ")) {
    const token = authHeader.slice(7);
    return verifySessionToken(token);
  }
  
  return null;
}

/**
 * 设置会话Cookie
 */
export function setSessionCookie(res: Response, token: string): void {
  res.cookie(AUTH_CONFIG.cookieName, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: AUTH_CONFIG.cookieMaxAge,
    path: "/",
  });
}

/**
 * 清除会话Cookie
 */
export function clearSessionCookie(res: Response): void {
  res.clearCookie(AUTH_CONFIG.cookieName, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
  });
}

/**
 * 验证密码
 */
export async function verifyPassword(
  plainPassword: string,
  hashedPassword: string
): Promise<boolean> {
  return bcrypt.compare(plainPassword, hashedPassword);
}

/**
 * 哈希密码
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10);
}

/**
 * 账号密码登录
 */
export async function loginWithPassword(
  email: string,
  password: string
): Promise<{ success: boolean; token?: string; user?: any; error?: string }> {
  // 查找用户
  const user = await db.getUserByEmail(email);
  if (!user) {
    return { success: false, error: "用户不存在" };
  }
  
  // 验证密码
  const isValid = await verifyPassword(password, user.password);
  if (!isValid) {
    return { success: false, error: "密码错误" };
  }
  
  // 创建会话令牌
  const token = await createSessionToken({
    userId: user.id,
    email: user.email,
    role: user.role,
    name: user.name || undefined,
  });
  
  // 更新最后登录时间
  await db.upsertUser({
    openId: user.openId,
    lastSignedIn: new Date(),
  });
  
  return {
    success: true,
    token,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
      role: user.role,
    },
  };
}

/**
 * 认证中间件
 */
export async function authenticateRequest(req: Request): Promise<any> {
  const session = await getSessionFromRequest(req);
  
  if (!session) {
    throw new Error("未登录或会话已过期");
  }
  
  // 获取完整用户信息
  const user = await db.getUserById(session.userId);
  if (!user) {
    throw new Error("用户不存在");
  }
  
  return user;
}
