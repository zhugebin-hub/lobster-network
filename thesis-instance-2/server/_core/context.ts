import type { CreateExpressContextOptions } from "@trpc/server/adapters/express";
import type { User } from "../../drizzle/schema";
import { COOKIE_NAME } from "@shared/const";
import { parse as parseCookieHeader } from "cookie";
import { jwtVerify } from "jose";
import * as db from "../db";

export type TrpcContext = {
  req: CreateExpressContextOptions["req"];
  res: CreateExpressContextOptions["res"];
  user: User | null;
};

function getSessionSecret() {
  const secret = process.env.JWT_SECRET || "thesis-secret-key";
  return new TextEncoder().encode(secret);
}

export async function createContext(
  opts: CreateExpressContextOptions
): Promise<TrpcContext> {
  let user: User | null = null;

  try {
    const cookieHeader = opts.req.headers.cookie;
    if (cookieHeader) {
      const cookies = parseCookieHeader(cookieHeader);
      const sessionCookie = cookies[COOKIE_NAME];

      if (sessionCookie) {
        const secretKey = getSessionSecret();
        const { payload } = await jwtVerify(sessionCookie, secretKey, {
          algorithms: ["HS256"],
        });
        const openId = payload.openId as string;

        if (openId) {
          user = await db.getUserByOpenId(openId);
          if (user) {
            await db.upsertUser({
              openId: user.openId,
              lastSignedIn: new Date(),
            });
          }
        }
      }
    }
  } catch (error) {
    // Authentication is optional for public procedures.
    user = null;
  }

  return {
    req: opts.req,
    res: opts.res,
    user,
  };
}
