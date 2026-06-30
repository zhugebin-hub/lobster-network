import { describe, it, expect } from "vitest";
import { appRouter } from "./routers";
import type { TrpcContext } from "./_core/context";

type CookieCall = {
  name: string;
  value?: string;
  options: Record<string, unknown>;
};

function createMockContext(user?: TrpcContext["user"]): { ctx: TrpcContext; cookies: CookieCall[]; clearedCookies: CookieCall[] } {
  const cookies: CookieCall[] = [];
  const clearedCookies: CookieCall[] = [];

  const ctx: TrpcContext = {
    user: user || null,
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

describe("Purchase Module - Public Procedures", () => {
  it("should get lab admin wechat info (may be null if not set)", async () => {
    // 先登录获取用户上下文
    const { ctx: loginCtx, cookies } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    // 使用已登录用户调用
    const { ctx: userCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: loginResult.user!.role as "admin" | "teacher" | "student",
    });
    const caller = appRouter.createCaller(userCtx);
    
    const result = await caller.purchase.getLabAdminWechat();
    // 结果可能是 null 或包含 wechatId 和 wechatNote
    if (result) {
      expect(result).toHaveProperty("wechatId");
      expect(result).toHaveProperty("wechatNote");
    }
  });
});

describe("Purchase Module - Admin Procedures", () => {
  it("should get special roles list (lab_admin)", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: adminCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(adminCtx);
    
    const labAdmins = await caller.purchase.getSpecialRoles({ roleType: "lab_admin" });
    expect(Array.isArray(labAdmins)).toBe(true);
  });

  it("should get special roles list (asset_leader)", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: adminCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(adminCtx);
    
    const assetLeaders = await caller.purchase.getSpecialRoles({ roleType: "asset_leader" });
    expect(Array.isArray(assetLeaders)).toBe(true);
  });

  it("should get all purchase requests", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: adminCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(adminCtx);
    
    const requests = await caller.purchase.getAllRequests({});
    expect(Array.isArray(requests)).toBe(true);
  });

  it("should get pending lab review requests", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: adminCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(adminCtx);
    
    const requests = await caller.purchase.getPendingLabReview();
    expect(Array.isArray(requests)).toBe(true);
  });

  it("should get pending asset review requests", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: adminCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(adminCtx);
    
    const requests = await caller.purchase.getPendingAssetReview();
    expect(Array.isArray(requests)).toBe(true);
  });
});

describe("Purchase Module - User Role Checks", () => {
  it("should check if user is lab admin", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: userCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(userCtx);
    
    const isLabAdmin = await caller.purchase.isLabAdmin();
    expect(typeof isLabAdmin).toBe("boolean");
  });

  it("should check if user is asset leader", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: userCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(userCtx);
    
    const isAssetLeader = await caller.purchase.isAssetLeader();
    expect(typeof isAssetLeader).toBe("boolean");
  });

  it("should get user special roles", async () => {
    const { ctx: loginCtx } = createMockContext();
    const loginCaller = appRouter.createCaller(loginCtx);
    
    const loginResult = await loginCaller.auth.login({
      email: "root",
      password: "xd-zjgsu",
    });
    
    expect(loginResult.success).toBe(true);
    
    const { ctx: userCtx } = createMockContext({
      id: loginResult.user!.id,
      email: loginResult.user!.email,
      name: loginResult.user!.name || null,
      role: "admin",
    });
    const caller = appRouter.createCaller(userCtx);
    
    const roles = await caller.purchase.getMySpecialRoles();
    expect(Array.isArray(roles)).toBe(true);
  });
});
