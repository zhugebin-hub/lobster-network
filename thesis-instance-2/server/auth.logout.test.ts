import { describe, expect, it } from "vitest";
import { appRouter } from "./routers";
import { COOKIE_NAME } from "../shared/const";
import type { TrpcContext } from "./_core/context";

type CookieCall = {
  name: string;
  value?: string;
  options: Record<string, unknown>;
};

function createMockContext(): { ctx: TrpcContext; cookies: CookieCall[]; clearedCookies: CookieCall[] } {
  const cookies: CookieCall[] = [];
  const clearedCookies: CookieCall[] = [];

  const ctx: TrpcContext = {
    user: null,
    req: {
      protocol: "https",
      headers: {},
    } as TrpcContext["req"],
    res: {
      cookie: (name: string, value: string, options: Record<string, unknown>) => {
        cookies.push({ name, value, options });
      },
      clearCookie: (name: string, options: Record<string, unknown>) => {
        clearedCookies.push({ name, options });
      },
    } as TrpcContext["res"],
  };

  return { ctx, cookies, clearedCookies };
}

describe("auth.login", () => {
  it("should login with admin credentials (root/xd-zjgsu)", async () => {
    const { ctx, cookies } = createMockContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });

    expect(result.success).toBe(true);
    expect(result.user?.email).toBe("root");
    expect(result.user).toBeDefined();
    expect(result.user?.role).toBe("admin");
    expect(cookies.length).toBeGreaterThan(0);
    expect(cookies[0]?.name).toBe(COOKIE_NAME);
  });

  it("should reject invalid credentials", async () => {
    const { ctx } = createMockContext();
    const caller = appRouter.createCaller(ctx);

    await expect(
      caller.auth.login({
        email: "root",
        password: "wrongpassword",
      })
    ).rejects.toThrow();
  });
});

describe("auth.logout", () => {
  it("clears the session cookie and reports success", async () => {
    const { ctx, clearedCookies } = createMockContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.auth.logout();

    expect(result).toEqual({ success: true });
    expect(clearedCookies).toHaveLength(1);
    expect(clearedCookies[0]?.name).toBe(COOKIE_NAME);
  });
});

describe("auth.me", () => {
  it("returns null for unauthenticated user", async () => {
    const { ctx } = createMockContext();
    const caller = appRouter.createCaller(ctx);

    const result = await caller.auth.me();

    expect(result).toBeNull();
  });
});
